from kivy.base import runTouchApp
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder
import os, sys
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox

Builder.load_string('''
<Root>:
    blue: blue
    red: red
    Rotabox:
        id: blue
        size: 320, 320
        pivot: 500, 300
        custom_bounds:
            [[(0.223, 0.68), (0.223, 0.404), (0.353, 0.28)],
            [(0.402, 0.391), (0.528, 0.262), (0.855, 0.587), (0.519, 0.552),
            (0.384, 0.684)]]
        open_bounds: [0, 1]
        draw_bounds: True
        Image:
            source: 'data/logo/kivy-icon-256.png'
            color: .2, .2, .7, 1
    Rotabox:
        id: red
        size: 200, 132
        pivot: 800, 300
        custom_bounds:
            [[(0.016, 0.977), (0.016, 0.343), (0.214, 0.029)],
            [(0.264, 0.974), (0.262, 0.338), (0.483, -0.002), (0.986, 0.752)]]
        open_bounds: [0, 1]
        draw_bounds: True
        Image:
            source: 'kivy.png'
            color: .5, 0, .2, 1
''')


class Root(Widget):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)
        self.blue.draw_color.rgba = 1, 1, 1, 1
        self.red.draw_color.rgba = 1, 1, 1, 1

    def update(self, *args):
        this = self.blue
        that = self.red
        if this.collide_widget(that):
            that.x += .5
            this.angle += .5
            this.x -= 1
        else:
            that.x -= .5
            that.angle -= .6


runTouchApp(Root())
