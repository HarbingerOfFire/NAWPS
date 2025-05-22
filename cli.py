import winreg
import re

def write_registry_from_config(config: str):
    current_key = None

    for line in config.strip().splitlines():
        line = line.strip()

        if not line or line.startswith(";") or line.startswith("#"):
            continue  # skip comments or blank lines

        if line.startswith("[") and line.endswith("]"):
            key_path = line[1:-1]
            if key_path.startswith("HKEY_CLASSES_ROOT\\"):
                current_key = (winreg.HKEY_CLASSES_ROOT, key_path[len("HKEY_CLASSES_ROOT\\"):])
            elif key_path.startswith("HKEY_CURRENT_USER\\"):
                current_key = (winreg.HKEY_CURRENT_USER, key_path[len("HKEY_CURRENT_USER\\"):])
            elif key_path.startswith("HKEY_LOCAL_MACHINE\\"):
                current_key = (winreg.HKEY_LOCAL_MACHINE, key_path[len("HKEY_LOCAL_MACHINE\\"):])
            elif key_path.startswith("HKEY_USERS\\"):
                current_key = (winreg.HKEY_USERS, key_path[len("HKEY_USERS\\"):])
            elif key_path.startswith("HKEY_CURRENT_CONFIG\\"):
                current_key = (winreg.HKEY_CURRENT_CONFIG, key_path[len("HKEY_CURRENT_CONFIG\\"):])
            else:
                raise ValueError(f"Unsupported root key in path: {key_path}")
        elif "=" in line and current_key:
            name, value = map(str.strip, line.split("=", 1))

            if value.startswith("dword:"):
                dword_value = int(value.split(":")[1], 16)
                with winreg.CreateKeyEx(current_key[0], current_key[1], 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name.strip('"'), 0, winreg.REG_DWORD, dword_value)
            elif value.startswith("qword:"):
                qword_value = int(value.split(":")[1], 16)
                with winreg.CreateKeyEx(current_key[0], current_key[1], 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name.strip('"'), 0, winreg.REG_QWORD, qword_value)
            elif value.startswith("REG_SZ:"):
                REG_SZ_value = value.split(":", 1)[1].strip('"')
                with winreg.CreateKeyEx(current_key[0], current_key[1], 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name.strip('"'), 0, winreg.REG_SZ, REG_SZ_value)
            elif value.startswith("REG_MULTI_SZ:"):
                REG_MULTI_SZ_value = value.split(":", 1)[1].strip('"').split("\\0")
                with winreg.CreateKeyEx(current_key[0], current_key[1], 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name.strip('"'), 0, winreg.REG_MULTI_SZ, REG_MULTI_SZ_value)
            elif value.startswith("REG_EXPAND_SZ:"):
                REG_EXPAND_SZ_value = value.split(":", 1)[1].strip('"')
                with winreg.CreateKeyEx(current_key[0], current_key[1], 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name.strip('"'), 0, winreg.REG_EXPAND_SZ, REG_EXPAND_SZ_value)
            elif value.startswith("REG_BINARY:"):
                REG_BINARY_value = bytes.fromhex(value.split(":", 1)[1].strip('"'))
                with winreg.CreateKeyEx(current_key[0], current_key[1], 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name.strip('"'), 0, winreg.REG_BINARY, REG_BINARY_value)
            else:
                raise ValueError(f"Unsupported value format: {value}")
        else:
            raise SyntaxError(f"Invalid line in config: {line}")
