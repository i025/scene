# Reference and observed render anchors (normalized, visually estimated):
# Back corner at floor: reference (0.69, 0.80), render (0.69, 0.78).
# Cabinet: reference (0.16, 0.40)-(0.31, 0.83), render (0.15, 0.43)-(0.28, 0.79).
# Mural: reference (0.37, 0.24)-(0.64, 0.80), render (0.34, 0.23)-(0.57, 0.78).
# Foreground right cove endpoint: reference (0.91, 0.91); render extends beyond
# the right and bottom crop. The reference has an exposed right wall end.
# Ceiling: reference ends near y=.22; render ends near y=.22. Both have nearly
# horizontal back-wall edges and a right wall that recedes toward the corner.
#
# Ranked corrections:
# 1. Shorten FRONT from -3.10 to -2.05, moving the right-wall end and foreground
#    skirting endpoint up and left into frame, without moving the back corner.
# 2. The rendered walls, floor and mural are washed out. Reduce illumination and
#    use more saturated blue and darker grey finishes; light direction also affects
#    brightness. Keep the existing camera, which matches most architectural anchors.
# 3. Shift the mural right and widen it; increase the cabinet height and move it
#    slightly right. These change local bounds without shifting the wall corner.
# 4. The reference mural has dark crossing stems and broad translucent seed heads;
#    the render's pale lines leave the panel nearly blank. Strengthen and enlarge
#    these forms while preserving open gaps. Improve cabinet door contrast.
# The ceiling grid and back-wall/floor overlap are retained. Hidden services and
# the exact photographic detail are uncertain. The numbered markers are omitted.
# Primitive estimate: architecture 20, cabinet 20, mural about 130, screen 2,
# ceiling 32; roughly 205 meshes. No external image or projected texture is used.

import math
import random
import bpy
from mathutils import Vector
from sceneact import *

random.seed(24)
W, H = 5.40, 3.05
BACK, RIGHT, FRONT = 1.65, 2.70, -2.05
CAMERA_POSITION = (-0.15, -7.4, 1.90)
CAMERA_TARGET = (0.72, 1.35, 1.57)
CAMERA_LENS = 35.0

BLUE = (0.025, 0.30, 0.52)
BLUE_RIGHT = (0.025, 0.31, 0.52)
SEAM = (0.018, 0.19, 0.29)
FLOOR = (0.32, 0.36, 0.35)
COVE = (0.77, 0.82, 0.79)
STEEL = (0.48, 0.54, 0.53)
STEEL_LIGHT = (0.68, 0.73, 0.71)
GLASS = (0.07, 0.12, 0.12)
CEILING = (0.12, 0.15, 0.15)
RAIL = (0.39, 0.44, 0.43)

scene = Scene("Clean laboratory")
arch = Asset("Modular cleanroom architecture")
arch.include("grey floor", box((12,13,.12), center=(0,-2.4,-.07), color=FLOOR))
arch.include("blue back wall", box((W,.10,H), center=(0,BACK,H/2), color=BLUE))
arch.include("blue right wall", box((.10,BACK-FRONT,H),
    center=(RIGHT,(BACK+FRONT)/2,H/2), color=BLUE_RIGHT))
for i,x in enumerate((-2.10,-.80,.42,1.58,2.35)):
    arch.include("back panel seam %d"%i, box((.012,.012,H-.06),
        center=(x,BACK-.057,H/2),color=SEAM))
for i,y in enumerate((-1.65,-.70,.25,1.20)):
    arch.include("right panel seam %d"%i, box((.012,.012,H-.06),
        center=(RIGHT-.057,y,H/2),color=SEAM))
arch.include("back cove backing",box((W,.14,.10),
    center=(0,BACK-.12,.05),color=COVE))
arch.include("back cove round",rod(.065,start=(-W/2,BACK-.18,.06),
    end=(RIGHT-.12,BACK-.18,.06),color=COVE))
arch.include("right cove backing",box((.14,BACK-FRONT,.10),
    center=(RIGHT-.12,(BACK+FRONT)/2,.05),color=COVE))
arch.include("right cove round",rod(.065,start=(RIGHT-.18,FRONT,.06),
    end=(RIGHT-.18,BACK-.18,.06),color=COVE))
arch.include("right exposed edge",box((.08,.08,H+.05),
    center=(RIGHT,FRONT+.04,H/2),color=(.30,.35,.34)))
scene.include("architecture",arch)

