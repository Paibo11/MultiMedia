# Импорт необходимых модулей и библиотек
import sys  # Для работы с системными параметрами и аргументами
import math  # Для математических вычислений (sin, cos, sqrt и т.д.)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QSlider, QLabel, QPushButton, QScrollArea,
                               QSizePolicy, QGroupBox)  # Виджеты PySide6 для создания интерфейса
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QPolygonF,
                           QLinearGradient)  # Инструменты для рисования и работы с графикой
from PySide6.QtCore import Qt, QPoint, QPointF  # Основные классы Qt (например, для работы с точками)
from enum import Enum  # Для создания перечислений (enum)

# Перечисление для методов закраски
class ShadingMode(Enum):
    MONOTONE = "Монотонное"  # Монотонная закраска (один цвет с учётом освещения)
    GOURAUD = "Градиент Гуро"  # Градиентная закраска по методу Гуро
    PHONG = "Градиент Фонга"  # Градиентная закраска по методу Фонга

# Перечисление для методов отображения
class DisplayMode(Enum):
    POINTS = "Точки"  # Отображение только вершин в виде точек
    WIREFRAME = "Каркас"  # Отображение каркаса (линии между вершинами)
    FILLED = "Заливка"  # Полное заполнение граней с учётом закраски

# Класс Vector3D для работы с трёхмерными векторами
class Vector3D:
    def __init__(self, x, y, z):
        self.x = x  # Координата X
        self.y = y  # Координата Y
        self.z = z  # Координата Z

    def __add__(self, other):
        # Сложение двух векторов
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        # Вычитание двух векторов
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        # Умножение вектора на скаляр
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def length(self):
        # Вычисление длины вектора
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        # Нормализация вектора (приведение к единичной длине)
        length = self.length()
        if length == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        # Скалярное произведение векторов
        return self.x * other.x + self.y * other.y + self.z * other.z

# Класс Matrix4x4 для работы с матрицами 4x4 (для преобразований)
class Matrix4x4:
    def __init__(self):
        # Инициализация единичной матрицы 4x4
        self.m = [[0] * 4 for _ in range(4)]
        self.m[0][0] = 1
        self.m[1][1] = 1
        self.m[2][2] = 1
        self.m[3][3] = 1

    def __mul__(self, other):
        # Умножение матрицы на вектор или другую матрицу
        if isinstance(other, Vector3D):
            # Умножение матрицы на вектор (с учётом гомогенных координат)
            x = self.m[0][0] * other.x + self.m[0][1] * other.y + self.m[0][2] * other.z + self.m[0][3]
            y = self.m[1][0] * other.x + self.m[1][1] * other.y + self.m[1][2] * other.z + self.m[1][3]
            z = self.m[2][0] * other.x + self.m[2][1] * other.y + self.m[2][2] * other.z + self.m[2][3]
            w = self.m[3][0] * other.x + self.m[3][1] * other.y + self.m[3][2] * other.z + self.m[3][3]
            if w != 0:
                x /= w
                y /= w
                z /= w
            return Vector3D(x, y, z)
        elif isinstance(other, Matrix4x4):
            # Умножение двух матриц
            result = Matrix4x4()
            for i in range(4):
                for j in range(4):
                    result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
            return result

    @staticmethod
    def translation(x, y, z):
        # Создание матрицы переноса
        mat = Matrix4x4()
        mat.m[0][3] = x
        mat.m[1][3] = y
        mat.m[2][3] = z
        return mat

    @staticmethod
    def rotation_x(angle):
        # Создание матрицы вращения вокруг оси X
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[1][1] = math.cos(rad)
        mat.m[1][2] = -math.sin(rad)
        mat.m[2][1] = math.sin(rad)
        mat.m[2][2] = math.cos(rad)
        return mat

    @staticmethod
    def rotation_y(angle):
        # Создание матрицы вращения вокруг оси Y
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[0][0] = math.cos(rad)
        mat.m[0][2] = math.sin(rad)
        mat.m[2][0] = -math.sin(rad)
        mat.m[2][2] = math.cos(rad)
        return mat

    @staticmethod
    def rotation_z(angle):
        # Создание матрицы вращения вокруг оси Z
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[0][0] = math.cos(rad)
        mat.m[0][1] = -math.sin(rad)
        mat.m[1][0] = math.sin(rad)
        mat.m[1][1] = math.cos(rad)
        return mat

    @staticmethod
    def scaling(sx, sy, sz):
        # Создание матрицы масштабирования
        mat = Matrix4x4()
        mat.m[0][0] = sx
        mat.m[1][1] = sy
        mat.m[2][2] = sz
        return mat

