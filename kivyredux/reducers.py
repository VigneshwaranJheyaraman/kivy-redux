class Reducer(object):
    '''
        Reducer class which handles the action and updates the state
    '''

    def __init__(self, id, reducer_cb=None):
        self.__id = id
        self.__state ={}
        self.reducer = reducer_cb 

    @property
    def id(self):
        return self.__id
    
    @property
    def reducer(self):
        return self.__reducer_function
    
    @reducer.setter
    def reducer(self, reducer_new_cb):
        if reducer_new_cb:
            self.__reducer_function = reducer_new_cb else lambda state, widget: state
    
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, new_state):
        if new_state:
            self.__state = new_state