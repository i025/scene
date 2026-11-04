from sceneact import *
import bpy, math

# Observations: narrow shipboard room, red deck, cream structure, three left
# bunks, dark foreground ventilation cabinets, rear lockers, chair, workbench,
# red fire equipment, chalkboard, overhead pipes and suspended white lamps.
# Approximate landmarks: post x=277, lamp=(149,82), bunk upright x=152,
# lockers=(191,240), chair=(184,302). Camera calibration is uncertain.
scene = Scene('Ship compartment')
cream=(.64,.63,.50)
lightcream=(.76,.76,.65)
red=(.29,.075,.045)
steel=(.39,.43,.40)
dark=(.035,.065,.060)
green=(.055,.13,.12)

def B(parent,key,size,center,color):
    return parent.include(key,box(size=size,center=center,color=color))
def R(parent,key,r,a,b,color):
    return parent.include(key,rod(radius=r,start=a,end=b,color=color))
def asset(name):
    return scene.include(name,Asset(name))

# Architecture builder: deck, bulkheads, structural beamwork.
room=asset('architecture')
B(room,'deck',(5.6,12,.12),(0,1,-.06),red)
B(room,'left_bulkhead',(.14,10,3.4),(-2.05,1.5,1.7),cream)
B(room,'rear_bulkhead',(4.25,.15,3.4),(0,5.25,1.7),cream)
B(room,'right_return',(.15,4,3.4),(2.05,3.3,1.7),lightcream)
B(room,'right_equipment_wall',(1.45,.15,3.4),(1.55,1.65,1.7),lightcream)
B(room,'right_red_base',(1.45,.05,.48),(1.55,1.55,.24),red)
B(room,'ceiling',(4.3,10,.16),(0,1.5,3.47),(.36,.34,.25))
for i,y in enumerate([-2.6,-.4,1.8,4]):
    B(room,f'overhead_crossbeam_{i}',(4.2,.17,.27),(0,y,3.25),(.49,.37,.23))
for i,x in enumerate([-1.75,-1.15,-.45,.55,1.5]):
    B(room,f'ceiling_rib_{i}',(.10,8.7,.14),(x,1.1,3.28),(.50,.43,.31))
# Main steel support with the two distinct paint bands.
post=asset('foreground_support')
R(post,'lower_red',.105,(.69,-1.00,.03),(.69,-1.00,1.52),(.28,.075,.045))
R(post,'upper_cream',.105,(.69,-1,1.52),(.69,-1,3.48),(.67,.60,.40))
R(post,'foot_collar',.14,(.69,-1,.015),(.69,-1,.06),(.38,.23,.14))
B(room,'near_right_doorjamb',(.15,.22,3.3),(1.66,-2.6,1.65),(.29,.085,.05))
# Deck seams provide restrained surface cues.
for i,y in enumerate([-.9,.1,1.1,2.1,3.1,4.1]):
    B(room,f'deck_seam_{i}',(4,.008,.003),(0,y,.004),(.20,.065,.042))

# Left bunk builder: tubular frame, three supported thin pale mattresses.
bunks=asset('three_tier_bunks')
for i,z in enumerate([.48,1.12,1.78]):
    B(bunks,f'pan_{i}',(1.05,3.05,.075),(-1.30,1.70,z),(.16,.21,.19))
    B(bunks,f'mattress_{i}',(1.01,2.99,.115),(-1.30,1.70,z+.09),(.66,.69,.61))
    B(bunks,f'folded_blanket_{i}',(.98,.55,.065),(-1.30,2.83,z+.17),(.57,.59,.50))
    B(bunks,f'pillow_{i}',(.72,.39,.13),(-1.30,2.81,z+.22),(.77,.77,.67))
    R(bunks,f'outer_edge_{i}',.023,(-.75,.13,z+.04),(-.75,3.26,z+.04),dark)
for i,(x,y) in enumerate([(-1.86,.15),(-.74,.15),(-1.86,3.26),(-.74,3.26)]):
    R(bunks,f'post_{i}',.026,(x,y,.03),(x,y,2.73),dark)
R(bunks,'top_side_rail',.025,(-.74,.15,2.61),(-.74,3.26,2.61),dark)
for i,y in enumerate([.15,3.26]):
    R(bunks,f'top_end_rail_{i}',.023,(-1.86,y,2.61),(-.74,y,2.61),dark)
# Dark transverse framing visible in front of the rear furniture.
R(bunks,'extended_upright',.027,(-.73,.12,0),(-.73,.12,3.04),(.025,.032,.028))
R(bunks,'upper_crossbar',.025,(-.73,.12,2.78),(.55,.12,2.78),dark)
R(bunks,'back_upright',.025,(.55,.12,.02),(.55,.12,2.78),dark)
R(bunks,'low_crossbar',.024,(-.73,.12,.06),(.55,.12,.06),dark)

