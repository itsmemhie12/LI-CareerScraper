# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 20:56:39 2021

@author: michael
"""


import os
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import codecs
import re
import json
from tqdm import tqdm
import datetime


#####================ FUNCTION FOR GETTING DATA IN CAREER SECTION =================####
def dateConversion(date):
    try:
        conversion = datetime.strptime(date, '%b-%Y').strftime('%m/%d/%Y')
        return conversion
    except:
        return date
    
    
def companyNameLong(soup):
    a = []
    for x in soup.findAll('h3', class_ = 't-16 t-black t-bold'):
        #print(x.text.strip())
        a.append(x.text.strip())
    company = a[0].split('\n')[1]
    return company

def name_data(soup):
    name = soup.find('h1', class_ = 'text-heading-xlarge inline t-24 v-align-middle break-words').text
    print(name)
    check = re.search('[\w]', name)
    #print(check)
    if check is None:
        last_name = name[0:2]
        first_name = name[2::]
        print('LAST NAME: ', last_name)
        print('FIRST NAME: ', first_name)
    else:
        name_split = name.split(' ')
        last_name = name_split[-1]
        first = name_split[:-1]
        first_name = ','.join(first)
        print('LAST NAME: ', last_name)
        print('FIRST NAME: ', first_name)
    return first_name, last_name



def getCareerData(soup):
    career_highlight = {}
    for x in soup.findAll('li', class_ = 'pv-entity__position-group-pager pv-profile-section__list-item ember-view'):
        company = x.findAll('p', class_ = 'pv-entity__secondary-title t-14 t-black t-normal')
        if len(company) != 0:
            pos = x.find('h3', class_ = 't-16 t-black t-bold')
            company_f = company[0].text.strip().upper().split('\n')
            if len(company_f) > 1:
                company_name = company_f[0]
            else:
                company_name = company_f[0]
            position = pos.text.strip()
            print('POSITION:', position)
            print('COMPANY:', company_name) 
            try:
                date = x.findAll('span')[1].text
                STARTING_DATE = dateConversion(date.split('–')[0].strip().replace(' ', '-'))
                END_DATE = dateConversion(date.split('–')[1].strip().replace(' ', '-'))
                print('STARTING DATE EMPLOYED:', STARTING_DATE)
                print('ENDING DATE EMPLOYED:', END_DATE)
            except:
                date = x.findAll('span')[2].text
                STARTING_DATE = dateConversion(date.split('–')[0].strip().replace(' ', '-'))
                END_DATE = dateConversion(date.split('–')[1].strip().replace(' ', '-'))
                print('STARTING DATE EMPLOYED:', STARTING_DATE)
                print('ENDING DATE EMPLOYED:', END_DATE)
            data_extracted = [position, STARTING_DATE, END_DATE]
            print('EXTRACTED DATA: ', data_extracted)
            
            if company_name in career_highlight.keys():
                career_highlight[company_name].append(data_extracted)
            else:
                career_highlight[company_name] = [data_extracted]
            
        else:
            companyLong = companyNameLong(soup).strip().upper()
            #print('COMPANY LONG:', companyLong)
            POSITION = []
            for pos in x.findAll('h3', class_ = 't-14 t-black t-bold'):
                #print('POSITION AT {} : '.format(companyLong), pos.text.strip().replace('Title\n', ''))
                POSITION.append(pos.text.strip().replace('Title\n', ''))
            employed_date_in_companyLong = []
            for date in x.findAll('h4', class_ = 'pv-entity__date-range t-14 t-black--light t-normal'):
                #print(date.text.strip().replace('Dates Employed\n', ''))
                employed_date_in_companyLong.append(date.text.strip().replace('Dates Employed\n', ''))
            #LATEST POSITION AT CERTAIN COMPANY
            position = POSITION[0]
            #print('POSITION: ', position)
            #DATE SPAN OF THE EMPLOYMENT OF CERTAIN POSITION
            starting = employed_date_in_companyLong[-1].strip()
            STARTING_DATE = dateConversion(starting.split('–')[0].strip().replace(' ', '-'))
            #print('STARTING DATE EMPLOYED: ', STARTING_DATE)
            ending = employed_date_in_companyLong[0].strip()
            if ending.upper() == 'PRESENT':
                ENDING_DATE = 'PRESENT'
                #print('ENDING DATE EMPLOYED: ', ENDING_DATE)
            else:
                ENDING_DATE = dateConversion(ending.split('–')[1].strip().replace(' ', '-'))
                #print('ENDING DATE EMPLOYED: ', ENDING_DATE)
                
            data_extracted = [position, STARTING_DATE, ENDING_DATE]
            #print(data_extracted)
            if companyLong in career_highlight.keys():
                career_highlight[companyLong].append(data_extracted)
            else:
                career_highlight[companyLong] = [data_extracted]
        
        #print('===========')
        #print(' ')
    
    return career_highlight


#####==================== CLASS FOR PARSING DATA ==================================####
class getData(object):
    def __init__(self, file, COMPANY_KEYWORD):
        self.file = file
        self.COMPANY_KEYWORD = COMPANY_KEYWORD
        
    def parse(self):
        try:
            file = codecs.open(self.file , "r", "utf-8").read()
            soup = bs(file, 'html.parser')
            ###################### PROFILE NAME AND LINKEDIN URL ################################
            linkedin_url = soup.find('li', class_ = 'pv-text-details__right-panel-item').a['href']
            print(linkedin_url)
            first_name = name_data(soup)[0] 
            last_name = name_data(soup)[1] 
            LI_connection = soup.find('span', class_ = 't-bold').text
            ############################# FULL CAREER DATA ################################
            career_data = getCareerData(soup)
            print('CAREER DATA: ', career_data)
            print(type(career_data))
            ############### SORTING THE DATE INTO TOPCON CAREER ONLY #########################
            valid_key = []
            for key in career_data.keys():
                check = re.search(self.COMPANY_KEYWORD, key)
                if check is None:
                    pass
                else:
                    valid_key.append(key)
            ################ CONCATENATE THE DATA THAT CAREER WITH TOPCON ###################
            topcon_data_needed = []
            for key in valid_key:
                topcon_data = []
                for data in career_data[key]:
                    topcon_data = [key] + data
                    topcon_data_needed.append(topcon_data)
            
            df_topcon = pd.DataFrame(topcon_data_needed, columns = ['company','position', 'starting', 'end'])
            df_topcon['starting'] = pd.to_datetime(df_topcon['starting'])
            df_topcon = df_topcon.sort_values(by = 'starting').reset_index()
            ### COMPANY NAME IN TOPCON
            TOPCON_company = df_topcon['company'].tolist()[-1]
            ### LAST POSITION IN TOPCON
            TOPCON_position = df_topcon['position'].tolist()[-1]
            print('LAST POSITION IN TOPCON: ', TOPCON_position)
            ### ENDING DATE THAT WORKING IN TOPCON
            TOPCON_end  = df_topcon['end'].tolist()[-1]
            if type(TOPCON_end) is str:
                pass
            else:
                TOPCON_end  = df_topcon['end'].tolist()[-1].strftime('%m/%d/%Y')
            print('LAST DATE THAT HE IS IN TOPCON: ', TOPCON_end)
            #### STARTING DATE THAT HE/SHE WORK IN TOPCON
            TOPCON_start = df_topcon['starting'].tolist()[0].strftime('%m/%d/%Y')
            print('STARTING DATE THAT HE IS IN TOPCON: ', TOPCON_start)
            ######### GETTING THE CURRENT WORK HE HAD AFTER HE WORK IN TOPCON ##########
            #CURRENT COMPANY AND POSITION
            career = []
            for job in career_data.keys():
                data = []
                #print(career_highlight[job])
                for company in career_data[job]:
                    data = [job] + company 
                    print(data)
                    print(' ==== ')
                    career.append(data)
            df_career = pd.DataFrame(career, columns = ['company', 'position', 'starting', 'end'])
            try:
                index_current_job = df_career['end'].tolist().index('Present')
                current_company = df_career['company'][index_current_job]
                current_position = df_career['position'][index_current_job]
                current_starting = df_career['starting'][index_current_job]
                current_end = df_career['end'][index_current_job]
                print('CURRENT COMPANY: ', current_company)
                print('CURRENT POSITION: ', current_position)
                print('CURRENT STARTING DATE: ', current_starting)
                print('CURRENT ENDING DATE: ', current_end)
            except:
                df_career = df_career.sort_values(by = 'end').reset_index()
                df_career = df_career.reset_index()
                current_company = df_career['company'].tolist()[-1]
                current_position = df_career['position'].tolist()[-1]
                current_starting = df_career['starting'].tolist()[-1]
                current_end = df_career['end'].tolist()[-1]
                print('CURRENT COMPANY: ', current_company)
                print('CURRENT POSITION: ', current_position)
                print('CURRENT STARTING DATE: ', current_starting)
                print('CURRENT ENDING DATE: ', current_end)
                    
            
            
            output = [linkedin_url, first_name, last_name, TOPCON_company, TOPCON_position, TOPCON_start, TOPCON_end, LI_connection, current_company, current_position, current_starting, current_end]
            return output
        
        except Exception as e:
            print('ERROR AT PARSE: ', e)
        
   