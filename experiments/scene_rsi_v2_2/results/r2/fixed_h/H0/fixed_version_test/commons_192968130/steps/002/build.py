from sceneact import *
import bpy
import math
import random

random.seed(12)
scene = Scene("Walnut kitchen")

def add(name, size, center, color):
    node = box(size=size, center=center, color=color)
    scene.include(name, node)
    return node

wood = (.235, .105, .043)
stone = (.73, .705, .65)

# Architecture.
add("floor", (10, 12, .12), (-1, 0, -.065), (.57, .54, .48))
add("back_wall", (7, .13, 3.4), (-1.85, 3.58, 1.7), (.095, .068, .043))
add("right_wall", (.12, 10, 3.4), (1.15, -.8, 1.7), (.87, .855, .80))
add("ceiling", (8, 11, .12), (-1.6, -.4, 3.20), (.83, .82, .77))

for i in range(48):
    x = -4.55 + i * .09
    if x > -.37:
        break
    shade = random.uniform(.78, 1.2)
    add("vertical_oak_%02d" % i, (.052, .075, 3.12),
        (x, 3.465, 1.58),
        (.42 * shade, .22 * shade, .095 * shade))

# White door and frame.
add("door_recess", (1.02, .08, 2.27), (-.86, 3.435, 1.135), (.48, .46, .40))
add("door_leaf", (.88, .055, 2.16), (-.86, 3.37, 1.085), (.79, .80, .77))
for x in (-1.345, -.375):
    add("door_frame_side_" + str(x), (.055, .06, 2.27),
        (x, 3.335, 1.135), (.88, .88, .84))
add("door_frame_top", (1.025, .06, .055),
    (-.86, 3.335, 2.245), (.88, .88, .84))
add("door_handle_plate", (.033, .014, .13),
    (-1.195, 3.326, 1.06), (.56, .56, .52))
scene.include("door_handle", rod(
    .012, start=(-1.20, 3.30, 1.10), end=(-1.08, 3.30, 1.10),
    color=(.40, .41, .39)))
scene.include("keyhole", ball(
    .013, center=(-1.195, 3.31, 1.015), color=(.22, .23, .21)))
for z in (.28, 1.12):
    add("wall_switch_" + str(z), (.095, .022, .095),
        (-1.55, 3.40, z), (.88, .87, .82))
    add("switch_inner_" + str(z), (.065, .008, .065),
        (-1.55, 3.383, z), (.75, .75, .70))

# Low cabinet against the feature wall.
add("bench_dark_body", (1.55, .53, .53), (-2.96, 3.16, .265), (.028, .035, .032))
add("bench_white_drawer", (1.43, .022, .36), (-2.99, 2.883, .225), (.83, .85, .83))
add("bench_wood_top", (1.57, .56, .045), (-2.96, 3.15, .555), (.16, .13, .09))
add("bench_right_end", (.045, .55, .55), (-2.19, 3.15, .28), (.035, .041, .037))

# Pale staggered floor tiles.
for ix in range(13):
    for iy in range(21):
        x = -4.8 + ix * .61 + (.305 if iy % 2 else 0)
        y = -4.8 + iy * .42
        v = random.uniform(-.025, .025)
        add("floor_tile_%d_%d" % (ix, iy), (.603, .413, .012),
            (x, y, .003), (.58 + v, .555 + v, .505 + v))

# Base cupboards and counter.
add("base_cabinets", (1.39, 6.65, .80), (.405, .06, .43), (.22, .17, .12))
add("plinth", (1.24, 6.65, .10), (.46, .06, .07), (.07, .065, .05))
add("countertop", (1.43, 6.76, .055), (.405, .06, .865), stone)
for y in (-2.65, -1.82, -.99, -.16, .67, 1.50, 2.33, 3.1):
    add("cabinet_front_" + str(y), (.022, .81, .72), (-.301, y, .43), wood)

# Reflective cream backsplash.
add("backsplash", (.025, 6.9, .94), (1.078, -.02, 1.36), (.82, .825, .79))
add("backsplash_bottom_seal", (.018, 6.9, .012),
    (1.056, -.02, .905), (.66, .66, .61))
for y in (-1.9, .65, 2.75):
    add("backsplash_joint_" + str(y), (.005, .007, .88),
        (1.060, y, 1.36), (.76, .77, .73))

# Walnut wall cabinets.
add("upper_cabinet_body", (.94, 6.85, 1.47), (.65, -.02, 2.485), wood)
add("upper_end_panel", (.055, .39, 1.53),
    (-.285, 3.23, 2.515), (.17, .072, .028))
add("upper_end_return", (.42, .055, 1.53), (-.055, 3.43, 2.515), wood)
for i in range(9):
    y = -3.02 + i * .78
    add("upper_door_%d" % i, (.027, .768, 1.40), (.164, y, 2.505), wood)
    add("upper_door_bottom_%d" % i, (.045, .768, .035),
        (.145, y, 1.789), (.115, .051, .023))
add("under_cabinet_shadow", (.90, 6.8, .025),
    (.65, -.02, 1.752), (.105, .09, .061))
add("led_channel", (.022, 6.77, .018), (.265, -.02, 1.733), (.73, .66, .47))

# Dark sink with a narrow ribbed draining area.
add("sink_rim", (.98, 1.00, .018), (.275, .56, .902), (.24, .205, .125))
add("sink_black_recess", (.91, .91, .019),
    (.275, .56, .912), (.018, .021, .018))
add("sink_basin_bottom", (.64, .63, .012),
    (.145, .56, .917), (.025, .032, .028))
for x in (-.19, .48):
    add("sink_basin_side_" + str(x), (.025, .74, .022),
        (x, .56, .927), (.11, .105, .072))
