from sceneact import *
import bpy
import random

# Review of step 2 against the photograph:
# 1. Back furniture remains left and low, while the near bunk's main post is close.
#    Move camera right and turn left for parallax; lower target to raise the scene.
# 2. The cropped right bunk disappeared. Reposition it using the new camera and
#    raise its upper silhouette so its nearest post crosses the top image edge.
# 3. Floor and ceiling remain too light. Darken oak and reduce ceiling reflectance.
# Estimated anchors: near post (.28,.28)-(.28,.90), wardrobe (.54,.35)-(.66,.68),
# fireplace (.68,.40)-(.90,.69), cropped foreground post x=.94.
CAMERA = (3.30, -4.60, 1.65)
TARGET = (-1.80, 3.25, 1.12)
LENS = 34
BACK_Y = 4.65
ROOM_HEIGHT = 3.05
LIGHT_POWER = 760
NEAR_BUNK_CENTER = (-1.72, -.05)
REAR_BUNK_CENTER = (-2.0, 2.45)
FOREGROUND_BUNK_CENTER = (3.87, -.95)

scene = Scene("Old dormitory")
random.seed(17)
cream = (.61, .63, .35)
wood = (.18, .085, .028)
iron = (.065, .082, .080)
linen = (.86, .88, .86)
stone = (.37, .36, .29)

def B(parent, key, size, center, color):
    return parent.include(key, box(size=size, center=center, color=color))

def R(parent, key, a, b, r=.022, c=iron):
    return parent.include(key, rod(radius=r, start=a, end=b, color=c))

floor = Asset("Worn oak floor")
for i in range(25):
    x = -3.25 + (i + .5) * .26
    for j in range(4):
        y = -3.75 + (j + .5) * 2.12
        shade = random.uniform(.72, 1.20)
        B(floor, f"board_{i}_{j}", (.255, 2.112, .085), (x, y, -.044),
          tuple(v * shade for v in (.145, .075, .030)))
scene.include("floorboards", floor)

architecture = Asset("Plastered room")
B(architecture, "back_wall", (6.7, .18, ROOM_HEIGHT),
  (0, BACK_Y + .09, ROOM_HEIGHT / 2), cream)
B(architecture, "left_wall", (.16, 8.6, ROOM_HEIGHT),
  (-3.33, .45, ROOM_HEIGHT / 2), (.66, .66, .44))
B(architecture, "ceiling", (6.7, 8.7, .14),
  (0, .4, ROOM_HEIGHT + .07), (.43, .46, .29))
scene.include("architecture", architecture)

timber = Asset("Exposed structural timbers")
for j, y in enumerate((-3.3, -.6, 2.0, 4.48)):
    B(timber, f"upright_{j}", (.17, .16, 3.02), (-3.225, y, 1.51), wood)
B(timber, "midrail", (.14, 8.6, .17), (-3.225, .45, 1.96), wood)
B(timber, "toprail", (.16, 8.6, .20), (-3.225, .45, 2.94), (.10, .047, .016))
for j, y in enumerate((.2, 3.9)):
    B(timber, f"beam_{j}", (6.6, .23, .24), (0, y, 2.98), (.09, .042, .014))
scene.include("timbers", timber)

def bunk(name, cx, cy, length=2.27, width=1.02):
    bed = Asset(name)
    xmin, xmax = cx - length/2, cx + length/2
    ymin, ymax = cy - width/2, cy + width/2
    for i, x in enumerate((xmin, xmax)):
        for j, y in enumerate((ymin, ymax)):
            R(bed, f"post_{i}_{j}", (x, y, .035), (x, y, 2.10), .027)
            B(bed, f"foot_{i}_{j}", (.095, .085, .027), (x, y, .025), iron)
            bed.include(f"cap_{i}_{j}",
                        ball(radius=.031, center=(x, y, 2.10), color=iron))
    for level, z in enumerate((.46, 1.57)):
        B(bed, f"deck_{level}", (length + .015, width, .07), (cx, cy, z), iron)
        bed.include(f"mattress_{level}",
                    fillet_box(size=(length-.065, width-.055, .155),
                               radius=.055, center=(cx, cy, z+.11), color=linen))
        B(bed, f"sheet_edge_{level}", (length-.10, .045, .13),
          (cx, ymin+.008, z+.12), (.74, .80, .86))
        bed.include(f"pillow_{level}",
                    fillet_box(size=(.46, .65, .17), radius=.075,
                               center=(xmin+.29, cy, z+.255),
                               color=(.93, .93, .88)))
        for j, y in enumerate((ymin, ymax)):
            R(bed, f"longrail_{level}_{j}", (xmin, y, z), (xmax, y, z), .025)
        for side, x in enumerate((xmin, xmax)):
            for k, dz in enumerate((.23, .39)):
                R(bed, f"endrail_{level}_{side}_{k}",
                  (x, ymin, z+dz), (x, ymax, z+dz), .018)
            for k in range(3):
                y = ymin + width*(k+1)/4
                R(bed, f"spindle_{level}_{side}_{k}",
                  (x, y, z+.04), (x, y, z+.40), .012)
    for j, z in enumerate((1.91, 2.045)):
        R(bed, f"guard_{j}", (xmin, ymin, z), (xmax, ymin, z), .017)
    for j, y in enumerate((cy-.30, cy+.30)):
        R(bed, f"ladder_side_{j}",
          (xmax+.035, y, .08), (xmax+.035, y, 1.96), .021)
    for j, z in enumerate((.37, .68, .99, 1.30, 1.61)):
        R(bed, f"rung_{j}",
          (xmax+.035, cy-.30, z), (xmax+.035, cy+.30, z), .018)
    return bed

