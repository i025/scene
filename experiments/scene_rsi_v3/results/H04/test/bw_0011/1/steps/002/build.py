# Reference inventory, normalized image coordinates (visual estimates):
# Floor foreground: (0,.80)-(1,1); wall/floor corner near (.70,.79).
# Back blue wall: (.10,.22)-(.70,.84), vertical panel joints.
# Stainless double-door cabinet: (.16,.40)-(.31,.84), dark glazed openings
# and horizontal shelves; it overlaps the blue wall.
# Dandelion mural: (.37,.24)-(.64,.80), pale upper region, warm base,
# dark intersecting stems and translucent-looking seed heads.
# Right blue wall: (.64,.14)-(.91,.93), clock at (.79,.33)-(.88,.51).
# Dark exposed ceiling and T-grid occupy the upper ~.23 of the image;
# bright LED panels sit near its back edge. White coved skirting follows
# both walls, with the right-hand segment sloping down toward the right.
# Structural services and the parts outside the image remain uncertain.
#
# Previous render versus reference: back-wall lower left approximately
# (.27,.69) versus (.10,.84); mural top-left (.42,.32) versus (.37,.24);
# back corner upper (.64,.30) versus (.64,.25); right foreground lower
# (.73,.94) versus (.91,.93); screen center (.64,.44) versus (.84,.42).
# The previous room is too small in frame, the right wall is too narrow,
# and the mural lacks the reference's dark lower density. The broad floor
# edge, cabinet openings, ceiling crop, and vertical wall joints are retained.
# Corrections, ranked by visible extent:
# 1. Increase lens from 27 to 37 mm to expand the room in frame; aim a
#    little right to keep the back corner near its reference position.
# 2. Move the screen forward along the right wall and extend that wall
#    forward, moving the screen and front base contour to the right.
# 3. Enlarge the cabinet slightly and increase mural stem/seed coverage.
# 4. Add a white ceiling perimeter band and restrained visible services.
# A numerical trial compares the old and new cameras. Computed projections
# are geometry-point checks, separate from the observed image contours.
#
# Estimated expanded primitive meshes: room and trim 27, cabinet 25,
# mural approximately 150, screen 4, ceiling and services 38; total ~244.
# Text objects are additional. No external files or image textures are used.

import math
import random
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

random.seed(16)

# Dimensions and camera parameters are independently editable.
LEFT = -3.30
CORNER = 2.05
BACK = 2.0
FRONT = -3.8
HEIGHT = 3.15
OLD_CAMERA = (0.25, -8.5, 2.65)
OLD_TARGET = (0.15, 1.55, 1.60)
OLD_LENS = 27.0
CAMERA_POSITION = (0.25, -8.5, 2.65)
CAMERA_TARGET = (0.61, 1.55, 1.62)
CAMERA_LENS = 37.0

blue = (.045, .43, .67)
joint = (.025, .29, .43)
white = (.81, .85, .83)
steel = (.56, .61, .60)
darksteel = (.20, .25, .25)
floor_color = (.49, .53, .52)
dark_ceiling = (.10, .13, .14)

scene = Scene("Clean laboratory corner")
room = Asset("Modular room")
room.include("self levelling floor", box((10, 11, .10),
    center=(0, -.8, -.06), color=floor_color))
room.include("back wall", box((CORNER-LEFT, .10, HEIGHT),
    center=((LEFT+CORNER)/2, BACK, HEIGHT/2), color=blue))
room.include("right wall", box((.10, BACK-FRONT, HEIGHT),
    center=(CORNER, (BACK+FRONT)/2, HEIGHT/2), color=blue))
for i, x in enumerate([-2.72, -1.55, -.50, .55, 1.55, 1.91]):
    room.include("back vertical joint %02d" % i,
        box((.012, .012, HEIGHT-.10),
            center=(x, BACK-.057, HEIGHT/2), color=joint))
for i, y in enumerate([1.58, .80, .02, -.76, -1.54, -2.32, -3.10, -3.75]):
    room.include("right vertical joint %02d" % i,
        box((.012, .012, HEIGHT-.10),
            center=(CORNER-.057, y, HEIGHT/2), color=joint))
room.include("back base", box((CORNER-LEFT, .18, .13),
    center=((LEFT+CORNER)/2, BACK-.10, .065), color=white))
room.include("back rounded cove", rod(.075,
    start=(LEFT, BACK-.18, .075), end=(CORNER, BACK-.18, .075), color=white))
room.include("right base", box((.18, BACK-FRONT, .13),
    center=(CORNER-.10, (BACK+FRONT)/2, .065), color=white))
room.include("right rounded cove", rod(.075,
    start=(CORNER-.18, FRONT, .075),
    end=(CORNER-.18, BACK, .075), color=white))
