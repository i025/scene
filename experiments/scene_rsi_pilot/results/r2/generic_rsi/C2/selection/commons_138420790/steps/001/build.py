from sceneact import *
import bpy
import math

# OBJECT LEDGER (normalized reference image bounds, approximate):
# floor: (0,.66)-(1,1), large pale gray tiles, supports cabinetry and posts.
# foreground timber post: (.16,0)-(.31,.99), full rectangular wood body;
# occludes left cabinetry, rear counter and the island's far-left corner.
# island: (.33,.55)-(.90,.85), pale thick top, filled left end, three long
# handleless front drawers, recessed dark plinth; supported on floor.
# suspended hood: (.415,.045)-(.73,.44), tall ivory rectangular chimney,
# flat underside with a small metallic edge; hangs from ceiling over island.
# sink/faucet: (.48,.54)-(.73,.62), inset sink and slim chrome gooseneck.
# rear kitchen: (.005,.285)-(.94,.75), black tall cupboard at left,
# dark tiled backsplash, illuminated niche, dark counter and base cabinets.
# oven tower: (.665,.40)-(.79,.59), two black glass/stainless appliances.
# right partition: (.78,.35)-(.97,.67), broad charcoal vertical mass.
# right timber post: (.94,.25)-(.98,.67), behind partition.
# ceiling: (0,0)-(1,.34), black exposed deck, cross beams, pipes.
# ANCHORS: foreground post bottom (.23,.975), island left top (.335,.593),
# island front lower corner (.62,.846), island right top (.897,.572),
# hood bottom left (.416,.426), hood top ridge (.56,.047),
# oven center (.728,.49), rear niche red kettle (.505,.527).
# Perspective: island long edges run up-right; depth edges run up-left.
# Uprights nearly vertical. Camera is in front and left of the island,
# at standing height, with a modest downward tilt and a portrait frame.
# Geometry uses SceneAct only. Unique finish colors isolate shader edits;
# shared world-coordinate references prevent primitive-local texture stretching.

P = {
    'camera': (-3.75, -5.7, 2.48),
    'target': (0.0, .55, 1.79),
    'lens': 43,
    'island_center': (0, -.05),
    'island_length': 2.35,
    'island_depth': 1.08,
    'worktop_height': .96,
    'ceiling': 3.65,
}
C = {
    'floor': (.56,.55,.51),
    'white': (.69,.70,.66),
    'hood': (.78,.77,.69),
    'black': (.033,.038,.036),
    'cabinet': (.055,.060,.057),
    'backsplash': (.047,.053,.050),
    'wood': (.38,.225,.112),
    'metal': (.40,.43,.43),
}

scene = Scene('Kitchen reconstruction')

def block(parent, name, size, center, color):
    return parent.include(name, box(size=size, center=center, color=color))

floor = Asset('tiled_floor')
block(floor, 'floor_slab', (14,14,.12), (0,0,-.065), C['floor'])
scene.include('tiled_floor', floor)

walls = Asset('room_shell')
block(walls, 'rear_wall', (9,.18,3.8), (0,2.60,1.85), (.36,.37,.34))
block(walls, 'left_wall', (.18,8,3.8), (-3.1,1.1,1.85), (.40,.41,.38))
block(walls, 'rear_upper_band', (7,.12,.53), (0,2.40,2.87), (.40,.42,.40))
scene.include('room_shell', walls)

ceiling = Asset('exposed_ceiling')
block(ceiling, 'dark_roof_deck', (10,11,.16), (0,1,3.83), (.025,.031,.030))
for i, x in enumerate([-3.1,-2.25,-1.4,-.55,.30,1.15,2.,2.85,3.7]):
    block(ceiling, 'deck_rib_%02d' % i, (.035,9,.075), (x,1,3.70), (.052,.060,.057))
for i, y in enumerate([-1.4,.80,2.9]):
    block(ceiling, 'major_cross_beam_%02d' % i, (9,.22,.31), (0,y,3.51), (.045,.055,.052))
for i, x in enumerate([-1.9,1.95]):
    block(ceiling, 'longitudinal_beam_%02d' % i, (.19,8,.24), (x,.8,3.52), (.040,.047,.044))
