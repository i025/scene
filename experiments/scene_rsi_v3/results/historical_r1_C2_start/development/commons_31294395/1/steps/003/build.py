from sceneact import *
import bpy

# Reference inventory, approximate normalized image bounds:
# Patterned bedroom walls, back/right corner around x=.57; white ceiling
# molding and beige carpet. Two tall windows at x=0-.13 and .23-.43, with
# dark green shades, bright lower panes, and white trim.
# Gold oval portrait between windows; two small pale framed pictures on wall.
# Dark furniture under windows, small white-clothed table; blue and ochre
# folding screen at x=.41-.62, y=.33-.62, partly hidden.
# Large dark wooden bed at x=.43-.98, y=.45-1, with white bedding, two
# pillows, high footboard in foreground, headboard at right.
# Olive armchair at x=.28-.54, y=.51-1, overlapping footboard; small dark
# spindle chair behind bed. Small rugs on floor and a dark bedside cabinet.
# Screen artwork and hidden furniture surfaces are uncertain.
#
# Render comparison: the previous view shows too much floor and ceiling;
# the bed and windows are too small and the corner is too far right. The
# chair is too round and faces the camera too directly. This revision moves
# closer, shifts the corner left in the frame, enlarges the bed, and turns
# the chair to show its side. Expanded primitive estimate: architecture 8,
# windows 16, pictures 10, furniture 17, screen 16, bed 17, armchair 15,
# small chair 11, rugs 10: approximately 120 meshes, no Boolean operations.

scene = Scene('Bedroom')
wall = (.30, .19, .135)
trim = (.90, .89, .84)
wood = (.13, .054, .028)
dark = (.055, .022, .014)
gold = (.65, .44, .15)
olive = (.25, .27, .055)

