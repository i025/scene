from sceneact import *
import bpy
import math
import random

# Reference estimates: chaise bounds (0.04,.24)-(.83,.93);
# wall/floor boundary around y=.52; foreground chair cropped at lower left.
CHAISE_LENGTH = 3.05
CHAISE_WIDTH = 1.10
SEAT_HEIGHT = .79
CAMERA_POSITION = (2.05, -6.0, 4.10)
CAMERA_TARGET = (.12, .12, 1.10)
CAMERA_LENS = 60

random.seed(8)
scene = Scene("French chaise longue")
wall = (.76, .73, .64)
trim = (.82, .79, .68)
green = (.31, .37, .30)
gold = (.61, .53, .35)
pale_gold = (.77, .69, .48)
fabric = (.84, .79, .69)

room = Asset("Paneled room")
room.include("floor", box((12, 12, .12), center=(0, 0, -.08),
                          color=(.23, .13, .08)))
room.include("back_wall", box((9, .16, 4.3),
                             center=(0, 1.18, 2.12), color=wall))
for i, (z, thickness, depth) in enumerate([
    (.12, .15, .12), (.24, .045, .07), (.36, .045, .065),
    (1.94, .075, .08), (2.04, .035, .06), (2.40, .055, .06),
    (2.72, .05, .065), (2.85, .035, .05)
]):
    room.include(
        f"horizontal_molding_{i}",
        box((8.7, depth, thickness), center=(0, 1.055, z), color=trim)
    )

for p, (left, right) in enumerate([
    (-3.0, -1.75), (-1.69, 2.10), (2.17, 3.40)
]):
    for layer in range(3):
        inset = layer * .025
        lo, hi = .45 + inset, 1.83 - inset
        a, b = left + inset, right - inset
        color = trim if layer != 1 else (.62, .59, .50)
        for j, x in enumerate((a, b)):
            room.include(
                f"panel_{p}_{layer}_vertical_{j}",
                box((.018, .035, hi-lo),
                    center=(x, 1.069-layer*.009, (hi+lo)/2), color=color)
            )
        for j, z in enumerate((lo, hi)):
            room.include(
                f"panel_{p}_{layer}_horizontal_{j}",
                box((b-a, .035, .018),
                    center=((a+b)/2, 1.069-layer*.009, z), color=color)
            )

for j, x in enumerate((-1.72, .64)):
    room.include(f"wall_joint_{j}",
                 box((.009, .006, 3.9), center=(x, 1.086, 2.02),
                     color=(.40, .38, .32)))

room.include("right_pilaster",
             box((.30, .34, 3.2), center=(2.62, .94, 1.58), color=trim))
room.include("right_wall_return",
             box((.9, .7, 3.3), center=(3.16, 1.38, 1.6),
                 color=(.71, .68, .58)))
scene.include("room", room)

floor = Asset("Parquet")
wood_colors = [
    (.23, .125, .075), (.28, .15, .09), (.21, .105, .063),
    (.31, .18, .105), (.255, .135, .077), (.26, .145, .09)
]
# Paired perpendicular boards form a repeating herringbone floor.
board_length = .60
board_width = .12
for row in range(-11, 12):
    for col in range(-11, 12):
        u = col * board_length + row * board_width
        v = row * board_length - col * board_width
        for k in range(2):
            if k == 0:
                a, b = u + board_length/2, v + board_width/2
                angle = 45
            else:
                a, b = u + board_length + board_width/2, v + board_length/2
                angle = 135
            x = (a-b) / math.sqrt(2)
            y = (a+b) / math.sqrt(2)
            if abs(x) > 5 or abs(y) > 5:
                continue
            plank = box((board_length-.006, board_width-.004, .018),
                        center=(x, y, -.008),
                        color=random.choice(wood_colors))
            plank.turn("z", angle)
            floor.include(f"board_{row}_{col}_{k}", plank)
scene.include("parquet", floor)

chaise = Asset("Chaise longue")
front_rail = [
    (-1.30, -.565, .66), (-1.03, -.57, .60),
    (-.70, -.575, .58), (-.25, -.578, .57),
    (.22, -.575, .56), (.69, -.57, .55),
    (1.15, -.55, .55), (1.43, -.43, .57)
]
chaise.include("front_green_apron",
               sweep_tube(points=front_rail, radius=.075, color=green))
