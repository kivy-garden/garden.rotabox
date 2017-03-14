'''

ROTABOX                                           kivy 1.9.0 - python 2.7.10
=======

Rotabox is a *kivy widget* with customizable 2D bounds that follow its rotation.
The users can shape their own, specific bounds, to fit an image (or a series of
images in an animation), using  a visual editor (See Rotaboxer below).

Rotabox also offers multitouch interactivity (drag, rotation and scaling).

____________
Basic Usage:

    To use Rotabox, just include *rotabox.py* in your project files.

        from rotabox import Rotabox

        rb = Rotabox()
        rb.image = Image(source='img.png')
        rb.add_widget(rb.image)
        rb.bounds = [[[(0.015, 0.981), (0.019, 0.342),
                       (0.212, 0.034), (0.21, 0.427),
                       (0.48, -0.001), (0.714, 0.342),
                       (0.985, 0.75), (0.462, 0.668),
                       (0.262, 0.978), (0.265, 0.599)],
                      [9, 1, 3, 7, 5]]]

    * Make a Rotabox instance.
    * Add an Image widget to the instance and assign it to the instance's
      [image] attribute.
    * Set the instance's [bounds]:
        * Define a polygon that covers the instance's area that needs to be
          collision-aware (e.g. its image's opaque area), as a list of point
          tuples (See API below).
        * Promote some of the polygon's vertices to checkpoints (See Concept
          below) and make a second list with their indices.
        * Put the two lists in another list for the polygon.
        * Repeat for additional polygons and put them all in yet another list
          and assign it to the instance's [bounds] attribute (See API below).

    Use [angle] and [origin] attributes for rotation.

________________
Rotabox Concept:

    To detect membership of a point in a polygon's area, Rotabox uses the
    polygon's sides in the following manner:
    Think of a polygon's vertex (e.g. C in the example) and its two adjacent
    sides (BC and CD) as a whole (a corner).
    If  the vertex is a checkpoint, the corner's legs become rays, extending to
    infinity.
    A corner like that, divides the whole plane into two regions.
    The checkpoint then keeps the region containing the polygon and discards
    the rest.
    The collidable area is what's left when all the checkpoints are done
    discarding.
    In the example below, three positions are examined for a possible collision
    with a rectangular polygon, with two checkpoints A and B.
                                                          .
                                                          .
                         A o------------------------------. . . . . . . . .
                           |                              |
                           |                              |
              (1)          |         (2)                  |
                           |                              |     (3)
                           |                              |
                           |                              |
         1. Colliding      |     2. Colliding             | 3. Colliding
       according to B      |   according to both!         | according to A
      (A's 'False' area)   | (Legitimate collision)       |(B's 'False' area)
        . . . . . . . . . .|------------------------------o
                           .                               B
                           .
                           .
    There's no need for the remaining two vertices of the above rectangle to be
    checkpoints, since their legs are already parts of A and C corners.

    NOTE: As a general rule, at least one of any two consecutive vertices should
    be a checkpoint, but they don't both have to be.

    In the above example it's just a matter of economy, but in certain cases
    there are vertices that can't be checkpoints.

    Consider the concave polygon below, to see the problem:
                                                  .
                                                  .
                        A ________________________.F
                         |                        |
                         |                        |
                         |                        |
                         |                        |
                    . . .|. . . . . . ____________|
                         |           |D            E
                         |           |
                         |           |
                         |           |
                         |           |
                         |___________|
                        B             C

    Vertices C and E cannot be checkpoints because one of each's legs is
    crossing the polygon. (e.g. E's horizontal leg excludes the lower part).
    So, starting with D and having to skip C and E, B and F must be checkpoints.
    A, could be a checkpoint too, but it's not required, since its legs are
    already parts of B and F.

    NOTE: For a vertex to qualify as a checkpoint, none of its adjacent sides
    should cross the polygon area if extended.

    More than one polygons can be defined for Rotabox bounds.
    So, a complex shape can always be broken into more simple ones.

____
API:
_____________
Restrictions:

    In order to be able to maintain any arbitrary aspect ratio
    (e.g. its image's ratio), Rotabox doesn't use the [size_hint] property.
    Of course, [size] property can always be used in a relative manner
    (e.g. self.width = self.parent.width * .5).
    Also, there's no need to specify a (None, None) value for the [size_hint]).

    Rotabox can only have one child. It can be an Image but not necessarily.

_______
Basics:

    [image] Image (None):
        Rotabox's only child will most likely be an Image.
        If so, it will be assigned to this attribute by default.
        Otherwise, the user can explicitly define an [image] somewhere in the
        widget's tree, that the custom bounds will use as a reference.
        One can also use an .atlas spritesheet as an animation source and define
        different bounds for each frame (See [bounds] below).

    [ratio] float (0.)
        If [image] is not defined, [ratio] (if provided) can be used to keep the
        bounds relevant to something else.

    [angle] NumericProperty (0):
        The angle of rotation.

    [origin] tuple (center):
        The point of rotation.

________________________________
Customizing the Collidable Area:

    [allow_custom_bounds] boolean (False):
        The user will have to enable Rotabox's ability to compensate for
        rotation and allow bounds modification.
        With [allow_custom_bounds] enabled, the default settings provide a
        colliding rectangle, the size of the widget, that follows its rotation.

    [bounds] ObjectProperty (list or dict) ([[[(0, 0), (1, 0), (1, 1), (0, 1)],
                                              [0, 2]]])
        This is how the custom bounds are being defined by the user.
        [bounds] can be a list of one or more polygons' data as seen in
        its default value, above. Here's another example with more polygons:

            self.bounds = [[[(0.013, 0.985), (0.022, 0.349),
                             (0.213, 0.028), (0.217, 0.681)],
                            [1, 3]],
                           [[(0.267, 0.346), (0.483, -0.005),
                             (0.691, 0.316), (0.261, 0.975)],
                            [0, 2]],
                           [[(0.539, 0.674), (0.73, 0.37),
                             (0.983, 0.758)],
                            [2, 0]]]

        It can also be a dictionary, in case of animated bounds (different
        bounds for different frames of an animation sequence in an .atlas file),
        where the keys correspond to the frame names in the .atlas file and each
        item is a list of one or more polygons' data like the above.
        Here's an example of such a dictionary:

            self.bounds = {'00': [[[(0.201, 0.803), (0.092, 0.491),
                                    (0.219, 0.184), (0.526, 0.064)],
                                   [1, 3]],
                                  [[(0.419, 0.095), (0.595, 0.088),
                                    (0.644, 0.493)],
                                   [1, 2]]],
                           '01': [[[(0.357, 0.902), (0.17, 0.65),
                                    (0.184, 0.337), (0.343, 0.095),
                                    (0.644, 0.098)],
                                   [0, 2, 4]]],
                           '02': [[[(...
                                    ...
                                   ... etc ]]]}

        Each polygon's data consist of two lists:

            1. A list of point tuples (x, y) that constitute the polygon.
            Points' values should be expressed as percentages of the widget's
            width and height, where (0, 0) is widget's (x, y), (1, 1) is
            widget's (right, top) and (.5, .5) is widget's center.

            2. A list of indices, determining which points of the previous
            list, will be used as checkpoints {See Consept above).

            IMPORTANT: A checkpoint must be able to have the whole polygon
                between its adjacent sides to qualify (See 'Rotabox concept'
                below).

    [draw_bounds] boolean (False):
        This option could be useful during the manipulation of the widget's
        bounds, as it makes the bounds visible.
        There's also a visual editor available (See Rotaboxer below).

_______________
Extra features:

    Polygon-specific collision:
        In a positive collision check, instead of True, the number of the
        colliding polygon is returned (i.e. 1 for the first, 2 for the second,
        and so on).
        So, if there are more than one polygons, the user can check weather a
        specific polygon is colliding:

            if self.collide_widget(stone) == 1:
                print("I've been hit in the head!")

    Non-Rotabox widgets classification:
        There might be cases where Rotabox will have to determine how a certain
        non-Rotabox widget will be treated (collision-wise).
        Two possible cases are addressed in the code (but out-commended) using
        the arbitrary flags [bullet] and [platform].

        (NOTE: THE FLAGS MUST BE DEFINED BY THE USER IN SAID WIDGET).

__________
Rotaboxer:
    (A visual editor for Rotabox bounds)

    A convenient way to shape the colliding areas of a Rotabox widget,
    especially when dealing with multiple frames of a spritesheet animation.
    The user opens a .png image or an .atlas file in the editor, works on its
    bounds and, when ready, copies the resulting code to clipboard for use in a
    Rotabox widget.

    To use it run rotaboxer.py directly.
    It can be found next to this module at the package root.

___________________________________________________________________________
If this module is run directly, shows an example, where two Rotabox widgets,
of different configurations, collide with each other while rotating. The code
of the example is below, at the end of the document, and is not an essential
part of the module.

unjuan 2017
'''

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.graphics import PushMatrix, Rotate, PopMatrix
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import (NumericProperty, ReferenceListProperty,
                             AliasProperty, ObjectProperty, BooleanProperty,
                             ListProperty, BoundedNumericProperty)
