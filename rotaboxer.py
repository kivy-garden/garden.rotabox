# coding=utf-8
# version 0.8.0 - kivy 1.9.0 - python 2.7.10
'''
ROTABOXER
____________________ RUN THE MODULE DIRECTLY TO USE ___________________________

    Rotaboxer is an editing tool for the Rotabox* bounds.
    With an image as input, the user can visually shape specific colliding
    bounds for it.

    The result is the code (a list or a dictionary) to be used by a Rotabox
    widget, in a kivy project.

    Animated bounds are also supported, with the use of atlases.
    Rotaboxer lets you browse through the individual frames of a sequence
    and define different bounds for each one.

   *___________________________________________________________________________
    Rotabox is a kivy widget, that can have rotatable, custom shaped, animated
    2D colliding bounds.
    To understand the concept of the Rotabox collision detection, you can refer
    to its module's documentation.

unjuan 2016
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import base64
import json
import re
import os
import copy
import time

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


__author__ = 'unjuan'
__version__ = '0.8.0.0'


class ScrollLabel(ScrollView):
    """ A scrolling label with translation and background color options
    """
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(ScrollLabel, self).__init__(**kwargs)


# noinspection PyIncorrectDocstring
def folder_sort(files, filesystem):
    """ Sorts the files and folders in the 'File Dialogs' popups.
    Used in the FileChooserListViewX class
    """
    return (sorted((f for f in files if filesystem.is_dir(f)), key=sorting) +
            sorted((f for f in files if not filesystem.is_dir(f)), key=sorting))


def sorting(item):
    return item[0].upper() if type(item) == list \
        else item.lower()


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


# noinspection PyIncorrectDocstring,PyArgumentList
class LoadDialog(FloatLayout):
    """ 'Load File' popup dialog.
    """
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
            # noinspection PyUnresolvedReferences
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


# noinspection PyIncorrectDocstring,PyArgumentList
class SaveDialog(FloatLayout):
    """ 'Save File' popup dialog.
    """
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
            # noinspection PyUnresolvedReferences
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
        # self.draw_bounds = True

    def on_size(self, *args):
        self.x -= self.size[0] * .5
        self.y -= self.size[1] * .5
        self.update()


class Point(ToggleButton):

    def __init__(self, root, mag, **kwargs):
        super(Point, self).__init__(**kwargs)
        # self.background_color = 1, .5, .6, 1
        self.size_hint = None, None
        self.size = mag * 5, mag * 5
        self.background_normal = self.background_down = 'dot.png'
        self.line = Line(rectangle=(self.x, self.y, self.width, self.height),
                         dash_offset=3, dash_length=2)
        self.canvas.add(Color(0, 1, 0, 1))
        self.canvas.add(self.line)
        self.root = root
        self.appointed = False
        self.clock = None
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
            self.background_color = 1, 1, 1, 1
        else:
            self.opacity = 0

    def on_press(self, *args):
        if self.root.paint_btn.state != 'down':
            for poly in self.root.dummy[self.root.curr_frame].itervalues():
                if self in poly['btn_points']:
                    self.root.curr_poly = poly
                    self.root.curr_index = poly['btn_points'].index(self)
                    break
            self.clock = Clock.schedule_once(self.grab, .12)

    def grab(self, *args):
            self.root.draw_points = False
            Window.bind(on_motion=self.drag)

    def drag(self, *args):
        self.opacity = 0
        self.center = self.root.scat.to_widget(*args[2].pos)
        self.root.draw()

    def on_release(self, *args):
        if not self.root.paint_btn.state == 'down':
            if self.clock and self.clock.is_triggered:
                self.clock.cancel()
            else:
                self.opacity = 1
                self.root.draw_points = True
                Window.unbind(on_motion=self.drag)
                self.root.actions += 1
                self.root.draw()
            self.state = 'down'

    def pop(self, *args):
            point_popup = BoxLayout(orientation='vertical')
            chk_btn = Button(background_color=(.3, .4, .3, 1),
                             on_release=self.root.set_check_point)
            if self.root.curr_index in self.root.curr_poly['check_points']:
                chk_btn.text = 'Undo checkpoint'
            else:
                chk_btn.text = 'Make checkpoint'
            point_popup.add_widget(chk_btn)
            rem_btn = Button(background_color=(.3, .4, .3, 1),
                             on_release=self.root.remove_point)
            rem_btn.text = 'Remove point'
            point_popup.add_widget(rem_btn)
            clear_btn = Button(background_color=(.3, .4, .3, 1),
                               on_release=self.root.confirm_clear)
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
        self.dummy = {'0': {}}
        self.keys = []
        self.curr_frame = '0'
        self.curr_poly = None
        self.curr_index = None
        self.draw_points = True
        self.popup = None
        self.lines = []
        self.dots = []
        self.actions = 0
        self.filename = ''
        self.source = ''
        self.atlas_source = ''
        self.image = ''
        self.code = ''
        self.save_name = ''
        self.mag = 3
        self.last_dir = app_config.get('last dir', './')
        EventLoop.window.bind(on_keyboard=self.on_key)

    # ------------------------ EDITOR -----------------------

    def add_point(self, x, y):
        if not self.curr_poly:
            self.curr_poly = self.dummy[self.curr_frame]['{}'.format(
                str(len(self.dummy[self.curr_frame])))] = {}
            self.curr_poly['btn_points'] = [Point(self, self.mag, pos=(x, y),
                                                  state='down')]
            self.curr_poly['points'] = []
            self.curr_poly['check_points'] = []
            self.scat.add_widget(self.curr_poly['btn_points'][-1])
            self.curr_index = 0
        else:
            self.curr_poly['btn_points'][self.curr_index].state = 'normal'
            self.curr_index += 1
            self.curr_poly['btn_points'].insert(self.curr_index,
                                                (Point(self, self.mag,
                                                       pos=(x, y))))
            self.curr_poly['btn_points'][self.curr_index].state = 'down'
            self.scat.add_widget(self.curr_poly['btn_points'][self.curr_index])
        self.actions += 1
        self.update_points()
        self.draw()

    def remove_point(self, *args):
        try:
            self.curr_poly['btn_points'][self.curr_index].dismiss_popup()
            self.scat.remove_widget(self.curr_poly['btn_points'].pop(
                                    self.curr_index))
            if self.curr_index > -1:
                self.curr_index -= 1
            if len(self.curr_poly['btn_points']):
                self.curr_poly['btn_points'][self.curr_index].state = 'down'
                self.update_points()
            else:
                self.remove_polygon(self.curr_poly)
                self.curr_poly = None
                self.curr_index = None
            self.actions += 1
            self.draw()
        except (IndexError, TypeError) as e:
            print(e)
            pass

    def update_points(self):
        self.curr_poly['check_points'] = []
        for i in xrange(len(self.curr_poly['btn_points'])):
            if self.curr_poly['btn_points'][i].appointed:
                self.curr_poly['check_points'].append(i)

    def confirm_clear(self, *args):
        if self.curr_poly:
            self.warn('Warning!',
                      'You are about to delete a polygon.\n'
                      'Confirm?', self.clear_polygon)

    def clear_polygon(self, *args):
        self.dismiss_popup()
        self.curr_poly['btn_points'][self.curr_index].dismiss_popup()
        while len(self.curr_poly['btn_points']):
            self.scat.remove_widget(self.curr_poly['btn_points'].pop())
        self.remove_polygon(self.curr_poly)
        self.curr_poly = None
        self.actions += 1
        self.draw()

    def remove_polygon(self, poly):
        for k, v in self.dummy[self.curr_frame].items():
            if v == poly:
                del self.dummy[self.curr_frame][k]
                self.curr_index = None

    def set_check_point(self, *args):
        if self.curr_poly:
            self.curr_poly['btn_points'][self.curr_index].dismiss_popup()
            if self.curr_poly['btn_points'][self.curr_index].appointed:
                self.curr_poly['btn_points'][self.curr_index].appointed = False
                self.curr_poly['check_points'].remove(self.curr_index)
            else:
                self.curr_poly['btn_points'][self.curr_index].appointed = True
                self.curr_poly['check_points'].append(self.curr_index)
            self.actions += 1
            self.draw()

    def deselect_polygon(self):
        if self.curr_poly:
            self.curr_poly['btn_points'][self.curr_index].state = 'normal'
            self.curr_poly = None
            self.curr_index = None
            self.draw()

    def navigate(self, btn):
        if self.atlas_source:
            while len(self.scat.children) > 1:
                for point in self.scat.children:
                    if isinstance(point, Point):
                        self.scat.remove_widget(point)
            self.clear()
            self.curr_poly = None
            if btn == '>':
                self.curr_frame = \
                    self.keys[self.keys.index(self.curr_frame) + 1] \
                    if self.keys.index(self.curr_frame) + 1 < len(self.keys) \
                    else self.keys[0]
            else:
                self.curr_frame = \
                    self.keys[self.keys.index(self.curr_frame) - 1] \
                    if self.keys.index(self.curr_frame) > 0 \
                    else self.keys[-1]
            self.sprite.image.source = ('atlas://' + self.filename +
                                        '/' + self.curr_frame)
            for poly in self.dummy[self.curr_frame].itervalues():
                for point in poly['btn_points']:
                    self.scat.add_widget(point)
                    point.opacity = 0
                for index in poly['check_points']:
                    poly['btn_points'][index].appointed = True
            self.curr_poly = None
            self.draw()
            self.board1.text = (self.image + '\n('
                                + str(self.keys.index(self.curr_frame)+ 1)
                                + '  of  '
                                + str(len(self.keys)) + '  frames)')

    def zoom(self, btn):
        if btn == 'plus' and self.scat.scale < 5.1:
            self.scat.scale += 0.4
        elif btn == 'minus' and self.scat.scale > 0.4:
            self.scat.scale -= 0.3

    def help(self):
        content = BoxLayout(orientation='vertical')
        scrl_label = ScrollLabel()
        scrl_label.label.padding_x = 10
        scrl_label.label.color = .75, .45, .75, 1
        scrl_label.scroll_y = 1
        scrl_label.label.font_size = '18sp'
        scrl_label.label.markup = True
        scrl_label.text = '''
{0}[size=22][b]Rotaboxer {4}[/b]{3}

