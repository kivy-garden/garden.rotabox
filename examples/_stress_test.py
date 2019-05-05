# coding=utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)
from kivy.config import Config
from kivy.graphics.context_instructions import PushMatrix, Rotate, PopMatrix

Config.set('modules', 'monitor', '')
from kivy.base import runTouchApp
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from random import random
from kivy.clock import Clock
import sys, os
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox


class RotaChild(Rotabox):
    def __init__(self, **kwargs):
        super(RotaChild, self).__init__(**kwargs)
        self.image = Image(source='kivy.png')
        self.add_widget(self.image)
        self.custom_bounds = [[(0.013, 0.985), (0.016, 0.407), (0.202, 0.696)],
                             [(0.033, 0.315), (0.212, 0.598), (0.218, 0.028)],
                             [(0.267, 0.346), (0.483, 0.000), (0.691, 0.316),
                              (0.261, 0.975)],
                             [(0.539, 0.674), (0.73, 0.37), (0.983, 0.758)]]
        self.angle_step = random() * 4 - 2
        self.vx = random() * 2 - 1
        self.vy = random() * 2 - 1

    def run(self, *args):
        if abs(self.vx) > 1:
            self.vx *= .97
        if abs(self.vy) > 1:
            self.vy *= .97
        self.x += self.vx
        self.y += self.vy
        self.angle += self.angle_step

    def change(self):
        self.image.color = [random() for _ in range(3)] + [1]


class ImgChild(Image):
    def __init__(self, **kwargs):
        super(ImgChild, self).__init__(**kwargs)
        self.source = 'kivy.png'
        self.size_hint=(None, None)
        self.angle = 0
        self.origin = self.center
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=self.angle,
                                   axis=(0, 0, 1),
                                   origin=self.origin)
        with self.canvas.after:
            PopMatrix()
        self.angle_step = random() * 4 - 2
        self.vx = random() * 2 - 1
        self.vy = random() * 2 - 1

    def run(self, *args):
        if abs(self.vx) > 1:
            self.vx *= .97
        if abs(self.vy) > 1:
            self.vy *= .97
        self.x += self.vx
        self.y += self.vy
        self.angle += self.angle_step
        self.rotation.origin = self.origin
        self.rotation.angle = self.angle

    def change(self):
        self.color = [random() for _ in range(3)] + [1]


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.kids = []
        for i in xrange(90):
            child = RotaChild()
            # child = ImgChild()
            child.size = 40, 26
            child.center = random() * Window.width, random() * Window.height
            self.add_widget(child)
            self.kids.append(child)
        Clock.schedule_interval(self.update, 1/60)

    def update(self, *args):
        kids = self.kids
        for i in xrange(len(kids)):
            child = kids[i]
            for j in xrange(i + 1, len(kids)):
                child2 = kids[j]
                if child.collide_widget(child2):  # or child2.collide_widget(child):
                    self.bounce(child, child2)
                    child.angle_step = random() * 4 - 2
            if self.x > child.x:
                child.vx *= -1
            if self.right < child.right:
                child.vx *= -1
            if self.y > child.y:
                child.vy *= -1
            if self.top < child.top:
                child.vy *= -1
            child.run()

    def bounce(self, child, child2):
        child.change()
        child2.change()
        dx = child2.x - child.x
        dy = child2.y - child.y
        dist = (dx * dx + dy * dy) ** .5
        contact_point_x = child.x + float(dx) / dist * (dist + 1)
        contact_point_y = child.y + float(dy) / dist * (dist + 1)
        deflection_x = (contact_point_x - child2.x)
        deflection_y = (contact_point_y - child2.y)
        child.vx -= deflection_x * .5
        child.vy -= deflection_y * .5
        child2.vx += deflection_x * .5
        child2.vy += deflection_y * .5


if __name__ == '__main__':
    runTouchApp(Root())