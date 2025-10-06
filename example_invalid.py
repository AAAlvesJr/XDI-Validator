from xdi_validator import validate
import json

invalid_xdi   = open("/home/augalves/Development/INCT/XDI_QUATI/09200157_Cobre_CuOH2_M1_Si.xdi", "r")

errors, data = validate(invalid_xdi)

if not len(errors):
    print(data)
    print("File invalid.xdi is VALID!")
else:
    print("invalid.xdi is INVALID!")
    for error in errors:
        print(error)
