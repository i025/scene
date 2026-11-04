from sceneact import *
import bpy
import math
import random

# Estimated image anchors (upper-left origin):
# main bunk posts (.28,.29)-(.28,.90), (.40,.33)-(.40,.83);
# wardrobe (.54,.35)-(.66,.68); fireplace (.68,.39)-(.90,.69).
# Camera is near the right-hand doorway, looking diagonally toward the back wall.
CAMERA = (2.65, -4.6, 1.65)
TARGET = (-0.25, 3.25, 1.43)
LENS = 26
ROOM_WIDTH = 6.5
ROOM_DEPTH = 8.4
ROOM_HEIGHT = 3.05
BACK_Y = 4.65
LIGHT_POWER = 1150

scene = Scene("Old dormitory")
random.seed(17)
cream = (.64, .65, .42)
wood = (.24, .13, .055)
iron = (.075, .095, .092)
linen = (.84, .86, .83)
stone = (.40, .38, .29)

def add_box(parent, key, size, center, color):
    return parent.include(key, box(size=size, center=center, color=color))

def add_rod(parent, key, a, b, radius=.022, color=iron):
    return parent.include(key, rod(radius=radius, start=a, end=b, color=color))

# Broad, individually editable floorboards.
floor = Asset("Worn oak floor")
for i in range(25):
    x = -3.25 + (i + .5) * .26
    for j in range(4):
        y = -3.75 + (j + .5) * 2.12
        shade = random.uniform(.78, 1.18)
        add_box(floor, f"board_{i}_{j}", (.255, 2.112, .085),
                (x, y, -.044), tuple(v * shade for v in (.30, .185, .093)))
scene.include("floorboards", floor)

architecture = Asset("Plastered room")
add_box(architecture, "back_wall", (6.7, .18, ROOM_HEIGHT),
        (0, BACK_Y + .09, ROOM_HEIGHT / 2), cream)
add_box(architecture, "left_wall", (.16, 8.6, ROOM_HEIGHT),
        (-3.33, .45, ROOM_HEIGHT / 2), (.68, .68, .49))
add_box(architecture, "ceiling", (6.7, 8.7, .14),
        (0, .4, ROOM_HEIGHT + .07), (.57, .59, .43))
scene.include("architecture", architecture)

timber = Asset("Exposed dark structural timbers")
for j, y in enumerate((-3.3, -.6, 2.0, 4.48)):
    add_box(timber, f"wall_upright_{j}", (.17, .16, 3.02),
            (-3.225, y, 1.51), wood)
add_box(timber, "wall_mid_rail", (.14, 8.6, .17),
        (-3.225, .45, 1.96), wood)
add_box(timber, "wall_top_rail", (.16, 8.6, .20),
        (-3.225, .45, 2.94), (.16, .09, .035))
for j, y in enumerate((.2, 3.9)):
    add_box(timber, f"ceiling_beam_{j}", (6.6, .23, .24),
            (0, y, 2.98), (.13, .075, .026))
scene.include("timbers", timber)

def bunk(name, cx, cy, length=2.18, width=1.0):
    bed = Asset(name)
    xmin, xmax = cx - length/2, cx + length/2
    ymin, ymax = cy - width/2, cy + width/2
    for i, x in enumerate((xmin, xmax)):
        for j, y in enumerate((ymin, ymax)):
            add_rod(bed, f"post_{i}_{j}", (x,y,.035), (x,y,2.10), .027)
            add_box(bed, f"foot_{i}_{j}", (.095,.085,.027), (x,y,.025), iron)
            bed.include(f"cap_{i}_{j}", ball(radius=.031, center=(x,y,2.10), color=iron))
    for level, z in enumerate((.46, 1.57)):
        add_box(bed, f"deck_{level}", (length+.015,width,.07), (cx,cy,z), iron)
        # Radius is below half of the thinnest dimension.
        bed.include(f"mattress_{level}", fillet_box(
            size=(length-.065,width-.055,.155), radius=.055,
            center=(cx,cy,z+.11), color=linen))
        add_box(bed, f"sheet_edge_{level}", (length-.10,.045,.13),
                (cx,ymin+.008,z+.12), (.75,.80,.84))
        pillow = fillet_box(size=(.46,.65,.17), radius=.075,
                            center=(xmin+.29,cy,z+.255), color=(.91,.91,.85))
        bed.include(f"pillow_{level}", pillow)
        for j, y in enumerate((ymin, ymax)):
            add_rod(bed, f"long_frame_{level}_{j}",
                    (xmin,y,z), (xmax,y,z), .025)
        # End rails emphasize the visible metal footboards.
        for side, x in enumerate((xmin,xmax)):
            for k, dz in enumerate((.23,.39)):
                add_rod(bed, f"endrail_{level}_{side}_{k}",
                        (x,ymin,z+dz), (x,ymax,z+dz), .018)
            for k in range(3):
                y = ymin + width*(k+1)/4
                add_rod(bed, f"end_spindle_{level}_{side}_{k}",
                        (x,y,z+.04), (x,y,z+.40), .012)
    # Upper safety rail on the long exposed side.
    for j,z in enumerate((1.91,2.045)):
        add_rod(bed, f"upper_guard_{j}", (xmin,ymin,z), (xmax,ymin,z), .017)
    # Narrow ladder at the exposed end.
    for j,y in enumerate((cy-.30,cy+.30)):
        add_rod(bed, f"ladder_side_{j}", (xmax+.035,y,.08),
                (xmax+.035,y,1.96), .021)
    for j,z in enumerate((.37,.68,.99,1.30,1.61)):
        add_rod(bed, f"ladder_rung_{j}", (xmax+.035,cy-.30,z),
                (xmax+.035,cy+.30,z), .018)
    return bed

