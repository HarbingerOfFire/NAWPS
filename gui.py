import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import Literal
import winreg

# Set appearance and theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class Setting(ctk.CTkFrame):
    def __init__(self, parent, type: Literal["list", "switch"], name: str, options=None):
        super().__init__(parent)
        self.name = name
        self.type = type
        self.widget = None

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
        else:
            raise ValueError("Setting type must be 'list' or 'switch'")

    # COMMON GET/SET
    def get(self):
        if self.widget:
            return self.widget.get()
        raise AttributeError("Widget not initialized")

    def set(self, value):
        if self.widget:
            self.widget.set(value)
        else:
            raise AttributeError("Widget not initialized")

    # SWITCH METHODS
    def toggle_switch(self):
        if self.type == "switch":
            self.set(not self.get())
        else:
            raise TypeError("toggle_switch can only be called on a 'switch' Setting")

    def switch_get(self):
        if self.type != "switch":
            raise TypeError("Not a switch setting")
        return self.get()

    def switch_set(self, value):
        if self.type != "switch":
            raise TypeError("Not a switch setting")
        self.set(value)

    # LIST METHODS
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

    def __str__(self):
        return f"{self.name}: {self.get()}"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NAWPS - Windows Settings")
        self.geometry("400x300")
        self.settings = []

    def not_implemented(self):
        messagebox.showinfo("Not Implemented", "This feature is not implemented yet.")

    def message_error(self, message):
        messagebox.showinfo("Error", message)

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

            return not system_value # True for Dark Mode (to set toggle on for dark mode)
        except FileNotFoundError:
            return False
        
    def AppTheme(self, set:bool=True, value=None):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                system_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                if system_value == 1:
                    system_value = "Light"
                if system_value == 0:
                    system_value = "Dark"

            if set:
                if value is None:
                    raise ValueError("Value must be provided when setting AppTheme")
                if value == "Light":
                    new_value = 1
                elif value == "Dark":
                    new_value = 0

                with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, new_value)
                
                system_value = value
            return system_value
        except FileNotFoundError:
            return False

def gui_main():
    app = App()

    # Example usage
    system_theme = Setting(app, type="switch", name="System Theme")
    app.add_setting(system_theme, function=app.SystemTheme)

    app_select = Setting(app, type="list", name="App Theme", options=["Light", "Dark"])
    app.add_setting(app_select, function=app.AppTheme)

    app.mainloop()


if __name__ == "__main__":
    gui_main()