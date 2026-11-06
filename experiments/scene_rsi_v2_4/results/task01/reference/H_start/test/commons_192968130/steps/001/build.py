from sceneact import *
import bpy
import math

# Reference inventory (normalized image bounds; estimates only):
# Architecture: pale tiled floor (0,.75)-( .45,1), white ceiling (0,0)-(.46,.12);
# rear timber slat wall (0,.11)-(.46,.77), with narrow dark gaps.
# White door and frame (.31,.29)-(.45,.77), silver handle at (.34,.53).
# Low black bench with white inset front (0,.65)-(.20,.81), partly cropped left.
# Right kitchen: marble counter (.36,.59)-(1,1), dark sink (.46,.64)-(.62,.72),
# black glass hob (.39,.77)-(.78,1), four faint circular heating zones.
# Glossy ivory backsplash (.58,.28)-(1,.92), overlapping counter reflections.
# Dark walnut upper cabinets (.46,0)-(1,.43), projecting over the backsplash,
# with metallic extractor underside and warm continuous undercabinet illumination.
# Cabinet interiors, faucet configuration, and cropped near base cabinetry uncertain.
# Named assets below preserve these groups and meaningful component parts.
# Estimated expansion: about 155 meshes: 56 slats, 30 floor pieces,
# 18 architectural/door/bench pieces, 25 kitchen pieces, 16 hob rings/details,
# and 10 cabinet/extractor pieces. No fillets, booleans, or dense tube paths.

scene = Scene('Warm narrow contemporary kitchen')
ivory = (.83,.81,.74)
wood = (.19,.075,.026)
dark = (.018,.015,.012)
metal = (.37,.35,.29)

def add(parent, name, size, center, color):
    node = box(size=size, center=center, color=color)
    parent.include(name,node)
    return node

architecture = Asset('room_architecture')
add(architecture,'rear_wall_backing',(5.8,.12,2.85),(-.9,4.55,1.425),(.065,.036,.019))
add(architecture,'right_plastered_wall',(.12,6.6,2.85),(1.78,1.3,1.425),(.87,.86,.81))
add(architecture,'ceiling',(5.8,6.6,.12),(-1.06,1.3,2.9),(.89,.88,.83))
add(architecture,'floor_base',(6,7,.09),(-1,1.1,-.055),(.56,.52,.44))
scene.include('architecture',architecture)

floor = Asset('rectangular_stone_floor')
for row in range(6):
    for col in range(5):
        x=-3.6+col*1.15+(0.575 if row%2 else 0)
        y=-1.1+row*.94
        c=(.57+.018*((col+row)%3),.54+.016*((col+row)%3),.48+.016*((col+row)%3))
        add(floor,f'tile_{row}_{col}',(1.144,.934,.025),(x,y,.002),c)
scene.include('floor',floor)

slats=Asset('rear_vertical_oak_slats')
for i in range(56):
    x=-3.45+i*.083
    # The door occludes the uninterrupted slats behind it.
    c=[(.36,.17,.067),(.43,.215,.092),(.31,.135,.047),(.39,.185,.073)][i%4]
    add(slats,f'slat_{i}',(.057,.055,2.68),(x,4.455,1.34),c)
scene.include('timber_wall',slats)

door=Asset('white_door_and_trim')
door_x=-.27
add(door,'frame_left',(.065,.09,2.08),(door_x-.465,4.375,1.04),(.87,.87,.83))
add(door,'frame_right',(.065,.09,2.08),(door_x+.465,4.375,1.04),(.87,.87,.83))
add(door,'frame_header',(.995,.09,.075),(door_x,4.375,2.075),(.89,.89,.85))
add(door,'door_leaf',(.866,.055,2.005),(door_x,4.39,1.012),(.79,.80,.77))
add(door,'upper_inset_line',(.003,.004,1.86),(door_x+.36,4.355,1.04),(.69,.70,.67))
add(door,'handle_backplate',(.035,.018,.13),(door_x-.338,4.342,1.03),(.54,.54,.50))
door.include('handle_stem',rod(.013,start=(door_x-.338,4.335,1.05),end=(door_x-.338,4.29,1.05),color=metal))
door.include('lever',rod(.013,start=(door_x-.338,4.285,1.05),end=(door_x-.215,4.285,1.05),color=metal))
add(door,'keyhole',(.012,.006,.024),(door_x-.338,4.33,.965),dark)
scene.include('door',door)

fixtures=Asset('rear_wall_electrical_fittings')
add(fixtures,'light_switch',(.105,.022,.085),(-.92,4.398,1.075),(.88,.87,.80))
add(fixtures,'switch_center',(.061,.012,.054),(-.92,4.38,1.075),(.78,.77,.72))
add(fixtures,'low_socket',(.075,.022,.08),(-.88,4.398,.27),(.89,.88,.82))
scene.include('wall_fittings',fixtures)

