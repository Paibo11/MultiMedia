from PySide6.QtWidgets import (QMainWindow, QWidget, QLineEdit, QPushButton,
                               QLabel, QVBoxLayout, QHBoxLayout)
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


        self.min_input = QLineEdit("1.0")
        self.max_input = QLineEdit("10.0")
        self.cylinder_count = QLineEdit("5")

        self.add_function_button = QPushButton("Добавить функцию")
        self.plot_button = QPushButton("Построить график")

        # Установка макета
        main_layout = QVBoxLayout(self.central_widget)
        self.function_layout = QVBoxLayout()

        # Размещаем поля ввода границ и цилиндров
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("От:"))
        range_layout.addWidget(self.min_input)
        range_layout.addWidget(QLabel("До:"))
        range_layout.addWidget(self.max_input)
        range_layout.addWidget(QLabel("Кол-во цилиндров:"))
        range_layout.addWidget(self.cylinder_count)

        main_layout.addLayout(range_layout)
        main_layout.addLayout(self.function_layout)
        main_layout.addWidget(self.add_function_button)
        main_layout.addWidget(self.plot_button)
        main_layout.addWidget(self.plot_widget)

        # Добавление первого ввода функции
        self.add_function_input()

        # Подключение сигналов
        self.add_function_button.clicked.connect(self.add_function_input)
        self.plot_button.clicked.connect(self.plot_graph)

    def add_function_input(self):
        function_input = QLineEdit()
        function_input.setPlaceholderText("Введите функцию, например: sin(x)")
        self.function_inputs.append(function_input)
        if len(self.function_inputs) == 1:
            function_input.setText("sin(x)")
        self.function_layout.addWidget(function_input)

    def plot_graph(self):
        # Получаем текущие значения из полей ввода
        try:
            min_val = float(self.min_input.text())
            max_val = float(self.max_input.text())
            count = int(self.cylinder_count.text())

            # Формируем строку параметров для DataProcessor
            range_str = f"{min_val},{max_val},{count}"

            data_processor = DataProcessor(self.function_inputs, range_str)
            x_values, y_values = data_processor.process_data()

            plot_generator = PlotGenerator(
                "Gistogram parallepiped",  # Тип графика
                x_values,
                y_values,
                self.function_inputs
            )
            plot_generator.generate_plot(self.plot_widget)
        except ValueError:
            print("Ошибка ввода данных. Убедитесь, что введены корректные числовые значения.")

