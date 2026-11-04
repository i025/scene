from sceneact import *
import bpy, math, random

random.seed(19)
scene = Scene(name="Classroom")
cream = (.79, .775, .69)
blue = (.018, .12, .32)
green = (.045, .145, .080)
steel = (.57, .59, .55)

scene.include("wall", box((14, .18, 6.5), center=(0, 1.43, 3.25), color=cream))
scene.include("blue_wall", box((14, .035, 1.51), center=(0, 1.315, .755), color=blue))
scene.include("floor", box((14, 13, .10), center=(0, -3, -.07), color=(.46, .29, .16)))
scene.include("skirting", box((14, .055, .065), center=(0, 1.275, .032), color=(.63, .48, .30)))

board = Asset("Large worn green chalkboard")
board.include("backing", box((5.74, .07, 1.94), center=(0, 1.23, 2.14), color=(.26, .29, .21)))
for i, x in enumerate((-1.4275, 1.4275)):
    board.include("green_panel_" + str(i), box((2.845, .025, 1.90), center=(x, 1.18, 2.14), color=green))
for z in (1.181, 3.099):
    board.include("horizontal_rim_" + str(z), box((5.73, .028, .019), center=(0, 1.153, z), color=(.37, .40, .29)))
for x in (-2.86, .005, 2.86):
    board.include("vertical_rim_" + str(x), box((.016, .028, 1.92), center=(x, 1.153, 2.14), color=(.32, .36, .25)))
scene.include("chalkboard", board)

marks = Asset("Chalk dust and eraser traces")
for i in range(112):
    x = random.uniform(.07, 2.81)
    low = random.uniform(1.20, 1.70)
    high = random.uniform(2.70, 3.08)
    c = random.choice([(.13, .23, .135), (.20, .29, .17), (.27, .34, .21), (.105, .20, .12)])
    pts = []
    for j in range(15):
        z = low + (high - low) * j / 14
        xx = x + .018 * math.sin(j * .65 + i) + .015 * math.sin(j * .21 + i * 2)
        pts.append((xx, 1.151, z))
    marks.include("vertical_wipe_%d" % i, sweep_tube(points=pts, radius=random.uniform(.002, .009), color=c))

for i in range(54):
    x = random.uniform(-2.8, -.12)
    z = random.uniform(1.22, 2.95)
    length = random.uniform(.12, .61)
    pts = [(x + .018 * math.sin(j * .8 + i), 1.149, min(z + length * j / 10, 3.065)) for j in range(11)]
    marks.include("left_drip_%d" % i, sweep_tube(points=pts, radius=random.uniform(.002, .006), color=(.26, .37, .24)))

for i in range(34):
    cx = random.uniform(-2.5, -.45)
    cz = random.uniform(2.30, 2.89)
    rx = random.uniform(.23, .67)
    rz = random.uniform(.07, .30)
    start = random.uniform(-1.1, 1.0)
    pts = []
    for j in range(23):
        a = start + j * .075
        xx = cx + rx * math.cos(a)
        zz = cz + rz * math.sin(a)
        if -2.80 < xx < -.04 and 1.22 < zz < 3.07:
            pts.append((xx, 1.145, zz))
    if len(pts) > 2:
        marks.include("curved_eraser_%d" % i, sweep_tube(
            points=pts, radius=random.uniform(.003, .012),
            color=random.choice([(.19, .29, .18), (.26, .35, .23), (.12, .23, .14)])))

for i in range(100):
    x = random.uniform(-2.80, 2.80)
    z = random.uniform(1.22, 3.06)
    if random.random() < .65:
        marks.include("chalk_speck_%d" % i, box(
            (random.uniform(.004, .018), .002, random.uniform(.006, .026)),
            center=(x, 1.139, z), color=(.46, .51, .33)))
scene.include("dust", marks)

notice = Asset("Wall notice")
notice.include("paper_back", box((1.025, .023, .80), center=(.22, 1.27, 3.77), color=(.65, .61, .49)))
notice.include("paper", box((1.00, .008, .775), center=(.22, 1.251, 3.775), color=(.83, .80, .71)))
for x in (-.265, .705):
    notice.include("border_v" + str(x), box((.006, .004, .74), center=(x, 1.244, 3.775), color=(.58, .49, .37)))
for z in (3.407, 4.143):
    notice.include("border_h" + str(z), box((.97, .004, .006), center=(.22, 1.244, z), color=(.58, .49, .37)))
notice.include("hanger_left", rod(.002, start=(-.275, 1.265, 4.17), end=(.22, 1.275, 4.57), color=(.48, .43, .32)))
notice.include("hanger_right", rod(.002, start=(.72, 1.265, 4.17), end=(.22, 1.275, 4.57), color=(.48, .43, .32)))
for col in range(3):
    cx = -.20 + col * .31
    for row in range(20):
        z = 4.08 - row * .030
        for k in range(random.randint(1, 3)):
            notice.include("print_%d_%d_%d" % (col, row, k), box(
                (random.uniform(.025, .065), .003, random.uniform(.002, .005)),
                center=(cx + k * .075, 1.237, z), color=(.40, .38, .33)))
