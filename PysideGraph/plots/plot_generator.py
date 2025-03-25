class PlotGenerator:
    def __init__(self, plot_base, x_values, y_values, function_input):
        self.plot_base = plot_base
        self.x_values = x_values
        self.y_values = y_values
        self.function_input = function_input

    def generate_plot(self, plot_widget):
        plot_widget.set_data(self.plot_base, self.x_values, self.y_values, self.function_input)
