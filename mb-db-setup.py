# standalone script for setting up the database to store post data and read instrument data from

import sqlite3
import os
import sys
import re
from sqlite3 import Error

if(len(sys.argv) < 3):
	print("Usage: mb-db-setup.py dblocation soundfontlocation <weightfile>")
	sys.exit(1)
	
DB_LOCATION=sys.argv[1]
SOUNDFONT_LOCATION=sys.argv[2]
if(len(sys.argv) >= 4):
	WEIGHT_FILE = sys.argv[3]
else:
	WEIGHT_FILE = ""
	
if(not os.path.exists(SOUNDFONT_LOCATION)):
	print("Soundfont folder not found")
	sys.exit(1)
	
if(WEIGHT_FILE and not os.path.exists(WEIGHT_FILE)):
	print("Weight file not found")
	sys.exit(1)

def main():
	setup = not os.path.exists(DB_LOCATION)
	conn = create_connection(DB_LOCATION)
	newdb = False
	if(setup):
		setup_db(conn)
		newdb = True
	
	soundfonts=[f for f in os.listdir(SOUNDFONT_LOCATION) if f.endswith('.sf2')]
	cumulativeWeight = 0
	
	if(WEIGHT_FILE):
		#Read in weights from weight file
		file = open(WEIGHT_FILE, 'r')
		reg = re.compile(r'^\s*(.*)\s*:\s*(\d*)\s*$')
		lines = file.readlines()
		for line in lines:
			r = reg.search(line)
			name = r.group(1)
			fn = name + ".sf2"
			if(fn in soundfonts):
				weight = int(r.group(2))
				cumulativeWeight += weight
				fullpath = os.path.abspath(fn)
				insert_instrument(conn, name, fullpath, weight, cumulativeWeight)
			else:
				print(f'Instrument {fn} not found')
				
	else:
		#Go through each soundfont in the folder and ask for the weight individually
		print("not yet implemented, write a weight file pls")
		if(newdb):
			os.remove(DB_LOCATION)



def create_connection(path):
	connection = None
	try:
		connection = sqlite3.connect(path)
		print("Connection to SQLite DB successful")
	except Error as e:
		print(f"The error '{e}' occurred")

	return connection
	
def execute_query(connection, query):
	cursor = connection.cursor()
	try:
		cursor.execute(query)
		connection.commit()
		print("Query executed successfully")
	except Error as e:
		print(f"The error '{e}' occurred")


def setup_db(conn):
	create_instruments_table = """
		CREATE TABLE IF NOT EXISTS Instruments(
			instrumentID INTEGER PRIMARY KEY AUTOINCREMENT,
			instrumentName TEXT NOT NULL ,
			fileLocation TEXT NOT NULL ,
			pickWeight INTEGER NOT NULL,
			cumulativeWeight INTEGER NOT NULL
		);
		"""
	create_posts_table = """
		CREATE TABLE IF NOT EXISTS Posts
		(
			postID INTEGER PRIMARY KEY AUTOINCREMENT,
			seed INTEGER,
			tempo DOUBLE,
			Key TEXT,
			postTime TEXT,
			facebookPostID INTEGER,
			twitterPostID INTEGER,
			mastodonPostID INTEGER,
			instrumentID INTEGER,
			
			FOREIGN KEY (instrumentID) REFERENCES Instruments (instrumentID)
		);"""
	execute_query(conn, create_instruments_table)
	execute_query(conn, create_posts_table)
	
def insert_instrument(conn, name, fullpath, weight, cumWeight):
	insert_query = """
		INSERT INTO 
			instruments(instrumentName, fileLocation, pickWeight, cumulativeWeight)
		VALUES
			("{}", "{}", {}, {});
		""".format(name, fullpath, weight, cumWeight)
	execute_query(conn, insert_query)
	
if(__name__ == '__main__'):
	main()
