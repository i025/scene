# Reference inventory, approximate normalized image bounds:
# - Blue rear wall (.10,.21)-(.70,.84), with vertical panel seams.
# - Blue right return (.69,.13)-(.91,.94), seams and exposed outer edge.
# - Light gray floor below the walls, with white rounded cove skirting.
# - Stainless double-door cabinet (.16,.40)-(.31,.83): two dark glazed
#   openings, shelves, central divider and handles.
# - Full-height dandelion mural (.37,.23)-(.64,.82), pale background,
#   darker stems and delicate seed structures. Fine details are uncertain.
# - Dark digital time/date display (.79,.35)-(.88,.51), on right wall.
# - Dark ceiling and exposed T-grid across upper image, with white LED
#   panels; some beams, hangers and services are partly hidden.
# - Numbered annotation markers are omitted.
#
# Feedback comparison: the initial view placed the rear corner too far
# right and the return wall continued beyond the frame; its lighting
# washed out the blue panels, cabinet glazing and mural. The ceiling was
# too light. This revision adjusts framing and the return depth, darkens
# the ceiling and surfaces, and strengthens the mural and cabinet detail.
# Estimated expanded primitive count: architecture 23, ceiling 28,
# cabinet 20, display 3, mural approximately 175 including sweep segments;
# total approximately 250. Geometry beyond the pictured edges is uncertain.

import math
import random
import bpy
from sceneact import *

random.seed(8)
scene = Scene("Clean laboratory")

blue = (0.025, 0.30, 0.49)
blue_right = (0.025, 0.27, 0.44)
joint = (0.025, 0.15, 0.22)
white = (0.77, 0.80, 0.78)
steel = (0.47, 0.52, 0.52)
dark = (0.12, 0.16, 0.16)
floor_color = (0.43, 0.47, 0.46)

room = Asset("Modular cleanroom enclosure")
room.include("floor", box((7.8, 6.0, .12), center=(2.1, -2.35, -.06), color=floor_color))
room.include("back_wall", box((4.85, .12, 3.0), center=(2.425, .06, 1.5), color=blue))
# The visible outside edge of the return terminates within the image.
return_depth = 2.05
room.include("right_wall", box((.12, return_depth, 3.0),
                                center=(4.86, -return_depth/2, 1.5), color=blue_right))
room.include("back_left_edge", box((.045, .14, 3.0), center=(0, 0, 1.5), color=(.55,.60,.59)))
room.include("return_outer_edge", box((.10, .08, 3.0),
                                     center=(4.86, -return_depth, 1.5), color=(.22,.27,.27)))
for i, x in enumerate((.48, 1.10, 1.68, 2.02, 3.94, 4.35)):
    room.include("back_joint_%d" % i, box((.012, .014, 2.92), center=(x, -.069, 1.5), color=joint))
for i, y in enumerate((-.45, -1.05, -1.62)):
    room.include("return_joint_%d" % i, box((.014, .012, 2.92), center=(4.785, y, 1.5), color=joint))
room.include("back_cove_base", box((4.83, .10, .10), center=(2.42,-.08,.05), color=white))
room.include("back_cove_curve", rod(.055, start=(.02,-.12,.055), end=(4.80,-.12,.055), color=white))
room.include("return_cove_base", box((.10, return_depth, .10),
                                     center=(4.78,-return_depth/2,.05), color=white))
room.include("return_cove_curve", rod(.055, start=(4.73,-.03,.055),
                                      end=(4.73,-return_depth,.055), color=white))
scene.include("architecture", room)

# Cabinet front is assembled from separate opaque dark glazing, metal frame,
# shelves and handles so that its two door openings remain easy to read.
cab = Asset("Stainless steel glass door cabinet")
cab.include("body", box((.99,.28,1.84), center=(1.0,-.19,.96), color=steel))
cab.include("dark_interior", box((.83,.018,1.65), center=(1.0,-.343,.97), color=(.105,.15,.15)))
for i, x in enumerate((.59, 1.00, 1.41)):
    cab.include("vertical_frame_%d" % i,
                box((.052,.055,1.78), center=(x,-.37,.97), color=(.72,.75,.73)))
for i, z in enumerate((.095, 1.845)):
    cab.include("horizontal_frame_%d" % i,
                box((.86,.055,.055), center=(1.0,-.37,z), color=(.72,.75,.73)))
for side, x in enumerate((.795,1.205)):
    cab.include("dark_glass_%d" % side,
                box((.34,.012,1.58), center=(x,-.378,.97), color=(.17,.22,.22)))
    for j,z in enumerate((.32,.62,.92,1.22,1.52)):
        cab.include("shelf_%d_%d" % (side,j),
                    box((.33,.012,.020), center=(x,-.39,z), color=(.52,.57,.55)))
for i,x in enumerate((.96,1.04)):
    cab.include("handle_%d" % i,
                rod(.010, start=(x,-.415,.87), end=(x,-.415,1.02), color=(.8,.82,.79)))
scene.include("cabinet", cab)

# Mural geometry, with pale cool field and warmer lower strip.
mural = Asset("Dandelion photographic wall graphic")
mural.include("pale_background", box((1.92,.025,2.84), center=(2.98,-.088,1.49), color=(.62,.72,.69)))
mural.include("warm_lower_band", box((1.92,.008,.32), center=(2.98,-.107,.24), color=(.69,.58,.40)))
for name,x in (("left",2.02),("right",3.94)):
    mural.include(name+"_border", box((.014,.015,2.84), center=(x,-.113,1.49), color=(.25,.35,.34)))
