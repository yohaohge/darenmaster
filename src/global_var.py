
"""
存放系统中需要多次使用的全局变量
在别的文件使用方法:
import global_var as gl
"""

# 当前登录用户信息
gl_user=(1, 'admin', '0', '0', '0')

# 管理模块标识
FLAG_TK_ACCOUNT = 0
FLAG_DAREN_POOL = 1 # 学生管理
FLAG_CLASS = 2 # 班级管理
FLAG_MSG = 3 # 私信管理
FLAG_DAREN_COLLECT = 4 # 成绩管理
FLAG_INFO = 5 # 修改资料
flag = FLAG_CLASS

nation = "PH"
selected_category = []
current_user = ""

collecting = False

# 登录窗口
LOGIN_WINDOW = None

# 软件账号用户
username = ""
password = ""