for j, dz in enumerate((-.047, .045)):
    chaise.include(
        f"front_beading_{j}",
        sweep_tube(points=[(x, y-.015, z+dz) for x, y, z in front_rail],
                   radius=.012, color=pale_gold)
    )
chaise.include(
    "rear_rail",
    sweep_tube(points=[(-1.4, .48, .64), (-.7, .53, .61),
                       (.5, .53, .60), (1.42, .41, .60)],
               radius=.055, color=green)
)
chaise.include(
    "foot_end_rail",
    sweep_tube(points=[(1.43, -.45, .58), (1.52, -.20, .59),
                       (1.54, .15, .60), (1.43, .45, .61)],
               radius=.055, color=green)
)

for i, (x, y) in enumerate([
    (-1.14, -.49), (1.28, -.44), (-1.16, .43), (1.29, .41)
]):
    side = 1 if x > 0 else -1
    points = [
        (x, y, .63), (x+side*.045, y-.015, .48),
        (x-side*.035, y-.025, .29), (x-side*.015, y-.045, .12),
        (x+side*.045, y-.075, .075)
    ]
    chaise.include(f"cabriole_leg_{i}",
                   sweep_tube(points=points, radius=.040, color=green))
    chaise.include(
        f"leg_gold_{i}",
        sweep_tube(points=[(a, b-.035, c) for a, b, c in points],
                   radius=.008, color=pale_gold)
    )
    chaise.include(
        f"foot_{i}",
        fillet_box((.11, .09, .055), radius=.024,
                   center=(points[-1][0], points[-1][1], .056), color=gold)
    )

head_outline = [
    (-1.45, -.53, .69), (-1.54, -.55, 1.18),
    (-1.59, -.50, 1.63), (-1.54, -.40, 1.85),
    (-1.48, -.17, 1.91), (-1.43, .10, 1.87),
    (-1.38, .36, 1.71), (-1.33, .51, 1.62),
    (-1.25, .54, 1.48), (-1.18, .54, .80)
]
chaise.include("head_carved_frame",
               sweep_tube(points=head_outline, radius=.047, color=green))
chaise.include(
    "head_gilt_bead",
    sweep_tube(points=[(x+.023, y-.007, z) for x, y, z in head_outline],
               radius=.012, color=pale_gold)
)

arm_top = [
    (-1.57, -.53, 1.58), (-1.41, -.59, 1.40),
    (-1.13, -.60, 1.30), (-.91, -.59, 1.26),
    (-.77, -.58, 1.17), (-.68, -.575, .94), (-.53, -.57, .73)
]
arm_bottom = [
    (-1.45, -.54, .76), (-1.23, -.58, .66),
    (-.91, -.58, .61), (-.60, -.57, .61), (-.53, -.57, .73)
]
chaise.include("near_arm_frame",
               sweep_tube(points=arm_top, radius=.047, color=green))
chaise.include("near_arm_lower",
               sweep_tube(points=arm_bottom, radius=.04, color=green))
for j, path in enumerate((arm_top, arm_bottom)):
    chaise.include(
        f"arm_gold_{j}",
        sweep_tube(points=[(x, y-.038, z+.004) for x, y, z in path],
                   radius=.012, color=pale_gold)
    )

far_arm = [
    (-1.40, .49, 1.72), (-1.18, .55, 1.52),
    (-.88, .56, 1.41), (-.65, .55, 1.40),
    (-.61, .55, 1.18), (-.48, .54, .91)
]
chaise.include("far_arm",
               sweep_tube(points=far_arm, radius=.04, color=green))
chaise.include(
    "far_arm_gold",
    sweep_tube(points=[(x, y-.02, z+.025) for x, y, z in far_arm],
               radius=.011, color=pale_gold)
)
chaise.include(
    "far_arm_upholstery",
    fillet_box((.65, .075, .38), radius=.035,
               center=(-.98, .52, 1.18), color=fabric)
)

