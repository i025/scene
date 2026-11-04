from sceneact import *
import bpy

# Observations: the first render is too distant; the island's long front is too
# broad relative to its end, and the foreground column overlaps the island.
# Reference landmarks: post x64..118, island corners (127,307),(238,322),(345,295),
# hood approximately x160..279 and y23..222.
# Main correction: camera azimuth, distance and aim. This should enlarge the
# kitchen and expose the island's broad end. Foreground post placement follows
# its reference screen position; other semantic groups retain their dimensions.
# Absolute camera calibration remains uncertain.
scene = Scene('Kitchen showroom')
ivory=(.65,.66,.63)
dark=(.045,.052,.050)
stone=(.72,.72,.66)

def cube(parent,key,size,center,color):
    return parent.include(key,box(size=size,center=center,color=color))

room=scene.include('architecture',Asset('Architecture'))
cube(room,'floor',(12,13,.12),(0,0,-.06),(.59,.59,.55))
cube(room,'rear_wall',(10,.16,4.3),(0,2.48,2.15),(.25,.27,.26))
cube(room,'left_wall',(.15,8,4.3),(-3.35,1,2.15),(.32,.33,.31))
cube(room,'ceiling',(11,11,.12),(0,0,4.22),(.035,.044,.041))
for i in range(-5,6):
    cube(room,'floor_joint_x_%d'%i,(.008,12,.0015),(i*1.25,0,.001),(.40,.41,.38))
for i in range(-5,7):
    cube(room,'floor_joint_y_%d'%i,(12,.008,.0015),(0,i*1.25,.001),(.40,.41,.38))
for i,x in enumerate([-3,-1.3,.5,2.3,4.1]):
    cube(room,'ceiling_long_beam_%d'%i,(.19,8,.26),(x,.1,4.02),(.035,.045,.042))
for i,y in enumerate([-2.5,-.6,1.3,3.2]):
    cube(room,'ceiling_cross_beam_%d'%i,(10,.22,.32),(0,y,3.94),(.048,.059,.055))
for i in range(15):
    cube(room,'ceiling_seam_%d'%i,(.025,9,.035),(-4+i*.57,0,4.135),(.012,.017,.016))

# Island maps to carcass, slab fronts, counter, inset hob, sink and faucet.
island=scene.include('island',Asset('Pale kitchen island'))
L,D=2.55,1.12
ix,iy=.10,-.05
cube(island,'recessed_dark_plinth',(L-.13,D-.12,.10),(ix,iy,.05),(.17,.18,.17))
cube(island,'carcass',(L,D,.80),(ix,iy,.50),ivory)
cube(island,'solid_left_end',(.075,D,.86),(ix-L/2+.0375,iy,.53),(.58,.60,.58))
for i,(z,h) in enumerate([(.235,.245),(.498,.245),(.761,.245)]):
    cube(island,'drawer_%d'%i,(L-.095,.027,h),(ix+.025,iy-D/2-.018,z),(.66,.68,.66))
cube(island,'countertop',(L+.035,D+.035,.035),(ix,iy,.9575),(.80,.81,.76))
cube(island,'flush_hob',(.77,.53,.003),(ix-.47,iy-.02,.977),(.71,.73,.69))
for i,xx in enumerate([ix-.69,ix-.29]):
    cube(island,'hob_zone_%d'%i,(.29,.37,.0015),(xx,iy-.02,.979),(.75,.77,.72))
cube(island,'sink_rim',(.47,.38,.006),(ix+.64,iy+.16,.979),(.58,.61,.58))
cube(island,'sink_basin',(.405,.315,.007),(ix+.64,iy+.16,.981),(.38,.43,.41))
cube(island,'sink_inner',(.33,.25,.008),(ix+.64,iy+.16,.985),(.47,.51,.48))
island.include('faucet',sweep_tube(
    points=[(ix+.65,iy+.41,.98),(ix+.65,iy+.41,1.19),
            (ix+.65,iy+.37,1.23),(ix+.65,iy+.22,1.23),
            (ix+.65,iy+.19,1.19)],radius=.014,color=(.53,.58,.56)))
