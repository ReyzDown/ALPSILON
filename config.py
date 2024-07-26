import subprocess


class Config:

    def install_dependencies():
        try:
            print("Updating package list...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            print("Installing libstdc++6...")
            subprocess.run(["sudo", "apt-get", "install", "-y", "libstdc++6"], check=True)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while installing dependencies: {e}")

    def create_directory_and_copy_library():
        try:
            print("Creating directory for the library...")
            subprocess.run(["sudo", "mkdir", "-p", "/home/marouane/snap/arduino-cli/53/.arduino15/packages/esp32/tools/xtensa-esp32-elf-gcc/gcc8_4_0-esp-2021r2-patch5/lib/"], check=True)
            print("Copying libstdc++.so.6 to the directory...")
            subprocess.run(["sudo", "cp", "/usr/lib/x86_64-linux-gnu/libstdc++.so.6", "/home/marouane/snap/arduino-cli/53/.arduino15/packages/esp32/tools/xtensa-esp32-elf-gcc/gcc8_4_0-esp-2021r2-patch5/lib/"], check=True)
            print("Library copied successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while creating directory or copying library: {e}")

    def is_dependency_installed():
        print("Checking if libstdc++6 is installed...")
        result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
        return "libstdc++.so.6" in result.stdout

    def install_platform():
        try:
            print("Updating Arduino CLI core index...")
            subprocess.run(["arduino-cli", "core", "update-index"], check=True)
            print("Installing ESP32 platform...")
            subprocess.run(["arduino-cli", "core", "install", "esp32:esp32"], check=True)
            print("ESP32 platform installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while installing the platform: {e}")

    def is_platform_installed():
        print("Checking if ESP32 platform is installed...")
        result = subprocess.run(["arduino-cli", "core", "list"], capture_output=True, text=True)
        return "esp32:esp32" in result.stdout