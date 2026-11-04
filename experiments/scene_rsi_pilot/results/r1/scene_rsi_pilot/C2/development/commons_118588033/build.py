from sceneact import *
import bpy

# Evidence and revision ledger:
# Measured facts: steps 1 and 2 returned valid images. Reported execution times
# were 5.325 and 5.953 seconds; these do not isolate rendering time.
# Visual estimates, reference / step 2:
# column foot ~(279,430) / (278,420); chair ~(175,300) / (170,272);
# machine top ~(235,278) / (238,251); left bunks end x~150 / x~146.
# The near column is closer to the reference than in step 1. Far furniture
# remains somewhat high; the equipment and ventilator are too heavily cropped.
# Floor and ceiling edges still converge toward the rear; support and occlusion
# are visual approximations, not calibrated or collision-tested relationships.
#
# Chosen family: APPEARANCE, specifically illumination only.
# Across floor, walls, mattresses and ceiling the rendering is substantially
# brighter and flatter than the photograph. Reduce area-light power to 42%
# and world strength from .32 to .10. Keep all surface colors unchanged.
# Prediction: darker reddish floor, stronger dark furniture silhouettes and
# ceiling shadows, with pale mattresses and luminous lamps remaining prominent.
# All projected anchors, owner silhouettes and foreground crops remain fixed.
#
# Inventory / ownership / actual support ledger:
# architecture: floor top Z=0, bulkheads, ceiling, beams and lower wall paint.
# foreground_column: coaxial painted regions and collars; floor/ceiling anchor.
# left_bunks: steel uprights on floor; decks support mattresses and pillows.
# left_platform: green top surface Z=.48; equipment feet center Z=.465.
# left_equipment_i: housing, cap, foot, front panel and vents share one owner.
# rear_lockers: floor-standing bodies with attached doors, labels and handles.
# chair: floor legs support seat; back and curved arms stay with chair owner.
# rear_machine: case on floor, supporting its top, pipes and valve.
# right_partition: wall support for board, fire station and notice.
# right_bench: floor legs and stretcher support green seat.
# left_ventilator: wall-supported housing, grille and louvers.
# ceiling_services / pendant_lamp_i: ceiling-supported pipes, braces and lamps.
# Front-to-back occlusion: near cases/benches, column, bunks/chair/machine,
# then lockers and rear bulkhead. Preserve near crops and column occlusion.
# Reference bounds: cases (0,245)-(79,361), bunks (53,213)-(151,331),
# board (294,176)-(347,246), fire station (296,255)-(325,311).
# Board and fire station already exist. Their current projection is beside
# the column and machine; no duplicate or exposure-driven translation is made.
# Uncertain: exact machine identity, rear doorway, bunk depth, fire appliance.

CAMERA = dict(position=(.15, -3.0, 1.67),
              target=(.05, 3.1, .75), lens=25.5)
ROOM = dict(left=-1.85, right=1.85, rear=4.65, height=3.22)
LIGHT_SCALE = .42
WORLD_STRENGTH = .10
PALETTE = dict(
    cream=(.63,.61,.48), wall=(.66,.67,.57),
    floor=(.29,.105,.065), brown=(.24,.085,.045),
    steel=(.40,.43,.40), dark=(.055,.075,.068),
    teal=(.045,.105,.11), mattress=(.72,.74,.66),
    green=(.035,.10,.075), red=(.67,.045,.025))
scene = Scene("Ship accommodation compartment")

def B(owner, name, size, center, color):
    return owner.include(name, box(size, center=center, color=color))

def R(owner, name, a, b, radius, color):
    return owner.include(name, rod(radius, start=a, end=b, color=color))