User's manual{1}

{0}[size=18]Description:{3}{1}
    Rotaboxer is an editing tool for the Rotabox{0}*{1}  bounds.
    With an image as input, one can visually shape specific
    colliding bounds for it.
    The result is the code (a list or a dictionary) to be used by a
    Rotabox widget, in a kivy project.
    Animated bounds are also supported, with the use of atlases.
    Rotaboxer lets you browse through the individual frames of
    a sequence and define different bounds for each one.

{0}[size=18]Controls:{3}{1}
    {0}[size=22]Left mouse button:{3}{1}
    Click on the image, to {0}add a new point{1}.
        Each new point is spawn connected to the currently
        selected point and next to it.

    Click on a point to {0}select{1} both the {0}point{1} and the {0}polygon{1} it
        belongs to.

    Drag a {0}point{1} to {0}move{1} it around.

    Drag on the image, while in {0}paint{1} mode, to {0}test{1} your bounds
        by painting on the collidable areas.

    {0}[size=22]Right mouse button:{3}{1}
    Click on a {0}point{1} to open its context {0}menu{1}.

    Drag to {0}position{1} the {0}workspace{1}.

    {0}[size=22]Mouse scroll:{3}{1}
    Scroll to {0}zoom{1}.

    {0}[size=22]Buttons & Keys:{3}{1}
{0}[size=18]Arrow keys:{3}{1}
    Move a point around, if one is selected.
    (Speed options when used with Shift or Control keys).
    Else, navigate or zoom (see below)

