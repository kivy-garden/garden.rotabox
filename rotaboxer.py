# coding=utf-8

'''
                                                    kivy 1.9.0 - python 2.7.10
ROTABOXER
____________________ RUN THE MODULE DIRECTLY TO USE ___________________________

    Rotaboxer is an editing tool for the Rotabox bounds*.
    With an image as input, the user can visually shape specific colliding
    bounds for it.

    The result is the code (a list or a dictionary) to be used by a Rotabox
    widget, in a kivy project.

    Animated bounds are also supported, with the use of atlases.
    Rotaboxer lets you browse through the individual frames of a sequence
    and define different bounds for each one.

   *___________________________________________________________________________
    To understand the concept of the Rotabox collision detection, you can refer
    to its module's documentation.

unjuan 2016
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import json

app_config = {}
try:
    with open('settings.json', 'r') as app_settings:
        app_config = json.load(app_settings)
except (IOError, KeyError) as err:
    print('on loading settings', err)
    pass

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'width', app_config.get('width', 580))
Config.set('graphics', 'height', app_config.get('height', 720))
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.clipboard import Clipboard
from rotabox import Rotabox
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.uix.popup import Popup
from kivy.app import platform
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.listview import ListItemButton
from kivy.graphics.instructions import InstructionGroup
from collections import deque
import base64
import re
import os
import sys
import traceback
import time

__author__ = 'unjuan'
__version__ = '0.9.0'


class ScrollLabel(ScrollView):
    """ A scrolling label with translation and background color options
    """
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(ScrollLabel, self).__init__(**kwargs)
        self.scroll_type = ['bars', 'content']
        self.bar_color = [.3, .4, .3, .35]
        self.bar_inactive_color = [.3, .4, .3, .15]
        self.bar_width = '10dp'


def folder_sort(files, filesystem):
    """ Sorts the files and folders in the 'File Dialogs' popups.
    Used in the FileChooserListViewX class
    """
    return (sorted((f for f in files if filesystem.is_dir(f)), key=sorting) +
            sorted((f for f in files if not filesystem.is_dir(f)), key=sorting))


def sorting(item):
    return item[0].upper() if type(item) == list else item.lower()


class FileChooserListViewX(FileChooserListView):
    """ Overrides the sorting method of the FileChooserListView class.
    """
    sort_func = ObjectProperty(folder_sort)

    def __init__(self, **kwargs):
        super(FileChooserListViewX, self).__init__(**kwargs)


class DarkButton(ListItemButton):
    """ Makes the drive letter buttons Dark Grey.
    """

    def __init__(self, **kwargs):
        super(DarkButton, self).__init__(**kwargs)


class LoadDialog(FloatLayout):
    """ 'Load File' popup dialog."""

    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    file_types = ListProperty(['*.*'])
    text_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self.drives_list.adapter.bind(
            on_selection_change=self.drive_selection_changed)
        self.filechooser.path = './'

    @staticmethod
    def get_win_drives():
        """ Finds the drive letters in Windows OS.
        """
        if platform == 'win':
            import win32api
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            return drives
        else:
            return []

    def drive_selection_changed(self, *args):
        """ Changes the current drive letter in Windows OS.
        """
        try:
            selected_item = args[0].selection[0].text
        except IndexError:
            return
        self.filechooser.path = selected_item


class SaveDialog(FloatLayout):
    """ 'Save File' popup dialog."""

    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    file_types = ListProperty(['*.*'])
    text_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SaveDialog, self).__init__(**kwargs)
        self.drives_list.adapter.bind(
            on_selection_change=self.drive_selection_changed)
        self.filechooser.path = './'

    @staticmethod
    def get_win_drives():
        """ Finds the drive letters in Windows OS.
        """
        if platform == 'win':
            import win32api
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            return drives
        else:
            return []

    def drive_selection_changed(self, *args):
        """ Changes the current drive letter in Windows OS.
        """
        try:
            selected_item = args[0].selection[0].text
        except IndexError:
            return
        self.filechooser.path = selected_item


class Sprite(Rotabox):
    def __init__(self, **kwargs):
        super(Sprite, self).__init__(**kwargs)
        self.custom_bounds = True

    def on_size(self, *args):
        self.x -= self.size[0] * .5
        self.y -= self.size[1] * .5
        self.update()


class Point(ToggleButton):
    busy = False

    def __init__(self, root, mag, **kwargs):
        super(Point, self).__init__(**kwargs)
        self.size_hint = None, None
        self.size = mag * 5, mag * 5
        self.background_normal = self.background_down = 'dot.png'
        self.line = Line(rectangle=(self.x, self.y, self.width, self.height),
                         dash_offset=1, dash_length=3)
        self.canvas.add(Color(0, 1, 0, 1))
        self.canvas.add(self.line)
        self.root = root
        self.appointed = False
        self.grabbed = False
        self.group = 'points'
        self.popup = None

    def on_size(self, *args):
        self.x -= self.size[0] * .5
        self.y -= self.size[1] * .5

    def on_pos(self, *args):
        try:
            self.line.rectangle = self.x, self.y, self.width, self.height
        except AttributeError:
            pass

    def on_state(self, *args):
        if self.state == 'down':
            self.opacity = 1
        else:
            self.opacity = 0

    def on_press(self, *args):
        if self.root.paint_btn.state != 'down':
            self.state = 'down'
            for p, pol in self.root.rec[self.root.frame].iteritems():
                if self in pol['btn_points']:
                    if self.root.index != pol['btn_points'].index(self) \
                            or self.root.pol != p:
                        self.root.pol = p
                        self.root.index = pol['btn_points'].index(self)
                        self.root.save_state(switch=1)
                    break

    def on_touch_move(self, touch):
        if self.state != 'down':
            return
        if Point.busy or self.grabbed:
            return
        if self.root.paint_btn.state == 'down':
            return
        if not self.collide_point(*touch.pos):
            return
        Window.bind(on_motion=self.drag)
        self.grabbed = True
        Point.busy = True

    def drag(self, *args):
        self.opacity = 0
        self.center = self.root.scat.to_widget(*args[2].pos)
        self.root.draw()

    def on_release(self, *args):
        if not self.root.paint_btn.state == 'down':
            self.opacity = 1
            Window.unbind(on_motion=self.drag)
            if self.grabbed:
                self.root.save_state(move=1)
                self.grabbed = False
                Point.busy = False
            self.root.draw()
            self.state = 'down'

    def pop_up(self, *args):
            point_popup = BoxLayout(orientation='vertical')
            chk_btn = Button(background_color=(.3, .4, .3, 1),
                             on_release=self.root.set_checkpoint)
            if self.appointed:
                chk_btn.text = 'Undo checkpoint'
            else:
                chk_btn.text = 'Make checkpoint'
            point_popup.add_widget(chk_btn)
            rem_btn = Button(background_color=(.3, .4, .3, 1),
                             on_release=self.root.remove_point)
            rem_btn.text = 'Remove point'
            point_popup.add_widget(rem_btn)
            clear_btn = Button(background_color=(.3, .4, .3, 1),
                               on_release=self.root.clear_polygon)
                               # on_release=self.root.confirm_clear)
            clear_btn.text = 'Remove polygon'
            point_popup.add_widget(clear_btn)
            cancel_btn = Button(background_color=(.3, .3, .5, 1),
                                on_release=self.dismiss_popup)
            cancel_btn.text = 'Cancel'
            point_popup.add_widget(cancel_btn)
            self.popup = Popup(content=point_popup, size_hint=(.3, .3))
            self.popup.title = "Edit point:"
            self.popup.open()
            with self.popup.content.canvas.before:
                Color(.3, .2, .1, .3)
                Rectangle(pos=self.popup.pos, size=self.popup.size)

    def dismiss_popup(self, *args):
        if self.popup:
            self.popup.dismiss()


class Editor(RelativeLayout):

    def __init__(self, **kwargs):
        super(Editor, self).__init__(**kwargs)
        self.rec = {}
        self.keys = []
        self.frame = '0'
        self.pol = None
        self.index = None
        self.lasts = ['0', None, None]
        self.clone_points = False
        # UNDO STATES
        self.history_states = 30
        self.history = deque()
        self.moves = []
        self.state = -1
        self.popup = None
        self.changes = 0
        self.filename = ''
        self.source = ''
        self.atlas_source = ''
        self.image = ''
        self.code = ''
        self.save_name = ''
        self.draw_group = InstructionGroup()
        self.scat.canvas.add(self.draw_group)
        self.paint_group = InstructionGroup()
        self.scat.canvas.add(self.paint_group)
        self.paint_mode = False
        self.mag = 3
        self.last_dir = app_config.get('last dir', './')
        EventLoop.window.bind(on_keyboard=self.on_key,
                              on_key_up=self.on_alt_up)
        Clock.schedule_once(self.load_dialog)

    def on_parent(self, *args):
        try:
            assert sys.platform == 'win32'
        except AssertionError:
            pass
        else:
            Window.bind(on_request_close=self.exit_check)

    # ------------------------ INPUT -----------------------

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
        content = LoadDialog(load=self.load_check, cancel=self.dismiss_popup,
                             file_types=['*.png', '*.atlas', '*.rbx'])
        if os.path.isdir(self.last_dir):
            content.ids.filechooser.path = self.last_dir
        else:
            './'
        self.popup = Popup(content=content, size_hint=(.8, .8),
                           color=(.4, .3, .2, 1),
                           title='Open image, atlas or project file:',
                           auto_dismiss=False)
        self.popup.open()

    def load_check(self, path, filename):
        if filename:
            self.last_dir = path
            self.clear_points()
            self.rec = {}
            self.frame = '0'
            self.pol = None
            self.index = None
            self.lasts = ['0', None, None]
            self.atlas_source = ''
            self.keys = []
            self.sprite.size = 100, 100
            self.sprite.pos = self.width * .5, self.height * .5
            self.scat.scale = 1
            self.paint_btn.state = 'normal'
            self.history = deque()
            self.state = -1
            self.changes = 0
            try:
                self.sprite.remove_widget(self.sprite.image)
            except AttributeError as e:
                print(e)
                pass
            if filename.endswith('.rbx'):
                self.load_proj(filename, path)
            else:
                self.load_img(filename, path)
        Clock.schedule_interval(self.hover, .1)
        self.save_state()
        self.update()
        self.draw()

    def load_img(self, filename, path, source=None):
        self.dismiss_popup()
        filename = os.path.join(path, filename)\
            .replace('./', '').replace('_RESCUED_', '')
        file_name = filename.replace('.png', '')\
            .replace('.atlas', '').replace('.rbx', '')
        if source:  # If a project is opened
            filename = filename.replace(filename.split('\\')[-1], source)
        self.image = filename.split('\\')[-1]
        self.save_name = file_name + '.rbx'
        try:
            self.source = os.path.relpath(os.path.join(path, filename))
        except ValueError as e:
            self.source = os.path.join(path, filename)
            print(e)
        if filename.endswith('.atlas'):
            try:
                with open(self.source, 'r') as ani:
                    atlas = json.load(ani)
            except (IOError, KeyError) as e:
                print('On loading img:', e)
                pass
            else:
                self.keys = sorted([key for key in atlas[filename.replace(
                    '.atlas', '.png').split('\\')[-1]].iterkeys()])
                self.filename = filename.replace('.atlas', '')
                try:
                    self.atlas_source = ('atlas://' +
                                         os.path.relpath(filename) +
                                         '/' + self.keys[0])
                except ValueError as e:
                    self.atlas_source = ('atlas://' +
                                         filename + '/' + self.keys[0])
                    print(e)
                for key in self.keys:
                    self.rec[key] = {}
                self.frame = self.keys[0]
                self.sprite.image = Image(source=self.atlas_source)
        else:
            self.sprite.image = Image(source=self.source)
        self.sprite.add_widget(self.sprite.image)
        self.sprite.image.size = self.sprite.image.texture_size
        self.sprite.size = self.sprite.image.size
        self.sprite.opacity = 1
        self.grid.opacity = 1
        self.mag = min(self.sprite.width * self.sprite.height / 1800., 3)
        self.board1.text = self.image

        if self.atlas_source:
            self.board1.text += ('\n('
                                 + str(self.keys.index(self.frame) + 1)
                                 + '  of  '
                                 + str(len(self.keys)) + '  frames)')

    def load_proj(self, filename, path):
        source = os.path.join(path, filename)
        try:
            with open(source, 'r') as proj:
                project = json.load(proj)
        except (IOError, KeyError) as e:
            print('On loading proj:', e)
            pass
        else:
            self.load_img(filename, path, source=project['image'])
            if not self.sprite.image.texture:
                    self.warn('Image "{}" is not found.'.format(
                              project['image']),
                              'Please, put the image with\n'
                              'the project file and try again.',
                              action=self.dismiss_popup, cancel=0)
                    return
            try:
                version = project['version']
                del project['version']
            except KeyError:
                version = '0.8.0'
            del project['image']
            self.restore(project, version)

    def clear_points(self):
        for frame in self.rec.itervalues():
            for poly in frame.itervalues():
                while len(poly['btn_points']):
                    self.scat.remove_widget(poly['btn_points'].pop())

    def restore(self, snapshot, v):
        for f, frame in snapshot.iteritems():
            if f in ['frame', 'pol', 'index']:
                continue
            self.rec[f] = {}
            for p, poly in frame.iteritems():
                self.rec[f][p] = {}
                self.rec[f][p]['check_points'] = poly['check_points'][:]
                self.rec[f][p]['btn_points'] = [Point(self, self.mag, pos=point)
                                                if int(v.replace('.', '')) > 80
                                                else Point(self, self.mag,
                                                           pos=(point[0] +
                                                                self.sprite.x,
                                                                point[1] +
                                                                self.sprite.y))
                                                for point in poly['points']]
                if f == self.frame:
                    for i in xrange(len(self.rec[f][p]['btn_points'])):
                        self.scat.add_widget(self.rec[f][p]['btn_points'][i])
                        self.rec[f][p]['btn_points'][i].opacity = 0
                        if i in poly['check_points']:
                            self.rec[f][p]['btn_points'][i].appointed = True

    # ------------------------ EDITOR -----------------------

    def add_point(self, x=None, y=None):

        if self.pol is not None:
            pol = self.rec[self.frame][self.pol]

            if not x or not y:  # If from keyboard
                if len(pol['btn_points']) > 1:
                    next_index = self.index + 1 \
                        if self.index + 1 < len(pol['btn_points']) else 0
                    x = (pol['btn_points'][self.index].center_x +
                        pol['btn_points'][next_index].center_x) / 2.
                    y = (pol['btn_points'][self.index].center_y +
                        pol['btn_points'][next_index].center_y) / 2.
                else:
                    x, y = self.sprite.center

            pol['btn_points'][self.index].state = 'normal'
            self.index += 1
            pol['btn_points'].insert(self.index, (Point(self, self.mag,
                                                        pos=(x, y),
                                                        state='down')))
            self.scat.add_widget(pol['btn_points'][self.index])
        else:
            if not x or not y:
                x, y = self.sprite.center
            self.pol = str(len(self.rec[self.frame]))
            pol = self.rec[self.frame][self.pol] = {}
            pol['btn_points'] = [Point(self, self.mag, pos=(x, y),
                                       state='down')]
            pol['check_points'] = []
            self.scat.add_widget(pol['btn_points'][-1])
            self.index = 0
        self.update_chk_points()
        self.save_state()
        self.draw()

    def remove_point(self, *args):
        try:
            pol = self.rec[self.frame][self.pol]
            pol['btn_points'][self.index].dismiss_popup()
            self.scat.remove_widget(pol['btn_points'].pop(
                                    self.index))
            if self.index > -1:
                self.index -= 1
            if len(pol['btn_points']):
                pol['btn_points'][self.index].state = 'down'
                self.update_chk_points()
            else:
                self.remove_polygon(pol)
                self.pol = None
                self.index = None
            self.save_state()
            self.draw()
        except (LookupError, TypeError) as e:
            print(e)
            pass

    def update_chk_points(self):
        pol = self.rec[self.frame][self.pol]
        pol['check_points'] = []
        for i in xrange(len(pol['btn_points'])):
            if pol['btn_points'][i].appointed:
                pol['check_points'].append(i)

    def set_checkpoint(self, *args):
        if self.pol:
            pol = self.rec[self.frame][self.pol]
            pol['btn_points'][self.index].dismiss_popup()
            if pol['btn_points'][self.index].appointed:
                pol['btn_points'][self.index].appointed = False
                pol['check_points'].remove(self.index)
            else:
                pol['btn_points'][self.index].appointed = True
                pol['check_points'].append(self.index)
            self.save_state()
            self.draw()

    def clear_polygon(self, *args):
        try:
            pol = self.rec[self.frame][self.pol]
        except LookupError as e:
            print('on clear polygon', e)
        else:
            pol['btn_points'][self.index].dismiss_popup()
            while len(pol['btn_points']):
                self.scat.remove_widget(pol['btn_points'].pop())
            self.remove_polygon(pol)
            self.pol = None
            self.index = None
            self.save_state()
            self.draw()

    def remove_polygon(self, pol):
        # Taking care of keys' consecutiveness in case of removing a middle one.
        p = len(self.rec[self.frame]) - 1
        for k, v in self.rec[self.frame].iteritems():
            if v == pol:
                p = int(k)
                break

        while p < len(self.rec[self.frame]) - 1:
            self.rec[self.frame][str(p)] = self.rec[self.frame][str(p + 1)]
            p += 1

        del self.rec[self.frame][str(p)]

    def deselect_polygon(self):
        if self.pol:
            self.rec[self.frame][self.pol]['btn_points'][self.index].state = \
                'normal'
            self.pol = None
            self.index = None
            self.save_state(switch=1)
            self.draw()

    def save_state(self, move=0, switch=0):
        if not move:
            if self.moves:
                self.history.append(self.moves[-1])
                self.changes += 1
                self.moves = []
        if not switch:
            if self.state != -1:
                index = self.state + len(self.history)
                while len(self.history) > index + 1:
                    self.history.pop()
                self.state = -1

            project = {'frame': self.frame, 'pol': self.pol,
                       'index': self.index}
            snapshot = self.store(project)

            if move:
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
            self.clear_points()
            self.paint_btn.state = 'normal'
            if self.atlas_source:
                self.frame = self.history[self.state]['frame']
                self.sprite.image.source = ('atlas://' + self.filename + '/'
                                                       + self.frame)
                self.board1.text = (self.image + '\n('
                                    + str(self.keys.index(self.frame) + 1)
                                    + '  of  '
                                    + str(len(self.keys)) + '  frames)')

            self.pol = self.history[self.state]['pol']
            self.index = self.history[self.state]['index']
            self.restore(self.history[self.state], __version__)
            try:
                self.rec[self.frame][self.pol]['btn_points'][self.index]\
                    .state = 'down'
            except KeyError:
                pass
            self.update()
            self.draw()

    def navigate(self, btn):
        cf = self.frame
        if self.atlas_source:
            while len(self.scat.children) > 1:
                for point in self.scat.children:
                    if isinstance(point, Point):
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

            self.sprite.image.source = ('atlas://' + self.filename + '/'
                                                   + self.frame)
            self.sprite.image.size = self.sprite.image.texture_size
            self.sprite.size = self.sprite.image.size
            self.sprite.center = self.width * .5, self.height * .5

            if self.clone_points:
                for key in self.rec[cf].iterkeys():
                    self.rec[self.frame][key] = {'btn_points': [],
                                                 'check_points': []}
                for (k, v), (k2, v2) in \
                        zip(self.rec[cf].iteritems(),
                            self.rec[self.frame].iteritems()):

                    for point in v['btn_points']:
                        v2['btn_points'].append(Point(self, self.mag,
                                                      pos=point.center))
                    v2['check_points'] = v['check_points'][:]
                if self.rec[cf]:
                    self.save_state()

            for poly in self.rec[self.frame].itervalues():
                for point in poly['btn_points']:
                    self.scat.add_widget(point)
                    point.opacity = 0
                for index in poly['check_points']:
                    poly['btn_points'][index].appointed = True

            self.pol = None
            self.index = None
            self.draw()
            self.board1.text = (self.image + '\n('
                                + str(self.keys.index(self.frame) + 1)
                                + '  of  '
                                + str(len(self.keys)) + '  frames)')

    def zoom(self, btn):
        if btn == 'plus':
            if self.scat.scale < 10:
                self.scat.scale += 0.5
        elif btn == 'minus':
            if self.scat.scale > 0.4:
                self.scat.scale -= 0.3

    # ------------------------ VISUALS -----------------------

    def update(self):
        if self.paint_btn.state == 'down':
            if not self.paint_mode:
                if self.index:
                    self.rec[self.frame][self.pol]['btn_points'][self.index]\
                        .opacity = 0
                self.calc_hints(self.rec[self.frame])
                self.sprite.bounds = [[[point for point in pol['points']],
                                       pol['check_points']]
                                      for pol
                                      in self.rec[self.frame].itervalues()
                                      if pol['points']]
                self.sprite.custom_bounds = True
                for entry in self.ids:
                    if hasattr(self.ids[entry], 'group'):
                        if self.ids[entry].group == 'edit' \
                                or self.ids[entry].group == 'nav':
                            self.ids[entry].disabled = True
                self.paint_btn.background_color = .9, .3, .9, 1
                self.paint_mode = True
        else:
            self.paint_mode = False
            for entry in self.ids:
                if hasattr(self.ids[entry], 'group'):
                    if not self.ids[entry].group == 'nav':
                        self.ids[entry].disabled = False
                    elif self.atlas_source:
                        self.ids[entry].disabled = False
                    else:
                        self.ids[entry].disabled = True
            self.paint_btn.background_color = .3, .15, .3, 1

            if self.state > -len(self.history) or self.moves:
                self.undo.disabled = False
            else:
                self.undo.disabled = True

            if self.state != -1:
                self.redo.disabled = False
            else:
                self.redo.disabled = True

            if self.paint_group.length():
                self.paint_group.clear()
        try:
            self.sprite.define_bounds()
        except TypeError as e:
            print(e)

    def hover(self, *args):
        pos = Window.mouse_pos
        if self.load_btn.collide_point(*pos):
            self.board2.text = 'Open image, atlas or project file. [O]'
            return True
        if self.save.collide_point(*pos):
            self.board2.text = 'Save current project to a project file. [S]\n' \
                               'If checked, it functions as a quick save ' \
                               '(no dialog) [Ctrl] + [S].'
            return True
        if self.help_btn.collide_point(*pos):
            self.board2.text = 'Help [F1]'
            return True
        if self.undo.collide_point(*pos):
            self.board2.text = 'Undo last action. [Ctrl] + [Z]'
            return True
        if self.redo.collide_point(*pos):
            self.board2.text = 'Redo last undone action. [Ctrl] + [Shift] + [Z]'
            return True
        if self.prev.collide_point(*pos):
            self.board2.text = "Previous frame of an atlas' sequence. [<] or " \
                               "[PageDown]\n" \
                               "If [Alt] is pressed, frame's points " \
                               "REPLACE previous frame's points."
            return True
        if self.next.collide_point(*pos):
            self.board2.text = "Next frame of an atlas' sequence. [>] or " \
                               "[PageUp]\n" \
                               "If [Alt] is pressed, frame's points REPLACE " \
                               "next frame's points."
            return True
        if self.minus.collide_point(*pos):
            self.board2.text = 'Zoom out. [-]'
            return True
        if self.plus.collide_point(*pos):
            self.board2.text = 'Zoom in. [+]'
            return True
        if self.des_btn.collide_point(*pos):
            self.board2.text = 'Deselect point and polygon.\n' \
                               'Next point will start a new polygon. [Space]'
            return True
        if self.chk_btn.collide_point(*pos):
            self.board2.text = 'Promote the selected point to a ' \
                               'checkpoint and vice versa. [Home] or [C]'
            return True
        if self.rem_btn.collide_point(*pos):
            self.board2.text = 'Delete the selected point. [Delete]'
            return True
        if self.clear_pol.collide_point(*pos):
            self.board2.text = 'Delete the selected polygon. [Shift] + [Delete]'
            return True
        if self.paint_btn.collide_point(*pos):
            self.board2.text = 'Enable / Disable Paint mode. [P]'
            return True
        if self.lang_btn.collide_point(*pos):
            self.board2.text = 'Choose a flavor for the resulting code. [L]'
            return True
        if self.copy_btn.collide_point(*pos):
            self.board2.text = 'Copy the resulting code to clipboard, ' \
                               'to use in a Rotabox widget. [Ctrl] + [C]'
            return True
        if self.paint_btn.state == 'down':
            self.board2.text = ('Paint on the image to test the '
                                'collidable areas.')
        else:
            self.board2.text = ('Click to add, select or move a point. '
                                'Right click on canvas to deselect point or move canvas. '
                                'Scroll to zoom.')

    def draw(self):
        self.draw_group.clear()
        if not self.rec:
            self.rec = {'0': {}}
        for poly in self.rec[self.frame].values():
            for i in xrange(len(poly['btn_points'])):
                if poly['btn_points'][i].appointed:
                    self.draw_group.add(Color(0.29, 0.518, 1, 1))
                    self.draw_group.add(Line(
                        circle=(poly['btn_points'][i].center_x,
                                poly['btn_points'][i].center_y, self.mag+1)))
                self.draw_group.add(Color(.7, 0, .7, 1))
                self.draw_group.add(Line(
                    circle=(poly['btn_points'][i].center_x,
                            poly['btn_points'][i].center_y, self.mag)))
                k = i - 1 if i > 0 else -1
                if poly['btn_points'][i].appointed \
                        or poly['btn_points'][k].appointed:
                    self.draw_group.add(Color(0.29, 0.518, 1, 1))
                else:
                    self.draw_group.add(Color(1, .29, 1, 1))
                self.draw_group.add(Line(
                    points=(poly['btn_points'][i].center_x,
                            poly['btn_points'][i].center_y,
                            poly['btn_points'][k].center_x,
                            poly['btn_points'][k].center_y)))
                self.draw_group.add(Color(0, 0, 0, 1))
                self.draw_group.add(Line(
                    points=(poly['btn_points'][i].center_x,
                            poly['btn_points'][i].center_y,
                            poly['btn_points'][k].center_x,
                            poly['btn_points'][k].center_y),
                    dash_offset=2,
                    dash_length=1))

    # ------------------------ OUTPUT -----------------------

    def calc_hints(self, frame):
        for pol in frame.itervalues():
            if len(pol['btn_points']) > 1:
                pol['points'] = [(round(float(point.center_x - self.sprite.x) /
                                        self.sprite.width, 3),
                                  round(float(point.center_y - self.sprite.y) /
                                        self.sprite.height, 3))
                                 for point in pol['btn_points']]
            else:
                pol['points'] = []

    def write(self):
        py = self.lang_btn.text.lstrip().startswith('py')
        if self.atlas_source:
            for frame in self.rec.itervalues():
                self.calc_hints(frame)
            if py:
                self.code = 'bounds = {'
            else:
                self.code = 'bounds:\n                {'
            for key in self.keys:
                self.code += "'" + key + "': ["
                self.write_more(key, py)
                if py:
                    self.code += '],\n                       '
                else:
                    self.code += '],\n                '
            self.code = (self.code.rstrip(',\n ') + '}')
            return
        self.rec[self.frame].itervalues()
        self.calc_hints(self.rec[self.frame])
        if py:
            self.code = 'bounds = ['
        else:
            self.code = 'bounds:\n                ['
        self.write_more(self.frame, py)
        self.code += ']'

    def write_more(self, frame, py):
        if self.atlas_source:
            poiws = '\n                                '
            chpws = '\n                               '
            polws = '\n                              '
        else:
            poiws = '\n                         '
            chpws = '\n                        '
            polws = '\n                       '
        kvspace = '\n                '
        for i in xrange(len(self.rec[frame])):
            poly = self.rec[frame][str(i)]
            if not poly['points']:
                continue
            self.code += '[['
            for point in poly['points']:
                self.code += '(' + str(point[0]) + ', ' + str(point[1]) + '), '
                if py and len(self.code.split('\n')[-1]) > 65:
                    self.code += poiws
                elif len(self.code.split('\n')[-1]) > 65:
                    self.code += kvspace
            self.code = (self.code.rstrip(',\n ') + '], ')
            if py:
                self.code += chpws + (str(poly['check_points']) + '],' + polws)
            elif len(self.code.split('\n')[-1]) > 65:
                self.code += kvspace + (str(poly['check_points']) + '],' +
                                        kvspace)
            else:
                self.code += (str(poly['check_points']) + '],' + kvspace)
        self.code = self.code.rstrip(',\n ')

    def copy_to_clipboard(self):
        self.write()
        code = self.code.decode('utf-8')
        Clipboard.copy(code)
        print(Clipboard.paste())

    # ------------------------ STORAGE -----------------------

    def store(self, project):
        for f, frame in self.rec.iteritems():
            project[f] = {}
            for p, poly in frame.iteritems():
                project[f][p] = {}
                project[f][p]['check_points'] = poly['check_points'][:]
                project[f][p]['points'] = [tuple(point.center)
                                           for point in poly['btn_points']]
        return project

    def save_dialog(self, *args):
        """ Shows the 'Save project' dialog."""
        if not self.sprite.image:
            return
        content = SaveDialog(save=self.save_check, cancel=self.dismiss_popup,
                             file_types=['*.rbx'])
        content.ids.filechooser.path = self.last_dir
        content.text_input.text = (self.save_name.split('\\')[-1])
        self.popup = Popup(content=content, size_hint=(.8, .8),
                           title='Save project:', auto_dismiss=False)
        self.popup.open()

    def save_check(self, path, filename):
        if filename:
            self.last_dir = path
            filename = self.sanitize_filename(filename)
            if not filename.endswith('.rbx'):
                filename += '.rbx'
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
            with open(self.save_name, 'w+') as proj:
                json.dump(project, proj, sort_keys=True, indent=4)
        except IOError as e:
            print('On saving:', e)
        else:
            self.changes = 0

    def exit_save(self, *args):
        project = self.store({})
        project['image'] = self.image
        project['version'] = __version__
        root, ext = os.path.splitext(self.save_name)
        save_name = root + '_RESCUED_' + ext
        try:
            with open(save_name, 'w+') as proj:
                json.dump(project, proj, sort_keys=True, indent=4)
        except IOError as e:
            print('On saving:', e)

    # ---------------------- USER EVENTS ---------------------

    def on_touch_down(self, touch):
        mouse_btn = ''
        if 'button' in touch.profile:
            mouse_btn = touch.button
        if not self.sprite.image and mouse_btn != 'right':
            super(Editor, self).on_touch_down(touch)
            return
        if mouse_btn == 'scrolldown':
            self.zoom('plus')
            return
        elif mouse_btn == 'scrollup':
            self.zoom('minus')
            return
        for entry in self.ids:
            widg = self.ids[entry]
            if ((isinstance(widg, (Button, ScrollLabel)) or entry == 'save') and
                    widg.collide_point(*widg.to_widget(*touch.pos))):
                if mouse_btn != 'right' and mouse_btn != 'middle':
                    super(Editor, self).on_touch_down(touch)
                    self.update()
                self.save_state(switch=1)
                return True
        pos = self.scat.to_widget(*touch.pos)
        for child in self.scat.children:
            if (isinstance(child, ToggleButton) and
                    child.collide_point(*pos) and
                    self.paint_btn.state != 'down'):
                super(Editor, self).on_touch_down(touch)
                if mouse_btn == 'right':
                    child.pop_up()
                self.update()
                self.draw()
                return True
        if mouse_btn == 'middle':
            self.scat.scale = 1
            return True
        if mouse_btn == 'right':
            self.deselect_polygon()
            super(Editor, self).on_touch_down(touch)
            return True
        elif self.paint_btn.state != 'down':
            self.add_point(*pos)
            super(Editor, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        '''If paint option is enabled, lets the user paint with the mouse on
        the collidable areas to examine custom bounds.
        '''
        mouse_btn = ''
        if 'button' in touch.profile:
            mouse_btn = touch.button
        pos = self.scat.to_widget(*touch.pos)
        if self.paint_btn.state == 'down' and mouse_btn != 'right':
            if self.sprite.collide_point(*pos):
                self.paint_group.add(Color(.7, .3, 0, 1))
                self.paint_group.add(Line(circle=(pos[0], pos[1], 1)))
        else:
            super(Editor, self).on_touch_move(touch)
            self.draw()

    def on_key(self, window, key, *args):
        """ What happens on keyboard press"""
        if key == 27:  # Esc/Back
            if self.popup:
                self.dismiss_popup()
                return True
            else:
                return False
        if key == 13:  # Enter
            if self.popup:
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
                else:
                    for child in self.popup.content.children:
                        if isinstance(child, Label):
                            if child.text.startswith('Project'):
                                self.load_dialog()
                            elif child.text.startswith('There'):
                                self.quit()
                            elif child.text.startswith('Filename'):
                                self.save_proj()
            return True

        if self.popup:
            return True
        if key not in [273, 274, 275, 276, 303, 304, 305, 306]:
            self.save_state(switch=1)

        if key == 111:  # O
                self.load_dialog()

        # ---------------- IF IMAGE IS PRESENT

        if key == 115:  # S
            if ['ctrl'] in args:
                self.save_proj()
            else:
                self.save_dialog()
        if key == 270 or key == 61:  # +
                self.zoom('plus')
        if key == 269 or key == 45:  # -
                self.zoom('minus')
        if key == 108:  # L
            if self.lang_btn.text == \
                    '  python  [font=guifont][size=10]a[/size][/font]':
                self.lang_btn.text = \
                    '  kvlang  [font=guifont][size=10]a[/size][/font]'
            else:
                self.lang_btn.text = \
                    '  python  [font=guifont][size=10]a[/size][/font]'
        if key == 99:  # C
            if ['ctrl'] in args:
                self.copy_to_clipboard()
        if key == 112:  # P
            if self.paint_btn.state == 'down':
                self.paint_btn.state = 'normal'
            else:
                self.paint_btn.state = 'down'
            self.update()
        if self.paint_btn.state == 'down':
            return True

        # --------------- IF NOT IN PAINT MODE

        if key == 122:  # Z
            if ['ctrl'] in args:
                self.change_state('undo')
            if ['shift', 'ctrl'] in args:
                self.change_state('redo')

        if key == 280 or key == 46:  # PageUp or >
                self.navigate('>')
        if key == 281 or key == 44:  # PageDown or <
                self.navigate('<')
        if key == 307 or key == 308:  # Alt
            self.prev.text = 't'
            self.next.text = 'y'
            self.clone_points = True

        if key == 277 or key == 97:  # Insert or A
                self.add_point()

        if key == 32:  # Space
            if self.index is None:
                try:
                    self.frame, self.pol, self.index = self.lasts
                    self.rec[self.frame][self.pol]['btn_points'][self.index]\
                        .state = 'down'
                except KeyError:
                    pass
                return True

        if self.index is not None:  # If a point is selected
            pol = self.rec[self.frame][self.pol]

            if key == 278 or key == 99:  # Home or C
                self.set_checkpoint()
            if key == 127:  # Delete
                if ['shift'] in args or ['ctrl'] in args:
                    self.clear_polygon()
                else:
                    self.remove_point()

            if key == 32:  # Space
                if args[2]:
                    pol['btn_points'][self.index].state = 'normal'
                    if ['alt'] in args:
                        self.index = self.index - 1 \
                            if self.index > 0 else -1
                    if ['ctrl'] in args:
                        self.index = self.index + 1 \
                            if self.index + 1 < len(pol['btn_points']) else 0
                    if ['shift'] in args:
                        self.pol = str(int(self.pol) - 1) \
                            if int(self.pol) > 0 \
                            else str(len(self.rec[self.frame]) - 1)
                        pol = self.rec[self.frame][self.pol]
                        self.index = -1
                    pol['btn_points'][self.index].on_press()
                    pol['btn_points'][self.index].on_release()
                else:
                    self.lasts = self.frame, self.pol, self.index
                    self.deselect_polygon()

            if key == 273:  # up
                if ['ctrl'] in args:
                    pol['btn_points'][self.index].center_y += .1
                elif ['shift'] in args:
                    pol['btn_points'][self.index].center_y += 10
                else:
                    pol['btn_points'][self.index].center_y += 1
                self.save_state(move=1)
            if key == 274:  # down
                if ['ctrl'] in args:
                    pol['btn_points'][self.index].center_y -= .1
                elif ['shift'] in args:
                    pol['btn_points'][self.index].center_y -= 10
                else:
                    pol['btn_points'][self.index].center_y -= 1
                self.save_state(move=1)
            if key == 275:  # right
                if ['ctrl'] in args:
                    pol['btn_points'][self.index].center_x += .1
                elif ['shift'] in args:
                    pol['btn_points'][self.index].center_x += 10
                else:
                    pol['btn_points'][self.index].center_x += 1
                self.save_state(move=1)
            if key == 276:  # left
                if ['ctrl'] in args:
                    pol['btn_points'][self.index].center_x -= .1
                elif ['shift'] in args:
                    pol['btn_points'][self.index].center_x -= 10
                else:
                    pol['btn_points'][self.index].center_x -= 1
                self.save_state(move=1)
        self.draw()

    def on_alt_up(self, window, key, *args):
        if key == 307 or key == 308:  # Alt
            self.prev.text = 'e'
            self.next.text = 'r'
            self.clone_points = False

    # ----------------------- UTILS --------------------------

    @staticmethod
    def sanitize_filename(filename):
        """ Creates a safe filename from the text input
        of the 'Save File' dialog.
        """
        filename = re.sub(r'[/:*?"<>|\\]', "_", filename)
        return filename

    def warn(self, title, text, action, cancel=1):
        """ Opens a dialog with a warning"""
        content = BoxLayout(orientation='vertical')
        label = Label(halign='center')
        label.text = text
        content.add_widget(label)

        buttons = BoxLayout(size_hint=(1, .5))

        if cancel:
            cancel_btn = Button(background_color=(.3, .3, .5, 1),
                                on_release=self.dismiss_popup)
            cancel_btn.text = 'Cancel'
            buttons.add_widget(cancel_btn)

        ok_btn = Button(background_color=(.3, .4, .3, 1),
                        on_press=action)
        ok_btn.text = 'OK'
        buttons.add_widget(ok_btn)

        content.add_widget(buttons)
        self.popup = Popup(title_align='center', content=content,
                           title_color=([1, .1, .1, 1]),
                           size_hint=(.5, .25))
        self.popup.title = title
        self.popup.open()

    def dismiss_popup(self, *args):
        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def exit_check(self, *args, **kwargs):
        if self.changes > 1:
            self.warn('Warning!', 'There are unsaved changes.\n'
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
        width, height = EventLoop.window.size
        # position = EventLoop.window.top, EventLoop.window.left
        config = {'width': width,
                  'height': height,
                  # 'pos': position,
                  'last dir': self.last_dir}
        try:
            with open('settings.json', 'w+') as settings:
                json.dump(config, settings)
        except IOError as e:
            print('On saving settings:', e)

    def help(self):
        content = BoxLayout(orientation='vertical')
        scrl_label = ScrollLabel()
        scrl_label.label.padding_x = 10
        scrl_label.label.color = .75, .45, .75, 1
        scrl_label.scroll_y = 1
        scrl_label.label.font_size = '18sp'
        scrl_label.label.markup = True
        scrl_label.text = '''
{0}{5}[b]Rotaboxer  {8}[/b]{7}

