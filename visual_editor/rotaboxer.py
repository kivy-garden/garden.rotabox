# coding=utf-8

'''
                                                                   kivy 2.0.0
ROTABOXER
______________________________________________________________________________

    Rotaboxer is an editing tool for the Rotabox bounds*.
    With an image as input, the user can visually shape specific colliding
    bounds for it.
    The result is the code (a list or a dictionary) on clipboard to paste in
    a Rotabox widget, in a kivy project.
    Animated bounds are also supported, with the use of atlases.

____________________ RUN THE MODULE DIRECTLY TO USE ___________________________

unjuan 2020
'''

from __future__ import absolute_import, division, unicode_literals, print_function
import json, os, sys

PYTHON2 = False
if sys.version_info < (3, 0):  # Python 2.x
    from codecs import open
    range = xrange
    PYTHON2 = True
from future.utils import iteritems, iterkeys, itervalues

# Sets the current dir to the program's dir.
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
app_config = {}
try:
    with open('rotaboxer/settings.json', 'r', encoding="UTF8") as app_settings:
        app_config = json.load(app_settings)
except (IOError, KeyError):
    pass
else:
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Config.set('graphics', 'width', app_config.get('width'))
    Config.set('graphics', 'height', app_config.get('height'))
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'top', app_config.get('top'))
    Config.set('graphics', 'left', app_config.get('left'))
from kivy.app import App
from kivy.lang import Builder
from kivy.base import EventLoop
from kivy.uix.checkbox import CheckBox
from kivy.uix.scatter import ScatterPlane
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.clipboard import Clipboard
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.uix.popup import Popup
from kivy.app import platform
from kivy.properties import ObjectProperty, ListProperty, StringProperty, \
    ReferenceListProperty, AliasProperty, BooleanProperty, NumericProperty
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.slider import Slider
from kivy.metrics import dp, sp
from collections import deque
from functools import partial
from threading import Thread
import re
import traceback
import time
import math

__author__ = 'unjuan'
__version__ = '0.13.2'

'''
The border length of the largest shape that would be considered as noice,
in make_border and link_points methods.'''
MIN_SHAPE = 5
'''
Number of iterations in the filter_border method.
'''
FILTER_PASSES = 10


class Point(ToggleButton):
    # noinspection PyArgumentList
    pivot_bond = ListProperty([.5, .5])

    def get_pivot_x(self):
        return self.x + self.width * self.pivot_bond[0]

    def set_pivot_x(self, value):
        if self.width > 1:
            self.x = value - self.width * self.pivot_bond[0]
        else:
            if value > 1:
                self.piv_x = value
    pivot_x = AliasProperty(get_pivot_x, set_pivot_x,
                            bind=('x', 'width', 'pivot_bond'))

    def get_pivot_y(self):
        return self.y + self.height * self.pivot_bond[1]

    def set_pivot_y(self, value):
        if self.height > 1:
            self.y = value - self.height * self.pivot_bond[1]
        else:
            if value > 1:
                self.piv_y = value
    pivot_y = AliasProperty(get_pivot_y, set_pivot_y,
                            bind=('y', 'height', 'pivot_bond'))
    '''Rotabox's pivot.'''
    pivot = ReferenceListProperty(pivot_x, pivot_y)

    def get_origin(self):
        return self.pivot

    def set_origin(self, point):
        pivot = point
        self.pivot_bond = ((pivot[0] - self.x) / float(self.width),
                           (pivot[1] - self.y) / float(self.height))
        self.pos = (self.x - (pivot[0] - point[0]),
                    self.y - (pivot[1] - point[1]))

    '''Rotabox's origin.'''
    origin = AliasProperty(get_origin, set_origin)

    # Initial widget size. Used for calculating the widget's scale.
    # noinspection PyArgumentList
    original_size = ListProperty([1, 1])

    def get_scale(self):
        return float(self.width) / self.original_size[0]

    def set_scale(self, amount):
        if amount < self.scale_min:
            amount = self.scale_min
        elif amount > self.scale_max:
            amount = self.scale_max

        pivot = self.pivot[:]
        self.size = (amount * self.original_size[0],
                     amount * self.original_size[1])
        self.pivot = pivot

    '''Rotabox's scale.'''
    scale = AliasProperty(get_scale, set_scale, bind=('width', 'height',
                                                      'original_size'))
    '''Minimum scale allowed.'''
    scale_min = NumericProperty(0.1)

    '''Maximum scale allowed.'''
    scale_max = NumericProperty(3)
    multi_selected = BooleanProperty(False)
    busy = False
    norm_fill_color = .5, 0, 0, 0
    down_fill_color = .5, 0, 0, .5
    norm_line_color = .3, .3, .3, .5
    down_line_color = .8, 0, 0, 1
    picked_line_color = 1.0, 0.7, 0.29, 1

    def __init__(self, pol, root, mag, **kwargs):
        self.editor = root
        self.piv_x = self.piv_y = 0
        super(Point, self).__init__(**kwargs)
        self.size = mag * 6, mag * 6
        self.original_size = self.size
        self.scale = 1.5 / self.editor.scat.scale + .1
        self.grabbed = False
        self.popup = None
        self.deselect = False
        self.pol = pol
        self.area_color = 0, 0, 0, 0
        self.line_color = 0, 0, 0, 0

    def on_size(self, *args):
        self.x -= self.size[0] * .5
        self.y -= self.size[1] * .5
        self.label.color = self.adjust_color(self.right, self.top)

    def on_pos(self, *args):
        try:
            self.label.color = self.adjust_color(self.right, self.top)
        except AttributeError:
            pass

    def on_state(self, *args):
        if self.state == 'down':
            if not self.multi_selected:
                self.line_color = self.down_line_color
            self.area_color = self.down_fill_color
        else:
            if not self.multi_selected:
                self.line_color = self.norm_line_color
            self.area_color = self.norm_fill_color

    def on_multi_selected(self, *args):
        if self.multi_selected:
            self.line_color = self.picked_line_color
        else:
            if self.state == 'down':
                self.area_color = self.down_fill_color
                self.line_color = self.down_line_color
            else:
                self.area_color = self.norm_fill_color
                self.line_color = self.norm_line_color

    def on_press(self, *args):
        self.state = 'down'
        if (self.editor.index != self.pol['btn_points'].index(self)
                or self.editor.pol != self.pol['key']):
            self.editor.pol = str(self.pol['key'])
            self.editor.index = self.pol['btn_points'].index(self)
            self.editor.save_state(motion_end=1)
            if self.editor.to_transfer:
                return
            if not self.editor.ordered:
                for pol in itervalues(self.editor.rec[self.editor.frame]):
                    if pol['number'] > self.pol['number']:
                        pol['number'] -= 1
                self.pol['number'] = len(self.editor.rec[self.editor.frame]) - 1

    def on_touch_move(self, touch):
        if self.state != 'down':
            return
        if Point.busy or self.grabbed:
            return
        if not self.collide_point(*touch.pos):
            return
        self.origin = touch.pos
        Window.bind(on_motion=self.drag)
        self.grabbed = True
        Point.busy = True

    def drag(self, *args):
        self.opacity = .3
        self.pivot = self.editor.scat.to_widget(*args[2].pos)
        self.editor.draw()

    def on_release(self, *args):
        Window.unbind(on_motion=self.drag)
        if self.grabbed:
            self.opacity = 1
            self.editor.save_state(msg=str(self.pol['btn_points'].index(self))
                                       + '_'
                                       + str(self.pol['key'])
                                       + '_'
                                       + str((round(self.center_x),
                                        round(self.center_y))),
                                   motion=1)
            self.grabbed = False
            Point.busy = False
            self.editor.draw()
        elif self.deselect:
            self.editor.deselect_polygon()
            self.deselect = False
            return
        self.state = 'down'

    def adjust_color(self, x, y):
        if self.editor.sprite.collide_point(x, y):
            image = self.editor.sprite.image
            x, y = x - image.x, y - image.y
            try:
                back = image._coreimage.read_pixel(x, image.height - y - 1)
            except (AttributeError, IndexError):
                pass
            else:
                if back[-1]:
                    color = [1 - back[0], 1 - back[1], 1 - back[2], 1]
                    if back[0] + back[1] + back[2] < 1.5:
                        d = 1 - max(color[:-1])
                        color[0] += d
                        color[1] += d
                        color[2] += d
                    else:
                        d = min(color[:-1])
                        color[0] -= d
                        color[1] -= d
                        color[2] -= d
                    return color
        return .4, .5, .7, 1.0

    def pop_up(self, *args):
        if self.popup:
            self.dismiss_popup()
        point_popup = BoxLayout(orientation='vertical')

        pick_btn = Button(background_color=(.13, .13, .2, 1),
                          on_release=partial(self.editor.pick_point, self))
        pick_btn.text = 'Pick point'
        point_popup.add_widget(pick_btn)

        rem_btn = Button(background_color=(.13, .13, .2, 1),
                         on_release=self.editor.remove_point)
        rem_btn.text = 'Remove point'
        point_popup.add_widget(rem_btn)

        opn_btn = Button(background_color=(.13, .13, .2, 1),
                         on_release=self.editor.open_polygon)
        opn_btn.text = self.editor.open_btn.text
        point_popup.add_widget(opn_btn)

        clear_btn = Button(background_color=(.13, .13, .2, 1),
                           on_release=self.editor.remove_polygon)
        clear_btn.text = 'Remove polygon'
        point_popup.add_widget(clear_btn)

        self.popup = AutoPopup(content=point_popup,
                               size_hint=(None, None),
                               size=(dp(240), dp(200)))
        self.popup.title = "Point menu:"
        self.popup.open()

    def dismiss_popup(self, *args):
        if self.popup:
            self.popup.dismiss()
            self.popup = None


# todo REMOVE when the issue with uix.Image and keep_data=True is fixed in kivy...
class KDImage(Image):
    def __init__(self, **kwargs):
        super(KDImage, self).__init__(**kwargs)
        self.texture_update()


# noinspection PyArgumentList
class Editor(FloatLayout):

    def __init__(self, **kwargs):
        super(Editor, self).__init__(**kwargs)
        self.rec = {}
        self.keys = []
        self.frame = '0'
        self.pol = None
        self.index = None
        self.lasts = ['0', None, None]
        self.history = deque()
        self.state = -1
        self.changes = 0
        self.motion_args = []
        self.atlas_source = ''
        self.animation = False
        self.clone_points = False
        self.ordered = True
        self.history_states = 30  # UNDO STATES
        self.moves = []
        self.popup = None
        self.filename = ''
        self.source = ''
        self.image = ''
        self.code = ''
        self.save_name = ''
        self.draw_group = InstructionGroup()
        self.scat.canvas.add(self.draw_group)
        self.line_width = 1
        self.mag = 2
        self.simplicity = 10
        self.ctrl = False
        self.to_transfer = []
        self.nums_on = False
        self.default_color = .29, .518, 1, 1
        self.last_dir = app_config.get('last dir', './')

        # for tracing
        self.simple_border = []
        self.simplest_border = []
        self.trace_mode = False
        self.temp_img = ''
        self.orig_source = None
        self.matte = 1, .5, 1, 1
        self.multi_shape = False
        self.all_frames = False
        self.all_go = False
        self.done = 0

        EventLoop.window.bind(on_keyboard=self.on_key,
                              on_key_up=self.on_key_up)
        Clock.schedule_once(self.load_dialog)

    def on_parent(self, *args):
        try:
            assert sys.platform == 'win32'
        except AssertionError:
            pass
        else:
            Window.bind(on_request_close=self.exit_check)

