from datetime import datetime
import pytest
from unittest.mock import patch

from pyituran import cmdline

from .mock_response import (
    MockResponse,
    REQUEST_OTP_RESPONSE,
    REQUEST_OTP_RESPONSE_WRONG_CREDENTIALS,
    AUTHENTICATE_RESPONSE,
    AUTHENTICATE_RESPONSE_WITH_WRONG_OTP,
    GET_VEHICLES_RESPONSE,
    GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS,
    VEHICLE_RESPONSE,
)

ID_NUMBER = "123456789"
PHONE_NUMBER = "0501234567"
MOBILE_ID = "1234567890abcdef"
OTP_CODE = "123456"

LICENSE_PLATE = "12345678"
LATITUTE = 25.0
LONGITUDE = -71.0
SPEED = 50
LAST_MILEAGE = 2000.5
HEADING = 150
ADDRESS = "Bermuda Triangle"
LAST_UPDATE = datetime(2024, 1, 2, 8, 30)
MODEL = "Fake Model"
MAKE = "Fake Make"


def test_no_arguments() -> None:
    with pytest.raises(SystemExit, match="2"):
        cmdline.main()


def test_help() -> None:
    with pytest.raises(SystemExit, match="0"):
        cmdline.main(["--help"])


def test_only_id() -> None:
    with pytest.raises(SystemExit, match="2"):
        cmdline.main(["--id-number", ID_NUMBER])


def test_authenticated() -> None:
    vehicle_xml = VEHICLE_RESPONSE.format(
        license_plate=LICENSE_PLATE,
        latitude=LATITUTE,
        longitude=LONGITUDE,
        speed=SPEED,
        last_mileage=LAST_MILEAGE,
        heading=HEADING,
        address=ADDRESS,
        last_update=LAST_UPDATE.isoformat(),
        model=MODEL,
        make=MAKE,
    )

    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE.format(
            id_number=ID_NUMBER, vehicles=vehicle_xml
        ),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        cmdline.main(["--id-number", ID_NUMBER, "--mobile-id", MOBILE_ID])


def test_not_authenticated() -> None:
    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS.format(id_number=ID_NUMBER),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        with patch("builtins.input", return_value="n"):
            cmdline.main(["--id-number", ID_NUMBER, "--mobile-id", MOBILE_ID])


def test_failed_to_authenticated() -> None:
    not_auth_response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS.format(id_number=ID_NUMBER),
    )
    wrong_credentials_response = MockResponse(
        200,
        REQUEST_OTP_RESPONSE_WRONG_CREDENTIALS,
    )

    with patch(
        "aiohttp.ClientSession.post",
        side_effect=[not_auth_response, wrong_credentials_response],
    ):
        with patch("builtins.input", return_value="y"):
            cmdline.main(["--id-number", ID_NUMBER, "--mobile-id", MOBILE_ID])


def test_authenticate() -> None:
    not_auth_response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS.format(id_number=ID_NUMBER),
    )
    auth_response = MockResponse(
        200,
        REQUEST_OTP_RESPONSE.format(id_number=ID_NUMBER),
    )
    wrong_otp = MockResponse(
        200,
        AUTHENTICATE_RESPONSE_WITH_WRONG_OTP,
    )
    correct_otp = MockResponse(
        200,
        AUTHENTICATE_RESPONSE,
    )
    vehicles = MockResponse(
        200,
        GET_VEHICLES_RESPONSE.format(id_number=ID_NUMBER, vehicles=""),
    )

    with patch(
        "aiohttp.ClientSession.post",
        side_effect=[
            not_auth_response,
            auth_response,
            wrong_otp,
            correct_otp,
            vehicles,
        ],
    ):
        with patch(
            "builtins.input", side_effect=["y", OTP_CODE + "1", OTP_CODE]
        ):
            cmdline.main(["--id-number", ID_NUMBER, "--mobile-id", MOBILE_ID])
