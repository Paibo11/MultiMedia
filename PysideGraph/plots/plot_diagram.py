from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import QRect,  Qt

import numpy as np


class Diagram:
    def __init__(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values
        self.min_x = np.min(x_values)
        self.max_x = np.max(x_values)
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


class PlotDiagram(Diagram):
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
        bar_styles = [
            QColor(210, 0, 107),
            QColor(255, 108, 0),
            QColor(0, 158, 142),
        ]
        
        
        bar_width = widget_width // len(self.x_values)  # Ширина каждого прямоугольника
        y_zero_mapped = int(widget_height - (0 - self.min_y) / (self.max_y - self.min_y) * widget_height)
        for i, y_data in enumerate(self.y_values):
            bar_color = bar_styles[i % len(bar_styles)]
            pen = QPen(bar_color)
            # pen.setWidth(bar_width)
            painter.setPen(pen)
            painter.setBrush(bar_color)

            for j in range(len(self.x_values)):
                x, y = self.map_to_widget(self.x_values[j], y_data[j], widget_width, widget_height)
                bar_height = widget_height - y
                if y_data[j] >= 0:
                    painter.drawRect(x - bar_width , y, bar_width, y_zero_mapped - y)
                else:
                    painter.drawRect(x - bar_width , y_zero_mapped, bar_width, y - y_zero_mapped)



