#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
-------------------------------------------------------------
    Creator : 汪春旺
       Date : 2018-09-01
    Project : zhihu
   FileName : run.py
Description : 
-------------------------------------------------------------
"""
from scrapy import cmdline

cmdline.execute('scrapy crawl userinfo'.split())
