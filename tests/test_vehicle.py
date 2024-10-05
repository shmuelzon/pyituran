from datetime import datetime
import pytest
from unittest.mock import patch

from pyituran import Ituran

from .mock_response import (
    MockResponse,
    GET_VEHICLES_RESPONSE,
    VEHICLE_RESPONSE,
)

ID_NUMBER = "123456789"
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
        ituran = Ituran(ID_NUMBER, "0501234567")
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
        assert vehicle.model == MODEL
        assert vehicle.make == MAKE
        assert str(vehicle) == f"{MAKE} {MODEL} @ ({LATITUTE}, {LONGITUDE})"
