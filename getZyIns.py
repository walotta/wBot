import requests
from bs4 import BeautifulSoup
import re

# ret: [学生学号], [参加总次数], [沙龙次数], [院系讲座次数]
def getInfo(studentId):
    try:
        url='https://zysalon.com/result?id={}'.format(studentId)

        html=requests.get(url)
        soup=BeautifulSoup(html.text,'html.parser')
        msg=[]
        id=0
        for child in soup.p.children:
            if id==0 or id==2:
                msg.append(str(child))
            id+=1
        info=[]
        for m in msg:
            for num in re.findall(r"\d+\.?\d*",m):
                info.append(num)
        info=[int(i) for i in info]
        if str(info[0])!=str(studentId):
            return 0,'url student number not fit'
        else:
            return 1,info
    except:
        return 0,'error occur'

# print(getInfo(studentId=520030910142))