# Restrained carved ornaments at the apron center and head crest.
for group, (cx, cy, cz, scale) in enumerate([
    (.22, -.657, .55, .15), (-1.49, -.38, 1.86, .10)
]):
    for sign in (-1, 1):
        points = []
        for k in range(30):
            angle = k/29 * 2*math.pi
            radius = scale * (1-.78*k/29)
            points.append((
                cx+sign*(.025+radius*math.cos(angle)),
                cy-.006*math.sin(angle),
                cz+.55*radius*math.sin(angle)
            ))
        chaise.include(f"scroll_{group}_{sign}",
                       sweep_tube(points=points, radius=.009, color=pale_gold))
scene.include("chaise", chaise)

pillow = Asset("Loose cream pillow")
pillow_body = fillet_box((.30, .80, .74), radius=.12,
                         center=(-1.12, -.08, 1.35),
                         color=(.91, .84, .70))
pillow_body.turn("y", -18)
pillow_body.turn("x", -7)
pillow_body.turn("z", -30)
pillow.include("pillow_body", pillow_body)
scene.include("pillow", pillow)

label = Asset("Seat label")
card = box((.19, .095, .008), center=(.72, .13, .969),
           color=(.055, .24, .19))
card.turn("z", 80)
label.include("green_card", card)
for i in range(4):
    line = box((.050, .0025, .001),
               center=(.72, .105+i*.016, .974),
               color=(.72, .78, .64))
    line.turn("z", -10)
    label.include(f"printed_line_{i}", line)
scene.include("label", label)

curtain = Asset("Curtains")
curtain.include(
    "bright_window",
    box((.10, 1.3, 3.3), center=(-2.13, .18, 1.7),
        color=(.96, .94, .84))
)
for i in range(13):
    y = -.65+i*.085
    x = -2.08+.035*math.sin(i*1.8)
    curtain.include(
        f"ivory_fold_{i}",
        rod(radius=.060, start=(x, y, .10), end=(x-.08, y, 3.2),
            color=(.83+.035*(i%3), .80+.035*(i%3), .70+.04*(i%3)))
    )
for i in range(5):
    curtain.include(
        f"gold_edge_{i}",
        rod(radius=.025,
            start=(-1.98+i*.024, -.69, .03),
            end=(-2.13+i*.026, -.69, 3.2),
            color=(.52+i*.035, .41+i*.035, .28+i*.03))
    )
scene.include("curtains", curtain)

chair = Asset("Foreground cane chair")
chair.include(
    "seat_frame",
    fillet_box((.84, .78, .10), radius=.045,
               center=(-1.53, -1.90, .48), color=green)
)
chair.include(
    "cane_base",
    box((.72, .66, .018), center=(-1.53, -1.90, .542),
        color=(.48, .32, .18))
)
for i in range(30):
    x = -1.87+i*.024
    chair.include(
        f"cane_x_{i}",
        rod(radius=.004, start=(x, -2.20, .556), end=(x, -1.60, .556),
            color=(.69, .52, .31))
    )
for i in range(27):
    y = -2.21+i*.024
    chair.include(
        f"cane_y_{i}",
        rod(radius=.004, start=(-1.87, y, .558), end=(-1.19, y, .558),
            color=(.70, .53, .33))
    )
for i, y in enumerate((-2.24, -1.56)):
    chair.include(
        f"seat_gilt_{i}",
        rod(radius=.012, start=(-1.93, y, .545), end=(-1.13, y, .545),
            color=pale_gold)
    )
scene.include("foreground_chair", chair)

realize(scene)

