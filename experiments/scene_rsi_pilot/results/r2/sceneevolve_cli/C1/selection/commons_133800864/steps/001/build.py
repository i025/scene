from sceneact import *
import bpy, math

# Window and blinds occupy approximately (0.00, 0.00) to (0.30, 0.80).
# Upper cabinet fills (0.30, 0.00) to (0.87, 0.54).
# Paper roll occupies (0.60, 0.08) to (0.84, 0.42).
# Hanging towel occupies (0.25, 0.48) to (0.46, 0.83).
# Counter spans the bottom quarter; dark sink is cropped at bottom left.
# Jug and blue filter pitcher occupy the lower right, below the cabinet.

scene = Scene('Kitchen corner')
ivory = (.76,.72,.59)
trim = (.86,.83,.72)
white = (.91,.89,.79)
steel = (.49,.48,.41)
dark = (.035,.041,.037)
counter_z = .91
cabinet_bottom = 1.64
camera_position = (-1.46,-3.25,2.13)
camera_target = (.03,.23,1.72)

def add(parent, name, node):
    parent.include(name, node)

# Architecture
architecture = Asset('Walls and window')
add(architecture,'rear_wall',box((3,.10,3.4),center=(.1,.65,1.7),color=(.72,.70,.59)))
add(architecture,'left_reveal',box((.11,.42,3.3),center=(-1.04,.38,1.65),color=trim))
add(architecture,'window_glass',box((.91,.025,2.52),center=(-.57,.56,1.88),color=(.62,.77,.80)))
for x in (-1.04,-.11):
    add(architecture,'window_frame_'+str(x),box((.055,.085,2.65),center=(x,.48,1.88),color=trim))
for z in (.56,1.78,3.19):
    add(architecture,'window_cross_'+str(z),box((.96,.065,.055),center=(-.57,.49,z),color=trim))
add(architecture,'window_center_mullion',box((.045,.065,2.55),center=(-.61,.48,1.88),color=trim))
# Loose outdoor color patches behind the slats.
for i,(x,z,r) in enumerate([(-.9,2.75,.13),(-.47,2.8,.14),(-.83,2.51,.10),(-.24,2.55,.12),(-.88,1.95,.10)]):
    add(architecture,'foliage_'+str(i),ball(r,center=(x,.545,z),color=(.44,.60,.48)))
for i in range(39):
    z=.65+i*.066
    slat=box((.96,.105,.018),center=(-.57,.365,z),color=(.83,.84,.77))
    slat.turn('x',-12)
    add(architecture,'blind_'+str(i),slat)
for i,x in enumerate((-.90,-.27)):
    add(architecture,'blind_tape_'+str(i),box((.014,.009,2.55),center=(x,.294,1.91),color=(.78,.77,.66)))
add(architecture,'pull_cord',rod(.004,start=(-.21,.26,2.55),end=(-.21,.26,1.94),color=white))
add(architecture,'cord_weight',rod(.009,length=.06,center=(-.21,.26,1.92),color=white))
scene.include('architecture',architecture)

cab = Asset('Cream wall cabinet')
add(cab,'body',box((1.05,.49,1.54),center=(.445,.375,2.41),color=ivory))
# Broad left cheek, front door and raised framing.
add(cab,'left_side',box((.045,.52,1.56),center=(-.09,.345,2.42),color=(.78,.75,.64)))
add(cab,'front_door',box((.99,.037,1.49),center=(.455,.105,2.43),color=(.78,.74,.62)))
for i,x in enumerate((.006,.904)):
    add(cab,'door_stile_'+str(i),box((.062,.029,1.46),center=(x,.073,2.43),color=ivory))
for i,z in enumerate((1.715,3.145)):
    add(cab,'door_rail_'+str(i),box((.95,.029,.067),center=(.455,.073,z),color=ivory))
add(cab,'recessed_panel',box((.76,.013,1.24),center=(.455,.083,2.43),color=(.76,.72,.60)))
add(cab,'bottom_edge',box((1.07,.53,.052),center=(.445,.348,1.66),color=(.82,.78,.66)))
add(cab,'knob_stem',rod(.014,start=(.888,.044,1.925),end=(.888,.001,1.925),color=steel))
add(cab,'knob',ball(.024,center=(.888,-.007,1.925),color=steel))
scene.include('cabinet',cab)

