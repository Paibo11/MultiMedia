import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QPainter, QPen, QFont, QColor
from PySide6.QtCore import Qt


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 700)  # Увеличиваем минимальную высоту окна
        self.functions = []  # Список для хранения функций и их цветов
        self.x_min = -4
        self.x_max = 4

        # Создаем элементы управления
        self.layout = QVBoxLayout()

        # Поля для ввода диапазона X
        self.range_layout = QHBoxLayout()
        self.x_min_input = QLineEdit(self)
        self.x_min_input.setPlaceholderText("Минимум X")
        self.x_min_input.setText(str(self.x_min))
        self.x_max_input = QLineEdit(self)
        self.x_max_input.setPlaceholderText("Максимум X")
        self.x_max_input.setText(str(self.x_max))
        self.range_layout.addWidget(self.x_min_input)
        self.range_layout.addWidget(self.x_max_input)

        # Поле для ввода функции
        self.function_input = QLineEdit(self)
        self.function_input.setPlaceholderText("Введите функцию")

        # Кнопка для добавления функции
        self.add_button = QPushButton("Добавить функцию", self)
        self.add_button.clicked.connect(self.add_function)

        # Кнопка для очистки графика
        self.clear_button = QPushButton("Очистить график", self)
        self.clear_button.clicked.connect(self.clear_graph)

        # Метка для отображения ошибок
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red;")

        # Добавляем элементы в layout
        self.layout.addLayout(self.range_layout)
        self.layout.addWidget(self.function_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.clear_button)
        self.layout.addWidget(self.error_label)
        self.setLayout(self.layout)

    def add_function(self):
        """Добавляет функцию в список и обновляет график."""
        func_text = self.function_input.text()
        try:
            self.x_min = float(self.x_min_input.text())
            self.x_max = float(self.x_max_input.text())

            # Проверяем корректность диапазона
            if self.x_min >= self.x_max:
                raise ValueError("Минимум X должен быть меньше максимума X")

            func = lambda x, f=func_text: eval(f, {'np': np, 'x': x})

            # Проверяем функцию на корректность
            test_x = np.linspace(self.x_min, self.x_max, 100)
            func(test_x)

            # Добавляем функцию и случайный цвет в список
            color = QColor(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
            self.functions.append((func, color))
            self.error_label.setText("")
            self.update()  # Обновляем график
        except Exception as e:
            self.error_label.setText(f"Ошибка: {str(e)}")

    def clear_graph(self):
        """Очищает график и обновляет отображение."""
        self.functions = []  # Очищаем список функций
        self.update()  # Обновляем график

    def paintEvent(self, event):
        painter = QPainter(self)
        width, height = self.width(), self.height()

        top_margin = 150
        graph_height = height - top_margin - 50
        center_x = width // 2
        center_y = top_margin + graph_height // 2  # Центр графика с учетом отступа

        # Рисуем оси
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(50, center_y, width - 50, center_y)  # Ось X
        painter.drawLine(center_x, top_margin, center_x, height - 50)  # Ось Y

        # Рисуем сетку
        painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        step_x = (width - 100) / 10  # Шаг сетки по X
        step_y = graph_height / 10   # Шаг сетки по Y
        for i in range(1, 10):
            # Вертикальные линии
            x = 50 + i * step_x
            painter.drawLine(x, top_margin, x, height - 50)
            # Горизонтальные линии
            y = top_margin + i * step_y
            painter.drawLine(50, y, width - 50, y)

        # Подписи осей
        painter.setPen(Qt.black)
        font = QFont("Times New Roman", 10)
        painter.setFont(font)

        # Подписи по оси X
        for i in range(1, 10):
            x = 50 + i * step_x
            value = self.x_min + (self.x_max - self.x_min) * (i / 10)
            painter.drawText(x - 10, center_y + 20, f"{value:.1f}")

        # Подписи по оси Y
        for i in range(1, 10):
            y = top_margin + i * step_y
            value = (1 - (i / 10)) * 2 - 1  # Нормализованные значения от -1 до 1
            painter.drawText(center_x + 10, y + 5, f"{value:.1f}")

        # Рисуем все функции
        for func, color in self.functions:
            painter.setPen(QPen(color, 2))
            x_values = np.linspace(self.x_min, self.x_max, 1000)
            y_values = func(x_values)

            # Масштабируем значения для отображения
            x_scaled = 50 + (x_values - self.x_min) / (self.x_max - self.x_min) * (width - 100)
            y_scaled = center_y - y_values * (graph_height / 2)

            # Рисуем линии
            for i in range(1, len(x_scaled)):
                painter.drawLine(x_scaled[i - 1], y_scaled[i - 1], x_scaled[i], y_scaled[i])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWidget()
    window.show()
    sys.exit(app.exec())
