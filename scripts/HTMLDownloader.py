# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 18:15:26 2021

@author: michael
"""

import pyautogui as py
import time
import pandas as pd

def getHTML(url, filename, URLBAR_COORD, SAVE_NAMING_BAR,T1, T2, T3, TD):
    MOVETO_URLBAR = py.moveTo(URLBAR_COORD[0],URLBAR_COORD[1])
    CLICK_URLBAR = py.click(URLBAR_COORD[0],URLBAR_COORD[1])
    REMOVED_CURRENT_URL = py.hotkey('ctrl','a')
    PASTE_NEW_URL = py.write(url)
    CLICK_ENTER = py.hotkey('enter')
    time.sleep(T1) ### IT IS THE TIME DELAY WAITING THE RELOAD ON THE WEBPAGE
    py.hotkey('pagedown')
    py.hotkey('pagedown')
    py.hotkey('pagedown')
    time.sleep(T2)
    SAVE = py.hotkey('ctrl','s')
    time.sleep(T3)
    FILE_RENAME = py.write(filename)
    CLICK_ENTER = py.hotkey('enter')
    time.sleep(TD)
    
