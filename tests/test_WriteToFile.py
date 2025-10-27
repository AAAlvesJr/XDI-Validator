import os
import unittest
from xdi_validator import validate, write_xdi
import copy

class TestWriteToFile(unittest.TestCase):


    def setUp(self):

        with open("tests/valid.xdi", "r") as valid_xdi:
            self.errors, self.data = validate(valid_xdi)

        self.generate_xdi_result = write_xdi(self.data, "tests/generated_valid.xdi" )
        self.invalid_data = copy.deepcopy(self.data)
        self.invalid_data["element"].pop("symbol")
        self.invalid_data["mono"].pop("d_spacing")


    def tearDown(self):

        os.remove('tests/generated_valid.xdi')
        del self.errors
        del self.data
        del self.invalid_data
        del self.generate_xdi_result

    def test_success_xdi_gen(self):

        self.assertEqual(self.generate_xdi_result, None)

    def test_invalid_data(self):

        result = write_xdi(self.invalid_data, "nofile.xdi")
        self.assertGreater( len(result), 0)
        self.assertIn("mono", result )
        self.assertIn("element", result)

    def test_dicts_match(self):

        with open("tests/generated_valid.xdi", "r") as xdi:
            errors, data = validate(xdi)

        self.assertDictEqual(self.data , data)


