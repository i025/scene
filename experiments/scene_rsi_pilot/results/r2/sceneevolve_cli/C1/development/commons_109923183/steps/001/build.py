# Image anchors: chaise occupies approximately (0.04,0.23) to (0.83,0.93).
# Tall upholstered head is at upper left; low rounded foot is at right.
# Wall/floor boundary slopes from (0.39,0.50) to (0.95,0.49).
# Cream wall panels fill the upper half; daylight enters along the left edge.
# A cream square pillow overlaps the tall head near (0.20,0.42).
# A second cane chair intrudes at the bottom-left corner.
from sceneact import *
import bpy, math, random
random.seed(12)

scene = Scene('French chaise room')
cream=(.76,.72,.62)
fabric=(.83,.78,.67)
paint=(.34,.39,.32)
gold=(.58,.49,.32)
wood=(.20,.105,.055)
wall=(.69,.67,.59)

def add(parent,name,node):
    parent.include(name,node)

def path(parent,name,points,r,color):
    for i in range(len(points)-1):
        add(parent,name+str(i),rod(r,start=points[i],end=points[i+1],color=color))

# Architecture
room=Asset('Paneled room')
add(room,'floor',box((12,12,.12),center=(0,0,-.08),color=wood))
# Individually editable parquet strips, with restrained color variation.
for i in range(12):
    for j in range(6):
        c=(.23+random.uniform(-.035,.035),.125+random.uniform(-.018,.018),.067)
        board=box((.78,.22,.018),center=((i-6)*.80,(j-3)*.235,0),color=c)
        board.turn('z',43,pivot=(0,0,0))
        add(room,f'parquet_{i}_{j}',board)
add(room,'rear_wall',box((8,.15,3.8),center=(0,1.08,1.85),color=wall))
add(room,'right_return',box((.15,3,3.8),center=(3.1,1.7,1.85),color=wall))
for z,depth,height in [(.10,.10,.18),(.25,.075,.05),(1.62,.055,.055),(1.72,.07,.055),(2.04,.055,.045),(2.18,.045,.04)]:
    add(room,'horizontal_'+str(z),box((7,.1+depth,height),center=(0,.965-depth/2,z),color=cream))
# Large rectangular wall moldings.
for k,(left,right) in enumerate([(-2.7,-1.65),(-1.60,2.35),(2.43,3.0)]):
    for side,x in enumerate((left,right)):
        add(room,f'panel_vertical_{k}_{side}',box((.026,.035,1.13),center=(x,.973,.91),color=cream))
    for side,z in enumerate((.36,1.46)):
        add(room,f'panel_horizontal_{k}_{side}',box((right-left,.035,.026),center=((left+right)/2,.973,z),color=cream))
    for side,x in enumerate((left+.055,right-.055)):
        add(room,f'panel_inner_{k}_{side}',box((.014,.024,1.01),center=(x,.95,.91),color=(.74,.71,.63)))
# Window and hanging curtains at left.
add(room,'window_light',box((.06,1.3,3.5),center=(-2.15,.13,1.7),color=(.96,.96,.89)))
for i in range(7):
    x=-2.05+i*.055
    add(room,f'curtain_{i}',rod(.055,start=(x,.53,.10),end=(x,.53,3.2),color=(.76+i*.016,.72+i*.017,.62+i*.022)))
scene.include('architecture',room)

chaise=Asset('Antique painted chaise longue')
# Main upholstered mattress, softly rounded perimeter.
add(chaise,'seat',fillet_box((2.52,1.03,.30),radius=.145,center=(.04,-.02,.77),color=fabric))
# Lower apron has a gently bowed silhouette and layered painted edges.
add(chaise,'apron',fillet_box((2.46,.98,.15),radius=.065,center=(.02,-.02,.565),color=paint))
for y in (-.525,.475):
    path(chaise,'apron_edge_'+str(y),[(-1.12,y,.62),(-.66,y,.59),(.15,y,.575),(.80,y,.59),(1.19,y,.62)],.022,gold)
    path(chaise,'apron_lower_'+str(y),[(-1.12,y,.53),(-.62,y,.50),(.15,y,.49),(.84,y,.51),(1.18,y,.55)],.025,cream)
# Cabriole legs with narrow curved ankles and small feet.
for n,(x,y) in enumerate([(-.98,-.43),(1.08,-.43),(-.99,.39),(1.08,.39)]):
    sign=1 if x>0 else -1
    pts=[(x,y,.58),(x+.055*sign,y,.43),(x-.025*sign,y-.015,.26),
         (x-.055*sign,y-.035,.08),(x+.01*sign,y-.065,.055)]
    path(chaise,'leg_'+str(n),pts,.043,paint)
    path(chaise,'leg_gold_'+str(n),[(a,b-.035,c) for a,b,c in pts],.010,gold)
# Upholstered head: broad high transverse back, slightly reclined.
head=fillet_box((.20,1.0,.84),radius=.09,center=(-1.13,.015,1.19),color=fabric)
head.turn('y',-14)
add(chaise,'head_upholstery',head)
# The rolled outline around the tall back.
outline=[(-1.18,-.51,.78),(-1.30,-.50,1.20),(-1.37,-.44,1.52),
         (-1.36,-.25,1.63),(-1.34,.09,1.66),(-1.31,.37,1.60),
         (-1.20,.51,1.44),(-1.02,.51,1.27),(-.66,.49,1.19),(-.52,.48,1.21)]
