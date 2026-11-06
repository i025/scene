from sceneact import *
import bpy
import math

# Reference inventory (normalized image bounds, estimated from the supplied view):
# Room: floor (0,.43)-(1,1), cream walls with yellow lower band, white ceiling.
# Left wall: repeated tall brown doors and bright windows (0,.16)-(.35,.60).
# Right wall: brown doors/windows (.65,.12)-(1,.66), high black loudspeaker.
# Rear stage: (.35,.23)-(.69,.47), dark opening, green side curtains,
# scalloped cream valance, green chalkboard and narrow blue panel.
# Desks/benches: (.01,.40)-(.93,.90), thin wooden frames, dark rectangular
# tops, open leg spaces and low shelves; rows overlap heavily toward the stage.
# Bags: black foreground left (.09,.72)-(.18,.91), black under left desk,
# blue foreground center (.63,.68)-(.73,.87), blue right (.76,.59)-(.83,.75),
# and several small bags partly hidden by desks.
# Ceiling: beams and six suspended three-blade fans; small framed wall pictures.
# Uncertain: furniture hidden behind front rows, stage recess depth, window exterior.
# Named SceneAct assets below preserve each composite and its meaningful parts.
# Estimated expansion: architecture/stage 60, windows/doors 75, furniture ~210,
# bags ~35, fans 30, pictures 16: approximately 426 simple meshes.
# No fillets, Boolean operations, external textures, or high-resolution decoration.

scene = Scene('Classroom')
cream = (.86,.85,.66)
white = (.93,.93,.86)
yellow = (.89,.68,.015)
wood = (.27,.205,.115)
edge = (.32,.27,.17)
topwood = (.22,.19,.135)
dark = (.035,.035,.025)
green = (.045,.19,.095)
blue = (.015,.22,.48)

def cube(parent, name, size, pos, color):
    node = box(size=size, center=pos, color=color)
    parent.include(name, node)
    return node

def line(parent, name, a, b, radius, color):
    node = rod(radius=radius, start=a, end=b, color=color)
    parent.include(name, node)
    return node

room = Asset('room_architecture')
cube(room,'tiled_floor',(9.0,18.8,.12),(0,1.5,-.06),(.65,.53,.32))
for side in (-1,1):
    x = side*4.5
    cube(room,f'cream_wall_{side}',(.16,18.8,4.55),(x,1.5,2.275),cream)
    cube(room,f'yellow_dado_{side}',(.025,18.8,1.20),(x-side*.095,1.5,.60),yellow)
cube(room,'rear_wall',(9,.16,4.55),(0,10.9,2.275),cream)
cube(room,'ceiling',(9,18.8,.12),(0,1.5,4.6),white)
for i,y in enumerate((-4.2,.3,4.8,9.1)):
    cube(room,f'ceiling_beam_{i}',(9,.20,.27),(0,y,4.40),white)
scene.include('room',room)

# Doors and windows are placed on the inward-facing surfaces.
for side in (-1,1):
    wall = Asset(('left' if side < 0 else 'right')+'_openings')
    x=side*4.39
    for j,y in enumerate((-3.3,.05,3.35,6.65,9.0)):
        door_y=y+.55
        cube(wall,f'door_frame_{j}',(.10,1.04,2.80),(x,door_y,1.40),(.26,.20,.12))
        cube(wall,f'door_leaf_{j}',(.12,.86,2.59),(x-side*.035,door_y,1.30),(.38,.28,.15))
        for k in (-1,1):
            cube(wall,f'door_stile_{j}_{k}',(.025,.045,2.44),
                 (x-side*.105,door_y+k*.31,1.32),(.53,.41,.24))
        cube(wall,f'door_panel_divider_{j}',(.025,.69,.055),
             (x-side*.108,door_y,1.35),(.53,.41,.24))
        cube(wall,f'door_handle_{j}',(.04,.05,.13),
             (x-side*.14,door_y-.29,1.28),(.73,.65,.37))
        wy=y-.72
        cube(wall,f'window_frame_{j}',(.13,1.10,1.94),(x,wy,2.45),(.27,.24,.15))
        cube(wall,f'bright_window_{j}',(.14,.94,1.78),
             (x-side*.025,wy,2.45),(.91,.96,.96))
        cube(wall,f'window_cross_{j}',(.035,.97,.065),
             (x-side*.11,wy,2.69),wood)
        cube(wall,f'window_mullion_{j}',(.035,.055,1.8),
             (x-side*.11,wy,2.45),wood)
    scene.include(wall.name,wall)

stage=Asset('rear_stage_and_curtains')
cube(stage,'stage_plinth',(6.7,1.85,.34),(0,9.90,.17),(.37,.30,.15))
cube(stage,'dark_stage_recess',(6.35,.12,2.66),(0,10.75,1.78),(.055,.038,.026))
cube(stage,'upper_dark_curtain',(6.15,.17,.46),(0,10.49,2.91),(.13,.065,.036))
for side in (-1,1):
    cube(stage,f'green_side_curtain_{side}',(.52,.26,2.60),
         (side*3.02,10.33,1.91),green)
    cube(stage,f'curtain_fold_{side}',(.13,.30,2.60),
         (side*2.87,10.29,1.91),(.09,.27,.10))
