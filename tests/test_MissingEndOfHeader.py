import unittest

import xdi_validator
from xdi_validator import validate

class TestMissingEndOfHeader(unittest.TestCase):


    def setUp(self):

        self.file =  open("tests/missing_end_of_header.xdi", "r")

    def tearDown(self):
        self.file.close()

    def test_missing_end_of_header(self):
        with self.assertRaises(xdi_validator.XDIEndOfHeaderMissingError) as error:
            validate(self.file)

