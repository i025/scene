# Reference inventory, approximate normalized image bounds:
# Ceiling occupies x 0-.46, y 0-.12. Pale tiled floor is at x 0-.4,
# y .76-1. A vertical walnut-slat feature wall fills x 0-.46, y .11-.76.
# A white door with frame, lever and keyhole overlaps the slats at
# x .31-.45, y .29-.77; two small white wall plates sit to its left.
# A low black cabinet with a white front is cropped at x 0-.20, y .65-.80.
# A long pale veined countertop extends from x .45, y .59 to the foreground
# at x .36-1, with a black foreground hob and a smaller dark inset at the back.
# A pale backsplash fills the right side behind the counter. Dark walnut upper
# cabinets, a stainless extractor and warm light strip occupy x .46-1, y 0-.43.
# Their continuation outside the frame and the inset's exact function are uncertain.
#
# Review of the second render: the door and slatted wall have roughly the right
# horizontal position, but sit too low; the upper cabinet and counter start too
# far right, and the foreground hob is outside the visible frame. The countertop
# also lacks the reference's veining and the upper cabinetry is too light.
# This revision shifts the view downward, extends the feature wall upward,
# brings the cabinet and counter edges left, and moves the hob into the foreground.
# Estimated expansion: approximately 130 SceneAct boxes and four torus meshes.

from sceneact import *
import bpy

scene = Scene('Modern kitchen')

