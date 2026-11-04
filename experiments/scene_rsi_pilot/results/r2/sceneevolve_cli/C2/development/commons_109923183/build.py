# Chaise bounds improved from step 1, but step 2 remains about (.14,.22)-(.77,.83) versus reference (.04,.24)-(.83,.93); lens 68 and a slightly higher target enlarge it downward.
# Wall base still descends toward the right near y=.72 versus reference y=.50; rotate the room moldings upward to the right and move the wall farther behind the chaise.
# Head and pillow remain too narrow, and the revised wing developed seams; turn the head surfaces toward the viewer and restore one continuous rounded wing per side.
from sceneact import *
import bpy
import random

scene = Scene('Louis XV chaise room')
LENGTH = 2.35
WIDTH = .91
SEAT_Z = .63
CAMERA = (1.30, -5.60, 4.20)
TARGET = (.13, 0, 1.02)
LENS = 68
WALL_ROTATION = 26
WALL_OFFSET = 1.05
HEAD_ROTATION = -25

ivory = (.72, .68, .57)
fabric = (.80, .75, .64)
sage = (.32, .38, .32)
trim = (.63, .61, .49)
wood = (.115, .052, .031)
wall = (.73, .71, .64)

scene.include('floor', box((10, 9, .10), center=(0, 0, -.07), color=wood))
room = Asset('Paneled room')
room.include('rear_wall', box((8, .14, 3.7), center=(0, 1.12, 1.8), color=wall))
room.include('right_return', box((.15, 1.8, 3.7), center=(2.40, 1.95, 1.8), color=wall))
for z, depth, height in [(.08,.09,.15), (.19,.055,.045), (.30,.045,.025),
                          (1.97,.055,.045), (2.12,.075,.055), (2.43,.045,.03)]:
    room.include('horizontal_' + str(z),
                 box((7.8, depth, height), center=(0, 1.015, z), color=ivory))
for x in [-2.6, -.9, 1.85, 2.18]:
    room.include('panel_vertical_' + str(x),
                 box((.035,.035,1.55), center=(x,1.017,1.12), color=ivory))
for z in [.40, 1.84]:
    room.include('panel_border_' + str(z),
                 box((4.35,.035,.035), center=(-.36,1.012,z), color=ivory))
for x in [-2.52, 1.77]:
    room.include('inner_border_' + str(x),
                 box((.022,.024,1.35), center=(x,.991,1.12), color=(.77,.75,.68)))
for z in [.46, 1.78]:
    room.include('inner_horizontal_' + str(z),
                 box((4.28,.024,.022), center=(-.375,.991,z), color=(.77,.75,.68)))
for x in [-1.69, .34]:
    room.include('cabinet_seam_' + str(x),
                 box((.009,.009,2.5), center=(x,1.032,1.35), color=(.37,.35,.29)))
for x, z in [(-1.46,2.03), (-1.32,2.04)]:
    room.include('cabinet_handle_' + str(x),
                 rod(.014, start=(x,.98,z-.025), end=(x,.955,z+.026), color=(.16,.15,.12)))
room.turn('z', WALL_ROTATION, pivot=(0,1.12,0))
room.move((0,WALL_OFFSET,0))
scene.include('room', room)

parquet = Asset('Parquet floor')
random.seed(9)
for row in range(12):
    for col in range(11):
        x = -4 + col*.69 + (row % 2)*.34
        y = -3.5 + row*.33
        c = random.uniform(.86,1.12)
        tile = box((.688,.328,.012), center=(x,y,-.011),
                   color=(.135*c,.067*c,.041*c))
        tile.turn('z', -34, pivot=(0,0,0))
        parquet.include('board_%d_%d' % (row,col), tile)
scene.include('parquet', parquet)

chaise = Asset('Antique upholstered chaise')
frame = Asset('Carved painted wooden frame')
upholstery = Asset('Cream woven upholstery')
head = Asset('Curved upholstered head')
upholstery.include('seat', fillet_box((2.24,.88,.23), radius=.112,
                                     center=(.03,0,SEAT_Z), color=fabric))
