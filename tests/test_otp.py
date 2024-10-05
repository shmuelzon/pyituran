import pytest
import string
from unittest.mock import patch

from .mock_response import (
    MockResponse,
    AUTHENTICATE_RESPONSE,
    AUTHENTICATE_RESPONSE_WITH_WRONG_OTP,
    REQUEST_OTP_RESPONSE,
    REQUEST_OTP_RESPONSE_WRONG_CREDENTIALS,
)
from pyituran import Ituran

ID_NUMBER = "123456789"
PHONE_NUMBER = "0501234567"
MOBILE_ID = "1234567890abcdef"


@pytest.mark.asyncio
async def test_mobile_id_generated_if_not_provided() -> None:
    ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
    assert len(ituran.mobile_id) == 16
    assert all(c in string.hexdigits for c in ituran.mobile_id)


@pytest.mark.asyncio
async def test_mobile_id_provided() -> None:
    ituran = Ituran(ID_NUMBER, PHONE_NUMBER, MOBILE_ID)
    assert ituran.mobile_id == MOBILE_ID


@pytest.mark.asyncio
async def test_request_otp_with_bad_credentials() -> None:
    response = MockResponse(
        200,
        REQUEST_OTP_RESPONSE_WRONG_CREDENTIALS,
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        with pytest.raises(Exception):
            await ituran.request_otp()


@pytest.mark.asyncio
async def test_request_otp() -> None:
    response = MockResponse(
        200,
        REQUEST_OTP_RESPONSE.format(id_number=ID_NUMBER),
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        assert await ituran.request_otp() is True


@pytest.mark.asyncio
async def test_authenticate_with_wrong_otp() -> None:
    response = MockResponse(
        200,
        AUTHENTICATE_RESPONSE_WITH_WRONG_OTP,
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        with pytest.raises(Exception):
            await ituran.authenticate("123456")


@pytest.mark.asyncio
async def test_authenticate() -> None:
    response = MockResponse(
        200,
        AUTHENTICATE_RESPONSE,
    )

    with patch("aiohttp.ClientSession.post", return_value=response):
        ituran = Ituran(ID_NUMBER, PHONE_NUMBER)
        assert await ituran.authenticate("123456") is True
