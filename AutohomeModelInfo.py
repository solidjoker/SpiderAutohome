
# coding: utf-8

# In[1]:


import re,os,pickle,time
from datetime import datetime, timedelta
import pandas as pd

from AutohomeModelSoupDecoding import AutohomeModelSoupDecoding


# In[2]:


class AutohomeModelInfo:
    """
    根据url获取数据
    """
    def __call__(self, url):
        self.SD = AutohomeModelSoupDecoding()
        self.soup, self.codedic = self.SD(url)
        if self.codedic:
            self.data = ['keyLink','config','option']
            self.datadic ={k: eval(self.getDataValue(k)) for k in self.data}
            return self.datadic
        else:
            return None
    def dictReplace(self, text, codedic):
        regex = re.compile('|'.join(map(re.escape, codedic)))
        return regex.sub(lambda m:codedic[m.group(0)].decode('utf-8'), text)
    def getDataValue(self, data):
        regex = r'.*var {data} = (.*);'.format(data=data)
        try:
            research = re.compile(regex).search(self.soup.text).group(1)
            specialdic = {'&nbsp': ' '}
            research = self.dictReplace(research, specialdic)
            return self.dictReplace(research, self.codedic)
        except:
            return None

# Test
# if __name__ == '__main__':
#     testurl = r'https://car.autohome.com.cn/config/series/771.html'
#     AMI = AutohomeModelInfo()
#     datadic = AMI(testurl)
#     print(datadic)  


# In[3]:


class AutohomeModelInfoDetail:
    """
    根据wbname中的id，获取详细信息
    附加功能，汽车之家keylink
    """
    def __init__(self, wbname = r'AutohomeModelUrls.xlsx', 
                 missionpkl=r'AutohomeModelMisson.pkl', 
                 datafolder=r'output', 
                 keypkl = r'AutohomeKey.pkl',
                 keytxt = r'Autohomekey.txt',
                 postponedays=10):
        self.wbname = wbname        
        self.missionpkl = missionpkl
        self.iddic = self.initCarpkl()        
        self.url = r'https://car.autohome.com.cn/config/series/{idcar}.html' 
        self.initfolder(datafolder)
        self.keypkl = keypkl
        self.keytxt = keytxt
        self.names = self.getkeyLink(self.keypkl)
        self.idpkl = datafolder + r'/{0}.pkl'
        self.idtxt = datafolder + r'/{0}.txt'
        self.postponedays = postponedays        
    def initCarpkl(self):
        f = self.missionpkl
        if os.path.exists(f):
            iddic = pickle.load(open(f, 'rb'))
        else:
            iddic = self.getIDdic()
            for k in iddic:
                iddic[k].update({'update': None})
            pickle.dump(iddic, open(f, 'wb'))
        return iddic
    def getIDdic(self):
        wbname = r'AutohomeModelUrls.xlsx'
        df = pd.read_excel(wbname)
        ModelIdName = df[['ModelId','ModelName']]
        iddic = {int(i):{'carname': j, 'update': None} for i,j in zip(ModelIdName['ModelId'],ModelIdName['ModelName'])}
        return iddic
    def initfolder(self, datafolder):
        if os.path.exists(datafolder):
            print('{0} existed'.format(datafolder))
        else:
            os.mkdir(datafolder)
            print('{0} created'.format(datafolder))    
    def getOneData(self, idcar):
        url = self.url.format(idcar=idcar)
        try:
            GetDataDic = AutohomeModelInfo()
            datadic = GetDataDic(url)
            return datadic
        except:
            return None
    def getAllData(self):
        fmt = '%Y/%m/%d'
        total = len(self.iddic)
        count = 0
        for idcar in list(self.iddic.keys()):
            count += 1
            if not self.iddic[idcar]['update'] or                     datetime.now() - datetime.strptime(self.iddic[idcar]['update'], fmt) > timedelta(days=self.postponedays):
                print('{count}/{total}\t>\t{idcar}'.format(count=count, total=total, idcar=idcar))
                time.sleep(1)
                datadic = self.getOneData(idcar)

