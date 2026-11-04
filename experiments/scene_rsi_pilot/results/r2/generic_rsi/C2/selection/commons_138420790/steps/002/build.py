from sceneact import *
import bpy

# REVISION LEDGER
# Camera residual: step 1 shows too little of the island's left end; the hood
# and ceiling sit low, while the foreground post covers the island end.
# Highest priority: correct the camera azimuth and the resulting occlusion order.
# Coupled geometry corrections: move the foreground post left in the new view,
# give the island a deeper, shorter footprint, and move the nearest ceiling beam
# behind the foreground post. Preserve the complete island, hood and rear kitchen.
# Appearance residual: charcoal surfaces read gray; retain floor illumination,
# darken the cabinet palette, and reduce the cool fill.
#
# Reference object ledger, normalized image bounds:
# floor (0,.66)-(1,1): broad pale tiles supporting all floor-standing objects.
# foreground oak post (.16,0)-(.31,.99): filled rectangular timber, foremost.
# island (.33,.55)-(.90,.85): thick top, broad left end, three drawers, plinth.
# hood (.415,.045)-(.73,.44): filled suspended chimney and metal underside.
# sink/tap (.48,.54)-(.73,.62): shallow inset and small curved chrome tap.
# rear kitchen (.005,.285)-(.94,.75): left tower, backsplash, illuminated niche,
# countertop, lower cupboards; behind island and foreground post.
# ovens (.665,.40)-(.79,.59): paired black glass appliances and steel handles.
# right partition (.78,.35)-(.97,.67): charcoal body and broad upper fascia.
# background timber (.94,.25)-(.98,.67): upright behind partition.
# exposed ceiling (0,0)-(1,.34): deck, joists, beams and conduit.
# kettle (.48,.51)-(.525,.55): red rounded body and dark handle on rear counter.
#
# Anchors to preserve / approach:
# post bottom (.23,.975); island back-left (.335,.593);
# island front-left (.62,.846); island right top (.897,.572);
# hood lower-left (.416,.426); hood top ridge (.56,.047);
# oven center (.728,.49); kettle center (.505,.527).
# Step-1 residuals: hood top ~(.50,.17), too low; hood bottom ~(.50,.49),
# too low; island end largely hidden; post right edge ~.36, too far right.
# Perspective hypothesis: upright architecture, long island edges up-right,
# depth edges up-left, camera at standing height looking from front-left.

P = {
    'camera': (-5.5, -3.8, 2.48),
    'target': (0.0, .55, 1.72),
    'lens': 47,
    'island_length': 1.95,
    'island_depth': 1.35,
    'island_x': .13,
    'island_y': -.05,
    'post': (-2.50, -.05),
    'key_power': 950,
    'fill_power': 240,
}
C = {
    'floor': (.56, .55, .51),
    'white': (.65, .67, .64),
    'hood': (.78, .77, .69),
    'black': (.014, .018, .017),
    'cabinet': (.022, .027, .025),
    'backsplash': (.021, .027, .024),
    'wood': (.38, .225, .112),
    'metal': (.40, .43, .43),
}

scene = Scene('Kitchen reconstruction')

def block(parent, name, size, center, color):
    return parent.include(name, box(size=size, center=center, color=color))

floor = Asset('tiled_floor')
block(floor, 'floor_slab', (14,14,.12), (0,0,-.065), C['floor'])
scene.include('tiled_floor', floor)

walls = Asset('room_shell')
block(walls, 'rear_wall', (11,.18,3.8), (0,2.60,1.85), (.30,.32,.30))
block(walls, 'left_wall', (.18,9,3.8), (-5.1,1.1,1.85), (.37,.39,.36))
block(walls, 'rear_upper_band', (8,.12,.53), (0,2.40,2.87), (.34,.37,.35))
scene.include('room_shell', walls)

ceiling = Asset('exposed_ceiling')
block(ceiling, 'dark_roof_deck', (12,11,.16), (0,1,3.83), (.018,.024,.023))
for i,x in enumerate([-4,-3.1,-2.25,-1.4,-.55,.30,1.15,2.,2.85,3.7]):
    block(ceiling, 'deck_rib_%02d' % i, (.035,9,.075),
          (x,1,3.70), (.037,.046,.042))
