# -*- coding: utf-8 -*-
import os.path
import pickle

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog, QLineEdit



huashu = []
if os.path.exists("user_data/huashu.pickle"):
    with open("user_data/huashu.pickle", "rb") as f:
        huashu = pickle.load(f)

print(huashu)

def addHuashu(name:str, content:str):
    huashu.append({"name":name, "content":content})
    with open("user_data/huashu.pickle", "wb") as f:
        pickle.dump(huashu,f)


class AddHuashu(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1000, 800)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(40, 40, 150, 31))
        self.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.textEdit = QtWidgets.QLineEdit(Form)
        self.textEdit.setGeometry(QtCore.QRect(200, 30, 700, 31))
        self.textEdit.setObjectName("textEdit")
        self.label0 = QtWidgets.QLabel(Form)
        self.label0.setGeometry(QtCore.QRect(40, 90, 150, 31))
        self.label0.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label0.setObjectName("label")
        self.textEdit0 = QtWidgets.QTextEdit(Form)
        self.textEdit0.setGeometry(QtCore.QRect(200, 80, 700, 500))
        self.textEdit0.setObjectName("textEdit")


        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(110, 700, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(lambda: self.addAdmin(Form))
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(190, 700, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(lambda: Form.hide())

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "新增角色"))
        self.label.setText(_translate("Form", "话术模版名称："))
        self.label0.setText(_translate("Form", "话术模版内容："))
        self.pushButton.setText(_translate("Form", "提交"))
        self.pushButton_2.setText(_translate("Form", "取消"))

    def addAdmin(self, Form):
        name = self.textEdit.text()
        content = self.textEdit0.toPlainText()
        print("添加话术", name, content)

        addHuashu(name, content)
        Form.hide()

if __name__ == "__main__":
    import sys

    App = QApplication(sys.argv)  # 创建QApplication对象，作为GUI主程序入口
    aw = AddHuashu()  # 创建主窗体对象，实例化Ui_MainWindow
    w = QMainWindow()  # 实例化QMainWindow类
    aw.setupUi(w)  # 主窗体对象调用setupUi方法，对QMainWindow对象进行设置
    w.show()  # 显示主窗体
    w.setWindowTitle('新增话术')
    sys.exit(App.exec_())  # 循环中等待退出程序