from math import radians, atan2, sin, cos
from itertools import izip

__author__ = 'unjuan'
__version__ = '0.9.0'

__all__ = 'Rotabox'


class Rotabox(Widget):
    '''See module's documentation.'''

    __events__ = ('on_transform_with_touch', 'on_bring_to_front')

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
    '''The widget's aspect ratio. If not defined, image's ratio will be used.'''
    aspect_ratio = NumericProperty(0.)

    '''This should be the image that any custom bounds are meant for.
    If not defined, widget will try to locate the upper image in its tree.'''
    image = ObjectProperty()

    '''Custom bounds' definition interface. (See module's documentation).'''
    custom_bounds = ObjectProperty([[[(0, 0), (1, 0), (1, 1), (0, 1)], [0, 2]]])

    '''If a polygon's index is in this list, the polygon becomes 'invisible'
    to the collision checks of others.'''
    hidden_bounds = ListProperty()

    '''Enables widget's advanced collision detection. If False, widget will
    collide as a normal (non-Rotabox) widget.'''
    allow_rotabox = BooleanProperty(True)

    # ------------------------------------------ TOUCH TRANSFORMATION INTERFACE
    '''If touched, the widget will be pushed to the top of parent widget tree.'''
    touched_to_front = BooleanProperty(False)

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

    '''Allow multitouch rotation.'''
    allow_touch_rotation = BooleanProperty(False)

    '''Allow multitouch scaling.'''
    allow_touch_scaling = BooleanProperty(False)

    '''Minimum scale allowed.'''
    scale_min = NumericProperty(0.01)

    '''Maximum scale allowed.'''
    scale_max = NumericProperty(1e20)

    def get_scale(self):
        return float(self.width) / self.original_size[0]

    def set_scale(self, scale):
        pivot = self.pivot[:]
        self.size = (scale * self.original_size[0],
                     scale * self.original_size[1])
        self.pivot = pivot
        if self.initial_scale:
            return
        self.initial_scale = self.scale

    '''Current widget's scale.'''
    scale = AliasProperty(get_scale, set_scale, bind=('width', 'height',
                                                      'original_size'))

    '''How many touches will be treated as one single drag touch.'''
    single_drag_touch = BoundedNumericProperty(1, min=1)

    '''How many touches will be treated as one single transformation touch.'''
    single_trans_touch = BoundedNumericProperty(1, min=1)

    '''Rotate around [origin]..'''
    single_touch_rotation = BooleanProperty(False)

    '''Scale around [origin].'''
    single_touch_scaling = BooleanProperty(False)

    '''If True, limiting the touch inside the bounds will be done after
    dispaching the touch to the child and grandchildren, so even outside the
    bounds they can still be touched.
    IMPORTANT NOTE: Grandchildren, inside or outside the bounds, can collide
        independently ONLY if widget is NOT ROTATED ([angle] must be 0).'''
    collide_after_children = BooleanProperty(True)

    # ------------------------------------------------------- UTILITY INTERFACE
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

    '''Signifies the completion of the widget's initial preparations.'''
    ready = BooleanProperty(False)

    '''Enables bounds visualization (for testing).'''
    draw_bounds = BooleanProperty(False)

    '''Enables touch painting on collidable areas (for testing).'''
    allow_paint = BooleanProperty(False)

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
        self.prepared = False
        self.frames = {}
        self.polygons = []
        self.visible_points = []
        self.bbox = ()
        self.visible_bbox = ()
        self.draw_lines = []
        self.paint_group = InstructionGroup()
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
                  hidden_bounds=self.on_reset)
        self.box_color = Color(1, 0, 0, 1)
        self.box_lines = []

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
            self.image.texture.mag_filter = 'nearest'
            self.image.allow_stretch = True
            # In case of a stationary widget with animated bounds.
            self.image.bind(source=self.trigger_update)

            # Calculating widget's size from available inputs.
            if (not (self.width - scale > 1 or self.height - scale > 1)
                    or self.sized_by_img):
                self.original_size = self.image.texture_size
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
            self.define_bounds()

            # Setting canvas in case of test drawing
            if self.draw_bounds:
                self.canvas.after.add(self.draw_color)
                # self.canvas.after.add(self.box_color)
                if self.frames:
                    self.polygons = self.frames[self.image.source.split('/')[-1]]

                for _ in self.polygons:
                    self.draw_lines.append(Line(close=True, dash_offset=3,
                                           dash_length=5))
                    self.box_lines.append(Line(close=True, dash_offset=3,
                                           dash_length=5))
                for line in self.draw_lines:
                    self.canvas.after.add(line)
                for line in self.box_lines:
                    self.canvas.after.add(line)
                # Securing draw on a stationary widget, by forcing the [update].
                self.x += .001
            if self.allow_paint:
                self.canvas.after.add(self.paint_group)
                self.paint_group.add(self.paint_color)

        self.trigger_update()

    def update_size(self):
        '''Size, scale and ratio handling.'''
        width, height = self.size
        if round(self.ratio, 2) != round(width / float(height), 2):
            # Adjusting size to fit ratio
            last_size = self.last_size
            if abs(width - last_size[0]) > abs(height - last_size[1]):
                self.size = width, float(width) / self.ratio
            else:
                self.size = height * self.ratio, height
            dw = self.width - last_size[0]
            dh = self.height - last_size[1]
            # Moving widget to keep pivot's position the same, to originate the
            # resizing from pivot.
            self.pivot = (self.pivot_x - dw * .5, self.pivot_y - dh * .5)

        if self.allow_rotabox:
            # Scaling widget's bounds
            if self.frames:
                for frame in self.frames.itervalues():
                    scale_polygons(self.size, frame)
            else:
                scale_polygons(self.size, self.polygons)

            self.update_bounds(self.polygons, True, self.radiangle, self.pos)

        if self.children:
            # Adjusting the child's size to fit widget's
            self.child.size = self.size

        self.last_size = self.size[:]
        self.trigger_update()

    def update(self, *args):
        '''Updates the widget's angle, point of rotation, bounds and child's
        position.
        Also runs the [scale] method on size change and the [prepare] method
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
                # An identically keyed atlas file is assumed here.
                self.polygons = self.frames[self.image.source.split('/')[-1]]
                motion = True
            if motion or angle:
                self.radiangle = radians(angle)  # % 6.2831853072
                self.update_bounds(self.polygons, motion, self.radiangle, pos)
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

    # ------------------------------------------------------ BOUNDS & COLLISION
    def define_bounds(self):
        '''Organising the data from the user's [self.custom_bounds] hints.'''
        if isinstance(self.custom_bounds, dict):   # Animation case
            for key, frame in self.custom_bounds.iteritems():
                self.frames[key] = self.make_polygons(frame)
        if isinstance(self.custom_bounds, list):  # Single image case
            self.polygons = self.make_polygons(self.custom_bounds)
        self.update_bounds(self.polygons, True, self.radiangle, self.pos)

    def make_polygons(self, frame):
        '''Construction of polygon objects.'''
        polygons = []
        for i in xrange(len(frame)):
            pol = Polygon()
            pol.hints = frame[i][0]
            pol.check_ids = frame[i][1]
            if i in self.hidden_bounds:
                pol.hidden = True
            polygons.append(pol)
        # Scaling the polygons' points of reference.
        scale_polygons(self.size, polygons)
        # Finding out the direction in which each polygon was defined
        trace_polygons(polygons)
        return polygons

    def update_bounds(self, polygons, motion, angle, pos):
        '''Converting each polygon's [points] of reference, into polygons's
        [bounds], taking widget's motion and/or rotation into account.
        All polygons' [bounds] then become the widget's [bounds], from which
        its [bbox] derive.'''
        points = []
        boxes = []
        for pol in polygons:
            if motion:
                move_bounds(angle, pol, pos)
            if angle:
                rotate_bounds(self.origin, angle, pol)
            pol.bbox = calculate_extremes(pol.points)
            boxes.append(pol.bbox)
            points += pol.points

        self.bbox = calculate_bbox(boxes)

        if not self.hidden_bounds:
            self.visible_points = points
            self.visible_bbox = self.bbox
            return

        hidden_pols = [pol for pol in polygons if pol.hidden]
        plain_pols = [pol for pol in polygons if pol not in hidden_pols]
        points = [point for pol in plain_pols for point in pol.points]

        self.polygons = plain_pols + hidden_pols
        self.visible_points = points

        self.visible_bbox = calculate_bbox([pol.bbox for pol in plain_pols])

    def collide_point(self, x=0, y=0):
        '''"Oddeven" point-in-polygon method:
        Checking the membership of touch point by assuming a ray from that
        point to infinity (to window right) and counting the number of
        polygon sides that this ray crosses. If this number is odd,
        the point is inside; if even, the point is outside.
        '''
        if self.allow_rotabox:
            for pol in self.polygons:
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

    def collide_widget(self, widget):
        '''Axis-aligned bounding box testing, before widget is sent to
        [collide_more] for more checks.
        '''
        try:  # Assuming the other widget is a Rotabox, too.
            this_box = self.bbox
            that_box = widget.visible_bbox
            if this_box[2] < that_box[0]:
                return False
            if this_box[0] > that_box[2]:
                return False
            if this_box[3] < that_box[1]:
                return False
            if this_box[1] > that_box[3]:
                return False
        except (AttributeError, IndexError):  # ..but it's not.
            return super(Rotabox, self).collide_widget(widget)
        return collide_more(self.polygons, widget, self.radiangle)

    def draw(self):
        '''If [draw_bounds] is True, visualises the widget's bounds.
        For testing.'''
        try:
            for i in xrange(len(self.polygons)):
                self.draw_lines[i].points = [n for point
                                             in self.polygons[i].points
                                             for n in point]

            #     box = self.polygons[i].bbox
            #     self.draw_color.rgba = .8, .2, 0, 1
            #     self.box_lines[i].points = [box[0], box[1],
            #                                 box[2], box[1],
            #                                 box[2], box[3],
            #                                 box[0], box[3]]
            # box = self.bbox
            # self.box_color.rgba = .8, .2, 0, 1
            # self.box_lines[0].points = (box[0], box[1],
            #                         box[2], box[1],
            #                         box[2], box[3],
            #                         box[0], box[3])
        except IndexError:
            pass

    # ----------------------------------- TOUCH HANDLING (altered Scatter code)
    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not self.collide_after_children:
            if not self.collide_point(x, y):
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
                or self.allow_touch_rotation
                or self.allow_touch_scaling
                or self.single_touch_rotation
                or self.single_touch_scaling
                or self.allow_paint):
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
            self.dispatch('on_bring_to_front', touch)

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
            if not self.allow_paint:
                return True
            # paint on collidable areas, for bounds inspection
            self.paint_group.add(Line(circle=(x, y, 3)))

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
                new_scale = scale * self.scale
                if new_scale < self.scale_min:
                    scale = self.scale_min / float(self.scale)
                elif new_scale > self.scale_max:
                    scale = self.scale_max / float(self.scale)
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

        # setting rotation origin to the anchor
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

        angle = new_line.angle(old_line) * self.allow_touch_rotation
        self.angle += angle

        if self.allow_touch_scaling:
            scale = new_line.length() / old_line.length()
            new_scale = scale * self.scale
            if new_scale < self.scale_min:
                scale = self.scale_min / float(self.scale)
            elif new_scale > self.scale_max:
                scale = self.scale_max / float(self.scale)
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

    def on_bring_to_front(self, touch):
        '''
        Called when a touch event causes the widget to be brought to the
        front of the parent (only if :attr:`touched_to_front` is True)

        :Parameters:
            `touch`: the touch object which brought the widget to front.
        '''
        pass

    # ---------------------------------------------------------- SIZE_HINT LOCK
    # Locking size_hint property to None, None,
    # in order to keep intended aspect ratio (critical for custom_bounds).
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
    size_hint = ReferenceListProperty(size_hint_x, size_hint_y)

    # Used for calculating the widget's scale. It's the user's input size
    # or the [texture_size] of the widget's [image].
    original_size = ListProperty([1, 1])

    # A fractional value that keeps [pivot] relative to the widget's size
    # and position. [origin] sets and changes it.
    pivot_bond = ListProperty([.5, .5])


