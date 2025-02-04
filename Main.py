import sys
import math
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtCore import Qt


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)  # Задаем размер окна

    def paintEvent(self, event):
        painter = QPainter(self)  # Создаем объект QPainter который позволяет рисовать на плоте

        painter.setPen(QPen(Qt.black, 2))
        width, height = self.width(), self.height()
        center_x, center_y = width // 2, height // 2
        painter.drawLine(50, center_y, width - 50, center_y)  # Ось X
        painter.drawLine(center_x, 50, center_x, height - 50)  # Ось Y

        painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        step = 50
        for y in range(center_y, height - 50, step):
            painter.drawLine(50, y, width - 50, y)
        for y in range(center_y, 0, -step):
            painter.drawLine(50, y, width - 50, y)
        for x in range(center_x, width - 50, step):
            painter.drawLine(x, 50, x, height - 50)
        for x in range(center_x, 0, -step):
            painter.drawLine(x, 50, x, height - 50)

        painter.setPen(Qt.black)
        font = QFont("Times New Roman", 15)
        painter.setFont(font)

        for x in range(center_x + step, width, step):
            painter.drawText(x, center_y + 20, f"{(x - center_x) // step}")
        for x in range(center_x - step, 0, -step):
            painter.drawText(x, center_y + 20, f"{(x - center_x) // step}")
        for y in range(center_y - step, 0, -step):
            painter.drawText(center_x + 5, y, f"{(center_y - y) // step}")
        for y in range(center_y + step, height, step):
            painter.drawText(center_x + 5, y, f"{(center_y - y) // step}")

        painter.drawText(width - 20, center_y + 20, "X")
        painter.drawText(center_x + 5, 15, "Y")
        painter.drawText(5, height - 5, "График: cos(x)")

        painter.setPen(QPen(Qt.blue, 2))
        step = 0.01
        scale_x, scale_y = 75, 50  # Масштабирование графика по X и Y
        prev_x, prev_y = None, None # Для того чтобы соединять точки линиями

        for i in range(-int(2 * math.pi / step), int(2 * math.pi / step)):
            x = i * step
            screen_x = center_x + x * scale_x  # Центрируем график
            screen_y = center_y - math.cos(x) * scale_y  # Инвертируем ось Y

            if 50 <= screen_x < width - 50 and 50 <= screen_y < height - 50:
                if prev_x is not None and prev_y is not None:
                    painter.drawLine(prev_x, prev_y, screen_x, screen_y)

            prev_x, prev_y = screen_x, screen_y


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWidget()  # создание плота
    window.show()  # Показываем плот
    sys.exit(app.exec())  # нужен чтобы показывать приложение