# Класс Face для представления граней объекта
class Face:
    def __init__(self, vertices, color):
        self.vertices = vertices  # Список вершин грани
        self.color = color  # Цвет грани
        self.normal = self.calculate_normal()  # Нормаль грани
        self.center = self.calculate_center()  # Центр грани

    def calculate_normal(self):
        # Вычисление нормали грани (вектор, перпендикулярный грани)
        if len(self.vertices) < 3:
            return Vector3D(0, 0, 0)
        v1 = self.vertices[1] - self.vertices[0]
        v2 = self.vertices[2] - self.vertices[0]
        normal = Vector3D(
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x
        )
        return normal.normalized()

    def calculate_center(self):
        # Вычисление центра грани (среднее по координатам вершин)
        if not self.vertices:
            return Vector3D(0, 0, 0)
        x = sum(v.x for v in self.vertices) / len(self.vertices)
        y = sum(v.y for v in self.vertices) / len(self.vertices)
        z = sum(v.z for v in self.vertices) / len(self.vertices)
        return Vector3D(x, y, z)

# Класс Letter3D для создания 3D букв (Т и Н)
class Letter3D:
    def __init__(self, height, width, depth, offset_x=0, letter_type='T'):
        self.height = height  # Высота буквы
        self.width = width  # Ширина буквы
        self.depth = depth  # Глубина буквы
        self.offset_x = offset_x  # Смещение по оси X
        self.letter_type = letter_type  # Тип буквы ('T' или 'H')
        self.vertices = []  # Список вершин
        self.faces = []  # Список граней
        self.update_geometry()  # Инициализация геометрии

    def update_geometry(self):
        # Обновление геометрии буквы при изменении параметров
        self.vertices = []
        self.faces = []
        h, w, d, ox = self.height, self.width, self.depth, self.offset_x
        bar_thickness = h * 0.2  # Толщина перекладин (20% от высоты)

        if self.letter_type == 'T':
            self._create_letter_T(h, w, d, ox, bar_thickness)
        elif self.letter_type == 'H':
            self._create_letter_H(h, w, d, ox, bar_thickness)
        elif self.letter_type == 'V':
            self._create_letter_V(h, w, d, ox, bar_thickness)

    def _create_letter_T(self, h, w, d, ox, bar_thickness):
        hw = w / 2
        hd = d / 2
        vw = w / 6
        front_top = [
            Vector3D(ox - hw, h, -hd), Vector3D(ox + hw, h, -hd),
            Vector3D(ox + hw, h - bar_thickness, -hd), Vector3D(ox - hw, h - bar_thickness, -hd)
        ]
        back_top = [
            Vector3D(ox - hw, h, hd), Vector3D(ox + hw, h, hd),
            Vector3D(ox + hw, h - bar_thickness, hd), Vector3D(ox - hw, h - bar_thickness, hd)
        ]
        front_vert = [
            Vector3D(ox - vw, h - bar_thickness, -hd), Vector3D(ox + vw, h - bar_thickness, -hd),
            Vector3D(ox + vw, 0, -hd), Vector3D(ox - vw, 0, -hd)
        ]
        back_vert = [
            Vector3D(ox - vw, h - bar_thickness, hd), Vector3D(ox + vw, h - bar_thickness, hd),
            Vector3D(ox + vw, 0, hd), Vector3D(ox - vw, 0, hd)
        ]
        self.vertices = front_top + back_top + front_vert + back_vert
        colors = [QColor(255, 140, 0), QColor(255, 165, 0), QColor(255, 127, 80)]
        self._create_faces_for_part(front_top, back_top, colors)
        self._create_faces_for_part(front_vert, back_vert, colors)
        self.faces.append(Face([front_top[2], front_top[3], front_vert[0], front_vert[1]], colors[1]))
        self.faces.append(Face([back_top[2], back_top[3], back_vert[0], back_vert[1]], colors[1]))


    def _create_letter_V(self, h, w, d, ox, bar_thickness):
        hw = w / 2
        hd = d / 2
        front_left = [
            Vector3D(ox - hw, h, -hd), Vector3D(ox - hw + bar_thickness, h, -hd),
            Vector3D(ox, 0, -hd), Vector3D(ox - bar_thickness, 0, -hd)
        ]
        back_left = [
            Vector3D(ox - hw, h, hd), Vector3D(ox - hw + bar_thickness, h, hd),
            Vector3D(ox, 0, hd), Vector3D(ox - bar_thickness, 0, hd)
        ]
        front_right = [
            Vector3D(ox + hw - bar_thickness, h, -hd), Vector3D(ox + hw, h, -hd),
            Vector3D(ox + bar_thickness, 0, -hd), Vector3D(ox, 0, -hd)
        ]
        back_right = [
            Vector3D(ox + hw - bar_thickness, h, hd), Vector3D(ox + hw, h, hd),
            Vector3D(ox + bar_thickness, 0, hd), Vector3D(ox, 0, hd)
        ]
        self.vertices = front_left + back_left + front_right + back_right
        colors = [QColor(255, 140, 0), QColor(255, 165, 0), QColor(255, 127, 80)]
        self._create_faces_for_part(front_left, back_left, colors)
        self._create_faces_for_part(front_right, back_right, colors)

    def _create_faces_for_part(self, front_vertices, back_vertices, colors):
        # Создание граней для части буквы (передняя, задняя, боковые, верхняя и нижняя)
        self.faces.append(Face(front_vertices, colors[0]))  # Передняя грань
        self.faces.append(Face(back_vertices, colors[0]))  # Задняя грань
        for i in range(len(front_vertices)):
            next_i = (i + 1) % len(front_vertices)
            side_face = [
                front_vertices[i],
                front_vertices[next_i],
                back_vertices[next_i],
                back_vertices[i]
            ]
            self.faces.append(Face(side_face, colors[1]))  # Боковые грани
        if len(front_vertices) >= 4:
            top_face = [front_vertices[0], front_vertices[1], back_vertices[1], back_vertices[0]]
            bottom_face = [front_vertices[2], front_vertices[3], back_vertices[3], back_vertices[2]]
            self.faces.append(Face(top_face, colors[2]))  # Верхняя грань
            self.faces.append(Face(bottom_face, colors[2]))  # Нижняя грань

