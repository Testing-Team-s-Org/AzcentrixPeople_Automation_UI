from playwright.sync_api import Page,expect


class LoginPage:

    def __init__(self, page):
        self.page =page
        #signInButton
        self.sign_in_button = page.get_by_role(
            "button", name="Sign In"
        )



    def signIn(self,company,username,password):
        self.page.locator('input[class="field__input"]').first.fill(company)
        self.page.locator('input[class="field__input"]').nth(1).fill(username)
        self.page.locator('input[class="field__input"]').nth(2).fill(password)
        self.signInButton()



    def signInButton(self):
        self.sign_in_button.click()

    def field_error(self, input_name):
        # The error <p> is a sibling of the input's wrapper, so scope to the whole .field block
        return self.page.locator("div.field", has=self.page.locator(f'input[name="{input_name}"]')).locator("p.field__error")

    def valid_Message(self):
        self.signInButton()
        # Verify Company Code validation
        expect(self.field_error("company_code")).to_have_text("Enter your company code.")
        # Verify Login ID validation
        expect(self.field_error("login_id")).to_have_text("Enter your Login ID.")
        # Verify Password validation
        expect(self.field_error("password")).to_have_text("Enter your password.")


        print("PASS: All required field validation messages displayed.")





