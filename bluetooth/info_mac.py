from mac_vendor_lookup import MacLookup

input_file = "mac_addresses.txt"

mac_lookup = MacLookup()
mac_lookup.update_vendors() # Update the local OUI database

# Read MAC addresses from file
with open(input_file, "r") as file:
	mac_addresses = [line.strip() for line in file]

for mac in mac_addresses:
	try:
		vendor = mac_lookup.lookup(mac)
		print(f"MAC address {mac} belongs to manufacturer: {vendor}")
	except KeyError:
		print(f"MAC address {mac} not found in the database.")

# Save the results to a file
with open("mac_vendor_info.txt", "a") as file:
	for mac in mac_addresses:
		try:
			vendor = mac_lookup.lookup(mac)
			file.write(f"MAC address {mac} belongs to manufacturer: {vendor}\n")
		except KeyError:
            		file.write(f"MAC address {mac} not found in the database.\n")
