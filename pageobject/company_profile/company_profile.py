from datetime import datetime

from playwright.sync_api import Page, expect


class CompanyProfile:
    """Page object for Organization > Company Setup > Company Profile."""

    def __init__(self, page: Page):
        self.page = page

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    def _section(self, heading):
        """Scope locators to one form section (needed for the repeated address labels)."""
        # Find the section whose heading matches, so "Country" or "City" is searched only inside it
        return self.page.locator(".form-section").filter(
            has=self.page.get_by_role("heading", name=heading))

    def _fill(self, locator, value):
        """Overwrite whatever is pre-filled in a text box, then read it back."""
        # fill() clears the old value and types the new one
        locator.fill(value)
        # Assert the text box now holds exactly what we typed
        expect(locator).to_have_value(value)

    def _select(self, locator, value):
        """Choose a dropdown option by its value, then read it back."""
        # Pick the option using its value attribute (for example IN, INR, en)
        locator.select_option(value)
        # Assert the dropdown now shows the option we picked
        expect(locator).to_have_value(value)

    def _check(self, locator, value):
        """Assert a text box or dropdown holds the expected value (retries until it does)."""
        # Compare the value on the page with the value from the JSON
        expect(locator).to_have_value(value)

    # ----------------------------------------
    # Page checks (before filling)
    # ----------------------------------------

    def verify_page_loaded(self):
        """The form is on screen once the 'Basic information' heading is visible."""
        # Wait for the first section heading, which proves the form has loaded
        expect(self.page.get_by_role("heading", name="Basic information")).to_be_visible()

    def verify_company_code_disabled(self):
        """Company code is managed by the provider, so its input must be disabled."""
        # The input has an aria-label, so find it through its visible <label> text
        code_input = self.page.locator(".field").filter(
            has=self.page.locator("label", has_text="Company code")).locator("input")
        # Assert the field cannot be edited
        expect(code_input).to_be_disabled()

    # ----------------------------------------
    # Fill the whole profile
    # ----------------------------------------

    def fill_company_profile(self, data):
        self.verify_page_loaded()
        self.verify_company_code_disabled()
        """Fill every section from the JSON data, in page order."""
        # Filling the basic information
        self.fill_basic_information(data["basic_information"])
        # Filling the localization details
        self.fill_localization(data["localization"])
        # Filling the contact information
        self.fill_contact_information(data["contact_information"])
        # Filling the registered address
        self.fill_registered_address(data["registered_address"])
        # Setting the toggle and filling the corporate address
        self.fill_corporate_address(data["corporate_address"])

    def fill_basic_information(self, data):
        """Names, company type, industry, registration number, incorporation date, website."""
        # Work only inside the Basic information section
        s = self._section("Basic information")

        # Company name (required)
        self._fill(s.get_by_label("Company name"), data["company_name"])
        # Display name
        self._fill(s.get_by_label("Display name"), data["display_name"])
        # Legal / registered name (required)
        self._fill(s.get_by_label("Legal / registered name"), data["legal_name"])
        # Company type dropdown
        self._select(s.get_by_label("Company type"), data["company_type"])
        # Industry dropdown
        self._select(s.get_by_label("Industry"), data["industry"])
        # Registration number
        self._fill(s.get_by_label("Registration number"), data["registration_number"])
        # Incorporation date, chosen from the calendar
        self.select_incorporation_date(data["incorporation_date"])
        # Website
        self._fill(s.get_by_label("Website"), data["website"])

    def select_incorporation_date(self, value):
        """Pick today's date from the calendar (future dates are disabled)."""
        assert value == "today", "Only 'today' is supported (future dates are disabled)"

        # Find the date button that belongs to the "Incorporation date" label
        trigger = self.page.locator(".field").filter(
            has=self.page.locator("label", has_text="Incorporation date")
        ).locator("button.date-field__trigger")
        # Open the calendar
        trigger.click()

        # Click the Today button inside the Incorporation date calendar
        self.page.get_by_role("dialog", name="Incorporation date calendar").get_by_role(
            "button", name="Today", exact=True).click()

        # The empty placeholder style goes away once a date is chosen
        expect(trigger).not_to_have_class(r"/date-field__trigger--empty/")

    def fill_localization(self, data):
        """Country, currency, language, timezone, date and number formats, financial year start."""
        # Work only inside the Localization section
        s = self._section("Localization")

        # Country (required)
        self._select(s.get_by_label("Country"), data["country"])
        # Default currency (required)
        self._select(s.get_by_label("Default currency"), data["currency"])
        # Default language (required)
        self._select(s.get_by_label("Default language"), data["language"])
        # Timezone (required)
        self._select(s.get_by_label("Timezone"), data["timezone"])
        # Date format (required)
        self._select(s.get_by_label("Date format"), data["date_format"])
        # Number format (required)
        self._select(s.get_by_label("Number format"), data["number_format"])
        # Financial year start month (required)
        self._select(s.get_by_label("Financial year starts (month)"), data["financial_year_month"])
        # Financial year start day
        self._select(s.get_by_label("Financial year starts (day)"), data["financial_year_day"])

    def fill_contact_information(self, data):
        """Official, alternate, HR, payroll and support contact details."""
        # Work only inside the Contact information section
        s = self._section("Contact information")

        # Official email
        self._fill(s.get_by_label("Official email"), data["official_email"])
        # Official phone
        self._fill(s.get_by_label("Official phone"), data["official_phone"])
        # Alternate phone
        self._fill(s.get_by_label("Alternate phone"), data["alternate_phone"])
        # HR email
        self._fill(s.get_by_label("HR email"), data["hr_email"])
        # Payroll email
        self._fill(s.get_by_label("Payroll email"), data["payroll_email"])
        # Support email
        self._fill(s.get_by_label("Support email"), data["support_email"])

    # ----------------------------------------
    # Addresses (same fields, different section)
    # ----------------------------------------

    def _fill_address(self, heading, data):
        """Fill one address block; used for both registered and corporate addresses."""
        # Work only inside the address section named by heading
        s = self._section(heading)

        # Address line 1 (required)
        self._fill(s.get_by_label("Address line 1"), data["address_line1"])
        # Address line 2
        self._fill(s.get_by_label("Address line 2"), data["address_line2"])
        # Country dropdown (required)
        self._select(s.get_by_label("Country"), data["country"])
        # State / Province (required)
        self._fill(s.get_by_label("State / Province"), data["state"])
        # City (required); exact=True because the Country dropdown also contains "City" (Vatican City)
        self._fill(s.get_by_role("textbox", name="City", exact=True), data["city"])
        # Postal / ZIP code (required)
        self._fill(s.get_by_label("Postal / ZIP code"), data["postal_code"])
        # District
        self._fill(s.get_by_label("District"), data["district"])
        # Landmark
        self._fill(s.get_by_label("Landmark"), data["landmark"])

    def fill_registered_address(self, data):
        """Fill the registered address block."""
        self._fill_address("Registered address", data)

    def fill_corporate_address(self, data):
        """Set the 'Same as registered address' toggle; if off, fill the corporate fields."""
        # The real checkbox and the clickable switch label
        toggle = self.page.get_by_role("switch", name="Same as registered address")
        switch = self.page.locator("label.switch").filter(has_text="Same as registered address")

        # Centre it on screen so the sticky Save bar does not cover it
        switch.evaluate("el => el.scrollIntoView({block: 'center'})")

        # Click only when the current state differs from what we want
        if toggle.is_checked() != data["same_as_registered"]:
            switch.click()

        if data["same_as_registered"]:
            # Toggle on: assert it is on, nothing more to fill
            expect(toggle).to_be_checked()
        else:
            # Toggle off: assert it is off, then fill the corporate fields that appear
            expect(toggle).not_to_be_checked()
            self._fill_address("Corporate / communication address", data)

    # ----------------------------------------
    # Save and verify the save
    # ----------------------------------------

    def save_profile(self):
        """Click the sticky 'Save profile' button."""
        self.page.get_by_role("button", name="Save profile").click()

    def verify_saved(self, expected):
        """Right after saving: the success toast and the Complete badge."""
        # Assert the toast text at the top right, for example "Company profile saved."
        toast = self.page.locator(".toaster .toast__text")
        expect(toast).to_have_text(expected["toast"])

        # Assert the status badge at the top left shows "Complete"
        badge = self.page.locator(".status-strip--ok .status-badge--ok")
        expect(badge).to_be_visible()
        expect(badge).to_have_text(expected["status_badge"])

    # ----------------------------------------
    # Verify the saved data after a reload
    # ----------------------------------------

    def verify_saved_profile(self, data):
        """Reload the page so the data comes from the server, then compare every field."""
        # Reload so the page shows what the server stored, not what is still in the browser
        self.page.reload()
        self.verify_page_loaded()

        # Asserting the basic information by comparing with the JSON
        self.verify_basic_information(data["basic_information"], data["localization"]["date_format"])
        # Asserting the localization details by comparing with the JSON
        self.verify_localization(data["localization"])
        # Asserting the contact information by comparing with the JSON
        self.verify_contact_information(data["contact_information"])
        # Asserting the registered address by comparing with the JSON
        self.verify_address("Registered address", data["registered_address"])
        # Asserting the toggle state and the corporate address by comparing with the JSON
        self.verify_corporate_address(data["corporate_address"])

    def verify_basic_information(self, data, date_format):
        """Saved names, type, industry, registration number, website and incorporation date."""
        # Work only inside the Basic information section
        s = self._section("Basic information")

        # Company name on the page must equal company_name in the JSON
        self._check(s.get_by_label("Company name"), data["company_name"])
        # Display name
        self._check(s.get_by_label("Display name"), data["display_name"])
        # Legal / registered name
        self._check(s.get_by_label("Legal / registered name"), data["legal_name"])
        # Company type
        self._check(s.get_by_label("Company type"), data["company_type"])
        # Industry
        self._check(s.get_by_label("Industry"), data["industry"])
        # Registration number
        self._check(s.get_by_label("Registration number"), data["registration_number"])
        # Website
        self._check(s.get_by_label("Website"), data["website"])
        # Incorporation date, compared with today's date in the saved date format
        self.verify_incorporation_date(data["incorporation_date"], date_format)

    def verify_incorporation_date(self, value, date_format):
        """The date button shows the saved date in the company's date format."""
        assert value == "today", "Only 'today' is supported"

        # Map the app's date format name to Python's format codes
        formats = {
            "DD-MM-YYYY": "%d-%m-%Y",
            "DD/MM/YYYY": "%d/%m/%Y",
            "YYYY-MM-DD": "%Y-%m-%d",
            "MM/DD/YYYY": "%m/%d/%Y",
            "DD.MM.YYYY": "%d.%m.%Y",
            "DD MMM YYYY": "%d %b %Y",
        }
        # Today's date written in that format, for example 19-11-2026
        expected = datetime.now().strftime(formats[date_format])

        # Assert the date button text equals the expected date
        trigger = self.page.locator(".field").filter(
            has=self.page.locator("label", has_text="Incorporation date")
        ).locator("button.date-field__trigger")
        expect(trigger).to_have_text(expected)

    def verify_localization(self, data):
        """Saved country, currency, language, timezone, formats and financial year start."""
        # Work only inside the Localization section
        s = self._section("Localization")

        # Each dropdown on the page must show the value saved in the JSON
        self._check(s.get_by_label("Country"), data["country"])
        self._check(s.get_by_label("Default currency"), data["currency"])
        self._check(s.get_by_label("Default language"), data["language"])
        self._check(s.get_by_label("Timezone"), data["timezone"])
        self._check(s.get_by_label("Date format"), data["date_format"])
        self._check(s.get_by_label("Number format"), data["number_format"])
        self._check(s.get_by_label("Financial year starts (month)"), data["financial_year_month"])
        self._check(s.get_by_label("Financial year starts (day)"), data["financial_year_day"])

    def verify_contact_information(self, data):
        """Saved emails and phone numbers."""
        # Work only inside the Contact information section
        s = self._section("Contact information")

        # Each email and phone on the page must equal the value in the JSON
        self._check(s.get_by_label("Official email"), data["official_email"])
        self._check(s.get_by_label("Official phone"), data["official_phone"])
        self._check(s.get_by_label("Alternate phone"), data["alternate_phone"])
        self._check(s.get_by_label("HR email"), data["hr_email"])
        self._check(s.get_by_label("Payroll email"), data["payroll_email"])
        self._check(s.get_by_label("Support email"), data["support_email"])

    def verify_address(self, heading, data):
        """Compare one address block with the JSON; used for registered and corporate."""
        # Work only inside the address section named by heading
        s = self._section(heading)

        # Each address field on the page must equal the value in the JSON
        self._check(s.get_by_label("Address line 1"), data["address_line1"])
        self._check(s.get_by_label("Address line 2"), data["address_line2"])
        self._check(s.get_by_label("Country"), data["country"])
        self._check(s.get_by_label("State / Province"), data["state"])
        self._check(s.get_by_role("textbox", name="City", exact=True), data["city"])
        self._check(s.get_by_label("Postal / ZIP code"), data["postal_code"])
        self._check(s.get_by_label("District"), data["district"])
        self._check(s.get_by_label("Landmark"), data["landmark"])

    def verify_corporate_address(self, data):
        """Toggle keeps its saved state; if off, the corporate fields must hold the saved values."""
        toggle = self.page.get_by_role("switch", name="Same as registered address")
        corporate = self._section("Corporate / communication address")

        if data["same_as_registered"]:
            # Toggle was saved on: it must still be on after reload
            expect(toggle).to_be_checked()
            # Toggle on: the corporate fields are hidden
            expect(corporate.get_by_label("Address line 1")).to_have_count(0)
        else:
            # Toggle was saved off: it must still be off after reload
            expect(toggle).not_to_be_checked()
            # Corporate fields are visible, so compare them with the JSON
            self.verify_address("Corporate / communication address", data)