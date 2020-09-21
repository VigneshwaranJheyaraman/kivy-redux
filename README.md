# Kivy Redux
[kivyredux](https://github.com/VigneshwaranJheyaraman/kivy-redux) is a python package, which allows to implement the [Redux](https://react-redux.js.org/)'s like implementation done on Kivy inspired from [Kovak's redux implementation](https://github.com/Kovak/Kivy-Redux-TodoList)

## Installation
Use the [pip](https://pip.pypa.io/en/stable/) package manager to install the kivy-redux package
```bash
pip install kivyredux
```

## Requirement
kivy-redux requires a python of version on or later 3.x i.e., python>=3.x

## Components
* ### State
  * **State** object lets you create a simple State similar to dictionary except it has stores them as attributes
    * *get* to get a requested attribute from state (instance method)
    * *update* to update a particular attribute within the state (instance method)
    * #### Static methods
        * *get_key* get a common attribute inside a State object
        * *update_key* update a common attribute within the state object
* ### Action
  * **Action** class lets you create actions for every dispatch to be mapped
    * Action(action_type, **data_to_be_used_by_action)
        * data_to_be_used_by_action are created as an dictionary of data used by the Action instance - action.data @property
        --- Defaults to empty dictionary
        * action_type - identifier of action
* ### Reducer
  * **Reducer** class lets you create a reducer object to be passed to Store for updating the state
    * Reducer(reducer_id, reducer_cb)
        * reducer_id unique identifier for the reducer
        --- Defaults to a random string
        * reducer_cb Callback function to be associated with the reducer instance
        --- Defaults to `None`
* ### Store
    * **Store** is the common store class which allows to handle connection with all the widgets and their properties being binded and mapped with state for updates
     * Store(reducers, state)
        * reducers is the collection of reducers that are associated with callback
        -- Defaults to an empty collection
        * state is the state which the store will handle with the dispatch of action within widgets and maps the state of widget properties with updated state
        --- Defaults to and empty State object
        * #### Instance Methods
            * connect(mapper, dispatcher, widget)
                * mapper -> mapping function for widget props whenever state is updated
                --- Defaults to `None`
                * dispatcher -> binded with the widget's property and dispatches the action for any property 
                changes
                --- Defaults to `None`
                    * Function parameter -> dispatch_function, widget
                    * Function to return 
                    ```javascript
                        {
                            bind:{
                                prop_name:lambda *largs, **kwargs: dispatch_function(prop_action)
                            },
                            init:{
                                prop_name:initial_value
                            } // new properties for the widget
                        }
                    ```
                * widget -> Widget to bind with store
            * add_mapping_binding(widget, new_mapper, new_dispatcher, replace_mapping, replace_binding)
                * widget -> Widget to insert additional mapping and binding function
                * new_mapper -> new mapping function
                -- Defaults to `None`
                * new_dispatcher -> new dispatch function **Similar to connect function**
                -- Defaults to `None`
                * replace_mapping -> replace the exisiting mapping function with new_mapping
                --- Defaults to `False`
                * replace_binding -> unbind all initially binded properties and bind newly dispatched proeprties
                --- Defaults to `False`
            * add_reducer(new_reducer)
                *new_reducer -> new reducer to be added to reducer's connection
                --- Must be of **Reducer** type

## Usage
```python
#store.py
from kivyredux import State, Store, Action, Reducer
common_state = State(saying_hi=False, saying_bye=True) #Can also user [common_state={}]
def sample_reducer(action, state=common_state):
    if action.type == 'HI':
        previous_value = state.get('saying_hi')
        state.update('saying_hi', not previous_value)
    elif action.type == 'BYE':
        previous_value =state.get('saying_bye')
        state.update('saying_bye', not previous_value)
    else:
        pass
    return state
hi_bye_reducer = Reducer(reducer_cb=sample_reducer)
hi_action = Action(action_type='HI')
bye_action = Action(action_type='BYE')
common_store = Store(reducers=[hi_bye_reducer], state=common_state)
#sample widget
#hi_bye.kv
'''
#:kivy 1.1.0
<HiClass>:
    text:'HI' if self.hi else 'Bye'
#Functional component cannot be specified with basic props
#i.e.,
#<ByeFunction>:
#    color:[1,1,1,1] #doesn't work
'''
#hi.py
from kivy.uix.label import Label
from kivy.lang.builder import Builder
from .store import common_store, hi_action, bye_action
#class components
Builder.load_file('hi_bye.kv')
class Hi(Label):
    '''
        Class component which inherits Label widget
    '''
    __widget__ = 'HiClass' # [IMPORTANT] to map with .kv file's name
    pass

def mapper(state, widget):
    #Maps Hi
    widget.hi = state.get('saying_hi')

def dispatcher(dispatch, widget):
    #dispatches hi action
    return {
        'bind':{
            'hi':lambda *largs, **kwargs: dispatch(hi_action)
        },
        'init':{
            'hi':False
        }
    }

HiClass= common_store.connect(mapper, dispatcher, Hi)#class component created

def bye_mapper(state,widget):
    #Maps bye
    widget.bye = state.get('saying_bye')

def bye_dispatcher(dispatch, widget):
    #Dispatches bye action
    return {
        'bind':{
            'bye':lambda *largs, **kwargs: dispatch(bye_action)
        },
        'init':{
            'bye':True
        }
    }

def ByeFunction(*largs, **kwargs):
    '''
        Functional component which returns a Label widget
    '''
    return Label(**kwargs)

ByeFunction = cs.connect(bye_mapper, bye_dispatcher, ByeFunction)#Functional component created
#main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from .hi import HiClass, ByeFunction
from kivy.factory import Factory
class HBContainer(BoxLayout):
    pass

class HBApp(App):
    def build(self):
        Factory.register('ByeFunction', cls=ByeFunction)
        Factory.register('HiClass', cls=HiClass)
        return HBContainer()

#hb.kv
'''
<HBContainer>:
    HiClass:
    ByeFunction:
        text:'Bye' if self.bye else 'Hi'
'''
```
## License
[MIT](https://github.com/VigneshwaranJheyaraman/kivy-redux/LICENSE)