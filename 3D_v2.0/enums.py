from enum import Enum

class ShadingMode(Enum):
    MONOTONE = "Монотонное"
    GOURAUD = "Градиент Гуро"
    PHONG = "Градиент Фонга"

class DisplayMode(Enum):
    POINTS = "Точки"
    WIREFRAME = "Каркас"
    FILLED = "Заливка" 