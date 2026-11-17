

class LoginPage:

    def __init__(self, page):
        self.page =page



    def signIn(self,company,username,password):
        self.page.locator('input[class="field__input"]').first.fill(company)
        self.page.locator('input[class="field__input"]').nth(1).fill(username)
        self.page.locator('input[class="field__input"]').nth(2).fill(password)
        self.page.get_by_role("button",name="Sign In").click()