import numpy as np
import ast
import sympy as sp


class DataProcessor:
    def __init__(self, functions, range_str):
        self.functions = functions
        self.range_str = range_str

    def process_data(self):
        y_values = []
        num = 300
        try:
            start, stop, num = map(ast.literal_eval, self.range_str.split(','))
        except:
            start, stop = map(ast.literal_eval, self.range_str.split(','))

        x_range = np.linspace(start, stop, num)  # Генерируем массив x
        x_sym = sp.Symbol('x')  # Объявляем символ x

        for func in self.functions:
            expr = sp.sympify(func.text())  # Преобразуем строку в sympy-выражение

            # Вычисляем значения y для каждого x из x_range
            y_data = np.array([expr.subs(x_sym, x_val).evalf() for x_val in x_range])

            y_values.append(y_data)  # Добавляем результат в список
        print(y_data)
        return x_range, np.array(y_values)
