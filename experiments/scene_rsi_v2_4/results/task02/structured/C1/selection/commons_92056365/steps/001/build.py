import bpy
import math
import random
from sceneact import *

# Reference inventory (normalized image bounds, estimated from the photograph):
# Architecture: pale slatted ceiling (0,0)-(1,.33), rear glazing
# (0,.30)-(.74,.55), right glazing (.72,.23)-(1,.68), dark tiled floor.
# Furniture: repeated gray upholstered pedestal chairs and booths, primarily
# (.01,.50)-(.88,.95); thin dark square tables between them. Foreground left
# booth and table are cropped. Right foreground chair overlaps the palm.
# Pendants: prominent open bell at (.02,.12)-(.23,.40), smaller repeating
# bells across (.10,.29)-(1,.44). Main shade has a broad rim, rounded shoulder,
# narrow cylindrical neck, and a visible pale recessed interior.
# Plants: dense palm at (.76,.39)-(1,1), low foliage across rear seating.
# Exterior trees are uncertain silhouettes beyond very bright windows.
#
# Asset mapping: room/{floor,ceiling,slats,window_frames}; individual
# table/{top,edge,column,foot}; chair/{seat,back,arms,column,foot};
# pendant/{outer_shell,inner_lining,neck,cord,ceiling_plate};
# palm/{pot,stems,leaflets}; rear_planter/{container,foliage}.
# Local dimensions are defined in factories, independently of placement.
# Estimated expansion: 170 chair primitives, 45 table primitives, 65 room
# primitives, ~75 lamp operands/parts, 100 plant primitives, 22 exterior
# masses: approximately 480 meshes before Boolean realization.
# Camera, depth, and object scale are estimates, not recovered calibration.

random.seed(14)
scene = Scene("Window_side_cafeteria")

WHITE = (.83, .84, .81)
FRAME = (.40, .43, .41)
FABRIC = (.37, .41, .38)
SIDE = (.43, .46, .43)
DARK = (.075, .09, .08)
TOP = (.15, .18, .16)
METAL = (.57, .59, .56)
LEAF = (.065, .10, .07)

def add(parent, name, shape):
    parent.include(name, shape)
    return shape

def place(asset, name, position, angle=0):
    asset.turn(axis="+z", degrees=angle, pivot=(0, 0, 0))
    asset.move(position)
    scene.include(name, asset)
    return asset

def ellipsoid(radius, factors, center, color):
    n = ball(radius=radius, center=(0, 0, 0), color=color)
    n.resize(factors, pivot=(0, 0, 0))
    n.move(center)
    return n

room = Asset("Room")
add(room, "floor", box(size=(13, 19, .13), center=(0, 2, -.075),
                       color=(.27, .29, .27)))
add(room, "ceiling", box(size=(13, 19, .12), center=(0, 2, 4.10),
                         color=(.89, .90, .87)))
# Narrow ceiling boards run across the room.
for i in range(47):
    y = -6.5 + i * .36
    add(room, "ceiling_joint_%02d" % i,
        box(size=(12.9, .013, .009), center=(0, y, 4.032),
            color=(.64, .66, .63)))
# Low window aprons and deep continuous horizontal rails.
add(room, "back_apron", box(size=(12.8, .18, .48),
    center=(0, 9, .24), color=WHITE))
add(room, "back_sill", box(size=(12.8, .27, .09),
    center=(0, 8.94, .70), color=FRAME))
add(room, "back_header", box(size=(12.8, .20, .17),
    center=(0, 9, 3.12), color=FRAME))
add(room, "right_apron", box(size=(.18, 16, .48),
    center=(6.3, 1, .24), color=WHITE))
add(room, "right_sill", box(size=(.28, 16, .09),
    center=(6.25, 1, .70), color=FRAME))
add(room, "right_header", box(size=(.18, 16, .15),
    center=(6.3, 1, 3.12), color=FRAME))
