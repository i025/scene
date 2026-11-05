from sceneact import *
import bpy
import math
import random

random.seed(19)
scene = Scene(name="Classroom")
cream = (.79, .775, .69)
blue = (.015, .105, .31)
green_left = (.045, .145, .080)
green_right = (.046, .146, .081)
metal = (.52, .55, .51)

scene.include("plaster wall", box((14, .18, 6.5),
    center=(0, 1.43, 3.25), color=cream))
scene.include("blue painted wall", box((14, .035, 1.51),
    center=(0, 1.315, .755), color=blue))
scene.include("floor", box((14, 13, .10),
    center=(0, -3, -.07), color=(.48, .30, .16)))
scene.include("baseboard", box((14, .055, .05),
    center=(0, 1.275, .025), color=(.66, .50, .31)))

board = Asset("Green chalkboard")
board.include("backing", box((5.74, .055, 1.94),
    center=(0, 1.23, 2.14), color=(.20, .25, .16)))
board.include("left slate", box((2.845, .025, 1.90),
    center=(-1.4275, 1.18, 2.14), color=green_left))
board.include("right slate", box((2.845, .025, 1.90),
    center=(1.4275, 1.18, 2.14), color=green_right))
for i, z in enumerate((1.181, 3.099)):
    board.include("horizontal edge %d" % i, box((5.73, .02, .012),
        center=(0, 1.156, z), color=(.30, .34, .23)))
for i, x in enumerate((-2.86, .005, 2.86)):
    board.include("vertical edge %d" % i, box((.012, .02, 1.92),
        center=(x, 1.156, 2.14), color=(.26, .31, .20)))
scene.include("board", board)

# Sparse flecks of chalk are separate small meshes.
flecks = Asset("Chalk remnants")
for i in range(28):
    x = random.uniform(-2.8, 2.8)
    z = random.uniform(1.22, 3.05)
    flecks.include(str(i), box(
        (random.uniform(.004, .013), .003, random.uniform(.006, .022)),
        center=(x, 1.148, z), color=(.43, .48, .30)))
scene.include("chalk remnants", flecks)

notice = Asset("Hanging classroom notice")
notice.include("back", box((1.025, .018, .80),
    center=(.22, 1.29, 3.77), color=(.67, .62, .51)))
notice.include("paper", box((1.00, .008, .775),
    center=(.22, 1.274, 3.775), color=(.831, .801, .711)))
for i, x in enumerate((-.265, .705)):
    notice.include("side %d" % i, box((.005, .004, .74),
        center=(x, 1.267, 3.775), color=(.63, .53, .40)))
for i, z in enumerate((3.407, 4.143)):
    notice.include("edge %d" % i, box((.97, .004, .005),
        center=(.22, 1.267, z), color=(.63, .53, .40)))
notice.include("left string", rod(.0015,
    start=(-.275, 1.29, 4.17), end=(.22, 1.29, 4.57),
    color=(.53, .48, .36)))
notice.include("right string", rod(.0015,
    start=(.72, 1.29, 4.17), end=(.22, 1.29, 4.57),
    color=(.53, .48, .36)))
for col in range(3):
    for row in range(13):
        notice.include("text %d %d" % (col, row), box(
            (random.uniform(.11, .22), .002, .003),
            center=(-.105 + col * .31, 1.263, 4.06 - row * .043),
            color=(.44, .41, .35)))
notice.include("heading", box((.37, .002, .007),
    center=(.22, 1.262, 4.11), color=(.39, .35, .29)))
scene.include("notice", notice)
scene.include("small wall fixture", rod(.052,
    start=(-.49, 1.32, 3.98), end=(-.49, 1.26, 3.98),
    color=(.14, .11, .08)))
scene.include("fixture highlight", ball(.012,
    center=(-.50, 1.248, 3.997), color=(.55, .48, .34)))

def desk(name, x, y, width, depth, height, pale=False):
    a = Asset(name)
    topcolor = (.86, .62, .29) if not pale else (.81, .75, .64)
    a.include("desktop", box((width, depth, .055),
        center=(x, y, height), color=topcolor))
    a.include("front edge", box((width, .022, .018),
        center=(x, y-depth/2-.002, height-.019),
        color=(.70, .44, .17) if not pale else (.66, .59, .47)))
    for i, xx in enumerate((x-width/2+.12, x+width/2-.12)):
        for j, yy in enumerate((y-depth/2+.09, y+depth/2-.09)):
            a.include("leg %d %d" % (i, j), box((.034, .034, height-.055),
                center=(xx, yy, (height-.055)/2), color=metal))
        a.include("side brace %d" % i, box((.025, depth-.18, .025),
            center=(xx, y, .30), color=metal))
        a.include("bracket %d" % i, box((.045, .04, .14),
            center=(xx, y-depth/2+.09, height-.10),
            color=(.55, .54, .44)))
    a.include("cross rail", box((width-.24, .03, .035),
        center=(x, y+.15, height-.14), color=(.39, .42, .37)))
    scene.include(name, a)

