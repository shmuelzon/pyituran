import pytest
from unittest.mock import patch

from pyituran import Ituran

from .mock_response import (
    MockResponse,
    GET_VEHICLES_RESPONSE,
    GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS,
)

ID_NUMBER = "123456789"


@pytest.mark.asyncio
async def test_not_authenticated() -> None:
    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS.format(id_number=ID_NUMBER),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, "0501234567", "deadbeef")
        assert await ituran.is_authenticated() is False


@pytest.mark.asyncio
async def test_is_authenticated() -> None:
    response = MockResponse(
        200,
        GET_VEHICLES_RESPONSE.format(id_number=ID_NUMBER, vehicles=""),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, "0501234567", "deadbeef")
        assert await ituran.is_authenticated() is True


@pytest.mark.asyncio
async def test_invalid_status() -> None:
    response = MockResponse(
        404,
        GET_VEHICLES_RESPONSE.format(id_number=ID_NUMBER, vehicles=""),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, "0501234567", "deadbeef")
        with pytest.raises(Exception):
            await ituran.is_authenticated()