for i,y in enumerate([.60,2.9]):
    block(ceiling, 'major_cross_beam_%02d' % i, (11,.24,.31),
          (0,y,3.51), (.031,.042,.038))
for i,x in enumerate([-1.9,1.95]):
    block(ceiling, 'longitudinal_beam_%02d' % i, (.22,8,.27),
          (x,.8,3.52), (.029,.037,.034))
ceiling.include('exposed_conduit', rod(.023, start=(-2.8,2.08,3.40),
    end=(2.8,2.08,3.40), color=(.13,.15,.14)))
ceiling.include('conduit_drop', rod(.021, start=(1.48,2.08,3.40),
    end=(1.48,2.08,3.14), color=(.13,.15,.14)))
scene.include('exposed_ceiling', ceiling)

post = Asset('timber_foreground')
block(post, 'solid_timber', (.33,.34,4.4),
      (*P['post'],2.19), C['wood'])
scene.include('timber_foreground', post)

post2 = Asset('timber_background')
block(post2, 'upright', (.18,.20,3.45), (2.05,2.11,1.72), C['wood'])
scene.include('timber_background', post2)

island = Asset('kitchen_island')
L,D = P['island_length'],P['island_depth']
cx,cy = P['island_x'],P['island_y']
block(island, 'recessed_plinth', (L-.13,D-.13,.12),
      (cx,cy,.075), (.11,.13,.12))
block(island, 'cabinet_body', (L-.04,D-.04,.77),
      (cx,cy,.49), (.50,.53,.50))
block(island, 'left_filled_end', (.075,D,.87),
      (cx-L/2+.0375,cy,.505), C['white'])
block(island, 'right_filled_end', (.055,D,.87),
      (cx+L/2-.0275,cy,.505), C['white'])
front_y = cy-D/2-.012
for i,(bottom,height) in enumerate([(.13,.235),(.376,.235),(.622,.270)]):
    block(island, 'drawer_%d' % i, (L-.14,.037,height),
          (cx+.018,front_y,bottom+height/2), (.65,.67,.64))
    if i < 2:
        block(island, 'shadow_reveal_%d' % i, (L-.15,.025,.013),
              (cx+.018,front_y+.007,bottom+height+.008), (.20,.23,.21))
block(island, 'pale_solid_worktop', (L+.035,D+.035,.055),
      (cx,cy,.9325), (.78,.79,.74))
scene.include('kitchen_island', island)

sink = Asset('sink_and_tap')
sx,sy = cx+.22,.18
block(sink, 'steel_sink_rim', (.59,.41,.009), (sx,sy,.963), (.53,.57,.56))
block(sink, 'sink_dark_inset', (.535,.352,.008), (sx,sy,.969), (.30,.35,.34))
block(sink, 'sink_bottom', (.45,.27,.007), (sx,sy,.974), (.43,.48,.47))
tx,ty = cx+.39,.43
sink.include('tap_foot', rod(.028, length=.025,
    center=(tx,ty,.977), color=C['metal']))
sink.include('tap_stem', rod(.014, start=(tx,ty,.985),
    end=(tx,ty,1.105), color=C['metal']))
sink.include('curved_tap', sweep_tube(points=[
    (tx,ty,1.09),(tx,ty,1.145),(tx-.025,ty-.025,1.170),
    (tx-.075,ty-.075,1.170),(tx-.105,ty-.12,1.145),
    (tx-.105,ty-.12,1.11)], radius=.013, color=(.57,.62,.61)))
sink.include('tap_control', rod(.008, start=(tx+.025,ty,1.00),
    end=(tx+.065,ty,1.06), color=C['metal']))
scene.include('sink_and_tap', sink)

hood = Asset('suspended_hood')
block(hood, 'large_ivory_chimney', (.98,.85,1.67),
      (-.24,.18,2.745), C['hood'])
block(hood, 'bottom_metal_lip', (.985,.855,.016),
      (-.24,.18,1.909), (.48,.49,.44))
block(hood, 'underside_filter', (.62,.53,.009),
      (-.24,.18,1.898), (.24,.27,.24))
block(hood, 'small_control', (.052,.012,.012),
      (-.24,-.251,1.93), (.34,.36,.34))
scene.include('suspended_hood', hood)

