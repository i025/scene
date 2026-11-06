from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(17)

# Reference inventory (estimated normalized image bounds):
# Ceiling boards: (0,0)-(1,.32), fine parallel seams and perimeter fascia.
# Rear windows: (0,.29)-(.66,.57), right windows: (.66,.25)-(1,.62);
# dark vertical mullions, low sill, pale outdoor trees.
# Dark rectangular tiled floor: (.25,.57)-(1,1).
# Left booth backs: (0,.51)-(.33,.90), overlapping broad upholstered panels;
# nearest light table: (0,.85)-(.46,1), clipped by bottom and left edges.
# Pedestal dining chairs and tables: (.33,.52)-(.89,1), flat tall backs,
# thin tops, shiny stems and broad round feet. Rear parts are occluded.
# Ten bell pendants: large left lamp (.02,.12)-(.23,.36), smaller lamps
# (.07,.33)-(1,.44); cylindrical necks, bands, long fine suspension wires.
# Palm: (.78,.40)-(1,1), multiple feather fronds, open gaps, dark pot.
# Rear shrubs: (.30,.48)-(.59,.60). Hidden furniture arrangements uncertain.
#
# Feedback comparison: the first view showed too little right glazing, the
# palm was outside the frame, rear ceiling was too low, and upholstery was
# too light. Revised camera turns toward the right windows and looks down
# slightly; furniture positions retain their staggered screen distribution.
# The nearest booth/table and lamp are adjusted separately for their crops.
#
# Expansion estimate: architecture 132 primitives, exterior 23,
# furniture about 200, lamps 90 including cutters, palm 166,
# sill shrubs 54: approximately 665 primitives. No fillet boxes.

scene = Scene('Reconstructed cafeteria')
C = {
    'ceiling': (.84,.85,.81), 'floor': (.095,.112,.10),
    'grout': (.25,.27,.23), 'frame': (.19,.22,.19),
    'seat': (.18,.205,.18), 'edge': (.32,.35,.30),
    'table': (.23,.26,.22), 'chrome': (.63,.66,.63),
    'lamp': (.025,.040,.025), 'leaf': (.035,.075,.035),
    'white': (.83,.84,.78)
}
def B(a,n,s,p,c):
    node=box(s,center=p,color=c)
    a.include(n,node)
    return node
def R(a,n,r,p,q,c):
    node=rod(r,start=p,end=q,color=c)
    a.include(n,node)
    return node
def D(a,n,r,h,p,c):
    return R(a,n,r,(p[0],p[1],p[2]-h/2),
             (p[0],p[1],p[2]+h/2),c)
def E(a,n,p,s,c):
    node=ball(1,center=p,color=c)
    node.resize(s)
    a.include(n,node)
    return node

room=Asset('architecture')
B(room,'dark_tile_floor',(11,16,.12),(0,.4,-.07),C['floor'])
B(room,'slatted_white_ceiling',(11,16,.10),(0,.4,3.72),C['ceiling'])
for i in range(56):
    B(room,f'ceiling_joint_{i}',(10.9,.007,.005),
      (0,-7.3+i*.28,3.665),(.59,.62,.57))
for i in range(32):
    B(room,f'long_tile_joint_{i}',(.007,15.8,.003),
      (-5.35+i*.345,.4,-.005),C['grout'])
for i in range(23):
    B(room,f'cross_tile_joint_{i}',(10.8,.007,.003),
      (0,-7.2+i*.66,-.004),(.22,.24,.20))
B(room,'rear_wall_below_glass',(10.8,.19,.85),(0,7.2,.425),(.62,.65,.59))
B(room,'rear_sill',(10.8,.32,.08),(0,7.10,.91),(.30,.34,.29))
B(room,'rear_ceiling_fascia',(10.8,.19,.16),(0,7.16,3.51),C['frame'])
for i,x in enumerate([-5.2,-3.7,-2.15,-.6,.95,2.5,4.05,5.3]):
    B(room,f'rear_window_mullion_{i}',(.055,.13,2.58),(x,7.14,2.2),C['frame'])
B(room,'rear_low_window_rail',(10.7,.10,.04),(0,7.1,1.1),C['frame'])
B(room,'right_wall_below_glass',(.19,15.7,.83),(5.35,-.55,.415),(.64,.67,.60))
B(room,'right_sill',(.33,15.7,.08),(5.27,-.55,.91),C['frame'])
B(room,'right_ceiling_fascia',(.16,15.7,.16),(5.3,-.55,3.51),C['frame'])
for i,y in enumerate([-7,-4.8,-2.5,-.2,2.1,4.4,7.1]):
    B(room,f'right_window_mullion_{i}',(.12,.055,2.6),(5.28,y,2.2),C['frame'])
