# Reference inventory (normalized image bounds, approximate):
# - Pale gray floor: lower portion, (0, .78) to (1, 1); rounded white cove.
# - Blue paneled back wall: (.10, .22) to (.70, .84), with vertical seams.
# - Blue right return wall: (.69, .13) to (.91, .91), with vertical seams.
# - Stainless double-door cabinet: (.16, .40) to (.31, .83), shelves and handles.
# - Dandelion photographic mural: (.37, .23) to (.64, .82); fine overlapping
#   seed heads and purple stems. Exact fine details are uncertain.
# - Dark digital clock: (.79, .35) to (.88, .51), on the right wall.
# - Exposed dark ceiling and T grid: (0, 0) to (.97, .23), with white LED panels.
# - Ceiling framing, rods and services are partly occluded by the visible ceiling.
# - Numbered reference markers are intentionally omitted.
#
# Estimated expanded SceneAct primitives: architecture ~30, ceiling ~45,
# cabinet ~28, display ~3, mural ~125, lighting panels ~4; total ~235.
# Mural is a procedural arrangement of geometric stems and seed filaments,
# rather than a reference image or external texture.

import math
import random
import bpy
from sceneact import *

random.seed(15)
scene = Scene("Clean laboratory")

blue = (0.035, 0.42, 0.66)
blue_alt = (0.035, 0.39, 0.62)
seam = (0.018, 0.19, 0.29)
floor_color = (0.49, 0.53, 0.52)
white = (0.83, 0.87, 0.85)
steel = (0.56, 0.61, 0.60)
dark_steel = (0.15, 0.20, 0.20)
ceiling_dark = (0.16, 0.20, 0.20)
grid_color = (0.38, 0.44, 0.43)
mural_bg = (0.69, 0.79, 0.75)

# World coordinates: back wall at y=0; room extends toward negative y.
# Right wall extends from x=4.8 toward the camera.
room = Asset("Architecture")
room.include("floor", box((6.9, 5.8, 0.12), center=(2.25, -2.30, -0.06), color=floor_color))
room.include("back_wall", box((4.85, 0.12, 3.0), center=(2.425, 0.06, 1.50), color=blue))
room.include("right_wall", box((0.12, 3.6, 3.0), center=(4.86, -1.80, 1.50), color=blue_alt))
room.include("left_edge", box((0.055, 0.16, 3.0), center=(0, 0, 1.5), color=white))
room.include("right_outer_edge", box((0.10, 0.10, 3.0), center=(4.86, -3.58, 1.5), color=(0.28, 0.32, 0.31)))

# Narrow seams in the modular panels.
for i, x in enumerate((0.48, 1.10, 1.68, 2.02, 3.94, 4.35)):
    room.include("back_panel_joint_%02d" % i,
                 box((0.012, 0.014, 2.89), center=(x, -0.069, 1.50), color=seam))
for i, y in enumerate((-0.48, -1.24, -2.07, -2.91)):
    room.include("return_panel_joint_%02d" % i,
                 box((0.014, 0.014, 2.89), center=(4.785, y, 1.50), color=seam))

# White curved cove skirting, approximated by a low plinth and a round transition.
room.include("back_cove_plinth", box((4.83, 0.10, 0.105), center=(2.42, -0.075, 0.052), color=white))
room.include("back_cove_round", rod(0.055, start=(0, -0.12, 0.055), end=(4.80, -0.12, 0.055), color=white))
room.include("return_cove_plinth", box((0.10, 3.55, 0.105), center=(4.78, -1.78, 0.052), color=white))
room.include("return_cove_round", rod(0.055, start=(4.73, 0, 0.055), end=(4.73, -3.55, 0.055), color=white))
scene.include("architecture", room)

# A shallow stainless cabinet with two glazed doors, visible shelves and handles.
cabinet = Asset("Stainless glass storage cabinet")
cabinet.include("body", box((0.99, 0.31, 1.84), center=(1.00, -0.20, 0.96), color=steel))
cabinet.include("interior", box((0.84, 0.025, 1.62), center=(1.00, -0.367, 0.98), color=(0.20, 0.27, 0.27)))
for x in (0.61, 1.39):
    cabinet.include("side_frame_%.2f" % x, box((0.055, 0.055, 1.77), center=(x, -0.39, 0.97), color=white))
