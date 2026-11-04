from sceneact import *
import bpy
import math
import random

random.seed(8)

# Visual anchor: corridor convergence is approximately (0.08, 0.49).
# Visual anchor: right shelving fills roughly x=0.24..1.00, reaching both crops.
# Visual anchor: exposed book opening lies around x=0.64..0.69.
# Visual anchor: floor occupies the lower left wedge below y=0.54.
# Visual anchor: fluorescent fixtures follow the upper left-to-center diagonal.
# Visual anchor: nearest crank hardware is cropped at the lower right.

CAMERA = dict(position=(0.0, -3.2, 1.58), yaw=27.0, lens=27.5, drop=0.055)
DIM = dict(length=28.0, ceiling=3.35, cabinet_height=3.12,
           cabinet_depth=4.1, aisle_edge=1.60, module_width=0.91, gap=0.045)
FINISH = dict(panel=(0.63, 0.65, 0.59), edge=(0.40, 0.43, 0.35),
              floor=(0.36, 0.39, 0.35), wall=(0.72, 0.73, 0.65),
              ceiling=(0.66, 0.68, 0.61), black=(0.035, 0.044, 0.037),
              steel=(0.44, 0.48, 0.46), paper=(0.79, 0.79, 0.68))
LIGHT = dict(power=190, ambient=0.29)
scene = Scene("Compact archive corridor")

architecture = Asset("architecture")
architecture.include("floor", box((8.5, 34, .12), center=(2.15, 11, -.06),
                                  color=FINISH["floor"]))
architecture.include("ceiling", box((8.5, 34, .14), center=(2.15, 11, 3.42),
                                    color=FINISH["ceiling"]))
architecture.include("left_wall", box((.17, 34, 3.4), center=(-1.14, 11, 1.7),
                                     color=FINISH["wall"]))
architecture.include("left_baseboard", box((.055, 32, .12), center=(-1.035, 11, .06),
                                          color=(.30, .33, .28)))
architecture.include("back_wall", box((8, .15, 3.4), center=(2.1, 28, 1.7),
                                     color=(.56, .59, .50)))
for i in range(12):
    y = -2.0 + i * 2.55
    architecture.include("ceiling_joint_%02d" % i,
                         box((7.5, .012, .013), center=(2, y, 3.341),
                             color=(.49, .51, .46)))
for i in range(3):
    architecture.include("conduit_%d" % i,
                         rod(.025 if i == 0 else .014,
                             start=(-.90 + .14*i, -5, 3.17),
                             end=(-.90 + .14*i, 28, 3.17),
                             color=(.57, .60, .51)))
scene.include("architecture", architecture)

def archive_module(key, y, width):
    a = Asset(key)
    x = DIM["aisle_edge"]
    h = DIM["cabinet_height"]
    a.include("end_panel", box((.065, width, h), center=(x, y, h/2),
                               color=FINISH["panel"]))
    a.include("trailing_edge", box((.09, .035, h),
                                   center=(x-.006, y+width/2-.0175, h/2),
                                   color=FINISH["edge"]))
    a.include("bottom_rail", box((.10, width, .08), center=(x+.005, y, .06),
                                color=(.32, .35, .29)))
    a.include("top_cap", box((.11, width, .045), center=(x+.015, y, h-.018),
                            color=(.70, .71, .65)))
    # Closed stacks run away from the corridor, behind their end panels.
    a.include("stack_body", box((DIM["cabinet_depth"], width-.05, h-.09),
                                center=(x+DIM["cabinet_depth"]/2+.04, y, h/2),
                                color=(.43, .46, .39)))
    plate_y = y + .08
    a.include("label_border", box((.022, .44, .195),
                                  center=(x-.047, plate_y, 2.67),
                                  color=(.20, .23, .21)))
    a.include("label_card", box((.009, .416, .171),
                                center=(x-.063, plate_y, 2.67),
                                color=(.84, .85, .80)))
    for line in range(2):
        for word in range(3):
            a.include("label_print_%d_%d" % (line, word),
                      box((.003, .061 + .011*word, .008),
                          center=(x-.070, plate_y-.132+word*.104,
                                  2.704-line*.066),
                          color=(.25, .28, .28)))
    a.include("lock_plate", box((.018, .065, .115),
                                center=(x-.047, y-.15, 1.26),
                                color=FINISH["steel"]))
    a.include("lock_slot", box((.006, .009, .036),
                               center=(x-.059, y-.15, 1.26),
                               color=FINISH["black"]))
    a.include("lock_tab", rod(.012, start=(x-.073, y-.15, 1.29),
                              end=(x-.092, y-.15, 1.22),
                              color=(.61, .65, .64)))
    hub_y = y-.10
    a.include("crank_hub", rod(.075, start=(x-.042, hub_y, .69),
                              end=(x-.115, hub_y, .69), color=FINISH["black"]))
    a.include("hub_center", rod(.025, start=(x-.12, hub_y, .69),
                                end=(x-.13, hub_y, .69), color=FINISH["steel"]))
    a.include("crank_arm", rod(.022, start=(x-.132, hub_y, .69),
                              end=(x-.132, hub_y+.055, 1.00),
                              color=FINISH["steel"]))
    a.include("crank_crossbar", rod(.018, start=(x-.132, hub_y+.055, 1.0),
                                   end=(x-.132, hub_y+.29, 1.0),
                                   color=FINISH["steel"]))
    a.include("crank_grip", rod(.029, start=(x-.14, hub_y+.18, 1.0),
                               end=(x-.14, hub_y+.31, 1.0),
                               color=FINISH["black"]))
    return a

