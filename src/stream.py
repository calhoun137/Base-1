class Stream:
    """
    A Physical Input Register.
    Holds one term of 'Mass' in memory explicitly.
    """
    def __init__(self, generator):
        self._gen = generator
        self._head = None
        self._fill() # Charge the register

    def _fill(self):
        try:
            self._head = next(self._gen)
        except StopIteration:
            self._head = None # The End of the Universe

    @property
    def head(self):
        """Observation (Cost: 0 mass)"""
        return self._head

    def consume(self):
        """Consumption (Cost: Irreversible Time)"""
        if self._head is None:
            raise StopIteration("Stream is exhausted")
        
        val = self._head
        self._fill()
        return val
    
    # Python Iterator Compatibility
    def __iter__(self): return self
    def __next__(self): return self.consume()
