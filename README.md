# XDI-Validator
A standalone JSON Schema based validator for XDI files used to save XAS data aiming to be fully compliant with the XDI/1.0 specification..

## Usage 

As simple as it gets : 

```python
# import the 
from xdi_validator import validate, XDIEndOfHeaderMissingError

xdi_document = open('filename.xdi', 'r')
try:
    xdi_errors, xdi_dict = validate(xdi_document)
except XDIEndOfHeaderMissingError as ex:
    print(ex.message)

if xdi_errors:
    print('XDI is invalid!')
    for error in xdi_errors:
        print(error)
else:
    print('XDI is valid!')
    print(xdi_dict)
    
```