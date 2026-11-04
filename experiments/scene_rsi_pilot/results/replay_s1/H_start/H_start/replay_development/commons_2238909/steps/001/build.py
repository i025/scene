from sceneact import *
import bpy
import math

# Anchors: corridor vanishing point near (0.08, 0.49).
# Right storage cabinets cover (0.20, 0.00) through (1.00, 1.00).
# Foreground cabinet cranks occupy the lower right quarter.
# Ceiling lights recede from (0.38, 0.00) toward (0.08, 0.46).
# A narrow exposed column of books appears around (0.66, 0.50).
# Grey polished floor widens from the distant left to the lower image edge.

scene = Scene('Compact archive corridor')
ivory = (.63, .65, .59)
edge = (.30, .32, .23)
metal = (.29, .32, .29)
black = (.035, .045, .038)
floor_color = (.32, .35, .31)
ceiling_color = (.69, .70, .65)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# Architecture
add(scene, 'concrete_floor', (9, 43, .14), (1.3, 15, -.09), floor_color)
add(scene, 'ceiling', (8, 43, .15), (1.3, 15, 3.24), ceiling_color)
add(scene, 'left_wall', (.16, 43, 3.25), (-1.72, 15, 1.56), (.65, .66, .59))
add(scene, 'end_wall', (8, .15, 3.25), (1.3, 35, 1.56), (.53, .55, .46))
add(scene, 'left_baseboard', (.07, 41, .14), (-1.60, 15, .07), (.30, .32, .26))

# Long exposed ceiling pipes and structural strips.
for i, x in enumerate([-1.52, -1.29, -.93]):
    scene.include('pipe_%d' % i, rod(radius=.035 if i != 1 else .055,
                  start=(x, -5, 3.07), end=(x, 35, 3.07),
                  color=(.54, .56, .49)))
add(scene, 'ceiling_rail', (.11, 41, .11), (.77, 15, 3.10), (.75, .76, .69))

# Repeated mobile shelving banks. Broad blank steel ends face the aisle.
for i in range(25):
    y = -1.70 + i * 1.28
    bank = Asset('Mobile shelving %02d' % i)
    front = .82
    width = 1.22
    if i == 1:
        front = 1.10
        width = .94
    add(bank, 'steel_end', (.085, width, 3.05),
        (front, y, 1.555), ivory)
    add(bank, 'far_body', (3.7, width, 3.02),
        (front + 1.91, y, 1.54), (.55, .57, .49))
    # A narrow olive folded edge distinguishes successive cabinet ends.
    add(bank, 'folded_edge', (.12, .055, 3.07),
        (front - .015, y - width / 2, 1.55), edge)
    add(bank, 'bottom_plinth', (.14, width, .11),
        (front - .012, y, .075), (.22, .25, .20))
    # Vertical center seam and two tiny locking fittings.
    add(bank, 'panel_seam', (.009, .012, 2.97),
        (front - .048, y + .05, 1.55), (.44, .46, .40))
    for j, yy in enumerate([y - .29, y + .32]):
        add(bank, 'lock_plate_%d' % j, (.021, .055, .12),
            (front - .057, yy, 1.04), (.44, .48, .46))
        bank.include('lock_pin_%d' % j,
            rod(radius=.016, start=(front - .085, yy, 1.025),
                end=(front - .085, yy, 1.095), color=(.19, .23, .22)))
    # Handwheel and offset winding handle, mounted on the aisle face.
    cy = y - .08
    bank.include('wheel', rod(radius=.113, length=.065,
                  center=(front - .10, cy, .64), axis='+x', color=black))
    bank.include('wheel_hub', rod(radius=.038, length=.083,
                  center=(front - .145, cy, .64), axis='+x', color=metal))
    bank.include('crank_arm', rod(radius=.020,
                  start=(front - .19, cy, .64),
                  end=(front - .19, cy + .13, .95), color=metal))
    bank.include('crank_grip', rod(radius=.027,
                  start=(front - .20, cy + .13, .95),
                  end=(front - .20, cy + .34, .95), color=black))
    # Framed call-number plaques near the upper edge.
    add(bank, 'label_frame', (.024, .43, .18),
        (front - .062, y + .05, 2.54), (.23, .25, .23))
    add(bank, 'paper_label', (.027, .405, .155),
        (front - .078, y + .05, 2.54), (.78, .79, .74))
    scene.include('bank_%02d' % i, bank)

