import unittest
from xdi_validator import validate

class TestWrongFields(unittest.TestCase):


    def setUp(self):

        with open("tests/wrong_fields.xdi", "r") as wrong_fields:
            self.errors, self.data = validate(wrong_fields)

    def tearDown(self):
        del self.errors
        del self.data

    def test_invalid_column(self):
        self.assertIn("column['1']", self.errors)

    def test_invalid_element_symbol(self):
        self.assertIn("element.symbol", self.errors)

    def test_invalid_element_edge(self):
        self.assertIn("element.edge", self.errors)

    def test_invalid_element_ref_edge(self):
        self.assertIn("element.ref_edge", self.errors)

    def test_invalid_scan_edge_energy(self):
        self.assertIn("scan.edge_energy", self.errors)

    def test_invalid_scan_start_time(self):
        self.assertIn("scan.start_time", self.errors)

    def test_invalid_scan_end_time(self):
        self.assertIn("scan.end_time", self.errors)

    def test_invalid_mono_d_spacing(self):
        self.assertIn("mono.d_spacing", self.errors)

    def test_invalid_facility_energy(self):
        self.assertIn("facility.energy", self.errors)

    def test_invalid_facility_current(self):
        self.assertIn("facility.current", self.errors)

    def test_invalid_sample_stoichiometry(self):
        self.assertIn("sample.stoichiometry", self.errors)

    def test_invalid_sample_temperature(self):
        self.assertIn("sample.temperature", self.errors)

    def test_invalid_data(self):
        self.assertIn("data", self.errors)

    def test_invalid_array_labels_line(self):
        self.assertIn("array_labels_line", self.errors)