class Polygon(object):  # A DICTIONARY ????????????????????????????????????
    '''An internal object to keep each polygon's data.'''
    __slots__ = ('hints', 'ref_pts', 'rel_pts', 'points', 'bbox',
                 'hidden', 'check_ids', 'rays', 'neg_dir')

    def __init__(self):
        self.hints = []  # User points' hints.
        self.ref_pts = []  # Scaled points.
        self.rel_pts = []  # Translated points.
        self.points = []  # Final points (any rotation is considered here).
        self.bbox = ()  # Rough bounding box from widget's extremities.
        self.hidden = False  # Polygon 'invisible' to others' checks.
        self.check_ids = []  # Checkpoints' indices in [points].
        self.rays = []  # Checkpoints' adjacent sides' angles.
        self.neg_dir = False  # Clockwise-defined polygon.


def locate_images(root):
    '''Traversing the widget tree to find the topmost Image to assign to
    [image] property.'''
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


def scale_polygons(size, polygons):
    '''Scaling the polygons' points of reference.'''
    for pol in polygons:
        pol.ref_pts = [tuple(x * y for x, y in izip(point, size))
                       for point in pol.hints]
        # Populating these, also, in case of a not rotated, still widget.
        pol.points = pol.rel_pts = pol.ref_pts


def trace_polygons(polygons):
    '''Determining the direction in which each polygon is defined (i.e.
    clockwise or not), essential for making sure that collision checks are
    pointed towards the inside of the polygon.
    Also, storing segment angles, to use in collision checks later.'''
    pi = 3.142
    for pol in polygons:
        diffs = 0
        last_angle = None
        for i in xrange(len(pol.ref_pts)):
            j = (i + 1) % len(pol.ref_pts)
            # Polygon segment's angle (angle difference from x axis).
            angle = atan2(pol.ref_pts[j][1] - pol.ref_pts[i][1],
                          pol.ref_pts[j][0] - pol.ref_pts[i][0])
            # Calculating each two segments' difference in angle
            try:
                diff = angle - last_angle
            except TypeError:
                # For the first comparison use the last segment's angle
                last_angle = atan2(pol.ref_pts[i][1] - pol.ref_pts[-1][1],
                                   pol.ref_pts[i][0] - pol.ref_pts[-1][0])
                diff = angle - last_angle
            # Normalizing the angles difference
            if diff > pi:
                diff -= pi
            elif diff < -pi:
                diff += pi
            diffs += diff
            # Storing the angles of segment couples containing
            # a checkpoint.
            if i in pol.check_ids:
                pol.rays.append([last_angle + pi, angle])
            else:
                pol.rays.append(None)
            last_angle = angle
        # Determining the direction of the polygon
        if diffs < 0:
            pol.neg_dir = True


