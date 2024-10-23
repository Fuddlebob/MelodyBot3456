import jsonreader
import sqlite3
import os
import sys
import re
from sqlite3 import Error
import random



class InstrumentPicker(object):

	def __init__(self, conn):
		self.conn = conn


	def Pick(self):
		cur = self.conn.cursor()
		#find highest weight in table
		maxweight = cur.execute("""
			SELECT 
				cumulativeWeight
			FROM 
				'Instruments' 
			ORDER BY 
				cumulativeWeight DESC 
			LIMIT 1
			;""").fetchone()[0]
		#generate random number from 0 - maxweight
		rand = random.randint(0, maxweight-1)
		#find lowest instrument w/ cumulativeWeight above that number
		result = cur.execute("""
			SELECT
				instrumentName,
				fileLocation
			FROM
				'Instruments'
			WHERE
				cumulativeWeight > {}
			ORDER BY
				cumulativeWeight ASC
			LIMIT 1
		""".format(rand)).fetchone()
		#return name and filepath of that instrument
		
		return result