def textile(name, base, patterned=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*base, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*base, 1)
    shader.inputs["Roughness"].default_value = .91

    coordinates = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 155
    noise.inputs["Detail"].default_value = 2
    links.new(coordinates.outputs["Generated"], noise.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .13
    bump.inputs["Distance"].default_value = .012
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])

    if patterned:
        wave = nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "Y"
        wave.inputs["Scale"].default_value = 13
        wave.inputs["Distortion"].default_value = .15
        links.new(coordinates.outputs["Generated"], wave.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        colors = [
            (0, base), (.73, base), (.79, (.67, .49, .46)),
            (.83, base), (.92, base), (.955, (.75, .60, .53)),
            (1, base)
        ]
        ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
        for index, (position, color) in enumerate(colors):
            element = (ramp.color_ramp.elements[0] if index == 0
                       else ramp.color_ramp.elements.new(position))
            element.position = position
            element.color = (*color, 1)
        links.new(wave.outputs["Color"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    return mat

cloth = textile("Woven ivory and faded rose stripes", fabric, True)
plain = textile("Cream pillow textile", (.89, .83, .70))

# Target SceneAct members through their ancestor markers.
for ob in list(bpy.data.objects):
    if ob.type != "MESH":
        continue
    ancestor = ob
    ancestry = []
    while ancestor is not None:
        ancestry.append(ancestor.name.lower())
        ancestor = ancestor.parent
    if any("pillow" in name for name in ancestry):
        ob.data.materials.clear()
        ob.data.materials.append(plain)
    elif any("far_arm_upholstery" in name for name in ancestry):
        ob.data.materials.clear()
        ob.data.materials.append(cloth)

upholstery_group = bpy.data.objects.new("Tailored chaise upholstery", None)
bpy.context.collection.objects.link(upholstery_group)
chaise_marker = next(
    (ob for ob in bpy.data.objects
     if ob.type == "EMPTY" and ob.name.lower() == "chaise"), None
)
if chaise_marker is not None:
    upholstery_group.parent = chaise_marker
    upholstery_group.matrix_parent_inverse = chaise_marker.matrix_world.inverted()

def mesh_object(name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    ob.parent = upholstery_group
    ob.matrix_parent_inverse = upholstery_group.matrix_world.inverted()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return ob

# Broad, gently domed mattress with rounded corners and a low vertical edge.
vertices = []
faces = []
segments = 96
rings = 32
for j in range(rings+1):
    latitude = -math.pi/2+math.pi*j/rings
    radial = max(0, math.cos(latitude))**.36
    vertical = math.copysign(abs(math.sin(latitude))**.65,
                             math.sin(latitude))
    for i in range(segments):
        angle = 2*math.pi*i/segments
        x = math.copysign(abs(math.cos(angle))**.47, math.cos(angle))
        y = math.copysign(abs(math.sin(angle))**.63, math.sin(angle))
        vertices.append((
            .015 + (CHAISE_LENGTH/2-.035)*radial*x,
            (CHAISE_WIDTH/2+.002)*radial*y,
            SEAT_HEIGHT+.165*vertical
        ))
for j in range(rings):
    for i in range(segments):
        a = j*segments+i
        b = j*segments+(i+1)%segments
        faces.append((a, b, b+segments, a+segments))
mesh_object("Continuous upholstered mattress", vertices, faces, cloth)

head_vertices = [
    (-1.41, -.49, .79), (-1.48, -.50, 1.20),
    (-1.51, -.46, 1.61), (-1.47, -.37, 1.79),
    (-1.41, -.16, 1.85), (-1.36, .10, 1.81),
    (-1.31, .34, 1.66), (-1.26, .46, 1.56),
    (-1.19, .48, .80), (-1.29, -.01, 1.31)
]
head = mesh_object(
    "Head upholstered panel", head_vertices,
    [(i, (i+1)%9, 9) for i in range(9)], cloth
)
solid = head.modifiers.new("Head padding thickness", "SOLIDIFY")
solid.thickness = .055

side_vertices = [
    (-1.51, -.548, 1.51), (-1.37, -.56, 1.36),
    (-1.11, -.565, 1.26), (-.92, -.56, 1.22),
    (-.81, -.56, 1.13), (-.73, -.56, .92),
    (-.57, -.55, .72), (-.64, -.55, .66),
    (-.93, -.55, .66), (-1.22, -.55, .71),
    (-1.42, -.54, .81), (-1.23, -.58, 1.00)
]
side = mesh_object(
    "Near upholstered curved side", side_vertices,
    [(i, (i+1)%11, 11) for i in range(11)], cloth
)
solid = side.modifiers.new("Side padding thickness", "SOLIDIFY")
solid.thickness = .045

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((-3, -1, 3.3), power=650, size=3,
             target=(0, 0, .65), color=(1, .93, .82))
area_emitter((1, -3, 3.8), power=160, size=4,
             target=(0, 0, 1), color=(.87, .92, 1))

blender_scene = bpy.context.scene
if blender_scene.world is None:
    blender_scene.world = bpy.data.worlds.new("World")
blender_scene.world.use_nodes = True
background = blender_scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (.73, .76, .79, 1)
background.inputs["Strength"].default_value = .25
blender_scene.view_settings.view_transform = "AgX"
