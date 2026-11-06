from sceneact import *
import bpy
import math
import random

# Reference inventory (normalized image bounds, estimated from the photograph):
# Architecture: carpet (0,.59)-(1,1), cream back wall (.11,.37)-(.53,.61),
# right wall (.52,0)-(1,.85), bright left partition (0,.32)-(.12,.67).
# Suspended ceiling spans the upper image; a few missing left-edge tiles reveal
# dark cavities and bent grid members. Tile seams converge toward the back.
# Whiteboard: (.59,.26)-(.92,.59), long right-wall rectangle with aluminum frame,
# a central division, and a narrow lower tray. No evidenced writing.
# Flag: (.45,.32)-(.51,.43), hanging beneath an angled pole near the back corner.
# Back-wall fixtures: gray vent (.15,.44)-(.25,.48), open electrical box,
# displaced gray cover, and two small pale labels near (.32,.48).
# Floor debris: dark broken ceiling panels mainly left/center (.02,.64)-(.43,.81),
# narrow metal rails, and overlapping ochre insulation sheets (.56,.67)-(.90,.79).
# Shapes and depths remain approximate; no furniture is visible.
#
# Local profiles, instance placement, and camera parameters are kept separate.
# Approximately 180 SceneAct primitive meshes, including ceiling panels and seams;
# flag uses 13 separately editable stripes plus canton, with no dense microgeometry.

scene = Scene("Damaged classroom")
cream = (.70,.68,.60)
ceiling_color = (.65,.68,.67)
grid_color = (.48,.52,.51)
dark = (.065,.08,.077)
metal = (.48,.53,.54)

def add_box(parent, name, size, center, color):
    obj = box(size=size, center=center, color=color)
    parent.include(name, obj)
    return obj

def place(asset, name, position, rotation=(0,0,0)):
    asset.turn(euler=rotation, pivot=(0,0,0))
    asset.move(position)
    scene.include(name, asset)
    return asset

room = Asset("Room shell")
add_box(room, "Carpet slab", (5.5,12,.12), (-.25,-2,-.06), (.115,.125,.112))
add_box(room, "Rear plaster", (5.6,.15,3.9), (-.25,4.075,1.95), cream)
add_box(room, "Right plaster", (.15,12,3.9), (2.575,-2,1.95), (.76,.735,.66))
add_box(room, "Left wall", (.12,12,3.9), (-3.06,-2,1.95), (.78,.79,.75))
add_box(room, "Rear dark skirting", (5.5,.045,.13), (-.25,3.985,.065), dark)
add_box(room, "Right dark skirting", (.045,12,.14), (2.485,-2,.07), dark)
scene.include("Architecture", room)

# Independent ceiling tile instances; the dark plenum is visible through omissions.
ceiling = Asset("Suspended ceiling")
add_box(ceiling, "Dark plenum above openings", (5.5,12,.07), (-.25,-2,4.09), (.08,.105,.105))
tile_w, tile_d = .61,1.22
for ix in range(9):
    for iy in range(10):
        x = -3 + (ix+.5)*tile_w
        y = -8 + (iy+.5)*tile_d
        missing = ix == 0 and iy in (5,6,7)
        if not missing:
            c = (.66+.012*((ix+iy)%3), .69+.009*((ix+iy)%3), .68)
            add_box(ceiling, "Acoustic tile %02d %02d"%(ix,iy),
                    (tile_w-.013,tile_d-.013,.035),(x,y,3.9),c)
for ix in range(10):
    add_box(ceiling,"Long grid %d"%ix,(.014,12.2,.023),
            (-3+ix*tile_w,-1.9,3.875),grid_color)
for iy in range(11):
    add_box(ceiling,"Cross grid %d"%iy,(5.49,.014,.023),
            (-.255,-8+iy*tile_d,3.875),grid_color)
scene.include("Ceiling grid and panels",ceiling)

# A pair of inset translucent fluorescent panels.
for i,y in enumerate((-1.3,1.14)):
    fixture=Asset("Fluorescent ceiling fixture")
    add_box(fixture,"Metal rim",(.59,1.19,.03),(0,0,0),(.55,.59,.58))
    add_box(fixture,"Clouded diffuser",(.55,1.14,.015),(0,0,-.024),(.78,.82,.81))
    place(fixture,"Ceiling light %d"%i,(-1.78,y,3.866))

# Whiteboard local frame: thin dimension along local X, length along local Y.
board=Asset("Wall whiteboard")
board_length, board_height = 3.45,1.83
add_box(board,"White enamel surface",(.034,board_length,board_height),(0,0,0),(.78,.80,.79))
for y in (-board_length/2,board_length/2):
    add_box(board,"Vertical frame %.2f"%y,(.057,.035,board_height+.06),(-.018,y,0),metal)
