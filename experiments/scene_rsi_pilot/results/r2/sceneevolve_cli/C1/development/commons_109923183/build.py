# The view is too high and too far left; lower the camera and view slightly from the foot.
# The pillow appears narrow; turn its broad face toward the camera.
# Wall panels are too tall in projection, and the parquet pattern needs world-scale boards.
from sceneact import *
import bpy, math

scene = Scene('French chaise room')
cream=(.76,.72,.62)
fabric=(.83,.78,.67)
paint=(.29,.35,.29)
gold=(.56,.48,.33)
wood=(.16,.075,.042)
wall=(.69,.67,.59)

def add(parent,name,node):
    parent.include(name,node)

def path(parent,name,points,r,color):
    for i in range(len(points)-1):
        add(parent,name+str(i),rod(r,start=points[i],end=points[i+1],color=color))

room=Asset('Room architecture')
add(room,'floor',box((12,12,.12),center=(0,0,-.065),color=wood))
panels=Asset('Cream wall paneling')
add(panels,'rear_wall',box((8,.15,3.8),center=(0,1.08,1.85),color=wall))
add(panels,'right_return',box((.15,3,3.8),center=(2.17,1.7,1.85),color=wall))
for z,depth,height in [(.10,.10,.18),(.25,.075,.05),(1.62,.055,.055),(1.72,.07,.055),(2.04,.055,.045),(2.18,.045,.04)]:
    add(panels,'horizontal_'+str(z),box((7,.1+depth,height),center=(0,.965-depth/2,z),color=cream))
for k,(left,right) in enumerate([(-2.7,-1.65),(-1.60,1.83),(1.94,2.13)]):
    for side,x in enumerate((left,right)):
        add(panels,f'panel_vertical_{k}_{side}',box((.026,.035,1.13),center=(x,.973,.91),color=cream))
    for side,z in enumerate((.36,1.46)):
        add(panels,f'panel_horizontal_{k}_{side}',box((right-left,.035,.026),center=((left+right)/2,.973,z),color=cream))
    if right-left>.5:
        for side,x in enumerate((left+.055,right-.055)):
            add(panels,f'panel_inner_{k}_{side}',box((.014,.024,1.01),center=(x,.95,.91),color=(.74,.71,.63)))
        for side,z in enumerate((.415,1.405)):
            add(panels,f'panel_inner_horizontal_{k}_{side}',box((right-left-.11,.024,.014),center=((left+right)/2,.95,z),color=cream))
panels.move((0,.56,0))
add(room,'wall_panels',panels)
add(room,'window_light',box((.035,1.5,3.5),center=(-1.94,.32,1.7),color=(.98,.97,.91)))
for i in range(9):
    x=-1.91+i*.037
    add(room,f'curtain_{i}',rod(.042,start=(x,.73,.10),end=(x,.73,3.2),color=(.77+i*.014,.73+i*.015,.65+i*.017)))
for i,x in enumerate((-.93,-.85)):
    fitting=ball(.024,center=(x,1.49,1.83),color=(.12,.10,.065))
    fitting.resize((.55,.45,1.45))
    add(room,f'wall_fitting_{i}',fitting)
scene.include('architecture',room)

chaise=Asset('Antique painted chaise longue')
add(chaise,'seat',fillet_box((2.52,1.03,.30),radius=.145,center=(.04,-.02,.77),color=fabric))
add(chaise,'apron',fillet_box((2.46,.98,.17),radius=.065,center=(.02,-.02,.555),color=paint))
for y in (-.525,.475):
    path(chaise,'apron_edge_'+str(y),[(-1.12,y,.62),(-.66,y,.59),(.15,y,.575),(.80,y,.59),(1.19,y,.62)],.014,gold)
    path(chaise,'apron_lower_'+str(y),[(-1.12,y,.53),(-.62,y,.49),(.15,y,.475),(.84,y,.50),(1.18,y,.55)],.014,cream)
for n,(x,y) in enumerate([(-.98,-.43),(1.08,-.43),(-.99,.39),(1.08,.39)]):
    sign=1 if x>0 else -1
    pts=[(x,y,.58),(x+.055*sign,y,.43),(x-.025*sign,y-.015,.26),
         (x-.055*sign,y-.035,.08),(x+.01*sign,y-.065,.055)]
    path(chaise,'leg_'+str(n),pts,.036,paint)
    path(chaise,'leg_gold_'+str(n),[(a,b-.029,c) for a,b,c in pts],.007,gold)
