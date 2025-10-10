import ctypes
import os
import sys
import datetime

def log(msg):
    with open("set_title.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")

def set_window_title(hwnd, new_title):
    SetWindowTextW = ctypes.windll.user32.SetWindowTextW
    SetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    SetWindowTextW.restype = ctypes.c_int

    result = SetWindowTextW(hwnd, ctypes.c_wchar_p(new_title))
    return result

if __name__ == "__main__":
    log(f"Arguments received: {sys.argv}")

    if len(sys.argv) != 3:
        log("Usage error: expected 2 arguments (hwnd and title)")
        sys.exit(1)

    hwnd_str = sys.argv[1]
    new_title = sys.argv[2]

    try:
        hwnd = int(hwnd_str, 0)
        log(f"Parsed hwnd: {hwnd}")
    except ValueError:
        log(f"Invalid hwnd value: {hwnd_str}")
        sys.exit(1)

    result = set_window_title(hwnd, new_title)
    if result != 0:
        log(f"Title set successfully to '{new_title}'")
    else:
        log("Failed to set title.")

os._exit(0)  # Ensure no cleanup that might hang the subprocess