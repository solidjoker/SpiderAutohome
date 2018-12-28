
# coding: utf-8

# In[1]:


from urllib import request
from bs4 import BeautifulSoup
import pandas as pd
import time, re, collections, sys
pd.options.display.max_rows = 10


# In[7]:


def ManuUrlFormat(a,b):
    manuUrl = r'https://car.autohome.com.cn/price/brand-{0}-{1}.html'
    return manuUrl.format(a,b)

def getManuUrls(wbName,wbManuName):
    df = pd.read_excel(wbName)
    df = df[['BrandName','BrandId','ManuName','ManuId']].drop_duplicates().reset_index(drop=True) # BrandId
    df['ManuUrl'] = df.apply(lambda row: ManuUrlFormat(row['BrandId'],row['ManuId']),axis=1)
    df = df.set_index(['ManuId'])
    df.to_excel(wbManuName)
    return df

def Main_getManuUrls():
    wbName = 'AutohomeModelUrls.xlsx'
    wbManuName = 'AutohomeManuUrls.xlsx'
    print('%s Done!' %sys._getframe().f_code.co_name)    
    return  getManuUrls(wbName, wbManuName)


# In[8]:


if __name__ == '__main__':
    Main_getManuUrls()

