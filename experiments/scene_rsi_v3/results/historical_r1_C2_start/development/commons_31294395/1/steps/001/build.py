from sceneact import *
import bpy
import math

# Reference inventory, estimated normalized image bounds:
# Room: carpeted floor across lower image, patterned back and right walls,
# white ceiling cornice; back/right corner near x=.57. The camera-facing wall
# and much of the ceiling are outside the image.
# Two tall back-wall windows: left partly cropped (0-.13, .07-.60), center
# (.23-.43, .08-.59), white trim, green shades and bright lower panes.
# Wall pictures: oval gold portrait (.13-.25, .17-.36), two small framed
# portraits (.47-.54, .12-.28 and .66-.71, .16-.29).
# Low dark cabinets and a small white-covered table beneath the left windows.
# Decorative blue and ochre folding screen (.41-.62, .33-.62), partially
# occluded by chair and bed. Exact painting details are uncertain.
# Bed (.43-.98, .45-.98): dark wood headboard and footboard, white mattress,
# cover and two pillows; headboard at right, footboard toward foreground.
# Olive upholstered armchair (.28-.54, .51-1): curved high back, arms,
# seat, dark legs; overlaps bed footboard.
# Small wooden chair near back wall (.64-.70, .46-.65), partly hidden.
# Narrow patterned rugs near the windows and at the foot of the bed.
# Approximate expanded mesh count: architecture 23, windows 22, pictures 12,
# cabinets and table 22, screen 21, bed 23, armchair 15, chair 12, rugs 10:
# around 160 primitive meshes, with no Boolean operations.

scene = Scene('Bedroom')
wall = (0.32, 0.22, 0.17)
trim = (0.90, 0.90, 0.84)
darkwood = (0.115, 0.045, 0.028)
wood = (0.19, 0.085, 0.045)
ivory = (0.83, 0.82, 0.75)
gold = (0.66, 0.47, 0.17)
olive = (0.30, 0.32, 0.095)

