from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
import os, sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))  # Sets the current dir to the program's dir.
sys.path.append(os.path.abspath(".."))

Builder.load_string('''
#:import Rotabox rotabox.Rotabox

<LogoBox@Rotabox>:
    custom_bounds:
        [[(0.02, 0.977), (0.018, 0.335), (0.212, 0.042), (0.217, 0.408), 
        (0.48, -0.004), (0.988, 0.758), (0.458, 0.665), (0.26, 0.988), 
        (0.268, 0.585)]]
    Image:
        source: 'kivy.png'

<Root>:
    Label:
        pos: root.width * .35, root.height * .85
        text: 'Click to change the point of rotation.'
    LogoBox:
        id: logo
        pivot: root.center
    Widget:
        id: red
        color: 1, .3, .3, 1
        size: 10, 10
        canvas:
            Color:
                rgba: self.color
            Ellipse:
                pos: self.pos
                size: self.size
''')


class Root(Widget):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.idx = 0
        Clock.schedule_interval(self.update, 1/60.)

    def update(self, *args):
        self.ids.logo.angle -= .5
        self.ids.red.center = self.ids.logo.origin

    def on_touch_down(self, touch):
        idx = self.idx
        if idx > 8:
            idx = 0
        self.ids.logo.origin = self.ids.logo.get_point(0, idx)
        self.idx = idx + 1


runTouchApp(Root())
