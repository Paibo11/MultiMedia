from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt

import numpy as np


class Line:
    def __init__(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values
        self.min_x = np.min(self.x_values)
        self.max_x = np.max(self.x_values)
        self.min_y = np.mean([np.min(data) for data in self.y_values])
        self.max_y = np.mean([np.max(data) for data in self.y_values])

        # Ограничиваем значения min_y и max_y
        min_y_limit = -2  # Минимальное значение для min_y
        max_y_limit = 2  # Максимальное значение для max_y

        if self.min_y > min_y_limit:
            self.min_y = min_y_limit
        if self.max_y < max_y_limit:
            self.max_y = max_y_limit

    def map_to_widget(self, x, y, widget_width, widget_height):
        x_mapped = int((x - self.min_x) / (self.max_x - self.min_x) * widget_width)
        y_mapped = int(widget_height - (y - self.min_y) / (self.max_y - self.min_y) * widget_height)
        return x_mapped, y_mapped

    def draw_grid(self, painter, widget_width, widget_height, style):
        raise NotImplementedError("Subclasses should implement this method")

    def draw_plot(self, painter, widget_width, widget_height):
        raise NotImplementedError("Subclasses should implement this method")

class PlotLine(Line):
    def draw_grid(self, painter, widget_width, widget_height, style):
        pen = QPen(style.grid_color)
        pen.setWidth(style.grid_width)
        pen.setStyle(Qt.DashLine)  # Устанавливаем пунктирный стиль
        painter.setPen(pen)

        # Рисуем вертикальные линии сетки
        for x in range(int(self.min_x), int(np.ceil(self.max_x))):
            x_mapped = int((x - self.min_x) / (self.max_x - self.min_x) * widget_width)
            painter.drawLine(x_mapped, 0, x_mapped, widget_height)

        # Рисуем горизонтальные линии сетки
        y_zero_mapped = int(widget_height - (0 - self.min_y) / (self.max_y - self.min_y) * widget_height)
        max_value = np.max([abs(int(self.min_y)), int(self.max_y)])
        for y in range(1, max_value + 1):
            y_mapped = int(y_zero_mapped - (y - self.min_y) / (self.max_y - self.min_y) * widget_height)
            painter.drawLine(0, y_zero_mapped - y_mapped, widget_width, y_zero_mapped - y_mapped)
            painter.drawLine(0, y_zero_mapped + y_mapped, widget_width, y_zero_mapped + y_mapped)

        # Рисуем ось X (горизонтальную линию через нулевую отметку на оси Y)
        pen.setStyle(Qt.SolidLine)  # Устанавливаем сплошной стиль для оси X
        pen.setColor(QColor(0, 0, 0))  # Устанавливаем черный цвет для оси X
        painter.setPen(pen)
        painter.drawLine(0, y_zero_mapped, widget_width, y_zero_mapped)

        # Рисуем ось Y (вертикальную линию через нулевую отметку на оси X)
        x_zero_mapped = int((0 - self.min_x) / (self.max_x - self.min_x) * widget_width)
        painter.drawLine(x_zero_mapped, 0, x_zero_mapped, widget_height)

    def draw_plot(self, painter, widget_width, widget_height):
        # Список стилей для каждой функции
        line_styles = [
            (QColor(255, 0, 0), 2),  # Красные линии, толщина 2
            (QColor(0, 255, 0), 2),  # Зелёные линии, толщина 2
            (QColor(0, 0, 255), 2)   # Синие линии, толщина 2
        ]

        for i, y_data in enumerate(self.y_values):
            line_color, line_width = line_styles[i % len(line_styles)]
            pen = QPen(line_color)
            pen.setWidth(line_width)
            painter.setPen(pen)

            for j in range(len(self.x_values) - 1):
                x1, y1 = self.map_to_widget(self.x_values[j], y_data[j], widget_width, widget_height)
                x2, y2 = self.map_to_widget(self.x_values[j + 1], y_data[j + 1], widget_width, widget_height)
                painter.drawLine(x1, y1, x2, y2)