head=fillet_box((.20,1.0,.84),radius=.09,center=(-1.13,.015,1.19),color=fabric)
head.turn('y',-14)
add(chaise,'head_upholstery',head)
outline=[(-1.18,-.51,.78),(-1.30,-.50,1.20),(-1.37,-.44,1.52),
         (-1.36,-.25,1.63),(-1.34,.09,1.66),(-1.31,.37,1.60),
         (-1.20,.51,1.44),(-1.02,.51,1.27),(-.66,.49,1.19),(-.52,.48,1.21)]
path(chaise,'head_frame',outline,.030,paint)
path(chaise,'head_frame_gilt',[(x-.018,y-.018,z+.025) for x,y,z in outline],.009,gold)
panel=fillet_box((.63,.095,.48),radius=.044,center=(-.99,-.485,.93),color=fabric)
panel.turn('y',-16)
add(chaise,'near_side_panel',panel)
arm=[(-1.34,-.51,1.47),(-1.33,-.54,1.27),(-1.18,-.56,1.15),
     (-.88,-.56,1.08),(-.66,-.54,1.07),(-.66,-.53,.91),(-.55,-.51,.67)]
path(chaise,'front_arm',arm,.030,paint)
path(chaise,'front_arm_gold',[(x,y-.023,z+.018) for x,y,z in arm],.008,gold)
path(chaise,'side_bottom',[(-1.19,-.54,.73),(-.99,-.55,.63),(-.73,-.55,.60),(-.56,-.53,.67)],.023,paint)
far=fillet_box((.64,.11,.30),radius=.05,center=(-.88,.445,1.05),color=fabric)
far.turn('y',21)
add(chaise,'far_side_panel',far)
for i in range(9):
    a=i*math.tau/8
    add(chaise,f'medallion_{i}',ball(.026,center=(.20+.073*math.cos(a),-.548,.535+.045*math.sin(a)),color=gold))
for side in (-1,1):
    path(chaise,f'carved_scroll_{side}',[(.20+side*.08,-.55,.54),(.20+side*.14,-.55,.565),(.20+side*.20,-.55,.55)],.012,gold)
for x in (-1.14,1.12):
    for j in range(3):
        add(chaise,f'corner_rosette_{x}_{j}',ball(.022,center=(x+j*.025,-.53,.585+j*.013),color=cream))
for i in range(4):
    add(chaise,f'crest_{i}',ball(.025,center=(-1.38,-.24+i*.075,1.65+.025*math.sin(i)),color=gold))
pillow_color=(.86,.77,.59)
pillow=fillet_box((.65,.27,.67),radius=.125,center=(-.99,-.10,1.245),color=pillow_color)
pillow.turn('x',-13)
pillow.turn('y',-15)
pillow.turn('z',-13)
add(chaise,'loose_pillow',pillow)
label=box((.095,.18,.008),center=(.77,.16,.925),color=(.075,.24,.20))
label.turn('z',-8)
add(chaise,'museum_label',label)
for j in range(3):
    add(chaise,f'label_mark_{j}',box((.035,.004,.002),center=(.77,.12+j*.025,.931),color=(.65,.74,.61)))
scene.include('chaise',chaise)

chair=Asset('Foreground cane chair')
cane_color=(.40,.27,.14)
add(chair,'cane_seat',fillet_box((.66,.66,.065),radius=.03,center=(-1.32,-1.55,.39),color=cane_color))
for y in (-1.89,-1.21):
    add(chair,'seat_rail_'+str(y),box((.75,.055,.10),center=(-1.32,y,.38),color=paint))
for x in (-1.68,-.96):
    add(chair,'seat_end_'+str(x),box((.055,.70,.10),center=(x,-1.55,.38),color=gold))
scene.include('foreground_chair',chair)

realize(scene)

