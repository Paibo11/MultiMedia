from PySide6.QtGui import QPen, QColor, QPainter, QPolygon, QBrush, QPainterPath
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
import numpy as np
from sympy import Float
import math

from scipy.stats import gaussian_kde, mode
import itertools


class PlotTriangle:
    def __init__(self, x_values, y_values, function_input, widget_width, widget_height):
        self.function_input = function_input
        self.x_values = x_values
        self.unclear_value = y_values
        self.min_x = np.min(x_values)
        self.max_x = np.max(x_values)

        self.window_start = 50
        self.window_end = 15
        self.widget_width = widget_width - self.window_start - self.window_end
        self.widget_height = widget_height - self.window_start

        self.y_values = []
        self.x_grid = [[0] * len(y_values[0]) for _ in range(len(y_values))]
        for sublist in self.unclear_value:
            cleaned_sublist = [
                float(value) if isinstance(value, (int, float, Float)) else 0
                for value in sublist
            ]
            self.y_values.append(cleaned_sublist)

        all_y_values = np.concatenate(self.y_values)

        lower_bound = np.percentile(all_y_values, 5)
        upper_bound = np.percentile(all_y_values, 95)
        self.min_y = lower_bound
        self.max_y = upper_bound
        self.max_y_without_padd = np.max(y_values)
        self.min_y_without_padd = np.min(y_values)
        # Добавляем отступ для визуального комфорта
        y_range = self.max_y - self.min_y
        padding = y_range * 0.6
        self.min_y -= padding
        self.max_y += padding

        if self.min_y > 0:
            self.min_y = 0 - padding
        if self.max_y < 0:
            self.max_y = 0 + padding

    def calculate_x_mapped(self):
        gap_size = 20  # Размер промежутка между группами цилиндров

        total_bar_width = (self.widget_width - gap_size * (len(self.x_values) - 1)) // len(self.x_values)
        cylinder_bar = total_bar_width // len(self.y_values)

        for j in range(len(self.x_values)):
            x_start = j * (total_bar_width + gap_size)  # Добавляем зазор между группами
            for i, y_data in enumerate(self.y_values):
                adjusted_x = self.calculate_cylinder_x(x_start, i, cylinder_bar)
                self.x_grid[i][j] = adjusted_x

    def x_widget(self, x, widget_width):
        return int((x - self.min_x) / (self.max_x - self.min_x) * widget_width)

    def y_widget(self, y, widget_height):
        return int(widget_height - (y - self.min_y) / (self.max_y - self.min_y) * widget_height)

    def draw_legend(self, painter):
        pastel_styles = [
            QColor(255, 182, 193),
            QColor(173, 216, 230),
            QColor(144, 238, 144),
            QColor(221, 160, 221),
            QColor(255, 218, 185),
            QColor(175, 238, 238),
            QColor(255, 228, 196),
            QColor(216, 191, 216)
        ]

        text_offset = 20
        legend_start_x = 0
        legend_start_y = self.widget_height + self.window_start / 2 - text_offset / 2
        box_size = 15
        gap = 5

        # Вычисляем ширину каждой легенды
        item_widths = [
            box_size + text_offset + painter.fontMetrics().horizontalAdvance(item.text()) + gap
            for item in self.function_input
        ]
        total_width = sum(item_widths) - gap

        # Рисуем белый фон под легенду
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(legend_start_x - 5, self.widget_height, total_width + 10, self.window_start)

        # Рисуем элементы легенды в ряд
        current_x = legend_start_x
        for i, item in enumerate(self.function_input):
            color = pastel_styles[i % len(pastel_styles)]
            painter.setBrush(color)
            painter.drawRect(current_x, legend_start_y, box_size, box_size)
            painter.drawText(current_x + text_offset, legend_start_y + box_size // 2 + 5, item.text())
            current_x += item_widths[i]

    def draw_grid(self, painter, style):
        pen = QPen(style.grid_color)
        pen.setWidth(style.grid_width)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        # Рисуем вертикальные линии сетки
        self.calculate_x_mapped()
        transorm_grid = np.array(self.x_grid).T

        for j in range(len(self.x_values)):
            x_mapped = np.mean(transorm_grid[j][:])
            painter.drawLine(x_mapped, 0, x_mapped, self.widget_height)

            label = f"{self.x_values[j]:.2f}"  # Format the label as needed
            painter.drawText(x_mapped + 5, self.widget_height - 5, label)

        # Рисуем горизонтальные линии сетки
        y_zero_mapped = self.y_widget(0, self.widget_height)
        max_value = float(np.max([abs(self.min_y_without_padd), self.max_y_without_padd]))

        # Горизонтальные линии
        step = max_value / 4
        y = 0
        while y < float(np.max([abs(self.min_y), self.max_y])):
            y += step

            y_mapped = self.y_widget(y, self.widget_height)
            if y == 0:
                painter.drawLine(0, y_mapped, self.window_start + self.widget_width + self.window_end, y_mapped)
                label = f" {y:.3f}"  # Format the label as needed
                painter.drawText(5, y_mapped, label)
                continue
            if y_mapped > 0:
                painter.drawLine(0, y_mapped, self.window_start + self.widget_width + self.window_end, y_mapped)
                label = f"{y:.3f}"  # Format the label as needed
                painter.drawText(5, y_mapped, label)

            horizont_mapped = y_zero_mapped + (y_zero_mapped - y_mapped)
            if horizont_mapped < self.widget_height:
                painter.drawLine(0, horizont_mapped, self.window_start + self.widget_width + self.window_end,
                                 horizont_mapped)
                label = f"-{y:.3f}"  # Format the label as needed
                painter.drawText(5, horizont_mapped, label)

        # Рисуем ось X
        pen.setStyle(Qt.SolidLine)
        pen.setColor(style.grid_black)
        painter.setPen(pen)
        painter.drawLine(0, y_zero_mapped, self.window_end + self.window_start + self.widget_width, y_zero_mapped)

    def calculate_cylinder_x(self, x_start, i, cylinder_bar):
        self.shift = i * (cylinder_bar // 3)  # Смещение влево
        x_cylinder = self.window_start + x_start + i * cylinder_bar + cylinder_bar / 2 - (2 * self.shift)
        return x_cylinder

    def draw_cylinder(self, painter, center_x, y_zero_mapped, y_data_value, cylinder_bar, depth_shift=0):
        radius = cylinder_bar // 2
        height = abs(self.y_widget(y_data_value, self.widget_height) - y_zero_mapped)
        is_positive = y_data_value >= 0

        # Смещение вверх по Y для эффекта глубины
        depth_offset = -depth_shift * (radius // 1.3)

        # Определяем позиции верха и низа цилиндра с учетом смещения
        if is_positive:
            cylinder_top = y_zero_mapped - height + depth_offset
            cylinder_bottom = y_zero_mapped + depth_offset
        else:
            cylinder_top = y_zero_mapped + depth_offset
            cylinder_bottom = y_zero_mapped + height + depth_offset

        # Сохраняем текущие настройки пера и кисти
        old_pen = painter.pen()
        old_brush = painter.brush()

        # Устанавливаем цвет границы
        border_color = painter.brush().color().darker(120)
        painter.setPen(QPen(border_color, 1))

        # Рисуем верхний эллипс
        top_ellipse = QRectF(center_x - radius, cylinder_top - radius // 4,
                             radius * 2, radius // 2)
        painter.drawEllipse(top_ellipse)

        # Рисуем боковые линии
        left = center_x - radius
        right = center_x + radius
        painter.drawLine(QPointF(left, cylinder_top), QPointF(left, cylinder_bottom))
        painter.drawLine(QPointF(right, cylinder_top), QPointF(right, cylinder_bottom))

        # Рисуем нижний эллипс
        bottom_ellipse = QRectF(center_x - radius, cylinder_bottom - radius // 4,
                                radius * 2, radius // 2)
        painter.drawEllipse(bottom_ellipse)

        # Заливаем цилиндр (рисуем закрытый путь)
        path = QPainterPath()
        path.moveTo(left, cylinder_top)
        path.arcTo(top_ellipse, 180, 180)
        path.lineTo(right, cylinder_bottom)
        path.arcTo(bottom_ellipse, 0, -180)
        path.closeSubpath()

        painter.drawPath(path)
        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def draw_plot(self, painter):
        pastel_styles = [
            QColor(255, 182, 193),
            QColor(173, 216, 230),
            QColor(144, 238, 144),
            QColor(221, 160, 221),
            QColor(255, 218, 185),
            QColor(175, 238, 238),
            QColor(255, 228, 196),
            QColor(216, 191, 216)
        ]

        gap_size = 20  # Размер промежутка между группами цилиндров

        total_bar_width = (self.widget_width - gap_size * (len(self.x_values) - 1)) // len(self.x_values)
        cylinder_bar = total_bar_width // len(self.y_values)

        self.y_zero_mapped = self.y_widget(0, self.widget_height)
        for j in range(len(self.x_values)):
            x_start = j * (total_bar_width + gap_size)  # Добавляем зазор между группами
            for i, y_data in reversed(list(enumerate(self.y_values))):  # Инвертируем порядок отрисовки
                pastel_color = pastel_styles[i % len(pastel_styles)]
                painter.setBrush(pastel_color)
                # Граница чуть темнее основного цвета
                painter.setPen(QPen(pastel_color.darker(120), 1))

                adjusted_x = self.calculate_cylinder_x(x_start, i, cylinder_bar)
                self.draw_cylinder(painter, adjusted_x, self.y_zero_mapped, y_data[j], cylinder_bar, depth_shift=i)

        self.draw_legend(painter)