# Open narrow shelf bay with books visible between the nearest two banks.
bookshelf = Asset('Exposed book bay')
bay_y = -.77
add(bookshelf, 'dark_back', (.16, .34, 3.00), (1.20, bay_y, 1.54), (.10, .12, .08))
for j, z in enumerate([.12, .73, 1.38, 2.06, 2.73, 3.04]):
    add(bookshelf, 'shelf_%d' % j, (.57, .38, .037),
        (.97, bay_y, z), (.25, .28, .20))
book_colors = [(.12,.16,.12), (.30,.12,.055), (.39,.20,.08),
               (.13,.19,.20), (.45,.40,.22), (.16,.18,.13)]
for row, base in enumerate([.15, .76, 1.41, 2.09, 2.76]):
    for j in range(5):
        h = [.47,.53,.43,.56,.49][(j + row) % 5]
        if row == 4:
            h = .22
        yy = bay_y - .14 + j * .064
        add(bookshelf, 'book_%d_%d' % (row,j), (.32,.051,h),
            (.91,yy,base+h/2), book_colors[(j+row)%len(book_colors)])
        if row < 2:
            add(bookshelf, 'spine_label_%d_%d' % (row,j), (.006,.037,.065),
                (.746,yy,base+.12), (.65,.66,.56))
scene.include('book_bay', bookshelf)

# Utility furniture along the left wall.
for i, yy in enumerate([-.3, 2.6, 6.8, 12.0, 18.0]):
    cart = Asset('Aisle cart %d' % i)
    add(cart, 'top', (.47,.77,.06), (-1.35,yy,.77), (.24,.27,.19))
    add(cart, 'lower', (.43,.71,.05), (-1.35,yy,.18), (.28,.30,.24))
    for j, (xx, dy) in enumerate([(-1.54,-.30),(-1.16,-.30),(-1.54,.30),(-1.16,.30)]):
        add(cart, 'leg_%d' % j, (.035,.035,.62), (xx,yy+dy,.45), metal)
    scene.include('cart_%d' % i, cart)
add(scene, 'near_left_bin', (.32,.38,.54), (-1.39,1.62,.28), (.12,.15,.11))
add(scene, 'distant_box', (.39,.48,.43), (-1.30,9.1,.23), (.44,.40,.26))

# Fluorescent luminaires, with opaque housings and luminous undersides.
for i, yy in enumerate([-2.1, 1.65, 5.4, 9.15, 12.9, 16.65, 20.4, 24.15, 27.9, 31.65]):
    fixture = Asset('Fluorescent fixture %d' % i)
    add(fixture, 'housing', (.42,1.65,.17), (-.51,yy,3.055), (.73,.75,.71))
    add(fixture, 'diffuser', (.33,1.54,.025), (-.51,yy,2.958), (.94,.98,1.0))
    add(fixture, 'center_strip', (.028,1.55,.03), (-.51,yy,2.939), (.48,.51,.49))
    scene.include('light_fixture_%d' % i, fixture)

# Hanging exit marker in the far left aisle.
add(scene, 'exit_sign', (.50,.065,.22), (-1.11,8.8,2.53), (.78,.80,.72))

realize(scene)

# Give the paper labels fine printed horizontal marks without adding meshes.
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    if 'diffuser' in obj.name:
        mat = bpy.data.materials.new('Fluorescent white')
        mat.diffuse_color = (.88,.94,1,1)
        mat.use_nodes = True
        bs = mat.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value = (.88,.94,1,1)
        bs.inputs['Emission Color'].default_value = (.88,.94,1,1)
        bs.inputs['Emission Strength'].default_value = 4
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    for mat in obj.data.materials:
        if mat and mat.use_nodes:
            bs = mat.node_tree.nodes.get('Principled BSDF')
            if bs:
                bs.inputs['Roughness'].default_value = .47
                if 'floor' in obj.name:
                    bs.inputs['Roughness'].default_value = .26

# The camera looks diagonally across the aisle, placing its vanishing point left.
CAMERA = (-1.13, -4.35, 1.56)
TARGET = (4.15, 10.3, 1.59)
set_view(CAMERA, TARGET, lens=30, sensor=36)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (.53,.56,.48,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value = .34

for i, yy in enumerate([-2, 2, 6, 10, 15, 21, 28, 33]):
    area_emitter(position=(-.55,yy,2.91), power=160, size=2.0,
                 target=(-.15,yy+.3,0), color=(.90,.96,1.0))
area_emitter(position=(-1.35,-3,2.4), power=100, size=3,
             target=(1.0,1.5,1.3), color=(.93,.96,.85))

sc.render.resolution_x = 512
sc.render.resolution_y = 384
sc.render.resolution_percentage = 100
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.view_settings.view_transform = 'AgX'