for i, x in enumerate([-6.25, -3.75, -1.25, 1.25, 3.75, 6.25]):
    add(room, "back_mullion_%d" % i,
        box(size=(.065, .13, 2.45), center=(x, 8.98, 1.91), color=FRAME))
for i, y in enumerate([-6, -3.2, -.4, 2.4, 5.2, 8.95]):
    add(room, "right_mullion_%d" % i,
        box(size=(.13, .065, 2.45), center=(6.27, y, 1.91), color=FRAME))
# Floor tile joints: restrained geometry, with stagger implied by short cross joints.
for i in range(28):
    x = -6.4 + i * .47
    add(room, "floor_long_joint_%d" % i,
        box(size=(.010, 18, .003), center=(x, 1.8, -.006),
            color=(.45, .46, .43)))
for i in range(22):
    y = -6.5 + i * .79
    add(room, "floor_cross_joint_%d" % i,
        box(size=(12.7, .009, .003), center=(0, y, -.004),
            color=(.37, .39, .36)))
scene.include("architecture", room)

def chair(width=.98):
    # Local front is -Y. Broad square back, thin arms, open space below seat.
    a = Asset("Upholstered_pedestal_chair")
    add(a, "circular_floor_foot",
        rod(radius=.30, length=.045, center=(0, 0, .027), color=METAL))
    add(a, "pedestal",
        rod(radius=.065, length=.40, center=(0, 0, .25), color=METAL))
    add(a, "seat_cushion",
        box(size=(width, .78, .13), center=(0, -.02, .53), color=FABRIC))
    add(a, "broad_back",
        box(size=(width, .115, .74), center=(0, .37, .92), color=FABRIC))
    add(a, "left_arm_panel",
        box(size=(.095, .76, .48), center=(-width/2+.03, .015, .78), color=SIDE))
    add(a, "right_arm_panel",
        box(size=(.095, .76, .48), center=(width/2-.03, .015, .78), color=SIDE))
    add(a, "back_upper_piping",
        box(size=(width, .125, .025), center=(0, .37, 1.295), color=SIDE))
    return a

def booth(width=1.95):
    a = Asset("Wide_booth")
    add(a, "base", box(size=(width-.12, .63, .33),
                       center=(0, .02, .24), color=DARK))
    add(a, "seat", box(size=(width, .79, .14),
                       center=(0, -.02, .48), color=FABRIC))
    add(a, "back", box(size=(width, .15, .80),
                       center=(0, .36, .91), color=FABRIC))
    add(a, "top_seam", box(size=(width, .16, .025),
                           center=(0, .36, 1.32), color=SIDE))
    return a

def table(width=1.24, depth=.92):
    a = Asset("Square_pedestal_table")
    add(a, "floor_disc",
        rod(radius=.31, length=.045, center=(0, 0, .03), color=METAL))
    add(a, "chrome_column",
        rod(radius=.052, length=.75, center=(0, 0, .42), color=METAL))
    add(a, "dark_edge", box(size=(width, depth, .055),
                            center=(0, 0, .825), color=DARK))
    add(a, "laminate_top", box(size=(width-.012, depth-.012, .018),
                               center=(0, 0, .86), color=TOP))
    return a

# Three principal furniture lanes. Depth and overlap take precedence over
# uncertain exact seating counts behind the visible chair backs.
for lane, x in enumerate([-3.4, -.40, 2.52]):
    for row, y in enumerate([.0, 2.65, 5.05, 7.25]):
        place(table(), "table_%d_%d" % (lane, row), (x, y, 0))
        if lane == 0:
            place(booth(1.92), "left_booth_%d" % row, (x, y-1.03, 0))
        else:
            place(chair(), "front_chair_%d_%d" % (lane, row),
                  (x, y-1.02, 0), 180)
        if row > 0:
            place(chair(.95), "rear_chair_%d_%d" % (lane, row),
                  (x, y+.94, 0), 0)

