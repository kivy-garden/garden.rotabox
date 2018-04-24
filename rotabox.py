'''

ROTABOX                                           kivy 1.10.0 - python 2.7.13
=======

Rotabox is a *kivy widget* with customizable 2D bounds that follow its rotation.
The users can shape their own, specific bounds, to fit an image (or a series of
images in an animation), using  a visual editor (See Rotaboxer below).

Rotabox also offers multitouch interactivity (drag, rotation and scaling).

==========================
Features & particularities

Collision detection methods:
    Rotabox offers two collision approaches.
    They can't be both used at the same time on the same widget and, normally,
    collisions are thought to happen between widgets that use the same detection
    method.
    Combinations between the two are possible but rather heavier.

* Segment intersection detection (Default option):
    (See 'Introduction to Algorithms 3rd Edition', ch.33 Computational Geometry
    (https://mitpress.mit.edu/books/introduction-algorithms)
    and 'Line Segment Intersection' lecture notes by Jeff Erickson
    (http://jeffe.cs.illinois.edu/teaching/373/notes/x06-sweepline.pdf))
    
    * Supports open-shaped bounds, down to just a single line segment.
    
    * Interacts with Rotaboxes that use either detection method
        (more expensive if method is different) and regular widgets.
    
    * In a positive check against a Rotabox of the same method, instead of
        *True*, both the intersected sides' indices and their respecrive
        polygons' indices are returned, in the form of:
        [(this_pol_i, this_side_i), (that_pol_i, that_side_i)].

* Point membership in polygon detection:
    (See 'Even-odd rule'(https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule "")
    
    * It can be less expensive when dealing with complex shapes (more than 15
        segments), as it can benefit from breaking these shapes into more simple
        ones when making the bounds in the editor.
    
    * Requires mutual collision checks (All involved widgets should check for
        an accurate reading).
        
    * Interacts with Rotaboxes that use the same detection method and regular
        widgets (but behaving, itself, like a regular widget while doing so).
        
    * In a positive check against a Rotabox of the same method, instead of
        *True*, the checker's collided polygon's index is returned, in a tuple 
        (i) to always evaluate to True.

Hidden collision bounds
    Rotabox can hide certain polygons from others' collision checks and use them
    as one-way detectors.
    A second layer of bounds can have its uses (e.g. in longer distances, acting
    as the 'perception' of an enemy sprite in a game).

Open collision bounds (Segment method only)
    If a polygon is open, the segment between the last and first points of the
    polygon is not considered in the collision checks.
    Since the segment collision method is only concerned with the polygon's
    sides, a widget can 'enter' an open polygon, passing through the opening,
    and then hit the back wall from inside, for example.
    Note that *collide_point* doesn't work for an open polygon (i.e. an open
    polygon cannot be touched).

Visual point tracking
    Since a rotating widget doesn't really rotate, its points lose their
    reference to its visual (Positional properties like [top] or [center] don't
    rotate).
    Rotabox can track any of its own points while rotating, provided that they
    are predefined (Hence, the custom bounds' ability).
    They then can be accessed using their indices.
    This can be useful, for example, in changing the point of rotation to a
    predefined point on the widget while the latter is rotating.
    These points could be another use for the 'hidden bounds' feature (see
    above) when using other points for collision detection at the same time.

Touch interactivity
    Since, due to the differences between the Scatter and Rotabox concepts, a
    way to combine the two couldn't be found, Rotabox uses the Scatter widget's
    code, modified to act on the actual size and position of the widget and
    child (essential for accurate collision detection).
    It supports single and multitouch drag, rotation and scaling (the latter two
    use the *origin* property in the singletouch option).

Restrictions
* In order to be able to maintain any arbitrary aspect ratio (e.g. its image's
    ratio), Rotabox can't use the *size_hint* property.
    Try using *size* property in a relative manner instead
    (e.g. `self.width = self.parent.width * .5`).

* Rotabox can only have one child. It can be an *Image* but not necessarily.
    Grandchildren, however, can collide independently, only if the widget is not
    rotated ( *angle* must be *0* ).

===
API

Basic Usage
    To use Rotabox, just include *rotabox.py* in your project files.

        from rotabox import Rotabox
        ...
        rb = Rotabox()
        rb.add_widget(Image(source='img.png'))
        self.add_widget(rb)

The instance's default bounding box will be a rectangle, the size of the image,
that rotates with it.
Use *angle* and *origin* properties for rotation.

_________
Interface

**angle** *NumericProperty* (0):
    The angle of rotation in degrees.

**origin** *AliasProperty* *tuple* (center):
    Sets the point of rotation. Default position is the widget's center.

**image** *ObjectProperty*:
    Rotabox's only child will most likely be an *Image*.
    If not so, Rotabox will attempt to find the topmost *Image* in its tree and
    assign it to this property.
    Otherwise, the user can specify an *image* somewhere in the widget's tree,
    that the custom bounds will use as a reference.
    An .atlas spritesheet can also be used as an animation source and different
    bounds can be defined for each frame.

**aspect_ratio** *NumericProperty* (0.)
    If not provided, *image*'s ratio is going to be used.

_______________________________
Customizing the Collidable Area

**Rotaboxer** Visual editor.
    A convenient way to define the *custom_bounds* of a Rotabox widget.
    To use it, run *rotaboxer.py* directly. It can be found at the repository
    root.
    Open a *.png* image or an *.atlas* file in the editor, draw bounds for it
    and export the resulting code to clipboard, to use in a Rotabox widget.

**custom_bounds** *ObjectProperty* (`[[(0, 0), (1, 0), (1, 1), (0, 1)]]`)
    This is where the custom bounds are being defined.
    It's also the output of the Rotaboxer tool (above).
    It can be a *list* of one or more polygons' data as seen in its default
    value, above.

    Each polygon's data is a *list* of point tuples `(x, y)`.
    Points' values should be expressed as percentages of the widget's *width*
    and *height*, where `(0, 0)` is widget's `(x, y)`, `(1, 1)` is widget's
    `(right, top)` and `(.5, .5)` is widget's *center*.

    Here's another example with more polygons:

        self.bounds = [[(0.013, 0.985), (0.022, 0.349),
                        (0.213, 0.028), (0.217, 0.681)],
                       [(0.267, 0.346), (0.483, -0.005),
                         (0.691, 0.316), (0.261, 0.975)],
                       [(0.539, 0.674), (0.73, 0.37),
                         (0.983, 0.758)]]

    *custom_bounds* can also be a *dictionary*, in case of animated bounds
    (different bounds for different frames of an animation sequence in an
    *.atlas* file), where the *keys* correspond to the frame names in the
    *.atlas* file and each *item* is a *list* of one or more polygons' data
    like the above.
    Here's an example of such a *dictionary*:

        self.bounds = {'00': [[(0.201, 0.803), (0.092, 0.491),
                               (0.219, 0.184), (0.526, 0.064)],
                              [(0.419, 0.095), (0.595, 0.088),
                                (0.644, 0.493)]],
                       '01': [[(0.357, 0.902), (0.17, 0.65),
                               (0.184, 0.337), (0.343, 0.095),
                               (0.644, 0.098)]],
                       '02': [[(...
                                ...
                               ... etc ]]}

**hidden_bounds** *ListProperty*:
    If a polygon's index is in this list, the polygon becomes 'invisible' to the
    collision checks of others.

**segment_mode** *BooleanProperty* (True):
    Toggle between the two collision detection methods *(See Features above)*.

**open_bounds** *ListProperty*:
    If a polygon's index is in this list, the segment between the last and first
    points of the polygon is not considered in the collision checks
    (segment_mode only).

**draw_bounds** *BooleanProperty* (False):
    This option could be useful during testing, as it makes the widget's bounds
    visible.

_______________
Touch interface
    Most of it is familiar from the Scatter widget.

**touched_to_front** *BooleanProperty* (False)
    If touched, the widget will be pushed to the top of the parent widget tree.

**collide_after_children** *BooleanProperty* (True)
    If True, limiting the touch inside the bounds will be done after dispaching
    the touch to the child and grandchildren, so even outside the bounds they
    can still be touched.
    *IMPORTANT NOTE: Grandchildren, inside or outside the bounds, can collide
    independently ONLY if widget is NOT ROTATED ( *angle* must be *0* ).*

Single touch definitions:

**single_drag_touch** *BoundedNumericProperty* (1, min=1)
    How many touches will be treated as one single drag touch.

**single_trans_touch** *BoundedNumericProperty* (1, min=1)
 How many touches will be treated as one single transformation touch.

Single touch operations:

**allow_drag_x** *BooleanProperty* (False)
**allow_drag_y** *BooleanProperty* (False)
**allow_drag** *AliasProperty*

**single_touch_rotation** *BooleanProperty* (False)
    Rotate around *origin*.

**single_touch_scaling** *BooleanProperty* (False)
    Scale around *origin*.

Multitouch rotation/scaling:

**multi_touch_rotation** *BooleanProperty* (False)
**multi_touch_scaling** *BooleanProperty* (False)

_________________
Utility interface

**scale** *AliasProperty*
    Current widget's scale.

**scale_min** *NumericProperty* (0.01)
**scale_max** *NumericProperty* (1e20)
    Optional scale restrictions.

**pivot** *ReferenceListProperty*
    The point of rotation and scaling.
    While *origin* property sets *pivot*'s position, relatively to widget's
    *size* and *pos*, *pivot* itself can be used to position the widget, much
    like *pos* or *center*.

**ready** *BooleanProperty* (False)
    Useful to read in cases where the widget is stationary.
    Signifies the completion of the widget's initial preparations.

**get_point(pol_index, point_index)** *Method*
    Returns the current position of a certain point.
    The argument indices are based on user's [custom_bounds]' structure.

**draw_bounds** *BooleanProperty* (False)
    This option could be useful during testing, as it makes the widget's bounds
    visible.


___________________________________________________________________________
A Rotabox example can be seen if this module is run directly.

unjuan 2018
'''

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.graphics import PushMatrix, Rotate, PopMatrix
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import (NumericProperty, ReferenceListProperty,
                             AliasProperty, ObjectProperty, BooleanProperty,
                             ListProperty, BoundedNumericProperty)
