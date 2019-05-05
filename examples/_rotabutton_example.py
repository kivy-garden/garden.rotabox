from kivy.base import runTouchApp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
import sys, os
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox

Builder.load_string('''
<Root>:
    RotaButton:
        size: 200, 50
        center: 400, 300
        img_source: 'atlas://data/images/defaulttheme/button'
        on_press:
            self.img_source = 'atlas://data/images/defaulttheme/button_pressed'
            self.angle -= 5
            if not self.angle: self.angle -= .0000001  # if angle is 0 canvas doesn't update ???
        on_release:
            self.img_source = 'atlas://data/images/defaulttheme/button'
        canvas.before:
            BorderImage:
                source: self.img_source
                pos: self.pos
                size: self.size
        Label:
            size_hint: 1, 1
            text: 'A Rotabox Button'
    ''')


class RotaButton(ButtonBehavior, Rotabox):
    pass


class Root(FloatLayout):
    pass


runTouchApp(Root())
