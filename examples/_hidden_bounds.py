from kivy.base import runTouchApp
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.lang import Builder
import sys, os
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox

Builder.load_string('''
<Root>:
    Rotabox:
        id: blue
        size: root.width * .25, root.height * .22
        center: root.width * .3, root.height * .5
        custom_bounds:
            [[(0.015, 0.985), (0.015, 0.346), (0.215, 0.035),
            (0.215, 0.419), (0.485, -0.004), (0.692, 0.315), (0.982, 0.75),
            (0.463, 0.665), (0.265, 0.977), (0.265, 0.596)],
            [(-.1, -.7), (1.1, -.7), (-.1, 1.7), (1.1, 1.7)]]
        hidden_bounds: [1]
        draw_bounds: True
        Image:
            source: 'kivy.png'
            color: 0, .3, .7, 1
    Rotabox:
        id: red
        size: root.width * .25, root.height * .22
        center: root.width * .8, root.height * .5
        custom_bounds:
            [[(0.015, 0.985), (0.015, 0.346), (0.215, 0.035),
            (0.215, 0.419), (0.485, -0.004), (0.692, 0.315), (0.982, 0.75),
            (0.463, 0.665), (0.265, 0.977), (0.265, 0.596)]]
        Image:
            source: 'kivy.png'
            color: .7, 0, 0, 1
    ''')


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)

    def update(self, *args):
        this = self.ids.blue
        that = self.ids.red
        hit = this.collide_widget(that)
        if hit:
            if hit[0][0] not in this.hidden_bounds:
                this.x -= 1
                that.x += 1
            else:
                this.draw_color.rgba = 0, 0.8, 1.5, 1
        else:
            this.draw_color.rgba = .1, .2, .3, 1

        this.x += .5
        that.x -= .5
        this.angle -= .3
        that.angle += .2

if __name__ == '__main__':
    runTouchApp(Root())
