# Reference inventory, approximate normalized image bounds:
# - Chaise (0.04, 0.23)-(0.83, 0.93): broad cream striped seat with
#   rounded foot, tall curved head at left, enclosed upholstered arms,
#   carved gray-brown wooden rails and curved legs. Rear supports are obscured.
# - Cream square pillow (0.08, 0.27)-(0.32, 0.53) rests against the head.
# - Dark green rectangular label (0.68, 0.53)-(0.71, 0.59) on the seat.
# - Cream paneled wall, baseboard and right return occupy the upper half.
# - Dark wooden floor fills the lower half; window and curtain appear at left.
# - Cropped cane chair fragment appears in the lower left.
#
# Compared with the last render, the reference has a fuller rectangular
# cushion, a square pillow, a taller solid near arm, darker floor and wood,
# more visible floor behind the foot, and a more overhead view. The head is
# closer to the left edge. Wall panels are broader and less prominent.
# Estimated expanded primitive count: about 250, including tube segments,
# molding, seat stripes, chair fragment, and rounded-box expansions.

from sceneact import *
import bpy
import math

scene = Scene("Paneled room with chaise")

wall_color = (0.64, 0.61, 0.55)
trim = (0.70, 0.67, 0.61)
shadow = (0.43, 0.40, 0.35)
floor_color = (0.085, 0.031, 0.018)
frame = (0.24, 0.22, 0.16)
frame_light = (0.43, 0.39, 0.29)
fabric = (0.70, 0.62, 0.57)
side_fabric = (0.59, 0.51, 0.46)
pillow_color = (0.78, 0.69, 0.56)
stripe = (0.54, 0.42, 0.39)

def tube(parent, name, points, radius, color):
    parent.include(name, sweep_tube(points=points, radius=radius, color=color))

room = Asset("architecture")
room.include("dark_wood_floor",
             box((9, 8, .1), center=(0, 0, -.07), color=floor_color))
room.include("back_wall",
             box((8, .12, 3.6), center=(0, 1.40, 1.8), color=wall_color))
room.include("right_wall_return",
             box((.12, 2.7, 3.6), center=(3.05, .2, 1.8), color=wall_color))
room.include("baseboard",
             box((7.9, .08, .20), center=(0, 1.30, .16), color=trim))
room.include("baseboard_cap",
             box((7.9, .10, .035), center=(0, 1.27, .28), color=trim))

def wall_rod(name, a, b, radius=.010, color=trim):
    room.include(name, rod(radius, start=a, end=b, color=color))

# Wide inset wall panel and the adjacent vertical panel divisions.
for idx, (left, right) in enumerate([(-3.10, -1.12), (-1.02, 1.98), (2.08, 3.0)]):
    for k, inset in enumerate((0.0, .055)):
        x0, x1 = left + inset, right - inset
        z0, z1 = .38 + inset, 1.80 - inset
        y = 1.315 - k * .007
        for suffix, a, b in [
            ("bottom", (x0,y,z0), (x1,y,z0)),
            ("top", (x0,y,z1), (x1,y,z1)),
            ("left", (x0,y,z0), (x0,y,z1)),
            ("right", (x1,y,z0), (x1,y,z1))
        ]:
            wall_rod("panel_%d_%d_%s" % (idx,k,suffix), a, b)
wall_rod("upper_rail", (-3.8,1.28,2.02), (3.0,1.28,2.02), .020)
wall_rod("upper_rail_shadow", (-3.8,1.31,2.12), (3.0,1.31,2.12), .006, shadow)
for i, x in enumerate((-1.18, .18)):
    wall_rod("upper_joint_%d" % i, (x,1.325,1.84), (x,1.325,3.1), .003, shadow)
for i, x in enumerate((-1.05, -.96)):
    room.include("wall_fitting_%d" % i,
                 ball(.020, center=(x,1.25,1.99), color=(.08,.075,.06)))
scene.include("architecture", room)

seams = Asset("floorboard_seams")
for i in range(-6, 7):
    y = i * .53
    seams.include("seam_%d" % i,
                  rod(.0015, start=(-4,y,-.013), end=(4,y,-.013),
                      color=(.045,.016,.010)))
scene.include("floorboard_seams", seams)

window = Asset("window_and_curtain")
window.include("bright_window",
               box((.45,.06,2.9), center=(-2.30,1.20,1.50),
                   color=(.95,.94,.88)))
window.include("window_frame",
               box((.055,.10,2.9), center=(-2.06,1.14,1.50),
                   color=(.76,.73,.65)))
for i in range(5):
    window.include("curtain_fold_%d" % i,
                   box((.065,.08,2.8),
                       center=(-2.03+i*.055,1.09-(i%2)*.025,1.45),
                       color=(.66+i*.015,.61+i*.015,.52+i*.015)))
scene.include("window_and_curtain", window)

chaise = Asset("chaise_longue")

# A rounded rectangular cushion has a broad, flat central upholstered surface.
seat = fillet_box((2.65, 1.24, .27), radius=.13,
                  center=(.10, 0, .73), color=fabric)
