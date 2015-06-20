#-*-: coding:utf-8 -*-
import sys
import yaml
import datetime
from collections import defaultdict

class MetaInfo:
    def __init__():
        self.orig = ""

num = 0
meta_text = ""
body = ""
for line in sys.stdin:
#    line = line.strip()
    if line.startswith("==="):
        num += 1
    else:
        if num <= 1:
#            meta_text += line + "\n"
            meta_text += line.strip() + "\n"
        else:
            if "{% block content %}" in line:
                continue
            elif "{% mark content %}" in line:
                continue
            elif "endmark" in line:
                continue
            elif "endblock" in line:
                continue
            elif line.startswith("{% syntax "):
                lang = line.split()[2]
                body += "{{< highlight %s >}}\n" % lang
            elif line.startswith("{% endsyntax"):
                body += "{{< /highlight >}}\n"
            else:
#                body += line.decode('utf8') + "\n"
                body += line.decode('utf8')

#print meta_text
meta = yaml.load(meta_text)
print "+++"
for k, v in meta.iteritems():
    if k == "created":
        k = "date"
    elif k == "extends" or k == "index":
        continue
    if type(v) == int:
        print "%s = %d" % (k, v)
    elif type(v) == list:
        print k, " = [",
        for vv in v:
            print '"%s",' % vv,
        print "]"
    elif type(v) == datetime.date:
        print "%s = \"%s\"" % (k, v.strftime("%Y-%m-%d"))
    else:
        print "%s = \"%s\"" % (k, v.encode('utf8'))
print "\n+++"

print body.encode('utf8')
