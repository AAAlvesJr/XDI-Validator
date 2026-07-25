import os
import unittest
from xdi_validator import validate

class TestMissingFields(unittest.TestCase):


    def setUp(self):

        with open(os.path.dirname(__file__) + "/missing_fields.xdi", "r") as wrong_fields:
            self.errors, self.data = validate(wrong_fields)

    def tearDown(self):
        del self.errors
        del self.data

    def test_missing_element(self):
        self.assertIn("element", self.errors)
        self.assertEqual(2, len(self.errors["element"]))

    def test_mono_dspacing_not_required_for_energy_abscissa(self):
        # missing_fields.xdi has Column.1: energy — per XDI/1.0 spec,
        # Mono.d_spacing is only required when the abscissa is
        # monochromator angle or encoder step count. So no mono error
        # should fire despite Mono.d_spacing being absent.
        self.assertNotIn("mono", self.errors)