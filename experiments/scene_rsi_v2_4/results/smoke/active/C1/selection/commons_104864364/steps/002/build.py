from sceneact import *
import bpy
import math

# Reference inventory and landmarks:
# Cream room, yellow lower walls, warm tiled floor; side openings occupy
# left x=0-.32 and right x=.70-1. Stage x=.37-.66, y=.24-.46.
# Green board x=.47-.58, y=.33-.42; dark curtain and pale scalloped valance.
# Desks have dark broad tops, thin legs and large gaps underneath.
# Foreground left desk x=.14-.36,y=.60-.89; central x=.51-.70,y=.56-.81;
# right x=.76-.93,y=.53-.73. Blue/black backpacks remain separate assets.
# Large ceiling fans near (.18,.04),(.74,.04), smaller fans deeper.
# Speakers, portraits, ceiling beams, fluorescent tubes and books are visible.
# Wall/floor lines converge around (.51,.39), with some occluded evidence.
# Near fans are cropped by the top border; nearest left desk is fully visible.
#
# Review: previous build executed successfully. Stage and board were too low,
# foreground left furniture and black bag extended too far left, fans were
# above the frame, and material appearance was excessively pale.
# Camera correction raises eye height and downward pitch together: predicts
# higher distant stage/board while retaining near desktop height approximately.
# Local foreground desk/bag placement and fan depth correct independent errors.
# Lower illumination and darker wood address appearance separately from geometry.
# The previous floor material lookup used semantic names absent from realized
# mesh names. Here the floor's material is assigned using its explicit bounds.
# Remaining uncertainties: exact room depth, window recesses, hidden furniture.
#
# Expanded primitive estimate: architecture/openings 110, stage/board 47,
# desks 242, bags 44, equipment/fans/pictures 65, props 12: about 520 meshes.
# No Boolean or fillet expansion; no render or file output in this program.

scene = Scene("Classroom")
cream=(.72,.72,.51)
white=(.83,.84,.73)
yellow=(.82,.57,.008)
wood=(.115,.065,.025)
edge=(.20,.135,.055)
topwood=(.105,.087,.051)
dark=(.012,.019,.018)
metal=(.12,.13,.10)

def cube(parent,name,size,center,color):
    o=box(size=size,center=center,color=color)
    parent.include(name,o)
    return o

def beam(parent,name,a,b,r,color):
    o=rod(radius=r,start=a,end=b,color=color)
    parent.include(name,o)
    return o

room=Asset("Architecture")
scene.include("Architecture",room)
cube(room,"Tiled_floor",(8.7,18,.12),(0,7,0),(.54,.39,.20))
cube(room,"Left_cream_wall",(.15,16,4.5),(-4.37,7.8,2.25),cream)
cube(room,"Right_cream_wall",(.15,16,4.5),(4.37,7.8,2.25),cream)
cube(room,"Rear_wall",(8.7,.18,4.5),(0,15.7,2.25),cream)
cube(room,"Left_yellow_band",(.035,16,1.05),(-4.278,7.8,.55),yellow)
cube(room,"Right_yellow_band",(.035,16,1.05),(4.278,7.8,.55),yellow)
cube(room,"Rear_yellow_band",(8.6,.035,1.05),(0,15.58,.55),yellow)
cube(room,"Ceiling",(8.8,17,.15),(0,7.5,4.57),white)
for i,y in enumerate([2.2,7.1,11.8]):
    cube(room,"Ceiling_cross_beam_%d"%i,(8.6,.24,.26),(0,y,4.37),white)
for x in [-2.25,2.25]:
    cube(room,"Long_beam_%s"%x,(.19,16,.16),(x,7.7,4.43),white)
for x in [-4.23,4.23]:
    cube(room,"Skirting_%s"%x,(.06,16,.12),(x,7.7,.12),(.29,.23,.10))

