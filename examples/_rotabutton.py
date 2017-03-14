from kivy.base import runTouchApp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
import sys, os
sys.path.append(os.path.abspath(".."))
from rotabox import Rotabox

Builder.load_string('''
<Root>:
    RotaButton:
        size: 200, 50
        aspect_ratio: 4
        center: 550, 300
        img_source: 'atlas://data/images/defaulttheme/button'
        on_press:
            self.img_source = 'atlas://data/images/defaulttheme/button_pressed'
            self.angle -= 5
        on_release:
            self.img_source = 'atlas://data/images/defaulttheme/button'
        angle: 30
        canvas.before:
            BorderImage:
                source: self.img_source
                pos: self.pos
                size: self.size
        Label:
            size_hint: 1, 1
            text: 'A Rotabox Button'
    ''')


class ButtonInRotabox(Rotabox):
    def __init__(self, **kwargs):
        super(ButtonInRotabox, self).__init__(**kwargs)
        self.btn = Button(text='A Button in Rotabox', on_press=self.rotate)
        self.add_widget(self.btn)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.btn.dispatch('on_press')
            self.btn._do_press()

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.btn._do_release()

    def rotate(self, *args):
        self.angle -= 5


class RotaButton(ButtonBehavior, Rotabox):
    pass


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.bir = ButtonInRotabox(size=(200, 50), center=(150, 280),
                                   angle=30)
        self.add_widget(self.bir)

runTouchApp(Root())