# Left foreground shelf and the two distinctive slotted electrical boxes.
shelf=asset('foreground_left_shelf')
B(shelf,'worktop',(.85,2.45,.10),(-1.69,-1.56,.62),green)
B(shelf,'lower_shelf',(.85,2.45,.10),(-1.69,-1.56,.14),(.055,.10,.08))
for i,y in enumerate([-2.65,-.48]):
    B(shelf,f'leg_{i}',(.07,.08,.60),(-1.30,y,.30),dark)
for i,y in enumerate([-1.96,-1.02]):
    cab=Asset(f'ventilator_{i}')
    B(cab,'body',(.57,.67,.83),(-1.66,y,1.085),(.045,.09,.085))
    B(cab,'front_inset',(.015,.53,.70),(-1.365,y,1.085),(.08,.12,.11))
    for j in range(17):
        B(cab,f'louvre_{j}',(.027,.48,.014),(-1.346,y,.77+j*.037),(.26,.32,.29))
    B(cab,'top_cap',(.65,.73,.055),(-1.66,y,1.52),(.065,.13,.12))
    shelf.include(f'cabinet_{i}',cab)

# Wall-mounted cream heater on the upper left.
heater=asset('left_wall_heater')
B(heater,'case',(.26,.70,.86),(-1.87,-.10,2.24),(.62,.62,.52))
B(heater,'dark_grille',(.018,.53,.49),(-1.726,-.1,2.16),(.055,.075,.07))
for j in range(6):
    B(heater,f'grille_slat_{j}',(.025,.55,.037),(-1.71,-.10,1.95+j*.081),(.70,.70,.60))
B(heater,'upper_label',(.02,.23,.055),(-1.71,-.1,2.53),(.26,.29,.25))

# Rear lockers builder, with seams, vents and small hardware.
lockers=asset('rear_steel_lockers')
for i,x in enumerate([-.63,-.12,.39]):
    B(lockers,f'body_{i}',(.49,.62,1.88),(x,3.84,.97),steel)
    B(lockers,f'door_{i}',(.46,.035,1.80),(x,3.51,.97),(.46,.49,.44))
    for j in range(5):
        B(lockers,f'vent_{i}_{j}',(.23,.013,.018),(x,3.484,1.55-j*.057),(.25,.29,.26))
    B(lockers,f'handle_{i}',(.027,.035,.12),(x+.15,3.465,1.07),(.16,.19,.17))
    B(lockers,f'label_{i}',(.12,.013,.05),(x,3.476,1.73),(.69,.70,.61))
    B(lockers,f'foot_{i}',(.37,.43,.10),(x,3.84,.05),(.24,.28,.24))
for i,x in enumerate([-.65,-.25,.25]):
    lockers.include(f'top_roll_{i}',ball(.14,center=(x,3.83,2.02),color=(.48,.49,.40)))

# Chair builder, all parts share one movable semantic group.
chair=asset('pale_metal_chair')
B(chair,'seat',(.48,.46,.065),(-.30,2.09,.49),(.49,.48,.35))
for i,x in enumerate([-.51,-.09]):
    for j,y in enumerate([1.90,2.28]):
        R(chair,f'leg_{i}_{j}',.018,(x,y,.03),(x,y,.48),(.55,.55,.43))
    R(chair,f'back_post_{i}',.019,(x,2.29,.45),(x,2.35,1.02),(.58,.57,.45))
B(chair,'backrest',(.46,.065,.25),(-.30,2.34,.87),(.56,.55,.42))
for i,x in enumerate([-.55,-.05]):
    R(chair,f'arm_front_{i}',.018,(x,1.92,.47),(x,1.92,.70),(.57,.57,.45))
    R(chair,f'arm_{i}',.019,(x,1.92,.70),(x,2.30,.73),(.57,.57,.45))

# Rear utility counter and industrial plumbing.
desk=asset('rear_workbench')
B(desk,'counter',(.84,.68,.10),(.67,2.20,.91),(.23,.25,.20))
B(desk,'cabinet',(.72,.56,.82),(.67,2.23,.45),(.23,.27,.23))
B(desk,'door',(.59,.025,.65),(.67,1.935,.45),(.28,.31,.26))
B(desk,'handle',(.14,.025,.023),(.67,1.91,.71),(.12,.15,.12))
for i,x in enumerate([.40,.86]):
    R(desk,f'riser_{i}',.029,(x,2.37,.96),(x,2.37,2.85),(.16,.19,.15))
R(desk,'connecting_pipe',.035,(.4,2.37,2.85),(.86,2.37,2.85),(.18,.20,.16))
B(desk,'small_instrument',(.17,.12,.25),(.50,2.15,1.08),(.39,.39,.30))

