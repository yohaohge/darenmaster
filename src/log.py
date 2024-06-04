import threading

logLock = threading.Lock()
logs = []
def addlog(text:str):
    print("添加日志")
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logLock.acquire()
    logs.append(now + text)
    logLock.release()

def getlog() -> list:
    print("获取日志")
    global logs
    logLock.acquire()
    ret = logs
    logs = []

    logLock.release()
    return ret

