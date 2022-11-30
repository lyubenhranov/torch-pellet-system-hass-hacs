import http.client
from codecs import encode
import json
import datetime
import requests


class TorchApi:
    """An API client to work with the Torch Web System"""

    SESSION_COOKIE_HEADER_VALUE = ""

    SESSION_EXPIRATION_DATE = datetime.datetime.now() - datetime.timedelta(days=1)

    TORCH_AUTHENTICATION_RESULT = {
        "InvalidCredentials": "Invalid Credentials",
        "ServiceUnavailable": "Torch Web Interface no available",
        "LoginSucceeded": "Login succeeded",
    }

    TORCH_WEB_INTERFACE_BASE_URL = "my.torch-burner.eu"

    CREDENTIALS_USERNAME = ""
    CREDENTIALS_PASSWORD = ""

    def get_new_session_id(self) -> None:
        """Getting a new session id from the Torch Web Insterface"""

        http_connection = http.client.HTTPSConnection(self.TORCH_WEB_INTERFACE_BASE_URL)
        http_connection.request("GET", "/user/", "", {})
        response = http_connection.getresponse()
        set_cookie_header_value = response.headers.get("Set-Cookie")

        self.SESSION_COOKIE_HEADER_VALUE = set_cookie_header_value[
            0 : set_cookie_header_value.index(";")
        ]

        self.SESSION_EXPIRATION_DATE = datetime.datetime.now() + datetime.timedelta(
            minutes=30
        )

    def ensure_valid_session(self):
        """Ensuring a valid session id from the Torch Web Insterface is present"""

        if self.SESSION_EXPIRATION_DATE < datetime.datetime.now():
            self.get_new_session_id()
            self.login()

    def login(self, username="", password=""):
        """Login the user in the Torch Web Insterface"""

        if username == "":
            username = self.CREDENTIALS_USERNAME

        if password == "":
            password = self.CREDENTIALS_PASSWORD

        payload = {"username": username, "password": password}
        headers = {"Cookie": self.SESSION_COOKIE_HEADER_VALUE}

        login_response = requests.request(
            "POST",
            "https://my.torch-burner.eu/",
            headers=headers,
            data=payload,
            files=[],
            timeout=120,
        )

        if login_response.status_code == 200:
            response_content = login_response.text

            if (
                response_content.find("Потребителското име и паролата несъвпадат!")
                != -1
            ):
                return self.TORCH_AUTHENTICATION_RESULT["InvalidCredentials"]
            else:
                return self.TORCH_AUTHENTICATION_RESULT["LoginSucceeded"]
        else:
            return self.TORCH_AUTHENTICATION_RESULT["ServiceUnavailable"]

    def __init__(self, username, password):
        """Initialize the API Module with credentials"""

        self.CREDENTIALS_USERNAME = username
        self.CREDENTIALS_PASSWORD = password

        self.ensure_valid_session()

    def set_burner_status(self, status):
        """Switching the pellet burner on and off"""

        self.ensure_valid_session()

        http_connection = http.client.HTTPSConnection(self.TORCH_WEB_INTERFACE_BASE_URL)

        data_list = []

        boundary = "wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T"

        data_list.append(encode("--" + boundary))
        data_list.append(encode("Content-Disposition: form-data; name=goto;"))

        data_list.append(encode("Content-Type: {}".format("text/plain")))
        data_list.append(encode(""))

        data_list.append(encode(status))
        data_list.append(encode("--" + boundary + "--"))
        data_list.append(encode(""))

        payload = b"\r\n".join(data_list)

        headers = {
            "Cookie": self.SESSION_COOKIE_HEADER_VALUE,
            "X-Requested-With": "XMLHttpRequest",
            "Content-type": "multipart/form-data; boundary={}".format(boundary),
        }

        http_connection.request("POST", "/user/ajax/burner_onoff", payload, headers)

        status_set_response = http_connection.getresponse()

        print(status_set_response.status)

    def turn_burner_on(self):
        """Turn on the Pellet Burner"""

        self.set_burner_status("on")

    def turn_burner_off(self):
        """Turn off the Pellet Burner"""

        self.set_burner_status("off")

    def get_data(self):
        """Get your Torch Pellet System current data readings"""

        self.ensure_valid_session()

        http_connection = http.client.HTTPSConnection(self.TORCH_WEB_INTERFACE_BASE_URL)

        headers = {
            "Cookie": self.SESSION_COOKIE_HEADER_VALUE,
            "Accept": "*/*",
            "Referer": "https://my.torch-burner.eu/user/",
            "X-Requested-With": "XMLHttpRequest",
        }

        http_connection.request("GET", "/user/ajax/get_data", "", headers)

        response = http_connection.getresponse()
        response_content = response.read().decode("utf-8")

        sanitized_response_content = response_content[
            response_content.index("{") : len(response_content)
        ]

        parsedData = json.loads(sanitized_response_content)

        systemData = parsedData["vars"]

        dataToReturn = {}

        for dataItem in systemData:
            dataToReturn[dataItem["id"]] = dataItem["value"]

        return dataToReturn