def opening(side,y,width,kind,index):
    a=Asset("%s_%s_%d"%(side,kind,index))
    scene.include(a.name,a)
    x=-4.265 if side=="Left" else 4.265
    s=1 if side=="Left" else -1
    if kind=="Window":
        z0,h=1.30,2.02
        cube(a,"Bright_glazing",(.027,width,h),(x,y,z0+h/2),(.82,.88,.85))
        for d in [-1,1]:
            cube(a,"Side_frame_%d"%d,(.10,.075,h+.18),
                 (x+s*.055,y+d*width/2,z0+h/2),wood)
            cube(a,"Shutter_%d"%d,(.075,width*.19,h*.87),
                 (x+s*.10,y+d*width*.39,z0+h*.47),(.19,.105,.035))
        for j,z in enumerate([z0,z0+h,z0+h*.78]):
            cube(a,"Crossbar_%d"%j,(.11,width+.1,.065),(x+s*.055,y,z),wood)
        cube(a,"Center_mullion",(.09,.045,h),(x+s*.07,y,z0+h/2),wood)
    else:
        h=2.8
        cube(a,"Door_leaf",(.06,width,h),(x+s*.05,y,h/2),(.22,.13,.055))
        for d in [-1,1]:
            cube(a,"Door_jamb_%d"%d,(.14,.10,h+.12),
                 (x+s*.07,y+d*width/2,h/2),(.28,.18,.075))
        cube(a,"Door_header",(.14,width+.16,.12),(x+s*.07,y,h),edge)
        for k in [-.28,.28]:
            cube(a,"Door_panel_%s"%k,(.025,width*.35,h*.75),
                 (x+s*.09,y+k*width,h*.48),(.27,.17,.07))
        cube(a,"Handle",(.075,.045,.12),(x+s*.13,y+width*.32,1.25),(.46,.40,.22))

for i,(y,w,k) in enumerate([
    (1.15,1.35,"Window"),(3.65,1.0,"Door"),(5.7,1.25,"Window"),
    (8.15,.95,"Door"),(10.4,1.15,"Window"),(12.6,.85,"Door")]):
    opening("Left",y,w,k,i)
for i,(y,w,k) in enumerate([
    (1.5,1.0,"Door"),(4.3,1.4,"Window"),(7.0,1.05,"Door"),
    (9.3,1.35,"Window"),(12.1,1.05,"Door")]):
    opening("Right",y,w,k,i)

stage=Asset("Stage")
scene.include("Stage",stage)
cube(stage,"Platform",(5.35,2.05,.3),(-.05,14.45,.20),(.27,.17,.065))
cube(stage,"Dark_backdrop",(4.8,.10,2.65),(-.05,15.35,1.86),(.035,.009,.005))
cube(stage,"Proscenium_top",(5.5,.18,.20),(-.05,13.82,3.47),white)
for x in [-2.66,2.59]:
    cube(stage,"Green_side_curtain_%s"%x,(.43,.30,2.75),
         (x,14.03,2.03),(.025,.13,.025))
    cube(stage,"Outer_pillar_%s"%x,(.13,.28,3.05),
         (x+(-.29 if x<0 else .29),13.9,1.72),white)
for i in range(11):
    x=-2.36+i*.46
    cube(stage,"Valance_panel_%d"%i,(.47,.10,.31),(x,13.75,3.28),(.74,.70,.50))
    o=ball(radius=.235,center=(x,13.75,3.16),color=(.74,.70,.50))
    o.resize((1,.25,.55))
    stage.include("Scallop_%d"%i,o)
for i in range(7):
    cube(stage,"Curtain_fold_%d"%i,(.12,.10,2.2),
         (-1.95+i*.62,15.25,1.8),(.065,.015,.008))
cube(stage,"Blue_side_notice",(.55,.08,1.27),(2.05,13.95,1.25),(.14,.49,.64))

board=Asset("Freestanding_chalkboard")
scene.include("Freestanding_chalkboard",board)
cube(board,"Writing_face",(2.05,.065,.98),(.12,13.15,1.43),(.045,.16,.105))
for x in [-.94,1.18]:
    cube(board,"Vertical_frame_%s"%x,(.055,.09,1.07),(x,13.11,1.43),(.22,.25,.17))
    beam(board,"Stand_%s"%x,(x,13.13,.27),(x,13.13,1.97),.024,metal)
    beam(board,"Foot_%s"%x,(x,12.83,.25),(x,13.55,.25),.025,metal)
for z in [.91,1.95]:
    cube(board,"Horizontal_frame_%s"%z,(2.17,.09,.055),(.12,13.11,z),(.26,.28,.19))
beam(board,"Chalk_line",(-.72,13.07,1.04),(-.41,13.07,1.83),.008,(.57,.65,.52))

def desk(name,x,y,w):
    a=Asset(name)
    scene.include(name,a)
    cube(a,"Desktop",(w,.63,.09),(x,y,.96),topwood)
    cube(a,"Front_apron",(w-.06,.065,.18),(x,y+.235,.82),edge)
    cube(a,"Book_shelf",(w-.15,.43,.055),(x,y,.62),(.13,.085,.035))
    for dx in [-w/2+.08,w/2-.08]:
        for dy in [-.23,.23]:
            cube(a,"Desk_leg_%s_%s"%(dx,dy),(.065,.065,.91),(x+dx,y+dy,.475),edge)
    cube(a,"Bench_seat",(w-.08,.29,.075),(x,y+.75,.49),(.16,.11,.045))
    for dx in [-w/2+.15,w/2-.15]:
        cube(a,"Bench_leg_%s"%dx,(.07,.18,.46),(x+dx,y+.75,.24),edge)
    cube(a,"Bench_stretcher",(w-.25,.055,.065),(x,y+.75,.21),edge)

