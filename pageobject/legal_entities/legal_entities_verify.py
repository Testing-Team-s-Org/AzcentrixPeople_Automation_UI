
import re
from datetime import datetime
from playwright.sync_api import expect

from pageobject.legal_entities.legal_entities import LegalEntities


class LegalEntitiesVerify(LegalEntities):

    # ----------------------------------------
    # Complete Legal Entity Verification
    # ----------------------------------------

    def verify_legal_entity(self, data):

        self.verify_entity_header(data)
        self.verify_entity_overview(data)
        self.verify_entity_address(data)
        self.add_statutory_registration(data)
        self.verify_effective_information(data)
        self.verify_entity_activity()

    # ----------------------------------------
    # Common Tab Navigation
    # ----------------------------------------

    def click_tab(self, tab_name):

        tab = self.page.get_by_role("tab", name=tab_name, exact=True)
        tab.click()
        expect(tab).to_have_attribute("aria-selected", "true")

    # ----------------------------------------
    # Header Verification
    # ----------------------------------------

    def verify_entity_header(self, data):

        basic = data["basic_information"]

        header = self.page.locator(".record-header__identity")

        expect(header.locator(".record-header__title")).to_have_text(basic["entity_name"])

        expect(header.locator(".record-header__code")).to_have_text(basic["entity_code"])

        expect(header.locator(".status-badge")).to_have_text("Active")

    # ----------------------------------------
    # Reusable Detail Field Assertion
    # ----------------------------------------

    def verify_detail_field(self, section, label, expected):

        field = section.locator(".detail-tiles > div").filter(
            has=self.page.locator("dt", has_text=label))

        expect(field.locator("dd")).to_have_text(str(expected))

    # ----------------------------------------
    # Overview Verification
    # ----------------------------------------

    def verify_entity_overview(self, data):

        self.click_tab("Overview")

        basic = data["basic_information"]
        contact = data["contact_information"]

        overview = self.page.locator("section.setup-section").filter(has=self.page.get_by_role(
                "heading",name="Overview",exact=True))

        expect(overview).to_be_visible()

        self.verify_detail_field(overview,
            "Entity code",
            basic["entity_code"]
        )

        self.verify_detail_field(
            overview,
            "Legal entity name",
            basic["entity_name"]
        )

        self.verify_detail_field(
            overview,
            "Short name",
            basic["short_name"] or "—"
        )

        self.verify_detail_field(
            overview,
            "Registration number",
            basic["registration_number"]
        )

        country_names = {
            "IN": "India",
            "US": "United States",
            "GB": "United Kingdom",
            "AE": "United Arab Emirates",
            "SG": "Singapore"
        }

        self.verify_detail_field(
            overview,
            "Country",
            country_names.get(
                basic["country"],
                basic["country"]
            )
        )

        self.verify_detail_field(
            overview,
            "Currency",
            basic["currency"]
        )

        self.verify_detail_field(
            overview,
            "Official email",
            contact["official_email"]
        )

        phone_codes = {
            "IN": "+91",
            "US": "+1",
            "GB": "+44",
            "AE": "+971",
            "SG": "+65"
        }

        phone_number = "".join(
            char for char in contact["official_phone"]
            if char.isdigit()
        )

        expected_phone = (
            phone_codes.get(
                contact["phone_country"], ""
            ) + phone_number
        )

        self.verify_detail_field(
            overview,
            "Official phone",
            expected_phone
        )

        self.verify_detail_field(
            overview,
            "HR email",
            contact["hr_email"]
        )

        self.verify_detail_field(
            overview,
            "Payroll email",
            contact["payroll_email"]
        )

        print("Overview verification passed")

    # ----------------------------------------
    # Address Verification
    # ----------------------------------------

    def verify_entity_address(self, data):

        self.click_tab("Address")

        address = data["registered_address"]

        registered = self.page.locator(".address-card").filter(has=self.page.get_by_role(
                "heading",name="Registered address",exact=True))

        expect(registered).to_be_visible()

        # Address line 1 and 2
        address_lines = [
            address["address_line1"],
            address.get("address_line2", "")
        ]

        expected_street = ", ".join(
            value for value in address_lines
            if value
        )

        expect(registered.locator(".address-card__street")).to_have_text(expected_street)

        # Landmark (span index 1; index 0 is the street line)
        expect(registered.locator(".address-card__body > span").nth(1)).to_have_text(address["landmark"])

        # City and District (rendered as "City, District")
        expected_city_district = f'{address["city"]}, {address["district"]}'

        expect(registered.locator(".address-card__body > span").nth(2)).to_have_text(expected_city_district)

        # State and Postal Code
        expected_state_postal = (f'{address["state"]} - 'f'{address["postal_code"]}')

        expect(registered.locator(".address-card__body > span").nth(3)).to_have_text(expected_state_postal)

        # Country
        country_names = {
            "IN": "India",
            "US": "United States",
            "GB": "United Kingdom",
            "AE": "United Arab Emirates",
            "SG": "Singapore"
        }

        expected_country = country_names.get(
            address["country"],
            address["country"]
        )

        expect(
            registered.locator(
                ".address-card__body > span"
            ).nth(4)
        ).to_have_text(expected_country)

        # Corporate Address
        corporate = self.page.locator(".address-card").filter(has=self.page.get_by_role("heading",
                name="Corporate address",exact=True))

        expect(corporate).to_be_visible()

        if data["corporate_address"]["same_as_registered"]:

            expect(corporate.locator(".address-card__same")).to_have_text("Same as registered address")

        print("Address verification passed")

    # ----------------------------------------
    # Statutory Registration - PAN
    # ----------------------------------------

    def add_statutory_registration(self, data):

        self.click_tab("Statutory registrations")

        registration = data["statutory_registration"]

        form = self.page.locator("div.card").filter(has=self.page.get_by_role(
                "heading",name="Add registration",exact=True))

        expect(form).to_be_visible()

        # Select PAN
        form.get_by_role("combobox", name="Type").select_option(registration["type"])

        # Fill PAN Number
        form.get_by_role( "textbox", name="Number").fill(registration["number"])

        # Open Effective From Calendar
        effective_from = form.locator('button.date-field__trigger[aria-required="true"]')

        effective_from.click()

        # Select Current Date
        calendar = self.page.get_by_role("dialog", name=re.compile("calendar", re.IGNORECASE))

        expect(calendar).to_be_visible()

        calendar.get_by_role("button", name="Today",exact=True).click()

        # Add Registration
        form.get_by_role("button", name="Add registration",exact=True).click()

        print("PAN registration submitted")

    # ----------------------------------------
    # Effective Information Verification
    # ----------------------------------------

    def verify_effective_information(self, data):

        self.click_tab("Effective information")

        section = self.page.locator("section.setup-section").filter(has=self.page.get_by_role(
                "heading",name="Effective information",exact=True))

        expect(section).to_be_visible()

        # Effective From - selected current date
        expected_date = datetime.now().strftime("%d %b %Y").lstrip("0")

        self.verify_detail_field(section,"Effective from",expected_date)

        # Effective To
        self.verify_detail_field(section,"Effective to","Open-ended")

        # Status
        self.verify_detail_field(section,"Status","Active")

        # Deactivated
        self.verify_detail_field(section,"Deactivated","—")

        # Created and Updated should have values
        for label in ["Created", "Last updated"]:

            field = section.locator(".detail-tiles > div").filter(
                has=self.page.locator("dt", has_text=label))

            value = field.locator("dd")

            expect(value).to_be_visible()

            expect(value).not_to_be_empty()

        print("Effective information verification passed")

    # ----------------------------------------
    # Activity Verification
    # ----------------------------------------

    def verify_entity_activity(self):

        self.click_tab("Activity")

        section = self.page.locator("section.setup-section").filter(
            has=self.page.get_by_role("heading",name="Activity",exact=True))

        expect(section).to_be_visible()

        activity_items = section.locator(
            ".activity__item"
        )

        expect(activity_items.first).to_be_visible()

        # Find Legal Entity Created activity
        created_activity = activity_items.filter(has=self.page.locator(
            ".activity__title", has_text="Legal entity created"))

        expect(created_activity).to_have_count(1)

        expect(created_activity.locator(
            ".activity__title")).to_have_text("Legal entity created")

        # Timestamp should be present
        timestamp = created_activity.locator(".activity__time")

        expect(timestamp).to_be_visible()
        expect(timestamp).not_to_be_empty()

        expect(timestamp).to_have_attribute("datetime", re.compile(r".+"))

        # Actor should be present
        actor = created_activity.locator(".activity__actor strong")

        expect(actor).to_be_visible()
        expect(actor).not_to_be_empty()

        print("Activity verification passed")
