import requests
import sys
import os
from bs4 import BeautifulSoup
import random
import urllib.parse
import time

class XMULogin:
    URLLogin        = "http://ids.xmu.edu.cn/authserver/login"
    URLNeedCaptcha  = "http://ids.xmu.edu.cn/authserver/needCaptcha.html"
    URLCaptchaImage = "http://ids.xmu.edu.cn/authserver/captcha.html"
    HEADERS = {
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "http://ids.xmu.edu.cn/authserver/login",
        "Accept-Encoding" : "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,ru;q=0.6,zh-TW;q=0.5"
    }
    def __init__(self):
        return
    def __saveCaptchaTo(self,path="./tmp"):      # 验证码保存到本地，以返回给用户，让用户自己输入
        filename = "%s.captcha.jpg" %(self.sid)
        path=os.path.join(path,filename)
        r=self.sess.get(XMULogin.URLCaptchaImage)
        if r.status_code == 200:
          with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
              f.write(chunk)
          return path
        else:
          return "error.jpg"
    def __needCaptcha(self):                    # 判断是否需要验证码
        payload={
            "username":self.sid,
            "_": int(time.time()*1000)
        }
        r=self.sess.get(XMULogin.URLNeedCaptcha,params=payload)
        # print("need captcha:%s" %(r.text))
        if r.text.strip() == "false":
            return False
        else:
            return True

    def __getHiddenInputParams(self):            # 获取隐藏参数，不知是干嘛的
        resp=self.sess.get(XMULogin.URLLogin)
        soup = BeautifulSoup(resp.text, "html.parser")
        params={
          "lt" : soup.find(attrs={"name":"lt"}).get("value"),
          "dllt" : soup.find(attrs={"name":"dllt"}).get("value"),
          "execution" : soup.find(attrs={"name":"execution"}).get("value"),
          "_eventId" : soup.find(attrs={"name":"_eventId"}).get("value"),
          "rmShown" : soup.find(attrs={"name":"rmShown"}).get("value"),
        }
        # print(params)
        return params

    def __getLoginFailedReason(self,r):          # 通过response返回登陆失败原因
        if r.text.find("无效的验证码") !=-1:
            self.loginFailedReason =  "验证码错误！"
        elif r.text.find("您提供的用户名或者密码有误")!=-1:
            self.loginFailedReason = "您提供的用户名或者密码有误"
        elif r.text.find("认证服务不可用,请稍后再试，或联系管理员")!=-1:
            self.loginFailedReason = "认证服务不可用,请稍后再试，或联系管理员"
        else:
            self.loginFailedReason = "未知错误，请联系管理员"
            # print(r.text)
        return self.loginFailedReason

    def __loginWithoutCaptcha(self):            # 不需要验证码登陆
        payload = self.__getHiddenInputParams()
        payload["username"] = self.sid
        payload["password"] = self.pwd
        resp=self.sess.post(XMULogin.URLLogin,data=payload,headers=XMULogin.HEADERS,timeout=10)
        if resp.text.find("安全退出")!=-1:
            return True
        else:
            self.__getLoginFailedReason(resp)
            return False

    def __loginWithCaptcha(self):               # 需要验证码的登陆
        # print("with captcha")
        path=self.__saveCaptchaTo()
        # print("saveto:"+path)
        payload = self.__getHiddenInputParams()
        payload["captchaResponse"] = input("输入验证码")
        resp=self.sess.post(XMULogin.URLLogin,data=payload,headers=XMULogin.HEADERS,timeout=10)
        if resp.text.find("安全退出")!=-1:
            return True
        else:
            self.__getLoginFailedReason(resp)
            return False
    # public method
    def reloadCaptcha(self):
        return self.__saveCaptchaTo()

    def login(self,sid,pwd):
        self.sess = requests.Session()
        self.sid = sid
        self.pwd = pwd
        if self.__needCaptcha():
            return self.__loginWithCaptcha()
        else:
            return self.__loginWithoutCaptcha()

if __name__ == "__main__":
    login=XMULogin()
    if login.login("23020161153315","159147") == True:
          print("login success")
    else:
          print(login.loginFailedReason)
