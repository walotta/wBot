import os
import getpass
import cryptocode
import hashlib
import requests
import time
import threading

def hash(msg):
    tmp=hashlib.sha256(str(msg).encode('utf-8'))
    tmp=tmp.hexdigest()
    return tmp

class tgBot:
    tokenFileName='token.encrypt'
    tokenHashFileName='token.hash'
    logFileName='bot.log'
    proxies = { "http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890",}

    def makePOST(self,method,info=None):
        try:
            r=requests.post('https://api.telegram.org/bot{}/{}'.format(self.token,method), proxies=self.proxies, data=info)
            retJson=r.json()
        except:
            return 0,None
        if not retJson['ok']:
            print('connect error!')
            print(retJson)
            return 0,None
        return 1,retJson['result']

    def sendTEXT(self,chat_id,text,parse_mode=None):
        info={'chat_id':chat_id,'text':text}
        if parse_mode!=None:
            info['parse_mode']=parse_mode
        ret=self.makePOST('sendMessage',info)
        return ret

    def getNewMessage(self):
        try:
            info={}
            if self.msgId!=-1:
                info={'offset':self.msgId}
            info['timeout']=self.timeout
            r = self.session.post('https://api.telegram.org/bot{}/{}'.format(self.token,'getUpdates'), proxies=self.proxies, data=info)
        except:
            return 0,None
        if not r.json()['ok']:
            print('connect error!')
            return 0,None
        else:
            if len(r.json()['result'])==0:
                return 2,[]
            else:
                self.msgId=r.json()['result'][-1]['update_id']+1
                return 1,r.json()['result']

    def __init__(self):
        print('tgBot init...')
        token=''
        self.msgId=-1
        self.session=requests.Session()
        self.timeout=600
        self.replyMessage=None
        self.planList=[]
        self.interval=1
        # get bot token
        if os.path.exists(tgBot.tokenFileName):
            # already have token
            pwd=getpass.getpass('enter your key to unlock your bot token: ')
            token=''
            with open(tgBot.tokenFileName,'r') as f:
                token=f.read()
            result=cryptocode.decrypt(token,pwd)
            while not result:
                print('password is incorrect!')
                pwd=getpass.getpass('enter your key to unlock your bot token: ')
                result=cryptocode.decrypt(token,pwd)
            token=result
            Htoken=hash(token)
            with open(tgBot.tokenHashFileName,'r') as f:
                oriHash=f.read()
                if oriHash!=Htoken:
                    print('error! token File is broken')
                    exit(1)
        else:
            # accept token
            token=input('enter your token: ')
            pwd=getpass.getpass('enter your password to protect your token: ')
            repeatPwd=getpass.getpass('repeat your password: ')
            while pwd!=repeatPwd:
                print('your two password is not the same one!')
                pwd=getpass.getpass('enter your password to protect your token: ')
                repeatPwd=getpass.getpass('repeat your password: ')
            Htoken=hash(token)
            encryptToken=cryptocode.encrypt(token,pwd)
            with open(tgBot.tokenFileName,'w') as f:
                f.write(encryptToken)
            with open(tgBot.tokenHashFileName,'w') as f:
                f.write(Htoken)
        self.token=token
        access,myInfo=self.getMe()
        if access!=1:
            print('tgBot init fail!')
            print(myInfo)
            exit(1)
        else:
            def listen(self):
                retCode,ret=self.getNewMessage()
                if retCode==1:
                    for m in ret:
                        try:
                            self.unpackMessage(m)
                        except:
                            print('deal with message error!')
                elif retCode<1:
                    print('get message error!')
            self.addPlan([listen])
            print('tgBot {}({}) init finish!'.format(myInfo['id'],myInfo['username']))

    def getMe(self):
        return self.makePOST('getMe')

    def addPlan(self,plans:list):
        for p in plans:
            def warpFunc():
                while True:
                    p(self)
                    time.sleep(self.interval)
            t = threading.Thread(target=warpFunc)
            t.setDaemon(True)
            self.planList.append(t)

    def run(self):
        for p in self.planList:
            p.start()

    def checkPlansRunning(self):
        ret=[]
        for p in self.planList:
            ret.append(p.is_alive())
        return ret

    def unpackMessage(self,msg:dict):
        if 'message' in msg:
            self.replyMessage(self,msg['message'])
        else:
            print('message type cannot deal with!')