# Foreground cropped pieces establish the photograph's close scale.
place(booth(2.32), "foreground_left_booth", (-3.52, -2.65, 0), 0)
place(table(2.20, 1.18), "foreground_left_table", (-3.52, -4.05, 0))
place(chair(1.15), "foreground_right_chair", (3.70, -2.0, 0), 175)
place(table(1.33, 1.0), "foreground_right_table", (2.53, -1.40, 0))

def shade_shell(radius, height, thickness, color):
    outer = ellipsoid(1, (radius, radius, height), (0, 0, 0), color)
    inner = ellipsoid(1, (radius-thickness, radius-thickness, height-thickness),
                      (0, 0, -.006), color)
    lower = box(size=(radius*3, radius*3, height*3),
                center=(0, 0, -height*1.5), color=color)
    return subtract(outer, inner, lower)

def pendant(radius=.40, rim_height=2.70, ceiling=4.03):
    a = Asset("Open_bell_pendant")
    # Contour landmarks: rim diameter 1, shoulder at .55 of dome height,
    # neck diameter .36 of rim diameter; interior remains geometrically open.
    dome_h = radius*.83
    shell = shade_shell(radius, dome_h, .027, DARK)
    shell.move((0, 0, rim_height))
    add(a, "outer_shell", shell)
    lining = shade_shell(radius-.030, dome_h-.027, .012, (.84, .85, .80))
    lining.move((0, 0, rim_height+.004))
    add(a, "recessed_white_lining", lining)
    neck_r = radius*.34
    neck_h = radius*.70
    add(a, "neck", rod(radius=neck_r, length=neck_h,
        center=(0, 0, rim_height+dome_h+neck_h*.25), color=DARK))
    add(a, "neck_band", rod(radius=neck_r*1.025, length=.035,
        center=(0, 0, rim_height+dome_h+neck_h*.28),
        color=(.30, .33, .29)))
    top = rim_height+dome_h+neck_h*.75
    if top < ceiling:
        add(a, "suspension_cord", rod(radius=.009,
            start=(0, 0, top), end=(0, 0, ceiling), color=DARK))
    add(a, "ceiling_plate", rod(radius=.085, length=.018,
        center=(0, 0, ceiling), color=DARK))
    return a

place(pendant(.65, 2.92), "large_left_foreground_pendant", (-4.13, -2.15, 0))
for i, (x, y, r, z) in enumerate([
    (-3.4, 3.5, .36, 2.66),
    (-3.4, 7.2, .27, 2.60),
    (-.55, 5.0, .34, 2.69),
    (2.05, 4.6, .39, 2.77),
    (4.62, 1.25, .49, 2.96),
    (4.72, 5.2, .32, 2.73),
    (5.76, 6.8, .29, 2.72),
    (-4.9, 6.5, .25, 2.59)
]):
    place(pendant(r, z), "repeating_pendant_%02d" % i, (x, y, 0))

def leaf_between(start, end, width, color):
    dx, dy, dz = [end[i]-start[i] for i in range(3)]
    length = math.sqrt(dx*dx+dy*dy+dz*dz)
    n = ellipsoid(1, (width, .014, length*.5), (0, 0, 0), color)
    # Rotate the long local Z axis toward the desired vector.
    polar = math.degrees(math.acos(max(-1, min(1, dz/length))))
    azimuth = math.degrees(math.atan2(dy, dx))
    n.turn(axis="+y", degrees=polar, pivot=(0, 0, 0))
    n.turn(axis="+z", degrees=azimuth, pivot=(0, 0, 0))
    n.move(tuple((start[i]+end[i])*.5 for i in range(3)))
    return n

palm = Asset("Foreground_palm")
add(palm, "square_planter", box(size=(.66, .65, .65),
                              center=(0, 0, .325), color=(.12, .15, .12)))