{6}Description{7}{4}
    Rotaboxer is an editing tool for the Rotabox{0}*{4}  bounds.
    With an image as input, one can visually shape specific
    collision bounds for it, then copy the resulting code to
    clipboard and use it with a Rotabox widget, in a kivy project.
    Animated bounds are also supported, with the use of atlases.
    Rotaboxer lets you browse through the individual frames of
    a sequence and define different bounds for each one.

{0}{5}User's manual{7}{4}

{0}{6}Open an image{7}{4} (.png), {0}{6}sequence{7}{4} (.atlas), or {0}{6}project file{7}{4} (.rbx):
    {0}Click{4} {1}Open{4} button {0}/{4} press {0}O{4} key.

{0}{6}Add a point{7}{4}:
    Each new point is spawn connected to the currently selected
    point and next to it. If no point is selected, new point starts a
    new polygon.
    {0}Click{4} on workspace {0}/{4} press {0}Insert{4} key {0}/{4} press {0}A{4} key.

{0}{6}Select a point{7}{4}:
    {0}Click{4} on a point.
    {0}{6}Select next / previous{7}{4} point:
        Press {0}Ctrl + Space{4} key comb. {0}/{4} Press {0}Alt + Space{4} key comb.
    {0}{6}Select different polygon{7}{4}:
        Press {0}Shift + Space{4} key comb.

