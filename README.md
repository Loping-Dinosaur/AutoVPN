# AutoVPN

Automates the connection to the ETH VPN using Cisco Secure Client (`vpncli.exe`) and automatically generates the Time-Based One-Time Password (TOTP) via Python.

## ⚠️ Security Warning & Disclaimer (Read Before Using)

**Important Notice Regarding Two-Factor Authentication (2FA) and Security Policies.**

While this script provides a convenient way to automate the VPN connection process, it fundamentally breaks the core principle of Two-Factor Authentication. By storing both your primary password (`VPN_PASS`) and your secondary factor seed (`OTP_SECRET`) in the same local `.env` file, you are reducing a two-factor system to a single-factor system (possession of your local machine). 

- **Compromise Risk:** If your local machine is ever compromised by malware or a malicious actor, they will instantly gain full, unhindered access to the university/corporate network under your identity.
- **Policy Compliance:** Using this automation may violate your institution's Acceptable Use Policy (such as the ETH Zurich BOT, Art. 9), which strictly requires the protection of personal credentials and prohibits the circumvention of security and access control measures.

**Use at your own risk.** This project is published for educational purposes to demonstrate CLI automation and Python OTP generation. By using it, you accept full responsibility for any security incidents or policy violations. Real-world engineering requires understanding the trade-offs between user convenience and security—this script heavily prioritizes convenience at the absolute cost of cryptographic identity verification.

## Prerequisites
- Windows OS (due to Cisco path configurations)
- Python 3.x installed
- Cisco Secure Client installed
- Your ETH credentials and OTP Secret (base32 string)

## Installation

1. **Clone the repository:**
   ```cmd
   git clone https://github.com/Loping-Dinosaur/AutoVPN.git
   cd AutoVPN
   ```

2. **Create and activate a virtual environment:**
   ```cmd
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Configuration:**
   - Copy `.env.example` and rename it to `.env`:
     ```cmd
     copy .env.example .env
     ```
   - Open the `.env` file with a text editor and fill in your actual credentials (`VPN_USER`, `VPN_PASS`, `OTP_SECRET`). 
   - *Note: Keep your `.env` file safe and NEVER upload it to GitHub.*

## Create a Desktop Shortcut (.bat file)
## Running AutoVPN (Silent / Headless)

To run the script easily by double-clicking an icon on your desktop, you can create a simple Batch file:
You can launch AutoVPN in the background without opening a terminal window:

1. Right-click on an empty space on your Desktop and select **New -> Text Document**.
2. Rename the file to `Connect_VPN.bat` (make sure you delete the `.txt` extension).
3. Right-click the new `.bat` file, select **Edit**, and paste the following code (adjust the paths if you cloned the repository to a folder other than `C:\projects\AutoVPN`):
- **From Windows Search / Start Menu**: Press `Win`, type `AutoVPN`, and press `Enter`.
- **Using the VBScript launcher**: Double-click `run_autovpn.vbs` in the project root.
- **From Desktop**: Create a shortcut to `run_autovpn.vbs` (or run it via `wscript.exe`).

   ```bat
   @echo off
   start "" "C:\projects\AutoVPN\.venv\Scripts\pythonw.exe" "C:\projects\AutoVPN\vpn_auto.py"
   ```

4. Save the file.
5. Now you can simply double-click `Connect_VPN.bat` or launch **AutoVPN** directly from the Windows Start menu!

## Notes

- **Auto-Close UI:** If the Cisco Secure Client graphical interface is already open, the script will automatically close it before connecting to avoid conflicts. It will safely reopen the UI after the connection is established (if `CISCO_UI_PATH` is configured in your `.env` file).
