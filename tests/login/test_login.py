import json

import pytest

from pageobject.login import LoginPage
from pageobject.forgot_password import ForgotPasswordPage

from pageobject.navigation.navigation_page import NavigationPage


@pytest.fixture
def login_data(data_dir):
    """All login test data: valid credentials, invalid password and expected messages."""
    with open(data_dir / "Login-Credential.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def valid_credentials(login_data):
    """Valid login from Login-Credential.json."""
    return login_data["superadmin"]


def test_logins(browserInstance, valid_credentials):
    code = valid_credentials["companyCode"]
    userName = valid_credentials["userName"]
    password = valid_credentials["password"]

    login = LoginPage(browserInstance)
    login.signIn(code, userName, password)
    login.verify_login_success()

    #navigate
    navi = NavigationPage(browserInstance)
    navi.legalentities()


@pytest.mark.regression
def test_login_validation_errors(browserInstance, valid_credentials, login_data):
    messages = login_data["messages"]
    login = LoginPage(browserInstance)

    # Step 1 - Login page is open (browserInstance navigates to the URL)
    login.verify_login_page()

    # Step 2 - Sign in with every field empty
    login.click_sign_in()

    # Step 3 - Each required field shows its own validation message
    login.verify_required_field_errors(messages["required"])
    login.verify_login_page()

    # Step 4 - Valid company code and username, wrong password
    login.signIn(valid_credentials["companyCode"], valid_credentials["userName"], login_data["invalid_password"])

    # Step 5 - Credentials error is shown and the user stays on the login page
    login.verify_form_alert(messages["invalid_credentials"])
    login.verify_login_page()


@pytest.mark.smoke
@pytest.mark.regression
def test_forgot_password_and_remember_me_login(browserInstance, valid_credentials, login_data):
    messages = login_data["messages"]
    login = LoginPage(browserInstance)

    # Step 1 - Open Forgot password and request a reset for a valid user
    login.click_forgot_password()
    forgot_password = ForgotPasswordPage(browserInstance)
    forgot_password.verify_page_loaded()
    forgot_password.request_reset(valid_credentials["companyCode"], valid_credentials["userName"])

    # Step 2 - Success message, then back to company login
    forgot_password.verify_success_message(messages["reset_success"])
    forgot_password.back_to_login()
    login.verify_login_page()

    # Step 3 - Valid credentials with Remember me checked
    login.fill_credentials(valid_credentials["companyCode"], valid_credentials["userName"],
                           valid_credentials["password"])
    login.check_remember_me()
    login.click_sign_in()

    login.verify_login_success()
