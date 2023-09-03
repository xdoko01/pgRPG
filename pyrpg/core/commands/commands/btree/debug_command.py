from abc import ABC, abstractmethod, abstractproperty

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    register(fnc=cmd_debug, alias=module_name)

def cmd_debug():
    pass

class CmdContext(ABC):
    
    @abstractproperty
    def bb_locals(self):
        pass
    
    @abstractproperty
    def bb_globals(self):
        pass

    @abstractmethod
    def get_init_time(self):
        '''Time when the running behavior was first visited - init.
        '''
        pass

    @abstractmethod
    def get_duration(self):
        '''How long is the behavior node running.
        '''
        pass

    @abstractmethod
    def get_tick_count(self):
        '''How many times the behavior was executed.
        '''
        pass
    
    @abstractmethod
    def get_keys_pressed(self):
        '''Return pressed keys.
        '''
        pass
      
    @abstractmethod
    def get_env_events(self):
        '''Return mouse and other action events.
        '''
        pass

class BTreeBlackboard(CmdContext):
     def __init__(self):
        pass


if __name__ == '__main__':

    bb = BTreeBlackboard()

