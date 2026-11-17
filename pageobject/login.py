import re

from playwright.sync_api import expect


class LoginPage:

    def __init__(self, page):
        self.page = page

        # Login form fields (located by their stable "name" attribute)
        self.company_code = self.page.locator('input[name="company_code"]')
        self.login_id = self.page.locator('input[name="login_id"]')
        self.password = self.page.locator('input[name="password"]')
        self.remember_me = self.page.get_by_role("checkbox", name="Remember me")
        self.sign_in_button = self.page.get_by_role("button", name="Sign In")
        self.forgot_password_link = self.page.get_by_role("link", name="Forgot password?")

        # Page-level alert shown above the form, e.g. "Invalid company or login credentials."
        self.form_alert = self.page.locator(".login > .alert[role='alert']")

    # Login page URL, allowing an optional query string such as ?next=...
    LOGIN_URL = re.compile(r"/login(\?.*)?$")

    def signIn(self, company, username, password):
        self.fill_credentials(company, username, password)
        self.click_sign_in()

    def fill_credentials(self, company, username, password):
        self.company_code.fill(company)
        self.login_id.fill(username)
        self.password.fill(password)

    def click_sign_in(self):
        self.sign_in_button.click()

    def check_remember_me(self):
        self.remember_me.check()
        expect(self.remember_me).to_be_checked()

    def click_forgot_password(self):
        self.forgot_password_link.click()

    def field_error(self, field):
        """Inline validation message linked to an input through aria-describedby."""
        error_id = field.get_attribute("aria-describedby")
        assert error_id, "Field has no linked validation message (aria-describedby is missing)"
        return self.page.locator(f'[id="{error_id}"]')

    def verify_field_error(self, field, expected_message):
        # Wait for the field to be flagged invalid before reading its message
        expect(field).to_have_attribute("aria-invalid", "true")
        expect(self.field_error(field)).to_have_text(expected_message)

    def verify_required_field_errors(self, messages):
        self.verify_field_error(self.company_code, messages["company_code"])
        self.verify_field_error(self.login_id, messages["login_id"])
        self.verify_field_error(self.password, messages["password"])

    def verify_form_alert(self, expected_message):
        expect(self.form_alert).to_be_visible()
        expect(self.form_alert).to_have_text(expected_message)

    def verify_login_page(self):
        expect(self.page).to_have_url(self.LOGIN_URL)
        expect(self.sign_in_button).to_be_visible()

    def verify_login_success(self):
        # Leaving /login and seeing the main menu means the session is active
        expect(self.page).not_to_have_url(self.LOGIN_URL, timeout=15000)
        expect(self.page.get_by_role("link", name="Organization", exact=True)).to_be_visible(timeout=15000)
