# -*- coding: utf-8 -*-
"""
Created on Sat May 25 23:39:05 2019

@author: Mochi
"""

import threading

def do_nothing():
    return True


background_running = threading.Event()
background_thread = threading.Thread(target=do_nothing, args=[])
background_thread.start()

background_running.clear()
background_thread.join()

print('joined')
# use a separate thread to display the GOL board and play notes
background_running.set()
background_thread = threading.Thread(target=do_nothing, args=[])
background_thread.start()