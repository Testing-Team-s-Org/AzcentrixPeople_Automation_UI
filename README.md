# Playwright UI Automation (Python)

End-to-end UI tests for the company setup portal, written with **Playwright for Python** and run with **pytest**. Tests drive a real browser, log in, maintain the company profile and legal entities, and verify what the application shows.

## Project structure

```
Playwright/
├── .env                      # Login secrets (NOT committed - see Setup)
├── .env.example              # Empty template for .env
├── .github/workflows/
│   └── ui-tests.yml          # CI: runs the UI tests on push / pull request / manual trigger
├── main.py                   # PyCharm template script (not used by the tests)
├── pytest.ini                # pytest settings, markers, default options
├── requirements.txt          # Python dependencies
├── data/
│   ├── Company_profile.json  # Test data for the company profile save + verify
│   ├── Legal_entities.json   # Test data for legal entity creation
│   └── Login-Credential.json # Not read by any test at present
├── reports/                  # Generated HTML test reports (created on first run)
├── pageobject/               # Page Object Model - one class per page
│   ├── login.py              # Company login page (sign in, validation, forgot password)
│   ├── navigation/navigation_page.py       # Side menu navigation
│   ├── company_profile/company_profile.py  # Fill, save and verify the company profile
│   └── legal_entities/
│       ├── legal_entities.py          # Create / fill / submit the form
│       └── legal_entities_verify.py   # Verify the created entity
└── tests/
    ├── conftest.py           # Shared fixtures, command-line options, report naming
    ├── login/
    │   └── test_login.py
    └── organisation/
        ├── test_company_profile.py
        └── test_Legal_Entities.py
```

## How it works

- **Page objects** (`pageobject/`) hold the locators and actions for each screen. Tests call methods such as `signIn()` or `fill_legal_entity()` and never touch selectors directly.
- **Test data** lives in `data/*.json`. The company profile and legal entity tests read their input from there, via the `data_dir` fixture.
- **Credentials and environments:** every test that logs in takes the `admin_one` fixture and reads `admin_one.credentials.company_code`, `.username` and `.password`. Values come from the block of `.env` for the selected environment (`dev` or `testing`).
- **Unique entity codes:** each legal entity run appends a timestamp to the base code in the JSON (`IND` becomes e.g. `IND261117123807`), so repeated runs don't collide. The code is read back from the input box, and the verify step checks that exact value.

## Setup

1. **Python and virtual environment** (from the project root):

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Browsers** (one-time, after installing the packages):

   ```bat
   python -m playwright install chromium firefox
   ```

   `chrome` and `edge` run the Google Chrome and Microsoft Edge installed on the machine, so those two must be installed too.

3. **Credentials** - copy the template and fill in real values:

   ```bat
   copy .env.example .env
   ```

   ```env
   TEST_ENV=testing                      # dev | testing

   DEV_URL=https://103.110.236.187:8822/login
   DEV_ADMIN_ONE_COMPANY_CODE=...
   DEV_ADMIN_ONE_USERNAME=...
   DEV_ADMIN_ONE_PASSWORD=...

   TESTING_URL=http://192.168.11.32:8180/login
   TESTING_ADMIN_ONE_COMPANY_CODE=...
   TESTING_ADMIN_ONE_USERNAME=...
   TESTING_ADMIN_ONE_PASSWORD=...
   ```

   `.env` is listed in `.gitignore` and must never be committed. If any value is missing, the tests stop with a clear message naming the missing key.

## Running the tests

Run from the project root:

```bat
:: All tests on Chrome (default browser)
python -m pytest tests --browser_name=chrome

:: One folder
python -m pytest tests/organisation --browser_name=chrome

:: One test file
python -m pytest tests/organisation/test_Legal_Entities.py --browser_name=chrome

:: Firefox
python -m pytest tests/organisation/test_Legal_Entities.py --browser_name=firefox
```

| Option | Default | Values | Purpose |
|---|---|---|---|
| `--browser_name` | `chrome` | `chrome`, `edge`, `firefox`, `webkit` | Browser to launch |
| `--env` | `TEST_ENV` from `.env`, else `testing` | `dev`, `testing` | Environment: picks the URL and admin_one login from `.env` |
| `--url_name` | `<ENV>_URL` from `.env` | any URL | Login page override |

Examples: `python -m pytest tests --env dev` or `python -m pytest tests --env testing -m smoke`.

`pytest.ini` already adds `-v -s`, so `print` output (such as the generated entity code) is shown on every run.

### Run by marker

Tests are tagged `smoke` (quick critical path) or `regression` (full coverage):

```bat
python -m pytest tests -m smoke --browser_name=chrome
python -m pytest tests -m regression --browser_name=chrome
```

The company profile and legal entity tests carry both markers. The login tests carry no `smoke` or `regression` marker, so `-m smoke` and `-m regression` do not run them.

### Parallel run (optional)

`pytest-xdist` is installed. Tests marked `parallel` can run side by side:

```bat
python -m pytest tests/login -n 2 --dist loadgroup
```

- `@pytest.mark.parallel` marks a test as safe to run in parallel.
- `@pytest.mark.xdist_group("login")` keeps every test in the same group on one worker, in file order.