# ,,,------------------------ EDITOR -----------------------
    def add_point(self, x=None, y=None, state=True):
        frame = self.rec[self.frame]
        if self.pol is not None:
            pol = frame[self.pol]

            if not x or not y:  # If from keyboard
                if len(pol['btn_points']) > 1:
                    next_index = (self.index + 1) % len(pol['btn_points'])
                    x = (pol['btn_points'][self.index].center_x +
                         pol['btn_points'][next_index].center_x) * .5
                    y = (pol['btn_points'][self.index].center_y +
                         pol['btn_points'][next_index].center_y) * .5
                else:
                    x, y = self.sprite.center

            pol['btn_points'][self.index].state = 'normal'
            self.index += 1
            pol['btn_points'].insert(self.index, (Point(pol, self, self.mag,
                                                        pos=(x, y),
                                                        text=str(self.index),
                                                        state='down')))
            self.scat.add_widget(pol['btn_points'][self.index])
        else:
            if not (x and y):
                x, y = self.sprite.center
            self.pol = str(len(frame))
            pol = frame[self.pol] = {}

            pol['number'] = pol['key'] = int(self.pol)
            pol['open'] = False
            pol['btn_points'] = [Point(pol, self, self.mag, pos=(x, y),
                                       text=str(0))]
            pol['color'] = self.default_color
            pol['label'] = Label(size=(dp(50), dp(50)), font_size='35sp', bold=True,
                                 color=pol['color'][:-1] + (.3,))
            self.scat.add_widget(pol['label'])
            self.scat.add_widget(pol['btn_points'][-1])
            self.index = 0
        if state:
            self.save_state('Added point {} to polygon {} at {}'
                            .format(self.index, self.pol, (round(x), round(y))))
            self.draw()

    def remove_point(self, state=True, *args):
        if not self.to_transfer:
            try:
                p, i = self.pol, self.index
                pol = self.rec[self.frame][self.pol]
                pol['btn_points'][self.index].dismiss_popup()
                self.scat.remove_widget(pol['btn_points'].pop(
                                        self.index))
                if self.index > -1:
                    self.index -= 1
                if len(pol['btn_points']):
                    pol['btn_points'][self.index].state = 'down'
                else:
                    self.remove_gap(pol)
                    self.pol = None
                    self.index = None
            except (LookupError, TypeError) as er:
                print('on remove_point: ', er)
            else:
                if state:
                    self.save_state('Removed point {} from polygon {}'
                                    .format(i, p))
                    self.draw()

    def remove_polygon(self, *args):
        if not self.to_transfer:
            try:
                pol = self.rec[self.frame][self.pol]
            except LookupError as er:
                print('on clear_polygon: ', er)
            else:
                pol['btn_points'][self.index].dismiss_popup()
                while len(pol['btn_points']):
                    self.scat.remove_widget(pol['btn_points'].pop())
                self.scat.remove_widget(pol['label'])
                self.remove_gap(pol)
                pidx = self.pol
                self.pol = None
                self.index = None
                self.save_state('Removed polygon {}'.format(pidx))
                self.draw()

    def remove_gap(self, pol):
        # Taking care of indices' consecutiveness in case of removing
        # a middle one.
        frame = self.rec[self.frame]

        p = len(frame) - 1
        for k, v in iteritems(frame):
            if v['number'] > pol['number']:
                v['number'] -= 1
            elif v == pol:
                p = int(k)
        pol['number'] = len(frame) - 1

        while p < len(frame) - 1:
            frame[str(p)] = frame[str(p + 1)]
            frame[str(p)]['key'] = p
            frame[str(p)]['label'].text = str(p)
            p += 1

        del frame[str(p)]

    def open_polygon(self, *args):
        if self.pol:
            pol = self.rec[self.frame][self.pol]
            pol['btn_points'][self.index].dismiss_popup()
            if pol['open']:
                pol['open'] = False
                self.save_state('Closed polygon {}'.format(self.pol))
            else:
                pol['open'] = True
                self.save_state('Opened polygon {}'.format(self.pol))
            self.update()
            self.draw()

    def deselect_polygon(self):
        if self.pol:
            self.rec[self.frame][self.pol]['btn_points'][self.index].state = \
                'normal'
            self.lasts = self.frame, self.pol, self.index
            self.pol = None
            self.index = None
            self.save_state(motion_end=1)
            self.draw()

    def pick_point(self, point, *args):
        point.dismiss_popup()
        if point.multi_selected:
            self.to_transfer.remove((self.pol,
                                     point.pol['btn_points'].index(point)))
            point.multi_selected = False
            self.draw()
            return

        self.to_transfer.append((self.pol, point.pol['btn_points'].index(point)))
        point.multi_selected = True
        self.draw()

    def transfer_points(self, point=None, pp=None):
        poli = poii = ''
        if pp:
            poli, poii = self.pol, self.index
            self.pol, self.index = pp[0], pp[1]
        self.save_state('Picked Points {}'.format(self.to_transfer))
        if pp:
            self.pol, self.index = poli, poii

        frame = self.rec[self.frame]
        ptis = {}
        ordered = [None] * len(self.to_transfer)
        for e in self.to_transfer:
            try:
                ptis[e[0]].append(e[1])
            except KeyError:
                ptis[e[0]] = [e[1]]

        if point:
            if point.multi_selected:
                self.empty_cut()
                self.save_state('Cancelled transfer')
                return

            for p, plg in sorted(iteritems(ptis), reverse=True):
                for pidx in sorted(plg, reverse=True):
                    xpol = frame[p]
                    cutpoint = xpol['btn_points'][pidx]
                    ordered[self.to_transfer.index((p, pidx))] = cutpoint
                    cutpoint.pol = point.pol
                    cutpoint.multi_selected = False
                    cutpoint.area_color = cutpoint.norm_fill_color
                    cutpoint.line_color = cutpoint.norm_line_color

                    del xpol['btn_points'][pidx]

                    if not xpol['btn_points']:
                        for apol in itervalues(frame):
                            if apol['number'] > xpol['number']:
                                apol['number'] -= 1
                        self.scat.remove_widget(xpol['label'])
                        self.remove_gap(xpol)

            i = point.pol['btn_points'].index(point) + 1
            for cutpoint in ordered:
                cutpoint.pol['btn_points'].insert(i, cutpoint)
                i += 1

            self.pol = str(point.pol['key'])
            curpoint = frame[self.pol]['btn_points'][self.index]
            curpoint.area_color = curpoint.norm_fill_color
            curpoint.line_color = curpoint.norm_line_color
            self.index = i - 1
            frame[self.pol]['btn_points'][self.index].state = 'down'
            msg = 'Pasted {} points to polygon {}'.format(len(ordered), self.pol)

        else:
            self.deselect_polygon()
            self.pol = str(len(frame))
            pol = frame[self.pol] = {}

            pol['number'] = pol['key'] = int(self.pol)
            pol['open'] = False
            pol['btn_points'] = []
            pol['color'] = self.default_color
            pol['label'] = Label(size=(dp(50), dp(50)), font_size='35sp', bold=True,
                                 color=pol['color'][:-1] + (.3,))
            self.scat.add_widget(pol['label'])

            for p, plg in sorted(iteritems(ptis), reverse=True):
                for pidx in sorted(plg, reverse=True):
                    xpol = frame[p]
                    cutpoint = xpol['btn_points'][pidx]
                    ordered[self.to_transfer.index((p, pidx))] = cutpoint
                    cutpoint.pol = pol
                    cutpoint.multi_selected = False
                    cutpoint.area_color = cutpoint.norm_fill_color
                    cutpoint.line_color = cutpoint.norm_line_color

                    del xpol['btn_points'][pidx]

                    if not xpol['btn_points']:
                        for apol in itervalues(frame):
                            if apol['number'] > xpol['number']:
                                apol['number'] -= 1
                        self.scat.remove_widget(xpol['label'])
                        self.remove_gap(xpol)
            i = 0
            for cutpoint in ordered:
                pol['btn_points'].insert(i, cutpoint)
                i += 1
            self.pol = str(pol['key'])
            self.index = i - 1
            # noinspection PyUnresolvedReferences
            pol['btn_points'][self.index].state = 'down'
            msg = 'New polygon ({}) of {} points'.format(self.pol, len(ordered))
        self.empty_cut()
        self.save_state(msg)
        self.draw()

    def empty_cut(self):
        for entry in self.to_transfer:
            try:
                point = self.rec[self.frame][entry[0]]['btn_points'][entry[1]]
                if entry[1] != self.index:
                    point.area_color = point.norm_fill_color
                    point.line_color = point.norm_line_color
                point.multi_selected = False
            except (KeyError, IndexError) as er:
                print('on empty_cut: ', er)
        del self.to_transfer[:]

    def save_state(self, msg='__state', motion=0, motion_end=0):
        if msg != '__state' and self.history \
                  and self.history[self.state][0] == msg:
            return
        if not motion:
            if self.moves:
                args = self.motion_args[-1].split('_')
                last = self.moves[-1][:]
                last = ('Moved point {} of polygon {} to {}'.format(args[0],
                                                                    args[1],
                                                                    args[2]),
                        last[1])
                self.history.append(last)
                self.changes += 1
                del self.moves[:]
        if not motion_end:
            if self.state != -1:
                index = self.state + len(self.history)
                while len(self.history) > index + 1:
                    self.history.pop()
                self.state = -1

            project = {'frame': self.frame, 'pol': self.pol, 'index': self.index,
                       'to_transfer': self.to_transfer[:]}
            snapshot = msg, self.store(project)

            if motion:
                self.motion_args.append(snapshot[0])
                self.moves.append(snapshot)
            else:
                self.history.append(snapshot)
                self.changes += 1
                if len(self.history) > self.history_states:
                    self.history.popleft()
        self.update()

    def change_state(self, btn):
        if btn == 'redo':
            if not self.state < -1:
                return
            self.state += 1
            self.changes += 1
        elif btn == 'undo':
            if not self.state > -len(self.history):
                return
            self.state -= 1
            self.changes -= 1

        if -len(self.history) <= self.state < 0:
            self.busy.opacity = 1
            Clock.schedule_once(self.build_state, .1)

    def build_state(self, *args):
        self.clear_points()
        state = self.history[self.state][1]
        if self.atlas_source:
            self.frame = state['frame']
            self.sprite.image.source = (
                        'atlas://' + self.filename + '/' + self.frame)
            self.board1.text = (self.image + '\n(' + str(
                self.keys.index(self.frame) + 1) + '  of  ' + str(
                len(self.keys)) + '  frames)')
        self.pol = state['pol']
        self.index = state['index']
        self.to_transfer = state['to_transfer'][:]
        self.restore(state, __version__)
        try:
            self.rec[self.frame][self.pol]['btn_points'][
                self.index].state = 'down'
        except (KeyError, IndexError):
            pass
        for entry in self.to_transfer:
            pol = self.rec[self.frame][entry[0]]
            cutpoint = pol['btn_points'][entry[1]]
            cutpoint.multi_selected = True
        self.update()
        self.draw()
        self.busy.opacity = 0

    def navigate(self, btn):
        cf = self.frame
        if self.atlas_source:
            self.empty_cut()
            while len(self.scat.children) > 1:
                for point in self.scat.children:
                    if isinstance(point, (Point, Label)):
                        self.scat.remove_widget(point)
            if btn == '>':
                self.frame = \
                    self.keys[self.keys.index(self.frame) + 1] \
                    if self.keys.index(self.frame) + 1 < len(self.keys) \
                    else self.keys[0]
            else:
                self.frame = \
                    self.keys[self.keys.index(self.frame) - 1] \
                    if self.keys.index(self.frame) > 0 \
                    else self.keys[-1]
            try:
                self.sprite.image.source = ('atlas://' + self.filename + '/'
                                                       + self.frame)
            except ZeroDivisionError:
                pass
            self.sprite.image.size = self.sprite.image.texture_size
            self.sprite.size = self.sprite.image.size
            self.sprite.center = self.width * .6, self.height * .5

            if self.clone_points:
                for key in iterkeys(self.rec[cf]):
                    self.rec[self.frame][key] = {'btn_points': []}
                for (k, v), (k2, v2) in \
                        zip(iteritems(self.rec[cf]),
                            iteritems(self.rec[self.frame])):

                    for i, point in enumerate(v['btn_points']):
                        v2['btn_points'].append(Point(v2, self, self.mag,
                                                      text=str(i),
                                                      pos=point.center))
                    v2['key'] = v['key']
                    v2['number'] = v['number']
                    v2['open'] = v['open']
                    v2['color'] = v['color'][:]
                    v2['label'] = Label(size=(dp(50), dp(50)), font_size='35sp',
                                        bold=True, color=v2['color'][:-1] + (.3,))
                    self.scat.add_widget(v2['label'])
                if self.rec[cf]:
                    self.save_state('Cloned points of frame {} to frame {}'
                                    .format(cf, self.frame))

            for pol in itervalues(self.rec[self.frame]):
                for point in pol['btn_points']:
                    self.scat.add_widget(point)
                    point.area_color = point.norm_fill_color
                    point.line_color = point.norm_line_color

            self.pol = None
            self.index = None
            self.adjust_points()
            self.update()
            self.draw()
            self.board1.text = (self.image + '\n('
                                + str(self.keys.index(self.frame) + 1)
                                + '  of  '
                                + str(len(self.keys)) + '  frames)')

    def clear_points(self):
        for frame in itervalues(self.rec):
            for pol in itervalues(frame):
                while len(pol['btn_points']):
                    self.scat.remove_widget(pol['btn_points'].pop())
                self.scat.remove_widget(pol['label'])
            frame.clear()
        self.rec.clear()

