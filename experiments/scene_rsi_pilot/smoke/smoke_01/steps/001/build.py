from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(8)
scene = Scene(name="Small corner kitchen")
wood = (.24, .073, .032)
cream = (.72, .61, .46)
wall = (.72, .70, .63)
tile = (.66, .53, .41)
chrome = (.54, .57, .57)

def add(name, node):
    scene.include(name, node)

add("floor", box((7, 7, .10), center=(1, -1, -.05), color=(.37, .35, .31)))
add("left plaster wall", box((.12, 4.5, 3.4), center=(-.075, -1.6, 1.7), color=wall))
add("window wall", box((4.5, .12, 3.4), center=(2.1, .075, 1.7), color=wall))

# The two cabinet runs meet at the inside corner.
add("left cabinet carcass", box((.59, 2.35, .84), center=(.295, -1.175, .46), color=wood))
add("back cabinet carcass", box((3.1, .58, .84), center=(1.55, -.29, .46), color=wood))
add("left recessed toe kick", box((.47, 2.35, .12), center=(.235, -1.175, .075), color=(.105, .045, .025)))
add("back recessed toe kick", box((3.1, .46, .12), center=(1.55, -.23, .075), color=(.105, .045, .025)))

def handle(name, a, b):
    add(name, rod(.008, start=a, end=b, color=chrome))

for i in range(4):
    yc = -2.35 + (i + .5) * .435
    add("left lower door %d" % i,
        box((.025, .422, .745), center=(.604, yc, .482), color=wood))
    hy = yc + (.135 if i % 2 == 0 else -.135)
    handle("left lower pull %d" % i, (.632, hy, .69), (.632, hy, .83))
    for zz in (.705, .815):
        add("left pull mount %d %s" % (i, zz),
            rod(.006, start=(.614, hy, zz), end=(.634, hy, zz), color=chrome))

for i in range(6):
    xc = .62 + (i + .5) * .415
    add("back lower door %d" % i,
        box((.402, .025, .745), center=(xc, -.595, .482), color=wood))
    hx = xc + (.13 if i % 2 == 0 else -.13)
    handle("back lower pull %d" % i, (hx, -.625, .69), (hx, -.625, .83))
    for zz in (.705, .815):
        add("back pull mount %d %s" % (i, zz),
            rod(.006, start=(hx, -.607, zz), end=(hx, -.632, zz), color=chrome))

# Beige stone countertop, including actual openings for the bowls.
add("return countertop", box((.665, 2.40, .047), center=(.3125, -1.18, .918), color=cream))
counter = box((3.18, .665, .047), center=(1.56, -.3125, .918), color=cream)
sink_x = 1.56
for dx in (-.286, .286):
    cutter = fillet_box((.493, .355, .3), radius=.065,
                        center=(sink_x + dx, -.333, .91))
    counter = subtract(counter, cutter)
add("sink run countertop", counter)

# A low stone upstand and square ceramic backsplash.
add("left stone upstand", box((.034, 2.4, .055), center=(.02, -1.18, .966), color=cream))
add("back stone upstand", box((3.18, .034, .055), center=(1.56, -.02, .966), color=cream))
for row in range(2):
    z = 1.0 + (row + .5) * .285
    for i in range(9):
        y = -2.50 + (i + .5) * .285
        c = tuple(v + random.uniform(-.025, .025) for v in tile)
        add("left backsplash %d %d" % (row, i),
            box((.016, .279, .279), center=(.004, y, z), color=c))
    for i in range(12):
        x = (i + .5) * .285
        c = tuple(v + random.uniform(-.022, .022) for v in tile)
        add("back backsplash %d %d" % (row, i),
            box((.279, .016, .279), center=(x, -.006, z), color=c))

# Tall, dark timber upper cabinets along the return.
add("upper left carcass", box((.345, 2.40, 1.18), center=(.1725, -1.18, 2.13), color=wood))
for i in range(5):
    yc = -2.38 + (i + .5) * .475
    add("upper left door %d" % i,
        box((.024, .462, 1.165), center=(.357, yc, 2.135), color=wood))
    hy = yc + (.16 if i % 2 == 0 else -.16)
    handle("upper left handle %d" % i, (.381, hy, 1.585), (.381, hy, 1.745))
add("corner upper carcass", box((.64, .33, 1.18), center=(.32, -.165, 2.13), color=wood))
for i in range(2):
    xc = .345 + (i + .5) * .145
    add("corner upper door %d" % i,
        box((.139, .025, 1.165), center=(xc, -.343, 2.135), color=wood))
    handle("corner upper handle %d" % i,
           (xc + .035, -.369, 1.59), (xc + .035, -.369, 1.75))

# Two white double-hung windows; the right one extends out of the photograph.
for wi, xc in enumerate((1.35, 2.51)):
    width = .86
    bottom, top = 1.285, 2.94
    middle = (bottom + top) / 2
    add("daylight glass %d" % wi,
        box((width, .018, top-bottom), center=(xc, -.037, middle),
            color=(.91, .93, .86)))
    for xx in (xc - width/2 - .025, xc + width/2 + .025):
        add("window outer side %d %s" % (wi, xx),
            box((.066, .075, top-bottom+.12), center=(xx, -.069, middle),
                color=(.86, .86, .80)))
    for zz in (bottom-.025, top+.025):
        add("window outer horizontal %d %s" % (wi, zz),
            box((width+.16, .08, .065), center=(xc, -.073, zz),
                color=(.88, .88, .83)))
    for xx in (xc-width/2+.026, xc+width/2-.026):
        add("window sash side %d %s" % (wi, xx),
            box((.031, .041, top-bottom-.04), center=(xx, -.095, middle),
                color=(.93, .93, .88)))
    add("window meeting rail %d" % wi,
        box((width-.035, .048, .061), center=(xc, -.104, 2.105),
            color=(.94, .94, .89)))
    add("deep white sill %d" % wi,
        box((width+.17, .16, .043), center=(xc, -.105, bottom-.045),
            color=(.85, .85, .79)))
    # Barely visible pale forms beyond the overexposed glazing.
    add("distant light building %d" % wi,
        box((.28, .005, .18), center=(xc-.1, -.051, 2.37),
            color=(.85, .86, .79)))

