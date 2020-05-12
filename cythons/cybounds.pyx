#!python
#cython: boundscheck=False, initializedcheck=False, cdivision=True, wraparound=False

from libc.math cimport sin, cos
from cpython cimport array


cdef dict peers = {}


# ______________________________________________________________________ UPDATE
cdef scale(double[::1] points, int length, double width, double height):
    cdef Py_ssize_t i

    for i in range(0, length, 2):
        points[i] = points[i] * width
        points[i+1] = points[i+1] * height


cdef move(double[::1] points, int length, double pos0, double pos1):
    cdef Py_ssize_t i
    for i in range(0, length, 2):
        points[i] = points[i] + pos0
        points[i+1] = points[i+1] + pos1


cdef rotate(double[::1] points, int length, double angle,
            double orig0, double orig1):
    cdef double ptsi, c = cos(angle), s = sin(angle)
    cdef Py_ssize_t i

    for i in range(0, length, 2):
        points[i] = points[i] - orig0
        points[i+1] = points[i+1] - orig1
        ptsi = points[i]
        points[i] = ptsi * c - points[i+1] * s
        points[i+1] = ptsi * s + points[i+1] * c
        points[i] = points[i] + orig0
        points[i+1] = points[i+1] + orig1


cdef calc_bbox(double[::1] points, int length, double[::1] bbox):
    cdef Py_ssize_t i, h
    cdef double ipt, i1pt

    for i in range(0, length, 2):
        ipt = points[i]
        i1pt = points[i+1]

        if ipt < bbox[0]:
            bbox[0] = ipt
        if ipt > bbox[2]:
            bbox[2] = ipt
        if i1pt < bbox[1]:
            bbox[1] = i1pt
        if i1pt > bbox[3]:
            bbox[3] = i1pt


cdef calc_segboxes(double[::1] points, Py_ssize_t[::1] polids,
                   Py_ssize_t[::1] ptids, int[::1] plens, int length,
                   double[::1] bbox,
                   double[::1] blefts, double[::1] bbotts,
                   double[::1] brghts, double[::1] btops):
    cdef Py_ssize_t i
    cdef double ipt, i1pt, i2pt, i3pt
    cdef int wrap

    for i in range(0, length, 2):
        ipt = points[i]
        i1pt = points[i+1]
        wrap = plens[polids[i]] * 2 - 2
        if ptids[i] < plens[polids[i]] - 1:
            i2pt = points[i+2]
            i3pt = points[i+3]
        else:
            i2pt = points[i-wrap]
            i3pt = points[i-wrap+1]

        blefts[i] = ipt if ipt <= i2pt else i2pt
        bbotts[i] = i1pt if i1pt <= i3pt else i3pt
        brghts[i] = ipt if ipt >= i2pt else i2pt
        btops[i] = i1pt if i1pt >= i3pt else i3pt

        if blefts[i] < bbox[0]:
            bbox[0] = blefts[i]
        if brghts[i] > bbox[2]:
            bbox[2] = brghts[i]
        if bbotts[i] < bbox[1]:
            bbox[1] = bbotts[i]
        if btops[i] > bbox[3]:
            bbox[3] = btops[i]


cdef calc_polboxes(double[::1] points, int[::1] plens, double[::1] bbox,
                   double[::1] blefts, double[::1] bbotts,
                   double[::1] brghts, double[::1] btops):
    cdef Py_ssize_t i, strt = 0
    cdef double left, bottom, right, top, ipt, i1pt

    for p in range(len(plens)):
        left = float("inf")
        bottom = float("inf")
        right = 0.
        top = 0.
        for i in range(strt, strt + plens[p] * 2, 2):
            ipt = points[i]
            i1pt = points[i+1]

            if ipt < left:
                left = ipt
            if ipt > right:
                right = ipt
            if i1pt < bottom:
                bottom = i1pt
            if i1pt > top:
                top = i1pt

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


