from sceneact import *
import bpy
import math

# Estimated image anchors (upper-left origin):
# foreground timber: x=.17-.30; island corners (.33,.59),(.62,.62),(.90,.57),(.62,.85)
# hood: top (.42,.08),(.56,.045),(.73,.15); bottom (.42,.425),(.72,.435)
# Camera is nearly level; a leftward viewpoint reveals the island's left end.
CAMERA = (-3.65, -6.7, 1.78)
TARGET = (0.05, 0.1, 1.78)
LENS = 36
ISLAND_CENTER = (.35, -.48)
ISLAND_WIDTH = 2.38
ISLAND_DEPTH = 1.10
CEILING_HEIGHT = 3.65
KEY_POWER = 1150

scene = Scene('Dark contemporary kitchen')
ivory = (.62,.64,.61)
black = (.027,.033,.032)
charcoal = (.065,.073,.072)
steel = (.36,.39,.38)

def cube(parent, name, size, center, color):
    return parent.include(name, box(size=size, center=center, color=color))

architecture = Asset('Room')
cube(architecture,'floor',(14,13,.12),(0,0,-.07),(.65,.64,.59))
cube(architecture,'rear_wall',(8,.16,3.65),(0,2.03,1.825),(.30,.32,.30))
cube(architecture,'left_wall',(.15,7,3.65),(-3.4,.0,1.825),(.34,.35,.32))
cube(architecture,'ceiling',(10,10,.12),(0,0,3.71),(.038,.045,.043))
scene.include('architecture',architecture)

# Fine grout lines remain separate editable geometry.
tiles = Asset('Large pale floor tiles')
for i in range(-5,7):
    cube(tiles,f'joint_x_{i}',(.006,12,.002),(i*.9,0,-.008),(.39,.39,.36))
for i in range(-5,7):
    cube(tiles,f'joint_y_{i}',(12,.006,.002),(0,i*.9,-.008),(.39,.39,.36))
scene.include('floor_joints',tiles)

ceiling = Asset('Exposed dark ceiling structure')
for i,x in enumerate([-3,-1.9,-.8,.3,1.4,2.5,3.6]):
    cube(ceiling,f'joist_{i}',(.085,7,.20),(x,.1,3.54),(.027,.034,.033))
for i,y in enumerate([-.9,.9,2.0]):
    cube(ceiling,f'cross_beam_{i}',(9,.20,.32),(0,y,3.41),(.045,.053,.051))
for i,x in enumerate([-.9,-.5,-.1,.3,.7,1.1,1.5,1.9,2.3,2.7,3.1]):
    cube(ceiling,f'roof_seam_{i}',(.016,7,.025),(x,0,3.635),(.012,.016,.015))
ceiling.include('utility_pipe',rod(radius=.027,start=(-2.7,1.25,3.36),end=(2.9,1.25,3.36),color=(.10,.12,.12)))
scene.include('ceiling_structure',ceiling)

# Warm timber columns, including the large cropped foreground occluder.
posts = Asset('Timber support columns')
cube(posts,'foreground_column',(.37,.39,4.5),(-1.68,-2.10,1.92),(.38,.235,.115))
cube(posts,'rear_right_column',(.19,.20,3.6),(2.74,1.36,1.8),(.48,.31,.17))
scene.include('wood_columns',posts)

back = Asset('Rear kitchen cabinetry')
cube(back,'lower_bank',(4.15,.68,.87),(-.35,1.55,.435),black)
cube(back,'dark_worktop',(4.22,.73,.045),(-.35,1.51,.892),(.055,.059,.055))
cube(back,'stone_backsplash',(4.28,.045,.84),(-.35,1.91,1.32),(.039,.044,.041))
for i,x in enumerate([-2.02,-1.31,-.60,.11,.82]):
    cube(back,f'base_front_{i}',(.695,.028,.77),(x,1.185,.445),(.047,.052,.049))
cube(back,'upper_cabinets',(3.65,.52,.43),(-.54,1.66,2.01),(.075,.084,.079))
cube(back,'warm_lit_splash',(2.45,.025,.37),(-.49,1.873,1.155),(.30,.245,.205))
cube(back,'upper_light_strip',(2.55,.04,.014),(-.48,1.55,1.79),(.72,.61,.43))
scene.include('rear_counter',back)

tall = Asset('Tall black cabinet on left')
cube(tall,'carcass',(.74,.80,2.43),(-2.49,1.37,1.215),(.025,.031,.030))
cube(tall,'door',(.715,.035,2.36),(-2.49,.955,1.215),(.057,.065,.062))
cube(tall,'horizontal_seam',(.72,.012,.008),(-2.49,.931,2.05),(.015,.019,.018))
scene.include('left_tall_cabinet',tall)

ovens = Asset('Oven tower')
cube(ovens,'tower',(.76,.76,2.32),(1.72,1.51,1.16),(.035,.040,.038))
for i,z in enumerate([1.00,1.57]):
    cube(ovens,f'oven_frame_{i}',(.65,.035,.49),(1.72,1.111,z),(.25,.27,.25))
    cube(ovens,f'oven_glass_{i}',(.555,.022,.32),(1.72,1.085,z+.035),(.018,.037,.043))
    cube(ovens,f'oven_control_{i}',(.58,.024,.072),(1.72,1.076,z+.208),(.105,.12,.12))
    cube(ovens,f'oven_handle_{i}',(.48,.065,.026),(1.72,1.043,z-.13),(.47,.48,.44))
cube(ovens,'bottom_door',(.65,.03,.65),(1.72,1.107,.34),(.043,.048,.045))
scene.include('ovens',ovens)

