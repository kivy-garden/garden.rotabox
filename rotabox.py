
'''

ROTABOX                                           kivy 1.9.0 - python 2.7.10
=======
    Rotabox is kivy widget with fully customizable 2D bounds that follow its
    rotation.
    The users shape their own, specific bounds, to fit an image (or a series
    of images in an animation), using polygons.
    There's a handy editor for this, available in the package (See Rotaboxer
    at the end of this document).

____________
Basic Usage:

    To use Rotabox, just include *rotabox.py* in your project files.

        from rotabox import Rotabox

        rb = Rotabox()
        rb.image = Image(source='img.png')
        rb.add_widget(rb.image)
        rb.custom_bounds = True
        rb.bounds = [[[(0.015, 0.981), (0.019, 0.342),
                       (0.212, 0.034), (0.21, 0.427),
                       (0.48, -0.001), (0.714, 0.342),
                       (0.985, 0.75), (0.462, 0.668),
                       (0.262, 0.978), (0.265, 0.599)],
                      [9, 1, 3, 7, 5]]]

    * Make a Rotabox instance.
    * Add an Image widget to the instance and assign it to the instance's
      [image] attribute.
    * Switch the instance's [custom_bounds] flag to True.
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

    NOTE: As a general rule, at least one of two consecutive vertices should be
    a checkpoint, but they don't both have to be.

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

    [angle] AliasProperty (0):
        The angle of rotation.

    [origin] tuple (center):
        The point of rotation.

________________________________
Customizing the Collidable Area:

    [custom_bounds] boolean (False):
        The user will have to enable Rotabox's ability to compensate for
        rotation and allow bounds modification.
        With [custom_bounds] enabled, the default settings provide a colliding
        rectangle, the size of the widget, that follows its rotation.

    [bounds] list or dict ([[[(0, 0), (1, 0), (1, 1), (0, 1)], [0, 2]]])
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
        bounds, as it makes the bounds visible and lets the user paint with
        the mouse on the collidable areas, to test them.
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

unjuan 2016
'''

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import PushMatrix, Rotate, PopMatrix
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import (NumericProperty, ReferenceListProperty,
                             AliasProperty, ObjectProperty)
from math import radians, atan2, sin, cos
from itertools import izip

__author__ = 'unjuan'
__version__ = '0.8.0'

