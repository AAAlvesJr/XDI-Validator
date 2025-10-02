import re
import json
import jsonschema
import io


class XDIEndOfHeaderMissingError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def validate(file: io.TextIOWrapper) -> tuple[list, dict]:
    """
    Analyse and validate contents of a XDI file against the XDI specification version 1.0 as
    described in https://github.com/XraySpectroscopy/XAS-Data-Interchange/blob/master/specification/xdi_spec.pdf.

    Example:
    ```
        from xdi_validator import validate

        xdi_document = open('filename.xdi', 'r')
        try:
            xdi_errors, xdi_dict = validate_xdi(xdi_document)
        except XDIEndOfHeaderMissingError as ex:
            print(ex.message)

        if not xdi_errors:
            print(XDI is valid!)
        else:
            for error in xdi_errors:
                print(error)
    ```
    Args:

        :param file: File-like object containing a xdi document.
        :return: Tuple(error_list, json_repr), where error_list is a list containing errors found in the xdi and
        json_repr is a json dict representing the structure of the xdi file.
        :exception: Raises a XDIEndOfHeaderMissingError if the token to mark the end of header is not present or
        is malformed.
    """

    regex_version = r"^# XDI/(?P<version>\d+)\.(?P<subversion>\d+)\.?(?P<patch>\d*)\s+?(?P<application>[\w\W\D]*)$"
    regex_fields = r"^# (?P<namespace>\w+)\.(?P<tag>\w+):\s*(?P<value>[\w\W\s*]+)\n$"
    regex_fields_end = r"^#\s+///(/*)$"
    regex_header_end = r"^#\s+---(-*)$"
    regex_comment = r"#\s+((\w*\W*\s*)+)"
    regex_float = r"([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))?"

    versions = []
    fields = []
    comments = []
    data = []
    data_missed = []
    error_list = []

    fields_ended = False
    header_ended = False

    for index, line in enumerate(file, start=1):
        match_field = re.match(regex_fields, line, flags=re.IGNORECASE)
        match_version = re.match(regex_version, line, flags=re.IGNORECASE)
        match_fields_end = re.match(regex_fields_end, line, flags=re.IGNORECASE)
        match_header_end = re.match(regex_header_end, line, flags=re.IGNORECASE)
        match_comment = re.match(regex_comment, line, flags=re.IGNORECASE)

        if match_fields_end and not fields_ended:
            fields_ended = True
            continue
        elif match_header_end and not header_ended:
            header_ended = True
            continue
        elif match_field and not fields_ended:
            fields.append((match_field, index))
            continue
        elif match_version and not fields_ended:
            versions.append((match_version, index))
            continue
        elif fields_ended and not header_ended and match_comment:
            comments.append(match_comment)
            continue
        elif header_ended:
            entry = re.finditer(regex_float, line, flags=re.IGNORECASE)
            entry_list = [number.group(0) for number in entry]
            if len(entry_list) and not match_comment:
                data.append([float(number) for number in entry_list])
        else:
            data_missed.append(line)

    if not header_ended:
        raise XDIEndOfHeaderMissingError(
            message=f"Header-end line ('# ---') not found. Analysis can't proceed. Ckeck the file."
        )

    xdi_dict = {}
    path_dict = {}

    # VERSION ====================================>
    for match, index in versions:
        xdi_dict["version"] = match.group("version")
        xdi_dict["subversion"] = match.group("subversion")
        xdi_dict["patch"] = match.group("patch")
        xdi_dict["application"] = match.group("application")
        path_dict[match.group("version").lower()] = index
        path_dict[match.group("subversion").lower()] = index

    # FIELDS =====================================>
    for match, index in fields:
        if match.group("namespace").lower() not in xdi_dict:
            xdi_dict[match.group("namespace").lower()] = {}
            path_dict[match.group("namespace").lower()] = {}
        xdi_dict[match.group("namespace").lower()][match.group("tag").lower()] = (
            match.group("value")
        )
        path_dict[
            f"{match.group('namespace').lower()}.{match.group('tag').lower()}"
        ] = index

    # COMMENTS ===================================>
    for match in comments:
        if "comments" not in xdi_dict:
            xdi_dict["comments"] = []
        xdi_dict["comments"].append(match.group(1).rstrip().strip())

    # DATA =======================================>
    for idx, match in enumerate(data):
        if "data" not in xdi_dict:
            xdi_dict["data"] = list([list() for _ in range(len(xdi_dict["column"]))])
        if len(match) != len(xdi_dict["column"]):
            error_list.append(
                f"[ERROR] <Data Line>: {idx} - <Message>: The number of tags in Column namespace ({len(xdi_dict['column'])}) "
                f"does not match the number of measurements data section ({len(match)})."
            )
            continue
        for i in range(len(xdi_dict["column"])):
            xdi_dict["data"][i].append(match[i])

    # IGNORED DATA ===============================>

    json_repr = json.dumps(xdi_dict, indent=4, ensure_ascii=False)

    Vtor = jsonschema.Draft202012Validator(get_schema())

    try:
        Vtor.validate(xdi_dict)
    except jsonschema.exceptions.ValidationError:

        for index, error in enumerate(Vtor.iter_errors(xdi_dict)):
            key = error.json_path.replace("$.", "")
            if key in path_dict:
                line_number = path_dict[key]
            else:
                line_number = 1
            error_list.append(f"[ERROR] <Path>: {error.json_path} - <Line>: {line_number} - <Message>: {error.message}")

    return error_list, xdi_dict