# Full-height feature mural, assembled as a field and editable plant silhouettes.
mural = Asset("Dandelion feature wall")
MX0, MX1, MZ0, MZ1 = -.46, 1.67, .10, 3.00
MY = BACK-.066
mural.include("pale field",box((MX1-MX0,.014,MZ1-MZ0),
    center=((MX0+MX1)/2,MY,(MZ0+MZ1)/2),color=(.67,.79,.74)))
for i in range(6):
    mural.include("warm lower field %d"%i,box((MX1-MX0,.006,.125),
        center=((MX0+MX1)/2,MY-.012,.14+i*.12),
        color=(.67+.018*i,.49+.043*i,.36+.055*i)))
INK=(.14,.045,.10)
FINE=(.28,.34,.31)
stems=[
 ((-.40,.12),(.58,1.54)), ((-.31,.12),(.40,1.80)),
 ((-.02,.12),(1.02,1.45)), ((.22,.12),(.76,1.84)),
 ((.60,.12),(.10,1.37)), ((.88,.12),(.25,1.20)),
 ((1.35,.12),(.85,1.53)), ((1.50,.12),(.40,.90)),
 ((-.42,.43),(1.48,.78)), ((-.40,.78),(1.40,.28)),
 ((-.28,1.02),(.80,.54)), ((.30,.85),(1.04,1.52)),
 ((.05,1.33),(.95,.52)), ((.49,1.48),(.59,2.64)),
 ((-.38,1.20),(.40,.94)), ((.91,.15),(1.48,.57))
]
for i,(a,b) in enumerate(stems):
    mural.include("stem %02d"%i,rod(.014 if i<10 else .009,
        start=(a[0],MY-.030,a[1]),end=(b[0],MY-.030,b[1]),color=INK))
heads=[(-.20,2.62,.76),(.60,2.63,.77),(1.34,2.43,.62),
       (-.17,1.79,.55),(.93,1.65,.53),(1.35,1.05,.48),
       (-.12,.79,.48)]
for h,(cx,cz,r) in enumerate(heads):
    mural.include("seed center %d"%h,ball(.020,center=(cx,MY-.042,cz),color=INK))
    for j in range(20):
        a=2*math.pi*j/20+h*.19
        length=r*(.85+.15*random.random())
        ex,ez=cx+length*math.cos(a),cz+length*math.sin(a)
        if MX0+.015<ex<MX1-.015 and MZ0+.015<ez<MZ1-.015:
            mural.include("filament %d %02d"%(h,j),rod(.004,
                start=(cx+.07*math.cos(a),MY-.041,cz+.07*math.sin(a)),
                end=(ex,MY-.041,ez),color=FINE))
scene.include("feature mural",mural)

cabinet=Asset("Stainless glazed storage cabinet")
CAB_X,CAB_W,CAB_H,CAB_Y=-1.72,1.18,2.04,BACK-.095
cabinet.include("metal front",box((CAB_W,.10,CAB_H),
    center=(CAB_X,CAB_Y,CAB_H/2),color=STEEL_LIGHT))
for i,dx in enumerate((-.285,.285)):
    cabinet.include("dark glazed opening %d"%i,box((.37,.014,1.76),
        center=(CAB_X+dx,CAB_Y-.060,1.05),color=GLASS))
    for j,z in enumerate((.34,.65,.96,1.27,1.58,1.86)):
        cabinet.include("shelf %d %d"%(i,j),box((.34,.012,.018),
            center=(CAB_X+dx,CAB_Y-.071,z),color=(.42,.48,.46)))
    x=CAB_X+(-.055 if i==0 else .055)
    cabinet.include("pull %d"%i,rod(.013,start=(x,CAB_Y-.085,.92),
        end=(x,CAB_Y-.085,1.12),color=(.25,.30,.29)))
cabinet.include("center divider",box((.045,.025,CAB_H-.04),
    center=(CAB_X,CAB_Y-.065,CAB_H/2),color=STEEL))
cabinet.include("top cap",box((CAB_W+.04,.13,.055),
    center=(CAB_X,CAB_Y,CAB_H),color=STEEL_LIGHT))
scene.include("cabinet",cabinet)

screen=Asset("Digital time and date display")
SX,SY,SZ=RIGHT-.065,-1.00,2.06
screen.include("dark bezel",box((.035,.92,.61),
    center=(SX,SY,SZ),color=(.035,.065,.14)))
