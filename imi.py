"""
Author: miaobuao
repo:   https://github.com/miaobuao/ImitateWebSite
mirror: https://gitee.com/miaobuao/ImitateWebSite
"""

import sys
import meo
import threading
import re
import os
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse


def isHttps(https_url):
    try:
        if requests.get(https_url).status_code == 200:
            return True
    except:
        return False


def checkout_ssl(url):
    info = urlparse(url)
    path = ''
    oldpath = info[2]
    for i in oldpath.split("/"):
        if i:
            path += ('/'+i)
    if not info[0]:
        https = "https://"+info[1]+path
        if isHttps(https):
            return https
        else:
            return "http://"+info[1]+path
    else:
        return info[0]+"://"+info[1]+path


class Download(threading.Thread):

    path: str
    url:  str
    resp: requests.Response

    def add(self, url, path):
        self.path = path
        self.url = checkout_ssl(url)
        info = os.path.split(self.path)
        if not os.path.isdir(info[0]):
            os.makedirs(info[0])
        try:
            self.resp = requests.get(self.url, stream=True)
        except requests.exceptions.InvalidURL as e:
            meo.screen.red_font(f"Error URL: {self.url}")
            raise e

    def run(self):
        if os.path.exists(self.path) and not os.path.isfile(self.path):
            self.path = os.path.join(self.path, "index.html")
        with open(self.path, 'wb') as f:
            for chunk in self.resp.iter_content(1024):
                if chunk:
                    f.write(chunk)


def isUrl(link):
    if re.match('(http[s]?:)?//[0-9a-zA-Z-_]+\..+', link, re.M | re.I) == None:
        return False
    else:
        return True


def get_relative_path(dir):
    if re.match("\./.+", dir) != None:
        return dir
    else:
        return "./"+dir


def checkout_dir(path):
    info = os.path.split(path)
    if not os.path.isdir(info[0]):
        os.makedirs(info[0])

def baseUrl(url):
    url = checkout_ssl(url)
    info = urlparse(url)[:3]
    path = '/'+'/'.join(info[2].split("/")[:-1])+"/"
    if path == '//':
        path = "/"
    return info[0]+"://"+info[1]+path


def fixSrc(src):
    lists = src.split("/")
    words = []
    for i in lists:
        if i != '':
            words.append(i)
    return "/".join(words)
    
def fixPath(path):
    info = os.path.split(path)
    path = []
    for i in info[0].split('/'):
        if i != '':
            path.append(i)
    path.append(info[1])
    return '/'.join(path)
class Imitate:

    @property
    def html(self):
        resp_enc = self.resp.encoding
        text = self.resp.text.encode(resp_enc).decode(self.encoding)
        return text

    @property
    def content(self):
        return self.resp.content

    @property
    def doc(self):
        doc = bs(self.content, features="lxml")
        return doc

    def __init__(self, url, root="./", encoding=sys.getdefaultencoding(), ignore_err=True):
        self.url = urlparse(url)
        self.oURL = url
        self.root = get_relative_path(root)
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self.text = ''
        self.resp = requests.get(url)
        self.encoding = encoding
        self.ignore_err = ignore_err

    def output(self, path, content):
        checkout_dir(path)
        with open(path, "w", encoding=self.encoding) as f:
            f.write(content)

    def clone_tag(self, tag):
        try:
            attrs = tag.attrs
        except AttributeError as e:
            return

        if src := attrs.get("src", None):
            src_type = "src"
        elif src := attrs.get("href", None):
            src_type = 'href'
        else:
            return
            
        src = src.strip() # type: str
        if isUrl(src):
            info = urlparse(src)
            tar = fixSrc(fixPath(info[1]+info[2]))
            source = self.root+"/" + info[1]+info[2]
        else:
            tar = src
            source = self.root + "/" + src
            src = baseUrl(self.oURL)+"/"+src
        tag.attrs[src_type] = tar
        print(tar)

        try:
            down = Download()
            down.add(src, source)
            down.run()
        except requests.exceptions.InvalidURL as e:
            print(tag)
            print(e)
            exit()

    def clone_doc(self, doc):
        for tag in doc.descendants:
            try:
                self.clone_tag(tag)
            except Exception as e:
                if not self.ignore_err:
                    raise e
        return doc

    def run(self):
        doc = self.doc
        doc = self.clone_doc(doc)

        if os.path.split(urlparse(self.oURL)[2])[1] == '':
            outpath = self.root+'/'+"index.html"
            self.output(outpath, doc.prettify())
        else:
            outpath = self.root+'/'+os.path.split(urlparse(self.oURL)[2])[1]
            self.output(outpath, doc.prettify())
