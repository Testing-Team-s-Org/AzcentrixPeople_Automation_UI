# Playwright UI Automation (Python)

End-to-end UI tests for the company setup portal, written with **Playwright for Python** and run with **pytest**. Tests drive a real browser (Chrome, Edge or Firefox), log in, create a legal entity, and verify what the application shows.

## Project structure

```
Playwright/
├── .env                      # Login secrets (NOT committed - see below)
├── .env.example              # Empty template for .env
├── pytest.ini                # pytest settings (pythonpath = project root)
├── requirements.txt          # Python dependencies
├── data/
│   └── Legal_entities.json   # Test data for legal entity creation
├── reports/                  # Generated HTML test reports (created on first run)
│   ├── Legal_Entities_report.html        # single test file
│   ├── automation_report.html            # whole suite, no marker
│   └── automation_report_smoke.html      # whole suite with -m smoke
├── pageobject/               # Page Object Model - one class per page
│   ├── login.py
│   ├── navigation/navigation_page.py
│   └── legal_entities/
│       ├── legal_entities.py          # Create / fill / submit the form
│       └── legal_entities_verify.py   # Verify the created entity
└── tests/
    ├── conftest.py           # Shared fixtures and command-line options
    ├── login/test_login.py
    └── legal-entities/test_Legal_Entities.py
```

## How it works

- **Page objects** (`pageobject/`) hold the locators and actions for each screen. Tests call methods such as `signIn()` or `fill_legal_entity()` and never touch selectors directly.
- **Test data** lives in `data/*.json`. The legal entity test reads its input from there.
- **Credentials** are read from `.env`, never from source files.
- **Unique entity codes:** each run appends a timestamp to the base code in the JSON (`IND` becomes e.g. `IND261117123807`), so repeated runs don't collide. The code is read back from the input box, and the verify step checks that exact value.

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

3. **Credentials** - copy the template and fill in real values:

   ```bat
   copy .env.example .env
   ```

   ```env
   LOGIN_COMPANY_CODE=your-company-code
   LOGIN_USERNAME=your-user@example.com
   LOGIN_PASSWORD=your-password
   ```

   `.env` is listed in `.gitignore` and must never be committed. If any value is missing, the tests stop with a clear message naming the missing key.

## Running the tests

Run from the project root:

```bat
:: All tests on Chrome (default browser)
python -m pytest tests -s --browser_name=chrome

:: One test file
python -m pytest tests/legal-entities/test_Legal_Entities.py -s --browser_name=chrome

:: Firefox
python -m pytest tests/legal-entities/test_Legal_Entities.py -s --browser_name=firefox
```

| Option | Default | Values | Purpose |
|---|---|---|---|
| `--browser_name` | `chrome` | `chrome`, `edge`, `firefox` | Browser to launch |
| `--url_name` | `https://103.110.236.187:8822/login` | any URL | Application login page |

`-s` shows `print` output, such as the generated entity code.

Run by marker (tests are tagged `smoke` or `regression`):

```bat
python -m pytest tests -m smoke --browser_name=chrome
python -m pytest tests -m regression --browser_name=chrome
```

## Reports

Every run writes an HTML report to `reports/`. The file name depends on what you ran:

| Command | Report file |
|---|---|
| one test file, e.g. `tests/legal-entities/test_Legal_Entities.py` | `reports/Legal_Entities_report.html` |
| one folder, e.g. `tests/login` | `reports/login_report.html` |
| whole suite, no marker | `reports/automation_report.html` |
| whole suite with `-m smoke` / `-m regression` | `reports/automation_report_smoke.html` / `..._regression.html` |

Open the file in any browser. Its heading, module, test file, browser and marker are taken from the command you ran. To write to a specific file, pass `--html=reports/<name>.html` yourself and it is used instead.

## Fixtures (`tests/conftest.py`)

| Fixture | Scope | Provides |
|---|---|---|
| `browserInstance` | function | A browser page opened on the login URL, with SSL errors ignored. Closed after the test. |
| `credentials` | session | `companyCode`, `userName`, `password` loaded from `.env`. Fails if any is empty. |
| `data_dir` | session | Absolute path to the `data/` folder, so tests can load JSON without relative-path tricks. |

Use them by naming them as test arguments:

```python
def test_example(browserInstance, credentials, data_dir):
    with open(data_dir / "Legal_entities.json", encoding="utf-8") as f:
        ...
```

## Test flow: create and verify a legal entity

`test_create_legal_entity` runs these steps:

1. Log in with the `credentials` fixture.
2. Navigate to **Legal Entities**.
3. `fill_legal_entity()` clicks **Add legal entity**, fills the basic information (with a timestamped code), contact, registered and corporate address, sets the default flag, picks the effective-from date (Today), and submits. It returns the code it entered.
4. Check that the returned code starts with the JSON base code.
5. Verify the created entity: header, overview, address, statutory registration (adds a PAN), effective information, and the activity log.

## Adding a new test

1. Put its input data in `data/` if it needs any.
2. Add locators and actions to a page object in `pageobject/`.
3. Create `tests/<area>/test_<name>.py`, and take `browserInstance`, `credentials` or `data_dir` as arguments as needed.

## Troubleshooting

- **`Missing login values in .env`** - the `.env` file is missing or a key is empty. Check the file is in the project root.
- **`Executable doesn't exist` for a browser** - run `python -m playwright install <browser>`.
- **Click times out or "intercepts pointer events"** - an element is hidden under the modal or below the fold. Scroll it into view first (see `select_effective_date`).
- **Locator or strict-mode errors** - a second dialog or element matches the same role and name. Narrow the locator with a name or a container.
- **`Page.locator() got an unexpected keyword argument 'text'`** - use `has_text=` in Playwright locators.
