from botAPI import tgBot
import time
import numpy as np
import os
import json
from getZyIns import getInfo as getIns

personDB=dict()
dbName='personDb.npy'
cmdListFileName='command.json'
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
    with open(cmdListFileName,'r') as f:
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
    bot.sendTEXT(id,'let me find out how many times of zyins you have already taken...')
    retZyinsInfo(bot,id)

def retZyinsInfo(bot:tgBot,id):
    retCode,ret=getIns(personDB[id]['stdId'])
    if retCode==1:
        bot.sendTEXT(id,'your ins times is {}'.format(ret[1]))
    else:
        bot.sendTEXT(id,'I think maybe some error occur, I cannot find your info...')

def queryStuId(bot:tgBot,id):
    global statusDict
    bot.sendTEXT(id,'may I have your SJTU student id?')
    statusDict[id]=haveStuId

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
        elif info=='/askIns':
            if 'stdId' not in personDB[id] or personDB[id]['stdId']==None:
                queryStuId(bot,id)
            else:
                retZyinsInfo(bot,id)
        elif info=='/stuId':
            queryStuId(bot,id)
    else:
        bot.sendTEXT(id,"sorry I don't like this command...")

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