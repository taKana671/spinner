import math
import sys

import numpy as np

from direct.gui.DirectGui import DirectFrame
import direct.gui.DirectGuiGlobals as DGG
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import OnscreenImage
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import TransparencyAttrib, AntialiasAttrib
from panda3d.core import Point3, Vec3
from panda3d.core import Texture

from example2 import create_shaded_image
from example import create_normal_dot



from direct.gui.DirectWaitBar import DirectWaitBar


class SpinnerDots(DirectFrame):

    def __init__(self, parent=None, shaded=True, **kw):
        super().__init__(parent, **kw)

        self.initialiseoptions(type(self))
        self.set_transparency(TransparencyAttrib.MAlpha)

        tex = Texture('image')
        tex.setup_2d_texture(
            # 200, 200,
            64, 64,
            Texture.T_unsigned_byte,
            Texture.F_rgba
        )
        # img = create_shaded_image()
        img = create_normal_dot()
        tex.set_ram_image(img)

        # self.sprites = [Sprite('transparent_circle.png', i) for i in range(6)]
        # self.sprites = [Sprite('shaded_sphere.png', i) for i in range(6)]
        self.sprites = [Sprite(tex, i) for i in range(6)]

    def calc_center_and_radius(self, size):
        center = size // 2
        radius = size / 2 - 2
        return center, radius

    def create_texture(self, shaded, color):
        size = 64

        img = self.create_shaded_dot(size, color) if shaded \
            else self.create_normal_dot(size, color)

        tex = Texture('image')
        tex.setup_2d_texture(
            x_size=size,
            y_size=size,
            component_type=Texture.T_unsigned_byte,
            format=Texture.F_rgba
        )
        tex.set_ram_image(img)
        return tex

    def create_normal_dot(self, size, color):
        center, radius = self.calc_center_and_radius(size)

        # Create a coordinate grid and calculate the distance from the center.
        y, x = np.ogrid[:size, :size]
        dist = np.sqrt((x - center) ** 2 + (y - center) ** 2)

        # Create an alpha mask for anti-aliasing.
        blur_width = 1.0
        alpha = np.clip((radius - dist) / blur_width + 0.5, 0, 1) * 255

        # Create a BGR image and combine it with the alpha channel to convert it to a BGRA image.
        img = np.full((size, size, 3), color, dtype=np.uint8)
        img = np.dstack((img, alpha))
        return img

    def create_shaded_dot(self):
        pass


    def update(self):
        dt = globalClock.get_dt()

        for sprite in self.sprites:
            sprite.update(dt)
            # sprite.update()

    def finish(self):
        for sprite in self.sprites:
            sprite.finish()


class Sprite(OnscreenImage):

    def __init__(self, image, starting_order, radius=0.15, scale=0.03, duration=3.0):
        super().__init__(
            image=image,
            parent=base.aspect2d,
            pos=Point3(radius, 0, 0),
            scale=(scale, 1, scale)
        )
        self.hide()
        self.set_name(f'circle_{starting_order}')
        self.set_transparency(TransparencyAttrib.M_alpha)

        self.radius = radius
        self.duration = duration
        self.elapsed = 0.0
        self.delay = starting_order * 0.15
        self.is_started = False

    def in_out_quart(self, x):
        # Clamp x so that it does not go outside the range of 0.0 to 1.0 by a small margin.
        if (x := max(0.0, min(x, 1.0))) < 0.5:
            return 8 * math.pow(x, 4)

        return 1 - math.pow(-2 * x + 2, 4) / 2

    def update(self, dt):


        dt = globalClock.get_dt()

        self.elapsed += dt
        current_time = self.elapsed - self.delay

        if not self.is_started:
            if current_time >= 0.0:
                self.show()
                self.is_started = True

        # Even if current_time continues to increase indefinitely, ensure that loop_time
        # is in the range of the remainder (0.0 to 3.0 seconds) when divided by self.duration.
        loop_time = current_time % self.duration
        # Divide loop_time (0.0–3.0) by self.duration(3.0), which is the total duration, 
        # to set the argument passed to the function to a value between 0 and 1.
        step = loop_time / self.duration

        eased_t = self.in_out_quart(step)
        theta = 2 * math.pi * eased_t
        x = self.radius * math.sin(theta)
        y = self.radius * math.cos(theta)
        self.set_pos(Point3(x, 0, y))

    def finish(self):
        self.hide()
        self.destroy()



class SpinnerDemo(ShowBase):

    def __init__(self):
        super().__init__()
        self.disable_mouse
        self.render.set_antialias(AntialiasAttrib.M_auto)
        self.camera.set_pos(20, -30, 5)
        self.camera.look_at(0, 0, 0)

        # self.sprites = [Sprite('circle.png', i) for i in range(6)]
        self.spinner = SpinnerDots()
        self.accept('escape', sys.exit)
        self.task_mgr.add(self.update, 'update')

    def update(self, task):
        dt = globalClock.get_dt()

        self.spinner.update()
        # for sprite in self.sprites:
        #     sprite.update(dt)
            # sprite.update()

        return task.cont


if __name__ == '__main__':
    spinner = SpinnerDemo()
    spinner.run()