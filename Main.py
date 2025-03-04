import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QPainter, QPen, QFont, QColor, QBrush
from PySide6.QtCore import Qt


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 700)
        self.graphs = []  # Список для хранения графиков и их данных
        self.x_min = -4
        self.x_max = 4
        self.y_scale = 1.5  # Коэффициент масштабирования по оси Y

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
        self.function_input.setPlaceholderText("Введите функцию, например np.sin(x)")

        # Кнопка для построения графика
        self.add_button = QPushButton("Построить график", self)
        self.add_button.clicked.connect(self.add_graph)

        # Кнопка для очистки графика
        self.clear_button = QPushButton("Очистить", self)
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

    def add_graph(self):
        """Добавляет график функции и цилиндры."""
        func_text = self.function_input.text()
        try:
            self.x_min = float(self.x_min_input.text())
            self.x_max = float(self.x_max_input.text())

            if self.x_min >= self.x_max:
                raise ValueError("Минимум X должен быть меньше максимума X")

            # Создаем функцию
            func = lambda x, f=func_text: eval(f, {'np': np, 'x': x})

            # Генерируем точки графика
            x_values = np.linspace(self.x_min, self.x_max, 500)  # Увеличиваем количество точек
            y_values = func(x_values)
            graph_points = list(zip(x_values, y_values))

            # Генерируем цилиндры (уменьшаем количество цилиндров)
            x_cyl = np.linspace(self.x_min, self.x_max, 20)  # Уменьшаем количество цилиндров до 30
            y_cyl = func(x_cyl)
            cylinders = list(zip(x_cyl, y_cyl))  # (x, y) для каждого цилиндра

            # Добавляем график и цилиндры в список с уникальным цветом
            color = self._get_soft_color()  # Используем мягкий цвет
            self.graphs.append({
                'points': graph_points,
                'cylinders': cylinders,
                'color': color
            })

            self.error_label.setText("")
            self.update()  # Обновляем график
        except Exception as e:
            self.error_label.setText(f"Ошибка: {str(e)}")

    def clear_graph(self):
        """Очищает график и цилиндры."""
        self.graphs = []
        self.update()

    def _get_soft_color(self):
        """Генерирует мягкий цвет."""
        # Генерация пастельных цветов
        r = np.random.randint(150, 230)  # Ограничиваем яркость
        g = np.random.randint(150, 230)
        b = np.random.randint(150, 230)
        return QColor(r, g, b)

    def paintEvent(self, event):
        """Отрисовывает график и цилиндры."""
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

        # Подписи по оси Y (статичные значения от -2 до 2 с шагом 0.5)
        y_values = np.arange(-2, 2.1, 0.5)  # Статичные значения от -2 до 2 с шагом 0.5
        for value in y_values:
            y_scaled = center_y - (value / 2) * (graph_height / 2)  # Масштабируем по y_max=2
            painter.drawText(center_x + 10, y_scaled + 5, f"{value:.1f}")

        # Рисуем графики функций
        y_max = 2  # Фиксированное максимальное значение по Y
        for idx, graph in enumerate(self.graphs):
            painter.setPen(QPen(graph['color'], 2))
            prev_x, prev_y = None, None
            for x, y in graph['points']:
                x_scaled = 50 + (x - self.x_min) / (self.x_max - self.x_min) * (width - 100)
                y_scaled = center_y - (y / y_max) * (graph_height / 2)  # Масштабируем по y_max
                if prev_x is not None:
                    painter.drawLine(prev_x, prev_y, x_scaled, y_scaled)
                prev_x, prev_y = x_scaled, y_scaled

        # Рисуем цилиндры (инвертированные)
        for idx, graph in enumerate(self.graphs):
            cylinder_color = graph['color'].darker(120)  # Слегка темнее для цилиндров
            outline_color = graph['color'].darker(150)  # Обводка чуть темнее

            # Смещение для каждой новой функции
            x_shift = idx * 15  # Смещение по X для каждой новой функции

            for cylinder in graph['cylinders']:
                x, y = cylinder

                # Масштабируем координаты
                x_scaled = 50 + (x - self.x_min) / (self.x_max - self.x_min) * (width - 100)
                y_scaled = center_y - (y / y_max) * (graph_height / 2)  # Масштабируем по y_max

                # Применяем смещение по X
                x_scaled += x_shift

                # Параметры цилиндра
                rect_width = 15  # Увеличиваем ширину цилиндра
                rect_height = abs(y_scaled - center_y)  # Высота цилиндра

                # Рисуем эллипс на оси X (с обводкой)
                painter.setPen(QPen(outline_color, 1))  # Обводка темным цветом
                painter.setBrush(QBrush(cylinder_color))  # Заливка цветом графика
                painter.drawEllipse(
                    int(x_scaled - rect_width / 2),
                    int(center_y - 5),  # Эллипс на оси X
                    int(rect_width),
                    10
                )

                # Рисуем верхнюю (или нижнюю) часть цилиндра
                base_x = int(x_scaled - rect_width / 2)
                base_y = int(y_scaled if y > 0 else center_y)
                painter.drawRect(
                    base_x,
                    base_y,
                    int(rect_width),
                    int(rect_height)
                )

                # Рисуем нижний эллипс (на оси X) с обводкой
                painter.drawEllipse(
                    base_x,
                    base_y - 5 if y > 0 else base_y + rect_height - 5,
                    int(rect_width),
                    10
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWidget()
    window.show()
    sys.exit(app.exec_())
