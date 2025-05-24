import customtkinter as ctk
import winreg
import tkinter.messagebox as messagebox

# Set appearance and theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class DarkModeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows Settings - Appearance")
        self.geometry("400x200")

        # Title label
        self.label = ctk.CTkLabel(self, text="Dark Mode", font=("Segoe UI", 20))
        self.label.pack(pady=20)

        # Toggle switch
        self.dark_mode_switch = ctk.CTkSwitch(self, text="Enable Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_switch.pack(pady=10)

        # Initialize switch state
        self.update_switch_state()

    def update_switch_state(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                apps_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                system_value, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")

                if apps_value == 0 and system_value == 0:
                    self.dark_mode_switch.select()
                else:
                    self.dark_mode_switch.deselect()
        except FileNotFoundError:
            self.dark_mode_switch.deselect()

    def toggle_dark_mode(self):
        enable_dark = self.dark_mode_switch.get() == 1
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,
                                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0,
                                    winreg.KEY_SET_VALUE) as key:
                # Set App mode
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0 if enable_dark else 1)
                # Set System mode
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0 if enable_dark else 1)

        except PermissionError:
            messagebox.showerror("Permission Denied", "Please run this program as Administrator.")


if __name__ == "__main__":
    app = DarkModeApp()
    app.mainloop()
