from PySide6.QtWidgets import QMainWindow, QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QComboBox
from .plot_widget import PlotWidget
from data import DataProcessor
from plots.plot_generator import PlotGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualization App")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Создание виджетов
        self.plot_widget = PlotWidget()
        self.function_inputs = []
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("Впишите границы и кол-во цилиндров")
        self.range_input.setText("1,10,5")
        self.add_function_button = QPushButton("Add")
        self.plot_button = QPushButton("Update")

        # Тип графика всегда
        self.plot_type = "Gistogram parallepiped"

        # Установка макета
        main_layout = QVBoxLayout(self.central_widget)
        self.function_layout = QVBoxLayout()

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Границы и кол-во цилиндров:"))
        range_layout.addWidget(self.range_input)

        main_layout.addLayout(range_layout)
        main_layout.addLayout(self.function_layout)
        main_layout.addWidget(self.add_function_button)
        main_layout.addWidget(self.plot_button)
        main_layout.addWidget(self.plot_widget)

        # Добавление первого ввода функции
        self.add_function_input()

        # Подключение сигналов и слотов
        self.add_function_button.clicked.connect(self.add_function_input)
        self.plot_button.clicked.connect(self.plot_graph)

    def add_function_input(self):
        function_input = QLineEdit()
        function_input.setPlaceholderText("Впишите функцию например: sin(x)")
        self.function_inputs.append(function_input)
        if len(self.function_inputs) == 1:
            function_input.setText("sin(x)")
        self.function_layout.addWidget(function_input)

    def plot_graph(self):
        data_processor = DataProcessor(self.function_inputs, self.range_input.text())
        x_values, y_values = data_processor.process_data()

        plot_generator = PlotGenerator(self.plot_type, x_values, y_values, self.function_inputs)
        plot_generator.generate_plot(self.plot_widget)


# Пример использования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())