frame.include('under_seat', box((2.17,.83,.12), center=(.01,0,.465), color=sage))
for y in [-.444,.444]:
    frame.include('long_rail_' + str(y),
        sweep_tube(points=[(-1.10,y,.52),(-.65,y,.49),(.25,y,.47),
                           (.94,y,.45),(1.14,y,.40)], radius=.033, color=sage))
    frame.include('rail_highlight_' + str(y),
        sweep_tube(points=[(-1.09,y-.008,.545),(-.55,y-.008,.52),
                           (.30,y-.008,.50),(1.02,y-.008,.47)], radius=.009, color=trim))
for x in [-.91,1.02]:
    for y in [-.36,.36]:
        sign = 1 if x > 0 else -1
        pts = [(x,y,.49),(x+.025*sign,y,.36),
               (x-.04*sign,y+.025,.15),(x+.025*sign,y+.02,.065)]
        frame.include('leg_%s_%s' % (x,y), sweep_tube(points=pts, radius=.034, color=sage))
        frame.include('leg_trim_%s_%s' % (x,y),
            sweep_tube(points=[(p[0],p[1]-.029,p[2]) for p in pts], radius=.009, color=trim))
        frame.include('foot_%s_%s' % (x,y), ball(.043, center=pts[-1], color=trim))

back = fillet_box((.15,.88,.77), radius=.065, center=(-1.075,.015,1.055), color=fabric)
back.turn('y', -13)
head.include('high_back', back)
head.include('rounded_back_crown',
    resized(ball(.5, center=(-1.16,.015,1.39), color=fabric), (.18,.83,.24)))
for y in [-.46,.46]:
    head.include('head_post_' + str(y),
        sweep_tube(points=[(-.99,y,.48),(-1.12,y,.80),(-1.22,y,1.22),
                           (-1.22,y,1.46),(-1.11,y,1.51)], radius=.028, color=sage))
head.include('crown',
    sweep_tube(points=[(-1.16,-.46,1.45),(-1.19,-.32,1.53),
                       (-1.20,-.05,1.56),(-1.19,.25,1.52),(-1.14,.46,1.43)],
               radius=.034, color=sage))
head.include('crown_inlay',
    sweep_tube(points=[(-1.13,-.44,1.46),(-1.16,-.28,1.51),
                       (-1.17,.02,1.53),(-1.15,.29,1.49),(-1.11,.43,1.42)],
               radius=.009, color=trim))
head.turn('z', HEAD_ROTATION, pivot=(-1.075,0,1.0))
chaise.include('head', head)

for y in [-.445,.445]:
    panel = fillet_box((.49,.082,.48), radius=.039,
                       center=(-.92,y,.83), color=fabric)
    panel.turn('y', -13)
    upholstery.include('continuous_wing_' + str(y), panel)
    frame.include('arm_' + str(y),
        sweep_tube(points=[(-1.23,y,1.31),(-1.09,y,1.17),(-.88,y,1.04),
                           (-.65,y,.99),(-.60,y,.91),(-.61,y,.58)],
                   radius=.029, color=sage))
    frame.include('arm_inlay_' + str(y),
        sweep_tube(points=[(-1.22,y-.023,1.32),(-1.07,y-.023,1.19),
                           (-.86,y-.023,1.06),(-.64,y-.023,1.01)],
                   radius=.009, color=trim))
    frame.include('wing_base_' + str(y),
        sweep_tube(points=[(-1.13,y,.58),(-.99,y,.49),(-.77,y,.47),(-.61,y,.54)],
                   radius=.025, color=sage))
for x, z, s in [(-.10,.44,.065),(-.19,.46,.038),(.00,.45,.038),(.97,.43,.028)]:
    frame.include('carving_' + str(x),
        resized(ball(1, center=(x,-.463,z), color=trim), (s,.019,s*.66)))
