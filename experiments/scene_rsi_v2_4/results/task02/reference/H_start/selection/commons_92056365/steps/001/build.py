from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(17)

# Reference inventory, normalized image bounds:
# Architecture: pale slatted ceiling (0,0)-(1,.34); rear glazing
# (0,.30)-(.67,.62), right glazing (.66,.24)-(1,.66); dark tiled floor
# (0,.58)-(1,1). Window mullions, low sills and ceiling perimeter are visible.
# Left booths: overlapping broad rectangular upholstered backs and seats,
# (0,.51)-(.34,.90); nearest pale table crops across (0,.85)-(.46,1).
# Central/right dining groups: gray rectangular pedestal seats, dark thin
# tabletops, chrome stems and circular feet, (.33,.51)-(.91,.97).
# Pendant lamps: large cropped-perspective bell at (.02,.12)-(.23,.40);
# smaller suspended bells across (.08,.30)-(1,.44), with thin long cords.
# Plants: large feathery palm (.78,.39)-(1,1); small shrubs along rear sill
# (.28,.47)-(.58,.62). Outdoor foliage is pale and partially obscured.
# Hidden seat upholstery and table arrangements are uncertain.
#
# Named SceneAct assets below preserve architecture, individual furniture
# assemblies, lamps, and plant crowns with editable semantic children.
# Estimated expansion: architecture ~120 boxes; furniture ~180 primitives;
# lamps ~65 including Boolean operands; plants ~125; exterior ~25.
# Total approximately 515 primitive meshes, no fillet boxes or dense sweeps.

scene = Scene('Daylit cafeteria')
C = {
    'ceiling': (.83,.84,.80), 'floor': (.21,.23,.21),
    'grout': (.39,.40,.36), 'frame': (.23,.25,.22),
    'seat': (.29,.32,.28), 'seat_edge': (.39,.41,.36),
    'table': (.34,.36,.31), 'chrome': (.65,.68,.65),
    'lamp': (.055,.075,.048), 'leaf': (.09,.14,.08),
    'outside': (.86,.88,.83), 'white': (.83,.84,.77)
}
def B(parent, name, size, center, col):
    n = box(size, center=center, color=col)
    parent.include(name,n)
    return n
def R(parent,name,r,a,b,col):
    n=rod(r,start=a,end=b,color=col)
    parent.include(name,n)
    return n
def E(parent,name,center,scale,col):
    n=ball(1,center=center,color=col)
    n.resize(scale)
    parent.include(name,n)
    return n
def disk(parent,name,r,h,center,col):
    return R(parent,name,r,(center[0],center[1],center[2]-h/2),
             (center[0],center[1],center[2]+h/2),col)

architecture=Asset('room_architecture')
B(architecture,'dark_tile_floor',(11,16,.12),(0,.4,-.07),C['floor'])
B(architecture,'white_board_ceiling',(11,16,.10),(0,.4,3.72),C['ceiling'])
for i in range(49):
    y=-7.3+i*.315
    B(architecture,f'ceiling_board_joint_{i}',(10.9,.008,.008),(0,y,3.663),(.62,.64,.60))
for i in range(32):
    x=-5.35+i*.345
    B(architecture,f'floor_long_joint_{i}',(.009,15.8,.004),(x,.4,-.006),C['grout'])
for i in range(23):
    y=-7.2+i*.66
    B(architecture,f'floor_cross_joint_{i}',(10.8,.008,.004),(0,y,-.004),(.31,.33,.29))
B(architecture,'rear_low_wall',(10.8,.19,.85),(0,7.2,.425),(.67,.69,.63))
B(architecture,'rear_sill',(10.8,.33,.09),(0,7.10,.91),(.35,.38,.33))
B(architecture,'rear_header',(10.8,.2,.19),(0,7.16,3.5),C['frame'])
for i,x in enumerate([-5.2,-3.7,-2.15,-.6,.95,2.5,4.05,5.3]):
    B(architecture,f'rear_mullion_{i}',(.065,.13,2.58),(x,7.14,2.2),C['frame'])
B(architecture,'rear_horizontal_rail',(10.7,.11,.045),(0,7.1,1.1),C['frame'])
B(architecture,'right_low_wall',(.19,15.7,.83),(5.35,-.55,.415),(.68,.70,.64))
B(architecture,'right_window_sill',(.33,15.7,.08),(5.27,-.55,.91),C['frame'])
B(architecture,'right_header',(.16,15.7,.18),(5.3,-.55,3.5),C['frame'])
for i,y in enumerate([-7,-4.8,-2.5,-.2,2.1,4.4,7.1]):
    B(architecture,f'right_mullion_{i}',(.12,.065,2.6),(5.28,y,2.2),C['frame'])
B(architecture,'left_wall_base',(.16,15.5,1.0),(-5.4,-.5,.5),(.66,.68,.61))
scene.include('architecture',architecture)