ceiling.include('exposed_conduit', rod(.023, start=(-2.8,2.08,3.40), end=(2.8,2.08,3.40), color=(.16,.18,.17)))
ceiling.include('conduit_drop', rod(.021, start=(1.48,2.08,3.40), end=(1.48,2.08,3.14), color=(.16,.18,.17)))
scene.include('exposed_ceiling', ceiling)

post = Asset('timber_foreground')
block(post, 'solid_timber', (.33,.34,3.92), (-1.83,-1.20,1.94), C['wood'])
scene.include('timber_foreground', post)

post2 = Asset('timber_background')
block(post2, 'upright', (.18,.20,3.45), (2.05,2.11,1.72), C['wood'])
scene.include('timber_background', post2)

island = Asset('kitchen_island')
L, D = P['island_length'], P['island_depth']
cy = P['island_center'][1]
block(island, 'recessed_plinth', (L-.13,D-.13,.12), (0,cy,.075), (.16,.17,.16))
block(island, 'cabinet_body', (L-.04,D-.04,.77), (0,cy,.49), (.55,.57,.54))
block(island, 'left_filled_end', (.075,D,.87), (-L/2+.0375,cy,.505), C['white'])
block(island, 'right_filled_end', (.055,D,.87), (L/2-.0275,cy,.505), C['white'])
front_y = cy-D/2-.012
for i, (bottom, height) in enumerate([(.13,.235),(.376,.235),(.622,.270)]):
    block(island, 'drawer_%d' % i, (L-.14,.037,height),
          (.018,front_y,bottom+height/2), (.66,.68,.65))
    if i < 2:
        block(island, 'shadow_reveal_%d' % i, (L-.15,.025,.013),
              (.018,front_y+.007,bottom+height+.008), (.24,.27,.26))
block(island, 'pale_solid_worktop', (L+.035,D+.035,.055),
      (0,cy,.9325), (.78,.79,.74))
scene.include('kitchen_island', island)

sink = Asset('sink_and_tap')
# The shallow bowl occupies the rear half of the countertop.
sx, sy = .28, .16
block(sink, 'steel_sink_rim', (.59,.41,.009), (sx,sy,.963), (.53,.57,.56))
block(sink, 'sink_dark_inset', (.535,.352,.008), (sx,sy,.969), (.32,.37,.36))
block(sink, 'sink_bottom', (.45,.27,.007), (sx,sy,.971), (.43,.48,.47))
tx, ty = .45,.40
sink.include('tap_foot', rod(.028, length=.025, center=(tx,ty,.977), color=C['metal']))
sink.include('tap_stem', rod(.014, start=(tx,ty,.985), end=(tx,ty,1.105), color=C['metal']))
sink.include('curved_tap', sweep_tube(
    points=[(tx,ty,1.09),(tx,ty,1.145),(tx-.025,ty-.025,1.170),
            (tx-.075,ty-.075,1.170),(tx-.105,ty-.12,1.145),
            (tx-.105,ty-.12,1.11)],
    radius=.013, color=(.57,.62,.61)))
sink.include('tap_control', rod(.008, start=(tx+.025,ty,1.00),
                               end=(tx+.065,ty,1.06), color=C['metal']))
scene.include('sink_and_tap', sink)

hood = Asset('suspended_hood')
block(hood, 'large_ivory_chimney', (.98,.85,1.67), (-.24,.18,2.745), C['hood'])
block(hood, 'bottom_metal_lip', (.985,.855,.016), (-.24,.18,1.909), (.48,.49,.44))
block(hood, 'underside_filter', (.62,.53,.009), (-.24,.18,1.898), (.27,.29,.27))
block(hood, 'small_control', (.052,.012,.012), (-.24,-.251,1.93), (.34,.36,.34))
scene.include('suspended_hood', hood)

left_tower = Asset('left_tall_cupboards')
block(left_tower, 'tall_black_carcass', (.89,.66,2.32), (-2.07,1.97,1.16), C['cabinet'])
for i,(z,h) in enumerate([(.77,1.49),(1.91,.75)]):
    block(left_tower, 'flush_door_%d' % i, (.87,.024,h), (-2.07,1.624,z), (.062,.068,.065))
block(left_tower, 'vertical_door_joint', (.012,.008,2.24), (-2.04,1.607,1.15), (.023,.028,.026))
scene.include('left_tall_cupboards', left_tower)