{0}{6}Deselect{7}{4}:
    {0}Click{4} {3}Deselect{4} button {0}/{4} {0}Right click{4} anywhere on canvas {0}/{4}
    Press {0}Space{4} key.
    {0}{6}Reselect{7}{4} last point:
        Press {0}Space{4} key.

{0}{6}Move a point{7}{4}:
    {0}Click & drag{4} the point {0}/{4} Press {0}Up / Down / Left / Right{4} arrow
    keys. ({0}Ctrl +{4} for smaller steps. {0}Shift +{4} for bigger steps)

{0}{6}Remove a point{7}{4}:
    {0}Click{4} {3}Remove point{4} button {0}/{4} Press {0}Delete{4} key.

{0}{6}Remove a polygon{7}{4}:
    Delete the polygon that contains the selected point.
    {0}Click{4} {3}Remove polygon{4} button {0}/{4} Press {0}Shift + Delete{4} key comb.

{0}{6}Checkpoint promotion{7}{4}:
    Promote selected point to checkpoint (or the opposite).
    {0}Click{4} {3}Checkpoint{4} button {0}/{4} Press {0}Home{4} key {0}/{4} Press {0}C{4} key.

{0}{6}Navigate an atlas' frames{7}{4}:
    {0}Click{4} {2}[size=15][font=guifont]e[/font]{7}{4} {0}/{4} {2}[size=15][font=guifont]r[/font]{7}{4} buttons {0}/{4} Press {0}< / >{4} or {0}PageDown / PageUp{4}
     keys.
    {0}Clone points{4}:
    If {0}{6}Alt{7}{4} key is pressed, frame's points will REPLACE destination
    frame's points.