from math import radians, atan2, sin, cos
from itertools import izip

__author__ = 'unjuan'
__version__ = '0.10.1'

__all__ = 'Rotabox'


class Rotabox(Widget):
    '''See module's documentation.'''

    __events__ = ('on_transform_with_touch', 'on_touched_to_front')

    '''This should be the image that any custom bounds are meant for.
    If not defined, widget will try to locate the topmost image in its tree.'''
    image = ObjectProperty()

    '''The widget's aspect ratio. If not defined, image's ratio will be used.'''
    aspect_ratio = NumericProperty(0.)

    # ------------------------------------------------------ ROTATION INTERFACE
    '''Angle of Rotation.'''
    angle = NumericProperty(0)

    def get_origin(self):
        return self.pivot

    def set_origin(self, point):
        pivot = to_rotated(point, self.origin, -self.radiangle,
                           atan2, sin, cos)
        self.pivot_bond = ((pivot[0] - self.x) / float(self.width),
                           (pivot[1] - self.y) / float(self.height))
        self.pos = (self.x - (pivot[0] - point[0]),
                    self.y - (pivot[1] - point[1]))

    '''Sets the point of rotation. Default value is the widget's center.'''
    origin = AliasProperty(get_origin, set_origin)

    # ----------------------------------------------------- COLLISION INTERFACE
    '''Custom bounds' definition interface. (See module's documentation).'''
    custom_bounds = ObjectProperty([[(0, 0), (1, 0), (1, 1), (0, 1)]])

    '''If a polygon's index is in this list, the polygon becomes 'invisible'
    to the collision checks of others.'''
    hidden_bounds = ListProperty()

    '''Collision detection method switch (see documentation above).'''
    segment_mode = BooleanProperty(True)

    '''(segment_mode only) If a polygon's index is in this list, the segment
    between the last and first points of the polygon is not considered in the
    collision checks.'''
    open_bounds = ListProperty()

    '''Enables widget's advanced collision detection. If False, widget will
    collide as a normal (non-Rotabox) widget.'''
    allow_rotabox = BooleanProperty(True)

    # --------------------------------------------------------- TOUCH INTERFACE
    '''Allow touch translation on the X axis.'''
    allow_drag_x = BooleanProperty(False)

    '''Allow touch translation on the Y axis.'''
    allow_drag_y = BooleanProperty(False)

    def get_allow_drag(self):
        return self.allow_drag_x, self.allow_drag_y

    def set_allow_drag(self, value):
        if type(value) in (list, tuple):
            self.allow_drag_x, self.allow_drag_y = value
        else:
            self.allow_drag_x = self.allow_drag_y = bool(value)

    '''Allow touch translation on the X or Y axis.'''
    allow_drag = AliasProperty(get_allow_drag, set_allow_drag,
                               bind=('allow_drag_x', 'allow_drag_y'))

    '''Allow rotation around [origin]..'''
    single_touch_rotation = BooleanProperty(False)

    '''Allow scaling around [origin].'''
    single_touch_scaling = BooleanProperty(False)

    '''Allow multitouch rotation. [origin] is defined each time by the touch.'''
    multi_touch_rotation = BooleanProperty(False)

    '''Allow multitouch scaling. [origin] is defined each time by the touch.'''
    multi_touch_scaling = BooleanProperty(False)

    '''How many touches will be treated as one single drag touch.'''
    single_drag_touch = BoundedNumericProperty(1, min=1)

    '''How many touches will be treated as one single rotation/scaling touch.'''
    single_trans_touch = BoundedNumericProperty(1, min=1)

    '''If touched, the widget will be pushed to the top of parent widget tree.'''
    touched_to_front = BooleanProperty(False)

    '''If True, limiting the touch inside the bounds will be done after
    dispaching the touch to the child and grandchildren, so even outside the
    bounds they can still be touched.
    IMPORTANT NOTE: Grandchildren, inside or outside the bounds, can collide
        independently ONLY if widget is NOT ROTATED ([angle] must be 0).'''
    collide_after_children = BooleanProperty(False)

    # ------------------------------------------------------- UTILITY INTERFACE
    '''Access a point's current position, based on [custom_bounds] structure.'''
    def get_point(self, pol_index, point_index):
        if self.segment_mode:
            pindex = self.records[self.curr_key][
                'sides_index'][pol_index][point_index]
            return self.groups[pindex[0]].points[pindex[1]]
        else:
            return self.groups[pol_index].points[point_index]

    def get_scale(self):
        return float(self.width) / self.original_size[0]

    def set_scale(self, scale):
        if scale < self.scale_min:
            scale = self.scale_min
        elif scale > self.scale_max:
            scale = self.scale_max

        pivot = self.pivot[:]
        self.size = (scale * self.original_size[0],
                     scale * self.original_size[1])
        self.pivot = pivot
        if self.initial_scale:
            return
        self.initial_scale = self.scale

    '''Widget's current scale. Calculated from [original_size] (user's input
    [size] or [image]'s [texture_size]). Used for touch scaling but it can be an
    alternative to [size].'''
    scale = AliasProperty(get_scale, set_scale, bind=('width', 'height',
                                                      'original_size'))
    '''Minimum scale allowed.'''
    scale_min = NumericProperty(0.01)

    '''Maximum scale allowed.'''
    scale_max = NumericProperty(1e20)

    def get_pivot_x(self):
        return self.x + self.width * self.pivot_bond[0]

    def set_pivot_x(self, value):
        if self.width > 1:
            self.x = value - self.width * self.pivot_bond[0]
        elif value > 1:
                self.temp_piv_x = value
    pivot_x = AliasProperty(get_pivot_x, set_pivot_x,
                            bind=('x', 'width', 'pivot_bond'))

    def get_pivot_y(self):
        return self.y + self.height * self.pivot_bond[1]

    def set_pivot_y(self, value):
        if self.height > 1:
            self.y = value - self.height * self.pivot_bond[1]
        elif value > 1:
                self.temp_piv_y = value
    pivot_y = AliasProperty(get_pivot_y, set_pivot_y,
                            bind=('y', 'height', 'pivot_bond'))

    '''Point of rotation and scaling.
    While [origin] property sets [pivot] to any arbitrary position, [pivot]
    itself can be used to position the widget, much like [pos] or [center].'''
    pivot = ReferenceListProperty(pivot_x, pivot_y)

    '''Signifies the completion of the widget's initial preparations.
    Also, its state changes to True after every size change or reset.'''
    ready = BooleanProperty(False)

    '''Its state change signifies a reset. The reset completion signal, however,
    is the consequent [ready] state change to True.'''
    prepared = BooleanProperty(False)

    '''Enables bounds visualization (for testing).'''
    draw_bounds = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.size = [1, 1]
        self.temp_piv_x = self.temp_piv_y = 0
        self.initial_scale = 0
        self.touches = []
        self.last_touch_pos = {}
        self.trigger_update = Clock.create_trigger(self.update, -1)
        super(Rotabox, self).__init__(**kwargs)
        self.sized_by_img = False
        self.ratio = 1
        self.child = None
        self.draw_color = Color(0.29, 0.518, 1, 1)
        self.paint_color = Color(.7, .3, 0, 1)
        self.last_pos = [0, 0]
        self.last_size = self.size[:]
        self.radiangle = 0.
        self.frames = {}
        self.groups = ()  # polygons if point mode - sides if segment mode
        self.bbox = ()
        self.visible_bbox = ()
        self.visible_points = []  # Point mode
        self.visible_sides = ()  # Segment mode
        self.last_side = 0  # Segment mode
        self.curr_key = '00'  # Segment mode
        self.records = {}  # An index for segment mode to keep track of the
                         # different polygons' ranges in [groups] (sides).
        self.draw_lines = ()
        self.draw_hiddlines = ()
        self.box_lines = ()
        self.rotation = Rotate(angle=0, origin=self.center)
        self.canvas.before.add(PushMatrix())
        self.canvas.before.add(self.rotation)
        self.canvas.after.add(PopMatrix())
        self.bind(children=self.trigger_update,
                  parent=self.trigger_update,
                  pos=self.trigger_update,
                  pos_hint=self.trigger_update,
                  angle=self.trigger_update,
                  image=self.on_reset,
                  aspect_ratio=self.on_reset,
                  custom_bounds=self.on_reset,
                  hidden_bounds=self.on_reset,
                  allow_rotabox=self.on_reset)

    def add_widget(self, widget, **kwargs):
        '''Birth control.'''
        if self.children:
            raise Exception('Rotabox can only have one child.')
        super(Rotabox, self).add_widget(widget)
        self.child = self.children[0]

    def on_size(self, *args):
        '''Enables the ON SIZE section of the [update] method.'''
        self.ready = False
        self.trigger_update()

    def on_reset(self, *args):
        '''Enables bounds reset.'''
        self.prepared = False
        self.ready = False
        self.trigger_update()

    def prepare(self):
        '''Initial preparations.'''
        scale = self.initial_scale
        if not self.image:
            # Trying to auto-assign [image] property if not specified.
            self.image = locate_images(self)
        if self.image:
            try:
                self.image.texture.mag_filter = 'nearest'
            except AttributeError:
                pass
            self.image.allow_stretch = True
            # In case of a stationary widget with animated bounds.
            self.image.bind(source=self.trigger_update)

            # Calculating widget's size from available inputs.
            if (not (self.width - scale > 1 or self.height - scale > 1)
                    or self.sized_by_img):
                try:
                    self.original_size = self.image.texture.size
                except AttributeError:  # If animation, texture not ready (?)
                    self.original_size = self.image.size

                if not scale:
                    scale = 1
                self.size = [self.original_size[0] * scale,
                             self.original_size[1] * scale]
                if self.sized_by_img:
                    dw = self.width - self.last_size[0]
                    dh = self.height - self.last_size[1]
                    self.pivot = (self.pivot_x - dw * .5,
                                  self.pivot_y - dh * .5)
                self.sized_by_img = True
            else:
                self.original_size = self.size[:]
                if scale:
                    self.size = [self.size[0] * scale,
                                 self.size[1] * scale]
        else:
            self.original_size = self.size[:]
            if not scale:
                scale = 1
            self.size = [self.size[0] * scale,
                         self.size[1] * scale]

        # Setting the widget's ratio.
        if not self.aspect_ratio:
            if self.image and self.sized_by_img:
                self.ratio = self.image.image_ratio
            else:
                self.ratio = self.width / float(self.height)
        else:
            self.ratio = self.aspect_ratio

        # If [size] is not specified explicitly by the user, any input values
        # for [pivot] are withheld in [temp_piv_x] and [temp_piv_y], until
        # [size] gets its values from [image]. Then, [pivot] gets the withheld
        # values, here.
        if self.temp_piv_x or self.temp_piv_y:
            self.pivot = self.temp_piv_x, self.temp_piv_y
            self.temp_piv_x = self.temp_piv_y = 0

        if self.allow_rotabox:
            # Building widget's bounds.
            if self.segment_mode:
                self.define_sides()
            else:
                self.define_polygons()

            # Setting canvas in case of test drawing
            if self.draw_bounds:
                self.set_draw()

        self.trigger_update()

    def update_size(self):
        '''Size, scale and ratio handling.'''
        width, height = self.size
        if round(self.ratio, 3) != round(width / float(height), 3):
            # Adjusting size to fit ratio
            last_size = self.last_size
            if abs(width - last_size[0]) > abs(height - last_size[1]):
                self.size = width, float(width) / self.ratio
            else:
                self.size = height * self.ratio, height
            if last_size != [1, 1]:
                dw = self.width - last_size[0]
                dh = self.height - last_size[1]
                # Moving widget to keep pivot's position the same, to originate
                # the resizing from pivot.
                self.pivot = (self.pivot_x - dw * .5, self.pivot_y - dh * .5)

        if self.allow_rotabox:
            # Scaling widget's bounds
            if self.frames:
                for frame in self.frames.itervalues():
                    scale_bounds(self.size, frame)
            else:
                scale_bounds(self.size, self.groups)

            self.update_bounds(self.groups, True, self.radiangle, self.pos)

        if self.children:
            # Adjusting the child's size to fit widget's
            self.child.size = self.size

        self.last_size = self.size[:]
        self.trigger_update()

    def update(self, *args):
        '''Updates the widget's angle, point of rotation, bounds and child's
        position.
        Also runs the [update_size] method on size change and the [prepare] method
        initially and on reset.
        '''
        self.angle %= 360
        angle = self.angle
        if angle:
            # Updating the rotation instruction, in canvas.before.
            self.rotation.origin = self.origin
            self.rotation.angle = angle

        pos = self.pos
        motion = (abs(pos[0] - self.last_pos[0]) > .1
                  or abs(pos[1] - self.last_pos[1]) > .1)
        if motion:
            # Updating the child's position
            if self.children:
                self.child.pos = pos
            self.last_pos = pos[:]

        if self.allow_rotabox:
            # Updating custom bounds
            if self.frames:
                if self.segment_mode:
                    # An identically keyed atlas file is assumed here.
                    curr_key = self.image.source.split('/')[-1]
                    self.groups = self.frames[curr_key]
                    self.curr_key = curr_key
                else:
                    # An identically keyed atlas file is assumed here.
                    self.groups = self.frames[self.image.source.split('/')[-1]]
                motion = True
            if angle or motion:
                self.radiangle = radians(angle)
                self.update_bounds(self.groups, motion, self.radiangle, pos)
            if self.draw_bounds:
                self.draw()

        if self.ready:
            return
        # -------------------------- ON SIZE
        if self.prepared:
            self.update_size()
            self.ready = True
            return
        # ------------------------- ON RESET & INITIALLY
        self.prepare()
        self.prepared = True

    def set_draw(self):
        self.canvas.after.add(self.draw_color)
        if self.frames:
            pols = max(
                [len(frame) for frame in self.custom_bounds.itervalues()])
            if self.segment_mode:
                sides = max(
                    [len(pol) for frame in self.custom_bounds.itervalues() for
                     pol in frame])
        else:
            pols = len(self.custom_bounds)
            if self.segment_mode:
                sides = len(self.groups)
        if self.segment_mode:
            if self.open_bounds:
                self.draw_lines += tuple(
                    Line(close=True, dash_offset=3, dash_length=5) for _ in
                    xrange(sides))
            else:
                self.draw_lines += tuple(
                    Line(dash_offset=3, dash_length=5) for _ in xrange(pols))

            if self.hidden_bounds:
                self.draw_hiddlines += tuple(
                    Line(close=True, dash_offset=3, dash_length=1) for _ in
                    xrange(sides))
            self.box_lines += tuple(
                Line(close=True, dash_offset=3, dash_length=5) for _ in
                xrange(sides))
        else:
            self.draw_lines += tuple(
                Line(close=True, dash_offset=3, dash_length=5) for _ in
                xrange(pols))
            self.box_lines += tuple(
                Line(close=True, dash_offset=3, dash_length=5) for _ in
                xrange(pols))
        for line in self.draw_lines:
            self.canvas.after.add(line)
        for hline in self.draw_hiddlines:
            self.canvas.after.add(hline)
        for line in self.box_lines:
            self.canvas.after.add(line)

        # Securing draw on a stationary widget.
        self.x += .001

    def draw(self):
        '''
        If [draw_bounds] is True, visualises the widget's bounds.
        For testing.
        '''
        try:
            if self.segment_mode:
                if self.open_bounds:
                    for i, side in enumerate(self.groups):
                        if side.id[0] not in self.hidden_bounds:
                            self.draw_lines[i].points = [n for point
                                                         in side.points
                                                         for n in point]
                        else:
                            self.draw_hiddlines[i].points = [n for point
                                                             in side.points
                                                             for n in point]
                else:
                    pols_lens = self.records[self.curr_key]['pols_lens']
                    length = 0
                    for i, leng in enumerate(pols_lens):
                        if i not in self.hidden_bounds:
                            self.draw_lines[i].points = [n
                                                         for j in xrange(length,
                                                                         length
                                                                         + leng)
                                                         for point
                                                         in self.groups[j].points
                                                         for n in point]
                        else:
                            self.draw_hiddlines[i].points = [n
                                                     for j in xrange(length,
                                                                     length
                                                                     + leng)
                                                     for point
                                                     in self.groups[j].points
                                                     for n in point]
                        length += leng

                # for i in xrange(len(self.groups)):
                #     box = self.groups[i].bbox
                #     self.box_lines[i].points = [box[0], box[1],
                #                                 box[2], box[1],
                #                                 box[2], box[3],
                #                                 box[0], box[3]]
            else:
                for i in xrange(len(self.groups)):
                    self.draw_lines[i].points = [n for point
                                                 in self.groups[i].points
                                                 for n in point]
                    # box = self.polygons[i].bbox
                    # self.box_lines[i].points = [box[0], box[1],
                    #                             box[2], box[1],
                    #                             box[2], box[3],
                    #                             box[0], box[3]]
            # box = self.bbox
            # self.box_lines[0].points = (box[0], box[1],
            #                         box[2], box[1],
            #                         box[2], box[3],
            #                         box[0], box[3])
        except (IndexError, KeyError):
            pass

    # ------------------------------------------------------ BOUNDS & COLLISION
    def define_sides(self):
        '''Organising the data from the user's [self.custom_bounds] hints
        for 'segment intersection' detection method.
        '''
        if isinstance(self.custom_bounds, dict):   # Animation case
            for key, frame in self.custom_bounds.iteritems():
                sides, sindices = make_sides(frame, self.open_bounds)
                scale_bounds(self.size, sides)
                self.frames[key] = sides
                l = 0
                pollens = []
                pindices = []
                polends = []

                for i, pol in enumerate(frame):
                    if i not in self.open_bounds:
                        pollens.append(len(pol))
                        l += len(pol)
                    else:
                        pollens.append(len(pol) - 1)
                        l += len(pol) - 1
                    pindices.append(l)
                    polends.append(l)
                self.records[key] = {'pols_lens': pollens,
                                     'pols_index': pindices,
                                     'pols_ends': polends,
                                     'sides_index': sindices}
        if isinstance(self.custom_bounds, list):  # Single image case
            sides, sindices = make_sides(self.custom_bounds,
                                         self.open_bounds)
            scale_bounds(self.size, sides)
            self.groups = sides
            l = 0
            pollens = []
            pindices = []
            polends = []

            for i, pol in enumerate(self.custom_bounds):
                if i not in self.open_bounds:
                    pollens.append(len(pol))
                    l += len(pol)
                else:
                    pollens.append(len(pol) - 1)
                    l += len(pol) - 1
                pindices.append(l)
                polends.append(l)
            self.records[self.curr_key] = {'pols_lens': pollens,
                                           'pols_index': pindices,
                                           'pols_ends': polends,
                                           'sides_index': sindices}

        self.update_bounds(self.groups, True, self.radiangle, self.pos)

    def define_polygons(self):
        '''Organising the data from the user's [self.custom_bounds] hints
        for 'point in polygon' detection method.
        '''
        if isinstance(self.custom_bounds, dict):  # Animation case
            for key, frame in self.custom_bounds.iteritems():
                polygons = make_polygons(frame)
                scale_bounds(self.size, polygons)
                self.frames[key] = polygons
        if isinstance(self.custom_bounds, list):  # Single image case
            polygons = make_polygons(self.custom_bounds)
            scale_bounds(self.size, polygons)
            self.groups = polygons

        self.update_bounds(self.groups, True, self.radiangle, self.pos)

    def update_bounds(self, groups, motion, angle, pos):
        '''Updating the elements of the collision detection checks:
        The detectors ([groups]) & the outgoing data ([visible_bbox], etc.).
        '''
        if self.segment_mode:
            bboxes = ()
            # Trying to avoid calculating each point twice (each point being a
            # member of two sides), by passing the previous endpoint, to serve
            # as the next startpoint.
            motbpoint = ()
            rotbpoint = ()
            for s, side in enumerate(groups):
                if s in self.records[self.curr_key]['pols_index']:
                    # Resetting to calculate the first point of each polygon.
                    motbpoint = ()
                    rotbpoint = ()
                if motion:
                    motbpoint = move_sides(side, pos, motbpoint)
                if angle:
                    rotbpoint = rotate_sides(self.origin, angle, side, rotbpoint)
                side.bbox = calculate_bbox(points=side.points)
                bboxes += (side.bbox,)

            self.bbox = calculate_bbox(bboxes=bboxes)

            if not self.hidden_bounds:
                self.visible_sides = groups
                self.visible_bbox = self.bbox
                return

            plains = [side for side in groups
                      if side.id[0] not in self.hidden_bounds]
            self.visible_sides = plains
            self.visible_bbox = calculate_bbox(bboxes=[side.bbox
                                                       for side in plains])
        else:
            points = []
            bboxes = ()
            for pol in groups:
                if motion:
                    move_polygons(angle, pol, pos)
                if angle:
                    rotate_polygons(self.origin, angle, pol)
                pol.bbox = calculate_bbox(points=pol.points)
                bboxes += (pol.bbox,)
                points += pol.points

            self.bbox = calculate_bbox(bboxes=bboxes)

            if not self.hidden_bounds:
                self.visible_points = points
                self.visible_bbox = self.bbox
                return

            plain_pols = [pol for p, pol in enumerate(groups)
                          if p not in self.hidden_bounds]
            self.visible_points = [point for pol in plain_pols
                                   for point in pol.points]
            self.visible_bbox = calculate_bbox(bboxes=[pol.bbox
                                                       for pol in plain_pols])

    def collide_point(self, x=0, y=0):
        '''"Oddeven" point-in-polygon method:
        Checking the membership of touch point by assuming a ray at 0 angle
        from that point to infinity (through window right) and counting the
        number of polygon sides that this ray crosses. If this number is odd,
        the point is inside; if it's even, the point is outside.
        '''
        if self.allow_rotabox:
            if self.segment_mode:
                prevrang = 0
                for r, rang in enumerate(
                        self.records[self.curr_key]['pols_ends']):
                    if r in self.open_bounds:
                        continue
                    c = False
                    for i in xrange(prevrang, rang):
                        ax, ay = self.groups[i].points[0]
                        bx, by = self.groups[i].points[1]
                        if (((by > y) != (ay > y)) and
                                x < (ax - bx) * (y - by) / (ay - by) + bx):
                            c = not c
                    if c:
                        return c
                    prevrang = rang
                return False
            else:
                for pol in self.groups:
                    points = pol.points
                    ppl = len(points)
                    j = ppl - 1
                    c = False
                    for i in xrange(ppl):
                        x1, y1 = points[j]
                        x2, y2 = points[i]
                        if (((y2 > y) != (y1 > y)) and
                                x < (x1 - x2) * (y - y2) / (y1 - y2) + x2):
                            c = not c
                        j = i
                    if c:
                        return c
                return False
        else:
            return super(Rotabox, self).collide_point(x, y)

    def collide_widget(self, wid):
        '''Axis-aligned bounding box testing, before widget is sent to
        [collide_more] for more checks.
        '''
        if self.bbox:
            this_box = self.bbox
        else:
            return super(Rotabox, self).collide_widget(wid)
        try:  # Assuming the other widget is a Rotabox, too.
            that_box = wid.visible_bbox
            that_box[0]  # Optimization (trying to avoid 'if that_box:')
        except (AttributeError, IndexError):  # and if not..
            if self.segment_mode:
                that_box = wid.x, wid.y, wid.right, wid.top
            else:
                return super(Rotabox, self).collide_widget(wid)

        # Axis-aligned bounding boxes test. Similar to Widget's.
        if this_box[2] < that_box[0]:
            return False
        if this_box[0] > that_box[2]:
            return False
        if this_box[3] < that_box[1]:
            return False
        if this_box[1] > that_box[3]:
            return False

        if self.segment_mode:
            try:
                those_sides = wid.visible_sides
            except AttributeError:  # If wid is not a Rotabox..
                those_sides = (((wid.x, wid.top), (wid.x, wid.y)),
                               ((wid.x, wid.y), (wid.right, wid.y)),
                               ((wid.right, wid.y), (wid.right, wid.top)),
                               ((wid.right, wid.top), (wid.x, wid.top)))
            try:
                those_sides[0]
            except IndexError:  # If wid uses the other method..
                for pol in wid.groups:
                    pts = pol.points
                    l = len(pts)
                    those_sides += tuple(tuple([pts[i], pts[(i + 1) % l]])
                                         for i in xrange(l))

            coll = collide_sides(self.groups, that_box, those_sides,
                                 self.last_side)
            if coll:
                # Keeping and passing back the last collided side, to start the
                # checks with (optimization).
                self.last_side = (coll[2]
                                  if coll[0][0] not in self.hidden_bounds
                                  else 0)
                coll.pop()
            return coll
        else:
            return collide_polygons(self.groups, wid)

    # ----------------------------------- TOUCH HANDLING (altered Scatter code)
    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not self.collide_after_children:
            if not self.collide_point(x, y):
                # return super(Rotabox, self).on_touch_down(touch)
                return False

        # let the child widgets handle the event if they want
        if super(Rotabox, self).on_touch_down(touch):
            # ensure children don't have to do it themselves
            if 'multitouch_sim' in touch.profile:
                touch.multitouch_sim = True
            self.bring_to_front(touch)
            return True

        # if we don't have any active
        # interaction control, then don't accept the touch.
        if not (self.allow_drag_x
                or self.allow_drag_y
                or self.multi_touch_rotation
                or self.multi_touch_scaling
                or self.single_touch_rotation
                or self.single_touch_scaling):
            return False

        if self.collide_after_children:
            if not self.collide_point(x, y):
                return False

        if 'multitouch_sim' in touch.profile:
            touch.multitouch_sim = True

        # grab the touch so we get all it later move events for sure
        self.bring_to_front(touch)
        touch.grab(self)
        self.touches.append(touch)
        self.last_touch_pos[touch] = x, y

        return True

    def bring_to_front(self, touch):
        '''Auto bring to front.'''
        if self.touched_to_front and self.parent:
            parent = self.parent
            if parent.children[0] is self:
                return
            parent.remove_widget(self)
            parent.add_widget(self)
            self.dispatch('on_touched_to_front', touch)

    def on_touch_move(self, touch):
        x, y = touch.x, touch.y

        # let the child widgets handle the event if they want
        if self.collide_point(x, y) and not touch.grab_current == self:
            if super(Rotabox, self).on_touch_move(touch):
                return True

        # rotate/scale/translate
        if touch in self.touches and touch.grab_current == self:
            if self.transform_with_touch(touch):
                self.dispatch('on_transform_with_touch', touch)
            self.last_touch_pos[touch] = x, y

        if self.collide_point(x, y):
            return True

    def transform_with_touch(self, touch):
        changed = False

        # drag
        touches = len(self.touches)
        if (touches == self.single_drag_touch
                and (self.allow_drag_x or self.allow_drag_y)):
            dx = (touch.x - self.last_touch_pos[touch][0]) * self.allow_drag_x
            dy = (touch.y - self.last_touch_pos[touch][1]) * self.allow_drag_y
            dx = float(dx) / self.single_drag_touch
            dy = float(dy) / self.single_drag_touch
            self.x += dx
            self.y += dy
            changed = True

        # single touch rotation / scaling
        if (touches == self.single_trans_touch
                and (self.single_touch_rotation or self.single_touch_scaling)):
            anchor = self.pivot
            old_line = Vector(*touch.ppos) - anchor
            new_line = Vector(*touch.pos) - anchor
            if not old_line.length():   # div by zero
                return changed
            if self.single_touch_rotation:
                angle = new_line.angle(old_line)
                self.angle += angle
            if self.single_touch_scaling:
                scale = new_line.length() / old_line.length()
                self.scale *= scale
            changed = True

        if touches == 1:
            return changed

        # we have more than one touch... list of last known pos
        points = [Vector(self.last_touch_pos[t]) for t in self.touches
                  if t is not touch]
        # add current touch last
        points.append(Vector(touch.pos))

        # we only want to transform if the touch is part of the two touches
        # farthest apart! So first we find anchor, the point to transform
        # around as another touch farthest away from current touch's pos
        anchor = max(points[:-1], key=lambda p: p.distance(touch.pos))

        # setting rotation origin to the anchor, if permitted
        self.origin = anchor
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

        angle = new_line.angle(old_line) * self.multi_touch_rotation
        self.angle += angle

        if self.multi_touch_scaling:
            scale = new_line.length() / old_line.length()
            self.scale *= scale
            changed = True
        return changed

    def on_touch_up(self, touch):
        # if the touch isnt on the widget we do nothing, just try children
        if not touch.grab_current == self:
            if super(Rotabox, self).on_touch_up(touch):
                return True

        # remove it from our saved touches
        if touch in self.touches and touch.grab_state:
            touch.ungrab(self)
            del self.last_touch_pos[touch]
            self.touches.remove(touch)

        # stop propagating if its within our bounds
        if self.collide_point(*touch.pos):
            return True

    def on_transform_with_touch(self, touch):
        '''
        Called when a touch event has transformed the widget.
        By default this does nothing, but can be overriden by derived
        classes that need to react to transformations caused by user
        input.

        :Parameters:
            `touch`: the touch object which triggered the transformation.
        '''
        pass

    def on_touched_to_front(self, touch):
        '''
        Called when a touch event causes the widget to be brought to the
        front of the parent (only if :attr:`touched_to_front` is True)

        :Parameters:
            `touch`: the touch object which brought the widget to front.
        '''
        pass

    # --------------------------------------------------------------- UTILITIES
    def get_size_hint_x(self):
        return None
    def set_size_hint_x(self, value):
        raise Exception("Rotabox can't use size_hint.")
    size_hint_x = AliasProperty(get_size_hint_x, set_size_hint_x)
    def get_size_hint_y(self):
        return None
    def set_size_hint_y(self, value):
        raise Exception("Rotabox can't use size_hint.")
    size_hint_y = AliasProperty(get_size_hint_y, set_size_hint_y)
    # Locking size_hint property to None, None,
    # in order to keep intended aspect ratio (critical for custom_bounds).
    size_hint = ReferenceListProperty(size_hint_x, size_hint_y)

    # Used for calculating the widget's scale. It's the user's input size
    # or the [texture_size] of the widget's [image].
    original_size = ListProperty([1, 1])

    # A fractional value that keeps [pivot] relative to the widget's size
    # and position. [origin] sets and changes it.
    pivot_bond = ListProperty([.5, .5])


