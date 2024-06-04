# coding:utf-8
import gc
from login_api import *
import qtawesome
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIntValidator
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QHeaderView, QTableWidgetItem, QComboBox, \
    QStyleOptionButton, QStyle, QRadioButton, QButtonGroup, QVBoxLayout, QCheckBox

from PyQt5.QtCore import Qt, pyqtSignal, QRect, QTimer

from grade_statistics.src.AddHuashu import *
# from grade_statistics.src.login import *
from log import *

from auto_collect import *
# 表头字段，全局变量
header_field = ['全选']
# 用来装行表头所有复选框 全局变量
global all_header_combobox
global all_class, class_dict, class_dict2
global data_list  # 数据库数据列表
global activat_menu  # 当前激活的菜单按钮
activat_menu = None
from collect_creator import *
from batch import *
import random
import _thread
from login_TK import *
import sys
import grade_statistics.src.global_var as gl

class CheckBoxHeader(QHeaderView):
    """自定义表头类"""

    # 自定义 复选框全选信号
    select_all_clicked = pyqtSignal(bool)
    # 这4个变量控制列头复选框的样式，位置以及大小
    _x_offset = 21
    _y_offset = 10
    _width = 20
    _height = 20

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isOn = False

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()

        self._y_offset = int((rect.height() - self._width) / 2.)

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(rect.x() + self._x_offset, rect.y() + self._y_offset, self._width, self._height)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if 0 == index:
            x = self.sectionPosition(index)
            if x + self._x_offset < event.pos().x() < x + self._x_offset + self._width and self._y_offset < event.pos().y() < self._y_offset + self._height:
                if self.isOn:
                    self.isOn = False
                else:
                    self.isOn = True
                    # 当用户点击了行表头复选框，发射 自定义信号 select_all_clicked()
                self.select_all_clicked.emit(self.isOn)

                self.updateSection(0)
        super(CheckBoxHeader, self).mousePressEvent(event)

    # 自定义信号 select_all_clicked 的槽方法
    def change_state(self, isOn):
        # 如果行表头复选框为勾选状态
        if isOn:
            # 将所有的复选框都设为勾选状态
            for i in all_header_combobox:
                i.setCheckState(Qt.Checked)
        else:
            for i in all_header_combobox:
                i.setCheckState(Qt.Unchecked)


