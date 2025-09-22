# (c) 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
author: Sagar Paul (@KB-perByte)
name: dme
short_description: HttpApi Plugin for Cisco Nxos Data Management Engine (DME)
description:
- This HttpApi plugin provides methods to connect to Cisco Nxos Data Management Engine (DME) over
  a HTTP(S)-based api.
version_added: 1.0.0
"""

import base64
import hashlib
import json
import time

from ansible.errors import AnsibleAuthenticationFailure
from ansible.module_utils.basic import to_bytes, to_text
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible_collections.ansible.netcommon.plugins.plugin_utils.httpapi_base import (
    HttpApiBase,
)

BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

LOGIN_URL = "/api/aaaLogin.json"
LOGOUT_URL = "/api/aaaLogout.json"


class HttpApi(HttpApiBase):

    def send_request(
        self,
        request_method,
        url,
        params=None,
        data=None,
        headers=None,
    ):

        params = params if params else {}
        headers = headers if headers else BASE_HEADERS
        data = data if data else {}

        if params:
            params_with_val = {}
            for param in params:
                if params[param] is not None:
                    params_with_val[param] = params[param]
            url = "{0}?{1}".format(url, urlencode(params_with_val))
        try:
            self._display_request(request_method)

            response, response_data = self.connection.send(
                url,
                to_bytes(json.dumps(data)),
                method=request_method,
                headers=headers,
            )
            value = self._get_response_value(response_data)

        except HTTPError as e:
            error = json.loads(e.read())
            return e.code, error
        return response.getcode(), self._response_to_json(value)

    def send_validate_request(
        self,
        request_method,
        url,
        params=None,
        data=None,
        headers=None,
    ):
        """
        Send validation request using JSON-RPC protocol.

        Note: This method uses direct requests due to the need for JSON-RPC protocol
        which is different from the standard REST API. This should be refactored
        to use Ansible's connection framework when possible.
        """
        connection_options = self.connection.get_options()
        username = connection_options.get("remote_user")
        password = connection_options.get("password")

        if not username or not password:
            raise AnsibleAuthenticationFailure("Username and password are required")

        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.session_key = encoded_credentials
        self._auth_header = f"Basic {encoded_credentials}"

        # Generate a dynamic CSRF token instead of using hardcoded value
        csrf_token = hashlib.md5(f"{username}{time.time()}".encode()).hexdigest()[:16]

        headers = {
            "Authorization": self._auth_header,
            "Content-Type": "application/json-rpc",
            "Host": self.connection.get_options().get("host")
            + ":"
            + to_text(self.connection.get_options().get("port")),
            "Origin": self.connection._url,
            "Referer": self.connection._url + "/",
            "anticsrf": csrf_token,
        }
        params = params if params else {}
        data = data if data else {}

        if params:
            params_with_val = {}
            for param in params:
                if params[param] is not None:
                    params_with_val[param] = params[param]
            url = "{0}?{1}".format(url, urlencode(params_with_val))

        try:
            self._display_request(request_method)

            # TODO: Refactor to use Ansible's connection framework
            # This direct requests usage should be replaced with proper connection handling
            import requests
            from requests.packages.urllib3.exceptions import InsecureRequestWarning

            session = requests.Session()

            # Respect SSL verification settings from connection options
            validate_certs = connection_options.get("validate_certs", True)
            session.verify = validate_certs

            if not validate_certs:
                # Suppress only the specific warning about unverified HTTPS requests
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

            response_data = session.post(
                self.connection._url + "/ins",
                data=to_bytes(json.dumps(data)),
                headers=headers,
                timeout=30,
            )
            response_data.raise_for_status()

            error_map = {}
            json_response = response_data.json()
            for data_idx in range(len(json_response)):
                if json_response[data_idx].get("error"):
                    error_map[data_idx] = ""

        except requests.exceptions.RequestException as e:
            raise AnsibleAuthenticationFailure(f"Request failed: {str(e)}")
        except (ValueError, KeyError) as e:
            raise AnsibleAuthenticationFailure(f"Invalid response format: {str(e)}")
        except HTTPError as e:
            error = json.loads(e.read())
            return e.code, error

        return 200, {
            "dme_data": json.loads(json_response[-1]["result"]["msg"]),
            "errors": error_map,
        }

    def _display_request(self, request_method):
        self.connection.queue_message(
            "vvvv",
            "DME API REST: %s %s" % (request_method, self.connection._url),
        )

    def _get_response_value(self, response_data):
        return to_text(response_data.getvalue())

    def _response_to_json(self, response_text):
        try:
            return json.loads(response_text) if response_text else {}
        except ValueError:
            return response_text

    def login(self, username, password):

        login_path = LOGIN_URL
        auth_data = {"aaaUser": {"attributes": {"name": username, "pwd": password}}}

        code, auth_data_raw = self.send_request("POST", login_path, data=auth_data)
        try:
            if code >= 400 and isinstance(auth_data_raw, dict):
                raise AnsibleAuthenticationFailure(
                    message="{0} Failed to acquire login token.".format(
                        auth_data_raw["error"].get("message"),
                    ),
                )

            auth_data = auth_data_raw.get("imdata")[0].get("aaaLogin").get("attributes")

            self._auth_token = auth_data.get("token")
            self.connection._auth = {"Cookie": f"APIC-cookie={self._auth_token}"}
            self._session_id = auth_data.get("sessionId")
            self._username = auth_data.get("userName")
            self._siteFineprint = auth_data.get("siteFingerprint")

        except KeyError:
            raise AnsibleAuthenticationFailure(
                message="Failed to acquire login token.",
            )

    def logout(self):
        if self.connection._auth is not None:
            code, auth_data_raw = self.send_request(
                "POST",
                LOGOUT_URL,
                data={
                    "aaaUser": {
                        "attributes": {"name": ""},
                    },
                },
            )
            # Clean up all tokens
            self.connection._auth = None
            self._auth_token = None