bench=Asset('low_black_bench_with_white_drawer')
add(bench,'black_carcass',(1.45,.43,.48),(-2.3,4.14,.24),(.025,.027,.025))
add(bench,'white_front_panel',(1.32,.025,.32),(-2.3,3.908,.215),(.80,.83,.81))
add(bench,'top_slab',(1.48,.45,.045),(-2.3,4.12,.495),(.018,.021,.019))
add(bench,'right_side',(.045,.44,.49),(-1.57,4.12,.245),(.028,.031,.027))
scene.include('bench',bench)

counter=Asset('marble_worktop_and_base')
# Right-side run. Counter hole is constructed from four solids.
xl,xr=.48,1.72
ya,yb=-1.6,4.42
sx0,sx1=.65,1.45
sy0,sy1=3.18,3.80
topz=.94
marble=(.68,.63,.51)
add(counter,'outer_left_marble_strip',(sx0-xl,yb-ya,.055),((xl+sx0)/2,(ya+yb)/2,topz),marble)
add(counter,'wall_side_marble_strip',(xr-sx1,yb-ya,.055),((xr+sx1)/2,(ya+yb)/2,topz),marble)
add(counter,'near_marble_slab',(sx1-sx0,sy0-ya,.055),((sx0+sx1)/2,(ya+sy0)/2,topz),marble)
add(counter,'far_marble_slab',(sx1-sx0,yb-sy1,.055),((sx0+sx1)/2,(yb+sy1)/2,topz),marble)
add(counter,'base_cabinet_body',(1.18,5.9,.85),(1.11,1.4,.45),(.51,.48,.40))
add(counter,'front_edge_fascia',(.035,6.02,.08),(.481,1.41,.9),(.62,.57,.47))
scene.include('counter',counter)

sink=Asset('dark_rectangular_sink')
add(sink,'basin_bottom',(.75,.57,.025),(1.05,3.49,.754),(.025,.025,.019))
add(sink,'left_inner_wall',(.025,.62,.17),(.662,3.49,.845),(.075,.065,.043))
add(sink,'right_inner_wall',(.025,.62,.17),(1.438,3.49,.845),(.075,.065,.043))
add(sink,'near_inner_wall',(.8,.025,.17),(1.05,3.19,.845),(.065,.055,.035))
add(sink,'far_inner_wall',(.8,.025,.17),(1.05,3.79,.845),(.065,.055,.035))
for name,size,center in [
    ('left_rim',(.035,.67,.016),(.635,3.49,.978)),
    ('right_rim',(.035,.67,.016),(1.465,3.49,.978)),
    ('near_rim',(.865,.035,.016),(1.05,3.16,.978)),
    ('far_rim',(.865,.035,.016),(1.05,3.82,.978))]:
    add(sink,name,size,center,(.24,.19,.10))
add(sink,'narrow_drain_rack',(.17,.51,.014),(1.335,3.49,.943),(.16,.135,.079))
for i in range(5):
    add(sink,f'drainer_slot_{i}',(.125,.014,.008),(1.335,3.29+i*.094,.953),(.025,.024,.018))
scene.include('sink',sink)

hob=Asset('black_glass_ceramic_cooktop')
add(hob,'glass_surface',(.99,1.56,.018),(1.035,.79,.981),(.009,.012,.011))
# Thin circular zones are mesh rings, each a single mesh.
def ring(name, x,y,r):
    n=64
    verts=[]
    for radius in (r-.003,r+.003):
        verts.extend([(x+radius*math.cos(2*math.pi*i/n),y+radius*math.sin(2*math.pi*i/n),.992) for i in range(n)])
    faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(ringmat)

scene.include('cooktop',hob)

backsplash=Asset('glossy_ivory_backsplash')
add(backsplash,'continuous_glass_panel',(.025,6.1,.74),(1.705,1.38,1.34),(.83,.82,.76))
for y in (1.15,3.18):
    add(backsplash,f'panel_joint_{y}',(.008,.008,.72),(1.686,y,1.34),(.74,.73,.68))
scene.include('backsplash',backsplash)

upper=Asset('walnut_upper_cabinet_run')
add(upper,'main_cabinet_mass',(.65,6.15,1.12),(1.39,1.36,2.27),wood)
add(upper,'back_end_panel',(.68,.075,1.17),(1.375,4.4,2.275),(.15,.057,.019))
add(upper,'lower_dark_edge',(.045,6.13,.045),(1.047,1.36,1.714),(.07,.034,.016))
for i,y in enumerate((-1.2,.05,1.30,2.55,3.8)):
    add(upper,f'door_front_{i}',(.027,1.23,1.065),(1.052,y,2.285),(.205+.012*(i%2),.092,.035))
    add(upper,f'lower_recess_{i}',(.013,1.20,.012),(1.032,y,1.775),(.055,.031,.018))
