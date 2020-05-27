import math
from mingus.containers import Track
import mingus.core.notes as notes
import mingus.core.keys as keys

class Song:
	instrument = "Electric Piano 1"	#instrument
	tempo = 120.0				#tempo in beats per minute
	notes = Track()				#Actual sequence of Notes (defined above)
	weights = None
	length = 16					#number of bars in the song
	key = "C"					#key of the song
	raw_song = []				#the song as a simple list of note/duration pairs
	
	def __init__(self):
		self.instrument = "Electric Piano 1"
		self.tempo = 120.0
		self.notes = Track()
		self.length = 16
		self.key = "C"
		self.raw_song = []
		self.weights = None
		