# -------------------------------- SEGMENT INTERSECTION DETECTION
def make_sides(frame, opens=None):
    '''
    Constructing side objects to organize, keep and update
    the bounds' points' data.
    '''
    sides = ()
    pairs = [(p, i, pol[i], pol[(i + 1) % len(pol)
                                if p not in opens
                                else i + 1
                                if i + 1 < len(pol)
                                else i])
             for p, pol in enumerate(frame)
             for i in xrange(len(pol))]
    pl = len(pairs)

    sindices = [[] for _ in xrange(len(frame))]
    sindex = []
    for k in xrange(pl):
        if pairs[k][2] != pairs[k][3]:
            side = Group()
            side.id = pairs[k][0], pairs[k][1]
            side.hints = pairs[k][2], pairs[k][3]
            sides += (side,)
            sindex.append((sides.index(side), 0))
        else:
            sindex.append((sindex[-1][0], 1))
        if not k + 1 < pl or pairs[k + 1][0] != pairs[k][0]:
            sindices[pairs[k][0]] += sindex[:]
            del sindex[:]

    return sides, sindices


def move_sides(side, pos, apoint):
    '''Translating sides by updating their [rel_pts] list.'''
    if apoint:
        side.points = side.rel_pts = apoint, (side.ref_pts[1][0] + pos[0],
                                              side.ref_pts[1][1] + pos[1])
    else:
        side.points = side.rel_pts = tuple(tuple(x + y
                                           for x, y in izip(point, pos))
                                           for point in side.ref_pts)
    return side.rel_pts[1]


