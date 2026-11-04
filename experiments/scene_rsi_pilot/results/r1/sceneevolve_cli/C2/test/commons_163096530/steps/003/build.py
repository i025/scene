from sceneact import *
import bpy
import random

random.seed(13)

ROOM_W, ROOM_D, ROOM_H = 6.4, 7.6, 3.55
BACK_Y, LEFT_X = 4.65, -2.2
BED_W, BED_L = 1.18, 2.38
CAMERA_POSITION = (2.15, -5.35, 1.82)
CAMERA_TARGET = (-.30, 2.35, 1.18)
CAMERA_LENS = 36

scene = Scene(name="Historic bunk room")
plaster = (.62, .65, .35)
ceiling_color = (.56, .60, .39)
timber = (.045, .025, .010)
metal = (.028, .036, .034)
linen = (.86, .89, .86)
stone = (.36, .35, .27)
wood = (.25, .115, .035)

architecture = Asset("Plaster walls and ceiling")
architecture.include("back_wall",
    box((ROOM_W, .18, ROOM_H),
        center=(0, BACK_Y+.09, ROOM_H/2), color=plaster))
architecture.include("left_wall",
    box((.16, ROOM_D, ROOM_H),
        center=(LEFT_X-.08, .9, ROOM_H/2), color=(.66,.66,.45)))
architecture.include("ceiling",
    box((ROOM_W, ROOM_D, .14),
        center=(0,.9,ROOM_H+.07), color=ceiling_color))
scene.include("architecture", architecture)

floor = Asset("Long worn floorboards")
for i in range(23):
    x = -3.2+(i+.5)*.282
    split = random.uniform(.6,2.8)
    for j,(ya,yb) in enumerate(((-2.9,split),(split+.012,BACK_Y))):
        tint = random.uniform(.72,1.20)
        floor.include(f"board_{i}_{j}",
            box((.274,yb-ya,.075),
                center=(x,(ya+yb)/2,-.042),
                color=(.085*tint,.039*tint,.014*tint)))
scene.include("floorboards",floor)

beams = Asset("Exposed structural timbers")
for i,y in enumerate((-1.75,.3,2.3,4.48)):
    beams.include(f"wall_post_{i}",
        box((.145,.16,ROOM_H),
            center=(LEFT_X+.045,y,ROOM_H/2),color=timber))
for i,z in enumerate((1.95,3.38)):
    beams.include(f"wall_rail_{i}",
        box((.15,ROOM_D,.15),
            center=(LEFT_X+.045,.9,z),color=timber))
for i,y in enumerate((-.8,3.35)):
    beams.include(f"ceiling_crossbeam_{i}",
        box((ROOM_W,.23,.23),
            center=(0,y,ROOM_H-.08),color=timber))
scene.include("timbers",beams)

def make_bunk(name,cx,cy,width=BED_W,length=BED_L,
              bottom=.49,upper=1.84,height=2.35):
    a=Asset(name)
    x0,x1=cx-width/2,cx+width/2
    y0,y1=cy-length/2,cy+length/2
    for ix,x in enumerate((x0,x1)):
        for iy,y in enumerate((y0,y1)):
            a.include(f"post_{ix}_{iy}",
                rod(.027,start=(x,y,.04),end=(x,y,height),color=metal))
            a.include(f"foot_{ix}_{iy}",
                box((.10,.10,.025),center=(x,y,.025),color=metal))
            a.include(f"cap_{ix}_{iy}",
                ball(.032,center=(x,y,height),color=metal))
    for level,z in enumerate((bottom,upper)):
        a.include(f"deck_{level}",
            box((width,length,.065),center=(cx,cy,z),color=(.045,.055,.05)))
        for ix,x in enumerate((x0,x1)):
            a.include(f"long_frame_{level}_{ix}",
                rod(.024,start=(x,y0,z+.02),end=(x,y1,z+.02),color=metal))
        a.include(f"mattress_{level}",
            box((width-.075,length-.06,.145),
                center=(cx,cy,z+.10),color=linen))
        a.include(f"pillow_{level}",
            fillet_box((width*.73,.43,.15),radius=.065,
                center=(cx,y1-.33,z+.24),color=(.94,.94,.88)))
        a.include(f"folded_sheet_{level}",
            box((width-.065,.50,.055),center=(cx,y0+.34,z+.193),
                color=(.79,.84,.84)))
        for iy,y in enumerate((y0,y1)):
            for rail,h in enumerate((.29,.44)):
                a.include(f"end_rail_{level}_{iy}_{rail}",
                    rod(.018,start=(x0,y,z+h),end=(x1,y,z+h),color=metal))
        if level==1:
            for rail,h in enumerate((.29,.43)):
                a.include(f"side_guard_{rail}",
                    rod(.019,start=(x0,y0,z+h),end=(x0,y1,z+h),color=metal))
    ladder_y=y0+.53
    for k,y in enumerate((ladder_y-.22,ladder_y+.22)):
        a.include(f"ladder_upright_{k}",
            rod(.022,start=(x1+.018,y,.12),
                end=(x1+.018,y,upper+.42),color=metal))
    for k in range(6):
        z=.30+k*.30
        a.include(f"ladder_rung_{k}",
            rod(.018,start=(x1+.025,ladder_y-.22,z),
                end=(x1+.025,ladder_y+.22,z),color=metal))
    return a

