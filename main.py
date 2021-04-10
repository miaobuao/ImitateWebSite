import sys
import threading
import re
import os
from bs4.element import PreformattedString
import requests as r
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, uses_netloc

class Download(threading.Thread):
    def __init___(self):
        super(Download, self).__init__()
        self.path = ''
        self.url = ''
        self.r = ''

    def fixUrl(self, url):
        info = urlparse(url)
        path = ''
        oldpath = info[2]
        for i in oldpath.split("/"):
            if i:
                path += ('/'+i)
        return info[0]+"://"+info[1]+path

    def add(self, url, path):
        self.path = path
        self.url = self.fixUrl(url)
        info = os.path.split(self.path)
        if not os.path.isdir(info[0]):
            os.makedirs(info[0])
        self.r = r.get(self.url, stream=True)
        print(self.url+" :: "+self.path)

    def run(self):
        with open(self.path, 'wb') as f:
            for chunk in self.r.iter_content(1024):
                if chunk:
                    f.write(chunk)


class Imitate:

    def isUrl(self, link):
        if re.match('http[s]?://.+\..+', link, re.M | re.I) == None:
            return False
        else:
            return True

    def html(self):
        self.text = self.r.text.encode(self.r.encoding).decode(self.encoding)

    def rightDir(self, dir):
        if(re.match("\./.+", dir) != None):
            return dir
        else:
            return "./"+dir

    def __init__(self, url, root="./"):
        self.url = urlparse(url)
        self.oURL = url
        self.root = self.rightDir(root)
        self.text = ''
        self.doc = ''
        self.r = r.get(url)
        self.encoding = sys.getdefaultencoding()

    def detectDir(self, path):
        info = os.path.split(path)
        if not os.path.isdir(info[0]):
            os.makedirs(info[0])

    def dom(self):
        self.doc = bs(self.r.content, features="lxml")

    def ishtml(self):
        if not self.text:
            self.html()

    def getHtml(self):
        self.isDom()
        return self.doc.prettify()

    def output(self, path, content):
        self.detectDir(path)
        with open(path, "w", encoding=self.encoding) as f:
            f.write(content)

    def outHtml(self, path):
        self.isDom()
        self.output(path, self.doc.prettify())

    def isDom(self):
        if not self.doc:
            self.dom()

    def getContent(self, url):
        return r.get(url).content

    def baseUrl(self, url):
        down = Download()
        url = down.fixUrl(url)
        info = urlparse(url)[:3]
        path = '/'+'/'.join(info[2].split("/")[:-1])+"/"
        if path == '//':
            path = "/"
        return info[0]+"://"+info[1]+path

    def basePath(self, path):
        return self.root+"/" + self.fixPath(path)

    def fixPath(self, path):
        info = os.path.split(path)
        path = []
        for i in info[0].split('/'):
            if i != '':
                path.append(i)
        return '/'.join(path)

    def run(self):
        self.isDom()
        for tag in self.doc.descendants:
            try:
                attrs = tag.attrs
                if attrs["src"]:
                    if self.isUrl(attrs['src']):
                        src = urlparse(attrs["src"])
                        source = self.root+"/" + \
                            src[1].replace(".", '/')+src[2]
                        down = Download()
                        down.add(src, source)
                        down.run()
                        self.doc.find(tag.name, tag.attrs).attrs['src'] = self.fixPath(
                            src[1].replace(".", '/')+src[2])
                    else:
                        src = self.baseUrl(self.oURL)+"/"+attrs['src']
                        source = self.root+"/"+urlparse(src)[2]
                        down = Download()
                        down.add(src, source)
                        down.run()
                        self.doc.find(tag.name, tag.attrs).attrs['src'] = self.fixPath(
                            urlparse(src)[2])
            except:
                pass
        for tag in self.doc.descendants:
            try:
                attrs = tag.attrs
                # print(attrs)
                if attrs["href"]:
                    if self.isUrl(attrs['href']):
                        src = urlparse(attrs["href"])
                        source = self.root+"/" + \
                            src[1].replace(".", '/')+src[2]
                        down = Download()
                        down.add(src, source)
                        down.run()
                        self.doc.find(tag.name, tag.attrs).attrs['href'] = self.fixPath(
                            src[1].replace(".", '/')+src[2])
                        next = self.basePath(self.doc.find(
                            tag.name, tag.attrs).attrs['href'])
                        # im = Imitate(src, next)
                        # im.run()
                    else:
                        src = self.baseUrl(self.oURL)+"/"+attrs['href']
                        source = self.root+"/"+urlparse(src)[2]
                        down = Download()
                        down.add(src, source)
                        down.run()
                        self.doc.find(tag.name, tag.attrs).attrs['href'] = self.fixPath(
                            urlparse(src)[2])
                        next = self.basePath(self.doc.find(
                            tag.name, tag.attrs).attrs['href'])
                        # im = Imitate(src, next)
                        # im.run()
            except:
                pass
        if os.path.split(urlparse(self.oURL)[2])[1] == '':
            self.output(self.root+'/'+"index.html", self.doc.prettify())
        else:
            self.output(
                self.root+'/'+os.path.split(urlparse(self.oURL)[2])[1], self.doc.prettify())

imitate = Imitate(input("输入URL："), input("输入路径："))
imitate.run()
