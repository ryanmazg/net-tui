import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WiFiNetwork:
    """Represents a WiFi network."""

    bssid: str
    ssid: str
    signal: int
    security: str
    in_use: bool


def scan_wifi_networks() -> Optional[List[WiFiNetwork]]:
    """
    Scans for available WiFi networks using nmcli.

    Returns a list of WiFiNetwork objects or None if an error occurs.
    """
    command = [
        "nmcli",
        "-t",
        "-f",
        "BSSID,SSID,SIGNAL,SECURITY,IN-USE",
        "device",
        "wifi",
        "list",
    ]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding="utf-8"
        )

        networks = []
        output_lines = result.stdout.strip().split("\n")

        for line in output_lines:
            parts = line.strip().split(":")

            if len(parts) < 8:
                continue

            # Parse results from nmcli
            bssid_parts = [p.replace("\\", "") for p in parts[0:6]]
            bssid = ":".join(bssid_parts)

            other_fields = parts[6:]

            ssid = other_fields[0].replace("\\:", ":")
            signal_str = other_fields[1]
            security = other_fields[2] if len(other_fields) > 2 else "Unknown"
            in_use_str = other_fields[3] if len(other_fields) > 3 else ""

            networks.append(
                WiFiNetwork(
                    bssid=bssid,
                    ssid=ssid or "Hidden Network",
                    signal=int(signal_str),
                    security=security,
                    in_use=(in_use_str == "*"),
                )
            )

        return networks

    except FileNotFoundError:
        print("Error: 'nmcli' command not found. Is NetworkManager installed?")
        return None
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Error processing nmcli output: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            print(f"Stderr: {e.stderr}")
        return None


if __name__ == "__main__":
    print("Scanning for WiFi networks...")
    found_networks = scan_wifi_networks()
    if found_networks:
        for net in found_networks:
            print(net)