{0}{6}Undo{7}{4} last action:
    {0}Click{4} {3}[font=guifont]q[/font]{4} button {0}/{4} Press {0}Ctrl + Z{4} key comb.

{0}{6}Redo{7}{4} last undone action:
    {0}Click{4} {3}[font=guifont]w[/font]{4} button {0}/{4} {0}{6}Ctrl + Shift + Z{7}{4} key comb.

{0}{6}Paint over the colliding areas{7}{4} for testing:
    {0}Click & drag{4} on the image, while in {0}paint mode{4}.
    Go in {0}{6}paint mode{7}{4}:
        {0}Click{4} [color=#ff77ff]Paint test{4} button {0}/{4} Press {0}P{4} key.

{0}{6}Output code{7}{4}.
    Copy the resulting code to clipboard, to use in a Rotabox
    widget:
    {0}Click{4} {1}to Clipboard{4} button {0}/{4} Press {0}Ctrl + C{4} key comb.
    {0}{6}Language{7}{4} of the output code (Indentation difference fix):
        {0}Click{4} {1}python / kvlang{4} button {0}/{4} Press {0}L{4} key.

{0}{6}Zoom{7}{4} in / out the canvas:
    {0}Click{4} {2}[font=guifont]s[/font]{4} {0}/{4} {2}{5}[font=guifont]s[/font]{7}{4} buttons {0}/{4} {0}Mouse Scroll{4} {0}/{4} Press {0}{6}- / +{7}{4} keys.
    Back to {0}{6}actual size{7}{4} (1:1):
    {0}Middle click{4} anywhere on canvas.

{0}{6}Adjust canvas position{7}{4}:
    {0}Right click & drag{4} canvas.

{0}{6}Point's context menu{7}{4}:
    {0}Right click{4} on a point.

{0}{6}Save project{7}{4}:
    {0}Click{4} {2}Save{4} button {0}/{4} Press {0}S{4} key (Opens a save dialog)
    {0}{6}Quick save{7}{4} (No save dialog is displayed):
        Have {2}□{4} checked, {0}/{4} Press {0}Ctrl + S{4} key comb.

    {0}Note{4}: Keep a project file with its image, to be able to open it.

    {0}Exit Save{4}: If not in Windows and the user exits the editor
    without saving changes (not because of a crash), no save
    prompt is displayed. Instead, the project is automatically
    saved at the project's (or image's) location, as:
    '<project (or image) name>_RESCUED_ON_EXIT_.rbx'.

