from playwright.sync_api import expect


class ForgotPasswordPage:

    def __init__(self, page):
        self.page = page

        self.title = self.page.get_by_role("heading", name="Reset your password")
        self.company_code = self.page.locator('input[name="company_code"]')
        self.login_id = self.page.locator('input[name="login_id"]')
        self.send_button = self.page.get_by_role("button", name="Send reset instructions")
        self.back_to_login_link = self.page.get_by_role("link", name="Back to company login")
        # Success banner replaces the form after a reset request
        self.success_message = self.page.locator(".login .alert--success[role='status']")

    def verify_page_loaded(self):
        # "Reset your password" header confirms the Forgot password page opened
        expect(self.title).to_be_visible()
        expect(self.title).to_have_text("Reset your password")

    def request_reset(self, company, username):
        self.company_code.fill(company)
        self.login_id.fill(username)
        self.send_button.click()

    def verify_success_message(self, expected_message):
        expect(self.success_message).to_be_visible(timeout=15000)
        expect(self.success_message).to_have_text(expected_message)
        # Form is no longer shown once the request is accepted
        expect(self.send_button).to_be_hidden()

    def back_to_login(self):
        self.back_to_login_link.click()
