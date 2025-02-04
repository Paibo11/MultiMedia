import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtCore import Qt

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)  # Задаем размер окна

    def paintEvent(self, event):
        painter = QPainter(self) # Создаем объект QPainter который позволяет рисовать на плоте

        painter.setPen(QPen(Qt.black, 2))
        width, height = self.width(), self.height()
        painter.drawLine(50, height - 50, width - 50, height - 50)  # Ось X
        painter.drawLine(50, height - 50, 50, 50)  # Ось Y

        painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        for y in range(50, height - 50, 25):
            painter.drawLine(50, y, width - 50, y)

        painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        for x in range(width - 50, 50, -25):
            painter.drawLine(x, 50, x, height - 50)

        painter.setPen(Qt.black)
        font = QFont("Times New Roman", 15)
        painter.setFont(font)

        for x in range(50, width - 50, 50):
            painter.drawText(x, height - 30, f"{(x - 50) // 50}")

        for y in range(50, height - 50, 50):
            painter.drawText(20, y + 5, f"{(height - 50 - y) // 50}")

        painter.drawText(width // 2, height - 10, "X")
        painter.drawText(1, height // 2, "Y")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWidget() # создание плота
    window.show() # Показываем плот
    sys.exit(app.exec()) # нужен чтобы показывать приложение
