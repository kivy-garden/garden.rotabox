from kivy.base import runTouchApp
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder
import os, sys
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox

Builder.load_string('''
<Root>:
    trap: trap
    logo: logo
    Rotabox:
        id: trap
        size: 320, 320
        center: 500, 300
        open_bounds: [0]
        draw_bounds: True
    Rotabox:
        id: logo
        size: 200, 132
        center: 800, 300
        custom_bounds:
            [[(0.018, 0.335), (0.212, 0.042), (0.217, 0.408),
            (0.48, -0.004), (0.988, 0.758), (0.458, 0.665), (0.26, 0.988),
            (0.268, 0.585), (0.02, 0.977)]]
        Image:
            source: 'kivy.png'
''')


class Root(Widget):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)

    def update(self, *args):
        this = self.trap
        that = self.logo
        if this.collide_widget(that):
            this.x -= 1
            this.angle += .3
            that.x += .5
        else:
            this.x += .5
            this.angle -= .3
            that.x -= .5
            that.angle -= .6

if __name__ == '__main__':
    runTouchApp(Root())
