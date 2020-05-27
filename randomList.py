import random
import types

def main():
	dict = {}
	rl = randomList()
	rl.add(1, 10)
	rl.add(2, 10)
	rl.add(3, 50)
	rl.add(4, 30)
	rl.add(5, 10)
	
	rl2 = randomList()
	rl2.add(6, 100)
	rl2.add(7, 100)
	rl2.add(8, 100)
	l = []
	l.append(9)
	l.append(10)
	l.append(11)
	l.append(12)
	rl.add(rl2, weight=20, recursive = False)
	rl.add(l, 20)
	
	
	
	for i in range(0, 100000):
		res = rl.pickNormal(recursive = True)
		if(res in dict):
			dict[res] = dict[res] + 1
		else:
			dict[res] = 1
	
	for i in sorted (dict.keys()):
		print(str(i) + ":" + "{0:.2f}".format(dict[i]/1000) + "%")
	print(rl.normalisedWeights())

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))
	


#Class for picking items randomly from a list in various ways
#Works recursively, meaning another randomlist can be added in to 
#nest probablities inside each other, so to speak
class randomList:
	list = []
	size = 0
	total = 0
	defaultweight = 1
	
	def __init__(self):
		self.list = []
		self.size = 0
		self.total = 0
		self.defaultweight = 1
		
	def add(self, item, weight=0, maxDepth=0, recursive=False):
		if(weight <= 0):
			weight = self.defaultweight
		if(recursive):
			maxDepth = 1000
		if(type(item) == list and maxDepth > 0):
			for i in item:
				self.add(i, weight, maxDepth - 1 )
		elif(type(item) == randomList and maxDepth > 0):
			for i in item.list:
				self.add(i[0], i[1])
		else:				
			if(self.contains(item)):
				i = self.index(item)
				r = self.list[i]
				self.list[i] = (r[0], r[1] + weight)
				self.total += weight
			else:
				self.list.append((item, weight))
				self.total += weight
				self.size += 1	
			
	def index(self, item):
		for i in self.list:
			if(i[0] == item):
				return self.list.index(i)
		return -1
		
	def contains(self, item):
		for i in self.list:
			if(i[0] == item):
				return True
		return False
		
	def setDefaultWeight(self, n):
		self.defaultweight = n
	
		
	def remove(self, item):
		#removes an item from the list
		for i in self.list:
			if(i[0] == item):
				self.total = self.total - i[1]
				self.list.remove(i)
		self.size -= 1
				
	def pickWeighted(self, maxDepth=0, recursive = False):
		if(self.list == []):
			return None
		#picks a random element from the list based on the relative weight of each element
		if(recursive):
			maxDepth = 1000
		n = random.uniform(0.0, self.total)
		c = 0;
		for i in self.list:
			c = c + i[1]
			if(n < c):
				if(maxDepth > 0):
					#If the item is also randomList, pickWeighted from that and return the result
					if(type(i[0]) == randomList):
						return i[0].pickWeighted(maxDepth - 1)
					if(type(i[0]) == list):
						#if the result is a regular list, pick one at random from the list
						return random.choice(i[0])
				return i[0]
		return None
		
	def normalisedWeights(self, recursive=True):
		#Returns the list with weights normalised to total 1
		newList = []
		for i in self.list:
			if(type(i[0]) == randomList and recursive):
				l = i[0].normalisedWeights(recursive)
				for j in l:
					newList.append((j[0], (j[1]*i[1])/self.total))
			elif(type(i[0]) == list and recursive):
				for j in i[0]:
					newList.append((j, (i[1]/len(i[0]))/self.total))
			else:
				newList.append((i[0], i[1]/self.total))
		return newList
		
	def pickUniform(self, maxDepth=0, recursive = False):
		if(self.list == []):
			return None
		if(recursive):
			maxDepth = 1000
		#picks a random element uniformly
		result = random.choice(self.list)[0]
		if(maxDepth > 0):
			if(type(result) == randomList):
				#if the result is a randomList, pickUniform that and return the result
				return result.pickUniform(maxDepth - 1)
			if(type(result) == list):
				#if the result is a regular list, pick one at random from the list
				return random.choice(list)
		return result
		
	def pickNormal(self, mu = 0.5, sigma = 0.25, maxDepth = 0, recursive = False):
		if(self.list == []):
			return None
		if(recursive):
			maxDepth = 1000
		#picks a random element with a normal distribution
		n = -1
		while(n < 0 or n > self.size - 1):
			n = int(round(random.gauss((self.size - 1) * mu, self.size* sigma)))
		result = self.list[n][0]
		if(maxDepth > 0):
			if(type(result) == randomList):
				return result.pickNormal(maxDepth=maxDepth - 1)
			if(type(result) == list):
				#if the result is a regular list, pick one at random from the list
				return random.choice(result)
		return result
		
	
		
		
if(__name__ == '__main__'):
	main()