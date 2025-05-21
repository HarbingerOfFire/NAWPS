import winreg
import re

ROOT_KEYS = {
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKU": winreg.HKEY_USERS,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
}

VALUE_TYPES = {
    "REG_SZ": winreg.REG_SZ,
    "REG_BINARY": winreg.REG_BINARY,
    "REG_DWORD": winreg.REG_DWORD,
    "REG_QWORD": winreg.REG_QWORD,    
    "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
    "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ
}

def parse_section_header(line):
    match = re.match(r"\[(HK[A-Z]+)[\\|](.+)\]", line.strip())
    if not match:
        raise ValueError(f"Invalid section header: {line}")
    root_str, subkey = match.groups()
    root = ROOT_KEYS.get(root_str)
    if root is None:
        raise ValueError(f"Unknown root key: {root_str}")
    return root, subkey

def parse_key_value(line):
    kv_match = re.match(r"([^:]+):([A-Z_]+)\s*=\s*(.+)", line.strip())
    if not kv_match:
        raise ValueError(f"Invalid key/value line: {line}")
    key_name, value_type, raw_value = kv_match.groups()
    value_type = value_type.strip()
    if value_type not in VALUE_TYPES:
        raise ValueError(f"Unsupported registry type: {value_type}")
    
    if value_type == "REG_DWORD":
        value = int(raw_value, 0)  # handles hex and decimal
    else:
        value = raw_value
    return key_name.strip(), VALUE_TYPES[value_type], value

def apply_registry_config(config_str: str):
    current_root = None
    current_path = None

    for line in config_str.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue  # skip empty lines and comments

        if line.startswith("[") and line.endswith("]"):
            current_root, current_path = parse_section_header(line)
        else:
            if current_root is None or current_path is None:
                raise ValueError(f"Key-value before any section: {line}")
            key_name, value_type, value = parse_key_value(line)

            with winreg.CreateKeyEx(current_root, current_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, key_name, 0, value_type, value)
                print(f"Set {key_name} = {value} ({value_type}) at [{current_path}]")

