# Reference inventory, normalized image bounds:
# Floor: x 0-.39, y .76-1, pale gray rectangular tiles.
# Slatted timber back wall: x 0-.46, y .11-.76, partly concealed by door.
# White door and frame: x .31-.45, y .29-.77, with handle and keyhole.
# Two small white wall plates left of door.
# Low black cabinet with white front: x 0-.20, y .65-.80, cropped at left.
# Counter: x .36-1, y .59-1, pale veined stone, with near black hob and
# smaller black inset at the back. Its near end is outside the frame.
# Pale glossy backsplash: x .58-1, y .38-.95.
# Dark walnut upper cupboards, extractor and under-cabinet light:
# x .46-1, y 0-.43. Their out-of-frame extent is uncertain.
# Ceiling occupies the top left; wall and cabinet returns meet at the back.
#
# Review of first render: back wall and door were much too small and centered;
# a large blank left wall and too much floor were visible. Move the camera closer
# to the back wall and aim slightly right. The foreground hob must move with the
# camera to remain visible. Darken upper cabinetry and retain the wall details.
# Primitive estimate: approximately 130 SceneAct boxes plus four burner rings.

from sceneact import *
import bpy

scene = Scene('Modern kitchen')

def add(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

floorcol = (.48, .46, .42)
woodbase = (.08, .028, .010)
slatcol = (.33, .12, .038)
darkwood = (.105, .033, .012)
marble = (.76, .74, .68)

architecture = Asset('Architecture')
add(architecture, 'floor', (8, 13, .10), (0, 0, -.06), floorcol)
add(architecture, 'back wall', (8, .12, 3.5), (0, 4.05, 1.75), (.78, .77, .73))
add(architecture, 'right wall', (.12, 13, 3.5), (2.25, -2.4, 1.75), (.83, .82, .78))
add(architecture, 'ceiling', (8, 13, .10), (0, 0, 3.48), (.78, .77, .74))
scene.include('architecture', architecture)

tiles = Asset('Floor tile joints')
for i in range(14):
    add(tiles, 'cross joint %02d' % i, (5.8, .007, .003),
        (-.7, -4.6 + i*.65, .002), (.38, .37, .34))
for i in range(11):
    add(tiles, 'long joint %02d' % i, (.007, 9, .003),
        (-3.4 + i*.53, -.5, .003), (.40, .39, .36))
scene.include('floor joints', tiles)

feature = Asset('Vertical timber feature wall')
add(feature, 'dark backing', (3.65, .055, 2.80), (-1.68, 3.94, 1.40), woodbase)
for i in range(51):
    x = -3.47 + i*.071
    add(feature, 'timber slat %02d' % i, (.043, .05, 2.80),
        (x, 3.895, 1.40), slatcol if i % 4 else (.25, .078, .021))
scene.include('timber wall', feature)

door = Asset('White door')
add(door, 'outer casing', (.92, .075, 2.08), (-.46, 3.82, 1.04), (.84, .84, .81))
add(door, 'door panel', (.78, .025, 1.98), (-.46, 3.768, 1.035), (.89, .89, .86))
add(door, 'left reveal', (.012, .01, 1.96), (-.855, 3.748, 1.04), (.52, .52, .49))
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
add(lowunit, 'black case', (1.30, .40, .60), (-2.83, 3.60, .30), (.018, .019, .018))
add(lowunit, 'white front', (1.17, .025, .34), (-2.83, 3.385, .22), (.85, .85, .82))
add(lowunit, 'top inset', (1.20, .025, .035), (-2.83, 3.37, .48), (.29, .16, .09))
scene.include('low unit', lowunit)

kitchen = Asset('Kitchen counter and cabinetry')
add(kitchen, 'base cabinetry', (1.42, 9.3, .84), (1.52, -.72, .42), (.30, .24, .19))
add(kitchen, 'countertop', (1.48, 9.4, .085), (1.48, -.70, .885), marble)
add(kitchen, 'counter front edge', (.035, 9.4, .095), (.73, -.70, .88), (.69, .67, .61))
add(kitchen, 'back walnut return', (.48, .06, 2.75), (.35, 3.89, 1.55), darkwood)
add(kitchen, 'backsplash', (.025, 9.3, 1.25), (2.175, -.70, 1.54), (.84, .83, .79))
add(kitchen, 'backsplash bottom seam', (.012, 9.3, .012), (2.155, -.70, .95), (.69, .68, .64))
for i, y in enumerate((-.7, 1.4, 3.4)):
    add(kitchen, 'backsplash panel seam %d' % i, (.01, .012, 1.15),
        (2.15, y, 1.55), (.76, .75, .71))
add(kitchen, 'upper cabinet mass', (1.05, 9.3, 1.12), (1.72, -.70, 2.91), darkwood)
add(kitchen, 'upper cabinet front', (.035, 9.3, 1.08), (1.18, -.70, 2.91), (.13, .043, .014))
add(kitchen, 'upper lower trim', (.065, 9.3, .055), (1.16, -.70, 2.34), (.07, .020, .006))
for i, y in enumerate((-3.6, -1.6, .4, 2.4)):
    add(kitchen, 'upper door seam %d' % i, (.012, .018, 1.04),
        (1.155, y, 2.91), (.045, .012, .004))
add(kitchen, 'under cabinet light', (.055, 8.8, .025), (1.18, -.70, 2.295), (1.0, .79, .47))
scene.include('kitchen', kitchen)

hob = Asset('Foreground induction hob')
add(hob, 'black glass', (1.00, 1.38, .018), (1.29, -.65, .939), (.008, .010, .010))
scene.include('hob', hob)

inset = Asset('Far counter inset')
add(inset, 'metal border', (.84, .72, .015), (1.23, 2.63, .938), (.33, .30, .25))
add(inset, 'dark inset', (.75, .63, .018), (1.23, 2.63, .949), (.018, .019, .016))
add(inset, 'inner edge', (.68, .015, .008), (1.23, 2.32, .961), (.36, .34, .29))
scene.include('far inset', inset)

hood = Asset('Extractor hood')
add(hood, 'hood underside', (.88, 1.50, .08), (1.70, .52, 2.30), (.44, .43, .39))
add(hood, 'hood dark vent', (.68, 1.20, .012), (1.66, .52, 2.252), (.17, .17, .15))
for i in range(4):
    add(hood, 'vent slat %d' % i, (.58, .018, .01),
        (1.67, .08 + i*.27, 2.244), (.42, .41, .37))
scene.include('extractor', hood)

realize(scene)

ringmat = bpy.data.materials.new('Subtle burner outline')
ringmat.diffuse_color = (.10, .095, .08, 1)
ringmat.use_nodes = True
ringmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .35
for j, (x, y, r) in enumerate([(1.05, -.35, .23), (1.48, -1.00, .23),
                                (1.51, -.33, .17), (1.05, -.98, .16)]):
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
background.inputs['Strength'].default_value = .38

set_view(position=(-.55, -1.0, 1.68), target=(.38, 3.8, 1.50), lens=24, sensor=36)
area_emitter(position=(-2.5, -1.5, 3.2), power=450, size=5,
             target=(0, 2, 0), color=(1.0, .91, .79))
area_emitter(position=(1.05, 1.5, 2.22), power=150, size=3,
             target=(1.6, 1.5, .8), color=(1.0, .72, .43))
area_emitter(position=(-1, 3, 3.2), power=130, size=3,
             target=(-1, 3, 1), color=(1, .90, .79))
sc.view_settings.view_transform = 'AgX'
