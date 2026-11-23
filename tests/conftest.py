import os
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from dotenv import load_dotenv
from pytest_metadata.plugin import metadata_key

# Project root = folder that holds pytest.ini (one level above tests/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"

# Load secrets from <project>/.env into os.environ (no-op if the file is missing)
load_dotenv(PROJECT_ROOT / ".env")

# Always run without the Playwright Inspector, even if PWDEBUG=1 is set in the terminal
os.environ["PWDEBUG"] = "0"

# Filled in by pytest_configure from the command line; read by the report hooks below
REPORT_INFO = {
    "module": "All Modules",
    "test_file": "All test files",
    "browser": "chrome",
    "marker": "",
}


@pytest.fixture(scope="session")
def data_dir():
    """Absolute path to the project's data/ folder (holds the JSON test data)."""
    path = PROJECT_ROOT / "data"
    assert path.is_dir(), f"data directory not found: {path}"
    return path


# Environments the suite can run against. Each one has its own block in .env:
#   <ENV>_URL, <ENV>_ADMIN_ONE_{COMPANY_CODE,USERNAME,PASSWORD}, <ENV>_ADMIN_TWO_{...}
ENVIRONMENTS = ("dev", "testing")


def _environment(config):
    """Environment from --env, else TEST_ENV in .env, else 'testing'."""
    return (config.getoption("--env") or os.getenv("TEST_ENV") or "testing").lower()


def _env_value(env, key):
    """Read one .env value for an environment, e.g. TESTING_URL or DEV_ADMIN_ONE_USERNAME."""
    return os.getenv(f"{env.upper()}_{key}")


def _admin_login(request, admin):
    """Login for one admin ('ADMIN_ONE' or 'ADMIN_TWO') in the selected environment."""
    env = _environment(request.config)
    creds = SimpleNamespace(
        company_code=_env_value(env, f"{admin}_COMPANY_CODE"),
        username=_env_value(env, f"{admin}_USERNAME"),
        password=_env_value(env, f"{admin}_PASSWORD"),
    )
    missing = [
        f"{env.upper()}_{admin}_{name.upper()}"
        for name, value in vars(creds).items() if not value
    ]
    if missing:
        pytest.fail(f"Missing values in .env: {', '.join(missing)}")
    return SimpleNamespace(credentials=creds)


@pytest.fixture(scope="session")
def admin_one(request):
    """Admin 1 login for the selected environment. Fails early if any value is missing.

    Use in a test as:  admin_one.credentials.company_code / .username / .password
    """
    return _admin_login(request, "ADMIN_ONE")


@pytest.fixture(scope="session")
def admin_two(request):
    """Admin 2 login for the selected environment. Same shape as admin_one."""
    return _admin_login(request, "ADMIN_TWO")


def pytest_addoption(parser):
    parser.addoption("--browser_name", action="store", default="chrome", help="Browser selection: chrome, edge, firefox, webkit")

    parser.addoption("--env", action="store", default=None, choices=ENVIRONMENTS,
                     help="Environment to test: dev or testing (default: TEST_ENV in .env, else testing)")

    parser.addoption("--url_name", action="store", default=None,
                     help="Login URL override. Default: <ENV>_URL from .env")


@pytest.fixture
def browserInstance(playwright, request):

    browser_name = request.config.getoption("--browser_name")
    url_name = request.config.getoption("--url_name") or _env_value(_environment(request.config), "URL")
    if not url_name:
        pytest.fail(f"No login URL for this environment: set {_environment(request.config).upper()}_URL in .env or pass --url_name")

    if browser_name == "chrome":
        # Use the installed Google Chrome; Playwright's bundled Chromium crashes in headed mode on this machine
        browser = playwright.chromium.launch(channel="chrome", headless=False)

    elif browser_name == "edge":
        browser = playwright.chromium.launch(channel="msedge",headless=False)

    elif browser_name == "firefox":
        browser = playwright.firefox.launch(headless=False)

    elif browser_name == "webkit":
        browser = playwright.webkit.launch(headless=False)

    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    # Ignore SSL certificate errors
    context = browser.new_context(ignore_https_errors=True)

    page = context.new_page()

    page.goto(url_name)

    yield page

    context.close()
    browser.close()


# ----------------------------------------------------------------------
# Report naming and labels - derived from what was asked to run
# ----------------------------------------------------------------------

def _label(name):
    """'Legal_Entities' -> 'Legal Entities'."""
    return name.replace("_", " ").replace("-", " ").strip().title()


def _resolve_report(config):
    """Work out module label, test-file label and report file name.

    - one test file  -> reports/<File_Name>[_<marker>]_report.html
    - one folder     -> reports/<folder>[_<marker>]_report.html
    - anything else  -> reports/automation_report[_<marker>].html  (overall)
    """
    marker = config.option.markexpr or ""
    suffix = f"_{re.sub(r'[^A-Za-z0-9]+', '_', marker).strip('_')}" if marker else ""

    args = [arg.split("::")[0] for arg in config.args]
    if len(args) == 1:
        target = Path(args[0])
        if not target.is_absolute():
            target = Path(config.invocation_params.dir) / target

        if target.is_file() and target.suffix == ".py":
            short = target.stem[5:] if target.stem.startswith("test_") else target.stem
            return {
                "module": _label(short),
                "test_file": target.name,
                "report": f"{short}{suffix}_report.html",
            }

        if target.is_dir() and target.resolve() != (PROJECT_ROOT / "tests").resolve():
            return {
                "module": _label(target.name),
                "test_file": f"{target.name}/ (folder)",
                "report": f"{target.name}{suffix}_report.html",
            }

    return {
        "module": "All Modules",
        "test_file": "All test files",
        "report": f"automation_report{suffix}.html",
    }


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    info = _resolve_report(config)
    REPORT_INFO.update(
        module=info["module"],
        test_file=info["test_file"],
        browser=config.getoption("--browser_name"),
        marker=config.option.markexpr or "",
    )

    # Only pick the file name automatically when --html was not given on the command line
    if not config.option.htmlpath:
        config.option.htmlpath = str(REPORTS_DIR / info["report"])


def pytest_sessionstart(session):
    # Metadata shows in the report's Environment table
    session.config.stash[metadata_key].update({
        "Project": "Legal Entities Automation",
        "Module": REPORT_INFO["module"],
        "Test File": REPORT_INFO["test_file"],
        "Browser": REPORT_INFO["browser"],
        "Marker": REPORT_INFO["marker"] or "none",
        "Framework": "Python + Playwright + Pytest",
        "Environment": _environment(session.config).upper(),
        "Executed By": "Automation Team",
    })


def pytest_html_report_title(report):
    report.title = f"{REPORT_INFO['module']} Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    execution_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    prefix.extend([
        f"<p><strong>Execution:</strong> {execution_date}</p>",
        f"<p><strong>Module:</strong> {REPORT_INFO['module']}</p>",
        f"<p><strong>Test file:</strong> {REPORT_INFO['test_file']}</p>",
        f"<p><strong>Browser:</strong> {REPORT_INFO['browser']}</p>",
    ])