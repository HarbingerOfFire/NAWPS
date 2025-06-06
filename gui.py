import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import Literal
import winreg


# Set appearance and theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class Setting(ctk.CTkFrame):
    def __init__(self, parent, type: Literal["list", "switch", "entry"], name: str, options=None):
        super().__init__(parent)
        self.name = name
        self.type = type
        self.widget = None
        self.button = None

        if type == "switch":
            ctk.CTkLabel(self, text=name).pack(anchor="w", padx=10, pady=5)
            self.widget = ctk.CTkSwitch(self, text=None)
            self.widget.pack(anchor="w", padx=10, pady=5)

        elif type == "list":
            if options is None:
                options = ["Option 1", "Option 2"]
            ctk.CTkLabel(self, text=name).pack(anchor="w", padx=10, pady=5)
            self.widget = ctk.CTkOptionMenu(self, values=options)
            self.widget.pack(anchor="w", padx=10, pady=5)

        elif type == "entry":
            ctk.CTkLabel(self, text=name).pack(anchor="w", padx=10, pady=5)
            entry_row = ctk.CTkFrame(self)
            self.widget = ctk.CTkEntry(entry_row)
            self.widget.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.button = ctk.CTkButton(entry_row, text="Apply")
            self.button.pack(side="right")
            entry_row.pack(fill="x", padx=10, pady=5)

        else:
            raise ValueError("Setting type must be 'list', 'switch', or 'entry'")

    def get(self):
        if self.widget:
            return self.widget.get()
        raise AttributeError("Widget not initialized")

    def set(self, value):
        if not self.widget:
            raise AttributeError("Widget not initialized")

        if self.type == "entry":
            self.widget.delete(0, "end")
            self.widget.insert(0, value)
        else:
            self.widget.set(value)

    def toggle_switch(self):
        if self.type != "switch":
            raise TypeError("toggle_switch can only be called on a 'switch' Setting")
        self.set(not self.get())

    def switch_get(self):
        if self.type != "switch":
            raise TypeError("Not a switch setting")
        return self.get()

    def switch_set(self, value):
        if self.type != "switch":
            raise TypeError("Not a switch setting")
        self.set(value)

    def add_option(self, option):
        if self.type != "list":
            raise TypeError("add_option only applies to 'list' Setting")
        current = self.widget.cget("values")
        self.widget.configure(values=[*current, option])

    def list_get(self):
        if self.type != "list":
            raise TypeError("Not a list setting")
        return self.get()

    def list_set(self, value):
        if self.type != "list":
            raise TypeError("Not a list setting")
        self.set(value)

    def entry_get(self):
        if self.type != "entry":
            raise TypeError("Not an entry setting")
        return self.get()

    def entry_set(self, value):
        if self.type != "entry":
            raise TypeError("Not an entry setting")
        self.widget.delete(0, "end")
        self.widget.insert(0, value)

    def __str__(self):
        return f"{self.name}: {self.get()}"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NAWPS - Windows Settings")
        self.geometry("400x350")
        self.settings = []

    def not_implemented(self):
        messagebox.showinfo("Not Implemented", "This feature is not implemented yet.")

    def message_error(self, message):
        messagebox.showinfo("Error", message)

    def rgb_to_bgr_dword(self, rgb):
        if isinstance(rgb, str):
            rgb = rgb.lstrip('#')
            if len(rgb) != 6:
                raise ValueError("Hex color must be 6 characters long")
            r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        elif isinstance(rgb, tuple) and len(rgb) == 3:
            r, g, b = rgb
        else:
            raise TypeError("Input must be a hex string or an (R, G, B) tuple")
        dword = (0xFF << 24) | (b << 16) | (g << 8) | r
        return dword
    
    def dword_to_rgb(self, dword):
        """
        Convert a DWORD registry color value (ARGB, with BGR byte order) back to an RGB tuple.
        Input can be int or hex string.
        """
        if isinstance(dword, str):
            dword = int(dword, 16)

        b = dword & 0xFF
        g = (dword >> 8) & 0xFF
        r = (dword >> 16) & 0xFF
        a = (dword >> 24) & 0xFF  # Often 0xFF (opaque), but may be used

        return (r, g, b), a


    def add_setting(self, setting: Setting, function=None):
        if function is None:
            function = self.not_implemented

        setting.pack(pady=10, fill="x", padx=10)
        self.settings.append(setting)

        if setting.type == "switch":
            try:
                if function(set=False):
                    setting.widget.select()
                else:
                    setting.widget.deselect()
            except Exception as e:
                print(f"Error checking initial state for {function.__name__}: {e}")

            setting.widget.configure(command=lambda: function())

        elif setting.type == "list":
            try:
                current_value = function(set=False)
                if current_value not in setting.widget.cget("values"):
                    raise ValueError("Current Value not in list of options")
                setting.list_set(current_value)
            except Exception as e:
                print(f"Error checking initial state: {e}")

            setting.widget.configure(command=lambda value: function(value=value))

        elif setting.type == "entry":
            try:
                current_value = function(set=False)
                setting.entry_set(current_value)
            except Exception as e:
                print(f"Error checking initial state: {e}")

            if setting.button:
                setting.button.configure(command=lambda: function(value=setting.entry_get()))

    def SystemTheme(self, set: bool = True):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                system_value, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                system_value = bool(system_value)

            if set:
                new_value = int(not system_value)
                with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, new_value)
                system_value = new_value

            return not system_value
        except FileNotFoundError:
            return False

    def AppTheme(self, set: bool = True, value=None):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                system_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                system_value = "Light" if system_value == 1 else "Dark"

            if set:
                if value is None:
                    raise ValueError("Value must be provided when setting AppTheme")
                new_value = 1 if value == "Light" else 0
                with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, new_value)
                system_value = value

            return system_value
        except FileNotFoundError:
            return False

    def AccentColor(self, set: bool = True, value=None):
        key_path = r"Software\Microsoft\Windows\DWM"
        key_path2 = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                system_value, _ = winreg.QueryValueEx(key, "ColorizationColor")
                prevalence, _ = winreg.QueryValueEx(key, "ColorPrevalence")
                if prevalence == 0:
                    system_value = "Default"
                else:
                    rgb = self.dword_to_rgb(system_value)[0]
                    system_value = "#{:02X}{:02X}{:02X}".format(*rgb)

            if set:
                if value is None:
                    raise ValueError("Value must be provided when setting AccentColor")

                if value == "Default":
                    new_value = 0x000000
                    new_prevalence = 0
                else:
                    new_value = self.rgb_to_bgr_dword(value)
                    new_prevalence = 1

                with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "ColorizationColor", 0, winreg.REG_DWORD, new_value)
                    winreg.SetValueEx(key, "ColorPrevalence", 0, winreg.REG_DWORD, new_prevalence)

                with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path2, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "AccentColorMenu", 0, winreg.REG_DWORD, new_value)

                system_value = value

            return system_value
        except FileNotFoundError:
            return False


def gui_main():
    app = App()

    try:
        # Example usage
        system_theme = Setting(app, type="switch", name="System Theme")
        app.add_setting(system_theme, function=app.SystemTheme)

        app_theme = Setting(app, type="list", name="App Theme", options=["Light", "Dark"])
        app.add_setting(app_theme, function=app.AppTheme)

        accent_color = Setting(app, type="entry", name="Accent Color (Hex)")
        app.add_setting(accent_color, function=app.AccentColor)

        app.mainloop()
    except Exception as e:
        app.message_error(e)
        app.mainloop()

if __name__ == "__main__":
    gui_main()
