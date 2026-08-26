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

from direct.gui.DirectWaitBar import DirectWaitBar


class SpinnerDots(DirectFrame):

    """Loading spinner
        Arges:
            dot_color (tuple): The color of the sprites; (RGBA); specify within the range of 0 to 1.
            shaded (Bool): If True, shaded circular sprites are created; default is True.
            radius (float): The radius of the circle around which the sprites rotate; default is 0.15.
            scale (float): The scale of the sprites; default is 0.03.
            duration (float): Seconds for a sprite to complete one rotation; default is 3.0 seconds.
    """

    def __init__(self, dot_color=None, dot_cnt=6, shaded=True, radius=0.15, scale=0.03, duration=3.0):
        super().__init__()
        self.initialiseoptions(type(self))

        tex = self.create_dot_texture(shaded, dot_color)
        self.sprites = [Sprite(self, tex, i, radius, scale, duration) for i in range(dot_cnt)]

    def create_dot_texture(self, shaded, dot_color):
        color = (1., 0., 0., 1.) if dot_color is None else dot_color
        *rgb, a = color
        bgr = np.array(rgb)[[2, 1, 0]]

        img_size = 64
        img = self.create_shaded_dot_img(img_size, bgr, a) if shaded \
            else self.create_dot_img(img_size, bgr, a)

        tex = Texture('image')
        tex.setup_2d_texture(
            x_size=img_size,
            y_size=img_size,
            component_type=Texture.T_unsigned_byte,
            format=Texture.F_rgba
        )
        tex.set_ram_image(img)
        return tex

    def calc_center_and_radius(self, size):
        center = size // 2
        radius = size / 2 - 2
        return center, radius

    def create_dot_img(self, size, bgr, a):
        center, radius = self.calc_center_and_radius(size)

        # Create a coordinate grid and calculate the distance from the center.
        y, x = np.ogrid[:size, :size]
        dist = np.sqrt((x - center) ** 2 + (y - center) ** 2)

        # Create an alpha mask for anti-aliasing.
        blur_width = 1.0
        alpha = np.clip((radius - dist) / blur_width + 0.5, 0, a) * 255
        alpha = alpha.astype(np.uint8)

        # Create a BGR image and combine it with the alpha channel to convert it to a BGRA image.
        img = np.full((size, size, 3), bgr * 255, dtype=np.uint8)
        img = np.dstack((img, alpha))

        return img

    def create_shaded_dot_img(self, size, bgr, a):
        center, radius = self.calc_center_and_radius(size)

        y, x = np.ogrid[:size, :size]
        dist = np.sqrt((x - center) ** 2 + (y - center) ** 2)

        # Create mask
        mask = dist <= radius

        # Calculating the spherical normal vector.
        # Use np.maximum in case the calculation result becomes slightly less than 0 due to rounding error.
        nx = (x - center) / radius
        ny = (y - center) / radius
        nz = np.sqrt(np.maximum(0.0, 1.0 - nx ** 2 - ny ** 2))

        # Light source vector (from the top left)
        lx, ly, lz = -0.8, 0.8, 1.0
        l_len = np.sqrt(lx ** 2 + ly ** 2 + lz ** 2)
        lx, ly, lz = lx / l_len, ly / l_len, lz / l_len

        # Calculate Shading.
        diffuse = np.maximum(0.0, nx * lx + ny * ly + nz * lz)
        shading = diffuse[:, :, np.newaxis] * (bgr * 255) + 40
        shading = np.clip(shading, 0, 255)

        # Create bgra image.
        bgra = np.zeros((size, size, 4), dtype=np.uint8)
        bgra[mask, :3] = shading[mask].astype(np.uint8)

        # Anti-aliasing
        alpha = np.clip((radius - dist) * 2.0 + 0.5, 0, a)
        bgra[:, :, 3] = (alpha * 255).astype(np.uint8)
        bgra[:, :, 3] = np.where(mask, bgra[:, :, 3], 0)
        return bgra

    def update(self):
        dt = globalClock.get_dt()

        for sprite in self.sprites:
            sprite.update(dt)
            # sprite.update()

    def finish(self):
        for sprite in self.sprites:
            sprite.finish()


class Sprite(OnscreenImage):

    # def __init__(self, parent, image, starting_order, radius=0.15, scale=0.03, duration=3.0):
    def __init__(self, parent, image, starting_order, radius, scale, duration):
        super().__init__(
            image=image,
            # parent=base.aspect2d,
            parent=parent,
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