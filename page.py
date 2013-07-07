#!/usr/bin/python
#-*- coding:utf8 -*-
import os
import re
import sys
import datetime
from hyde.generator import Generator
from hyde.fs import File, Folder
#from hyde.model import Config, Expando
from hyde.site import Node, RootNode, Site
from BeautifulSoup import BeautifulSoup
from xml.sax.saxutils import unescape

SITE_ROOT = Folder('.')
site = Site(SITE_ROOT)
blog = RootNode(SITE_ROOT.child_folder('content/blog'), site)
site.load()

gen = Generator(site)
gen.generate_all()

class Article(object):
    def __init__(self, relpath, html):
        self._ht = html
        self._meta = {}
        soup = BeautifulSoup(self._ht)
        contents = soup.find('article')
        self._title = contents.find('h1').renderContents().decode('utf8')
        title = ('<a href="/%s" class="title">%s</a>' % (relpath, self._title))

        contents.find('h1').contents[0].replaceWith(title)
        body = contents.renderContents()
        self._relpath = relpath
        date = soup.find('p', {'class': 'date'}).renderContents().strip()
        y, m, d = [int(d) for d in date.split('-')]
        self._date = datetime.date(y, m, d)
        for div in contents.findAll('div'):
            """ Ignore syntax highlight """
            if not div.has_key('class'): continue
            if div['class'] in ['codebox', 'highlight']: continue
            body = re.sub(str(div), '', body)
        """
        titleにリンクを付けるためにunescapeしてる
        """
        self._body = unescape(body)

    @property
    def relpath(self):
        return self._relpath

    @property
    def body(self):
        return self._body

    @property
    def date(self):
        return self._date

allarticles = []
pages = []
pagebox = []
num_entry = 5

"""
Get articles
"""
for year in ['2012', '2013']:
    blog = RootNode(SITE_ROOT.child_folder('content/blog/%s' % year), site)
    blog.load()
    for page in blog.walk_resources():
        relpath = 'blog/%s/%s' % (year, page.relative_path)
        deploy_file = File(Folder(site.config.deploy_root_path).child(relpath))
        article = Article(relpath, deploy_file.read_all())
        allarticles.append(article)

"""
Group articles
"""
allarticles = sorted(allarticles, key=lambda x:x.date, reverse=True)
for article in allarticles:
    if len(pagebox) >= num_entry:
        pages.append(pagebox)
        pagebox = []
    pagebox.append(article)
pages.append(pagebox)

for pid, page in enumerate(pages):
    pid += 1
    pagepath = SITE_ROOT.child('content/blog/page/%d/' % pid)
    nextpagepath = "/blog/page/%d/" % (pid - 1)
    prevpagepath = "/blog/page/%d/" % (pid + 1)

    pagefile = File(SITE_ROOT.child('content/blog/page/%d/index.html' % pid))
    if not os.path.exists:
        Folder(pagefile.parent).make()
    text = """---
extends: base.j2
title: Blog
---

{% block content %}
{% mark content %}

"""
    for article in page:
        text += article.body.decode('utf8') + '<br><br>'

    text += "<div class=\"bottom_article_nav\">\n"
    if pid != 1:
        text += ('<div class="next"><a href="%s">newer</a> &gt;</div>\n' %
                nextpagepath)

    if pid != len(pages):
        text += ('<div class="prev">&lt; <a href="%s">older</a></div>\n' %
                prevpagepath)
    text += "</div>\n"
    text += ('<div class="center"><a href="{{ content_url(archive) }}">archive</a></div>\n')

    text += '{% endmark %}\n'
    text += '{% endblock %}\n'
    pagefile.write(text)
