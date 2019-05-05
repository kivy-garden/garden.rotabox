from kivy.base import runTouchApp
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder
import os, sys
sys.path.append(os.path.abspath(".."))

Builder.load_string('''
#:import Rotabox rotabox.Rotabox

<Root>:
    trap: trap
    logo: logo
    Rotabox:
        id: trap
        size: 320, 320
        center: 400, 300
        open_bounds: [0]
        draw_bounds: 1
    Rotabox:
        id: logo
        size: 200, 132
        center: 800, 300
        custom_bounds:
            [[(0.013, 0.985), (0.016, 0.407), (0.202, 0.696)],
            [(0.267, 0.346), (0.483, -0.005), (0.691, 0.316), (0.261, 0.975)],
            [(0.539, 0.674), (0.73, 0.37), (0.983, 0.758)],
            [(0.033, 0.315), (0.212, 0.598), (0.218, 0.028)]]
        draw_bounds: 1
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