def add(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

architecture = Asset('Architecture')
add(architecture, 'floor', (8, 13, .10), (0, 0, -.06), (.40, .38, .35))
add(architecture, 'back wall', (8, .12, 3.5), (0, 4.05, 1.75), (.78, .77, .73))
add(architecture, 'right wall', (.12, 13, 3.5), (2.25, -2.4, 1.75), (.83, .82, .78))
add(architecture, 'ceiling', (8, 13, .10), (0, 0, 3.48), (.78, .77, .74))
scene.include('architecture', architecture)

tiles = Asset('Floor tile joints')
for i in range(14):
    add(tiles, 'cross joint %02d' % i, (5.8, .006, .003),
        (-.7, -4.6 + i*.65, .002), (.34, .33, .31))
for i in range(11):
    add(tiles, 'long joint %02d' % i, (.006, 9, .003),
        (-3.4 + i*.53, -.5, .003), (.35, .34, .32))
scene.include('floor joints', tiles)

feature = Asset('Vertical timber feature wall')
add(feature, 'dark backing', (3.65, .055, 3.10), (-1.68, 3.94, 1.55), (.055, .018, .006))
for i in range(51):
    x = -3.47 + i*.071
    add(feature, 'timber slat %02d' % i, (.043, .05, 3.10),
        (x, 3.895, 1.55),
        (.29, .105, .032) if i % 4 else (.22, .067, .018))
scene.include('timber wall', feature)

door = Asset('White door')
add(door, 'outer casing', (.92, .075, 2.08), (-.46, 3.82, 1.04), (.84, .84, .81))
add(door, 'door panel', (.78, .025, 1.98), (-.46, 3.768, 1.035), (.89, .89, .86))
add(door, 'left reveal', (.012, .01, 1.96), (-.855, 3.748, 1.04), (.52, .52, .49))
add(door, 'right reveal', (.010, .01, 1.96), (-.065, 3.748, 1.04), (.60, .60, .57))
add(door, 'top reveal', (.79, .01, .012), (-.46, 3.748, 2.02), (.54, .54, .51))
add(door, 'handle rose', (.035, .025, .05), (-.75, 3.72, .99), (.35, .34, .31))
add(door, 'handle lever', (.13, .025, .018), (-.70, 3.70, 1.01), (.47, .46, .43))
add(door, 'keyhole', (.018, .01, .026), (-.75, 3.70, .91), (.20, .20, .19))
scene.include('door', door)

switches = Asset('Wall switches')
add(switches, 'switch plate', (.10, .02, .09), (-1.09, 3.85, 1.12), (.87, .87, .83))
add(switches, 'low socket', (.075, .02, .075), (-1.04, 3.85, .23), (.87, .87, .83))
scene.include('switches', switches)

lowunit = Asset('Low black and white wall unit')
add(lowunit, 'black case', (1.65, .40, .60), (-2.82, 3.60, .30), (.012, .013, .012))
add(lowunit, 'white front', (1.52, .025, .34), (-2.82, 3.385, .22), (.85, .85, .82))
add(lowunit, 'top inset', (1.53, .025, .035), (-2.82, 3.37, .48), (.29, .16, .09))
scene.include('low unit', lowunit)

kitchen = Asset('Kitchen counter and cabinetry')
add(kitchen, 'base cabinetry', (1.75, 9.3, .84), (1.35, -.72, .42), (.22, .16, .12))
add(kitchen, 'countertop', (1.80, 9.4, .085), (1.32, -.70, .885), (.76, .74, .68))
add(kitchen, 'counter front edge', (.035, 9.4, .095), (.41, -.70, .88), (.69, .67, .61))
add(kitchen, 'back walnut return', (.48, .06, 3.05), (.35, 3.89, 1.70), (.09, .027, .008))
add(kitchen, 'backsplash', (.025, 9.3, 1.25), (2.175, -.70, 1.54), (.84, .83, .79))
add(kitchen, 'backsplash bottom seam', (.012, 9.3, .012), (2.155, -.70, .95), (.69, .68, .64))
for i, y in enumerate((-.7, 1.4, 3.4)):
    add(kitchen, 'backsplash panel seam %d' % i, (.01, .012, 1.15),
        (2.15, y, 1.55), (.76, .75, .71))
add(kitchen, 'upper cabinet mass', (1.45, 9.3, 1.12), (1.52, -.70, 2.91), (.07, .022, .008))
add(kitchen, 'upper cabinet front', (.035, 9.3, 1.08), (.78, -.70, 2.91), (.085, .025, .007))
add(kitchen, 'upper lower trim', (.065, 9.3, .055), (.76, -.70, 2.34), (.045, .012, .004))
for i, y in enumerate((-3.6, -1.6, .4, 2.4)):
    add(kitchen, 'upper door seam %d' % i, (.012, .018, 1.04),
        (.755, y, 2.91), (.025, .007, .002))
add(kitchen, 'under cabinet light', (.055, 8.8, .025), (.81, -.70, 2.295), (1.0, .79, .47))
scene.include('kitchen', kitchen)

hob = Asset('Foreground induction hob')
add(hob, 'black glass', (1.12, 1.55, .018), (1.18, .55, .939), (.006, .007, .006))
scene.include('hob', hob)

inset = Asset('Far counter inset')
add(inset, 'metal border', (.84, .72, .015), (1.23, 2.85, .938), (.33, .30, .25))
add(inset, 'dark inset', (.75, .63, .018), (1.23, 2.85, .949), (.018, .019, .016))
add(inset, 'inner edge', (.68, .015, .008), (1.23, 2.54, .961), (.36, .34, .29))
scene.include('far inset', inset)

hood = Asset('Extractor hood')
add(hood, 'hood underside', (1.15, 1.55, .08), (1.57, .90, 2.30), (.44, .43, .39))
add(hood, 'hood dark vent', (.90, 1.20, .012), (1.56, .90, 2.252), (.17, .17, .15))
for i in range(4):
    add(hood, 'vent slat %d' % i, (.78, .018, .01),
        (1.56, .46 + i*.27, 2.244), (.42, .41, .37))
scene.include('extractor', hood)

realize(scene)

# The countertop is a separate box, given a restrained procedural stone finish.
# Identify it by its dimensions and position, which are unique in this scene.
for obj in bpy.data.objects:
    if (obj.type == 'MESH' and abs(obj.dimensions.x - 1.80) < .02
            and abs(obj.dimensions.y - 9.4) < .02
            and abs(obj.dimensions.z - .085) < .02):
        mat = bpy.data.materials.new('Warm veined stone')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get('Principled BSDF')
        bsdf.inputs['Roughness'].default_value = .26
        coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (3.0, 18.0, 3.0)
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 4.0
        noise.inputs['Detail'].default_value = 3.0
        noise.inputs['Roughness'].default_value = .7
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .39
        ramp.color_ramp.elements[0].color = (.31, .29, .25, 1)
        ramp.color_ramp.elements[1].position = .48
        ramp.color_ramp.elements[1].color = (.79, .77, .71, 1)
        links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        obj.data.materials.clear()
        obj.data.materials.append(mat)

ringmat = bpy.data.materials.new('Subtle burner outline')
ringmat.diffuse_color = (.10, .095, .08, 1)
ringmat.use_nodes = True
ringmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .35
for j, (x, y, r) in enumerate([
        (.91, .90, .23), (1.40, .18, .23),
        (1.42, .90, .17), (.91, .18, .16)]):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=48, minor_segments=4,
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
background.inputs['Strength'].default_value = .32

set_view(position=(-.55, -1.0, 1.68), target=(.38, 3.8, 1.25), lens=24, sensor=36)
area_emitter(position=(-2.5, -1.5, 3.2), power=350, size=5,
             target=(0, 2, 0), color=(1.0, .91, .79))
area_emitter(position=(1.05, 1.5, 2.22), power=140, size=3,
             target=(1.6, 1.5, .8), color=(1.0, .72, .43))
area_emitter(position=(-1, 3, 3.2), power=110, size=3,
             target=(-1, 3, 1), color=(1, .90, .79))
sc.view_settings.view_transform = 'AgX'
