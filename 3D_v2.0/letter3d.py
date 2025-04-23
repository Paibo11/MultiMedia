from math_utils import Vector3D
from face import Face
from PySide6.QtGui import QColor


class Letter3D:
    def __init__(self, height, width, depth, offset_x=0, letter_type='X'):
        self.height = height
        self.width = width
        self.depth = depth
        self.offset_x = offset_x
        self.letter_type = letter_type
        self.vertices = []
        self.faces = []
        self.update_geometry()

    def update_geometry(self):
        self.vertices = []
        self.faces = []
        h, w, d, ox = self.height, self.width, self.depth, self.offset_x
        bar_thickness = h * 0.2

        if self.letter_type == 'X':
            self._create_letter_X(h, w, d, ox, bar_thickness)
        else:
            self._create_letter_K(h, w, d, ox, bar_thickness)

    def _create_letter_X(self, h, w, d, ox, bar_thickness):
        hw = w / 2
        hd = d / 2
        bt = bar_thickness

        # Diagonal from top-left to bottom-right
        front_diag1 = [
            Vector3D(ox - hw, h, -hd), Vector3D(ox - hw + bt, h, -hd),
            Vector3D(ox + hw - bt, 0, -hd), Vector3D(ox + hw, 0, -hd)
        ]
        back_diag1 = [
            Vector3D(ox - hw, h, hd), Vector3D(ox - hw + bt, h, hd),
            Vector3D(ox + hw - bt, 0, hd), Vector3D(ox + hw, 0, hd)
        ]

        # Diagonal from top-right to bottom-left
        front_diag2 = [
            Vector3D(ox + hw, h, -hd), Vector3D(ox + hw - bt, h, -hd),
            Vector3D(ox - hw + bt, 0, -hd), Vector3D(ox - hw, 0, -hd)
        ]
        back_diag2 = [
            Vector3D(ox + hw, h, hd), Vector3D(ox + hw - bt, h, hd),
            Vector3D(ox - hw + bt, 0, hd), Vector3D(ox - hw, 0, hd)
        ]

        self.vertices = front_diag1 + back_diag1 + front_diag2 + back_diag2
        colors = [QColor(255, 255, 255), QColor(255, 255, 255), QColor(255, 255, 255)]
        self._create_faces_for_part(front_diag1, back_diag1, colors)
        self._create_faces_for_part(front_diag2, back_diag2, colors)

    def _create_letter_K(self, h, w, d, ox, bar_thickness):
        hw = w / 2
        hd = d / 2
        bt = bar_thickness
        mid_height = h * 0.5  # Where the diagonal part starts

        # Vertical part
        front_vert = [
            Vector3D(ox - hw, h, -hd), Vector3D(ox - hw + bt, h, -hd),
            Vector3D(ox - hw + bt, 0, -hd), Vector3D(ox - hw, 0, -hd)
        ]
        back_vert = [
            Vector3D(ox - hw, h, hd), Vector3D(ox - hw + bt, h, hd),
            Vector3D(ox - hw + bt, 0, hd), Vector3D(ox - hw, 0, hd)
        ]

        # Top diagonal part (from middle to top-right)
        front_top_diag = [
            Vector3D(ox - hw + bt, mid_height, -hd), Vector3D(ox + hw, h, -hd),
            Vector3D(ox + hw - bt, h, -hd), Vector3D(ox - hw + bt, mid_height + bt, -hd)
        ]
        back_top_diag = [
            Vector3D(ox - hw + bt, mid_height, hd), Vector3D(ox + hw, h, hd),
            Vector3D(ox + hw - bt, h, hd), Vector3D(ox - hw + bt, mid_height + bt, hd)
        ]

        # Bottom diagonal part (from middle to bottom-right)
        front_bottom_diag = [
            Vector3D(ox - hw + bt, mid_height, -hd), Vector3D(ox + hw, 0, -hd),
            Vector3D(ox + hw - bt, 0, -hd), Vector3D(ox - hw + bt, mid_height - bt - 2, -hd)
        ]
        back_bottom_diag = [
            Vector3D(ox - hw + bt, mid_height, hd), Vector3D(ox + hw, 0, hd),
            Vector3D(ox + hw - bt, 0, hd), Vector3D(ox - hw + bt, mid_height - bt - 2, hd)
        ]

        self.vertices = (front_vert + back_vert +
                         front_top_diag + back_top_diag +
                         front_bottom_diag + back_bottom_diag)

        colors = [QColor(255, 255, 255), QColor(255, 255, 255), QColor(255, 255, 255)]
        self._create_faces_for_part(front_vert, back_vert, colors)
        self._create_faces_for_part(front_top_diag, back_top_diag, colors)
        self._create_faces_for_part(front_bottom_diag, back_bottom_diag, colors)

    def _create_faces_for_part(self, front_vertices, back_vertices, colors):
        self.faces.append(Face(front_vertices, colors[0]))
        self.faces.append(Face(back_vertices, colors[0]))
        for i in range(len(front_vertices)):
            next_i = (i + 1) % len(front_vertices)
            side_face = [
                front_vertices[i],
                front_vertices[next_i],
                back_vertices[next_i],
                back_vertices[i]
            ]
            self.faces.append(Face(side_face, colors[1]))
        if len(front_vertices) >= 4:
            top_face = [front_vertices[0], front_vertices[1], back_vertices[1], back_vertices[0]]
            bottom_face = [front_vertices[2], front_vertices[3], back_vertices[3], back_vertices[2]]
            self.faces.append(Face(top_face, colors[2]))
            self.faces.append(Face(bottom_face, colors[2]))