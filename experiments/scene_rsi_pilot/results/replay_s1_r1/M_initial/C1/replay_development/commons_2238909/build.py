from sceneact import *
import bpy
import math
import random

random.seed(8)

# Anchor: corridor convergence approximately (0.08, 0.49).
# Anchor: shelving fills the right side and reaches both crops.
# Anchor: exposed book opening approximately x=0.64..0.69.
# Anchor: floor forms the lower-left wedge below y=0.54.
# Anchor: fluorescent fixtures recede along the upper-left diagonal.
# Anchor: nearest crank is cropped at the lower-right edge.

CAMERA = dict(position=(0, -3.2, 1.58), yaw=27, lens=27.5, drop=-.006)
DIM = dict(length=28, ceiling=3.35, cabinet_height=3.12,
           cabinet_depth=4.1, aisle_edge=1.60, module_width=.91,
           gap=.045, label_height=2.25)
FINISH = dict(panel=(.63,.65,.59), edge=(.40,.43,.35),
              floor=(.36,.39,.35), wall=(.72,.73,.65),
              ceiling=(.66,.68,.61), black=(.035,.044,.037),
              steel=(.44,.48,.46), paper=(.79,.79,.68))
LIGHT = dict(power=62, ambient=.10, fill=30)

# Correction archive_near / foreground layout and open_book_bay:
# The render shows one broad foreground panel and no exposed books.
# Existing books overlap the closed panel footprints; omission is not the cause.
# Hypothesis: narrower foreground carriages and a real gap will recover the
# reference's foreground rhythm and dark book opening. Change local geometry
# and placement, retaining camera and finishes. Risk: foreground crank crops
# change; opening width in projection remains an estimate.
#
# Correction archive_module / label_height:
# Foreground labels approach the upper crop much earlier than in the reference,
# while the hardware is visible. Hypothesis: labels are mounted too high.
# Lower labels as attached groups; preserve locks, cranks and cabinet heights.
# Risk: distant labels descend slightly toward the convergence.

scene = Scene("Compact archive corridor")
architecture = Asset("architecture")
architecture.include("floor", box((8.5,34,.12), center=(2.15,11,-.06),
                                  color=FINISH["floor"]))
architecture.include("ceiling", box((8.5,34,.14), center=(2.15,11,3.42),
                                    color=FINISH["ceiling"]))
architecture.include("left_wall", box((.17,34,3.4), center=(-1.14,11,1.7),
                                     color=FINISH["wall"]))
architecture.include("left_baseboard", box((.055,32,.12),
                     center=(-1.035,11,.06), color=(.30,.33,.28)))
architecture.include("back_wall", box((8,.15,3.4), center=(2.1,28,1.7),
                                     color=(.56,.59,.50)))
for i in range(12):
    architecture.include("ceiling_joint_%02d" % i,
        box((7.5,.012,.013), center=(2,-2+i*2.55,3.341),
            color=(.49,.51,.46)))
for i in range(3):
    architecture.include("conduit_%d" % i,
        rod(.025 if i == 0 else .014,
            start=(-.90+.14*i,-5,3.17), end=(-.90+.14*i,28,3.17),
            color=(.57,.60,.51)))
scene.include("architecture", architecture)

