import sqlite3
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QLabel
from PyQt5.QtGui import QPixmap


class ImgWidget(QLabel):
    def __init__(self, image, from_data=True, parent=None):
        super(ImgWidget, self).__init__(parent)
        if from_data:
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image)
        else:
            self.pixmap = QPixmap(image)
        self.setPixmap(self.pixmap)
        self.resize(self.sizeHint())


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design.ui', self)
        self.con = sqlite3.connect("library")
        self.get_btn.clicked.connect(lambda: self.update_result(False))
        self.update_result()

    def update_result(self, first_time=True):
        cur = self.con.cursor()
        # Получили результат запроса, который ввели в текстовое поле
        if first_time: 
            result = cur.execute(f"Select * from books").fetchall()
        elif self.comboBox.currentText() == 'Title':
            # print(self.comboBox.currentText(), self.lineEdit.text())
            result = cur.execute(f"Select * from books WHERE {self.comboBox.currentText()} like '{self.lineEdit.text()}%'").fetchall()
        elif self.comboBox.currentText() == 'Author':  
            result = cur.execute(f"""Select * from books WHERE genre=(SELECT 
                    id FROM authors WHERE Author like '{self.lineEdit.text()}%')""").fetchall()

        # print(result)
        # Заполнили размеры таблицы
        if result:
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setColumnCount(len(result[0]))
            self.titles = [description[0] for description in cur.description]
            self.titles[2] = 'Author'
            self.tableWidget.setHorizontalHeaderLabels(self.titles)
            # Заполнили таблицу полученными элементами
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    if j == 4:
                        res = cur.execute(f"""SELECT title FROM genres WHERE id = '{val}'""").fetchone()[0]
                        # print(res)
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(res)))
                    elif j == 2:
                        res = cur.execute(f"""SELECT Author FROM authors WHERE id = '{val}'""").fetchone()[0]
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(res)))
                    elif j == 5:
                        if val is None:
                            self.tableWidget.setCellWidget(i, j, ImgWidget(image='without.jpg', from_data=False))
                        else:
                            self.tableWidget.setCellWidget(i, j, ImgWidget(image=val))
                    else:
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()
        else:
            self.tableWidget.clear()


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())