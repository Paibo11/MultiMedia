import sys
import math
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QSlider, QLabel, QPushButton, QScrollArea,
                               QSizePolicy, QGroupBox, QButtonGroup)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QPolygonF,
                           QLinearGradient)
from PySide6.QtCore import Qt, QPoint, QPointF
from enum import Enum


class DisplayMode(Enum):
    POINTS = "Точки"
    WIREFRAME = "Каркас"
    FILLED = "Заливка"


class Vector3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __neg__(self):
        return Vector3D(-self.x, -self.y, -self.z)

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
        raise TypeError("Can only multiply Vector3D by scalar")

    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)
        raise TypeError("Can only divide Vector3D by scalar")

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        length = self.length()
        if length == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )


class Matrix4x4:
    def __init__(self):
        self.m = [[0] * 4 for _ in range(4)]
        for i in range(4):
            self.m[i][i] = 1

    def __mul__(self, other):
        if isinstance(other, Vector3D):
            x = self.m[0][0] * other.x + self.m[0][1] * other.y + self.m[0][2] * other.z + self.m[0][3]
            y = self.m[1][0] * other.x + self.m[1][1] * other.y + self.m[1][2] * other.z + self.m[1][3]
            z = self.m[2][0] * other.x + self.m[2][1] * other.y + self.m[2][2] * other.z + self.m[2][3]
            w = self.m[3][0] * other.x + self.m[3][1] * other.y + self.m[3][2] * other.z + self.m[3][3]
            if w != 0:
                return Vector3D(x / w, y / w, z / w)
            return Vector3D(x, y, z)
        elif isinstance(other, Matrix4x4):
            result = Matrix4x4()
            for i in range(4):
                for j in range(4):
                    result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
            return result

    @staticmethod
    def translation(x, y, z):
        m = Matrix4x4()
        m.m[0][3] = x
        m.m[1][3] = y
        m.m[2][3] = z
        return m

    @staticmethod
    def rotation_x(angle):
        m = Matrix4x4()
        rad = math.radians(angle)
        m.m[1][1] = math.cos(rad)
        m.m[1][2] = -math.sin(rad)
        m.m[2][1] = math.sin(rad)
        m.m[2][2] = math.cos(rad)
        return m

    @staticmethod
    def rotation_y(angle):
        m = Matrix4x4()
        rad = math.radians(angle)
        m.m[0][0] = math.cos(rad)
        m.m[0][2] = math.sin(rad)
        m.m[2][0] = -math.sin(rad)
        m.m[2][2] = math.cos(rad)
        return m

    @staticmethod
    def rotation_z(angle):
        m = Matrix4x4()
        rad = math.radians(angle)
        m.m[0][0] = math.cos(rad)
        m.m[0][1] = -math.sin(rad)
        m.m[1][0] = math.sin(rad)
        m.m[1][1] = math.cos(rad)
        return m

    @staticmethod
    def scaling(sx, sy, sz):
        m = Matrix4x4()
        m.m[0][0] = sx
        m.m[1][1] = sy
        m.m[2][2] = sz
        return m


class Face:
    def __init__(self, vertices, color):
        self.vertices = vertices
        self.color = color
        self.normal = self.calculate_normal()
        self.center = self.calculate_center()

    def calculate_normal(self):
        if len(self.vertices) < 3:
            return Vector3D(0, 0, 0)
        v1 = self.vertices[1] - self.vertices[0]
        v2 = self.vertices[2] - self.vertices[0]
        return v1.cross(v2).normalized()

    def calculate_center(self):
        if not self.vertices:
            return Vector3D(0, 0, 0)
        x = sum(v.x for v in self.vertices) / len(self.vertices)
        y = sum(v.y for v in self.vertices) / len(self.vertices)
        z = sum(v.z for v in self.vertices) / len(self.vertices)
        return Vector3D(x, y, z)


