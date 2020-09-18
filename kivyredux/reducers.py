class Reducer(object):
    '''
        Reducer class which handles the action and updates the state
    '''

    def __init__(self, id=None, reducer_cb=None):
        self.__id = id if id else self.__hash__()
        self.__reducer_function = reducer_cb 

    @property
    def id(self):
        return self.__id
    
    @property
    def reducer(self):
        return self.__reducer_function
    
    @reducer.setter
    def reducer(self, reducer_new_cb):
        if reducer_new_cb:
            self.__reducer_function = reducer_new_cb if reducer_new_cb else lambda state, widget: state