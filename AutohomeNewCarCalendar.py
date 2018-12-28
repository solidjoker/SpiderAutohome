
# coding: utf-8

# In[2]:


import datetime,time,os,sys,re,pprint,pickle,inspect
import urllib.request
import bs4
from selenium import webdriver
import pandas as pd
import numpy as np


# In[3]:


class AutohomeNewCarCalendar():
    
    def __init__(self):
        self.ahnccUrl = r'https://www.autohome.com.cn/newbrand/{year}'
        self.urldic = {year:self.ahnccUrl.format(year=year) for year in range(2011,datetime.datetime.now().year+1)}
        self.base_pkl = 'AutohomeNewCarCalendar_base.pkl'
        self.task_pkl = 'AutohomeNewCarCalendar_task.pkl'
        if not os.path.exists(self.base_pkl):
            # 基础数据，仅包含汽车之家信息，index:url,yearmonth:年月,info:text信息
            self.getBaseInfos()
        if not os.path.exists(self.task_pkl):
            # 基础数据基础上，包含BrandName,ManuName,ModelName,ModelType
            self.initTask()
        self.matchUrls = r'AutohomeModelUrls.xlsx'
        assert os.path.exists(self.matchUrls),'%s not exist!' % self.matchUrls
        self.output = r'AutohomeNewCarCalendar.txt' 

    def __call__(self):
        self.updateBaseInfos()
        self.updateTask()
        return self.runTasks()
               
    def updateTask(self):
        dftask = pickle.load(open(self.task_pkl,'rb'))
        dfbase = pickle.load(open(self.base_pkl,'rb'))
        df = pd.concat([dftask,dfbase],axis=0,sort=False)
        df.drop_duplicates('href',inplace=True)
        df.reset_index(drop=True,inplace=True)
        df.sort_index(inplace=True)
        df.loc[df['Status'].isnull(),['ModelId','Status']] = None
        df.to_pickle(self.task_pkl)
        return df

    def runTasks(self):
        df = pickle.load(open(self.task_pkl,'rb'))
        df = df.copy()
        for i in range(len(df)):
            if not df.iloc[i]['Status']:
                print('%s in %s' % (i,len(df)))
                result = self.getModelId(df.loc[i,'href'])
                print('ModelId:',result)
                df.iloc[i]['ModelId'] = result
                df.iloc[i]['Status'] = True
                df.to_pickle(self.task_pkl)
        if df['Status'].count() == len(df):
            print('MergeDFs')
            return self.mergeDFs(self.matchUrls)
        return False
    
    def mergeDFs(self,matchUrls):
        try:
            df = pickle.load(open(self.task_pkl,'rb'))
            df['ModelId'] = df['ModelId'].apply(lambda x: int(x) if x else None)
            dfindex = pd.read_excel(matchUrls)
            df = df.merge(dfindex,how='left',on='ModelId').sort_values('yearmonth').to_csv(self.output,sep='\t',index=None)
            os.startfile(self.output)
            return True
        except:
            return False
        
    def getModelId(self,url):
        trytime = 3
        while trytime:
            try:
                f = urllib.request.urlopen(url)
                bsObj = bs4.BeautifulSoup(f,'lxml')
                ahref = bsObj.find('div',{'class':'athm-sub-nav__car__name'}).find('a').attrs['href']
                regex = re.compile(r'/(.*)/.*')
                return regex.match(ahref).group(1)
            except:
                trytime -= 1        
        return None

    def updateBaseInfos(self):
        df = pickle.load(open(self.base_pkl,'rb'))
        newdf = self.getBaseInfo(self.urldic[datetime.datetime.now().year])
        df = pd.concat([df,newdf]).drop_duplicates()
        df.to_pickle(self.base_pkl)
        return df
        
    def getBaseInfos(self,year=None):
        if year:
            urldic = {year:self.ahnccUrl.format(year=year)}
        else:
            urldic = self.urldic
        dfs = []
        for url in urldic.values():
            dfs.append(self.getBaseInfo(url))
        df = pd.concat(dfs,ignore_index=True)
        df.to_pickle(self.base_pkl)
        return df

    def getBaseInfo(self,url):
        dfs = []
        f = urllib.request.urlopen(url)
        bsObj = bs4.BeautifulSoup(f,'lxml')
        divs = bsObj.find_all('div',{'class':'select-list'})
        for div in divs:
            ym = div.find('h4')
            lis = div.find_all('li')
            for li in lis:    
                dfs.append(pd.DataFrame({'href':['https:{url}'.format(url=li.find('a').attrs['href'])],
                                         'yearmonth':[ym.text],
                                         'info':[li.text]}))
        df = pd.concat(dfs,ignore_index=True)     
        return df

    def initTask(self):
        df = pickle.load(open(self.base_pkl,'rb'))
        df['ModelId'] = None
        df['Status'] = None
        df.to_pickle(self.task_pkl)
   


# In[4]:


if __name__ == '__main__':
    # 更新新车月历
    NewCarCalendar = AutohomeNewCarCalendar()
    NewCarCalendar()