# ,,,------------------------ INPUT -----------------------
    def load_dialog(self, *args):
        """ Shows the 'Import/Open' dialog."""
        if self.popup:
            self.changes = 0
            self.dismiss_popup()
        if self.changes > 1:
            self.warn('Warning!', 'Project is not saved\n'
                                  'and will be lost.\nContinue?',
                      action=self.load_dialog)
            return
        content = LoadDialog()
        content.load = self.load_check
        content.cancel = self.dismiss_popup
        content.file_types = ['*.png', '*.atlas', '*.bounds']
        if os.path.isdir(self.last_dir):
            content.filechooser.path = self.last_dir
        else:
            content.filechooser.path = './'
        self.popup = AutoPopup()
        self.popup.content = content
        self.popup.size_hint = .6, .9
        self.popup.title = 'Open image, atlas or project file:'
        self.popup.auto_dismiss = False
        self.popup.open()

    def load_check(self, path, filename):
        if filename:
            filename = filename[0]
            self.last_dir = path
            self.clear_points()
            self.rec = {}
            del self.keys[:]
            self.frame = '0'
            self.pol = None
            self.index = None
            self.lasts = ['0', None, None]
            self.history = deque()
            self.state = -1
            self.changes = 0
            self.atlas_source = ''
            self.animation = False
            self.sprite.size = dp(1), dp(1)
            self.sprite.pos = self.width * .6, self.height * .5
            self.scat.scale = 1
            self.ctrl = False

            # for tracing
            self.simple_border = []
            self.simplest_border = []
            self.trace_mode = False
            self.temp_img = ''
            self.orig_source = None
            self.matte = 1, .5, 1, 1
            self.multi_shape = False
            self.multi_chk.active = False
            self.all_frames = False
            self.all_chk.active = False
            self.all_go = False
            self.done = 0
            self.trace_box.thres = dp(1.0)

            self.empty_cut()
            try:
                self.sprite.remove_widget(self.sprite.image)
            except AttributeError:
                pass
            if filename.endswith('.bounds'):
                self.load_proj(filename, path)
            else:
                self.load_img(filename, path)
                self.save_state("Loaded image '{}'".format(filename))
                self.update()
                self.draw()
        Clock.schedule_interval(self.hover, .1)

    def load_img(self, filename, path, source=None):
        self.dismiss_popup()
        filename = os.path.join(path, filename)\
            .replace('./', '').replace('_RESCUED_', '')
        file_name = filename.replace('.png', '')\
            .replace('.atlas', '').replace('.bounds', '')
        if source:  # If a project is opened
            filename = filename.replace(filename.split('\\')[-1], source)
        self.image = filename.split('\\')[-1]
        self.save_name = file_name + '.bounds'
        try:
            self.source = os.path.relpath(os.path.join(path, filename))
        except ValueError as er:
            self.source = os.path.join(path, filename)
            print('on load_img(relpath): ', er)
        if filename.endswith('.atlas'):
            try:
                with open(self.source, 'r', encoding="UTF8") as ani:
                    atlas = json.load(ani)
            except (IOError, KeyError) as er:
                print('On load_img(atlas reading):', er)
            else:
                self.keys = sorted([key for key in iterkeys(
                    atlas[filename.replace('.atlas', '.png').split('\\')[-1]])])
                self.filename = filename.replace('.atlas', '')
                try:
                    self.atlas_source = ('atlas://' +
                                         os.path.relpath(filename) +
                                         '/' + self.keys[0])
                except ValueError as er:
                    self.atlas_source = ('atlas://' +
                                         filename + '/' + self.keys[0])
                    print('on load_img(atlas relpath): ', er)
                for key in self.keys:
                    self.rec[key] = {}
                self.frame = self.keys[0]
                self.sprite.image = Image(source=self.atlas_source)
        else:
            self.sprite.image = KDImage(source=self.source, keep_data=True)
        self.sprite.add_widget(self.sprite.image)
        self.sprite.image.size = self.sprite.image.texture_size
        self.sprite.size = self.sprite.image.size
        self.sprite.image.pos = self.sprite.pos
        self.sprite.opacity = 1
        self.grid.opacity = 1
        self.mag = min(self.sprite.image.width
                       * self.sprite.image.height / 1800., 3)
        self.board1.text = self.image

        if self.atlas_source:
            self.board1.text += ('\n('
                                 + str(self.keys.index(self.frame) + 1)
                                 + '  of  '
                                 + str(len(self.keys)) + '  frames)')

    def load_proj(self, filename, path):
        source = os.path.join(path, filename)
        try:
            with open(source, 'r', encoding="UTF8") as proj:
                project = json.load(proj)
        except (IOError, KeyError) as er:
            print('On load_proj(proj reading): ', er)
        else:
            self.load_img(filename, path, source=project['image'])
            if not self.sprite.image.texture:
                self.sprite.remove_widget(self.sprite.image)
                self.sprite.image = None
                self.sprite.opacity = 0
                self.grid.opacity = 0
                self.board1.text = ''
                self.warn("Image '{}' is not found.".format(
                          project['image']),
                          "Please, put the image\n"
                          "in the project file's directory\n"
                          "and try again.",
                          action=self.dismiss_popup, cancel=0)
                return
            try:
                version = project['version']
                del project['version']
            except KeyError as er:
                print('on load_proj(version): ', er)
                version = '0.8.0'
            del project['image']
            Clock.schedule_once(partial(self.load_proj_fin, project, version,
                                        filename))

    def load_proj_fin(self, project, version, filename, *args):
        self.restore(project, version)
        self.save_state("Loaded project '{}'".format(filename))
        self.update()
        self.draw()

    def restore(self, snapshot, version):
        for f, sframe in iteritems(snapshot):
            if f in ('frame', 'pol', 'index', 'to_transfer'):
                continue
            self.rec[f] = {}
            for p, pol in iteritems(sframe):
                self.rec[f][p] = {}
                self.rec[f][p]['key'] = pol['key']
                self.rec[f][p]['number'] = pol['number']
                try:
                    self.rec[f][p]['open'] = pol['open']
                except Exception:
                    self.rec[f][p]['open'] = False
                self.rec[f][p]['color'] = tuple(pol['color'])
                self.rec[f][p]['label'] = Label(size=(dp(50), dp(50)), font_size='35sp',
                                                bold=True,
                                                color=self.rec[f][p]['color'][:-1] + (.3,))
                self.scat.add_widget(self.rec[f][p]['label'])
                self.rec[f][p]['btn_points'] = [Point(self.rec[f][p], self,
                                                      self.mag,
                                                      text=str(i),
                                                      pos=(point[0] +
                                                           self.sprite.x,
                                                           point[1] +
                                                           self.sprite.y))
                                                for i, point in enumerate(
                                                                pol['points'])]
                if f == self.frame:
                    for i in range(len(self.rec[f][p]['btn_points'])):
                        point = self.rec[f][p]['btn_points'][i]
                        self.scat.add_widget(point)
                        point.area_color = point.norm_fill_color
                        point.line_color = point.norm_line_color

# ,,,------------------------ OUTPUT -----------------------
    def unlock_order(self, state=None, *args):
        if not state:
            state = self.index_btn.state
            if state == 'down':
                self.index_btn.state = 'normal'
                self.ordered = True
            else:
                self.index_btn.state = 'down'
                self.ordered = False
        else:
            if state == 'down':
                self.ordered = False
            else:
                self.ordered = True

    def check_out(self, *args):
        if self.atlas_source:
            self.manage_multi()
        else:
            self.choose_lang()

    def manage_multi(self, *args):
        popup = BoxLayout(orientation='vertical')

        sf_btn = Button(background_color=(.13, .13, .2, 1),
                        on_release=self.export_all)
        sf_btn.text = 'Single frame (current)'
        popup.add_widget(sf_btn)
        ani_btn = Button(background_color=(.13, .13, .2, 1),
                         on_release=partial(self.export_all, True))
        ani_btn.text = 'Animation (all frames)'
        popup.add_widget(ani_btn)

        self.popup = AutoPopup(content=popup,
                               size_hint=(None, None),
                               size=(dp(240), dp(150)))
        self.popup.title = 'Multi-frame export options'
        self.popup.open()

    def export_all(self, xall=False, *args):
        self.dismiss_popup()
        self.animation = xall
        self.choose_lang()

    def choose_lang(self, *args):
        self.dismiss_popup()
        popup = BoxLayout(orientation='vertical')

        py_btn = Button(background_color=(.13, .13, .2, 1),
                        on_release=self.to_clipboard)
        py_btn.text = 'Python'
        popup.add_widget(py_btn)
        kv_btn = Button(background_color=(.13, .13, .2, 1),
                        on_release=partial(self.to_clipboard, False))
        kv_btn.text = 'KVlang'
        popup.add_widget(kv_btn)

        self.popup = AutoPopup(content=popup,
                               size_hint=(None, None),
                               size=(dp(240), dp(150)))
        self.popup.title = 'Select code language:'
        self.popup.open()

    def to_clipboard(self, py=True, *args):
        self.dismiss_popup()
        self.write(py)
        code = self.code if not PYTHON2 else self.code.decode('utf-8')
        Clipboard.copy(code)
        self.warn('Bounds exported!',
                  'Code is now on the clipboard,\n'
                  'ready to Paste in a Rotabox widget\n'
                  'that uses the same image.',
                  action=self.dismiss_popup, cancel=0,
                  tcolor=(.1, .65, .1, 1))
        print(Clipboard.paste())

    def write(self, py=True):
        if self.atlas_source and self.animation:
            if py:
                self.code = 'custom_bounds = {\n            '
            else:
                self.code = 'custom_bounds:\n            {'
            keys = sorted(self.rec.keys())
            for key in keys:
                frame = self.rec[key]
                if frame:
                    self.calc_hints(frame)
                    pols = self.sort_polygons(frame)
                    self.code += "'" + key + "': ["
                    self.write_more(pols, py)
                    if py:
                        self.code += '],\n            '
                    else:
                        self.code += '],\n            '
            self.code = (self.code.rstrip(',\n ') + '}')
            return
        frame = self.rec[self.frame]
        self.calc_hints(frame)
        if py:
            self.code = 'custom_bounds = [\n            '
        else:
            self.code = 'custom_bounds:\n            ['
        pols = self.sort_polygons(frame)
        opens = self.write_more(pols, py)
        self.code += ']'
        if opens:
            if py:
                self.code += '\n        open_bounds = {}'.format(opens)
            else:
                self.code += '\n        open_bounds: {}'.format(opens)

    @staticmethod
    def sort_polygons(frame):
        pols = []
        i = 0
        while i < len(frame):
            for pol in itervalues(frame):
                if pol['number'] == i:
                    pols.append(pol)
                    break
            i += 1
        return pols

    def calc_hints(self, frame):
        for pol in itervalues(frame):
            if len(pol['btn_points']):
                pol['hints'] = [(round(float(point.center_x - self.sprite.x) /
                                       self.sprite.width, 3),
                                 round(float(point.center_y - self.sprite.y) /
                                       self.sprite.height, 3))
                                for point in pol['btn_points']]
            else:
                pol['hints'] = []

    def write_more(self, pols, py):
        opens = []
        anim = self.atlas_source and self.animation
        if anim:
            poiws = '\n                   '
            polws = '\n                  '
        else:
            poiws = '\n             '
            polws = '\n            '
        kvspace = '\n            '
        for pol in pols:
            if not pol['hints']:
                continue
            if pol['open']:
                opens.append(pol['number'])
            self.code += '['
            i_3 = 0
            for i, point in enumerate(pol['hints']):
                self.code += '(' + str(point[0]) + ', ' + str(point[1]) + '), '
                if (not anim and i - i_3 == 3) or (anim and i - i_3 == 2):
                    if py:
                        self.code += poiws
                    else:
                        self.code += kvspace
                    i_3 = i + 1
            self.code = (self.code.rstrip(',\n ') + '], ')
            if py:
                self.code += polws
            else:
                self.code += kvspace
        self.code = self.code.rstrip(',\n ')
        return opens

