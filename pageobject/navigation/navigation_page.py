class NavigationPage:

    def __init__(self, page):
        self.page =page

    def orgainsation(self):
        organization_menu =self.page.get_by_role("link",name="Organization", exact=True)
        organization_menu.click()

    def companysetup(self):
        self.orgainsation()
        company_setup =self.page.get_by_role("link",name='Company Setup', exact=True)
        company_setup.click()

    def legalentities(self):
        self.orgainsation()
        self.companysetup()
        legal_entities =self.page.get_by_role("link",name='Legal Entities', exact=True)
        legal_entities.click()

    def companyprofile(self):
        self.orgainsation()
        self.companysetup()
        company_profile = self.page.get_by_role("link", name="Company Profile", exact=True)
        company_profile.click()