def chair(name, x, y, top, width):
    a = Asset(name)
    a.include("seat", box((width, .46, .035),
        center=(x, y, .47), color=(.67, .36, .12)))
    back = box((width, .035, .25),
        center=(x, y+.20, top-.125), color=(.69, .38, .13))
    back.turn("Y", -3)
    a.include("wooden back", back)
    for i, xx in enumerate((x-width/2+.045, x+width/2-.045)):
        a.include("rear support %d" % i, box((.025, .025, top-.055),
            center=(xx, y+.21, (top-.055)/2), color=metal))
        a.include("front leg %d" % i, box((.03, .03, .45),
            center=(xx, y-.18, .225), color=metal))
    scene.include(name, a)

chair("Chair behind desk", -1.12, .72, 1.10, .64)
desk("Middle desk", -.69, -.10, 2.67, .72, .86)
desk("Foreground left desk", -.83, -1.52, 2.60, .72, .81)
chair("Foreground left chair", -1.28, -2.50, 1.045, .67)
desk("Foreground right desk", 2.53, -1.53, 2.03, .76, .80, True)
chair("Foreground right chair", 2.01, -2.47, 1.035, .69)

realize(scene)

# Procedural slate and chalk dust avoid expensive stroke geometry.
def slate_material(name, right):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    bs.inputs["Roughness"].default_value = .90
    coord = nodes.new("ShaderNodeTexCoord")

    def noise(scale, detail, stretch):
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = stretch
        links.new(coord.outputs["Generated"], mapping.inputs[0])
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Detail"].default_value = detail
        tex.inputs["Roughness"].default_value = .72
        links.new(mapping.outputs[0], tex.inputs["Vector"])
        return tex

    broad = noise(5, 3, (3.7, 1, .13) if right else (1.4, 1, 1.6))
    fine = noise(7, 2, (16, 1, .17) if right else (13, 1, .45))
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = .60
    links.new(broad.outputs["Fac"], mix.inputs[1])
    links.new(fine.outputs["Fac"], mix.inputs[2])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .12
    ramp.color_ramp.elements[0].color = (.017, .065, .029, 1)
    ramp.color_ramp.elements[1].position = .69
    ramp.color_ramp.elements[1].color = (
        (.32, .36, .20, 1) if right else (.22, .32, .19, 1))
    middle = ramp.color_ramp.elements.new(.42)
    middle.color = (.075, .16, .075, 1)
    links.new(mix.outputs[0], ramp.inputs[0])
    links.new(ramp.outputs[0], bs.inputs["Base Color"])
    return mat

left_mat = slate_material("Left erased green slate", False)
right_mat = slate_material("Right vertically wiped green slate", True)

# A few broad, curved eraser marks are produced within the left material.
nodes = left_mat.node_tree.nodes
links = left_mat.node_tree.links
bs = nodes.get("Principled BSDF")
base_socket = bs.inputs["Base Color"]
previous = base_socket.links[0].from_socket
coord = nodes.new("ShaderNodeTexCoord")
for cx, cz, rx, rz in [
    (.67, .65, .24, .22), (.71, .73, .29, .17),
    (.57, .87, .35, .12), (.22, .83, .32, .095),
    (.72, .58, .21, .17)
]:
    subtract_node = nodes.new("ShaderNodeVectorMath")
    subtract_node.operation = "SUBTRACT"
    subtract_node.inputs[1].default_value = (cx, 0, cz)
    links.new(coord.outputs["Generated"], subtract_node.inputs[0])
    scale_node = nodes.new("ShaderNodeVectorMath")
    scale_node.operation = "MULTIPLY"
    scale_node.inputs[1].default_value = (1/rx, 0, 1/rz)
    links.new(subtract_node.outputs[0], scale_node.inputs[0])
    length_node = nodes.new("ShaderNodeVectorMath")
    length_node.operation = "LENGTH"
    links.new(scale_node.outputs[0], length_node.inputs[0])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    for pos, value in [(.0, 0), (.90, 0), (.97, .43), (1.02, .16), (1.07, 0)]:
        if pos == 0:
            el = ramp.color_ramp.elements[0]
        else:
            el = ramp.color_ramp.elements.new(pos)
        el.color = (value, value, value, 1)
    links.new(length_node.outputs["Value"], ramp.inputs[0])
    mix = nodes.new("ShaderNodeMixRGB")
    links.new(ramp.outputs[0], mix.inputs[0])
    links.new(previous, mix.inputs[1])
    mix.inputs[2].default_value = (.31, .40, .25, 1)
    previous = mix.outputs[0]
links.new(previous, base_socket)

for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        for slot in obj.material_slots:
            if slot.material:
                c = slot.material.diffuse_color
                if all(abs(c[i]-green_left[i]) < .0002 for i in range(3)):
                    slot.material = left_mat
                elif all(abs(c[i]-green_right[i]) < .0002 for i in range(3)):
                    slot.material = right_mat

set_view((0, -8.8, 2.65), (0, 1.30, 2.08), lens=50, sensor=36)
area_emitter((-3.8, -3.8, 5.4), power=1050, size=4.2,
    target=(0, 1.1, 1.7), color=(1, .95, .83))
area_emitter((2, -4, 4.4), power=160, size=5,
    target=(0, 1, 2), color=(.83, .89, 1))
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.65, .68, .66, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .35

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 24
sc.cycles.use_denoising = True
sc.render.resolution_x = 512
sc.render.resolution_y = 337
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.view_settings.exposure = .15
