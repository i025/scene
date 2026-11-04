from sceneact import *
import bpy

# Evidence ledger:
# Reference: timber x64:118, cropped at top, ends near y504; island
# x127:346/y285:435; hood x159:279/y24:223. Dark rear cabinetry,
# pale tiled floor, exposed dark ceiling, small red-handled kettle.
# Observed feedback: a broad pale foreground surface covers the left half.
# Island, oven, hood and ceiling remain visible at several farther depths.
# Hypothesis: the camera is outside the left wall and sees its outer face.
# Correction family: camera only. Geometry, finishes and lighting retained.
# Camera moves inside the room; focal length compensates for closer viewpoint.
# Ownership: architecture owns floor/walls/beams; each timber is an Asset.
# RearCounter owns fitted units/backsplash/light strip; OvenTower owns ovens.
# Island owns drawers/plinth/slab/sink/tap/hob; Hood owns shell and underside.
# Kettle is independent, supported at rear counter z=1.01.
# Front-to-back: foreground timber, island/hood, rear cabinetry, rear wall.
# All estimated bounds and calibration remain visual hypotheses.

scene = Scene("Kitchen")
ivory = (.70, .70, .65)
bodygrey = (.48, .49, .47)
black = (.035, .040, .039)
dark = (.065, .071, .068)
steel = (.39, .42, .41)
tile = (.69, .68, .63)

def addbox(owner, slot, size, center, color):
    return owner.include(slot, box(size=size, center=center, color=color))

architecture = Asset("Architecture")
addbox(architecture, "floor", (14,14,.12), (0,0,-.06), tile)
addbox(architecture, "rear_wall", (10,.15,3.7), (0,3.15,1.85), (.32,.34,.32))
addbox(architecture, "left_wall", (.16,8,3.7), (-3.45,1.2,1.85), (.36,.37,.34))
addbox(architecture, "ceiling", (11,11,.12), (0,0,3.62), (.027,.033,.031))
for i in range(-6,7):
    addbox(architecture, f"floor_seam_x_{i}", (.009,13,.0015),
           (i*1.15,0,.001), (.49,.49,.45))
    addbox(architecture, f"floor_seam_y_{i}", (13,.009,.0015),
           (0,i*1.15,.001), (.49,.49,.45))
for i in range(12):
    addbox(architecture, f"ceiling_board_seam_{i}", (.015,10,.017),
           (-4.5+i*.75,.2,3.55), (.012,.016,.015))
for i,x in enumerate((-3.0,-.6,2.15,4.2)):
    addbox(architecture, f"ceiling_beam_{i}", (.22,10,.27),
           (x,0,3.43), (.043,.050,.047))
for i,y in enumerate((-.9,1.9,3.1)):
    addbox(architecture, f"ceiling_cross_member_{i}", (10,.13,.15),
           (0,y,3.42), (.055,.063,.059))
scene.include("architecture", architecture)

post = Asset("ForegroundTimber")
addbox(post, "timber", (.32,.34,3.65), (-2.18,-.79,1.825), (.39,.25,.135))
scene.include("foreground_timber", post)
farpost = Asset("FarTimber")
addbox(farpost, "timber", (.16,.19,3.5), (3.23,2.48,1.75), (.48,.32,.18))
scene.include("far_timber", farpost)

rear = Asset("RearCounter")
addbox(rear, "base", (4.75,.66,.91), (-.35,2.57,.475), black)
addbox(rear, "toe_recess", (4.65,.57,.10), (-.35,2.59,.05), (.015,.019,.018))
addbox(rear, "countertop", (4.82,.74,.045), (-.35,2.53,.9875), (.10,.105,.097))
for i in range(6):
    addbox(rear, f"door_{i}", (.76,.025,.77),
           (-2.29+i*.78,2.224,.52), (.045,.052,.047))
addbox(rear, "backsplash", (4.85,.035,.79), (-.34,2.914,1.41), (.075,.084,.076))
for i in range(7):
    addbox(rear, f"backsplash_joint_{i}", (.006,.007,.79),
           (-2.65+i*.77,2.891,1.41), (.031,.038,.033))
