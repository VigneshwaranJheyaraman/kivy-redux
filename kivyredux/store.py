from kivyredux.reducers import Reducer
from kivyredux.error import NotReducerType, NoWidgetConnected
from kivyredux.state import State
from kivyredux.constants import StoreProps, ConnectionProps
from copy import deepcopy
class Store(object):
    '''
        This class creates a common store object with maps Kivy's widget properties with state 
        and updates the store based on the dispatch actions associated with the widget properties
    '''
    def __init__(self, reducers=[], state=State()):
        '''
            @param reducers = List of Reducer objects
            @param state = State if user defined to provide one
        '''
        self.__store_reducers = {}
        self.__store = state
        for each_reducer in reducers:
            if type(each_reducer) != Reducer:
                raise NotReducerType("Expected a Reducer object got an {}".format(type(each_reducer)))
            self.__store_reducers[each_reducer.id] = each_reducer.reducer
        self.__widgets_connections = {}
        self.__widget_connection_object = {
            StoreProps.mapping:[],
            StoreProps.binding:[]
        }
        self.__map_property_object = {
            StoreProps.map_cb:None, 
        }
        self.__bind_property_object = {
            StoreProps.bind_prop:None, 
            StoreProps.bind_dispatch:None, 
            StoreProps.bind_bounded:False
        }
    
    @property
    def state(self):
        return self.__store
    
    @property
    def connections(self):
        return self.__widgets_connections
    
    def add_mapping_binding(self, widget=None, mapper=None, dispatcher=None, replace_mapping=False, replace_bind=False):
        '''
            Updates the mapping and binding properties with the existing connections for specific widget
            @param widget: the widget to update the properties
            @param mapper: new mapper function to add
            @param dispatcher : new dispatcher function to add of format {
                'bind':{
                    //props to be binded
                }
            }
            @replace_mapping: should replace exisiting mappings defaults to False
            @replace_bind: should replace exisiting bindings defaults to False
        '''
        if not widget:
            raise NoWidgetConnected("Expected Widget object got {} object".format(type(widget)))
        if not self.connections.get(widget, None):
            raise NoWidgetConnected("Cannot map or bind with None object first connect the store with the Widget")
        if dispatcher and ConnectionProps.init in dispatcher:
            del dispatcher[ConnectionProps.init]
        self.__update_connections(widget, mapper, dispatcher, replace_map, replace_bind)
    
    def __add_widget_mappers(self, widget_connections, new_mapper, replace =False):
        '''
            Updates the mapping functions for the specific widgets
            @param widget_connections: existing_mapping
            @param new_mapper: new mapping function to be added
            @param replace: replace the existing mapping with the new mapping
        '''
        previously_mapped_functions = [] if replace else widget_connections.get(StoreProps.mapping, [])
        new_mapper_object = deepcopy(self.__map_property_object)
        new_mapper_object[StoreProps.map_cb] = new_mapper
        widget_connections[StoreProps.mapping] = previously_mapped_functions.append(new_mapper_object)
        return widget_connections
    
    def __add_widget_binders(self, widget, widget_connections, new_bind_props, replace=False):
        '''
            Adds widget binding props
            @param widget: widget to bind the property
            @param widget_connections: internal widget exisiting connections
            @param new_bind_props: newly yet be added binded props
            @param replace: replaces the exisisting_binding by unbinding already binded props
        '''
        update_bind_properties = []
        for each_prop in new_bind_props:
            new_bind_property = deepcopy(self.__bind_property_object)
            new_bind_property[StoreProps.bind_prop] = each_prop
            new_bind_property[StoreProps.bind_dispatch] = new_bind_props[each_prop]
            update_bind_properties.append(new_bind_property)
        if replace:
            for previously_binded_props in widget_connections[StoreProps.binding]:
                widget.unbind(**{
                    previously_binded_props.get(StoreProps.bind_prop): previously_binded_props.get(StoreProps.bind_dispatch)
                })
            widget_connections[StoreProps.binding] = update_bind_properties
        else:
            widget_connections[StoreProps.binding]+= update_bind_properties
        return widget_connections
    
    def __bind_props_with_widget(self, widget, widget_dispatch_props):
        '''
            Bind the properties with dispatch_props
            @param widget:widget to bind with
            @widget_dispatch_props: internal widget's binded properties
        '''
        for prop in widget_dispatch_props:
            if not prop.get(StoreProps.bind_bounded):
                widget.bind(**{prop.get(StoreProps.bind_prop): prop.get(StoreProps.bind_dispatch)})
                prop[StoreProps.bind_bounded] = True
        return widget_dispatch_props                

    def __connect(self, mapper=None, dispatcher =None, widget):
        '''
            Establish a connection with widget [Internal]
            @param mapper:mapping function defaults to None
            @param dispatcher:dispatcher function defaults to None
            @param widget:widget to connect to the store [@REQUIRED]
        '''
        self.__update_connections(
            widget=widget,
            mapper=mapper,
            dispatcher=dispatcher
        )
        return widget
        
    def connect(self, mapper=None, dispatcher=None, widget=None):
        '''
            Function to connect store with widget
        '''
        if not widget:
            raise NoWidgetConnected("Excepted Widget type object instead got".format(type(widget)))
        if type(widget).__name__ == "function":
            #its a functional component
            return lambda *largs, **kwargs : self.__connect(mapper, dispatcher, widget(*largs, **kwargs))
        else:
            return self.__connect(mapper, dispatcher, widget)
        
    def __dispatch(self, action):
        '''
            Dispatches the action to reducers collection
            @param action: action of type Action
        '''
        self.__update_state_with_reducer(action)
        self.__map_state_with_widgets()
    
    def __map_state_with_widgets(self):
        '''
            Calls the mapping function call back and updates all widgets with state
        '''
        widgets_list = self.__widgets_connections
        for widget in widgets_list:
            mapped_callbacks =widgets_list[widget].get(StoreProps.mapping)
            for map_function in mapped_callbacks:
                map_function.get(StoreProps.map_cb) and map_function.get(StoreProps.map_cb)(self.state, widget)

    def __update_state_with_reducer(self, action):
        '''
            From the list of reducers calls all the reducers with specified action
            @param action:action to be invoked
        '''
        reducers_list = self.__store_reducers
        for each_reducer in reducers_list:
            self.__store = reducers_list[each_reducer].reducer(action, self.state)
    
    def __update_connections(self, widget, mapper=None, dispatcher=None, replace_map=False, replace_bind=False):
        widget_connections = self.connections.get(widget, None)
        if not widget_connections:
            widget_connections = deepcopy(self.__widget_connection_object)
        if mapper:
            widget_connections = self.__add_widget_mappers(widget_connections, mapper, replace_map)
            mapper(self.state, widget)
        if dispatcher:
            dispatch_properties = dispatcher(self.__dispatch, widget)
            bind_props = dispatch_properties.get(ConnectionProps.bind,{})
            init_props = dispatch_properties.get(ConnectionProps.init, {})
            for initializer in init_props:
                setattr(widget, initializer, init_props[initializer])
            widget_connections = self.__add_widget_binders(widget, widget_connections, bind_props, replace_bind)
            widget_connections[StoreProps.binding]= self.__bind_props_with_widget(widget, widget_connections.get(StoreProps.binding))
        self.__widgets_connections[widget] = widget_connections