# ________________________________________________________________ INTERSECTION
cdef intersection(double[::1] pts, Py_ssize_t[::1] ptids, int[::1] plens,
                  Py_ssize_t[::1] opens,
                  double[::1] t_pts, Py_ssize_t[::1] t_ptis, int[::1] t_plens,
                  Py_ssize_t[::1] t_opens):

    cdef Py_ssize_t k, i, i1, i2, i3, j, j1, j2, j3, p, t_p, \
        t_strt, strt, o = 0, t_o = 0
    cdef double v10, v11, v20, v21, v30, v31, v40, v41
    cdef int pl, tpl, wrap, t_wrap

    strt = 0
    for p in range(len(plens)):
        for k in range(len(opens)):
            if opens[k] == p:
                o = 2
                break
        pl = plens[p]
        wrap = pl * 2 - 2
        for i in range(strt, strt + pl * 2 - o, 2):
            i1 = i + 1
            if ptids[i] < pl - 1:
                i2 = i1 + 1
                i3 = i2 + 1
            else:
                i2 = i - wrap
                i3 = i2 + 1
            v10 = pts[i]
            v11 = pts[i1]
            v20 = pts[i2]
            v21 = pts[i3]

            t_strt = 0
            for t_p in range(len(t_plens)):
                for l in range(len(t_opens)):
                    if t_opens[l] == t_p:
                        t_o = 2
                        break
                tpl = t_plens[t_p]
                t_wrap = tpl * 2 - 2
                for j in range(t_strt, t_strt + tpl * 2 - t_o, 2):
                    j1 = j + 1
                    if t_ptis[j] < tpl - 1:
                        j2 = j1 + 1
                        j3 = j2 + 1
                    else:
                        j2 = j - t_wrap
                        j3 = j2 + 1
                    v30 = t_pts[j]
                    v31 = t_pts[j1]
                    v40 = t_pts[j2]
                    v41 = t_pts[j3]
                    # Segment intersection detection method:
                    # If the vertices v1 and v2 are not on opposite sides of the
                    # segment v3, v4, or the vertices v3 and v4 are not on opposite
                    # sides of the segment v1, v2, there's no intersection.
                    if (((v40 - v30) * (v11 - v31)
                         - (v10 - v30) * (v41 - v31) > 0)
                            == ((v40 - v30) * (v21 - v31)
                                - (v20 - v30) * (v41 - v31) > 0)):
                        continue
                    elif (((v20 - v10) * (v31 - v11)
                           - (v30 - v10) * (v21 - v11) > 0)
                              == ((v20 - v10) * (v41 - v11)
                                  - (v40 - v10) * (v21 - v11) > 0)):
                        continue

                    return [p, ptids[i], t_p, t_ptis[j]]
                t_strt = t_strt + tpl * 2
        strt = strt + pl * 2
    return False