cube(stage,'cream_valance_header',(6.45,.24,.30),(0,10.19,3.20),(.91,.86,.65))
for i in range(12):
    scallop=ball(radius=.265,center=(-2.93+i*.53,10.18,3.03),color=(.90,.85,.65))
    scallop.resize((1,.38,.68))
    stage.include(f'valance_scallop_{i}',scallop)
cube(stage,'chalkboard_frame',(2.70,.12,1.28),(.30,9.88,1.17),(.37,.34,.21))
cube(stage,'chalkboard',(2.57,.035,1.15),(.30,9.80,1.17),(.10,.245,.19))
line(stage,'board_support_left',(-1.10,9.77,.35),(-.92,9.77,1.70),.022,wood)
line(stage,'board_support_right',(1.68,9.77,.35),(1.52,9.77,1.70),.022,wood)
line(stage,'chalk_diagonal',(-.84,9.772,.74),(-.45,9.772,1.62),.009,(.62,.68,.57))
cube(stage,'blue_stage_panel',(.60,.12,1.38),(2.23,9.96,1.01),(.22,.61,.77))
scene.include('stage',stage)

# Sparse, editable desks: open frames and shelves occupy the same visual
# regions as the reference without filling their large leg gaps.
def desk(name,x,y,w=1.73,d=.71):
    a=Asset(name)
    h=1.02
    cube(a,'desktop',(w,d,.09),(x,y,h),topwood)
    cube(a,'front_apron',(w-.08,.065,.18),(x,y-d/2+.045,h-.13),edge)
    for ix in (-1,1):
        for iy in (-1,1):
            cube(a,f'leg_{ix}_{iy}',(.065,.065,.97),
                 (x+ix*(w/2-.10),y+iy*(d/2-.08),.485),edge)
    cube(a,'low_book_shelf',(w-.19,d*.66,.045),(x,y,.66),wood)
    # Separate narrow wooden seating bench behind each desk.
    by=y+.78
    cube(a,'bench_seat',(w,.29,.065),(x,by,.60),(.31,.25,.15))
    for ix in (-1,1):
        cube(a,f'bench_leg_{ix}',(.075,.22,.57),
             (x+ix*(w/2-.14),by,.285),edge)
    cube(a,'bench_stretcher',(w-.20,.045,.065),(x,by,.22),edge)
    scene.include(name,a)
    return a

placements=[]
for col,x in enumerate((-2.75,-.22,2.36)):
    front=(-2.0,-.45,.85)[col]
    for row in range(5):
        y=front+row*1.72
        if y < 8.4:
            placements.append((f'desk_c{col}_r{row}',x,y,1.78 if col==0 else 1.67))
for name,x,y,w in placements:
    desk(name,x,y,w)

# Partial desks at the far left edge.
for i,y in enumerate((-.15,3.0,5.8)):
    desk(f'left_edge_desk_{i}',-4.20,y,1.23,.64)

# Small books and papers, visible on a restrained subset of desk tops.
books=Asset('books_and_notebooks')
for i,(x,y,col) in enumerate((
    (-2.85,-2.00,(.72,.72,.61)),(-2.4,-.28,(.76,.18,.28)),
    (-.43,1.29,(.83,.80,.63)),(2.42,2.57,(.76,.21,.30)),
    (-2.85,3.16,(.82,.84,.73)),(-.1,4.70,(.12,.21,.23)),
    (2.2,5.99,(.75,.73,.57)),(-3.95,3.0,(.75,.18,.33))
)):
    cube(books,f'book_{i}',(.36,.24,.035),(x,y,1.085),col)
scene.include('books',books)

def bag(name,x,y,z=.32,color=blue,scale=1):
    a=Asset(name)
    body=ball(radius=1,center=(x,y,z),color=color)
    body.resize((.27*scale,.18*scale,.39*scale))
    a.include('rounded_fabric_body',body)
    pocket=ball(radius=1,center=(x,y-.16*scale,z-.06*scale),
                color=tuple(c*.79 for c in color))
    pocket.resize((.21*scale,.075*scale,.24*scale))
    a.include('front_pocket',pocket)
    line(a,'zipper',(x-.17*scale,y-.229*scale,z+.11*scale),
         (x+.17*scale,y-.229*scale,z+.11*scale),.009*scale,(.38,.46,.43))
    line(a,'handle_left',(x-.08*scale,y,z+.34*scale),
         (x-.06*scale,y,z+.46*scale),.018*scale,color)
    line(a,'handle_right',(x-.06*scale,y,z+.46*scale),
         (x+.08*scale,y,z+.35*scale),.018*scale,color)
    line(a,'loose_shoulder_strap',(x+.20*scale,y+.01,z+.18*scale),
         (x+.36*scale,y-.08,.035),.025*scale,(.025,.036,.041))
    scene.include(name,a)