def move_bounds(angle, pol, pos):
    # Translating points to current position.
    pol.rel_pts = [[x + y for x, y in izip(point, pos)]
                   for point in pol.ref_pts]
    if not angle:
        pol.points = pol.rel_pts


def rotate_bounds(origin, angle, pol):
    # Optimizations
    at = atan2
    si = sin
    co = cos
    pol.points = [to_rotated(point, origin, angle, at, si, co)
                  for point in pol.rel_pts]


def to_rotated(point, orig, angle, arctan, sine, cosine):
    '''Tranlating each polygon's point acccording to widget's rotation.'''
    dx = point[0] - orig[0]
    dy = point[1] - orig[1]
    distance = (dx * dx + dy * dy) ** .5
    angle = (angle + arctan(dy, dx)) % 6.283  # 2pi
    return (orig[0] + distance * cosine(angle),
            orig[1] + distance * sine(angle))


def calculate_extremes(points):
    '''An axis-aligned bounding box, calculated from polygon extremities.'''
    if points:
        left, bottom = map(min, *points)
        right, top = map(max, *points)
        return left, bottom, right, top
    return ()


def calculate_bbox(bboxes):
    '''An axis-aligned bounding box, calculated from polygons' bboxes.'''
    if bboxes:
        if len(bboxes) > 1:
            left, bottom, _, _ = map(min, *bboxes)
            _, _, right, top = map(max, *bboxes)
            return left, bottom, right, top
        else:
            return bboxes[0]
    else:
        return ()


