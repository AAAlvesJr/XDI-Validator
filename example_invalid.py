from xdi_validator import validate
import json

with open("invalid.xdi", "r") as invalid_xdi:

    errors, data = validate(invalid_xdi)

    if not len(errors):
        print(data)
        print("File invalid.xdi is VALID!")
    else:
        print("invalid.xdi is INVALID!")
        print(json.dumps(errors, indent=2))
