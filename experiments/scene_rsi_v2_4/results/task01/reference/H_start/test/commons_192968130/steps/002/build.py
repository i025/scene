from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, estimated normalized bounds:
# Rear oak slats: (0,.11)-(.46,.76), narrow black vertical gaps.
# White door: (.31,.29)-(.45,.77), thin frame, silver lever and keyhole.
# Bench: (0,.65)-(.20,.81), black top/sides, broad white inset front.
# Pale rectangular floor tiles: (0,.76)-(.42,1); ceiling above rear wall.
# Marble worktop: (.36,.59)-(1,1), narrow front edge and dark irregular veins.
# Recessed black sink: (.46,.64)-(.62,.72), bronze rim and right draining rack.
# Black ceramic hob: (.40,.77)-(.79,1), four subtle heating circles.
# Ivory reflective backsplash: (.58,.29)-(1,.91).
# Dark walnut upper cabinets: (.46,0)-(1,.43), broad end panel, door seams.
# Extractor underside and continuous warm light below cabinets.
# Hidden cabinet interiors, faucet and cropped foreground remain uncertain.
#
# Feedback: door was too far right/down; kitchen perspective faced across the
# worktop instead of along it. Upper cabinets were too narrow and too pale.
# Material selection by Blender object names failed because primitives retain
# generic names. This revision assigns finishes using geometric bounds.
#
# Expanded geometry estimate: 155 boxes/rods plus 4 simple ring meshes.
# No booleans, fillet expansions, or dense nested detail.

scene = Scene('Revised warm kitchen')
KITCHEN_SHIFT = -.18
COUNTER_END = 3.52
COUNTER_START = -1.6

def add(asset, name, size, center, color):
    n = box(size=size, center=center, color=color)
    asset.include(name, n)
    return n

def kitchen_add(asset, name, size, center, color):
    return add(asset, name, size,
               (center[0]+KITCHEN_SHIFT, center[1], center[2]), color)

room = Asset('room_architecture')
add(room, 'rear_dark_backing', (5.8,.12,2.85), (-.9,4.55,1.425), (.055,.028,.014))
add(room, 'right_wall', (.12,6.6,2.85), (1.60,1.3,1.425), (.78,.77,.72))
add(room, 'ceiling', (5.8,6.6,.12), (-1.06,1.3,2.91), (.79,.78,.74))
add(room, 'floor_base', (6,7,.09), (-1,1.1,-.055), (.43,.40,.35))
scene.include('architecture', room)

floor = Asset('stone_tile_floor')
for row in range(6):
    for col in range(5):
        x = -3.6 + col*1.15 + (.575 if row % 2 else 0)
        y = -1.1 + row*.94
        d = .012*((col+row)%3)
        add(floor, f'tile_{row}_{col}', (1.144,.934,.025),
            (x,y,.002), (.47+d,.44+d,.39+d))
scene.include('floor', floor)

slats = Asset('oak_slat_feature_wall')
slat_pitch = .083
slat_width = .057
for i in range(56):
    c = [(.28,.115,.037),(.34,.155,.055),
         (.25,.095,.026),(.31,.132,.043)][i%4]
    add(slats, f'oak_slat_{i}', (slat_width,.055,2.68),
        (-3.45+i*slat_pitch,4.455,1.34), c)
scene.include('oak_wall', slats)

door = Asset('white_door_and_frame')
dx = -.27
white = (.76,.77,.74)
add(door,'left_trim',(.065,.09,2.08),(dx-.465,4.375,1.04),white)
add(door,'right_trim',(.065,.09,2.08),(dx+.465,4.375,1.04),white)
add(door,'header',(.995,.09,.075),(dx,4.375,2.075),white)
add(door,'leaf',(.866,.055,2.005),(dx,4.39,1.012),(.71,.73,.71))
add(door,'leaf_right_reveal',(.003,.004,1.86),(dx+.36,4.355,1.04),(.53,.55,.53))
add(door,'handle_plate',(.035,.018,.13),(dx-.338,4.342,1.03),(.40,.41,.39))
door.include('handle_stem', rod(.013,start=(dx-.338,4.335,1.05),
                               end=(dx-.338,4.29,1.05),color=(.38,.39,.37)))