# ,,,------------------------ STORAGE -----------------------
    def store(self, project):
        for f, frame in iteritems(self.rec):
            project[f] = {}
            for p, pol in iteritems(frame):
                project[f][p] = {}
                project[f][p]['key'] = pol['key']
                project[f][p]['number'] = pol['number']
                try:
                    project[f][p]['open'] = pol['open']
                except Exception:
                    project[f][p]['open'] = False
                project[f][p]['color'] = pol['color']
                project[f][p]['points'] = [tuple([point.center_x - self.sprite.x,
                                                  point.center_y - self.sprite.y])
                                           for point in pol['btn_points']]

        return project

    def save_dialog(self, *args):
        """ Shows the 'Save project' dialog."""
        if not self.sprite.image:
            return
        content = SaveDialog(save=self.save_check, cancel=self.dismiss_popup,
                             file_types=['*.bounds'])
        content.ids.filechooser.path = self.last_dir
        content.text_input.text = (self.save_name.split('\\')[-1])
        self.popup = AutoPopup(content=content, size_hint=(.6, .9),
                               title='Save project:', auto_dismiss=False)
        self.popup.open()

    def save_check(self, path, filename):
        if filename:
            self.last_dir = path
            filename = self.sanitize_filename(filename)
            if not filename.endswith('.bounds'):
                filename += '.bounds'
            self.save_name = os.path.join(path, filename)
            if os.path.isfile(self.save_name):
                self.dismiss_popup()
                self.warn('Warning!', 'Filename already exists.\n'
                          'Overwrite?', self.save_proj)
                return
            self.save_proj()
        self.dismiss_popup()

    def save_proj(self, *args):
        self.dismiss_popup()
        project = self.store({})
        project['image'] = self.image
        project['version'] = __version__
        try:
            with open(self.save_name, 'w+', encoding="UTF8") as proj:
                json.dump(project, proj, sort_keys=True, indent=4)
        except IOError as er:
            print('On save_proj:', er)
        else:
            self.changes = 0

    def exit_save(self, *args):
        project = self.store({})
        project['image'] = self.image
        project['version'] = __version__
        root, ext = os.path.splitext(self.save_name)
        save_name = root + '_RESCUED_' + ext
        try:
            with open(save_name, 'w+', encoding="UTF8") as proj:
                json.dump(project, proj, sort_keys=True, indent=4)
        except IOError as er:
            print('On exit_save: ', er)

# ,,,---------------------- USER EVENTS ---------------------
    def on_touch_down(self, touch):
        mouse_btn = ''
        if self.shortcuts.opacity:
            self.hide_keys()
            return
        if 'button' in touch.profile:
            mouse_btn = touch.button
        if not self.sprite.image:
            super(Editor, self).on_touch_down(touch)
            return
        if self.trace_mode and not self.trace_box.collide_point(*touch.pos) \
                and mouse_btn != 'scrolldown' and mouse_btn != 'scrollup' and mouse_btn not in ['right', 'middle']:
            return
        if mouse_btn == 'scrolldown':
            self.zoom('in')
            return
        elif mouse_btn == 'scrollup':
            self.zoom('out')
            return
        for entry in self.ids:
            widg = self.ids[entry]
            if self.trace_mode:
                if (hasattr(widg, 'group')
                        and widg.group not in ['trace', 'method']
                        and mouse_btn not in ['right', 'middle']):
                    continue
            if ((isinstance(widg, (Button, CheckBox, ScrollLabel, Slider))
                    or entry == 'save')
                    and widg.collide_point(*widg.to_widget(*touch.pos))):
                if mouse_btn != 'right' and mouse_btn != 'middle':
                    super(Editor, self).on_touch_down(touch)
                    self.update()
                self.save_state(motion_end=1)
                return True
        pos = self.scat.to_widget(*touch.pos)
        for child in self.scat.children:
            if (isinstance(child, ToggleButton) and
                    child.collide_point(*pos)):
                return self.touch_point(touch, mouse_btn, child)
        if mouse_btn == 'middle':
            self.scat.scale = 1
            return True
        if mouse_btn == 'right':
            super(Editor, self).on_touch_down(touch)
            return True
        elif self.grid.collide_point(*touch.pos):
            if not self.trace_mode:
                if not self.to_transfer:
                    self.add_point(*pos)
                else:
                    self.transfer_points()
            super(Editor, self).on_touch_down(touch)

    def touch_point(self, touch, mouse_btn, point):
        if point.state == 'down' and mouse_btn != 'right':
            point.deselect = True
        polpoi = self.pol, self.index
        super(Editor, self).on_touch_down(touch)
        if self.ctrl:
            self.pick_point(point)
        elif self.to_transfer:
            self.transfer_points(point, polpoi)

        if mouse_btn == 'right':
            point.pop_up()
        self.update()
        self.draw()
        return True

    def on_key(self, window, key, *args):
        """ What happens on keyboard press"""
        # print(key)

        if key == 119:  # W
            self.wgh_btn.state = 'down'
            self.uni_btn.state = 'normal'
            self.weighted_mode()
        if key == 117:  # U
            self.wgh_btn.state = 'normal'
            self.uni_btn.state = 'down'
            self.uniform_mode()

        if key == 305 or key == 306:  # Ctrl
            self.ctrl = True
        if key == 27:  # Esc/Back
            if self.trace_mode:
                self.cancel_trace()
                return True
            elif self.popup:
                self.dismiss_popup()
                return True
            elif self.to_transfer:
                self.save_state('Picked Points {}'
                                .format(self.to_transfer))
                self.empty_cut()
                self.save_state('Cancelled transfer')
                return True
            elif self.shortcuts.opacity:
                self.hide_keys()
                return True
            else:
                return False
        if key == 13 or key == 271:  # Enter
            if self.trace_mode:
                if self.popup:
                    self.matte = self.popup.content.clr.color
                    self.col_prmpt.color = self.popup.content.clr.color
                    self.sprite.color = self.popup.content.clr.color
                    self.make_image()
                    self.dismiss_popup()
                else:
                    self.accept_points()
            elif self.popup:
                if self.popup.title.startswith('Open'):
                    self.load_check(self.popup.content.filechooser.path,
                                    self.popup.content.filechooser.filename)
                elif self.popup.title.startswith('Save'):
                    self.save_check(self.popup.content.filechooser.path,
                                    self.popup.content.text_input.text)
                elif self.popup.title.startswith('Image'):
                    self.dismiss_popup()
                elif self.popup.title.startswith('Help'):
                    self.dismiss_popup()
                elif self.popup.title.startswith('Bounds'):
                    self.dismiss_popup()
                else:
                    for child in self.popup.content.children:
                        if isinstance(child, Label):
                            if child.text.startswith('Project'):
                                self.load_dialog()
                            elif child.text.startswith('There'):
                                self.quit()
                            elif child.text.startswith('Filename'):
                                self.save_proj()
            elif self.to_transfer:
                p = None
                if self.index:
                    point = self.rec[self.frame][
                                            self.pol]['btn_points'][self.index]
                    if not point.multi_selected:
                        p = point
                self.transfer_points(p)
            return True

        if key == 104:  # H
            if self.popup and self.popup.title.startswith('Select info'):
                self.help()
        if key == 107:  # K
            print(self.popup.title)
            if self.popup and self.popup.title.startswith('Select code'):
                self.to_clipboard(py=False)

        if key == 97:  # A
            if self.popup and self.popup.title.startswith('Multi-frame'):
                self.choose_lang()
        if key == 112:  # P
            if self.popup and self.popup.title.startswith('Select code'):
                self.to_clipboard()

        if key == 115:  # S
            if ['ctrl'] in args:
                self.save_proj()
            else:
                if self.popup and self.popup.title.startswith('Select info'):
                    self.show_keys()
                elif self.popup and self.popup.title.startswith('Multi-frame'):
                    self.choose_lang()
                else:
                    self.save_dialog()

        if self.popup:
            return True
        if key not in [273, 274, 275, 276, 303, 304, 305, 306] and self.history:
            self.save_state(motion_end=1)

        if key == 111:  # O
            if ['ctrl'] in args:
                self.load_dialog()
                return
            self.open_polygon()

        # ---------------- IF IMAGE IS PRESENT

        if key == 270 or key == 61:  # +
            # if self.trace_mode:
            #     self.minus_btn.dispatch('on_release')
            # else:
            self.zoom('in')
        if key == 269 or key == 45:  # -
            # if self.trace_mode:
            #     self.plus_btn.dispatch('on_release')
            # else:
            self.zoom('out')

        if key == 49:  # 1
            self.set_color((.29, .518, 1, 1))
        if key == 50:  # 1
            self.set_color((1, .29, .29, 1))
        if key == 51:  # 1
            self.set_color((.29, 1, .29, 1))
        if key == 52:  # 1
            self.set_color((1, 1, .29, 1))
        if key == 53:  # 1
            self.set_color((1, .29, 1, 1))
        if key == 54:  # 1
            self.set_color((.29, 1, 1, 1))

        if key == 110:  # N
            self.nums_on = not self.nums_on
            self.num_box.active = self.nums_on
            self.update()

        if key == 114:  # R
            self.unlock_order()

        if key == 101:  # E
            self.check_out()

        if key == 122:  # Z
            if ['ctrl'] in args:
                self.change_state('undo')
            if ['shift', 'ctrl'] in args:
                self.change_state('redo')

        if key == 46:  # >
            self.navigate('>')
        if key == 44:  # <
            self.navigate('<')

        if key == 307 or key == 308:  # Alt
            self.prev.text = 't'
            self.next.text = 'y'
            self.clone_points = True

        if key == 97:  # A
            if ['ctrl'] in args:
                for p, pol in (iteritems(self.rec[self.frame])):
                    for i, point in enumerate(pol['btn_points']):
                        self.to_transfer.append((p, i))
                        point.multi_selected = True
            else:
                self.add_point()

        if key == 32:  # Space
            if self.index is None:
                try:
                    self.frame, self.pol, self.index = self.lasts
                    self.rec[self.frame][self.pol]['btn_points'][self.index]\
                        .state = 'down'
                except KeyError as er:
                    print('on on_key(Space): ', er)
                return True

        if key == 273:  # up
            for point in self.to_transfer:
                curr_point = self.rec[self.frame][point[0]]['btn_points'][point[1]]
                if ['ctrl'] in args:
                    curr_point.center_y += dp(.1)
                elif ['shift'] in args:
                    curr_point.center_y += dp(10)
                else:
                    curr_point.center_y += dp(1)
                self.save_state(msg=str(self.index)
                                + '_'
                                + str(self.pol)
                                + '_'
                                + str((round(curr_point.center_x),
                                       round(curr_point.center_y))),
                                motion=1)
        if key == 274:  # down
            for point in self.to_transfer:
                curr_point = self.rec[self.frame][point[0]]['btn_points'][point[1]]
                if ['ctrl'] in args:
                    curr_point.center_y -= dp(.1)
                elif ['shift'] in args:
                    curr_point.center_y -= dp(10)
                else:
                    curr_point.center_y -= dp(1)
                self.save_state(msg=str(self.index)
                                + '_'
                                + str(self.pol)
                                + '_'
                                + str((round(curr_point.center_x),
                                       round(curr_point.center_y))),
                                motion=1)
        if key == 275:  # right
            for point in self.to_transfer:
                curr_point = self.rec[self.frame][point[0]]['btn_points'][point[1]]
                if ['ctrl'] in args:
                    curr_point.center_x += dp(.1)
                elif ['shift'] in args:
                    curr_point.center_x += dp(10)
                else:
                    curr_point.center_x += dp(1)
                self.save_state(msg=str(self.index)
                                + '_'
                                + str(self.pol)
                                + '_'
                                + str((round(curr_point.center_x),
                                       round(curr_point.center_y))),
                                motion=1)
        if key == 276:  # left
            for point in self.to_transfer:
                curr_point = self.rec[self.frame][point[0]]['btn_points'][point[1]]
                if ['ctrl'] in args:
                    curr_point.center_x -= dp(.1)
                elif ['shift'] in args:
                    curr_point.center_x -= dp(10)
                else:
                    curr_point.center_x -= dp(1)
                self.save_state(msg=str(self.index)
                                + '_'
                                + str(self.pol)
                                + '_'
                                + str((round(curr_point.center_x),
                                       round(curr_point.center_y))),
                                motion=1)

        if key == 98:  # B
            self.start_trace()

        # ---------------- IF SELECTED POINT

        if self.index is not None:
            pol = self.rec[self.frame][self.pol]
            curr_point = pol['btn_points'][self.index]

            if key == 109:  # M
                curr_point.pop_up()

            if key == 112:  # P
                self.pick_point(curr_point)

            if key == 127:  # Delete
                if ['shift'] in args or ['ctrl'] in args:
                    self.remove_polygon()
                else:
                    self.remove_point()

            if key == 32:  # Space
                if args[2]:
                    curr_point.state = 'normal'
                    if ['alt'] in args:
                        self.index = (self.index - 1) % len(pol['btn_points'])
                    if ['ctrl'] in args:
                        self.index = (self.index + 1) % len(pol['btn_points'])
                    if ['shift'] in args:
                        self.pol = str(
                            (int(self.pol) - 1) % len(self.rec[self.frame]))
                        pol = self.rec[self.frame][self.pol]
                        for apol in itervalues(self.rec[self.frame]):
                            if apol['number'] > pol['number']:
                                apol['number'] -= 1
                        pol['number'] = len(self.rec[self.frame]) - 1
                        self.index = -1
                    pol['btn_points'][self.index].on_press()
                    pol['btn_points'][self.index].on_release()
                else:
                    self.lasts = self.frame, self.pol, self.index
                    self.deselect_polygon()

            if key == 273:  # up
                if not self.to_transfer:
                    if ['ctrl'] in args:
                        curr_point.center_y += dp(.1)
                    elif ['shift'] in args:
                        curr_point.center_y += dp(10)
                    else:
                        curr_point.center_y += dp(1)
                    self.save_state(msg=str(self.index)
                                    + '_'
                                    + str(self.pol)
                                    + '_'
                                    + str((round(curr_point.center_x),
                                           round(curr_point.center_y))),
                                    motion=1)
            if key == 274:  # down
                if not self.to_transfer:
                    if ['ctrl'] in args:
                        curr_point.center_y -= dp(.1)
                    elif ['shift'] in args:
                        curr_point.center_y -= dp(10)
                    else:
                        curr_point.center_y -= dp(1)
                    self.save_state(msg=str(self.index)
                                    + '_'
                                    + str(self.pol)
                                    + '_'
                                    + str((round(curr_point.center_x),
                                           round(curr_point.center_y))),
                                    motion=1)
            if key == 275:  # right
                if not self.to_transfer:
                    if ['ctrl'] in args:
                        curr_point.center_x += dp(.1)
                    elif ['shift'] in args:
                        curr_point.center_x += dp(10)
                    else:
                        curr_point.center_x += dp(1)
                    self.save_state(msg=str(self.index)
                                    + '_'
                                    + str(self.pol)
                                    + '_'
                                    + str((round(curr_point.center_x),
                                           round(curr_point.center_y))),
                                    motion=1)
            if key == 276:  # left
                if not self.to_transfer:
                    if ['ctrl'] in args:
                        curr_point.center_x -= dp(.1)
                    elif ['shift'] in args:
                        curr_point.center_x -= dp(10)
                    else:
                        curr_point.center_x -= dp(1)
                    self.save_state(msg=str(self.index)
                                    + '_'
                                    + str(self.pol)
                                    + '_'
                                    + str((round(curr_point.center_x),
                                           round(curr_point.center_y))),
                                    motion=1)
        self.draw()

    def on_key_up(self, window, key, *args):
        if key == 307 or key == 308:  # Alt
            self.prev.text = 'e'
            self.next.text = 'r'
            self.clone_points = False
        if key == 305 or key == 306:  # Ctrl
            self.ctrl = False

