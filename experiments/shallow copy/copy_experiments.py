'''
	Example demonstrates that shallow copy.copy() firstly creates new instance with references to the
	old object, BUT allows rewriting values on the new object. The rewrite creates new address, i.e.
	does not have impact on the original object.
'''

import copy

class Key:

	def __init__(self):
		self.dict = { 'a' : 1, 'b' : 2 }
		self.list = [1, 1]
		self.string = 'This is Key'

	def __str__(self):
		return f"Instance of {self.__class__.__name__}\tInstance Addr:\t{hex(id(self))}\
			\n\tDict:\t{self.dict}\tList:\t{self.list}\tString:\t{self.string}\
			\n\tDict Addr:\t{hex(id(self.dict))}\tList Addr:\t{hex(id(self.list))}\tString Addr:\t{hex(id(self.string))}"
	


key = Key()
print(key)

grey_key = copy.copy(key)
print('***')
print(key)
print(grey_key)

grey_key.string = 'This is Grey Key'
print('***')
print(key)
print(grey_key)
