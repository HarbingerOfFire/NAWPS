import sys

def main_gui():
    from gui import gui_main
    gui_main()

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

    try:
        conf = sys.argv[1]
        main(conf)
    except IndexError:
        main()