scene.include("front_left_bunk",make_bunk("Main left bunk",-1.15,.60))
scene.include("rear_left_bunk",
    make_bunk("Rear left bunk",-1.25,2.72,width=1.12,length=2.24))

foreground=make_bunk("Foreground right bunk",3.22,-1.45,
    width=1.18,length=2.45,bottom=.47,upper=1.87,height=2.65)
foreground.include("warm_wood_end",
    box((.075,.10,2.65),center=(2.57,-2.66,1.325),color=(.45,.23,.07)))
scene.include("foreground_bunk",foreground)

wardrobe=Asset("Narrow oak wardrobe")
wx,wy,ww,wh,wd=-.05,4.25,.90,1.92,.48
for i,x in enumerate((wx-ww/2+.055,wx+ww/2-.055)):
    wardrobe.include(f"side_{i}",
        box((.085,wd,wh),center=(x,wy,wh/2+.06),color=wood))
    wardrobe.include(f"foot_{i}",
        box((.12,.36,.10),center=(x,wy,.05),color=(.23,.105,.035)))
wardrobe.include("back",
    box((ww,.05,wh),center=(wx,wy+wd/2-.025,wh/2+.06),
        color=(.12,.045,.012)))
for key,z,thick in (
    ("base",.15,.10),("middle_shelf",.72,.055),
    ("top",1.99,.09),("cornice",2.05,.055)):
    wardrobe.include(key,
        box((ww+(.10 if key=="cornice" else 0),wd+.055,thick),
            center=(wx,wy-.015,z),color=wood))
wardrobe.include("left_door",
    box((.40,.055,1.75),center=(wx-.225,wy-wd/2-.025,1.045),
        color=(.29,.14,.043)))
for i,z in enumerate((.55,1.48)):
    wardrobe.include(f"door_panel_{i}",
        box((.30,.018,.67),center=(wx-.225,wy-wd/2-.059,z),
            color=(.245,.105,.027)))
wardrobe.include("door_knob",
    ball(.022,center=(wx-.065,wy-wd/2-.09,1.04),color=(.15,.12,.055)))
wardrobe.include("hanging_rail",
    rod(.015,start=(wx+.025,wy-.06,1.81),
        end=(wx+.36,wy-.06,1.81),color=metal))
for i in range(3):
    x=wx+.08+i*.09
    wardrobe.include(f"hanger_{i}",
        rod(.009,start=(x,wy-.06,1.78),
            end=(x+.055,wy-.06,1.66),color=(.20,.17,.12)))
scene.include("wardrobe",wardrobe)

fireplace=Asset("Stone fireplace and dark hearth")
fx,fy=1.62,4.48
fireplace.include("recess",
    box((1.42,.10,1.15),center=(fx,fy-.025,.60),color=(.027,.024,.018)))
fireplace.include("hearth",
    box((2.02,.83,.07),center=(fx,fy-.37,.035),color=(.20,.18,.13)))
for i,x in enumerate((fx-.88,fx+.88)):
    fireplace.include(f"stone_jamb_{i}",
        box((.30,.29,1.15),center=(x,fy-.11,.61),color=stone))
fireplace.include("broad_top_lintel",
    box((2.07,.31,.26),center=(fx,fy-.11,1.30),color=(.40,.39,.29)))
fireplace.include("inner_top_lintel",
    box((1.48,.23,.14),center=(fx,fy-.19,1.12),color=(.30,.29,.21)))
for row in range(7):
    z=.16+row*.128
    for col in range(4):
        x=fx-.55+col*.31+(row%2)*.075
        if x<fx+.64:
            tint=random.uniform(.65,1.3)
            fireplace.include(f"brick_{row}_{col}",
                box((.28,.035,.105),center=(x,fy-.094,z),
                    color=(.065*tint,.055*tint,.038*tint)))