B(room,'left_low_wall',(.16,15.5,1),(-5.4,-.5,.5),(.60,.63,.57))
scene.include('architecture',room)

outside=Asset('exterior')
B(outside,'pale_rear_view',(23,.1,8),(0,10,3),(.91,.93,.87))
B(outside,'pale_right_view',(.1,23,8),(8,0,3),(.94,.95,.90))
for i in range(21):
    E(outside,f'distant_tree_{i}',
      (random.uniform(-8,8),random.uniform(8,9.5),random.uniform(1.4,2.7)),
      (random.uniform(.35,.85),.32,random.uniform(.45,.95)),
      random.choice([(.64,.70,.61),(.74,.79,.70),(.81,.84,.77)]))
scene.include('exterior',outside)

def chair(name,x,y,facing=1,width=.95):
    a=Asset(name)
    B(a,'seat_cushion',(width,.65,.15),(x,y,.54),C['seat'])
    B(a,'rectangular_upholstered_back',(width,.11,.81),
      (x,y-facing*.31,.91),C['seat'])
    B(a,'upper_back_edge',(width+.018,.12,.022),
      (x,y-facing*.31,1.318),C['edge'])
    # A small exposed side edge gives the slab its characteristic thickness.
    B(a,'left_back_edge',(.022,.12,.79),
      (x-width/2,y-facing*.31,.91),C['edge'])
    D(a,'round_chrome_foot',.265,.045,(x,y,.035),C['chrome'])
    D(a,'polished_pedestal',.065,.43,(x,y,.26),C['chrome'])
    scene.include(name,a)

def table(name,x,y,w=1.35,d=.86,pale=False):
    a=Asset(name)
    topcol=(.52,.55,.48) if pale else C['table']
    B(a,'thin_table_surface',(w,d,.055),(x,y,.865),topcol)
    B(a,'light_table_edge',(w+.008,d+.008,.015),(x,y,.838),(.52,.55,.48))
    D(a,'chrome_column',.061,.79,(x,y,.425),C['chrome'])
    D(a,'round_base',.28,.035,(x,y,.025),C['chrome'])
    D(a,'cup',.043,.064,(x+.13,y,.929),C['white'])
    D(a,'saucer',.075,.010,(x+.13,y,.898),(.72,.75,.67))
    D(a,'ashtray',.065,.024,(x-.22,y+.09,.906),(.55,.59,.51))
    scene.include(name,a)

# Near booth crops across the left edge; successive booths recede behind it.
for i,y in enumerate([-4.85,-2.5,-.15,2.2,4.55,6.2]):
    a=Asset(f'left_booth_{i}')
    x=-2.55
    B(a,'broad_upholstered_back',(2.10,.15,.79),(x,y-.48,.99),C['seat'])
    B(a,'wide_seat',(2.10,.77,.18),(x,y-.08,.54),(.23,.26,.22))
    B(a,'bench_plinth',(1.94,.64,.43),(x,y-.08,.235),(.12,.15,.12))
    B(a,'top_piping',(2.11,.16,.022),(x,y-.48,1.398),C['edge'])
    scene.include(f'left_booth_{i}',a)
    table(f'left_table_{i}',x+.10,y+.73,2.18,1.0,pale=True)

# The nearer right group is larger and partly hidden by the palm.
for col,x in enumerate([.95,3.15]):
    rows=[-1.65,.85,3.35,5.7] if col==0 else [-2.45,.15,2.8,5.45]
    for row,y in enumerate(rows):
        table(f'dining_table_{col}_{row}',x,y,1.43,.91)
        chair(f'front_chair_{col}_{row}',x,y-.93,1,1.06)
        if row<3:
            chair(f'rear_chair_{col}_{row}',x,y+.93,-1,1.06)
for i,(x,y) in enumerate([(-.2,1.6),(-.2,3.9),(4.35,2.2),(4.35,4.6)]):
    chair(f'side_chair_{i}',x,y,1,.82)

def pendant(name,x,y,r=.34,lower=2.55,neck=.24):
    a=Asset(name)
    shell=ball(1,center=(x,y,lower+.03),color=C['lamp'])
    shell.resize((r,r,r*.83))
    cut=box((r*3,r*3,r*2),center=(x,y,lower-r),color=C['lamp'])
    inner=ball(1,center=(x,y,lower+.005),color=C['white'])
    inner.resize((r*.91,r*.91,r*.74))
    a.include('open_bell_shade',subtract(shell,cut,inner))
    D(a,'recessed_pale_reflector',r*.79,.012,(x,y,lower+.045),(.85,.87,.78))
    D(a,'cylindrical_neck',r*.37,neck,
      (x,y,lower+r*.67+neck*.40),C['lamp'])
    for k in range(2):
        D(a,f'neck_band_{k}',r*.375,.025,
          (x,y,lower+r*.67+neck*(.28+k*.35)),(.29,.33,.27))
    top=lower+r*.67+neck*.9
    R(a,'suspension_wire',.007,(x,y,top),(x,y,3.66),(.10,.13,.10))
    D(a,'ceiling_rose',.071,.012,(x,y,3.65),C['lamp'])
    scene.include(name,a)

