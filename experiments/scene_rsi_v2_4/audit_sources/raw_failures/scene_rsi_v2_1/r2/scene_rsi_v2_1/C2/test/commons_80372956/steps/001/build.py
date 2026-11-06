import bpy
import math
import random
from mathutils import Vector
from sceneact import *

# Estimated image inventory, normalized coordinates, origin at top left:
# White pitched ceiling fills the frame; its ridge is near x=.49.
# Narrow raised ribs run vertically at x≈.05,.10,.19,.29,.39,.49,
# .59,.69,.79,.89,.98, with broad white boarded spaces between them.
# Ochre framing crosses y≈.50 and borders y≈.02 and .94; the lower
# border rises to y≈.88 at the central ridge. Connections overlap ribs.
# Brass chandelier bounds: (.33,.25)-(.67,.77), hub center (.497,.508).
# Hub diameter≈.062 image width; terminal balls diameter≈.025.
# Selected terminals: (.410,.314),(.508,.273),(.597,.325),
# (.349,.437),(.655,.463),(.641,.619),(.576,.713),(.478,.748).
# Thin exposed arms leave substantial negative space between terminals.
# Terminal depths and the concealed ceiling attachment remain uncertain.

random.seed(12)
scene = Scene("Ceiling and brass starburst")
ivory = (.76, .775, .74)
rib_white = (.84, .845, .79)
timber = (.35, .265, .115)
edge_gold = (.43, .335, .16)
brass = (.67, .43, .085)
dark_brass = (.24, .17, .045)

roof = Asset("White boarded pitched ceiling")
slope = .19
ridge_z = 6.22

def height(x):
    return ridge_z - slope * abs(x)

# Two roof slopes, with transverse board seams.
for side in (-1, 1):
    angle = side * math.degrees(math.atan(slope))
    for j in range(35):
        y = -2.8 + j * .164
        c = .755 + random.uniform(-.018, .018)
        p = box((4.35, .159, .055),
                center=(side * 2.14, y, height(2.14) + .045),
                color=(c, c + .013, c - .005))
        p.turn('y', angle)
        roof.include(f"board_{side}_{j}", p)

# Long, pale raised rafters, their darker edges supplying thin shadows.
for i in range(-5, 6):
    x = i * .647
    z = height(x)
    roof.include(f"rafter_shadow_{i}",
                 box((.107, 5.8, .155), center=(x, 0, z-.075),
                     color=(.57, .55, .44)))
    roof.include(f"rafter_face_{i}",
                 box((.073, 5.8, .159), center=(x-.009, 0, z-.087),
                     color=rib_white))
scene.include("ceiling", roof)

framing = Asset("Ochre structural ceiling framing")
for k, y in enumerate((-2.04, .015, 2.24)):
    for side in (-1, 1):
        x = side * 1.83
        p = box((3.70, .14, .17),
                center=(x, y, height(x)-.18), color=timber)
        p.turn('y', side * math.degrees(math.atan(slope)))
        framing.include(f"crossbeam_{k}_{side}", p)
        lip = box((3.70, .035, .045),
                  center=(x, y-.065, height(x)-.285), color=edge_gold)
        lip.turn('y', side * math.degrees(math.atan(slope)))
        framing.include(f"beam_edge_{k}_{side}", lip)
    # Small ridge joint wrapping the cross members.
    framing.include(f"ridge_joint_{k}",
                    box((.17, .24, .24),
                        center=(0, y, ridge_z-.195), color=(.28,.22,.115)))
    framing.include(f"ridge_joint_face_{k}",
                    box((.106, .263, .12),
                        center=(0, y-.006, ridge_z-.295), color=edge_gold))
    for side in (-1, 1):
        x = side * 3.03
        framing.include(f"outer_connection_{k}_{side}",
                        box((.49, .29, .18),
                            center=(x, y, height(x)-.25), color=edge_gold))
        framing.include(f"outer_strap_{k}_{side}",
                        box((.065, .36, .245),
                            center=(x-side*.10, y, height(x)-.24),
                            color=(.30,.23,.11)))
        for dx in (-.16, .16):
            framing.include(f"bolt_{k}_{side}_{dx}",
                            ball(.022,
                                 center=(x+dx, y-.12, height(x)-.35),
                                 color=dark_brass))
# Central narrow roof ridge, partly concealed by the chandelier.
framing.include("ridge",
                box((.105, 5.8, .16),
                    center=(0,0,ridge_z-.075), color=(.54,.49,.35)))
scene.include("framing", framing)

