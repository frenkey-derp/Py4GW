import Py4GW

MODULE_NAME = "Test"

def on_enable():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} loaded successfully.")

def on_disable():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} unloaded successfully.")
    
def configure():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} configuration opened.")
    
def draw():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} drawing UI.")
    
def update():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} updating state.")

def main():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} running.")
    
    
# These functions need to be available at module level
__all__ = ['on_enable', 'on_disable', 'configure', 'draw', 'update', 'main']

if __name__ == "__main__":
    main()