door.include('silver_lever', rod(.013,start=(dx-.338,4.285,1.05),
                               end=(dx-.215,4.285,1.05),color=(.43,.44,.42)))
add(door,'keyhole',(.012,.006,.024),(dx-.338,4.33,.965),(.035,.035,.03))
scene.include('door',door)

fittings = Asset('wall_switch_and_socket')
add(fittings,'switch_plate',(.105,.022,.085),(-.92,4.398,1.075),(.80,.79,.73))
add(fittings,'switch_rocker',(.061,.012,.054),(-.92,4.38,1.075),(.69,.69,.65))
add(fittings,'low_socket',(.075,.022,.08),(-.88,4.398,.27),(.81,.80,.75))
scene.include('electrical_fittings',fittings)

bench = Asset('black_bench_with_white_inset')
add(bench,'carcass',(1.45,.43,.48),(-2.3,4.14,.24),(.012,.016,.014))
add(bench,'white_drawer',(1.32,.025,.32),(-2.3,3.908,.215),(.73,.78,.76))
add(bench,'black_top',(1.48,.45,.045),(-2.3,4.12,.495),(.012,.016,.014))
add(bench,'end_panel',(.045,.44,.49),(-1.57,4.12,.245),(.017,.020,.017))
scene.include('bench',bench)

counter = Asset('marble_worktop_and_base')
xl,xr = .48,1.72
ya,yb = COUNTER_START,COUNTER_END
sx0,sx1 = .65,1.45
sy0,sy1 = 2.50,3.12
marble_color = (.61,.56,.45)
kitchen_add(counter,'left_marble_strip',(sx0-xl,yb-ya,.055),
            ((xl+sx0)/2,(ya+yb)/2,.94),marble_color)
kitchen_add(counter,'back_marble_strip',(xr-sx1,yb-ya,.055),
            ((xr+sx1)/2,(ya+yb)/2,.94),marble_color)
kitchen_add(counter,'near_marble_slab',(sx1-sx0,sy0-ya,.055),
            ((sx0+sx1)/2,(ya+sy0)/2,.94),marble_color)
kitchen_add(counter,'far_marble_slab',(sx1-sx0,yb-sy1,.055),
            ((sx0+sx1)/2,(yb+sy1)/2,.94),marble_color)
kitchen_add(counter,'base_cabinet',(1.18,yb-ya-.03,.85),
            (1.11,(ya+yb)/2,.45),(.36,.32,.25))
kitchen_add(counter,'front_marble_edge',(.035,yb-ya,.08),
            (.481,(ya+yb)/2,.90),marble_color)
scene.include('counter',counter)

sink = Asset('recessed_dark_sink')
sink_y = (sy0+sy1)/2
black = (.016,.018,.014)
kitchen_add(sink,'bottom',(.75,.57,.025),(1.05,sink_y,.754),black)
kitchen_add(sink,'left_wall',(.025,.62,.17),(.662,sink_y,.845),(.045,.038,.024))
kitchen_add(sink,'right_wall',(.025,.62,.17),(1.438,sink_y,.845),(.045,.038,.024))
kitchen_add(sink,'near_wall',(.8,.025,.17),(1.05,sy0+.01,.845),(.04,.033,.021))
kitchen_add(sink,'far_wall',(.8,.025,.17),(1.05,sy1-.01,.845),(.04,.033,.021))
for name,size,center in [
    ('left_rim',(.035,.67,.016),(.635,sink_y,.978)),
    ('right_rim',(.035,.67,.016),(1.465,sink_y,.978)),
    ('near_rim',(.865,.035,.016),(1.05,sy0-.03,.978)),
    ('far_rim',(.865,.035,.016),(1.05,sy1+.02,.978))]:
    kitchen_add(sink,name,size,center,(.18,.14,.075))