# The broad first end is partially outside the right frame.
scene.include("archive_near", archive_module("archive_near", -1.42, 1.43))
start = -.20
for i in range(24):
    y = start + i*(DIM["module_width"]+DIM["gap"])
    scene.include("archive_%02d" % i,
                  archive_module("archive_%02d" % i, y, DIM["module_width"]))

opening = Asset("open_book_bay")
bay_y = -.59
opening.include("recess_back", box((.055, .255, 3.08),
                                   center=(2.08, bay_y, 1.55),
                                   color=(.085, .105, .079)))
for j, z in enumerate((.13, .93, 1.74, 2.52, 3.10)):
    opening.include("shelf_%d" % j, box((.50, .30, .034),
                                       center=(1.85, bay_y, z),
                                       color=(.23, .27, .21)))
for j, z in enumerate((.17, .97, 1.78, 2.56)):
    for k in range(4):
        height = random.uniform(.43, .63) if j != 3 else random.uniform(.35, .49)
        col = [(0.20, .23, .16), (.35, .16, .085),
               (.15, .18, .14), (.49, .40, .23)][(j+k)%4]
        yy = bay_y-.103+k*.062
        opening.include("book_%d_%d" % (j,k),
                        box((.28, .053, height),
                            center=(1.77, yy, z+height/2), color=col))
        if k % 2 == 0:
            opening.include("spine_label_%d_%d" % (j,k),
                            box((.005, .035, .065),
                                center=(1.627, yy, z+.17),
                                color=(.72, .71, .57)))
scene.include("open_book_bay", opening)

left_details = Asset("left_wall_details")
for i in range(10):
    y = -.4 + i*2.45
    left_details.include("wall_post_%d" % i,
                         box((.085, .075, 3.13), center=(-1.01, y, 1.565),
                             color=(.61, .63, .54)))
    left_details.include("service_panel_%d" % i,
                         box((.045, .71, 1.55), center=(-1.025, y+.51, 1.70),
                             color=(.70, .72, .65)))
scene.include("left_wall_details", left_details)

fixtures = Asset("ceiling_fixtures")
for i in range(10):
    y = -2.25 + i*3.0
    fixtures.include("housing_%02d" % i,
                     box((.37, 1.65, .13), center=(.10, y, 3.22),
                         color=(.76, .79, .75)))
    fixtures.include("diffuser_%02d" % i,
                     box((.285, 1.56, .018), center=(.10, y, 3.144),
                         color=(.97, .98, 1.0)))
    fixtures.include("suspension_%02d" % i,
                     box((.045, .055, .12), center=(.10, y, 3.325),
                         color=(.53, .57, .53)))
scene.include("ceiling_fixtures", fixtures)

exit_sign = Asset("exit_sign")
exit_sign.include("case", box((.06, .42, .19), center=(-.77, 9.8, 2.72),
                               color=(.78, .79, .71)))
for i in range(4):
    exit_sign.include("red_letter_%d" % i,
                      box((.008, .043, .105), center=(-.807, 9.66+i*.081, 2.72),
                          color=(.67, .045, .025)))
scene.include("exit_sign", exit_sign)

cart = Asset("distant_service_cart")
for z in (.15, .73):
    cart.include("tray_%.2f" % z, box((.54, .74, .06),
                                     center=(-.58, 11.9, z),
                                     color=(.19, .22, .15)))
for i, x in enumerate((-.81, -.35)):
    for j, y in enumerate((11.59, 12.21)):
        cart.include("upright_%d_%d" % (i,j),
                     rod(.021, start=(x,y,.08), end=(x,y,.96),
                         color=(.22,.25,.18)))
cart.include("contents", box((.34,.43,.30), center=(-.57,11.94,.91),
                             color=(.29,.25,.13)))
scene.include("distant_service_cart", cart)

foreground_table = Asset("left_foreground_table")
foreground_table.include("top", box((.58, .83, .055),
                                    center=(-1.0, -.28, .78),
                                    color=(.28,.25,.16)))
foreground_table.include("leg", box((.055,.055,.76),
                                    center=(-.76,-.05,.38),
                                    color=(.16,.18,.13)))
scene.include("left_foreground_table", foreground_table)

realize(scene)
yaw = math.radians(CAMERA["yaw"])
p = CAMERA["position"]
set_view(p, (p[0]+20*math.sin(yaw), p[1]+20*math.cos(yaw),
             p[2]-20*CAMERA["drop"]),
         lens=CAMERA["lens"], sensor=36)

for i in range(10):
    y = -2.25+i*3.0
    area_emitter((.1,y,3.12), power=LIGHT["power"], size=1.5,
                 target=(.2,y,.1), color=(.91,.96,1.0))
area_emitter((-.5,-3.6,2.7), power=90, size=3,
             target=(1.6,1,1.3), color=(.88,.92,1.0))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.62,.67,.62,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = LIGHT["ambient"]

for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Roughness"].default_value = .71
        color = bs.inputs["Base Color"].default_value
        if color[0] > .94 and color[1] > .94:
            bs.inputs["Emission Color"].default_value = (.87,.92,1,1)
            bs.inputs["Emission Strength"].default_value = 2.3
        elif abs(color[0]-.36)<.012 and abs(color[1]-.39)<.012:
            bs.inputs["Roughness"].default_value = .29