room.include("right outer metal edge", box((.075,.075,HEIGHT),
    center=(CORNER, FRONT, HEIGHT/2), color=(.35,.39,.38)))
scene.include("architecture", room)

# Graphic is interpreted with geometry and a procedural color gradient,
# rather than using the source image as a texture.
art = Asset("Dandelion feature wall")
AX0, AX1 = -1.02, .91
AZ0, AZ1 = .14, 3.03
AY = BACK-.078
art.include("mural ground", box((AX1-AX0,.024,AZ1-AZ0),
    center=((AX0+AX1)/2,AY,(AZ0+AZ1)/2), color=(.79,.89,.84)))
# Warm bottom, with several soft color bands kept subordinate to stems.
for i in range(5):
    h = .105
    art.include("warm base band %d" % i,
        box((AX1-AX0,.005,h+.002),
            center=((AX0+AX1)/2,AY-.016,AZ0+h*(i+.5)),
            color=[(.48,.31,.27),(.62,.49,.35),(.74,.67,.48),
                   (.80,.76,.59),(.82,.83,.69)][i]))

def line2(name, a, b, radius, color):
    art.include(name, rod(radius, start=(a[0],AY-.026,a[1]),
        end=(b[0],AY-.026,b[1]), color=color))

purple = (.19,.055,.15)
muted = (.37,.39,.34)
stems = [
    ((-.98,.18),(.23,1.43)), ((-.95,.35),(.73,.70)),
    ((-.65,.14),(.65,1.04)), ((-.10,.14),(.30,1.58)),
    ((.80,.18),(.12,1.38)), ((.89,.42),(.42,1.45)),
    ((-.96,.82),(.08,.50)), ((-.40,.20),(-.70,1.13)),
    ((.35,.16),(-.23,.85)), ((-.18,1.15),(-.46,2.72)),
    ((.18,1.45),(.63,1.87)), ((-.02,1.33),(-.72,1.58)),
    ((-.99,.49),(.58,.28)), ((-.83,.18),(.87,.53)),
    ((-.72,.14),(.16,.95)), ((.80,.15),(-.28,.64)),
    ((-.96,.26),(.46,.59)), ((-.56,.15),(.75,.38)),
]
for i, (a,b) in enumerate(stems):
    line2("crossing stem %02d" % i, a, b, .009 if i < 12 else .005, purple)

heads = [(-.48,2.72,.55),(.51,2.82,.57),(-.92,1.72,.56),
         (.84,1.55,.49),(-.73,.72,.48),(.42,.60,.44),
         (.09,.30,.40)]
for j,(hx,hz,r) in enumerate(heads):
    for k in range(18):
        angle = 2*math.pi*k/18 + .13*j
        x1 = hx + .035*math.cos(angle)
        z1 = hz + .035*math.sin(angle)
        x2 = hx + r*math.cos(angle)
        z2 = hz + r*math.sin(angle)
        if AX0+.015 < x2 < AX1-.015 and AZ0+.015 < z2 < AZ1-.015:
            line2("seed filament %d %02d" % (j,k),
                  (x1,z1),(x2,z2),.0022,muted)
scene.include("feature wall", art)

cab = Asset("Stainless steel glazed double cabinet")
CX, CY, CW, CH, CZ = -2.15, BACK-.19, 1.08, 1.98, 1.06
cab.include("cabinet outer body", box((CW,.28,CH),
    center=(CX,CY+.07,CZ),color=steel))
cab.include("cabinet dark interior", box((CW-.15,.025,CH-.16),
    center=(CX,CY-.081,CZ),color=darksteel))
for i,x in enumerate([CX-CW/2+.045,CX,CX+CW/2-.045]):
    cab.include("vertical frame %d" % i, box((.07,.055,CH-.07),
        center=(x,CY-.12,CZ),color=steel))
for i,z in enumerate([CZ-CH/2+.04,CZ+CH/2-.04]):
    cab.include("horizontal frame %d" % i, box((CW,.055,.075),
        center=(CX,CY-.12,z),color=steel))
for i,z in enumerate([.38,.67,.96,1.25,1.54,1.83]):
    cab.include("interior shelf %d" % i, box((CW-.14,.12,.025),
        center=(CX,CY-.10,z),color=(.72,.76,.73)))
for i,x in enumerate([CX-.26,CX+.26]):
    cab.include("glazed door %d" % i, box((.40,.014,CH-.20),
        center=(x,CY-.156,CZ),color=(.22,.31,.31),opacity=.30))
for i,x in enumerate([CX-.052,CX+.052]):
    cab.include("handle %d" % i, rod(.011,
        start=(x,CY-.20,.94),end=(x,CY-.20,1.13),color=(.85,.88,.86)))
