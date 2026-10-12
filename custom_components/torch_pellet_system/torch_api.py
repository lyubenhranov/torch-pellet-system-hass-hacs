import http.client
from codecs import encode
import json
import datetime
import requests
import ssl

from .constants import PELLET_SYSTEM_TNC_STATUS_KEY

class TorchApi:
    """An API client to work with the Torch Web System"""
    ssl._create_default_https_context = ssl._create_unverified_context

    USER_AGENT_VALUE = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:157.0) Gecko/20100101 Firefox/157.0"

    SESSION_COOKIE_HEADER_VALUE = ""

    SESSION_EXPIRATION_DATE = datetime.datetime.now() - datetime.timedelta(days=1)

    TORCH_AUTHENTICATION_RESULT = {
        "InvalidCredentials": "Invalid Credentials",
        "ServiceUnavailable": "Torch Web Interface no available",
        "LoginSucceeded": "Login succeeded",
    }

    TORCH_WEB_INTERFACE_BASE_URL = "my.torch.bg"

    CREDENTIALS_USERNAME = ""
    CREDENTIALS_PASSWORD = ""
    DEVICE_ID = ""

    def ensure_valid_session(self):
        """Ensuring a valid session id from the Torch Web Insterface is present"""
        ssl._create_default_https_context = ssl._create_unverified_context

        if self.SESSION_EXPIRATION_DATE < datetime.datetime.now():
            self.login()

    def login(self, username="", password=""):
        """Login the user in the Torch Web Insterface"""
        ssl._create_default_https_context = ssl._create_unverified_context

        if username == "":
            username = self.CREDENTIALS_USERNAME

        if password == "":
            password = self.CREDENTIALS_PASSWORD

        payload = f"identifier={username}&password={password}"
        headers = {
            "User-Agent": self.USER_AGENT_VALUE,
            "Origin": "https://my.torch.bg",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        login_response = requests.request(
            "POST",
            "https://my.torch.bg/login",
            headers=headers,
            data=payload,
            files=[],
            timeout=120,
            verify=False
        )

        if login_response.status_code == 200:

            response_content = login_response.text

            if (
                response_content.find("invalid_credentials")
                != -1
            ):
                return self.TORCH_AUTHENTICATION_RESULT["InvalidCredentials"]
            else:
                set_cookie_header_value = login_response.headers.get("Set-Cookie")

                self.SESSION_COOKIE_HEADER_VALUE = set_cookie_header_value[
                    0 : set_cookie_header_value.index(";")
                ]

                self.SESSION_EXPIRATION_DATE = datetime.datetime.now() + datetime.timedelta(
                    minutes=30
                )

                return self.TORCH_AUTHENTICATION_RESULT["LoginSucceeded"]
        else:
            return self.TORCH_AUTHENTICATION_RESULT["ServiceUnavailable"]

    def __init__(self, username, password, deviceId):
        """Initialize the API Module with credentials"""
        ssl._create_default_https_context = ssl._create_unverified_context

        self.CREDENTIALS_USERNAME = username
        self.CREDENTIALS_PASSWORD = password
        self.DEVICE_ID = deviceId

        self.ensure_valid_session()

    def send_command_to_device(self, command):
        """Sending commands to the pellet burner"""

        ssl._create_default_https_context = ssl._create_unverified_context

        self.ensure_valid_session()

        http_connection = http.client.HTTPSConnection(self.TORCH_WEB_INTERFACE_BASE_URL, context = ssl._create_unverified_context())

        payload = f"{{\"kind\": \"{command}\"}}"

        headers = {
            "User-Agent": self.USER_AGENT_VALUE,
            "Cookie": self.SESSION_COOKIE_HEADER_VALUE,
            "Content-Type": "application/json"
        }

        http_connection.request("POST", f"/api/devices/{self.DEVICE_ID}/command", payload, headers)

        send_command_response = http_connection.getresponse()

        print(send_command_response.status)

    def turn_burner_on(self):
        """Turn on the Pellet Burner"""
        ssl._create_default_https_context = ssl._create_unverified_context

        self.send_command_to_device("state.start")

    def turn_burner_off(self):
        """Turn off the Pellet Burner"""
        ssl._create_default_https_context = ssl._create_unverified_context

        self.send_command_to_device("state.stop")

    def get_data(self):
        """Get your Torch Pellet System devices data"""
        ssl._create_default_https_context = ssl._create_unverified_context

        self.ensure_valid_session()

        http_connection = http.client.HTTPSConnection(self.TORCH_WEB_INTERFACE_BASE_URL, context = ssl._create_unverified_context())

        headers = {
            "User-Agent": self.USER_AGENT_VALUE,
            "Cookie": self.SESSION_COOKIE_HEADER_VALUE
        }

        http_connection.request("GET", "/devices/__data.json", "", headers)

        response = http_connection.getresponse()
        response_content = response.read().decode("utf-8")

        sanitized_response_content = response_content[
            response_content.index("{") : len(response_content)
        ]

        parsedData = json.loads(sanitized_response_content)

        deviceData = None

        for dataNode in parsedData["nodes"]:
            if dataNode["type"] == "skip":
                continue

            try:
                if dataNode["data"][0]["devices"] is not None:

                    if dataNode["data"][dataNode["data"][2]["id"]] == self.DEVICE_ID:

                        deviceData = dataNode["data"]
            except:
                continue

        dataToReturn = {}

        if deviceData is not None:
            deviceTelemetry = deviceData[deviceData[2]["lastTelemetry"]]

            for key, value in deviceTelemetry.items():
                dataToReturn[key] = deviceData[value]

            deviceLastSeenAtDate = datetime.datetime.strptime(deviceData[deviceData[2]["lastSeenAt"]][1], "%Y-%m-%dT%H:%M:%S.%fZ")

            if (datetime.datetime.utcnow() - deviceLastSeenAtDate).seconds > 120:
                dataToReturn[PELLET_SYSTEM_TNC_STATUS_KEY] = 0
            else:
                dataToReturn[PELLET_SYSTEM_TNC_STATUS_KEY] = 1

        return dataToReturn