def archive_module(key, y, width):
    a = Asset(key)
    x, h = DIM["aisle_edge"], DIM["cabinet_height"]
    a.include("end_panel", box((.065,width,h), center=(x,y,h/2),
                               color=FINISH["panel"]))
    a.include("trailing_edge", box((.09,.035,h),
        center=(x-.006,y+width/2-.0175,h/2), color=FINISH["edge"]))
    a.include("bottom_rail", box((.10,width,.08),
        center=(x+.005,y,.06), color=(.32,.35,.29)))
    a.include("top_cap", box((.11,width,.045),
        center=(x+.015,y,h-.018), color=(.70,.71,.65)))
    a.include("stack_body", box((DIM["cabinet_depth"],width-.05,h-.09),
        center=(x+DIM["cabinet_depth"]/2+.04,y,h/2),
        color=(.43,.46,.39)))
    label = Asset("label")
    py, pz = y+.035, DIM["label_height"]
    label.include("label_border", box((.022,.44,.195),
        center=(x-.047,py,pz), color=(.20,.23,.21)))
    label.include("label_card", box((.009,.416,.171),
        center=(x-.063,py,pz), color=(.84,.85,.80)))
    for line in range(2):
        for word in range(3):
            label.include("label_print_%d_%d" % (line,word),
                box((.003,.061+.011*word,.008),
                    center=(x-.070,py-.132+word*.104,pz+.034-line*.066),
                    color=(.25,.28,.28)))
    a.include("label", label)
    a.include("lock_plate", box((.018,.065,.115),
        center=(x-.047,y-.15,1.26), color=FINISH["steel"]))
    a.include("lock_slot", box((.006,.009,.036),
        center=(x-.059,y-.15,1.26), color=FINISH["black"]))
    a.include("lock_tab", rod(.012, start=(x-.073,y-.15,1.29),
        end=(x-.092,y-.15,1.22), color=(.61,.65,.64)))
    hy = y-.10
    a.include("crank_hub", rod(.075, start=(x-.042,hy,.69),
        end=(x-.115,hy,.69), color=FINISH["black"]))
    a.include("hub_center", rod(.025, start=(x-.12,hy,.69),
        end=(x-.13,hy,.69), color=FINISH["steel"]))
    a.include("crank_arm", rod(.022, start=(x-.132,hy,.69),
        end=(x-.132,hy+.055,1), color=FINISH["steel"]))
    a.include("crank_crossbar", rod(.018, start=(x-.132,hy+.055,1),
        end=(x-.132,hy+.29,1), color=FINISH["steel"]))
    a.include("crank_grip", rod(.029, start=(x-.14,hy+.18,1),
        end=(x-.14,hy+.31,1), color=FINISH["black"]))
    return a

scene.include("archive_near", archive_module("archive_near",-1.47,.54))
scene.include("archive_foreground_01",
              archive_module("archive_foreground_01",-2.04,.54))
scene.include("archive_foreground_02",
              archive_module("archive_foreground_02",-2.61,.54))
for i in range(24):
    key = "archive_%02d" % i
    y = -.20+i*(DIM["module_width"]+DIM["gap"])
    scene.include(key, archive_module(key,y,DIM["module_width"]))

opening = Asset("open_book_bay")
bay_y, bay_width = -.9275, .48
opening.include("recess_back", box((.055,bay_width,3.08),
    center=(2.08,bay_y,1.55), color=(.085,.105,.079)))
for k, yy in enumerate((bay_y-bay_width/2,bay_y+bay_width/2)):
    opening.include("side_%d" % k,
        box((.50,.025,3.10), center=(1.85,yy,1.55),
            color=(.23,.27,.21)))
for j,z in enumerate((.13,.93,1.74,2.52,3.10)):
    opening.include("shelf_%d" % j,
        box((.50,bay_width,.034), center=(1.85,bay_y,z),
            color=(.23,.27,.21)))
for j,z in enumerate((.17,.97,1.78,2.56)):
    for k in range(7):
        height = random.uniform(.43,.63) if j != 3 else random.uniform(.35,.49)
        col = [(.20,.23,.16),(.35,.16,.085),
               (.15,.18,.14),(.49,.40,.23)][(j+k)%4]
        yy = bay_y-.198+k*.064
        opening.include("book_%d_%d" % (j,k),
            box((.28,.053,height), center=(1.77,yy,z+height/2), color=col))
        if k % 2 == 0:
            opening.include("spine_label_%d_%d" % (j,k),
                box((.005,.035,.065), center=(1.627,yy,z+.17),
                    color=(.72,.71,.57)))
scene.include("open_book_bay", opening)

