from collections import defaultdict
from aiohttp import FormData
import pytest
from unittest.mock import patch

from .mock_response import (
    MockResponse,
    AUTHENTICATE_RESPONSE,
    GET_ELECTRIC_DATA_RESPONSE,
    GET_VEHICLES_RESPONSE,
    REQUEST_OTP_RESPONSE,
    VEHICLE_RESPONSE,
)
from pyituran import Ituran

ID_NUMBER = "123456789"
PHONE_NUMBER = "0501234567"
MOBILE_ID = "1234567890abcdef"
OTP_CODE = "123456"
PLATFORM_ID = "123456"


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


@pytest.mark.asyncio
async def test_get_electric_vehicles_request() -> None:
    vehicle_xml = VEHICLE_RESPONSE.format_map(
        defaultdict(
            lambda: "0",
            platform_id=PLATFORM_ID,
            product_name="Ituran app4AllEV",
            last_update="2024-01-01T00:00:00",
        )
    )
    vehicles_response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE.format(
            id_number=ID_NUMBER, vehicles=vehicle_xml
        ),
    )
    electric_data_response = MockResponse(
        200,
        GET_ELECTRIC_DATA_RESPONSE.format(diagnostic_values=""),
    )

    with patch(
        "aiohttp.ClientSession.post",
        side_effect=[vehicles_response, electric_data_response],
    ) as post_mocked:
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER, MOBILE_ID)
        await ituran.get_vehicles()
        expected_vehicle_data = FormData(
            {
                "UserName": ID_NUMBER,
                "GetAddress": True,
                "Password": MOBILE_ID,
            }
        )
        expected_electric_data = FormData(
            {
                "UserName": ID_NUMBER,
                "PlatformId": PLATFORM_ID,
                "Password": MOBILE_ID,
            }
        )
        sent_data: FormData = post_mocked.call_args_list[0][1]["data"]
        assert expected_vehicle_data().decode() == sent_data().decode()
        sent_data2: FormData = post_mocked.call_args_list[1][1]["data"]
        assert expected_electric_data().decode() == sent_data2().decode()
