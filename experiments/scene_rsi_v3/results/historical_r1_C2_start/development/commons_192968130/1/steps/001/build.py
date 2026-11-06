# Reference inventory, approximate normalized image bounds:
# - Pale tiled floor: lower left, x 0-.39, y .76-1; partly hidden by counter.
# - Back wall with dark vertical timber slats: x 0-.46, y .11-.76;
#   interrupted by a white door at x .31-.45, y .30-.77.
# - White door, frame, lever handle and small wall switches.
# - Low black-and-white cabinet or heater: x 0-.20, y .65-.80, cropped at left.
# - Long pale marble kitchen countertop: x .36-1, y .59-1, receding to back;
#   black glass hob in foreground and a smaller dark inset near the back.
# - Pale backsplash and right wall above the worktop: x .58-1, y .38-.95.
# - Dark walnut overhead cupboards and range hood: x .46-1, y 0-.43;
#   illuminated strip beneath. Parts beyond image boundaries are uncertain.
# Expanded primitive estimate: about 125 boxes and rods, including 51 slats,
# 25 floor seams, 8 hob details and all architectural and cabinet pieces.

from sceneact import *
import bpy
import math

scene = Scene('Modern kitchen')

def add_box(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

white = (0.82, 0.82, 0.79)
wallwhite = (0.78, 0.77, 0.73)
floorcol = (0.48, 0.46, 0.42)
woodbase = (0.13, 0.050, 0.019)
slatcol = (0.36, 0.145, 0.052)
darkwood = (0.16, 0.060, 0.025)
black = (0.012, 0.013, 0.012)
metal = (0.42, 0.42, 0.39)
marble = (0.76, 0.74, 0.68)

architecture = Asset('Architecture')
add_box(architecture, 'floor', (8, 13, .10), (0, 0, -.06), floorcol)
add_box(architecture, 'back_wall', (8, .12, 3.5), (0, 4.05, 1.75), wallwhite)
add_box(architecture, 'right_wall', (.12, 13, 3.5), (2.25, -2.4, 1.75), (0.83, 0.82, 0.78))
add_box(architecture, 'ceiling', (8, 13, .10), (0, 0, 3.48), (0.78, 0.77, 0.74))
scene.include('architecture', architecture)

# Fine, subdued floor tile joints.
tiles = Asset('Floor tile joints')
for i in range(14):
    y = -4.6 + i * .65
    add_box(tiles, 'cross_joint_%02d' % i, (5.8, .009, .003), (-.7, y, .002), (.37, .36, .33))
for i in range(11):
    x = -3.4 + i * .53
    add_box(tiles, 'long_joint_%02d' % i, (.008, 9, .003), (x, -.5, .003), (.39, .38, .35))
scene.include('floor_joints', tiles)

# Timber feature wall. Slats stand slightly proud of a near-black backing.
feature = Asset('Vertical timber feature wall')
add_box(feature, 'dark backing', (3.65, .055, 2.80), (-1.68, 3.94, 1.40), woodbase)
for i in range(51):
    x = -3.47 + i * .071
    add_box(feature, 'timber slat %02d' % i, (.043, .05, 2.80),
            (x, 3.895, 1.40), slatcol if i % 4 else (.29, .105, .034))
scene.include('timber_wall', feature)

door = Asset('White door')
# Mounted in front of slatted wall; the visible white panel occludes the slats.
add_box(door, 'outer white casing', (.92, .075, 2.08), (-.46, 3.82, 1.04), (.84, .84, .81))
add_box(door, 'door panel', (.78, .025, 1.98), (-.46, 3.768, 1.035), (.89, .89, .86))
# Narrow line along the inside of the frame.
add_box(door, 'left reveal', (.012, .01, 1.96), (-.855, 3.748, 1.04), (.52, .52, .49))
add_box(door, 'top reveal', (.79, .01, .012), (-.46, 3.748, 2.02), (.54, .54, .51))
add_box(door, 'handle rose', (.035, .025, .05), (-.75, 3.72, .99), (.35, .34, .31))
add_box(door, 'handle lever', (.13, .025, .018), (-.70, 3.70, 1.01), (.47, .46, .43))
add_box(door, 'keyhole', (.018, .01, .026), (-.75, 3.70, .91), (.20, .20, .19))
scene.include('door', door)

switches = Asset('Wall switches')
add_box(switches, 'switch plate', (.10, .02, .09), (-1.09, 3.85, 1.12), (.87, .87, .83))
add_box(switches, 'low socket', (.075, .02, .075), (-1.04, 3.85, .23), (.87, .87, .83))
scene.include('switches', switches)

lowunit = Asset('Low black and white wall unit')
add_box(lowunit, 'black case', (1.30, .40, .60), (-2.83, 3.60, .30), (.018, .019, .018))
add_box(lowunit, 'white front', (1.17, .025, .34), (-2.83, 3.385, .22), (.85, .85, .82))
add_box(lowunit, 'top inset', (1.20, .025, .035), (-2.83, 3.37, .48), (.29, .16, .09))
scene.include('low_unit', lowunit)

kitchen = Asset('Kitchen counter and cabinetry')
# Counter runs along the right wall, from the camera foreground to the back wall.
add_box(kitchen, 'base cabinetry', (1.42, 9.3, .84), (1.52, -.72, .42), (.30, .24, .19))
add_box(kitchen, 'countertop', (1.48, 9.4, .085), (1.48, -.70, .885), marble)
add_box(kitchen, 'counter front edge', (.035, 9.4, .095), (.73, -.70, .88), (.69, .67, .61))
# Back end vertical walnut return.
add_box(kitchen, 'back walnut return', (.48, .06, 2.75), (.35, 3.89, 1.55), darkwood)
# Pale backsplash along right wall.
add_box(kitchen, 'backsplash', (.025, 9.3, 1.25), (2.175, -.70, 1.54), (.84, .83, .79))
# Horizontal and vertical joints in backsplash.
add_box(kitchen, 'backsplash bottom seam', (.012, 9.3, .012), (2.155, -.70, .95), (.69, .68, .64))
for i, y in enumerate((-.7, 1.4, 3.4)):
    add_box(kitchen, 'backsplash panel seam %d' % i, (.01, .012, 1.15),
            (2.15, y, 1.55), (.76, .75, .71))
# Upper cupboards project out over counter.
add_box(kitchen, 'upper cabinet mass', (1.05, 9.3, 1.12), (1.72, -.70, 2.91), darkwood)
add_box(kitchen, 'upper cabinet front', (.035, 9.3, 1.08), (1.18, -.70, 2.91), (.21, .085, .035))
add_box(kitchen, 'upper lower trim', (.065, 9.3, .055), (1.16, -.70, 2.34), (.12, .045, .018))
for i, y in enumerate((-3.6, -1.6, .4, 2.4)):
    add_box(kitchen, 'upper door seam %d' % i, (.012, .018, 1.04),
            (1.155, y, 2.91), (.075, .029, .012))
# Long under-cabinet warm light strip.
add_box(kitchen, 'under cabinet light', (.055, 8.8, .025), (1.18, -.70, 2.295), (1.0, .79, .47))
scene.include('kitchen', kitchen)

# Foreground black induction glass and its restrained burner markings.
hob = Asset('Foreground induction hob')
add_box(hob, 'black glass', (1.00, 1.38, .018), (1.29, -2.35, .939), (.008, .010, .010))
# Thin concentric burner arcs are represented by flattened dark metallic rings.
scene.include('hob', hob)

# Far black rectangular inset and its metal rim, visible near the back.
inset = Asset('Far counter inset')
add_box(inset, 'metal border', (.84, .72, .015), (1.23, 2.63, .938), (.33, .30, .25))
add_box(inset, 'dark inset', (.75, .63, .018), (1.23, 2.63, .949), (.018, .019, .016))
add_box(inset, 'inner edge', (.68, .015, .008), (1.23, 2.32, .961), (.36, .34, .29))
scene.include('far_inset', inset)

# Slim stainless extractor, beneath the upper cabinets.
hood = Asset('Extractor hood')
add_box(hood, 'hood underside', (.88, 1.50, .08), (1.70, .52, 2.30), (.44, .43, .39))
add_box(hood, 'hood dark vent', (.68, 1.20, .012), (1.66, .52, 2.252), (.17, .17, .15))
for i in range(4):
    add_box(hood, 'vent slat %d' % i, (.58, .018, .01),
            (1.67, .08 + i*.27, 2.244), (.42, .41, .37))
scene.include('extractor', hood)

realize(scene)

# Materials for the large worktop: low-contrast procedural stone.
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'countertop' in obj.name.lower():
        mat = bpy.data.materials.new('Warm veined pale stone')
        mat.diffuse_color = (.76, .74, .68, 1)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get('Principled BSDF')
        bsdf.inputs['Roughness'].default_value = .28
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 5.0
        tex.inputs['Detail'].default_value = 3.0
        tex.inputs['Roughness'].default_value = .7
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (2.0, 13.0, 3.0)
        coord = nodes.new('ShaderNodeTexCoord')
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .30
        ramp.color_ramp.elements[0].color = (.42, .40, .36, 1)
        ramp.color_ramp.elements[1].position = .57
        ramp.color_ramp.elements[1].color = (.82, .80, .74, 1)
        links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
        links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        obj.data.materials.clear()
        obj.data.materials.append(mat)

# Induction rings: editable shallow curves on the glass.
ringmat = bpy.data.materials.new('Subtle burner outline')
ringmat.diffuse_color = (.12, .115, .105, 1)
ringmat.use_nodes = True
ringmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .35
for j, (x, y, r) in enumerate([(1.05, -2.05, .23), (1.48, -2.70, .23),
                                (1.51, -2.03, .17), (1.05, -2.68, .16)]):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=4,
        location=(x, y, .954), major_radius=r, minor_radius=.003)
    ring = bpy.context.object
    ring.name = 'Induction burner ring %d' % j
    ring.data.materials.append(ringmat)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.66, .68, .70, 1)
background.inputs['Strength'].default_value = .45

set_view(position=(-.55, -5.8, 1.68), target=(.15, 3.8, 1.50), lens=24, sensor=36)
area_emitter(position=(-2.5, -1.5, 3.2), power=600, size=5,
             target=(0, 2, 0), color=(1.0, .91, .79))
area_emitter(position=(1.05, 1.5, 2.22), power=180, size=3,
             target=(1.6, 1.5, .8), color=(1.0, .72, .43))
area_emitter(position=(-1, 3, 3.2), power=180, size=3,
             target=(-1, 3, 1), color=(1, .90, .79))
sc.view_settings.view_transform = 'AgX'