for z in (-board_height/2,board_height/2):
    add_box(board,"Horizontal frame %.2f"%z,(.06,board_length+.035,.035),(-.018,0,z),metal)
add_box(board,"Panel joining strip",(.042,.018,board_height),(-.025,.52,0),(.68,.71,.70))
add_box(board,"Marker ledge",(.105,board_length,.035),(-.065,0,-board_height/2-.025),metal)
place(board,"Whiteboard on right wall",(2.455,.97,2.22))

# Bright flat partitions along the left side.
partition=Asset("Left pale partition panels")
for i in range(6):
    add_box(partition,"Panel %d"%i,(.035,1.12,2.85),(0,i*1.13,1.425),(.87,.88,.85))
    add_box(partition,"Vertical joint %d"%i,(.043,.013,2.85),(-.006,i*1.13-.56,1.425),(.70,.73,.72))
place(partition,"Left partitions",(-2.985,-3.25,0))

fixtures=Asset("Back wall fittings")
add_box(fixtures,"Vent dark inset",(.98,.025,.40),(-2.05,3.97,2.15),(.31,.37,.38))
for i in range(7):
    add_box(fixtures,"Vent horizontal louver %d"%i,(.92,.025,.008),
            (-2.05,3.948,1.985+i*.047),(.39,.43,.43))
add_box(fixtures,"Electrical cabinet rim",(.34,.07,.47),(-.72,3.945,1.85),(.48,.52,.50))
add_box(fixtures,"Open cabinet dark interior",(.27,.018,.38),(-.72,3.898,1.85),(.16,.20,.19))
add_box(fixtures,"Cabinet internal plate",(.12,.025,.25),(-.72,3.878,1.86),(.61,.64,.59))
fixtures.include("Exposed cabinet wire",rod(radius=.012,start=(-.80,3.85,1.98),end=(-.77,3.85,1.75),color=(.13,.16,.15)))
cover=box(size=(.52,.045,.43),center=(0,0,0),color=(.40,.46,.44))
cover.turn("y",38,pivot=(0,0,0))
cover.move((-.46,3.84,1.48))
fixtures.include("Hanging tilted cabinet door",cover)
for i in range(2):
    add_box(fixtures,"Wall label %d"%i,(.15,.014,.21),(.04+i*.24,3.973,1.51+i*.04),(.79,.79,.71))
    add_box(fixtures,"Label print %d"%i,(.083,.009,.025),(.04+i*.24,3.961,1.54+i*.04),(.33,.36,.33))
scene.include("Rear wall fixtures",fixtures)

# Flag cloth: editable shallow waviness, with stripes extending down from canton.
flag=Asset("American flag and pole")
flag.include("Angled pole",rod(radius=.012,start=(0,0,0),end=(-.78,-.12,.52),color=(.24,.26,.24)))
# Broad cloth plane follows the hanging flag's narrowing, slightly folded profile.
for i in range(13):
    ztop=.48-i*.079
    width=.43*(.88+.12*math.cos(i*.24))
    stripe=box(size=(width,.014,.081),center=(-.67+width/2,-.13-.025*math.sin(i*.55),ztop-.04),
               color=(.62,.075,.065) if i%2==0 else (.81,.79,.69))
    stripe.turn("y",-7,pivot=(-.67,-.13,.48))
    flag.include("Cloth stripe %02d"%i,stripe)
add_box(flag,"Blue star field",(.195,.018,.43),(-.567,-.16,.267),(.12,.18,.24))
for j in range(4):
    for k in range(3):
        add_box(flag,"Star fleck %d %d"%(j,k),(.012,.005,.012),
                (-.638+k*.054,-.173,.11+j*.085),(.78,.80,.74))
place(flag,"Back corner flag",(1.75,3.83,3.20))

# Fallen acoustic tiles: modest thickness, irregular overlapping orientations.
random.seed(12)
def fallen_panel(name, dimensions, position, angle, color, tilt=(0,0)):
    a=Asset(name)
    add_box(a,"Broken panel body",dimensions,(0,0,dimensions[2]/2),color)
    # A pale torn edge makes the thin slab legible against the carpet.
    add_box(a,"Exposed pale edge",(dimensions[0],.018,.014),
            (0,-dimensions[1]/2,dimensions[2]*.65),(.48,.49,.40))
    return place(a,name,position,(tilt[0],tilt[1],angle))

