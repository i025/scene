import math
import random
import bpy
from sceneact import *

# Revision family: illumination/world appearance only.
# Measured evidence: step 1 returned a valid image; reported execution elapsed 19.624 s.
# Visual estimates, not calibrated measurements:
# reference cabinet bounds ~84,118--160,244; render ~128,130--192,233.
# Reference mural ~191,73--326,236; render ~219,86--335,225.
# Far floor corner reference ~351,234; render ~356,225.
# Near right floor contact reference ~466,275; render ~474,285.
# Back ceiling edge reference slopes down to the right; render is more horizontal.
# These geometric discrepancies remain unresolved in this appearance-only revision.
# Largest broad discrepancy: blue walls, gray floor, steel and mural are all too pale.
# Prediction: lower illumination restores blue saturation, dark steel/glass interiors,
# gray floor and dark ceiling contrast while all silhouettes/projections stay fixed.
# Camera-visible exterior is white, matching the open white reference margins.
#
# Evidence/ownership ledger:
# architecture: blue back/right walls, vertical joints, floor and curved base transition.
# cabinet: floor-supported body, two framed glass doors, handles and internal shelves.
# mural: wall-supported backing and botanical stems/seed filaments, species uncertain.
# display: right-wall-supported casing, screen, attached time/date segments.
# suspended_ceiling: grid, tiles and LED diffusers, above walls at z=3.23.
# services: overhead slab, beams, pipes and suspension rods.
# Front-to-back: floor foreground crops bottom; ceiling crops top; cabinet overlaps
# back panels; mural is in front of back wall; display is in front of right wall.
# No absent object is duplicated or moved. Absolute room scale remains uncertain.

CAMERA = dict(position=(-1.15, -6.8, 1.83),
              target=(-0.62, 2.8, 1.78), lens=32.0)
ROOM = dict(left=-3.85, right=1.65, back=3.0, front=-1.45, height=3.2)
CABINET = dict(x=-2.60, y=2.76, width=1.28, depth=.40, height=2.12)
MURAL = dict(left=-1.39, right=1.12, bottom=.13, top=3.10, y=2.885)
DISPLAY = dict(x=1.555, y=.42, z=2.22, width=1.03, height=.73)
LIGHTING = dict(world_strength=.12, led_power=65, entrance_power=135,
                diffuser_strength=1.5)

BLUE = (.075, .48, .66)
SEAM = (.065, .34, .44)
STEEL = (.57, .62, .60)
WHITE = (.86, .90, .87)
FLOOR = (.46, .51, .49)
GLASS = (.27, .34, .31)
scene = Scene("Clean laboratory")

def add(parent, slot, size, center, color):
    return parent.include(slot, box(size=size, center=center, color=color))

arch = Asset("Room envelope")
scene.include("architecture", arch)
add(arch, "floor", (7.8, 7.1, .12), (-.6, .2, -.06), FLOOR)
add(arch, "back_wall", (5.5, .14, 3.2), (-1.10, 3.07, 1.6), BLUE)
add(arch, "right_wall", (.14, 4.45, 3.2), (1.72, .775, 1.6), BLUE)
for i, x in enumerate([-3.20, -2.53, -1.86, -1.19, -.52, .15, .82]):
    add(arch, "back_seam_%02d" % i, (.009, .008, 3.15),
        (x, 2.994, 1.615), SEAM)
for i, y in enumerate([-1.42, -.60, .22, 1.05, 1.88, 2.70]):
    add(arch, "return_seam_%02d" % i, (.008, .011, 3.17),
        (1.644, y, 1.615), SEAM)
for j in range(7):
    t = (j + .5) * math.pi / 14
    yy = 2.90 + .10 * math.sin(t)
    zz = .10 - .10 * math.cos(t)
    add(arch, "back_cove_%d" % j, (5.5, .025, .025),
        (-1.10, yy, zz + .018), WHITE)
    xx = 1.55 + .10 * math.sin(t)
    add(arch, "side_cove_%d" % j, (.025, 4.45, .025),
        (xx, .775, zz + .018), WHITE)
