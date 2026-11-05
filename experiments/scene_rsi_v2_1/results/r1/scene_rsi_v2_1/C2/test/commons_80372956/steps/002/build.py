from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, estimated normalized image bounds:
# roof_shell fills (0,0)-(1,1): two pale boarded slopes meeting near x=.49.
# ceiling_battens: narrow raised strips about .09 image widths apart.
# structural_frame: ochre transverse beams near y=.01, .50, .92;
# longitudinal edge rails near x=.06 and .94, chunky junction brackets.
# chandelier: (.33,.25)-(.67,.77), reflective central globe, twenty thin
# radial spokes with alternating lengths and small spherical terminals.
# suspension: slender central stem behind globe; its attachment is occluded.
# ceiling_hardware: four small dark fasteners on the visible roof surface.
# Unseen roof continuation and suspension geometry remain uncertain.
#
# Feedback comparison: chandelier size and central placement were close.
# Its spoke pattern was horizontally reversed. Roof edge rails and outer
# transverse beams were outside the frame, and lighting washed out the brass.
# Preserve the editable object structure while correcting these discrepancies.
#
# Expanded primitive estimate:
# roof 2 + seams 82 + battens 14 + frame 29 + chandelier 66
# + suspension 3 + fasteners 4 = approximately 200 meshes. No booleans.

scene = Scene('Brass chandelier beneath boarded roof')
ivory = (.60, .63, .62)
seam_color = (.46, .49, .47)
batten_color = (.65, .64, .56)
timber_color = (.35, .27, .12)
edge_color = (.43, .34, .17)
gold = (.64, .44, .095)

roof_height = 7.15
roof_slope = .24
half_width = 5.8
slope_angle = math.degrees(math.atan(roof_slope))

roof = Asset('roof_shell')
for side in (-1, 1):
    slab = box(
        (half_width, 10.5, .12),
        center=(side*half_width/2, 0,
                roof_height-roof_slope*half_width/2),
        color=ivory
    )
    slab.turn('y', side*slope_angle)
    roof.include('painted_roof_half_' + str(side), slab)
    joints = Asset('board_seams_' + str(side))
    for j in range(41):
        yy = -5.05+j*.252
        joints.include(
            'board_joint_%02d' % j,
            rod(.004,
                start=(side*.018, yy, roof_height-.065),
                end=(side*half_width, yy,
                     roof_height-roof_slope*half_width-.065),
                color=seam_color)
        )
    roof.include('fine_board_joints_' + str(side), joints)
scene.include('roof_shell', roof)

battens = Asset('ceiling_battens')
for i in range(-6, 7):
    xx = i*.94
    battens.include(
        'raised_longitudinal_batten_%02d' % (i+6),
        box((.105, 10.4, .15),
            center=(xx, 0, roof_height-roof_slope*abs(xx)-.12),
            color=batten_color)
    )
battens.include(
    'central_ridge_cover',
    box((.15, 10.5, .19), center=(0, 0, roof_height-.16),
        color=(.48, .45, .33))
)
scene.include('ceiling_battens', battens)

frame = Asset('structural_frame')
for row, yy in enumerate((-2.34, .05, 2.88)):
    for side in (-1, 1):
        beam = box(
            (5.72, .25, .27),
            center=(side*2.86, yy,
                    roof_height-.35-roof_slope*2.86),
            color=timber_color
        )
        beam.turn('y', side*slope_angle)
        frame.include('crossbeam_%d_%d' % (row, side), beam)
        lip = box(
            (5.72, .045, .04),
            center=(side*2.86, yy-.14,
                    roof_height-.505-roof_slope*2.86),
            color=edge_color
        )
        lip.turn('y', side*slope_angle)
        frame.include('beam_lip_%d_%d' % (row, side), lip)
    frame.include(
        'ridge_joint_%d' % row,
        box((.23, .32, .34),
            center=(0, yy, roof_height-.39),
            color=(.29, .24, .13))
    )
    for side in (-1, 1):
        xx = side*3.67
        zz = roof_height-.37-roof_slope*abs(xx)
        frame.include(
            'end_bracket_%d_%d' % (row, side),
            box((.69, .43, .32), center=(xx, yy, zz),
                color=edge_color)
        )
        frame.include(
            'bracket_dark_seat_%d_%d' % (row, side),
            box((.47, .08, .09), center=(xx, yy-.24, zz-.15),
                color=timber_color)
        )
for side in (-1, 1):
    xx = side*3.67
    frame.include(
        'perimeter_rail_%d' % side,
        box((.20, 10.4, .27),
            center=(xx, 0, roof_height-.36-roof_slope*abs(xx)),
            color=timber_color)
    )