fallen_panel("Rear fallen tile",(.85,.52,.025),(-1.55,1.65,.015),-12,(.27,.29,.25))
fallen_panel("Rear tile fragment",(.55,.32,.024),(-1.85,1.91,.04),9,(.39,.40,.32))
fallen_panel("Middle left tile",(.95,.54,.025),(-2.12,-.30,.015),-17,(.35,.36,.30))
fallen_panel("Middle tile overlap",(.60,.34,.025),(-1.88,-.12,.045),12,(.24,.26,.23))
fallen_panel("Foreground broad fragment",(1.17,.66,.035),(-1.48,-2.15,.014),14,(.29,.30,.25))
fallen_panel("Foreground upper fragment",(.86,.51,.025),(-1.22,-1.94,.055),-17,(.37,.38,.31))
fallen_panel("Foreground narrow fragment",(.73,.22,.023),(-1.02,-2.24,.078),29,(.22,.25,.22))

insulation=Asset("Fallen yellow insulation sheets")
# Broad thin solids with independently adjustable contour proportions.
add_box(insulation,"Lower ochre slab",(1.29,.94,.055),(0,.10,.045),(.59,.45,.16))
top=add_box(insulation,"Large yellow upper slab",(1.32,1.08,.065),(.27,-.21,.12),(.69,.55,.22))
top.turn("x",-10,pivot=(.27,-.21,.12))
add_box(insulation,"Broken narrow left tongue",(.23,.78,.055),(-.55,-.01,.077),(.67,.53,.20))
place(insulation,"Yellow debris pile",(1.43,-1.49,.012),(0,0,-9))

rails=Asset("Detached metal ceiling rails")
rail_specs=[
    ((-.92,-1.12,.045),(-.05,-1.28,.038)),
    ((-1.85,-.91,.045),(-.92,-1.13,.042)),
    ((1.59,-2.04,.036),(2.48,-3.75,.045)),
    ((1.80,-2.18,.04),(2.50,-4.17,.047)),
    ((2.18,-2.36,.046),(2.50,-3.07,.048)),
]
for i,(p,q) in enumerate(rail_specs):
    dx,dy=q[0]-p[0],q[1]-p[1]
    length=math.hypot(dx,dy)
    a=Asset("Loose T rail")
    add_box(a,"Flat flange",(length,.037,.015),(0,0,.008),(.59,.63,.62))
    add_box(a,"Upright web",(length,.009,.031),(0,0,.025),(.35,.40,.40))
    place(a,"Floor rail %d"%i,((p[0]+q[0])/2,(p[1]+q[1])/2,(p[2]+q[2])/2),
          (0,0,math.degrees(math.atan2(dy,dx))))
scene.include("Small rail scraps",rails)

# A few small light chips, kept sparse at this image resolution.
chips=Asset("Small floor chips")
for i in range(15):
    x=random.uniform(-2.6,2.2)
    y=random.uniform(-3.2,2.9)
    add_box(chips,"Chip %02d"%i,(random.uniform(.025,.075),random.uniform(.025,.09),.007),
            (x,y,.008),(.45,.44,.34))
scene.include("Scattered chips",chips)

# Small ceiling smoke detector.
detector=Asset("Ceiling smoke detector")
d=ball(radius=.09,center=(0,0,0),color=(.73,.74,.68))
d.resize((1,1,.38),pivot=(0,0,0))
detector.include("Detector housing",d)
place(detector,"Smoke detector",(-1.54,-2.35,3.84))

realize(scene)

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
background.inputs["Color"].default_value=(.71,.76,.79,1)
background.inputs["Strength"].default_value=.35

# Restrained procedural carpet and plaster detail; no photographic textures.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat is None:
            continue
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Roughness"].default_value=.86
    if "Carpet slab" in obj.name and obj.data.materials:
        mat=obj.data.materials[0]
        nt=mat.node_tree
        bs=nt.nodes.get("Principled BSDF")
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=165
        noise.inputs["Detail"].default_value=2
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.23
        ramp.color_ramp.elements[0].color=(.055,.065,.056,1)
        ramp.color_ramp.elements[1].position=.78
        ramp.color_ramp.elements[1].color=(.20,.21,.17,1)
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.20
        bump.inputs["Distance"].default_value=.012
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

# Camera estimated independently from rear wall width, corner height, and board edges.
set_view(position=(-2.5,-6,1.65),target=(2.0,4,1.68),lens=26.5,sensor=36)
area_emitter(position=(-2.65,-1.0,2.7),power=560,size=4.5,target=(1,1,1.2),color=(.86,.93,1.0))
area_emitter(position=(-.8,1.1,3.72),power=160,size=2.2,target=(0,0,0),color=(.94,.95,.88))
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
