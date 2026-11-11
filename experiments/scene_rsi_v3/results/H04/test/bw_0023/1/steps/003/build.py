# Reference inventory and anchors, estimated within the phone's interior view:
# Vaults and pointed arcades fill the upper half, with clustered columns on
# both sides and a bright distant opening around (.35,.55)-(.55,.80).
# A dark-red stair rail crosses the lower foreground from about (.08,.70)
# toward (.85,1.0); pale steps remain visible through and behind its gaps.
# The magenta sphere is centered near (.48,.51), while the larger bubble
# enters from the right around (.68,.35) and is cropped by the screen edge.
# A small chandelier hangs against the distant architecture. The lower stair,
# far wall, and bubble's hidden side are uncertain.
#
# Comparison with the second render, in the same subject-frame coordinates:
# The distant opening is centered around (.50,.58), versus roughly (.40,.60)
# in the reference; its broad wall and flat illumination obscure arcade depth.
# The foreground rail runs from roughly (.15,.66) to (.70,1.0), compared with
# approximately (.08,.70) to (.85,1.0). Its slope is broadly similar, but the
# rendered tread silhouettes and ornate infill are insufficiently visible.
# The rendered magenta sphere is centered near (.47,.58), versus (.48,.51).
# The bubble occupies about (.58,.35)-(.80,.80), versus a right-cropped
# form beginning near (.68,.35). It is incorrectly occluded by the right pier.
# The largest discrepancy is the ceiling: broad flat pitched panels cover the
# rib geometry, whereas the reference has a shaded network of curved ribs and
# separate vault surfaces. The rendered hall is also flatter and less layered.
#
# Ranked corrections and predicted effects:
# 1. Raise the ceiling infill above the rib paths and retain the curved ribs.
#    The upper field gains visible crossing ribs and deeper shaded junctions.
# 2. Move the bubble toward the camera and right (BUBBLE_CENTER), enlarging it.
#    Its left contour should move right and its right contour beyond the crop;
#    placing it in front of the near pier prevents that pier cutting it off.
# 3. Raise the magenta sphere locally (MAGENTA_CENTER) so its center moves up.
# 4. Extend the rail left and right, and make its treads more visible behind
#    it. These local changes widen the foreground railing without moving the
#    background. Reduce uniform fill and add warm chandelier and distant light
#    for more graded illumination. Camera pose and lens remain unchanged.
#
# Approximate expanded SceneAct primitive count: vault ribs 5*2*3*7=210,
# vault shells and ridge 16; columns and arcade 12*7+10*13=214;
# staircase and rail about 65; chandelier 19; spheres 2: about 526 total.

import math
import bpy
from mathutils import Vector
from sceneact import (
    Scene, Asset, box, ball, rod, sweep_tube,
    realize, set_view, area_emitter
)

# Camera is independent of the scene dimensions.
CAM_POS = (0.15, -7.9, 3.05)
CAM_TARGET = (0.0, 4.5, 3.55)
CAM_LENS = 25.0

BAY = 3.0
BAYS = 5
SPRING = 4.1
VAULT_TOP = 6.65
PIER_X = 2.85
MAGENTA_CENTER = (-0.28, 1.0, 3.25)
MAGENTA_RADIUS = 0.46
BUBBLE_CENTER = (3.00, -2.25, 2.85)
BUBBLE_RADIUS = 1.55
RAIL_Y = -3.10

stone = (0.65, 0.57, 0.45)
light_stone = (0.79, 0.73, 0.62)
rib_stone = (0.40, 0.34, 0.28)
floor_stone = (0.61, 0.55, 0.46)
red = (0.22, 0.018, 0.018)
gold = (0.58, 0.33, 0.075)
magenta = (0.68, 0.006, 0.36)

scene = Scene("Neo-Gothic heritage gallery")
vaults = Asset("Vaults")
columns = Asset("Columns")
stairs = Asset("Staircase and railing")
chandelier = Asset("Chandelier")
spheres = Asset("Spheres")

# Floor, walls and luminous distant end.
vaults.include("stone floor", box((7.6, 22, .18), center=(0, 4, -.10), color=floor_stone))
vaults.include("left wall", box((.20, 20, 4.3), center=(-3.17, 4.2, 2.1), color=stone))
vaults.include("right wall", box((.20, 20, 4.3), center=(3.17, 4.2, 2.1), color=stone))
vaults.include("far wall", box((6.2, .16, 6.7), center=(0, 12.4, 3.3), color=light_stone))
vaults.include("bright far opening", box((2.1, .08, 3.5), center=(-.55, 12.28, 2.12),
                                         color=(.98, .93, .80)))

