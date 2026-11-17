from playwright.sync_api import Page

from pageobject.login import LoginPage

from pageobject.navigation.navigation_page import NavigationPage


def test_logins(page: Page, browserInstance, credentials):
    # credentials come from .env via the conftest.py fixture
    code = credentials["companyCode"]
    userName = credentials["userName"]
    password = credentials["password"]

    login = LoginPage(browserInstance)
    login.signIn(code, userName, password)

    #navigate
    navi = NavigationPage(browserInstance)
    navi.legalentities()
