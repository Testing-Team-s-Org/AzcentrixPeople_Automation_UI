from playwright.sync_api import Page,expect


class LoginPage:

    def __init__(self, page):
        self.page =page

        #signInButton
        self.sign_in_button = page.get_by_role(
            "button", name="Sign In"
        )
        self.send_button = self.page.get_by_role("button", name="Send reset instructions")
        self.company_code= self.page.locator('input[name="company_code"]')
        self.user_name = self.page.locator('input[name="login_id"]')

    #successful signin
    def signIn(self,company,username,password):
        self.company_code.fill(company)
        self.user_name.fill(username)
        self.page.locator('input[name="password"]').fill(password)
        self.signInButton()

    def signOut(self):
        # Open account menu
        account_menu = self.page.locator("button.user-menu__trigger")
        expect(account_menu).to_be_visible()
        account_menu.click()

        # Wait for Sign out button and click
        signout_button = self.page.locator("button.user-menu__signout")
        expect(signout_button).to_be_visible()
        signout_button.click()

        expect (self.sign_in_button).to_be_visible()


    #Validation message assertion
    def valid_Message(self):
        self.signInButton()
        # Verify Company Code validation
        expect(self.field_error("company_code")).to_have_text("Enter your company code.")
        # Verify Login ID validation
        expect(self.field_error("login_id")).to_have_text("Enter your Login ID.")
        # Verify Password validation
        expect(self.field_error("password")).to_have_text("Enter your password.")
        print("PASS: All required field validation messages displayed.")

    #forgot password
    def forgot_password(self,company, username):
      #click forgot password
      self.click_forgot_password()
      #reset credentials
      self.request_reset( company, username)
      #verify successful reset link sent
      self.verify_success_message()



    def signInButton(self):
        self.sign_in_button.click()

    def field_error(self, input_name):
        # The error <p> is a sibling of the input's wrapper, so scope to the whole .field block
        return self.page.locator("div.field", has=self.page.locator(f'input[name="{input_name}"]')).locator("p.field__error")

    def click_forgot_password(self):
        self.page.get_by_role("link", name="Forgot password?").click()
        expect(self.page.get_by_role("heading", name="Reset your password")).to_be_visible()

    def request_reset(self, company, username):
        self.company_code.fill(company)
        self.user_name.fill(username)
        self.send_button.click()

    def verify_success_message(self):
        expect(self.page.get_by_role("status")).to_be_visible()
        expect( self.page.get_by_role("status")).to_contain_text(  "Password reset instructions have been sent")
        self.page.get_by_role("link", name="Back to company login").click()










