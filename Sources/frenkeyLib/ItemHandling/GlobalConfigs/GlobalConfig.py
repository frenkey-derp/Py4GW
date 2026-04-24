from typing import ClassVar, Self, cast


class GlobalConfig:
    '''
    A global configuration that is shared across the entire application. It is used to store settings and rules that are relevant to multiple parts of the application.
    
    All GlobalConfig instances are singletons, meaning that there will only be one instance of each config.
    This is because the configs are meant to be global and shared across the entire application, and having multiple instances would lead to confusion and bugs.
    The singleton pattern is implemented in a way that allows for easy subclassing, so that each specific config can have its own instance while still sharing the same base functionality.
    '''


    _initialized: bool = False    
    _instances: ClassVar[dict[type[Self], Self]] = {}

    def __new__(cls: type[Self]) -> Self:
        instance = cast(Self | None, cls._instances.get(cls))
        if instance is None:
            instance = cast(Self, super().__new__(cls))
            instance._initialized = False
            cls._instances[cls] = instance
        return instance
    
    def __init__(self: Self) -> None:
        if self._initialized:
            return
        
        self._initialized = True