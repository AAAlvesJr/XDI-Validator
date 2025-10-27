from datetime import datetime

from xdi_validator import validate, write_xdi
import json

with open("valid.xdi", "r") as valid_xdi:

    errors, data = validate(valid_xdi)

    if not len(errors):
        print( json.dumps(data, indent=3))
        print("File valid.xdi is VALID!")
    else:
        print("valid.xdi is INVALID!")
        for error in errors:
            print(error)