textile=bpy.data.materials.new('Ivory woven upholstery with faded rose dashes')
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
    m=nodes.new('ShaderNodeMath')
    m.operation='MULTIPLY'
    m.inputs[1].default_value=scale
    links.new(socket,m.inputs[0])
    s=nodes.new('ShaderNodeMath')
    s.operation='SINE'
    links.new(m.outputs[0],s.inputs[0])
    return s.outputs[0]
wy=wave(sep.outputs['Y'],125)
wx=wave(sep.outputs['X'],110)
threshold=nodes.new('ShaderNodeMath')
threshold.operation='GREATER_THAN'
threshold.inputs[1].default_value=.94
links.new(wy,threshold.inputs[0])
dash=nodes.new('ShaderNodeMath')
dash.operation='GREATER_THAN'
dash.inputs[1].default_value=.45
links.new(wx,dash.inputs[0])
mul=nodes.new('ShaderNodeMath')
mul.operation='MULTIPLY'
links.new(threshold.outputs[0],mul.inputs[0])
links.new(dash.outputs[0],mul.inputs[1])
mix=nodes.new('ShaderNodeMixRGB')
mix.inputs[1].default_value=(.83,.78,.67,1)
mix.inputs[2].default_value=(.59,.37,.34,1)
links.new(mul.outputs[0],mix.inputs[0])
links.new(mix.outputs[0],bs.inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=185
links.new(geo.outputs['Position'],noise.inputs['Vector'])
bump=nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.12
bump.inputs['Distance'].default_value=.006
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs[0],bs.inputs['Normal'])

floor_mat=bpy.data.materials.new('Dark polished parquet')
floor_mat.use_nodes=True
fn=floor_mat.node_tree.nodes
fl=floor_mat.node_tree.links
fb=fn.get('Principled BSDF')
fb.inputs['Roughness'].default_value=.34
fg=fn.new('ShaderNodeNewGeometry')
mapping=fn.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value[2]=math.radians(43)
fl.new(fg.outputs['Position'],mapping.inputs['Vector'])
brick=fn.new('ShaderNodeTexBrick')
brick.inputs['Scale'].default_value=1
brick.inputs['Brick Width'].default_value=.73
brick.inputs['Row Height'].default_value=.17
brick.inputs['Mortar Size'].default_value=.001
brick.inputs['Mortar Smooth'].default_value=.001
brick.inputs['Color1'].default_value=(.115,.047,.028,1)
brick.inputs['Color2'].default_value=(.19,.084,.047,1)
brick.inputs['Mortar'].default_value=(.075,.032,.019,1)
fl.new(mapping.outputs['Vector'],brick.inputs['Vector'])
fl.new(brick.outputs['Color'],fb.inputs['Base Color'])

cane_mat=bpy.data.materials.new('Woven cane')
cane_mat.use_nodes=True
cn=cane_mat.node_tree.nodes
cl=cane_mat.node_tree.links
cb=cn.get('Principled BSDF')
cg=cn.new('ShaderNodeNewGeometry')
check=cn.new('ShaderNodeTexChecker')
check.inputs['Scale'].default_value=95
check.inputs['Color1'].default_value=(.39,.25,.13,1)
check.inputs['Color2'].default_value=(.16,.095,.045,1)
cl.new(cg.outputs['Position'],check.inputs['Vector'])
cl.new(check.outputs['Color'],cb.inputs['Base Color'])
cb.inputs['Roughness'].default_value=.8

for obj in bpy.data.objects:
    if obj.type=='MESH':
        for slot in obj.material_slots:
            mat=slot.material
            if mat and all(abs(mat.diffuse_color[k]-fabric[k])<.012 for k in range(3)):
                slot.material=textile
            elif mat and all(abs(mat.diffuse_color[k]-wood[k])<.008 for k in range(3)):
                slot.material=floor_mat
            elif mat and all(abs(mat.diffuse_color[k]-cane_color[k])<.008 for k in range(3)):
                slot.material=cane_mat

CAMERA_POSITION=(.55,-5.35,3.25)
CAMERA_TARGET=(.045,.04,.93)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=56)
area_emitter((-3.5,-.6,3.5),power=470,size=3.0,target=(-.4,0,.7),color=(1,.94,.82))
area_emitter((1,-3,3.5),power=85,size=4,target=(0,0,.6),color=(.87,.91,1))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.68,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.25
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
