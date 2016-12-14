'''STRESS TEST FOR ROTABOX
Collisions with animated bounds.
'''

from __future__ import (absolute_import, division, print_function, unicode_literals)
from kivy.config import Config
Config.set('modules', 'monitor', '')
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from rotabox import Rotabox
from random import random
from kivy.clock import Clock
from functools import partial


class Coin(Rotabox):
    def __init__(self, **kwargs):
        super(Coin, self).__init__(**kwargs)
        self.image = Image(source='atlas://images/coins/0')
        self.add_widget(self.image)
        self.custom_bounds = True
        self.bounds = {'0': [[[(0.201, 0.803), (0.092, 0.491),
                               (0.219, 0.184), (0.526, 0.064),
                               (0.83, 0.188), (0.947, 0.491),
                               (0.83, 0.812), (0.531, 0.944)],
                              [1, 3, 5, 7]]],
                       '1': [[[(0.357, 0.902), (0.17, 0.65),
                               (0.184, 0.337), (0.343, 0.095),
                               (0.644, 0.098), (0.813, 0.346),
                               (0.81, 0.709), (0.651, 0.902)],
                              [3, 5, 7, 1]]],
                       '2': [[[(0.402, 0.908), (0.301, 0.725),
                               (0.298, 0.33), (0.415, 0.085),
                               (0.627, 0.098), (0.734, 0.346),
                               (0.73, 0.693), (0.616, 0.905)],
                              [2, 4, 6, 0]]],
                       '3': [[[(0.411, 0.9), (0.364, 0.493),
                               (0.419, 0.095), (0.595, 0.088),
                               (0.644, 0.493), (0.588, 0.908)],
                              [1, 5, 3]]],
                       '4': [[[(0.422, 0.906), (0.426, 0.085),
                               (0.572, 0.085), (0.572, 0.915)],
                              [0, 2]]],
                       '5': [[[(0.422, 0.098), (0.592, 0.098),
                               (0.644, 0.487), (0.568, 0.908),
                               (0.422, 0.915), (0.364, 0.497)],
                              [5, 1, 3]]],
                       '6': [[[(0.395, 0.096), (0.591, 0.093),
                               (0.701, 0.304), (0.709, 0.622),
                               (0.595, 0.904), (0.371, 0.911),
                               (0.262, 0.626), (0.277, 0.293)],
                              [7, 1, 3, 5]]],
                       '7': [[[(0.354, 0.085), (0.612, 0.094),
                               (0.789, 0.312), (0.811, 0.654),
                               (0.617, 0.902), (0.341, 0.897),
                               (0.164, 0.641), (0.187, 0.295)],
                              [6, 0, 2, 4]]],
                       '8': [[[(0.305, 0.103), (0.68, 0.12),
                               (0.87, 0.368), (0.843, 0.748),
                               (0.582, 0.918), (0.296, 0.893),
                               (0.092, 0.671), (0.083, 0.329)],
                              [7, 1, 3, 5]]],
                       '9': [[[(0.291, 0.09), (0.68, 0.115),
                               (0.884, 0.372), (0.893, 0.641),
                               (0.658, 0.889), (0.305, 0.889),
                               (0.051, 0.637), (0.06, 0.325)],
                              [7, 1, 3, 5]]]}
        self.angle_step = random() * 4 - 2
        self.vx = random() * 2 - 1
        self.vy = random() * 2 - 1
        self.nap = random() * .07 + .02
        self.turn()

    def turn(self, frame=0, *args):
        if frame > 9:
            frame = 0
        try:
            self.image.source = 'atlas://images/coins/{}'.format(frame)
        except IndexError:
            return
        else:
            Clock.schedule_once(partial(self.turn, frame + 1), self.nap)

    def run(self, *args):
        if abs(self.vx) > 1:
            self.vx *= .97
        if abs(self.vy) > 1:
            self.vy *= .97
        self.x += self.vx
        self.y += self.vy
        self.angle += self.angle_step


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        for i in xrange(30):
            coin = Coin(size_hint=(None, None), size=(100, 120))
            coin.center = random() * Window.width, random() * Window.height
            self.add_widget(coin)
        Clock.schedule_interval(self.update, .016)

    def update(self, *args):
        children = self.children
        for i in xrange(len(children)):
            child = children[i]
            for j in xrange(i + 1, len(children)):
                child2 = children[j]
                if child.collide_widget(child2) or child2.collide_widget(child):
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
                    child.nap = random() * .07 + .02
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
#


class CrashTestApp(App):
    def build(self):
        return Root()


if __name__ == '__main__':
    CrashTestApp().run()                                                                                                                                                                                                                                                                                                                              