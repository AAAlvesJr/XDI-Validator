import unittest
from xdi_validator import validate

class TestValidXDI(unittest.TestCase):


    def setUp(self):

        with open("tests/valid.xdi", "r") as valid_xdi:
            self.errors, self.data = validate(valid_xdi)

    def tearDown(self):
        del self.errors
        del self.data

    def test_valid(self):
        self.assertEqual(len(self.errors), 0)