# Right bulkhead objects face the camera.
wallitems=asset('right_wall_equipment')
B(wallitems,'chalkboard_frame',(.77,.055,.83),(1.46,1.55,2.03),(.30,.31,.25))
B(wallitems,'chalkboard',(.69,.018,.75),(1.46,1.512,2.03),(.18,.23,.21))
B(wallitems,'paper_notice',(.30,.015,.51),(1.99,1.51,1.75),(.75,.75,.66))
fire=Asset('red_fire_station')
B(fire,'backplate',(.30,.045,.62),(1.22,1.46,1.14),(.67,.045,.025))
R(fire,'extinguisher_body',.10,(1.22,1.37,.90),(1.22,1.37,1.25),(.78,.055,.025))
fire.include('rounded_top',ball(.10,center=(1.22,1.37,1.25),color=(.76,.05,.025)))
R(fire,'handle',.021,(1.15,1.36,1.36),(1.29,1.36,1.36),(.23,.22,.16))
B(fire,'label',(.105,.015,.15),(1.22,1.258,1.13),(.79,.75,.59))
wallitems.include('fire_station',fire)

# Cropped right foreground green bench.
bench=asset('foreground_right_bench')
B(bench,'seat',(.48,1.64,.075),(1.32,-2.13,.47),(.035,.10,.075))
for i,y in enumerate([-2.80,-1.46]):
    for j,x in enumerate([1.13,1.50]):
        R(bench,f'leg_{i}_{j}',.018,(x,y,.015),(x,y,.44),(.10,.14,.11))
R(bench,'lower_brace',.015,(1.13,-2.80,.16),(1.13,-1.46,.16),dark)

# Overhead pipes, cable runs, and visible lamp shades.
pipes=asset('overhead_services')
for i,x in enumerate([-1.7,-1.29,.27]):
    R(pipes,f'longitudinal_pipe_{i}',.044,(x,-3.4,2.94),(x,4.95,2.94),(.60,.61,.51))
    for j,y in enumerate([-1.8,.2,2.2,4.2]):
        R(pipes,f'pipe_hanger_{i}_{j}',.013,(x,y,2.94),(x,y,3.4),(.23,.24,.19))
for i,y in enumerate([.1,2.6,4.4]):
    R(pipes,f'cross_pipe_{i}',.034,(-1.95,y,2.85),(.8,y,2.85),(.59,.61,.51))
R(pipes,'rear_vertical',.055,(.92,4.96,1.4),(.92,4.96,3.25),(.42,.43,.34))
R(pipes,'black_cable',.017,(-.65,-1.9,3.22),(-.65,4.5,3.22),(.025,.03,.023))
lamps=[]
for i,(x,y,z,r) in enumerate([(-.62,-.95,2.94,.27),(-.52,1.80,2.89,.19),(-.35,3.75,2.88,.16)]):
    a=Asset(f'hanging_lamp_{i}')
    R(a,'stem',.023,(x,y,z+.08),(x,y,3.35),(.22,.24,.20))
    # Stacked short rings approximate the shallow flared white metal shade.
    for j in range(6):
        rr=r*(1-.10*j)
        R(a,f'shade_ring_{j}',rr,(x,y,z+j*.022),(x,y,z+(j+1)*.022),(.77,.80,.72))
    R(a,'glowing_underside',r*.91,(x,y,z-.008),(x,y,z+.005),(.95,.98,.91))
    scene.include(f'ceiling_lamp_{i}',a)
    lamps.append((x,y,z))

# API audit: no fillet boxes; dimensions/radii positive, every loop key unique,
# no binding dependencies, supports explicitly meet deck or their shelf surfaces.
realize(scene)
set_view(position=(.02,-4.8,1.67),target=(.00,2.5,1.57),lens=23.5,sensor=36)

world=bpy.data.worlds.new('World') if bpy.context.scene.world is None else bpy.context.scene.world
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.29,.32,.28,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35
area_emitter((-.4,-1.4,3.05),power=180,size=1.5,target=(-.5,.4,.3),color=(1,.91,.74))
area_emitter((-.4,2.0,3.05),power=130,size=1.2,target=(0,2,.2),color=(.85,.94,1))
area_emitter((0,-4,2.5),power=90,size=3,target=(0,1,1.2),color=(1,.88,.72))
for i,(x,y,z) in enumerate(lamps):
    data=bpy.data.lights.new(f'bulb_{i}','POINT')
    data.energy=28
    data.color=(.90,.96,1)
    data.shadow_soft_size=.16
    ob=bpy.data.objects.new(f'bulb_{i}',data)
    bpy.context.collection.objects.link(ob)
    ob.location=(x,y,z-.08)

# Rough satin paint and restrained deck sheen.
for mat in bpy.data.materials:
    if mat.use_nodes:
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Roughness'].default_value=.64
for obj in bpy.data.objects:
    if obj.type=='MESH':
        for poly in obj.data.polygons:
            if len(poly.vertices)==4:
                pass
scene_bpy=bpy.context.scene
scene_bpy.render.engine='CYCLES'
scene_bpy.cycles.samples=32
scene_bpy.view_settings.view_transform='AgX'
scene_bpy.render.resolution_x=384
scene_bpy.render.resolution_y=512
scene_bpy.render.resolution_percentage=100
