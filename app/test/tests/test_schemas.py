# -*- coding: utf-8 -*-
import unittest

import jsonschema

from schemas import PROFILE_IN_SCHEMA
from schemas import PROFILE_OUT_SCHEMA


class TestSchemas(unittest.TestCase):
    def test_validate_profile_in(self):
        profile = {
            "first_name": "John",
            "last_name": "Doe"
        }
        jsonschema.validate(profile, schema=PROFILE_IN_SCHEMA)

        missing_last_name = {
            "first_name": "John"
        }

        self.assertRaises(jsonschema.ValidationError, jsonschema.validate, missing_last_name, PROFILE_IN_SCHEMA)

    def test_validate_profile_out(self):
        profile = {
            "first_name": "John",
            "last_name": "Doe",
            "id": "1234"
        }
        jsonschema.validate(profile, schema=PROFILE_OUT_SCHEMA)

        missing_id = {
            "first_name": "John",
            "last_name": "Doe",
        }

        self.assertRaises(jsonschema.ValidationError, jsonschema.validate, missing_id, PROFILE_OUT_SCHEMA)
