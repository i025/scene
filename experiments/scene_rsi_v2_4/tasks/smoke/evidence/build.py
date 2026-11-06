from sceneact import *
import bpy
import math

# Reference inventory, normalized image bounds:
# Cream classroom walls and ceiling; yellow dado; tiled floor (.0,.43)-(1,1).
# Tall brown doors and bright windows along both walls, overlapping desks.
# Rear stage (.36,.23)-(.67,.45): dark recess, green curtains, scalloped
# cream valance, green board with thin supports, narrow blue panel.
# Wooden desks and benches (.0,.41)-(.92,.90): dark thin tops, slender legs,
# open lower spaces, shelves and separate narrow seats.
# Black bag (.09,.73)-(.17,.91), horizontal black bag beneath front desk;
# blue backpack (.64,.69)-(.72,.86), turquoise bag (.76,.60)-(.83,.74);
# smaller bags and books partly occluded by furniture.
# Ceiling beams, six three-blade fans, wall speakers and framed portraits.
# Hidden stage depth and occluded furniture remain approximate.
#
# Feedback comparison: furniture was too pale, foreground columns too far
# left, center/right front desks too distant, stage header too low, floor
# tiles absent because realized mesh names did not preserve the part name.
# Preserve the room and composite hierarchy; correct these local parameters.
# Expansion estimate: architecture/openings 115; stage 25; 18 desks*11=198;
# bags 50; fans 30; pictures/books 23: approximately 441 primitive meshes.
# No Boolean operations or fillet expansion.

scene = Scene('Classroom')
cream = (.79,.78,.56)
white = (.88,.88,.79)
yellow = (.88,.62,.006)
wood = (.115,.074,.030)
edge = (.15,.108,.049)
topwood = (.065,.051,.029)
dark = (.008,.012,.014)
green = (.018,.12,.035)
blue = (.008,.16,.37)

def cube(parent,name,size,pos,color):
    node=box(size=size,center=pos,color=color)
    parent.include(name,node)
    return node

def line(parent,name,a,b,radius,color):
    node=rod(radius=radius,start=a,end=b,color=color)
    parent.include(name,node)
    return node

room=Asset('room_architecture')
cube(room,'tiled_floor',(9,18.8,.12),(0,1.5,-.06),(.58,.40,.18))
for side in (-1,1):
    x=side*4.5
    cube(room,f'cream_wall_{side}',(.16,18.8,4.55),(x,1.5,2.275),cream)
    cube(room,f'yellow_dado_{side}',(.025,18.8,1.20),
         (x-side*.095,1.5,.60),yellow)
cube(room,'rear_wall',(9,.16,4.55),(0,10.9,2.275),cream)
cube(room,'ceiling',(9,18.8,.12),(0,1.5,4.6),white)
for i,y in enumerate((-4.2,.3,4.8,9.1)):
    cube(room,f'ceiling_beam_{i}',(9,.20,.27),(0,y,4.40),white)
scene.include('room',room)

for side in (-1,1):
    wall=Asset(('left' if side<0 else 'right')+'_openings')
    x=side*4.39
    for j,y in enumerate((-3.3,.05,3.35,6.65,9.0)):
        dy=y+.55
        cube(wall,f'door_frame_{j}',(.10,1.04,2.80),(x,dy,1.40),wood)
        cube(wall,f'door_leaf_{j}',(.12,.86,2.59),
             (x-side*.035,dy,1.30),(.24,.145,.061))
        for k in (-1,1):
            cube(wall,f'door_stile_{j}_{k}',(.025,.045,2.44),
                 (x-side*.105,dy+k*.31,1.32),(.38,.26,.12))
        cube(wall,f'door_panel_divider_{j}',(.025,.69,.055),
             (x-side*.108,dy,1.35),(.38,.26,.12))
        cube(wall,f'door_handle_{j}',(.04,.05,.13),
             (x-side*.14,dy-.29,1.28),(.55,.44,.20))
        wy=y-.72
        cube(wall,f'window_frame_{j}',(.13,1.10,1.94),(x,wy,2.45),wood)
        cube(wall,f'bright_window_{j}',(.14,.94,1.78),
             (x-side*.025,wy,2.45),(.94,.97,1))
        cube(wall,f'window_cross_{j}',(.035,.97,.065),
             (x-side*.11,wy,2.69),wood)
        cube(wall,f'window_mullion_{j}',(.035,.055,1.8),
             (x-side*.11,wy,2.45),wood)
    scene.include(wall.name,wall)

stage=Asset('rear_stage_and_curtains')
cube(stage,'stage_plinth',(6.7,1.85,.34),(0,9.90,.17),(.24,.17,.06))
cube(stage,'dark_stage_recess',(6.35,.12,3.35),(0,10.75,2.10),(.018,.009,.005))
cube(stage,'upper_dark_curtain',(6.15,.17,.63),(0,10.49,3.35),(.055,.022,.010))
for side in (-1,1):
    cube(stage,f'green_side_curtain_{side}',(.52,.26,3.30),
         (side*3.02,10.33,2.26),green)
    cube(stage,f'curtain_fold_{side}',(.13,.30,3.30),
         (side*2.87,10.29,2.26),(.035,.21,.045))