# ,,,------------------------ VISUALS -----------------------
    def show_numbers(self):
        if self.rec:
            frame = self.rec[self.frame]
            if self.nums_on:
                for p, pol in iteritems(frame):
                    xs = 0
                    ys = 0
                    minx = 1000000
                    miny = 1000000
                    maxx = 0
                    maxy = 0
                    for i, point in enumerate(pol['btn_points']):
                        point.text = str(i)
                        x = point.center_x
                        xs += x
                        y = point.center_y
                        ys += y
                        if x < minx:
                            minx = x
                        if x > maxx:
                            maxx = x
                        if y < miny:
                            miny = y
                        if y > maxy:
                            maxy = y
                    label = pol['label']
                    pw, ph = (maxx - minx), (maxy - miny)
                    label.center = minx + pw * .5, miny + ph * .5
                    diag = (pw * ph) ** .5
                    label.width = pw * .33
                    label.height = ph * .33
                    label.font_size = sp(round(diag * .3))
                    label.color = pol['color'][:-1] + (.3,)
                    label.text = str(pol['key'])
                    label.opacity = 1
            else:
                for pol in itervalues(frame):
                    for point in pol['btn_points']:
                        point.text = ''
                    pol['label'].opacity = 0
            pols = [None] * len(frame)
            c = 0
            while c < len(frame):
                pols[frame[str(c)]['number']] = c
                c += 1
            self.board4.text = "Polygons' export order:\n" + str(pols)
        else:
            self.board4.text = "Polygons' export order:\n" + '[]'

    def show_history(self):
        str1 = str3 = ''
        if self.state - 1 >= -len(self.history):
            str1 = self.history[self.state - 1][0]
        if self.state + 1 < 0:
            str3 = self.history[self.state + 1][0]
        str2 = self.history[self.state][0]
        '[color=#ffffff]{}[/color]'
        self.board3.text = '[color=#444444]{}[/color]'.format(str1) \
                           + '\n' \
                           + '[color=#909090]{}[/color]'.format(str2) \
                           + '\n' \
                           + '[color=#444444]{}[/color]'.format(str3)

    def update(self):
        self.show_numbers()
        self.show_history()

        for entry in self.ids:
            if hasattr(self.ids[entry], 'group'):
                if not (self.ids[entry].group == 'nav' or entry == 'col_prmpt'):
                    self.ids[entry].disabled = False
                elif self.atlas_source:
                    if entry == 'col_prmpt':
                        self.col_back.opacity = 1
                    self.ids[entry].disabled = False
                else:
                    if entry == 'col_prmpt':
                        self.col_back.opacity = 0
                    self.ids[entry].disabled = True

        if self.trace_mode:
            self.multi_btn.disabled = False
            if self.atlas_source:
                self.all_btn.disabled = False
                self.all_chk.disabled = False
            else:
                self.all_btn.disabled = True
                self.all_chk.disabled = True

        if self.state > -len(self.history) or self.moves:
            self.undo.disabled = False
        else:
            self.undo.disabled = True

        if self.state != -1:
            self.redo.disabled = False
        else:
            self.redo.disabled = True

        if self.pol:
            pol = self.rec[self.frame][self.pol]
            if pol['open']:
                self.open_btn.text = 'Close polygon'
            else:
                self.open_btn.text = 'Open polygon'

    def hover(self, *args):
        pos = Window.mouse_pos
        if self.trace_mode:
            for entry in self.ids:
                btn = self.ids[entry]
                if hasattr(btn, 'group'):
                    if btn.group == 'trace':
                        if btn.collide_point(*pos):
                            if entry == 'multi_rel':
                                self.board2.text = 'Continue tracing until all shapes are included.'
                            elif entry == 'col_rel':
                                self.board2.text = 'Background adjustment for optimum separation ' \
                                       'in non-alpha tracing (.atlas images).'
                                self.col_prmpt.background_color = .23, .23, .3, 1
                            elif entry == 'all_rel':
                                self.board2.text = 'All frames will be processed with these settings.'
                            btn.background_color = .23, .23, .3, 1
                            return True
                        else:
                            btn.background_color = .13, .13, .2, 1
                self.board2.text = "Using image's outline to define bounds. Adjust border complexity."
            return
        for entry in self.ids:
            btn = self.ids[entry]
            if entry == 'num_btn':
                btn.background_color = 0, 0, 0, 1
                continue
            if entry.startswith(('blue', 'red_', 'green',
                                'yellow', 'magenta', 'cyan')):
                btn.background_color = btn.original_color
                continue
            if entry == 'index_btn':
                btn.background_color = (btn.norm_color if btn.state == 'normal'
                                        else btn.down_color)
                continue
            if isinstance(btn, Button):
                self.ids[entry].background_color = .13, .13, .2, 1

        if self.load_btn.collide_point(*pos):
            self.board2.text = 'Open an image, atlas or project file. ' \
                               '[Ctrl] + [O]'
            self.load_btn.background_color = .23, .23, .3, 1
            return True
        if self.save.collide_point(*pos):
            self.board2.text = 'Save current project to a project file. [S]\n' \
                               'If checked, it functions as a quick save/' \
                               'overwrite (no dialog) [Ctrl] + [S].'
            self.save_btn.background_color = .23, .23, .3, 1
            return True
        if self.help_btn.collide_point(*pos):
            self.board2.text = 'Help [F1]'
            self.help_btn.background_color = .23, .23, .3, 1
            return True
        if self.undo.collide_point(*pos):
            self.board2.text = 'Undo last action. [Ctrl] + [Z]'
            self.undo.background_color = .23, .23, .3, 1
            return True
        if self.redo.collide_point(*pos):
            self.board2.text = 'Redo last undone action. [Ctrl] + [Shift] + [Z]'
            self.redo.background_color = .23, .23, .3, 1
            return True
        if self.prev.collide_point(*pos):
            self.board2.text = "Previous frame of an atlas' sequence. [<]\n" \
                               "If [Alt] is pressed, frame's points " \
                               "REPLACE previous frame's points."
            self.prev.background_color = .23, .23, .3, 1
            return True
        if self.next.collide_point(*pos):
            self.board2.text = "Next frame of an atlas' sequence. [>]\n" \
                               "If [Alt] is pressed, frame's points REPLACE " \
                               "next frame's points."
            self.next.background_color = .23, .23, .3, 1
            return True
        if self.minus.collide_point(*pos):
            self.board2.text = 'Zoom out. [-]'
            self.minus.background_color = .23, .23, .3, 1
            return True
        if self.plus.collide_point(*pos):
            self.board2.text = 'Zoom in. [+]'
            self.plus.background_color = .23, .23, .3, 1
            return True
        if self.trace_btn.collide_point(*pos):
            self.board2.text = "Image's outline tracing. A convenient place to start. [T]"
            self.trace_btn.background_color = .23, .23, .3, 1
            return True
        if self.cancel_btn.collide_point(*pos):
            self.board2.text = 'Cancel points transfer. [Esc]'
            self.cancel_btn.background_color = .23, .23, .3, 1
            return True
        if self.rem_btn.collide_point(*pos):
            self.board2.text = 'Delete the selected point. [Delete]'
            self.rem_btn.background_color = .23, .23, .3, 1
            return True
        if self.clear_pol.collide_point(*pos):
            self.board2.text = 'Delete the selected polygon. [Shift] + [Delete]'
            self.clear_pol.background_color = .23, .23, .3, 1
            return True
        if self.open_btn.collide_point(*pos):
            self.board2.text = 'Open/close the selected polygon. [O]'
            self.open_btn.background_color = .23, .23, .3, 1
            return True
        if self.copy_btn.collide_point(*pos):
            self.board2.text = 'Export the resulting code to clipboard, ' \
                               'to use in a Rotabox widget. [E]'
            self.copy_btn.background_color = .23, .23, .3, 1
            return True
        if self.num_area.collide_point(*pos):
            self.board2.text = "Show/Hide the polygons' and points' indices. [N]"
            self.num_btn.background_color = .23, .23, .3, 1
            return True
        else:
            self.num_btn.background_color = .13, .13, .2, 1
        if self.index_btn.collide_point(*pos):
            self.board2.text = "Set the polygons' order in the exported code. [R]"
            if self.index_btn.state == 'normal':
                self.index_btn.background_color = .23, .23, .3, 1
            else:
                self.index_btn.background_color = 1, .15, .15, 1
            return True
        if self.blue_btn.collide_point(*pos):
            self.board2.text = "Set the color of the current polygon or set " \
                               "default polygon color. [1]"
            self.blue_btn.background_color = 0.59, 0.818, 1.3, 1
            return True
        if self.red_btn.collide_point(*pos):
            self.board2.text = "Set the color of the current polygon or set " \
                               "default polygon color. [2]"
            self.red_btn.background_color = 1.3, 0.59, 0.59, 1
            return True
        if self.green_btn.collide_point(*pos):
            self.board2.text = "Set the color of the current polygon or set " \
                               "default polygon color. [3]"
            self.green_btn.background_color = 0.59, 1.3, 0.59, 1
            return True
        if self.yellow_btn.collide_point(*pos):
            self.board2.text = "Set the color of the current polygon or set " \
                               "default polygon color. [4]"
            self.yellow_btn.background_color = 1.3, 1.3, 0.59, 1
            return True
        if self.magenta_btn.collide_point(*pos):
            self.board2.text = "Set the color of the current polygon or set " \
                               "default polygon color. [5]"
            self.magenta_btn.background_color = 1.3, 0.59, 1.3, 1
            return True
        if self.cyan_btn.collide_point(*pos):
            self.board2.text = "Set the color of the current polygon or set " \
                               "default polygon color. [6]"
            self.cyan_btn.background_color = 0.59, 1.3, 1.3, 1
            return True

        if self.board3.collide_point(*pos):
            self.board2.text = "History logs (previous, current and (if undo) "\
                               "next states)."
            return True
        if self.board4.collide_point(*pos):
            self.board2.text = "The order in which the polygons would be " \
                               "written if exported."
            return True
        if self.to_transfer:
            self.board2.text = ("Click on a different point to transfer the "
                                "picked points after it, or click anywhere to "
                                "make a separate new polygon [Enter]. Press "
                                "[Esc] to cancel.")
            return True
        if not self.ordered:
            self.board2.text = ("Select each polygon in the order that they need "
                                "to be in the outputed list. When finished, click "
                                "on the order button once more to lock the order "
                                "again.")
            return True
        self.board2.text = ('Click to add/select or drag to move a point. '
                            'Right click on canvas to move the image.\n'
                            'Scroll to zoom. Middle click to reset zoom.')

    def set_color(self, color, *args):
        if self.pol:
            self.rec[self.frame][self.pol]['color'] = tuple(color)
            self.update()
            self.draw()
        else:
            self.default_color = color

    def draw(self):
        self.draw_group.clear()
        if not self.rec:
            self.rec = {'0': {}}
        for pol in itervalues(self.rec[self.frame]):
            points = pol['btn_points']
            for i in range(len(points)):
                if not pol['open']:
                    k = (i + 1) % len(points)
                else:
                    k = i + 1 if i + 1 < len(points) else i

                self.draw_group.add(Color(*pol['color']))
                self.draw_group.add(Line(points=(points[i].center_x,
                                                 points[i].center_y,
                                                 points[k].center_x,
                                                 points[k].center_y),
                                         width=self.line_width))
                self.draw_group.add(Color(0, 0, 0, 1))
                self.draw_group.add(Line(points=(points[i].center_x,
                                                 points[i].center_y,
                                                 points[k].center_x,
                                                 points[k].center_y),
                                         dash_offset=2,
                                         dash_length=1))
                self.draw_group.add(Color(1, 1, 1, 1))
                self.draw_group.add(Line(circle=(points[i].center_x,
                                                 points[i].center_y,
                                                 self.mag - 1.8)))
                self.draw_group.add(Color(0, 0, 0, 1))
                self.draw_group.add(Line(circle=(points[i].center_x,
                                                 points[i].center_y,
                                                 self.mag - 2)))

    def zoom(self, btn):
        if btn == 'in':
            if self.scat.scale < 10:
                self.scat.scale += 0.5
                self.adjust_points()
        elif btn == 'out':
            if self.scat.scale > 0.4:
                self.scat.scale -= 0.3
                self.adjust_points()

    def adjust_points(self):
        for chld in self.scat.children:
            if isinstance(chld, Button):
                chld.scale = 1.5 / self.scat.scale + .1