def rotate_sides(origin, angle, side, apoint):
    '''Rotating sides by updating their [points] list.'''
    # Optimizations
    at = atan2
    si = sin
    co = cos
    if apoint:
        side.points = apoint, to_rotated(side.rel_pts[1],
                                         origin, angle, at, si, co)
    else:
        side.points = tuple(to_rotated(point, origin, angle, at, si, co)
                            for point in side.rel_pts)
    return side.points[1]


def collide_sides(sides, that_box, those_sides, last):
    '''Segment intersection detection method.'''
    ls = len(sides)
    for i in xrange(ls):
        i = (i + last) % ls
        side = sides[i]
        # Preliminary 1: side's bbox vs widget's bbox.
        box = side.bbox
        if box[2] < that_box[0]:
            continue
        if box[0] > that_box[2]:
            continue
        if box[3] < that_box[1]:
            continue
        if box[1] > that_box[3]:
            continue

        v1, v2 = side.points
        for a_side in those_sides:
            try:
                # Preliminary 2: side's bbox vs widget's side's bbox.
                a_box = a_side.bbox
                if box[2] < a_box[0]:
                    continue
                if box[0] > a_box[2]:
                    continue
                if box[3] < a_box[1]:
                    continue
                if box[1] > a_box[3]:
                    continue
                v3, v4 = a_side.points
            except AttributeError:  # If the other not in segment mode.
                v3, v4 = a_side[0], a_side[1]
            # Main check:
            # If the vertices v1 and v2 are not on opposite sides of the segment
            # v3, v4, or the vertices v3 and v4 are not on opposite sides of
            # the segment v1, v2, there's no intersection.
            if (((v4[0] - v3[0]) * (v1[1] - v3[1]) - (v1[0] - v3[0]) * (
                v4[1] - v3[1]) > 0)
                    == ((v4[0] - v3[0]) * (v2[1] - v3[1]) - (v2[0] - v3[0]) * (
                    v4[1] - v3[1]) > 0)):
                continue
            elif (((v2[0] - v1[0]) * (v3[1] - v1[1]) - (v3[0] - v1[0]) * (
                v2[1] - v1[1]) > 0)
                    == ((v2[0] - v1[0]) * (v4[1] - v1[1]) - (v4[0] - v1[0]) * (
                    v2[1] - v1[1]) > 0)):
                continue
            try:
                return [side.id, a_side.id, i]
            except AttributeError:  # If the other not in segment mode.
                return [side.id, those_sides.index(a_side), i]
    return False


