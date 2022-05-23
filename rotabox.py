"""

ROTABOX                              python 2.7 kivy 1.10 / python 3.7 kivy 2.1
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

Open collision bounds (Segment method only)
    If a polygon is open, the segment between the last and first points of the
    polygon is not considered in the collision checks.
    Since the segment collision method is only concerned with the polygon's
    sides, a widget can 'enter' an open polygon, passing through the opening,
    and then hit the back wall from inside, for example.
    Note that *collide_point* doesn't work for an open polygon (i.e. an open
    polygon cannot be touched accurately).

Visual point tracking
    Since a rotating widget doesn't really rotate, its points lose their
    reference to its visual (Positional properties like [top] or [center] don't
    rotate).
    Rotabox can track any of its own points while rotating, provided that they
    are predefined (Hence, the custom bounds' ability).
    They then can be accessed using their indices.
    This can be useful, for example, in changing the point of rotation to a
    predefined point on the widget while the latter is rotating.

Touch interactivity
    Since, due to the differences between the Scatter and Rotabox concepts, a
    way to combine the two couldn't be found, Rotabox uses the Scatter widget's
    code, modified to act on the actual size and position of the widget and
    child (essential for accurate collision detection).
    It supports single and multitouch drag, rotation and scaling (the latter two
    use the *origin* property in the singletouch option).

Cython option
    Rotabox tries by default to use a compiled cython module (cybounds.so or
    cybounds.pyd) for an about X5 speedup.
    User needs to compile it for specific systems using the provided
    cybounds.c file.

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
    To use Rotabox, just include *rotabox_full.py* in your project files.

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
    To use it, run *rotaboxer.py* directly. It can be found in the
    *Visual Editor* folder, at the repository.
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

**segment_mode** *BooleanProperty* (True):
    Toggle between the two collision detection methods *(See Features above)*.

**open_bounds** *ListProperty*:
    If a polygon's index is in this list, the segment between the last and first
    points of the polygon is not considered in the collision checks
    (segment_mode only).

**pre_check** *BooleanProperty* (False):
    A collision optimization switch for larger widgets in Cython.
    For small widgets (under 45 points), the tax of extra calculations
    outweighs any benefit in collision.

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

**pivot** *ReferenceListProperty*
    The point of rotation and scaling.
    While *origin* property sets *pivot*'s position, relatively to widget's
    *size* and *pos*, *pivot* itself can be used to position the widget, much
    like *pos* or *center*.

**get_point(pol_index, point_index)** *Method*
    Returns the current position of a certain point.
    The argument indices are based on user's [custom_bounds]' structure.

**read_bounds(filename)** *Method*
    Define [custom_bounds] using a rotaboxer's project file (.bounds file).
    To work, [size] should be already defined.

**draw_bounds** *NumericProperty* (0)
    This option can be useful during testing, as it makes the widget's bounds
    visible. (1 for bounds, 2 for bounds & bounding boxes)

**scale** *AliasProperty*
    Current widget's scale.

**scale_min** *NumericProperty* (0.01)
**scale_max** *NumericProperty* (1e20)
    Optional scale restrictions.

**ready** *BooleanProperty* (False)
    Signifies the completion of the widget's initial preparations.
	Useful to read in cases where the widget is stationary.
    Also, its state changes to False when a size change or reset is triggered
    and back to True after said size change or reset.

**prepared** *BooleanProperty* (False)
    Its state change signifies a reset.
    The reset completion signal, however, is the consequent [ready] state change
    to True.


___________________________________________________________________________
A Rotabox example can be seen if this module is run directly.
"""

__author__ = 'unjuan'
__version__ = '0.13.0'

__all__ = ('Rotabox', )

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.graphics import PushMatrix, Rotate, PopMatrix
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import (NumericProperty, ReferenceListProperty,
                             AliasProperty, ObjectProperty, BooleanProperty,
                             ListProperty, BoundedNumericProperty, partial)
from math import radians, sin, cos
import json, sys

if sys.version_info < (3, 0):  # Python 2.x
    from codecs import open
    range = xrange
from future.utils import iteritems, itervalues

try:
    from cybounds import define_bounds, resize, aniresize, get_peers, \
        update_bounds, aniupdate_bounds, point_in_bounds, collide_bounds
    peers = get_peers()
