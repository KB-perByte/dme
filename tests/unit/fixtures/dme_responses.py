# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Mock DME API responses for testing."""

# Mock login response
MOCK_LOGIN_RESPONSE = {
    "imdata": [
        {
            "aaaLogin": {
                "attributes": {
                    "token": "test-token-12345",
                    "sessionId": "test-session-id",
                    "userName": "admin",
                    "siteFingerprint": "test-fingerprint"
                }
            }
        }
    ]
}

# Mock logout response
MOCK_LOGOUT_RESPONSE = {
    "imdata": []
}

# Mock class query response (for dme_command)
MOCK_CLASS_RESPONSE = {
    "imdata": [
        {
            "ipv4aclACL": {
                "attributes": {
                    "dn": "sys/acl/ipv4/name-[ACL1v4]",
                    "fragments": "disabled",
                    "ignRoutable": "no",
                    "name": "ACL1v4",
                    "perACEStatistics": "off",
                    "udfPresent": "no"
                }
            }
        },
        {
            "ipv4aclACL": {
                "attributes": {
                    "dn": "sys/acl/ipv4/name-[ACL2v4]",
                    "fragments": "disabled",
                    "ignRoutable": "no",
                    "name": "ACL2v4",
                    "perACEStatistics": "off",
                    "udfPresent": "no"
                }
            }
        }
    ],
    "totalCount": "2"
}

# Mock managed object response (for dme_command)
MOCK_MO_RESPONSE = {
    "imdata": [
        {
            "l1PhysIf": {
                "attributes": {
                    "FECMode": "auto",
                    "accessVlan": "vlan-1",
                    "adminSt": "up",
                    "autoNeg": "on",
                    "beacon": "off",
                    "bw": "default",
                    "controllerId": "",
                    "delay": "1",
                    "descr": "Test interface description",
                    "dn": "sys/intf/phys-[eth1/1]",
                    "duplex": "auto",
                    "id": "eth1/1",
                    "layer": "Layer2",
                    "mtu": "1500",
                    "speed": "auto"
                },
                "children": [
                    {
                        "rmonEtherStats": {
                            "attributes": {
                                "broadcastPkts": "100",
                                "octets": "1000000",
                                "pkts": "500"
                            }
                        }
                    }
                ]
            }
        }
    ],
    "totalCount": "1"
}

# Mock validation response (for dme_validate)
MOCK_VALIDATION_SUCCESS_RESPONSE = {
    "dme_data": {
        "topSystem": {
            "children": [
                {
                    "interfaceEntity": {
                        "children": [
                            {
                                "l1PhysIf": {
                                    "attributes": {
                                        "descr": "Test description",
                                        "id": "eth1/2"
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    },
    "errors": {}
}

MOCK_VALIDATION_ERROR_RESPONSE = {
    "dme_data": {
        "topSystem": {
            "children": [
                {
                    "interfaceEntity": {
                        "children": [
                            {
                                "l1PhysIf": {
                                    "attributes": {
                                        "id": "eth1/2"
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    },
    "errors": {
        0: "Invalid command: idescription"
    }
}

# Mock configuration response (for dme_config)
MOCK_CONFIG_SUCCESS_RESPONSE = {
    "imdata": []
}

# Mock JSON-RPC responses for validation
MOCK_JSONRPC_SUCCESS_RESPONSE = [
    {
        "jsonrpc": "2.0",
        "result": {
            "msg": '{"topSystem": {"children": [{"interfaceEntity": {"children": [{"l1PhysIf": {"attributes": {"descr": "Test description", "id": "eth1/2"}}}]}}]}}'
        },
        "id": 1
    }
]

MOCK_JSONRPC_ERROR_RESPONSE = [
    {
        "jsonrpc": "2.0",
        "error": {
            "code": -32600,
            "message": "Invalid Request"
        },
        "id": 1
    }
]

# Error responses
MOCK_AUTH_ERROR_RESPONSE = {
    "error": {
        "code": "401",
        "message": "Authentication failed"
    }
}

MOCK_HTTP_ERROR_RESPONSE = {
    "error": {
        "code": "400",
        "message": "Bad Request"
    }
}