left_tower = Asset('left_tall_cupboards')
block(left_tower, 'tall_black_carcass', (.89,.66,2.32),
      (-2.07,1.97,1.16), C['cabinet'])
for i,(z,h) in enumerate([(.77,1.49),(1.91,.75)]):
    block(left_tower, 'flush_door_%d' % i, (.87,.024,h),
          (-2.07,1.624,z), (.027,.032,.029))
block(left_tower, 'vertical_door_joint', (.012,.008,2.24),
      (-2.04,1.607,1.15), (.009,.013,.011))
scene.include('left_tall_cupboards', left_tower)

rear = Asset('rear_counter_and_backsplash')
block(rear, 'black_backsplash', (3.47,.09,1.10),
      (-.18,2.36,1.52), C['backsplash'])
for i,x in enumerate([-1.42,-.87,-.32,.23,.78,1.33]):
    block(rear, 'vertical_tile_joint_%d' % i, (.005,.006,1.05),
          (x,2.309,1.52), (.039,.045,.039))
block(rear, 'horizontal_tile_joint', (3.45,.006,.006),
      (-.18,2.307,1.55), (.039,.045,.039))
block(rear, 'lower_cabinet', (2.91,.65,.87),
      (-.43,2.03,.47), C['black'])
for i,x in enumerate([-1.42,-.69,.04,.77]):
    block(rear, 'base_front_%d' % i, (.718,.022,.77),
          (x,1.694,.48), (.022,.028,.024))
block(rear, 'rear_worktop', (3.02,.72,.046),
      (-.43,2.01,.925), (.13,.15,.13))
block(rear, 'warm_niche_back', (2.80,.018,.31),
      (-.43,2.292,1.14), (.27,.22,.19))
block(rear, 'upper_dark_cupboard', (3.04,.42,.64),
      (-.43,2.17,1.87), (.018,.024,.020))
block(rear, 'under_cabinet_strip', (2.83,.03,.014),
      (-.43,1.956,1.543), (.92,.75,.54))
scene.include('rear_counter_and_backsplash', rear)

kettle = Asset('red_kettle')
kettle.include('rounded_red_body', ball(.087,
    center=(-.19,1.93,1.04), color=(.65,.009,.022)))
block(kettle, 'black_lower_base', (.13,.115,.025),
      (-.19,1.93,.974), (.012,.016,.014))
kettle.include('handle', sweep_tube(points=[
    (-.26,1.93,1.05),(-.26,1.93,1.13),(-.20,1.93,1.16),
    (-.14,1.93,1.13),(-.14,1.93,1.07)],
    radius=.012, color=(.017,.021,.018)))
kettle.include('short_spout', rod(.025, start=(-.125,1.93,1.055),
    end=(-.085,1.93,1.09), color=(.09,.11,.09)))
scene.include('red_kettle', kettle)

ovens = Asset('oven_tower')
block(ovens, 'dark_tall_housing', (.74,.66,2.27),
      (1.48,2.0,1.135), (.014,.021,.017))
for i,z in enumerate([1.12,1.64]):
    block(ovens, 'steel_oven_surround_%d' % i, (.64,.026,.46),
          (1.48,1.653,z), (.25,.28,.27))
    block(ovens, 'black_glass_%d' % i, (.56,.014,.302),
          (1.48,1.631,z-.025), (.008,.017,.020))
    block(ovens, 'control_band_%d' % i, (.60,.014,.075),
          (1.48,1.627,z+.168), (.08,.10,.10))
    block(ovens, 'steel_handle_%d' % i, (.50,.035,.021),
          (1.48,1.599,z+.105), (.50,.53,.52))
    for j,x in enumerate([1.245,1.715]):
        ovens.include('knob_%d_%d' % (i,j),
            rod(.014, start=(x,1.61,z+.171),
                end=(x,1.59,z+.171), color=(.42,.44,.43)))
scene.include('oven_tower', ovens)

partition = Asset('right_dark_partition')
block(partition, 'tall_slab', (.53,.64,2.53),
      (2.11,1.87,1.265), (.020,.027,.023))
block(partition, 'broad_front_panel', (.55,.035,2.15),
      (2.11,1.528,1.09), (.014,.022,.017))
block(partition, 'upper_gray_fascia', (1.00,.59,.28),
      (1.88,1.94,2.56), (.22,.26,.23))