placements=[
    (-1.65,2.75,1.52),(-3.9,3.8,1.45),
    (.95,4.2,1.85),(3.13,5.3,1.65),
    (-2.12,5.35,1.65),(-3.65,6.4,1.4),
    (.92,6.55,1.7),(2.85,7.7,1.5),
    (-2.05,7.45,1.62),(-.25,8.4,1.52),
    (.94,8.8,1.68),(-2.0,9.25,1.6),
    (2.9,9.6,1.45),(.98,10.45,1.6),
    (-1.95,10.8,1.55),(-.25,11.5,1.4),
    (2.85,11.4,1.4),(.95,12.0,1.5),
    (-1.9,12.15,1.5),(-3.7,8.8,1.3),
    (-3.6,11.0,1.25),(3.15,12.65,1.25)]
for i,(x,y,w) in enumerate(placements):
    desk("Pupil_desk_%02d"%i,x,y,w)

def bag(name,x,y,z,color,scale=1):
    a=Asset(name)
    scene.include(name,a)
    body=ball(radius=1,center=(x,y,z+.29*scale),color=color)
    body.resize((.22*scale,.145*scale,.35*scale))
    a.include("Fabric_body",body)
    pocket=ball(radius=1,center=(x,y-.125*scale,z+.22*scale),
                color=tuple(c*.76 for c in color))
    pocket.resize((.17*scale,.065*scale,.19*scale))
    a.include("Front_pocket",pocket)
    beam(a,"Zipper",(x-.12*scale,y-.18*scale,z+.35*scale),
         (x+.12*scale,y-.18*scale,z+.35*scale),.009*scale,(.25,.34,.31))
    beam(a,"Handle_left",(x-.07*scale,y,z+.59*scale),
         (x-.055*scale,y,z+.71*scale),.018*scale,dark)
    beam(a,"Handle_right",(x-.055*scale,y,z+.71*scale),
         (x+.065*scale,y,z+.60*scale),.018*scale,dark)
    beam(a,"Loose_strap",(x+.14*scale,y+.04,z+.48*scale),
         (x+.30*scale,y-.02,z+.035),.018*scale,dark)

bag("Foreground_black_backpack",-2.02,1.95,.08,(.006,.016,.032),1.1)
bag("Foreground_blue_backpack",1.12,2.55,.07,(.006,.13,.34),1.12)
bag("Central_dark_backpack",-.02,4.25,.07,(.008,.018,.028),.95)
bag("Right_turquoise_backpack",2.8,4.8,.07,(.005,.22,.34),1.0)
bag("Left_blue_bag",-2.85,6.0,.46,(.006,.12,.40),.7)
bag("Distant_blue_bag",1.8,9.8,.08,(.005,.14,.29),.7)

satchel=Asset("Satchel_under_left_desk")
scene.include("Satchel_under_left_desk",satchel)
cube(satchel,"Soft_case",(.66,.26,.14),(-1.45,2.7,.21),(.008,.012,.009))
beam(satchel,"Raised_handle",(-1.71,2.7,.27),(-1.43,2.7,.37),.014,dark)

props=Asset("Desktop_objects")
scene.include("Desktop_objects",props)
for i,(x,y) in enumerate([
    (-2.15,5.35),(-3.7,6.4),(.88,4.2),
    (-1.9,9.25),(2.9,9.6),(-.25,11.5)]):
    cube(props,"Exercise_book_%d"%i,(.34,.23,.025),(x,y,1.023),(.65,.62,.48))
    if i%2==0:
        cube(props,"Book_cover_%d"%i,(.36,.24,.012),(x,y,1.045),(.24,.035,.08))

def fan(name,x,y,z,r):
    a=Asset(name)
    scene.include(name,a)
    beam(a,"Suspension",(x,y,4.45),(x,y,z+.05),.025,(.17,.14,.09))
    o=ball(radius=.105,center=(x,y,z),color=(.085,.066,.037))
    o.resize((1,1,.55))
    a.include("Motor",o)
    for k in range(3):
        ang=18+120*k
        theta=math.radians(ang)
        o=box(size=(r*.95,.16*r,.025),
              center=(x+math.cos(theta)*r*.54,y+math.sin(theta)*r*.54,z),
              color=(.13,.10,.06))
        o.turn("z",ang)
        a.include("Blade_%d"%k,o)

