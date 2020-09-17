class Action(object):

    def __init__(self, action_type, **kwargs):
        self.__type = action_type
        self.data = kwargs if kwargs else {}
            
    @property
    def type(self):
        return self.__type
    
    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, kwargs):
        self.__data = kwargs

    def __repr__(self):
        return '<Action type={}>'.format(self.type)