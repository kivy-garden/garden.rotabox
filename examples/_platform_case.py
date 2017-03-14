# coin spritesheet borrowed from:
# http://www.williammalone.com/articles/html5-animation-sprite-sheet-photoshop/

from kivy.base import runTouchApp
from functools import partial
from random import random
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.clock import Clock
import time
import sys, os
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox

Builder.load_string(str('''
<Root>:
    slotleft: slotleft
    slotright: slotright
    BoxLayout:
        id: slotleft
        size_hint: None, None
        size: root.width * .6, root.height * .01
        pos: 0, root.height * .2
        canvas:
            Color:
                rgb: 0.682, 0.251, 0.98
            Rectangle:
                pos: self.pos
                size: self.size
    BoxLayout:
        id: slotright
        size_hint: None, None
        size: root.width * .4, root.height * .01
        pos: root.width * .625, root.height * .2
        canvas:
            Color:
                rgb: 0.682, 0.251, 0.98
            Rectangle:
                pos: self.pos
                size: self.size
'''))


class Coin(Rotabox):
    def __init__(self, **kwargs):
        super(Coin, self).__init__(**kwargs)
        self.add_widget(Image(source='atlas://coins/0'))
        self.custom_bounds = {'0': [[(0.201, 0.803), (0.092, 0.491),
                               (0.219, 0.184), (0.526, 0.064),
                               (0.83, 0.188), (0.947, 0.491),
                               (0.83, 0.812), (0.531, 0.944)]],
                           '1': [[(0.357, 0.902), (0.17, 0.65),
                                   (0.184, 0.337), (0.343, 0.095),
                                   (0.644, 0.098), (0.813, 0.346),
                                   (0.81, 0.709), (0.651, 0.902)]],
                           '2': [[(0.402, 0.908), (0.301, 0.725),
                                   (0.298, 0.33), (0.415, 0.085),
                                   (0.627, 0.098), (0.734, 0.346),
                                   (0.73, 0.693), (0.616, 0.905)]],
                           '3': [[(0.411, 0.9), (0.364, 0.493),
                                   (0.419, 0.095), (0.595, 0.088),
                                   (0.644, 0.493), (0.588, 0.908)]],
                           '4': [[(0.422, 0.906), (0.426, 0.085),
                                   (0.572, 0.085), (0.572, 0.915)]],
                           '5': [[(0.422, 0.098), (0.592, 0.098),
                                   (0.644, 0.487), (0.568, 0.908),
                                   (0.422, 0.915), (0.364, 0.497)]],
                           '6': [[(0.395, 0.096), (0.591, 0.093),
                                   (0.701, 0.304), (0.709, 0.622),
                                   (0.595, 0.904), (0.371, 0.911),
                                   (0.262, 0.626), (0.277, 0.293)]],
                           '7': [[(0.354, 0.085), (0.612, 0.094),
                                   (0.789, 0.312), (0.811, 0.654),
                                   (0.617, 0.902), (0.341, 0.897),
                                   (0.164, 0.641), (0.187, 0.295)]],
                           '8': [[(0.305, 0.103), (0.68, 0.12),
                                   (0.87, 0.368), (0.843, 0.748),
                                   (0.582, 0.918), (0.296, 0.893),
                                   (0.092, 0.671), (0.083, 0.329)]],
                           '9': [[(0.291, 0.09), (0.68, 0.115),
                                   (0.884, 0.372), (0.893, 0.641),
                                   (0.658, 0.889), (0.305, 0.889),
                                   (0.051, 0.637), (0.06, 0.325)]]}
        self.speed = random() * .3 + 1.5
        self.bind(ready=self.turn)

    def turn(self, frame=0, *args):
        if frame > 9:
            frame = 0
        try:
            self.image.source = 'atlas://coins/{}'.format(frame)
        except IndexError:
            return
        Clock.schedule_once(partial(self.turn, frame + 1), .15)


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.coins = []
        self.lastTime = time.clock()
        Clock.schedule_interval(self.update, .016)

    def update(self, *args):
        if time.clock() - self.lastTime > 1:
            self.coins.append(Coin(scale=.7,
                                   pos=(self.width * .01, self.height * .2)))
            self.add_widget(self.coins[-1])
            self.lastTime = time.clock()

        for coin in self.coins:
            if coin.x > self.width * 1.1 or coin.y < self.height * -.1:
                self.remove_widget(self.coins.pop(self.coins.index(coin)))
            if (coin.collide_widget(self.slotleft)
                    or coin.collide_widget(self.slotright)):
                if self.slotleft.top > coin.center_y:
                    coin.y -= coin.speed
                    continue
                coin.x += coin.speed
                if coin.y < self.height * .19:
                    coin.y += 1
            else:
                coin.y -= coin.speed


runTouchApp(Root())