for i,(x,y,z,r) in enumerate([
    (-3.05,4.0,4.03,.95),(2.30,4.3,4.08,1.0),
    (-1.85,9.5,4.01,.63),(1.9,9.9,4.03,.62),
    (0,13.0,4.02,.46)]):
    fan("Ceiling_fan_%d"%i,x,y,z,r)

fixtures=Asset("Fluorescent_lighting")
scene.include("Fluorescent_lighting",fixtures)
for i,(x,y) in enumerate([(-2.6,3.0),(0,5.5),(-1.6,10.7),(1.5,12.1)]):
    cube(fixtures,"Tube_housing_%d"%i,(1.18,.10,.07),(x,y,4.28),(.65,.67,.55))
    cube(fixtures,"White_tube_%d"%i,(1.09,.05,.035),(x,y,4.23),(.92,.94,.83))

decor=Asset("Wall_equipment_and_portraits")
scene.include("Wall_equipment_and_portraits",decor)
for i,(x,y,z) in enumerate([
    (-4.12,.3,3.35),(-4.12,11.6,3.3),(4.10,7.5,3.2),(4.10,13.3,3.15)]):
    o=cube(decor,"Speaker_%d"%i,(.26,.43,.70),(x,y,z),(.008,.025,.023))
    o.turn("y",-12 if x>0 else 12)
for i,(side,y,z) in enumerate([
    (-1,3.8,3.58),(-1,9.0,3.58),(1,3.8,3.62),
    (1,6.3,3.67),(1,11.1,3.62)]):
    x=side*4.25
    cube(decor,"Picture_frame_%d"%i,(.065,.50,.69),(x,y,z),(.25,.21,.09))
    cube(decor,"Picture_mat_%d"%i,(.075,.42,.60),(x-side*.03,y,z),(.75,.73,.55))
    o=ball(radius=1,center=(x-side*.08,y,z+.08),color=(.16,.18,.13))
    o.resize((.018,.12,.16))
    decor.include("Portrait_head_%d"%i,o)
    cube(decor,"Portrait_shoulders_%d"%i,(.025,.26,.20),
         (x-side*.08,y,z-.14),(.11,.15,.15))

realize(scene)

floor_mat=bpy.data.materials.new("Warm ceramic tile grid")
floor_mat.use_nodes=True
nodes=floor_mat.node_tree.nodes
links=floor_mat.node_tree.links
bsdf=nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value=.64
tex=nodes.new("ShaderNodeTexCoord")
brick=nodes.new("ShaderNodeTexBrick")
brick.inputs["Color1"].default_value=(.47,.31,.13,1)
brick.inputs["Color2"].default_value=(.67,.49,.25,1)
brick.inputs["Mortar"].default_value=(.44,.35,.22,1)
brick.inputs["Scale"].default_value=2.5
brick.inputs["Mortar Size"].default_value=.008
brick.inputs["Mortar Smooth"].default_value=.006
brick.inputs["Brick Width"].default_value=.72
brick.inputs["Row Height"].default_value=.55
brick.offset=.0
links.new(tex.outputs["Object"],brick.inputs["Vector"])
links.new(brick.outputs["Color"],bsdf.inputs["Base Color"])
for ob in bpy.data.objects:
    if ob.type=="MESH":
        if ob.dimensions.x>8.5 and ob.dimensions.y>17 and ob.dimensions.z<.2:
            ob.data.materials.clear()
            ob.data.materials.append(floor_mat)

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
background.inputs["Color"].default_value=(.78,.83,.76,1)
background.inputs["Strength"].default_value=.32

# Explicit camera: width 8.6, length 15.6, ceiling 4.5; eye 2.15 m.
# Downward pitch about 9.6 degrees; principal point remains unshifted.
set_view(position=(0,-2,2.15),target=(.05,14,-.55),
         lens=25,sensor=36,shift=(0,0))
area_emitter(position=(-3.9,3.3,2.9),power=450,size=3,
             target=(0,5,.3),color=(1,.96,.82))
area_emitter(position=(-3.9,9,2.9),power=350,size=3,
             target=(0,9,.5),color=(1,.97,.86))
area_emitter(position=(3.9,5,3),power=340,size=3,
             target=(0,6,.5),color=(1,.98,.88))
area_emitter(position=(0,5,4.22),power=180,size=5,
             target=(0,7,0),color=(1,.98,.9))
area_emitter(position=(0,12,4.15),power=100,size=4,
             target=(0,12,0),color=(1,.98,.9))
sc.view_settings.view_transform="AgX"