island.include('faucet_lever',rod(radius=.008,
    start=(ix+.70,iy+.41,1.01),end=(ix+.77,iy+.41,1.09),color=(.57,.60,.58)))

hood=scene.include('extractor',Asset('Suspended rectangular stone hood'))
cube(hood,'stone_shell',(1.05,.90,1.85),(ix-.12,iy+.12,2.91),stone)
cube(hood,'underside',(1.02,.87,.025),(ix-.12,iy+.12,1.976),(.51,.53,.49))
cube(hood,'filter',(.68,.53,.008),(ix-.12,iy+.12,1.960),(.24,.26,.24))
for i in range(8):
    cube(hood,'filter_slot_%d'%i,(.55,.008,.002),(ix-.12,iy-.10+i*.055,1.955),(.15,.17,.15))
cube(hood,'small_control',(.065,.018,.017),(ix-.14,iy-.34,1.992),(.32,.34,.30))

# Rear kitchen maps to base run, upper doors and illuminated working niche.
kitchen=scene.include('rear_kitchen',Asset('Rear cabinetry'))
back_y=1.92
cube(kitchen,'base_run',(4.85,.64,.91),(-.15,back_y,.475),dark)
cube(kitchen,'rear_worktop',(4.91,.70,.035),(-.15,back_y-.015,.9475),(.13,.14,.13))
for i in range(8):
    cube(kitchen,'base_front_%d'%i,(.585,.025,.76),(-2.29+i*.605,back_y-.334,.49),(.055,.061,.057))
cube(kitchen,'backsplash',(4.8,.025,.84),(-.16,2.245,1.39),(.045,.051,.047))
for i in range(7):
    cube(kitchen,'backsplash_joint_%d'%i,(.006,.005,.82),(-2.45+i*.72,2.226,1.38),(.075,.079,.071))
cube(kitchen,'upper_cupboard_run',(4.82,.48,.52),(-.15,2.06,2.12),(.075,.082,.078))
for i in range(8):
    cube(kitchen,'upper_door_%d'%i,(.59,.023,.50),(-2.28+i*.605,1.805,2.12),(.064,.071,.066))
cube(kitchen,'warm_niche_back',(2.75,.02,.36),(-.62,2.21,1.19),(.29,.23,.19))
cube(kitchen,'strip_light',(2.72,.035,.014),(-.62,1.86,1.392),(.93,.79,.60))
cube(kitchen,'left_tall_cabinet',(.73,.83,2.52),(-2.96,1.82,1.26),(.046,.052,.049))
for i,z in enumerate([.89,2.17]):
    cube(kitchen,'left_tall_reveal_%d'%i,(.70,.004,.008),(-2.96,1.402,z),(.025,.030,.028))

tower=scene.include('oven_bank',Asset('Right oven cabinet bank'))
cube(tower,'tower_body',(.91,.82,2.46),(1.93,1.90,1.23),(.055,.061,.057))
cube(tower,'left_trim',(.07,.035,1.32),(1.52,1.472,1.28),(.14,.15,.14))
for i,z in enumerate([1.00,1.62]):
    cube(tower,'oven_metal_frame_%d'%i,(.69,.035,.55),(1.93,1.472,z),(.29,.31,.29))
    cube(tower,'oven_glass_%d'%i,(.59,.015,.38),(1.93,1.447,z-.025),(.021,.036,.038))
    cube(tower,'oven_control_band_%d'%i,(.64,.02,.09),(1.93,1.443,z+.207),(.27,.29,.27))
    cube(tower,'oven_handle_%d'%i,(.52,.045,.026),(1.93,1.405,z+.12),(.49,.51,.48))
cube(tower,'bottom_door',(.72,.025,.54),(1.93,1.473,.29),(.065,.070,.064))
cube(room,'right_partition',(.19,1.05,2.86),(2.64,2.05,1.43),(.31,.33,.31))
cube(room,'rear_bulkhead',(1.65,.65,.38),(2.13,2.21,2.68),(.34,.36,.34))
cube(room,'right_dark_panel',(.70,.09,2.15),(2.74,1.43,1.075),(.035,.042,.038))