add(upper,'warm_light_diffuser',(.032,5.94,.016),(1.43,1.38,1.689),(.98,.85,.57))
scene.include('upper_cabinets',upper)

hood=Asset('extractor_underside')
add(hood,'brushed_metal_underplate',(.55,1.25,.028),(1.37,.76,1.683),(.43,.42,.36))
add(hood,'filter_left',(.29,.40,.008),(1.35,.48,1.665),(.31,.32,.28))
add(hood,'filter_right',(.29,.40,.008),(1.35,1.02,1.665),(.31,.32,.28))
add(hood,'small_control',(.03,.075,.009),(1.13,.74,1.66),(.055,.056,.049))
scene.include('extractor',hood)

realize(scene)

# Shared restrained procedural surface families.
def principled_material(name,color,rough=.45,metallic=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metallic
    return m

stone=principled_material('warm ivory stone with irregular veins',marble,.3)
nodes=stone.node_tree.nodes
links=stone.node_tree.links
tex=nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value=6
tex.inputs['Detail'].default_value=4
tex.inputs['Roughness'].default_value=.75
coord=nodes.new('ShaderNodeTexCoord')
mapping=nodes.new('ShaderNodeVectorMath')
mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(2.0,4.0,6.0)
links.new(coord.outputs['Generated'],mapping.inputs[0])
links.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.34
ramp.color_ramp.elements[0].color=(.16,.12,.075,1)
ramp.color_ramp.elements[1].position=.48
ramp.color_ramp.elements[1].color=(.73,.68,.57,1)
links.new(tex.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])

glass=principled_material('reflective black ceramic',(.008,.011,.009),.12,.3)
splashmat=principled_material('polished ivory backsplash',(.80,.80,.74),.14,.08)
ringmat=principled_material('subtle grey hob markings',(.075,.074,.055),.38)
walnut=principled_material('walnut fine directional grain',(.18,.073,.025),.34)
wn=walnut.node_tree.nodes
wl=walnut.node_tree.links
wc=wn.new('ShaderNodeTexCoord')
wm=wn.new('ShaderNodeVectorMath')
wm.operation='MULTIPLY'
wm.inputs[1].default_value=(12,2,35)
wt=wn.new('ShaderNodeTexNoise')
wt.inputs['Scale'].default_value=2.3
wt.inputs['Detail'].default_value=2
wr=wn.new('ShaderNodeValToRGB')
wr.color_ramp.elements[0].color=(.065,.021,.008,1)
wr.color_ramp.elements[1].color=(.27,.125,.047,1)
wl.new(wc.outputs['Generated'],wm.inputs[0])
wl.new(wm.outputs[0],wt.inputs['Vector'])
wl.new(wt.outputs['Fac'],wr.inputs[0])
wl.new(wr.outputs[0],wn.get('Principled BSDF').inputs['Base Color'])

for ob in bpy.context.scene.objects:
    if ob.type!='MESH':
        continue
    name=ob.name.lower()
    material=None
    if 'marble' in name:
        material=stone
    elif 'glass_surface' in name:
        material=glass
    elif 'continuous_glass_panel' in name:
        material=splashmat
    elif 'door_front_' in name or 'main_cabinet_mass' in name or 'back_end_panel' in name:
        material=walnut
    if material:
        ob.data.materials.clear()
        ob.data.materials.append(material)

for x,y,r in ((.79,.37,.205),(1.29,.37,.18),(.79,1.16,.205),(1.29,1.16,.18)):
    ring('heating_zone',x,y,r)

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
background.inputs['Color'].default_value=(.76,.79,.82,1)
background.inputs['Strength'].default_value=.33

set_view(position=(-.78,-1.08,1.64),target=(.05,4.35,1.36),lens=29,sensor=36)
area_emitter(position=(-2.4,.35,2.55),power=650,size=3.6,target=(.3,3,.7),color=(1,.92,.80))
area_emitter(position=(-1.5,3.1,2.65),power=230,size=2.1,target=(-.6,4.4,1.2),color=(1,.94,.85))
area_emitter(position=(1.31,2.4,1.66),power=85,size=1.65,target=(1.67,2.4,1.08),color=(1,.76,.43))
area_emitter(position=(1.30,.2,1.66),power=70,size=1.5,target=(1.66,.2,1.05),color=(1,.80,.51))
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=0
