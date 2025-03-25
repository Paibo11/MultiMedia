from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter
from plots import PlotStyle, PlotLine, PlotDiagram, PlotTriangle


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.plot_base = None
        self.x_values = None
        self.y_values = None

        self.setMinimumSize(600, 400)
        self.style = PlotStyle()

    def set_data(self, plot_base, x_values, y_values, function_input):
        self.x_values = x_values
        self.y_values = y_values
        self.plot_base = plot_base
        self.function_input = function_input
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Устанавливаем фон
        painter.setBrush(self.style.background_color)
        painter.drawRect(self.rect())

        if self.plot_base == "Line Plot":
            self.plot_base = PlotLine(self.x_values, self.y_values)
        elif self.plot_base == "Diagram Plot":
            self.plot_base = PlotDiagram(self.x_values, self.y_values)
        elif self.plot_base == "Gistogram parallepiped":
            self.plot_base = PlotTriangle(self.x_values, self.y_values, self.function_input, self.width(), self.height())

        if self.plot_base:
            # Рисуем сетку
            self.plot_base.draw_grid(painter, self.style)

            # Рисуем график
            self.plot_base.draw_plot(painter)

        painter.end()
