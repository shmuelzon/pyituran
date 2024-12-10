from datetime import datetime
import pytest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from pyituran import Ituran
from pyituran.exceptions import IturanApiError, IturanAuthError

from .mock_response import (
    MockResponse,
    GET_VEHICLES_RESPONSE,
    GET_VEHICLES_RESPONSE_UNKNOWN_ERROR,
    GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS,
    VEHICLE_RESPONSE,
)

ID_NUMBER = "123456789"
PHONE_NUMBER = "0501234567"
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


@pytest.mark.asyncio
async def test_vehicle() -> None:
    vehicle_xml = VEHICLE_RESPONSE.format(
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
    )

    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE.format(
            id_number=ID_NUMBER, vehicles=vehicle_xml
        ),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        vehicles = await ituran.get_vehicles()
        assert len(vehicles) == 1
        vehicle = vehicles[0]
        assert vehicle.license_plate == LICENSE_PLATE
        assert vehicle.gps_coordinates == (LATITUTE, LONGITUDE)
        assert vehicle.speed == SPEED
        assert vehicle.mileage == LAST_MILEAGE
        assert vehicle.heading == HEADING
        assert vehicle.address == ADDRESS
        assert vehicle.last_update == LAST_UPDATE
        assert vehicle.battery_voltage == BATTERY_VOLTAGE
        assert vehicle.model == MODEL
        assert vehicle.make == MAKE
        assert str(vehicle) == f"{MAKE} {MODEL} @ ({LATITUTE}, {LONGITUDE})"


@pytest.mark.asyncio
async def test_vehicles_bad_response_code() -> None:
    response = MockResponse(
        400,
        GET_VEHICLES_RESPONSE.format(id_number=ID_NUMBER, vehicles=""),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        with pytest.raises(IturanApiError):
            await ituran.get_vehicles()


@pytest.mark.asyncio
async def test_vehicles_bad_response_content() -> None:
    response = MockResponse(
        200,
        "",
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        with pytest.raises(IturanApiError):
            await ituran.get_vehicles()


@pytest.mark.asyncio
async def test_vehicles_not_authenticated() -> None:
    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS.format(id_number=ID_NUMBER),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        with pytest.raises(IturanAuthError):
            await ituran.get_vehicles()


@pytest.mark.asyncio
async def test_vehicles_unknown_error() -> None:
    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE_UNKNOWN_ERROR.format(id_number=ID_NUMBER),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        with pytest.raises(IturanApiError):
            await ituran.get_vehicles()