cube(stage,'cream_valance_header',(6.45,.24,.26),(0,10.19,3.89),(.84,.76,.51))
for i in range(12):
    node=ball(radius=.265,center=(-2.93+i*.53,10.18,3.72),
              color=(.84,.76,.51))
    node.resize((1,.38,.68))
    stage.include(f'valance_scallop_{i}',node)
cube(stage,'chalkboard_frame',(2.40,.12,1.18),(.30,9.88,1.40),(.24,.24,.12))
cube(stage,'chalkboard',(2.29,.035,1.07),(.30,9.80,1.40),(.035,.15,.10))
line(stage,'board_support_left',(-.94,9.77,.35),(-.78,9.77,1.94),.022,wood)
line(stage,'board_support_right',(1.55,9.77,.35),(1.40,9.77,1.94),.022,wood)
line(stage,'chalk_diagonal',(-.72,9.772,.95),(-.38,9.772,1.82),.009,(.49,.56,.43))
cube(stage,'blue_stage_panel',(.60,.12,1.38),(2.23,9.96,1.11),(.12,.44,.64))
scene.include('stage',stage)

def desk(name,x,y,w=1.67,d=.71):
    a=Asset(name)
    h=1.02
    cube(a,'desktop',(w,d,.075),(x,y,h),topwood)
    cube(a,'front_apron',(w-.08,.065,.14),(x,y-d/2+.045,h-.105),edge)
    for ix in (-1,1):
        for iy in (-1,1):
            cube(a,f'leg_{ix}_{iy}',(.061,.061,.98),
                 (x+ix*(w/2-.09),y+iy*(d/2-.07),.49),edge)
    cube(a,'book_shelf',(w-.19,d*.66,.035),(x,y,.69),wood)
    by=y+.78
    cube(a,'bench_seat',(w,.27,.06),(x,by,.60),wood)
    for ix in (-1,1):
        cube(a,f'bench_leg_{ix}',(.065,.21,.57),
             (x+ix*(w/2-.13),by,.285),edge)
    cube(a,'bench_stretcher',(w-.20,.045,.055),(x,by,.22),edge)
    scene.include(name,a)

# Front rows are individually positioned to reproduce the staggered silhouettes.
# Columns converge toward their original positions near the stage.
for col,(front_x,back_x,front_y,w) in enumerate((
    (-1.72,-2.45,-2.40,1.48),
    (.95,.10,-1.50,1.54),
    (3.05,2.50,-.30,1.58)
)):
    for row in range(6):
        y=front_y+row*1.72
        if y<8.5:
            x=front_x+(back_x-front_x)*row/5
            desk(f'desk_c{col}_r{row}',x,y,w)
for i,y in enumerate((-.15,3.0,5.8)):
    desk(f'left_edge_desk_{i}',-3.90,y,1.23,.64)

books=Asset('books_and_notebooks')
for i,(x,y,col) in enumerate((
    (-1.85,-2.40,(.68,.69,.56)),(-1.8,-.68,(.64,.035,.13)),
    (.80,.22,(.74,.72,.56)),(3.00,1.42,(.66,.06,.16)),
    (-2.1,2.76,(.75,.78,.65)),(.40,3.66,(.025,.09,.12)),
    (2.7,4.86,(.64,.61,.42)),(-3.95,3.0,(.65,.045,.18))
)):
    cube(books,f'book_{i}',(.36,.24,.035),(x,y,1.075),col)
scene.include('books',books)

def bag(name,x,y,z=.32,color=blue,scale=1):
    a=Asset(name)
    # Broad shoulders and a flatter base produce a backpack rather than an egg.
    cube(a,'fabric_lower_body',(.43*scale,.28*scale,.43*scale),
         (x,y,z-.035*scale),color)
    body=ball(radius=1,center=(x,y,z+.14*scale),color=color)
    body.resize((.235*scale,.155*scale,.24*scale))
    a.include('rounded_shoulders',body)
    pocket=ball(radius=1,center=(x,y-.14*scale,z-.055*scale),
                color=tuple(c*.70 for c in color))
    pocket.resize((.19*scale,.066*scale,.205*scale))
    a.include('front_pocket',pocket)
    line(a,'zipper',(x-.16*scale,y-.205*scale,z+.095*scale),
         (x+.16*scale,y-.205*scale,z+.095*scale),.008*scale,(.18,.30,.33))
    line(a,'handle_left',(x-.07*scale,y,z+.33*scale),
         (x-.055*scale,y,z+.43*scale),.016*scale,color)
    line(a,'handle_right',(x-.055*scale,y,z+.43*scale),
         (x+.07*scale,y,z+.34*scale),.016*scale,color)
    line(a,'loose_shoulder_strap',(x+.19*scale,y+.01,z+.16*scale),
         (x+.31*scale,y-.08,.025),.022*scale,(.008,.014,.020))
    scene.include(name,a)