addbox(rear, "upper_cabinets", (4.8,.48,.71), (-.35,2.71,2.175), (.045,.052,.047))
for i in range(6):
    addbox(rear, f"upper_joint_{i}", (.009,.012,.70),
           (-2.34+i*.79,2.462,2.175), (.017,.023,.020))
addbox(rear, "under_cabinet_light", (3.8,.035,.018),
       (-.6,2.465,1.813), (.92,.77,.57))
scene.include("rear_counter", rear)

left = Asset("LeftTallCabinet")
addbox(left, "carcass", (.82,.81,2.32), (-2.84,2.45,1.16), (.043,.049,.045))
addbox(left, "front", (.795,.025,2.26), (-2.84,2.032,1.17), (.058,.065,.059))
addbox(left, "horizontal_seam", (.79,.006,.009), (-2.84,2.015,2.03), (.022,.027,.024))
scene.include("left_tall_cabinet", left)

ovens = Asset("OvenTower")
addbox(ovens, "cabinet", (.76,.75,2.41), (1.72,2.54,1.205), (.075,.081,.075))
addbox(ovens, "lower_door", (.69,.025,.83), (1.72,2.15,.45), (.055,.061,.055))
for i,z in enumerate((1.14,1.73)):
    addbox(ovens, f"oven_frame_{i}", (.65,.035,.51), (1.72,2.145,z), (.23,.25,.24))
    addbox(ovens, f"oven_glass_{i}", (.56,.014,.32), (1.72,2.121,z+.035), (.022,.036,.039))
    addbox(ovens, f"control_strip_{i}", (.65,.018,.09), (1.72,2.115,z-.20), (.36,.37,.34))
    addbox(ovens, f"handle_{i}", (.50,.045,.022), (1.72,2.085,z+.21), steel)
scene.include("oven_tower", ovens)

right = Asset("RightTallCabinet")
addbox(right, "carcass", (.91,.83,2.65), (2.61,2.55,1.325), (.044,.051,.046))
addbox(right, "door", (.84,.026,2.32), (2.61,2.118,1.20), (.055,.062,.055))
addbox(right, "top_fascia", (1.07,.91,.25), (2.55,2.55,2.575), (.09,.103,.096))
scene.include("right_tall_cabinet", right)

island = Asset("Island")
ix,iy = .15,-.10
width,depth = 2.40,1.42
addbox(island, "plinth", (2.26,1.28,.13), (ix,iy,.065), (.17,.18,.16))
addbox(island, "body", (width,depth,.85), (ix,iy,.555), bodygrey)
addbox(island, "left_end", (.035,depth,.91),
       (ix-width/2-.008,iy,.535), (.49,.50,.48))
for i,(z,h) in enumerate(((.235,.23),(.49,.245),(.765,.27))):
    addbox(island, f"drawer_{i}", (width-.045,.035,h),
           (ix,iy-depth/2-.023,z), (.59,.60,.57))
    addbox(island, f"drawer_shadow_{i}", (width-.045,.016,.015),
           (ix,iy-depth/2-.044,z+h/2+.009), (.23,.25,.23))

sinkx,sinky = .67,.12
slab = box((width+.035,depth+.035,.055),
           center=(ix,iy,1.0125), color=(.77,.78,.72))
cut = box((.60,.40,.15),
          center=(sinkx,sinky,1.015), color=(.77,.78,.72))
island.include("countertop", subtract(slab,cut))
addbox(island, "sink_bottom", (.59,.39,.022), (sinkx,sinky,.925), (.57,.61,.59))
for i,x in enumerate((sinkx-.30,sinkx+.30)):
    addbox(island, f"sink_side_{i}", (.015,.41,.09), (x,sinky,.976), (.66,.69,.65))
for i,y in enumerate((sinky-.20,sinky+.20)):
    addbox(island, f"sink_end_{i}", (.61,.015,.09), (sinkx,y,.976), (.66,.69,.65))
island.include("tap", sweep_tube(
    points=[(sinkx+.02,sinky+.30,1.04),
            (sinkx+.02,sinky+.30,1.22),
            (sinkx+.02,sinky+.28,1.27),
            (sinkx+.02,sinky+.22,1.29),
            (sinkx+.02,sinky+.10,1.29),
            (sinkx+.02,sinky+.06,1.25)],
    radius=.013, color=(.58,.63,.61)))
