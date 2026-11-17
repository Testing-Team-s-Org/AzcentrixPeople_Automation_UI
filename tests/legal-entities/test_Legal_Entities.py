import copy
import json

import pytest

from pageobject.login import LoginPage
from pageobject.navigation.navigation_page import NavigationPage
from pageobject.legal_entities.legal_entities import LegalEntities
from pageobject.legal_entities.legal_entities_verify import LegalEntitiesVerify


@pytest.mark.smoke
@pytest.mark.regression
def test_create_legal_entity(browserInstance, credentials, data_dir):

    # Test data comes from the data/ folder via the data_dir fixture
    with open(data_dir / "Legal_entities.json", "r", encoding="utf-8") as f:
        entity_data = json.load(f)["legal_entities"][0]

    # Step 1 - Login (credentials from .env)
    login = LoginPage(browserInstance)
    login.signIn(credentials["companyCode"], credentials["userName"], credentials["password"])

    # Step 2 - Navigate
    navi = NavigationPage(browserInstance)
    navi.legalentities()

    # Step 3 - Create Legal Entity
    legal_entity = LegalEntities(browserInstance)

    # fill_legal_entity() opens the form itself (add_Entity), so don't click it again here.
    # This method must submit the form and return entered code
    entered_code = legal_entity.fill_legal_entity(entity_data)

    print("entered_code", entered_code)

    assert entered_code, "Legal entity code was not returned"

    assert entered_code.startswith(
        entity_data["basic_information"]["entity_code"]
    ), "Generated entity code does not match expected prefix"

    # Step 4 - Prepare Expected Data
    expected_data = copy.deepcopy(entity_data)

    expected_data["basic_information"]["entity_code"] = entered_code

    # Step 5 - Verify Created Legal Entity
    legal_entity_verify = LegalEntitiesVerify(browserInstance)

    legal_entity_verify.verify_legal_entity(expected_data)
    print("Legal Entity created and verified successfully")
