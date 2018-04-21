from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from rotabox import Rotabox

Builder.load_string('''
<Root>:
    canvas:
        Color:
            rgba: [.1, .1, .1, 1]
        Line:
            points: [self.width * .5, 0, self.width * .5, self.height]
        Line:
            points: [0, self.height * .5, self.width, self.height * .5]
    GearBox:
        # segment_mode: False
        custom_bounds: [[(0, 0), (.5, .5), (1, 0)]]
        # draw_bounds: True
        pivot: root.width * .5, root.height * .5
        Image:
            source: 'wheel.png'
    ''')


class GearBox(Rotabox):
    pass


class Root(Widget):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)

    def update(self, *args):
        self.children[0].angle -= 1

    def on_touch_down(self, touch):
        child = self.children[0]
        center = child.get_point(0, 1)

        if (-3 < abs(child.origin[0]) - abs(center[0]) < 3
                and -3 < abs(child.origin[1]) - abs(center[1]) < 3):
            child.origin = center[0] + 50, center[1] + 50
        else:
            child.origin = center

if __name__ == '__main__':
    runTouchApp(Root())
