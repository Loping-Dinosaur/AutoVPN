import os
import subprocess
import sys
import pytest
import pyotp

import vpn_auto


def test_generate_otp():
    # Use a known secret and verify output is 6 digits
    secret = pyotp.random_base32()
    otp = vpn_auto.generate_otp(secret)
    assert isinstance(otp, str)
    assert otp.isdigit() and len(otp) == 6


def test_generate_otp_with_spaces():
    secret = pyotp.random_base32()
    spaced = " ".join(secret[i : i + 4] for i in range(0, len(secret), 4))
    otp = vpn_auto.generate_otp(spaced)
    # result should match original
    assert otp == vpn_auto.generate_otp(secret)


def test_get_env_missing(monkeypatch):
    monkeypatch.delenv("FOO", raising=False)
    with pytest.raises(SystemExit) as exc:
        vpn_auto.get_env("FOO")
    assert "Environment variable FOO is not set" in str(exc.value)


def test_get_env_empty(monkeypatch):
    monkeypatch.setenv("BAR", "   ")
    with pytest.raises(SystemExit):
        vpn_auto.get_env("BAR")


def test_get_env_optional(monkeypatch):
    monkeypatch.delenv("BAZ", raising=False)
    assert vpn_auto.get_env("BAZ", required=False) is None


def test_call_cisco_cli_default(monkeypatch, tmp_path):
    # capture the arguments passed to subprocess.run
    captured = {}

    def fake_run(cmd, input=None, **kwargs):
        captured['cmd'] = cmd
        captured['input'] = input
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    res = vpn_auto.call_cisco_cli("host", "user", "pass", "otp", None)
    assert res.returncode == 0
    # default vpn group should be student-net
    assert "student-net" in captured['input']
    assert captured['cmd'][0] == "vpncli.exe"


def test_resolve_cli_executable_defaults():
    assert vpn_auto._resolve_cli_executable(None) == "vpncli.exe"
    # blank string also falls back
    assert vpn_auto._resolve_cli_executable("   ") == "vpncli.exe"


def test_call_cisco_cli_with_path(monkeypatch, tmp_path):
    captured = {}

    def fake_run(cmd, input=None, **kwargs):
        captured['cmd'] = cmd
        captured['input'] = input
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    # create a dummy file to satisfy existence check
    path = tmp_path / "vpncli.exe"
    path.write_text("")
    res = vpn_auto.call_cisco_cli("h", "u", "p", "o", str(path))
    assert res.returncode == 0
    assert captured['cmd'][0] == str(path)
    assert "student-net" in captured['input']


def test_resolve_cli_executable_bad_path(monkeypatch, tmp_path):
    bad = tmp_path / "doesnotexist.exe"
    with pytest.raises(SystemExit) as exc:
        vpn_auto._resolve_cli_executable(str(bad))
    assert "Cisco CLI not found" in str(exc.value)


def test_custom_group(monkeypatch, tmp_path):
    # ensure vpn_group parameter is honoured
    captured = {}

    def fake_run(cmd, input=None, **kwargs):
        captured['input'] = input
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    vpn_auto.call_cisco_cli("h", "u", "p", "o", None, vpn_group="staff-net")
    assert captured['input'].startswith("staff-net")


def test_load_config_no_file(monkeypatch, tmp_path):
    # if the configuration file is missing we should not raise, but we should
    # log a warning message
    monkeypatch.setattr(type(vpn_auto.CONFIG_PATH), "exists", lambda self: False)
    from io import StringIO
    oldout = sys.stdout
    sys.stdout = StringIO()
    try:
        vpn_auto.load_config()
        out = sys.stdout.getvalue()
    finally:
        sys.stdout = oldout
    assert "WARNING" in out


def test_main_success(monkeypatch, tmp_path):
    # prepare environment and monkeypatch
    monkeypatch.setenv("VPN_HOST", "h")
    monkeypatch.setenv("VPN_USER", "u")
    monkeypatch.setenv("VPN_PASS", "p")
    monkeypatch.setenv("OTP_SECRET", pyotp.random_base32())
    monkeypatch.delenv("CISCO_CLI_PATH", raising=False)

    fake = subprocess.CompletedProcess(args=["vpncli.exe"], returncode=0, stdout="connected", stderr="")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: fake)
    # avoid loading actual .env
    monkeypatch.setattr(vpn_auto, "load_config", lambda: None)

    # capture print output
    from io import StringIO
    oldout = sys.stdout
    olderr = sys.stderr
    sys.stdout = StringIO()
    try:
        vpn_auto.main()
        out = sys.stdout.getvalue()
    finally:
        sys.stdout = oldout
        sys.stderr = olderr

    assert "Connection attempt complete" in out


def test_main_failure(monkeypatch):
    monkeypatch.setenv("VPN_HOST", "h")
    monkeypatch.setenv("VPN_USER", "u")
    monkeypatch.setenv("VPN_PASS", "p")
    monkeypatch.setenv("OTP_SECRET", pyotp.random_base32())
    monkeypatch.delenv("CISCO_CLI_PATH", raising=False)
    fake = subprocess.CompletedProcess(args=["vpncli.exe"], returncode=1, stdout="", stderr="error")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: fake)
    monkeypatch.setattr(vpn_auto, "load_config", lambda: None)

    with pytest.raises(SystemExit) as exc:
        vpn_auto.main()
    assert exc.value.code == 1
