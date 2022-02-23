from botAPI import tgBot
import time
import random
import numpy as np
import os
import json
import getZyIns

personDB=dict()
dbName='personDb.npy'
cmdDict=dict()
statusDict=dict()
def Init():
    # init db
    global personDB
    if os.path.exists(dbName):
        personDB=np.load(dbName, allow_pickle=True).item()
    else:
        np.save(dbName,personDB)
    #init cmd JSON
    global cmdDict
    with open(tgBot.cmdListFileName,'r') as f:
        cmdDict=json.load(f)

def dbSave():
    global personDB
    np.save(dbName,personDB)

def haveStuId(bot:tgBot,id,info:str):
    global personDB
    global statusDict
    personDB[id]['stdId']=info
    dbSave()
    del statusDict[id]
    bot.sendTEXT(id,'wow, I have already bear your student id in my mind.')
    bot.sendTEXT(id,"Now I can dive into your school's network to find out your personal information.")
    bot.sendTEXT(id,'for example, let me find out how many times of zyins you have already taken...')
    retZyinsInfo(bot,id)

def retZyinsInfo(bot:tgBot,id):
    retCode,ret=getZyIns.getInfo(personDB[id]['stdId'])
    if retCode==1:
        bot.sendTEXT(id,'your ins times is {}'.format(ret[1]))
    else:
        bot.sendTEXT(id,'I think maybe some error occur, I cannot find your info...')

def retZyinsDetail(bot:tgBot,id):
    retCode,info,detail=getZyIns.getDetail(personDB[id]['stdId'])
    if retCode==1:
        ret="I find your bound student id is *{0}*, your total zysalon times is *{1}*, among them, salon times is *{2}* while lecture is *{3}*\. what's more, the details are: "
        ret=ret.format(*info)
        retDetail='\n'.join(detail)
        bot.sendTEXT(id,ret,parse_mode='MarkdownV2')
        bot.sendTEXT(id,retDetail)
    else:
        bot.sendTEXT(id,'I think maybe some error occur, I cannot find your info...')

def queryStuId(bot:tgBot,id):
    global statusDict
    bot.sendTEXT(id,'may I have your SJTU student id?')
    statusDict[id]=haveStuId

personRandlowDict=dict()
def receiveRandomHigh(bot:tgBot,id,info:str):
    high=0
    try:
        high=int(info)
    except:
        bot.sendTEXT(id,'you should only give me a number!')
    else:
        global personRandlowDict
        low=personRandlowDict[id]
        if low>high:
            bot.sendTEXT(id,'you are so bad to give me a upside down number set, but I am a so smart bot that I will give you a number between them, lol')
            low,high=high,low
        bot.sendTEXT(id,'I think *{}* is a good number for now qwq'.format(random.randint(low,high)),parse_mode='MarkdownV2')
        global statusDict
        del statusDict[id]
        del personRandlowDict[id]

def receiveRandomLow(bot:tgBot,id,info:str):
    global personRandlowDict
    try:
        personRandlowDict[id]=int(info)
    except:
        bot.sendTEXT(id,'you should only give me a number!')
    else:
        bot.sendTEXT(id,'give me the higher bound(include)')
        global statusDict
        statusDict[id]=receiveRandomHigh

def dealCmd(bot:tgBot,id,info:str):
    if info[1:] in cmdDict:
        if info=='/start':
            bot.sendTEXT(id,'hello *{}*'.format(personDB[id]['info']['first_name']),parse_mode='MarkdownV2')
        elif info=='/help':
            toSend=['This is all the command I can understand:']
            for name in cmdDict:
                toSend.append('    /{:<7}: {}'.format(name,cmdDict[name]))
            toSend='\n'.join(toSend)
            bot.sendTEXT(id,toSend)
        elif info=='/askins':
            if 'stdId' not in personDB[id] or personDB[id]['stdId']==None:
                queryStuId(bot,id)
            else:
                retZyinsInfo(bot,id)
        elif info=='/insdetail':
            if 'stdId' not in personDB[id] or personDB[id]['stdId']==None:
                bot.sendTEXT(id,'I cannot find out your information before you tell me your SJTU student id, you can tell me with /stuid')
            else:
                retZyinsDetail(bot,id)
        elif info=='/stuid':
            queryStuId(bot,id)
        elif info=='/randint':
            bot.sendTEXT(id,'give me your random lower bound(include)')
            global statusDict
            statusDict[id]=receiveRandomLow
    else:
        bot.sendTEXT(id,"sorry I'm afraid that I don't like this command...")

def dealChat(bot:tgBot,id,info:str):
    global statusDict
    if id not in statusDict:
        bot.sendTEXT(id,'you can start talking to me with some command')
    else:
        statusDict[id](bot,id,info)

def dealMessage(bot:tgBot,msg:dict):
    global personDB
    id=msg['chat']['id']
    if 'text' in msg:
        info=msg['text']
        if id not in personDB:
            # unknow user!
            if info=='/start':
                personDB[id]={'info':msg['chat'],'stuId':None}
                dbSave()
                print('user {} sign in'.format(personDB[id]['info']['first_name']))
                bot.sendTEXT(id,'welcome *{}*\!'.format(personDB[id]['info']['first_name']),parse_mode='MarkdownV2')
                dealCmd(bot,id,'/help')
            else:
                bot.sendTEXT(id,"your identity information is not found in bot's database, please use /start")
        else:
            if info[0]=='/':
                dealCmd(bot,id,info)
            else:
                dealChat(bot,id,info)
                # bot.sendTEXT(id,'sorry, This sentence is too hard for me to understand... :)')
    else:
        bot.sendTEXT(id,'sorry, this type of message is not support now... :)')

def botInit():
    bot=tgBot()
    bot.replyMessage=dealMessage
    # def send_to_whiskey(b:tgBot):
    #     time.sleep(60)
    #     b.sendTEXT(1629396977,'this is a mutiPross test')
    # bot.addPlan([send_to_whiskey])
    return bot

if __name__=='__main__':
    Init()
    bot=botInit()
    bot.run()
    while True:
        cmd=input()
        if cmd=='stop' or cmd=='quit' or cmd=='exit':
            print('stopping bot...')
            dbSave()
            quit()
        elif cmd=='ls -usr':
            for key in personDB:
                print(key,personDB[key]['info']['first_name'])
        elif cmd=='status':
            status=bot.checkPlansRunning()
            runCnt=0
            for s in status:
                if s:
                    runCnt+=1
            print('running: {}/{}'.format(runCnt,len(status)))