# Granite counter and inset dark sink.
counter = Asset('Counter and sink')
add(counter,'granite',box((2.65,1.13,.075),center=(.02,.05,counter_z-.038),color=(.32,.31,.25)))
add(counter,'backsplash',box((2.65,.055,.16),center=(.02,.585,.99),color=(.32,.31,.25)))
add(counter,'sink_rim',box((.79,.64,.018),center=(-.69,-.265,.925),color=(.38,.39,.34)))
add(counter,'sink_dark_basin',box((.70,.55,.025),center=(-.69,-.29,.935),color=(.026,.035,.031)))
for i,x in enumerate((-.99,-.39)):
    add(counter,'sink_side_'+str(i),box((.025,.55,.03),center=(x,-.29,.948),color=steel))
add(counter,'faucet_base',rod(.053,length=.025,center=(-.67,.061,.946),color=steel))
add(counter,'faucet_upright',rod(.018,start=(-.67,.061,.95),end=(-.67,.061,1.25),color=steel))
add(counter,'faucet_spout',sweep_tube(points=[(-.67,.061,1.25),(-.67,.045,1.30),(-.67,-.035,1.31),(-.67,-.11,1.27)],radius=.015,color=steel))
for i,x in enumerate((-.85,-.49)):
    add(counter,'tap_base_'+str(i),rod(.035,length=.025,center=(x,.045,.947),color=steel))
    add(counter,'tap_handle_'+str(i),rod(.012,start=(x,.045,.96),end=(x+.035,.045,1.02),color=steel))
scene.include('counter',counter)

# Wall-mounted towel ring and hanging folded cloth.
towel = Asset('Towel and ring')
add(towel,'mount',rod(.052,start=(-.075,.065,1.99),end=(-.075,-.002,1.99),color=steel))
add(towel,'mount_neck',rod(.018,start=(-.075,-.005,1.99),end=(-.075,-.075,1.99),color=steel))
ring_points=[]
for i in range(21):
    a=2*math.pi*i/20
    ring_points.append((-.075+.115*math.sin(a),-.082,1.865+.15*math.cos(a)))
add(towel,'ring',sweep_tube(points=ring_points,radius=.008,color=steel))
for i in range(7):
    x=-.16+i*.028
    top=1.745-.018*abs(i-3)
    bottom=1.087+.025*math.sin(i*1.6)
    strip=box((.040,.038,bottom-top if bottom>top else top-bottom),
              center=(x,-.125-.016*math.sin(i*1.3),(top+bottom)/2),
              color=(.83+.009*i,.80+.009*i,.71+.009*i))
    strip.turn('y',-5+2*i)
    add(towel,'cloth_fold_'+str(i),strip)
add(towel,'cloth_fold_over_ring',resized(ball(.105,center=(-.075,-.105,1.735),color=white),(1,.46,.47)))
scene.include('towel',towel)

# Vertical paper towel holder.
paper=Asset('Paper towel dispenser')
roll_center=(.55,-.022,2.30)
add(paper,'roll',rod(.145,length=.69,center=roll_center,color=(.91,.88,.77)))
add(paper,'paper_outer_sheet',box((.245,.016,.65),center=(.55,-.166,2.30),color=(.92,.89,.79)))
add(paper,'upper_spindle',rod(.018,length=.12,center=(.55,-.022,2.69),color=steel))
add(paper,'finial',resized(ball(.032,center=(.55,-.022,2.75),color=steel),(.8,.8,1.25)))
for i,x in enumerate((.43,.67)):
    add(paper,'lower_bracket_'+str(i),ball(.027,center=(x,-.007,1.94),color=(.24,.24,.20)))
add(paper,'holder_arm',rod(.018,start=(.55,.09,1.96),end=(.55,-.06,1.96),color=steel))
scene.include('paper',paper)

