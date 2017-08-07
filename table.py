from bs4 import BeautifulSoup
import os.path
import shutil
from datetime import datetime
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

for m in makelist(table):
    date, mag, starttime, startalt, startaz, hightime, highalt, highaz, endtime, endalt, endaz, passtype, link = m
    fn = "".join(x for x in date+starttime if x.isalnum())+".png"

    start = datetime.strptime(date+" %d "%now.year+starttime, '%d %b %Y %H:%M:%S')
    minutes = (start - now).total_seconds() / 60.0
    if minutes <16. and minutes > 14.:
        # tweet
        ft = "".join(x for x in date+starttime if x.isalnum())+".tweeted"
        if not os.path.isfile(ft):
            with open(ft, 'w') as f:
                f.write("tweeted")

            message = "#ISS visible from #Toronto in 15 minutes! @Space_Station will move from %s to %s (altitude: %s, mag: %s). Data from http://heavens-above.com" %(startaz, endaz, highalt, mag)

            print(len(message), message)

    