cdef intersection_pc(double[::1] pts, Py_ssize_t[::1] ptids, int le,
                     int[::1] plens, Py_ssize_t[::1] opens, double[::1] lefts,
                     double[::1] botts, double[::1] rghts, double[::1] tops,
                     double[::1] t_box, double[::1] t_pts,
                     Py_ssize_t[::1] t_ptis, int t_le, int[::1] t_plens,
                     Py_ssize_t[::1] t_opens, double[::1] t_lefts,
                     double[::1] t_botts, double[::1] t_rghts,
                     double[::1] t_tops):

    cdef Py_ssize_t p, k, i, i1, i2, i3, j, j1, j2, j3, t_strt, \
                    strt, o = 0, t_o = 0
    cdef double v10, v11, v20, v21, v30, v31, v40, v41
    cdef int pl, tpl, wrap, t_wrap

    strt = 0
    for p in range(len(plens)):
        for k in range(len(opens)):
            if opens[k] == p:
                o = 2
                break
        pl = plens[p]
        wrap = pl * 2 - 2
        for i in range(strt, strt + pl * 2 - o, 2):
            if rghts[i] < t_box[0]:
                continue
            if lefts[i] > t_box[2]:
                continue
            if tops[i] < t_box[1]:
                continue
            if botts[i] > t_box[3]:
                continue
            i1 = i + 1
            if ptids[i] < pl - 1:
                i2 = (i1 + 1) % le
                i3 = i2 + 1
            else:
                i2 = i - wrap
                i3 = i2 + 1
            v10 = pts[i]
            v11 = pts[i1]
            v20 = pts[i2]
            v21 = pts[i3]

            t_strt = 0
            for t_p in range(len(t_plens)):
                for l in range(len(t_opens)):
                    if t_opens[l] == t_p:
                        t_o = 2
                        break
                tpl = t_plens[t_p]
                t_wrap = tpl * 2 - 2
                for j in range(t_strt, t_strt + tpl * 2 - t_o, 2):
                    if rghts[i] < t_lefts[j]:
                        continue
                    if lefts[i] > t_rghts[j]:
                        continue
                    if tops[i] < t_botts[j]:
                        continue
                    if botts[i] > t_tops[j]:
                        continue
                    j1 = j + 1
                    if t_ptis[j] < tpl - 1:
                        j2 = (j1+1) % t_le
                        j3 = j2 + 1
                    else:
                        j2 = j - t_wrap
                        j3 = j2 + 1
                    v30 = t_pts[j]
                    v31 = t_pts[j1]
                    v40 = t_pts[j2]
                    v41 = t_pts[j3]
                    # Segment intersection detection method:
                    # If the vertices v1 and v2 are not on opposite sides of the
                    # segment v3, v4, or the vertices v3 and v4 are not on opposite sides of
                    # the segment v1, v2, there's no intersection.
                    if (((v40 - v30) * (v11 - v31)
                         - (v10 - v30) * (v41 - v31) > 0)
                            == ((v40 - v30) * (v21 - v31)
                                - (v20 - v30) * (v41 - v31) > 0)):
                        continue
                    elif (((v20 - v10) * (v31
                          - v11) - (v30 - v10) * (v21 - v11) > 0)
                            == ((v20 - v10) * (v41 - v11)
                                - (v40 - v10) * (v21 - v11) > 0)):
                        continue

                    return [p, ptids[i], t_p, t_ptis[j]]

                t_strt = t_strt + tpl * 2
        strt = strt + pl * 2
    return False


def intersection_w(double[::1] pts, Py_ssize_t[::1] ptids, int[::1] plens,
                   Py_ssize_t[::1] opens, double[::1] t_box):
    cdef Py_ssize_t p, k, i, i1, i2, i3, j, j1, j2, j3, t_strt, o = 0
    cdef double v10, v11, v20, v21, v30, v31, v40, v41
    cdef int pl, wrap
    cdef double[::1] t_pts = array.array('d', [t_box[0], t_box[1], t_box[2],
                                               t_box[1], t_box[2], t_box[3],
                                               t_box[0], t_box[3]])
    o = 0
    strt = 0
    for p in range(len(plens)):
        for k in range(len(opens)):
            if opens[k] == p:
                o = 2
                break
        pl = plens[p]
        wrap = pl * 2 - 2
        for i in range(strt, strt + pl * 2 - o, 2):
            i1 = i + 1
            if ptids[i] < pl - 1:
                i2 = i1 + 1
                i3 = i2 + 1
            else:
                i2 = i - wrap
                i3 = i2 + 1
            v10 = pts[i]
            v11 = pts[i1]
            v20 = pts[i2]
            v21 = pts[i3]

            for j in range(0, 8, 2):
                j1 = j + 1
                if j < 6:
                    j2 = j1 + 1
                    j3 = j2 + 1
                else:
                    j2 = j - 6  # wrap
                    j3 = j2 + 1
                v30 = t_pts[j]
                v31 = t_pts[j1]
                v40 = t_pts[j2]
                v41 = t_pts[j3]
                # Segment intersection detection method:
                # If the vertices v1 and v2 are not on opposite sides of the
                # segment v3, v4, or the vertices v3 and v4 are not on opposite
                # sides of the segment v1, v2, there's no intersection.
                if (((v40 - v30) * (v11 - v31)
                     - (v10 - v30) * (v41 - v31) > 0)
                        == ((v40 - v30) * (v21 - v31)
                            - (v20 - v30) * (v41 - v31) > 0)):
                    continue
                elif (((v20 - v10) * (v31 - v11)
                       - (v30 - v10) * (v21 - v11) > 0)
                          == ((v20 - v10) * (v41 - v11)
                              - (v40 - v10) * (v21 - v11) > 0)):
                    continue

                return [p, ptids[i], 0, j/2]
        strt = strt + pl * 2
    return False


