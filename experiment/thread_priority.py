import threading
import ctypes
import time
import platform 

def set_thread_priority(priority):
    if platform.system() != "Windows":
        return
    w32 = ctypes.windll.kernel32
    SET_THREAD = 0x20
    thread_id = w32.GetCurrentThreadId()
    thread_handle = w32.OpenThread(SET_THREAD, False, thread_id)
    w32.SetThreadPriority(thread_handle, priority)
    w32.CloseHandle(thread_handle)

def get_thread_priority():
    if platform.system() != "Windows":
        return 0
    w32 = ctypes.windll.kernel32
    GET_THREAD = 0x40
    thread_id = w32.GetCurrentThreadId()
    thread_handle = w32.OpenThread(GET_THREAD, False, thread_id)
    priority = w32.GetThreadPriority(thread_handle)
    w32.CloseHandle(thread_handle)
    return priority

if __name__ == '__main__':
    priority = get_thread_priority()
    print(priority)
    set_thread_priority(1)
    print(get_thread_priority())
    set_thread_priority(priority)
    print(get_thread_priority())
