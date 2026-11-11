# Reference inventory and image anchors (visual estimates, not calibration):
# The requested subject is the interior visible on the phone screen. Its screen
# occupies roughly x=.31-.63 of the supplied 512x288 image; the reconstruction
# fills the 16:9 output with that interior rather than reproducing the phone.
# Within the screen: tall ribbed vaults occupy the upper half; pointed arcades
# and clustered columns recede toward a bright far end; a stair and dark red
# railing cross the lower foreground. A chandelier hangs near the distant center.
# A magenta sphere overlaps the arcade, and a larger iridescent sphere overlaps
# the right foreground.
# Approximate subject-frame anchors: vault apex (.48,.05), far opening (.48,.58),
# near left column (.16,.45), near right column (.85,.38), stair rail (.25,.83)
# to (.88,.99), magenta sphere (.49,.52), bubble (.79,.65).
# Dominant edges: ribs rise diagonally toward vault intersections; the stair
# handrail descends toward image right; vertical columns converge in depth.
# Far architecture, lower stair termination, and the bubble's back surface are
# partially occluded and remain approximate.
#
# Primitive estimate: architecture ~150, columns ~90, stair and rail ~100,
# chandelier ~25, spheres 2: approximately 370 SceneAct primitives. Each short
# sweep expands to 2*n-1 primitives; the count includes these expansions.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, sweep_tube, realize, set_view, area_emitter

# Major dimensions are kept separate from the camera for later adjustment.
HALL_WIDTH = 5.8
BAY = 3.0
BAYS = 5
SPRING = 4.1
VAULT_TOP = 6.65
CAM_POS = (0.15, -7.9, 3.05)
CAM_TARGET = (0.0, 4.5, 3.55)
CAM_LENS = 25.0

stone = (0.68, 0.61, 0.48)
stone_light = (0.81, 0.76, 0.65)
stone_shadow = (0.49, 0.43, 0.33)
floor_color = (0.63, 0.57, 0.47)
red = (0.24, 0.025, 0.025)
gold = (0.65, 0.39, 0.10)
dark = (0.16, 0.12, 0.09)
magenta = (0.78, 0.015, 0.46)

scene = Scene("Heritage gallery")
vaults = Asset("Vaults")
columns = Asset("Columns")
stairs = Asset("Staircase and railing")
chandelier = Asset("Chandelier")
spheres = Asset("Spheres")

# Simple shells are deliberately faceted between ribs, retaining an open,
# recognizable vault silhouette while keeping the construction compact.
vaults.include("floor", box((7.6, 22.0, .18), center=(0, 4.0, -.10), color=floor_color))
vaults.include("left wall", box((.20, 20.0, 4.3), center=(-3.17, 4.2, 2.1), color=stone))
vaults.include("right wall", box((.20, 20.0, 4.3), center=(3.17, 4.2, 2.1), color=stone))
vaults.include("far luminous wall", box((6.2, .16, 6.7), center=(0, 12.4, 3.3), color=stone_light))

# Narrow clerestory apertures and bright far-end opening.
vaults.include("far opening", box((2.1, .08, 3.4), center=(0, 12.28, 2.1), color=(.93, .88, .69)))
for side in (-1, 1):
    for j in range(BAYS):
        y = -3.0 + j * BAY
        vaults.include("window_%s_%s" % (side, j),
                       box((.025, 1.12, 1.65), center=(side * 3.045, y, 2.95),
                           color=(.85, .81, .66)))

# Segmented ceiling panels follow the cross-section of a pointed vault.
# Ribs use sparse paths, with most points at the visible bends.
for j in range(BAYS):
    y0 = -4.5 + j * BAY
    ym = y0 + BAY / 2
    y1 = y0 + BAY
    for side in (-1, 1):
        # Broad infill slopes rising to the center ridge.
        panel = box((3.48, BAY + .08, .12),
                    center=(side * 1.48, ym, 5.38), color=stone_light)
        panel.turn(axis="y", degrees=side * -40)
        vaults.include("vault panel %s %s" % (j, side), panel)
        points = [(side*2.92, y0, SPRING), (side*2.55, y0, 5.05),
                  (side*1.55, y0, 6.05), (0, y0, VAULT_TOP)]
        vaults.include("transverse rib %s %s" % (j, side),
                       sweep_tube(points=points, radius=.075, color=stone_shadow))
        diag = [(side*2.92, y0, SPRING), (side*2.35, y0+.55, 5.18),
                (side*1.35, ym-.25, 6.13), (0, ym, VAULT_TOP)]
        vaults.include("diagonal rib %s %s" % (j, side),
                       sweep_tube(points=diag, radius=.065, color=stone_shadow))
        diag2 = [(side*2.92, y1, SPRING), (side*2.35, y1-.55, 5.18),
                 (side*1.35, ym+.25, 6.13), (0, ym, VAULT_TOP)]
        vaults.include("diagonal return %s %s" % (j, side),
                       sweep_tube(points=diag2, radius=.065, color=stone_shadow))
    vaults.include("ridge %s" % j,
                   rod(.065, start=(0, y0, VAULT_TOP), end=(0, y1, VAULT_TOP),
                       color=stone_shadow))

