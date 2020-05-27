import json
import sys

class safeDict(object):
	def __init__(self, dict, default=None):
		self.dict = dict
		self.default = default
		
	def __getitem__(self, key):
		if key in self.dict:
			res = self.dict[key]
			if(type(res) == dict):
				return safeDict(res, self.default)
			return res
		return None


class Reader(object):
	def __init__(self, filename):
		with open(filename, 'r') as f:
			self.dict = safeDict(json.load(f))
	
	def __getitem__(self, key):
		return self.dict[key]

