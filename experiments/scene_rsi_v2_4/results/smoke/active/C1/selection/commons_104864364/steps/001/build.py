from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized image bounds:
# Room: cream walls and ceiling, mustard lower wall band, tan tiled floor.
# Left openings .00-.31/.15-.58; right doors/windows .72-1/.12-.65.
# Raised stage .37-.66/.24-.46, dark red curtain, green side curtains,
# scalloped cream valance and a freestanding green chalkboard.
# Wooden desks/benches fill .00-.94/.42-.89 with substantial open leg gaps.
# Foreground left desk .14-.36/.59-.89, central desk .50-.71/.56-.82,
# right desk .76-.93/.53-.73. Bags below and beside several desks.
# Ceiling fans at .06-.26/.00-.09, .64-.87/.00-.09, and smaller fans deeper.
# Black wall speakers, portraits, fluorescent fixtures and exposed ceiling beams.
# Backstage detail and objects behind desks remain uncertain.
#
# Landmarks: floor/wall borders converge near (.51,.39); left yellow band
# runs from (0,.42) to (.36,.43), right band from (1,.46) to (.65,.40).
# Stage upper edge spans (.38,.24)-(.66,.24); board (.47,.33)-(.58,.42).
# Foreground left table corners approximately (.14,.61),(.35,.60),(.35,.67).
# Ceiling back intersection at y=.22; near fans are genuinely top-cropped.
# Camera horizon approximately .40, uncertain due to desk occlusions.
#
# Scale: meters. Room width 8.6, depth 15.6, height 4.5.
# Camera (0,-2,1.85), lens 25 mm; downward pitch about 5 degrees.
# Primitive estimate: architecture/openings ~125, 22 desk assemblies ~242,
# bags ~35, stage ~35, fans/lights/pictures ~80: approximately 520 meshes.
# No boolean work, fillet expansions, or dense repeated microstructure.

random.seed(8)
scene = Scene("Classroom")
cream = (.84, .83, .66)
white = (.94, .94, .85)
yellow = (.91, .69, .015)
wood = (.29, .22, .115)
edge = (.37, .30, .17)
topwood = (.27, .245, .17)
dark = (.035, .042, .034)
metal = (.22, .22, .18)

def cube(parent, name, size, center, color):
    obj = box(size=size, center=center, color=color)
    parent.include(name, obj)
    return obj

def beam(parent, name, a, b, r, color):
    obj = rod(radius=r, start=a, end=b, color=color)
    parent.include(name, obj)
    return obj

room = Asset("Architecture")
scene.include("Architecture", room)
cube(room, "Tiled_floor", (8.7,18,.12), (0,7,.0), (.64,.52,.32))
cube(room, "Left_cream_wall", (.15,16,4.5), (-4.37,7.8,2.25), cream)
cube(room, "Right_cream_wall", (.15,16,4.5), (4.37,7.8,2.25), cream)
cube(room, "Rear_wall", (8.7,.18,4.5), (0,15.7,2.25), cream)
cube(room, "Left_yellow_band", (.035,16,1.05), (-4.278,7.8,.55), yellow)
cube(room, "Right_yellow_band", (.035,16,1.05), (4.278,7.8,.55), yellow)
cube(room, "Rear_yellow_band", (8.6,.035,1.05), (0,15.58,.55), yellow)
cube(room, "Ceiling", (8.8,17,.15), (0,7.5,4.57), white)
for i,y in enumerate([2.2,7.1,11.8]):
    cube(room, "Ceiling_cross_beam_%d"%i, (8.6,.24,.26), (0,y,4.37), white)
for x in [-2.25,2.25]:
    cube(room, "Ceiling_long_beam_%s"%x, (.19,16,.16), (x,7.7,4.43), white)
for x in [-4.23,4.23]:
    cube(room, "Skirting_%s"%x, (.06,16,.12), (x,7.7,.12), (.43,.36,.19))

