
# coding: utf-8

# In[1]:


import os, logging, copy, pickle
import pandas as pd
pd.options.display.max_rows = 10


# In[2]:


class AutohomeModelInfoOutput:
    def __init__(self, datafolder=r'output', output=r'AutohomeModelInfo.xlsx'):
        self.output = output
        if self.checkfolder(datafolder):
            self.datafolder = datafolder
            self.files = self.getfiles()
            self.getExcel()
            logging.critical('Please find the excel :%s'%self.output)
        else:
            logging.warning('Failed!')

    def checkfolder(self, datafolder):
        if os.path.exists(datafolder):
            return True
        return False

    def getfiles(self):
        files = os.listdir(self.datafolder)
        return [os.path.join(self.datafolder, filename) for filename in files if filename.endswith('txt')]
    
    def getExcel(self):
        dfs = [pd.read_csv(i,delimiter='\t') for i in self.files]
        df = pd.concat(dfs,ignore_index=True,sort=False,join='outer')        
        df.to_excel(self.output)


# In[3]:


if __name__ == '__main__':
    mission = r'AutohomeModelMisson.pkl'
    data = pickle.load(open(mission,'rb'))
    df = pd.DataFrame(data).transpose()
    print('%s/%s'% (df.count()['update'],df.count()['carname']))
    if df.count()['update'] == df.count()['carname']:
        AH =  AutohomeModelInfoOutput()    

