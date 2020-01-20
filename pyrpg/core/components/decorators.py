class Memoize:
	"""
	Decorator adding caching of instances to the classes
	TODO - it would be nice to have function to limit the cache 
	(100 records max for example) - parameter of decorator and
	then start to rewrite some old records in cache.
	TODO - it would be nice to have some function to flush cache.
    Note:
    All above is implemented in @functools.lru_cache decorator.
	"""
	def __init__(self, func):
		self.func = func
		self._cache = {}

	def __call__(self, *args, **kwargs):
		if args not in self._cache:
			self._cache.update( {args : self.func(*args, **kwargs)} )  #memo[args[1]] = self.fn(*args, **kwargs)
		return self._cache.get(args) #[args[1]]	