add(palm, "soil", box(size=(.58, .57, .025),
                     center=(0, 0, .66), color=(.07, .08, .06)))
for f in range(8):
    theta = f*math.tau/8 + .15
    reach = [1.05, 1.20, .9, 1.03, 1.25, .85, 1.0, 1.12][f]
    high = 2.48 + .17*math.sin(f*2)
    base = (0, 0, .66)
    p1 = (.18*math.cos(theta), .18*math.sin(theta), high-.45)
    p2 = (.57*reach*math.cos(theta), .57*reach*math.sin(theta), high)
    p3 = (reach*math.cos(theta), reach*math.sin(theta), high-.24)
    add(palm, "frond_stem_%d" % f,
        sweep_tube(points=[base, p1, p2, p3], radius=.012, color=LEAF))
    for j in range(5):
        t = .26+j*.145
        radial = reach*t
        z = high-.6*(t-.62)**2
        c = (radial*math.cos(theta), radial*math.sin(theta), z)
        for side in [-1, 1]:
            spread = (.36*(1-t)+.10)*side
            tip = (c[0]+.23*math.cos(theta)-spread*math.sin(theta),
                   c[1]+.23*math.sin(theta)+spread*math.cos(theta),
                   c[2]-.14-.09*t)
            add(palm, "leaflet_%d_%d_%d" % (f, j, side),
                leaf_between(c, tip, .038, LEAF))
place(palm, "right_foreground_palm", (4.85, -1.73, 0), 10)

planter = Asset("Rear_low_planter")
add(planter, "container", box(size=(3.5, .48, .46),
                             center=(0, 0, .70), color=(.28, .31, .27)))
for i in range(25):
    x = random.uniform(-1.65, 1.65)
    y = random.uniform(-.18, .18)
    z = random.uniform(.98, 1.30)
    add(planter, "foliage_%d" % i,
        ellipsoid(.17, (1.2, .7, .65), (x, y, z),
                  (.24+random.random()*.10, .29, .24)))
place(planter, "rear_foliage_divider", (-.75, 6.4, 0))

# Bright exterior geometry; no photograph, backdrop texture, or projection.
outside = Asset("Exterior")
add(outside, "bright_ground", box(size=(40, 28, .08),
    center=(0, 20, -.16), color=(.82, .84, .79)))
for i in range(16):
    x = random.uniform(-13, 14)
    y = random.uniform(12, 20)
    z = random.uniform(1.5, 3.3)
    add(outside, "distant_tree_%d" % i,
        ellipsoid(1, (random.uniform(.8, 1.5), .8, random.uniform(.8, 1.6)),
                  (x, y, z), (.59, .63, .56)))
scene.include("outside", outside)

realize(scene)

# Lighting and camera are deliberately separate from all asset parameters.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.87, .89, .86, 1)
background.inputs["Strength"].default_value = .75

set_view(position=(-4.10, -8.40, 2.62),
         target=(.30, 5.00, 1.94), lens=33, sensor=36)
area_emitter(position=(0, 8.0, 3.35), power=1500, size=9,
             target=(0, 1.0, .3), color=(1, 1, .97))
area_emitter(position=(6.0, 1.0, 3.1), power=1100, size=7,
             target=(0, 1, .8), color=(1, 1, .98))
area_emitter(position=(-3, -4, 3.8), power=220, size=5,
             target=(0, 2, .5), color=(1, 1, 1))

# Restrained neutral finish preserves the reference's monochrome appearance.
for material in bpy.data.materials:
    if material.use_nodes:
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value = .52
            base = bsdf.inputs["Base Color"].default_value
            gray = .299*base[0] + .587*base[1] + .114*base[2]
            bsdf.inputs["Base Color"].default_value = (gray, gray, gray, base[3])

sc.render.resolution_x = 512
sc.render.resolution_y = 379
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = .45
sc.camera.data.clip_start = .06
sc.camera.data.clip_end = 150
