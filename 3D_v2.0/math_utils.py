import math

class Vector3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        length = self.length()
        if length == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

class Matrix4x4:
    def __init__(self):
        self.m = [[0] * 4 for _ in range(4)]
        self.m[0][0] = 1
        self.m[1][1] = 1
        self.m[2][2] = 1
        self.m[3][3] = 1

    def __mul__(self, other):
        if isinstance(other, Vector3D):
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
            result = Matrix4x4()
            for i in range(4):
                for j in range(4):
                    result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
            return result

    @staticmethod
    def translation(x, y, z):
        mat = Matrix4x4()
        mat.m[0][3] = x
        mat.m[1][3] = y
        mat.m[2][3] = z
        return mat

    @staticmethod
    def rotation_x(angle):
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[1][1] = math.cos(rad)
        mat.m[1][2] = -math.sin(rad)
        mat.m[2][1] = math.sin(rad)
        mat.m[2][2] = math.cos(rad)
        return mat

    @staticmethod
    def rotation_y(angle):
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[0][0] = math.cos(rad)
        mat.m[0][2] = math.sin(rad)
        mat.m[2][0] = -math.sin(rad)
        mat.m[2][2] = math.cos(rad)
        return mat

    @staticmethod
    def rotation_z(angle):
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[0][0] = math.cos(rad)
        mat.m[0][1] = -math.sin(rad)
        mat.m[1][0] = math.sin(rad)
        mat.m[1][1] = math.cos(rad)
        return mat

    @staticmethod
    def scaling(sx, sy, sz):
        mat = Matrix4x4()
        mat.m[0][0] = sx
        mat.m[1][1] = sy
        mat.m[2][2] = sz
        return mat 