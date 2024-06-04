import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QListWidget, QListWidgetItem, QWidget
from AddHuashu import *
import global_var as gl

class SlidingListExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("选择话术")
        self.setGeometry(100, 100, 500, 600)
        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        self.list_widget.setAlternatingRowColors(True)

        # 添加列表项
        for item in huashu:
            list_item = QListWidgetItem(self.list_widget)
            list_item.setText(item["name"] + "\r\n\r\n" + item["content"])

        # 设置主窗口的布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.list_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.list_widget.itemClicked.connect(self.handleItemClicked)

    def handleItemClicked(self, item):
        print(self.list_widget.currentRow())
        gl.currentHuashu = huashu[self.list_widget.currentRow()]["content"]
        print(gl.currentHuashu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    example = SlidingListExample()
    example.show()
    sys.exit(app.exec_())