{0}{6}Help{7}{4}:
    {0}Click{4} {2}{5}?{7}{4} button {0}/{4} Press {0}F1{4} key.
     ___________________________________________________________________________
  {0}*{4} Rotabox is a kivy widget, that has rotatable, fully
    customizable 2D colliding bounds.
    To understand the concept of the Rotabox collision detection,
    you can refer to its module's documentation.
        '''.format('[color=#ffffff]', '[color=#cc9966]', '[color=#9999ff]',
                   '[color=#729972]', '[/color]', '[size=25]', '[size=20]',
                   '[/size]', __version__)
        content.add_widget(scrl_label)

        ok_btn = Button(background_color=(.3, .4, .3, 1), size_hint=(1, .1),
                        on_press=self.dismiss_popup)
        ok_btn.text = 'OK'
        content.add_widget(ok_btn)

        self.popup = Popup(title_align='center', content=content,
                           size_hint=(1, 1))
        self.popup.title = 'Help'
        self.popup.open()
        with self.popup.content.canvas.before:
            Color(.3, .2, .1, .3)
            Rectangle(pos=self.popup.pos, size=self.popup.size)


class Rotaboxer(App):
    texture = ObjectProperty()

    def build(self):
        self.use_kivy_settings = False
        with open("guifont.ttf", "wb") as font:
            font.write(base64.b64decode('''