left_details = Asset("left_wall_details")
for i in range(10):
    y = -.4+i*2.45
    left_details.include("wall_post_%d" % i,
        box((.085,.075,3.13), center=(-1.01,y,1.565),
            color=(.61,.63,.54)))
    left_details.include("service_panel_%d" % i,
        box((.045,.71,1.55), center=(-1.025,y+.51,1.70),
            color=(.70,.72,.65)))
scene.include("left_wall_details", left_details)

fixtures = Asset("ceiling_fixtures")
for i in range(10):
    y = -2.25+i*3
    fixtures.include("housing_%02d" % i,
        box((.37,1.65,.13), center=(.10,y,3.22), color=(.76,.79,.75)))
    fixtures.include("diffuser_%02d" % i,
        box((.285,1.56,.018), center=(.10,y,3.144), color=(.97,.98,1)))
    fixtures.include("suspension_%02d" % i,
        box((.045,.055,.12), center=(.10,y,3.325), color=(.53,.57,.53)))
scene.include("ceiling_fixtures", fixtures)

exit_sign = Asset("exit_sign")
exit_sign.include("case", box((.06,.42,.19), center=(-.77,9.8,2.72),
                               color=(.78,.79,.71)))
for i in range(4):
    exit_sign.include("red_letter_%d" % i,
        box((.008,.043,.105), center=(-.807,9.66+i*.081,2.72),
            color=(.67,.045,.025)))
scene.include("exit_sign", exit_sign)

cart = Asset("distant_service_cart")
for z in (.15,.73):
    cart.include("tray_%.2f" % z, box((.54,.74,.06),
        center=(-.58,11.9,z), color=(.19,.22,.15)))
for i,x in enumerate((-.81,-.35)):
    for j,y in enumerate((11.59,12.21)):
        cart.include("upright_%d_%d" % (i,j),
            rod(.021, start=(x,y,.08), end=(x,y,.96), color=(.22,.25,.18)))
cart.include("contents", box((.34,.43,.30), center=(-.57,11.94,.91),
                             color=(.29,.25,.13)))
scene.include("distant_service_cart", cart)

foreground_table = Asset("left_foreground_table")
foreground_table.include("top", box((.58,.83,.055), center=(-1,-.28,.78),
                                    color=(.28,.25,.16)))
foreground_table.include("leg", box((.055,.055,.76), center=(-.76,-.05,.38),
                                    color=(.16,.18,.13)))
scene.include("left_foreground_table", foreground_table)

assert DIM["module_width"] > .05
assert len(scene.members) == 34
assert bay_y-bay_width/2 > -1.47+.54/2
assert bay_y+bay_width/2 < -.20-.91/2

realize(scene)
yaw = math.radians(CAMERA["yaw"])
p = CAMERA["position"]
set_view(p, (p[0]+20*math.sin(yaw), p[1]+20*math.cos(yaw),
             p[2]-20*CAMERA["drop"]), lens=CAMERA["lens"], sensor=36)
for i in range(10):
    y = -2.25+i*3
    area_emitter((.1,y,3.12), power=LIGHT["power"], size=1.5,
                 target=(.2,y,.1), color=(.91,.96,1))
area_emitter((-.5,-3.6,2.7), power=LIGHT["fill"], size=3,
             target=(1.6,1,1.3), color=(.88,.92,1))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes["Background"]
background.inputs["Color"].default_value = (.62,.67,.62,1)
background.inputs["Strength"].default_value = LIGHT["ambient"]

for mat in bpy.data.materials:
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Roughness"].default_value = .71
        color = bs.inputs["Base Color"].default_value
        if color[0] > .94 and color[1] > .94:
            bs.inputs["Emission Color"].default_value = (.87,.92,1,1)
            bs.inputs["Emission Strength"].default_value = 2.3
        elif abs(color[0]-.36) < .012 and abs(color[1]-.39) < .012:
            bs.inputs["Roughness"].default_value = .29
