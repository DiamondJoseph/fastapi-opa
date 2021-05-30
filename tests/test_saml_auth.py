from unittest.mock import Mock

import pytest
from mock import patch
from starlette.responses import RedirectResponse

from fastapi_opa.auth.auth_saml import SAMLAuthentication
from fastapi_opa.auth.auth_saml import SAMLConfig


@pytest.mark.asyncio
async def test_single_sign_on():
    saml_conf = SAMLConfig(settings_directory="./tests/test_data/saml")
    saml_auth = SAMLAuthentication(saml_conf)

    saml_auth_mock = Mock()
    saml_auth_mock.login.return_value = "http://idp.com/cryptic-stuff"
    response = await saml_auth.single_sign_on(saml_auth_mock)

    assert isinstance(response, RedirectResponse)
    assert response.headers.get("location") == "http://idp.com/cryptic-stuff"


@pytest.mark.asyncio
@patch("fastapi_opa.auth.auth_saml.OneLogin_Saml2_Utils")
async def test_assertion_consumer_service(saml_util_mock):
    saml_util_mock.get_self_url.return_value = "http://sp.com"
    saml_conf = SAMLConfig(settings_directory="./tests/test_data/saml")
    saml_auth = SAMLAuthentication(saml_conf)
    saml_auth_mock = Mock()
    saml_auth_mock.get_errors.return_value = []
    saml_auth_mock.get_attributes.return_value = {
        "Role": [
            "default-roles-example-realm",
            "uma_authorization",
            "view-profile",
            "manage-account",
            "manage-account-links",
            "offline_access",
        ]
    }
    saml_auth_mock.get_nameid.return_value = "alice"
    saml_auth_mock.get_nameid_format.return_value = (
        "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
    )
    saml_auth_mock.get_nameid_nq.return_value = None
    saml_auth_mock.get_nameid_spnq.return_value = None
    saml_auth_mock.get_session_index.return_value = "8167416b-6a10-4a4c-889c-7574074e3fc5::f1eaf88b-2bb9-4d2e-8d3d-39587ba1ef37"  # noqa

    response = await saml_auth.assertion_consumer_service(
        saml_auth_mock, {"post_data": []}
    )
    expected = {
        "samlUserdata": {
            "Role": [
                "default-roles-example-realm",
                "uma_authorization",
                "view-profile",
                "manage-account",
                "manage-account-links",
                "offline_access",
            ]
        },
        "samlNameId": "alice",
        "samlNameIdFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",  # noqa
        "samlNameIdNameQualifier": None,
        "samlNameIdSPNameQualifier": None,
        "samlSessionIndex": "8167416b-6a10-4a4c-889c-7574074e3fc5::f1eaf88b-2bb9-4d2e-8d3d-39587ba1ef37",  # noqa
    }
    assert expected == response