scene.include("near_left_bunk", bunk("Near left bunk", -2.00, -.05, 2.27, 1.02))
scene.include("rear_left_bunk", bunk("Rear left bunk", -2.00, 2.45, 2.27, 1.02))

# The close right bunk is deliberately cropped by the camera.
scene.include("foreground_right_bunk",
              bunk("Foreground right bunk", 3.50, -2.15, 2.14, 1.04))

cabinet = Asset("Oak bedside wardrobe")
cx, cy = -.43, 4.33
add_box(cabinet, "back", (.94,.055,1.72), (cx,cy+.22,.94), (.25,.13,.045))
for j,x in enumerate((cx-.46,cx+.46)):
    add_box(cabinet, f"side_{j}", (.065,.49,1.74), (x,cy,.94), (.34,.185,.065))
    add_box(cabinet, f"foot_{j}", (.12,.38,.12), (x,cy,.075), (.22,.11,.035))
add_box(cabinet, "cornice", (1.08,.60,.075), (cx,cy,1.84), (.32,.18,.067))
add_box(cabinet, "cornice_lip", (1.12,.62,.032), (cx,cy,1.89), (.39,.23,.085))
add_box(cabinet, "base", (1.0,.55,.09), (cx,cy,.15), (.30,.15,.045))
add_box(cabinet, "middle_shelf", (.87,.49,.055), (cx,cy,.80), (.34,.19,.075))
# Left door; the right bay is open and dark.
add_box(cabinet, "left_door", (.43,.055,1.56), (cx-.225,cy-.27,.98), (.40,.235,.085))
for j,z in enumerate((.55,1.37)):
    add_box(cabinet, f"door_panel_{j}", (.32,.025,.59),
            (cx-.225,cy-.305,z), (.34,.18,.054))
add_rod(cabinet, "door_handle", (cx-.065,cy-.325,.95),
        (cx-.065,cy-.325,1.035), .012, (.13,.10,.045))
add_rod(cabinet, "hanging_bar", (cx+.04,cy,1.71),
        (cx+.40,cy,1.71), .012)
for j in range(3):
    x = cx+.11+j*.095
    add_rod(cabinet, f"hanger_left_{j}", (x,cy,1.65),(x-.06,cy-.01,1.55),.008)
    add_rod(cabinet, f"hanger_right_{j}", (x-.06,cy-.01,1.55),(x+.06,cy-.01,1.55),.008)
scene.include("wardrobe", cabinet)

# Fireplace: a deep black recess with soot-dark brickwork and heavy stone surround.
fire = Asset("Stone fireplace")
fx = 1.68
add_box(fire, "recess", (1.52,.035,1.24), (fx,4.535,.68), (.055,.047,.034))
for row in range(8):
    for col in range(6):
        x = fx-.68 + col*.255 + (.10 if row%2 else 0)
        if x < fx+.73:
            c = random.uniform(.09,.19)
            add_box(fire, f"brick_{row}_{col}", (.238,.055,.125),
                    (x,4.49,.16+row*.14), (c,c*.85,c*.65))
for j,x in enumerate((fx-.91,fx+.91)):
    add_box(fire, f"stone_pier_{j}", (.29,.34,1.32),
            (x,4.37,.70), stone)
    for k in range(3):
        add_box(fire, f"pier_joint_{j}_{k}", (.295,.345,.012),
                (x,4.37,.32+k*.39), (.28,.27,.21))
add_box(fire, "stone_lintel", (2.10,.38,.30), (fx,4.34,1.49), (.47,.45,.35))
add_box(fire, "mantel_edge", (2.20,.43,.065), (fx,4.31,1.66), (.43,.42,.32))
add_box(fire, "inner_top", (1.53,.15,.13), (fx,4.33,1.28), (.31,.30,.23))
add_box(fire, "hearth", (2.15,.78,.065), (fx,4.14,.033), (.26,.25,.19))
for j in range(4):
    add_box(fire, f"hearth_seam_{j}", (.012,.77,.003),
            (fx-.80+j*.54,4.14,.068), (.12,.12,.09))
scene.include("fireplace", fire)