def addbox(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def ellipsoid(parent, name, center, scale, color):
    shape = ball(1, center=center, color=color)
    shape.resize(scale, pivot=center)
    parent.include(name, shape)

room = Asset('Architecture')
addbox(room, 'carpet_floor', (7.2, 8.0, .12), (0, .1, -.08), (.49, .47, .43))
addbox(room, 'back_wall', (7.2, .12, 3.45), (0, 3.2, 1.72), wall)
addbox(room, 'right_wall', (.12, 8, 3.45), (3.55, -.75, 1.72), wall)
addbox(room, 'back_baseboard', (7.1, .08, .16), (0, 3.10, .10), (.20, .13, .09))
addbox(room, 'right_baseboard', (.08, 7.9, .16), (3.46, -.75, .10), (.20, .13, .09))
addbox(room, 'back_cornice', (7.15, .19, .16), (0, 3.07, 3.34), trim)
addbox(room, 'right_cornice', (.19, 7.8, .16), (3.43, -.75, 3.34), trim)
addbox(room, 'ceiling', (7.2, 8, .10), (0, -.75, 3.48), (.83, .84, .81))
scene.include('architecture', room)

# White surrounds stand in front of the wallpaper; shades obscure most glazing.
windows = Asset('Windows')
for label, x, width in [('left', -2.88, 1.18), ('middle', -1.12, 1.18)]:
    addbox(windows, label+'_recess', (width, .055, 2.48), (x, 3.105, 1.93), (.91, .92, .88))
    addbox(windows, label+'_glass', (width-.17, .035, 2.27), (x, 3.065, 1.93), (.33, .52, .48))
    addbox(windows, label+'_shade', (width-.22, .03, 1.55), (x, 3.035, 2.27), (.27, .48, .43))
    addbox(windows, label+'_lower_light', (width-.22, .025, .57), (x, 3.015, 1.24), (.87, .95, .91))
    for dx in (-width/2+.055, width/2-.055):
        addbox(windows, label+'_side_trim_'+str(dx), (.11, .12, 2.53), (x+dx, 2.99, 1.93), trim)
    addbox(windows, label+'_top_trim', (width+.08, .12, .12), (x, 2.99, 3.17), trim)
    addbox(windows, label+'_sill', (width+.13, .20, .10), (x, 2.97, .71), trim)
scene.include('windows', windows)

pictures = Asset('Wall_Pictures')
# Flattened overlapping ovals provide a gold frame and dark portrait opening.
ellipsoid(pictures, 'oval_gold_frame', (-2.03, 3.025, 2.40), (.37, .055, .48), gold)
ellipsoid(pictures, 'oval_dark_inset', (-2.03, 2.96, 2.40), (.29, .035, .39), (.055, .035, .026))
ellipsoid(pictures, 'portrait_face', (-2.03, 2.918, 2.48), (.052, .018, .075), (.56, .36, .23))
ellipsoid(pictures, 'portrait_clothing', (-2.03, 2.915, 2.34), (.12, .02, .11), (.13, .10, .09))
for label, x, z in [('large', .03, 2.67), ('small', 1.65, 2.60)]:
    width = .39 if label == 'large' else .27
    height = .53 if label == 'large' else .46
    addbox(pictures, label+'_frame', (width, .06, height), (x, 3.015, z), (.68, .58, .35))
    addbox(pictures, label+'_mat', (width-.055, .025, height-.055), (x, 2.973, z), (.90, .89, .82))
    ellipsoid(pictures, label+'_portrait', (x, 2.951, z), (width*.24, .012, height*.31), (.50, .49, .46))
scene.include('pictures', pictures)

furniture = Asset('Back_Wall_Furniture')
# Low dark case beneath cropped window.
addbox(furniture, 'left_cabinet_body', (1.05, .42, .55), (-3.04, 2.75, .48), wood)
addbox(furniture, 'left_cabinet_top', (1.13, .48, .08), (-3.04, 2.74, .79), darkwood)
for x in (-3.47, -2.61):
    for y in (2.60, 2.89):
        addbox(furniture, 'cabinet_leg_'+str(x)+'_'+str(y), (.07, .07, .28), (x, y, .17), darkwood)
# Small table with white draped cloth.
addbox(furniture, 'table_top', (.73, .53, .07), (-1.94, 2.65, .77), wood)
for x in (-2.25, -1.63):
    for y in (2.44, 2.84):
        addbox(furniture, 'table_leg_'+str(x)+'_'+str(y), (.045, .045, .73), (x, y, .38), darkwood)
addbox(furniture, 'white_tablecloth', (.80, .59, .035), (-1.94, 2.64, .82), (.90, .90, .84))
# A triangular drape is represented by a rotated thin square.
cloth = box(size=(.52, .035, .52), center=(-1.94, 2.34, .61), color=(.88, .88, .82))
cloth.turn(axis='+y', degrees=45)
furniture.include('hanging_tablecloth', cloth)
ellipsoid(furniture, 'table_bowl', (-1.91, 2.62, .87), (.18, .12, .045), (.72, .73, .65))
addbox(furniture, 'middle_chest', (1.02, .42, .52), (-1.02, 2.78, .42), darkwood)
addbox(furniture, 'middle_chest_top', (1.10, .48, .07), (-1.02, 2.75, .71), wood)
scene.include('back_furniture', furniture)

screen = Asset('Folding_Screen')
addbox(screen, 'left_panel', (.70, .065, 1.57), (.18, 2.55, 1.16), (.55, .37, .15))
addbox(screen, 'right_panel', (.70, .065, 1.57), (.90, 2.55, 1.16), (.035, .13, .54))
for x in (-.17, .53, 1.25):
    addbox(screen, 'frame_'+str(x), (.035, .09, 1.61), (x, 2.50, 1.16), darkwood)
for z in (.37, 1.95):
    addbox(screen, 'edge_'+str(z), (1.46, .09, .035), (.54, 2.50, z), darkwood)
# Broad, irregularly placed colored shapes suggest the painted decoration.
ellipsoid(screen, 'blue_cloud', (.17, 2.49, 1.48), (.37, .018, .20), (.045, .17, .55))
ellipsoid(screen, 'gold_figure', (.98, 2.48, 1.52), (.18, .018, .24), (.75, .48, .19))
ellipsoid(screen, 'ochre_hill', (.73, 2.48, .73), (.34, .018, .19), (.62, .34, .16))
ellipsoid(screen, 'flower_one', (.12, 2.47, 1.06), (.18, .016, .11), (.77, .61, .42))
ellipsoid(screen, 'flower_two', (.50, 2.47, .79), (.15, .016, .10), (.76, .56, .36))
ellipsoid(screen, 'flower_center', (.12, 2.45, 1.06), (.045, .01, .035), (.31, .27, .21))
scene.include('folding_screen', screen)

bed = Asset('Bed')
# Long axis along X, with head at the right wall.
addbox(bed, 'base', (2.75, 1.63, .28), (1.85, .45, .38), darkwood)
addbox(bed, 'mattress', (2.58, 1.51, .29), (1.84, .45, .62), (.84, .83, .78))
addbox(bed, 'white_cover', (1.80, 1.53, .13), (1.50, .44, .82), (.86, .85, .80))
# Headboard and footboard.
addbox(bed, 'headboard', (.14, 1.78, .90), (3.23, .45, .79), darkwood)
addbox(bed, 'headboard_top', (.20, 1.84, .10), (3.23, .45, 1.27), (.15, .07, .045))
addbox(bed, 'footboard', (.13, 1.76, .94), (.43, .45, .65), darkwood)
addbox(bed, 'footboard_top', (.20, 1.84, .09), (.43, .45, 1.15), (.16, .07, .045))
for y in (-.38, 1.28):
    addbox(bed, 'foot_post_'+str(y), (.15, .15, 1.08), (.43, y, .62), darkwood)
    addbox(bed, 'head_post_'+str(y), (.15, .15, 1.20), (3.23, y, .69), darkwood)
    addbox(bed, 'side_rail_'+str(y), (2.78, .08, .26), (1.83, y, .35), darkwood)
# Pillows are soft, slightly raised ellipsoids.
for i, y in enumerate((.02, .80)):
    ellipsoid(bed, 'pillow_'+str(i), (2.65, y, 1.00), (.48, .38, .22), (.91, .90, .85))
scene.include('bed', bed)

armchair = Asset('Olive_Armchair')
# Broad back, seat and raised curved arms, viewed from behind and the side.
ellipsoid(armchair, 'upholstered_back', (-.72, -.55, .87), (.68, .22, .78), olive)
ellipsoid(armchair, 'seat_cushion', (-.72, -.89, .54), (.61, .52, .19), (.37, .38, .12))
ellipsoid(armchair, 'left_arm', (-1.29, -.88, .72), (.19, .53, .36), (.31, .33, .095))
ellipsoid(armchair, 'right_arm', (-.16, -.88, .72), (.19, .53, .36), (.29, .30, .085))
addbox(armchair, 'chair_base', (1.10, .85, .25), (-.72, -.88, .35), (.27, .27, .075))
for x in (-1.15, -.28):
    for y in (-1.20, -.55):
        addbox(armchair, 'leg_'+str(x)+'_'+str(y), (.07, .07, .33), (x, y, .17), darkwood)
# Sparse upholstery buttons.
for x in (-1.00, -.72, -.44):
    for z in (.82, 1.09):
        ellipsoid(armchair, 'button_'+str(x)+'_'+str(z), (x, -.785, z), (.025, .012, .025), (.20, .21, .06))
scene.include('armchair', armchair)

chair = Asset('Small_Wood_Chair')
addbox(chair, 'seat', (.46, .42, .07), (1.55, 2.12, .53), darkwood)
for x in (1.36, 1.74):
    for y in (1.95, 2.28):
        addbox(chair, 'leg_'+str(x)+'_'+str(y), (.045, .045, .53), (x, y, .27), darkwood)
for x in (1.36, 1.74):
    addbox(chair, 'back_post_'+str(x), (.045, .045, .72), (x, 2.28, .85), darkwood)
addbox(chair, 'back_top', (.46, .05, .07), (1.55, 2.28, 1.19), darkwood)
for x in (1.47, 1.55, 1.63):
    addbox(chair, 'back_spindle_'+str(x), (.025, .035, .52), (x, 2.28, .89), darkwood)
scene.include('small_chair', chair)

rugs = Asset('Rugs')
for name, center, size in [
    ('window_rug', (-1.45, 1.75, .012), (1.15, .65, .025)),
    ('foreground_rug', (1.20, -1.95, .015), (2.05, .78, .03))
]:
    x, y, z = center
    sx, sy, sz = size
    addbox(rugs, name+'_base', size, center, (.43, .20, .16))
    addbox(rugs, name+'_inner', (sx-.10, sy-.10, .012), (x, y, z+.02), (.22, .27, .35))
    addbox(rugs, name+'_field', (sx-.20, sy-.20, .012), (x, y, z+.03), (.53, .28, .20))
    for yy in (y-sy/2+.08, y+sy/2-.08):
        addbox(rugs, name+'_border_'+str(yy), (sx-.12, .035, .014), (x, yy, z+.04), (.77, .68, .52))
scene.include('rugs', rugs)

realize(scene)

# Apply a shared fine mottled wallpaper to the two large wall meshes.
wallmat = bpy.data.materials.new('Fine patterned brown wallpaper')
wallmat.diffuse_color = (0.32, 0.22, 0.17, 1)
wallmat.use_nodes = True
nodes = wallmat.node_tree.nodes
links = wallmat.node_tree.links
bsdf = nodes.get('Principled BSDF')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 210
noise.inputs['Detail'].default_value = 2
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .28
ramp.color_ramp.elements[0].color = (.12, .08, .055, 1)
ramp.color_ramp.elements[1].position = .72
ramp.color_ramp.elements[1].color = (.48, .34, .24, 1)
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and obj.data.materials:
        for idx, mat in enumerate(obj.data.materials):
            if mat and all(abs(mat.diffuse_color[i] - wall[i]) < .015 for i in range(3)):
                obj.data.materials[idx] = wallmat

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
background.inputs['Color'].default_value = (.75, .78, .80, 1)
background.inputs['Strength'].default_value = .45

set_view((-.45, -7.7, 3.05), (.15, 1.05, 1.45), lens=32)
area_emitter((-2.5, 1.5, 3.0), power=650, size=3.0, target=(.2, .5, .5))
area_emitter((1, -3.5, 4.2), power=450, size=4.0, target=(.6, 1, .8))
