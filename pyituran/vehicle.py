"""Class representing an Ituran vehicle."""

from datetime import datetime
import logging
from typing import List, Optional, Tuple
import xml.etree.ElementTree as ElementTree
from zoneinfo import ZoneInfo

from pyituran.const import (
    EV_BATTERY_LEVEL_LABELS,
    EV_BATTERY_RANGE_LABELS,
    EV_CHARGING_MODE_LABELS,
    XML_VEHICLE_BATTERY_VOLTAGE,
    XML_VEHICLE_DATA_LABEL,
    XML_VEHICLE_DATA_VALUE,
    XML_VEHICLE_DIAGNOSTIC_VALUES,
    XML_VEHICLE_MODEL,
    XML_VEHICLE_MAKE,
    XML_VEHICLE_PLATE,
    XML_VEHICLE_LATITUTE,
    XML_VEHICLE_LONGITUDE,
    XML_VEHICLE_ADDRESS,
    XML_VEHICLE_SPEED,
    XML_VEHICLE_HEADING,
    XML_VEHICLE_LAST_MILEAGE,
    XML_VEHICLE_UPDATE_DATE,
)

logger = logging.getLogger(__package__)


class Vehicle:
    def __init__(
        self,
        xml: ElementTree.Element,
        electric_data_xml: Optional[ElementTree.Element],
    ) -> None:
        self.__make: str = self.__xml_get_field(xml, XML_VEHICLE_MAKE)
        self.__model: str = self.__xml_get_field(xml, XML_VEHICLE_MODEL)
        self.__license_plate: str = self.__xml_get_field(
            xml, XML_VEHICLE_PLATE
        )
        self.__latitue: float = float(
            self.__xml_get_field(xml, XML_VEHICLE_LATITUTE)
        )
        self.__longitude: float = float(
            self.__xml_get_field(xml, XML_VEHICLE_LONGITUDE)
        )
        self.__address: str = self.__xml_get_field(xml, XML_VEHICLE_ADDRESS)
        self.__speed: int = int(self.__xml_get_field(xml, XML_VEHICLE_SPEED))
        self.__heading: int = int(
            self.__xml_get_field(xml, XML_VEHICLE_HEADING)
        )
        self.__mileage: float = float(
            self.__xml_get_field(xml, XML_VEHICLE_LAST_MILEAGE)
        )
        self.__battery_voltage: float = float(
            self.__xml_get_field(xml, XML_VEHICLE_BATTERY_VOLTAGE)
        )
        self.__last_update: datetime = datetime.fromisoformat(
            self.__xml_get_field(xml, XML_VEHICLE_UPDATE_DATE)
        )
        if self.__last_update.tzinfo is None:
            self.__last_update = self.__last_update.replace(
                tzinfo=ZoneInfo("Asia/Jerusalem")
            )
        self.__is_electric_vehicle: bool = False
        self.__is_charging: bool = False
        self.__battery_level: int = 0
        self.__battery_range: int = 0
        if electric_data_xml is None:
            return
        self.__is_electric_vehicle = True
        self.__is_charging = bool(
            self.__electric_data_get_value(
                electric_data_xml, EV_CHARGING_MODE_LABELS
            )
        )
        self.__battery_level = self.__electric_data_get_value(
            electric_data_xml, EV_BATTERY_LEVEL_LABELS
        )
        self.__battery_range = self.__electric_data_get_value(
            electric_data_xml, EV_BATTERY_RANGE_LABELS
        )

    @property
    def make(self) -> str:
        return self.__make

    @property
    def model(self) -> str:
        return self.__model

    @property
    def license_plate(self) -> str:
        return self.__license_plate

    @property
    def gps_coordinates(self) -> Tuple[float, float]:
        return (self.__latitue, self.__longitude)

    @property
    def address(self) -> str:
        return self.__address

    @property
    def heading(self) -> int:
        return self.__heading

    @property
    def speed(self) -> int:
        return self.__speed

    @property
    def mileage(self) -> float:
        return self.__mileage

    @property
    def battery_voltage(self) -> float:
        return self.__battery_voltage

    @property
    def last_update(self) -> datetime:
        return self.__last_update

    @property
    def is_electric_vehicle(self) -> bool:
        return self.__is_electric_vehicle

    @property
    def is_charging(self) -> bool:
        return self.__is_charging

    @property
    def battery_level(self) -> int:
        return self.__battery_level

    @property
    def battery_range(self) -> int:
        return self.__battery_range

    def __str__(self) -> str:
        return f"{self.make} {self.model} @ {self.gps_coordinates}"

    def __xml_get_field(self, xml: ElementTree.Element, path: str) -> str:
        element = xml.find(path)
        assert element is not None
        text = element.text
        assert text is not None
        return text

    def __electric_data_get_value(
        self, xml: ElementTree.Element, labels: List[str]
    ) -> int:
        for diagnostic_value in xml.iterfind(XML_VEHICLE_DIAGNOSTIC_VALUES):
            label = diagnostic_value.findtext(XML_VEHICLE_DATA_LABEL) or ""
            for search_label in labels:
                if search_label not in label:
                    continue
                value = diagnostic_value.findtext(XML_VEHICLE_DATA_VALUE)
                if value is not None:
                    return int(value)
        return 0
