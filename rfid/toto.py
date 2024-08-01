from py122u import nfc
import time
import pymysql

def read_data_mifare(reader):
	try:
		reader.connect()
		badge_data = []
		
		# Read all 16 sectors
		for sector in range(16):

			key_a = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
			reader.load_authentication_data(0x00, key_a)
			reader.authentication(sector * 4, 0x60, 0x00)
			sector_data = []

			for block_offset in range(4):
				block_number = sector * 4 + block_offset
				data = reader.read_binary_blocks(block_number, 16)
				sector_data.append(data)
			badge_data.append(sector_data, )
		print("Badge data read successfully.")
		return badge_data, reader.get_uid()
	except Exception as e:
		print(f"Error reading badge data: {e}")


def save_badge(badge_data, badge_id):
    print("Inserting data")
    connection = pymysql.connect(
		host="localhost",
		port="3306",
		user="raspoutine",
		passwd="l3tm31n###",
		database="OUR_DB")
	try:
		cursor = connection.cursor()

		insert_query = "INSERT INTO badge_infos (id, data) VALUES (%s, %s)"
		values = (badge_id, badge_data)
		try:
			cursor.execute(insert_query, values)
			connection.commit()
			print("Data inserted successfully.")
		except pymysql.IntegrityError as e:
			if e.args[0] == 1062:
				print("Duplicate entry detected. Data not inserted.")
			else:
				raise Exeception("Duplicate key")
	finally:
		cursor.close()
		connection.close()

reader = nfc.Reader()


print("Listening ...")

badge_data = []

while True:
	try:
		badge_data, uid = read_data_mifare(reader)
        print(badge_data, uid)
		if badge_data :
			save_badge(badge_data, uid)
			print("Listening ...")
	except:
		pass
	time.sleep(0.3)

