from copy import deepcopy
from kivyredux.constants import ConnectionProps
class StoreWidgetInternalMapper(object):
    def __init__(self, *largs, **kwargs):
        self.__map_callbacks=[]
        self.__dispatch_object = {
            ConnectionProps.bind:{}, 
            ConnectionProps.init:{}
        }
        super(StoreMapper, self).__init__(*largs, **kwargs)
        self.connect()
        self.connect_store_to_children()

    def add_mapper(self, map_function):
        if map_function:
            self.__map_callbacks.append(lambda state, widget: map_function(state,widget))
    
    def bind_prop(self, new_prop):
        new_dispatch_object = deepcopy(self.__dispatch_object)
        bind_props = new_dispatch_object.get(ConnectionProps.bind)
        new_dispatch_object[ConnectionProps.bind] = {
            **bind_props,
            **new_prop
        }
        self.__dispatch_object = deepcopy(new_dispatch_object)
    
    def init_prop(self, new_prop):
        new_dispatch_object = deepcopy(self.__dispatch_object)
        init_prop = new_dispatch_object.get(ConnectionProps.init)
        new_dispatch_object[ConnectionProps.init] = {
            **init_prop,
            **new_prop
        }
        self.__dispatch_object = deepcopy(new_dispatch_object)

    def unbind_prop(self, prop_key):
        new_dispatch_object = deepcopy(self.__dispatch_object)
        if new_dispatch_object.get(ConnectionProps.bind).get(prop_key, None):
            del new_dispatch_object[ConnectionProps.bind][prop_key]
        self.__dispatch_object = deepcopy(new_dispatch_object)

    def dest_prop(self, prop_key):
        new_dispatch_object = deepcopy(self.__dispatch_object)
        if new_dispatch_object.get(ConnectionProps.init).get(prop_key, None):
            del new_dispatch_object[ConnectionProps.init][prop_key]
        self.__dispatch_object = deepcopy(new_dispatch_object)
    
    def mapper(self, state, widget):
        for each_mapper in self.__map_callbacks:
            each_mapper(state, widget)

    def dispatcher(self, dispatch, widget):
        return self.__dispatch_object
    
    def connect(self):
        pass

    def connect_store_to_children(self, widget=None):
        pass