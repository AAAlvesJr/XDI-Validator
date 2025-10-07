[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI - Version](https://img.shields.io/pypi/v/xdi-validator?pypiBaseUrl=https%3A%2F%2Fpypi.org&style=flat-square)](https://pypi.org/project/xdi-validator/)

# XDI-Validator

## What is it?

XDI-Validator is a standalone JSON Schema based validator for XDI files.
XDI (*.xdi) is a format used to save XAS data. This validator aiming to be
fully compliant with the XDI/1.0 specification, as detailed in the documents 
[XAS Data Interchange Format Draft Specification, version 1.0](https://github.com/XraySpectroscopy/XAS-Data-Interchange/blob/master/specification/xdi_spec.pdf)
and [Dictionary of XAS Data Interchange Metadata](https://github.com/XraySpectroscopy/XAS-Data-Interchange/blob/master/specification/xdi_dictionary.pdf).

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

Note: Sure, users can also to use the library for parsing and converting XDI files into json. 

## How to install?

XDI-Validator is available in PyPI. The project page is https://pypi.org/project/xdi-validator/.  
To install XDI-Validator on your development environment, just issue the command:

```terminal
 pip install xdi-validator
```
To build and install from the source code do:

1. Clone the repository: `git clone https://github.com/AAAlvesJr/XDI-Validator.git`
2. Go the project directory: `cd XDI-Validator`
3. Build the package: `python3 -m build`
4. Install the wheel: `pip install dist/xdi_validator-{VERSION}-py3-none-any.whl`

where `VERSION` is the package version. 

## Source code

Access to the source code is granted via the project GitHub repository at the
url  https://github.com/AAAlvesJr/XDI-Validator.

## Dependencies 

XDI-Validator's only external dependency is [jsonschema](https://pypi.org/project/jsonschema/) package. 

## How to contribute 

Please, submit a pull request. PR adding new features should implement the correspondind unit test. 
Aside that, please, feel free to open issues for bugs and features requests. 

## License 

XDI-Validator is available under the MIT license. See the LICENSE file for more info.