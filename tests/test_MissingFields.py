import unittest
from xdi_validator import validate

class TestMissingFields(unittest.TestCase):


    def setUp(self):

        with open("tests/missing_fields.xdi", "r") as wrong_fields:
            self.errors, self.data = validate(wrong_fields)

    def tearDown(self):
        del self.errors
        del self.data

    def test_missing_element(self):
        self.assertIn("element", self.errors)
        self.assertEqual(2, len(self.errors["element"]))

    def test_missing_mono(self):
        self.assertIn("mono", self.errors)