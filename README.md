# Focus

Block distracting sites using your hosts file.

## Important Notes

- **Secure DNS**: If using Brave or Chrome, you must disable "Secure DNS" (DNS over HTTPS) in settings.
- **Restart Browser**: You may need to close your browser fully for the changes to take effect.

## Usage

1. Edit `config.toml` in the root directory.
2. Run the launcher for your operating system.

> **Note:** These scripts edit the system hosts file and must be run as **Administrator** (Windows) or with **sudo** (macOS/Linux).

## Blocking

- **macOS**: `MacOS/Start_Focus.command`
- **Windows**: `Windows/Start_Focus.bat`
- **Linux**: `Linux/Start_Focus.sh`

## Unblocking

- **macOS**: `MacOS/End_Focus.command`
- **Windows**: `Windows/End_Focus.bat`
- **Linux**: `Linux/End_Focus.sh`
