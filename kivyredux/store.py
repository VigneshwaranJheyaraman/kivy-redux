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
            self.add_reducer(each_reducer)
        self.__widgets_connections = {}
        self.__num_of_connections =0
        self.__widget_connection_object = {
            StoreProps.mapping:[],
            StoreProps.binding:[],
            StoreProps.widget:None
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
        if not hasattr(widget, StoreProps.widget_key) or not self.connections.get(getattr(widget, StoreProps.widget_key), None):
            raise NoWidgetConnected("Cannot map or bind with None object first connect the store with the Widget")
        if dispatcher and ConnectionProps.init in dispatcher:
            del dispatcher[ConnectionProps.init]
        self.__update_connections(widget, mapper, dispatcher, replace_map=replace_mapping, replace_bind=replace_bind)
    
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
        previously_mapped_functions.append(new_mapper_object)
        widget_connections[StoreProps.mapping] = previously_mapped_functions
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
    
    def add_reducer(self, new_reducer):
            '''
                Adds a reducer to the reducer's collection
                @param new_reducer: new Reducer object to be added to store
            '''
            if type(new_reducer) != Reducer:
                raise NotReducerType("Expected a Reducer object got an {}".format(type(new_reducer)))
            if new_reducer.id in self.__store_reducers:
                raise KeyError("The reducer {} already exists".format(new_reducer.id))
            self.__store_reducers[new_reducer.id] = new_reducer.reducer

    def __bind_props_with_widget(self, widget, widget_dispatch_props):
        '''
            Bind the properties with dispatch_props
            @param widget:widget to bind with
            @widget_dispatch_props: internal widget's binded properties
        '''
        for prop in widget_dispatch_props:
            if not prop.get(StoreProps.bind_bounded):
                dispatch_function = prop.get(StoreProps.bind_dispatch)
                if not dispatch_function:
                    raise AttributeError("Expected function got {} object check the function with property".format(type(dispatch_function)))
                widget.bind(**{prop.get(StoreProps.bind_prop): dispatch_function})
                prop[StoreProps.bind_bounded] = True
        return widget_dispatch_props

    def __connect(self, widget, mapper=None, dispatcher =None):
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
        self.__num_of_connections+=1
        return widget
        
    def connect(self, mapper=None, dispatcher=None, widget=None):
        '''
            Function to connect store with widget
        '''
        if not widget:
            raise NoWidgetConnected("Excepted Widget type object instead got {}".format(type(widget)))
        if "function" in str(widget):
            #its a functional component
            new_widget = lambda *largs, **kwargs:self.__connect(
                widget=widget(*largs, **kwargs),
                mapper=mapper,
                dispatcher=dispatcher,
            )
            new_widget.__qualname__ = widget.__name__
            return new_widget
        elif "class" in str(widget):
            store_connector = self.__connect
            def init_function(self, **kwargs):
                super(new_class, self).__init__(**kwargs)
                store_connector(
                    mapper=mapper, 
                    dispatcher=dispatcher, 
                    widget=self
                )
            widget_name = widget.__name__
            if hasattr(widget, StoreProps.widget_name_prop):
                widget_name = widget.__widget__
            new_class= type(widget_name, (widget, ), {
                '__init__':lambda self, **kwargs: init_function(self, **kwargs)
            })
            return new_class
        else:
            return self.__connect(
                mapper=mapper,
                dispatcher=dispatcher,
                widget=widget,
            )

        
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
            widget_comp = widgets_list[widget].get(StoreProps.widget)
            for map_function in mapped_callbacks:
                map_function.get(StoreProps.map_cb) and map_function.get(StoreProps.map_cb)(self.state, widget_comp)

    def __update_state_with_reducer(self, action):
        '''
            From the list of reducers calls all the reducers with specified action
            @param action:action to be invoked
        '''
        reducers_list = self.__store_reducers
        for each_reducer in reducers_list:
            self.__store = reducers_list[each_reducer](action, self.state)
    
    def __update_connections(self, widget, mapper=None, dispatcher=None, replace_map=False, replace_bind=False):
        if not hasattr(widget, StoreProps.widget_key):
            setattr(widget, StoreProps.widget_key, self.__num_of_connections)
        widget_connections = self.connections.get(getattr(widget, StoreProps.widget_key), None)
        if not widget_connections:
            widget_connections = deepcopy(self.__widget_connection_object)
        if mapper:
            widget_connections = self.__add_widget_mappers(widget_connections, mapper, replace_map)
            mapper(self.state, widget)
        if dispatcher:
            dispatch_properties = dispatcher(self.__dispatch, widget)
            if not dispatch_properties:
                raise NotImplementedError("Requires some thing to bind with dispatcher object not empty")
            bind_props = dispatch_properties.get(ConnectionProps.bind,{})
            init_props = dispatch_properties.get(ConnectionProps.init, {})
            for initializer in init_props:
                widget.create_property(initializer, init_props[initializer])
            widget_connections = self.__add_widget_binders(widget, widget_connections, bind_props, replace_bind)
            widget_connections[StoreProps.binding]= self.__bind_props_with_widget(widget, widget_connections.get(StoreProps.binding))
        widget_connections[StoreProps.widget] = widget
        self.__widgets_connections[getattr(widget, StoreProps.widget_key)] = widget_connections