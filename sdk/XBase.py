#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-03-03 01:36:47
# @Author  : Robin

from HttpHolder import HttpHolder
import json

class XBase(object):
	def __init__(self, username="nobody", password="nobody", app="app", apiurl="http://xbase.sinaapp.com/api/"):
		super(XBase, self).__init__()
		self.username = username
		self.password = password
		self.baseurl = '%s%s'%(apiurl, app)
	
	def __gethttp__(self):
		import urllib
		au = '%s:%s'%(self.username, self.password)
		au = 'Basic %s'%urllib.base64.b64encode(au)
		return HttpHolder(headers={'Authorization':au})

	def __getitem__(self, key):
		'''
		获取单个记录
		'''
		h = self.__gethttp__()
		url = '%s/%s'%(self.baseurl, key)
		return h.open_html(url)

	def __setitem__(self, key, value):
		'''
		设置单个记录
		'''
		h = self.__gethttp__()
		url = '%s/%s'%(self.baseurl, key)
		h.open_html(url, data=value)

	def items(self):
		'''
		获取所有记录元组
		'''
		h = self.__gethttp__()
		dic = json.loads(h.open_html(self.baseurl))
		return dic.items()

if __name__ == '__main__':
	xb = XBase()
	xb['t'] = '中国'
	print xb['t']
	print xb.items()


