from stateMachine import State

@State
def Increment(value):
	return value + 1

@State
def Add(valueA, valueB):
	return valueA + valueB

@State
def ReturnOne():
	return 1

@State
def DisplayValue(value):
	print(value)

@State
class Test:
	def __init__(self, a, b=2):
		self.a = a
		self.b = b

	def __call__(self, c, d=3):
		print(self.a)
		print(self.b)
		print(c)
		print(d)
