# coding: UTF-8 

'''

def hello():  
    return 'hello everyone, my name is 侯海涛。'  
    
def application(environ, start_response):
    start_response('200 ok', [('content-type', 'text/plain')])
    return hello()  
    #return ['Hello, SAE!']
'''


import hashlib  

import web  

import lxml  

import time  

import os  

import urllib2,json  

from lxml import etree  

import sae              

import random

import re  

import web.db
import sae.const



db = web.database(
    dbn='mysql',
    host=sae.const.MYSQL_HOST,
    port=int(sae.const.MYSQL_PORT),
    user=sae.const.MYSQL_USER,
    passwd=sae.const.MYSQL_PASS,
    db=sae.const.MYSQL_DB
)


def updatelocal(member, location_x, location_y):
    
    #myvar = dict(name=member)
    #results =  db.select('location_info', myvar, where="member = $name")
    
    
    results = db.query("SELECT * FROM `location_info` where member = '%s' "%member)
    
    
    if len(results) == 0:
    
    	return db.insert('location_info', member=member, location_x=location_x, location_y=location_y)
    else:
        return db.update('location_info', where="member = '%s'"%member, location_x=location_x, location_y=location_y)
    
  
def getlocal(member):
    
    results = db.query("SELECT * FROM `location_info` where member = '%s' "%member)
    
    if len(results) == 0:
        return 0,0
    else:
        tmp = results[0] 
        return tmp['location_x'],tmp['location_y']



# 首页
class hello:
    
    
    def GET(self):  

        web.header('Content-Type', 'text/html; charset=UTF-8')
        return '<h1>你好，我是侯海涛 ！</h1>'
    
    



# 测试
class test:
    
    def GET(self):  
        
        #url = "https://api.weixin.qq.com/cgi-bin/groups/get?access_token=o4OfP6HNAMv-2A9vQ_74qoC1OJpPL2lKqUpFkKO4_AYE-76u-PEDN7Yi9EIpktLC-7w2VHD_nNfyoJWsb0X-4A9Uc_3KwLZVEb9cvsx2z_I"
                    
        #req = urllib2.Request(url)
        #res = urllib2.urlopen(req)
        #html = res.read()
        
        #print html
                    

        web.header('Content-Type', 'text/html; charset=UTF-8')
        return 'test ！'
    


    
    
    
# 有道翻译
def youdao(word):
    word = word.encode('utf-8')
    qword =urllib2.quote(word)
    baseurl =r'http://fanyi.youdao.com/openapi.do?keyfrom=share360&key=743803410&type=data&doctype=json&version=1.1&q='
    url =baseurl+qword
    resp =urllib2.urlopen(url)
    fanyi =json.loads(resp.read())
    if fanyi['errorCode'] ==0:        
        if 'basic' in fanyi.keys():
            trans =u'%s:\n%s\n%s\n网络释义：\n%s'%(fanyi['query'],''.join(fanyi['translation']),''.join(fanyi['basic']['explains']),''.join(fanyi['web'][0]['value']))
            return trans
        else:
            trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'],''.join(fanyi['translation']))        
            return trans
    elif fanyi['errorCode'] ==20:
        return u'对不起，要翻译的文本过长'
    elif fanyi['errorCode'] ==30:
        return u'对不起，无法进行有效的翻译'
    elif fanyi['errorCode'] ==40:
        return u'对不起，不支持的语言类型'
    else:
        return u'对不起，您输入的单词%s无法翻译,请检查拼写'%word

    
