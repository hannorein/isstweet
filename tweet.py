# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import shutil
from datetime import datetime
import urllib
import requests

ha_url = "http://www.heavens-above.com/PassSummary.aspx?satid=25544&lat=43.7654&lng=-79.206&loc=Toronto&alt=141&tz=EST"
cached_file = "pass.html"
if not os.path.isfile(cached_file):
    response = requests.get(ha_url,stream=True)
    response.raw.decode_content = True
    with open('pass.html', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
with open(cached_file, 'r') as content_file:
    content = content_file.read()

soup = BeautifulSoup(content, "html.parser")
table = soup.find('table',{ "class" : "standardTable" })

def makelist(table):
  result = []
  allrows = table.findAll('tr')
  for row in allrows[2:]:
    result.append([])
    allcols = row.findAll('td')
    href = ""
    for col in allcols:
        a = col.find("a")
        if a is not None:
            href="http://www.heavens-above.com/"+a["href"]
        thestrings = [s for s in col.findAll(text=True)]
        thetext = ''.join(thestrings)
        result[-1].append(thetext)
    result[-1].append(href)
  return  result

for m in makelist(table):
    date, mag, starttime, startalt, startaz, hightime, highalt, highaz, endtime, endalt, endaz, passtype, link = m
    fn = "".join(x for x in date+starttime if x.isalnum())+".png"
    fn = "png/"+fn

    # get images
    if not os.path.isfile(fn):
        response = requests.get(link)
        response.raw.decode_content = True

        soup = BeautifulSoup(response.text, "html.parser")
        img = soup.find('img',{ "id" : "ctl00_cph1_imgViewFinder" })
        imgsrc = "http://www.heavens-above.com/"+img["src"]

        r = requests.get(imgsrc, stream=True)
        with open(fn, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)  

now = datetime.now()

debug = True
for m in makelist(table):
    date, mag, starttime, startalt, startaz, hightime, highalt, highaz, endtime, endalt, endaz, passtype, link = m
    fn = "".join(x for x in date+starttime if x.isalnum())+".png"
    fn = "png/"+fn

    start = datetime.strptime(date+" %d "%now.year+starttime, '%d %b %Y %H:%M:%S')
    minutes = (start - now).total_seconds() / 60.0
    ft = "".join(x for x in date+starttime if x.isalnum())+".tweeted"
    # tweet 1 hour before
    if (minutes <61. and minutes > 59.) or debug:
        ft1 = "tweeted1/"+ft
        if not os.path.isfile(ft1) or debug:
            debug = False # only once
            with open(ft1, 'w') as f:
                message = "#ISS flying over #Toronto in 1 hour! Track {0} to {1}, altitude {2}deg, mag {3}. 🚀 {4}".format(startaz, endaz, highalt[0:-1], mag,urllib.quote(link))
                print(len(message), message)
                f.write(message)

            os.system("bash uploadToTwitter.bash %s %s"%(ft1,fn))
    # tweet 10 minutes before
    if (minutes <11. and minutes > 9.) or debug:
        ft2 = "tweeted2/"+ft
        if not os.path.isfile(ft1) or debug:
            debug = False # only once
            with open(ft1, 'w') as f:
                message = "#ISS flying over #Toronto in 10 minutes! Track {0} to {1}, altitude {2}deg, mag {3}. 🚀 {4}".format(startaz, endaz, highalt[0:-1], mag,urllib.quote(link))
                print(len(message), message)
                f.write(message)

            os.system("bash uploadToTwitter.bash %s %s"%(ft1,fn))
    # tweet right now
    if (minutes <1. and minutes > -1) or debug:
        ft2 = "tweeted3/"+ft
        if not os.path.isfile(ft1) or debug:
            debug = False # only once
            with open(ft1, 'w') as f:
                message = "#ISS flying over #Toronto right now! Look up! Track {0} to {1}, altitude {2}deg, mag {3}. 🚀 {4}".format(startaz, endaz, highalt[0:-1], mag,urllib.quote(link))
                print(len(message), message)
                f.write(message)

            os.system("bash uploadToTwitter.bash %s %s"%(ft1,fn))

    