# __________________________________________________________________ MEMBERSHIP
cdef membership(double[::1] pts, int[::1] plens, double[::1] t_pts,
                int[::1] t_plens):
    '''
        Point-in-polygon (oddeven) collision detection method:
        Checking the membership of each point by assuming a ray at 0 angle
        from that point to infinity (through window right) and counting the
        number of times that this ray crosses the polygon line. If this number
        is odd, the point is inside; if it's even, the point is outside.
        Note that if the ray crosses a polygon's vertex, it will count both 
        concerned sides, giving an innacurate reading.
    '''
    cdef Py_ssize_t p, t_p, i, j, k, h, t_h, strt, t_strt
    cdef double x, y, x1, y1, x2, y2
    cdef int plx2
    cdef bint c

    strt = 0
    for p in range(len(plens)):
        plx2 = plens[p] * 2
        t_strt = 0
        for t_p in range(len(t_plens)):
            for k in range(t_strt, t_strt + t_plens[t_p] * 2, 2):
                x = t_pts[k]
                y = t_pts[k + 1]
                c = 0
                j = strt + plx2 - 2
                for i in range(strt, strt + plx2, 2):
                    x1 = pts[j]
                    y1 = pts[j + 1]
                    x2 = pts[i]
                    y2 = pts[i + 1]
                    if (((y2 > y) != (y1 > y))
                            and x < (x1 - x2) * (y - y2) / (y1 - y2) + x2):
                        c = not c
                    j = i
                if c:
                    return [p, t_p]
            t_strt = t_strt + t_plens[t_p] * 2
        strt = strt + plx2
    return False


cdef membership_pc(double[::1] pts, int[::1] plens, double[::1] lefts,
                   double[::1] botts, double[::1] rghts, double[::1] tops,
                   double[::1] t_box, double[::1] t_pts,
                   int[::1] t_plens):
    '''
        Point-in-polygon (oddeven) collision detection method:
        Checking the membership of each point by assuming a ray at 0 angle
        from that point to infinity (through window right) and counting the
        number of times that this ray crosses the polygon line. If this number
        is odd, the point is inside; if it's even, the point is outside.
        Note that if the ray crosses a polygon's vertex, it will count both 
        concerned sides, giving an innacurate reading.
    '''
    cdef Py_ssize_t p, t_p, i, j, k, h, t_h, strt, t_strt
    cdef double x, y, x1, y1, x2, y2
    cdef bint c

    strt = 0
    for p in range(len(plens)):
        # Preliminary 1: pol's bbox vs widget's bbox.
        plx2 = plens[p] * 2
        if rghts[p] < t_box[0]:
            strt = strt + plx2
            continue
        if lefts[p] > t_box[2]:
            strt = strt + plx2
            continue
        if tops[p] < t_box[1]:
            strt = strt + plx2
            continue
        if botts[p] > t_box[3]:
            strt = strt + plx2
            continue

        t_strt = 0
        for t_p in range(len(t_plens)):
            for k in range(t_strt, t_strt + t_plens[t_p] * 2, 2):
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
                # Main check:
                c = 0
                j = strt + plx2 - 2
                for i in range(strt, strt + plx2, 2):
                    x1 = pts[j]
                    y1 = pts[j+1]
                    x2 = pts[i]
                    y2 = pts[i+1]
                    if (((y2 > y) != (y1 > y))
                            and x < (x1 - x2) * (y - y2) / (y1 - y2) + x2):
                        c = not c
                    j = i
                if c:
                    return [p, t_p]
            t_strt = t_strt + t_plens[t_p] * 2
        strt = strt + plx2
    return False


