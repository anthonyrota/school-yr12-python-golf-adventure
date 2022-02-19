from pyglet import gl
from pyglet.math import Vec2, Mat4
from Rectangle import Rectangle


class Camera:
    def __init__(self, game):
        self._game = game
        self.position = Vec2()
        self.width = 1

    def get_matrix(self):
        height = self.get_height()
        view_matrix = Mat4()
        view_matrix = view_matrix.scale(2 / self.width, 2 / height)
        view_matrix = view_matrix.translate(
            -self.position.x * 2 / self.width - 1,
            -self.position.y * 2 / height - 1,
            0.0,
        )
        return view_matrix

    def update_opengl_matrix(self):
        scale = self.get_scale()
        gl.glScalef(scale, scale, 1)
        gl.glTranslatef(-self.position.x * scale, -self.position.y * scale, 0.0)

    def get_view_rect(self):
        return Rectangle(
            self.position,
            self.width,
            self.get_height(),
        )

    def get_height(self):
        return self.width * self.get_aspect()

    def get_aspect(self):
        return self._game.window.height / self._game.window.width
    
    def get_scale(self):
        return self._game.window.width / self.width