def bx(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def ell(parent, name, center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    parent.include(name, obj)

room = Asset('Architecture')
bx(room, 'carpet', (12, 12, .12), (0, 0, -.08), (.48, .46, .42))
bx(room, 'back_wall', (12, .12, 3.45), (-1.4, 3.2, 1.72), wall)
bx(room, 'right_wall', (.12, 12, 3.45), (3.55, -2.7, 1.72), wall)
bx(room, 'back_baseboard', (12, .08, .14), (-1.4, 3.10, .09), (.19, .12, .08))
bx(room, 'right_baseboard', (.08, 12, .14), (3.46, -2.7, .09), (.19, .12, .08))
bx(room, 'back_cornice', (12, .18, .16), (-1.4, 3.07, 3.35), trim)
bx(room, 'right_cornice', (.18, 12, .16), (3.43, -2.7, 3.35), trim)
bx(room, 'ceiling', (12, 12, .10), (-1.4, -2.7, 3.48), (.84, .85, .82))
scene.include('architecture', room)

windows = Asset('Windows')
for label, x in [('left', -2.88), ('middle', -1.12)]:
    width = 1.18
    bx(windows, label+'_recess', (width, .055, 2.48), (x, 3.105, 1.93), (.91, .92, .88))
    bx(windows, label+'_glass', (width-.17, .035, 2.27), (x, 3.065, 1.93), (.34, .53, .48))
    bx(windows, label+'_shade', (width-.22, .03, 1.55), (x, 3.035, 2.27), (.17, .36, .30))
    bx(windows, label+'_lower_light', (width-.22, .025, .57), (x, 3.015, 1.24), (.94, .99, .97))
    for j, dx in enumerate((-width/2+.055, width/2-.055)):
        bx(windows, label+'_side_'+str(j), (.11, .12, 2.53), (x+dx, 2.99, 1.93), trim)
    bx(windows, label+'_top', (width+.08, .12, .12), (x, 2.99, 3.17), trim)
    bx(windows, label+'_sill', (width+.13, .20, .10), (x, 2.97, .71), trim)
scene.include('windows', windows)

pictures = Asset('Wall_Pictures')
ell(pictures, 'oval_gold_frame', (-2.03, 3.025, 2.40), (.37, .055, .48), gold)
ell(pictures, 'oval_dark_inset', (-2.03, 2.96, 2.40), (.29, .035, .39), (.045, .025, .018))
ell(pictures, 'portrait_face', (-2.03, 2.918, 2.48), (.052, .018, .075), (.56, .36, .23))
ell(pictures, 'portrait_clothing', (-2.03, 2.915, 2.34), (.12, .02, .11), (.12, .09, .08))
for label, x, z, width, height in [
    ('large', .03, 2.67, .39, .53),
    ('small', 1.65, 2.60, .27, .46)
]:
    bx(pictures, label+'_frame', (width, .06, height), (x, 3.015, z), (.68, .58, .35))
    bx(pictures, label+'_mat', (width-.055, .025, height-.055), (x, 2.973, z), (.90, .89, .82))
    ell(pictures, label+'_portrait', (x, 2.951, z), (width*.24, .012, height*.31), (.50, .49, .46))
scene.include('pictures', pictures)

furniture = Asset('Back_Wall_Furniture')
bx(furniture, 'left_cabinet_body', (1.05, .42, .55), (-3.04, 2.75, .48), wood)
bx(furniture, 'left_cabinet_top', (1.13, .48, .08), (-3.04, 2.74, .79), dark)
for i, x in enumerate((-3.47, -2.61)):
    for j, y in enumerate((2.60, 2.89)):
        bx(furniture, 'cabinet_leg_%d_%d'%(i,j), (.07, .07, .28), (x, y, .17), dark)
bx(furniture, 'table_top', (.73, .53, .07), (-1.94, 2.65, .77), wood)
for i, x in enumerate((-2.25, -1.63)):
    for j, y in enumerate((2.44, 2.84)):
        bx(furniture, 'table_leg_%d_%d'%(i,j), (.045, .045, .73), (x, y, .38), dark)
bx(furniture, 'tablecloth_top', (.80, .59, .035), (-1.94, 2.64, .82), (.90, .90, .84))
cloth = box(size=(.52, .035, .52), center=(-1.94, 2.34, .61), color=(.88, .88, .82))
cloth.turn(axis='+y', degrees=45)
furniture.include('hanging_tablecloth', cloth)
ell(furniture, 'table_bowl', (-1.91, 2.62, .87), (.18, .12, .045), (.72, .73, .65))
bx(furniture, 'middle_chest', (1.02, .42, .52), (-1.02, 2.78, .42), dark)
bx(furniture, 'middle_chest_top', (1.10, .48, .07), (-1.02, 2.75, .71), wood)
scene.include('back_furniture', furniture)

screen = Asset('Folding_Screen')
bx(screen, 'left_panel', (.70, .065, 1.57), (.18, 2.55, 1.16), (.55, .37, .15))
bx(screen, 'right_panel', (.70, .065, 1.57), (.90, 2.55, 1.16), (.018, .075, .48))
for i, x in enumerate((-.17, .53, 1.25)):
    bx(screen, 'upright_'+str(i), (.035, .09, 1.61), (x, 2.50, 1.16), dark)
for i, z in enumerate((.37, 1.95)):
    bx(screen, 'edge_'+str(i), (1.46, .09, .035), (.54, 2.50, z), dark)
ell(screen, 'blue_cloud', (.17, 2.49, 1.48), (.37, .018, .20), (.025, .12, .52))
ell(screen, 'blue_cloud_lower', (.44, 2.48, 1.18), (.27, .016, .15), (.025, .12, .52))
ell(screen, 'gold_figure', (.98, 2.48, 1.52), (.18, .018, .24), (.75, .48, .19))
ell(screen, 'ochre_hill', (.73, 2.48, .73), (.34, .018, .19), (.62, .34, .16))
ell(screen, 'flower_one', (.12, 2.47, 1.06), (.18, .016, .11), (.77, .61, .42))
ell(screen, 'flower_two', (.50, 2.47, .79), (.15, .016, .10), (.76, .56, .36))
ell(screen, 'flower_center', (.12, 2.45, 1.06), (.045, .01, .035), (.31, .27, .21))
scene.include('folding_screen', screen)

bed = Asset('Bed')
bx(bed, 'base', (2.85, 1.85, .31), (1.85, .32, .38), dark)
bx(bed, 'mattress', (2.70, 1.74, .29), (1.84, .32, .62), (.84, .83, .78))
bx(bed, 'white_cover', (1.90, 1.76, .13), (1.49, .31, .82), (.86, .85, .80))
bx(bed, 'headboard', (.14, 1.96, .90), (3.28, .32, .79), dark)
bx(bed, 'headboard_top', (.20, 2.02, .10), (3.28, .32, 1.27), wood)
bx(bed, 'footboard', (.14, 1.94, 1.02), (.39, .32, .69), dark)
bx(bed, 'footboard_top', (.20, 2.02, .09), (.39, .32, 1.22), wood)
for i, y in enumerate((-.60, 1.24)):
    bx(bed, 'foot_post_'+str(i), (.15, .15, 1.16), (.39, y, .66), dark)
    bx(bed, 'head_post_'+str(i), (.15, .15, 1.20), (3.28, y, .69), dark)
    bx(bed, 'side_rail_'+str(i), (2.88, .08, .26), (1.83, y, .35), dark)
for i, y in enumerate((-.13, .76)):
    ell(bed, 'pillow_'+str(i), (2.67, y, 1.00), (.47, .43, .22), (.91, .90, .85))
bed.turn(axis='+z', degrees=18, pivot=(1.85, .32, 0))
bed.move((-.10, -.30, 0))
scene.include('bed', bed)

armchair = Asset('Olive_Armchair')
ell(armchair, 'upholstered_back', (-.72, -.48, .92), (.66, .20, .72), olive)
ell(armchair, 'seat_cushion', (-.72, -.88, .57), (.57, .50, .16), (.34, .35, .09))
ell(armchair, 'left_arm', (-1.28, -.87, .73), (.16, .52, .32), (.29, .31, .075))
ell(armchair, 'right_arm', (-.16, -.87, .73), (.16, .52, .34), (.23, .25, .055))
bx(armchair, 'chair_base', (1.10, .85, .30), (-.72, -.88, .35), (.25, .26, .06))
for i, x in enumerate((-1.15, -.28)):
    for j, y in enumerate((-1.20, -.55)):
        bx(armchair, 'leg_%d_%d'%(i,j), (.07, .07, .33), (x, y, .17), dark)
for i, x in enumerate((-1.00, -.72, -.44)):
    for j, z in enumerate((.88, 1.14)):
        ell(armchair, 'button_%d_%d'%(i,j), (x, -.69, z), (.025, .012, .025), (.19, .20, .045))
armchair.turn(axis='+z', degrees=-65, pivot=(-.72, -.75, 0))
armchair.move((-.38, -.40, 0))
scene.include('armchair', armchair)

chair = Asset('Small_Wood_Chair')
bx(chair, 'seat', (.46, .42, .07), (1.55, 2.12, .53), dark)
for i, x in enumerate((1.36, 1.74)):
    for j, y in enumerate((1.95, 2.28)):
        bx(chair, 'leg_%d_%d'%(i,j), (.045, .045, .53), (x, y, .27), dark)
for i, x in enumerate((1.36, 1.74)):
    bx(chair, 'back_post_'+str(i), (.045, .045, .72), (x, 2.28, .85), dark)
bx(chair, 'back_top', (.46, .05, .07), (1.55, 2.28, 1.19), dark)
for i, x in enumerate((1.47, 1.55, 1.63)):
    bx(chair, 'back_spindle_'+str(i), (.025, .035, .52), (x, 2.28, .89), dark)
scene.include('small_chair', chair)

nightstand = Asset('Right_Bedside_Table')
bx(nightstand, 'body', (.54, .57, .60), (3.28, -1.03, .31), dark)
bx(nightstand, 'top', (.61, .64, .07), (3.28, -1.03, .64), wood)
scene.include('nightstand', nightstand)

rugs = Asset('Rugs')
for name, center, size in [
    ('window_rug', (-1.45, 1.75, .012), (1.15, .65, .025)),
    ('foreground_rug', (1.20, -2.10, .015), (2.05, .78, .03))
]:
    x, y, z = center
    sx, sy, sz = size
    bx(rugs, name+'_base', size, center, (.43, .20, .16))
    bx(rugs, name+'_inner', (sx-.10, sy-.10, .012), (x, y, z+.02), (.22, .27, .35))
    bx(rugs, name+'_field', (sx-.20, sy-.20, .012), (x, y, z+.03), (.53, .28, .20))
    for i, yy in enumerate((y-sy/2+.08, y+sy/2-.08)):
        bx(rugs, name+'_border_'+str(i), (sx-.12, .035, .014), (x, yy, z+.04), (.77, .68, .52))
scene.include('rugs', rugs)

realize(scene)

wallmat = bpy.data.materials.new('Fine patterned brown wallpaper')
wallmat.diffuse_color = (.30, .19, .135, 1)
wallmat.use_nodes = True
nodes = wallmat.node_tree.nodes
links = wallmat.node_tree.links
bsdf = nodes.get('Principled BSDF')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 210
noise.inputs['Detail'].default_value = 2
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .28
ramp.color_ramp.elements[0].color = (.07, .035, .025, 1)
ramp.color_ramp.elements[1].position = .72
ramp.color_ramp.elements[1].color = (.43, .25, .15, 1)
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
background.inputs['Strength'].default_value = .32

set_view((-3.5, -5.5, 2.70), (.25, 1.0, 1.53), lens=36)
area_emitter((-2.5, 1.5, 3.0), power=600, size=3.0, target=(.2, .5, .5))
area_emitter((1, -3.5, 4.2), power=260, size=4.0, target=(.6, 1, .8))
