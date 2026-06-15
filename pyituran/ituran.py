"""Module client for the Ituran web service."""

import aiohttp
from aiohttp import FormData
import logging
from typing import List, Optional
import uuid
import xml.etree.ElementTree as ElementTree

from pyituran.const import (
    ACTIVATION_URL,
    ERROR_INVALID_CREDENTIALS,
    ERROR_OK,
    ERROR_WRONG_OTP_CODE,
    EV_PRODUCT_NAMES,
    ITURAN_GET_ELECTRIC_DATA_URL,
    ITURAN_GET_VEHICLES_URL,
    OTP_VERIFICATION_URL,
    XML_ERROR_DESCRIPTION,
    XML_RESPONSE_STATUS,
    XML_RETURN_CODE,
    XML_VEHICLE_DATA,
    XML_VEHICLE_PLATFORM_ID,
    XML_VEHICLE_SERVICE,
    XML_VEHICLE_PRODUCT_NAME,
    XML_VEHICLE_SERVICES,
    XML_VEHICLE_UNIT,
    XML_VEHICLE_UNITS,
    XML_VEHICLES_LIST,
)
from pyituran.exceptions import IturanApiError, IturanAuthError
from pyituran.vehicle import Vehicle

logger = logging.getLogger(__package__)


class Ituran:
    def __init__(
        self,
        id_number: str,
        phone_number: str,
        mobile_id: Optional[str] = None,
    ) -> None:
        assert id_number is not None
        assert phone_number is not None
        self.__id_number = id_number
        self.__phone_number = phone_number
        self.__mobile_id = (
            mobile_id if mobile_id is not None else self.__generate_mobile_id()
        )

    async def is_authenticated(self) -> bool:
        """Tests if current credentials are valid."""
        try:
            _ = await self.get_vehicles()
            return True
        except IturanAuthError:
            return False

    async def request_otp(self) -> bool:
        data = FormData()
        data.add_field("UserName", self.__id_number)
        data.add_field("SiebelPassword", self.__phone_number)
        data.add_field("AppId", 49)
        data.add_field("OSType", "Android")
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug("Requesting OTP")
                async with session.post(ACTIVATION_URL, data=data) as response:
                    response_data = await response.text()
            logger.debug(f"Got {response.status}: {response_data}")
            assert response.status == 200
            root = ElementTree.fromstring(response_data)
            response_status = root.find(XML_RESPONSE_STATUS)
            assert response_status is not None
            if response_status.text == ERROR_INVALID_CREDENTIALS:
                raise IturanAuthError
            if response_status.text != ERROR_OK:
                raise Exception(response_status.text)
        except IturanAuthError:
            raise
        except Exception as e:
            logging.error(f"Failed requesting OTP: {e}")
            raise IturanApiError(e)
        return True

    async def authenticate(self, otp: str) -> bool:
        data = FormData()
        data.add_field("UserName", self.__id_number)
        data.add_field("SiebelPassword", self.__phone_number)
        data.add_field("OTPcode", otp)
        data.add_field("AppId", 49)
        data.add_field("MobileId", self.__mobile_id)
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Authenticating with OTP {otp}")
                async with session.post(
                    OTP_VERIFICATION_URL, data=data
                ) as response:
                    response_data = await response.text()
            logger.debug(f"Got {response.status}: {response_data}")
            root = ElementTree.fromstring(response_data)
            response_status = root.find(XML_RESPONSE_STATUS)
            assert response_status is not None
            if response_status.text == ERROR_WRONG_OTP_CODE:
                raise IturanAuthError
            if response_status.text != ERROR_OK:
                raise IturanApiError(response_status.text)
        except IturanAuthError:
            raise
        except Exception as e:
            logging.error(f"Failed authenticating: {e}")
            raise IturanApiError(e)
        return True

    async def get_vehicles(self) -> List[Vehicle]:
        vehicles: List[Vehicle] = []
        try:
            root = await self.__get_vehicles_xml()
            error = self.__get_error_from_response(root)
            if error is not None:
                if error == ERROR_INVALID_CREDENTIALS:
                    raise IturanAuthError
                raise IturanApiError(error)
            vehicles_list = root.find(XML_VEHICLES_LIST)
            assert vehicles_list is not None
            for vehicle in vehicles_list:
                electric_data = await self.__get_electic_data(vehicle)
                vehicles.append(Vehicle(vehicle, electric_data))
        except IturanAuthError:
            raise
        except Exception as e:
            logging.error(f"Failed getting list of vehicles: {e}")
            raise IturanApiError(e)
        return vehicles

    @property
    def mobile_id(self):
        return self.__mobile_id

    async def __get_vehicles_xml(self) -> ElementTree.Element:
        data = FormData()
        data.add_field("UserName", self.__id_number)
        data.add_field("GetAddress", True)
        data.add_field("Password", self.__mobile_id)
        async with aiohttp.ClientSession() as session:
            logger.debug("Getting list of vehicles")
            async with session.post(
                ITURAN_GET_VEHICLES_URL, data=data
            ) as response:
                response_data = await response.text()
        if response.status != 200:
            raise IturanApiError
        logger.debug(f"Got {response.status}: {response_data}")
        return ElementTree.fromstring(response_data)

    async def __get_electic_data(
        self, vehicle: ElementTree.Element
    ) -> Optional[ElementTree.Element]:
        if not self.__is_electric_vehicle(vehicle):
            return None
        platform_id = vehicle.findtext(XML_VEHICLE_PLATFORM_ID) or ""
        xml = await self.__get_electric_data_xml(platform_id)
        if xml is None:
            return None
        return xml.find(XML_VEHICLE_DATA)

    async def __get_electric_data_xml(
        self, platform_id: str
    ) -> Optional[ElementTree.Element]:
        data = FormData()
        data.add_field("UserName", self.__id_number)
        data.add_field("PlatformId", platform_id)
        data.add_field("Password", self.__mobile_id)
        async with aiohttp.ClientSession() as session:
            logger.debug(f"Getting electric data for {platform_id}")
            async with session.post(
                ITURAN_GET_ELECTRIC_DATA_URL, data=data
            ) as response:
                response_data = await response.text()
        if response.status != 200:
            return None
        logger.debug(f"Got {response.status}: {response_data}")
        return ElementTree.fromstring(response_data)

    def __get_error_from_response(
        self, xml: ElementTree.Element
    ) -> Optional[str]:
        return_code = xml.find(XML_RETURN_CODE)
        error_description = xml.find(XML_ERROR_DESCRIPTION)
        assert return_code is not None and error_description is not None
        if return_code.text == ERROR_OK.upper():
            return None
        return error_description.text

    def __is_electric_vehicle(self, vehicle: ElementTree.Element) -> bool:
        for product_name in vehicle.iterfind(
            f"{XML_VEHICLE_UNITS}/{XML_VEHICLE_UNIT}/"
            + f"{XML_VEHICLE_SERVICES}/{XML_VEHICLE_SERVICE}/"
            + f"{XML_VEHICLE_PRODUCT_NAME}"
        ):
            product_name = (
                product_name.text.lower() if product_name.text else ""
            )
            if any(
                ev_product_name in product_name
                for ev_product_name in EV_PRODUCT_NAMES
            ):
                return True
        return False

    def __generate_mobile_id(self) -> str:
        return uuid.uuid4().hex[:16]