radiator = Asset("Small pale radiator")
for j in range(8):
    x = 2.10+j*.035
    add_rod(radiator, f"rib_{j}", (x,4.02,.09), (x-.09,4.12,.58),
            .014, (.66,.70,.65))
add_rod(radiator, "top_pipe", (2.00,4.12,.58),(2.28,4.12,.58),.016,(.65,.68,.62))
add_rod(radiator, "bottom_pipe", (2.10,4.02,.09),(2.38,4.02,.09),.015,(.65,.68,.62))
scene.include("radiator", radiator)

bin_asset = Asset("Black hearth bin")
add_rod(bin_asset, "body", (2.73,4.03,.02),(2.73,4.03,.28),.10,(.055,.060,.052))
scene.include("hearth_bin", bin_asset)

clock = Asset("Small wall clock")
add_rod(clock, "rim", (-.48,4.52,2.27),(-.48,4.58,2.27),.125,(.43,.49,.42))
add_rod(clock, "face", (-.48,4.505,2.27),(-.48,4.515,2.27),.109,(.61,.67,.58))
add_rod(clock, "hand_one", (-.48,4.492,2.27),(-.48,4.492,2.335),.005,(.25,.28,.24))
add_rod(clock, "hand_two", (-.48,4.49,2.27),(-.435,4.49,2.25),.004,(.25,.28,.24))
scene.include("clock", clock)

# Small wall lamps above the beds.
for j,y in enumerate((.1,2.55)):
    lamp = Asset(f"Wall lamp {j}")
    add_box(lamp, "mount", (.07,.14,.22), (-3.16,y,2.25), (.16,.19,.16))
    lamp.include("shade", fillet_box(size=(.16,.16,.19), radius=.035,
                                    center=(-3.08,y,2.27), color=(.27,.32,.26)))
    add_box(lamp, "glass", (.025,.105,.09), (-2.988,y,2.26), (.72,.74,.60))
    scene.include(f"wall_lamp_{j}", lamp)

# All primitive sizes are positive; fillets fit the thinnest dimension.
# Repeated children have indexed keys. Materials are edited via group descendants.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient world")
sc.world.use_nodes = True
sc.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (.55,.60,.48,1)
sc.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = .32

def descendants(obj):
    if obj.type == 'MESH':
        yield obj
    for child in obj.children:
        yield from descendants(child)

def texture_group(group_name, style):
    group = bpy.data.objects.get(group_name)
    if group is None:
        return
    for obj in descendants(group):
        for slot in obj.material_slots:
            if not slot.material:
                continue
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bsdf = nodes.get("Principled BSDF")
            bsdf.inputs["Roughness"].default_value = .78
            base = tuple(bsdf.inputs["Base Color"].default_value)
            tex = nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value = 5 if style == "wood" else 15
            tex.inputs["Detail"].default_value = 3
            coord = nodes.new("ShaderNodeTexCoord")
            mapping = nodes.new("ShaderNodeVectorMath")
            mapping.operation = 'MULTIPLY'
            mapping.inputs[1].default_value = (26,1.4,5) if style == "wood" else (1,1,1)
            links.new(coord.outputs["Generated"], mapping.inputs[0])
            links.new(mapping.outputs[0], tex.inputs["Vector"])
            ramp = nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = .17
            ramp.color_ramp.elements[0].color = tuple(v*.55 for v in base[:3])+(1,)
            ramp.color_ramp.elements[1].position = .83
            ramp.color_ramp.elements[1].color = tuple(min(v*1.3,1) for v in base[:3])+(1,)
            links.new(tex.outputs["Fac"],ramp.inputs[0])
            links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = .24
            bump.inputs["Distance"].default_value = .018 if style == "wood" else .035
            links.new(tex.outputs["Fac"],bump.inputs["Height"])
            links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])

texture_group("floorboards", "wood")
texture_group("timbers", "wood")
texture_group("wardrobe", "wood")
texture_group("architecture", "plaster")
texture_group("fireplace", "stone")

for group_name in ("near_left_bunk","rear_left_bunk","foreground_right_bunk"):
    group = bpy.data.objects.get(group_name)
    if group:
        for obj in descendants(group):
            for slot in obj.material_slots:
                if slot.material:
                    mat = slot.material
                    mat.use_nodes = True
                    bs = mat.node_tree.nodes.get("Principled BSDF")
                    color = bs.inputs["Base Color"].default_value
                    if max(color[:3]) < .2:
                        bs.inputs["Metallic"].default_value = .65
                        bs.inputs["Roughness"].default_value = .30

set_view(CAMERA, TARGET, lens=LENS, sensor=36)
area_emitter(position=(-2.2,-3.2,2.35), power=LIGHT_POWER, size=3.4,
             target=(-.7,1.5,.7), color=(.88,.94,1.0))
area_emitter(position=(1.6,1.0,2.7), power=140, size=3.0,
             target=(.3,4.4,1.2), color=(1,.88,.65))

sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x = 512
sc.render.resolution_y = 341
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .25
