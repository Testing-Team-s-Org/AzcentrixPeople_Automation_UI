from playwright.sync_api import Page, Playwright

from pageobject.login import LoginPage

from pageobject.navigation.navigation_page import NavigationPage


def test_logins(page: Page, browserInstance, credentials):
    # credentials come from .env via the conftest.py fixture
    code = credentials["companyCode"]
    userName = credentials["userName"]
    password = credentials["password"]

    login = LoginPage(browserInstance)
    login.signIn(code, userName, password)


def test_valid_message_displayed(playwright:Playwright,browserInstance):
    login = LoginPage(browserInstance)
    login.valid_Message()