outside=Asset('bright_exterior_and_distant_trees')
B(outside,'rear_luminous_view',(23,.1,8),(0,10,3),C['outside'])
B(outside,'right_luminous_view',(.1,23,8),(8,0,3),(.90,.91,.87))
for i in range(21):
    x=random.uniform(-8,8)
    y=random.uniform(8,9.5)
    E(outside,f'distant_tree_crown_{i}',(x,y,random.uniform(1.4,2.7)),
      (random.uniform(.35,.85),.32,random.uniform(.45,.95)),
      random.choice([(.69,.73,.66),(.75,.78,.70),(.80,.82,.76)]))
scene.include('exterior',outside)

def chair(name,x,y,facing=1,width=.9):
    a=Asset(name)
    # Facing indicates the direction from the back toward the table.
    B(a,'upholstered_seat',(width,.65,.16),(x,y,.54),C['seat'])
    B(a,'tall_flat_back',(width,.115,.81),(x,y-facing*.31,.91),C['seat'])
    B(a,'back_upper_piping',(width+.025,.13,.025),(x,y-facing*.31,1.318),C['seat_edge'])
    disk(a,'circular_chrome_floor_foot',.265,.045,(x,y,.035),C['chrome'])
    disk(a,'central_chrome_pedestal',.068,.43,(x,y,.26),C['chrome'])
    scene.include(name,a)
    return a

def table(name,x,y,w=1.2,d=.84):
    a=Asset(name)
    B(a,'thin_dark_tabletop',(w,d,.065),(x,y,.865),C['table'])
    B(a,'bright_table_edge',(w+.009,d+.009,.018),(x,y,.843),(.58,.60,.53))
    disk(a,'central_polished_column',.065,.79,(x,y,.425),C['chrome'])
    disk(a,'round_floor_base',.29,.035,(x,y,.025),C['chrome'])
    disk(a,'small_white_cup',.043,.065,(x+.13,y,.932),C['white'])
    disk(a,'saucer',.075,.012,(x+.13,y,.897),(.66,.69,.62))
    disk(a,'small_ashtray',.065,.025,(x-.22,y+.09,.909),(.61,.64,.57))
    scene.include(name,a)

# Broad booth seats and long backs on the left.
for i,y in enumerate([-3.2,-.9,1.4,3.7,5.8]):
    a=Asset(f'left_booth_{i}')
    B(a,'broad_upholstered_back',(2.12,.16,.79),(-3.88,y-.48,.99),C['seat'])
    B(a,'wide_seat_cushion',(2.12,.78,.19),(-3.88,y-.08,.54),(.33,.36,.31))
    B(a,'solid_bench_plinth',(1.94,.64,.43),(-3.88,y-.08,.235),(.24,.27,.23))
    B(a,'top_back_piping',(2.13,.17,.026),(-3.88,y-.48,1.398),(.48,.50,.43))
    scene.include(f'left_booth_{i}',a)
    table(f'left_table_{i}',-3.75,y+.72,w=2.18,d=1.0)

# Two receding ranks of individually supported cafeteria seats.
for col,x in enumerate([-.52,2.18]):
    for row,y in enumerate([-.8,1.65,4.1,6.0]):
        table(f'dining_table_{col}_{row}',x,y,w=1.43,d=.91)
        chair(f'dining_front_seat_{col}_{row}',x,y-.93,1,width=1.06)
        if row<3:
            chair(f'dining_rear_seat_{col}_{row}',x,y+.93,-1,width=1.06)
# Extra visible side seats produce the staggered overlap down the central aisle.
for i,(x,y) in enumerate([(-1.7,2.1),(-1.7,4.3),(3.9,2.4),(3.9,4.8)]):
    chair(f'side_seat_{i}',x,y,1,.83)

def pendant(name,x,y,r=.34,lower=2.62,neck=.25):
    a=Asset(name)
    domecenter=(x,y,lower+.03)
    shell=ball(1,center=domecenter,color=C['lamp'])
    shell.resize((r,r,r*.83))
    cut=box((r*3,r*3,r*2),center=(x,y,lower-r),color=C['lamp'])
    inner=ball(1,center=(x,y,lower+.005),color=C['white'])
    inner.resize((r*.91,r*.91,r*.74))
    a.include('hollow_bell_shade',subtract(shell,cut,inner))
    # Pale underside, recessed inside the dark shade.
    disk(a,'recessed_white_reflector',r*.79,.012,(x,y,lower+.045),(.87,.88,.79))
    disk(a,'cylindrical_upper_housing',r*.37,neck,
         (x,y,lower+r*.67+neck*.40),C['lamp'])
    for k in range(2):
        disk(a,f'upper_housing_band_{k}',r*.375,.026,
             (x,y,lower+r*.67+neck*(.28+k*.35)),(.30,.33,.27))
    top=lower+r*.67+neck*.9
    R(a,'thin_suspension_wire',.009,(x,y,top),(x,y,3.66),(.13,.16,.12))
    disk(a,'ceiling_rose',.075,.014,(x,y,3.65),C['lamp'])
    scene.include(name,a)

