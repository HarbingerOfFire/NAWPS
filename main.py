import sys

def main_gui():
    from gui import App, Setting
    app = App()

    # Example usage
    system_theme = Setting(app, type="switch", name="System Theme")
    app.add_setting(system_theme, function=app.SystemTheme)

    app_select = Setting(app, type="list", name="App Theme", options=["Light", "Dark"])
    app.add_setting(app_select, function=app.AppTheme)

    app.mainloop()


def main_cli(conf=None):
    import cli
    with open(conf, 'r') as file:
        config_str = file.read()
        cli.write_registry_from_config(config_str)

def main(conf=None):
    if conf is None:
        main_gui()
        return

    main_cli(conf)


if __name__ == "__main__":

    import ctypes
    import sys
    
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    if not is_admin():
        print("Not running as admin. Trying to elevate...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    
    print("Running with admin privileges.")

    try:
        conf = sys.argv[1]
        main(conf)
    except IndexError:
        main()
