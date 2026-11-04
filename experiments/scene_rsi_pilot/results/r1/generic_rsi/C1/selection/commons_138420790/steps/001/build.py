import bpy
import math
from sceneact import *

# Image landmarks (x/W,y/H): island top (.33,.59)-(.89,.57),
# island bottom (.62,.85); hood (.42,.05)-(.72,.43);
# timber post (.17,0)-(.30,.98); oven (.68,.44)-(.78,.58).
# Camera is almost level. Island depth and the hood's ceiling attachment
# are the principal uncertain proportions.
CAMERA = (-3.9, -6.2, 1.78)
TARGET = (0.0, 0.65, 1.78)
LENS = 39
ISLAND_L, ISLAND_D, ISLAND_H = 2.35, 1.17, 0.94
HOOD_BOTTOM, HOOD_TOP = 1.98, 3.80
KEY_POWER = 1250

scene = Scene('Industrial kitchen')
ivory = (.63,.64,.61)
stone = (.72,.72,.67)
black = (.032,.036,.034)
charcoal = (.065,.071,.069)
wood = (.34,.20,.105)

def block(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset('Architecture')
block(architecture,'floor',(14,14,.12),(0,0,-.06),(.57,.56,.51))
block(architecture,'rear_wall',(9,.16,4.3),(0,2.85,2.15),(.24,.25,.23))
block(architecture,'left_wall',(.16,8,4.3),(-3.5,1.5,2.15),(.31,.32,.29))
block(architecture,'ceiling',(10,10,.14),(0,0,3.88),(.035,.042,.040))
# Broad exposed beams and smaller roof joists.
for i,x in enumerate([-3.3,-1.8,-.3,1.2,2.7,4.2]):
    block(architecture,f'joist_{i}',(.12,8,.22),(x,.8,3.72),(.026,.032,.030))
for i,y in enumerate([-1.5,1.25,3.0]):
    block(architecture,f'main_beam_{i}',(10,.24,.38),(0,y,3.59),(.043,.052,.051))
scene.include('architecture',architecture)

# Large pale floor tiles with very fine grout lines.
tiles = Asset('Floor joints')
for i in range(-8,9):
    block(tiles,f'x_joint_{i}',(.008,13,.002),(i*.92,0,.001),(.40,.40,.37))
    block(tiles,f'y_joint_{i}',(13,.008,.002),(0,i*.92,.001),(.40,.40,.37))
scene.include('floor_joints',tiles)

island = Asset('Island')
block(island,'recessed_plinth',(ISLAND_L-.12,ISLAND_D-.13,.105),(0,0,.0525),(.20,.22,.21))
block(island,'cabinet_body',(ISLAND_L,ISLAND_D,.79),(0,0,.50),ivory)
block(island,'solid_left_end',(.055,ISLAND_D,.85),(-ISLAND_L/2-.01,0,.51),(.57,.59,.57))
# Handleless drawers on the long near face.
for i in range(3):
    z = .215+i*.245
    block(island,f'drawer_{i}',(ISLAND_L-.065,.035,.226),(0,-ISLAND_D/2-.022,z),(.65,.66,.63))
    block(island,f'drawer_shadow_{i}',(ISLAND_L-.07,.018,.012),(0,-ISLAND_D/2-.043,z+.116),(.27,.29,.28))
block(island,'stone_top',(ISLAND_L+.035,ISLAND_D+.035,.045),(0,0,.9275),stone)
# Flat inset cooktop on left half.
block(island,'cooktop_outline',(.62,.50,.006),(-.62,.03,.953),(.48,.49,.45))
block(island,'cooktop_surface',(.59,.47,.007),(-.62,.03,.956),(.66,.67,.61))
# Pale sink rim and dark shallow basin, toward the far edge.
block(island,'sink_rim',(.50,.38,.009),(.40,.28,.955),(.78,.79,.75))
block(island,'sink_basin',(.445,.325,.009),(.40,.28,.962),(.46,.49,.47))
block(island,'sink_bottom',(.37,.25,.009),(.40,.28,.967),(.57,.60,.57))
faucet = Part('Chrome faucet')
faucet.include('spout',sweep_tube(points=[
    (.59,.47,.96),(.59,.47,1.12),(.58,.47,1.18),
    (.52,.47,1.205),(.39,.47,1.205),(.35,.47,1.17),
    (.35,.47,1.105)],radius=.012,color=(.65,.69,.68)))
faucet.include('lever',rod(radius=.008,start=(.65,.47,.97),end=(.65,.47,1.07),color=(.55,.59,.58)))
island.include('faucet',faucet)
scene.include('island',island)

hood = Asset('Suspended stone extractor')
block(hood,'tall_rectangular_shell',(1.18,.96,HOOD_TOP-HOOD_BOTTOM),(-.18,.02,(HOOD_TOP+HOOD_BOTTOM)/2),(.72,.71,.65))
block(hood,'underside',(.99,.80,.018),(-.18,.02,HOOD_BOTTOM-.005),(.43,.44,.40))
block(hood,'bottom_edge',(1.19,.97,.025),(-.18,.02,HOOD_BOTTOM+.006),(.62,.62,.57))
block(hood,'small_control',(.035,.025,.012),(-.55,-.48,HOOD_BOTTOM+.025),(.25,.26,.23))
scene.include('extractor',hood)

back = Asset('Back kitchen cabinetry')
# Tall refrigerator volume on the left.
block(back,'left_tower',(1.02,.66,2.36),(-2.16,2.22,1.18),(.043,.048,.045))
block(back,'tower_front',(1.00,.025,2.31),(-2.16,1.875,1.18),(.060,.065,.060))
block(back,'tower_upper_seam',(1.0,.015,.009),(-2.16,1.854,2.02),(.023,.026,.024))
# Base cabinets and thin dark work surface.
block(back,'base_run',(3.65,.63,.89),(.12,2.23,.445),(.045,.050,.047))
block(back,'rear_counter',(3.75,.72,.045),(.12,2.18,.915),(.11,.12,.11))
block(back,'backsplash',(3.78,.055,.73),(.12,2.57,1.30),(.045,.054,.051))
block(back,'upper_cabinets',(3.58,.40,.48),(.05,2.43,1.98),(.034,.041,.038))
block(back,'warm_niche_back',(2.0,.025,.38),(-.48,2.525,1.18),(.27,.22,.19))
block(back,'niche_light_strip',(2.0,.025,.015),(-.48,2.49,1.39),(.85,.67,.47))
for i,x in enumerate([-1.25,-.45,.35,1.15]):
    block(back,f'base_seam_{i}',(.009,.012,.79),(x,1.906,.45),(.016,.02,.018))
# Right tall oven stack.
block(back,'oven_tower',(.87,.70,2.18),(1.77,2.25,1.09),(.038,.044,.041))
for i,z in enumerate([.87,1.40]):
    block(back,f'oven_trim_{i}',(.72,.035,.43),(1.77,1.88,z),(.20,.22,.21))
    block(back,f'oven_glass_{i}',(.62,.018,.28),(1.77,1.853,z+.025),(.027,.045,.049))
    block(back,f'oven_handle_{i}',(.57,.035,.024),(1.77,1.823,z+.15),(.40,.43,.42))
    block(back,f'oven_controls_{i}',(.67,.015,.055),(1.77,1.849,z-.16),(.32,.33,.30))
block(back,'right_end_panel',(.38,.77,2.52),(2.40,2.23,1.26),(.040,.047,.043))
scene.include('back_cabinets',back)

# Small red countertop kettle, conspicuous in the reference.
kettle = Asset('Red kettle')
kettle.include('body',ball(radius=.092,center=(-.43,2.12,1.035),color=(.64,.012,.022)))
block(kettle,'black_base',(.17,.14,.025),(-.43,2.12,.944),(.012,.015,.014))
kettle.include('handle',sweep_tube(points=[
    (-.51,2.12,1.06),(-.51,2.12,1.145),(-.47,2.12,1.174),
    (-.40,2.12,1.174),(-.35,2.12,1.13),(-.35,2.12,1.06)],
    radius=.012,color=(.018,.019,.017)))
scene.include('kettle',kettle)

# Foreground timber post is intentionally cropped above frame.
posts = Asset('Structural timber')
block(posts,'foreground_post',(.32,.34,4.5),(-2.10,-1.35,2.25),wood)
block(posts,'rear_right_post',(.17,.21,3.55),(2.95,2.15,1.775),(.44,.30,.17))
scene.include('timber',posts)

# A dark partition and bright glimpse of adjoining space on the right.
partition = Asset('Right room boundary')
block(partition,'dark_partition',(.16,1.25,2.65),(2.86,2.38,1.325),(.055,.061,.056))
block(partition,'upper_gray_fascia',(3.4,.15,.36),(1.45,2.71,2.68),(.33,.36,.34))
block(partition,'distant_light_wall',(.17,2.0,3.3),(3.65,3.0,1.65),(.63,.63,.56))
scene.include('partition',partition)

realize(scene)

# Procedural finishes use no external images.
def mesh_children(parent_name):
    parent = bpy.data.objects.get(parent_name)
    return [] if parent is None else [o for o in parent.children_recursive if o.type == 'MESH']

for ob in mesh_children('timber'):
    for slot in ob.material_slots:
        if slot.material:
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bs = nodes.get('Principled BSDF')
            tex = nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value = 5
            tex.inputs['Detail'].default_value = 3
            coord = nodes.new('ShaderNodeTexCoord')
            mapping = nodes.new('ShaderNodeVectorMath')
            mapping.operation = 'MULTIPLY'
            mapping.inputs[1].default_value = (6,6,.18)
            links.new(coord.outputs['Generated'],mapping.inputs[0])
            links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
            ramp = nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position = .22
            ramp.color_ramp.elements[0].color = (.16,.085,.035,1)
            ramp.color_ramp.elements[1].position = .80
            ramp.color_ramp.elements[1].color = (.51,.34,.19,1)
            links.new(tex.outputs['Fac'],ramp.inputs[0])
            links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
            bs.inputs['Roughness'].default_value = .65

for ob in mesh_children('extractor'):
    for slot in ob.material_slots:
        if slot.material:
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            bs = nodes.get('Principled BSDF')
            noise = nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 105
            noise.inputs['Detail'].default_value = 2
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = .16
            bump.inputs['Distance'].default_value = .018
            links.new(noise.outputs['Fac'],bump.inputs['Height'])
            links.new(bump.outputs['Normal'],bs.inputs['Normal'])
            bs.inputs['Roughness'].default_value = .88

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.32,.35,.36,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .28
set_view(CAMERA,TARGET,lens=LENS,sensor=36,shift=(0,0))
sc.camera.data.clip_end = 100
area_emitter((-3,-3,3.25),power=KEY_POWER,size=4.2,target=(0,.6,.7),color=(1,.94,.84))
area_emitter((2,-.4,3.1),power=650,size=3,target=(0,0,.8),color=(.86,.92,1))
area_emitter((-.5,2.02,1.43),power=65,size=1.5,target=(-.5,2.2,.93),color=(1,.75,.57))
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
# All boxes have positive dimensions; tubes have distinct successive points.
# Geometry remains grouped as separate editable architectural and fixture assets.
