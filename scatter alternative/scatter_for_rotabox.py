'''Scatter2 (for Rotabox):
A basic alternative of the Scatter widget, that doesn't use matrices.
Made, using code from the original Scatter, altered to be compatible with the
Rotabox widget.
The idea is to put a Rotabox in it, as a child.
'''

from math import radians
from kivy.properties import BooleanProperty, AliasProperty, NumericProperty
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.uix.widget import Widget


class Scatter2(Widget):

    __events__ = ('on_transform_with_touch', 'on_bring_to_front')

    auto_bring_to_front = BooleanProperty(True)
    '''If True, the widget will be automatically pushed on the top of parent
    widget list for drawing.

    :attr:`auto_bring_to_front` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to True.
    '''

    do_translation_x = BooleanProperty(True)
    '''Allow translation on the X axis.

    :attr:`do_translation_x` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    do_translation_y = BooleanProperty(True)
    '''Allow translation on Y axis.

    :attr:`do_translation_y` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    def _get_do_translation(self):
        return (self.do_translation_x, self.do_translation_y)

    def _set_do_translation(self, value):
        if type(value) in (list, tuple):
            self.do_translation_x, self.do_translation_y = value
        else:
            self.do_translation_x = self.do_translation_y = bool(value)
    do_translation = AliasProperty(
        _get_do_translation, _set_do_translation,
        bind=('do_translation_x', 'do_translation_y'))
    '''Allow translation on the X or Y axis.

    :attr:`do_translation` is an :class:`~kivy.properties.AliasProperty` of
    (:attr:`do_translation_x` + :attr:`do_translation_y`)
    '''

    do_rotation = BooleanProperty(True)
    '''Allow rotation.

    :attr:`do_rotation` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    do_scale = BooleanProperty(True)
    '''Allow scaling.

    :attr:`do_scale` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    '''Minimum scaling factor allowed.'''
    scale_min = NumericProperty(0.1)

    '''Maximum scaling factor allowed.'''
    scale_max = NumericProperty(1e20)

    def __init__(self, **kwargs):
        self._touches = []
        self._last_touch_pos = {}
        self._trigger_layout = Clock.create_trigger(self.do_layout, -1)
        super(Scatter2, self).__init__(**kwargs)
        self.child = None
        self.scale_f = 1.

    def add_widget(self, widget, index=0, **kwargs):
        if self.children:
            raise Exception('Scatter2 can have one child only.')
        super(Scatter2, self).add_widget(widget, index)
        self.child = self.children[0]
        self.child.bind(parent=self._trigger_layout,
                        size=self._trigger_layout,
                        pos=self._trigger_layout)

    def do_layout(self, *largs, **kwargs):
        self.center = self.child.center

    def collide_point(self, x, y):
        return self.child.collide_point(x, y)

    def transform_with_touch(self, touch):
        # just do a simple one finger drag
        changed = False
        if len(self._touches) == 1:
            # _last_touch_pos has last pos in correct parent space,
            # just like incoming touch
            dx = (touch.x - self._last_touch_pos[touch][0]) \
                * self.do_translation_x
            dy = (touch.y - self._last_touch_pos[touch][1]) \
                * self.do_translation_y

            self.child.x += dx
            self.child.y += dy

            changed = True

        if len(self._touches) == 1:
            return changed

        # we have more than one touch... list of last known pos
        points = [Vector(self._last_touch_pos[t]) for t in self._touches
                  if t is not touch]
        # add current touch last
        points.append(Vector(touch.pos))

        # we only want to transform if the touch is part of the two touches
        # farthest apart! So first we find anchor, the point to transform
        # around as another touch farthest away from current touch's pos
        anchor = max(points[:-1], key=lambda p: p.distance(touch.pos))

        # now we find the touch farthest away from anchor, if its not the
        # same as touch. Touch is not one of the two touches used to transform
        farthest = max(points, key=anchor.distance)
        if farthest is not points[-1]:
            return changed

        # ok, so we have touch, and anchor, so we can actually compute the
        # transformation
        old_line = Vector(*touch.ppos) - anchor
        new_line = Vector(*touch.pos) - anchor
        if not old_line.length():   # div by zero
            return changed

        angle = radians(new_line.angle(old_line)) * self.do_rotation
        self.child.angle += angle * 50

        if self.do_scale:
            diff = new_line.length() - old_line.length()
            min_dim = min(self.child.width, self.child.height)
            min_dim_orig = min_dim / self.scale_f

            if self.scale_min < (min_dim + diff) / min_dim_orig < self.scale_max:
                self.child.width += diff * 2
                self.child.height += diff * 2
                self.child.center = self.center
                self.scale_f = (min(self.child.width, self.child.height) /
                                min_dim_orig)
                changed = True
        return changed

    def _bring_to_front(self, touch):
        # auto bring to front
        if self.parent:
            parent = self.parent
            if parent.children[0] is self:
                return
            parent.remove_widget(self)
            parent.add_widget(self)
            self.dispatch('on_bring_to_front', touch)

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        # if not self.do_collide_after_children:
        if not self.collide_point(x, y):
            return False

        # if we don't have any active
        # interaction control, then don't accept the touch.
        if not self.do_translation_x and \
                not self.do_translation_y and \
                not self.do_rotation and \
                not self.do_scale:
            return False

        if self.auto_bring_to_front:
            self._bring_to_front(touch)
        touch.grab(self)
        self._touches.append(touch)
        self._last_touch_pos[touch] = touch.pos

        return True

    def on_touch_move(self, touch):
        x, y = touch.x, touch.y

        # rotate/scale/translate
        if touch in self._touches and touch.grab_current == self:
            if self.transform_with_touch(touch):
                self.dispatch('on_transform_with_touch', touch)
            self._last_touch_pos[touch] = touch.pos

        # stop propagating if its within our bounds
        if self.collide_point(x, y):
            return True

    def on_touch_up(self, touch):
        x, y = touch.x, touch.y

        # remove it from our saved touches
        if touch in self._touches and touch.grab_state:
            touch.ungrab(self)
            del self._last_touch_pos[touch]
            self._touches.remove(touch)

        # stop propagating if its within our bounds
        if self.collide_point(x, y):
            return True

    def on_transform_with_touch(self, touch):
        '''
        Called when a touch event has transformed the scatter widget.
        By default this does nothing, but can be overriden by derived
        classes that need to react to transformations caused by user
        input.

        :Parameters:
            `touch`: the touch object which triggered the transformation.

        .. versionadded:: 1.8.0
        '''
        pass

    def on_bring_to_front(self, touch):
        '''
        Called when a touch event causes the scatter to be brought to the
        front of the parent (only if :attr:`auto_bring_to_front` is True)

        :Parameters:
            `touch`: the touch object which brought the scatter to front.

        .. versionadded:: 1.9.0
        '''
        pass