# Класс SceneWidget для отображения 3D сцены
class SceneWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)  # Включение автоматической заливки фона
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(50, 50, 50))  # Тёмный фон, как на изображении
        self.setPalette(p)
        self.t_letter = Letter3D(100, 60, 30, offset_x=-10, letter_type='T')  # Буква Т
        self.n_letter = Letter3D(100, 60, 30, offset_x=60, letter_type='V')  # Буква V
        self.camera_pos = Vector3D(0, 0, -400)  # Позиция камеры
        self.camera_rot = [0, 0, 0]  # Углы поворота камеры (X, Y, Z)
        self.object_transform = Matrix4x4.rotation_z(180)  # Начальное вращение объекта на 180 градусов
        self.scale = 1.0  # Текущий масштаб
        self.base_scale = 1.4  # Базовый масштаб для пропорций
        self.auto_scale = True  # Автоматическое масштабирование
        self.light_dir = Vector3D(0.5, 0.5, -1).normalized()  # Направление света
        self.light_pos = self.light_dir * 150  # Позиция источника света (на расстоянии 150 от начала координат)
        self.display_mode = DisplayMode.FILLED  # Режим отображения (по умолчанию заливка)
        self.shading_mode = ShadingMode.PHONG  # Режим закраски (по умолчанию Фонг)
        self.mirror_x = False  # Зеркальное отображение по X
        self.mirror_y = False  # Зеркальное отображение по Y
        self.mirror_z = False  # Зеркальное отображение по Z
        self.last_mouse_pos = None  # Для отслеживания предыдущей позиции мыши
        self.setMouseTracking(True)  # Включаем отслеживание движения мыши

    def compute_phong_lighting(self, normal, position, face_normal):
        # Модель освещения Фонга
        ambient_strength = 0.3  # Сила фонового освещения
        diffuse_strength = 0.6  # Сила диффузного освещения
        specular_strength = 0.5  # Сила зеркального освещения
        shininess = 32  # Коэффициент блеска (чем больше, тем меньше блик)

        light_pos = self.light_pos  # Позиция источника света
        light_dir = (light_pos - position).normalized()  # Направление света

        # Вычисляем нормаль, направленную к источнику света
        to_light = (light_pos - position).normalized()
        world_normal = self.object_transform * face_normal
        world_normal = world_normal.normalized()

        # Проверяем, с какой стороны находится свет
        if world_normal.dot(to_light) < 0:
            world_normal = -world_normal  # Инвертируем нормаль, если свет с другой стороны

        # Затухание света
        distance = (light_pos - position).length()
        constant_attenuation = 1.0
        linear_attenuation = 0.09
        quadratic_attenuation = 0.032
        attenuation = 1.0 / (constant_attenuation + linear_attenuation * distance + quadratic_attenuation * distance * distance)

        ambient = ambient_strength  # Фоновый компонент
        diffuse = diffuse_strength * max(0, world_normal.dot(light_dir))  # Диффузный компонент
        reflect_dir = (light_dir - world_normal * (2 * world_normal.dot(light_dir))).normalized()  # Вектор отражения света
        specular = specular_strength * max(0, reflect_dir.dot(to_light)) ** shininess  # Зеркальный компонент

        intensity = (ambient + diffuse + specular) * attenuation  # Итоговая интенсивность с учетом затухания
        return min(1.0, max(0.3, intensity))  # Ограничиваем интенсивность

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        self.draw_axes(painter)

        # Подготавливаем все грани обоих букв
        all_faces = []

        # Подготавливаем грани буквы Т
        t_faces = self._prepare_letter_faces(self.t_letter)
        all_faces.extend(t_faces)

        # Подготавливаем грани буквы V
        v_faces = self._prepare_letter_faces(self.n_letter)
        all_faces.extend(v_faces)

        # Сортируем все грани по глубине
        all_faces.sort(reverse=True, key=lambda x: x[0])

        # Отрисовываем грани в порядке от дальних к ближним
        for depth, face, screen_points, intensities, positions, face_normals in all_faces:
            if len(screen_points) >= 3:
                if self.display_mode == DisplayMode.POINTS:
                    painter.setPen(QPen(face.color, 5))
                    for point in screen_points:
                        if point.x() != -1000 and point.y() != -1000:
                            painter.drawPoint(point)
                elif self.display_mode == DisplayMode.WIREFRAME:
                    polygon = QPolygonF(screen_points)
                    painter.setPen(QPen(face.color, 2))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPolygon(polygon)
                elif self.display_mode == DisplayMode.FILLED:
                    self._draw_filled_face(painter, face, screen_points, intensities, positions, face_normals)

        self.draw_light_source(painter)

    def _prepare_letter_faces(self, letter):
        faces_with_depth = []
        transformed_vertices = []
        vertex_normals = []

        mirror_matrix = Matrix4x4.scaling(
            -1 if self.mirror_x else 1,
            -1 if self.mirror_y else 1,
            -1 if self.mirror_z else 1
        )

        # Преобразуем вершины и вычисляем нормали
        for v in letter.vertices:
            v_mirrored = mirror_matrix * v
            v_transformed = self.object_transform * v_mirrored
            v_camera = self.apply_camera_transform(v_transformed)
            transformed_vertices.append(v_camera)

            normal_sum = Vector3D(0, 0, 0)
            count = 0
            for face in letter.faces:
                if v in face.vertices:
                    normal_sum = normal_sum + face.normal
                    count += 1
            vertex_normals.append(normal_sum.normalized() if count > 0 else Vector3D(0, 0, 1))

        # Подготавливаем каждую грань
        for face in letter.faces:
            face_vertices = [transformed_vertices[letter.vertices.index(v)] for v in face.vertices]
            face_normals = [vertex_normals[letter.vertices.index(v)] for v in face.vertices]

            # Вычисляем среднюю глубину грани
            avg_depth = sum(v.z for v in face_vertices) / len(face_vertices)

            screen_points = []
            intensities = []
            positions = []

            # Вычисляем нормаль грани
            v1 = face_vertices[1] - face_vertices[0]
            v2 = face_vertices[2] - face_vertices[0]
            face_normal = Vector3D(
                v1.y * v2.z - v1.z * v2.y,
                v1.z * v2.x - v1.x * v2.z,
                v1.x * v2.y - v1.y * v2.x
            ).normalized()

            # Проецируем вершины на экран и вычисляем освещение
            for i, v in enumerate(face_vertices):
                if v.z > 0:
                    factor = 300 / v.z
                    aspect_ratio = self.width() / self.height()
                    px = v.x * factor * self.base_scale * (1 / aspect_ratio if aspect_ratio > 1 else 1) + self.width() / 2
                    py = v.y * factor * self.base_scale * (1 if aspect_ratio > 1 else aspect_ratio) + self.height() / 2
                    screen_points.append(QPointF(px, py))
                    intensity = self.compute_phong_lighting(face_normals[i], v, face_normal)
                    intensities.append(intensity)
                    positions.append(v)
                else:
                    screen_points.append(QPointF(-1000, -1000))
                    intensities.append(0)
                    positions.append(Vector3D(0, 0, 0))

            faces_with_depth.append((avg_depth, face, screen_points, intensities, positions, face_normals))

        return faces_with_depth

    def _draw_filled_face(self, painter, face, screen_points, intensities, positions, face_normals):
        if len(screen_points) < 3:
            return

        if self.shading_mode == ShadingMode.MONOTONE:
            world_normal = self.object_transform * face.normal
            world_normal = world_normal.normalized()
            intensity = max(0.3, world_normal.dot(self.light_dir))
            color = QColor(
                min(255, int(face.color.red() * intensity)),
                min(255, int(face.color.green() * intensity)),
                min(255, int(face.color.blue() * intensity))
            )
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(QBrush(color))
            painter.drawPolygon(QPolygonF(screen_points))

        elif self.shading_mode == ShadingMode.GOURAUD:
            for i in range(len(screen_points) - 2):
                triangle = QPolygonF([screen_points[0], screen_points[i + 1], screen_points[i + 2]])

                gradient = QLinearGradient(screen_points[0], screen_points[i + 1])

                color0 = QColor(
                    min(255, int(face.color.red() * intensities[0])),
                    min(255, int(face.color.green() * intensities[0])),
                    min(255, int(face.color.blue() * intensities[0]))
                )
                color1 = QColor(
                    min(255, int(face.color.red() * intensities[i + 1])),
                    min(255, int(face.color.green() * intensities[i + 1])),
                    min(255, int(face.color.blue() * intensities[i + 1]))
                )
                color2 = QColor(
                    min(255, int(face.color.red() * intensities[i + 2])),
                    min(255, int(face.color.green() * intensities[i + 2])),
                    min(255, int(face.color.blue() * intensities[i + 2]))
                )

                gradient.setColorAt(0, color0)
                gradient.setColorAt(0.5, color1)
                gradient.setColorAt(1, color2)

                painter.setPen(QPen(Qt.black, 1))
                painter.setBrush(QBrush(gradient))
                painter.drawPolygon(triangle)

        elif self.shading_mode == ShadingMode.PHONG:
            for i in range(len(screen_points) - 2):
                triangle = QPolygonF([screen_points[0], screen_points[i + 1], screen_points[i + 2]])

                v1 = positions[i + 1] - positions[0]
                v2 = positions[i + 2] - positions[0]
                triangle_normal = Vector3D(
                    v1.y * v2.z - v1.z * v2.y,
                    v1.z * v2.x - v1.x * v2.z,
                    v1.x * v2.y - v1.y * v2.x
                ).normalized()

                world_normal = self.object_transform * triangle_normal
                world_normal = world_normal.normalized()

                intensity = self.compute_phong_lighting(world_normal, positions[0])

                color = QColor(
                    min(255, int(face.color.red() * intensity)),
                    min(255, int(face.color.green() * intensity)),
                    min(255, int(face.color.blue() * intensity))
                )

                painter.setPen(QPen(Qt.black, 1))
                painter.setBrush(QBrush(color))
                painter.drawPolygon(triangle)

    def draw_axes(self, painter):
        # Отрисовка осей координат
        origin = self.project_point(Vector3D(0, 0, 0))  # Начало координат
        x_end = self.project_point(Vector3D(150, 0, 0))  # Конец оси X
        y_end = self.project_point(Vector3D(0, 150, 0))  # Конец оси Y
        z_end = self.project_point(Vector3D(0, 0, 150))  # Конец оси Z
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(origin, x_end)
        painter.drawText(x_end + QPoint(5, 5), "X")  # Ось X (красная)
        painter.setPen(QPen(Qt.green, 2))
        painter.drawLine(origin, y_end)
        painter.drawText(y_end + QPoint(5, 5), "Y")  # Ось Y (зелёная)
        painter.setPen(QPen(Qt.blue, 2))
        painter.drawLine(origin, z_end)
        painter.drawText(z_end + QPoint(5, 5), "Z")  # Ось Z (синяя)

    def draw_light_source(self, painter):
        # Отрисовка источника света в виде жёлтой точки
        light_pos = self.light_pos  # Позиция источника света
        screen_pos = self.project_point(light_pos)  # Проецируем позицию на экран
        if screen_pos.x() != -1000 and screen_pos.y() != -1000:  # Проверяем, что точка видима
            painter.setPen(QPen(Qt.yellow, 1))  # Жёлтый цвет для источника света
            painter.setBrush(QBrush(Qt.yellow))  # Заливка жёлтым
            painter.drawEllipse(screen_pos, 5, 5)  # Рисуем небольшую окружность (диаметр 10 пикселей)
            painter.drawText(screen_pos + QPoint(10, 10), "Light")  # Подпись "Light"

    def project_point(self, point):
        # Проецирование 3D точки на 2D экран
        v_transformed = self.object_transform * point  # Применение трансформации объекта
        v_camera = self.apply_camera_transform(v_transformed)  # Применение трансформации камеры
        if v_camera.z > 0:  # Проверка, что точка находится перед камерой
            factor = 300 / v_camera.z  # Перспективная проекция
            aspect_ratio = self.width() / self.height()  # Соотношение сторон окна
            # Учёт масштаба и соотношения сторон при проецировании
            px = v_camera.x * factor * self.base_scale * (1 / aspect_ratio if aspect_ratio > 1 else 1) + self.width() / 2
            py = v_camera.y * factor * self.base_scale * (1 if aspect_ratio > 1 else aspect_ratio) + self.height() / 2
            return QPoint(int(px), int(py))  # Возвращаем экранные координаты
        return QPoint(-1000, -1000)  # Точка за камерой (не отображается)

    def apply_camera_transform(self, v):
        # Применение трансформации камеры (вращение и перенос)
        rot_x = Matrix4x4.rotation_x(self.camera_rot[0])  # Вращение вокруг оси X
        rot_y = Matrix4x4.rotation_y(self.camera_rot[1])  # Вращение вокруг оси Y
        rot_z = Matrix4x4.rotation_z(self.camera_rot[2])  # Вращение вокруг оси Z
        rotation = rot_x * rot_y * rot_z  # Комбинированная матрица вращения
        # Матрица переноса (смещение камеры)
        translation = Matrix4x4.translation(-self.camera_pos.x, -self.camera_pos.y, -self.camera_pos.z)
        camera_transform = rotation * translation  # Итоговая трансформация камеры
        return camera_transform * v  # Применение трансформации к точке

    def auto_scale_view(self):
        # Автоматическое масштабирование сцены в зависимости от размера окна
        if self.auto_scale:
            self.base_scale = min(self.width(), self.height()) / 600.0  # Масштаб относительно размера окна

    def resizeEvent(self, event):
        # Обработка изменения размера окна
        self.auto_scale_view()  # Обновление масштаба
        super().resizeEvent(event)  # Вызов родительского метода

    def set_mirror(self, axis):
        # Установка зеркального отображения по заданной оси
        if axis == 0:
            self.mirror_x = not self.mirror_x  # Переключение зеркала по X
        elif axis == 1:
            self.mirror_y = not self.mirror_y  # Переключение зеркала по Y
        else:
            self.mirror_z = not self.mirror_z  # Переключение зеркала по Z
        self.update()  # Перерисовка сцены

    def set_light_direction(self, x, y, z):
        # Установка направления источника света
        self.light_dir = Vector3D(x, y, z).normalized()  # Нормализация вектора направления
        self.light_pos = self.light_dir * 150  # Обновляем позицию источника света
        self.update()  # Перерисовка сцены

    def set_display_mode(self, mode):
        # Установка режима отображения (точки, каркас, заливка)
        self.display_mode = mode
        self.update()  # Перерисовка сцены

    def set_shading_mode(self, mode):
        # Установка режима закраски (монотонное, Гуро, Фонг)
        self.shading_mode = mode
        self.update()  # Перерисовка сцены

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.RightButton and self.last_mouse_pos is not None:
            current_pos = event.position()
            dx = -(current_pos.x() - self.last_mouse_pos.x())
            dy = current_pos.y() - self.last_mouse_pos.y()

            # Вращение по оси Y при движении мыши по X
            rot_y = Matrix4x4.rotation_y(dx * 0.5)
            # Вращение по оси X при движении мыши по Y
            rot_x = Matrix4x4.rotation_x(dy * 0.5)

            # Применяем вращение к текущей трансформации объекта
            self.object_transform = rot_y * rot_x * self.object_transform
            self.update()

            self.last_mouse_pos = current_pos

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.last_mouse_pos = None

    def wheelEvent(self, event):
        # Получаем угол поворота колесика
        delta = event.angleDelta().y()

        # Определяем направление движения камеры
        move_amount = delta / 120  # Нормализуем значение
        zoom_factor = 10  # Коэффициент масштабирования

        # Изменяем позицию камеры по оси Z
        self.camera_pos.z += move_amount * zoom_factor

        # Ограничиваем минимальное расстояние камеры
        if self.camera_pos.z > -50:
            self.camera_pos.z = -50

        self.update()  # Перерисовываем сцену