scene.include("near_left_bunk", bunk("Near left bunk", *NEAR_BUNK_CENTER))
scene.include("rear_left_bunk", bunk("Rear left bunk", *REAR_BUNK_CENTER))
foreground = bunk("Foreground right bunk", *FOREGROUND_BUNK_CENTER, 2.14, 1.04)
foreground.resize((1, 1, 1.25), pivot=(0, 0, 0))
scene.include("foreground_right_bunk", foreground)

cabinet = Asset("Oak wardrobe")
cx, cy = -.43, 4.33
B(cabinet, "back", (.94, .055, 1.72), (cx, cy+.22, .94), (.24, .12, .038))
for j, x in enumerate((cx-.46, cx+.46)):
    B(cabinet, f"side_{j}", (.065, .49, 1.74), (x, cy, .94), (.34, .185, .065))
    B(cabinet, f"foot_{j}", (.12, .38, .12), (x, cy, .075), (.22, .11, .035))
B(cabinet, "cornice", (1.08, .60, .075), (cx, cy, 1.84), (.32, .18, .067))
B(cabinet, "cornice_lip", (1.12, .62, .032), (cx, cy, 1.89), (.39, .23, .085))
B(cabinet, "base", (1.0, .55, .09), (cx, cy, .15), (.30, .15, .045))
B(cabinet, "middle_shelf", (.87, .49, .055), (cx, cy, .80), (.34, .19, .075))
B(cabinet, "left_door", (.43, .055, 1.56),
  (cx-.225, cy-.27, .98), (.40, .235, .085))
for j, z in enumerate((.55, 1.37)):
    B(cabinet, f"panel_{j}", (.32, .025, .59),
      (cx-.225, cy-.305, z), (.34, .18, .054))
R(cabinet, "handle", (cx-.065, cy-.325, .95),
  (cx-.065, cy-.325, 1.035), .012, (.13, .10, .045))
R(cabinet, "hanging_bar", (cx+.04, cy, 1.71), (cx+.40, cy, 1.71), .012)
for j in range(3):
    x = cx+.11+j*.095
    R(cabinet, f"hanger_a_{j}", (x, cy, 1.65), (x-.06, cy-.01, 1.55), .008)
    R(cabinet, f"hanger_b_{j}", (x-.06, cy-.01, 1.55),
      (x+.06, cy-.01, 1.55), .008)
scene.include("wardrobe", cabinet)

fire = Asset("Stone fireplace")
fx = 1.68
B(fire, "recess", (1.52, .035, 1.24), (fx, 4.535, .68), (.045, .037, .026))
for row in range(8):
    for col in range(6):
        x = fx-.68+col*.255+(.10 if row % 2 else 0)
        if x < fx+.73:
            c = random.uniform(.065, .155)
            B(fire, f"brick_{row}_{col}", (.238, .055, .125),
              (x, 4.49, .16+row*.14), (c, c*.83, c*.64))
for j, x in enumerate((fx-.91, fx+.91)):
    B(fire, f"pier_{j}", (.29, .34, 1.32), (x, 4.37, .70), stone)
    for k in range(3):
        B(fire, f"joint_{j}_{k}", (.295, .345, .009),
          (x, 4.37, .32+k*.39), (.28, .27, .21))
B(fire, "lintel", (2.10, .38, .30), (fx, 4.34, 1.49), (.43, .42, .34))
B(fire, "mantel", (2.20, .43, .065), (fx, 4.31, 1.66), (.40, .39, .31))
B(fire, "inner_top", (1.53, .15, .13), (fx, 4.33, 1.28), (.31, .30, .23))
for j, sgn in enumerate((-1, 1)):
    pivot = (fx+sgn*.72, 4.32, 1.24)
    block = box(size=(.20, .16, .20), center=pivot, color=stone)
    block.turn(axis="+y", degrees=sgn*25, pivot=pivot)
    fire.include(f"inner_shoulder_{j}", block)
B(fire, "hearth", (2.15, .78, .065), (fx, 4.14, .033), (.24, .23, .18))
for j in range(4):
    B(fire, f"hearth_seam_{j}", (.009, .77, .003),
      (fx-.80+j*.54, 4.14, .068), (.12, .12, .09))
scene.include("fireplace", fire)

radiator = Asset("Small pale radiator")
for j in range(8):
    x = 2.10+j*.035
    R(radiator, f"rib_{j}", (x, 4.02, .09), (x-.09, 4.12, .58),
      .014, (.70, .73, .68))
