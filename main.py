# -*- coding: utf-8 -*-
"""
Created on Tue November 23 15:16:07 2021

@author: michaelbr.manuel
"""


#Installation of Packages
import sys
sys.path.append('./scripts')
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import  *
import os
import pandas as pd
from scripts.HTMLDownloader import getHTML
from scripts.HTMLParser import getData
import pyautogui as py
import time
from bs4 import BeautifulSoup as bs
import codecs
import re
import json
from tqdm import tqdm
import datetime


class LinkedIn(QDialog):
    def __init__(self):
        super(LinkedIn, self).__init__()
        loadUi('./UI/linkedinScraper.ui', self)
        widget.setFixedHeight(568)
        widget.setFixedWidth(491)
        self.inputBtn.clicked.connect(self.inputFile)
        self.downloadBtn.clicked.connect(self.downloadHTMLFile)
        self.folderPath.clicked.connect(self.htmlParsing)
        self.parseDataBtn.clicked.connect(self.parsedHTMLFile)
        self.savedBtn.clicked.connect(self.saveData)
        self.company_keyword.textChanged.connect(self.companyKeyword)
        
    def inputFile(self):
        path = os.getcwd()
        file_path = QFileDialog.getOpenFileName(self,  'Open File', path, filter="Excels files (*.xlsx *.xls)")  
        self.pathBrowser.setText(file_path[0])
        print(file_path[0])
        try:
            self.df_urls = pd.read_excel(file_path[0], engine = 'openpyxl', sheet_name = 'main')
            self.df_urls = self.df_urls[self.df_urls['to_download'] == 'yes']
            self.df_urls  =self.df_urls.reset_index()
            print(self.df_urls)
            df_settings = pd.read_excel(file_path[0], engine = 'openpyxl', sheet_name = 'settings')
            df_settings = df_settings.set_index('DESCRIPTION')
            self.URLBAR_COORD_X_Axis = df_settings['VALUE']['URLBAR_COORD_X-Axis']
            self.URLBAR_COORD_Y_Axis = df_settings['VALUE']['URLBAR_COORD_Y-Axis']
            self.SAVE_NAMING_BAR_X_Axis = df_settings['VALUE']['SAVE_NAMING_BAR_X_Axis']
            self.SAVE_NAMING_BAR_Y_Axis = df_settings['VALUE']['SAVE_NAMING_BAR_Y_Axis']
            self.time_1 = df_settings['VALUE']['time_1']
            self.time_2 = df_settings['VALUE']['time_2']
            self.time_3 = df_settings['VALUE']['time_3']
            self.td = df_settings['VALUE']['time_download']
            QMessageBox.information(self, "STATUS", "DONE IMPORTING THE INPUT FILE!!")
        except:
            QMessageBox.information(self, "ERROR", "Please Check the Input File!!")

    def downloadHTMLFile(self):
        i = 0
        for i in range(len(self.df_urls['URL'])):
            NAME = self.df_urls['URL'][i].split('/')[-1]
            FILENAME = '{}-{}'.format(self.df_urls['MARKINGS'][i], NAME)
            URLBAR_COORD = [self.URLBAR_COORD_X_Axis, self.URLBAR_COORD_Y_Axis]
            SAVE_NAMING_BAR = [self.SAVE_NAMING_BAR_X_Axis, self.SAVE_NAMING_BAR_Y_Axis]
            DOWNLOAD_HTML = getHTML(self.df_urls['URL'][i], FILENAME, URLBAR_COORD, SAVE_NAMING_BAR,self.time_1, self.time_2, self.time_3, self.td)
            time.sleep(5)
            i+=1
         
        QMessageBox.information(self, "STATUS", "DOWNLOADING HTML FILES DONE!!...")
        
    def htmlParsing(self):
        path = os.getcwd()
        self.folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        print(self.folderpath)
        self.folderPathDir.setText(self.folderpath)

        
    def companyKeyword(self):
        self.keyword = self.company_keyword.text().upper()
        print('KEYWORD ', self.keyword)
            
        
    def parsedHTMLFile(self):
        try:
            self._thread = QThread(self)
            self._worker = Worker(self.folderpath, self.keyword)
            self._worker.moveToThread(self._thread)
            self._thread.started.connect(self._worker.parseData)
            self._worker.data_parsed.connect(self.dataAggregator)
            self._thread.start()
        except:
            QMessageBox.information(self, "ERROR", "Please fill-up the COMPANY KEYWORD box!!")
        
    def dataAggregator(self, data):
        print('kel: ', data)
        self.DF_DATA = pd.DataFrame(data, columns = ['LinkedIn URL', 'First Name', 'Last Name', 'Target Company', 'Last Position', 'Start', 'Finish', 'LI Connections', 'Current Company', 'Current Job Title', 'Start', 'Finish'])
        i = 0
        first_name = []
        last_name = []
        for i in range(len(self.DF_DATA['Last Name'])):
            if len(self.DF_DATA['First Name'][i]) == 0:
                first_name.append(self.DF_DATA['Last Name'][i][2::])
                last_name.append(self.DF_DATA['Last Name'][i][0:2])
                print(self.DF_DATA['Last Name'][i][2::])
                print(self.DF_DATA['Last Name'][i][0:2])
                
            else:
                first_name.append(self.DF_DATA['First Name'][i])
                last_name.append(self.DF_DATA['Last Name'][i])
            i+=1
            

        self.DF_DATA['First Name'] = first_name
        self.DF_DATA['Last Name'] = last_name
        QMessageBox.information(self, "STATUS", "DONE PARSING THE DATA!!")
        
    def saveData(self):
        path = os.getcwd()
        try:
            filename = QFileDialog.getSaveFileName(self, 'Save File', path ,filter="Excels files (*.xlsx *.xls)")
            if filename[0] == "":
                return 0
            else:
                print(filename[0])
                name = filename[0]
                self.DF_DATA.to_excel('{}'.format(name), index = False)
                QMessageBox.information(self, "STATUS", "Done Saving the Exempted URLS! with a file name: {}".format(name))
        except Exception as e:
            QMessageBox.information(self, "ERROR", "Please Check the specified folder if it is correct!!")
            print(e)
        
        
    
        