Only the two login tests that have these markers are safe to run in parallel. The CI workflow does not use `-n`.

## Reports

Every run writes an HTML report to `reports/`. The file name depends on what you ran:

| Command | Report file |
|---|---|
| one test file, e.g. `tests/organisation/test_company_profile.py` | `reports/company_profile_report.html` |
| one test file, e.g. `tests/organisation/test_Legal_Entities.py` | `reports/Legal_Entities_report.html` |
| one folder, e.g. `tests/login` | `reports/login_report.html` |
| one folder with a marker, e.g. `tests/organisation -m smoke` | `reports/organisation_smoke_report.html` |
| whole suite, no marker | `reports/automation_report.html` |
| whole suite with `-m smoke` / `-m regression` | `reports/automation_report_smoke.html` / `reports/automation_report_regression.html` |

Open the file in any browser. Its heading, module, test file, browser and marker are taken from the command you ran. To write to a specific file, pass `--html=reports/<name>.html` yourself and it is used instead.

## Fixtures (`tests/conftest.py`)

| Fixture | Scope | Provides |
|---|---|---|
| `browserInstance` | function | A browser page opened on the login URL, with SSL errors ignored. Closed after the test. |
| `admin_one` | session | `credentials.company_code`, `.username`, `.password` for the selected environment, loaded from `.env`. Fails if any is empty. |
| `data_dir` | session | Absolute path to the `data/` folder, so tests can load JSON without relative-path tricks. |

Use them by naming them as test arguments:

```python
def test_example(browserInstance, admin_one, data_dir):
    with open(data_dir / "Legal_entities.json", encoding="utf-8") as f:
        ...
```

## Test flow: company profile (`tests/organisation/test_company_profile.py`)

`test_save_company_profile` (markers `smoke`, `regression`) runs these steps:

1. Load the first entry of `data/Company_profile.json`.
2. Log in with the `admin_one` fixture.
3. Navigate to **Organization > Company Setup > Company Profile**.
4. Check the page loaded and the company code is disabled, fill the form, and save.
5. Check the **Company profile saved.** message and the Complete badge.
6. Reload the page and compare every saved value with the JSON.

## Test flow: create and verify a legal entity (`tests/organisation/test_Legal_Entities.py`)

`test_create_legal_entity` (markers `smoke`, `regression`) runs these steps:

1. Log in with the `credentials` fixture.
2. Navigate to **Legal Entities**.
3. `fill_legal_entity()` clicks **Add legal entity**, fills the basic information (with a timestamped code), contact, registered and corporate address, sets the default flag, picks the effective-from date (Today), and submits. It returns the code it entered.
4. Check that the returned code starts with the JSON base code.
5. Verify the created entity: header, overview, address, statutory registration (adds a PAN), effective information, and the activity log.

## Test flow: login (`tests/login/test_login.py`)

| Test | Marker | Steps |
|---|---|---|
| `test_logins` | `parallel`, group `login` | Sign in with the `.env` credentials. |
| `test_valid_message_displayed` | `parallel`, group `login` | Click **Sign In** with empty fields and check each field's required message (`Enter your company code.`, `Enter your Login ID.`, `Enter your password.`). |
| `test_forgot_password` | none | Open **Forgot password?**, request a reset for the `.env` account, check the success message, then go **Back to company login**. This sends a real reset email to the account on every run. |

## CI (`.github/workflows/ui-tests.yml`)

- **On push and pull request** to `main` or `master`: runs the `smoke` tests on Chrome.
- **Manual run** (`workflow_dispatch`): choose the marker (`smoke`, `regression`, `all`) and the browser (`chrome`, `firefox`).
- CI runs the `testing` environment. The workflow maps repository secrets `LOGIN_COMPANY_CODE`, `LOGIN_USERNAME` and `LOGIN_PASSWORD` to `TESTING_ADMIN_ONE_*`, and sets `TESTING_URL`. No `.env` file is needed on the runner.
- The HTML reports in `reports/` are uploaded as a workflow artifact, kept for 14 days.

## Adding a new test

1. Put its input data in `data/` if it needs any, and load it through the `data_dir` fixture.
2. Add locators and actions to a page object in `pageobject/`.
3. Create `tests/<area>/test_<name>.py`, take `browserInstance`, `credentials` or `data_dir` as arguments as needed, and tag it with `smoke`, `regression` or both.

## Troubleshooting

- **`Missing login values in .env`** - the `.env` file is missing or a key is empty. Check the file is in the project root.
- **`Executable doesn't exist` for a browser** - run `python -m playwright install <browser>`.
- **Browser fails to launch with `chrome` or `edge`** - these use the installed browser. Install Google Chrome or Microsoft Edge, or use `--browser_name=firefox`.
- **Click times out or "intercepts pointer events"** - an element is hidden under the modal or below the fold. Scroll it into view first (see `select_effective_date`).
- **Locator or strict-mode errors** - a second dialog or element matches the same role and name. Narrow the locator with a name or a container.
- **`Page.locator() got an unexpected keyword argument 'text'`** - use `has_text=` in Playwright locators.
