# XDI-Validator
A standalone JSON Schema based validator for XDI files used to save XAS data aiming to be fully compliant with the XDI/1.0 specification..

## Usage 

As simple as it gets : 

```python
# import the functionality from the module
from xdi_validator import validate, XDIEndOfHeaderMissingError

# open the xdi file
with open('filename.xdi', 'r') as xdi_document:
    
    # Validate the file. If there is no end-of-header token
    # an exception is raised
    try:
        xdi_errors, xdi_dict = validate(xdi_document)
    except XDIEndOfHeaderMissingError as ex:
        print(ex.message)
        
    # check if there are errors
    if xdi_errors:
        print('XDI is invalid!')
        for error in xdi_errors:
            print(error)
    else:
        print('XDI is valid!')
        print(xdi_dict)
    
```