kitchen_add(sink,'right_drainer',(.17,.51,.014),(1.335,sink_y,.943),(.115,.095,.05))
for i in range(5):
    kitchen_add(sink,f'drainer_slot_{i}',(.125,.014,.008),
                (1.335,sink_y-.20+i*.094,.953),black)
scene.include('sink',sink)

hob = Asset('black_glass_hob')
kitchen_add(hob,'ceramic_surface',(.99,1.56,.018),(1.035,.79,.981),(.006,.009,.007))
scene.include('hob',hob)

splash = Asset('glossy_ivory_backsplash')
kitchen_add(splash,'glass_panel',(.025,5.15,.74),(1.705,.96,1.34),(.72,.72,.67))
for y in (1.15,3.18):
    kitchen_add(splash,f'fine_panel_joint_{y}',(.008,.006,.72),
                (1.686,y,1.34),(.65,.65,.60))
scene.include('backsplash',splash)

upper = Asset('walnut_overhead_cabinets')
# Wider projecting cabinets reproduce the large dark foreground canopy.
front_x = .32
wall_x = 1.54
cabinet_y0,cabinet_y1 = -1.72,4.40
cabinet_bottom = 1.71
cabinet_top = 2.85
walnut_color = (.095,.034,.011)
add(upper,'main_mass',(wall_x-front_x,cabinet_y1-cabinet_y0,
                      cabinet_top-cabinet_bottom),
    ((front_x+wall_x)/2,(cabinet_y0+cabinet_y1)/2,
     (cabinet_bottom+cabinet_top)/2),walnut_color)
add(upper,'rear_end_panel',(wall_x-front_x+.035,.065,1.17),
    ((front_x+wall_x)/2,4.40,2.275),(.073,.024,.008))
add(upper,'bottom_front_shadow',(.03,6.12,.032),
    (front_x-.015,1.34,1.715),(.025,.012,.005))
for i,y in enumerate((-1.10,.12,1.34,2.56,3.78)):
    add(upper,f'walnut_door_{i}',(.026,1.205,1.065),
        (front_x-.015,y,2.285),walnut_color)
    add(upper,f'lower_door_reveal_{i}',(.016,1.18,.013),
        (front_x-.031,y,1.775),(.022,.011,.005))
add(upper,'warm_light_strip',(.025,6.02,.012),(1.46,1.32,1.686),(.95,.72,.35))
scene.include('upper_cabinets',upper)

hood = Asset('metal_extractor_underside')
add(hood,'underplate',(.92,1.25,.026),(.91,.76,1.682),(.30,.30,.27))
add(hood,'filter_near',(.52,.40,.008),(.92,.48,1.664),(.22,.23,.21))
add(hood,'filter_far',(.52,.40,.008),(.92,1.02,1.664),(.22,.23,.21))
add(hood,'black_control',(.055,.075,.009),(.56,.74,1.657),(.02,.021,.018))
scene.include('extractor',hood)

realize(scene)

def material(name,color,roughness=.4,metallic=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metallic
    return m

stone=material('veined beige marble',marble_color,.27)
n=stone.node_tree.nodes
l=stone.node_tree.links
coord=n.new('ShaderNodeTexCoord')
noise=n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=3.8
noise.inputs['Detail'].default_value=3
noise.inputs['Roughness'].default_value=.7
l.new(coord.outputs['Object'],noise.inputs['Vector'])
vor=n.new('ShaderNodeTexVoronoi')
vor.feature='DISTANCE_TO_EDGE'
vor.inputs['Scale'].default_value=7
l.new(noise.outputs['Color'],vor.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.018
ramp.color_ramp.elements[0].color=(.085,.064,.037,1)
ramp.color_ramp.elements[1].position=.065
ramp.color_ramp.elements[1].color=(.65,.60,.49,1)
l.new(vor.outputs['Distance'],ramp.inputs[0])
l.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])

