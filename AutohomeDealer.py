
# coding: utf-8

# In[163]:


import json,re,pickle,os,time,traceback,tqdm,threading
from urllib import request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


# In[168]:


class AutohomeDealer():
    '''
    0. need 'AutohomeManuUrls.xlsx'
    1. getProvinceCity to get province and city code, create 'DealersProvinceCity.xlsx'
    2. getCityDistribution to get city distribution code, create 'DealersProvinceCityDistribution.xlsx'
    3.1 getDealerinfoBrandManu or 3.2 getDealerinfo of All 
    4.1 readDealerInfoBrandManu or 4.2 readDealerinfo of All
    '''
    def __init__(self):
        self.wtime = 0.1
        self.AutohomeManuUrls = 'AutohomeManuUrls.xlsx'
        assert os.path.exists(self.AutohomeManuUrls)
        self.DealersProvinceCity = 'DealersProvinceCity.xlsx'
        self.distribution = 'distribution'
        self.DealersCityDistribution = 'DealersCityDistribution.xlsx'
        self.dealerinfo = 'dealerinfo'
        self.numbersInPage = 15
        self.dealercolumns = ['dealerurl','dealername','dealertype','dealerzhuying','dealertel','dealeraddress']
        
    def getProvinceCity(self):
        '''
        get province and city code
        '''
        url = r'https://dealer.autohome.com.cn/DealerList/GetAreasAjax?provinceId=0&cityId=0&brandid=0&manufactoryid=0&seriesid=0&isSales=0'
        html = request.urlopen(url)
        soup = BeautifulSoup(html.read(), 'lxml')
        datas = json.loads(soup.text)['AreaInfoGroups']
        pdfs = []
        for data in datas:
            for k,v in data.items():
                if k !='Key':
                    for province in v:
                        pdf = pd.DataFrame(province)
                        cdf = pd.DataFrame(dict(pdf['Cities'])).transpose()
                        pdfs.append(pdf.merge(cdf,left_index=True,right_index=True,suffixes=('_Province','_City')))        
        pdf = pd.concat(pdfs,ignore_index=True)
        del pdf['Cities']
        pdf.to_excel(self.DealersProvinceCity)
        return pdf   
    def getCityDistribution(self,pdf=None,replace=None):
        '''
        get city and distribution code
        '''
        if not pdf:
            pdf=pd.read_excel(self.DealersProvinceCity)
        #return pdf
        # 导出 区域代码
        for index in tqdm.tnrange(len(pdf['Pinyin_City'])):
#        for i in pdf['Pinyin_City'].index:
            self.subgetCityDistribution(pdf['Pinyin_City'][index],self.distribution,replace=replace)
        # 保存 区域代码
        dfs = []
        for Pinyin_City in list(os.walk(self.distribution))[0][2]:
            lst = pickle.load(open(os.path.join(self.distribution,Pinyin_City),'rb'))
            df = pd.DataFrame(lst)
            dfs.append(df)
        df = pd.concat(dfs).reset_index(drop=True)    
        df.to_excel(self.DealersCityDistribution)
        return True
    def subgetCityDistribution(self,Pinyin_City=None,distribution=None,replace=None):
        # subget city and distribution code
        if not os.path.exists(distribution):
            os.mkdir(distribution)
        if not replace:
            if os.path.exists(os.path.join(distribution,Pinyin_City)):
                return False
        try:
            lst = []
            areaurl = r'https://dealer.autohome.com.cn/{Pinyin_City}'
            html = request.urlopen(areaurl.format(Pinyin_City=Pinyin_City))
            soup = BeautifulSoup(html.read(), 'lxml')
            div = soup.find('div',{'class':'item-box'})
            divas = div.findAll('a')
            regex = r'/(.*?)/(.*?)/.*'
            for index in range(len(divas)):
#            for diva in divas:
                diva = divas[index]
                dic = {}
                areainfo = diva.get('href')
                f = re.search(regex,areainfo).groups()
                diva.text
                dic['Pinyin_City'] = f[0]
                dic['Distribution'] = diva.text
                dic['DistributionId'] = f[1]
                lst.append(dic)
            pickle.dump(lst,open(os.path.join(distribution,Pinyin_City),'wb'))    
            return True
        except:
            traceback.print_exc()
            print(Pinyin_City)
            return False
    
    def getDealerInfoBrandManu(self,BrandId=None,ManuId=None,replace=None):
        '''
        3.1 get Dealerinfo of Brand and Manu
        '''        
        if not os.path.exists(self.dealerinfo):
            os.mkdir(self.dealerinfo)
        brandmanu = pd.read_excel(self.AutohomeManuUrls)
        if BrandId not in brandmanu['BrandId']:
            print('%s not existed!'%BrandId)
            return False
        if ManuId not in brandmanu['ManuId']:
            print('%s not existed!'%BrandId)
            return False            
        distribution = pd.read_excel(self.DealersCityDistribution)
        threads = []    #线程存放列表
        pageIndex = 1
        for Pinyin_City,DistributionId in distribution[['Pinyin_City','DistributionId']].values:
            if DistributionId != 0:
                action = self.subgetDealerInfo
                t = threading.Thread(target=action,kwargs=dict(dirname=self.dealerinfo,
                                        Pinyin_City=Pinyin_City,DistributionId=DistributionId,
                                        BrandId=BrandId,ManuId=ManuId,pageIndex=pageIndex,replace=replace))
