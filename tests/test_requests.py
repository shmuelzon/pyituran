from aiohttp import FormData
import pytest
from unittest.mock import patch

from .mock_response import (
    MockResponse,
    AUTHENTICATE_RESPONSE,
    GET_VEHICLES_RESPONSE,
    REQUEST_OTP_RESPONSE,
)
from pyituran import Ituran

ID_NUMBER = "123456789"
PHONE_NUMBER = "0501234567"
MOBILE_ID = "1234567890abcdef"
OTP_CODE = "123456"


@pytest.mark.asyncio
async def test_otp_request() -> None:
    response = MockResponse(
        200,
        REQUEST_OTP_RESPONSE.format(id_number=ID_NUMBER),
    )

    with patch(
        "aiohttp.ClientSession.post", return_value=response
    ) as post_mocked:
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER, MOBILE_ID)
        await ituran.request_otp()
        expected_data = FormData(
            {
                "UserName": ID_NUMBER,
                "SiebelPassword": PHONE_NUMBER,
                "AppId": 49,
                "OSType": "Android",
            }
        )
        sent_data: FormData = post_mocked.call_args[1]["data"]
        assert expected_data().decode() == sent_data().decode()


@pytest.mark.asyncio
async def test_authentication_request() -> None:
    response = MockResponse(
        200,
        AUTHENTICATE_RESPONSE,
    )

    with patch(
        "aiohttp.ClientSession.post", return_value=response
    ) as post_mocked:
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER, MOBILE_ID)
        await ituran.authenticate(OTP_CODE)
        expected_data = FormData(
            {
                "UserName": ID_NUMBER,
                "SiebelPassword": PHONE_NUMBER,
                "OTPcode": OTP_CODE,
                "AppId": 49,
                "MobileId": MOBILE_ID,
            }
        )
        sent_data: FormData = post_mocked.call_args[1]["data"]
        assert expected_data().decode() == sent_data().decode()


@pytest.mark.asyncio
async def test_get_vehicles_request() -> None:
    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE.format(id_number=ID_NUMBER, vehicles=""),
    )

    with patch(
        "aiohttp.ClientSession.post", return_value=response
    ) as post_mocked:
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER, MOBILE_ID)
        await ituran.get_vehicles()
        expected_data = FormData(
            {
                "UserName": ID_NUMBER,
                "GetAddress": True,
                "Password": MOBILE_ID,
            }
        )
        sent_data: FormData = post_mocked.call_args[1]["data"]
        assert expected_data().decode() == sent_data().decode()