for z in (0.10, 1.84):
    cabinet.include("horizontal_frame_%.2f" % z, box((0.84, 0.055, 0.055), center=(1.00, -0.39, z), color=white))
cabinet.include("center_mullion", box((0.045, 0.055, 1.70), center=(1.00, -0.40, 0.97), color=white))
for z in (0.38, 0.70, 1.02, 1.34, 1.65):
    cabinet.include("shelf_%.2f" % z, box((0.78, 0.19, 0.025), center=(1.00, -0.34, z), color=(0.65, 0.70, 0.68)))
for x in (0.79, 1.21):
    cabinet.include("glazing_%.2f" % x, box((0.32, 0.012, 1.57), center=(x, -0.42, 0.98), color=(0.35, 0.44, 0.44), opacity=0.22))
for x in (0.955, 1.045):
    cabinet.include("handle_%.3f" % x, rod(0.012, start=(x, -0.462, 0.85), end=(x, -0.462, 1.02), color=(0.72, 0.76, 0.74)))
scene.include("cabinet", cabinet)

# Mural surface: pale, softly mottled background with a subtle warm lower edge.
mural = Asset("Dandelion mural")
mural.include("background", box((1.92, 0.025, 2.84), center=(2.98, -0.088, 1.49), color=mural_bg))
mural.include("lower_warm_band", box((1.92, 0.006, 0.22), center=(2.98, -0.107, 0.19), color=(0.78, 0.67, 0.48)))
mural.include("left_border", box((0.015, 0.017, 2.84), center=(2.02, -0.112, 1.49), color=(0.32, 0.45, 0.43)))
mural.include("right_border", box((0.015, 0.017, 2.84), center=(3.94, -0.112, 1.49), color=(0.32, 0.45, 0.43)))

# Graphic stems and fine radial dandelion structures, kept within the mural.
ink = (0.22, 0.09, 0.19)
fine = (0.31, 0.32, 0.29)
front_y = -0.122
stems = [
    [(2.10, .12), (2.49, .45), (3.12, .77), (3.43, 1.52)],
    [(2.43, .12), (2.93, .34), (3.31, .72), (3.55, 1.67)],
    [(3.72, .12), (3.47, .45), (3.20, .83), (2.91, 1.20)],
    [(3.90, .20), (3.45, .39), (3.13, .57), (2.75, .90)],
    [(2.77, .10), (2.95, .40), (3.09, .70), (3.03, 1.14)],
    [(2.23, .12), (2.62, .27), (2.92, .43), (3.60, .55)]
]
for i, path in enumerate(stems):
    pts = [(x, front_y - i * .001, z) for x, z in path]
    mural.include("dark_stem_%02d" % i, sweep_tube(points=pts, radius=0.010 if i < 3 else 0.006, color=ink))

heads = [(2.37, 2.06, .54), (3.61, 2.32, .56),
         (2.76, 1.12, .49), (3.68, 1.20, .50)]
for h, (cx, cz, radius) in enumerate(heads):
    mural.include("seed_center_%d" % h, ball(0.028, center=(cx, front_y-.012, cz), color=ink))
    for j in range(15):
        a = 2 * math.pi * j / 15 + 0.07 * h
        ex = cx + radius * math.cos(a)
        ez = cz + radius * math.sin(a)
        # Clip visible filaments to the mural rectangle.
        ex = min(3.91, max(2.05, ex))
        ez = min(2.87, max(.10, ez))
        sx = cx + .045 * math.cos(a)
        sz = cz + .045 * math.sin(a)
        mural.include("filament_%d_%02d" % (h, j),
                      rod(.0027, start=(sx, front_y-.014, sz),
                          end=(ex, front_y-.014, ez), color=fine))
        if j % 2 == 0:
            dx = .045 * math.cos(a + .65)
            dz = .045 * math.sin(a + .65)
            mural.include("seed_tip_%d_%02d" % (h, j),
                          rod(.002, start=(ex-dx, front_y-.015, ez-dz),
                              end=(ex+dx, front_y-.015, ez+dz), color=(.48, .51, .45)))