AAEAAAAOAIAAAwBgT1MvMn+sfT4AAAFoAAAATlZETViCPInQAAAM8AAABeBjbWFwDzQf8AAAA1wAAAH
SY3Z0IAAUAAAAAAaYAAAAAmZwZ20yTXNmAAAFNAAAAWJnbHlmmiZ/HQAABtQAAAW4aGVhZAlIuxIAAA
DsAAAANmhoZWEIBgPoAAABJAAAACRobXR4Ko4AmQAABpwAAAA4bG9jYQi+BzwAAAyMAAAAHm1heHACH
wG4AAABSAAAACBuYW1lEu6UUgAAAbgAAAGhcG9zdHDBc2AAAAysAAAARHByZXC4AAArAAAFMAAAAAQA
AQAAAAEAAFTY6o9fDzz1AAkD6AAAAADTIbsfAAAAANMhux//+P/5A/AD9QAAAAkAAgAAAAAAAAABAAA
D9f/5ACYD6P/4//gD8AABAAAAAAAAAAAAAAAAAAAADgABAAAADgBVAAYAAAAAAAEAAAAAAAoAAAIAAW
IAAAAAAAADCQGQAAUAAAK8AooAAACMArwCigAAAd0AMgD6AAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAA
AAAAHB5cnMAQAAgAKACvP84AEsD9QAHAAAAAAAQAMYAAQAAAAAAAQAHAAAAAQAAAAAAAgAHAAcAAQAA
AAAAAwASAA4AAQAAAAAABAAHACAAAQAAAAAABQANACcAAQAAAAAABgAHADQAAQAAAAAAEAAHADsAAQA
AAAAAEgAHAEIAAwABBAkAAQAOAEkAAwABBAkAAgAOAFcAAwABBAkAAwAkAGUAAwABBAkABAAOAIkAAw
ABBAkABQAaAJcAAwABBAkABgAOALEAAwABBAkAEAAOAL8AAwABBAkAEgAOAM1ndWlmb250UmVndWxhc
kZPTlRMQUIzMDpUVEVYUE9SVGd1aWZvbnRWZXJzaW9uIDEuMDAgZ3VpZm9udGd1aWZvbnRndWlmb250
AGcAdQBpAGYAbwBuAHQAUgBlAGcAdQBsAGEAcgBGAE8ATgBUAEwAQQBCADMAMAA6AFQAVABFAFgAUAB
PAFIAVABnAHUAaQBmAG8AbgB0AFYAZQByAHMAaQBvAG4AIAAxAC4AMAAwACAAZwB1AGkAZgBvAG4AdA
BnAHUAaQBmAG8AbgB0AGcAdQBpAGYAbwBuAHQAAAAAAAADAAAAAwAAAXoAAQAAAAAAHAADAAEAAAEiA
AABBgAAAQAAAAAAAAABAgAAAAIAAAAAAAAAAAAAAAAAAAABAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAFAAYHAAAAAAAAAAA
ICQoLAAAMAA0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAFgAAAASABAAAwACACAAYQBlAGgAdAB3AHkAoP//AAAA
IABhAGUAZwBxAHcAeQCg////4/+j/6D/n/+X/5X/lP9jAAEAAAAAAAAAAAAAAAAAAAAAAAAABABYAAA
AEgAQAAMAAgAgAGEAZQBoAHQAdwB5AKD//wAAACAAYQBlAGcAcQB3AHkAoP///+P/o/+g/5//l/+V/5
T/YwABAAAAAAAAAAAAAAAAAAAAAAAAAAC4AAAruAAALEu4AAlQWLEBAY5ZuAH/hbgARB25AAkAA19eL
bgAASwgIEVpRLABYC24AAIsuAABKiEtuAADLCBGsAMlRlJYI1kgiiCKSWSKIEYgaGFksAQlRiBoYWRS
WCNlilkvILAAU1hpILAAVFghsEBZG2kgsABUWCGwQGVZWTotuAAELCBGsAQlRlJYI4pZIEYgamFksAQ
lRiBqYWRSWCOKWS/9LbgABSxLILADJlBYUViwgEQbsEBEWRshISBFsMBQWLDARBshWVktuAAGLCAgRW
lEsAFgICBFfWkYRLABYC24AAcsuAAGKi24AAgsSyCwAyZTWLCAG7BAWYqKILADJlNYIyGwwIqKG4ojW
SCwAyZTWCMhuAEAioobiiNZILADJlNYIyG4AUCKihuKI1kguAADJlNYsAMlRbgBgFBYIyG4AYAjIRuw
AyVFIyEjIVkbIVlELbgACSxLU1hFRBshIVktAAAAFAAAAfQAAAAAAAAB9AAAAfQAAAPoAD4D6P/4AYY
APAPoAD4D6AAAA+j/+APoAAAD6P/4A+gAAAPo//kAAQA+//4DqgP1AAoAABMBFhQHAQYmJxE2ewMgDw
/84AwjDh8D4f44CTsH/jgIBQ8DwSIAAAH/+P/5A/AD8QAVAAAJAh4BDgEnAS4BNzY3MjYzATYeAQYDs
/2IAngmFyxUJvzrJhcWDBcBAgEDFSZULBcDOv67/roTS0MVFAGXEkwiEw0CAZcUFUNLAAACADwBHAFe
At8ACwA9ABq6AB4ACQADK7gAHhC4AAkQuAA30LgANy8wMRMeAQcOAScuATc+ARMWFRQGBw4BDwEOAQc
OARUUBisBIiY1PgE3PgE3Njc+ATc2NTQnJiMiBwYVIzY3NjMyxhcdAQEeFxUeAQEfgisMCQYXEBYIDg
MCAQMFQAYCAQQICBULDA0FCAMODQwiIQ4OUgM1IjFBAYMBHRcXGwEBHBcXHAE8HzwTHw0IEwwQBg8JB
QkIAgUFAhUfCggTCAkIBAgFEREXERIWFxdSIRYAAAAGAD4AAAOpA+gAHQApADUAQQBNAFQAc7oAEQAU
AAMruAAREAC4ABAvuABRL7oAGQAeAAMruAAZELoABwAIAAMruAAHELoAJQAqAAMruAAlELoAMQA2AAM
ruAAxELoASAABAAMruABIELoAPQBCAAMruAA9ELgAEBC4AA/cuAAHELgAUtC4AFIvMDEBBSIGFBYzIR
UhIgYUFjMhFSEiJjURNDYzITIWFREDISIGFBYzITI2NCYHISIGFBYzITI2NCYHISIGFBYzITI2NCYHI
SIGFBYzITI2NCYXBwYjESEUA6n88wwTEwwBlv5qDBMTDAGW/ksaJSUaAu0aJV79UQwTEwwCrw0SEg39
UQwTEwwCrw0SEg39UQwTEwwCrw0SEg39UQwTEwwCrw0SEj76EhkBOAF4ARMaEj4TGRO6JBoDahskJBv
90AHxEhoSEhoSfRIaEhIaEnwTGhISGhN9ExoSEhoT5/sSATkaAAAAAQAAAAAD6QPpACYAHwC6AAcAAA
ADK7gABxC6AB4ADgADK7gAHhC4ABrQMDEhIiYnNx4BMzI+ATQuASMiBxcWJyEiJicDJh8BPgEzMh4CF
A4CAfVzy0djNZdWZqxlZaxmjWp7ARj+vgwRAQEBIoNErV9muYZPT4a5Y1dNQUllrMysZV57IgEbDwE3
FwGDPkVQhrjMuYZPAAAB//j/+QPwA/EAFQAACQEGLgE2NwkBLgE+ARcBMhYzFhcWBgOz/OsmVCwXJgJ
4/YgmFyxUJgMVAQIBFwwWFwGk/mkUFUNLEwFGAUUUS0MVFP5pAg0TIkwAAgAAAAAD6APnABcAJAAAJS
cGIyIuAjQ+AjIeAhUUBxcWFAYiASYiDgEUHgEyPgE0JgN9wnWRWKJ2RUV2orGidkVXwRMlNP7DSKmQV
FSQqZBUVBPBV0V2obKidUVFdaJZkXTCEjQlA0AqU5GokVNTkaiRAAAC//j/+QPvA/AACAAeAAABBiIm
NDYyFhQDCQEeAQ4BJwEuATc2NzI2NwE2HgEGA8MkaElJaEk2/YkCdyYXLFQl/OsmFxYMFwECAQMVJVQ
sFwGbJElpSUlpAXr+uv67FEpDFRQBlhNMIRMNAgEBlhQVQ0sAAAEAAAAAA+kD6QAmACMAugAQABcAAy
u4ABAQugAgAAkAAyu4ACAQuAAk0LgAJC8wMQEOASMhBj8BJiMiDgEUHgEzMjY3Fw4BIyIuAjQ+AjMyF
hc3NgcD5wERDP69FwF7ao1mrGVlrGZWlzVjR8tzZrmGT0+GuWZfrUSDIgECmw8bASJ7XmWszatlSUFN
V2NPhrnMuIZPRD6DARcAAAL/+f/5A/AD8AAIAB4AABM2MhYUBiImNAUBBi4BNjcJAS4BPgEXAR4BMxY
XFgYkJWhJSWhJA7P86yVULBcmAnf9iSYXLFQlAxUBAgEXDBYXAk0lSWlJSWmG/moUFUNKFAFFAUYTS0
MVFP5qAQINEyFMAAAAAAAAAAAAAAAAABoARgCyAWgBtAHgAhoCVAKiAtwAAAACAAAAAAAA/5wAMgAAA
AAAAAAAAAAAAAAAAAAAAAAAAA4AAAECAAIAAwBEAEgASgBLAFQAVQBWAFcAWgBcBS5udWxsAAAAAQAB
AQEBAQAMAPgI/wAIAAn//wAJAAr//wAKAAv//wALAAz//wAMAA3//wANAA7//wAOAA///wAPABD//wA
QABH//wARABL//wASABP//wATABT//wAUABX//wAVABb//wAWABf//wAXABj//wAYABn//wAZABr//w
AaABv//wAbABz//wAcAB3//wAdAB7//wAeAB///wAfACD//wAgACH//wAhACL//wAiACP//wAjACT//
wAkACX//wAlACb//wAmACf//wAnACj//wAoACn//wApACr//wAqACv//wArACz//wAsAC3//wAtAC7/
/wAuAC///wAvADD//wAwADH//wAxADL//wAyADP//wAzADT//wA0ADX//wA1ADb//wA2ADf//wA3ADj
//wA4ADn//wA5ADr//wA6ADv//wA7ADz//wA8AD3//wA9AD7//wA+AD///wA/AED//wBAAEH//wBBAE
L//wBCAEP//wBDAET//wBEAEX//wBFAEb//wBGAEf//wBHAEj//wBIAEn//wBJAEr//wBKAEv//wBLA
Ez//wBMAE3//wBNAE///wBOAFD//wBPAFH//wBQAFL//wBRAFP//wBSAFT//wBTAFX//wBUAFb//wBV
AFf//wBWAFj//wBXAFn//wBYAFr//wBZAFv//wBaAFz//wBbAF3//wBcAF7//wBdAF///wBeAGD//wB
fAGH//wBgAGL//wBhAGP//wBiAGT//wBjAGX//wBkAGb//wBlAGf//wBmAGj//wBnAGn//wBoAGr//w
BpAGv//wBqAGz//wBrAG3//wBsAG7//wBtAG///wBuAHD//wBvAHH//wBwAHL//wBxAHP//wByAHT//
wBzAHX//wB0AHb//wB1AHf//wB2AHj//wB3AHn//wB4AHr//wB5AHv//wB6AHz//wB7AH3//wB8AH7/
/wB9AH///wB+AID//wB/AIH//wCAAIL//wCBAIP//wCCAIT//wCDAIX//wCEAIb//wCFAIf//wCGAIj
//wCHAIn//wCIAIr//wCJAIv//wCKAIz//wCLAI3//wCMAI7//wCNAI///wCOAJD//wCPAJH//gCQAJ
L//gCRAJP//gCSAJT//gCTAJX//gCUAJb//gCVAJf//gCWAJj//gCXAJn//gCYAJr//gCZAJv//gCaA
J3//gCbAJ7//gCcAJ///gCdAKD//gCeAKH//gCfAKL//gCgAKP//gChAKT//gCiAKX//gCjAKb//gCk
AKf//gClAKj//gCmAKn//gCnAKr//gCoAKv//gCpAKz//gCqAK3//gCrAK7//gCsAK///gCtALD//gC
uALH//gCvALL//gCwALP//gCxALT//gCyALX//gCzALb//gC0ALf//gC1ALj//gC2ALn//gC3ALr//g
C4ALv//gC5ALz//gC6AL3//gC7AL7//gC8AL///gC9AMD//gC+AMH//gC/AML//gDAAMP//gDBAMT//
gDCAMX//gDDAMb//gDEAMf//gDFAMj//gDGAMn//gDHAMr//gDIAMv//gDJAMz//gDKAM3//gDLAM7/
/gDMAM///gDNAND//gDOANH//gDPANL//gDQANP//gDRANT//gDSANX//gDTANb//gDUANf//gDVANj
//gDWANn//gDXANr//gDYANv//gDZANz//gDaAN3//gDbAN7//gDcAN///gDdAOD//gDeAOH//gDfAO
L//gDgAOP//gDhAOT//gDiAOX//gDjAOb//gDkAOf//gDlAOj//gDmAOn//gDnAOv//gDoAOz//gDpA
O3//gDqAO7//gDrAO///gDsAPD//gDtAPH//gDuAPL//gDvAPP//gDwAPT//gDxAPX//gDyAPb//gDz
APf//gD0APj//gD1APn//gD2APr//gD3APv//gD4APz//gD5AP3//gD6AP7//gD7AP///gD8AQD//gD
9AQH//gD+AQL//gD/AQP//g=='''))
        with open("grid.png", "wb") as img:
            img.write(base64.b64decode('''
iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29
mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAAMUExURQICAhEREQoKCgAAAMve66sAAALaSURBVH
jaYmAcYAAQQAyMTAMLAAII6ABmPICJkYGZtvIAATTgDgAIoAF3AEAADbgDAAJowB0AEEAD7gCAABpwB
wAE0IA7ACCABtwBAAE04A4ACKABdwBAAA24AwACaMAdABBAA+4AgAAacAcABNCAOwAggAbcAQABNOAO
AAigAXcAQAANuAMAAmjAHQAQQAPuAIAAGnAHAATQgDsAIIAG3AEAATTgDgAIoAF3AEAADbgDAAKIQOe
UkUDflXJ5gAACOmBgu+cAAQR0AAMeAAxCBtrKAwTQgKcBgAAacAcABNCAOwAggAbcAQABNOAOAAigAX
cAQAANuAMAAmjAHQAQQAPuAIAAGnAHAATQgDsAIIAG3AEAATTgDgAIoAF3AEAADbgDAAJowB0AEEAD7
gCAABpwBwAE0IA7ACCABtwBAAE04A4ACKABdwBAAA24AwACaMAdABBAA+4AgAAacAcABNCAOwAggAbc
AQABNOAOAAigAR8fAAigAR8fAAigAR8fAAigAU8DAAE04A4ACKABdwBAAA24AwACaMAdABBAA+4AgAA
acAcABNCAOwAggAbcAQABNOAOAAigAXcAQAANuAMAAmjAHQAQQAPuAIAAGnAHAATQgDsAIIAG3AEAAT
TgDgAIoAF3AEAADbgDAAJowB0AEEAD7gCAABpwBwAE0IA7ACCABtwBAAE04A4ACKABdwBAAA24AwACa
MAdABBAAz4+ABBAAz4+ABBAAz4+ABBAA54GAAJowB0AEEAD7gCAABpwBwAE0IA7ACCABtwBAAE04A4A
CKABdwBAAA24AwACaMAdABBAA+4AgAAacAcABNCAOwAggAbcAQABNOAOAAigAXcAQAANuAMAAmjAHQA
QQAPuAIAAGnAHAATQgDsAIIAG3AEAATTgDgAIoAF3AEAADbgDAAJowB0AEEAD7gCAABpwBwAE0IA7AC
CABnx8ACCABnx8ACDAAIOyqUUTQiRTAAAAAElFTkSuQmCC'''))
        self.texture = Image(source='grid.png').texture
        self.texture.wrap = 'repeat'
        self.texture.uvsize = (8, 8)
        with open("dot.png", "wb") as dot:
            dot.write(base64.b64decode('''
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACXBIWXMAAAsTAAALEwEAmpwYAAAABGd
BTUEAALGOfPtRkwAAACBjSFJNAAB6JQAAgIMAAPn/AACA6QAAdTAAAOpgAAA6mAAAF2+SX8VGAAAAEE
lEQVR42mL4//8/A0CAAQAI/AL+26JNFgAAAABJRU5ErkJggg=='''))
        root = Editor()
        return root

    def _on_keyboard_settings(self, window, *largs):
        key = largs[0]
        setting_key = 282  # F1/Menu

        if key == setting_key:  # toggle settings panel
            self.root.help()
            return True

    def on_stop(self):
        try:
            os.remove('grid.png')
            os.remove('dot.png')
        except EnvironmentError as e:
            print('on removing', e)
        if self.root.changes > 1:
            self.root.exit_save()
        self.root.save_window()


def error_print():
    """ Appends the current error to the log text."""
    with open("err_log.txt", "a") as log:
        log.write('\nCrash@{}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
    traceback.print_exc(file=open("err_log.txt", "a"))
    traceback.print_exc()


if __name__ == '__main__':
    try:
        Rotaboxer().run()
    except Exception:
        error_print()