addbox(island, "tap_base", (.065,.065,.016), (sinkx+.02,sinky+.30,1.048), steel)
addbox(island, "flush_hob", (.63,.56,.003), (-.47,-.10,1.042), (.63,.65,.60))
scene.include("island", island)

hood = Asset("SuspendedHood")
addbox(hood, "main_shell", (1.08,1.02,1.66), (-.12,.27,2.61), (.76,.76,.69))
addbox(hood, "lower_lip", (1.10,1.04,.035), (-.12,.27,1.786), (.59,.60,.54))
addbox(hood, "underside", (.91,.85,.012), (-.12,.27,1.765), (.33,.35,.31))
scene.include("hood", hood)

kettle = Asset("Kettle")
kettle.include("body", ball(.102, center=(-.62,2.35,1.115), color=(.021,.026,.023)))
addbox(kettle, "base", (.18,.15,.025), (-.62,2.35,1.026), (.045,.047,.041))
kettle.include("red_handle", sweep_tube(
    points=[(-.72,2.37,1.10),(-.73,2.37,1.20),
            (-.69,2.37,1.25),(-.60,2.37,1.26),
            (-.55,2.37,1.21),(-.55,2.37,1.13)],
    radius=.018, color=(.70,.008,.018)))
kettle.include("spout", rod(.025, start=(-.55,2.33,1.12),
                           end=(-.50,2.30,1.17), color=(.16,.17,.15)))
scene.include("kettle", kettle)

# No fillets; all tube segments have distinct endpoints; include keys unique.
realize(scene)

def descendants(marker):
    found = bpy.data.objects.get(marker)
    assert found is not None, marker
    meshes = [o for o in found.children_recursive if o.type == 'MESH']
    assert meshes, marker
    return meshes

for obj in descendants("foreground_timber") + descendants("far_timber"):
    obj.data = obj.data.copy()
    material = bpy.data.materials.new(obj.name + "_wood")
    material.use_nodes = True
    nodes,links = material.node_tree.nodes,material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = .72
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 5
    tex.inputs["Detail"].default_value = 4
    coords = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeVectorMath")
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (8,8,.32)
    links.new(coords.outputs["Generated"], mapping.inputs[0])
    links.new(mapping.outputs[0], tex.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .20
    ramp.color_ramp.elements[0].color = (.13,.065,.025,1)
    ramp.color_ramp.elements[1].position = .80
    ramp.color_ramp.elements[1].color = (.56,.36,.18,1)
    links.new(tex.outputs["Fac"], ramp.inputs[0])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .19
    bump.inputs["Distance"].default_value = .035
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    obj.data.materials.clear()
    obj.data.materials.append(material)

for marker in ("island","hood","oven_tower","rear_counter"):
    for obj in descendants(marker):
        obj.data = obj.data.copy()
        for slot in obj.material_slots:
            if slot.material:
                mat = slot.material.copy()
                slot.material = mat
                mat.use_nodes = True
                principled = mat.node_tree.nodes.get("Principled BSDF")
                if principled:
                    principled.inputs["Roughness"].default_value = .38 if marker == "island" else .58

# Only this parameter family changes relative to the first build.
CAMERA_POSITION = (-3.25,-4.40,2.18)
CAMERA_TARGET = (-.30,.55,1.58)
CAMERA_LENS = 32
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.22,.25,.26,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .35

area_emitter((-3.0,-3.4,3.05), power=650, size=4.0,
             target=(0,0,.6), color=(1,.94,.83))
area_emitter((2.6,-.8,3.15), power=420, size=3.0,
             target=(.3,.1,1), color=(.88,.94,1))
area_emitter((-.8,2.36,1.79), power=55, size=2.0,
             target=(-.8,2.85,1.2), color=(1,.76,.56))
area_emitter((-3.0,1.5,2.7), power=170, size=2.0,
             target=(-2.0,1.0,1), color=(1,.95,.85))

render_scene = bpy.context.scene
render_scene.render.resolution_x = 384
render_scene.render.resolution_y = 512
render_scene.render.resolution_percentage = 100
render_scene.render.engine = 'CYCLES'
render_scene.cycles.samples = 64
render_scene.view_settings.view_transform = 'AgX'
