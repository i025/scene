from sceneact import *
import bpy
import math

# Reference inventory (normalized image coordinates, approximate):
# Ceiling fills frame: pale painted boards, fine horizontal seams, regularly
# spaced raised battens running vertically in the image. Two roof slopes meet
# at the center ridge (x=.50). Their depth and unseen continuation are uncertain.
# Ochre structural beams cross at y=.02, .50, and .96, with brackets at the
# left/right edges and center junctions. The chandelier overlaps the middle beam.
# Brass chandelier: bounds (.33,.25)-(.67,.77), central globe around (.50,.50).
# Twenty thin radiating arms have alternating long/short lengths, open gaps,
# and small reflective spherical ends. A narrow suspension rises behind it.
# Assets: roof_shell, ceiling_battens, structural_frame, chandelier, suspension.
# Estimated expanded geometry: 2 roof slabs + 82 seam rods + 22 battens +
# 24 structural parts + 1 globe + 60 arm parts + 5 central ornaments +
# 3 suspension parts = approximately 199 primitive meshes. No booleans.

scene = Scene('Upward view of brass chandelier')
ivory = (.73, .75, .72)
seam_color = (.59, .61, .58)
batten_color = (.72, .70, .61)
timber_color = (.34, .28, .15)
edge_color = (.43, .36, .20)
gold = (.68, .48, .12)

roof = Asset('roof_shell')
roof_height = 7.15
roof_slope = .095
half_width = 5.8
for side in (-1, 1):
    slab = box((half_width, 10.5, .12),
               center=(side * half_width / 2, 0,
                       roof_height - roof_slope * half_width / 2),
               color=ivory)
    slab.turn('y', side * math.degrees(math.atan(roof_slope)))
    roof.include('painted_roof_half_' + str(side), slab)
    seams = Asset('board_seams_' + str(side))
    for j in range(41):
        yy = -5.05 + j * .252
        seams.include('board_joint_%02d' % j,
                      rod(.004, start=(side*.018, yy, roof_height-.066),
                          end=(side*half_width, yy,
                               roof_height-roof_slope*half_width-.066),
                          color=seam_color))
    roof.include('fine_board_joints_' + str(side), seams)
scene.include('roof_shell', roof)

battens = Asset('ceiling_battens')
for i in range(-10, 11):
    xx = i * .94
    if abs(xx) > 5.7:
        continue
    zz = roof_height - roof_slope * abs(xx) - .12
    battens.include('raised_longitudinal_batten_%02d' % (i+10),
                    box((.105, 10.4, .15), center=(xx, 0, zz),
                        color=batten_color))
battens.include('central_ridge_cover',
                box((.15, 10.5, .19), center=(0, 0, roof_height-.16),
                    color=(.57,.53,.40)))
scene.include('ceiling_battens', battens)

frame = Asset('structural_frame')
for row, yy in enumerate((-3.65, .05, 3.7)):
    for side in (-1, 1):
        start = (side*.025, yy, roof_height-.35)
        end = (side*5.7, yy, roof_height-.35-roof_slope*5.7)
        beam = box((5.72, .19, .23),
                   center=(side*2.86, yy,
                           roof_height-.35-roof_slope*2.86),
                   color=timber_color)
        beam.turn('y', side*math.degrees(math.atan(roof_slope)))
        frame.include('crossbeam_%d_%d' % (row,side), beam)
        # Narrow lighter lip on the visible underside.
        lip = box((5.72, .045, .035),
                  center=(side*2.86, yy-.105,
                          roof_height-.485-roof_slope*2.86),
                  color=edge_color)
        lip.turn('y', side*math.degrees(math.atan(roof_slope)))
        frame.include('beam_lip_%d_%d' % (row,side), lip)
    frame.include('ridge_joint_%d' % row,
                  box((.23,.29,.33),
                      center=(0,yy,roof_height-.37),
                      color=(.30,.26,.16)))
    for side in (-1,1):
        frame.include('end_bracket_%d_%d' % (row,side),
                      box((.68,.42,.28),
                          center=(side*4.64,yy,roof_height-.75),
                          color=edge_color))
for side in (-1,1):
    frame.include('perimeter_rail_%d' % side,
                  box((.20,10.4,.27),
                      center=(side*4.64,0,roof_height-.75),
                      color=timber_color))