bag('foreground_black_bag',-2.38,-2.97,.34,(.004,.012,.023),1.05)
bag('foreground_blue_backpack',1.29,-2.35,.35,(.006,.16,.40),1.04)
bag('right_turquoise_backpack',3.06,-.10,.32,(.004,.23,.36),.94)
bag('middle_black_bag',.18,-.30,.28,(.005,.010,.015),.85)
bag('left_middle_blue_bag',-2.52,1.06,.30,(.008,.13,.32),.80)
bag('far_right_bag',2.75,4.04,.25,(.008,.10,.23),.66)
lying=Asset('bag_under_front_left_desk')
b=ball(radius=1,center=(-1.72,-2.42,.16),color=(.005,.010,.014))
b.resize((.43,.21,.12))
lying.include('horizontal_body',b)
line(lying,'trailing_strap',(-2.12,-2.52,.12),(-2.40,-2.82,.025),.020,dark)
scene.include('lying_bag',lying)

for i,(x,y,z) in enumerate((
    (-1.90,-1.50,4.05),(2.15,-1.00,4.10),
    (-2.35,3.15,3.99),(2.35,3.60,3.99),
    (-1.85,7.80,3.99),(1.85,8.00,3.99)
)):
    fan=Asset(f'ceiling_fan_{i}')
    line(fan,'downrod',(x,y,4.49),(x,y,z),.024,(.10,.085,.061))
    motor=ball(radius=.14,center=(x,y,z),color=(.10,.08,.055))
    motor.resize((1,1,.45))
    fan.include('motor',motor)
    for k in range(3):
        angle=math.radians(k*120+18)
        blade=cube(fan,f'blade_{k}',(.97,.145,.025),
                   (x+.55*math.cos(angle),y+.55*math.sin(angle),z),
                   (.14,.12,.085))
        blade.turn('z',k*120+18)
    scene.include(f'fan_{i}',fan)

for side,y,z in ((-1,4.5,3.1),(1,3.3,3.25)):
    a=Asset(f'wall_speaker_{side}')
    node=cube(a,'speaker_case',(.24,.55,.79),
              (side*4.18,y,z),(.005,.020,.020))
    node.turn('y',side*12)
    scene.include(a.name,a)

for side,ys in ((-1,(-1.6,5.6)),(1,(.5,5.8,8.2))):
    for j,y in enumerate(ys):
        a=Asset(f'framed_wall_picture_{side}_{j}')
        cube(a,'frame',(.07,.43,.65),(side*4.36,y,3.52),(.18,.16,.075))
        cube(a,'paper',(.075,.35,.56),(side*4.31,y,3.52),(.73,.76,.59))
        cube(a,'portrait',(.08,.16,.32),(side*4.26,y,3.52),(.065,.16,.17))
        scene.include(a.name,a)

realize(scene)
sc=bpy.context.scene

# Select the floor by geometry, since realization assigns generic mesh names.
floor_mat=bpy.data.materials.new('ochre_square_floor_tiles')
floor_mat.use_nodes=True
nodes=floor_mat.node_tree.nodes
links=floor_mat.node_tree.links
bs=nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.47
coord=nodes.new('ShaderNodeTexCoord')
brick=nodes.new('ShaderNodeTexBrick')
brick.inputs['Color1'].default_value=(.43,.28,.115,1)
brick.inputs['Color2'].default_value=(.69,.53,.29,1)
brick.inputs['Mortar'].default_value=(.39,.31,.18,1)
brick.inputs['Scale'].default_value=1
brick.inputs['Mortar Size'].default_value=.006
brick.inputs['Mortar Smooth'].default_value=.003
brick.inputs['Brick Width'].default_value=.30
brick.inputs['Row Height'].default_value=.30
brick.offset=0
links.new(coord.outputs['Object'],brick.inputs['Vector'])
links.new(brick.outputs['Color'],bs.inputs['Base Color'])
for obj in sc.objects:
    if obj.type=='MESH':
        if obj.dimensions.x>8.8 and obj.dimensions.y>18 and obj.location.z<.1:
            obj.data.materials.clear()
            obj.data.materials.append(floor_mat)

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
background.inputs['Strength'].default_value=.35

set_view((.12,-6.8,2.28),(0,8,-.10),lens=25,sensor=36)
area_emitter((-3.6,-1.5,3.6),power=650,size=4,
             target=(0,2,.1),color=(1,.96,.83))
area_emitter((3.5,3,3.5),power=500,size=4,
             target=(0,4,.5),color=(1,.98,.88))
area_emitter((-3.3,7.2,3.4),power=400,size=3,
             target=(0,7,.4),color=(1,.97,.83))
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=-.20
sc.view_settings.gamma=1
