
# coding: utf-8

# In[1]:


import datetime, time, re, collections, sys

import pandas as pd
from selenium import webdriver
pd.options.display.max_rows = 10

from AutohomeBrandUrls import Main_getBrandUrls
from AutohomeManuUrls import Main_getManuUrls


# In[2]:


def getModelTypeUrls():
    '''
    获取汽车之家分级别页面url
    '''
    modelTypes = {
        'a00':'微型车','a0':'小型车','a':'紧凑型车','b':'中型车','c':'中大型车','d':'大型车','suva0':'小型SUV','suva':'紧凑型SUV',
        'suvb':'中型SUV','suvc':'中大型SUV','suvd':'大型SUV','mpv':'mpv','s':'跑车','p':'皮卡','mb':'微面','qk':'轻客'
    }
    baseUrl = 'https://www.autohome.com.cn/'       
    return collections.OrderedDict({'%s%s/' %(baseUrl,modelType):modelTypes[modelType] for modelType in modelTypes})    

def getModelUrls(url, browser, ModelType, ModelUrlDict):
    ModelUrl = collections.OrderedDict()
    browser.get(url)
    
    div_content = browser.find_element_by_xpath("//div[@class='tab-content']")
    div_brandpys = browser.find_elements_by_xpath(".//div[@class='uibox']")
    div_brandpys = [div_brandpy for div_brandpy in div_brandpys if div_brandpy.text]

    for div_brands in div_brandpys:
        dl_brands = div_brands.find_elements_by_tag_name('dl')
        for div_brand in dl_brands:
            BrandName = div_brand.find_element_by_tag_name('dt').text
            BrandId = div_brand.get_attribute('id')
            div_manus = div_brand.find_element_by_tag_name('dd').find_elements_by_xpath(".//div[@class='h3-tit']") # 厂商
            uls_models = div_brand.find_element_by_tag_name('dd').find_elements_by_tag_name('ul') # 车型s 
            regex1 = r'https://car.autohome.com.cn/.*?/brand-\d*-(\d*).html.*'
            p1 = re.compile(regex1)
            regex2 = r'指导价：(.*)'
            p2 = re.compile(regex2)    

            for i in range(len(div_manus)):
                ManuName = div_manus[i].text
                ManuId = p1.match(div_manus[i].find_element_by_tag_name('a').get_attribute('href')).groups(1)[0]
                lis = uls_models[i].find_elements_by_tag_name('li')
                for li in lis:
                    try:
                        ModelId = li.get_attribute('id')[1:]
                        ModelName = li.find_element_by_tag_name('a').text
                        ModelPrice = p2.match(li.find_element_by_tag_name('div').text).groups(1)[0]    
                        ModelUrl[ModelId] = collections.OrderedDict()
                        ModelUrl[ModelId]['BrandName'] = BrandName
                        ModelUrl[ModelId]['BrandId'] = BrandId
                        ModelUrl[ModelId]['ManuName'] = ManuName
                        ModelUrl[ModelId]['ManuId'] = ManuId
                        ModelUrl[ModelId]['ModelName'] = ModelName
                        ModelUrl[ModelId]['ModelType'] = ModelType
                        ModelUrl[ModelId]['ModelPrice'] = ModelPrice
                        ModelUrl[ModelId]['ModelUrl'] = r'https://www.autohome.com.cn/%s/' % ModelId
                    except:
                        pass

    
    ModelUrlDict.update(ModelUrl)


# In[3]:


def Main_getModelUrls():
    startTime = datetime.datetime.now()
    ModelTypeUrls = getModelTypeUrls()
    ModelUrlDict = collections.OrderedDict()
    wbName = 'AutohomeModelUrls.xlsx'
    chromepath = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
    browser = webdriver.Chrome(executable_path=chromepath)
    
    for url in ModelTypeUrls:
        print(url,'Start!')
        getModelUrls(url,browser,ModelTypeUrls[url],ModelUrlDict)
        df = pd.DataFrame(ModelUrlDict).transpose()
        df.index.name = 'ModelId'    
        df[['BrandName','BrandId','ManuName','ManuId','ModelName','ModelPrice','ModelType','ModelUrl']].to_excel(wbName)
    print('%s Done!' %sys._getframe().f_code.co_name)
    print("耗时: " + str((datetime.datetime.now() - startTime).seconds) + "秒")


# In[4]:


if __name__ == '__main__':
    Main_getModelUrls()
    Main_getBrandUrls()    
    Main_getManuUrls()