pendant('large_foreground_left_pendant',-3.45,-3.4,.57,2.67,.33)
for i,(x,y,r,z) in enumerate([
    (-3.6,.2,.37,2.55),(-3.65,3.9,.29,2.49),
    (-.25,4.4,.30,2.53),(-.1,1.1,.35,2.58),
    (2.45,-.1,.40,2.69),(2.4,3.4,.29,2.57),
    (4.75,2.5,.28,2.61),(4.8,5.7,.25,2.6),
    (-3.65,6.3,.23,2.47)]):
    pendant(f'receding_pendant_{i}',x,y,r,z,.21)

def spindle(parent,name,start,end,width,col):
    mid=(Vector(start)+Vector(end))/2
    vec=Vector(end)-Vector(start)
    n=ball(1,center=tuple(mid),color=col)
    n.resize((width,width*.32,vec.length*.57))
    # Rotate a Z-aligned ellipsoid to the intended direction.
    direction=vec.normalized()
    tilt=math.degrees(math.acos(max(-1,min(1,direction.z))))
    az=math.degrees(math.atan2(direction.y,direction.x))
    n.turn('y',tilt,pivot=tuple(mid))
    n.turn('z',az,pivot=tuple(mid))
    parent.include(name,n)

palm=Asset('large_foreground_feathery_palm')
disk(palm,'dark_cylindrical_planter',.34,.55,(4.25,-2.15,.275),(.16,.20,.15))
R(palm,'main_trunk',.045,(4.25,-2.15,.45),(4.16,-2.1,1.67),(.21,.25,.16))
crown=Vector((4.16,-2.1,1.62))
for f in range(8):
    angle=math.radians(15+f*45)
    horizontal=Vector((math.cos(angle),math.sin(angle),0))
    side=Vector((-math.sin(angle),math.cos(angle),0))
    length=[1.45,1.22,1.55,1.35,1.3,1.45,1.15,1.35][f]
    points=[]
    for t in [0,.35,.70,1]:
        p=crown+horizontal*(length*t)+Vector((0,0,.85*math.sin(t*2.0)-.23*t))
        points.append(tuple(p))
    palm.include(f'frond_{f}_curved_spine',sweep_tube(points=points,radius=.012,color=C['leaf']))
    for j,t in enumerate([.22,.38,.54,.70,.85]):
        stem=crown+horizontal*(length*t)+Vector((0,0,.85*math.sin(t*2)-.23*t))
        leaflet_length=.46*(1-.46*t)
        for sign in [-1,1]:
            tip=stem+side*(sign*leaflet_length)+horizontal*.19+Vector((0,0,-.13))
            spindle(palm,f'frond_{f}_leaflet_{j}_{sign}',tuple(stem),tuple(tip),.047,C['leaf'])
scene.include('foreground_palm',palm)

shrubs=Asset('rear_sill_planting')
for i in range(6):
    x=-2.4+i*.57
    disk(shrubs,f'pot_{i}',.16,.25,(x,5.92,1.0),(.33,.36,.29))
    for j in range(4):
        dx=random.uniform(-.24,.24)
        dz=random.uniform(.2,.55)
        R(shrubs,f'twig_{i}_{j}',.012,(x,5.92,1.1),(x+dx,5.92,1.1+dz),C['leaf'])
        E(shrubs,f'foliage_{i}_{j}',(x+dx,5.92,1.1+dz),(.20,.16,.15),(.28,.34,.25))
scene.include('rear_plants',shrubs)

realize(scene)

sc=bpy.context.scene
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
background.inputs['Color'].default_value=(.80,.83,.77,1)
background.inputs['Strength'].default_value=.7

# Low eye level and a wide lens preserve the large near pendant and foreground crop.
set_view(position=(-2.0,-7.2,2.12),target=(.0,3.4,1.87),lens=26.5,sensor=36)
area_emitter((0,5.8,3.25),power=1500,size=7,target=(0,0,0),color=(.95,1,.92))
area_emitter((4.9,-.6,2.8),power=1250,size=6,target=(-2,1,.6),color=(1,1,.94))
area_emitter((-3,-3,3.4),power=350,size=4,target=(0,2,0),color=(.94,.97,.91))

# Shared material refinement keeps the image close to the muted monochrome reference.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.68
        col=bs.inputs['Base Color'].default_value
        if min(col[:3])>.57 and max(col[:3])<.75:
            bs.inputs['Metallic'].default_value=.55
            bs.inputs['Roughness'].default_value=.26
sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.2