except ImportError:
    import logging
    logging.log(30,  "[Rotabox     ] cybounds module NOT found. "
                     "Using internal functions instead.\n")

    from array import array
    peers = {}

    def scale(points, length, width, height):
        for h in range(0, length, 2):
            points[h] = points[h] * width
            points[h+1] = points[h+1] * height

    def move(points, length, pos0, pos1):
        for i in range(0, length, 2):
            points[i] = points[i] + pos0
            points[i+1] = points[i+1] + pos1

    def rotate(points, length, angle, orig0, orig1):
        c = cos(angle)
        s = sin(angle)

        for j in range(0, length, 2):
            points[j] = points[j] - orig0
            points[j+1] = points[j+1] - orig1
            pj = points[j]
            points[j] = pj * c - points[j+1] * s
            points[j+1] = pj * s + points[j+1] * c
            points[j] = points[j] + orig0
            points[j+1] = points[j+1] + orig1

    def calc_segboxes(points, polids, ptids, plens, length, bbox, blefts, bbotts,
                      brghts, btops):
        for k in range(0, length, 2):
            k1 = k + 1
            off = plens[polids[k]] * 2 - 2
            if ptids[k] < plens[polids[k]] - 1:
                k2 = k1 + 1
                k3 = k2 + 1
            else:
                k2 = k - off
                k3 = k2 + 1

            blefts[k] = points[k] if points[k] <= points[k2] else points[k2]
            bbotts[k] = points[k1] if points[k1] <= points[k3] else points[k3]
            brghts[k] = points[k] if points[k] >= points[k2] else points[k2]
            btops[k] = points[k1] if points[k1] >= points[k3] else points[k3]

            if blefts[k] < bbox[0]:
                bbox[0] = blefts[k]
            if brghts[k] > bbox[2]:
                bbox[2] = brghts[k]
            if bbotts[k] < bbox[1]:
                bbox[1] = bbotts[k]
            if btops[k] > bbox[3]:
                bbox[3] = btops[k]

    def calc_polboxes(points, plens, bbox, blefts, bbotts, brghts, btops):
        strt = 0
        for p in range(len(plens)):
            left = float("inf")
            bottom = float("inf")
            right = 0.
            top = 0.
            for l in range(strt, strt + plens[p] * 2, 2):
                l1 = l + 1

                if points[l] < left:
                    left = points[l]
                if points[l] > right:
                    right = points[l]
                if points[l1] < bottom:
                    bottom = points[l1]
                if points[l1] > top:
                    top = points[l1]

            if left < bbox[0]:
                bbox[0] = left
            if right > bbox[2]:
                bbox[2] = right
            if bottom < bbox[1]:
                bbox[1] = bottom
            if top > bbox[3]:
                bbox[3] = top

            blefts[p] = left
            bbotts[p] = bottom
            brghts[p] = right
            btops[p] = top

            strt = strt + plens[p] * 2

    def intersection_w(pts, ptids, plens, opens, t_box):
        t_pts = [t_box[0], t_box[1], t_box[2], t_box[1],
                 t_box[2], t_box[3], t_box[0], t_box[3]]
        o = 0
        strt = 0
        for p in range(len(plens)):
            if p in opens:
                o = 2
            for i in range(strt, strt + plens[p] * 2 - o, 2):
                i1 = i + 1
                off = plens[p] * 2 - 2
                if ptids[i] < plens[p] - 1:
                    i2 = i1 + 1
                    i3 = i2 + 1
                else:
                    i2 = i - off
                    i3 = i2 + 1
                v10 = pts[i]
                v11 = pts[i1]
                v20 = pts[i2]
                v21 = pts[i3]

                for j in range(0, 8, 2):
                    j1 = j + 1
                    t_off = 6
                    if j < 6:
                        j2 = j1 + 1
                        j3 = j2 + 1
                    else:
                        j2 = j - t_off
                        j3 = j2 + 1
                    v30 = t_pts[j]
                    v31 = t_pts[j1]
                    v40 = t_pts[j2]
                    v41 = t_pts[j3]
                    # Segment intersection detection method:
                    # If the vertices v1 and v2 are not on opposite sides of the
                    # segment v3, v4, or the vertices v3 and v4 are not on
                    # opposite sides of the segment v1, v2, there's no
                    # intersection.
                    if (((v40 - v30) * (v11 - v31) -
                         (v10 - v30) * (v41 - v31) > 0) ==
                        ((v40 - v30) * (v21 - v31) -
                         (v20 - v30) * (v41 - v31) > 0)):
                        continue
                    elif (((v20 - v10) * (v31 - v11) -
                           (v30 - v10) * (v21 - v11) > 0) ==
                          ((v20 - v10) * (v41 - v11) -
                           (v40 - v10) * (v21 - v11) > 0)):
                        continue

                    return [p, ptids[i], 0, j/2]
            strt = strt + plens[p] * 2
        return False

    def intersection_f(pts, ptids, plens, opens, t_pts, t_polis, t_ptis, t_plens):
        o = 0
        strt = 0
        for p in range(len(plens)):
            if p in opens:
                o = 2
            for i in range(strt, strt + plens[p] * 2 - o, 2):
                i1 = i + 1
                off = plens[p] * 2 - 2
                if ptids[i] < plens[p] - 1:
                    i2 = i1 + 1
                    i3 = i2 + 1
                else:
                    i2 = i - off
                    i3 = i2 + 1
                v10 = pts[i]
                v11 = pts[i1]
                v20 = pts[i2]
                v21 = pts[i3]

                t_strt = 0
                for t_p in range(len(t_plens)):
                    for j in range(t_strt, t_strt + t_plens[t_p] * 2, 2):
                        j1 = j + 1
                        t_off = t_plens[t_polis[j]] * 2 - 2
                        if t_ptis[j] < t_plens[t_polis[j]] - 1:
                            j2 = j1 + 1
                            j3 = j2 + 1
                        else:
                            j2 = j - t_off
                            j3 = j2 + 1
                        v30 = t_pts[j]
                        v31 = t_pts[j1]
                        v40 = t_pts[j2]
                        v41 = t_pts[j3]
                        # Segment intersection detection method:
                        # If the vertices v1 and v2 are not on opposite sides of
                        # the segment v3, v4, or the vertices v3 and v4 are not
                        # on opposite sides of the segment v1, v2, there's no
                        # intersection.
                        if (((v40 - v30) * (v11 - v31) -
                             (v10 - v30) * (v41 - v31) > 0) ==
                            ((v40 - v30) * (v21 - v31) -
                             (v20 - v30) * (v41 - v31) > 0)):
                            continue
                        elif (((v20 - v10) * (v31 - v11) -
                               (v30 - v10) * (v21 - v11) > 0) ==
                              ((v20 - v10) * (v41 - v11) -
                               (v40 - v10) * (v21 - v11) > 0)):
                            continue

                        return [p, ptids[i], t_p, t_ptis[j]]
                    t_strt = t_strt + t_plens[t_p] * 2
            strt = strt + plens[p] * 2
        return False

    def intersection(pts, ptids, le, plens, opens, lefts, botts, rghts, tops,
                     t_box, t_pts, t_ptis, t_le, t_plens, t_opens, t_lefts,
                     t_botts, t_rghts, t_tops):
        o = 0
        t_o = 0
        strt = 0
        for p in range(len(plens)):
            if p in opens:
                o = 2
            for i in range(strt, strt + plens[p] * 2 - o, 2):
                if rghts[i] < t_box[0]:
                    continue
                if lefts[i] > t_box[2]:
                    continue
                if tops[i] < t_box[1]:
                    continue
                if botts[i] > t_box[3]:
                    continue
                i1 = i + 1
                off = plens[p] * 2 - 2
                if ptids[i] < plens[p] - 1:
                    i2 = (i1 + 1) % le
                    i3 = i2 + 1
                else:
                    i2 = i - off
                    i3 = i2 + 1
                v10 = pts[i]
                v11 = pts[i1]
                v20 = pts[i2]
                v21 = pts[i3]

                t_strt = 0
                for t_p in range(len(t_plens)):
                    if t_p in t_opens:
                        t_o = 2
                    for j in range(t_strt, t_strt + t_plens[t_p] * 2 - t_o, 2):
                        if rghts[i] < t_lefts[j]:
                            continue
                        if lefts[i] > t_rghts[j]:
                            continue
                        if tops[i] < t_botts[j]:
                            continue
                        if botts[i] > t_tops[j]:
                            continue
                        j1 = j + 1
                        t_off = t_plens[t_p] * 2 - 2
                        if t_ptis[j] < t_plens[t_p] - 1:
                            j2 = (j1+1) % t_le
                            j3 = j2 + 1
                        else:
                            j2 = j - t_off
                            j3 = j2 + 1
                        v30 = t_pts[j]
                        v31 = t_pts[j1]
                        v40 = t_pts[j2]
                        v41 = t_pts[j3]
                        # Segment intersection detection method:
                        # If the vertices v1 and v2 are not on opposite sides of
                        # the segment v3, v4, or the vertices v3 and v4 are not
                        # on opposite sides of the segment v1, v2, there's no
                        # intersection.
                        if (((v40 - v30) * (v11 - v31) -
                             (v10 - v30) * (v41 - v31) > 0) ==
                            ((v40 - v30) * (v21 - v31) -
                             (v20 - v30) * (v41 - v31) > 0)):
                            continue
                        elif (((v20 - v10) * (v31 - v11) -
                               (v30 - v10) * (v21 - v11) > 0) ==
                              ((v20 - v10) * (v41 - v11) -
                               (v40 - v10) * (v21 - v11) > 0)):
                            continue

                        return [p, ptids[i], t_p, t_ptis[j]]
                    t_strt = t_strt + t_plens[t_p] * 2
            strt = strt + plens[p] * 2
        return False

    def membership(pts, plens, lefts, botts, rghts, tops,
                   t_box, t_pts, t_polis, t_le):
        strt = 0
        for p, pl in enumerate(plens):
            # Preliminary 1: pol's bbox vs widget's bbox.
            if rghts[p] < t_box[0]:
                strt = strt + pl * 2
                continue
            if lefts[p] > t_box[2]:
                strt = strt + pl * 2
                continue
            if tops[p] < t_box[1]:
                strt = strt + pl * 2
                continue
            if botts[p] > t_box[3]:
                strt = strt + pl * 2
                continue

            for k in range(0, t_le, 2):
                x = t_pts[k]
                y = t_pts[k + 1]
                # Preliminary 2: pol's bbox vs widget's points to filter out.
                if rghts[p] < x:
                    continue
                if lefts[p] > x:
                    continue
                if tops[p] < y:
                    continue
                if botts[p] > y:
                    continue
                # Point-in-polygon (oddeven) collision detection method:
                # Checking the membership of each poby assuming a ray at 0 angle
                # from that poto infinity (through window right) and counting
                # the number of times that this ray crosses the polygon line.
                # If this number is odd, the pois inside; if it's even, the pois
                # outside.
                c = 0
                j = strt + pl * 2 - 2
                for i in range(strt, strt + pl * 2, 2):
                    x1 = pts[j]
                    y1 = pts[j+1]
                    x2 = pts[i]
                    y2 = pts[i+1]
                    if (((y2 > y) != (y1 > y))
                            and x < (x1 - x2) * (y - y2) / (y1 - y2) + x2):
                        c = not c
                    j = i
                if c:
                    return [p, t_polis[k]]
            strt = strt + pl * 2
        return False

    def collide_bounds(rid, wid, frame='bounds', tframe='bounds'):

        try:
            this_box = peers[rid]['bbox']
        except KeyError:
            return False

        try:
            that_box = peers[wid]['bbox']
        except TypeError:
            that_box = wid

        try:
            if this_box[2] < that_box[0]:
                return False
        except IndexError:
            return False
        if this_box[0] > that_box[2]:
            return False
        if this_box[3] < that_box[1]:
            return False
        if this_box[1] > that_box[3]:
            return False

        bounds = peers[rid][frame]
        try:
            tbounds = peers[wid][tframe]
        except TypeError:
            return intersection_w(bounds['points'], bounds['pt_ids'],
                                  bounds['pol_lens'], bounds['opens'], that_box)

        if peers[rid]['seg']:
            if peers[wid]['seg']:
                return intersection(bounds['points'], bounds['pt_ids'],
                                    bounds['length'], bounds['pol_lens'],
                                    bounds['opens'], bounds['lefts'],
                                    bounds['botts'], bounds['rights'],
                                    bounds['tops'], that_box,
                                    tbounds['points'], tbounds['pt_ids'],
                                    tbounds['length'], tbounds['pol_lens'],
                                    tbounds['opens'], tbounds['lefts'],
                                    tbounds['botts'], tbounds['rights'],
                                    tbounds['tops'])
            else:
                return intersection_f(bounds['points'], bounds['pt_ids'],
                                      bounds['pol_lens'], bounds['opens'],
                                      tbounds['points'], tbounds['pol_ids'],
                                      tbounds['pt_ids'], tbounds['pol_lens'])
        else:
            return membership(bounds['points'], bounds['pol_lens'],
                              bounds['lefts'], bounds['botts'], bounds['rights'],
                              bounds['tops'], that_box, tbounds['points'],
                              tbounds['pol_ids'],
                              tbounds['length'])

    def point_in_bounds(x, y, rid, frame='bounds'):
            '''"Oddeven" point-in-polygon method:
            Checking the membership of touch poby assuming a ray at 0 angle
            from that poto infinity (through window right) and counting the
            number of polygon sides that this ray crosses. If this number is
            odd, the pois inside; if it's even, the pois outside.
            '''
            bounds = peers[rid][frame]
            strt = 0
            for r, rang in enumerate(bounds['pol_lens']):
                c = 0
                j = strt + rang * 2 - 2
                for i in range(strt, strt + rang * 2, 2):
                    x1, y1 = bounds['points'][j], bounds['points'][j+1]
                    x2, y2 = bounds['points'][i], bounds['points'][i+1]
                    if (((y2 > y) != (y1 > y)) and
                            x < (x1 - x2) * (y - y2) / (y1 - y2) + x2):
                        c = not c
                    j = i
                if c:
                    return c
                strt = strt + rang * 2
            return False

    def update_bounds(motion, angle, origin, rid, frame='bounds'):
        '''Updating the elements of the collision detection checks.
        '''
        try:
            bounds = peers[rid][frame]
        except TypeError:
            return

        if motion:
            move(bounds['points'], bounds['length'], motion[0], motion[1])

        if angle:
            rotate(bounds['points'], bounds['length'], angle, origin[0],
                   origin[1])

        bbox = array('d', [float("inf"), float("inf"), 0., 0.])

        if peers[rid]['seg']:
            calc_segboxes(bounds['points'], bounds['pol_ids'], bounds['pt_ids'],
                          bounds['pol_lens'], bounds['length'], bbox,
                          bounds['lefts'], bounds['botts'], bounds['rights'],
                          bounds['tops'])
        else:
            calc_polboxes(bounds['points'], bounds['pol_lens'], bbox,
                          bounds['lefts'], bounds['botts'], bounds['rights'],
                          bounds['tops'])

        peers[rid]['bbox'] = bbox

    def aniupdate_bounds(motion, pos, angle, origin, rid, frame='bounds'):
        '''Updating the elements of the collision detection checks,
        in case of an animation.
        '''
        try:
            bounds = peers[rid][frame]
        except TypeError:
            return

        if motion:
            bounds['mov_pts'][:] = bounds['sca_pts']
            move(bounds['mov_pts'], bounds['length'], pos[0], pos[1])
            bounds['points'][:] = bounds['mov_pts']

        if angle:
            bounds['points'][:] = bounds['mov_pts']
            rotate(bounds['points'], bounds['length'], angle, origin[0],
                   origin[1])

        bbox = array('d', [float("inf"), float("inf"), 0., 0.])

        if peers[rid]['seg']:
            calc_segboxes(bounds['points'], bounds['pol_ids'], bounds['pt_ids'],
                          bounds['pol_lens'], bounds['length'], bbox,
                          bounds['lefts'], bounds['botts'], bounds['rights'],
                          bounds['tops'])
        else:
                calc_polboxes(bounds['points'], bounds['pol_lens'], bbox,
                              bounds['lefts'], bounds['botts'], bounds['rights'],
                              bounds['tops'])

        peers[rid]['bbox'] = bbox

    def resize(width, height, rid):
        for k, frame in iteritems(peers[rid]):
            if k == 'bounds':
                bounds = peers[rid]['bounds']
                bounds['points'][:] = bounds['hints']
                scale(bounds['points'], bounds['length'], width, height)
                break
        else:
            for k, frame in iteritems(peers[rid]):
                if k != 'bbox' and k != 'vbbox' and k != 'hhits' and k != 'seg' \
                        and k != 'friendly':
                    frame['points'][:] = frame['hints']
                    scale(frame['points'], frame['length'], width, height)

    def aniresize(width, height, rid):
        for k, frame in iteritems(peers[rid]):
            if k == 'bounds':
                bounds = peers[rid]['bounds']
                bounds['sca_pts'][:] = bounds['hints']
                scale(bounds['sca_pts'], bounds['length'], width, height)
                break
        else:
            for k, frame in iteritems(peers[rid]):
                if k != 'bbox' and k != 'seg' and k != '':
                    frame['sca_pts'][:] = frame['hints']
                    scale(frame['sca_pts'], frame['length'], width, height)

    def define_frame(frame, opens, seg_mode, bounds, ani=False):
        for p in range(len(frame)):
            pol = frame[p]
            plen = len(pol)
            array.extend(bounds['pol_lens'], array('i', [plen]))
            for i in range(plen):
                array.extend(bounds['hints'], array('d', [pol[i][0], pol[i][1]]))
                array.extend(bounds['pol_ids'], array('i', [p, p]))
                array.extend(bounds['pt_ids'], array('i', [i, i]))
                bounds['length'] += 2

        if seg_mode:
            length = bounds['length']
        else:
            length = len(bounds['pol_lens'])
        bounds['lefts'] = array('d', [float("inf")] * length)
        bounds['botts'] = array('d', [float("inf")] * length)
        bounds['rights'] = array('d', [0.] * length)
        bounds['tops'] = array('d', [0.] * length)

        if seg_mode:
            bounds['opens'] = array('i', opens)

        if ani:
            bounds['mov_pts'][:] = bounds['sca_pts'][:] = bounds['hints']
        bounds['points'][:] = bounds['hints']

    def define_bounds(custom_bounds, open_bounds, segment_mode, rid, pc):
        '''Organising the data from the user's [self.custom_bounds] hints.
        The [pc] parameter is not used. It's here for compatibility with the
        equivalent function in the cython module.
        '''
        frames = {}

        if isinstance(custom_bounds, dict):   # Animation case
            for key, frame in iteritems(custom_bounds):
                bounds = {'hints': array('d'), 'sca_pts': array('d'),
                          'mov_pts': array('d'), 'points': array('d'),
                          'pol_ids': array('i'), 'pt_ids': array('i'),
                          'pol_lens': array('i'), 'length': 0}
                if isinstance(open_bounds, dict):
                    opens = array('i', open_bounds[key])
                else:
                    opens = array('i', open_bounds)

                define_frame(frame, opens, segment_mode, bounds, ani=True)

                frames[key] = bounds

        elif isinstance(custom_bounds, list):  # Single image case
            bounds = {'hints': array('d'), 'points': array('d'),
                      'pol_ids': array('i'), 'pt_ids': array('i'),
                      'pol_lens': array('i'), 'length': 0}
            define_frame(custom_bounds, open_bounds, segment_mode, bounds)

            frames['bounds'] = bounds

        frames['bbox'] = array('d', [])
        frames['seg'] = segment_mode

        peers[rid] = frames