# ______________________________________________________________________ CPDEFS
cpdef collide_bounds(rid, wid, frame='bounds', tframe='bounds'):
    '''
        Axis-aligned bounding box testing.
    '''
    this = peers[rid]
    this_box = this['bbox']
    try:
        that = peers[wid]
    except TypeError:
        wid = array.array('d', wid)
        that_box = wid
    else:
        that_box = that['bbox']

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

    bounds = this[frame]
    try:
        tbounds = that[tframe]
    except UnboundLocalError:
        return intersection_w(bounds['points'], bounds['pt_ids'],
                              bounds['pol_lens'], bounds['opens'], that_box)

    if this['seg']:
        if not (this['pre_check'] and that['pre_check'] and that['seg']):
            return intersection(bounds['points'], bounds['pt_ids'],
                                bounds['pol_lens'], bounds['opens'],
                                tbounds['points'], tbounds['pt_ids'],
                                tbounds['pol_lens'], tbounds['opens'])
        else:
            return intersection_pc(bounds['points'], bounds['pt_ids'],
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
        if not (this['pre_check'] and that['pre_check']):
            return membership(bounds['points'], bounds['pol_lens'],
                              tbounds['points'], tbounds['pol_lens'])
        else:
            return membership_pc(bounds['points'], bounds['pol_lens'],
                                 bounds['lefts'], bounds['botts'],
                                 bounds['rights'], bounds['tops'], that_box,
                                 tbounds['points'], tbounds['pol_lens'])


cpdef point_in_bounds(x, y, rid, frame='bounds'):
    '''"Oddeven" point-in-polygon method:
        Checking the membership of touch point by assuming a ray at 0 angle
        from that point to infinity (through window right) and counting the
        number of polygon sides that this ray crosses. If this number is odd,
        the point is inside; if it's even, the point is outside.
        Note that if the ray crosses a polygon's vertex, it will count both 
        concerned sides, giving an innacurate reading.
    '''
    bounds = peers[rid][frame]
    cdef Py_ssize_t r, j, i, strt = 0
    cdef int rang
    cdef bint c
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


cpdef update_bounds(motion, angle, origin, rid, frame='bounds'):
    '''
        Updating the elements of the collision detection checks.
    '''
    try:
        bounds = peers[rid][frame]
    except TypeError:
        return

    if motion:
        move(bounds['points'], bounds['length'], motion[0], motion[1])

    if angle:
        rotate(bounds['points'], bounds['length'], angle, origin[0], origin[1])

    bbox = array.array('d', [float("inf"), float("inf"), 0., 0.])

    if not peers[rid]['pre_check']:
        calc_bbox(bounds['points'], bounds['length'], bbox)
    elif peers[rid]['seg']:
        calc_segboxes(bounds['points'], bounds['pol_ids'], bounds['pt_ids'],
                      bounds['pol_lens'], bounds['length'], bbox,
                      bounds['lefts'], bounds['botts'], bounds['rights'],
                      bounds['tops'])
    else:
        calc_polboxes(bounds['points'], bounds['pol_lens'], bbox,
                      bounds['lefts'], bounds['botts'], bounds['rights'],
                      bounds['tops'])

    peers[rid]['bbox'] = bbox


cpdef aniupdate_bounds(motion, pos, angle, origin, rid, frame='bounds'):
    '''
        Updating the elements of the collision detection checks in case of an 
        animation.
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
        rotate(bounds['points'], bounds['length'], angle, origin[0], origin[1])

    bbox = array.array('d', [float("inf"), float("inf"), 0., 0.])

    if not peers[rid]['pre_check']:
        calc_bbox(bounds['points'], bounds['length'], bbox)
    elif peers[rid]['seg']:
        calc_segboxes(bounds['points'], bounds['pol_ids'], bounds['pt_ids'],
                      bounds['pol_lens'], bounds['length'], bbox,
                      bounds['lefts'], bounds['botts'], bounds['rights'],
                      bounds['tops'])
    else:
        calc_polboxes(bounds['points'], bounds['pol_lens'], bbox,
                      bounds['lefts'], bounds['botts'], bounds['rights'],
                      bounds['tops'])

    peers[rid]['bbox'] = bbox


cpdef resize(width, height, rid):
    for k, frame in peers[rid].items():
        if k == 'bounds':
            bounds = peers[rid]['bounds']
            bounds['points'][:] = bounds['hints']
            scale(bounds['points'], bounds['length'], width, height)
            break
    else:
        for k, frame in peers[rid].items():
            if k != 'bbox' and k != 'seg' and k != 'pre_check':
                frame['points'][:] = frame['hints']
                scale(frame['points'], frame['length'], width, height)


cpdef aniresize(width, height, rid):
    for k, frame in peers[rid].items():
        if k == 'bounds':
            bounds = peers[rid]['bounds']
            bounds['sca_pts'][:] = bounds['hints']
            scale(bounds['sca_pts'], bounds['length'], width, height)
            break
    else:
        for k, frame in peers[rid].items():
            if k != 'bbox' and k != 'seg' and k != 'pre_check':
                frame['sca_pts'][:] = frame['hints']
                scale(frame['sca_pts'], frame['length'], width, height)


cdef define_frame(list frame, dict bounds, int[::1] opens,
                   bint seg_mode, bint ani, bint pre_check):
    cdef Py_ssize_t p, i
    cdef int plen
    cdef list pol
    for p in range(len(frame)):
        pol = frame[p]
        plen = len(pol)
        array.extend(bounds['pol_lens'], array.array('i', [plen]))
        for i in range(plen):
            array.extend(bounds['hints'], array.array('d', [pol[i][0], pol[i][1]]))
            array.extend(bounds['pol_ids'], array.array('i', [p, p]))
            array.extend(bounds['pt_ids'], array.array('i', [i, i]))
            bounds['length'] += 2

    if  pre_check:
        if seg_mode:
            length = bounds['length']
        else:
            length = len(bounds['pol_lens'])
        bounds['lefts'] = array.array('d', [float("inf")] * length)
        bounds['botts'] = array.array('d', [float("inf")] * length)
        bounds['rights'] = array.array('d', [0.] * length)
        bounds['tops'] = array.array('d', [0.] * length)

    bounds['opens'] = array.array('i', opens)

    if ani:
        bounds['mov_pts'][:] = bounds['sca_pts'][:] = bounds['hints']
    bounds['points'][:] = bounds['hints']


cpdef define_bounds(custom_bounds, open_bounds, segment_mode, rid, pre_check):
    '''Organising the data from the user's [custom_bounds] hints
    for 'segment intersection' detection method.
    '''
    cdef dict frames = {}

    if isinstance(custom_bounds, dict):   # Animation case
        for key, frame in custom_bounds.items():
            bounds = {'hints': array.array('d'), 'sca_pts': array.array('d'),
                      'mov_pts': array.array('d'), 'points': array.array('d'),
                      'pol_ids': array.array('i'), 'pt_ids': array.array('i'),
                      'pol_lens': array.array('i'), 'length': 0}
            if isinstance(open_bounds, dict):
                opens = array.array('i', open_bounds[key])
            else:
                opens = array.array('i', open_bounds)

            define_frame(frame, bounds, opens, segment_mode, 1, pre_check)

            frames[key] = bounds

    elif isinstance(custom_bounds, list):  # Single image case
        bounds = {'hints': array.array('d'), 'points': array.array('d'),
                  'pol_ids': array.array('i'), 'pt_ids': array.array('i'),
                  'pol_lens': array.array('i'), 'length': 0}
        define_frame(custom_bounds, bounds, array.array('i', open_bounds),
                     segment_mode, 0, pre_check)
        frames['bounds'] = bounds

    frames['bbox'] = array.array('d', [])
    frames['seg'] = segment_mode
    frames['pre_check'] = pre_check

    peers[rid] = frames


cpdef get_peers():
    return peers