# ,,,----------------------- UTILS --------------------------
    @staticmethod
    def sanitize_filename(filename):
        """ Creates a safe filename from the text input
        of the 'Save File' dialog.
        """
        filename = re.sub(r'[/:*?"<>|\\]', "_", filename)
        return filename

    def warn(self, title, text, action, cancel=1, tcolor=(1, .1, .1, 1)):
        """ Opens a dialog with a warning"""
        content = BoxLayout(orientation='vertical')
        label = Label(halign='center')
        label.text = text
        content.add_widget(label)

        buttons = BoxLayout(size_hint=(1, .4))

        if cancel:
            cancel_btn = Button(background_color=(.13, .13, .2, 1),
                                on_release=self.dismiss_popup)
            cancel_btn.text = 'Cancel'
            buttons.add_widget(cancel_btn)

        ok_btn = Button(background_color=(.13, .13, .2, 1),
                        on_release=action)
        ok_btn.text = 'OK'
        buttons.add_widget(ok_btn)

        content.add_widget(buttons)
        title_color = tcolor
        self.popup = AutoPopup(title_align='center', content=content,
                               title_size='18sp',
                               title_color=title_color,
                               size_hint=(None, None),
                               size=(dp(440), dp(240)))
        self.popup.title = title
        self.popup.open()

    def dismiss_popup(self, *args):
        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def exit_check(self, *args, **kwargs):
        copied = True
        if self.changes > 1:
            self.write()
            if self.code not in ('custom_bounds = []',
                                 'custom_bounds:\n            []',
                                 'custom_bounds = {}',
                                 'custom_bounds:\n            {}'):
                clip = self.code if not PYTHON2 else self.code.decode('utf-8')
                if Clipboard.paste() != clip:
                    copied = False

            self.warn('Warning!', 'There are unsaved changes.\n'
                      'Exit anyway?' if copied
                      else 'There are unsaved changes.\n'
                      "There are also changes, not exported to clipboard.\n "
                      "Exporting to clipboard is the only way to generate the\n"
                      "code needed to define this editor's bounds in Rotabox.\n"
                      'Exit anyway?', self.quit)
            return True
        else:
            self.quit()

    def quit(self, *args):
        self.changes = 0
        App.get_running_app().on_stop()
        sys.exit()

    def save_window(self):
        """ Saves the json based configuration settings
        """
        config = {'width': Window.width,
                  'height': Window.height,
                  'left': Window.left,
                  'top': Window.top,
                  'last dir': self.last_dir}
        try:
            with open('rotaboxer/settings.json', 'w+', encoding="UTF8") as settings:
                json.dump(config, settings)
        except IOError as er:
            print('On save_window: ', er)

    def select_help(self, *args):
        popup = BoxLayout(orientation='vertical')

        help_btn = Button(background_color=(.13, .13, .2, 1),
                          on_release=self.help)
        help_btn.text = 'Help'
        popup.add_widget(help_btn)

        keys_btn = Button(background_color=(.13, .13, .2, 1),
                          on_release=self.show_keys)
        keys_btn.text = 'Keyboard shortcuts'
        popup.add_widget(keys_btn)

        self.popup = AutoPopup(content=popup,
                               size_hint=(None, None),
                               size=(dp(240), dp(150)))
        self.popup.title = 'Select info:'
        self.popup.open()

    def show_keys(self, *args):
        self.dismiss_popup()
        self.board1.opacity = 0
        self.board2.opacity = 0
        self.board3.opacity = 0
        self.board4.opacity = 0
        self.mask.opacity = 1
        self.shortcuts.opacity = 1
        self.key_lbl.text = '''
{0}Add point{2}: {1}{0}[A]{2}{3}
{0}Point menu{2}: {1}{0}[M]{2}{3}

{0}Deselect{2}/{0}Reselect{2}: {1}{0}[Space]{2}{3}
Select next point {1}{0}[Ctrl + Space]{2}{3}
Select previous point {1}{0}[Alt + Space]{2}{3}
Select previous polygon {1}{0}[Shft + Space]{2}{3}

{0}Move point{2}: {1}{0}[Arrows]{2}{3}
Fast {1}{0}[Shft + Arrows]{2}{3}
Fine {1}{0}[Ctrl + Arrows]{2}{3}

{0}Transfer points to another polygon{2}:
Pick point {1}{0}[Ctrl + Click]{2}{3}
Pick selected point {1}{0}[P]{2}{3}
Transfer picked points {1}{0}[Enter]{2}{3}

{0}Dialog Cancel{2}: {1}{0}[Esc]{2}{3}
{0}Dialog OK{2}: {1}{0}[Enter]{2}{3}
        '''.format('[color=#ffffff]', '[size=19]', '[/color]', '[/size]')

    def hide_keys(self):
        self.board1.opacity = 1
        self.board2.opacity = 1
        self.board3.opacity = 1
        self.board4.opacity = 1
        self.mask.opacity = 0
        self.shortcuts.opacity = 0

    def help(self, *args):
        self.dismiss_popup()
        content = BoxLayout(orientation='vertical')
        scrl_label = ScrollLabel()
        scrl_label.label.padding_x = dp(10)
        scrl_label.scroll_y = 1
        scrl_label.label.font_size = '18sp'
        scrl_label.label.markup = True
        scrl_label.text = '''
{0}{5}[b]Rotaboxer  {8}[/b]{7}{4}

Rotaboxer is an editing tool for the Rotabox collision bounds.
With an image as input, specific bounds can be visually shaped for it, to export as code to clipboard and use as {0}custom bounds{4} of a Rotabox widget, in a kivy project.
Animated bounds are also supported, with the use of .atlas files.

{0}{5}Usage{7}{4}
This document is complementary to the editor's {0}tooltips{4} and the {0}Keyboard shortcuts{4} document.
It's a short desciption of the process with special notes where things may not be apparent.

{0}{6}Opening an image {7}{4}or an image{0}{6} sequence{7}{4}
Open a {0}.png{4} or {0}.atlas{4} file, with the image(s) the resulting bounds are meant for.

{0}{6}Adding bounds automatically {7}{4}using image's outline
{0}Auto bounds{4} button starts an alpha tracing (or color tracing in the case of an .atlas image) to determine the image's outline and brings up an interface to control the accuracy/complexity of the result.
{0}Matte color{4} button allows adjustment of the background color that will be added for the tracing of an .atlas image. It needs to be clearly distinguishable from the image's outline.
{0}All shapes{4} checkbox switches between stopping the tracing after the first encountered shape (to avoid transparency islands inside a single-shaped image) and continuing the tracing to include all shapes (of a multi-shaped image).
If {0}All frames{4} is checked, {0}Accept{4} button will process the entire animation with the current settings.

{0}{6}Adding points to form polygons{7}{4}
New points are added by {0}clicking{4} on the workspace.
Each new point is spawn connected to the currently selected point and after it, in terms of index numbers. Any indices after the selected will shift.
If no point is selected, the new point will start a new polygon.

{0}{6}Selecting a point/polygon{7}{4}
{0}Click{4} on a point to select/deselect it.
When selecting a point, the encompassing polygon is selected too.
(See {0}Keyboard shortcuts{4} for selection conveniences).

{0}{6}Moving a point{7}{4}:
A point can be moved by {0}Clicking & dragging{4} it, or by using the {0}keyboard arrows{4}.

{0}{6}Reordering polygons{7}{4}:
If {0}Order polygons{4} is pressed, the polygons can be selected, consecutively, in the (intended) exporting order.
{0}Note{4} that their displayed number doesn't change but their order does (watch the label bottom-right corner of the workarea).
{0}Important{4}: The order that the polygons will be written in the resulting {0}custom_bounds{4} list will be the order in which polygons are going to be considered during collision checks in Rotabox.

{0}{6}Transfering points to another polygon{7}{4}:
Not to be confused with a positional transfer, this is only a linkage change; an exchange between polygons' vertices.
A point can be picked by {0}Ctrl + clicking{4} on it.
When the desired points are picked, they can be attached to another polygon by {0}clicking on one of its points{4}. They will be added after the clicked point in the order they were picked.
Alternatively, they can form a {0}new polygon{4} by {0}clicking anywhere{4} in the workspace.

{0}{6}Exporting the bounds{7}{4}.
The Rotaboxer output, is the resulting code of {0}Export bounds{4} which is copied to the {0}clipboard{4}, to be used in a Rotabox widget.
There's an option for {0}python{4} syntax or {0}kvlang{4} syntax (due to the indentation differences).
If an {0}.atlas{4} file is being used, there is an option to determine whether it is an animation sequence. If it is an animation, the exported bounds of {0}all frames{4} will be a dictionary. Else, the exported bounds will be a list, concerning only the {0}current frame{4}.

{0}{6}Zooming in / out the workspace{7}{4}:
{0}Middle click{4} anywhere on the workspace to go back to the normal view.

{0}{6}Moving the image{7}{4}:
{0}Right click & drag{4} to move the image.

{0}{6}Cloning points between frames{7}{4}:
While advancing through an atlas' images using the screen buttons or the {0}[<]/[>]{4} keys, the points of the current frame can be {0}cloned{4} to the next, using the {0}[Alt]{4} key, together with the aforementioned buttons or keys.
{0}Warning{4}: The points of the current frame {0}will replace{4} any points on the next.

{0}{6}Saving a project{7}{4}:
A project file should be kept with the involved image file, to be able to open.
If not in Windows and the user exits the editor without saving changes (not because of a crash), no save prompt is displayed. Instead, the project is automatically saved at the project's (or image's) location, as '<project (or image) name>_RESCUED_.bounds'.

        '''.format('[color=#ffffff]', '[color=#cc9966]', '[color=#9999ff]',
                   '[color=#729972]', '[/color]', '[size=25]', '[size=20]',
                   '[/size]', __version__)
        content.add_widget(scrl_label)

        ok_btn = Button(background_color=(.13, .13, .2, 1),
                        size_hint=(1, .1),
                        on_press=self.dismiss_popup)
        ok_btn.text = 'OK'
        content.add_widget(ok_btn)

        self.popup = AutoPopup(title_align='center', content=content,
                               size_hint=(1, 1),
                               title_size='18sp')
        self.popup.title = 'Help'
        self.popup.open()

