from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
import sys, os
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox
from kivy.lang import Builder

Builder.load_string('''
<Root>:
    Rotabox:
        size: root.width * .4, root.height * .528
        center: root.width * .3, root.height * .5
        custom_bounds:
            [[(0.225, 0.685), (0.222, 0.405), (0.353, 0.278), (0.356, 0.435),
            (0.53, 0.261), (0.665, 0.398), (0.849, 0.587), (0.515, 0.553),
            (0.386, 0.683), (0.384, 0.526)],
            [(-.2, -.2), (1.2, -.2), (1.2, 1.2), (-.2, 1.2)]]
        hidden_bounds: [1]
        draw_bounds: True
        Image:
            source: 'data/logo/kivy-icon-256.png'
            color: 0, .3, .7, 1
    Rotabox:
        size: root.width * .25, root.height * .22
        center: root.width * .8, root.height * .5
        custom_bounds:
            [[(0.015, 0.985), (0.015, 0.346), (0.215, 0.035),
            (0.215, 0.419), (0.485, -0.004), (0.692, 0.315), (0.982, 0.75),
            (0.463, 0.665), (0.265, 0.977), (0.265, 0.596)],
            [(-.7, -.5), (1.7, -.5), (1.7, 1.5), (-.7, 1.5)]]
        hidden_bounds: [1]
        draw_bounds: True
        Image:
            source: 'kivy.png'
            color: .8, .2, 0, 1
    ''')


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)

    def update(self, *args):
        for i in xrange(len(self.children)):
            this = self.children[i]
            for j in xrange(i + 1, len(self.children)):
                that = self.children[j]
                hit = this.collide_widget(that)
                if hit:
                    if hit[0][0] not in this.hidden_bounds:
                        this.draw_color.rgba = 1, 0.518, 1, 1
                        that.draw_color.rgba = 1, 0.518, 1, 1
                        this.x += 1
                        that.x -= 1
                        continue
                    else:
                        this.draw_color.rgba = 0, 0.8, 1.5, 1
                else:
                    this.draw_color.rgba = .1, .1, .1, 1
                this.x -= .5
                that.x += .5
                this.angle -= .5
                that.angle += .6


runTouchApp(Root())