# ------------------------------------ POINT IN POLYGON DETECTION
def make_polygons(frame):
    '''
    Constructing polygon objects to organize, keep and update
    the bounds' points' data.
    '''
    polygons = ()
    for i in xrange(len(frame)):
        pol = Group()
        pol.hints = frame[i]
        polygons += (pol,)
    return polygons


def move_polygons(angle, pol, pos):
    '''Translating polygons by updating their [rel_pts] list.'''
    pol.points = pol.rel_pts = [[x + y for x, y in izip(point, pos)]
                   for point in pol.ref_pts]


def rotate_polygons(origin, angle, pol):
    '''Rotating polygons by updating their [points] list.'''
    # Optimizations
    at = atan2
    si = sin
    co = cos
    pol.points = [to_rotated(point, origin, angle, at, si, co)
                  for point in pol.rel_pts]


def collide_polygons(polygons, alien):
    ''''Point in polygon' collision detection method.'''
    that_box = alien.visible_bbox
    those_points = alien.visible_points

    for pol in polygons:
        # Preliminary 1: pol's bbox vs widget's bbox.
        box = pol.bbox
        if box[2] < that_box[0]:
            continue
        if box[0] > that_box[2]:
            continue
        if box[3] < that_box[1]:
            continue
        if box[1] > that_box[3]:
            continue

        # Preliminary 2: pol's bbox vs widget's points to filter out.
        aliens = [point for point in those_points if
                  box[0] <= point[0] <= box[2] and
                  box[1] <= point[1] <= box[3]]
        if not aliens:
            continue

        points = pol.points
        ppl = len(points)
        # Main check ('oddeven' point-in-polygon method):
        # Checking the membership of each point by assuming a ray at 0 angle
        # from that point to infinity (through window right) and counting the
        # number of polygon sides that this ray crosses. If this number is odd,
        # the point is inside; if it's even, the point is outside.
        for x, y in aliens:
            j = ppl - 1
            c = False
            for i in xrange(ppl):
                x1, y1 = points[j]
                x2, y2 = points[i]
                if (((y2 > y) != (y1 > y))
                        and x < (x1 - x2) * (y - y2) / (y1 - y2) + x2):
                    c = not c
                j = i
            if c:
                return polygons.index(pol),
    return False


