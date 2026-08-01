import os
import unittest

from xdi_validator import validate


class TestSeparatorsWithoutSpace(unittest.TestCase):
    """The header-end and field-end lines need no space after the '#'.

    The specification defines each as

        comment token + separator token + end-of-line token

    where the separator token is "three or more" dashes or slashes. No
    whitespace token sits between the comment token and the separator,
    so a file written "#-----" conforms. 258 of the 272 files in the XDI
    Data Library are written that way, and every one of them was
    rejected before this.
    """

    def setUp(self):
        here = os.path.dirname(__file__)
        self.unspaced = open(here + "/separators_without_space.xdi", "r")
        self.spaced = open(
            os.path.dirname(here) + "/valid.xdi", "r")

    def tearDown(self):
        self.unspaced.close()
        self.spaced.close()

    def test_unspaced_separators_are_accepted(self):
        errors, obj = validate(self.unspaced)
        self.assertEqual(errors, {})
        self.assertIn("scan", obj)

    def test_spaced_separators_still_accepted(self):
        """The form the specification illustrates must keep working."""
        errors, _obj = validate(self.spaced)
        self.assertEqual(errors, {})
