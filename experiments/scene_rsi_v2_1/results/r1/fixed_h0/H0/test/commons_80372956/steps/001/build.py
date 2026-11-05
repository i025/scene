from sceneact import *
import bpy
import math
import random

random.seed(8)
scene = Scene("White timber ceiling and brass chandelier")
white = (0.79, 0.80, 0.76)
seam = (0.62, 0.63, 0.58)
timber = (0.34, 0.26, 0.12)
edgewood = (0.43, 0.34, 0.17)
gold = (0.67, 0.48, 0.105)
darkgold = (0.36, 0.245, 0.045)

# Shallow pitched ceiling, with its ridge running vertically through the view.
def height(x):
    return 6.65 - 0.105 * abs(x)

roof = Asset("Painted boarded ceiling")
for side in (-1, 1):
    panel = box((4.5, 9, .12),
                center=(side * 2.25, 0, height(2.25)),
                color=white)
    panel.turn(axis="+y", degrees=side * 6.0)
    roof.include("roof_panel_%s" % side, panel)

# Fine transverse joints in the painted boards.
for j in range(-24, 25):
    y = j * .19
    for side in (-1, 1):
        line = box((4.5, .009, .009),
                   center=(side * 2.25, y, height(2.25)-.065),
                   color=(.69, .70, .66))
        line.turn(axis="+y", degrees=side * 6)
        roof.include("board_joint_%s_%s" % (j, side), line)

# Raised narrow white rafters.
for i in range(-6, 7):
    x = i * .69
    roof.include("white_rafter_%02d" % (i+6),
                 box((.105, 9, .17), center=(x, 0, height(x)-.14),
                     color=(.87, .865, .81)))
    roof.include("rafter_side_%02d" % (i+6),
                 box((.018, 9, .105), center=(x+.058, 0, height(x)-.16),
                     color=(.65, .65, .59)))
scene.include("ceiling", roof)

frame = Asset("Exposed timber framing")
for y in (0, -2.75, 2.92):
    for side in (-1, 1):
        b = box((4.65, .19, .20),
                center=(side*2.27, y, height(2.27)-.34),
                color=timber)
        b.turn(axis="+y", degrees=side*6)
        frame.include("crossbeam_%s_%s" % (y, side), b)
        lip = box((4.65, .035, .045),
                  center=(side*2.27, y-.105, height(2.27)-.235),
                  color=edgewood)
        lip.turn(axis="+y", degrees=side*6)
        frame.include("beam_lip_%s_%s" % (y, side), lip)

for x in (-3.65, 3.65):
    frame.include("side_beam_%s" % x,
                  box((.23, 9, .26), center=(x, 0, height(x)-.33),
                      color=timber))
    for y in (-2.75, 0, 2.92):
        frame.include("joint_block_%s_%s" % (x,y),
                      box((.55,.36,.29),
                          center=(x,y,height(x)-.37),color=edgewood))
        frame.include("joint_plate_%s_%s" % (x,y),
                      box((.38,.39,.045),
                          center=(x,y,height(x)-.54),color=timber))
for y in (-2.75, 2.92):
    frame.include("ridge_joint_%s" % y,
                  box((.20,.38,.35),center=(0,y,6.28),color=timber))
frame.include("ridge",box((.075,9,.10),center=(0,0,6.49),color=edgewood))
scene.include("framing", frame)

# Occasional dark fixing marks on the white ceiling.
for k, (x,y) in enumerate([(-1.85,1.48),(1.77,1.52),
                            (-1.73,-1.32),(1.73,-1.36)]):
    scene.include("ceiling_fixing_%d" % k,
                  ball(.018,center=(x,y,height(x)-.081),
                       color=(.18,.18,.15)))

fixture = Asset("Polished brass radial chandelier")
zc = 4.47
fixture.include("central_globe", ball(.185,center=(0,0,zc),color=gold))
fixture.include("upper_collar",
                rod(.105,start=(0,0,zc+.12),end=(0,0,zc+.23),color=gold))
