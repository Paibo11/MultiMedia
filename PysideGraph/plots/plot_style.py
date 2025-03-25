from PySide6.QtGui import QColor

class PlotStyle:
    def __init__(self):
        self.background_color = QColor(255, 255, 255)  # Белый фон
        self.line_color = QColor(0, 0, 0)  # Чёрные линии
        self.line_width = 10  # Толщина линий
        self.grid_color = QColor(50, 50, 50)  # Цвет сетки
        self.grid_black = QColor(0,0,0)
        self.grid_width = 1  # Толщина линий сетки

    def set_background_color(self, color):
        self.background_color = QColor(color)

    def set_line_color(self, color):
        self.line_color = QColor(color)

    def set_line_width(self, width):
        self.line_width = width

    def set_grid_color(self, color):
        self.grid_color = QColor(color)

    def set_grid_width(self, width):
        self.grid_width = width