[color=#cc9966]{2}[b][Open][/b]{3}{1} button ({0}{2}O{3}{1} key):
    Prompts to open an image (.png), an image atlas (.atlas),
    or a previously saved project file (.rbx).

[color=#9999ff]{2}[b][□ Save][/b]{3}{1} button ({0}{2}S{3}{1} key):
    Prompts to save current project to a project file.
    If checked, it functions as a quick save (no dialog).
    (Keep the project file with its image, to be able to open it).

    {0}Auto Save{1}: If the user exits the editor without saving changes,
    the project is automatically appended to the 'sessions.json'
    file, at the editor's location, with date and name added to it.
    So, if exited by mistake (not a crash), one can retrieve the
    session by copying the appropriate line from the json file to
    make a new rbx file.
    Note, that the file is not maintained by the program and its
    cleanup or disposal is at the user's discretion.

[color=#9999ff][size=22][b][?][/b]{3}{1} button ({0}{2}F1{3}{1} key):
    Leads here.

[color=#7272bf][size=24][b][<][>][/b]{3}{1} buttons ({0}{2}Left-Right{3}{1} keys):
    Navigate through an atlas' images.

[color=#9999ff][size=18][□]{3}{1} [color=#7272bf][size=24][b][□][/b]{3}{1} buttons ({0}{2}Up-Down{3}{1} keys):
    Zoom.

[color=#729972]{2}[b][Deselect][/b]{3}{1} button ({0}{2}D{3}{1} key):
    Each new point is automatically a part of a polygon.
    This button deselects the current polygon, so the next new
    point will start a new one.

[color=#729972]{2}[b][Check-point][/b]{3}{1} button ({0}{2}Space{3}{1} key):
    Makes the selected point one of the collision check-points
    for its container polygon.

[color=#729972]{2}[b][Remove point][/b]{3}{1} button ({0}{2}Delete{3}{1} key):
    Deletes the selected point.

[color=#729972]{2}[b][Delete polygon][/b]{3}{1} button ({0}{2}Ctrl + Delete{3}{1} keys):
    Deletes the polygon that contains the selected point.

[color=#ff99ff]{2}[b][Paint][/b]{3}{1} button ({0}{2}P{3}{1} key):
    Enables mouse painting over the bounded areas, to test
    collision detection. A testing tool.

[color=#9999ff]{2}[b][Clear][/b]{3}{1} button ({0}{2}C{3}{1} key):
    Cleans after the Paint mode.

[color=#cc9966]{2}[b][Code to Clipboard][/b]{3}{1} button ({0}{2}Ctrl + C{3}{1} keys):
    Copies the resulting code to clipboard, to use in a project.
    {0}NOTE:{1} Image.source's path in the code will be relative to
    where Rotaboxer is (if in the same drive).

     ____________________________________________________________________________
  {0}*{1} Rotabox is a kivy widget, that can have rotatable, custom
    shaped, animated colliding bounds.
    To understand the concept of the Rotabox collision detection,
    you can refer to its module's documentation.
        '''.format('[color=#ffffff]', '[/color]', '[size=20]', '[/size]',
                   __version__)
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

    # ------------------------ VISUALS -----------------------

    def update(self):
        if self.paint_btn.state == 'down':
            if self.curr_index:
                self.curr_poly['btn_points'][self.curr_index].opacity = 0
            self.make_points()
            sw = self.sprite.width
            sh = self.sprite.height
            self.sprite.bounds = [[[(round(float(pt[0]) / sw, 3),
                                     round(float(pt[1]) / sh, 3))
                                    for pt in poly['points']],
                                   poly['check_points']]
                                  for poly
                                  in self.dummy[self.curr_frame].itervalues()]
            self.sprite.custom_bounds = True
            for entry in self.ids:
                if hasattr(self.ids[entry], 'group'):
                    if self.ids[entry].group == 'edit':
                        self.ids[entry].disabled = True
            self.paint_btn.background_color = 1.8, .3, .5, 1
        else:
            if self.curr_poly:
                self.curr_poly['btn_points'][self.curr_index].opacity = 1
            self.sprite.bounds = [[[(0, 0), (1, 0), (1, 1), (0, 1)], [0, 2]]]
            for entry in self.ids:
                if hasattr(self.ids[entry], 'group'):
                    if not self.ids[entry].group == 'nav':
                        self.ids[entry].disabled = False
                    elif self.atlas_source:
                        self.ids[entry].disabled = False
                    else:
                        self.ids[entry].disabled = True
            self.paint_btn.background_color = .3, .15, .3, 1
        try:
            self.sprite.define_bounds()
        except TypeError as e:
            print(e)

        if not len(self.dots):
            self.clear_btn.disabled = True
        else:
            self.clear_btn.disabled = False

        if self.curr_poly and not len(self.curr_poly['btn_points']):
            self.curr_poly = None

    def make_points(self):
        for frame in self.dummy.itervalues():
            for poly in frame.itervalues():
                poly['points'] = [(point.center_x - self.sprite.x,
                                   point.center_y - self.sprite.y)
                                  for point in poly['btn_points']]

    def hover(self, *args):
        pos = Window.mouse_pos
        if self.load_btn.collide_point(*pos):
            self.board2.text = 'Open  image,  atlas  or  project  file.  [O]'
            return True
        if self.save.collide_point(*pos):
            self.board2.text = 'Save  current  project  to  a  project  file.\n' \
                               'If  checked,  it  functions  as  a  quick  ' \
                               'save  (no dialog)  [S].'
            return True
        if self.help_btn.collide_point(*pos):
            self.board2.text = 'Help  [F1]'
            return True
        if self.prev.collide_point(*pos):
            self.board2.text = "Navigate  through  an  atlas'  images.  [Left]"
            return True
        if self.next.collide_point(*pos):
            self.board2.text = "Navigate  through  an  atlas'  images.  [Right]"
            return True
        if self.minus.collide_point(*pos):
            self.board2.text = 'Zoom  out.  [Down]'
            return True
        if self.plus.collide_point(*pos):
            self.board2.text = 'Zoom  in.  [Up]'
            return True
        if self.des_btn.collide_point(*pos):
            self.board2.text = 'Next  point  will  start  a  new  polygon.  [D]'
            return True
        if self.chk_btn.collide_point(*pos):
            self.board2.text = 'Promote  the  selected  point  to  a  ' \
                               'check-point  and  vice  versa.  [Space]'
            return True
        if self.rem_btn.collide_point(*pos):
            self.board2.text = 'Remove  the  selected  point.  [Delete]'
            return True
        if self.clear_pol.collide_point(*pos):
            self.board2.text = 'Delete  the  selected  polygon.  [Ctrl] + [Delete]'
            return True
        if self.paint_btn.collide_point(*pos):
            self.board2.text = 'Enable / Disable  Paint  mode.  [P]'
            return True
        if self.clear_btn.collide_point(*pos):
            self.board2.text = 'Clean  after  the  Paint  mode.  [C]'
            return True
        if self.copy_btn.collide_point(*pos):
            self.board2.text = 'Copy  the  resulting  code  to  clipboard,  ' \
                               'to  use  in  a  project.  [Ctrl] + [C]'
            return True
        if self.paint_btn.state == 'down':
            self.board2.text = ('Paint  on  the  image  to  test  the  '
                                'collidable  areas.')
        else:
            self.board2.text = ('Click  to  add,  select  or  move  a  point.  '
                                'Right  click  to  move  canvas  or  on  '
                                'point  for  context  menu.  '
                                'Scroll  to  zoom.')

    # noinspection PyArgumentList
    def draw(self):
        while len(self.lines):
            self.scat.canvas.remove(self.lines.pop(0))
        mag = self.mag
        with self.scat.canvas:
            for poly in self.dummy[self.curr_frame].values():
                for i in xrange(len(poly['btn_points'])):
                    if self.draw_points:
                        Color(1, 0, 1, 1)
                        if poly['btn_points'][i].appointed:
                            Color(0.29, 0.518, 1, 1)
                        self.lines.append(Line(
                            circle=(poly['btn_points'][i].center_x,
                                    poly['btn_points'][i].center_y, mag)))
                    Color(.7, 0, .7, 1)
                    k = i - 1 if i > 0 else -1
                    if poly['btn_points'][i].appointed or poly['btn_points'][k].appointed:
                            Color(0.29, 0.518, 1, 1)
                    self.lines.append(Line(
                        points=(poly['btn_points'][i].center_x,
                                poly['btn_points'][i].center_y,
                                poly['btn_points'][k].center_x,
                                poly['btn_points'][k].center_y)))

    def clear(self):
        while len(self.dots):
            self.scat.canvas.remove(self.dots.pop(0))
        self.clear_btn.disabled = True

    # ------------------------ INPUT -----------------------

    def load_dialog(self, *args):
        """ Shows the 'Import/Open' dialog.
        """
        if self.popup:
            self.actions = 0
            self.dismiss_popup()
        if self.actions:
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

            # Clean up
            for frame in self.dummy.itervalues():
                for poly in frame.itervalues():
                    while len(poly['btn_points']):
                        self.scat.remove_widget(poly['btn_points'].pop())
            self.curr_poly = None
            self.atlas_source = ''
            self.dummy = {'0': {}}
            self.keys = []
            self.curr_frame = '0'
            self.sprite.size = 100, 100
            self.sprite.pos = self.width * .5, self.height * .5
            self.scat.scale = 1
            self.actions = 0
            self.clear()
            try:
                self.sprite.remove_widget(self.sprite.image)
            except AttributeError as e:
                print(e)
                pass
            # if filename[0].endswith('.rbx'):
            if filename.endswith('.rbx'):
                self.load_proj(filename, path)
            else:
                self.load_img(filename, path)
        Clock.schedule_interval(self.hover, .1)
        self.update()
        self.draw()

    def load_img(self, filename, path, source=None):
        self.dismiss_popup()
        filename = os.path.join(path, filename)
        self.filename = filename.replace('.png',
                                         '').replace('.atlas',
                                                     '').replace('.rbx', '')
        if source:
            filename = filename.replace(filename.split('\\')[-1], source)
        self.image = filename.split('\\')[-1]
        self.save_name = self.filename + '.rbx'
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
                try:
                    self.atlas_source = ('atlas://' +
                                         os.path.relpath(self.filename) +
                                         '/' + self.keys[0])
                except ValueError as e:
                    self.atlas_source = ('atlas://' +
                                         self.filename + '/' + self.keys[0])
                    print(e)
                for key in self.keys:
                    self.dummy[key] = {}
                self.curr_frame = self.keys[0]
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
                                + str(self.keys.index(self.curr_frame)+ 1)
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
                    self.warn('Image "{}" is not found.'.format(project['image']),
                              'Please, put the image with\n'
                              'the project file and try again.',
                              action=self.dismiss_popup, cancel=0)
                    return
            del project['image']
            self.dummy = copy.deepcopy(project)
            for frame in self.dummy.itervalues():
                for poly in frame.itervalues():
                    poly['btn_points'] = []
                    for point in poly['points']:
                        bpos = point[0] + self.sprite.x, point[1] + self.sprite.y
                        poly['btn_points'].append(Point(self, self.mag, pos=bpos))

            for poly in self.dummy[self.curr_frame].values():
                for i in xrange(len(poly['btn_points'])):
                    point = poly['btn_points'][i]
                    self.scat.add_widget(point)
                    point.opacity = 0
                    if i in poly['check_points']:
                        point.appointed = True

    # ------------------------ OUTPUT -----------------------

    def make_hints(self, frame):
        for poly in frame.itervalues():
            poly['points'] = [(round(float(point.center_x - self.sprite.x) /
                                     self.sprite.width, 3),
                               round(float(point.center_y - self.sprite.y) /
                                     self.sprite.height, 3))
                              for point in poly['btn_points']]

    def write(self):
        py = self.lang_btn.text.lstrip().startswith('py')
        if self.atlas_source:
            for frame in self.dummy.itervalues():
                self.make_hints(frame)
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
        self.dummy[self.curr_frame].itervalues()
        self.make_hints(self.dummy[self.curr_frame])
        if py:
            self.code = 'bounds = ['
        else:
            self.code = 'bounds:\n                ['
        self.write_more(self.curr_frame, py)
        self.code += ']'

    def write_more(self, frame, py):
        if self.atlas_source:
            poiws = '\n                               '
            chpws = '\n                              '
            polws = '\n                             '
        else:
            poiws = '\n                         '
            chpws = '\n                        '
            polws = '\n                       '
        kvspace = '\n                '
        for i in xrange(len(self.dummy[frame])):
            poly = self.dummy[frame][unicode(i)]
            self.code += '[['
            for point in poly['points']:
                self.code += '(' + str(point[0]) + ', ' + str(point[1]) + '), '
                # if len(self.code.split('\n')[-1]) > 40:
                if py and len(self.code.split('\n')[-1]) > 40:
                    self.code += poiws
                elif len(self.code.split('\n')[-1]) > 64:
                    self.code += kvspace
            self.code = (self.code.rstrip(',\n ') + '], ')
            if py:
                self.code += chpws + (str(poly['check_points']) + '],' + polws)
            elif len(self.code.split('\n')[-1]) > 65:
                self.code += kvspace + (str(poly['check_points']) + '],' + kvspace)
            else:
                self.code += (str(poly['check_points']) + '],' + kvspace)
        self.code = self.code.rstrip(',\n ')

    def copy(self):
        # if self.lang_btn.text.startswith('py'):
        self.write()
        # else:
        #     self.write2()
        code = self.code.decode('utf-8')
        Clipboard.copy(code)
        print(Clipboard.paste())

    def save_dialog(self, *args):
        """ Shows the 'Save project' dialog.
        """
        if self.popup:
            self.dismiss_popup()
        content = SaveDialog(save=self.save_check, cancel=self.dismiss_popup,
                             file_types=['*.rbx'])
        content.ids.filechooser.path = self.last_dir
        content.text_input.text = (self.save_name.split('\\')[-1] or
                                   self.filename.split('\\')[-1]) + '.rbx'
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
        self.make_points()
        project = copy.deepcopy(self.dummy)
        for frame in project.itervalues():
            for poly in frame.itervalues():
                del poly['btn_points']
        project['image'] = self.image
        try:
            with open(self.save_name, 'w+') as proj:
                json.dump(project, proj, sort_keys=True, indent=4)
        except IOError as e:
            print('On saving:', e)
            pass
        else:
            self.actions = 0

    def exit_save(self, *args):
        self.make_points()
        for frame in self.dummy.itervalues():
            for poly in frame.itervalues():
                del poly['btn_points']
        project = {'..date': time.strftime("%Y/%m/%d_%H:%M:%S"),
                   '..name': self.save_name,
                   '.image': self.image}
        project.update(self.dummy)
        try:
            with open('sessions.json', 'a') as proj:
                out = json.dumps(project, proj, separators=(',', ':'),
                                 sort_keys=True)
                proj.write(out + '\n')
        except IOError as e:
            print('On saving:', e)
            pass

    # ------------------------ OTHER -----------------------

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
        try:
            for entry in self.ids:
                widg = self.ids[entry]
                if (isinstance(widg, (Button, ScrollLabel)) and
                        widg.collide_point(*touch.pos))\
                    or ((entry == 'save_btn' or entry == 'chk_box') and
                            widg.collide_point(*widg.to_widget(*touch.pos))):
                    if mouse_btn != 'right':
                        super(Editor, self).on_touch_down(touch)
                        self.update()
                    return True
            pos = self.scat.to_widget(*touch.pos)
            for child in self.scat.children:
                if (isinstance(child, ToggleButton) and
                        child.collide_point(*pos) and
                        self.paint_btn.state != 'down'):
                    super(Editor, self).on_touch_down(touch)
                    if mouse_btn == 'right':
                        child.pop()
                    self.update()
                    self.draw()
                    return True
            if mouse_btn == 'right':
                super(Editor, self).on_touch_down(touch)
                return
            elif self.paint_btn.state != 'down':
                self.add_point(*pos)
                super(Editor, self).on_touch_down(touch)
        except IndexError as e:
            pass
            print('touch_down', e)

    # noinspection PyArgumentList
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
                with self.scat.canvas:
                    Color(.7, .3, 0, 1)
                    self.dots.append(Line(circle=(pos[0], pos[1], 1)))
                self.clear_btn.disabled = False
        else:
            super(Editor, self).on_touch_move(touch)
            self.draw()

    # noinspection PyUnusedLocal
    def on_key(self, window, key, *args):
        """ What happens on keyboard press"""
        # print(key, args)
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
                                    self.popup.content.filechooser.selection)
                elif self.popup.title.startswith('Save'):
                    self.save_check(self.popup.content.filechooser.path,
                                    self.popup.content.text_input.text)
                elif self.popup.title.startswith('Image'):
                    self.dismiss_popup()
                else:
                    for child in self.popup.content.children:
                        if isinstance(child, Label):
                            if child.text.startswith('Project'):
                                self.load_dialog()
                            elif child.text.startswith('Filename'):
                                self.save_proj()
                            elif child.text.startswith('You'):
                                self.clear_polygon()
            return True
        if key == 111:  # O
            self.load_dialog()
        if key == 115:  # S
            if self.chk_box.active:
                self.save_proj()
            else:
                self.save_dialog()
        if key == 100:  # D
            self.deselect_polygon()
        if key == 32 and self.curr_index:  # Space
            self.set_check_point()
        if key == 127:  # Delete
            if ['ctrl'] in args:
                self.confirm_clear()
            else:
                self.remove_point()
        if key == 112:  # P
            if self.paint_btn.state == 'down':
                self.paint_btn.state = 'normal'
            else:
                self.paint_btn.state = 'down'
        if key == 99:  # C
            if ['ctrl'] in args:
                self.copy()
            else:
                self.clear()

        if key == 273:  # up
            if self.curr_index is not None:
                if ['ctrl'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_y += .1
                elif ['shift'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_y += 10
                else:
                    self.curr_poly['btn_points'][self.curr_index].center_y += 1
            else:
                self.zoom('plus')
        if key == 274:  # down
            if self.curr_index is not None:
                if ['ctrl'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_y -= .1
                elif ['shift'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_y -= 10
                else:
                    self.curr_poly['btn_points'][self.curr_index].center_y -= 1
            else:
                self.zoom('minus')
        if key == 275:  # right
            if self.curr_index is not None:
                if ['ctrl'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_x += .1
                elif ['shift'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_x += 10
                else:
                    self.curr_poly['btn_points'][self.curr_index].center_x += 1
            else:
                self.navigate('>')
        if key == 276:  # left
            if self.curr_index is not None:
                if ['ctrl'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_x -= .1
                elif ['shift'] in args:
                    self.curr_poly['btn_points'][self.curr_index].center_x -= 10
                else:
                    self.curr_poly['btn_points'][self.curr_index].center_x -= 1
            else:
                self.navigate('<')
        self.draw()

    @staticmethod
    def sanitize_filename(filename):
        """ Creates a safe filename from the text input
        of the 'Save File' dialog.
        """
        filename = re.sub(r'[/:*?"<>|\\]', "_", filename)
        return filename

    def dismiss_popup(self, *args):
        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def warn(self, title, text, action, cancel=1):
        """ Opens a dialog with a warning
        """
        content = BoxLayout(orientation='vertical')
        label = Label(halign='center')
        label.text = text
        content.add_widget(label)

        buttons = BoxLayout(size_hint=(1, .5))

        if cancel:
            cancel_btn = Button(background_color=(.3, .3, .5, 1),
                                on_press=self.dismiss_popup)
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


class Rotaboxer(App):
    texture = ObjectProperty()

    def build(self):
        self.use_kivy_settings = False
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
        except EnvironmentError:
            pass
        if self.root.actions:
            self.root.exit_save()
        self.root.save_window()

if __name__ == '__main__':
    Rotaboxer().run()