chandelier = Asset("Polished brass radial chandelier")
hub = Vector((0, -.025, 4.52))
chandelier.include("central_globe", ball(.163, center=tuple(hub), color=brass))
# Nested rounded fittings create the irregular bright central crown.
chandelier.include("upper_collar",
                    rod(.073, start=(0,-.025,4.62),
                        end=(0,-.025,4.85), color=brass))
chandelier.include("lower_button",
                    ball(.058, center=(0,-.025,4.35), color=brass))
# A slender suspension, substantially hidden by the radial assembly.
chandelier.include("suspension",
                    rod(.014, start=(0,-.025,4.73),
                        end=(0,-.025,6.03), color=brass))
chandelier.include("ceiling_rosette",
                    rod(.085, start=(0,-.025,6.01),
                        end=(0,-.025,6.07), color=brass))

# Image-space terminal arrangement, independent of ball sizes and arm thickness.
terminal_pixels = [
    (210,107,4.58), (260,93,4.65), (306,111,4.57),
    (179,149,4.59), (228,133,4.32), (258,123,4.25),
    (284,133,4.38), (209,155,4.23), (302,159,4.23),
    (335,158,4.58), (328,211,4.52), (299,190,4.29),
    (280,208,4.29), (295,243,4.58), (245,255,4.57),
    (250,215,4.20), (225,207,4.31), (202,238,4.57),
    (177,194,4.57), (209,181,4.28)
]
camera_z = .15
focal_pixels = 512 * 32 / 36
ball_radius = .061
for i, (px, py, depth) in enumerate(terminal_pixels):
    dist = depth - camera_z
    x = (px-254) * dist / focal_pixels
    # Small correction for the camera's slight upward tilt toward +Y.
    y = -(py-171) * dist / focal_pixels + (-.15 + .15*dist/5.85)
    endpoint = Vector((x,y,depth))
    direction = (endpoint-hub).normalized()
    start = hub + direction*.126
    end = endpoint-direction*.026
    chandelier.include(f"arm_{i}",
                        rod(.0105, start=tuple(start), end=tuple(end),
                            color=brass))
    chandelier.include(f"hub_socket_{i}",
                        rod(.022, start=tuple(hub+direction*.139),
                            end=tuple(hub+direction*.205), color=brass))
    chandelier.include(f"terminal_globe_{i}",
                        ball(ball_radius, center=tuple(endpoint), color=brass))
    # Fine circular bands add the visible dark grooves of the brass terminals.
    axis = direction
    helper = Vector((0,0,1)) if abs(axis.z)<.9 else Vector((0,1,0))
    u = axis.cross(helper).normalized()
    v = axis.cross(u).normalized()
    for band, offset in enumerate((-.020,.020)):
        rr = math.sqrt(ball_radius**2-offset**2)*1.003
        pts = []
        for j in range(33):
            a = j*2*math.pi/32
            q = endpoint + axis*offset + rr*(u*math.cos(a)+v*math.sin(a))
            pts.append(tuple(q))
        chandelier.include(f"terminal_band_{i}_{band}",
                            sweep_tube(points=pts, radius=.0032,
                                       color=dark_brass))
    chandelier.include(f"terminal_tip_{i}",
                        ball(.017, center=tuple(endpoint+axis*.058),
                             color=brass))
scene.include("chandelier", chandelier)

# Sparse dark ceiling screw heads, visible in otherwise broad pale panels.
fasteners = Asset("Ceiling fasteners")
for i,(x,y) in enumerate(((-1.68,1.12),(1.61,1.13),
                           (-1.61,-.99),(1.57,-1.00))):
    fasteners.include(f"screw_{i}",
                      ball(.013,center=(x,y,height(x)-.047),
                           color=(.17,.16,.12)))
scene.include("fasteners",fasteners)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("World")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background:
    background.inputs["Color"].default_value = (.32,.34,.37,1)
    background.inputs["Strength"].default_value = .45

# Set metallic response on the SceneAct brass materials.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        rgba = bs.inputs["Base Color"].default_value
        r,g,b = rgba[:3]
        if r > g*1.22 and g > b*1.6:
            bs.inputs["Metallic"].default_value = .91
            bs.inputs["Roughness"].default_value = .19
        else:
            bs.inputs["Roughness"].default_value = .77

set_view((0,-.15,.15),(0,0,6.0),lens=32,sensor=36)
area_emitter((-2.8,-1.8,2.7),power=650,size=3.2,
             target=(0,0,5.8),color=(1.0,.94,.81))
area_emitter((2.5,.6,3.2),power=430,size=2.5,
             target=(0,0,5.7),color=(.85,.91,1.0))
area_emitter((-.5,2.3,3.9),power=240,size=1.6,
             target=(0,0,4.5),color=(1.0,.94,.80))

sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.render.resolution_x = 512
sc.render.resolution_y = 341
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .05