# Countertop blender, canister and small metal cup.
appliances=Asset('Countertop accessories')
add(appliances,'blender_base',resized(ball(.105,center=(.205,.31,1.045),color=(.035,.041,.036)),(.9,.9,1.22)))
add(appliances,'blender_collar',rod(.072,length=.045,center=(.205,.31,1.15),color=dark))
cup=rod(.068,length=.27,center=(.20,.31,1.302),color=(.36,.39,.35))
cup.turn('y',-10)
add(appliances,'blender_clear_cup',cup)
add(appliances,'cup_highlight',rod(.006,start=(.165,.244,1.19),end=(.123,.244,1.44),color=(.70,.72,.65)))
add(appliances,'green_canister',rod(.063,length=.23,center=(-.035,.265,1.035),color=(.35,.37,.22)))
add(appliances,'canister_rim',rod(.067,length=.018,center=(-.035,.265,1.158),color=steel))
add(appliances,'small_cup',rod(.048,length=.068,center=(-.30,-.01,.956),color=(.28,.27,.20)))
add(appliances,'small_cup_dark_top',rod(.037,length=.004,center=(-.30,-.01,.993),color=dark))
scene.include('accessories',appliances)

jug=Asset('Translucent water jug')
add(jug,'body',resized(ball(.155,center=(.47,-.05,1.102),color=(.69,.71,.65)),(1,.78,1.12)))
add(jug,'lower_body',box((.255,.205,.14),center=(.47,-.05,1.012),color=(.70,.72,.66)))
add(jug,'shoulder',resized(ball(.116,center=(.47,-.05,1.245),color=(.71,.73,.67)),(1,.83,.85)))
add(jug,'neck',rod(.035,length=.073,center=(.47,-.05,1.329),color=(.77,.78,.71)))
add(jug,'cap',rod(.038,length=.026,center=(.47,-.05,1.365),color=(.85,.84,.75)))
handle=subtract(resized(ball(.079,center=(.554,-.044,1.245),color=(.69,.71,.65)),(.78,.53,1.15)),
                resized(ball(.051,center=(.554,-.044,1.252)),(.75,1.2,1.12)))
add(jug,'handle',handle)
scene.include('jug',jug)

pitcher=Asset('Blue water filter pitcher')
add(pitcher,'blue_reservoir',resized(ball(.159,center=(.82,.245,1.125),color=(.055,.10,.20)),(1,.76,1.47)))
add(pitcher,'flat_base',rod(.121,length=.035,center=(.82,.245,.952),color=(.10,.14,.20)))
add(pitcher,'upper_blue_body',rod(.139,length=.185,center=(.82,.245,1.27),color=(.075,.13,.24)))
lid=resized(ball(.16,center=(.82,.245,1.376),color=(.38,.39,.34)),(1,.82,.22))
add(pitcher,'lid',lid)
add(pitcher,'spout',box((.065,.09,.037),center=(.69,.235,1.376),color=(.39,.40,.35)))
add(pitcher,'clear_handle',sweep_tube(points=[(.943,.245,1.32),(1.013,.245,1.29),(1.043,.245,1.18),(1.017,.245,1.04),(.949,.245,1.005)],radius=.023,color=(.53,.57,.54)))
add(pitcher,'front_glint',rod(.006,start=(.755,.124,1.02),end=(.745,.124,1.30),color=(.28,.35,.43)))
scene.include('pitcher',pitcher)

realize(scene)

# Procedural surface finishes keep the scene fully editable.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.63
    c=mat.diffuse_color
    if abs(c[0]-.32)<.018 and abs(c[1]-.31)<.018:
        nt=mat.node_tree
        noise=nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=165
        noise.inputs['Detail'].default_value=3
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.27
        ramp.color_ramp.elements[0].color=(.075,.067,.047,1)
        ramp.color_ramp.elements[1].position=.73
        ramp.color_ramp.elements[1].color=(.55,.50,.37,1)
        nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.22
        bump.inputs['Distance'].default_value=.006
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
    if abs(c[0]-.49)<.015:
        bs.inputs['Metallic'].default_value=.75
        bs.inputs['Roughness'].default_value=.28

set_view(camera_position,camera_target,lens=51,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.67,.70,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.35
area_emitter((-1.5,-.2,2.45),power=210,size=1.7,target=(.35,.2,1.4),color=(.83,.91,1))
area_emitter((.2,-2.5,3.0),power=130,size=2.5,target=(.3,.3,1.7),color=(1,.83,.61))
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