bag('foreground_black_bag',-3.16,-2.57,.36,(.018,.035,.050),1.05)
bag('foreground_blue_backpack',1.29,-1.92,.40,(.015,.26,.52),1.12)
bag('right_turquoise_backpack',3.06,.66,.35,(.015,.36,.49),.94)
bag('middle_black_bag',-.18,.30,.30,(.018,.027,.032),.85)
bag('left_middle_blue_bag',-3.22,1.36,.32,(.025,.24,.45),.80)
bag('far_right_bag',2.75,4.04,.25,(.025,.20,.35),.66)
lying=Asset('bag_under_front_left_desk')
b=ball(radius=1,center=(-2.35,-1.92,.16),color=(.018,.026,.030))
b.resize((.48,.22,.13))
lying.include('horizontal_body',b)
line(lying,'trailing_strap',(-2.8,-2.02,.12),(-3.0,-2.42,.025),.023,dark)
scene.include('lying_bag',lying)

# Six ceiling fans: slender rods, compact motor and broad three-blade silhouettes.
for i,(x,y) in enumerate(((-2.45,-2.85),(2.45,-1.6),
                          (-2.35,3.15),(2.35,3.6),
                          (-1.85,7.8),(1.85,8.0))):
    fan=Asset(f'ceiling_fan_{i}')
    line(fan,'downrod',(x,y,4.49),(x,y,3.99),.026,(.21,.20,.16))
    motor=ball(radius=.14,center=(x,y,3.98),color=(.22,.20,.16))
    motor.resize((1,1,.45))
    fan.include('motor',motor)
    for k in range(3):
        angle=math.radians(k*120+18)
        blade=cube(fan,f'blade_{k}',(.97,.145,.025),
                   (x+.55*math.cos(angle),y+.55*math.sin(angle),3.99),
                   (.27,.26,.23))
        blade.turn('z',k*120+18)
    scene.include(f'fan_{i}',fan)

for side,y,z in ((-1,4.5,3.1),(1,3.3,3.25)):
    speaker=Asset(f'wall_speaker_{side}')
    node=cube(speaker,'black_speaker_case',(.24,.55,.79),
              (side*4.18,y,z),(.018,.045,.045))
    node.turn('y',side*12)
    scene.include(speaker.name,speaker)

for side,ys in ((-1,(-1.6,5.6)),(1,(.5,5.8,8.2))):
    for j,y in enumerate(ys):
        a=Asset(f'framed_wall_picture_{side}_{j}')
        cube(a,'frame',(.07,.43,.65),(side*4.36,y,3.52),(.34,.31,.20))
        cube(a,'picture_paper',(.075,.35,.56),(side*4.31,y,3.52),(.82,.84,.69))
        cube(a,'portrait_mark',(.08,.16,.32),(side*4.26,y,3.52),(.19,.30,.31))
        scene.include(a.name,a)

realize(scene)

# Procedural floor: broad pale ochre tiles with fine joints and modest variation.
sc=bpy.context.scene
for obj in sc.objects:
    if obj.type=='MESH' and 'tiled_floor' in obj.name:
        mat=bpy.data.materials.new('warm_small_square_floor_tiles')
        mat.use_nodes=True
        n=mat.node_tree.nodes
        l=mat.node_tree.links
        bs=n.get('Principled BSDF')
        bs.inputs['Roughness'].default_value=.53
        tex=n.new('ShaderNodeTexCoord')
        brick=n.new('ShaderNodeTexBrick')
        brick.inputs['Color1'].default_value=(.57,.40,.20,1)
        brick.inputs['Color2'].default_value=(.77,.65,.43,1)
        brick.inputs['Mortar'].default_value=(.48,.43,.31,1)
        brick.inputs['Scale'].default_value=1
        brick.inputs['Mortar Size'].default_value=.008
        brick.inputs['Mortar Smooth'].default_value=.005
        brick.inputs['Brick Width'].default_value=.36
        brick.inputs['Row Height'].default_value=.36
        brick.offset=0
        l.new(tex.outputs['Object'],brick.inputs['Vector'])
        l.new(brick.outputs['Color'],bs.inputs['Base Color'])
        obj.data.materials.clear()
        obj.data.materials.append(mat)

if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.83,.88,.91,1)
background.inputs['Strength'].default_value=.65

set_view((.12,-6.8,2.28),(0,8,-.10),lens=25,sensor=36)
area_emitter((-3.6,-1.5,3.6),power=1500,size=5,target=(0,2,.1),color=(1,.96,.83))
area_emitter((3.5,3.0,3.5),power=1200,size=5,target=(0,4,.5),color=(1,.98,.88))
area_emitter((-3.3,7.2,3.4),power=850,size=4,target=(0,7,.4),color=(1,.97,.83))
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