scene.include('structural_frame', frame)

hardware = Asset('ceiling_hardware')
for i, (xx, yy) in enumerate(((-2.16, 1.51), (2.19, 1.48),
                             (-2.12, -1.36), (2.14, -1.38))):
    hardware.include(
        'small_dark_fastener_%d' % i,
        ball(.022, center=(xx, yy,
                          roof_height-roof_slope*abs(xx)-.075),
             color=(.12, .13, .12))
    )
scene.include('ceiling_hardware', hardware)

chandelier = Asset('chandelier')
hub = (.027, 0, 5.08)
chandelier.include(
    'large_polished_central_globe',
    ball(.218, center=hub, color=gold)
)

# Image-space offsets from the globe center. Looking upward reverses world X.
endpoints = [
    (6,80), (52,62), (81,14), (74,-39), (40,-71),
    (-9,-83), (-53,-66), (-77,-22), (-75,23), (-44,65),
    (-26,39), (3,49), (30,38), (46,13), (44,-18),
    (26,-38), (-4,-44), (-29,-35), (-45,-9), (-45,17)
]
world_per_pixel = .0137
for k, (px, py) in enumerate(endpoints):
    arm = Asset('radial_arm_%02d' % k)
    depth_offset = .055*math.sin(k*2.1)
    end = (hub[0]-px*world_per_pixel,
           hub[1]+py*world_per_pixel, hub[2]+depth_offset)
    vec = tuple(end[j]-hub[j] for j in range(3))
    length = math.sqrt(sum(v*v for v in vec))
    unit = tuple(v/length for v in vec)
    base = tuple(hub[j]+unit[j]*.17 for j in range(3))
    neck = tuple(end[j]-unit[j]*.055 for j in range(3))
    arm.include(
        'slender_brass_spoke',
        rod(.011, start=base, end=neck, color=gold)
    )
    arm.include(
        'terminal_neck',
        rod(.024,
            start=tuple(end[j]-unit[j]*.115 for j in range(3)),
            end=end, color=gold)
    )
    arm.include(
        'reflective_round_terminal',
        ball(.085 if k < 10 else .073, center=end, color=gold)
    )
    chandelier.include('arm_%02d' % k, arm)

for k, (yy, radius) in enumerate(((.22,.067), (.285,.046), (.34,.052))):
    chandelier.include(
        'central_upper_fitting_%d' % k,
        ball(radius, center=(hub[0], yy, hub[2]+.035), color=gold)
    )
chandelier.include(
    'central_lower_button',
    ball(.055, center=(hub[0], -.225, hub[2]+.015), color=gold)
)
chandelier.include(
    'central_front_boss',
    ball(.091, center=(hub[0], -.012, hub[2]-.184), color=gold)
)
scene.include('chandelier', chandelier)

suspension = Asset('suspension')
suspension.include(
    'thin_hanging_stem',
    rod(.014, start=(hub[0], .20, 5.16),
        end=(0, .82, 7.00), color=(.30, .26, .13))
)
suspension.include(
    'ceiling_mount',
    rod(.075, start=(0, .82, 6.94), end=(0, .82, 7.08), color=gold)
)
suspension.include(
    'stem_lower_sleeve',
    rod(.026, start=(hub[0], .22, 5.19),
        end=(hub[0], .35, 5.58), color=gold)
)
scene.include('suspension', suspension)

realize(scene)

processed_materials = set()
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    # Smooth curved geometry while retaining crisp architectural boxes.
    if len(obj.data.polygons) > 12:
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    for mat in obj.data.materials:
        if mat is None or mat.name in processed_materials:
            continue
        processed_materials.add(mat.name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is None:
            continue
        c = tuple(bsdf.inputs['Base Color'].default_value[:3])
        is_gold = sum((c[i]-gold[i])**2 for i in range(3)) < .003
        bsdf.inputs['Metallic'].default_value = 1.0 if is_gold else 0.0
        bsdf.inputs['Roughness'].default_value = .16 if is_gold else .62

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
background.inputs['Color'].default_value = (.49, .54, .62, 1)
background.inputs['Strength'].default_value = .13

set_view((0, -.14, 0), (0, 0, 6.9), lens=26, sensor=36)
camera = sc.camera
direction = Vector((0, 0, 6.9))-camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

area_emitter((-3, -1, 3.0), power=360, size=3.8,
             target=(0, 0, 6.8), color=(.88, .94, 1))
area_emitter((3, 2, 3.8), power=250, size=2.8,
             target=(0, 0, 5.8), color=(1, .90, .72))
area_emitter((-.8, -3, 4.6), power=90, size=1.3,
             target=(0, 0, 5.08), color=(1, 1, 1))
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = -.25