scene.include("mural", mural)

# Clock panel mounted flush to the right wall.
display = Asset("Wall digital display")
display.include("frame", box((0.045, 0.80, 0.63), center=(4.765, -1.92, 2.05), color=(0.13, 0.18, 0.24)))
display.include("screen", box((0.012, 0.74, 0.56), center=(4.735, -1.92, 2.05), color=(0.035, 0.09, 0.19)))
display.include("lower_rule", box((0.007, 0.66, 0.008), center=(4.726, -1.92, 1.91), color=(0.25, 0.38, 0.47)))
scene.include("digital_display", display)

# Exposed ceiling with narrow T-bar grid and two flush luminous panels.
ceiling = Asset("Ceiling grid and exposed services")
ceiling.include("dark_soffit", box((5.10, 3.75, .10), center=(2.42, -1.82, 3.08), color=ceiling_dark))
for i, x in enumerate((0.0, .8, 1.6, 2.4, 3.2, 4.0, 4.8)):
    ceiling.include("longitudinal_T_bar_%d" % i,
                    box((.028, 3.65, .045), center=(x, -1.78, 3.005), color=grid_color))
for i, y in enumerate((-.15, -.75, -1.35, -1.95, -2.55, -3.15, -3.55)):
    ceiling.include("cross_T_bar_%d" % i,
                    box((4.83, .026, .045), center=(2.41, y, 3.00), color=grid_color))
for i, (x, y) in enumerate(((2.82, -.52), (.94, -2.35), (3.78, -2.80))):
    ceiling.include("LED_panel_%d" % i,
                    box((.70, .49, .025), center=(x, y, 2.974), color=(.88, .97, .98)))
for i, x in enumerate((.15, 1.75, 3.35, 4.68)):
    ceiling.include("structure_beam_%d" % i,
                    box((.075, 3.65, .12), center=(x, -1.8, 3.19), color=(.21, .25, .24)))
for i, x in enumerate((.45, 1.65, 2.85, 4.05)):
    ceiling.include("hanger_%d" % i,
                    rod(.012, start=(x, -.35, 3.02), end=(x, -.35, 3.32), color=steel))
ceiling.include("exposed_service", rod(.035, start=(.10, -.32, 3.18), end=(4.70, -.32, 3.18), color=(.30, .34, .33)))
scene.include("ceiling", ceiling)

realize(scene)

# Configure physically distinct surface finishes after SceneAct realization.
for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value = 0.65

# Add legible screen lettering as editable Blender text objects.
def wall_text(name, text, location, size, color):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.0005
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    # Text local X maps along wall toward increasing y; local Y points upward.
    obj.rotation_euler = (math.pi / 2, 0, math.pi / 2)
    mat = bpy.data.materials.get("Clock lettering")
    if mat is None:
        mat = bpy.data.materials.new("Clock lettering")
        mat.diffuse_color = (*color, 1)
        mat.use_nodes = True
        node = mat.node_tree.nodes.get("Principled BSDF")
        node.inputs["Base Color"].default_value = (*color, 1)
        node.inputs["Emission Color"].default_value = (*color, 1)
        node.inputs["Emission Strength"].default_value = 0.3
    obj.data.materials.append(mat)

wall_text("Digital time", "09:29:07", (4.717, -1.92, 2.09), .115, (.58, .72, .78))
wall_text("Digital date", "2026.11.11", (4.716, -1.92, 1.96), .045, (.48, .62, .70))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.72, 0.78, 0.78, 1)
background.inputs["Strength"].default_value = 0.45

# LED panels illuminate the room with large, soft area sources.
for x, y in ((2.82, -.52), (.94, -2.35), (3.78, -2.80)):
    area_emitter((x, y, 2.90), power=350, size=1.15, target=(x, y, 0.0), color=(0.88, 0.95, 1.0))
area_emitter((1.8, -4.2, 3.7), power=350, size=4.0, target=(2.4, -.5, 1.3))

set_view((2.30, -7.6, 2.35), (2.55, -.10, 1.43), lens=35, sensor=36)
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