# Класс MainWindow для создания главного окна приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Буквы ТН")  # Заголовок окна
        self.setGeometry(100, 100, 1000, 800)  # Размер и положение окна
        main_widget = QWidget()
        self.setCentralWidget(main_widget)  # Установка центрального виджета
        layout = QHBoxLayout(main_widget)  # Основной горизонтальный layout
        self.scene = SceneWidget()  # Создание сцены
        layout.addWidget(self.scene, stretch=3)  # Добавление сцены в layout (занимает 3/4 пространства)

        # Создание панели управления с прокруткой
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(5, 5, 5, 5)  # Отступы
        control_layout.setSpacing(10)  # Расстояние между элементами

        # Установка политики размеров для панели управления
        control_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # Добавление элементов управления
        self.create_letter_controls(control_layout, "Буква Т:", 't')  # Управление параметрами буквы Т
        self.create_letter_controls(control_layout, "Буква Н:", 'n')  # Управление параметрами буквы Н
        self.create_transform_controls(control_layout, "Управление объектом:",
                                       self.rotate_object, self.scale_object)  # Управление вращением и масштабом объекта


        # Кнопка сброса вида
        reset_btn = QPushButton("Сбросить вид")
        reset_btn.setMinimumHeight(40)
        reset_btn.clicked.connect(self.reset_view)  # Привязка метода сброса
        control_layout.addWidget(reset_btn)
        control_layout.addStretch()  # Растяжка для выравнивания элементов

        # Добавление панели управления в область с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidget(control_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(350)  # Минимальная ширина панели управления
        scroll_area.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        layout.addWidget(scroll_area, stretch=1)  # Панель занимает 1/4 пространства

    def create_letter_controls(self, layout, title, prefix):
        # Создание элементов управления параметрами буквы
        group = QGroupBox(title)  # Группа с заголовком
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(5)

        # Создание слайдеров для высоты, ширины и глубины
        for param, text in [('height', 'Высота'), ('width', 'Ширина'), ('depth', 'Глубина')]:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(10, 200)  # Диапазон значений
            slider.setValue(getattr(self.scene, f"{prefix}_letter").__dict__[param])  # Начальное значение
            # Привязка изменения значения слайдера к обновлению параметра
            slider.valueChanged.connect(lambda v, p=param, pr=prefix: self.update_letter_param(pr, p, v))

            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)

            group_layout.addWidget(label)
            group_layout.addWidget(slider)

        layout.addWidget(group)

    def create_transform_controls(self, layout, title, rotate_cb, scale_cb):
        # Создание элементов управления трансформацией (вращение и масштаб)
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        if rotate_cb:
            # Создание кнопок для вращения по осям X, Y, Z
            rot_group = QWidget()
            rot_layout = QHBoxLayout(rot_group)
            rot_layout.setSpacing(5)

            for axis, text in [(0, "X"), (1, "Y"), (2, "Z")]:
                btn_layout = QVBoxLayout()
                btn_layout.setSpacing(5)

                label = QLabel(text)
                label.setAlignment(Qt.AlignCenter)
                btn_layout.addWidget(label)

                btn_plus = QPushButton("+")
                btn_plus.setMinimumSize(50, 30)
                btn_plus.clicked.connect(lambda _, a=axis: rotate_cb(a, 10))  # Вращение на +10 градусов
                btn_layout.addWidget(btn_plus)

                btn_minus = QPushButton("-")
                btn_minus.setMinimumSize(50, 30)
                btn_minus.clicked.connect(lambda _, a=axis: rotate_cb(a, -10))  # Вращение на -10 градусов
                btn_layout.addWidget(btn_minus)

                rot_layout.addLayout(btn_layout)

            group_layout.addWidget(rot_group)

        if scale_cb:
            # Создание слайдера для масштабирования
            scale_slider = QSlider(Qt.Horizontal)
            scale_slider.setRange(100, 400)  # Диапазон масштаба
            scale_slider.setValue(100)  # Начальное значение (100%)
            scale_slider.valueChanged.connect(scale_cb)  # Привязка изменения масштаба

            label = QLabel("Масштаб:")
            label.setAlignment(Qt.AlignCenter)

            group_layout.addWidget(label)
            group_layout.addWidget(scale_slider)

        layout.addWidget(group)

    def create_mirror_controls(self, layout):
        # Создание кнопок для зеркального отображения
        group = QGroupBox("Зеркальное отображение")
        group_layout = QHBoxLayout(group)
        group_layout.setSpacing(10)

        for axis, text in [(0, "X"), (1, "Y")]:
            btn = QPushButton(f"Зеркало {text}")
            btn.setCheckable(True)  # Кнопка с переключением состояния
            btn.setMinimumSize(80, 30)
            btn.clicked.connect(lambda _, a=axis: self.scene.set_mirror(a))  # Привязка метода зеркального отображения
            group_layout.addWidget(btn)

        layout.addWidget(group)

    def create_light_controls(self, layout):
        # Создание слайдеров для направления источника света
        group = QGroupBox("Источник света")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(5)

        for axis, text in [('x', 'X'), ('y', 'Y'), ('z', 'Z')]:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(-180, 180)  # Диапазон от -90 до 90 градусов (180 градусов в сумме)
            slider.setValue(30 if axis == 'z' else 45 if axis == 'x' else 45)  # Начальные значения: x=45, y=45, z=30
            slider.valueChanged.connect(lambda v, a=axis: self.update_light(a, v))  # Привязка изменения направления

            label = QLabel(f"Направление {text}:")
            label.setAlignment(Qt.AlignCenter)

            group_layout.addWidget(label)
            group_layout.addWidget(slider)

        layout.addWidget(group)

    def create_display_controls(self, layout):
        # Создание кнопок для выбора режима отображения
        group = QGroupBox("Режим отображения")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(5)

        for mode in DisplayMode:
            btn = QPushButton(mode.value)
            btn.setCheckable(True)
            btn.setMinimumHeight(30)
            btn.setChecked(mode == DisplayMode.FILLED)  # Начальный выбор
            btn.clicked.connect(lambda _, m=mode: self.update_display(m))  # Привязка изменения режима
            group_layout.addWidget(btn)

        layout.addWidget(group)

    def create_shading_controls(self, layout):
        # Создание кнопок для выбора метода закраски
        group = QGroupBox("Метод закраски")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(5)

        for mode in ShadingMode:
            btn = QPushButton(mode.value)
            btn.setCheckable(True)
            btn.setMinimumHeight(30)
            btn.setChecked(mode == ShadingMode.PHONG)  # Начальный выбор
            btn.clicked.connect(lambda _, m=mode: self.update_shading(m))  # Привязка изменения метода
            group_layout.addWidget(btn)

        layout.addWidget(group)

    def update_letter_param(self, prefix, param, value):
        # Обновление параметра буквы (высота, ширина, глубина)
        letter = getattr(self.scene, f"{prefix}_letter")
        setattr(letter, param, value)
        letter.update_geometry()  # Пересчёт геометрии буквы
        self.scene.update()  # Перерисовка сцены

    def rotate_object(self, axis, angle):
        # Вращение объекта вокруг заданной оси
        if axis == 0:
            rot = Matrix4x4.rotation_x(angle)
        elif axis == 1:
            rot = Matrix4x4.rotation_y(angle)
        else:
            rot = Matrix4x4.rotation_z(angle)
        self.scene.object_transform = rot * self.scene.object_transform  # Применение вращения
        self.scene.update()  # Перерисовка сцены

    def scale_object(self, value):
        # Изменение масштаба объекта
        scale_factor = value / 100.0
        self.scene.base_scale = scale_factor
        self.scene.update()  # Перерисовка сцены

    def rotate_camera(self, axis, angle):
        # Вращение камеры вокруг заданной оси
        self.scene.camera_rot[axis] += angle
        self.scene.update()  # Перерисовка сцены

    def update_light(self, axis, value):
        # Обновление направления источника света с ограничением до 180 градусов
        rad = math.radians(value)  # Преобразование градусов в радианы
        current = [self.scene.light_dir.x, self.scene.light_dir.y, self.scene.light_dir.z]

        # Начальное направление света (0.5, 0.5, -1) нормализуется
        if axis == 'x':
            # Поворот по X: изменяем только x-компоненту в пределах 180 градусов
            current[0] = math.sin(rad) * 0.707 + 0.5  # 0.707 = sqrt(2)/2 для начального угла
            current[1] = 0.5  # Сохраняем Y
            current[2] = -math.cos(rad) * 0.707 - 0.5  # Z изменяется в противоположную сторону
        elif axis == 'y':
            # Поворот по Y: изменяем только y-компоненту в пределах 180 градусов
            current[0] = 0.5  # Сохраняем X
            current[1] = math.sin(rad) * 0.707 + 0.5
            current[2] = -math.cos(rad) * 0.707 - 0.5
        else:  # axis == 'z'
            # Поворот по Z: изменяем x и y, сохраняя z
            current[0] = math.cos(rad) * 0.5  # X вращается вокруг Z
            current[1] = math.sin(rad) * 0.5  # Y вращается вокруг Z
            current[2] = -1  # Z остаётся неизменным

        # Установка нового направления света
        self.scene.set_light_direction(current[0], current[1], current[2])

    def update_display(self, mode):
        # Обновление режима отображения
        self.scene.set_display_mode(mode)
        # Обновление состояния кнопок (выделение активного режима)
        for btn in self.findChildren(QPushButton):
            if btn.text() in [m.value for m in DisplayMode]:
                btn.setChecked(btn.text() == mode.value)

    def update_shading(self, mode):
        # Обновление метода закраски
        self.scene.set_shading_mode(mode)
        # Обновление состояния кнопок (выделение активного метода)
        for btn in self.findChildren(QPushButton):
            if btn.text() in [m.value for m in ShadingMode]:
                btn.setChecked(btn.text() == mode.value)

    def reset_view(self):
        # Сброс всех параметров сцены к начальным значениям
        self.scene.camera_pos = Vector3D(0, 0, -400)  # Начальная позиция камеры
        self.scene.camera_rot = [0, 0, 0]  # Сброс углов поворота камеры
        self.scene.object_transform = Matrix4x4.rotation_z(180)  # Начальное вращение объекта
        self.scene.base_scale = 1.4  # Сброс масштаба
        self.scene.mirror_x = False  # Сброс зеркального отображения по X
        self.scene.mirror_y = False  # Сброс зеркального отображения по Y
        self.scene.mirror_z = False  # Сброс зеркального отображения по Z
        self.scene.set_light_direction(0.5, 0.5, -1)  # Начальное направление света
        self.scene.set_display_mode(DisplayMode.FILLED)  # Начальный режим отображения
        self.scene.set_shading_mode(ShadingMode.PHONG)  # Начальный метод закраски
        self.scene.update()  # Перерисовка сцены

# Точка входа в приложение
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())