class Rotabox(Widget):
    '''(See module's documentation).'''

    '''Rotation angle.'''
    angle = NumericProperty()
    bounds = ObjectProperty()

    # Locking size_hint property to None, None.
    def get_size_hint_x(self):
        return None
    def set_size_hint_x(self, value):
        if value is not None:
            raise Exception("Rotabox can't use size_hint.")
    size_hint_x = AliasProperty(get_size_hint_x, set_size_hint_x)
    def get_size_hint_y(self):
        return None
    def set_size_hint_y(self, value):
        if value is not None:
            raise Exception("Rotabox can't use size_hint.")
    size_hint_y = AliasProperty(get_size_hint_y, set_size_hint_y)
    size_hint = ReferenceListProperty(size_hint_x, size_hint_y)

    class Polygon(object):
        '''An internal object to keep each polygon's data.'''

        __slots__ = ('hints', 'ref_pts', 'rel_pts', 'points',
                     'check_ids', 'rays', 'neg_dir')

        def __init__(self):
            self.hints = []  # User points.
            self.ref_pts = []  # Scaled points.
            self.rel_pts = []  # Translated points.
            self.points = []  # Final points.
            self.check_ids = []  # checkpoints' indices.
            self.rays = []  # checkpoints' adjacent sides' angles.
            self.neg_dir = False  # Clockwise-defined polygon.

    def __init__(self, **kwargs):
        self._trigger_update = Clock.create_trigger(self.update, -1)
        super(Rotabox, self).__init__(**kwargs)

        '''Rotation point.'''
        self.origin = self.center

        '''If an image is assigned, it will determine the widget's ratio.'''
        self.image = None

        '''Arbitrary aspect ratio (if no image assigned).'''
        self.ratio = 0.

        '''Enable custom bounds. If False, widget will collide as a
        non-Rotabox widget.'''
        self.custom_bounds = False

        '''Custom bounds' definition interface. Can be a list in the form of
        [polygons[polygon[points],[chk_points]]] (like the rectangle used
        below as default) or a dictionary containing several lists like this,
        with keys matching the keys in an .atlas file.'''
        self.bounds = [[[(0, 0), (1, 0), (1, 1), (0, 1)], [0, 2]]]

        '''Enable bounds visualization and mouse painting (for testing).'''
        self.draw_bounds = False

        self.frames = {}
        self.polygons = []
        self.points = []
        self.box = [0, 0, 0, 0]
        self.last_angle = 0
        self.last_pos = []
        self.radiangle = 0
        self.draw_lines = []
        self.draw_color = Color(0.29, 0.518, 1, 1)
        self.rotate = Rotate(angle=0, origin=self.center)
        self.canvas.before.add(PushMatrix())
        self.canvas.before.add(self.rotate)
        self.canvas.after.add(PopMatrix())
        self.paint_group = InstructionGroup()
        self.bind(children=self._trigger_update,
                  parent=self._trigger_update,
                  size=self._trigger_update,
                  pos=self._trigger_update,
                  angle=self._trigger_update)
        self.scaled = False
        self.ready = False

    def add_widget(self, widget, index=0, **kwargs):
        '''Birth control'''

        if self.children:
            raise Exception('Rotabox can have one child only.')
        return super(Rotabox, self).add_widget(widget, index)

    def on_size(self, *args):
        '''Enables the ON SIZE section of the [update] method.'''
        self.scaled = False

    def on_bounds(self, *args):
        '''Enables bounds reset.'''

        self.scaled = False
        self.ready = False
        self._trigger_update()

    def prepare(self):
        '''Initial preparations.'''

        if not self.image:
            # Auto assigning [self.image] if child is an image.
            if isinstance(self.children[0], Image):
                self.image = self.children[0]
        if self.image:
            self.image.allow_stretch = True
            # self.image.texture.mag_filter = 'nearest'
            self.image.bind(source=self.scale)
        # Building widget's bounds.
        if self.custom_bounds:
            self.define_bounds()

        if self.draw_bounds:
            self.canvas.after.add(self.paint_group)
            self.canvas.after.add(self.draw_color)
            for _ in self.polygons:
                self.draw_lines.append(Line(close=True, dash_offset=3,
                                       dash_length=5))
            for line in self.draw_lines:
                self.canvas.after.add(line)

    def scale(self, *args):
        '''Size and ratio updates.'''
        # Adjusting the widget's ratio if [self.image] or [self.ratio]
        try:
            self.ratio = self.image.image_ratio
        except AttributeError:
            pass
        if self.ratio and self.height:
            w, h = self.size
            ratio = self.ratio
            if abs(ratio - w / float(h)) > .01:
                self.size = ((h * ratio, h) if h < w / ratio
                             else (w, w / ratio))

        # Adjusting the child's or image's size
        try:
            self.image.size = self.size
        except AttributeError:
            self.children[0].size = self.size

        # Updating widget's bounds
        if self.custom_bounds:
            if self.frames:
                for frame in self.frames.itervalues():
                    self.scale_bounds(self.size, frame)
            else:
                self.scale_bounds(self.size, self.polygons)

    def update(self, *args):
        '''The central updater.
        Maintains the widget's point of rotation, verifies motion and updates
        the child's (or image's if different) position and the custom bounds.
        Also runs the [scale] method on size and the [prepare] method initially.
        '''

        if self.angle:
            # Updating internal angle of rotation
            self.rotate.angle = self.angle
        if self.children:
            motion = self.pos != self.last_pos
            if motion:
                # Updating internal point of rotation
                self.rotate.origin = self.origin
                # Updating the child's or image's position
                if self.image:
                    self.image.pos = self.pos
                else:
                    self.children[0].pos = self.pos
                self.last_pos = self.pos[:]
            # Updating custom bounds
            if self.custom_bounds:
                if self.frames:
                    # An identically keyed atlas file is assumed here.
                    polygons = self.frames[self.image.source.split('/')[-1]]
                else:
                    polygons = self.polygons
                if motion or self.angle:
                    self.radiangle = radians(self.angle) % 6.283
                    self.update_bounds(polygons, motion, self.radiangle)
            if self.scaled:
                return

            # -------------------------- ON SIZE
            self.scale()
            self.scaled = True
            if self.ready:
                return

            # ------------------------- INITIALLY
            self.prepare()
            self.ready = True

    # ---------------------------------------------- BOUNDS & COLLISION

    def define_bounds(self):
        '''Organising the data from the user's [self.bounds] hints.'''

        if isinstance(self.bounds, dict):   # Animation case
            for key, frame in self.bounds.iteritems():
                self.frames[key] = self.make_polygons(frame)
        if isinstance(self.bounds, list):  # Single image case
            self.polygons = self.make_polygons(self.bounds)
        self.update_bounds(self.polygons, True)

    def make_polygons(self, frame):
        '''Construction of polygon objects.'''

        polygons = []
        for p in frame:
            pol = self.Polygon()
            pol.hints = p[0]
            pol.check_ids = p[1]
            polygons.append(pol)

        # Scaling the polygons' points of reference.
        self.scale_bounds(self.size, polygons)
        # Finding out the direction in which each polygon was defined
        self.trace_polygons(polygons)

        return polygons

    @staticmethod
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
                j = i + 1 if i + 1 < len(pol.ref_pts) else 0
                # Polygon segment's angle (angle difference from x axis).
                angle = atan2(pol.ref_pts[j][1] - pol.ref_pts[i][1],
                              pol.ref_pts[j][0] - pol.ref_pts[i][0])
                if last_angle is None:
                    # For the first comparison use the last segment's angle
                    last_angle = atan2(pol.ref_pts[i][1] - pol.ref_pts[-1][1],
                                       pol.ref_pts[i][0] - pol.ref_pts[-1][0])
                # Calculating each two segments' difference in angle
                diff = angle - last_angle
                # Normalizing the angles difference
                if diff > pi:
                    diff -= pi
                elif diff < -pi:
                    diff += pi
                diffs += diff
                # Storing the angles of the couples of segments that contain
                # a checkpoint.
                if i in pol.check_ids:
                    pol.rays.append([last_angle + pi, angle])
                else:
                    pol.rays.append(None)
                last_angle = angle
            # Determining the direction of the polygon
            if diffs < 0:
                pol.neg_dir = True

    @staticmethod
    def scale_bounds(size, polygons):
        '''Scaling the polygons' points of reference.'''

        for pol in polygons:
            pol.ref_pts = [tuple(x * y for x, y in izip(point, size))
                           for point in pol.hints]
            # Populating these, also, in case of a still widget.
            pol.rel_pts = pol.ref_pts
            pol.points = pol.ref_pts

    def update_bounds(self, polygons=None, motion=False, angle=0.):
        '''Converting each polygon's [points] of reference, into polygons's
        [bounds], taking widget's motion and/or rotation into account.
        All polygons' [bounds] then become the widget's [bounds], from which
        its [box] derive.'''

        # Translating points to current position.
        if motion:
            # Optimization
            pos = self.pos
            for pol in polygons:
                pol.rel_pts = [[x + y for x, y in izip(point, pos)]
                                for point in pol.ref_pts]
            if not angle:
                for pol in polygons:
                    pol.points = pol.rel_pts
        # Rotating points to current angle.
        if angle:
            # Optimizations
            at = atan2
            si = sin
            co = cos
            origin = self.origin
            to_rotated = self.to_rotated
            for pol in polygons:
                pol.points = [to_rotated(point, origin, angle, at, si, co)
                              for point in pol.rel_pts]
        # The widget's bounds
        bounds = [point for pol in polygons for point in pol.points]
        self.box = self.calc_box(bounds)
        self.points = bounds

        if self.draw_bounds:
            self.draw()

    @staticmethod
    def to_rotated(point, orig, angle, arctan, sine, cosine):
        '''Tranlating each polygon's point acccording to rotation.'''

        dx = point[0] - orig[0]
        dy = point[1] - orig[1]
        distance = (dx * dx + dy * dy) ** .5
        angle = (angle + arctan(dy, dx)) % 6.283

        return ((orig[0] + distance * cosine(angle)),
                (orig[1] + distance * sine(angle)))

    @staticmethod
    def calc_box(bounds):
        '''An axis-aligned bounding box, calculated from widget extremities.'''

        if bounds:
            left, bottom = map(min, *bounds)
            right, top = map(max, *bounds)
            return [left, bottom, right, top]
        return []

    def collide_widget(self, widget):
        '''Axis-aligned bounding box intersection tests.
        Each incoming widget's rough borders are checked against this widget's
        rough borders and if colliding, its bounds' points or vertices are
        filtered, before being sent to [collide_point] for fine checking.'''

        if self.box:
            this_box = self.box
            try:  # Assuming that widget is a Rotabox with custom bounds.
                that_box = widget.box
                # First check ([box] vs [box])
                if this_box[2] < that_box[0]:
                    return False
                if this_box[0] > that_box[2]:
                    return False
                if this_box[3] < that_box[1]:
                    return False
                if this_box[1] > that_box[3]:
                    return False
                points = widget.points
            except (AttributeError, IndexError):  # ..but it's not.
                # First check ([box] vs Widget's bbox)
                if this_box[2] < widget.x:
                    return False
                if this_box[0] > widget.right:
                    return False
                if this_box[3] < widget.y:
                    return False
                if this_box[1] > widget.top:
                    return False

                ''' Optional conditionals to determine how Rotabox will treat
                certain non-Rotabox widgets (See 'Extra features' in module's
                documentation).

                [bullet] is a non-Rotabox widget, small enough to be treated
                    as a single point.
                    (ATTRIBUTE MUST BE DEFINED BY THE USER IN SAID WIDGET).
                '''
                # try:
                #     if widget.bullet:
                #         if self.collide_point(points=widget.center):
                #             return True
                # except AttributeError:
                #     pass

                '''
                [platform] is a non-Rotabox widget whose vertices are too far
                    apart and should be treated in a coarse manner.
                    (ATTRIBUTE MUST BE DEFINED BY THE USER IN SAID WIDGET)
                '''
                # try:
                #     if widget.platform:
                #         return True
                # except AttributeError:
                #     pass

                points = [(widget.x, widget.y), (widget.right, widget.y),
                          (widget.right, widget.top), (widget.x, widget.top)]

            # Second check (Filter individual points)
            hot_points = [point for point in points if
                          this_box[0] <= point[0] <= this_box[2] and
                          this_box[1] <= point[1] <= this_box[3]]

            # Third check (Fine checking most probable points).
            return self.collide_point(alien_points=hot_points)
        else:
            # Falling back to original Widget's checks.
            return super(Rotabox, self).collide_widget(widget)

    def collide_point(self, x=0, y=0, alien_points=None):
        '''Also serves as the [collide_widget]'s fine section.
            Supports lists of points as well.'''

        if self.custom_bounds:
            # If checking for a touch
            if not alien_points:
                alien_points = [(x, y)]
            angle = self.radiangle
            # The other widget's points
            for alien in alien_points:
                for pol in self.polygons:
                    # For each point with its index in [check_ids]:
                    for index in pol.check_ids:
                        checkpoint = pol.points[index]
                        # Calculating the angle of the ray that starts from
                        # the checkpoint and passes through the incoming point.
                        ray0 = atan2(alien[1] - checkpoint[1],
                                     alien[0] - checkpoint[0]) % 6.283  # 2pi
                        # Updating the angles of checkpoint's adjacent sides.
                        ray1 = (pol.rays[index][0] + angle) % 6.283
                        ray2 = (pol.rays[index][1] + angle) % 6.283
                        # Considering polygon's direction.
                        if pol.neg_dir:
                            ray1, ray2 = ray2, ray1
                        # Normalizing comparison if the cartesian circle seam
                        # (360 = 0) is between the check-angles.
                        if not ray1 > ray2:
                            ray1 = (ray1 + 6.293 - ray2) % 6.283
                            ray0 = (ray0 + 6.293 - ray2) % 6.283
                            ray2 = .01
                        # Checking weather the alien-angle is between the
                        # check-angles.
                        if not ray1 > ray0 > ray2:
                            break
                    else:  # If no break
                        '''Returning the number of the colliding polygon
                        (index + 1 to be sure it evaluates to True).'''
                        return self.polygons.index(pol) + 1
            # If all broke
            return False
        else:
            # Falling back to original Widget's check.
            return super(Rotabox, self).collide_point(x, y)

    def on_touch_move(self, touch):
        '''If [draw_bounds] is True, manages painting on collidable areas, for
        bounds inspection.'''

        if self.draw_bounds:
            if self.collide_point(*touch.pos):
                self.paint_group.add(Color(.7, .3, 0, 1))
                self.paint_group.add(Line(circle=(touch.pos[0],
                                                  touch.pos[1], 3)))
        else:
            super(Rotabox, self).on_touch_move(touch)

    def draw(self):
        '''If [draw_bounds] is True, visualises the widget's bounds.
        For bounds testing.'''

        try:
            for i in xrange(len(self.polygons)):
                self.draw_lines[i].points = [n for point
                                             in self.polygons[i].points
                                             for n in point]
        except IndexError:
            pass

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
'''THIS IS THE END OF THE ACTUAL MODULE. THE REST, IS JUST A USAGE EXAMPLE.'''
# vvvvvvvvvvvvvvvvvvvvv (Run the module directly, to watch) vvvvvvvvvvvvvvvvvvv