for i in range(3):
    fireplace.include(f"ash_log_{i}",
        rod(.038,start=(fx-.40+i*.24,fy-.30,.12),
            end=(fx-.13+i*.24,fy-.41,.14),color=(.035,.03,.02)))
fireplace.resize((1,1,1.15),pivot=(fx,fy,0))
fireplace.move((.20,0,0))
scene.include("fireplace",fireplace)

radiator=Asset("Small leaning hearth radiator")
for i in range(8):
    x=2.28+i*.036
    radiator.include(f"fin_{i}",
        rod(.012,start=(x,4.03,.10),end=(x-.07,4.11,.53),
            color=(.68,.71,.67)))
for i,z in enumerate((.13,.51)):
    radiator.include(f"crossbar_{i}",
        rod(.016,start=(2.25,4.06,z),end=(2.55,4.06,z),color=(.65,.68,.64)))
scene.include("radiator",radiator)

accessories=Asset("Room accessories")
accessories.include("coal_scuttle",
    rod(.10,start=(2.87,4.09,.04),end=(2.87,4.09,.29),color=(.025,.03,.025)))
accessories.include("poker",
    rod(.012,start=(2.94,4.10,.08),end=(2.94,4.10,.76),color=metal))
accessories.include("wall_plate",
    rod(.105,start=(.10,4.535,2.39),end=(.10,4.565,2.39),color=(.46,.55,.49)))
accessories.include("plate_center",
    ball(.016,center=(.10,4.51,2.39),color=(.65,.68,.56)))
for i,y in enumerate((.35,2.80)):
    accessories.include(f"bed_wall_fitting_{i}",
        box((.10,.12,.21),center=(LEFT_X+.125,y,2.44),color=(.16,.21,.17)))
scene.include("accessories",accessories)

realize(scene)

def textured_material(mat,kind):
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bsdf=nodes.get("Principled BSDF")
    if bsdf is None:
        return
    base=tuple(bsdf.inputs["Base Color"].default_value)
    coord=nodes.new("ShaderNodeTexCoord")
    mapping=nodes.new("ShaderNodeVectorMath")
    mapping.operation='MULTIPLY'
    mapping.inputs[1].default_value=(24,1.4,5) if kind=="wood" else (1,1,1)
    tex=nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=5 if kind=="wood" else 7
    tex.inputs["Detail"].default_value=3
    links.new(coord.outputs["Generated"],mapping.inputs[0])
    links.new(mapping.outputs[0],tex.inputs["Vector"])
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.18
    ramp.color_ramp.elements[1].position=.82
    ramp.color_ramp.elements[0].color=tuple(v*.55 for v in base[:3])+(1,)
    ramp.color_ramp.elements[1].color=tuple(min(v*1.15,1) for v in base[:3])+(1,)
    links.new(tex.outputs["Fac"],ramp.inputs[0])
    links.new(ramp.outputs[0],bsdf.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.19
    bump.inputs["Distance"].default_value=.025 if kind=="wood" else .018
    links.new(tex.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs[0],bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value=.76 if kind=="wood" else .87

for mat in list(bpy.data.materials):
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    r,g,b,_=bsdf.inputs["Base Color"].default_value
    if r>g*1.20 and g>b*1.18:
        textured_material(mat,"wood")
    elif .30<r<.77 and .29<g<.78 and b<.60:
        textured_material(mat,"plaster")
    elif max(r,g,b)<.08 and abs(r-g)<.016:
        bsdf.inputs["Metallic"].default_value=.65
        bsdf.inputs["Roughness"].default_value=.30
    else:
        bsdf.inputs["Roughness"].default_value=.84

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
world_scene=bpy.context.scene
if world_scene.world is None:
    world_scene.world=bpy.data.worlds.new("Room ambient")
world_scene.world.use_nodes=True
background=world_scene.world.node_tree.nodes["Background"]
background.inputs["Color"].default_value=(.65,.72,.78,1)
background.inputs["Strength"].default_value=.22
area_emitter((-2.3,-3.4,3.1),power=1050,size=2.5,
    target=(-1.1,1.6,.6),color=(.91,.95,1.0))
area_emitter((2.7,1.0,3.05),power=100,size=3.0,
    target=(.5,3.8,1.0),color=(1.0,.91,.70))
world_scene.view_settings.view_transform='AgX'

# Source audit:
# All dimensions/radii are positive; rod endpoints are distinct keyword arguments.
# Pillow radius .065 <= half the minimum dimension (.075).
# Repeated include keys contain loop indices.
# Fireplace scaling uses an explicit floor pivot.
# Editable parts remain inside meaningful SceneAct assets.
# Camera, lighting and material customization follow realize().
# No external files, rendering, saving, or runner settings are accessed.
