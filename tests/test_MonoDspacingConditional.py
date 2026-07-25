"""XDI/1.0 spec: Mono.d_spacing is required only when the abscissa
(Column.1) is monochromator angle or encoder step count. For energy
or wavelength abscissae, Mono.d_spacing is optional.

Ref: https://github.com/XraySpectroscopy/XAS-Data-Interchange/blob/master/specification/spec.md
"""
import os
import unittest
from xdi_validator import validate


HERE = os.path.dirname(__file__)


class TestMonoDspacingConditional(unittest.TestCase):

    def _validate(self, fname):
        with open(os.path.join(HERE, fname), "r") as f:
            errors, _data = validate(f)
        return errors

    def test_angle_abscissa_missing_dspacing_errors(self):
        errors = self._validate("missing_dspacing_angle.xdi")
        self.assertIn("mono", errors,
            "Column.1: angle → Mono.d_spacing must be required")

    def test_angle_abscissa_with_dspacing_ok(self):
        errors = self._validate("valid_angle_dspacing.xdi")
        self.assertNotIn("mono", errors,
            "Column.1: angle with Mono.d_spacing present → no mono error")

    def test_energy_abscissa_missing_dspacing_ok(self):
        # valid.xdi has Column.1: energy and Mono.d_spacing present —
        # remove the d_spacing header at read-time (in-memory) and
        # confirm no mono error fires for an energy abscissa.
        import io
        with open(os.path.join(HERE, "valid.xdi"), "r") as f:
            src = f.read()
        stripped = "\n".join(
            line for line in src.splitlines()
            if not line.lstrip("# ").startswith("Mono.d_spacing")
        )
        errors, _ = validate(io.StringIO(stripped))
        self.assertNotIn("mono", errors,
            "Column.1: energy without Mono.d_spacing → no mono error")


if __name__ == "__main__":
    unittest.main()