path(chaise,'head_frame',outline,.039,paint)
path(chaise,'head_frame_gilt',[(x-.018,y-.018,z+.025) for x,y,z in outline],.012,gold)
# Side panel and curved front arm, below the pillow.
panel=fillet_box((.63,.095,.48),radius=.044,center=(-.99,-.485,.93),color=fabric)
panel.turn('y',-16)
add(chaise,'near_side_panel',panel)
arm=[(-1.34,-.51,1.47),(-1.33,-.54,1.27),(-1.18,-.56,1.15),
     (-.88,-.56,1.08),(-.66,-.54,1.07),(-.66,-.53,.91),(-.55,-.51,.67)]
path(chaise,'front_arm',arm,.037,paint)
path(chaise,'front_arm_gold',[(x,y-.023,z+.018) for x,y,z in arm],.011,gold)
path(chaise,'side_bottom',[(-1.19,-.54,.73),(-.99,-.55,.63),(-.73,-.55,.60),(-.56,-.53,.67)],.028,paint)
# Far side low upholstered sweep.
far=fillet_box((.64,.11,.30),radius=.05,center=(-.88,.445,1.05),color=fabric)
far.turn('y',21)
add(chaise,'far_side_panel',far)
# Small gilded carved accents, including central apron medallion.
for i in range(7):
    angle=i*math.pi/3
    add(chaise,f'medallion_{i}',ball(.033,center=(.20+.065*math.cos(angle),-.548,.54+.04*math.sin(angle)),color=gold))
for x in (-1.14,1.12):
    for j in range(3):
        add(chaise,f'corner_rosette_{x}_{j}',ball(.027,center=(x+j*.025,-.53,.585+j*.013),color=cream))
for i in range(4):
    add(chaise,f'crest_{i}',ball(.030,center=(-1.38,-.24+i*.075,1.65+.025*math.sin(i)),color=gold))
# Soft square pillow, propped diagonally against the head.
pillow=fillet_box((.30,.67,.66),radius=.14,center=(-.90,-.015,1.22),color=(.88,.81,.66))
pillow.turn('y',-22)
pillow.turn('x',-8)
add(chaise,'loose_pillow',pillow)
# Tiny dark museum label on the seat.
label=box((.095,.18,.008),center=(.77,.16,.925),color=(.075,.24,.20))
label.turn('z',-8)
add(chaise,'museum_label',label)
for j in range(3):
    add(chaise,f'label_mark_{j}',box((.035,.004,.002),center=(.77,.12+j*.025,.931),color=(.65,.74,.61)))
scene.include('chaise',chaise)

# A second chair is cropped at the lower left.
chair=Asset('Foreground cane chair')
add(chair,'cane_seat',fillet_box((.66,.66,.065),radius=.03,center=(-1.67,-1.43,.39),color=(.42,.30,.16)))
for y in (-1.77,-1.09):
    add(chair,'seat_rail_'+str(y),box((.75,.055,.10),center=(-1.67,y,.38),color=paint))
for x in (-2.03,-1.31):
    add(chair,'seat_end_'+str(x),box((.055,.70,.10),center=(x,-1.43,.38),color=gold))
scene.include('foreground_chair',chair)

realize(scene)
# Procedural textile: faint woven ribs and small faded rose dashes.
textile=bpy.data.materials.new('Ivory woven upholstery with faded rose stripes')
textile.diffuse_color=(*fabric,1)
textile.use_nodes=True
nodes=textile.node_tree.nodes
links=textile.node_tree.links
bs=nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.87
geo=nodes.new('ShaderNodeNewGeometry')
sep=nodes.new('ShaderNodeSeparateXYZ')
links.new(geo.outputs['Position'],sep.inputs[0])
def wave(socket,scale):
    m=nodes.new('ShaderNodeMath');m.operation='MULTIPLY';m.inputs[1].default_value=scale
    links.new(socket,m.inputs[0])
    s=nodes.new('ShaderNodeMath');s.operation='SINE';links.new(m.outputs[0],s.inputs[0])
    return s.outputs[0]
wy=wave(sep.outputs['Y'],150)
wx=wave(sep.outputs['X'],95)
threshold=nodes.new('ShaderNodeMath');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=.91
links.new(wy,threshold.inputs[0])
dash=nodes.new('ShaderNodeMath');dash.operation='GREATER_THAN';dash.inputs[1].default_value=.35
links.new(wx,dash.inputs[0])
mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY'
links.new(threshold.outputs[0],mul.inputs[0]);links.new(dash.outputs[0],mul.inputs[1])
mix=nodes.new('ShaderNodeMixRGB')
mix.inputs[1].default_value=(.83,.78,.67,1)
mix.inputs[2].default_value=(.56,.36,.32,1)
links.new(mul.outputs[0],mix.inputs[0]);links.new(mix.outputs[0],bs.inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=185
links.new(geo.outputs['Position'],noise.inputs['Vector'])
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.009
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],bs.inputs['Normal'])
for obj in bpy.data.objects:
    if obj.type=='MESH':
        for slot in obj.material_slots:
            mat=slot.material
            if mat and all(abs(mat.diffuse_color[k]-fabric[k])<.012 for k in range(3)):
                slot.material=textile
        if obj.data:
            for poly in obj.data.polygons:
                poly.use_smooth=True

CAMERA_POSITION=(3.05,-5.1,3.30)
CAMERA_TARGET=(-.05,.02,.91)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=47)
area_emitter((-3.5,-.6,3.5),power=520,size=3.0,target=(-.4,0,.7),color=(1,.94,.82))
area_emitter((1,-3,3.5),power=110,size=4,target=(0,0,.6),color=(.87,.91,1))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.68,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.30
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