#                     self.subgetDealerInfo(dirname=self.dealerinfo,
#                                             Pinyin_City=Pinyin_City,DistributionId=DistributionId,
#                                             BrandId=BrandId,ManuId=ManuId,pageIndex=pageIndex,replace=replace)
                threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()   
        return True
    def getDealerInfoAll(self,replace=None):
        '''
        3.2 get Dealerinfo All
        '''
        brandmanu = pd.read_excel(self.AutohomeManuUrls)
        for index in tqdm.tnrange(len(brandmanu[['BrandId','ManuId']])):
            BrandId,ManuId = brandmanu[['BrandId','ManuId']].iloc[index].values
            self.getDealerInfoBrandManu(BrandId=BrandId,ManuId=ManuId,replace=replace)
        return True
    def subgetDealerInfo(self,dirname=None,Pinyin_City=None,DistributionId=None,
                         BrandId=None,ManuId=None,pageIndex=1,replace=False):
        '''
        subget Dealerinfo
        '''
        dealerinfourlformat = r'https://dealer.autohome.com.cn/{Pinyin_City}/{DistributionId}/{BrandId}/0/{ManuId}/{pageIndex}/0/0/0.html'
        dealerinfourl = dealerinfourlformat.format(Pinyin_City=Pinyin_City,DistributionId=DistributionId,
                                       BrandId=BrandId,ManuId=ManuId,pageIndex=pageIndex)
        detailfilenameformat = 'detail-{Pinyin_City}-{DistributionId}-{BrandId}-{ManuId}-{pageIndex}'
        detailfilename = detailfilenameformat.format(Pinyin_City=Pinyin_City,
                                     DistributionId=DistributionId,
                                     BrandId=BrandId,
                                     ManuId=ManuId,
                                     pageIndex=pageIndex)
        sumfilenameformat = 'sum-{Pinyin_City}-{DistributionId}-{BrandId}-{ManuId}-{pageIndex}'
        sumfilename = sumfilenameformat.format(Pinyin_City=Pinyin_City,
                                     DistributionId=DistributionId,
                                     BrandId=BrandId,
                                     ManuId=ManuId,
                                     pageIndex=pageIndex)
        dfr = pd.DataFrame({'Pinyin_City':Pinyin_City,'DistributionId':DistributionId,
                        'BrandId':BrandId,'ManuId':ManuId,'dummy':True},index=[0])
        if not replace:
            if os.path.exists(os.path.join(dirname,sumfilename)):
                return False
        time.sleep(self.wtime)
        html = request.urlopen(dealerinfourl)
        soup = BeautifulSoup(html.read(), 'lxml')
        div = soup.find('div',{'class':'dealer-list-wrap'})
        ul = div.find('ul',{'class':'list-box'})
        lis = ul.findAll('li',{'class':'list-item'})
        lenlis = len(lis)
        # print(dealerurl,lenlis)
        if lenlis == 0:
            dfr['Count']=lenlis
            dfr.to_pickle(os.path.join(dirname,sumfilename))
            return False
        elif lenlis < self.numbersInPage:
            lst = []
            for i in range(lenlis):
                dic = {}
                for d in self.dealercolumns:
                    dic.setdefault(d,None)
                dic.setdefault('dummy',True)
                a = lis[i].find('a')
                regex = r'(//dealer.autohome.com.cn/.*/)'
                dic['dealerurl'] = re.search(regex,a.get('href')).group()
                spans = lis[i].findAll('span')
                dic['dealername'] = spans[0].text
                for span in spans:
                    if span.get('class') == ['green']:
                        dic['dealertype'] = span.text.strip()
                    if '主营品牌' in span.text:
                        dic['dealerzhuying'] = span.text.replace('主营品牌：','').strip()
                    if span.get('class') == ['tel']:
                        dic['dealertel'] = span.text.strip()    
                    if span.get('class') == ['info-addr']:
                        dic['dealeraddress'] = span.text.strip()  
                lst.append(dic)
            df = pd.DataFrame(lst)
            df.merge(dfr,on='dummy').to_pickle(os.path.join(dirname,detailfilename))       
            dfr['Count']=lenlis
            dfr.to_pickle(os.path.join(dirname,sumfilename))
            return True
        else:
            # 循环
            getDealerInfo(dirname=dirname,Pinyin_City=Pinyin_City,DistributionId=DistributionId,
            BrandId=BrandId,ManuId=ManuId,pageIndex=pageIndex+1,replace=replace)
          
    def readDealerInfoAll(self):
        '''
        readDealerinfo
        '''
        if not os.path.exists(self.dealerinfo):
            print('%s not existed!'%BrandId)
            return False
        files = list(os.walk(self.dealerinfo))[0][2]
        infotype = 'sum'

        infotype = 'sum'
        dfcolumns = ['BrandName','ManuName','Name_Province','Name_City','Distribution','Count']
        self.subreadDealerInfoBrandManu(infotype=infotype,
                dfcolumns=dfcolumns,OpenFile=True,filterfunc=None)
    
        infotype = 'detail'
        self.subreadDealerInfoBrandManu(infotype=infotype,
                dfcolumns=self.dealercolumns+dfcolumns[:-1],OpenFile=True,filterfunc=None)
    def readDealerInfoBrandManu(self,BrandId=None,ManuId=None,Detail=False,OpenFile=True):
        '''
        readDealerinfoBrandManu
        '''
        # check files
        if not os.path.exists(self.dealerinfo):
            print('%s not existed!'%BrandId)
            return False
        brandmanu = pd.read_excel(self.AutohomeManuUrls)
        if BrandId not in brandmanu['BrandId']:
            print('%s not existed!'%BrandId)
            return False
        if ManuId not in brandmanu['ManuId']:
            print('%s not existed!'%BrandId)
            return False
        
        # read sum
        infotype = 'sum'
        dfcolumns = ['BrandName','ManuName','Name_Province','Name_City','Distribution','Count']
        self.subreadDealerInfoBrandManu(infotype=infotype,BrandId=BrandId,ManuId=ManuId,
                    dfcolumns=dfcolumns,OpenFile=OpenFile)
        if Detail:
            infotype = 'detail'
            self.subreadDealerInfoBrandManu(infotype=infotype,BrandId=BrandId,ManuId=ManuId,
                    dfcolumns=self.dealercolumns+dfcolumns[:-1],OpenFile=OpenFile)
            
        return True
    def subreadDealerInfoBrandManu(self,infotype=None,BrandId=None,ManuId=None,
                                   dfcolumns=None,OpenFile=True,filterfunc=True):
        dfmanu = pd.read_excel(self.AutohomeManuUrls)
        dfcd = pd.read_excel(self.DealersCityDistribution)
        dfpc = pd.read_excel(self.DealersProvinceCity)
        excelfileformat = '{infotype}-{BrandId}-{ManuId}.xlsx'
        files = list(os.walk(self.dealerinfo))[0][2]
        if filterfunc:
            filterfunc = lambda f:f.split('-')[3:5]==[str(BrandId),str(ManuId)]
            files = [f for f in files if (f.startswith(infotype) and not f.endswith('.xlsx') and filterfunc(f))]
        else:
            files = [f for f in files if (f.startswith(infotype) and not f.endswith('.xlsx'))]
        dfs = []
        for index in tqdm.tnrange(len(files)):
            dfs.append(pd.read_pickle(os.path.join(self.dealerinfo,files[index])))
        df = pd.concat(dfs)
        if filterfunc:
            excelfile = excelfileformat.format(infotype=infotype,BrandId=BrandId,ManuId=ManuId)
        else:
            excelfile = excelfileformat.format(infotype=infotype,BrandId='all',ManuId='all')
        excelfile = os.path.join(self.dealerinfo,excelfile)
        if 'Count' in df.columns:
            df = df[df['Count']!=0]
        df = df.merge(dfmanu,how='left',on=['BrandId','ManuId'])
        df = df.merge(dfcd,how='left',on=['Pinyin_City','DistributionId'])
        df = df.merge(dfpc,how='left',on='Pinyin_City')
        df[dfcolumns].to_excel(excelfile,index=False)
        if OpenFile:
            os.startfile(excelfile)
        return excelfile


# In[169]:


if __name__ == '__main__':
    AD = AutohomeDealer()
    # 1. getProvinceCity to get province and city code, create 'DealersProvinceCity.xlsx'
    # AD.getProvinceCity() 
    # 2. getCityDistribution to get city distribution code, create 'DealersProvinceCityDistribution.xlsx'
    # AD.getCityDistribution(replace=True)
    
    # BrandId = 46
    # ManuId = 319
    # Detail = True
    # 3.1 getDealerinfoBrandManu or 3.2 getDealerinfoAll 
    # 3.1
    # AD.getDealerInfoBrandManu(BrandId=BrandId,ManuId=ManuId)
    # 3.2
    # AD.getDealerInfoAll()
    # 4.1 readDealerinfoBrandManu or 4.2 readDealerinfo All 
    # 4.1
    # AD.readDealerInfoBrandManu(BrandId=BrandId,ManuId=ManuId,Detail=Detail)
    # 4.2
    # AD.readDealerInfoAll()


# In[ ]:


AD.getDealerInfoAll()