for side in (-1, 1):
    for j in range(BAYS):
        y = -3.0 + j * BAY
        vaults.include("side window %s %s" % (side, j),
                       box((.025, 1.12, 1.65), center=(side * 3.045, y, 2.95),
                           color=(.87, .83, .71)))

# High solid infill lies behind the visible rib network. The shallow pitched
# surfaces keep the hall enclosed while exposing the curved structural ribs.
for j in range(BAYS):
    y0 = -4.5 + j * BAY
    ym = y0 + BAY / 2
    y1 = y0 + BAY
    for side in (-1, 1):
        panel = box((4.35, BAY + .12, .14),
                    center=(side * 1.48, ym, 6.14), color=light_stone)
        panel.turn(axis="y", degrees=side * 25)
        vaults.include("vault infill %s %s" % (j, side), panel)

        transverse = [
            (side*2.92, y0, SPRING),
            (side*2.55, y0, 5.05),
            (side*1.55, y0, 6.05),
            (0, y0, VAULT_TOP)
        ]
        diagonal = [
            (side*2.92, y0, SPRING),
            (side*2.35, y0+.55, 5.18),
            (side*1.35, ym-.25, 6.13),
            (0, ym, VAULT_TOP)
        ]
        return_rib = [
            (side*2.92, y1, SPRING),
            (side*2.35, y1-.55, 5.18),
            (side*1.35, ym+.25, 6.13),
            (0, ym, VAULT_TOP)
        ]
        vaults.include("transverse rib %s %s" % (j, side),
                       sweep_tube(points=transverse, radius=.075, color=rib_stone))
        vaults.include("diagonal rib %s %s" % (j, side),
                       sweep_tube(points=diagonal, radius=.065, color=rib_stone))
        vaults.include("return rib %s %s" % (j, side),
                       sweep_tube(points=return_rib, radius=.065, color=rib_stone))
    vaults.include("longitudinal ridge %s" % j,
                   rod(.055, start=(0, y0, VAULT_TOP),
                       end=(0, y1, VAULT_TOP), color=rib_stone))

# Pointed arcades and grouped shafts.
for side in (-1, 1):
    x = side * PIER_X
    for j in range(BAYS + 1):
        y = -4.5 + j * BAY
        columns.include("pier core %s %s" % (side, j),
                        rod(.15, start=(x, y, .15), end=(x, y, SPRING),
                            color=light_stone))
        for k, (dx, dy) in enumerate(((-.14, 0), (.14, 0), (0, -.14), (0, .14))):
            columns.include("clustered shaft %s %s %s" % (side, j, k),
                            rod(.052, start=(x+dx, y+dy, .15),
                                end=(x+dx, y+dy, SPRING), color=stone))
        columns.include("pier base %s %s" % (side, j),
                        box((.52, .52, .18), center=(x, y, .12), color=rib_stone))
        columns.include("pier capital %s %s" % (side, j),
                        box((.60, .60, .20), center=(x, y, SPRING-.04),
                            color=light_stone))
        if j < BAYS:
            arch = [
                (x, y, 3.65), (x, y+.32, 4.25),
                (x, y+.78, 4.78), (x, y+BAY/2, 5.12),
                (x, y+BAY-.78, 4.78), (x, y+BAY-.32, 4.25),
                (x, y+BAY, 3.65)
            ]
            columns.include("pointed arcade %s %s" % (side, j),
                            sweep_tube(points=arch, radius=.075, color=rib_stone))

# Marble flight and landing, descending from left to right.
stairs.include("upper landing",
               box((2.2, 2.0, .18), center=(-2.35, -2.2, 1.60),
                   color=light_stone))
for i in range(13):
    x = -2.50 + i * .38
    z = 1.60 - i * .112
    stairs.include("marble tread %02d" % i,
                   box((.41, 1.65, .13), center=(x, -2.25, z), color=light_stone))
    stairs.include("tread nosing %02d" % i,
                   box((.035, 1.67, .035), center=(x+.19, -2.25, z+.07),
                       color=rib_stone))

# Open red ironwork and a narrow brass handrail.
for i in range(14):
    x = -2.65 + i * .38
    z = 1.68 - i * .112
    stairs.include("baluster %02d" % i,
                   rod(.029, start=(x, RAIL_Y, z),
                       end=(x, RAIL_Y, z+.95), color=red))
    if i < 13:
        stairs.include("diagonal iron %02d" % i,
                       rod(.020, start=(x, RAIL_Y, z+.14),
                           end=(x+.38, RAIL_Y, z+.75), color=red))
        stairs.include("cross iron %02d" % i,
                       rod(.018, start=(x, RAIL_Y, z+.76),
                           end=(x+.38, RAIL_Y, z+.03), color=red))