# Stainless double sink, with rounded rims and depressed bowls.
rim = fillet_box((1.17, .498, .025), radius=.075,
                 center=(sink_x, -.333, .952), color=chrome)
for dx in (-.286, .286):
    rim = subtract(rim, fillet_box((.493, .355, .12), radius=.067,
                                  center=(sink_x+dx, -.333, .947)))
add("stainless sink rim", rim)
for i, dx in enumerate((-.286, .286)):
    outer = fillet_box((.519, .385, .166), radius=.075,
                       center=(sink_x+dx, -.333, .866), color=chrome)
    inner = fillet_box((.486, .349, .19), radius=.068,
                       center=(sink_x+dx, -.333, .899))
    add("sink bowl %d" % i, subtract(outer, inner))
    add("sink drain %d" % i,
        rod(.033, length=.004, center=(sink_x+dx, -.333, .79),
            color=(.22, .24, .23)))

add("faucet foot", rod(.031, length=.023, center=(sink_x, -.108, .975), color=chrome))
add("curved faucet", sweep_tube(
    points=[(sink_x, -.108, .98), (sink_x, -.108, 1.10),
            (sink_x, -.115, 1.17), (sink_x, -.145, 1.197),
            (sink_x, -.205, 1.198), (sink_x, -.245, 1.18),
            (sink_x, -.255, 1.14)],
    radius=.013, color=chrome))
for dx in (-.15, .15):
    add("tap base %s" % dx,
        rod(.023, length=.028, center=(sink_x+dx, -.11, .975), color=chrome))
    add("tap lever %s" % dx,
        rod(.009, start=(sink_x+dx, -.11, .991),
            end=(sink_x+dx, -.16, 1.023), color=chrome))

realize(scene)

# Procedural finishes supply subtle grain without image textures.
def wood_material():
    m = bpy.data.materials.new("reddish brown vertical timber")
    m.use_nodes = True
    n = m.node_tree.nodes
    l = m.node_tree.links
    bs = n.get("Principled BSDF")
    bs.inputs["Roughness"].default_value = .34
    tex = n.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 1
    tex.inputs["Detail"].default_value = 3
    coord = n.new("ShaderNodeTexCoord")
    scale = n.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = (35, 35, 2)
    l.new(coord.outputs["Generated"], scale.inputs[0])
    l.new(scale.outputs[0], tex.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .18
    ramp.color_ramp.elements[0].color = (.075, .017, .008, 1)
    ramp.color_ramp.elements[1].position = .82
    ramp.color_ramp.elements[1].color = (.30, .092, .038, 1)
    l.new(tex.outputs["Fac"], ramp.inputs[0])
    l.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    return m

timber = wood_material()
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    for slot in obj.material_slots:
        mat = slot.material
        if not mat:
            continue
        rgb = mat.diffuse_color[:3]
        if sum(abs(rgb[i] - wood[i]) for i in range(3)) < .06:
            slot.material = timber
        else:
            mat.use_nodes = True
            bs = mat.node_tree.nodes.get("Principled BSDF")
            if not bs:
                continue
            if sum(abs(rgb[i] - chrome[i]) for i in range(3)) < .06:
                bs.inputs["Metallic"].default_value = .86
                bs.inputs["Roughness"].default_value = .24
            elif "daylight glass" in obj.name:
                bs.inputs["Base Color"].default_value = (.93, .95, .87, 1)
                bs.inputs["Emission Color"].default_value = (.93, .95, .86, 1)
                bs.inputs["Emission Strength"].default_value = .7
            elif "countertop" in obj.name:
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                noise = nodes.new("ShaderNodeTexNoise")
                noise.inputs["Scale"].default_value = 145
                noise.inputs["Detail"].default_value = 2
                ramp = nodes.new("ShaderNodeValToRGB")
                ramp.color_ramp.elements[0].color = (.44, .34, .23, 1)
                ramp.color_ramp.elements[1].color = (.78, .69, .54, 1)
                links.new(noise.outputs["Fac"], ramp.inputs[0])
                links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
                bs.inputs["Roughness"].default_value = .48

set_view((3.05, -4.05, 2.20), (.85, -.75, 1.35), lens=44, sensor=36)
area_emitter((1.7, -1.0, 3.5), power=240, size=3.0, target=(.7, -.6, .8),
             color=(1.0, .91, .79))
area_emitter((1.6, -.35, 2.2), power=105, size=1.3, target=(.4, -1.5, .7),
             color=(1.0, .98, .88))
area_emitter((3.2, -3.8, 2.8), power=110, size=3.0, target=(.3, -.5, 1.2))

world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.77, .79, .77, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .45
sc = bpy.context.scene
sc.render.resolution_x = 256
sc.render.resolution_y = 171
sc.render.resolution_percentage = 100
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.view_settings.exposure = 0
sc.view_settings.gamma = 1
