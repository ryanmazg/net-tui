import subprocess
import re
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class BluetoothDevice:
    """Represents a Bluetooth device."""

    mac_address: str
    name: str
    connected: bool


def _parse_device_line(line: str) -> Optional[dict]:
    """Parses a single line of output from 'bluetoothctl devices'."""
    match = re.match(r"Device (([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}) (.*)", line)
    if match:
        return {"mac_address": match.group(1), "name": match.group(3)}
    return None


def discover_new_devices(timeout: int = 8) -> bool:
    """
    Scans for new, discoverable Bluetooth devices for a set duration.
    This is a blocking operation.
    Returns True on success, False on failure.
    """
    print(f"Scanning for new devices for {timeout} seconds...")
    command = ["bluetoothctl", "--timeout", str(timeout), "scan", "on"]
    try:
        subprocess.run(
            command, capture_output=True, text=True, check=True, encoding="utf-8"
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error during Bluetooth discovery: {e}")
        return False


def scan_bluetooth_devices() -> Optional[List[BluetoothDevice]]:
    """
    Lists known (paired) Bluetooth devices and their connection status.
    Returns a list of BluetoothDevice objects or None if an error occurs.
    """
    try:
        all_devices_result = subprocess.run(
            ["bluetoothctl", "devices"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        connected_devices_result = subprocess.run(
            ["bluetoothctl", "devices", "Connected"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )

        connected_macs: Set[str] = set()
        for line in connected_devices_result.stdout.strip().split("\n"):
            parsed = _parse_device_line(line)
            if parsed:
                connected_macs.add(parsed["mac_address"])

        devices: List[BluetoothDevice] = []
        for line in all_devices_result.stdout.strip().split("\n"):
            parsed = _parse_device_line(line)
            if parsed:
                mac = parsed["mac_address"]
                devices.append(
                    BluetoothDevice(
                        mac_address=mac,
                        name=parsed["name"],
                        connected=(mac in connected_macs),
                    )
                )

        return devices

    except FileNotFoundError:
        print("Error: 'bluetoothctl' command not found. Is bluez-utils installed?")
        return None
    except subprocess.CalledProcessError as e:
        if "No default controller available" in e.stderr:
            return []
        print(f"Error executing bluetoothctl: {e}")
        print(f"Stderr: {e.stderr}")
        return None


if __name__ == "__main__":
    print("--- Testing Discovery (this will take a few seconds) ---")
    discover_new_devices(timeout=5)
    print("\n--- Listing All Known Devices ---")
    found_devices = scan_bluetooth_devices()
    if found_devices is not None:
        if not found_devices:
            print("No devices found. Is Bluetooth turned on and are devices paired?")
        for dev in found_devices:
            print(dev)
    else:
        print("An error occurred during scanning.")
