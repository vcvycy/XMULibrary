from XMULogin import XMULogin
from bottle import *
if __name__ == "__main__":
    xmu=XMULogin()
    print(xmu.login("23020161153315", "159147"))