def collide_more(polygons, alien, angle):
    albox = alien.visible_bbox
    alpoints = alien.visible_points
    for pol in polygons:
        # Preliminary 1: Filtering own pols vs widget's bbox.
        box = pol.bbox
        if box[2] < albox[0]:
            continue
        if box[0] > albox[2]:
            continue
        if box[3] < albox[1]:
            continue
        if box[1] > albox[3]:
            continue

        # Preliminary 1: Filtering the other widget's points
        alien_points = [point for point in alpoints if
                        box[0] <= point[0] <= box[2] and
                        box[1] <= point[1] <= box[3]]
        if not alien_points:
            continue

        for alpoint in alien_points:
            # For each point with its index in [check_ids]:
            for idx in pol.check_ids:
                checkpoint = pol.points[idx]
                # Calculating the angle of the ray that starts from
                # the checkpoint and passes through the alien point.
                ray0 = atan2(alpoint[1] - checkpoint[1],
                             alpoint[0] - checkpoint[0]) % 6.283  # 2pi
                # Updating the angles of checkpoint's adjacent sides.
                ray1 = (pol.rays[idx][0] + angle) % 6.283
                ray2 = (pol.rays[idx][1] + angle) % 6.283
                # Considering polygon's direction.
                if pol.neg_dir:
                    ray1, ray2 = ray2, ray1
                # Normalizing comparison if the cartesian circle's
                # seam (360 = 0) is between the check-angles.
                if not ray1 > ray2:
                    ray1 = (ray1 + 6.283 - ray2)  # % 6.283
                    ray0 = (ray0 + 6.283 - ray2) % 6.283
                    ray2 = 0
                # Checking weather the alien-angle is between the
                # check-angles.
                if not ray1 > ray0 > ray2:
                    break
            # If no break
            else:
                # Polygons without checkpoints skip the loop, causing false
                # positives.
                if pol.check_ids:
                    # Returning the colliding polygon's index, in a tuple to
                    # always evaluate to True.
                    return polygons.index(pol),
    # If all broke
    return False


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
'''THIS IS THE END OF THE ACTUAL MODULE. THE REST, IS JUST A USAGE EXAMPLE.'''
# vvvvvvvvvvvvvvvvvvvv (Run the module directly, to watch) vvvvvvvvvvvvvvvvvvv