stairs.include("red handrail",
               rod(.060, start=(-2.65, RAIL_Y, 2.63),
                   end=(2.29, RAIL_Y, 1.174), color=red))
stairs.include("brass handrail edge",
               rod(.022, start=(-2.65, RAIL_Y, 2.69),
                   end=(2.29, RAIL_Y, 1.234), color=gold))
stairs.include("lower rail",
               rod(.033, start=(-2.65, RAIL_Y, 1.85),
                   end=(2.29, RAIL_Y, .394), color=red))

# Brass chandelier with individually visible bulbs.
chandelier.include("suspension chain",
                   rod(.024, start=(0, 4, 6.50), end=(0, 4, 4.65), color=gold))
chandelier.include("central stem",
                   rod(.05, start=(0, 4, 4.10), end=(0, 4, 4.70), color=gold))
chandelier.include("central body", ball(.12, center=(0, 4, 4.18), color=gold))
for k in range(8):
    a = 2 * math.pi * k / 8
    x = .67 * math.cos(a)
    y = 4 + .67 * math.sin(a)
    chandelier.include("brass arm %s" % k,
                       rod(.025, start=(0, 4, 4.18), end=(x, y, 4.30), color=gold))
    chandelier.include("warm bulb %s" % k,
                       ball(.075, center=(x, y, 4.39), color=(1, .82, .50)))

spheres.include("matte magenta sphere",
                ball(MAGENTA_RADIUS, center=MAGENTA_CENTER, color=magenta))
spheres.include("iridescent bubble",
                ball(BUBBLE_RADIUS, center=BUBBLE_CENTER, color=(.6, .65, .8)))

for name, asset in (
    ("Vaults", vaults),
    ("Columns", columns),
    ("Staircase & railing", stairs),
    ("Chandelier", chandelier),
    ("Spheres", spheres),
):
    scene.include(name, asset)

realize(scene)
sc = bpy.context.scene

# Explicit world setup after SceneAct clears the factory scene.
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
wn = sc.world.node_tree.nodes
wl = sc.world.node_tree.links
background = wn.get("Background") or wn.new("ShaderNodeBackground")
output = wn.get("World Output") or wn.new("ShaderNodeOutputWorld")
wl.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.72, .76, .81, 1)
background.inputs["Strength"].default_value = .28

# Restrained stone bump and soft surface variation.
for mat in list(bpy.data.materials):
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    if c[0] > .4 and .7 < c[1] / max(c[0], .001) < 1.1 and c[2] < c[0]:
        bsdf.inputs["Roughness"].default_value = .70
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 17
        noise.inputs["Detail"].default_value = 2
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .10
        bump.inputs["Distance"].default_value = .025
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# View-dependent, partly transparent interference colors.
bubble = bpy.data.materials.new("Thin-film iridescent bubble")
bubble.use_nodes = True
n = bubble.node_tree.nodes
l = bubble.node_tree.links
n.clear()
out = n.new("ShaderNodeOutputMaterial")
mix = n.new("ShaderNodeMixShader")
transparent = n.new("ShaderNodeBsdfTransparent")
gloss = n.new("ShaderNodeBsdfPrincipled")
gloss.inputs["Metallic"].default_value = .22
gloss.inputs["Roughness"].default_value = .12
if "Coat Weight" in gloss.inputs:
    gloss.inputs["Coat Weight"].default_value = .8
layer = n.new("ShaderNodeLayerWeight")
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 2.8
noise.inputs["Detail"].default_value = 2
tex = n.new("ShaderNodeTexCoord")
l.new(tex.outputs["Generated"], noise.inputs["Vector"])
mult = n.new("ShaderNodeMath")
mult.operation = "MULTIPLY"
mult.inputs[1].default_value = .34
l.new(noise.outputs["Fac"], mult.inputs[0])
add = n.new("ShaderNodeMath")
add.operation = "ADD"
l.new(layer.outputs["Facing"], add.inputs[0])
l.new(mult.outputs[0], add.inputs[1])
wave = n.new("ShaderNodeMath")
wave.operation = "MULTIPLY"
wave.inputs[1].default_value = 3.0
l.new(add.outputs[0], wave.inputs[0])
fract = n.new("ShaderNodeMath")
fract.operation = "FRACT"
l.new(wave.outputs[0], fract.inputs[0])
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
colors = [
    (0.0, (.10, .24, .95, 1)),
    (.16, (.05, .88, .85, 1)),
    (.32, (.90, .86, .12, 1)),
    (.50, (1, .30, .06, 1)),
    (.68, (.95, .03, .52, 1)),
    (.84, (.44, .04, .85, 1)),
    (1.0, (.12, .32, .95, 1))
]
ramp.color_ramp.elements[0].position = colors[0][0]
ramp.color_ramp.elements[0].color = colors[0][1]
for position, color in colors[1:]:
    element = ramp.color_ramp.elements.new(position)
    element.color = color
