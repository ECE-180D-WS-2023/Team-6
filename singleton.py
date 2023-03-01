class Singleton:
	"""
		Singleton pattern.
		Overload only class that must have one instance.
		Stores the instance in a static variable: Class.instance
		(Check Singleton design pattern for more info)
	"""
	def __new__(cls,*args,**kwargs):
		if not hasattr(cls, 'instance'):
			cls.instance = super(Singleton, cls).__new__(cls)
		return cls.instance