fixture.include("lower_finial",
                ball(.065,center=(0,0,zc-.185),color=gold))
fixture.include("finial_tip",
                ball(.029,center=(0,0,zc-.235),color=darkgold))
fixture.include("suspension",
                rod(.026,start=(0,0,zc+.17),end=(0,.055,6.23),color=gold))
fixture.include("ceiling_canopy",
                rod(.10,start=(0,.055,6.18),end=(0,.055,6.27),color=gold))
fixture.include("stem_ornament",
                ball(.055,center=(0,.015,5.05),color=gold))

def ring(name, cx, cy, z, radius, tube, color):
    points = []
    for j in range(49):
        a = 2*math.pi*j/48
        points.append((cx+radius*math.cos(a),cy+radius*math.sin(a),z))
    fixture.include(name,sweep_tube(points=points,radius=tube,color=color))

ring("central_equatorial_band",0,0,zc,.184,.012,gold)
ring("central_lower_band",0,0,zc-.11,.15,.009,darkgold)

# Alternating long and short curved arms create the dense sunburst silhouette.
for i in range(20):
    angle = math.radians(i*18+8)
    long_arm = (i % 2 == 0)
    reach = (1.075 if long_arm else .635) * random.uniform(.96,1.035)
    ux, uy = math.cos(angle), math.sin(angle)
    endpoint_z = zc + (.09 if long_arm else .12)
    points = []
    for j in range(17):
        t = j/16
        r = .13+(reach-.13)*t
        bend = .035*math.sin(math.pi*t)
        points.append((ux*r-uy*bend,uy*r+ux*bend,
                       zc+.018+.09*t-.095*math.sin(math.pi*t)))
    fixture.include("curved_arm_%02d" % i,
                    sweep_tube(points=points,radius=.013,color=gold))
    x,y = ux*reach,uy*reach
    fixture.include("cup_stem_%02d" % i,
                    rod(.018,start=points[-1],
                        end=(x,y,endpoint_z+.035),color=gold))
    cup = ball(.083 if long_arm else .068,
               center=(x,y,endpoint_z),color=gold)
    cup.resize((1,1,.42))
    fixture.include("brass_cup_%02d" % i,cup)
    ring("cup_rim_%02d" % i,x,y,endpoint_z-.014,
         .075 if long_arm else .060,.010,gold)
    ring("cup_inner_ring_%02d" % i,x,y,endpoint_z-.029,
         .048 if long_arm else .037,.006,darkgold)
    fixture.include("cup_center_%02d" % i,
                    ball(.026,center=(x,y,endpoint_z-.035),color=gold))
    # Small collars where the arms emerge from the central globe.
    fixture.include("root_bead_%02d" % i,
                    ball(.026,center=(ux*.245,uy*.245,zc+.025),color=gold))

scene.include("chandelier",fixture)
realize(scene)

# Metallic brass and softly textured painted timber.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    col = bsdf.inputs["Base Color"].default_value
    if col[0] > col[1]*1.15 and col[1] > col[2]*1.8:
        if col[0] > .5:
            bsdf.inputs["Metallic"].default_value = .88
            bsdf.inputs["Roughness"].default_value = .23
        else:
            bsdf.inputs["Metallic"].default_value = .15
            bsdf.inputs["Roughness"].default_value = .46
    else:
        bsdf.inputs["Roughness"].default_value = .76

set_view(position=(0,-.25,.20),target=(0,0,6.45),lens=28,sensor=36)
camera = bpy.context.scene.camera
camera.data.lens = 28
camera.data.sensor_width = 36

area_emitter(position=(-3,-1.5,3.8),power=550,size=4.0,
             target=(0,0,6.2),color=(1,.96,.87))
area_emitter(position=(2.8,2.5,3.1),power=420,size=3.0,
             target=(0,0,5.5),color=(.88,.94,1))
area_emitter(position=(-1,1,2),power=170,size=1.5,
             target=(0,0,4.5),color=(1,1,.94))
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value=(.68,.73,.80,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.40

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.render.resolution_x = 512
sc.render.resolution_y = 341
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = .15
