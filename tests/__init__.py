import unittest

from tests.test_WrongFields import *
from tests.test_MissingFields import *
from tests.test_MissingEndOfHeader import *
from tests.test_ValidXDI import *
from tests.test_WriteToFileTwo import *
from tests.test_WriteToFile import *

if __name__ == "__main__":
    unittest.main(verbosity=2)