scene.include('structural_frame', frame)

chandelier = Asset('chandelier')
hub = (0, 0, 5.08)
chandelier.include('large_polished_central_globe',
                    ball(.218, center=hub, color=gold))

# Pixel-offset estimates preserve the unequal arm lengths and open silhouette.
endpoints = [
    (6,80),(52,62),(81,14),(74,-39),(40,-71),
    (-9,-83),(-53,-66),(-77,-22),(-75,23),(-44,65),
    (-26,39),(3,49),(30,38),(46,13),(44,-18),
    (26,-38),(-4,-44),(-29,-35),(-45,-9),(-45,17)
]
world_per_pixel = .0137
for k, (px,py) in enumerate(endpoints):
    arm = Asset('radial_arm_%02d' % k)
    depth_offset = .055 * math.sin(k*2.1)
    end = (px*world_per_pixel, py*world_per_pixel,
           hub[2]+depth_offset)
    vec = (end[0],end[1],end[2]-hub[2])
    length = math.sqrt(sum(v*v for v in vec))
    unit = tuple(v/length for v in vec)
    base = tuple(hub[j]+unit[j]*.17 for j in range(3))
    neck = tuple(end[j]-unit[j]*.055 for j in range(3))
    arm.include('slender_brass_spoke',
                rod(.011, start=base, end=neck, color=gold))
    arm.include('terminal_neck',
                rod(.024,
                    start=tuple(end[j]-unit[j]*.115 for j in range(3)),
                    end=end, color=gold))
    arm.include('reflective_round_terminal',
                ball(.077 if k<10 else .068, center=end, color=gold))
    chandelier.include('arm_%02d' % k, arm)

for k, (yy,rr) in enumerate(((.22,.067),(.285,.046),(.34,.052))):
    chandelier.include('central_upper_fitting_%d' % k,
                        ball(rr, center=(0, yy, hub[2]+.035),color=gold))
chandelier.include('central_lower_button',
                    ball(.055,center=(0,-.225,hub[2]+.015),color=gold))
chandelier.include('central_front_boss',
                    ball(.091,center=(0,-.012,hub[2]-.184),color=gold))
scene.include('chandelier', chandelier)

suspension = Asset('suspension')
suspension.include('thin_hanging_stem',
                   rod(.014,start=(0,.20,5.16),
                       end=(0,.82,7.00),color=(.38,.32,.17)))
suspension.include('ceiling_mount',
                   rod(.075,start=(0,.82,6.94),
                       end=(0,.82,7.08),color=gold))
suspension.include('stem_lower_sleeve',
                   rod(.026,start=(0,.22,5.19),
                       end=(0,.35,5.58),color=gold))
scene.include('suspension', suspension)

realize(scene)

# Smooth curved metal parts and share a compact material palette.
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for polygon in obj.data.polygons:
        if len(polygon.vertices) <= 4:
            polygon.use_smooth = True
    for mat in obj.data.materials:
        if mat is None:
            continue
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if not bsdf:
            continue
        color = tuple(bsdf.inputs['Base Color'].default_value[:3])
        is_gold = color[0] > color[1]*1.2 and color[1] > color[2]*1.8
        if is_gold:
            bsdf.inputs['Metallic'].default_value = .88
            bsdf.inputs['Roughness'].default_value = .20
        else:
            bsdf.inputs['Roughness'].default_value = .68

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
background.inputs['Color'].default_value = (.65,.70,.78,1)
background.inputs['Strength'].default_value = .40

set_view((0,-.14,0), (0,0,6.9), lens=26, sensor=36)
# Explicitly orient image vertical along the roof ridge.
camera = sc.camera
from mathutils import Vector
direction = Vector((0,0,6.9))-camera.location
camera.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
area_emitter((-3,-1,3.0), power=700, size=4.5,
             target=(0,0,6.8), color=(.88,.94,1))
area_emitter((3,2,3.8), power=550, size=3.4,
             target=(0,0,5.8), color=(1,.90,.69))
area_emitter((-.8,-3,4.6), power=190, size=2.0,
             target=(0,0,5.08), color=(1,1,1))
sc.view_settings.view_transform = 'AgX'