# 微信测试  
class WeixinInterface:  

   

    def __init__(self):  

        self.app_root = os.path.dirname(__file__)  

        self.templates_root = os.path.join(self.app_root, 'templates')  

        self.render = web.template.render(self.templates_root)  

   

    def GET(self):  

        #获取输入参数  

        data = web.input()  

        signature=data.signature  

        timestamp=data.timestamp  

        nonce=data.nonce  

        echostr=data.echostr  

        #自己的token  

        token="dingding" #这里改写你在微信公众平台里输入的token  

        #字典序排序  

        list=[token,timestamp,nonce]  

        list.sort()  

        sha1=hashlib.sha1()  

        map(sha1.update,list)  

        hashcode=sha1.hexdigest()  

        #sha1加密算法  

   

        #如果是来自微信的请求，则回复echostr  

        if hashcode == signature:  

            return echostr 
        
        
    def POST(self):  

        str_xml = web.data() #获得post来的数据  

        xml = etree.fromstring(str_xml)#进行XML解析  

        

        msgType=xml.find("MsgType").text  

        fromUser=xml.find("FromUserName").text  

        toUser=xml.find("ToUserName").text  
        

        
        if msgType == "event":
            mscontent = xml.find("Event").text
            if mscontent == "subscribe":
                replayText = u'''感谢您关注【分享你我他】\n我是侯叮叮\n我们为您提供本地生活指南，做最好的本地微信平台。\n目前平台功能如下：\n【1】 查天气，如输入：北京天气\n【2】 查公交，如输入：北京 公交 518\n【3】 翻译，如输入：翻译 你好\n【4】 收听音乐，请输入：音乐 \n【5】 获取附近相关信息，例如输入：周边 饭店\n更多内容，敬请期待...'''
                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            if mscontent == "unsubscribe":
                replayText = u'我现在功能还很简单，知道满足不了您的需求，但是我会慢慢改进，欢迎您以后再来'
                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
    
    
        # 获取位置
    	if msgType == "location":
            
            Location_X = xml.find("Location_X").text
            Location_Y = xml.find("Location_Y").text
            Label = xml.find("Label").text
            #print "fffff"+Label
            
            replayText = u'您的位置： 纬度 ' + Location_X + ";" + u'经度 ' + Location_Y + u"\n具体地址：" + Label
            
            updatelocal(fromUser,Location_X,Location_Y)
            
            return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            
            
   

    	
        if msgType == "text":
            content=xml.find("Content").text#获得用户所输入的内容  
            
            
            #http://api.36wu.com/Bus/GetLineInfo?city=北京&line=509
            
            
            reObj1 = re.compile(u'天气')
            reObj2 = re.compile(u'公交')
            reObj3 = re.compile(u'翻译')
            reObj4 = re.compile(u'周边')
            
            try:
                
                if len(reObj2.findall(content)) >  0:
                    
                    tmp = content.split()
                    
                    word = tmp[0].encode('utf-8')
                    qword =urllib2.quote(word)
                    url = "http://api.36wu.com/Bus/GetLineInfo?city="+qword +"&line=" + tmp[2]
                    
                    req = urllib2.Request(url)
                    res = urllib2.urlopen(req)
                    html = res.read()
                    jsonData = json.loads(html)
                    #print jsonData
                    
                    replayText = u"【" + jsonData['data'][0]['name'] + u"】" + "\n" + jsonData['data'][0]['info'] + "\n\n" + jsonData['data'][0]['stats'] 
                    
                    return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
                    
                 
                # 周边    
                elif len(reObj4.findall(content)) >  0:
                    
                    
                    tmp = content.split()
                    
                    word = tmp[1].encode('utf-8')
                    qword =urllib2.quote(word)
                    
                    
                    #http://api.map.baidu.com/place/v2/search?q=银行&region=北京&output=json&ak=188cd1fcce2268d056829ef33b7e2e78
                    #http://api.map.baidu.com/place/v2/search?q=ATM&location=40.043,116.287&output=json&ak=188cd1fcce2268d056829ef33b7e2e78
                    
     		
                    Location_X ,Location_Y = getlocal(fromUser)
                    
                    
                    if Location_X == 0:
                        
                        return self.render.reply_text(fromUser,toUser,int(time.time()),u"对不起，获取您的位置失败，请重新发送您的位置进行定位！")
                
                    
                    url = "http://api.map.baidu.com/place/v2/search?q="+qword+"&page_size=7&page_num=0&location="+str(Location_X)+","+str(Location_Y)+"&output=json&ak=188cd1fcce2268d056829ef33b7e2e78&scope=2"
                    
                    req = urllib2.Request(url)
                    res = urllib2.urlopen(req)
                    html = res.read()
                    jsonData = json.loads(html)
                    
                    
                    num = 0
                    content = []
                    
                    for tmp in jsonData['results']:
                        num += 1
                        
                        item = {}
                        item['descrip'] = ""
                        item['hqUrl'] = ""
                        item['picUrl'] = ""
                        title =  u"【"+tmp["name"] + u"】" +"\t "+tmp["address"] 
                        if num == 1 :
                            item['title'] = u"【附近的周边信息如下】\n" 
                            item['picUrl'] = "http://www.scly168.com/TMFile/TripPic/1422_b.jpg"
                        else:
                            
                            if 'detail_url' in tmp["detail_info"]:
                                #item['hqUrl'] =  tmp["detail_info"]["detail_url"]
                                item['hqUrl'] =  "http://share360.sinaapp.com/"
                                
                            item['title'] = title
                                
                                
                        content.append(item)
                                
                    return self.render.reply_news(fromUser,toUser,int(time.time()),num,content) 
                    
                    
                    
                
                elif len(reObj1.findall(content)) >  0:
                    
                    word = content.encode('utf-8')
                    qword =urllib2.quote(word)
        
                    url = "http://api.map.baidu.com/telematics/v3/weather?location="+qword +"&output=json&ak=188cd1fcce2268d056829ef33b7e2e78"
                    
                    req = urllib2.Request(url)
                    res = urllib2.urlopen(req)
                    html = res.read()
                    jsonData = json.loads(html)
                    
                    result = ""
                    
                    #for tmp in jsonData['results'][0]['index']:
                    #    result = result + tmp["title"] + u"："+tmp["zs"]  + "\n" + tmp["tipt"] + u"："+tmp["des"] + "\n"
                    
                    #for tmp in jsonData['results'][0]['weather_data']:
                    #    result = result + tmp["date"] + "\t "+tmp["weather"]  + "\t" + tmp["wind"] + "\t"+tmp["temperature"] + "\n" 
                    #    result = result + "---------------------------" + "\n" 
                    #return self.render.reply_text(fromUser,toUser,int(time.time()),result) 
                    today = jsonData['results'][0]['weather_data'][0]
                    
                    
                    title = u"【" + jsonData['results'][0]['currentCity'] + u"】" + today["date"] + "\t "+today["weather"]  + "\t" + today["wind"] + "\t"+today["temperature"] 
                    descrip = ""
                    picUrl = today["dayPictureUrl"]
                    hqUrl = picUrl
                    
                    num = 0
                    content = []
                    
                    for tmp in jsonData['results'][0]['weather_data']:
                        num += 1
                        
                        item = {}
                        item['descrip'] = ""
                        item['hqUrl'] = ""
                        title = tmp["date"] + "\t "+tmp["weather"]  + "\t" + tmp["wind"] + "\t"+tmp["temperature"] 
                        picUrl = tmp["dayPictureUrl"]
                        if num == 1 :
                            item['title'] = u"【" + jsonData['results'][0]['currentCity'] + u"】" + title
                            item['picUrl'] = "http://s3.sinaimg.cn/bmiddle/61c798a3x776d43c8ec32&690"
                        else:
                            item['title'] = title
                            item['picUrl'] = picUrl
                        
                        content.append(item)
                    
                    return self.render.reply_news(fromUser,toUser,int(time.time()),num,content) 
                
                elif content.isdigit():
    
                    #if int(content) == 1:
                    #    return self.render.reply_text(fromUser,toUser,int(time.time()),u"hi，你好！") 
                    #else:
                    #    return self.render.reply_text(fromUser,toUser,int(time.time()),u"hi，数字！"+content) 
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"hi，您输入了数字："+content) 
                    
                elif content.lower() == u'音乐':
                    musicList = [
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/destiny.mp3','Destiny',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/5days.mp3','5 Days',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/Far%20Away%20%28Album%20Version%29.mp3','Far Away (Album Version)',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/%E5%B0%91%E5%B9%B4%E6%B8%B8.mp3',u'少年游',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/%E8%8F%8A.mp3',u'菊--关喆',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/%E7%A6%BB%E4%B8%8D%E5%BC%80%E4%BD%A0.mp3',u'离不开你',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/%E9%99%8C%E7%94%9F%E4%BA%BA.mp3',u'陌生人',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/%E8%8A%B1%E5%AE%B9%E7%98%A6.mp3',u'花容瘦',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/%E4%B9%98%E5%AE%A2.mp3',u'乘客',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/If%20My%20Heart%20Was%20A%20House.mp3',u'If My Heart Was A House',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/Hello%20Seattle%EF%BC%88Remix%E7%89%88%EF%BC%89.mp3',u'Hello Seattle（Remix版',u'献给我的宝贝侯叮叮'],
                        [r'http://bcs.duapp.com/yangyanxingblog3/music/Everybody%20Hurts.mp3',u'Everybody Hurts',u'献给我的宝贝侯叮叮']                            
                    ]
                    music = random.choice(musicList)
                    musicurl = music[0]
                    musictitle = music[1]
                    musicdes =music[2]
                    return self.render.reply_music(fromUser,toUser,int(time.time()),musictitle,musicdes,musicurl)
                
                elif len(reObj3.findall(content)) >  0:
                    tmp = content.split()
                    youdao_content = youdao(tmp[1])
                    return self.render.reply_text(fromUser,toUser,int(time.time()),youdao_content) 
    
                else:
                    
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"hi，我是侯叮叮，微信功能还在开发中，暂时没有什么功能，您刚才说的是："+content) 
            
            except Exception,e:
                print str(e)
                
                return self.render.reply_text(fromUser,toUser,int(time.time()),u"hi，我是侯叮叮，对不起，您输入的有误！") 


           
                  
       
                   
            
urls = (             
'/','hello',
'/test','test',
            
'/weixin','WeixinInterface'
            
)              
            
               
            
app_root = os.path.dirname(__file__)              
            
templates_root = os.path.join(app_root, 'templates')     
            
render = web.template.render(templates_root)             

   

app = web.application(urls, globals()).wsgifunc()  

application = sae.create_wsgi_app(app) 