class Letter3D:
    def __init__(self, position_x=0, position_y=0, position_z=0, letter_type='X'):
        self.position = Vector3D(position_x, position_y, position_z)
        self.letter_type = letter_type
        self.vertices = []
        self.faces = []
        self.update_geometry()

    def update_geometry(self):
        self.vertices = []
        self.faces = []
        h, w, d = 100, 60, 30  # Фиксированные размеры букв
        bt = h * 0.2  # Толщина элементов буквы

        if self.letter_type == 'X':
            self._create_letter_X(h, w, d, bt)
        elif self.letter_type == 'K':
            self._create_letter_K(h, w, d, bt)

    def _create_letter_X(self, h, w, d, bt):
        hw = w / 2
        hd = d / 2

        # Диагональ из левого верхнего в правый нижний угол
        front_diag1 = [
            Vector3D(-hw, h, -hd), Vector3D(-hw + bt, h, -hd),
            Vector3D(hw, 0, -hd), Vector3D(hw - bt, 0, -hd)
        ]
        back_diag1 = [v + Vector3D(0, 0, d) for v in front_diag1]

        # Диагональ из правого верхнего в левый нижний угол
        front_diag2 = [
            Vector3D(hw, h, -hd), Vector3D(hw - bt, h, -hd),
            Vector3D(-hw, 0, -hd), Vector3D(-hw + bt, 0, -hd)
        ]
        back_diag2 = [v + Vector3D(0, 0, d) for v in front_diag2]

        self.vertices = front_diag1 + back_diag1 + front_diag2 + back_diag2
        colors = [QColor(255, 255, 255)] * 3
        self._create_faces_for_part(front_diag1, back_diag1, colors)
        self._create_faces_for_part(front_diag2, back_diag2, colors)

    def _create_letter_K(self, h, w, d, bt):
        hw = w / 2
        hd = d / 2
        mid = h * 0.5

        # Вертикальная часть
        front_vert = [
            Vector3D(-hw, h, -hd), Vector3D(-hw + bt, h, -hd),
            Vector3D(-hw + bt, 0, -hd), Vector3D(-hw, 0, -hd)
        ]
        back_vert = [v + Vector3D(0, 0, d) for v in front_vert]

        # Верхняя диагональная часть
        front_top = [
            Vector3D(-hw + bt, mid, -hd), Vector3D(hw, h, -hd),
            Vector3D(hw - bt, h, -hd), Vector3D(-hw + bt, mid + bt, -hd)
        ]
        back_top = [v + Vector3D(0, 0, d) for v in front_top]

        # Нижняя диагональная часть
        front_bottom = [
            Vector3D(-hw + bt, mid, -hd), Vector3D(hw, 0, -hd),
            Vector3D(hw - bt, 0, -hd), Vector3D(-hw + bt, mid - bt, -hd)
        ]
        back_bottom = [v + Vector3D(0, 0, d) for v in front_bottom]

        self.vertices = front_vert + back_vert + front_top + back_top + front_bottom + back_bottom
        colors = [QColor(255, 255, 255)] * 3
        self._create_faces_for_part(front_vert, back_vert, colors)
        self._create_faces_for_part(front_top, back_top, colors)
        self._create_faces_for_part(front_bottom, back_bottom, colors)

    def _create_faces_for_part(self, front, back, colors):
        self.faces.append(Face(front, colors[0]))
        self.faces.append(Face(back, colors[0]))

        for i in range(len(front)):
            next_i = (i + 1) % len(front)
            side = [front[i], front[next_i], back[next_i], back[i]]
            self.faces.append(Face(side, colors[1]))

        if len(front) >= 4:
            top = [front[0], front[1], back[1], back[0]]
            bottom = [front[2], front[3], back[3], back[2]]
            self.faces.append(Face(top, colors[2]))
            self.faces.append(Face(bottom, colors[2]))


class SceneWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(150, 150, 150))
        self.setPalette(p)

        self.x_letter = Letter3D(position_x=-60, letter_type='X')
        self.k_letter = Letter3D(position_x=60, letter_type='K')

        self.camera_pos = Vector3D(0, 0, -400)
        self.camera_rot = [0, 0, 0]
        self.object_transform = Matrix4x4()
        self.base_scale = 1.4
        self.light_dir = Vector3D(0.5, -0.5, -1).normalized()  # Изменено направление света для Y вверх
        self.light_pos = self.light_dir * 150

        self.display_mode = DisplayMode.FILLED

        self.setMouseTracking(True)

    def compute_phong_lighting(self, normal, position, face_normal):
        ambient = 0.3
        diffuse = 0.6
        specular = 0.5
        shininess = 32

        light_dir = (self.light_pos - position).normalized()
        to_light = light_dir

        world_normal = (self.object_transform * normal).normalized()
        world_face_normal = (self.object_transform * face_normal).normalized()
        final_normal = (world_normal + world_face_normal).normalized()

        if final_normal.dot(to_light) < 0:
            final_normal = -final_normal

        distance = (self.light_pos - position).length()
        attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * distance * distance)

        diff = max(0, final_normal.dot(light_dir))
        reflect_dir = (light_dir - final_normal * 2 * final_normal.dot(light_dir)).normalized()
        spec = max(0, reflect_dir.dot(to_light)) ** shininess

        intensity = (ambient + diffuse * diff + specular * spec) * attenuation
        return min(1.0, max(0.3, intensity))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(150, 150, 150))

        self.draw_axes(painter)

        all_faces = []
        all_faces.extend(self._prepare_letter_faces(self.x_letter))
        all_faces.extend(self._prepare_letter_faces(self.k_letter))

        all_faces.sort(reverse=True, key=lambda x: x[0])

        for depth, face, screen_points, intensities, positions, normals in all_faces:
            if len(screen_points) < 3:
                continue

            if self.display_mode == DisplayMode.POINTS:
                painter.setPen(QPen(face.color, 5))
                for point in screen_points:
                    if point.x() != -1000 and point.y() != -1000:
                        painter.drawPoint(point)
            elif self.display_mode == DisplayMode.WIREFRAME:
                painter.setPen(QPen(face.color, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawPolygon(QPolygonF(screen_points))
            elif self.display_mode == DisplayMode.FILLED:
                self._draw_filled_face(painter, face, screen_points, intensities, positions, normals)

    def _prepare_letter_faces(self, letter):
        faces = []
        vertices = []
        normals = []

        # Применяем позицию буквы
        translation = Matrix4x4.translation(letter.position.x, letter.position.y, letter.position.z)

        for v in letter.vertices:
            tv = translation * v  # Сначала применяем позицию буквы
            tv = self.object_transform * tv  # Затем общие трансформации сцены
            cv = self.apply_camera_transform(tv)
            vertices.append(cv)

            n = Vector3D(0, 0, 0)
            count = 0
            for face in letter.faces:
                if v in face.vertices:
                    n += face.normal
                    count += 1
            normals.append((n / count).normalized() if count > 0 else Vector3D(0, 0, 1))

        for face in letter.faces:
            fv = [vertices[letter.vertices.index(v)] for v in face.vertices]
            fn = [normals[letter.vertices.index(v)] for v in face.vertices]

            avg_depth = sum(v.z for v in fv) / len(fv)

            screen_points = []
            intensities = []
            positions = []

            for i, v in enumerate(fv):
                if v.z > 0:
                    factor = 300 / v.z
                    ar = self.width() / self.height()
                    px = v.x * factor * self.base_scale * (1 / ar if ar > 1 else 1) + self.width() / 2
                    py = -v.y * factor * self.base_scale * (1 if ar > 1 else ar) + self.height() / 2  # Инвертируем Y
                    screen_points.append(QPointF(px, py))
                    intensities.append(self.compute_phong_lighting(fn[i], v, face.normal))
                    positions.append(v)
                else:
                    screen_points.append(QPointF(-1000, -1000))
                    intensities.append(0)
                    positions.append(Vector3D(0, 0, 0))

            faces.append((avg_depth, face, screen_points, intensities, positions, fn))

        return faces

    def _draw_filled_face(self, painter, face, points, intensities, positions, normals):
        intensity = self.compute_phong_lighting(normals[0], positions[0], face.normal)
        color = QColor(
            min(255, int(face.color.red() * intensity)),
            min(255, int(face.color.green() * intensity)),
            min(255, int(face.color.blue() * intensity))
        )
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygonF(points))

    def draw_axes(self, painter):
        origin = self.project_point(Vector3D(0, 0, 0))
        x_end = self.project_point(Vector3D(150, 0, 0))
        y_end = self.project_point(Vector3D(0, 150, 0))
        z_end = self.project_point(Vector3D(0, 0, 150))

        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(origin, x_end)
        painter.drawText(x_end + QPoint(5, 5), "X")

        painter.setPen(QPen(Qt.green, 2))
        painter.drawLine(origin, y_end)
        painter.drawText(y_end + QPoint(5, 5), "Y")

        painter.setPen(QPen(Qt.blue, 2))
        painter.drawLine(origin, z_end)
        painter.drawText(z_end + QPoint(5, 5), "Z")

    def project_point(self, point):
        v = self.apply_camera_transform(self.object_transform * point)
        if v.z > 0:
            factor = 300 / v.z
            ar = self.width() / self.height()
            px = v.x * factor * self.base_scale * (1 / ar if ar > 1 else 1) + self.width() / 2
            py = -v.y * factor * self.base_scale * (1 if ar > 1 else ar) + self.height() / 2  # Инвертируем Y
            return QPoint(int(px), int(py))
        return QPoint(-1000, -1000)

    def apply_camera_transform(self, v):
        rot_x = Matrix4x4.rotation_x(self.camera_rot[0])
        rot_y = Matrix4x4.rotation_y(self.camera_rot[1])
        rot_z = Matrix4x4.rotation_z(self.camera_rot[2])
        rotation = rot_x * rot_y * rot_z

        translation = Matrix4x4.translation(
            -self.camera_pos.x,
            -self.camera_pos.y,
            -self.camera_pos.z
        )

        return rotation * translation * v

    def set_display_mode(self, mode):
        self.display_mode = mode
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.RightButton and self.last_mouse_pos:
            current = event.position()
            dx = -(current.x() - self.last_mouse_pos.x())
            dy = current.y() - self.last_mouse_pos.y()

            rot_y = Matrix4x4.rotation_y(dx * 0.5)
            rot_x = Matrix4x4.rotation_x(dy * 0.5)

            self.object_transform = rot_y * rot_x * self.object_transform
            self.update()
            self.last_mouse_pos = current

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.last_mouse_pos = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.camera_pos.z += delta * 10
        self.camera_pos.z = max(self.camera_pos.z, -50)
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Буквы XK")
        self.setGeometry(100, 100, 1000, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout(main_widget)
        self.scene = SceneWidget()
        layout.addWidget(self.scene, stretch=3)

        # Панель управления
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)

        # Управление буквами
        self.create_letter_position_controls(control_layout, "Позиция буквы X:", 'x')
        self.create_letter_position_controls(control_layout, "Позиция буквы K:", 'k')

        # Управление трансформациями
        self.create_transform_controls(control_layout)

        # Режимы отображения
        self.create_display_controls(control_layout)

        # Кнопка сброса
        reset_btn = QPushButton("Сбросить вид")
        reset_btn.setMinimumHeight(40)
        reset_btn.clicked.connect(self.reset_view)
        control_layout.addWidget(reset_btn)

        control_layout.addStretch()

        # Добавляем панель управления с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidget(control_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(350)
        layout.addWidget(scroll_area, stretch=1)

    def create_letter_position_controls(self, layout, title, prefix):
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)

        for axis, text in [('x', 'X'), ('y', 'Y'), ('z', 'Z')]:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(-200, 200)
            slider.setValue(getattr(getattr(self.scene, f"{prefix}_letter").position, axis))
            slider.valueChanged.connect(lambda v, p=prefix, a=axis: self.update_letter_position(p, a, v))

            label = QLabel(f"Ось {text}")
            label.setAlignment(Qt.AlignCenter)

            group_layout.addWidget(label)
            group_layout.addWidget(slider)

        layout.addWidget(group)

    def create_transform_controls(self, layout):
        group = QGroupBox("Управление камерой")
        group_layout = QVBoxLayout(group)

        # Вращение
        rot_group = QGroupBox("Вращение")
        rot_layout = QHBoxLayout(rot_group)

        for axis, text in [(0, "X"), (1, "Y"), (2, "Z")]:
            btn_layout = QVBoxLayout()

            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(label)

            btn_plus = QPushButton("+")
            btn_plus.setMinimumSize(50, 30)
            btn_plus.clicked.connect(lambda _, a=axis: self.rotate_object(a, 10))
            btn_layout.addWidget(btn_plus)

            btn_minus = QPushButton("-")
            btn_minus.setMinimumSize(50, 30)
            btn_minus.clicked.connect(lambda _, a=axis: self.rotate_object(a, -10))
            btn_layout.addWidget(btn_minus)

            rot_layout.addLayout(btn_layout)

        group_layout.addWidget(rot_group)

        # Масштаб
        scale_slider = QSlider(Qt.Horizontal)
        scale_slider.setRange(50, 200)
        scale_slider.setValue(100)
        scale_slider.valueChanged.connect(self.scale_object)

        scale_label = QLabel("Масштаб:")
        scale_label.setAlignment(Qt.AlignCenter)

        group_layout.addWidget(scale_label)
        group_layout.addWidget(scale_slider)

        layout.addWidget(group)

    def create_display_controls(self, layout):
        group = QGroupBox("Режим отображения")
        group_layout = QVBoxLayout(group)

        btn_group = QButtonGroup(self)

        for mode in DisplayMode:
            btn = QPushButton(mode.value)
            btn.setCheckable(True)
            btn.setChecked(mode == DisplayMode.FILLED)
            btn.clicked.connect(lambda _, m=mode: self.scene.set_display_mode(m))
            btn_group.addButton(btn)
            group_layout.addWidget(btn)

        layout.addWidget(group)

    def update_letter_position(self, prefix, axis, value):
        letter = getattr(self.scene, f"{prefix}_letter")
        setattr(letter.position, axis, value)
        letter.update_geometry()
        self.scene.update()

    def rotate_object(self, axis, angle):
        if axis == 0:
            rot = Matrix4x4.rotation_x(angle)
        elif axis == 1:
            rot = Matrix4x4.rotation_y(angle)
        else:
            rot = Matrix4x4.rotation_z(angle)

        self.scene.object_transform = rot * self.scene.object_transform
        self.scene.update()

    def scale_object(self, value):
        self.scene.base_scale = value / 100.0
        self.scene.update()

    def reset_view(self):
        self.scene.camera_pos = Vector3D(0, 0, -400)
        self.scene.camera_rot = [0, 0, 0]
        self.scene.object_transform = Matrix4x4()
        self.scene.base_scale = 1.4
        self.scene.light_dir = Vector3D(0.5, -0.5, -1).normalized()
        self.scene.light_pos = self.scene.light_dir * 150
        self.scene.display_mode = DisplayMode.FILLED
        self.scene.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())