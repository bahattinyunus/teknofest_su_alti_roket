"""
CLI Tool for Wireless Firmware Over-The-Air (FOTA) Flashing & Blackbox Retrieval
Allows field engineers to upload STM32 binary images directly to the ESP32-S3 Wi-Fi bridge
and pull down PSRAM blackbox logs without opening physical hull seals.
"""

import sys
import os
import zlib
import argparse
from pathlib import Path

def calculate_crc32(filepath: str) -> int:
    crc = 0
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF

def upload_firmware(bin_path: str, server_ip: str = "192.168.4.1", port: int = 80):
    if not os.path.exists(bin_path):
        print(f"[ERROR] Firmware file not found: {bin_path}")
        return False

    file_size = os.path.getsize(bin_path)
    crc32_val = calculate_crc32(bin_path)

    print("=== SUNGUR FOTA WIRELESS FLASHING UTILITY ===")
    print(f"Target AP IP:   http://{server_ip}:{port}")
    print(f"Binary File:    {bin_path}")
    print(f"Binary Size:    {file_size} bytes ({file_size / 1024:.2f} KB)")
    print(f"Package CRC32:  0x{crc32_val:08X}")

    url = f"http://{server_ip}:{port}/update"
    print(f"\nInitiating HTTP POST transfer to {url}...")

    # We use urllib to avoid external dependencies like requests
    import urllib.request
    import urllib.error

    try:
        with open(bin_path, 'rb') as f:
            data = f.read()

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/octet-stream",
                "X-Firmware-CRC32": f"{crc32_val:08X}",
                "Content-Length": str(len(data))
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            body = response.read().decode('utf-8', errors='ignore')
            print(f"[STATUS {status}] Response: {body}")
            if status == 200:
                print("\n[SUCCESS] Firmware uploaded and flashed over-the-air!")
                return True
    except urllib.error.URLError as e:
        print(f"\n[NETWORK ERROR] Could not connect to ESP32-S3 AP at {server_ip}: {e.reason}")
        print("Tip: Ensure your engineering PC is connected to Wi-Fi SSID 'ROCKET_FOTA_ACCESS_POINT'.")
        return False
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return False

def download_blackbox(output_csv: str = "blackbox_mission_log.csv", server_ip: str = "192.168.4.1"):
    import urllib.request
    url = f"http://{server_ip}/blackbox"
    print(f"Fetching Blackbox telemetry from {url}...")
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            content = resp.read()
            with open(output_csv, 'wb') as f:
                f.write(content)
        print(f"[SUCCESS] Blackbox log saved to {output_csv} ({len(content)} bytes)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fetch blackbox log: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Underwater Rocket FOTA & Blackbox CLI")
    parser.add_argument("binary", nargs="?", help="Path to compiled .bin firmware")
    parser.add_argument("--ip", default="192.168.4.1", help="ESP32-S3 Access Point IP")
    parser.add_argument("--download-blackbox", action="store_true", help="Download PSRAM blackbox log")
    args = parser.parse_args()

    if args.download_blackbox:
        download_blackbox(server_ip=args.ip)
    elif args.binary:
        upload_firmware(args.binary, server_ip=args.ip)
    else:
        parser.print_help()
