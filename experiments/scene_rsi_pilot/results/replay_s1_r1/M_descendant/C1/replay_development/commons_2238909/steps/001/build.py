from sceneact import *
import bpy
import math
import random

# Hypothesis anchors: corridor convergence (.078,.505); ceiling edges meet there.
# Right cabinet/floor boundary: near (.53,1.0), middle (.25,.69), far (.10,.53).
# Left aisle edge: near (.025,.88), middle (.047,.64), far (.075,.53).
# Near right cabinets crop above/right; narrow book opening around (.65,.08)-(.71,.98).
# Owners: architecture, individual mobile shelving units, their panels/cranks/signs,
# exposed shelf contents, ceiling fixtures, and small left-side utility furniture.

random.seed(9)
scene = Scene("Compact archive aisle")
CAMERA_POSITION = (-0.35, -2.0, 1.62)
CAMERA_YAW = math.radians(28.0)
CAMERA_TARGET = (
    CAMERA_POSITION[0] + 12 * math.sin(CAMERA_YAW),
    CAMERA_POSITION[1] + 12 * math.cos(CAMERA_YAW),
    1.62
)
LENS = 28
CEILING_HEIGHT = 3.22
RIGHT_FACE = 1.20
CABINET_HEIGHT = 2.98
CABINET_DEPTH = 2.50
RUN_LENGTH = 25.0
PANEL_COLOR = (.59, .60, .54)
DARK_METAL = (.105, .12, .105)
SILVER = (.43, .47, .44)

architecture = Asset("Architecture")
architecture.include("archive_floor_surface",
    box((8, 31, .12), center=(1, 11, -.07), color=(.31, .34, .30)))
architecture.include("ceiling",
    box((7, 31, .12), center=(1, 11, CEILING_HEIGHT+.06), color=(.69,.70,.66)))
architecture.include("left_wall",
    box((.16, 29, 3.25), center=(-1.36, 11, 1.61), color=(.66,.67,.60)))
architecture.include("far_wall",
    box((7,.15,3.25), center=(1,26,1.61), color=(.57,.60,.54)))
for i in range(9):
    y = -.7 + i*3.2
    architecture.include(f"ceiling_cross_beam_{i}",
        box((5.8,.10,.18), center=(1,y,3.10), color=(.60,.62,.57)))
architecture.include("left_ceiling_service",
    box((.12,29,.18), center=(-1.07,11,3.05), color=(.50,.52,.45)))
architecture.include("right_light_raceway",
    box((.10,28,.09), center=(1.04,11,3.12), color=(.73,.74,.67)))
scene.include("architecture", architecture)