screen.include("blue face",box((.012,.84,.53),
    center=(SX-.025,SY,SZ),color=(.035,.10,.22)))
scene.include("digital display",screen)

ceiling=Asset("Exposed T-grid ceiling")
ceiling.include("dark ceiling field",box((8,10.5,.10),
    center=(0,-2.6,3.28),color=CEILING))
for i,x in enumerate((-3,-2.25,-1.5,-.75,0,.75,1.5,2.25,3)):
    ceiling.include("long grid rail %d"%i,box((.035,9.5,.035),
        center=(x,-2.2,3.08),color=RAIL))
for i,y in enumerate((-6,-5.15,-4.30,-3.45,-2.60,-1.75,-.90,-.05,.80,1.60)):
    ceiling.include("cross grid rail %d"%i,box((7,.035,.035),
        center=(0,y,3.08),color=RAIL))
for i,y in enumerate((-2.9,-.8,1.25)):
    ceiling.include("structural beam %d"%i,box((7,.13,.13),
        center=(0,y,3.23),color=(.25,.29,.28)))
for i,x in enumerate((-2.2,-.8,.8,2.2)):
    ceiling.include("suspension rod %d"%i,rod(.012,start=(x,.6,3.09),
        end=(x,.6,3.30),color=STEEL))
ceiling.include("service pipe",rod(.045,start=(-3,.9,3.21),
    end=(3,.9,3.21),color=(.32,.37,.36)))
for i,(x,y) in enumerate(((.70,.45),(-1.5,-2.1),(1.55,-3.7))):
    ceiling.include("LED panel %d"%i,box((.70,.70,.025),
        center=(x,y,3.055),color=(.92,.97,.96)))
ceiling.include("back fascia",box((W,.36,.055),
    center=(0,1.42,3.04),color=(.70,.74,.72)))
scene.include("ceiling",ceiling)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get("Background") or nodes.new("ShaderNodeBackground")
output=nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.80,.85,.84,1)
background.inputs["Strength"].default_value=.25

# The runner controls final output. Retain the input aspect for camera checks.
sc.render.resolution_x=512
sc.render.resolution_y=293
sc.render.resolution_percentage=100
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
landmarks=[
 ("back corner floor",(RIGHT-.12,BACK-.12,.08),(.69,.80)),
 ("mural upper left",(MX0,MY,MZ1),(.37,.24)),
 ("cabinet upper left",(CAB_X-CAB_W/2,CAB_Y-.06,CAB_H),(.16,.40)),
 ("right cove endpoint",(RIGHT-.12,FRONT,.08),(.91,.91))
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1))
        uv=None if clip.w<=1e-8 else (
            round(.5*(clip.x/clip.w+1),3),round(.5*(1-clip.y/clip.w),3))
        print(name,"reference",ref,"computed",uv)
projection_table("Retained camera")
# Small trial demonstrates camera aim direction; the supported local corrections
# retain the previous camera, so the trial is restored.
set_view(CAMERA_POSITION,(CAMERA_TARGET[0],CAMERA_TARGET[1],CAMERA_TARGET[2]+.08),
    lens=CAMERA_LENS)
projection_table("Trial upward aim")
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
bpy.context.view_layer.update()

def screen_text(name,text,location,size,color):
    curve=bpy.data.curves.new(name,"FONT")
    curve.body=text
    curve.align_x="CENTER"
    curve.align_y="CENTER"
    curve.size=size
    obj=bpy.data.objects.new(name,curve)
    sc.collection.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(math.pi/2,0,-math.pi/2)
    mat=bpy.data.materials.new(name+" material")
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*color,1)
        if "Emission Color" in bs.inputs:
            bs.inputs["Emission Color"].default_value=(*color,1)
            bs.inputs["Emission Strength"].default_value=.5
    curve.materials.append(mat)

screen_text("display time","09:29:07",(SX-.035,SY,SZ+.03),.125,(.67,.82,.88))
screen_text("display date","2026  11  11",(SX-.036,SY,SZ-.14),.042,(.53,.70,.78))
area_emitter((.70,.45,3.02),power=170,size=1.0,target=(.70,.45,0))
area_emitter((-1.50,-2.10,3.02),power=180,size=1.1,target=(-1.50,-2.10,0))
area_emitter((1.55,-3.70,3.02),power=180,size=1.1,target=(1.55,-3.70,0))
sc.render.engine="CYCLES"
sc.view_settings.view_transform="AgX"
