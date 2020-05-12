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
<Ramp@BoxLayout>:
    size_hint: None, None
    canvas:
        Color:
            rgb: 0.682, 0.251, 0.98
        Rectangle:
            pos: self.pos
            size: self.size

<Root>:
    slotleft: slotleft
    slotright: slotright
    Ramp:
        id: slotleft
        size: 450, 6
        pos: -50, 120
    Ramp:
        id: slotright
        size: 450, 6
        pos: 430, 120
'''))


class Coin(Rotabox):
    def __init__(self, **kwargs):
        super(Coin, self).__init__(**kwargs)
        self.image = Image(source='atlas://coins/0')
        self.add_widget(self.image)
        self.speed = random() * .3 + 1.5
        self.custom_bounds = self.read_bounds('coins.bounds')
        # self.draw_bounds = 1
        self.turn()

    def turn(self, frame=0, *args):
        if frame > 9:
            frame = 0
        try:
            self.image.source = 'atlas://coins/{}'.format(frame)
        except IndexError:
            return
        else:
            Clock.schedule_once(partial(self.turn, frame + 1), .15)


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.coins = []
        self.lastTime = time.clock()
        Clock.schedule_interval(self.update, .016)

    def update(self, *args):
        if time.clock() - self.lastTime > 1:
            self.coins.append(Coin(pos=(self.width * -.1, self.height * .2)))
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


if __name__ == '__main__':
    runTouchApp(Root())