ink = (.15,.045,.12)
soft = (.22,.25,.21)
y = -.135
paths = [
 [(2.04,.12),(2.49,.40),(2.92,.68),(3.25,1.15),(3.39,1.64)],
 [(2.20,.11),(2.61,.27),(3.04,.48),(3.37,.83),(3.62,1.67)],
 [(3.91,.11),(3.56,.34),(3.27,.65),(2.98,1.04),(2.76,1.40)],
 [(3.89,.21),(3.50,.36),(3.10,.54),(2.76,.89),(2.58,1.18)],
 [(2.54,.10),(2.86,.32),(3.02,.70),(2.96,1.14),(2.78,2.55)],
 [(2.07,.29),(2.48,.32),(2.95,.40),(3.47,.55),(3.87,.66)],
 [(2.15,.12),(2.53,.20),(2.87,.17),(3.30,.24),(3.79,.13)],
]
for i,path in enumerate(paths):
    mural.include("stem_%d" % i, sweep_tube(points=[(x,y-i*.001,z) for x,z in path],
                                            radius=.013 if i<4 else .008, color=ink))
# Seed heads are loose radial filaments rather than solid flower disks.
heads = [(2.25,1.72,.57),(2.85,2.48,.69),(3.67,2.12,.70),
         (3.53,1.15,.56),(2.58,.74,.48)]
for h,(cx,cz,r) in enumerate(heads):
    mural.include("seed_center_%d" % h, ball(.025, center=(cx,y-.015,cz), color=ink))
    for j in range(19):
        a=2*math.pi*j/19 + h*.13
        ex=min(3.91,max(2.05,cx+r*math.cos(a)))
        ez=min(2.89,max(.10,cz+r*math.sin(a)))
        sx=cx+.035*math.cos(a)
        sz=cz+.035*math.sin(a)
        if abs(ex-sx)+abs(ez-sz) < .01:
            continue
        mural.include("seed_ray_%d_%d" % (h,j),
                      rod(.0035, start=(sx,y-.017,sz), end=(ex,y-.017,ez), color=soft))
        if j%3==0:
            dx=.055*math.cos(a+.75)
            dz=.055*math.sin(a+.75)
            mural.include("seed_tip_%d_%d" % (h,j),
                          rod(.0025, start=(ex-dx,y-.018,ez-dz),
                              end=(ex+dx,y-.018,ez+dz), color=(.30,.32,.27)))
scene.include("mural", mural)

display = Asset("Digital wall time and date display")
display.include("frame", box((.045,.75,.61), center=(4.765,-1.25,2.04), color=(.10,.14,.19)))
display.include("screen", box((.012,.69,.55), center=(4.735,-1.25,2.04), color=(.02,.055,.13)))
display.include("screen_rule", box((.008,.62,.008), center=(4.725,-1.25,1.89), color=(.24,.35,.42)))
scene.include("display", display)

ceiling = Asset("Exposed ceiling T grid and services")
ceiling.include("dark_ceiling", box((5.10,3.35,.10), center=(2.42,-1.53,3.08), color=(.105,.13,.13)))
for i,x in enumerate((0,.8,1.6,2.4,3.2,4.0,4.8)):
    ceiling.include("longitudinal_grid_%d" % i,
                    box((.025,3.25,.035), center=(x,-1.52,3.005), color=(.30,.35,.34)))
for i,yy in enumerate((-.15,-.75,-1.35,-1.95,-2.55,-3.10)):
    ceiling.include("cross_grid_%d" % i,
                    box((4.84,.025,.035), center=(2.42,yy,3.00), color=(.30,.35,.34)))
for i,(x,yy) in enumerate(((2.85,-.50),(.95,-2.35),(3.75,-2.75))):
    ceiling.include("LED_panel_%d" % i,
                    box((.71,.49,.025), center=(x,yy,2.974), color=(.87,.93,.92)))
for i,x in enumerate((.15,1.75,3.35,4.68)):
    ceiling.include("structure_beam_%d" % i,
                    box((.075,3.2,.12), center=(x,-1.5,3.19), color=(.18,.21,.20)))
for i,x in enumerate((.45,1.65,2.85,4.05)):
    ceiling.include("hanger_%d" % i,
                    rod(.012,start=(x,-.35,3.02),end=(x,-.35,3.32),color=steel))
ceiling.include("service_pipe", rod(.035,start=(.10,-.32,3.18),
                                    end=(4.70,-.32,3.18),color=(.27,.30,.29)))
scene.include("ceiling", ceiling)

realize(scene)

# Legible editable clock lettering on the wall-facing side of the display.
def clock_text(name, text, location, size):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi/2, 0, math.pi/2)
    mat = bpy.data.materials.get("Clock lettering")
    if mat is None:
        mat = bpy.data.materials.new("Clock lettering")
        mat.diffuse_color = (.53,.67,.73,1)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (.53,.67,.73,1)
        bsdf.inputs["Emission Color"].default_value = (.53,.67,.73,1)
        bsdf.inputs["Emission Strength"].default_value = .3
    obj.data.materials.append(mat)

clock_text("Time", "09:29:07", (4.716,-1.25,2.08), .105)
clock_text("Date", "2026.11.11", (4.715,-1.25,1.96), .043)

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
background.inputs["Color"].default_value = (.75,.78,.78,1)
background.inputs["Strength"].default_value = .32

for mat in bpy.data.materials:
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value = .58

for x,yy in ((2.85,-.50),(.95,-2.35),(3.75,-2.75)):
    area_emitter((x,yy,2.90), power=110, size=1.15,
                 target=(x,yy,0), color=(.91,.96,1))
area_emitter((1.8,-4.2,3.7), power=110, size=4,
             target=(2.4,-.5,1.3), color=(1,1,1))

set_view((1.65,-7.6,2.35), (2.65,-.10,1.43), lens=35, sensor=36)
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