# ------------------------------------ UTILITIES
class Group(object):
    '''An object to keep each polygon's or side's data.'''
    __slots__ = 'id', 'hints', 'ref_pts', 'rel_pts', 'points', 'bbox'

    def __init__(self):
        self.id = ()  # Side's container polygon's original index, side's index
                      # in said polygon (segment collision mode).
        self.hints = ()  # User's relative points.
        self.ref_pts = ()  # Translated points due to sizing before any motion.
        self.rel_pts = []  # Translated points due to motion before rotation.
        self.points = []  # Translated points due to rotation. Final points,
                          # used for the collision tests.
        self.bbox = ()  # Polygon's or side's axis-aligned bounding box.


def scale_bounds(size, groups):
    '''Scaling polygons or sides by updating their [ref_pts] list.'''
    for obj in groups:
        obj.points = obj.rel_pts = obj.ref_pts = tuple(
            tuple(x * y for x, y in izip(point, size))
            for point in obj.hints)


def to_rotated(point, orig, angle, arctan, sine, cosine):
    '''Translating a point acccording to widget's rotation.'''
    dx = point[0] - orig[0]
    dy = point[1] - orig[1]
    distance = (dx * dx + dy * dy) ** .5
    angle = (angle + arctan(dy, dx)) % 6.283  # 2pi

    return (orig[0] + distance * cosine(angle),
            orig[1] + distance * sine(angle))