rear = Asset('rear_counter_and_backsplash')
block(rear, 'black_backsplash', (3.47,.09,1.10), (-.18,2.36,1.52), C['backsplash'])
for i,x in enumerate([-1.42,-.87,-.32,.23,.78,1.33]):
    block(rear, 'vertical_tile_joint_%d' % i, (.007,.006,1.05), (x,2.309,1.52), (.075,.080,.075))
block(rear, 'horizontal_tile_joint', (3.45,.006,.008), (-.18,2.307,1.55), (.075,.080,.075))
block(rear, 'lower_cabinet', (2.91,.65,.87), (-.43,2.03,.47), C['black'])
for i,x in enumerate([-1.42,-.69,.04,.77]):
    block(rear, 'base_front_%d' % i, (.718,.022,.77), (x,1.694,.48), (.047,.052,.049))
block(rear, 'rear_worktop', (3.02,.72,.046), (-.43,2.01,.925), (.18,.19,.175))
block(rear, 'warm_niche_back', (2.80,.018,.31), (-.43,2.292,1.14), (.27,.22,.19))
block(rear, 'upper_dark_cupboard', (3.04,.42,.64), (-.43,2.17,1.87), (.037,.042,.039))
block(rear, 'under_cabinet_strip', (2.83,.03,.014), (-.43,1.956,1.543), (.92,.75,.54))
scene.include('rear_counter_and_backsplash', rear)

kettle = Asset('red_kettle')
kettle.include('rounded_red_body', ball(.087, center=(-.19,1.93,1.04), color=(.65,.009,.022)))
block(kettle, 'black_lower_base', (.13,.115,.025), (-.19,1.93,.974), (.018,.021,.020))
kettle.include('handle', sweep_tube(points=[
    (-.26,1.93,1.05),(-.26,1.93,1.13),(-.20,1.93,1.16),
    (-.14,1.93,1.13),(-.14,1.93,1.07)], radius=.012, color=(.027,.029,.027)))
kettle.include('short_spout', rod(.025, start=(-.125,1.93,1.055),
                               end=(-.085,1.93,1.09), color=(.12,.13,.12)))
scene.include('red_kettle', kettle)

ovens = Asset('oven_tower')
block(ovens, 'dark_tall_housing', (.74,.66,2.27), (1.48,2.0,1.135), (.032,.038,.035))
for i,z in enumerate([1.12,1.64]):
    block(ovens, 'steel_oven_surround_%d' % i, (.64,.026,.46), (1.48,1.653,z), (.29,.31,.30))
    block(ovens, 'black_glass_%d' % i, (.56,.014,.302), (1.48,1.631,z-.025), (.018,.029,.032))
    block(ovens, 'control_band_%d' % i, (.60,.014,.075), (1.48,1.627,z+.168), (.12,.14,.14))
    block(ovens, 'steel_handle_%d' % i, (.50,.035,.021), (1.48,1.599,z+.105), (.50,.53,.52))
    for j,x in enumerate([1.245,1.715]):
        ovens.include('knob_%d_%d' % (i,j), rod(.014, start=(x,1.61,z+.171),
                      end=(x,1.59,z+.171), color=(.42,.44,.43)))
scene.include('oven_tower', ovens)

partition = Asset('right_dark_partition')
block(partition, 'tall_slab', (.53,.64,2.53), (2.11,1.87,1.265), (.047,.053,.049))
block(partition, 'broad_front_panel', (.55,.035,2.15), (2.11,1.528,1.09), (.033,.040,.036))
block(partition, 'upper_gray_fascia', (1.00,.59,.28), (1.88,1.94,2.56), (.30,.33,.31))
scene.include('right_dark_partition', partition)

# Source membership audit: preserve all semantic objects and count actual primitives.
required = ['tiled_floor','room_shell','exposed_ceiling','timber_foreground',
            'timber_background','kitchen_island','sink_and_tap','suspended_hood',
            'left_tall_cupboards','rear_counter_and_backsplash','red_kettle',
            'oven_tower','right_dark_partition']
for name in required:
    assert name in scene.members, name
for name in required:
    node = scene.members[name]
    print(name, sum(n.solid is not None for n in node.traverse()))
print('TOTAL', sum(n.solid is not None for n in scene.traverse()))

realize(scene)
sc = bpy.context.scene