class Rotabox(Widget):
    '''See module's documentation.'''

    __events__ = ('on_transform_with_touch', 'on_touched_to_front')

    # -------------------------------------------------------- VISUAL INTERFACE
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
        angle = -radians(self.last_angle)
        orig = self.origin
        s = sin(angle)
        c = cos(angle)

        # normalize (translate point so origin will be 0,0)
        dx = point[0] - orig[0]
        dy = point[1] - orig[1]

        # un-rotate point
        xnew = dx * c - dy * s
        ynew = dx * s + dy * c

        # translate point back:
        pivot = xnew + orig[0], ynew + orig[1]

        # lock pos-pivot relation
        self.pivot_bond = [(pivot[0] - self.x) / float(self.width),
                           (pivot[1] - self.y) / float(self.height)]

        # Since the image (on canvas) always starts each frame in zero angle,
        # an [origin] change in any non-zero angle breaks the continuity of
        # motion/rotation, introducing an image translation (jump).
        # compensating by changing the widget's position.

        # prevent a bounds' update to [pos] change below.
        self.allow = 0

        # compensating for image translation
        self.pos = (self.x - (pivot[0] - point[0]),
                    self.y - (pivot[1] - point[1]))

        # cannot wait for the triggered [update], at the end of this frame,
        # since it might concern other changes that require a bounds' update.
        self.update()

    '''Sets the point of rotation. Default value is the widget's center.
    Works nicely with the [get_point] method below and points already defined in
    [custom_bounds].'''
    origin = AliasProperty(get_origin, set_origin)

    # ----------------------------------------------------- COLLISION INTERFACE
    '''Enables widget's advanced collision detection. If False, widget will
    collide as a normal (non-Rotabox) widget.'''
    allow_rotabox = BooleanProperty(True)

    '''Custom bounds' definition interface. (See module's documentation).'''
    custom_bounds = ObjectProperty([[(0., 0.), (1., 0.), (1., 1.), (0., 1.)]])

    '''Collision detection method switch (see documentation above).'''
    segment_mode = BooleanProperty(True)

    '''(segment_mode) If a polygon's index is in this list, the segment
    between the last and first points of the polygon is not considered in the
    collision checks.'''
    open_bounds = ListProperty()

    '''(Cython) A collision optimization switch for larger widgets (45+ points).
    It's always True in Python but in Cython, for small widgets, the slight tax 
    in updating the bounds outweighs the benefit in collision.'''
    pre_check = BooleanProperty(False)

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

    '''If touched, widget will be pushed to the top of parent widget tree.'''
    touched_to_front = BooleanProperty(False)

    '''If True, limiting the touch inside the bounds will be done after
    dispaching the touch to the child and grandchildren, so even outside the
    bounds they can still be touched.
    IMPORTANT NOTE: Grandchildren, inside or outside the bounds, can collide
        independently ONLY if widget is NOT ROTATED ([angle] must be 0).'''
    collide_after_children = BooleanProperty(False)

    # ------------------------------------------------------- UTILITY INTERFACE
    def get_point(self, pol_index, point_index):
        '''Access a point's current position, based on [custom_bounds] structure.'''
        bounds = peers[self.rid][self.curr_key]
        index = (sum(bounds['pol_lens'][:pol_index]) + point_index) * 2
        return list(bounds['points'][index:index + 2])

    def read_bounds(self, filename, delayed=False, *args):
        '''
        Define [custom_bounds] using a rotaboxer's project file.
        To work, [size] should be already defined.
        '''
        if not self.prepared:
            Clock.schedule_once(partial(self.read_bounds, filename, True))
            return self.custom_bounds
        try:
            with open(filename, 'r', encoding="UTF8") as proj:
                project = json.load(proj)
        except (IOError, KeyError) as er:
            print('On read_bounds: ', er)
        else:
            bounds = {}
            opens = []
            for f, frame in iteritems(project):
                if f in ('image', 'version'):
                    continue
                pols = []
                i = 0
                while i < len(frame):
                    for pol in itervalues(frame):
                        if pol['number'] == i:
                            pols.append(pol)
                            break
                    i += 1
                bounds[f] = []
                for p, pol in enumerate(pols):
                    try:
                        if pol['open']:
                            opens.append(p)
                    except KeyError:
                        pass
                    bounds[f].append([(round(float(point[0]) / self.width, 3),
                                       round(float(point[1]) / self.height, 3))
                                      for point in pol['points']])
            blen = len(bounds)
            if blen:
                if opens:
                    self.open_bounds = opens
                if blen == 1:
                    bounds = bounds[list(bounds.keys())[0]]
                if delayed:
                    self.custom_bounds = bounds
                    return
                return bounds
            else:
                return self.custom_bounds

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
    While [origin] property sets [pivot]'s relation to widget, [pivot]
    itself can be used to position the widget, much like [pos] or [center].'''
    pivot = ReferenceListProperty(pivot_x, pivot_y)

    '''Signifies the completion of the widget's initial preparations.
    Also, its state changes to False when a size change or reset is triggered 
    and back to True after said size change or reset.'''
    ready = BooleanProperty(False)

    '''Its state change signifies a reset. The reset completion signal, however,
    is the consequent [ready] state change to True.'''
    prepared = BooleanProperty(False)

    '''Enables bounds visualization (for testing).'''
    draw_bounds = NumericProperty(0)

    def __init__(self, **kwargs):
        self.size = [1, 1]
        self.temp_piv_x = self.temp_piv_y = 0
        self.initial_scale = 0
        self.touches = []
        self.last_touch_pos = {}
        self.trigger_update = Clock.create_trigger(self.update, -1)
        self.trigger_draw = Clock.create_trigger(self.draw, -1)
        super(Rotabox, self).__init__(**kwargs)
        self.sized_by_img = False
        self.ratio = 1
        self.last_pos = [0, 0]
        self.last_size = self.size[:]
        self.last_angle = 0
        self.anim = False
        self.rid = 0
        self.curr_key = 'bounds'
        self.draw_color = Color(0.29, 0.518, 1, 1)
        self.box_color = Color(0.35, 0.15, 0, 1)
        self.draw_lines = ()
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
                  allow_rotabox=self.on_reset,
                  draw_bounds=self.on_reset)

    def add_widget(self, widget, **kwargs):
        '''Birth control.'''
        if self.children:
            raise Exception('Rotabox can only have one child.')
        super(Rotabox, self).add_widget(widget)

    def on_size(self, *args):
        '''Enables the ON SIZE section of the [update] method.'''
        self.ready = False
        self.trigger_update()

    def on_reset(self, *args):
        '''Enables bounds reset.'''
        self.ready = False
        self.prepared = False  # This needs to be second
        self.trigger_update()

    def on_open_bounds(self, *args):
        if self.open_bounds and not self.segment_mode:
            raise Exception('Open bounds are only applicable in Segment mode.')

    def prepare(self):
        '''Initial preparations.'''
        tempscale = self.initial_scale
        if not self.image:
            # Trying to auto-assign [image] property if not specified.
            self.image = self.locate_images()
        if self.image:
            try:
                self.image.texture.mag_filter = 'nearest'
            except AttributeError:
                pass
            self.image.allow_stretch = True
            # In case of a stationary widget with animated bounds.
            self.image.bind(source=self.trigger_update)

            # Calculating widget's size from available inputs.
            if (not (self.width - tempscale > 1 or self.height - tempscale > 1)
                    or self.sized_by_img):
                try:
                    self.original_size = self.image.texture.size
                except AttributeError:  # If animation, texture not ready (?)
                    self.original_size = self.image.size

                if not tempscale:
                    tempscale = 1
                self.size = [self.original_size[0] * tempscale,
                             self.original_size[1] * tempscale]
                if self.sized_by_img:
                    dw = self.width - self.last_size[0]
                    dh = self.height - self.last_size[1]
                    self.pivot = (self.pivot_x - dw * .5,
                                  self.pivot_y - dh * .5)
                self.sized_by_img = True
            else:
                self.original_size = self.size[:]
                if tempscale:
                    self.size = [self.size[0] * tempscale,
                                 self.size[1] * tempscale]
        else:
            self.original_size = self.size[:]
            if not tempscale:
                tempscale = 1
            self.size = [self.size[0] * tempscale,
                         self.size[1] * tempscale]

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
            # Generating a unique key for each instance
            try:
                self.rid = sorted(peers.keys())[-1] + 1
            except IndexError:
                pass
            if isinstance(self.custom_bounds, dict):
                self.curr_key = self.image.source.split('/')[-1]
                self.anim = True
            # Building widget's bounds.
            define_bounds(self.custom_bounds, self.open_bounds,
                          self.segment_mode, self.rid, self.pre_check)
            # Setting up canvas and triggers for test drawing
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
            if not self.anim:
                resize(self.width, self.height, self.rid)
                update_bounds(self.pos, radians(self.angle), self.origin,
                              self.rid, self.curr_key)
                self.allow = 0
            else:
                aniresize(self.width, self.height, self.rid)

        if self.children:
            # Adjusting the child's size to fit widget's
            self.children[0].size = self.size

        self.last_size = self.size[:]
        self.trigger_update()

    def update(self, *args):
        '''Updates the widget's angle, point of rotation, bounds and child's
        position.
        Also runs the [update_size] method on size change and the [prepare]
        method initially and on reset.
        '''

        if self.ready:
            self.angle %= 360
            angle = self.angle
            pos = self.pos

            # Updating the rotation instruction, in canvas.before
            self.rotation.origin = self.origin
            self.rotation.angle = angle

            # Updating the child's position
            if self.children:
                self.children[0].pos = pos

            motion = [pos[0] - self.last_pos[0], pos[1] - self.last_pos[1]]
            if abs(motion[0]) < .01 and abs(motion[1]) < .01:
                motion = []
            self.last_pos = pos[:]

            angle_diff = angle - self.last_angle
            if abs(angle_diff) < .01:
                angle_diff = 0
            self.last_angle = angle

            if not self.allow:
                self.allow = 1
                return

            if self.allow_rotabox:
                # Updating the custom bounds
                if self.anim:
                    # An identically keyed atlas file is assumed.
                    self.curr_key = self.image.source.split('/')[-1]
                    aniupdate_bounds(True, pos, radians(angle),
                                     self.origin, self.rid, self.curr_key)
                    return

                if motion or angle_diff:
                    update_bounds(motion, radians(angle_diff), self.origin,
                                  self.rid, self.curr_key)
        elif not self.prepared:
            self.prepare()
            self.prepared = True
        else:
            self.update_size()
            self.ready = True

    def collide_point(self, x=0, y=0):
        if self.allow_rotabox:
            return point_in_bounds(x, y, self.rid, frame=self.curr_key)
        else:
            return super(Rotabox, self).collide_point(x, y)

    def collide_widget(self, wid):
        try:
            try:
                return collide_bounds(self.rid, wid.rid, frame=self.curr_key,
                                      tframe=wid.curr_key)
            except AttributeError:
                if self.segment_mode:
                    return collide_bounds(self.rid,
                                          [wid.x, wid.y, wid.right, wid.top],
                                          frame=self.curr_key)
                return super(Rotabox, self).collide_widget(wid)
        except KeyError:
            return False

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
                _scale = new_line.length() / old_line.length()
                self.scale *= _scale
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
            _scale = new_line.length() / old_line.length()
            self.scale *= _scale
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
    def locate_images(self):
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

        for child in self.children:
            the_one = find_img(child)
            if isinstance(child, Image):
                return child
        return the_one
    
    def set_draw(self):
        '''Setting up canvas for test-drawing the bounds.'''

        if self.anim:
            pols = max([len(frame)
                        for frame in itervalues(self.custom_bounds)])
            length = max([len(pol)
                          for pol in itervalues(self.custom_bounds)])
        else:
            pols = len(self.custom_bounds)
            length = peers[self.rid][self.curr_key]['length']

        for i in range(pols):
            if i not in self.open_bounds or not self.segment_mode:
                self.draw_lines += tuple([Line(close=True, dash_offset=3,
                                               dash_length=5)])
            else:
                self.draw_lines += tuple([Line(close=False, dash_offset=3,
                                               dash_length=5)])

        self.canvas.after.add(self.draw_color)
        for line in self.draw_lines:
            self.canvas.after.add(line)

        if self.draw_bounds > 1:
            if self.segment_mode:
                self.box_lines += tuple(Line(close=True,
                                             dash_offset=5,
                                             dash_length=3)
                                        for _ in range(length + 1))
            else:
                self.box_lines += tuple(Line(close=True,
                                             dash_offset=5,
                                             dash_length=3)
                                        for _ in range(pols + 1))
            self.box_lines[-1].dash_offset = 8
            self.box_lines[-1].dash_length = 5

            self.canvas.after.add(self.box_color)
            for line in self.box_lines:
                self.canvas.after.add(line)

        # Securing draw on a stationary widget.
        self.x += .001
        self.bind(children=self.trigger_draw,
                  parent=self.trigger_draw,
                  pos=self.trigger_draw,
                  pos_hint=self.trigger_draw,
                  angle=self.trigger_draw,
                  ready=self.trigger_draw)
        try:
            self.image.bind(source=self.trigger_draw)
        except AttributeError:
            pass

    def draw(self, *args):
        '''
        If [draw_bounds] is True, visualises the widget's bounds.
        For testing.
        '''
        if self.ready:
            try:
                bounds = peers[self.rid][self.curr_key]
            except KeyError:
                return
            start = 0
            for i, leng in enumerate(bounds['pol_lens']):
                self.draw_lines[i].points = [bounds['points'][j]
                                             for j in range(start,
                                                            start
                                                            + leng * 2)]
                if self.draw_bounds > 1 and not self.segment_mode:
                    try:
                        self.box_lines[i].points = [bounds['lefts'][i],
                                                    bounds['botts'][i],
                                                    bounds['rights'][i],
                                                    bounds['botts'][i],
                                                    bounds['rights'][i],
                                                    bounds['tops'][i],
                                                    bounds['lefts'][i],
                                                    bounds['tops'][i]]
                    except KeyError:
                        pass
                start += leng * 2

            if self.draw_bounds > 1 and self.segment_mode:
                try:
                    bounds['lefts']
                except KeyError:
                    pass
                else:
                    for j in range(bounds['length']/2):
                        self.box_lines[j].points = [bounds['lefts'][j*2],
                                                    bounds['botts'][j*2],
                                                    bounds['rights'][j*2],
                                                    bounds['botts'][j*2],
                                                    bounds['rights'][j*2],
                                                    bounds['tops'][j*2],
                                                    bounds['lefts'][j*2],
                                                    bounds['tops'][j*2]]
            if self.draw_bounds > 1:
                box = peers[self.rid]['bbox']
                try:
                    self.box_lines[-1].points = (box[0], box[1],
                                                 box[2], box[1],
                                                 box[2], box[3],
                                                 box[0], box[3])
                except IndexError:
                    pass

    # Locking size_hint property to None, None,
    # in order to keep intended aspect ratio (critical for custom bounds).
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

    # Switch to suspend bounds' update while repositioning, during an [origin]
    # change or a resize.
    allow = BooleanProperty(1)


if __name__ == '__main__':
    from kivy.base import runTouchApp

    class Root(Widget):
        def __init__(self, **kwargs):
            super(Root, self).__init__(**kwargs)
            self.square = Rotabox(pivot=[200, 300])
            self.square.add_widget(Image(source="examples/square.png"))
            self.add_widget(self.square)

            self.logo = Rotabox(pivot=[600, 300], custom_bounds=[
                            [(0.013, 0.985), (0.016, 0.407), (0.202, 0.696)],
                            [(0.033, 0.315), (0.212, 0.598), (0.218, 0.028)],
                            [(0.267, 0.346), (0.483, 0.000), (0.691, 0.316),
                             (0.261, 0.975)],
                            [(0.539, 0.674), (0.73, 0.37), (0.983, 0.758)]])
            self.logo.add_widget(Image(source="examples/kivy.png"))
            self.add_widget(self.logo)

            Clock.schedule_interval(self.update, 1/60.)

        def update(self, *args):
            this = self.square
            that = self.logo
            collision = this.collide_widget(that)

            if collision:
                this.x -= 1
                that.x += 1
            else:
                this.x += .5
                this.angle += .5
                that.x -= .5
                that.angle -= .6

    runTouchApp(Root())
