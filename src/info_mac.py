from mac_vendor_lookup import MacLookup



class InfoMac:

	mac_lookup = MacLookup()
#	mac_lookup.update_vendors() # Update the local OUI database



	def __init__(self, mac):
		# Save the results to a file
		with open("./src/mac_vendor_info.txt", "a") as file:
			try:
				vendor = self.mac_lookup.lookup(mac)
				file.write(f"MAC address {mac} belongs to manufacturer: {vendor}\n")
			except KeyError:
						file.write(f"MAC address {mac} not found in the database.\n")
