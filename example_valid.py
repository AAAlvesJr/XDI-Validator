from xdi_validator import validate
import json

valid_xdi   = open("valid.xdi", "r")

errors, data = validate(valid_xdi)

if not len(errors):
    print( json.dumps(data, indent=3))
    print("File valid.xdi is VALID!")
else:
    print("valid.xdi is INVALID!")
    for error in errors:
        print(error)