l.new(fract.outputs[0], ramp.inputs["Fac"])
l.new(ramp.outputs["Color"], gloss.inputs["Base Color"])
l.new(transparent.outputs[0], mix.inputs[1])
l.new(gloss.outputs[0], mix.inputs[2])
mix.inputs[0].default_value = .76
l.new(mix.outputs[0], out.inputs["Surface"])

# Locate the realized sphere meshes by their world positions and diameters.
bpy.context.view_layer.update()
mesh_objects = [o for o in sc.objects if o.type == "MESH"]

def nearest_mesh(center, diameter):
    target = Vector(center)
    candidates = []
    for obj in mesh_objects:
        world_center = obj.matrix_world @ Vector((0, 0, 0))
        distance = (world_center - target).length
        candidates.append((distance + abs(max(obj.dimensions) - diameter) * .4, obj))
    return min(candidates, key=lambda item: item[0])[1]

bubble_obj = nearest_mesh(BUBBLE_CENTER, 2 * BUBBLE_RADIUS)
bubble_obj.data.materials.clear()
bubble_obj.data.materials.append(bubble)
for poly in bubble_obj.data.polygons:
    poly.use_smooth = True

mag_obj = nearest_mesh(MAGENTA_CENTER, 2 * MAGENTA_RADIUS)
for poly in mag_obj.data.polygons:
    poly.use_smooth = True
if mag_obj.data.materials:
    mat = mag_obj.data.materials[0]
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value = .65

# Preserve editable semantic collections. SceneAct's hierarchy remains intact.
for name in ("Vaults", "Columns", "Staircase & railing", "Chandelier", "Spheres"):
    if bpy.data.collections.get(name) is None:
        sc.collection.children.link(bpy.data.collections.new(name))
for obj in (bubble_obj, mag_obj):
    dest = bpy.data.collections["Spheres"]
    if obj.name not in dest.objects:
        dest.objects.link(obj)
    for collection in list(obj.users_collection):
        if collection != dest:
            collection.objects.unlink(obj)

# The runner controls the actual render and file saving.
sc.render.resolution_x = 3840
sc.render.resolution_y = 2160
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)

# Warm indoor key near the chandelier and daylight fill at the far end.
area_emitter((0, 4.0, 4.55), power=1000, size=2.0,
             target=(0, 2.5, 1.5), color=(1, .76, .52))
area_emitter((0, 11.4, 4.0), power=1900, size=4.0,
             target=(0, 2, 2.2), color=(1, .92, .78))
area_emitter((-2, -4, 5.8), power=300, size=4.0,
             target=(0, 2, 3), color=(1, .88, .72))

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass

# Computed point projections are distinct from the observed contour estimates.
# The camera is retained. A small upward trial is printed and restored; upward
# aim should move stationary points down in the frame.
landmarks = [
    ("background opening top", (-.55, 12.20, 3.8), (.40, .45)),
    ("left pier capital", (-PIER_X, -1.5, SPRING), (.16, .45)),
    ("foreground rail left", (-2.65, RAIL_Y, 2.69), (.08, .70)),
    ("foreground rail right", (2.29, RAIL_Y, 1.234), (.85, .98)),
    ("magenta center", MAGENTA_CENTER, (.48, .51)),
    ("bubble center", BUBBLE_CENTER, (.90, .65)),
]

def project_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print("Landmark projections:", label)
    for name, point, reference in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1),
            .5 * (1 - clip.y / clip.w))
        print(name, "reference", reference, "computed",
              None if uv is None else tuple(round(v, 3) for v in uv))

project_table("retained camera")
cam = sc.camera
saved_rotation = cam.rotation_euler.copy()
trial_target = Vector((CAM_TARGET[0], CAM_TARGET[1], CAM_TARGET[2] + .15))
cam.rotation_euler = (trial_target - Vector(CAM_POS)).to_track_quat("-Z", "Y").to_euler()
project_table("trial upward aim")
cam.rotation_euler = saved_rotation
bpy.context.view_layer.update()