if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.uix.floatlayout import FloatLayout
    from kivy.lang import Builder

    Builder.load_string('''
<Root>:
    blue: blue
    clear: clear
    Rotabox:
        id: blue
        size: root.width * .4, root.height * .528
        pivot: root.width * .3, root.height * .5
        custom_bounds:
            [[[(0.225, 0.685), (0.222, 0.405), (0.353, 0.278),
            (0.356, 0.435), (0.53, 0.261), (0.665, 0.398), (0.849, 0.587),
            (0.515, 0.553), (0.386, 0.683), (0.384, 0.526)], [1, 3, 5, 7, 9]]]
        Image:
            source: 'data/logo/kivy-icon-256.png'
            color: 0, .2, .5, 1
    Rotabox:
        id: clear
        size: root.width * .25, root.height * .22
        pivot: root.width * .8, root.height * .5
        custom_bounds:
            [[[(0.013, 0.985), (0.016, 0.407), (0.202, 0.696)],
            [1, 2]],
            [[(0.267, 0.346), (0.483, -0.005), (0.691, 0.316), (0.261, 0.975)],
            [0, 2]],
            [[(0.539, 0.674), (0.73, 0.37), (0.983, 0.758)],
            [2, 0]],
            [[(0.033, 0.315), (0.212, 0.598), (0.218, 0.028)],
            [0, 2]]]
        draw_bounds: True
    ''')

    class Root(FloatLayout):
        def __init__(self, **kwargs):
            super(Root, self).__init__(**kwargs)
            Clock.schedule_interval(self.update, 0)

        def update(self, *args):
            this = self.blue
            that = self.clear
            if this.collide_widget(that) or that.collide_widget(this):
                this.x -= 1
                that.x += 1
            else:
                this.x += .5
                that.x -= .5
                this.angle += .5
                that.angle -= .7

    runTouchApp(Root())
