import jsonreader
import os
import random
from randomList import randomList

class InstrumentPicker(object):

	def __init__(self, fp):
		self.sfDir = fp
		self.infoFile = fp + "info.json"
		reader = jsonreader.Reader(self.infoFile)
		self.tags = reader["Available_tags"]
		self.list = reader["Instruments"]


	def Pick(self):
		mrl = randomList()
		mrl.add(True, 5)
		mrl.add(False, 95)
		ilist = []
		if(mrl.pickWeighted()):
			ilist = self.Find(["Meme"])
			print("Searching for Meme instruments")
		else:
			tags_to_use = []
			#chance to pick specifically a meme font
			if(mrl.pickWeighted()):
				tags_to_use.append("Percussion")		
			
			if(not mrl.pickWeighted()):
				tags_to_use.append("Melodic")
				
			irl = randomList()
			irl.add("Instrumental", 95)
			irl.add("Electronic", 95)
			irl.add("Vox", 20)
			irl.add("SFX", 15)
			tags_to_use.append(irl.pickWeighted())
			ilist = self.Exclude(self.Find(tags_to_use), "Meme")
			print("Searching for instruments with tags: " + str(tags_to_use))
			if(not ilist):
				print("No instrument found, retrying.")
				return self.Pick()
			
		return random.choice(ilist);

	#Returns a list of all instruments with a particular tag
	def Find(self, tag):
		results = []
		if(isinstance(tag, list)):
			for item in self.list:
				flag = True
				for t in tag:
					if(not t in item["tags"]):
						flag = False
				if(flag):
					results.append(item["name"])
		else:
			for item in self.list:
				if(tag in item["tags"]):
					results.append(item["name"])
				
		return results
		
	#takes in a list of instruments, and then returns the subset that do not contain a given tag
	def Exclude(self, instruments, tag):
		results = []
		for instr in instruments:
			item = self.Get(instr)
			if(not tag in item["tags"]):
				results.append(instr)
		return results
		
	
	def Get(self, name):
		for item in self.list:
			if(item["name"] == name):
				return item
		return None
		

	def Test(self):
		print("Soundfont Directory: " + self.sfDir)
		print("Info File: " + self.infoFile)
		i = 0
		used_tags = []
		tag_count = {}
		for tag in self.tags:
			tag_count[tag] = 0
			
		for item in self.list:
			if(not os.path.exists(self.sfDir + item["name"] + ".sf2")):
				print("ERROR - Instrument not found: " + item["name"])
				return
			for t in item["tags"]:
				if(not t in used_tags):
					used_tags.append(t)
				tag_count[t] = tag_count[t] + 1
			i = i + 1
			
		print(str(i) + " Instruments listed")
		for t in used_tags:
			if(not t in self.tags):
				print("Unlisted tag found: \'" + t + "\'")
		for t in self.tags:
			if(not t in used_tags):
				print("Tag \'" + t + "\' is listed but not used")
		print("Tag Counts:")
		for i in tag_count.items():
			print(i[0] + ": " + str(i[1]))
			
		print(self.Pick())
		return

	
if(__name__ == '__main__'):
	ip = InstrumentPicker("Soundfonts/")
	ip.Test()