class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimeout)
        self.timer.start(1000)  # 每1000毫秒（1秒）触发一次

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.checkLogin)
        self.timer2.start(6000)  # 每1000毫秒（1秒）触发一次

    def onTimeout(self):
        # 获取当前时间并更新标签
        gc.collect()
        logs = getlog()
        if len(logs) > 0:
            text = self.logEdit.toPlainText() + "\r\n" + "\r\n".join(logs)
            self.logEdit.append(text)
            self.logEdit.moveCursor(self.logEdit.textCursor().End)

    def checkLogin(self):
        print(gl.username, gl.password)
        if not heart_beat(gl.username,gl.password):
            QMessageBox.information(self, "错误提示", "登录失效", QMessageBox.Yes | QMessageBox.No)
            sys.exit(0)
        print("登录保持")

    def submitData(self, id, flag):
        """
        提交数据
        :param id: 数据库id
        :param flag: 1. 学生 2.班级 3.角色
        :return:
        """
        return

    def collectDaren(self):
        collect_creator(gl.nation)

    def inviteDaren(self):
        if gl.current_user == "":
            QMessageBox.information(self, "错误提示", "没有登录tk账号", QMessageBox.Yes | QMessageBox.No)
            return
        input_min = 0
        if self.input_min.text().isdigit():
           input_min = int(self.input_min.text())
        _thread.start_new_thread(batch_invite,
                                 (gl.nation, gl.selected_category, self.input_name.text(), gl.current_user, input_min))

    def do_batch_msg(self):
        if gl.current_user == "":
            QMessageBox.information(self,"错误提示","没有登录tk账号",QMessageBox.Yes | QMessageBox.No)
            return
        if len(self.textEdit.toPlainText()) == 0:
            QMessageBox.information(self, "错误提示", "没有输入任何消息", QMessageBox.Yes | QMessageBox.No)
            return
        _thread.start_new_thread(batch_msg, (gl.nation, gl.selected_category, self.textEdit.toPlainText(), gl.current_user, 100))


    def stop_batch_msg(self):
        end_batch()

    def stop_invite(self):
        end_batch()

    def login(self):
        self.infoLabel.setText("登录中请稍等，浏览器启动可能需要点时间，请耐心等待")
        QApplication.processEvents()
        if loginTK():
            shop_name = get_home_info()
            gl.current_user = shop_name
            self.tiktok_management()
            self.left_label_1.setText(gl.current_user + ',' + gl.nation)
        else:
            gl.current_user = ""
            QMessageBox.critical(self, '失败', "登录TikTok卖家后台失败！")

    def autoCollect(self):
        if gl.collecting:
            return
        gl.collecting = True
        _thread.start_new_thread(auto, (gl.nation, 3, 100000))

    def stopCollect(self):
        gl.collecting = False

    def batchDelete(self, flag):
        """
        批量删除
        :return:
        """
        global all_header_combobox
        ids = [-1]
        for i in range(len(all_header_combobox)):
            # print(i)
            try:
                if all_header_combobox[i].checkState() == 2:
                    if flag == gl.FLAG_DAREN_COLLECT:
                        ids.append(self.tableWidget.item(i, 2).text())
                    else:
                        ids.append(self.tableWidget.item(i, 1).text())
            except Exception as e:
                print(e)
        if len(ids) == 1:
            QMessageBox.information(self, '失败', "未选择数据！")
            return
        self.deleteRow(ids, flag)

    def deleteRow(self, ids, flag):
        """
        删除数据
        :param ids: 数据库id列表
        :param flag: 1.学生 2.班级 3.角色 4.班级
        :return:
        """
        return

    def viewTable(self, id, flag):
        """
        查看详情
        :param id: 数据库id
        :param flag: xx管理
        :return:
        """
        return

    def buttonForRow(self, id, flag, info=''):
        """
        添加编辑、删除按钮
        :param id: 数据库中数据id
        :param flag: xx管理
        :param info: 其他附加信息
        :return:
        """
        widget = QWidget()
        # 编辑

        # 删除
        return widget

    def getDataList(self, flag, i=None):

        """
        获取并更新数据列表
        :param flag: xx管理
        :param i: 班级index
        :return:
        """
        global all_class, data_list
        data_list = ()
        if i == None:
            i = 0
        if flag == gl.FLAG_DAREN_POOL:
            data_list = nation_map[gl.nation].values()
        elif flag == gl.FLAG_MSG:
            data_list = huashu
        self.addTableRow(flag, data_list)

    def addTableRow(self, flag, dataList):
        global all_header_combobox, class_dict
        all_header_combobox = []

        self.tableWidget.setRowCount(0)
        if len(dataList) == 0:
            self.tableWidget.setRowCount(1)
            item = QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setText("无数据")
            self.tableWidget.setItem(0, 0, item)
            return

        self.tableWidget.setRowCount(len(dataList))
        i = 0
        for data in dataList:
            if flag == gl.FLAG_DAREN_POOL:
                item = QTableWidgetItem(str(data['name']))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(i, 1, item)
                item = QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setText(data['category'])
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(i, 2, item)
                item = QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                # print(student[2])
                item.setText(str(data['fans']))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(i, 3, item)


                if gl.current_user != "":
                    item = QTableWidgetItem()
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    item.setText(get_invite_time(data['name'], gl.nation, gl.current_user))
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.tableWidget.setItem(i, 4, item)

                    item = QTableWidgetItem()
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    item.setText(get_send_msg_time(data['name'], gl.nation, gl.current_user))
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.tableWidget.setItem(i, 5, item)
            i += 1

    def getClassList(self, name=''):
        return []
        # return sql_execute(getClassList(gl.gl_user[4], name))

    def setLeftMenu(self, button):
        """
        设置左侧菜单样式
        :param button: 当前选中按钮
        :return:
        """
        global activat_menu
        if activat_menu != None:
            activat_menu.setStyleSheet('''
                        width:20px;
                        font-size:15px;
                        ''')
        activat_menu = button
        button.setStyleSheet('''
                    width:20px;
                    font-size:15px;
                    border-left:4px solid #00bcd4;
                    font-weight:700;
                    ''')


    def logOut(self, tips=False):
        """
        退出登录
        :param tips: 是否显示提示框
        :return:
        """
        if tips:
            reply = QMessageBox.question(self, '退出登录', '确定要退出登录吗？', QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        gl.gl_user = ()
        self.aw = gl.LOGIN_WINDOW  # 创建主窗体对象，实例化Ui_MainWindow
        self.w = QMainWindow()  # 实例化QMainWindow类
        self.aw.setupUi(self.w)  # 主窗体对象调用setupUi方法，对QMainWindow对象进行设置
        self.w.show()  # 显示主窗体
        self.hide()

    def editUsername(self):
        """
        修改用户名
        :return:
        """
        reply = QMessageBox.question(self, '修改用户名', '修改用户名后，需要重新登录。是否继续？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            username = self.input_name.text()
            QMessageBox.about(self, '成功', '用户名修改成功！请重新登录。')
            self.logOut(False)
            # self.aw = Ui_MainWindow()  # 创建主窗体对象，实例化Ui_MainWindow
            # self.w = QMainWindow()  # 实例化QMainWindow类
            # self.aw.setupUi(self.w)  # 主窗体对象调用setupUi方法，对QMainWindow对象进行设置
            # self.w.show()  # 显示主窗体

    def modifyPassw(self):
        """
        修改密码
        :return:
        """
        return

    def addHuashu(self):
        """
        新增角色
        :return:
        """
        self.aw = AddHuashu()  # 创建主窗体对象，实例化Ui_MainWindow
        self.w = QMainWindow()  # 实例化QMainWindow类
        self.aw.setupUi(self.w)  # 主窗体对象调用setupUi方法，对QMainWindow对象进行设置
        self.w.show()  # 显示主窗体

    def tiktok_management(self):
        if self.right_widget:
            self.main_layout.removeWidget(self.right_widget)  # 移除已有右侧组件
        self.setWindowTitle('达人管家-tiktok店铺账号')
        self.setLeftMenu(self.left_button_2)
        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.right_layout = self.verticalLayout
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.right_widget, 0, 2, 12, 10)  # 右侧部件在第0行第3列，占8行9列

        self.widget = QtWidgets.QWidget()
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.horizontalLayout.addItem(spacerItem)

        # 收集达人
        self.pushButton_del = QtWidgets.QPushButton(self.widget)
        self.pushButton_del.setObjectName("pushButton_del")
        self.horizontalLayout.addWidget(self.pushButton_del)
        self.pushButton_del.clicked.connect(lambda: self.login())
        self.pushButton_del.setStyleSheet(''' text-align : center;
                                              background-color : #f44336;
                                              height : 30px;
                                              width: 80px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')

        self.widget2 = QtWidgets.QWidget()
        self.horizontalLayout2 = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout2.setObjectName("horizontalLayout")

        self.label_nation = QtWidgets.QLabel()
        self.label_nation.setText("站点选择")
        self.radioPH = QRadioButton('PH')
        self.radioMY = QRadioButton('MY')
        self.radioVN = QRadioButton('VN')
        self.radioSG = QRadioButton('SG')
        self.radioTH = QRadioButton('TH')

        if gl.nation == "PH":
            self.radioPH.toggle()
        elif gl.nation == "MY":
            self.radioMY.toggle()
        elif gl.nation == "VN":
            self.radioVN.toggle()
        elif gl.nation == "SG":
            self.radioSG.toggle()
        else:
            self.radioTH.toggle()


        self.radioPH.toggled.connect(lambda: self.selectNation())
        self.radioMY.toggled.connect(lambda: self.selectNation())
        self.radioVN.toggled.connect(lambda: self.selectNation())
        self.radioSG.toggled.connect(lambda: self.selectNation())
        self.radioTH.toggled.connect(lambda: self.selectNation())

        self.horizontalLayout2.addWidget(self.label_nation)
        self.horizontalLayout2.addWidget(self.radioPH)
        self.horizontalLayout2.addWidget(self.radioMY)
        self.horizontalLayout2.addWidget(self.radioVN)
        self.horizontalLayout2.addWidget(self.radioSG)
        self.horizontalLayout2.addWidget(self.radioTH)




        self.widget3 = QtWidgets.QWidget()
        self.horizontalLayout3 = QtWidgets.QHBoxLayout(self.widget3)
        self.horizontalLayout3.setObjectName("horizontalLayout")

        self.infoLabel = QtWidgets.QLabel()
        self.infoLabel.setGeometry(QtCore.QRect())

        if gl.current_user == "":
            self.infoLabel.setText("当前没有登录tiktok账号")
        else:
            self.infoLabel.setText("当前账号:"+gl.current_user)
        self.horizontalLayout3.addWidget(self.infoLabel)

        self.verticalLayout.addWidget(self.widget)
        self.verticalLayout.addWidget(self.widget2)
        self.verticalLayout.addWidget(self.widget3)
        self.verticalLayout.addItem(spacerItem)

        _translate = QtCore.QCoreApplication.translate
        self.pushButton_del.setText(_translate("Form", "tiktok账号登录"))

        return self.right_widget

    def selectNation(self):
        sender = self.sender()
        if sender.isChecked():
            addlog("选中" + sender.text())
            gl.nation = sender.text()
            if gl.current_user == "":
                self.left_label_1.setText('未登录,' + gl.nation)
            else:
                self.left_label_1.setText(gl.current_user + ',' + gl.nation)
        if gl.flag == gl.FLAG_DAREN_POOL:
            addlog("切换站点" + str(gl.flag) + gl.nation)
            self.getDataList(gl.FLAG_DAREN_POOL)

    def selectCatogary(self):
        sender = self.sender()
        if sender.text() not in gl.selected_category:
            gl.selected_category.append(sender.text())
        else:
            gl.selected_category.remove(sender.text())
        print(gl.selected_category)


    # 学生管理
    def daren_management(self):
        global all_class, class_dict, class_dict2
        class_dict = {}
        class_dict2 = {}
        if self.right_widget:
            self.main_layout.removeWidget(self.right_widget)  # 移除已有右侧组件
        self.setWindowTitle('达人管家-达人库')
        self.setLeftMenu(self.left_button_1)
        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.right_layout = self.verticalLayout
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.right_widget, 0, 2, 8, 10)  # 右侧部件在第0行第3列，占8行9列


        self.widget2 = QtWidgets.QWidget()
        self.horizontalLayout2 = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout2.setObjectName("horizontalLayout")

        self.label_nation = QtWidgets.QLabel()
        self.label_nation.setText("站点选择")
        self.radioPH = QRadioButton('PH')
        self.radioMY = QRadioButton('MY')
        self.radioVN = QRadioButton('VN')
        self.radioSG = QRadioButton('SG')
        self.radioTH = QRadioButton('TH')

        if gl.nation == "PH":
            self.radioPH.toggle()
        elif gl.nation == "MY":
            self.radioMY.toggle()
        elif gl.nation == "VN":
            self.radioVN.toggle()
        elif gl.nation == "SG":
            self.radioSG.toggle()
        else:
            self.radioTH.toggle()

        self.radioPH.toggled.connect(lambda: self.selectNation())
        self.radioMY.toggled.connect(lambda: self.selectNation())
        self.radioVN.toggled.connect(lambda: self.selectNation())
        self.radioSG.toggled.connect(lambda: self.selectNation())
        self.radioTH.toggled.connect(lambda: self.selectNation())

        self.horizontalLayout2.addWidget(self.label_nation)
        self.horizontalLayout2.addWidget(self.radioPH)
        self.horizontalLayout2.addWidget(self.radioMY)
        self.horizontalLayout2.addWidget(self.radioVN)
        self.horizontalLayout2.addWidget(self.radioSG)
        self.horizontalLayout2.addWidget(self.radioTH)

        self.verticalLayout.addWidget(self.widget2)

        self.tableWidget = QtWidgets.QTableWidget()
        # self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(7)

        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        self.verticalLayout.addWidget(self.tableWidget)

        _translate = QtCore.QCoreApplication.translate

        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "达人"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Form", "类别"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Form", "粉丝数"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("Form", "上次邀请时间"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("Form", "上次发消息时间"))

        header = CheckBoxHeader()  # 实例化自定义表头
        self.tableWidget.setHorizontalHeader(header)  # 设置表头
        header.select_all_clicked.connect(header.change_state)  # 行表头复选框单击信号与槽
        self.tableWidget.setColumnWidth(0, 50)
        # self.tableWidget.setRowHeight(40)
        self.tableWidget.setColumnWidth(1, 70)
        self.tableWidget.setColumnWidth(5, 197)

        self.tableWidget.verticalHeader().setDefaultSectionSize(32)

        # self.getDataList(gl.FLAG_DAREN_POOL)

        return self.right_widget

    # 成绩管理
    def daren_collect_management(self):
        global all_class, class_dict, class_dict2
        class_dict = {}
        class_dict2 = {}
        if self.right_widget:
            self.main_layout.removeWidget(self.right_widget)  # 移除已有右侧组件
        self.setWindowTitle('达人管家-达人收集')
        self.setLeftMenu(self.left_button_2)
        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.right_layout = self.verticalLayout
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.right_widget, 0, 2, 12, 10)  # 右侧部件在第0行第3列，占8行9列

        self.widget = QtWidgets.QWidget()
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self.horizontalLayout.addItem(spacerItem)

        # 收集达人
        self.pushButton_del = QtWidgets.QPushButton(self.widget)
        self.pushButton_del.setObjectName("pushButton_del")
        self.horizontalLayout.addWidget(self.pushButton_del)
        self.pushButton_del.clicked.connect(lambda: self.collectDaren())
        self.pushButton_del.setStyleSheet(''' text-align : center;
                                              background-color : #f44336;
                                              height : 30px;
                                              width: 80px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')

        # 自动收集达人
        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        self.pushButton_3.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_3.clicked.connect(lambda: self.autoCollect())
        self.pushButton_3.setStyleSheet(''' text-align : center;
                                              background-color : #009688;
                                              height : 30px;
                                              width: 50px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')

        # 停止收集达人
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton.clicked.connect(lambda: self.stopCollect())
        self.pushButton.setStyleSheet(''' text-align : center;
                                              background-color : #ff9800;
                                              height : 30px;
                                              width: 50px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')

        self.verticalLayout.addWidget(self.widget)
        self.tableWidget = QtWidgets.QWidget()

        self.verticalLayout.addWidget(self.tableWidget)

        _translate = QtCore.QCoreApplication.translate
        self.pushButton_del.setText(_translate("Form", "开始收集"))
        self.pushButton_3.setText(_translate("Form", "自动收集"))
        self.pushButton.setText(_translate("Form", "停止收集"))

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        return self.right_widget

    def daren_invite_management(self):
        gl.selected_category = []
        global all_class, class_dict, class_dict2
        class_dict = {}
        class_dict2 = {}
        if self.right_widget:
            self.main_layout.removeWidget(self.right_widget)  # 移除已有右侧组件
        self.setWindowTitle('达人管家-达人邀请')
        self.setLeftMenu(self.left_button_3)
        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.right_layout = self.verticalLayout
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.right_widget, 0, 2, 12, 10)  # 右侧部件在第0行第3列，占8行9列

        self.widget = QtWidgets.QWidget()
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")


        # 查询按钮
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_2.clicked.connect(lambda: self.inviteDaren())
        self.pushButton_2.setStyleSheet(''' text-align : center;
                                              background-color : #03a9f4;
                                              height : 30px;
                                              width: 50px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')


        # 批量删除按钮
        self.pushButton_del = QtWidgets.QPushButton(self.widget)
        self.pushButton_del.setObjectName("pushButton_del")
        self.horizontalLayout.addWidget(self.pushButton_del)
        self.pushButton_del.clicked.connect(lambda: self.stop_invite())
        self.pushButton_del.setStyleSheet(''' text-align : center;
                                              background-color : #f44336;
                                              height : 30px;
                                              width: 80px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')

        self.widget2 = QtWidgets.QWidget()
        self.horizontalLayout2 = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout2.setObjectName("horizontalLayout")

        label = QtWidgets.QLabel(self.widget2)
        label.setText("选择类目")
        self.horizontalLayout2.addWidget(label)
        items = ["美妆", "电子", "服饰", "食品", "家居生活", "母婴", "个护和健康"]
        for item in items:
            checkbox = QCheckBox(item, self.widget2)
            self.horizontalLayout2.addWidget(checkbox)
            checkbox.stateChanged.connect(lambda: self.selectCatogary())

        self.widget3 = QtWidgets.QWidget()
        self.horizontalLayout3 = QtWidgets.QHBoxLayout(self.widget3)
        self.horizontalLayout3.setObjectName("horizontalLayout")


        self.label_2 = QtWidgets.QLabel(self.widget3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout3.addWidget(self.label_2)

        self.input_name = QtWidgets.QLineEdit(self.widget3)
        self.input_name.setObjectName("input_name")
        self.horizontalLayout3.addWidget(self.input_name)
        self.input_name.setStyleSheet(''' height : 30px;
                                                      border-style: outset;
                                                      padding-left: 5px;
                                                      border: 1px solid #ccc;
                                                      border-radius: 5px;
                                                      font : 12px  ''')

        self.label_3 = QtWidgets.QLabel(self.widget3)
        self.label_3.setObjectName("label_3")
        self.label_3.setText("最少粉丝数")
        self.horizontalLayout3.addWidget(self.label_3)

        self.input_min = QtWidgets.QLineEdit(self.widget3)
        self.input_min.setObjectName("input_name")
        self.input_min.setText("100")
        self.input_min.setValidator(QIntValidator())
        self.horizontalLayout3.addWidget(self.input_min)

        self.verticalLayout.addWidget(self.widget)
        self.verticalLayout.addWidget(self.widget2)
        self.verticalLayout.addWidget(self.widget3)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("Form", "模版id"))
        self.pushButton_2.setText(_translate("Form", "开始邀请"))
        self.pushButton_del.setText(_translate("Form", "停止邀请"))

        return self.right_widget

    # 角色管理
    def msg_management(self):
        if self.right_widget:
            self.main_layout.removeWidget(self.right_widget)  # 移除已有右侧组件
        self.setWindowTitle('达人私信-达人管家')
        self.setLeftMenu(self.left_button_4)
        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.right_layout = self.verticalLayout
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.right_widget, 0, 2, 8, 10)  # 右侧部件在第0行第3列，占8行9列

        self.widget = QtWidgets.QWidget()
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        # 新增按钮
        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        self.pushButton_3.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_3.clicked.connect(lambda: self.addHuashu())
        self.pushButton_3.setStyleSheet(''' text-align : center;
                                                              background-color : #009688;
                                                              height : 30px;
                                                              width: 80px;
                                                              border-style: outset;
                                                              border-radius: 5px;
                                                              color: #fff;
                                                              font : 12px  ''')
        # 查询按钮
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_2.clicked.connect(lambda: self.do_batch_msg())
        self.pushButton_2.setStyleSheet(''' text-align : center;
                                              background-color : #03a9f4;
                                              height : 30px;
                                              width: 50px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')


        # 批量删除按钮
        self.pushButton_del = QtWidgets.QPushButton(self.widget)
        self.pushButton_del.setObjectName("pushButton_del")
        self.horizontalLayout.addWidget(self.pushButton_del)
        self.pushButton_del.clicked.connect(lambda: self.stop_batch_msg())
        self.pushButton_del.setStyleSheet(''' text-align : center;
                                              background-color : #f44336;
                                              height : 30px;
                                              width: 100px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')

        self.widget2 = QtWidgets.QWidget()
        self.horizontalLayout2 = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout2.setObjectName("horizontalLayout")

        label = QtWidgets.QLabel(self.widget2)
        label.setText("选择类目")
        self.horizontalLayout2.addWidget(label)
        items = ["美妆", "电子", "服饰", "食品", "家居生活", "母婴", "个护和健康"]
        for item in items:
            checkbox = QCheckBox(item, self.widget2)
            self.horizontalLayout2.addWidget(checkbox)
            checkbox.stateChanged.connect(lambda: self.selectCatogary())

        self.verticalLayout.addWidget(self.widget)
        self.verticalLayout.addWidget(self.widget2)

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setGeometry(QtCore.QRect(0, 0, 100, 300))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setPlaceholderText("请输入私信内容")

        self.widget3 = QtWidgets.QWidget()
        self.horizontalLayout3 = QtWidgets.QHBoxLayout(self.widget3)
        self.horizontalLayout3.setObjectName("horizontalLayout")

        self.label_3 = QtWidgets.QLabel(self.widget3)
        self.label_3.setObjectName("label_3")
        self.label_3.setText("最少粉丝数")
        self.horizontalLayout3.addWidget(self.label_3)

        self.input_min = QtWidgets.QLineEdit(self.widget3)
        self.input_min.setObjectName("input_name")
        self.input_min.setText("100")
        self.input_min.setValidator(QIntValidator())
        self.horizontalLayout3.addWidget(self.input_min)

        self.verticalLayout.addWidget(self.widget3)
        self.verticalLayout.addWidget(self.textEdit)


        # self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        _translate = QtCore.QCoreApplication.translate
        self.pushButton_3.setText(_translate("Form", "新增话术"))
        self.pushButton_2.setText(_translate("Form", "达人私信"))
        self.pushButton_del.setText(_translate("Form", "停止私信"))

        return self.right_widget

    # 修改资料
    def change_info(self):
        if self.right_widget:
            self.main_layout.removeWidget(self.right_widget)  # 移除已有右侧组件
        self.setWindowTitle('修改资料-达人管家')
        self.setLeftMenu(self.left_button_8)
        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.right_widget.setStyleSheet(''' background-image : url('bg.png');
                                            background-position:center;
                                            background-repeat:no-repeat;''')

        self.right_layout = self.verticalLayout
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.right_widget, 0, 2, 12, 10)  # 右侧部件在第0行第3列，占8行9列

        self.widget = QtWidgets.QWidget()
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.label_2)
        # 姓名输入框
        self.input_name = QtWidgets.QLineEdit(self.widget)
        self.input_name.setObjectName("input_name")
        self.input_name.setText(gl.gl_user[1])
        self.horizontalLayout.addWidget(self.input_name)
        self.input_name.setStyleSheet(''' height : 30px;
                                              border-style: outset;
                                              padding-left: 5px;
                                              border: 1px solid #ccc;
                                              border-radius: 5px;
                                              font : 12px  ''')

        self.widget2 = QtWidgets.QWidget()
        self.horizontalLayout2 = QtWidgets.QHBoxLayout(self.widget2)

        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout2.addItem(spacerItem2)
        self.label_pass0 = QtWidgets.QLabel(self.widget2)
        self.label_pass0.setText('  原密码')
        self.horizontalLayout2.addWidget(self.label_pass0)
        # 原密码输入框
        self.input_pass0 = QtWidgets.QLineEdit(self.widget2)
        self.input_pass0.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_pass0.setPlaceholderText('请输入原密码')
        self.horizontalLayout2.addWidget(self.input_pass0)
        self.input_pass0.setStyleSheet(''' height : 30px;
                                              border-style: outset;
                                              padding-left: 5px;
                                              border: 1px solid #ccc;
                                              border-radius: 5px;
                                              font : 12px  ''')

        self.widget3 = QtWidgets.QWidget()
        self.horizontalLayout3 = QtWidgets.QHBoxLayout(self.widget3)

        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout3.addItem(spacerItem3)
        self.label_pass1 = QtWidgets.QLabel(self.widget3)
        self.label_pass1.setText('  新密码')
        # 新密码输入框
        self.input_pass1 = QtWidgets.QLineEdit(self.widget3)
        self.input_pass1.setObjectName("input_pass1")
        self.input_pass1.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_pass1.setPlaceholderText('请输入新密码')
        self.horizontalLayout3.addWidget(self.label_pass1)
        self.horizontalLayout3.addWidget(self.input_pass1)
        self.input_pass1.setStyleSheet(''' height : 30px;
                                              border-style: outset;
                                              padding-left: 5px;
                                              border: 1px solid #ccc;
                                              border-radius: 5px;
                                              font : 12px  ''')

        self.widget4 = QtWidgets.QWidget()
        self.horizontalLayout4 = QtWidgets.QHBoxLayout(self.widget4)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout4.addItem(spacerItem4)
        self.label_pass2 = QtWidgets.QLabel(self.widget4)
        self.label_pass2.setText('重复密码')
        # 重复密码输入框
        self.input_pass2 = QtWidgets.QLineEdit(self.widget4)
        self.input_pass2.setObjectName("input_pass2")
        self.input_pass2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_pass2.setPlaceholderText('请重复新密码')
        self.horizontalLayout4.addWidget(self.label_pass2)
        self.horizontalLayout4.addWidget(self.input_pass2)
        self.input_pass2.setStyleSheet(''' height : 30px;
                                              border-style: outset;
                                              padding-left: 5px;
                                              border: 1px solid #ccc;
                                              border-radius: 5px;
                                              font : 12px  ''')
        self.widget5 = QtWidgets.QWidget()
        self.horizontalLayout5 = QtWidgets.QHBoxLayout(self.widget5)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout5.addItem(spacerItem5)
        # 提交按钮
        self.pushButton_3 = QtWidgets.QPushButton(self.widget5)
        self.pushButton_3.setObjectName("pushButton")
        self.horizontalLayout5.addWidget(self.pushButton_3)
        self.pushButton_3.clicked.connect(lambda: self.modifyPassw())
        self.pushButton_3.setStyleSheet(''' text-align : center;
                                                                      background-color : #009688;
                                                                      height : 30px;
                                                                      width: 80px;
                                                                      border-style: outset;
                                                                      border-radius: 5px;
                                                                      color: #fff;
                                                                      font : 12px  ''')
        # 查询按钮
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_2.clicked.connect(lambda: self.editUsername())
        self.pushButton_2.setStyleSheet(''' text-align : center;
                                              background-color : #03a9f4;
                                              height : 30px;
                                              width: 50px;
                                              border-style: outset;
                                              border-radius: 5px;
                                              color: #fff;
                                              font : 12px  ''')

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout2.addItem(spacerItem)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout3.addItem(spacerItem)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout4.addItem(spacerItem)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout5.addItem(spacerItem)

        spacerItem = QtWidgets.QSpacerItem(40, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.widget)
        spacerItem = QtWidgets.QSpacerItem(40, 300, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.widget2)
        self.verticalLayout.addWidget(self.widget3)
        self.verticalLayout.addWidget(self.widget4)
        self.verticalLayout.addWidget(self.widget5)

        spacerItem = QtWidgets.QSpacerItem(40, 200, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)

        _translate = QtCore.QCoreApplication.translate
        self.pushButton_3.setText(_translate("Form", "修改密码"))
        self.label_2.setText(_translate("Form", "用户名"))
        self.pushButton_2.setText(_translate("Form", "修改"))

        return self.right_widget

    def init_ui(self):
        print(gl.gl_user)
        self.setFixedSize(960, 800)
        self.main_widget = QtWidgets.QWidget()  # 创建窗口主部件
        self.main_layout = QtWidgets.QGridLayout()  # 创建主部件的网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        self.left_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.left_widget.setObjectName('left_widget')
        self.left_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.left_widget.setLayout(self.left_layout)  # 设置左侧部件布局为网格
        self.main_layout.addWidget(self.left_widget, 0, 0, 12, 2)  # 左侧部件在第0行第0列，占8行3列
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

        if gl.current_user == "":
            self.left_label_1 = QtWidgets.QPushButton('未登录,' + gl.nation)
        else:
            self.left_label_1 = QtWidgets.QPushButton(gl.current_user + ',' + gl.nation)


        self.left_label_1.setObjectName('left_label')
        self.left_label_3 = QtWidgets.QPushButton("个人中心")
        self.left_label_3.setObjectName('left_label')

        self.left_button_0 = QtWidgets.QPushButton(qtawesome.icon('fa.users', color='white'), "tiktok账号")
        self.left_button_0.setObjectName('left_button')
        self.left_button_0.clicked.connect(lambda: self.setRightWidget(gl.FLAG_TK_ACCOUNT))

        self.left_button_1 = QtWidgets.QPushButton(qtawesome.icon('fa.users', color='white'), "达人库")
        self.left_button_1.setObjectName('left_button')
        self.left_button_1.clicked.connect(lambda: self.setRightWidget(gl.FLAG_DAREN_POOL))
        self.left_button_2 = QtWidgets.QPushButton(qtawesome.icon('fa.id-card', color='white'), "达人收集")
        self.left_button_2.setObjectName('left_button')
        self.left_button_2.clicked.connect(lambda: self.setRightWidget(gl.FLAG_DAREN_COLLECT))
        self.left_button_3 = QtWidgets.QPushButton(qtawesome.icon('fa.institution', color='white'), "达人邀请")
        self.left_button_3.setObjectName('left_button')
        self.left_button_3.clicked.connect(lambda: self.setRightWidget(gl.FLAG_CLASS))
        self.left_button_4 = QtWidgets.QPushButton(qtawesome.icon('fa.user-secret', color='white'), "达人私信")
        self.left_button_4.setObjectName('left_button')
        self.left_button_4.clicked.connect(lambda: self.setRightWidget(gl.FLAG_MSG))

        self.left_button_5 = QtWidgets.QPushButton()
        # self.left_button_5.setObjectName('left_button')
        self.left_button_6 = QtWidgets.QPushButton()
        # self.left_button_6.setObjectName('left_button')
        self.left_button_7 = QtWidgets.QPushButton()
        # self.left_button_7.setObjectName('left_button')
        self.left_button_8 = QtWidgets.QPushButton(qtawesome.icon('fa.pencil-square-o', color='white'), "修改资料")
        self.left_button_8.setObjectName('left_button')
        self.left_button_8.clicked.connect(lambda: self.setRightWidget(gl.FLAG_INFO))
        self.left_button_9 = QtWidgets.QPushButton(qtawesome.icon('fa.sign-out', color='white'), "退出登录")
        self.left_button_9.setObjectName('left_button')
        self.left_button_9.clicked.connect(lambda: self.logOut(True))
        self.left_xxx = QtWidgets.QPushButton(" ")
        #
        # self.left_layout.addWidget(self.left_mini, 0, 0, 1, 1)
        # self.left_layout.addWidget(self.left_close, 0, 2, 1, 1)
        # self.left_layout.addWidget(self.left_visit, 0, 1, 1, 1)
        self.left_layout.addWidget(self.left_label_1, 1, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_0, 2, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_1, 3, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_2, 4, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_3, 5, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_4, 6, 0, 1, 3)
        self.left_layout.addWidget(self.left_label_3, 9, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_8, 10, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_9, 11, 0, 1, 3)
        # self.left_layout.addWidget(self.left_label_2, 5, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_5, 12, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_6, 13, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_7, 8, 0, 1, 3)

        self.left_widget.setStyleSheet('''
            QPushButton{border:none;color:white;}
            QPushButton#left_label{
                border:none;
                border-bottom:1px solid white;
                padding-bottom:2px;
                font-size:16px;
                font-weight:500;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
            QPushButton#left_button{
                width:20px;
                font-size:15px;
            }
            QPushButton#left_button:hover{font-weight:700;}
            QWidget#left_widget{
                background:#607d8b;
                border-top:1px solid white;
                border-bottom:1px solid white;
                border-left:1px solid white;
            }
        ''')
        self.right_widget = None
        self.setRightWidget()
        self.main_layout.setSpacing(0)

        self.bottom_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.bottom_widget.setObjectName('bottom_widget')
        self.bottom_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.bottom_widget.setLayout(self.bottom_layout)  # 设置左侧部件布局为网格
        self.logEdit = QtWidgets.QTextBrowser()
        self.bottom_layout.addWidget(self.logEdit)
        self.main_layout.addWidget(self.bottom_widget, 8, 2, 4, 10)  # 左侧部件在第0行第0列，占8行3列
        self.logEdit.setStyleSheet("background-color: #4c5a80; color: white;")  # 设置文本浏览器的背景色和文本颜色

    def setRightWidget(self, flag=gl.FLAG_DAREN_COLLECT):
        gl.flag = flag
        if flag == gl.FLAG_TK_ACCOUNT:
            self.right_widget = self.tiktok_management()
        elif flag == gl.FLAG_DAREN_POOL:
            self.right_widget = self.daren_management()
        elif flag == gl.FLAG_DAREN_COLLECT:
            self.right_widget = self.daren_collect_management()
        elif flag == gl.FLAG_CLASS:
            self.right_widget = self.daren_invite_management()
        elif flag == gl.FLAG_MSG:
            self.right_widget = self.msg_management()
        elif flag == gl.FLAG_INFO:
            self.right_widget = self.change_info()


def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
