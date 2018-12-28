
# coding: utf-8

# In[13]:


# python2

import re, logging, requests
from bs4 import BeautifulSoup
import PyV8


# #### <a href=https://www.cnblogs.com/qiyueliuguang/p/8144248.html>汽车之家配置参数抓取</a>

# In[14]:


class AutohomeModelSoupDecoding:
    def __call__(self, url):
        return self.getSoupDecoding(url)
    
    def getJs(self, html):
        try:
            alljs = ("var rules = '';"
                     "var document = {};"
                     "document.createElement = function() {"
                     "      return {"
                     "              sheet: {"
                     "                      insertRule: function(rule, i) {"
                     "                              if (rules.length == 0) {"
                     "                                      rules = rule;"
                     "                              } else {"
                     "                                      rules = rules + '#' + rule;"
                     "                              }"
                     "                      }"
                     "              }"
                     "      }"
                     "};"
                     "document.querySelectorAll = function() {"
                     "      return {};"
                     "};"
                     "document.head = {};"
                     "document.head.appendChild = function() {};"

                     "var window = {};"
                     "window.decodeURIComponent = decodeURIComponent;")

            js = re.findall('(\(function\([a-zA-Z]{2}.*?_\).*?\(document\);)', html)
            for item in js:
                alljs = alljs + item
            return alljs
        except:
            logging.exception('makejs function exception')
            return None
        
    def getClsContent(self, js):
        try:
            ctx = PyV8.JSContext()
            ctx.enter()
            ctx.eval(js)
            return ctx.eval('rules')
        except:
            logging.exception('clscontent function exception')
            return None

    def getCodedic(self, clscontent):
        data = clscontent.split('#')
        regexKey = r'\.(.*?)::'
        reKey = re.compile(regexKey).search
        regexValue = r'content:"(.*)"'
        reValue = re.compile(regexValue).search
        return {r"<span class='%s'></span>" % reKey(item).group(1): reValue(item).group(1) for item in data}
    
    def getSoupDecoding(self, url):
        html = requests.get(url)
        content = html.text
        soup = BeautifulSoup(content, 'lxml')
        js = self.getJs(content)
        if not js:
            logging.exception('makejs error')
            return soup, None
        clscontent = self.getClsContent(js)
        if not clscontent:
            logging.exception('clscontent error')
            return soup, None
        codedic = self.getCodedic(clscontent)
        return soup, codedic


# In[15]:


if __name__ == '__main__':
    import pprint
    testurl = r'https://car.autohome.com.cn/config/series/344.html'
    testurl = r'https://car.autohome.com.cn/config/series/771.html'

    SD = AutohomeModelSoupDecoding()
    soup, decoding = SD(testurl)
#     print('soup:')
#     print(soup)
#     print('-'*40)
    print('decoding:')
    if decoding:
        for k in decoding:
            print('{key}: {value}'.format(key=k, value=decoding[k]))
    print('-'*40)