def make_closed_unit(index, y0, width):
    a = Asset(f"Mobile archive shelving {index}")
    yc = y0 + width/2
    a.include(f"unit_{index}_interior",
        box((CABINET_DEPTH,width-.035,CABINET_HEIGHT-.09),
            center=(RIGHT_FACE+CABINET_DEPTH/2,yc,CABINET_HEIGHT/2),
            color=(.36,.38,.31)))
    a.include(f"unit_{index}_end_panel",
        box((.065,width,CABINET_HEIGHT),
            center=(RIGHT_FACE,yc,CABINET_HEIGHT/2+.035),
            color=PANEL_COLOR))
    a.include(f"unit_{index}_edge",
        box((.025,.024,CABINET_HEIGHT),
            center=(RIGHT_FACE-.040,y0+.012,CABINET_HEIGHT/2+.035),
            color=(.38,.40,.34)))
    a.include(f"unit_{index}_base",
        box((.13,width,.085), center=(RIGHT_FACE-.005,yc,.065),
            color=(.24,.27,.23)))
    # Small rectangular latch and narrow metallic pull.
    a.include(f"unit_{index}_latch_plate",
        box((.018,.054,.13), center=(RIGHT_FACE-.042,yc,1.02),
            color=SILVER))
    a.include(f"unit_{index}_latch_pull",
        rod(.012,start=(RIGHT_FACE-.065,yc-.018,.98),
            end=(RIGHT_FACE-.075,yc-.018,1.055),color=(.24,.28,.26)))
    # Hand wheel and offset crank, all owned by the shelving unit.
    z = .64
    a.include(f"unit_{index}_wheel",
        rod(.092,start=(RIGHT_FACE-.055,yc,z),
            end=(RIGHT_FACE-.105,yc,z),color=DARK_METAL))
    a.include(f"unit_{index}_hub",
        rod(.031,start=(RIGHT_FACE-.11,yc,z),
            end=(RIGHT_FACE-.14,yc,z),color=SILVER))
    a.include(f"unit_{index}_crank_arm",
        rod(.016,start=(RIGHT_FACE-.145,yc,z),
            end=(RIGHT_FACE-.145,yc-.105,z+.20),color=(.19,.22,.19)))
    a.include(f"unit_{index}_crank_grip",
        rod(.024,start=(RIGHT_FACE-.145,yc-.105,z+.20),
            end=(RIGHT_FACE-.145,yc-.30,z+.20),color=(.065,.08,.067)))
    # Slim black frame and off-white shelf-number card.
    a.include(f"unit_{index}_sign_frame",
        box((.028,.43,.155), center=(RIGHT_FACE-.058,yc,2.64),
            color=(.20,.23,.20)))
    a.include(f"unit_{index}_sign_card",
        box((.012,.405,.13), center=(RIGHT_FACE-.079,yc,2.64),
            color=(.80,.81,.76)))
    if index < 9:
        for row in range(2):
            for k in range(4):
                a.include(f"unit_{index}_print_{row}_{k}",
                    box((.006,.043,.007),
                        center=(RIGHT_FACE-.088,yc-.135+k*.077,2.67-row*.052),
                        color=(.31,.33,.31)))
    return a

# A narrow exposed bay interrupts the continuous pale cabinet ends.
near_positions = [(-1.55,.90),(-.60,.84)]
for i,(y,w) in enumerate(near_positions):
    scene.include(f"near_mobile_{i}",make_closed_unit(i,y,w))

open_y0, open_width = .285, .32
exposed = Asset("Exposed book shelving")
exposed.include("exposed_dark_back",
    box((.05,open_width,2.96), center=(1.83,open_y0+open_width/2,1.51),
        color=(.10,.13,.10)))
for side in (0,1):
    exposed.include(f"exposed_upright_{side}",
        box((.67,.035,2.98),center=(1.51,open_y0+side*open_width,1.52),
            color=(.22,.25,.20)))
for j,z in enumerate((.10,.72,1.32,1.94,2.55,2.99)):
    exposed.include(f"exposed_shelf_{j}",
        box((.68,open_width,.035),center=(1.51,open_y0+open_width/2,z),
            color=(.32,.34,.28)))
book_colors=[(.20,.16,.10),(.38,.16,.065),(.12,.17,.14),
             (.43,.34,.14),(.14,.17,.22),(.53,.43,.26)]
for level,base in enumerate((.12,.74,1.34,1.96,2.57)):
    for j in range(4):
        h=random.uniform(.32,.48)
        cy=open_y0+.045+j*.071
        exposed.include(f"exposed_book_{level}_{j}",
            box((.39,.059,h),center=(1.44,cy,base+h/2),
                color=book_colors[(j+level)%len(book_colors)]))
        if level in (0,2,4):
            exposed.include(f"exposed_book_label_{level}_{j}",
                box((.006,.043,.06),center=(1.241,cy,base+.10),
                    color=(.67,.66,.50)))
scene.include("open_book_bay",exposed)

for i in range(22):
    y = .65+i*.99
    scene.include(f"mobile_{i+2}",make_closed_unit(i+2,y,.935))

# Far-side storage and little work surfaces on the left.
left = Asset("Left wall fixtures")
for i in range(12):
    y=1.6+i*1.77
    left.include(f"left_wall_post_{i}",
        box((.075,.06,2.83),center=(-1.25,y,1.48),color=(.42,.45,.37)))
    left.include(f"left_wall_inset_{i}",
        box((.024,1.49,1.57),center=(-1.26,y+.78,1.62),
            color=(.64,.67,.61)))