# Surface detail uses a single tile shader with restrained stone variation.
# The thin grid represents visible tile joints, without tile mesh proliferation.
def opening(side, y, width, kind, index):
    a = Asset("%s_%s_%02d"%(side,kind,index))
    scene.include(a.name, a)
    x = -4.265 if side == "Left" else 4.265
    sign = 1 if side == "Left" else -1
    if kind == "Window":
        z0, h = 1.30, 2.02
        cube(a,"Bright_glazing",(.027,width,h),(x,y,z0+h/2),(.86,.91,.88))
        # Tall brown window shutters and clear central aperture.
        for d in [-1,1]:
            cube(a,"Side_frame_%d"%d,(.10,.075,h+.18),(x+sign*.055,y+d*width/2,z0+h/2),wood)
            cube(a,"Shutter_%d"%d,(.075,width*.19,h*.87),(x+sign*.10,y+d*width*.39,z0+h*.47),(.32,.22,.105))
        for z in [z0,z0+h,z0+h*.78]:
            cube(a,"Crossbar_%s"%z,(.11,width+.1,.065),(x+sign*.055,y,z),wood)
        cube(a,"Center_mullion",(.09,.045,h),(x+sign*.07,y,z0+h/2),wood)
    else:
        h=2.8
        cube(a,"Door_leaf",(.06,width,h),(x+sign*.05,y,h/2),(.36,.25,.135))
        for d in [-1,1]:
            cube(a,"Door_jamb_%d"%d,(.14,.10,h+.12),(x+sign*.07,y+d*width/2,h/2),(.44,.32,.19))
        cube(a,"Door_header",(.14,width+.16,.12),(x+sign*.07,y,h),edge)
        for k in [-.28,.28]:
            cube(a,"Door_panel_%s"%k,(.025,width*.35,h*.75),(x+sign*.09,y+k*width,h*.48),(.43,.31,.17))
        cube(a,"Door_handle",(.075,.045,.12),(x+sign*.13,y+width*.32,1.25),(.65,.60,.39))

for i,(y,w,k) in enumerate([(1.15,1.35,"Window"),(3.65,1.0,"Door"),
                            (5.7,1.25,"Window"),(8.15,.95,"Door"),
                            (10.4,1.15,"Window"),(12.6,.85,"Door")]):
    opening("Left",y,w,k,i)
for i,(y,w,k) in enumerate([(1.5,1.0,"Door"),(4.3,1.4,"Window"),
                            (7.0,1.05,"Door"),(9.3,1.35,"Window"),
                            (12.1,1.05,"Door")]):
    opening("Right",y,w,k,i)

stage=Asset("Stage")
scene.include("Stage",stage)
cube(stage,"Platform",(5.35,2.05,.3),(-.05,14.45,.20),(.43,.32,.16))
cube(stage,"Dark_backdrop",(4.8,.10,2.65),(-.05,15.35,1.86),(.075,.026,.019))
cube(stage,"Proscenium_top",(5.5,.18,.20),(-.05,13.82,3.47),white)
for x in [-2.66,2.59]:
    cube(stage,"Green_side_curtain_%s"%x,(.43,.30,2.75),(x,14.03,2.03),(.075,.20,.07))
    cube(stage,"White_outer_pillar_%s"%x,(.13,.28,3.05),(x+(-.29 if x<0 else .29),13.9,1.72),white)
for i in range(11):
    x=-2.36+i*.46
    cube(stage,"Valance_panel_%02d"%i,(.47,.10,.31),(x,13.75,3.28),(.87,.84,.66))
    scallop=ball(radius=.235,center=(x,13.75,3.16),color=(.87,.84,.66))
    scallop.resize((1,.25,.55))
    stage.include("Valance_scallop_%02d"%i,scallop)
for i in range(7):
    cube(stage,"Curtain_fold_%d"%i,(.12,.10,2.2),(-1.95+i*.62,15.25,1.8),(.12,.045,.025))

board=Asset("Freestanding_chalkboard")
scene.include("Freestanding_chalkboard",board)
cube(board,"Green_writing_face",(2.05,.065,.98),(.12,13.15,1.43),(.095,.25,.18))
for x in [-.94,1.18]:
    cube(board,"Frame_vertical_%s"%x,(.055,.09,1.07),(x,13.11,1.43),(.39,.38,.28))
    beam(board,"Stand_%s"%x,(x,13.13,.27),(x,13.13,1.97),.024,metal)
    beam(board,"Foot_%s"%x,(x,12.83,.25),(x,13.55,.25),.025,metal)
for z in [.91,1.95]:
    cube(board,"Frame_horizontal_%s"%z,(2.17,.09,.055),(.12,13.11,z),(.42,.42,.30))
beam(board,"Diagonal_chalk_line",(-.72,13.07,1.04),(-.41,13.07,1.83),.008,(.65,.71,.59))
cube(stage,"Blue_side_notice",(.55,.08,1.27),(2.05,13.95,1.25),(.28,.65,.77))