arch = Asset("architecture")
B(arch,"floor",(3.95,10,.12),(0,0,-.06),PALETTE["floor"])
B(arch,"left_wall",(.13,9.5,3.28),(-1.915,.2,1.58),PALETTE["wall"])
B(arch,"right_wall",(.13,9.5,3.28),(1.915,.2,1.58),PALETTE["wall"])
B(arch,"rear_bulkhead",(3.8,.14,3.25),(0,4.72,1.60),PALETTE["wall"])
B(arch,"ceiling",(3.95,9.8,.13),(0,.2,3.28),(.33,.28,.20))
for side,x in (("left",-1.835),("right",1.835)):
    B(arch,side+"_lower_paint",(.025,9.4,.47),(x,.2,.235),PALETTE["brown"])
    B(arch,side+"_skirting",(.05,9.4,.075),(x,.2,.045),(.17,.07,.04))
B(arch,"rear_lower_paint",(3.7,.025,.43),(0,4.635,.215),PALETTE["brown"])
for i,y in enumerate((-2.8,-1.0,1.0,2.8,4.4)):
    B(arch,f"transverse_beam_{i}",(3.8,.15,.23),(0,y,3.08),(.42,.28,.16))
for i,x in enumerate((-1.45,-.55,.55,1.5)):
    B(arch,f"ceiling_longitudinal_{i}",(.10,9.5,.16),(x,.2,3.13),(.46,.32,.20))
scene.include("architecture",arch)

column = Asset("foreground_column")
R(column,"brown_lower",(.79,-.32,.06),(.79,-.32,1.46),.105,PALETTE["brown"])
R(column,"cream_upper",(.79,-.32,1.46),(.79,-.32,3.25),.105,(.68,.60,.40))
R(column,"base_collar",(.79,-.32,.035),(.79,-.32,.085),.137,(.36,.19,.10))
R(column,"top_collar",(.79,-.32,3.10),(.79,-.32,3.23),.137,(.49,.39,.22))
scene.include("foreground_column",column)

bunk = Asset("three_tier_bunk")
bed_x,bed_y,bed_length = -1.30,2.16,2.95
for i,y in enumerate((.66,3.66)):
    for j,x in enumerate((-1.78,-.79)):
        R(bunk,f"upright_{i}_{j}",(x,y,.04),(x,y,2.58),.022,PALETTE["dark"])
for level,z in enumerate((.52,1.13,1.75)):
    B(bunk,f"deck_{level}",(1.02,bed_length,.065),(bed_x,bed_y,z),(.16,.20,.18))
    B(bunk,f"mattress_{level}",(.94,2.84,.135),(bed_x,bed_y,z+.10),PALETTE["mattress"])
    B(bunk,f"pillow_{level}",(.70,.40,.12),(bed_x,3.30,z+.21),(.78,.79,.70))
    R(bunk,f"outer_edge_{level}",(-.78,.66,z),(-.78,3.66,z),.022,PALETTE["dark"])
    R(bunk,f"head_rail_{level}",(-1.78,3.66,z+.29),(-.79,3.66,z+.29),.018,PALETTE["dark"])
    R(bunk,f"foot_rail_{level}",(-1.78,.66,z+.29),(-.79,.66,z+.29),.018,PALETTE["dark"])
R(bunk,"top_outer_rail",(-.79,.66,2.46),(-.79,3.66,2.46),.021,PALETTE["dark"])
for i,z in enumerate((.37,.81,1.40,2.00)):
    R(bunk,f"end_rung_{i}",(-1.69,.66,z),(-.85,.66,z),.016,PALETTE["dark"])
scene.include("left_bunks",bunk)

platform = Asset("left_equipment_platform")
B(platform,"top",(1.02,2.35,.10),(-1.38,-.76,.43),PALETTE["green"])
B(platform,"front_apron",(.09,2.35,.23),(-.85,-.76,.30),(.035,.075,.065))
for i,y in enumerate((-1.75,.25)):
    for j,x in enumerate((-1.77,-.91)):
        R(platform,f"leg_{i}_{j}",(x,y,.02),(x,y,.4),.022,PALETTE["dark"])
