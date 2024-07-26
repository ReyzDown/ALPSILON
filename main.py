import argparse
import os
import subprocess
import time
import serial
import sys
from config import Config



def compile_sketch(sketch_dir):
    arduino_cli_path = "arduino-cli"

    compile_cmd = [arduino_cli_path, "compile", "--fqbn", "esp32:esp32:esp32", sketch_dir]

    try:
        print(f"Compiling {sketch_dir}...")
        subprocess.run(compile_cmd, check=True)
        print("Compilation successful!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during compilation: {e}")
        sys.exit(1)

def upload_sketch(sketch_dir, port):
    arduino_cli_path = "arduino-cli"

    upload_cmd = [arduino_cli_path, "upload", "-p", port, "--fqbn", "esp32:esp32:esp32", sketch_dir]

    try:
        print(f"Uploading {sketch_dir} to {port}...")
        subprocess.run(upload_cmd, check=True)
        print("Upload successful!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during upload: {e}")
        sys.exit(1)

def read_serial_data(port):
    print("Reading data from serial port...")
    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    print(line)
                    if line == "End Scan":
                        #print("Fin du scan")
                        exit(1)
    except serial.SerialException as e:
        print(f"An error occurred while reading data from the ESP32: {e}")

def main():
    parser = argparse.ArgumentParser(description="Upload sketches to ESP32")
    parser.add_argument("-m", "--mode", choices=["wifi", "bluetooth"], required=True, help="Mode to run (wifi or bluetooth)")
    parser.add_argument("-p", "--port", required=True, help="Serial port for the ESP32 (e.g., COM3 ou /dev/ttyUSB0)")
    parser.add_argument("-nb", "--number", type=int, default=10, help="Number of scans (default is 10)")
    parser.add_argument("-s", "--save", type=str, help="Save serial output in file.txt")

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    if args.mode == "wifi":
        sketch_dir = os.path.join(base_dir, "wifi")
    elif args.mode == "bluetooth":
        sketch_dir = os.path.join(base_dir, "bluetooth")

    #conf = Config()
    #if not conf.is_platform_installed():
    #    print("ESP32 platform not found. Installing...")
    #    conf.install_platform()
    #    if not conf.is_platform_installed():
    #        print("Failed to install ESP32 platform. Exiting.")
    #        return
    #
    #if not conf.is_dependency_installed():
    #    print("Required dependencies not found. Installing...")
    #    conf.install_dependencies()
    #    if not conf.is_dependency_installed():
    #        print("Failed to install required dependencies. Exiting.")
    #        return
    #   
    #conf.create_directory_and_copy_library()

    compile_sketch(sketch_dir)
    upload_sketch(sketch_dir, args.port)

    print("Waiting for the ESP32 to be ready...")
    time.sleep(5)

    print(f"Sending the number of scans ({args.number}) to the ESP32 via serial port {args.port}...")
    try:
        with serial.Serial(args.port, 115200, timeout=1) as ser:
            ser.write(f"{args.number}\n".encode())
            print("Number of scans sent successfully.")
    except serial.SerialException as e:
        print(f"An error occurred while sending data to the ESP32: {e}")

    read_serial_data(args.port)

if __name__ == "__main__":
    main()
