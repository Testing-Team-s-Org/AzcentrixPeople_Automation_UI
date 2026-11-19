import json

import pytest

from pageobject.login import LoginPage
from pageobject.navigation.navigation_page import NavigationPage
from pageobject.company_profile.company_profile import CompanyProfile


@pytest.mark.smoke
@pytest.mark.regression
def test_save_company_profile(browserInstance, credentials, data_dir):

    # Load the test data from data/Company_profile.json
    with open(data_dir / "Company_profile.json", "r", encoding="utf-8") as f:
        profile_data = json.load(f)["company_profile"][0]

    # Step 1 - Login (credentials come from .env)
    login = LoginPage(browserInstance)
    login.signIn(credentials["companyCode"], credentials["userName"], credentials["password"])

    # Step 2 - Navigate: Organization > Company Setup > Company Profile
    navi = NavigationPage(browserInstance)
    navi.companyprofile()

    # Step 3 - Check the page loaded and Company code is disabled, then fill and save
    profile = CompanyProfile(browserInstance)

    profile.fill_company_profile(profile_data)
    profile.save_profile()

    # Step 4 - Assert the toast "Company profile saved." and the Complete badge
    profile.verify_saved(profile_data["expected"])

    # Step 5 - Reload and compare every saved value with the JSON
    profile.verify_saved_profile(profile_data)
    print("Company profile saved and verified successfully")