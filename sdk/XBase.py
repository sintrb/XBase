#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-03-03 01:36:47
# @Author  : Robin

from HttpHolder import HttpHolder
import json

class XBase(object):
	def __init__(self, username="nobody", password="nobody", app="app", apiurl="http://127.0.0.1:9999/api/"):
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
		if isinstance(value, unicode):
			value = value.encode('utf-8')
		elif not isinstance(value, str):
			value = str(value)
		if key!=None and not isinstance(key, str):
			key = str(key)
		h = self.__gethttp__()
		if key:
			url = '%s/%s'%(self.baseurl, key)
		else:
			url = self.baseurl
		h.open_html(url, data=value)
	def add(self, value):
		self.__setitem__(None, value)
	def items(self):
		'''
		获取所有记录元组
		'''
		h = self.__gethttp__()
		dic = json.loads(h.open_html(self.baseurl))
		return dic.items()

if __name__ == '__main__':
	xb = XBase()
	xb['t'] = u'中国'
	# print xb['t']
	# print xb.items()