for i in range(5):
    frame.include('medallion_bead_' + str(i),
        ball(.012, center=(-.16+i*.026,-.485,.42+abs(i-2)*.01), color=ivory))

pillow = fillet_box((.23,.64,.59), radius=.10,
                    center=(-.80,-.025,1.12), color=(.86,.79,.65))
pillow.turn('y', -20)
pillow.turn('x', -9)
pillow.turn('z', -35)
upholstery.include('loose_pillow', pillow)
chaise.include('frame', frame)
chaise.include('upholstery', upholstery)
label = box((.095,.17,.006), center=(.63,.16,.753), color=(.025,.20,.17))
label.turn('z', -6)
chaise.include('museum_label', label)
for i in range(3):
    chaise.include('label_print_' + str(i),
        box((.045,.004,.001), center=(.63,.12+i*.015,.757), color=(.63,.75,.66)))
scene.include('chaise', chaise)

chair = Asset('Foreground cane chair')
chair.include('seat_rim', fillet_box((.67,.66,.08), radius=.035,
                                    center=(-1.65,-1.27,.40), color=sage))
chair.include('cane_surface', box((.58,.57,.013),
                                 center=(-1.65,-1.27,.448), color=(.48,.33,.19)))
for i in range(17):
    x = -1.92+i*.033
    chair.include('cane_x_' + str(i),
        rod(.004, start=(x,-1.53,.46), end=(x,-1.01,.46), color=(.65,.49,.29)))
for i in range(17):
    y = -1.53+i*.032
    chair.include('cane_y_' + str(i),
        rod(.004, start=(-1.93,y,.462), end=(-1.37,y,.462), color=(.65,.49,.29)))
scene.include('foreground_chair', chair)

curtains = Asset('Left window curtains')
for i in range(7):
    x = -2.23+i*.046
    curtains.include('cream_fold_' + str(i),
        box((.055,.11,2.72), center=(x,.57+(.025 if i%2 else 0),1.35),
            color=(.79+i*.012,.75+i*.012,.65+i*.013)))
curtains.include('bright_window',
    box((.36,.04,2.7), center=(-2.47,.64,1.37), color=(.94,.96,.91)))
scene.include('curtains', curtains)

realize(scene)
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH' or not obj.data.materials:
        continue
    mat = obj.data.materials[0]
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Roughness'].default_value = .76
    if any(word in obj.name.lower() for word in ['upholstery','seat','wing','back']):
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 180
        tex.inputs['Detail'].default_value = 2
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .13
        bump.inputs['Distance'].default_value = .012
        links.new(tex.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bs.inputs['Normal'])
        if 'pillow' not in obj.name.lower():
            coord = nodes.new('ShaderNodeTexCoord')
            mapping = nodes.new('ShaderNodeVectorMath')
            mapping.operation = 'MULTIPLY'
            mapping.inputs[1].default_value = (1.1,4.4,1.1)
            links.new(coord.outputs['Generated'], mapping.inputs[0])
            vor = nodes.new('ShaderNodeTexVoronoi')
            vor.inputs['Scale'].default_value = 24
            links.new(mapping.outputs['Vector'], vor.inputs['Vector'])
            ramp = nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position = .055
            ramp.color_ramp.elements[0].color = (.48,.25,.23,1)
            ramp.color_ramp.elements[1].position = .115
            ramp.color_ramp.elements[1].color = (*fabric,1)
            links.new(vor.outputs['Distance'], ramp.inputs[0])
            links.new(ramp.outputs['Color'], bs.inputs['Base Color'])

set_view(CAMERA, TARGET, lens=LENS, sensor=36)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.72,.75,.79,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .32
area_emitter((-3.4,-.1,3.0), power=450, size=2.5, target=(-.2,0,.6), color=(1,.94,.83))
area_emitter((1,-3,3.6), power=90, size=3, target=(0,0,.8), color=(1,.96,.89))
sc.view_settings.view_transform = 'AgX'