kettle=scene.include('red_kettle',Asset('Red kettle'))
cube(kettle,'base',(.23,.18,.025),(-.63,1.88,.98),(.018,.019,.018))
kettle.include('red_body',ball(radius=.103,center=(-.63,1.88,1.085),color=(.65,.008,.025)))
cube(kettle,'lower_dark_band',(.17,.15,.052),(-.63,1.855,1.025),(.025,.025,.022))
kettle.include('handle',sweep_tube(
    points=[(-.70,1.89,1.09),(-.72,1.89,1.19),(-.67,1.89,1.225),
            (-.58,1.89,1.225),(-.54,1.89,1.18),(-.55,1.89,1.10)],
    radius=.014,color=(.035,.026,.024)))
kettle.include('spout',rod(radius=.025,start=(-.71,1.84,1.09),
    end=(-.77,1.82,1.14),color=(.18,.18,.16)))

posts=scene.include('timber_posts',Asset('Timber columns'))
# Reposition the foreground support for the revised camera's parallax.
cube(posts,'foreground_post',(.35,.37,4.35),(-2.28,-.28,2.175),(.37,.225,.115))
cube(posts,'far_right_post',(.17,.20,3.4),(3.02,1.49,1.70),(.45,.29,.15))

# Audit: no fillets; all dimensions and radii positive; all sibling keys unique.
# Floor, cabinetry, island and posts contact z=0. Counter parts contact their
# explicit supporting slabs. No persistent bindings or dependency cycles.
realize(scene)

def descendants(obj):
    yield obj
    for child in obj.children:
        yield from descendants(child)

def material_for_group(group_name,factory):
    marker=bpy.data.objects.get(group_name)
    if marker:
        for obj in descendants(marker):
            if obj.type=='MESH':
                obj.data.materials.clear()
                obj.data.materials.append(factory())

def wood_material():
    m=bpy.data.materials.new('Warm oak vertical grain')
    m.use_nodes=True
    n,l=m.node_tree.nodes,m.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.62
    tex=n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=4
    tex.inputs['Detail'].default_value=3.5
    coord=n.new('ShaderNodeTexCoord')
    mapping=n.new('ShaderNodeVectorMath')
    mapping.operation='MULTIPLY'
    mapping.inputs[1].default_value=(7,7,.20)
    l.new(coord.outputs['Generated'],mapping.inputs[0])
    l.new(mapping.outputs[0],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.20
    ramp.color_ramp.elements[0].color=(.16,.075,.028,1)
    ramp.color_ramp.elements[1].position=.82
    ramp.color_ramp.elements[1].color=(.51,.33,.18,1)
    l.new(tex.outputs['Fac'],ramp.inputs[0])
    l.new(ramp.outputs[0],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.19
    bump.inputs['Distance'].default_value=.016
    l.new(tex.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs[0],bs.inputs['Normal'])
    return m
material_for_group('timber_posts',wood_material)

def plaster_material():
    m=bpy.data.materials.new('Fine pale limestone')
    m.use_nodes=True
    n,l=m.node_tree.nodes,m.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(.70,.70,.64,1)
    bs.inputs['Roughness'].default_value=.82
    noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=65
    noise.inputs['Detail'].default_value=2
    bump=n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.16
    bump.inputs['Distance'].default_value=.008
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs[0],bs.inputs['Normal'])
    return m
material_for_group('stone_shell',plaster_material)

# Camera pose and focal length remain independent of geometry dimensions.
set_view(position=(-5.4,-2.6,1.95),target=(0,.5,1.38),
         lens=42,sensor=36,shift=(0,0))
sc=bpy.context.scene
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
if sc.world is None:
    sc.world=bpy.data.worlds.new('World')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.29,.32,.30,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.25
area_emitter(position=(-2.4,-3.3,3.4),power=850,size=4,
             target=(0,.2,.8),color=(1,.95,.85))
area_emitter(position=(3,-.6,3.4),power=500,size=3,
             target=(.2,0,1),color=(.87,.94,1))
area_emitter(position=(-.7,1.77,1.39),power=35,size=1.8,
             target=(-.7,2.18,1.12),color=(1,.72,.50))
area_emitter(position=(-2.6,1,3.35),power=230,size=2,
             target=(-1,1.6,1),color=(1,.95,.85))
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