def semantic_meshes(name):
    roots = [o for o in bpy.data.objects if o.type == 'EMPTY' and
             (o.name == name or o.name.startswith(name + '.'))]
    assert roots, 'Missing semantic marker: ' + name
    meshes = set()
    for root in roots:
        meshes.update(o for o in root.children_recursive if o.type == 'MESH')
    assert meshes, 'Empty material target: ' + name
    return roots[0], list(meshes)

def new_material(name, color, roughness=.5, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return mat

def assign(name, mat):
    root, meshes = semantic_meshes(name)
    for ob in meshes:
        ob.data.materials.clear()
        ob.data.materials.append(mat)
    return root, meshes

# Continuous vertical wood grain uses the semantic post as a shared reference.
wood = new_material('Warm weathered oak', (.40,.25,.13), .66)
nt = wood.node_tree
nodes, links = nt.nodes, nt.links
tc = nodes.new('ShaderNodeTexCoord')
wood_root, _ = semantic_meshes('timber_foreground')
tc.object = wood_root
mapping = nodes.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (9,9,.23)
links.new(tc.outputs['Object'], mapping.inputs[0])
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 4.3
noise.inputs['Detail'].default_value = 3
noise.inputs['Roughness'].default_value = .72
links.new(mapping.outputs['Vector'],noise.inputs['Vector'])
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .18
ramp.color_ramp.elements[0].color = (.15,.075,.029,1)
ramp.color_ramp.elements[1].position = .83
ramp.color_ramp.elements[1].color = (.56,.37,.20,1)
links.new(noise.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .20
bump.inputs['Distance'].default_value = .025
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])
assign('timber_foreground',wood)
assign('timber_background',wood)

tile = new_material('Large warm gray porcelain', C['floor'], .46)
root, _ = assign('tiled_floor', tile)
nt = tile.node_tree
tc = nt.nodes.new('ShaderNodeTexCoord')
tc.object = root
brick = nt.nodes.new('ShaderNodeTexBrick')
brick.offset = 0
brick.offset_frequency = 2
brick.inputs['Scale'].default_value = 1
brick.inputs['Brick Width'].default_value = 1.12
brick.inputs['Row Height'].default_value = 1.12
brick.inputs['Mortar Size'].default_value = .002
brick.inputs['Mortar Smooth'].default_value = .002
brick.inputs['Color1'].default_value = (.58,.575,.535,1)
brick.inputs['Color2'].default_value = (.61,.605,.565,1)
brick.inputs['Mortar'].default_value = (.39,.39,.36,1)
nt.links.new(tc.outputs['Object'],brick.inputs['Vector'])
nt.links.new(brick.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])

hoodmat = new_material('Ivory matte hood', C['hood'], .79)
root, meshes = semantic_meshes('suspended_hood')
# Only the tall chimney receives the mineral finish; preserve the underside metal.
for ob in meshes:
    if ob.dimensions.z > 1:
        ob.data.materials.clear()
        ob.data.materials.append(hoodmat)
nt = hoodmat.node_tree
tc = nt.nodes.new('ShaderNodeTexCoord')
tc.object = root
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 70
noise.inputs['Detail'].default_value = 2
nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
bump = nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .12
bump.inputs['Distance'].default_value = .012
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])

# Restrained roughness for the existing shared finishes.
for mat in bpy.data.materials:
    if mat.use_nodes:
        bs = mat.node_tree.nodes.get('Principled BSDF')
        if bs and mat not in (wood,tile,hoodmat):
            bs.inputs['Roughness'].default_value = .43

if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.33,.36,.38,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .28

set_view(P['camera'], P['target'], lens=P['lens'], sensor=36)
area_emitter((-3.5,-3.2,4.0), power=1050, size=4.2,
             target=(0,.2,.7), color=(1.0,.94,.84))
area_emitter((2.7,-.4,3.35), power=450, size=3.0,
             target=(0,.2,1.1), color=(.88,.94,1.0))
area_emitter((-.6,1.86,1.51), power=36, size=1.65,
             target=(-.6,2.24,1.04), color=(1.0,.70,.49))
area_emitter((-2.4,1.2,2.9), power=160, size=1.5,
             target=(-2.5,1.3,1), color=(1.0,.92,.80))
sc.view_settings.view_transform = 'AgX'