scene.include("left_platform",platform)
for idx,y in enumerate((-1.20,-.35)):
    case = Asset(f"ventilated_equipment_{idx}")
    B(case,"housing",(.57,.70,.79),(-1.49,y,.875),PALETTE["teal"])
    B(case,"top_cap",(.63,.75,.055),(-1.49,y,1.30),(.06,.08,.075))
    B(case,"front_panel",(.025,.58,.66),(-1.19,y,.89),(.11,.16,.15))
    for k in range(11):
        B(case,f"vent_{k}",(.028,.48,.018),(-1.172,y,.61+k*.049),(.025,.045,.045))
    B(case,"foot",(.62,.72,.045),(-1.49,y,.465),(.10,.12,.10))
    scene.include(f"left_equipment_{idx}",case)

lockers = Asset("rear_lockers")
for i,x in enumerate((-.53,.02,.57)):
    B(lockers,f"body_{i}",(.54,.50,1.76),(x,4.03,.91),PALETTE["steel"])
    B(lockers,f"door_{i}",(.505,.025,1.61),(x,3.764,.94),(.46,.49,.46))
    B(lockers,f"handle_{i}",(.035,.045,.17),(x+.16,3.73,1.02),(.16,.18,.16))
    for k in range(5):
        B(lockers,f"upper_slot_{i}_{k}",(.22,.012,.017),(x,3.744,1.40+k*.045),(.23,.27,.25))
    for k in range(3):
        B(lockers,f"lower_slot_{i}_{k}",(.21,.012,.017),(x,3.744,.35+k*.045),(.23,.27,.25))
    B(lockers,f"label_{i}",(.13,.015,.055),(x,3.739,1.25),(.66,.67,.59))
scene.include("rear_lockers",lockers)

rear = Asset("rear_fittings")
B(rear,"door_recess",(1.12,.03,2.45),(-.52,4.63,1.28),(.18,.21,.18))
B(rear,"door_inner",(.91,.035,2.23),(-.52,4.60,1.25),(.42,.45,.38))
for i,x in enumerate((-.99,-.05)):
    B(rear,f"door_jamb_{i}",(.065,.10,2.50),(x,4.55,1.28),(.22,.24,.19))
for i,y in enumerate((2.92,4.35)):
    R(rear,f"upper_cross_pipe_{i}",(-1.82,y,2.65),(1.82,y,2.65),.025,PALETTE["dark"])
scene.include("rear_fittings",rear)

chair = Asset("loose_chair")
cx,cy = -.28,2.48
B(chair,"seat",(.48,.45,.065),(cx,cy,.49),(.28,.29,.22))
B(chair,"back_cushion",(.44,.06,.39),(cx,cy+.20,.86),(.36,.37,.29))
for i,x in enumerate((cx-.23,cx+.23)):
    R(chair,f"front_leg_{i}",(x,cy-.22,.02),(x,cy-.18,.49),.019,(.58,.57,.45))
    R(chair,f"rear_leg_{i}",(x,cy+.29,.02),(x,cy+.17,1.03),.019,(.58,.57,.45))
    chair.include(f"arm_{i}",sweep_tube(
        points=[(x,cy-.16,.49),(x,cy-.20,.73),(x,cy+.19,.74),(x,cy+.20,.92)],
        radius=.018,color=(.60,.59,.48)))
scene.include("chair",chair)

machine = Asset("rear_machine")
B(machine,"case",(.73,.69,.88),(.75,2.64,.48),(.16,.18,.15))
B(machine,"top",(.79,.73,.055),(.75,2.64,.95),(.23,.23,.18))
B(machine,"front_panel",(.58,.018,.63),(.75,2.285,.49),(.20,.22,.18))
B(machine,"panel_seam",(.018,.018,.62),(.81,2.269,.49),(.07,.09,.075))
for i,x in enumerate((.45,1.04)):
    R(machine,f"upper_pipe_{i}",(x,2.73,.97),(x,2.73,1.64),.028,(.22,.23,.17))
