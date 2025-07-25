class Vector2i:
    def __init__(self, x=0, y=0):
        self.x = int(x)
        self.y = int(y) if y is not None else int(x)

    def copy(self):
        return Vector2i(self.x, self.y)

    def __eq__(self, other):
        return isinstance(other, Vector2i) and self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Vector2i({self.x}, {self.y})"

    def __add__(self, other):
        if isinstance(other, Vector2i):
            return Vector2i(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector2i):
            return Vector2i(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector2i(int(self.x * other), int(self.y * other))
        if isinstance(other, Vector2i):
            return Vector2i(self.x * other.x, self.y * other.y)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Vector2i(int(self.x / other), int(self.y / other))
        if isinstance(other, Vector2i):
            return Vector2i(int(self.x / other.x), int(self.y / other.y))
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            return Vector2i(self.x // other, self.y // other)
        if isinstance(other, Vector2i):
            return Vector2i(self.x // other.x, self.y // other.y)
        return NotImplemented

    def __neg__(self):
        return Vector2i(-self.x, -self.y)

    def __abs__(self):
        return Vector2i(abs(self.x), abs(self.y))

    def __hash__(self):
        return hash((self.x, self.y))

    def __iter__(self):
        yield self.x
        yield self.y

    def dot(self, other):
        """Скалярное произведение"""
        return self.x * other.x + self.y * other.y

    def sign(self):
        """Возвращает вектор с знаками компонентов (-1, 0, 1)"""
        return Vector2i(
            -1 if self.x < 0 else 1 if self.x > 0 else 0,
            -1 if self.y < 0 else 1 if self.y > 0 else 0
        )

    def length(self):
        """Длина вектора"""
        return (self.x**2 + self.y**2)**0.5

    def length_squared(self):
        """Квадрат длины вектора (для оптимизации)"""
        return self.x**2 + self.y**2

    def distance_to(self, other):
        """Расстояние до другого вектора"""
        return (self - other).length()

    def normalized(self):
        """Нормализованный вектор"""
        length = self.length()
        if length == 0:
            return Vector2i(0, 0)
        return Vector2i(int(self.x / length), int(self.y / length))

    def snapped(self, step):
        """Округление компонентов до шага"""
        return Vector2i(
            int(round(self.x / step.x) * step.x) if step.x != 0 else self.x,
            int(round(self.y / step.y) * step.y) if step.y != 0 else self.y
        )

    def clamp(self, min_val, max_val):
        """Ограничение значений компонентов"""
        if isinstance(min_val, Vector2i) and isinstance(max_val, Vector2i):
            return Vector2i(
                max(min_val.x, min(max_val.x, self.x)),
                max(min_val.y, min(max_val.y, self.y))
            )
        elif isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
            return Vector2i(
                max(min_val, min(max_val, self.x)),
                max(min_val, min(max_val, self.y))
            )
        return NotImplemented

    @classmethod
    def from_tuple(cls, tuple_val):
        """Создание из кортежа"""
        return cls(tuple_val[0], tuple_val[1])

    def to_tuple(self):
        """Преобразование в кортеж"""
        return (self.x, self.y)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector2i index out of range")
