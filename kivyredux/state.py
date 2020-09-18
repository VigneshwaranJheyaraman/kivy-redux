class State(object):
    def __init__(self, **kwargs):
        for each_attribute in kwargs:
            setattr(self, each_attribute, kwargs[each_attribute])
    
    def get(self, key):
        return getattr(self, key)
    
    def update(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
    
    @staticmethod
    def get_key(key):
        return getattr(State,key)
    
    @staticmethod
    def update_key(key, value):
        if hasattr(State, key):
            setattr(State, key, value)