scene.include('right_dark_partition', partition)

# Audit complete semantic groups, including every attached fixture and support.
required = [
    'tiled_floor','room_shell','exposed_ceiling','timber_foreground',
    'timber_background','kitchen_island','sink_and_tap','suspended_hood',
    'left_tall_cupboards','rear_counter_and_backsplash','red_kettle',
    'oven_tower','right_dark_partition']
for name in required:
    assert name in scene.members, name
    count = sum(n.solid is not None for n in scene.members[name].traverse())
    assert count > 0
    print(name, count)
print('TOTAL', sum(n.solid is not None for n in scene.traverse()))

realize(scene)
sc = bpy.context.scene

def semantic_meshes(name):
    roots = [o for o in bpy.data.objects if o.type == 'EMPTY'
             and (o.name == name or o.name.startswith(name+'.'))]
    assert roots, 'Missing semantic marker: '+name
    meshes = set()
    for root in roots:
        meshes.update(o for o in root.children_recursive if o.type == 'MESH')
    assert meshes, 'Empty material target: '+name
    return roots[0], list(meshes)

def material(name, color, roughness=.5, metallic=0):
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

wood = material('Weathered oak', (.40,.25,.13), .66)
nt = wood.node_tree
nodes,links = nt.nodes,nt.links
tc = nodes.new('ShaderNodeTexCoord')
tc.object = semantic_meshes('timber_foreground')[0]
mapping = nodes.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (9,9,.23)
links.new(tc.outputs['Object'],mapping.inputs[0])
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
bump.inputs['Strength'].default_value = .15
bump.inputs['Distance'].default_value = .018
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])
assign('timber_foreground',wood)
assign('timber_background',wood)

tile = material('Large warm gray porcelain', C['floor'], .46)
root,_ = assign('tiled_floor',tile)
nt = tile.node_tree
tc = nt.nodes.new('ShaderNodeTexCoord')
tc.object = root
brick = nt.nodes.new('ShaderNodeTexBrick')
brick.offset = 0
brick.inputs['Scale'].default_value = 1
brick.inputs['Brick Width'].default_value = 1.12
brick.inputs['Row Height'].default_value = 1.12
brick.inputs['Mortar Size'].default_value = .002
brick.inputs['Mortar Smooth'].default_value = .002
brick.inputs['Color1'].default_value = (.58,.575,.535,1)
brick.inputs['Color2'].default_value = (.61,.605,.565,1)
brick.inputs['Mortar'].default_value = (.39,.39,.36,1)
nt.links.new(tc.outputs['Object'],brick.inputs['Vector'])
nt.links.new(brick.outputs['Color'],
             nt.nodes.get('Principled BSDF').inputs['Base Color'])

hoodmat = material('Ivory mineral hood', C['hood'], .79)
root,meshes = semantic_meshes('suspended_hood')
matched = 0
for ob in meshes:
    if ob.dimensions.z > 1:
        ob.data.materials.clear()
        ob.data.materials.append(hoodmat)
        matched += 1
assert matched == 1
nt = hoodmat.node_tree
tc = nt.nodes.new('ShaderNodeTexCoord')
tc.object = root
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 70
noise.inputs['Detail'].default_value = 2
nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
bump = nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .08
bump.inputs['Distance'].default_value = .008
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'],
             nt.nodes.get('Principled BSDF').inputs['Normal'])

for mat in bpy.data.materials:
    if mat.use_nodes and mat not in (wood,tile,hoodmat):
        bs = mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Roughness'].default_value = .43

if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.33,.36,.38,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .22

set_view(P['camera'],P['target'],lens=P['lens'],sensor=36)
area_emitter((-3.5,-3.2,4.0),power=P['key_power'],size=4.2,
             target=(0,.2,.7),color=(1.0,.94,.84))
area_emitter((2.7,-.4,3.35),power=P['fill_power'],size=3.0,
             target=(0,.2,1.1),color=(.88,.94,1.0))
area_emitter((-.6,1.86,1.51),power=36,size=1.65,
             target=(-.6,2.24,1.04),color=(1.0,.70,.49))
area_emitter((-2.4,1.2,2.9),power=130,size=1.5,
             target=(-2.5,1.3,1),color=(1.0,.92,.80))
sc.view_settings.view_transform = 'AgX'