scene.include("storage cabinet",cab)

monitor = Asset("Wall mounted digital clock")
MY, MZ = -1.15, 2.12
monitor.include("dark bezel",box((.055,.80,.64),
    center=(CORNER-.085,MY,MZ),color=(.045,.07,.12)))
monitor.include("blue display face",box((.012,.72,.56),
    center=(CORNER-.119,MY,MZ),color=(.025,.09,.19)))
scene.include("clock display",monitor)

ceiling = Asset("T grid ceiling and exposed structure")
ceiling.include("dark overhead slab",box((8,8,.12),
    center=(0,-.3,3.61),color=dark_ceiling))
# White edge fascia and light-colored ceiling tiles behind the grid.
ceiling.include("back perimeter fascia",box((6.8,.50,.07),
    center=(0,1.86,3.23),color=(.69,.73,.71)))
ceiling.include("right perimeter fascia",box((.48,5.8,.07),
    center=(1.79,-.75,3.23),color=(.70,.74,.72)))
for i,x in enumerate([-3.2,-2.5,-1.8,-1.1,-.4,.3,1.0,1.7,2.4,3.1]):
    ceiling.include("longitudinal T rail %d" % i,box((.035,7.4,.045),
        center=(x,-.5,3.28),color=(.29,.37,.38)))
for i,y in enumerate([-3.6,-2.9,-2.2,-1.5,-.8,-.1,.6,1.3,2.0]):
    ceiling.include("transverse T rail %d" % i,box((7.0,.035,.045),
        center=(0,y,3.28),color=(.29,.37,.38)))
for i,x in enumerate([-2.5,-1.1,.3,1.7]):
    ceiling.include("structural beam %d" % i,box((.11,7,.18),
        center=(x,-.4,3.51),color=(.16,.20,.20)))
    for j,y in enumerate([-.9,1.1]):
        ceiling.include("hanger %d %d" % (i,j),rod(.012,
            start=(x,y,3.30),end=(x,y,3.59),color=darksteel))
for i,x in enumerate([-.5,1.0]):
    ceiling.include("LED panel %d" % i,box((.66,.66,.035),
        center=(x,1.25,3.245),color=(.91,.97,.96)))
for i,y in enumerate([-.7,.65]):
    ceiling.include("exposed service pipe %d" % i,rod(.025,
        start=(-3.2,y,3.46),end=(2.8,y,3.46),color=(.26,.31,.31)))
scene.include("ceiling",ceiling)

realize(scene)

def material(name,color,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=.45
    if emission and "Emission Color" in p.inputs:
        p.inputs["Emission Color"].default_value=(*color,1)
        p.inputs["Emission Strength"].default_value=emission
    return m

text_material=material("Display lettering",(.52,.72,.80),.3)
def screen_text(name,body,y,z,size):
    curve=bpy.data.curves.new(name,"FONT")
    curve.body=body
    curve.size=size
    curve.align_x="CENTER"
    curve.align_y="CENTER"
    obj=bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(obj)
    obj.location=(CORNER-.13,y,z)
    obj.rotation_euler=(math.pi/2,0,-math.pi/2)
    obj.data.materials.append(text_material)
screen_text("Time","09:23:07",MY,MZ+.06,.105)
screen_text("Date","2026 / 11 / 11",MY,MZ-.10,.042)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.68,.74,.77,1)
background.inputs["Strength"].default_value=.55

# Original image aspect is retained for camera projection and final framing.
sc.render.resolution_x=512
sc.render.resolution_y=293
sc.render.resolution_percentage=100
landmarks=[
    ("back lower left",(LEFT,BACK,0),(.10,.84)),
    ("mural upper left",(AX0,AY,AZ1),(.37,.24)),
    ("back corner upper",(CORNER,BACK,HEIGHT),(.64,.25)),
    ("right front lower",(CORNER,FRONT,0),(.91,.93)),
    ("screen center",(CORNER-.13,MY,MZ),(.84,.42)),
]
def projections(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,point,ref in landmarks:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*point,1))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print(name,"reference",ref,"projected",
              None if uv is None else tuple(round(v,3) for v in uv))

set_view(OLD_CAMERA,OLD_TARGET,lens=OLD_LENS)
projections("Previous camera")
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
projections("Revised camera")

# Broad lights placed at the ceiling panel positions provide even illumination.
area_emitter((-.5,1.2,3.19),power=400,size=1.1,target=(-.5,.5,0))
area_emitter((1.0,1.2,3.19),power=400,size=1.1,target=(.5,.3,0))
area_emitter((-1.5,-1.0,3.18),power=350,size=2.5,target=(-.5,1,1))