def desk(name,x,y,w=1.65):
    a=Asset(name)
    scene.include(name,a)
    cube(a,"Desktop",(w,.63,.09),(x,y,.89),topwood)
    cube(a,"Front_apron",(w-.06,.065,.18),(x,y+.235,.75),edge)
    cube(a,"Book_shelf",(w-.15,.43,.055),(x,y,.59),(.27,.22,.13))
    for dx in [-w/2+.08,w/2-.08]:
        for dy in [-.23,.23]:
            cube(a,"Desk_leg_%s_%s"%(dx,dy),(.065,.065,.84),(x+dx,y+dy,.44),edge)
    # The paired bench sits behind its desktop, visible as a narrow horizontal strip.
    cube(a,"Bench_seat",(w-.08,.29,.075),(x,y+.75,.49),(.31,.26,.15))
    for dx in [-w/2+.15,w/2-.15]:
        cube(a,"Bench_leg_%s"%dx,(.07,.18,.46),(x+dx,y+.75,.24),edge)
    cube(a,"Bench_stretcher",(w-.25,.055,.065),(x,y+.75,.21),edge)
    return a

# Rows are offset and vary in width as in the photograph.
placements=[
(-1.85,2.35,1.75),(-3.9,3.8,1.45),
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
    pocket=ball(radius=1,center=(x,y-.125*scale,z+.22*scale),color=tuple(c*.82 for c in color))
    pocket.resize((.17*scale,.065*scale,.19*scale))
    a.include("Front_pocket",pocket)
    beam(a,"Zipper",(x-.12*scale,y-.18*scale,z+.35*scale),
         (x+.12*scale,y-.18*scale,z+.35*scale),.009*scale,(.46,.53,.48))
    beam(a,"Handle_left",(x-.07*scale,y,z+.59*scale),(x-.055*scale,y,z+.71*scale),.018*scale,dark)
    beam(a,"Handle_right",(x-.055*scale,y,z+.71*scale),(x+.065*scale,y,z+.60*scale),.018*scale,dark)
    beam(a,"Loose_strap",(x+.14*scale,y+.04,z+.48*scale),
         (x+.30*scale,y-.02,z+.035),.018*scale,dark)

bag("Foreground_black_backpack",-2.75,1.75,.08,(.018,.035,.055),1.1)
bag("Foreground_blue_backpack",1.24,2.55,.07,(.015,.29,.54),1.12)
bag("Central_dark_backpack",-.43,4.25,.07,(.025,.045,.06),.95)
bag("Right_turquoise_backpack",2.8,4.8,.07,(.015,.40,.54),1.0)
bag("Left_blue_bag",-2.85,6.0,.46,(.02,.28,.60),.7)
bag("Distant_blue_bag",1.8,9.8,.08,(.015,.28,.48),.7)
# Flat black satchel beneath foreground desk.
satchel=Asset("Satchel_under_left_desk")
scene.include("Satchel_under_left_desk",satchel)
cube(satchel,"Soft_case",(.66,.26,.14),(-1.65,2.3,.21),(.018,.023,.021))
beam(satchel,"Raised_handle",(-1.91,2.3,.27),(-1.63,2.3,.37),.014,dark)

# Small visible schoolbooks and papers on selected desktops.
props=Asset("Desktop_objects")
scene.include("Desktop_objects",props)
for i,(x,y) in enumerate([(-2.15,5.35),(-3.7,6.4),(.88,4.2),
                            (-1.9,9.25),(2.9,9.6),(-.25,11.5)]):
    cube(props,"Exercise_book_%d"%i,(.34,.23,.025),(x,y,.953),(.71,.67,.56))
    if i%2==0:
        cube(props,"Book_cover_%d"%i,(.36,.24,.012),(x,y,.975),(.32,.13,.19))

def fan(name,x,y,z,r):
    a=Asset(name)
    scene.include(name,a)
    beam(a,"Suspension",(x,y,4.45),(x,y,z+.05),.025,(.30,.28,.23))
    hub=ball(radius=.105,center=(x,y,z),color=(.20,.18,.145))
    hub.resize((1,1,.55))
    a.include("Motor_hub",hub)
    for k in range(3):
        ang=math.radians(18+120*k)
        cx=x+math.cos(ang)*r*.54
        cy=y+math.sin(ang)*r*.54
        blade=box(size=(r*.95,.16*r,.025),center=(cx,cy,z),color=(.25,.235,.20))
        blade.turn('z',math.degrees(ang))
        a.include("Blade_%d"%k,blade)
for i,(x,y,z,r) in enumerate([(-2.2,1.8,4.03,.87),(2.1,2.2,4.08,.90),
                              (-1.85,8.0,4.01,.63),(1.9,8.4,4.03,.62),
                              (0,13.0,4.02,.46)]):
    fan("Ceiling_fan_%d"%i,x,y,z,r)

fixtures=Asset("Fluorescent_lighting")
scene.include("Fluorescent_lighting",fixtures)
for i,(x,y) in enumerate([(-2.6,1.0),(0,5.5),(-1.6,10.7),(1.5,12.1)]):
    cube(fixtures,"Tube_housing_%d"%i,(1.18,.10,.07),(x,y,4.28),(.76,.77,.68))
    cube(fixtures,"White_tube_%d"%i,(1.09,.05,.035),(x,y,4.23),(.97,.98,.92))

decor=Asset("Wall_equipment_and_portraits")
scene.include("Wall_equipment_and_portraits",decor)
for i,(x,y,z) in enumerate([(-4.12,.3,3.35),(-4.12,11.6,3.3),(4.10,7.5,3.2),(4.10,13.3,3.15)]):
    speaker=cube(decor,"Black_speaker_%d"%i,(.26,.43,.70),(x,y,z),(.025,.055,.05))
    speaker.turn("y", -12 if x>0 else 12)
for i,(side,y,z) in enumerate([(-1,3.8,3.58),(-1,9.0,3.58),
                                 (1,3.8,3.62),(1,6.3,3.67),(1,11.1,3.62)]):
    x=side*4.25
    cube(decor,"Picture_frame_%d"%i,(.065,.50,.69),(x,y,z),(.44,.38,.22))
    cube(decor,"Picture_mat_%d"%i,(.075,.42,.60),(x-side*.03,y,z),(.87,.85,.69))
    portrait=ball(radius=1,center=(x-side*.08,y,z+.08),color=(.34,.34,.27))
    portrait.resize((.018,.12,.16))
    decor.include("Portrait_head_%d"%i,portrait)
    cube(decor,"Portrait_shoulders_%d"%i,(.025,.26,.20),(x-side*.08,y,z-.14),(.25,.30,.31))

realize(scene)

# A restrained procedural ceramic floor: warm rectangular tiles with pale grout.
floor_mat=bpy.data.materials.new("Warm mottled ceramic tiles")
floor_mat.use_nodes=True
nodes=floor_mat.node_tree.nodes
links=floor_mat.node_tree.links
bsdf=nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value=.62
tex=nodes.new("ShaderNodeTexCoord")
brick=nodes.new("ShaderNodeTexBrick")
brick.inputs["Color1"].default_value=(.62,.48,.28,1)
brick.inputs["Color2"].default_value=(.79,.66,.43,1)
brick.inputs["Mortar"].default_value=(.56,.49,.35,1)
brick.inputs["Scale"].default_value=2.5
brick.inputs["Mortar Size"].default_value=.012
brick.inputs["Mortar Smooth"].default_value=.008
brick.inputs["Brick Width"].default_value=.72
brick.inputs["Row Height"].default_value=.55
brick.offset=.5
links.new(tex.outputs["Object"],brick.inputs["Vector"])
noise=nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=38
noise.inputs["Detail"].default_value=2
links.new(tex.outputs["Object"],noise.inputs["Vector"])
mix=nodes.new("ShaderNodeMixRGB")
mix.blend_type='MULTIPLY'
mix.inputs[0].default_value=.15
links.new(brick.outputs["Color"],mix.inputs[1])
links.new(noise.outputs["Fac"],mix.inputs[2])
links.new(mix.outputs[0],bsdf.inputs["Base Color"])
for ob in bpy.data.objects:
    if ob.type=='MESH' and 'Tiled_floor' in ob.name:
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
background.inputs["Color"].default_value=(.86,.89,.80,1)
background.inputs["Strength"].default_value=.65

set_view(position=(0,-2,1.85),target=(.05,14,.48),lens=25,sensor=36,shift=(0,0))
area_emitter(position=(-3.9,3.3,2.9),power=750,size=3.0,target=(0,5,.3),color=(1,.96,.82))
area_emitter(position=(-3.9,9.0,2.9),power=650,size=3.0,target=(0,9,.5),color=(1,.97,.86))
area_emitter(position=(3.9,5.0,3.0),power=600,size=3.0,target=(0,6,.5),color=(1,.98,.88))
area_emitter(position=(0,5.0,4.22),power=450,size=5,target=(0,7,0),color=(1,.98,.9))
area_emitter(position=(0,12.0,4.15),power=350,size=4,target=(0,12,0),color=(1,.98,.9))
sc.view_settings.view_transform='AgX'