chaise.include("broad_seat_cushion", seat)
chaise.include("upholstered_underbody",
               box((2.35,1.10,.16), center=(.03,0,.59), color=fabric))

head = ball(1, center=(-1.18,0,1.05), color=fabric)
head.resize((.27,.63,.62))
head.turn(axis="+y", degrees=-17)
chaise.include("raised_upholstered_head", head)

# Full side panels close the large spaces below the curved arm rails.
for s in (-1,1):
    side = ball(1, center=(-1.02,s*.53,.91), color=side_fabric)
    side.resize((.47,.105,.43))
    side.turn(axis="+y", degrees=-24)
    chaise.include("upholstered_side_%d" % s, side)

tube(chaise, "head_outer_crest",
     [(-1.04,-.60,.68),(-1.31,-.62,.94),(-1.45,-.54,1.31),
      (-1.44,-.31,1.52),(-1.40,0,1.59),(-1.44,.31,1.52),
      (-1.45,.54,1.31),(-1.31,.62,.94),(-1.04,.60,.68)],
     .036, frame)
tube(chaise, "head_crest_highlight",
     [(-1.41,-.51,1.31),(-1.40,-.29,1.49),(-1.36,0,1.56),
      (-1.40,.29,1.49),(-1.41,.51,1.31)], .010, frame_light)

for s in (-1,1):
    y = s*.60
    tube(chaise, "arm_rail_%d" % s,
         [(-1.37,y,1.29),(-1.23,y*1.04,1.10),
          (-1.04,y*1.05,.97),(-.82,y*1.05,.92),
          (-.70,y*1.02,.72),(-.57,y,.60)], .035, frame)
    tube(chaise, "arm_highlight_%d" % s,
         [(-1.28,y*1.02,1.14),(-1.05,y*1.05,1.00),
          (-.83,y*1.05,.95)], .010, frame_light)
    tube(chaise, "seat_apron_%d" % s,
         [(-.88,s*.56,.52),(-.48,s*.61,.49),(.20,s*.62,.47),
          (.91,s*.59,.48),(1.27,s*.49,.50)], .036, frame)
    tube(chaise, "apron_highlight_%d" % s,
         [(-.78,s*.57,.54),(-.42,s*.62,.51),(.26,s*.63,.49),
          (.93,s*.60,.50)], .010, frame_light)

tube(chaise, "foot_end_rail",
     [(1.20,-.51,.50),(1.36,-.36,.49),(1.43,0,.48),
      (1.36,.36,.49),(1.20,.51,.50)], .035, frame)

for x in (-.75,1.22):
    for s in (-1,1):
        y = s*.51
        tube(chaise, "leg_%s_%s" % (x,s),
             [(x,y,.52),(x+.04,y*1.04,.38),
              (x-.01,y*1.08,.22),(x-.04,y*1.10,.08),
              (x+.005,y*1.10,.045)], .035, frame)
        chaise.include("leg_knee_%s_%s" % (x,s),
                       ball(.060, center=(x,y,.49), color=frame_light))

for i, dx in enumerate((-.12,0,.12)):
    ornament = ball(.052, center=(.20+dx,-.63,.48), color=frame_light)
    ornament.resize((1,.28,.65))
    chaise.include("apron_carving_%d" % i, ornament)

# Fine stripes lie on the flat central portion of the cushion.
for i in range(-10,11):
    y = i*.053
    chaise.include("upholstery_stripe_%02d" % (i+10),
                   rod(.0023, start=(-.95,y,.867), end=(1.26,y,.867),
                       color=stripe))

# The photograph shows a square, softly rounded pillow rather than an oval.
pillow = fillet_box((.20,.68,.62), radius=.085,
                    center=(-1.02,-.05,1.22), color=pillow_color)
pillow.turn(axis="+y", degrees=-23)
chaise.include("cream_pillow", pillow)

label = box((.14,.075,.009), center=(.74,-.08,.873),
            color=(.025,.14,.13))
chaise.include("seat_label", label)
scene.include("chaise_longue", chaise)

fragment = Asset("foreground_cane_chair_fragment")
fragment.include("cane_seat",
                 box((.74,.54,.045), center=(-1.95,-1.65,.47),
                     color=(.42,.27,.17)))
tube(fragment, "seat_rim",
     [(-2.32,-1.92,.49),(-1.58,-1.92,.49),
      (-1.58,-1.38,.49),(-2.32,-1.38,.49)], .037, frame_light)
for i in range(8):
    x = -2.27+i*.09
    fragment.include("cane_line_%d" % i,
                     rod(.004, start=(x,-1.89,.496), end=(x,-1.41,.496),
                         color=(.65,.49,.34)))
scene.include("foreground_chair_fragment", fragment)

realize(scene)

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
background.inputs["Color"].default_value = (.73,.71,.67,1)
background.inputs["Strength"].default_value = .45

set_view((1.2,-6.5,4.15), (-.10,.12,.83), lens=65)
area_emitter((-3.8,-2.8,4.7), power=550, size=4.0,
             target=(-.2,.1,.6), color=(1.0,.91,.80))
area_emitter((2.8,-.8,4.5), power=160, size=3.5,
             target=(0,0,.7), color=(1.0,.95,.88))
