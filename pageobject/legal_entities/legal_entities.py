from datetime import datetime

from playwright.sync_api import Page, expect

class LegalEntities:


    def __init__(self, page):
        self.page =page

    def fill_legal_entity(self, data):
        """Fill the legal entity using JSON data."""
        self.add_Entity()

        entity_code = self.fill_basic_information(data["basic_information"])

        self.fill_contact_information(data["contact_information"])

        self.fill_registered_address(data["registered_address"])

        self.fill_corporate_address(data["corporate_address"])

        self.set_default_entity(data["default_entity"])

        self.select_effective_date()

        self.submit_entity()
        self.verify_form_visible()

        return entity_code


    def add_Entity(self):
        self.page.get_by_role('button',name=" Add legal entity").click()

    def fill_basic_information(self, data):
        #legal entity code - base value from JSON + timestamp so every run is unique
        code_box = self.page.get_by_role("textbox", name="Legal entity code")
        entity_code = f"{data['entity_code']}{datetime.now():%y%m%d%H%M%S}"
        code_box.fill(entity_code)

        # Read back what is actually in the input and check it was accepted
        entered_code = code_box.input_value()
        assert entered_code == entity_code, (
            f"Legal entity code mismatch: entered '{entity_code}', input holds '{entered_code}'")
        #legal entity name
        self.page.get_by_role("textbox", name="Legal entity name").fill(data["entity_name"])
        #short name
        self.page.get_by_role("textbox", name="Short name").fill(data["short_name"])
        #registration number
        self.page.get_by_role("textbox", name="Registration number").fill(data["registration_number"])
        #
        section = self.page.locator(".form-section").filter(has=self.page.get_by_role(
                "heading", name="Basic information"))

        section.get_by_role("combobox", name="Country").select_option(data["country"])

        return entity_code

    def fill_contact_information(self, data):
        #official email
        self.page.get_by_role("textbox", name="Official email").fill(data["official_email"])
        #offical phone countru code
        self.page.get_by_role("combobox",name="Official phone country code").select_option(data["phone_country"])
        #official phone
        self.page.get_by_role("textbox", name="Official phone").fill(data["official_phone"])
        #HR email
        self.page.get_by_role("textbox", name="HR email").fill(data["hr_email"])
        #payrollEmail
        self.page.get_by_role("textbox", name="Payroll email").fill(data["payroll_email"])

    def fill_registered_address(self, data):
        #address line 1
        self.page.get_by_role("textbox", name="Address line 1").fill(data["address_line1"])
        #address line 2
        self.page.get_by_role("textbox", name="Address line 2").fill(data["address_line2"])
        #registered address
        section = self.page.locator( ".form-section").filter(has=self.page.get_by_role(
            "heading", name="Registered address"))
        section.get_by_role("combobox", name="Country").select_option(data["country"])
        #state province
        self.page.get_by_role("textbox", name="State / Province").fill(data["state"])
        #city
        self.page.get_by_role("textbox", name="City", exact=True).fill(data["city"])
        #postal zip code
        self.page.get_by_role("textbox", name="Postal / ZIP code").fill(data["postal_code"])
        #district
        self.page.get_by_role("textbox", name="District").fill(data["district"])
        #landmark
        self.page.get_by_role("textbox", name="Landmark").fill(data["landmark"])

    def fill_corporate_address(self, data):
        self.page.get_by_role("switch", name="Same as registered address").set_checked(
            data["same_as_registered"])

    def set_default_entity(self, value):
        self.page.get_by_role("switch", name="Make this the default"
        ).set_checked(value)

    def select_effective_date(self):
        # Open Effective From calendar
        trigger = self.page.locator(".field").filter(has=self.page.locator("label", has_text="Effective from")).locator(
            "button.date-field__trigger")
        # Trigger sits below the fold on a 720px-high viewport; bring it into view first
        trigger.scroll_into_view_if_needed()
        trigger.click()

        # Select current date using Today button
        self.page.get_by_role("dialog", name="Effective from calendar").get_by_role(
            "button", name="Today").click()

    def submit_entity(self):
        self.page.get_by_role("button", name="Create legal entity"
        ).click()

    def verify_form_visible(self):
        expect(self.page.get_by_role("button", name="Create legal entity")).to_be_visible()