# Clustered piers and pointed arches along the two sides.
for side in (-1, 1):
    x = side * 2.85
    for j in range(BAYS + 1):
        y = -4.5 + j * BAY
        columns.include("pier core %s %s" % (side, j),
                        rod(.19, start=(x,y,.15), end=(x,y,SPRING), color=stone_light))
        for dx, dy in ((-.18,0),(.18,0),(0,-.17),(0,.17)):
            columns.include("shaft %s %s %s %s" % (side,j,dx,dy),
                            rod(.075, start=(x+dx,y+dy,.15),
                                end=(x+dx,y+dy,SPRING), color=stone))
        columns.include("base %s %s" % (side,j),
                        box((.65,.65,.18), center=(x,y,.12), color=stone_shadow))
        columns.include("capital %s %s" % (side,j),
                        box((.72,.72,.20), center=(x,y,SPRING-.04), color=stone_light))
        if j < BAYS:
            arch = [(x,y,3.65), (x,y+.32,4.25), (x,y+.78,4.78),
                    (x,y+BAY/2,5.12), (x,y+BAY-.78,4.78),
                    (x,y+BAY-.32,4.25), (x,y+BAY,3.65)]
            columns.include("pointed arcade %s %s" % (side,j),
                            sweep_tube(points=arch, radius=.085, color=stone_shadow))

# Stairway drops toward the camera. Treads are broad marble slabs; the railing
# crosses the near foreground and exposes the lower levels through its gaps.
STAIR_X = -1.45
for i in range(10):
    y = -5.6 + i * .39
    z = .08 + i * .145
    stairs.include("marble tread %02d" % i,
                   box((2.55,.43,.15), center=(STAIR_X,y,z), color=stone_light))
    stairs.include("tread nosing %02d" % i,
                   box((2.56,.045,.035), center=(STAIR_X,y-.20,z+.085), color=stone_shadow))

# Balustrade parallels the stair incline, with dark red uprights and gold top rail.
rail_x = -.10
for i in range(11):
    y = -5.72 + i * .39
    z = .18 + i * .145
    stairs.include("baluster %02d" % i,
                   rod(.035, start=(rail_x,y,z), end=(rail_x,y,z+1.03), color=red))
    if i < 10:
        stairs.include("diagonal iron %02d" % i,
                       rod(.022, start=(rail_x,y,z+.18),
                           end=(rail_x,y+.39,z+.91+.145), color=red))
stairs.include("red handrail",
               rod(.065, start=(rail_x,-5.72,1.21),
                   end=(rail_x,-1.82,2.66), color=red))
stairs.include("gold handrail edge",
               rod(.025, start=(rail_x,-5.72,1.28),
                   end=(rail_x,-1.82,2.73), color=gold))
stairs.include("lower red rail",
               rod(.035, start=(rail_x,-5.72,.40),
                   end=(rail_x,-1.82,1.85), color=red))

# A small brass chandelier suspended above the center of the gallery.
chandelier.include("chain", rod(.025, start=(0,4.0,6.5), end=(0,4.0,4.65), color=gold))
chandelier.include("central stem", rod(.055, start=(0,4.0,4.1), end=(0,4.0,4.7), color=gold))
chandelier.include("center body", ball(.13, center=(0,4.0,4.18), color=gold))
for k in range(8):
    a = 2*math.pi*k/8
    x, y = .67*math.cos(a), 4.0+.67*math.sin(a)
    chandelier.include("arm %s" % k,
                       rod(.025, start=(0,4.0,4.18), end=(x,y,4.30), color=gold))
    chandelier.include("bulb %s" % k,
                       ball(.075, center=(x,y,4.39), color=(1.0,.81,.43)))

# The two AR objects overlap the architecture; the bubble is closer to the
# viewer and larger. Its optical material is assigned after realization.
spheres.include("small magenta sphere",
                ball(.46, center=(-.28,1.0,2.82), color=magenta))
spheres.include("large iridescent sphere",
                ball(1.22, center=(1.66,-.15,2.86), color=(.6,.65,.8)))

for name, asset in (("Vaults",vaults), ("Columns",columns),
                    ("Staircase & railing",stairs), ("Chandelier",chandelier),
                    ("Spheres",spheres)):
    scene.include(name, asset)

realize(scene)
sc = bpy.context.scene

# Named collections make the visible families independently editable.
for collection_name in ("Vaults", "Columns", "Staircase & railing", "Chandelier", "Spheres"):
    if bpy.data.collections.get(collection_name) is None:
        sc.collection.children.link(bpy.data.collections.new(collection_name))