R(radiator, "top", (2.0, 4.12, .58), (2.28, 4.12, .58), .016, (.70, .73, .68))
R(radiator, "bottom", (2.10, 4.02, .09), (2.38, 4.02, .09),
  .015, (.70, .73, .68))
scene.include("radiator", radiator)

bin_asset = Asset("Black hearth bin")
R(bin_asset, "body", (2.73, 4.03, .02), (2.73, 4.03, .28),
  .10, (.045, .050, .042))
scene.include("hearth_bin", bin_asset)

clock = Asset("Wall clock")
R(clock, "rim", (-.48, 4.52, 2.27), (-.48, 4.58, 2.27),
  .125, (.43, .49, .42))
R(clock, "face", (-.48, 4.505, 2.27), (-.48, 4.515, 2.27),
  .109, (.61, .67, .58))
R(clock, "minute", (-.48, 4.492, 2.27), (-.48, 4.492, 2.335),
  .005, (.25, .28, .24))
R(clock, "hour", (-.48, 4.49, 2.27), (-.435, 4.49, 2.25),
  .004, (.25, .28, .24))
scene.include("clock", clock)

for j, y in enumerate((.1, 2.55)):
    lamp = Asset(f"Wall lamp {j}")
    B(lamp, "mount", (.07, .14, .22), (-3.16, y, 2.25), (.16, .19, .16))
    lamp.include("shade", fillet_box(size=(.16, .16, .19), radius=.035,
                                    center=(-3.08, y, 2.27), color=(.27, .32, .26)))
    B(lamp, "glass", (.025, .105, .09), (-2.988, y, 2.26), (.72, .74, .60))
    scene.include(f"wall_lamp_{j}", lamp)

# API audit: all dimensions/radii positive; rod endpoints distinct.
# Fillets .055 <= .155/2, .075 <= .17/2, .035 <= .16/2.
# Repeated keys indexed; transforms use explicit pivots.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient world")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (.55, .60, .46, 1)
background.inputs["Strength"].default_value = .22

def descendants(obj):
    if obj.type == "MESH":
        yield obj
    for child in obj.children:
        yield from descendants(child)

def texture_group(name, style):
    group = bpy.data.objects.get(name)
    if group is None:
        return
    for obj in descendants(group):
        for slot in obj.material_slots:
            if slot.material is None:
                continue
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            bs = nodes.get("Principled BSDF")
            bs.inputs["Roughness"].default_value = .60 if name == "floorboards" else .76
            base = tuple(bs.inputs["Base Color"].default_value)
            coord = nodes.new("ShaderNodeTexCoord")
            mapping = nodes.new("ShaderNodeVectorMath")
            mapping.operation = "MULTIPLY"
            mapping.inputs[1].default_value = (26, 1.4, 5) if style == "wood" else (1, 1, 1)
            noise = nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 5 if style == "wood" else 13
            noise.inputs["Detail"].default_value = 3
            links.new(coord.outputs["Generated"], mapping.inputs[0])
            links.new(mapping.outputs[0], noise.inputs["Vector"])
            ramp = nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = .17
            ramp.color_ramp.elements[0].color = tuple(v*.58 for v in base[:3])+(1,)
            ramp.color_ramp.elements[1].position = .83
            ramp.color_ramp.elements[1].color = tuple(min(v*1.23, 1) for v in base[:3])+(1,)
            links.new(noise.outputs["Fac"], ramp.inputs[0])
            links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = .19
            bump.inputs["Distance"].default_value = .012 if style == "wood" else .022
            links.new(noise.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], bs.inputs["Normal"])

for name, style in (("floorboards", "wood"), ("timbers", "wood"),
                    ("wardrobe", "wood"), ("architecture", "plaster"),
                    ("fireplace", "stone")):
    texture_group(name, style)

# Material edits traverse named groups and copy finishes before local changes.
for name in ("near_left_bunk", "rear_left_bunk", "foreground_right_bunk"):
    group = bpy.data.objects.get(name)
    if group:
        for obj in descendants(group):
            for slot in obj.material_slots:
                if slot.material:
                    mat = slot.material.copy()
                    slot.material = mat
                    mat.use_nodes = True
                    bs = mat.node_tree.nodes.get("Principled BSDF")
                    if max(bs.inputs["Base Color"].default_value[:3]) < .2:
                        bs.inputs["Metallic"].default_value = .68
                        bs.inputs["Roughness"].default_value = .29

set_view(CAMERA, TARGET, lens=LENS, sensor=36)
area_emitter(position=(-2.2, -3.2, 2.35), power=LIGHT_POWER, size=3.4,
             target=(-.7, 1.5, .7), color=(.88, .94, 1.0))
area_emitter(position=(1.6, 1.0, 2.7), power=120, size=3.0,
             target=(.3, 4.4, 1.2), color=(1.0, .90, .69))
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x = 512
sc.render.resolution_y = 341
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = .10