notice.include("heading", box((.37, .003, .008), center=(.22, 1.236, 4.11), color=(.40, .35, .30)))
scene.include("notice", notice)
scene.include("wall_fixture", rod(.052, start=(-.49, 1.30, 3.98), end=(-.49, 1.24, 3.98), color=(.16, .13, .10)))
scene.include("fixture_glint", ball(.014, center=(-.50, 1.233, 3.995), color=(.55, .49, .36)))

def desk(name, x, y, width=2.65, depth=.70, height=.85, pale=False):
    a = Asset(name)
    topcolor = (.83, .60, .28) if not pale else (.79, .73, .60)
    a.include("top", fillet_box((width, depth, .065), radius=.025, center=(x, y, height), color=topcolor))
    a.include("front_edge", box(
        (width - .055, .023, .025),
        center=(x, y - depth / 2 - .002, height - .018),
        color=(.71, .43, .15) if not pale else (.65, .57, .43)))
    for i, xx in enumerate((x - width / 2 + .12, x + width / 2 - .12)):
        for j, yy in enumerate((y - depth / 2 + .10, y + depth / 2 - .10)):
            a.include("leg_%d_%d" % (i, j), rod(.022, start=(xx, yy, .03), end=(xx, yy, height - .04), color=steel))
        a.include("side_rail_%d" % i, rod(.016, start=(xx, y - depth / 2 + .10, .30), end=(xx, y + depth / 2 - .10, .30), color=steel))
        a.include("front_bracket_%d" % i, box((.055, .045, .15), center=(xx, y - depth / 2 + .09, height - .12), color=(.58, .56, .45)))
    a.include("under_rail", rod(.018, start=(x - width / 2 + .12, y + .17, height - .14),
                               end=(x + width / 2 - .12, y + .17, height - .14), color=(.42, .44, .39)))
    scene.include(name, a)

def chair(name, x, y, back_top=1.10, width=.65):
    a = Asset(name)
    a.include("seat", fillet_box((width, .48, .045), radius=.018, center=(x, y, .48), color=(.65, .34, .11)))
    back = box((width, .042, .26), center=(x, y + .20, back_top - .13), color=(.65, .35, .12))
    back.turn("Y", -3)
    a.include("wood_back", back)
    for i, xx in enumerate((x - width / 2 + .045, x + width / 2 - .045)):
        a.include("back_support_%d" % i, rod(.017, start=(xx, y + .22, .05), end=(xx, y + .22, back_top - .045), color=(.57, .59, .53)))
        a.include("front_leg_%d" % i, rod(.020, start=(xx, y - .19, .025), end=(xx, y - .19, .48), color=steel))
        a.include("side_join_%d" % i, rod(.014, start=(xx, y - .19, .25), end=(xx, y + .22, .25), color=steel))
    scene.include(name, a)

chair("Chair behind middle desk", -1.12, .72, 1.10, .64)
desk("Middle desk", -.69, -.10, 2.67, .72, .86)
desk("Foreground left desk", -.83, -1.52, 2.60, .72, .81)
chair("Foreground wooden chair", -1.28, -2.50, 1.045, .67)
desk("Foreground right desk", 2.53, -1.53, 2.03, .76, .80, True)
chair("Right foreground chair", 2.01, -2.47, 1.035, .69)

realize(scene)

mat = bpy.data.materials.new("Mottled green slate with erased chalk")
mat.use_nodes = True
n = mat.node_tree.nodes
l = mat.node_tree.links
bs = n.get("Principled BSDF")
bs.inputs["Roughness"].default_value = .83
tex = n.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value = 5
tex.inputs["Detail"].default_value = 4
coord = n.new("ShaderNodeTexCoord")
mapping = n.new("ShaderNodeVectorMath")
mapping.operation = "MULTIPLY"
mapping.inputs[1].default_value = (3, 3, .5)
l.new(coord.outputs["Generated"], mapping.inputs[0])
l.new(mapping.outputs[0], tex.inputs["Vector"])
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .16
ramp.color_ramp.elements[0].color = (.016, .063, .030, 1)
ramp.color_ramp.elements[1].position = .85
ramp.color_ramp.elements[1].color = (.115, .215, .112, 1)
l.new(tex.outputs["Fac"], ramp.inputs[0])
l.new(ramp.outputs["Color"], bs.inputs["Base Color"])
bump = n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .14
bump.inputs["Distance"].default_value = .012
l.new(tex.outputs["Fac"], bump.inputs["Height"])
l.new(bump.outputs["Normal"], bs.inputs["Normal"])

for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        for slot in obj.material_slots:
            if slot.material:
                c = slot.material.diffuse_color
                if all(abs(c[i] - green[i]) < .005 for i in range(3)):
                    slot.material = mat

set_view((0, -8.8, 2.65), (0, 1.30, 2.08), lens=50, sensor=36)
area_emitter((-3.8, -3.8, 5.4), power=1050, size=4.2, target=(0, 1.1, 1.7), color=(1, .94, .80))
area_emitter((2, -4, 4.4), power=160, size=5, target=(0, 1, 2), color=(.83, .89, 1))
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.65, .68, .66, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .35
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.render.resolution_x = 512
sc.render.resolution_y = 337
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.view_settings.exposure = .15