add(arch, "back_base_edge", (5.5, .022, .035), (-1.1, 2.984, .115), WHITE)
add(arch, "side_base_edge", (.022, 4.45, .035), (1.634, .775, .115), WHITE)
add(arch, "front_corner_trim", (.055, .055, 3.22), (1.63, -1.44, 1.61), STEEL)

cab = Asset("Glazed stainless storage cabinet")
scene.include("cabinet", cab)
cx, cy = CABINET["x"], CABINET["y"]
add(cab, "body_back", (1.28, .055, 2.12), (cx, 2.935, 1.06), STEEL)
for i, x in enumerate([cx-.615, cx+.615]):
    add(cab, "side_%d" % i, (.05, .40, 2.12), (x, cy, 1.06), STEEL)
for i, z in enumerate([.045, 2.085]):
    add(cab, "cap_%d" % i, (1.28, .40, .07), (cx, cy, z), STEEL)
add(cab, "dark_interior", (1.15, .015, 1.96), (cx, 2.895, 1.065), (.21,.25,.23))
for i, z in enumerate([.30, .65, 1.00, 1.35, 1.70, 1.99]):
    add(cab, "shelf_%d" % i, (1.15, .32, .022), (cx, 2.75, z), (.69,.73,.69))
for i, x in enumerate([cx-.307, cx+.307]):
    door = cab.include("door_%d" % i, Part("Door %d" % i))
    add(door, "glass", (.474, .018, 1.82), (x, 2.548, 1.075), GLASS)
    for k, dx in enumerate([-.273, .273]):
        add(door, "upright_%d" % k, (.062, .045, 2.02), (x+dx, 2.525, 1.065), STEEL)
    for k, z in enumerate([.09, 2.04]):
        add(door, "rail_%d" % k, (.55, .045, .08), (x, 2.525, z), STEEL)
    hx = x + (.20 if i == 0 else -.20)
    door.include("handle", rod(.012, start=(hx,2.47,.98),
                              end=(hx,2.47,1.16), color=(.75,.78,.75)))

mural = Asset("Botanical wall mural")
scene.include("mural", mural)
add(mural, "background", (2.51, .025, 2.97), (-.135, 2.967, 1.615), (.76,.85,.73))
rng = random.Random(19)
flower_centers = [(-1.10,1.78,.55),(-.45,1.20,.68),(.10,1.77,.57),
                  (.72,.38,.66),(-.85,.27,.43)]
for n, (fx, fz, radius) in enumerate(flower_centers):
    base_x = min(1.08, fx + .45)
    mural.include("stem_%d" % n, rod(.013,
        start=(base_x,2.922,.14), end=(fx,2.922,fz), color=(.26,.13,.23)))
    for j in range(16):
        angle = rng.uniform(0, 2*math.pi)
        reach = radius*rng.uniform(.62,1.0)
        ex = max(-1.375,min(1.105,fx+math.cos(angle)*reach))
        ez = max(.145,min(3.085,fz+math.sin(angle)*reach))
        if abs(ex-fx)+abs(ez-fz) < .01:
            continue
        mural.include("ray_%d_%d" % (n,j), rod(.0024,
            start=(fx,2.914,fz), end=(ex,2.914,ez), color=(.42,.35,.38)))
        for k, da in enumerate([-.34,.34]):
            tx = max(-1.375,min(1.105,ex + .12*math.cos(angle+da)))
            tz = max(.145,min(3.085,ez + .12*math.sin(angle+da)))
            if abs(tx-ex)+abs(tz-ez) > .004:
                mural.include("filament_%d_%d_%d" % (n,j,k),
                    rod(.0012,start=(ex,2.912,ez),end=(tx,2.912,tz),
                        color=(.54,.53,.47)))
    mural.include("seed_head_%d" % n,
        ball(.029, center=(fx,2.915,fz),color=(.25,.12,.23)))