R(machine,"upper_crossbar",(.45,2.73,1.64),(1.04,2.73,1.64),.023,(.20,.22,.17))
R(machine,"valve_stem",(.64,2.47,.98),(.64,2.47,1.14),.026,(.44,.36,.14))
R(machine,"valve_bar",(.54,2.47,1.14),(.74,2.47,1.14),.018,(.35,.28,.12))
scene.include("rear_machine",machine)

wall = Asset("right_partition")
B(wall,"partition",(.91,.12,2.88),(1.405,3.57,1.44),(.70,.70,.60))
B(wall,"lower_paint",(.91,.025,.39),(1.405,3.495,.195),PALETTE["brown"])
scene.include("right_partition",wall)

board = Asset("wall_board")
B(board,"frame",(.70,.045,.78),(1.36,3.488,1.96),(.34,.33,.26))
B(board,"writing_surface",(.65,.017,.72),(1.36,3.456,1.96),(.19,.23,.21))
scene.include("wall_board",board)

fire = Asset("fire_station")
B(fire,"red_mount",(.34,.045,.57),(1.26,3.454,1.08),PALETTE["red"])
R(fire,"rounded_body",(1.26,3.36,.86),(1.26,3.36,1.22),.115,(.76,.065,.035))
fire.include("shoulder",ball(.115,center=(1.26,3.36,1.22),color=(.76,.065,.035)))
R(fire,"neck",(1.26,3.36,1.23),(1.26,3.36,1.36),.036,(.25,.20,.12))
R(fire,"handle",(1.20,3.35,1.36),(1.33,3.35,1.36),.018,(.17,.18,.14))
fire.include("hose",sweep_tube(
    points=[(1.32,3.34,1.33),(1.37,3.32,1.22),(1.35,3.32,1.00)],
    radius=.018,color=(.10,.11,.085)))
B(fire,"label",(.09,.012,.12),(1.26,3.24,1.13),(.84,.80,.62))
scene.include("fire_station",fire)

notice = Asset("wall_notice")
B(notice,"paper",(.25,.025,.47),(1.73,3.484,1.55),(.79,.78,.67))
for k in range(4):
    B(notice,f"text_line_{k}",(.16,.008,.01),(1.73,3.465,1.66-k*.045),(.40,.41,.35))
scene.include("wall_notice",notice)

bench = Asset("right_bench")
B(bench,"seat",(.49,2.15,.075),(1.64,-1.39,.49),PALETTE["green"])
for i,y in enumerate((-2.25,-.53)):
    for j,x in enumerate((1.45,1.81)):
        R(bench,f"leg_{i}_{j}",(x,y,.02),(x,y,.46),.022,PALETTE["dark"])
R(bench,"low_stretcher",(1.46,-2.25,.16),(1.46,-.53,.16),.018,PALETTE["dark"])
scene.include("right_bench",bench)

vent = Asset("left_wall_ventilator")
B(vent,"housing",(.18,.69,.69),(-1.73,.40,2.24),(.59,.60,.50))
B(vent,"dark_opening",(.025,.53,.48),(-1.624,.40,2.23),(.07,.09,.085))
for k in range(5):
    B(vent,f"louver_{k}",(.055,.53,.038),(-1.60,.40,2.04+k*.091),(.67,.68,.59))
scene.include("left_ventilator",vent)

services = Asset("ceiling_services")
for i,x in enumerate((-1.49,-.92)):
    R(services,f"long_cream_pipe_{i}",(x,-3.65,2.79),(x,4.52,2.79),.042,(.66,.67,.56))
