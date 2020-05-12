from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.base import runTouchApp
from kivy.lang import Builder
import sys, os
sys.path.append(os.path.abspath(".."))

Builder.load_string('''
#:import Rotabox rotabox.Rotabox

<Root>:
    red: red
    circle: circle
    Rotabox:
        id: red
        size: 200, 132
        pivot: 400, 300
        custom_bounds:
            [[(0.013, 0.985), (0.016, 0.407), (0.202, 0.696)],
            [(0.267, 0.346), (0.483, -0.005), (0.691, 0.316), (0.261, 0.975)],
            [(0.539, 0.674), (0.73, 0.37), (0.983, 0.758)],
            [(0.033, 0.315), (0.212, 0.598), (0.218, 0.028)]]
        draw_bounds: 1
    Widget:
        id: circle
        canvas:
            Color:
                rgba: 1, .5, 0, 1
            Line:
                circle: (self.center_x, self.center_y, 30, 0, 270)
 ''')


class Root(Widget):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)

    def update(self, *args):
        self.red.angle -= .6
        self.circle.center = self.red.get_point(2, 2)

if __name__ == '__main__':
    runTouchApp(Root())