screen = Asset("Time and date display")
scene.include("display", screen)
sx, sy, sz = DISPLAY["x"], DISPLAY["y"], DISPLAY["z"]
add(screen, "case", (.065,1.03,.73), (sx,sy,sz), (.42,.48,.51))
add(screen, "bezel", (.014,.98,.68), (sx-.039,sy,sz), (.08,.16,.24))
add(screen, "screen", (.008,.91,.60), (sx-.051,sy,sz), (.035,.10,.20))
segments = {
    "0":"abcedf", "1":"bc", "2":"abged", "3":"abgcd",
    "4":"fgbc", "5":"afgcd", "6":"afgecd", "7":"abc",
    "8":"abcdefg", "9":"abfgcd"
}
def digit(owner, name, value, yc, zc, scale=1.0):
    w, h, thick = .070*scale, .18*scale, .009*scale
    specs = {
        "a":(0,h/2,w,thick), "g":(0,0,w,thick), "d":(0,-h/2,w,thick),
        "f":(w/2,h/4,thick,h/2), "b":(-w/2,h/4,thick,h/2),
        "e":(w/2,-h/4,thick,h/2), "c":(-w/2,-h/4,thick,h/2)
    }
    for seg in segments[value]:
        dy,dz,wy,hz = specs[seg]
        add(owner,name+"_"+seg,(.004,wy,hz),
            (sx-.058,yc+dy,zc+dz),(.51,.68,.79))
for i, char in enumerate("092907"):
    digit(screen,"time_%d"%i,char,sy+.34-i*.132,sz+.045,.85)
for i, yc in enumerate([sy+.145,sy-.12]):
    for j, zz in enumerate([sz+.016,sz+.078]):
        add(screen,"colon_%d_%d"%(i,j),(.005,.012,.013),
            (sx-.060,yc,zz),(.58,.74,.82))
for i in range(9):
    add(screen,"date_mark_%d"%i,(.004,.026,.025),
        (sx-.058,sy+.28-i*.065,sz-.205),(.29,.48,.64))
for i in range(3):
    add(screen,"status_line_%d"%i,(.004,.15,.008),
        (sx-.058,sy+.30,sz+.23-i*.026),(.19,.39,.51))

ceil = Asset("Suspended ceiling")
scene.include("suspended_ceiling", ceil)
grid_z = 3.23
for i, x in enumerate([-3.85,-2.95,-2.05,-1.15,-.25,.65,1.65]):
    add(ceil,"longitudinal_%d"%i,(.027,5.9,.035),(x,.1,grid_z),(.59,.69,.70))
for i, y in enumerate([-2.85,-1.85,-.85,.15,1.15,2.15,3.0]):
    add(ceil,"cross_%d"%i,(5.55,.026,.035),(-1.10,y,grid_z),(.63,.71,.71))
for i, (x,y,wx,wy) in enumerate([
    (-3.40,2.57,.86,.82),(-2.50,2.57,.86,.82),
    (-1.60,2.57,.86,.82),(-.70,2.57,.86,.82),
    (.20,2.57,.86,.82),(1.14,2.57,.94,.82),
    (1.14,1.65,.94,.94),(1.14,.65,.94,.94)]):
    add(ceil,"ceiling_tile_%d"%i,(wx,wy,.035),(x,y,3.25),WHITE)
led_positions = [(-2.48,1.64),(-.25,1.64),(.17,-.34)]
for i,(x,y) in enumerate(led_positions):
    add(ceil,"led_frame_%d"%i,(.88,.97,.045),(x,y,3.221),(.75,.81,.80))
    add(ceil,"led_diffuser_%d"%i,(.82,.91,.018),(x,y,3.192),(.90,.98,.98))

services = Asset("Exposed overhead structure and services")
scene.include("services",services)
add(services,"concrete_slab",(7.3,6.5,.18),(-1.0,.2,3.94),(.23,.26,.25))
for i,y in enumerate([-2.1,.10,2.45]):
    add(services,"structure_beam_%d"%i,(6.8,.21,.25),(-1.0,y,3.74),(.29,.32,.30))
for i,x in enumerate([-3.35,-1.8,-.15,1.20]):
    services.include("conduit_%d"%i,rod(.018,start=(x,-2.9,3.61),
                                     end=(x,3.0,3.61),color=(.32,.49,.51)))
for i,(x,y) in enumerate([(-3.0,.1),(-2.05,2.1),(-1.15,-1.8),
                          (-.25,1.15),(.65,-.85),(1.6,2.1)]):
    services.include("hanger_%d"%i,rod(.008,start=(x,y,3.25),
                                     end=(x,y,3.85),color=(.48,.53,.51)))