pendant('large_left_foreground_lamp',-2.35,-3.4,.57,2.38,.37)
for i,(x,y,r,z) in enumerate([
    (-2.25,.2,.37,2.41),(-2.25,3.9,.29,2.40),
    (1.05,4.4,.30,2.43),(1.1,1.1,.35,2.46),
    (3.45,-.1,.40,2.51),(3.45,3.4,.29,2.46),
    (5.0,2.5,.28,2.49),(5.0,5.7,.25,2.49),
    (-2.25,6.3,.23,2.40)
]):
    pendant(f'receding_lamp_{i}',x,y,r,z,.23)

def spindle(a,name,start,end,width,col):
    mid=(Vector(start)+Vector(end))/2
    vec=Vector(end)-Vector(start)
    n=ball(1,center=tuple(mid),color=col)
    n.resize((width,width*.30,vec.length*.56))
    direction=vec.normalized()
    tilt=math.degrees(math.acos(max(-1,min(1,direction.z))))
    az=math.degrees(math.atan2(direction.y,direction.x))
    n.turn('y',tilt,pivot=tuple(mid))
    n.turn('z',az,pivot=tuple(mid))
    a.include(name,n)

palm=Asset('foreground_palm')
# Crown and pot are closer to the camera than most dining furniture.
base=Vector((4.12,-3.0,0))
D(palm,'dark_planter',.31,.53,tuple(base+Vector((0,0,.265))),(.09,.13,.085))
R(palm,'main_stem',.038,tuple(base+Vector((0,0,.45))),
  tuple(base+Vector((-.08,0,1.68))),(.14,.19,.10))
crown=base+Vector((-.08,0,1.65))
for f in range(10):
    angle=math.radians(6+f*36)
    horizontal=Vector((math.cos(angle),math.sin(angle),0))
    side=Vector((-math.sin(angle),math.cos(angle),0))
    length=[1.35,1.18,1.50,1.30,1.25,1.40,1.20,1.35,1.05,1.25][f]
    points=[]
    for t in [0,.35,.70,1]:
        p=crown+horizontal*(length*t)+Vector((0,0,.83*math.sin(t*2)-.27*t))
        points.append(tuple(p))
    palm.include(f'frond_{f}_spine',
                 sweep_tube(points=points,radius=.010,color=C['leaf']))
    for j,t in enumerate([.17,.30,.43,.56,.69,.82]):
        stem=crown+horizontal*(length*t)+Vector((0,0,.83*math.sin(t*2)-.27*t))
        for sign in [-1,1]:
            tip=stem+side*(sign*.47*(1-.45*t))+horizontal*.18+Vector((0,0,-.12))
            spindle(palm,f'frond_{f}_leaflet_{j}_{sign}',
                    tuple(stem),tuple(tip),.034,C['leaf'])
scene.include('foreground_palm',palm)

shrubs=Asset('rear_sill_shrubs')
for i in range(6):
    x=-1.3+i*.56
    D(shrubs,f'pot_{i}',.15,.24,(x,5.92,1),(.23,.28,.21))
    for j in range(4):
        dx=random.uniform(-.24,.24)
        dz=random.uniform(.2,.55)
        R(shrubs,f'twig_{i}_{j}',.009,(x,5.92,1.1),
          (x+dx,5.92,1.1+dz),C['leaf'])
        E(shrubs,f'leaf_cluster_{i}_{j}',(x+dx,5.92,1.1+dz),
          (.20,.16,.15),(.19,.27,.17))
scene.include('rear_shrubs',shrubs)

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
background.inputs['Color'].default_value=(.86,.88,.82,1)
background.inputs['Strength'].default_value=.46

set_view(position=(-2,-7.2,2.12),target=(2.55,3.4,1.37),lens=26.5,sensor=36)
area_emitter((0,6.5,3.2),power=1050,size=7,target=(0,0,0),color=(.98,1,.95))
area_emitter((5.0,-.6,2.9),power=950,size=6,target=(-2,1,.6),color=(1,1,.96))
area_emitter((-3,-3,3.4),power=170,size=4,target=(0,2,0),color=(.96,.98,.93))

for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.70
        col=bs.inputs['Base Color'].default_value
        if min(col[:3])>.57 and max(col[:3])<.70:
            bs.inputs['Metallic'].default_value=.75
            bs.inputs['Roughness'].default_value=.23

sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.05