def calculate_bbox(points=None, bboxes=None):
    '''An axis-aligned bounding box, calculated from points or bboxes.'''
    if points:
        left, bottom = map(min, *points)
        right, top = map(max, *points)
        return left, bottom, right, top
    if bboxes:
        if len(bboxes) > 1:
            left, bottom, _, _ = map(min, *bboxes)
            _, _, right, top = map(max, *bboxes)
            return left, bottom, right, top
        else:
            return bboxes[0]
    return ()


def locate_images(root):
    '''
    Traversing the widget tree to find the first topmost Image to assign to
    [image] property.
    '''
    the_one = None

    def find_img(widget):
        for kid in widget.children:
            img = find_img(kid)
            if isinstance(kid, Image):
                return kid
            return img

    for child in root.children:
        the_one = find_img(child)
        if isinstance(child, Image):
            return child
    return the_one


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
'''THIS IS THE END OF THE ACTUAL MODULE. THE REST, IS JUST A USAGE EXAMPLE.'''
# vvvvvvvvvvvvvvvvvvvv (Run the module directly, to watch) vvvvvvvvvvvvvvvvvvv

if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.lang import Builder

    Builder.load_string('''
<Root>:
    blue: blue
    red: red
    Rotabox:
        id: blue
        pivot: 250, 300
        single_touch_scaling: True
        custom_bounds:
            [[(0.018, 0.335), (0.212, 0.042), (0.217, 0.408),
            (0.48, -0.004), (0.988, 0.758), (0.458, 0.665), (0.26, 0.988),
            (0.268, 0.585), (0.02, 0.977)]]
        Image:
            source: 'examples/kivy.png'
            color: .5, .5, 0, 1
    Rotabox:
        id: red
        pivot: 600, 300
        allow_drag: True
        multi_touch_scaling: True
        custom_bounds:
            [[(0.018, 0.335), (0.212, 0.042), (0.217, 0.408),
            (0.48, -0.004), (0.988, 0.758), (0.458, 0.665), (0.26, 0.988),
            (0.268, 0.585), (0.02, 0.977)]]
        Image:
            source: 'examples/kivy.png'
            color: .5, 0, .5, 1
     ''')

    class Root(Widget):
        def __init__(self, **kwargs):
            super(Root, self).__init__(**kwargs)
            Clock.schedule_interval(self.update, 0)

        def update(self, *args):
            this = self.blue
            that = self.red
            if this.collide_widget(that):
                that.x += 1
                this.x -= 1
            else:
                this.x += .5
                that.x -= .5
                this.angle += .5
                that.angle -= .6

    runTouchApp(Root())
