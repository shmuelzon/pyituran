import io
import os


class MockResponse:
    def __init__(self, status: int, text: str) -> None:
        self.__status = status
        self.__text = text

    @property
    def status(self) -> int:
        return self.__status

    async def text(self) -> str:
        return self.__text

    async def __aexit__(self, *_) -> None:
        pass

    async def __aenter__(self):
        return self


def load_xml_template(file_name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "xml", file_name)
    with io.open(path, encoding="utf8") as xml_file:
        content = xml_file.read()
    return content


REQUEST_OTP_RESPONSE = load_xml_template("request_otp_response.xml")
REQUEST_OTP_RESPONSE_WRONG_CREDENTIALS = load_xml_template(
    "request_otp_response_wrong_credentials.xml"
)
AUTHENTICATE_RESPONSE = load_xml_template("authenticate_response.xml")
AUTHENTICATE_RESPONSE_WITH_WRONG_OTP = load_xml_template(
    "authenticate_response_with_wrong_otp.xml"
)
GET_VEHICLES_RESPONSE = load_xml_template("get_vehicles_response_base.xml")
VEHICLE_RESPONSE = load_xml_template("get_vehicles_response_vehicle.xml")
GET_VEHICLES_RESPONSE_WRONG_CREDENTIALS = load_xml_template(
    "get_vehicles_response_wrong_credentials.xml"
)
