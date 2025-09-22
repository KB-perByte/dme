#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
try:
    from ssl import CertificateError
except ImportError:
    from backports.ssl_match_hostname import CertificateError

import q
from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection, ConnectionError
from ansible.module_utils.six import iteritems

BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def find_dict_in_list(some_list, key, value):
    text_type = False
    try:
        to_text(value)
        text_type = True
    except TypeError:
        pass
    for some_dict in some_list:
        if key in some_dict:
            if text_type:
                if to_text(some_dict[key]).strip() == to_text(value).strip():
                    return some_dict, some_list.index(some_dict)
            else:
                if some_dict[key] == value:
                    return some_dict, some_list.index(some_dict)
    return None


class DmeRequest(object):
    def __init__(
        self,
        module=None,
        connection=None,
        headers=None,
        not_rest_data_keys=None,
        task_vars=None,
    ):
        self.module = module

        if module:
            self.connection = Connection(self.module._socket_path)
        elif connection:
            self.connection = connection
            try:
                self.connection.load_platform_plugins(
                    "cisco.dme.dme",
                )
                self.connection.set_options(var_options=task_vars)
            except ConnectionError:
                raise

        if not_rest_data_keys:
            self.not_rest_data_keys = not_rest_data_keys
        else:
            self.not_rest_data_keys = []
        self.not_rest_data_keys.append("validate_certs")
        self.headers = headers if headers else BASE_HEADERS

    def _httpapi_error_handle(self, method, uri, **kwargs):
        code = 99999
        response = {}
        try:
            code, response = self.connection.send_request(
                method,
                uri,
                **kwargs,
            )
        except ConnectionError as e:
            self.module.fail_json(
                msg="connection error occurred: {0}".format(e),
            )
        except CertificateError as e:
            self.module.fail_json(
                msg="certificate error occurred: {0}".format(e),
            )
        except ValueError as e:
            try:
                self.module.fail_json(
                    msg="certificate not found: {0}".format(e),
                )
            except AttributeError:
                pass
        if self.module:
            return response
        else:
            return code, response

    def _rpc_error_handle(self, method, uri, **kwargs):
        code = 99999
        response = {}
        try:
            code, response = self.connection.send_validate_request(
                method,
                uri,
                **kwargs,
            )
        except ConnectionError as e:
            self.module.fail_json(
                msg="connection error occurred: {0}".format(e),
            )
        except CertificateError as e:
            self.module.fail_json(
                msg="certificate error occurred: {0}".format(e),
            )
        except ValueError as e:
            try:
                self.module.fail_json(
                    msg="certificate not found: {0}".format(e),
                )
            except AttributeError:
                pass
        if self.module:
            return response
        else:
            return code, response

    def get(self, url, **kwargs):
        return self._httpapi_error_handle("GET", url, **kwargs)

    def put(self, url, **kwargs):
        return self._httpapi_error_handle("PUT", url, **kwargs)

    def post(self, url, **kwargs):
        return self._httpapi_error_handle("POST", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._httpapi_error_handle("PATCH", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._httpapi_error_handle("DELETE", url, **kwargs)

    def rpc_get(self, url, **kwargs):
        return self._rpc_error_handle("POST", url, **kwargs)