#                 try:  
#                     self.writekeylink(self.keypkl, datadic)
#                     del datadic['keyLink']
#                     self.iddic[idcar]['datafile'] = self.idpkl.format(idcar)
#                     self.iddic[idcar]['update'] = datetime.now().strftime(fmt)
#                     pickle.dump(datadic, open(self.idpkl.format(idcar), 'wb'))
#                     self.writeOutputTxt(idcar)
#                 except:
#                     self.iddic[idcar]['datafile'] = None
#                     self.iddic[idcar]['update'] = datetime.now().strftime(fmt)
#                 finally:
#                     pickle.dump(self.iddic, open(self.missionpkl, 'wb'))
                
                if datadic:
                    self.writekeylink(self.keypkl, datadic)
                    del datadic['keyLink']
                    self.iddic[idcar]['datafile'] = self.idpkl.format(idcar)
                    pickle.dump(datadic, open(self.idpkl.format(idcar), 'wb'))
                    self.writeOutputTxt(idcar)
                else:
                    self.iddic[idcar]['datafile'] = None
                    
                self.iddic[idcar]['update'] = datetime.now().strftime(fmt)
                pickle.dump(self.iddic, open(self.missionpkl, 'wb'))
    def writeOutputTxt(self, idcar):
        pkldata = pickle.load(open(self.idpkl.format(idcar)))
        with open(self.idtxt.format(idcar), 'wb') as f:
            config = pkldata['config']
            params = config['result']['paramtypeitems']
            datadic = {}    # 初始化
            param = params[0]['paramitems']
            datadiclen = len(param[0]['valueitems'])
            for i in range(datadiclen):
                datadic[i] = {name: None for name in self.names}
            for param in params:
                for i in range(datadiclen):
                    for j in param['paramitems']:
                        datadic[i].update({j['name']:j['valueitems'][i]['value']})
            option = pkldata['option']
            params = option['result']['configtypeitems']
            for param in params:
                for i in range(datadiclen):
                    for j in param['configitems']:
                        datadic[i].update({j['name']:j['valueitems'][i]['value']})

            # 写入数据
            titleline = '{0}\t{1}\t{2}\n'
            titleline = titleline.format('idcar', 'carname', '\t'.join(sorted(datadic[0].keys())))
            f.write(titleline)

            for i in datadic.keys():
                try:
                    dataline = '{0}\t{1}'.format(idcar,self.iddic[idcar]['carname'].encode('utf-8'))
                except:
                    dataline = '{0}\t{1}'.format(idcar,self.iddic[idcar]['carname'].encode('utf-8'))
                for k in sorted(datadic[i].keys()):
                    if datadic[i][k]:
                        dataline += '\t' + datadic[i][k] #.decode('utf-8')
                    else:
                        dataline += '\t' + '-'
                dataline += '\n'
                f.write(dataline)          
    def getkeyLink(self, keypkl):
        if os.path.exists(keypkl):
            with open(keypkl) as f:
                keyLink = pickle.load(f)
            return [k['name'] for k in keyLink['result']['items']]
        return None
    def writekeylink(self, keypkl, datadic):
        if not os.path.exists(keypkl):
            pickle.dump(datadic['keyLink'], open(keypkl, 'wb'))
            with open(self.keytxt,'wb') as f:
                f.write('link\tname\tid\n')
                for k in datadic['keyLink']['result']['items']:
                    f.write('{link}\t{name}\t{id}\n'.format(link=k['link'], name=k['name'], id=k['id']))


# In[4]:


if __name__ == '__main__':
    wbname = r'AutohomeModelUrls.xlsx' 
    missionpkl=r'AutohomeModelMisson.pkl' 
    datafolder=r'output'
    keypkl = r'AutohomeKey.pkl'
    keytxt = r'Autohomekey.txt' 
    postponedays=10
    Detail = AutohomeModelInfoDetail(wbname,missionpkl,datafolder,keypkl,keytxt,postponedays)
    Detail.getAllData()
    

