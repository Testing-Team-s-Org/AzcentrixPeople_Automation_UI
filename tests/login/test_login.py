# pytest "tests/login/test_login.py::test_logins" "tests/login/test_login.py::test_valid_message_displayed" -n 2 --dist loadgroup
#python -m pytest tests/login/test_login.py -s -n 4 ( 4 workers)
#
import pytest
from playwright.sync_api import Page, Playwright

from pageobject.login import LoginPage



@pytest.mark.parallel
@pytest.mark.xdist_group("login")
def test_logins(page: Page, browserInstance, admin_one):
    # admin_one comes from .env (selected environment) via the conftest.py fixture
    login = LoginPage(browserInstance)
    login.signIn(admin_one.credentials.company_code, admin_one.credentials.username, admin_one.credentials.password)

    login.signOut()


@pytest.mark.parallel
@pytest.mark.xdist_group("login")
def test_valid_message_displayed(playwright:Playwright,browserInstance):
    login = LoginPage(browserInstance)
    login.valid_Message()


def test_forgot_password(page: Page, browserInstance, admin_one):
    forgot = LoginPage(browserInstance)
    forgot.forgot_password(admin_one.credentials.company_code, admin_one.credentials.username)