
# coding: utf-8

# In[42]:


import datetime, time, re, collections, sys, urllib, os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  # 引入 ActionChains 类

pd.options.display.max_rows = 10


# In[43]:


def deleteunvalid(s):
    unvalidcharaters = ['/','\\',':','*','"','<','>','|','?']    
    for i in unvalidcharaters:
        s = s.replace(i,'_')
    return s


# In[53]:


def getBrandPictures(picturesfolder):
    if not os.path.exists(picturesfolder):
        os.mkdir(picturesfolder)
    wbbrand = r'AutohomeBrandUrls.xlsx'    
    df = pd.read_excel(wbbrand)    
    branddic = {i:b for i,b in zip(df['BrandId'],df['BrandName'])}    
    chromepath = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
    browser = webdriver.Chrome(executable_path=chromepath)
    url = r'https://car.autohome.com.cn/price/brand-{0}.html'
    
    count = 0
    for brandid in branddic.keys():
        if not (os.path.exists(r'{0}/{1}.{2}'.format(picturesfolder,deleteunvalid(branddic[brandid]),'jpg')) or                 os.path.exists(r'{0}/{1}.{2}'.format(picturesfolder,deleteunvalid(branddic[brandid]),'png'))):
            print('{count}/{total}\t>\t{brandid}'.format(count=count, total=len(branddic), brandid=brandid))
            browser.get(url.format(brandid))
            try:
                div = browser.find_element_by_xpath("//div[@class='carbradn-pic']")
                img = div.find_element_by_tag_name('img')
                img_url = img.get_attribute('src')
                ext = img_url.split('.')[-1]
                data = urllib.request.urlopen(img_url).read()
                with open(r'{0}/{1}.{2}'.format(picturesfolder,deleteunvalid(branddic[brandid]),ext),'wb') as f:
                    f.write(data)
            except:
                print('{brandname} has not picture'.format(brandname = deleteunvalid(branddic[brandid])))

        count +=1


# In[54]:


brandpicturesfolder = r'pictures_brand'
getBrandPictures(brandpicturesfolder)
print('Done!')


# In[46]:


def getModelPictures(picturesfolder):
    if not os.path.exists(picturesfolder):
        os.mkdir(picturesfolder)
    wbname = r'AutohomeModelUrls.xlsx'  
    df = pd.read_excel(wbname)    
    modeldic = {i:b for i,b in zip(df['ModelId'],df['ModelName'])}      
    chromepath = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
    browser = webdriver.Chrome(executable_path=chromepath)
    url = r'https://www.autohome.com.cn/{0}'
    
    count = 0
    for modelid in modeldic.keys():
        if not (os.path.exists(r'{0}/{1}.{2}'.format(picturesfolder,deleteunvalid(modeldic[modelid]),'jpg')) or                 os.path.exists(r'{0}/{1}.{2}'.format(picturesfolder,deleteunvalid(modeldic[modelid]),'png'))):
            print('{count}/{total}\t>\t{modelid}'.format(count=count, total=len(modeldic), modelid=modelid))
            browser.get(url.format(modelid))
            try:
                div = browser.find_element_by_xpath("//div[@class='pic-main']")
                img = div.find_element_by_tag_name('img')
                img_url = img.get_attribute('src')               
                ext = img_url.split('.')[-1]
                data = urllib.request.urlopen(img_url).read()
                with open(r'{0}/{1}.{2}'.format(picturesfolder,deleteunvalid(modeldic[modelid]),ext),'wb') as f:
                    f.write(data)
            except:
                try:
                    dl = browser.find_element_by_xpath("//dl[@class='models_pics']")
                    img = dl.find_element_by_tag_name('img')
                    img_url = img.get_attribute('src')               
                    ext = img_url.split('.')[-1]
                    data = urllib.request.urlopen(img_url).read()
                    with open(r'{0}/{1}.{2}'.format(picturesfolder,deleteunvalid(modeldic[modelid]),ext),'wb') as f:
                        f.write(data)
                except:
                    print('{brandname} has not picture'.format(brandname = deleteunvalid(modeldic[modelid])))

                
        count +=1


# In[48]:


modelpicturesfolder = r'pictures_model'
getModelPictures(modelpicturesfolder)
print('Done!')