# ,,,--------------------- IMAGE-TRACING -----------------------
    def start_trace(self):
        '''
        Deselecting and removing any Points from current frame,
        revealing the trace-GUI and wait-animation, and starting the image
        tracing in a thread.
        '''
        self.pol = None
        for pol in itervalues(self.rec[self.frame]):
            while len(pol['btn_points']):
                self.scat.remove_widget(pol['btn_points'].pop())
            self.scat.remove_widget(pol['label'])
        self.rec[self.frame].clear()
        self.trace_box.x = dp(5)
        self.trace_mode = True
        self.update()
        self.draw()

        self.busy.opacity = 1

        t = Thread(target=self.trace_image)
        t.daemon = True
        t.start()

    def make_image(self, *args):
        '''
        Exporting the Image of the current frame to a .png file, using it to
        make a new Image with keep_data=True to replace the one with the .atlas
        source and restarting the trace.
        '''

        # If it's a remake, after a change of the background color
        if self.popup:
            self.dismiss_popup()
            self.frame = self.orig_source[1]
            self.sprite.image.canvas.after.clear()

        self.temp_img = 'temp_' + self.image.split('.')[0] \
                        + self.frame + '.' + str(time.time()) + '.png'
        self.sprite.export_to_png(self.temp_img)

        newimage = KDImage(pos=self.sprite.image.pos, source=self.temp_img,
                           keep_data=True)
        self.sprite.remove_widget(self.sprite.image)
        self.sprite.add_widget(newimage)
        self.sprite.image = newimage

        Clock.schedule_once(self.retrace)

    def retrace(self, *args):
        '''
        Another start_trace with less preparation.
        '''
        self.sprite.image.canvas.after.clear()
        self.busy.opacity = 1

        t = Thread(target=self.trace_image)
        t.daemon = True
        t.start()

    def trace_image(self, *args):
        '''
        Detecting opaque areas in an image and keeping their outlines.
        '''
        read_pixel = self.sprite.image._coreimage.read_pixel

        # If image source is an .atlas file, an exception will be raised
        # (read_pixel doesn't work on .atlas files) and a background color will
        # be added to the image, to make it ready for an export to a substitude
        # .png, suitable for color tracing (export_to_png doesn't keep the alpha
        # channel). The new .png will then pass this test.
        try:
            test = read_pixel(0, 0)
        except AttributeError:
            self.orig_source = self.sprite.image.source, self.frame
            self.col_prmpt.color = self.matte
            self.sprite.color = self.matte
            Clock.schedule_once(self.make_image)
            return

        image = self.sprite.image

        # Detecting opaque pixels (or pixels distinguishable from the given
        # background) and giving them a value of 1 (instead of 0) in a matrix
        # representation of the image.
        shadow = []
        for x in range(int(image.width)):
            shadow.append([])
            for y in range(int(image.height)):
                pix_clr = read_pixel(x, int(image.height) - y - 1)

                if self.orig_source is None:
                    shadow[x].append(1 if pix_clr[-1] else 0)
                else:  # substitude .png
                    shadow[x].append(1 if pix_clr != test else 0)

        # Restoring the .atlas source and deleting the substitude .png
        if self.orig_source:
            self.sprite.color = tuple(self.matte[:-1]) + (0.0,)
            self.sprite.image.source = self.orig_source[0]
            try:
                os.remove(self.temp_img)
            except EnvironmentError:
                pass

        # Keeping the contour (outline) of the opaque area:
        # Only 1-points that border to 0-points keep their value, while they are
        # being transfered to the 'contour' matrix.
        contour = []
        for x in range(len(shadow)):
            contour.append([])
            for y in range(len(shadow[0])):
                if shadow[x][y]:
                    if not x or not y:
                        contour[x].append(1)
                        continue
                    try:
                        if not shadow[x][y - 1]:
                            contour[x].append(1)
                            continue

                        if not shadow[x][y + 1]:
                            contour[x].append(1)
                            continue

                        if not shadow[x - 1][y]:
                            contour[x].append(1)
                            continue

                        if not shadow[x + 1][y]:
                            contour[x].append(1)
                            continue
                    except IndexError:
                        contour[x].append(1)
                        continue

                contour[x].append(0)

        # Converting the 'contour' matrix to one or more lists of points [x, y]
        # representing polygon borders.
        self.make_border(contour)

    def make_border(self, contour, *args):
        '''
        Linking the points of the contour to form a border for each of the
        possible different shapes in the image, clearing the patterns
        representing straight lines of different angles in the dense
        (axis-aligned) contour and giving a first go to simplify the border
        with the default threshold, before letting the user take control.
        '''
        shapes = []
        found = []
        broken = False

        # Finding a starting point on the contour for each shape's border.
        # contour is still a two-dimentional matrix of 1s and 0s.
        for x in range(len(contour)):
            for y in range(len(contour[0])):
                if contour[x][y] and [x, y] not in found:
                    border = self.link_points(contour, x, y, found)

                    if len(border) > MIN_SHAPE:
                        shapes.append(border)

                    # no need to continue if image consists of a single shape.
                    if not self.multi_shape:
                        broken = True
                        break
            if broken:
                break

        # removing the patterns representing straight lines
        for shape in shapes:
            self.clear_patterns(shape)

        # utility variable for the GUI
        self.complexity = max(int(round(sum([len(shp) for shp in shapes]) * .03)), 3)

        self.simple_border = shapes

        # an initial filtering, using the default threshold value
        self.filter_border(self.trace_box.thres)

    @staticmethod
    def link_points(line, x, y, found, *args):
        '''
        Consecutive contour points' linking to a border chain.
        :param line: list (the contour)
        :param x: int
        :param y: int (coords of a new point with value 1)
        :param found: list (the already found points)
        :return: list (the points of a new border)
        '''
        border = []
        intersections = []
        first = [x, y]

        while [x, y] not in border:
            # previous iteration's candidate as the next border point
            border.append([x, y])
            found.append([x, y])

            up = [x, y + 1] if y + 1 < len(line[0]) else [x, y]
            upright = [x + 1, y + 1] if x + 1 < len(line) \
                                       and y + 1 < len(line[0]) else [x, y]
            right = [x + 1, y] if x + 1 < len(line) else [x, y]
            downright = [x + 1, y - 1] if x + 1 < len(line) and y > 0 else [x, y]
            down = [x, y - 1] if y > 0 else [x, y]
            downleft = [x - 1, y - 1] if x > 0 and y > 0 else [x, y]
            left = [x - 1, y] if x > 0 else [x, y]
            upleft = [x - 1, y + 1] if x > 0 and y + 1 < len(line[0]) else [x, y]

            candidates = []
            # looking around to find a candidate for the next border point
            for [j, k] in [up, upright, right, downright, down, downleft, left,
                           upleft]:

                # if back where we started and border is of sufficient length
                if [j, k] == first and len(border) > MIN_SHAPE:
                    return border

                # if point is opaque and new
                if line[j][k] and [j, k] not in found:
                    candidates.append([j, k])

            # if no new opaque point in the vicinity, we're backtracking
            if not candidates:
                try:
                    while True:
                        # undoing what's done since the last intersection
                        while len(border) > intersections[-1][0]:
                            border.pop()
                        else:
                            break
                    # another candidate tries as the next border point
                    x, y = intersections[-1][1].pop(0)
                    if not intersections[-1][1]:
                        intersections.pop()
                    continue
                except IndexError:
                    # no more intersections and nowhere to go. return border
                    break

            # if more than one path
            if len(candidates) > 1:
                # keeping the point of intersection and the alternative paths
                intersections.append([len(border), candidates[1:]])

            # the first candidate tries as the next border point
            x, y = candidates[0]

        return border

    def clear_patterns(self, border, *args):
        '''
        Detects and clears the patterns representing straight lines
        of different angles in the dense (axis-aligned) border.
        The idea is that a pattern is always in the form of two consecutive
        elements:
        a) a group of (one-pixel, same-angle) segments of some angle and
        b) a group of segments of a different angle.
        So, by measuring the angles and counting same-angle segments,
        two-element patterns emerge and are cleared as long as they repeat.
        Consecutive same-angle segments are also cleared in the process.

        :param border: list of points
        '''
        simple_border = []
        pattern = []
        count = 0
        previous_angle = None
        temp = []

        for i in range(len(border)):
            pt = border[i]
            nextp = border[(i + 1) % len(border)]
            angle, distance = self.calc_segment(nextp, pt)

            if previous_angle is None:
                simple_border.append(pt)  # keeping the very first point
                previous_angle = angle  # establishing new element's angle
                count = 1  # first point of new element
                continue

            if angle == previous_angle:  # an element continues

                # If a repeating element just completed with the previous point,
                # current point is kept and pattern is reset
                # (starting element doesn't fit the existing pattern)
                if len(pattern) == 2 and pattern[0] == [angle, count]:
                    simple_border.append(pt)
                    temp = []
                    del pattern[:]
                    count = 1  # first count of new element
                    continue

                count += 1   # continuing the element

            else:  # an element completed

                if len(pattern) == 2:  # if a pattern already exists,

                    # the complete element compares to the first element
                    # to determine repetition
                    if pattern[0][0] == previous_angle and pattern[0][1] >= count:

                        # If the repeating pattern doesn't use the whole element
                        # the pattern's first point is found and kept
                        if pattern[0][1] > count:
                            simple_border.append(border[temp[0][0] + (count - 1)])

                    # If repetition stops, the first element's candidate is kept
                    else:
                        simple_border.append(temp[0][1])

                    pattern.pop(0)  # first element removed (so second is first)
                    temp.pop(0)
                pattern.append([previous_angle, count]) # complete element added
                temp.append([i, pt])  # new element's first point as a candidate
                previous_angle = angle  # establishing new element's angle
                count = 1  # starting point-counting of the new element

            # when in last iteration the remaining points in temp are added
            # because, while they were never checked for a pattern, they still
            # represent angle changes.
            if i == len(border) - 1:
                simple_border += [p[1] for p in temp]

        border[:] = simple_border

    @mainthread
    def filter_border(self, thres, *args):
        '''
        Simplifying the border by eliminating the less critical points.
        If a point, assuming a segment between its left and right neighbors,
        is closer to the segment than the threshold value, it is left behind.

        :param thres: float (distance threshold)
        '''
        shapes = self.simple_border[:]
        pols = []
        points = 0
        for shape in shapes:
            curr_border = shape
            points2 = 0
            points3 = 0
            # More iterations with a lower threshold give a better result,
            # since the reference point of a check can then be checked too.
            # However there is a limit of iterations after which, no difference
            # is made.
            # For small images (~300x300) this limit is 3 or 4.
            # For long straight lines (~600 pixels) is around 9.
            # Default value is 10.
            # Threshold is controlled by the user.
            for p in range(FILTER_PASSES):
                skip = False
                simpler_border = []
                points3 = 0
                for i, pt in enumerate(curr_border):
                    if skip:
                        skip = False
                        continue
                    nextp = curr_border[(i + 1) % len(curr_border)]
                    nexter = curr_border[(i + 2) % len(curr_border)]
                    next_angle, next_dist = self.calc_segment(nexter, pt)

                    # axis-aligning the imaginary segment between pt and nexter
                    # (make it parallel to the x axis), to make its distance to
                    # nextp equal to the difference between pt's y and nextp's y
                    pts = self.rotate2axis([pt[0], pt[1], nextp[0], nextp[1]],
                                           -next_angle)

                    simpler_border.append(pt)
                    points3 += 1

                    # checking if the next point should be skipped
                    if abs(pts[3] - pts[1]) < thres:
                        skip = True
                curr_border = simpler_border

            points2 += points3
            pols.append(curr_border)
            points += points2

        self.simplest_border = pols

        self.sprite.image.canvas.after.clear()
        for pol in pols:
            self.draw_border(self.sprite.image, pol, close=True)
        self.counter.text = str(points) + ' points'

        self.busy.opacity = 0
        if self.all_go:
            self.accept_points()

    def accept_points(self):
        if self.orig_source:
            self.frame = self.orig_source[1]
            self.orig_source = None

        self.sprite.image.canvas.after.clear()

        for i, pol in enumerate(self.simplest_border):
            polygon = self.rec[self.frame][str(i)] = {}
            polygon['key'] = i
            polygon['number'] = i
            polygon['color'] = self.default_color
            polygon['label'] = Label(size=(dp(50), dp(50)), font_size='35sp', bold=True,
                                     color=polygon['color'][:-1] + (.3,))
            self.scat.add_widget(polygon['label'])
            polygon['open'] = False
            polygon['btn_points'] = [Point(polygon, self, self.mag, text=str(i),
                                           pos=(point[0] + self.sprite.x,
                                                point[1] + self.sprite.y))
                                     for i, point in enumerate(pol)]
            for i in range(len(polygon['btn_points'])):
                point = polygon['btn_points'][i]
                self.scat.add_widget(point)
                point.area_color = point.norm_fill_color
                point.line_color = point.norm_line_color

        self.done += 1
        if not self.all_frames or len(self.keys) == self.done:
            self.save_state('Auto-trace of frame {:02d}'.format(int(self.frame) + 1)
                            + ': ' + str(len(self.simplest_border)) + ' points')
            Clock.schedule_once(self.reset_trace)
        else:
            # continuing a loop to process all frames
            self.all_go = True  # filter_border will call us again
            self.navigate('>')
            self.start_trace()

    def cancel_trace(self):
        if self.orig_source:
            self.frame = self.orig_source[1]
            self.orig_source = None

        self.sprite.image.canvas.after.clear()

        self.save_state('temp')
        self.change_state('undo')
        self.history.pop()
        self.state = -1
        Clock.schedule_once(self.reset_trace)

    def reset_trace(self, *args):
        self.trace_box.x = dp(-148)
        self.trace_mode = False
        self.all_frames = False
        self.all_chk.active = False
        self.all_go = False
        self.done = 0
        self.update()
        self.draw()

    def open_color(self):
        prompt = ColorDialog()
        prompt.matte = self.matte
        prompt.clr.color = self.matte
        self.popup = AutoPopup(title_align='center', content=prompt,
                               title_size='18sp',
                               title_color=(1, .1, .1, 1),
                               size_hint=(None, None),
                               size=(dp(480), dp(350)))
        self.popup.title = 'Non-alpha tracing matte color'
        self.popup.open()

    def change_color(self):
        '''
        Delaying to make sure the new color will be there for the export_to_png
        :return:
        '''
        Clock.schedule_once(self.make_image)

    @staticmethod
    def calc_segment(nextp, this):
        dx = nextp[0] - this[0]
        dy = nextp[1] - this[1]
        distance = int(round(math.hypot(dx, dy)))
        angle = int(round(math.degrees(math.atan2(dy, dx)))) % 360
        return angle, distance

    @staticmethod
    def rotate2axis(points, angle):
        '''
        Rotating the relation between two points.
        :param points: list of points in the form of [x1, y1, x2, y2]
        :param angle: float angle in degrees
        :return:
        '''
        pts = points[:]
        orig0 = pts[2]
        orig1 = pts[3]
        angle = math.radians(angle)
        c = math.cos(angle)
        s = math.sin(angle)

        for j in [0, 2]:
            pts[j] = pts[j] - orig0
            pts[j + 1] = pts[j + 1] - orig1
            pj = pts[j]
            pts[j] = pj * c - pts[j + 1] * s
            pts[j + 1] = pj * s + pts[j + 1] * c
            pts[j] = pts[j] + orig0
            pts[j + 1] = pts[j + 1] + orig1
        return pts

    def delay_draw(self, border, *args):
        self.sprite.image.canvas.after.clear()
        self.draw_border(self.sprite.image, border, close=True)

    @staticmethod
    def draw_border(image, pts, col=0, close=False, pt_draw=True):
        colors = [(1, 0, 1, 1), (0, 1, 1, 1), (1, 1, 0, 1)]
        points = [[p[0] + image.x, p[1] + image.y] for p in pts]
        with image.canvas.after:
            Color(rgba=colors[col % len(colors)])
            Line(points=[c for pt in points for c in pt], close=close)
            if pt_draw:
                Color(rgba=colors[1])
                for pt in points:
                    Line(circle=(pt[0], pt[1], dp(.5)))