def get_schema() -> dict:
    schemadef = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "MIDB XDI json schema",
        "description": "Schema for XDI validation on MIDB",
        "type": "object",
        "properties": {
            "version": {"type": "string", "pattern": "^[1-9][0-9]*$"},
            "subversion": {"type": "string", "pattern": "^[0-9][0-9]*$"},
            "application": {"type": "string"},
            "facility": {
                "description": "Tags related to the synchrotron or other facility at which the measurement was made",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "energy": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: GeV, MeV)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(GeV|MeV)$",
                    },
                    "current": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: mA, A)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(mA|A)$",
                    },
                    "xray_source": {"type": "string"},
                },
            },
            "beamline": {
                "description": "Tags related to the structure of the beamline and its photon delivery system",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "collimation": {"type": "string"},
                    "focusing": {"type": "string"},
                    "harmonic_rejection": {"type": "string"},
                },
            },
            "mono": {
                "description": "Tags related to the monochromator",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "d_spacing": {"type": "string"},
                },
                "required": ["d_spacing"],
            },
            "detector": {
                "description": "Tags related to the details of the photon detection system",
                "type": "object",
                "properties": {
                    "I0": {"type": "string"},
                    "IT": {"type": "string"},
                    "IF": {"type": "string"},
                    "IR": {"type": "string"},
                },
            },
            "sample": {
                "description": "Tags related to the details of sample preparation and measurement",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "id": {"type": "string"},
                    "stoichiometry": {
                        "type": "string",
                        "pattern": "^(?# Format: 'IUCr definition of chemical_formula'; Note: parenthesis must separate each cluster, followed by the corresponding cluster count)(\\(*((Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Co|Cr|Cs|Cu|Ds|Db|Dy|Er|Es|Eu|F|Fe|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Ni|No|Np|O|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|U|V|W|Xe|Y|Yb|Zn|Zr)\\d*)+\\)*\\d*)+$",
                    },
                    "prep": {"type": "string"},
                    "experimenters": {"type": "string"},
                    "temperature": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: K, C)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(K|C)$",
                    },
                    "pressure": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: Pa, atm, bar, Torr, psi, Ba)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(Pa|atm|bar|Torr|psi|Ba)$",
                    },
                    "ph": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float]'; Accepted Units: not specified)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?$",
                    },
                    "eh": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: V)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+V$",
                    },
                    "volume": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: m3, cm3, mL,L)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(m3|cm3|mL|L)$",
                    },
                    "porosity": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float]'; Accepted Units: not specified)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?$",
                    },
                    "density": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: kg/m3, g/cm3)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(kg/m3|g/cm3)$",
                    },
                    "concentration": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: mol/L, 1/cm3, g/cm3)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(kg/m3|g/cm3)$",
                    },
                    "resistivity": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: Ω.m, Ω⋅cm )([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(Ω\\.m|Ω\\.cm)$",
                    },
                    "viscosity": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: Pa.s)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+Pa\\.s$",
                    },
                    "electric_field": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: V/m)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+V/m$",
                    },
                    "magnetic_field": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: T, G, Oe)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(T|G|Oe)$",
                    },
                    "magnetic_moment": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: A.m2)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+A\\.m2$",
                    },
                    "crystal_structure": {
                        "type": "string",
                        "pattern": "^(?# Accepted values: triclinic, monoclinic, orthorhombic, tetragonal, hexagonal, rhombohedral, cubic )(triclinic|monoclinic|orthorhombic|tetragonal|hexagonal|rhombohedral|cubic)$",
                    },
                    "electrochemical_potential": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: J/mol)([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+A\\.m2$",
                    },
                },
            },
            "scan": {
                "description": "Tags related to the parameters of the scan",
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "pattern": "^(?# Format: ISO 8601 speciﬁcation for combined dates and times - [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS][timezone]; Examples: '2007-04-05T14:30:22+02:00','2007-04-05T14:30:22+CEST')[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])(:([0-5][0-9]))?((\\+|-)?(((0[0-9]|1[0-2]):([0-9][0-5])))|([A-Za-z]+))?$",
                    },
                    "end_time": {
                        "type": "string",
                        "pattern": "^(?# Format: ISO 8601 speciﬁcation for combined dates and times - [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS][timezone]; Examples: '2007-04-05T14:30:22+02:00','2007-04-05T14:30:22+CEST')[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])(:([0-5][0-9]))?((\\+|-)?(((0[0-9]|1[0-2]):([0-9][0-5])))|([A-Za-z]+))?$",
                    },
                    "edge_energy": {
                        "type": "string",
                        "pattern": "^(?# Format: '[float] [unit]'; Accepted Units: eV. keV, 1/Å )([+-]?(?=\\.\\d|\\d)(?:\\d+)?(?:\\.?\\d*))(?:[Ee]([+-]?\\d+))?\\s+(eV|keV|1/Å)$",
                    },
                },
            },
            "element": {
                "description": " Tags related to the absorbing atom",
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "pattern": "^(?# Format: one of the standard atomic symbols)(Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Co|Cr|Cs|Cu|Ds|Db|Dy|Er|Es|Eu|F|Fe|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Ni|No|Np|O|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|U|V|W|Xe|Y|Yb|Zn|Zr)$",
                    },
                    "edge": {
                        "type": "string",
                        "pattern": "^(?# Format: measured absorption edge)(K|L|L1|L2|L3|M|M1|M2|M3|M4|M5|N|N1|N2|N3|N4|N5|N6|N7|O|O1|O2|O3|O4|O5|O6|O7)$",
                    },
                    "reference": {
                        "type": "string",
                        "pattern": "^(?# Format: one of the standard atomic symbols)(Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Co|Cr|Cs|Cu|Ds|Db|Dy|Er|Es|Eu|F|Fe|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Ni|No|Np|O|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|U|V|W|Xe|Y|Yb|Zn|Zr)$",
                    },
                    "ref_edge": {
                        "type": "string",
                        "pattern": "^(?# Format: measured absorption edge)(K|L|L1|L2|L3|M|M1|M2|M3|M4|M5|N|N1|N2|N3|N4|N5|N6|N7|O|O1|O2|O3|O4|O5|O6|O7)$",
                    },
                },
                "required": ["symbol"],
            },
            "column": {
                "description": "Tags used for identifying the data columns and their units",
                "type": "object",
                "properties": {
                    "1": {
                        "type": "string",
                        "pattern": "^(?# Format: word describing the measured quantity plus a unit when applicable)(\\w+\\s+\\w+|\\w+)$",
                    }
                },
                "patternProperties": {
                    "^[2-9][0-9]*$": {
                        "type": "string",
                        "pattern": "^(?# Format: word describing the measured quantity plus a unit when applicable)(\\w+\\s+\\w+|\\w+)$",
                    }
                },
                "minProperties": 1,
                "additionalProperties": False,
                "required": ["1"],
            },
            "data": {
                "description": "Data array",
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"type": ["number", "integer", "boolean"]},
                },
            },
        },
        "required": ["version", "subversion", "element", "mono"],
    }

    return schemadef