# Configure world explicitly after realization.
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nt = sc.world.node_tree
background = nt.nodes.get("Background") or nt.nodes.new("ShaderNodeBackground")
output = nt.nodes.get("World Output") or nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.72, 0.77, 0.83, 1)
background.inputs["Strength"].default_value = .45

# Reassign objects to semantic collections based on their generated hierarchy
# names where available, without modifying any geometry.
for obj in list(sc.objects):
    low = obj.name.lower()
    target = None
    if any(s in low for s in ("vault", "rib", "ridge", "floor", "wall", "window", "opening")):
        target = "Vaults"
    elif any(s in low for s in ("pier", "shaft", "capital", "arcade", "base")):
        target = "Columns"
    elif any(s in low for s in ("tread", "baluster", "rail", "iron", "nosing")):
        target = "Staircase & railing"
    elif any(s in low for s in ("chandelier", "chain", "bulb", "arm", "stem", "body")):
        target = "Chandelier"
    elif "sphere" in low:
        target = "Spheres"
    if target:
        dest = bpy.data.collections[target]
        if obj.name not in dest.objects:
            dest.objects.link(obj)
        for coll in list(obj.users_collection):
            if coll != dest:
                coll.objects.unlink(obj)

# Apply restrained procedural roughness to the shared stone-like materials.
for mat in list(bpy.data.materials):
    if not mat.use_nodes:
        continue
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if not principled:
        continue
    color = principled.inputs["Base Color"].default_value
    if color[0] > .4 and .7 < color[1] / max(color[0], .001) < 1.1 and color[2] < color[0]:
        principled.inputs["Roughness"].default_value = .68
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 17.0
        noise.inputs["Detail"].default_value = 2.0
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .12
        bump.inputs["Distance"].default_value = .035
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], principled.inputs["Normal"])

# A view-dependent rainbow coating over a translucent sphere suggests thin-film
# interference without relying on an image texture.
bubble = bpy.data.materials.new("Thin film iridescent soap bubble")
bubble.use_nodes = True
nodes = bubble.node_tree.nodes
links = bubble.node_tree.links
nodes.clear()
out = nodes.new("ShaderNodeOutputMaterial")
mix = nodes.new("ShaderNodeMixShader")
transparent = nodes.new("ShaderNodeBsdfTransparent")
gloss = nodes.new("ShaderNodeBsdfPrincipled")
gloss.inputs["Metallic"].default_value = .25
gloss.inputs["Roughness"].default_value = .12
if "Coat Weight" in gloss.inputs:
    gloss.inputs["Coat Weight"].default_value = .9
layer = nodes.new("ShaderNodeLayerWeight")
layer.inputs["Blend"].default_value = .3
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
colors = [(0.0,(.14,.42,.95,1)),(.18,(.15,.9,.75,1)),
          (.35,(.95,.8,.12,1)),(.52,(.98,.22,.46,1)),
          (.70,(.52,.08,.82,1)),(1.0,(.45,.8,1,1))]
ramp.color_ramp.elements[0].position = colors[0][0]
ramp.color_ramp.elements[0].color = colors[0][1]
for pos, col in colors[1:]:
    e = ramp.color_ramp.elements.new(pos)
    e.color = col
links.new(layer.outputs["Facing"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], gloss.inputs["Base Color"])
links.new(transparent.outputs[0], mix.inputs[1])
links.new(gloss.outputs[0], mix.inputs[2])
mix.inputs[0].default_value = .48
links.new(mix.outputs[0], out.inputs["Surface"])
for obj in sc.objects:
    if "large iridescent sphere" in obj.name.lower() and obj.type == "MESH":
        obj.data.materials.clear()
        obj.data.materials.append(bubble)

# Camera, lighting, and output aspect. The runtime owns rendering and saving.
sc.render.resolution_x = 3840
sc.render.resolution_y = 2160
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
area_emitter((0,3.4,4.5), power=850, size=2.2, target=(0,2,1), color=(1,.75,.48))
area_emitter((0,11.4,4.0), power=1800, size=4.0, target=(0,2,2.2), color=(1,.92,.75))
area_emitter((-2,-4,5.8), power=450, size=4.0, target=(0,2,3), color=(1,.88,.7))

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass

# Reference estimates are intentionally separate from computed projections.
# These checks concern positions only, not visibility or material appearance.
landmarks = [
    ("near vault apex", (0,-4.5,VAULT_TOP), (.48,.05)),
    ("far opening top", (0,12.20,3.8), (.48,.45)),
    ("left foreground capital", (-2.85,-4.5,SPRING), (.16,.45)),
    ("stair rail near end", (rail_x,-5.72,1.28), (.25,.83)),
    ("magenta center", (-.28,1.0,2.82), (.49,.52)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
                              scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark | estimated reference | projected")
for label, point, reference in landmarks:
    clip = proj @ cam.matrix_world.inverted() @ Vector((*point,1.0))
    uv = None if clip.w <= 1e-8 else (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(label, reference, None if uv is None else tuple(round(v,3) for v in uv))