if __name__ == '__main__':
    from kivy.config import Config
    Config.set('modules', 'monitor', '')
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.floatlayout import FloatLayout

    Builder.load_string('''
<Root>:
    blue: blue
    red: red
    Rotabox:
        id: blue
        size: root.width * .6, root.height * .528
        center: root.width * .3, root.height * .5
        image: img
        custom_bounds: True
        bounds:
            [[[(0.225, 0.685), (0.222, 0.405), (0.353, 0.278),
            (0.356, 0.435), (0.53, 0.261), (0.665, 0.398), (0.849, 0.587),
            (0.515, 0.553), (0.386, 0.683), (0.384, 0.526)], [1, 3, 5, 7, 9]]]
        # draw_bounds: True
        Image:
            id: img
            source: 'data/logo/kivy-icon-256.png'
            color: 0, .3, .7, 1
    Rotabox:
        id: red
        size: root.width * .25, root.height * .22
        center: root.width * .8, root.height * .5
        ratio: 1.5
        custom_bounds: True
        bounds:
            [[[(0.013, 0.985), (0.016, 0.407), (0.202, 0.696)],
            [1, 2]],
            [[(0.267, 0.346), (0.483, -0.005), (0.691, 0.316),
            (0.261, 0.975)], [0, 2]],
            [[(0.539, 0.674), (0.73, 0.37), (0.983, 0.758)], [2, 0]],
            [[(0.033, 0.315), (0.212, 0.598), (0.218, 0.028)],
            [0, 2]]]
        draw_bounds: True
        Widget:
    ''')

    class Root(FloatLayout):

        def __init__(self, **kwargs):
            super(Root, self).__init__(**kwargs)
            self.clock = Clock.schedule_interval(self.update, 0)

        def update(self, *args):
            if (self.blue.collide_widget(self.red) or
                    self.red.collide_widget(self.blue)):
                self.blue.x -= 1
                self.red.x += 1
            else:
                self.blue.x += .5
                self.red.x -= .5
                self.blue.angle += .5
                self.red.angle -= .7

    class Example(App):

        def build(self):
            return Root()

    Example().run()
