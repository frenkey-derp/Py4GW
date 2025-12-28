from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog


class XunlaiVaultHandler:
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(XunlaiVaultHandler, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
    
    def Run(self):
        ''' Method to run the Xunlai Vault handler logic. Processing the generator. '''
        
        ConsoleLog(str(self.__class__.__name__), "Running ...")
        pass