for y in (.185, .935):
    add("sink_basin_end_" + str(y), (.69, .025, .022),
        (.145, y, .927), (.12, .11, .075))
add("drainer", (.18, .80, .018), (.66, .56, .927), (.10, .105, .083))
for j in range(8):
    add("drainer_rib_%d" % j, (.15, .012, .009),
        (.66, .23 + j * .09, .941), (.34, .30, .20))

# Foreground glass cooktop.
add("hob_metal_edge", (1.15, 1.54, .015), (.36, -2.13, .906), (.20, .20, .17))
add("black_glass_hob", (1.125, 1.515, .012),
    (.36, -2.13, .918), (.009, .014, .013))
for i, (x, y, r) in enumerate([
    (.07, -1.72, .225), (.62, -1.72, .19),
    (.06, -2.42, .255), (.65, -2.42, .235)
]):
    points = [
        (x + r * math.cos(a * 2 * math.pi / 96),
         y + r * math.sin(a * 2 * math.pi / 96), .926)
        for a in range(97)
    ]
    scene.include("burner_%d" % i,
                  sweep_tube(points=points, radius=.0025, color=(.16, .17, .145)))
for j in range(5):
    add("hob_touch_%d" % j, (.018, .008, .001),
        (.90, -1.72 - j * .08, .927), (.30, .31, .27))

# Brushed metal extractor underside.
add("extractor_frame", (.70, 1.16, .035),
    (.66, -.22, 1.715), (.48, .47, .41))
add("extractor_filter", (.55, .78, .009),
    (.64, -.15, 1.692), (.35, .36, .33))
for i in range(13):
    add("extractor_slot_%d" % i, (.43, .009, .004),
        (.64, -.49 + i * .054, 1.685), (.22, .24, .22))
add("extractor_controls", (.13, .21, .009),
    (.39, -.52, 1.687), (.32, .33, .30))

realize(scene)

def material(name, color, roughness=.5, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    return mat

walnut = material("Walnut grain", wood, .33)
nodes = walnut.node_tree.nodes
links = walnut.node_tree.links
coord = nodes.new("ShaderNodeTexCoord")
mapping = nodes.new("ShaderNodeVectorMath")
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (11, 1.2, 3)
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 3
noise.inputs["Detail"].default_value = 3
links.new(coord.outputs["Generated"], mapping.inputs[0])
links.new(mapping.outputs[0], noise.inputs["Vector"])
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .18
ramp.color_ramp.elements[0].color = (.055, .018, .006, 1)
ramp.color_ramp.elements[1].position = .83
ramp.color_ramp.elements[1].color = (.31, .13, .045, 1)
links.new(noise.outputs["Fac"], ramp.inputs[0])
links.new(ramp.outputs[0], nodes.get("Principled BSDF").inputs["Base Color"])

marble = material("Warm veined stone", stone, .31)
nodes = marble.node_tree.nodes
links = marble.node_tree.links
coord = nodes.new("ShaderNodeTexCoord")
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 5
noise.inputs["Detail"].default_value = 5
noise.inputs["Roughness"].default_value = .72
links.new(coord.outputs["Generated"], noise.inputs["Vector"])
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .35
ramp.color_ramp.elements[0].color = (.20, .17, .12, 1)
ramp.color_ramp.elements[1].position = .43
ramp.color_ramp.elements[1].color = (.77, .745, .67, 1)
links.new(noise.outputs["Fac"], ramp.inputs[0])
links.new(ramp.outputs[0], nodes.get("Principled BSDF").inputs["Base Color"])
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .10
bump.inputs["Distance"].default_value = .006
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs[0], nodes.get("Principled BSDF").inputs["Normal"])

glass = material("Polished black ceramic", (.008, .012, .011), .095, .20)
backsplash_mat = material("Glossy ivory glass", (.83, .835, .80), .14)
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for i, mat in enumerate(obj.data.materials):
        if mat is None:
            continue
        c = mat.diffuse_color
        if sum(abs(c[k] - wood[k]) for k in range(3)) < .025:
            obj.data.materials[i] = walnut
        elif sum(abs(c[k] - stone[k]) for k in range(3)) < .025:
            obj.data.materials[i] = marble
        elif sum(abs(c[k] - (.009, .014, .013)[k]) for k in range(3)) < .009:
            obj.data.materials[i] = glass
        elif sum(abs(c[k] - (.82, .825, .79)[k]) for k in range(3)) < .015:
            obj.data.materials[i] = backsplash_mat

emission = material("Warm LED", (1, .79, .43), .3)
bs = emission.node_tree.nodes.get("Principled BSDF")
bs.inputs["Emission Color"].default_value = (1, .76, .36, 1)
bs.inputs["Emission Strength"].default_value = 6
for obj in bpy.context.scene.objects:
    if "led_channel" in obj.name.lower() and obj.type == 'MESH':
        obj.data.materials.clear()
        obj.data.materials.append(emission)

set_view((0, -3.60, 1.40), (0, 3.50, 1.303), lens=36, sensor=36)
area_emitter((-3, -1.7, 2.65), power=700, size=4.5,
             target=(-.6, 2, .6), color=(1, .94, .83))
area_emitter((-2.8, 2.5, 2.75), power=230, size=2.2,
             target=(-1, 3.45, 1.2), color=(1, .93, .80))
area_emitter((.44, .8, 1.70), power=65, size=2.5,
             target=(1.05, .8, 1.19), color=(1, .78, .43))
area_emitter((.40, -1.8, 1.70), power=55, size=2.2,
             target=(1.05, -1.8, 1.13), color=(1, .82, .55))

sc = bpy.context.scene
world = sc.world
if world is None:
    world = bpy.data.worlds.new("Kitchen World")
    sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.70, .72, .74, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .28

sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.render.resolution_x = 512
sc.render.resolution_y = 342
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
