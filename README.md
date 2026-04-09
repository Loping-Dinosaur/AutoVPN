# AutoVPN

Automates the connection to the ETH VPN using Cisco Secure Client (`vpncli.exe`) and automatically generates the Time-Based One-Time Password (TOTP) via Python.

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

To run the script easily by double-clicking an icon on your desktop, you can create a simple Batch file:

1. Right-click on an empty space on your Desktop and select **New -> Text Document**.
2. Rename the file to `Connect_VPN.bat` (make sure you delete the `.txt` extension).
3. Right-click the new `.bat` file, select **Edit**, and paste the following code (adjust the paths if you cloned the repository to a folder other than `C:\AutoVPN`):

   ```bat
   @echo off
   C:\AutoVPN\.venv\Scripts\python.exe C:\AutoVPN\vpn_auto.py
   ```

4. Save the file.
5. Now you can simply double-click `Connect_VPN.bat` on your desktop to automatically connect to the ETH VPN!