for i,y in enumerate((.0,2.9,5.8,10.8,15.0)):
    left.include(f"left_worktop_{i}",
        box((.58,.74,.065),center=(-1.06,y,.79),color=(.25,.27,.20)))
    for k,dy in enumerate((-.27,.27)):
        left.include(f"left_worktop_leg_{i}_{k}",
            box((.045,.045,.75),center=(-.88,y+dy,.39),
                color=(.22,.24,.19)))
for i,y in enumerate((1.3,4.2,7.2)):
    left.include(f"left_bin_{i}",
        box((.34,.38,.49),center=(-.95,y,.26),color=(.10,.14,.105)))
    left.include(f"left_bin_rim_{i}",
        box((.37,.41,.045),center=(-.95,y,.51),color=(.21,.24,.18)))
scene.include("left_furniture",left)

fixtures=Asset("Fluorescent ceiling fixtures")
for i,y in enumerate((-1.2,2.0,5.1,8.2,11.3,14.4,17.5,20.6,23.7)):
    fixtures.include(f"fixture_housing_{i}",
        box((.43,1.48,.15),center=(-.30,y,3.02),color=(.65,.68,.65)))
    fixtures.include(f"fixture_luminous_diffuser_{i}",
        box((.31,1.40,.018),center=(-.30,y,2.935),color=(.94,.97,1.0)))
    fixtures.include(f"fixture_end_cap_{i}",
        box((.43,.055,.18),center=(-.30,y-.72,3.005),color=(.48,.52,.48)))
fixtures.include("right_continuous_light",
    box((.065,27,.027),center=(1.00,11,3.065),color=(.94,.97,.91)))
scene.include("ceiling_lighting",fixtures)

exit_sign=Asset("Distant exit sign")
exit_sign.include("exit_back",box((.40,.075,.22),center=(-.80,8.6,2.55),color=(.78,.79,.68)))
for i in range(4):
    exit_sign.include(f"exit_red_letter_{i}",
        box((.035,.009,.115),center=(-.92+i*.075,8.556,2.55),color=(.72,.045,.025)))
scene.include("exit_sign",exit_sign)

realize(scene)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=LENS,sensor=36)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.65,.70,.62,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.32

for y in (-.9,2.5,6,10,14,18,22):
    area_emitter((-.20,y,2.91),power=150,size=2.0,
                 target=(.1,y,.0),color=(.91,.96,1.0))
area_emitter((.9,1.0,3.00),power=100,size=2.5,
             target=(1.2,3,1.1),color=(1,.98,.87))

# Scope procedural floor finish to the explicitly named floor marker.
floor_marker=bpy.data.objects.get("archive_floor_surface")
if floor_marker:
    floor_meshes=[o for o in floor_marker.children_recursive if o.type=="MESH"]
    if floor_marker.type=="MESH":
        floor_meshes.append(floor_marker)
    for obj in floor_meshes:
        for slot in obj.material_slots:
            if slot.material:
                mat=slot.material.copy()
                slot.material=mat
                mat.use_nodes=True
                nodes=mat.node_tree.nodes
                links=mat.node_tree.links
                bs=nodes.get("Principled BSDF")
                if bs:
                    bs.inputs["Roughness"].default_value=.34
                    tex=nodes.new("ShaderNodeTexNoise")
                    tex.inputs["Scale"].default_value=47
                    tex.inputs["Detail"].default_value=2
                    bump=nodes.new("ShaderNodeBump")
                    bump.inputs["Strength"].default_value=.14
                    bump.inputs["Distance"].default_value=.018
                    links.new(tex.outputs["Fac"],bump.inputs["Height"])
                    links.new(bump.outputs["Normal"],bs.inputs["Normal"])

for obj in bpy.data.objects:
    if obj.type=="MESH":
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bs=mat.node_tree.nodes.get("Principled BSDF")
                if bs and "diffuser" in obj.name:
                    bs.inputs["Emission Color"].default_value=(.85,.90,1,1)
                    bs.inputs["Emission Strength"].default_value=2
sc.view_settings.view_transform="AgX"
