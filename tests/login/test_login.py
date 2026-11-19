# pytest "tests/login/test_login.py::test_logins" "tests/login/test_login.py::test_valid_message_displayed" -n 2 --dist loadgroup
#python -m pytest tests/login/test_login.py -s -n 4 ( 4 workers)
#
import pytest
from playwright.sync_api import Page, Playwright

from pageobject.login import LoginPage



@pytest.mark.parallel
@pytest.mark.xdist_group("login")
def test_logins(page: Page, browserInstance, credentials):
    # credentials come from .env via the conftest.py fixture
    code = credentials["companyCode"]
    userName = credentials["userName"]
    password = credentials["password"]

    login = LoginPage(browserInstance)
    login.signIn(code, userName, password)


@pytest.mark.parallel
@pytest.mark.xdist_group("login")
def test_valid_message_displayed(playwright:Playwright,browserInstance):
    login = LoginPage(browserInstance)
    login.valid_Message()


def test_forgot_password(page: Page, browserInstance, credentials):
    code = credentials["companyCode"]
    userName = credentials["userName"]

    forgot = LoginPage(browserInstance)
    forgot.forgot_password(code, userName)