# Inline pre-execution self-review:
# Complete semantic owners and their actual support faces are listed above.
# Cabinet body reaches floor; mural/display lie on room-facing wall surfaces.
# Geometry, camera and non-light materials retained from successful step 1.
# Approx. 400 primitives; botanical family dominates with up to 240 thin rays/
# filaments plus stems/heads. Straight services use one rod per straight span.
# Every loop slot is unique within its parent; attached door nodes are retained.
# All sizes are finite positive; no fillets; every rod has distinct endpoints.
# Cove curvature is a seven-strip approximation, not a verified smooth junction.
# No new geometry after realize. Scoped material descendants are asserted nonempty.
# Review is static; no claim of collision testing or rendered color calibration.

realize(scene)

def owner_meshes(slot):
    marker = bpy.data.objects.get(slot)
    assert marker is not None, "Missing semantic marker: "+slot
    result = [o for o in marker.children_recursive if o.type == 'MESH']
    if marker.type == 'MESH':
        result.append(marker)
    assert result, "No meshes under "+slot
    return result

def scoped_materials(slot, callback):
    for obj in owner_meshes(slot):
        obj.data = obj.data.copy()
        for i, material in enumerate(obj.data.materials):
            if material:
                m = material.copy()
                obj.data.materials[i] = m
                m.use_nodes = True
                shader = m.node_tree.nodes.get("Principled BSDF")
                if shader:
                    callback(shader, m)

def cabinet_finish(shader, material):
    color = shader.inputs["Base Color"].default_value
    if color[0] > .45:
        shader.inputs["Metallic"].default_value = .78
        shader.inputs["Roughness"].default_value = .29
    elif color[0] > .24:
        shader.inputs["Roughness"].default_value = .17
        shader.inputs["Transmission Weight"].default_value = .48
        shader.inputs["IOR"].default_value = 1.46

scoped_materials("cabinet", cabinet_finish)
scoped_materials("architecture",
    lambda s,m: setattr(s.inputs["Roughness"],"default_value",.47))

for obj in owner_meshes("background"):
    obj.data = obj.data.copy()
    mat = obj.data.materials[0].copy()
    obj.data.materials[0] = mat
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 3.7
    tex.inputs["Detail"].default_value = 2.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .15
    ramp.color_ramp.elements[0].color = (.40,.59,.43,1)
    ramp.color_ramp.elements[1].position = .83
    ramp.color_ramp.elements[1].color = (.91,.97,.83,1)
    links.new(tex.outputs["Fac"],ramp.inputs[0])
    links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = .9

for i in range(len(led_positions)):
    for obj in owner_meshes("led_diffuser_%d"%i):
        obj.data = obj.data.copy()
        m = obj.data.materials[0].copy()
        obj.data.materials[0] = m
        m.use_nodes = True
        shader = m.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Emission Color"].default_value = (.83,.97,1,1)
        shader.inputs["Emission Strength"].default_value = LIGHTING["diffuser_strength"]

set_view(**CAMERA)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes, links = world.node_tree.nodes, world.node_tree.links
background = nodes.get("Background")
background.inputs[0].default_value = (.88,.94,.96,1)
background.inputs[1].default_value = LIGHTING["world_strength"]

# Keep open exterior margins white without flooding the room with environment light.
camera_background = nodes.new("ShaderNodeBackground")
camera_background.inputs["Color"].default_value = (1,1,1,1)
camera_background.inputs["Strength"].default_value = 1.0
light_path = nodes.new("ShaderNodeLightPath")
mix = nodes.new("ShaderNodeMixShader")
links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
links.new(background.outputs[0], mix.inputs[1])
links.new(camera_background.outputs[0], mix.inputs[2])
output = next(n for n in nodes if n.type == 'OUTPUT_WORLD')
links.new(mix.outputs[0], output.inputs["Surface"])

for x,y in led_positions:
    area_emitter((x,y,3.16),power=LIGHTING["led_power"],size=1.15,
                 target=(x,y,.1),color=(.87,.96,1.0))
area_emitter((-2.2,-3.0,3.0),power=LIGHTING["entrance_power"],size=4.5,
             target=(-.7,2.4,1.3),color=(.94,.98,1))