walnut=material('dark walnut directional grain',(.105,.038,.012),.3)
n=walnut.node_tree.nodes
l=walnut.node_tree.links
coord=n.new('ShaderNodeTexCoord')
scale=n.new('ShaderNodeVectorMath')
scale.operation='MULTIPLY'
scale.inputs[1].default_value=(20,15,.8)
noise=n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=3
noise.inputs['Detail'].default_value=2
ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color=(.035,.010,.003,1)
ramp.color_ramp.elements[1].color=(.17,.063,.019,1)
l.new(coord.outputs['Object'],scale.inputs[0])
l.new(scale.outputs[0],noise.inputs['Vector'])
l.new(noise.outputs['Fac'],ramp.inputs[0])
l.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])

glass=material('polished black hob',(.006,.009,.007),.095,.25)
splashmat=material('reflective ivory glass',(.72,.72,.67),.12,.12)
steel=material('brushed extractor steel',(.34,.34,.29),.33,.65)
markmat=material('faint hob rings',(.055,.053,.036),.37)
lightmat=material('warm luminous strip',(1,.72,.32),.3)
p=lightmat.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value=(1,.68,.25,1)
p.inputs['Emission Strength'].default_value=4

# Realized primitives use generic names: select finishes by world bounds.
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':
        continue
    pts=[ob.matrix_world @ Vector(v) for v in ob.bound_box]
    lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)))
    c=(lo+hi)/2
    d=hi-lo
    mat=None
    if abs(c.z-.94)<.005 or (abs(c.z-.90)<.005 and d.x<.05):
        mat=stone
    if abs(c.z-.981)<.003 and d.x>.8:
        mat=glass
    if abs(c.x-1.525)<.008 and d.y>4:
        mat=splashmat
    if c.x>.28 and c.x<1.57 and c.y<4.45 and c.z>2.0 and d.z>1:
        mat=walnut
    if abs(c.z-1.682)<.004 and d.x>.8:
        mat=steel
    if abs(c.z-1.686)<.002 and d.x<.04 and d.y>5:
        mat=lightmat
    if mat:
        ob.data.materials.clear()
        ob.data.materials.append(mat)

# Each annulus is one mesh. Centers correspond to four separate heating zones.
for j,(x,y,r) in enumerate(((.79,.37,.205),(1.29,.37,.18),
                             (.79,1.16,.205),(1.29,1.16,.18))):
    x+=KITCHEN_SHIFT
    count=64
    verts=[]
    for radius in (r-.002,r+.002):
        verts.extend((x+radius*math.cos(2*math.pi*i/count),
                      y+radius*math.sin(2*math.pi*i/count),.992)
                     for i in range(count))
    faces=[(i,(i+1)%count,(i+1)%count+count,i+count)
           for i in range(count)]
    mesh=bpy.data.meshes.new(f'heating_ring_{j}')
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(f'hob_heating_zone_{j}',mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(markmat)

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
background.inputs['Color'].default_value=(.72,.76,.82,1)
background.inputs['Strength'].default_value=.23

set_view(position=(.60,-1.08,1.89),
         target=(.60,4.35,1.168),lens=29,sensor=36)
area_emitter(position=(-2.4,.2,2.55),power=420,size=3.3,
             target=(.1,3,.6),color=(1,.94,.86))
area_emitter(position=(-1.6,3.0,2.60),power=120,size=2.0,
             target=(-.7,4.4,1.1),color=(1,.92,.80))
area_emitter(position=(1.35,2.75,1.66),power=55,size=1.5,
             target=(1.54,2.75,1.05),color=(1,.72,.36))
area_emitter(position=(1.35,.3,1.66),power=55,size=1.7,
             target=(1.54,.3,1.0),color=(1,.77,.43))
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=-.25
