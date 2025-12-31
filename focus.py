import sys
from pathlib import Path
import tomllib
import os
import subprocess

HOME = Path.home()
TAG = "# managed by focus-cli"


def is_admin():
    try:
        if sys.platform == "win32":
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except AttributeError:
        return False


def get_hosts_path():
    if sys.platform == "win32":
        path = Path(os.environ["SystemRoot"]) / "System32/drivers/etc/hosts"
        print(f"System is Windows. Accessing {path}")
    elif sys.platform == "darwin":
        path = Path("/etc/hosts")
        print(f"System is MacOS. Accessing {path}")
    elif sys.platform == "linux":
        path = Path("/etc/hosts")
        print(f"System is Linux. Accessing {path}")
    return path


def flush_dns():
    print("Flushing DNS cache...")
    if sys.platform == "win32":
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
    elif sys.platform == "darwin":
        subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], capture_output=True)
    elif sys.platform == "linux":
        subprocess.run(["resolvectl", "flush-caches"], capture_output=True)


def main():
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent

    config_path = base_dir / "config.toml"
    if not config_path.exists():
        config_path = base_dir.parent / "config.toml"

    is_start = False
    is_end = False

    if not is_admin():
        if sys.platform == "win32":
            print("You must run the program as Administrator. Exiting...")
        else:
            print("You must run the program with sudo. Exiting...")
        sys.exit(1)

    n = len(sys.argv)
    for i in range(1, n):
        if sys.argv[i] == "--start":
            is_start = True
        elif sys.argv[i] == "--end":
            is_end = True
        elif sys.argv[i] == "--config":
            if (i + 1) >= n:
                print("[ERROR] You must specify a path with the '--config' option. Exiting...")
                sys.exit(1)
            config_path = Path(sys.argv[i + 1]).resolve()

    if is_start and not config_path.exists():
        print("[ERROR] Config does not exist. Either define a config at " f"{config_path} or provide one as an argument to this script.")
        sys.exit(1)

    if (is_start and is_end) or (not is_start and not is_end):
        print("[ERROR] You must specify exactly one of '--start' or '--end'. Exiting...")
        sys.exit(1)

    hosts_path = get_hosts_path()
    with open(hosts_path, "r") as f:
        content = f.read().strip()

    lines = [line + "\n" for line in content.splitlines() if TAG not in line.strip()]

    if is_start:
        with open(config_path, "rb") as f:
            print(f"Reading config from '{config_path}'...")
            data = tomllib.load(f)

        if "banlist" not in data or len(data["banlist"]) == 0:
            print("[ERROR] 'banlist' missing. Existing...")
            sys.exit(1)

        print("Config valid.")

        if lines:
            lines.append("\n")

        for site in data["banlist"]:
            site = site.replace("https://", "").replace("http://", "").rstrip("/")

            if site.startswith("www."):
                root_domain = site[4:]
                www_domain = site
            else:
                root_domain = site
                www_domain = f"www.{site}"

            lines.append(f"127.0.0.1 {root_domain} {TAG}\n")
            lines.append(f"127.0.0.1 {www_domain} {TAG}\n")

            print(f"Blocking {root_domain}")
    else:
        print("Unblocking all sites...")

    with open(hosts_path, "w") as f:
        f.writelines(lines)

    flush_dns()
    print("Done!")


if __name__ == "__main__":
    main()
