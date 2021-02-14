import os, os.path
import math
import pandas as pd
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import seaborn as sns
from statistics import mean
import numpy as np
import matplotlib.pyplot as plt


class Scrapper:

    class Paginator(object):
        def __init__(self,scrapper):
            self.page = 0
            self.totalPages = 0
            self.link = scrapper.link
            self.driver=scrapper.driver

        def nextPage(self):
            self.driver.get(self.getPageLink(self.page+1))
            self.wait()
            self.page = self.page + 1

        def getPageLink(self, page_number):
            return self.link + str(page_number) + '.html'

        def openPage(self, n):
            if n != self.page:
                print("now opening", self.getPageLink(n))
                self.driver.get(self.getPageLink(n))
                self.wait()
                self.page = n

        def wait(self):
            try:
                navbar = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role = 'navigation']"))
                )
            except:
                self.driver.quit()

    def __init__(self, headless = False, link =""):
        PATHC = "C:\Program Files (x86)\chromedriver.exe"
        if(headless):
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(executable_path=PATHC,options=chrome_options)
        else:
            self.driver = webdriver.Chrome(executable_path=PATHC)

        self.link=link
        self.paginator = self.Paginator(self)

    def getMetaData(self):
        tot = self.driver.find_element_by_xpath("//div[@role = 'navigation']/preceding-sibling::div")

        totalrecords = int(str(tot.text).split()[4])
        displayedrecords = int(str(tot.text).split()[2])
        print("displaying "+str(displayedrecords)+" records")
        self.paginator.totalPages = math.ceil(totalrecords / displayedrecords)


    def goToPage(self,number):
        self.paginator.openPage(n = number)

    def scrap(self):
        element = self.driver.find_element_by_xpath("//div[@role = 'navigation']/preceding-sibling::ul")
        articles = element.find_elements(By.TAG_NAME,'article')
        print()
        list = []
        for ar in range(len(articles)):
            try:
                l = self.getSingleRecord(articles[ar])
                #   print("list ", l)
                list.append(l)
            except Exception as e:
                #print("Exception at "+str(articles[ar].text)+"\n"+str(e))
                pass
        dataa = pd.DataFrame(list,columns= ['currency','price','Location','Beds','Baths','Area','Title','Description'])

        return dataa

    def getSingleRecord(self,article):
        templist = []
        currency = article.find_element_by_xpath(".//span[@aria-label = 'Listing currency']").text
        price = article.find_element_by_xpath(".//span[@aria-label = 'Listing price']").text
        # trustedbadge =len(article.find_elements(By.XPATH ,".//svg[@aria-label = 'Trusted badge']")) != 0
        # titaniumbadge = len(article.find_elements(By.XPATH,".//span[@aria-label = 'Titanium badge']")) != 0
        location = article.find_element_by_xpath(".//div[@aria-label = 'Listing location']").text
        if len(article.find_elements(By.XPATH,".//span[@aria-label = 'Beds']")) > 0:
            beds = article.find_element_by_xpath(".//span[@aria-label = 'Beds']").text
        else:
            beds = 0
        if len(article.find_elements(By.XPATH,".//span[@aria-label = 'Baths']")) > 0:
            baths = article.find_element_by_xpath(".//span[@aria-label = 'Baths']").text
        else:
            baths = 0
        area = article.find_element_by_xpath(".//span[@aria-label = 'Area']").text
        title = article.find_element_by_xpath(".//h2[@aria-label = 'Listing title']").text
        try :
            description = article.find_element_by_xpath(".//div[@title = '"+title+"']/following-sibling::div[3]").text
        except:
            description = ""
        templist.append(currency)
        templist.append(price)
        # templist.append(trustedbadge)
        # templist.append(titaniumbadge)
        templist.append(location)
        templist.append(beds)
        templist.append(baths)
        templist.append(area)
        templist.append(title)
        templist.append(description)

        return templist


    def scrapSinglePage(self,p):
        self.goToPage(p)
        return self.scrap()

    def scrapPageRange(self,s,e):
        for i in range(s,e+1):
            yield self.scrapSinglePage(i)

    def end(self):
        try :
            self.driver.close()
        finally:
            self.driver.quit()


############################################################################

link = "https://www.zameen.com/Houses_Property/Islamabad_I_10-173-"
scrap = Scrapper( link = link)
scrap.goToPage(1)
scrap.getMetaData()




# simple version for working with CWD
folder_size = len([name for name in os.listdir('.') if os.path.isfile(name)])


# to scrap single page
# sn = scrap.scrapSinglePage(1)
# print(tabulate(sn,headers='keys'))
# sn.to_csv("data"+str(folder_size+1)+".csv",mode = 'a',header=False,index=False)



# to scrap multiple pages at once and saving data to csv
dat = scrap.scrapPageRange(1,12)
for d in dat:
    d.to_csv("data"+str(folder_size+1)+".csv",mode = 'a',header = False, index=False)
    print(tabulate(d,headers='keys'))


print("\nResults saved in data"+str(folder_size+1)+".csv")
scrap.end()

# # Reading Scraped data from csv file to generate visualizations.
# zameen = pd.read_csv("data11.csv",names=['currency','price','Trusted','Titanium','Location','Beds','Baths','Area','Title','Description']);
# g = sns.pairplot(zameen,hue='label',diag_kind="kde")
# g.map_lower(sns.kdeplot, levels=1)


# Visualizing the data w.r.t Price and Area
zameen = pd.read_csv("data"+str(folder_size+1)+".csv",names=['currency','price','Location','Beds','Baths','Area','Title','Description']);

result = zameen.groupby('Area')['price'].apply(list)
result = result.apply(lambda x: [float(i.split(' ')[0]) for i in x]).apply(mean)

height = result.values
bars = result.keys().map(lambda x: float(x.split(' ')[0]))
y_pos = np.arange(len(bars))
plt.bar(y_pos, height, color=(0.2, 0.4, 0.6, 0.6))
plt.xticks(y_pos, bars)
plt.legend(['Average Prices in I-10, Islamabad'])
plt.xlabel('Area in Marlas')
plt.ylabel('Price in Crore')
plt.show()