class Worker(QtCore.QObject):
    data_parsed = pyqtSignal(list)
    def __init__(self, folder_path, COMPANY_KEYWORD):
        super(Worker, self).__init__()
        self.folder_path = folder_path
        self.COMPANY_KEYWORD = COMPANY_KEYWORD
        
    def parseData(self):
        files = os.listdir(self.folder_path)
        html_files = []
        a = 0
        for file in files:
            filename = file.split('.')
            try:
                if filename[-1] == 'html':
                    print(filename)
                    html_files.append(file)
                else:
                    pass
            except:
                pass  
            a+=1
            
        EXTRACTED = []
        b = 0
        for html in tqdm(html_files):
            try:
                data = getData('{}/{}'.format(self.folder_path, html) , self.COMPANY_KEYWORD)
                extract_data = getData.parse(data)
                print(extract_data)
                EXTRACTED.append(extract_data)
                print(' ============== ')
                print(' ')
            except Exception as e:
                print('ERROR', e)
                pass
            b+=1

        CLEAN_EXTRACTED_DATA = []
        c = 0
        for data in EXTRACTED:
            if data is not None:
                CLEAN_EXTRACTED_DATA.append(data)
            else:
                pass
            c+=1
        
        self.data_parsed.emit(CLEAN_EXTRACTED_DATA)
        

        
        
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()                   #Stacking all the UI file into one list
    main = LinkedIn()
    widget.addWidget(main)                               #Adding main class into the stackedwidgets
    widget.show()
    sys.exit(app.exec_())