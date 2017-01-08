# -*- encoding: utf-8 -*-
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import async_timeout
from abc import ABCMeta, abstractmethod
import re
import csv

BaseUrl ="http://tsytaty.ukrayinskoyu.pro//"
TestUrl1 = "site/Цитати.html"
TestUrl2 = "site/дитинство.html"

class ListContent():
	__metaclass__ = ABCMeta
	def __init__(self, link):
          		self._link = link
          		self.records = []
	@abstractmethod
	def getList(self, page):     
 		pass
	def ListToObjs(self,list):
 		for item in list:
 			self.records.append(self.makeObject(item))
	@abstractmethod
	def makeObject(self,item):
 		pass

	async def fetch(self,session, url):
		with async_timeout.timeout(10):
			async with session.get(url) as response:
				return await response.text()
	async def get_html(self,loop,url):
		async with aiohttp.ClientSession(loop=loop) as session:
			html = await self.fetch(session, url)
			return html

class MainPage(ListContent):
	def __init__(self, link, loop, test=False):
		super(MainPage,self).__init__(link)
		HTML = open(self._link,'r').read() if test else loop.run_until_complete(self.get_html(loop,self._link))
		self.ListToObjs(self.getList(HTML))       
	def getList(self, page): 
		bs = BeautifulSoup(page, "html.parser")
		return bs.find_all("button",{"class":"btn-grey"})
	def makeObject(self, item):
		rec = {}
		rec['name'] = item.text
		rec['link'] = re.findall(r"'(.+)'",item['onclick'])[0]
		return rec

class TopicPage(ListContent):
	def __init__(self, link, loop, test=False):
		super(TopicPage,self).__init__(link)
		HTML = open(self._link,'r').read() if test else  loop.run_until_complete(self.get_html(loop,self._link))
		self.ListToObjs(self.getList(HTML,loop)) #save all items to self.records
	def getList(self,page,loop=None):
		bs = BeautifulSoup(page, "html.parser")
		list = bs.find_all("div",{"class":"post-description"})
		N = len(bs.find("nav",{"class":"pagination"}).find_all("li")) # number of pages
		for i in range(1,N):
			HTML= loop.run_until_complete(self.get_html(loop,self._link[:-5]+'-'+str(i)+'.html'))
			bs = BeautifulSoup(HTML, "html.parser")
			list.extend(bs.find_all("div",{"class":"post-description"}))
		return [x for x in list if x]

	def makeObject(self, item):
		rec = {}
		list = re.findall(r"([^\.^\n^!^\?]+[\.|\n|!|\?])",item.text)
		rec['description'] = list[:-1]
		rec['author'] = re.findall(r"([^\n]+)",list[-1])[0]
		return rec
def makeCSV():
	loop = asyncio.get_event_loop()
	home = MainPage(BaseUrl,loop)
	with open("DB.csv", 'w',newline='') as csvfile:
		fieldnames = ['name','link','author','description']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter =";")
		writer.writeheader()
		for item in home.records:
			page = TopicPage(BaseUrl+item['link'],loop)
			for record in page.records:
				record['name']=item['name']
				record['link']=BaseUrl+item['link']
				writer.writerow(record)