right = Asset('Right dark architectural cabinet')
cube(right,'black_wall',(.98,.74,2.40),(2.58,1.47,1.20),(.025,.031,.030))
cube(right,'front_panel',(.92,.045,2.13),(2.58,1.074,1.10),(.041,.047,.044))
cube(right,'top_gray_band',(1.18,.84,.31),(2.48,1.51,2.40),(.29,.32,.30))
scene.include('right_cabinet',right)

island = Asset('Pale island with three wide drawers')
ix,iy = ISLAND_CENTER
cube(island,'recessed_toe',(ISLAND_WIDTH-.10,ISLAND_DEPTH-.10,.105),(ix,iy,.077),(.15,.17,.16))
cube(island,'body',(ISLAND_WIDTH,ISLAND_DEPTH,.80),(ix,iy,.505),ivory)
cube(island,'left_end',(.055,ISLAND_DEPTH,.86),(ix-ISLAND_WIDTH/2-.005,iy,.49),(.51,.54,.52))
for i,z in enumerate([.235,.503,.771]):
    cube(island,f'drawer_{i}',(ISLAND_WIDTH-.065,.032,.252),(ix+.012,iy-ISLAND_DEPTH/2-.023,z),(.66,.68,.65))
    cube(island,f'shadow_reveal_{i}',(ISLAND_WIDTH-.065,.015,.012),(ix+.012,iy-ISLAND_DEPTH/2-.043,z+.131),(.21,.24,.23))
cube(island,'stone_counter',(ISLAND_WIDTH+.035,ISLAND_DEPTH+.035,.036),(ix,iy,.936),(.76,.77,.71))
scene.include('island',island)

# Shallow inset sink and slender curved chrome tap.
sink = Asset('Sink and faucet')
sx,sy = .75,-.12
cube(sink,'sink_rim',(.57,.40,.007),(sx,sy,.959),(.53,.56,.53))
cube(sink,'sink_bowl',(.51,.34,.008),(sx,sy,.964),(.38,.42,.40))
cube(sink,'basin_bottom',(.43,.27,.006),(sx,sy,.970),(.55,.58,.54))
sink.include('tap_base',rod(radius=.031,length=.025,center=(sx,sy+.26,.97),color=steel))
sink.include('tap',sweep_tube(points=[(sx,sy+.26,.98),(sx,sy+.26,1.15),(sx,sy+.24,1.21),(sx,sy+.18,1.23),(sx,sy+.10,1.21),(sx,sy+.08,1.15)],radius=.012,color=(.61,.66,.65)))
scene.include('sink',sink)
hob = Asset('Pale flush induction panel')
cube(hob,'glass_panel',(.69,.44,.005),(-.37,-.64,.958),(.69,.71,.65))
for i,x in enumerate([-.55,-.20]):
    cube(hob,f'zone_mark_{i}',(.19,.20,.002),(x,-.65,.962),(.75,.77,.70))
scene.include('cooktop',hob)

hood = Asset('Large suspended pale plaster extractor')
cube(hood,'monolithic_enclosure',(1.17,.89,1.92),(-.12,.04,2.84),(.70,.69,.62))
cube(hood,'bottom_plate',(1.13,.85,.024),(-.12,.04,1.874),(.47,.48,.43))
cube(hood,'underside_vent',(.68,.46,.013),(-.12,.04,1.857),(.20,.22,.20))
scene.include('extractor',hood)

kettle = Asset('Small red kettle')
kettle.include('red_body',ball(radius=.095,center=(-.48,1.50,1.005),color=(.65,.008,.015)))
cube(kettle,'dark_base',(.17,.14,.04),(-.48,1.50,.925),(.012,.014,.013))
kettle.include('handle',sweep_tube(points=[(-.56,1.50,1.04),(-.56,1.50,1.13),(-.49,1.50,1.16),(-.41,1.50,1.12),(-.40,1.50,1.04)],radius=.017,color=(.035,.026,.023)))
scene.include('red_kettle',kettle)

# All dimensions are positive; no fillets used; all repeated keys are indexed.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient world')
sc.world.use_nodes = True
sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value = (.19,.21,.19,1)
sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value = .35

# Edit only descendant meshes of each intended named group.
def mesh_children(group_name):
    root = bpy.data.objects.get(group_name)
    return [o for o in root.children_recursive if o.type == 'MESH'] if root else []

for obj in mesh_children('wood_columns'):
    for slot in obj.material_slots:
        if not slot.material:
            continue
        mat = slot.material.copy()
        slot.material = mat
        mat.use_nodes = True
        nt = mat.node_tree
        bs = nt.nodes.get('Principled BSDF')
        tex = nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 4
        tex.inputs['Detail'].default_value = 3
        coord = nt.nodes.new('ShaderNodeTexCoord')
        mapping = nt.nodes.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (6,6,.24)
        nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .20
        ramp.color_ramp.elements[0].color = (.15,.075,.029,1)
        ramp.color_ramp.elements[1].position = .80
        ramp.color_ramp.elements[1].color = (.49,.31,.15,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value = .65

for obj in mesh_children('extractor'):
    for slot in obj.material_slots:
        if slot.material:
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            nt = mat.node_tree
            noise = nt.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 95
            bump = nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = .15
            bump.inputs['Distance'].default_value = .012
            nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])

set_view(CAMERA,TARGET,lens=LENS,sensor=36,shift=(0,.015))
area_emitter((-3.0,-3.0,3.15),power=KEY_POWER,size=4.2,target=(0,0,.9),color=(1,.93,.82))
area_emitter((1.3,-.5,3.30),power=470,size=2.8,target=(.3,-.2,.6),color=(.88,.94,1))
area_emitter((-.5,1.48,1.72),power=34,size=1.8,target=(-.5,1.86,1.15),color=(1,.72,.51))
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
