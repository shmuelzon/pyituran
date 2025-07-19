from datetime import datetime
import pytest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from pyituran import cmdline

from .mock_response import (
    DIAGNOSTIC_VALUE_RESPONSE,
    GET_ELECTRIC_DATA_RESPONSE,
    MockResponse,
    REQUEST_OTP_RESPONSE,
    REQUEST_OTP_RESPONSE_UNKNOWN_ERROR,
    REQUEST_OTP_RESPONSE_WRONG_CREDENTIALS,
    AUTHENTICATE_RESPONSE,
    AUTHENTICATE_RESPONSE_WITH_UNKNOWN_ERROR,
    AUTHENTICATE_RESPONSE_WITH_WRONG_OTP,
    GET_VEHICLES_RESPONSE,
    GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS,
    VEHICLE_RESPONSE,
)

ID_NUMBER = "123456789"
PHONE_NUMBER = "0501234567"
PLATFORM_ID = "123456"
MOBILE_ID = "1234567890abcdef"
OTP_CODE = "123456"

LICENSE_PLATE = "12345678"
LATITUTE = 25.0
LONGITUDE = -71.0
SPEED = 50
LAST_MILEAGE = 2000.5
HEADING = 150
ADDRESS = "Bermuda Triangle"
LAST_UPDATE = datetime(2024, 1, 2, 8, 30, tzinfo=ZoneInfo("Asia/Jerusalem"))
BATTERY_VOLTAGE = 12.3
MODEL = "Fake Model"
MAKE = "Fake Make"
ITURAN4ALL = "Ituran4All"
APP4ALLEV = "Ituran app4AllEV"
BATTERY_PERCENT = 42
BATTERY_RANGE = 456


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
        platform_id=PLATFORM_ID,
        license_plate=LICENSE_PLATE,
        latitude=LATITUTE,
        longitude=LONGITUDE,
        speed=SPEED,
        last_mileage=LAST_MILEAGE,
        heading=HEADING,
        address=ADDRESS,
        last_update=LAST_UPDATE.replace(tzinfo=None).isoformat(),
        battery_voltage=BATTERY_VOLTAGE,
        model=MODEL,
        make=MAKE,
        product_name=ITURAN4ALL,
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


def test_failed_to_authenticated_unknown_error() -> None:
    not_auth_response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS.format(id_number=ID_NUMBER),
    )
    wrong_credentials_response = MockResponse(
        200,
        REQUEST_OTP_RESPONSE_UNKNOWN_ERROR,
    )

    with patch(
        "aiohttp.ClientSession.post",
        side_effect=[not_auth_response, wrong_credentials_response],
    ):
        with patch("builtins.input", return_value="y"):
            cmdline.main(["--id-number", ID_NUMBER, "--mobile-id", MOBILE_ID])


def test_failed_to_authenticated_wrong_credentials() -> None:
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
    otp_unknown_error = MockResponse(
        200,
        AUTHENTICATE_RESPONSE_WITH_UNKNOWN_ERROR,
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
            otp_unknown_error,
            correct_otp,
            vehicles,
        ],
    ):
        with patch(
            "builtins.input",
            side_effect=["y", OTP_CODE + "1", OTP_CODE, OTP_CODE],
        ):
            cmdline.main(["--id-number", ID_NUMBER, "--mobile-id", MOBILE_ID])


def test_output() -> None:
    vehicle_xml = VEHICLE_RESPONSE.format(
        platform_id=PLATFORM_ID,
        license_plate=LICENSE_PLATE,
        latitude=LATITUTE,
        longitude=LONGITUDE,
        speed=SPEED,
        last_mileage=LAST_MILEAGE,
        heading=HEADING,
        address=ADDRESS,
        last_update=LAST_UPDATE.replace(tzinfo=None).isoformat(),
        battery_voltage=BATTERY_VOLTAGE,
        model=MODEL,
        make=MAKE,
        product_name=APP4ALLEV,
    )
    electric_data_xml = (
        DIAGNOSTIC_VALUE_RESPONSE.format(
            label="Electric Data - Charging AC Mode - 2227",
            value=0,
            update_time=LAST_UPDATE.replace(tzinfo=None).isoformat(),
        )
        + DIAGNOSTIC_VALUE_RESPONSE.format(
            label="Electric Data - Battery Status Of Charge - 2334",
            value=BATTERY_PERCENT,
            update_time=LAST_UPDATE.replace(tzinfo=None).isoformat(),
        )
        + DIAGNOSTIC_VALUE_RESPONSE.format(
            label="Electric Data - Vehicle Range Of Battery - 2229",
            value=BATTERY_RANGE,
            update_time=LAST_UPDATE.replace(tzinfo=None).isoformat(),
        )
    )

    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE.format(
            id_number=ID_NUMBER, vehicles=vehicle_xml
        ),
    )
    electric_data_response = MockResponse(
        200,
        GET_ELECTRIC_DATA_RESPONSE.format(
            diagnostic_values=electric_data_xml,
        ),
    )

    with patch(
        "aiohttp.ClientSession.post",
        side_effect=[response, response, response, electric_data_response],
    ), patch("builtins.print") as print_mocked:
        cmdline.main(["--id-number", ID_NUMBER, "--mobile-id", MOBILE_ID])
        assert (
            print_mocked.call_args_list[0][0][0]
            == f"License plate: {LICENSE_PLATE}:\n"
            + f"\tMake: {MAKE}\n"
            + f"\tModel: {MODEL}\n"
            + f"\tLocation: ({LATITUTE}, {LONGITUDE})\n"
            + f"\tAddress: {ADDRESS}\n"
            + f"\tHeading: {HEADING}\n"
            + f"\tSpeed: {SPEED}\n"
            + f"\tMileage: {LAST_MILEAGE}\n"
            + f"\tBattery voltage: {BATTERY_VOLTAGE}\n"
            + f"\tLast update: {LAST_UPDATE}\n"
        )
        assert (
            print_mocked.call_args_list[1][0][0]
            == "\tIs charging: False\n"
            + f"\tBattery level: {BATTERY_PERCENT}\n"
            + f"\tBattery range: {BATTERY_RANGE}\n"
        )
