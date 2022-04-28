# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 10:37:48 2022

@author: humblemat
"""



import requests
from bs4 import BeautifulSoup
import pandas as pd



#%%

# Import required modules
from lxml import html
import requests
  

# Request the page

def scrape_income_data(ticker_symbol = 'tsla'):
    page = requests.get('https://roic.ai/company/' + ticker_symbol)
    soup = BeautifulSoup(page.text, 'lxml')
    
        
    table_root = soup.find(id='__next')
    trc_gen = table_root.children
    trc_gen.__next__()
    cursor = trc_gen.__next__().children.__next__().children
    cursor.__next__()
    cursor.__next__()
    cursor_table_root = cursor.__next__()
    
    cursor = cursor_table_root.children.__next__().children
    cursor = cursor.__next__().children.__next__()
    save_point_cursor_rows_parent = cursor
    cursor_rows = list(cursor.children)
    
    def parse_datarow(row):
        row_index_div, row_data_div = list(row.children)
        row_index = row_index_div.strings.__next__()
        row_data = []
        for i in row_data_div.strings:
            converted = None
            if i != '- -':
                is_percentage = False
                is_negative = False
                i = i.replace(',', '').strip()
                iterate_no_modified = False
                while not iterate_no_modified:
                    iterate_no_modified = True
                    if i[-1] == '%':
                        iterate_no_modified = False
                        is_percentage = True
                        i = i[:-1]
                    if i[0] == '(' and i[-1] == ')':
                        iterate_no_modified = False
                        is_negative = True
                        i = i [1:-1]
                    if iterate_no_modified:
                        converted = float(i)
                if is_negative:
                    converted = -converted
                if is_percentage:
                    converted = converted / 100
            else:
                converted = float('NaN')
            assert converted is not None
            row_data.append(converted)
        df = pd.DataFrame.from_dict({row_index:row_data })
        return df
    
    def parse_titlerow(row):
        row_index_div, row_data_div = list(row.children)
        row_index = row_index_div.strings.__next__()
        row_data = row_data_div.strings
        df = pd.DataFrame.from_dict({row_index:row_data })
        return df
    
    df_finale = pd.concat([parse_titlerow(cursor_rows[1])] 
                          + [parse_datarow(i) for i in cursor_rows[3:]] 
                          , axis = 1)
    return df_finale
