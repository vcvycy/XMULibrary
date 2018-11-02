from XMULogin import XMULogin
from bottle import *

@get("/")
def index():
    # print(os.curdir)
    return static_file("index.html","www")
@get("/login")
def login():
    sid = request.query.sid
    pwd = request.query.pwd
    print("%s %s" %(sid,pwd))
    if xmu.login(sid,pwd):
        return "<h1>%s 登陆成功</h1>" %(sid)
    else:
        return "<h1>登陆失败 : %s </h1> " %(xmu.loginFailedReason)
if __name__ == "__main__":
    xmu = XMULogin()
    run(host="0.0.0.0", port=81)