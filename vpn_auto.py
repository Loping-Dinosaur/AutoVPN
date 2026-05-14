from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("Please install python-dotenv: pip install python-dotenv")

try:
    import pyotp
except ImportError:
    sys.exit("Please install pyotp: pip install pyotp")

CONFIG_PATH = Path(__file__).parent / ".env"


def load_config() -> None:
    """Load environment variables from a .env file.

    If the expected configuration file is missing we no longer abort the
    program. A missing file is acceptable when the necessary variables are
    already provided by the shell, users may prefer that behaviour. We log a
    warning so that accidental misconfiguration is easier to notice during
    later troubleshooting.
    """

    if not CONFIG_PATH.exists():
        print(f"WARNING: Configuration file {CONFIG_PATH} not found, "
              "relying on existing environment variables")
        return
    load_dotenv(dotenv_path=CONFIG_PATH)


def get_env(var: str, required: bool = True) -> Optional[str]:
    val = os.getenv(var)
    if required and (val is None or val.strip() == ""):
        sys.exit(f"Environment variable {var} is not set or empty")
    return val


def generate_otp(secret: str) -> str:
    # pyotp expects base32 secret without spaces.  Users may accidentally put
    # spaces when copying from their configuration file, so remove all
    # whitespace before handing it off.
    clean = "".join(secret.split())
    return pyotp.TOTP(clean).now()


def _resolve_cli_executable(cli_path: Optional[str]) -> str:
    """Return an executable name usable by :func:`subprocess.run`.

    If the caller provided an explicit Cisco CLI path we verify that the
    file exists. A non-existent path is treated as a fatal configuration
    error; the error message is forwarded to the user via :func:`sys.exit`.
    When no path is given we fall back to ``vpncli.exe`` and allow the normal
    ``PATH`` lookup to take place.
    """

    if cli_path:
        path = cli_path.strip()
        if not path:
            return "vpncli.exe"
        if not Path(path).exists():
            sys.exit(f"Cisco CLI not found at {path}")
        return path

    return "vpncli.exe"


def call_cisco_cli(
    host: str,
    user: str,
    password: str,
    otp: str,
    cli_path: Optional[str],
    vpn_group: str = "1",  # Update to index 1
) -> subprocess.CompletedProcess:
    vpncli = _resolve_cli_executable(cli_path)

    # Pass host as an argument to the connect command
    cmd = [vpncli, "-s", "connect", host]

    # CLI sequence based on ETH server prompt:
    # 1. Group (e.g. student-net or staff-net)
    # 2. Username
    # 3. Password
    # 4. OTP (Second Password)
    input_cmds = f"{vpn_group}\n{user}\n{password}\n{otp}\n"

    return subprocess.run(cmd, input=input_cmds, capture_output=True, text=True)


def main() -> None:
    load_config()
    
    host = get_env("VPN_HOST")
    user = get_env("VPN_USER")
    password = get_env("VPN_PASS")
    otp_secret = get_env("OTP_SECRET")
    cli_path = get_env("CISCO_CLI_PATH", required=False)
    vpn_group = get_env("VPN_GROUP", required=False) or "1"
    ui_path = get_env("CISCO_UI_PATH", required=False)

    otp = generate_otp(otp_secret)

    if ui_path and os.name == 'nt':
        ui_name = Path(ui_path.strip()).name
        print(f"Closing {ui_name} (if open) to avoid conflicts...")
        subprocess.run(["taskkill", "/F", "/IM", ui_name], capture_output=True)
        time.sleep(1)

    print("Connecting to ETH VPN... (this might take a few seconds)")
    result = call_cisco_cli(host, user, password, otp, cli_path, vpn_group)

    if result.returncode != 0:
        print(f"Cisco CLI returned non-zero exit status: {result.returncode}")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(result.returncode)

    print("Connection attempt complete. Output below:")
    print(result.stdout)

    # Start the graphical user interface if path is provided and exists
    if ui_path and Path(ui_path.strip()).exists():
        subprocess.Popen([ui_path.strip()])


if __name__ == "__main__":
    main()