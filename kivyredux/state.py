class State(object):
    def __init__(self, **kwargs):
        for each_attribute in kwargs:
            setattr(State, each_attribute, kwargs[each_attribute])
    
    def get(self, key):
        return getattr(self, key)
    
    def update(self, key, value):
        if hasattr(self, key) and value:
            setattr(self, key, value)
    
    @staticmethod
    def get(key):
        return getattr(State,key)
    
    @staticmethod
    def update(key, value):
        if hasattr(State, key) and value:
            setattr(State, key, value)