class ScattBack(ScatterPlane):

    def apply_transform(self, trans, post_multiply=False, anchor=(0, 0)):
        '''Overriding, to have the anchor in window center'''
        super(ScattBack, self).apply_transform(trans, post_multiply=False,
                                               anchor=(Window.width * .6,
                                                       Window.height * .5))


class Sprite(BoxLayout):
    def __init__(self, **kwargs):
        super(Sprite, self).__init__(**kwargs)
        self.image = None

    def on_size(self, *args):
        self.x -= self.size[0] * .5
        self.y -= self.size[1] * .5


class TraceBox(BoxLayout):

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super(TraceBox, self).on_touch_down(touch)
            return True


class AutoPopup(Popup):
    '''Subclassing, to compensate if Esc key was used to close a popup.
    Seems that by (automatically) closing the popup, Esc consumes the event
    before completing the task to empty the self.popup variable.'''
    def on_dismiss(self, *args):
        for child in Window.children:
            if isinstance(child, Editor) and child.popup:
                child.popup = None


class ColorDialog(BoxLayout):
    pass


class ScrollLabel(ScrollView):
    """ A scrolling label with translation and background color options
    """
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(ScrollLabel, self).__init__(**kwargs)
        self.scroll_type = ['bars', 'content']
        self.bar_color = (.3, .3, .4, .35)
        self.bar_inactive_color = (.3, .3, .4, .15)
        self.bar_width = dp(10)
        self.scroll_wheel_distance = dp(50)


# noinspection PyIncorrectDocstring
def folder_sort(files, filesystem):
    """ Sorts the files and folders in the 'File Dialogs' popups.
    Used in the FileChooserListViewX class
    """
    return (sorted((f for f in files if filesystem.is_dir(f)), key=sorting) +
            sorted((f for f in files if not filesystem.is_dir(f)), key=sorting))


def sorting(item):
    return item[0].upper() if type(item) == list else item.lower()


def get_win_drives():
    """ Finds the drive letters in Windows OS.
    """
    if platform == 'win':
        import win32api
        # noinspection PyUnresolvedReferences
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        return drives
    else:
        return []


# noinspection PyIncorrectDocstring,PyArgumentList
class LoadDialog(BoxLayout):
    """ 'Load File' popup dialog.
    """
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    file_types = ListProperty(['*.*'])
    text_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self.filechooser.path = './'
        self.create_drives()

    def create_drives(self):
        """ Creates the Drive list in Windows OS.
        """
        for i in get_win_drives():
            btn = DarkButton()
            btn.text = i
            btn.bind(on_press=self.on_drive_selected)
            self.ids.drives_list.add_widget(btn)
        self.ids.drives_list.add_widget(Label())  # add empty space under the drives

    def on_drive_selected(self, *args):
        """ Changes the current drive letter in Windows OS.
        """
        try:
            selected_drive = args[0].text
        except IndexError:
            return
        self.filechooser.path = selected_drive


# noinspection PyIncorrectDocstring,PyArgumentList
class SaveDialog(BoxLayout):
    """ 'Save File' popup dialog.
    """
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    file_types = ListProperty(['*.*'])
    text_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SaveDialog, self).__init__(**kwargs)
        self.filechooser.path = './'
        self.create_drives()

    def create_drives(self):
        """ Creates the Drive list in Windows OS.
        """
        for i in get_win_drives():
            btn = DarkButton(text=i)
            btn.bind(on_press=self.on_drive_selected)
            self.ids.drives_list.add_widget(btn)
        self.ids.drives_list.add_widget(Label())  # add empty space under the drives

    def on_drive_selected(self, *args):
        """ Changes the current drive letter in Windows OS.
        """
        try:
            selected_drive = args[0].text
        except IndexError:
            return
        self.filechooser.path = selected_drive


class FileChooserListViewX(FileChooserListView):
    """ Overrides the sorting method of the FileChooserListView class.
    """
    sort_func = ObjectProperty(folder_sort)


class DarkButton(ToggleButton):
    """ Makes the drive letter buttons Dark Grey."""


class Rotaboxer(App):
    texture = ObjectProperty()

    def build(self):
        self.use_kivy_settings = False
        img = Image()
        img.source = 'rotaboxer/grid.png'
        self.texture = img.texture
        self.texture.wrap = 'repeat'
        self.texture.uvsize = (8, 8)
        Builder.load_file('rotaboxer/rotaboxer.kv')
        return Editor()

    def _on_keyboard_settings(self, window, *largs):
        key = largs[0]
        setting_key = 282  # F1/Menu

        if key == setting_key:  # toggle settings panel
            self.root.select_help()
            return True

    def on_stop(self):
        if self.root.changes > 1:
            self.root.exit_save()
        self.root.save_window()


def error_print():
    """ Appends the current error to the log text."""
    with open("rotaboxer/err_log.txt", "a", encoding="UTF8") as log:
        log.write('\nCrash@{}\n'.format(time.strftime(str("%Y-%m-%d %H:%M:%S"))))
    traceback.print_exc(file=open("rotaboxer/err_log.txt", "a"))
    traceback.print_exc()


try:
    Rotaboxer().run()
except Exception:
    error_print()