R(services,"rear_dark_pipe",(.62,1.35,2.59),(.62,4.53,2.59),.031,(.12,.14,.11))
R(services,"right_high_pipe",(1.44,-3.3,3.04),(1.44,4.50,3.04),.075,(.38,.36,.25))
for i,y in enumerate((-2.20,-.30,1.8,3.75)):
    R(services,f"cross_service_{i}",(-1.79,y,2.88),(.42,y,2.88),.029,(.64,.65,.55))
    R(services,f"diagonal_brace_{i}",(-1.73,y,2.55),(-1.18,y,3.19),.032,(.62,.57,.43))
    R(services,f"pipe_hanger_{i}",(-.92,y,2.78),(-.92,y,3.19),.018,(.24,.24,.19))
scene.include("ceiling_services",services)

lamp_locations = [(-.58,-1.36,2.75),(-.22,1.33,2.72),(.04,3.52,2.68)]
for i,(x,y,z) in enumerate(lamp_locations):
    lamp = Asset(f"pendant_lamp_{i}")
    R(lamp,"stem",(x,y,z+.08),(x,y,3.18),.019,(.19,.20,.16))
    shade = ball(1,center=(0,0,0),color=(.15,.17,.15))
    shade.resize((.235,.235,.095))
    shade.move((x,y,z+.045))
    lamp.include("curved_shade",shade)
    R(lamp,"white_diffuser",(x,y,z-.015),(x,y,z+.012),.218,(.94,.95,.84))
    R(lamp,"shade_rim",(x,y,z+.012),(x,y,z+.035),.242,(.22,.24,.20))
    scene.include(f"pendant_lamp_{i}",lamp)

# Pre-execution self-review:
# All geometry, camera parameters and composite transforms match step 2.
# Approximately 220 primitive meshes, including sweep expansion; locker vents
# and equipment slats are the largest decorative families. No dense ornaments.
# Every loop has unique include slots. Dimensions and radii are positive/finite.
# No fillet boxes; rod endpoints and consecutive sweep points are distinct.
# Furniture support coordinates and all foreground occluders are preserved.
# Some nominal contacts have small offsets; exact support is not certified.
# Realize precedes camera/world/lights. Lamp shader selection uses known owner
# markers and nonempty descendants. Local materials and mesh data are copied.
# No external files, render calls, saving or runner-owned setting changes.

realize(scene)
set_view(**CAMERA)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.40,.43,.36,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = WORLD_STRENGTH

area_emitter((-.45,-1.30,2.66),power=155*LIGHT_SCALE,size=.9,
             target=(-.3,.2,.3),color=(1,.91,.72))
area_emitter((-.15,1.4,2.63),power=125*LIGHT_SCALE,size=.75,
             target=(0,2.0,.45),color=(.91,.96,1))
area_emitter((.1,3.75,2.60),power=85*LIGHT_SCALE,size=.7,
             target=(0,3.0,.7),color=(1,.96,.82))
area_emitter((.4,-3.8,2.35),power=75*LIGHT_SCALE,size=2.6,
             target=(0,2,1),color=(.86,.89,1))

def descendant_meshes(marker):
    found = []
    pending = list(marker.children)
    while pending:
        obj = pending.pop()
        if obj.type == "MESH":
            found.append(obj)
        pending.extend(obj.children)
    return found

for i in range(len(lamp_locations)):
    marker = bpy.data.objects.get(f"pendant_lamp_{i}")
    assert marker is not None
    meshes = descendant_meshes(marker)
    assert meshes
    for obj in meshes:
        obj.data = obj.data.copy()
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                continue
            if min(mat.diffuse_color[:3]) > .7:
                local = mat.copy()
                slot.material = local
                local.use_nodes = True
                bsdf = local.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    if "Emission Color" in bsdf.inputs:
                        bsdf.inputs["Emission Color"].default_value = (1,.97,.83,1)
                        bsdf.inputs["Emission Strength"].default_value = 3
                    elif "Emission" in bsdf.inputs:
                        bsdf.inputs["Emission"].default_value = (1,.97,.83,1)
