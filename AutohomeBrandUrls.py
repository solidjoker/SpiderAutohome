
# coding: utf-8

# In[14]:


from urllib import request
from bs4 import BeautifulSoup
import pandas as pd
import time, re, collections, sys
pd.options.display.max_rows = 10


# In[17]:


def getBrandUrls(wbName,wbBrandName):
    df = pd.read_excel(wbName)
    df = df[['BrandName','BrandId']].drop_duplicates().reset_index(drop=True) # BrandId
    brandUrl = r'https://car.autohome.com.cn/price/brand-{0}.html'
    df['BrandUrl'] = df['BrandId'].apply(lambda r: brandUrl.format(r))
    df = df.set_index(['BrandId'])
    df.to_excel(wbBrandName)
    return df

def Main_getBrandUrls():
    wbName = 'AutohomeModelUrls.xlsx'
    wbBrandName = 'AutohomeBrandUrls.xlsx'
    print('%s Done!' %sys._getframe().f_code.co_name)    
    return getBrandUrls(wbName, wbBrandName)


# In[18]:


if __name__ == '__main__':
    Main_getBrandUrls()

