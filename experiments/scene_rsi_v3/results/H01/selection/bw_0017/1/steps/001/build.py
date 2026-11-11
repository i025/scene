# Reference inventory, estimated normalized image bounds:
# Hall: full frame; dark roof and beams in upper third, tall windows along left
# wall, glossy green floor visible in lower right. Far end is partially occluded.
# Processing platforms: approximately (0.18, 0.40)-(0.96, 0.83), with yellow
# guardrails, silver machine bodies, dark frames and several stair flights.
# Main machine: approximately (0.60, 0.30)-(0.80, 0.72), a large stainless
# enclosure with a dark horizontal opening and a curved silver duct above.
# Left machine and ducts: approximately (0.22, 0.30)-(0.57, 0.64), partially
# obscured by rails. Additional machinery at far right is partly cropped.
# Green vertical tank: approximately (0.36, 0.54)-(0.45, 0.79), in front of
# the platforms, with a rounded top and small connecting pipes.
# Blue conveyor: approximately (0.00, 0.77)-(0.63, 1.00), silver frames,
# transverse rollers and blue belts, overlapping the platform foreground.
# Stairs and railings overlap machines, especially at the left and right edges.
# Hidden machine interiors, pipe routes and far-wall details are uncertain.
#
# Estimated primitive count: architecture ~55, machinery ~45, platforms and
# railings ~100, ducts ~30, tank ~10, conveyors ~65, lights ~5: about 310.
# Rods and boxes each count as one; each short tube path expands to 2*n-1.

from sceneact import *
import bpy
import math

scene = Scene("Workshop")

# Palette: dark structural steel, stainless machinery, safety yellow, and epoxy.
steel = (0.105, 0.125, 0.13)
steel_light = (0.24, 0.27, 0.27)
roof = (0.17, 0.19, 0.19)
wall = (0.25, 0.27, 0.26)
silver = (0.58, 0.62, 0.61)
silver_light = (0.72, 0.75, 0.73)
dark = (0.065, 0.075, 0.072)
yellow = (1.0, 0.61, 0.015)
green = (0.025, 0.34, 0.21)
floor_green = (0.12, 0.35, 0.27)
blue = (0.025, 0.18, 0.48)
window = (0.70, 0.83, 0.90)

def add(asset, name, node):
    asset.include(name, node)

def beam(asset, name, a, b, width, color):
    add(asset, name, rod(width, start=a, end=b, color=color))

# Long workshop: y is the hall depth; the window wall is on the left.
hall = Asset("steel_frame_hall")
add(hall, "green_epoxy_floor", box((19, 25, .14), center=(0, 2, -.08), color=floor_green))
add(hall, "left_wall", box((.18, 25, 5.8), center=(-8.5, 2, 2.9), color=wall))
add(hall, "back_wall", box((17, .18, 5.8), center=(0, 14.4, 2.9), color=wall))
add(hall, "dark_roof", box((17.3, 25, .22), center=(0, 2, 6.05), color=roof))
for i, y in enumerate((-9, -5, -1, 3, 7, 11, 14)):
    for x in (-8.3, 8.3):
        add(hall, "column_%d_%s" % (i, str(x)), box((.24, .27, 6), center=(x, y, 3), color=steel))
    add(hall, "roof_cross_beam_%d" % i, box((16.8, .25, .32), center=(0, y, 5.8), color=steel))
for i, x in enumerate((-6, -3, 0, 3, 6)):
    add(hall, "roof_purlin_%d" % i, box((.12, 25, .12), center=(x, 2, 5.91), color=steel_light))
for i, y in enumerate((-8, -5.5, -3, -.5, 2, 4.5, 7, 9.5, 12)):
    add(hall, "window_%d" % i, box((.035, 1.18, 2.75), center=(-8.385, y, 3.1), color=window))
    add(hall, "window_mullion_%d" % i, box((.06, .045, 2.75), center=(-8.35, y, 3.1), color=steel))
    add(hall, "window_crossbar_%d" % i, box((.06, 1.2, .045), center=(-8.35, y, 3.1), color=steel))
scene.include("architecture", hall)

# Raised processing line and its open support structure.
platform = Asset("processing_platform")
add(platform, "deck", box((12.6, 3.5, .18), center=(.4, 4.3, 2.35), color=steel_light))
for x in (-5.6, -2.6, .4, 3.4, 6.4):
    for y in (2.8, 5.8):
        add(platform, "support_%s_%s" % (x, y), box((.16, .16, 2.35), center=(x, y, 1.17), color=steel))
for y in (2.65, 5.95):
    add(platform, "edge_beam_%s" % y, box((12.8, .14, .25), center=(.4, y, 2.25), color=steel))
# Safety rails have a top rail, intermediate rail and regularly spaced posts.
for y in (2.63, 5.97):
    for z in (2.93, 3.48):
        beam(platform, "long_guard_%s_%s" % (y, z), (-5.85, y, z), (6.65, y, z), .035, yellow)
    for i in range(12):
        x = -5.85 + i * (12.5 / 11)
        beam(platform, "guard_post_%s_%d" % (y, i), (x, y, 2.43), (x, y, 3.49), .034, yellow)
for x in (-5.85, 6.65):
    for z in (2.93, 3.48):
        beam(platform, "end_rail_%s_%s" % (x, z), (x, 2.63, z), (x, 5.97, z), .035, yellow)
scene.include("raised_platform", platform)

# Three stainless processing assemblies, each with an enclosure and dark opening.
machines = Asset("stainless_processing_machines")
for i, (x, y, w, d, h) in enumerate([
    (-4.05, 4.35, 2.0, 1.75, 1.55),
    (-.95, 4.55, 2.45, 1.85, 1.15),
    (3.10, 4.35, 3.05, 2.05, 2.20),
    (6.0, 5.0, 1.1, 1.2, 1.55),
]):
    z = 2.48 + h / 2
    add(machines, "machine_%d_body" % i, box((w, d, h), center=(x, y, z), color=silver))
    add(machines, "machine_%d_top" % i, box((w+.12, d+.12, .12), center=(x, y, 2.48+h), color=silver_light))
    front = y - d/2 - .015
    add(machines, "machine_%d_opening" % i, box((w*.77, .035, h*.27), center=(x, front, 2.48+h*.57), color=dark))
    for k in range(3):
        add(machines, "machine_%d_grille_%d" % (i,k), box((w*.72, .045, .025), center=(x, front-.025, 2.48+h*(.48+.07*k)), color=silver_light))
    add(machines, "machine_%d_lower_panel" % i, box((w*.9, .05, .24), center=(x, front-.03, 2.65), color=steel_light))
scene.include("process_equipment", machines)

# Visible insulated duct runs. Short segmented paths preserve prominent elbows.
pipes = Asset("insulated_ducts")
add(pipes, "left_riser", sweep_tube(points=[(-4.5,5.0,3.8),(-4.5,5.0,4.45),(-4.25,5.0,4.7),(-3.05,5.0,4.7),(-2.8,5.0,4.48),(-2.45,5.0,3.8)], radius=.16, color=silver_light))
add(pipes, "main_high_bend", sweep_tube(points=[(2.8,4.7,4.45),(2.8,4.7,5.05),(2.95,4.7,5.25),(3.25,4.7,5.25),(3.8,4.7,5.0),(4.0,4.7,4.65)], radius=.17, color=silver_light))
add(pipes, "horizontal_header", rod(.13, start=(-5.5,5.85,3.9), end=(6.4,5.85,3.9), color=silver))
for i, x in enumerate((-4.5, -2.6, -.5, 1.7, 4.0, 5.9)):
    beam(pipes, "pipe_hanger_%d" % i, (x,5.85,3.9), (x,5.85,5.75), .025, steel_light)
scene.include("ductwork", pipes)

# Yellow stairways connecting floor and raised work deck.
stairs = Asset("access_stairs")
def stair_run(name, x, y0, y1, width, steps):
    ztop = 2.43
    for i in range(steps):
        t = (i+.5)/steps
        y = y0 + (y1-y0)*t
        z = ztop*t
        add(stairs, name+"_tread_%d" % i, box((width, abs(y1-y0)/steps*.82, .06), center=(x,y,z), color=silver))
    for side in (-1, 1):
        xx = x + side*width*.52
        beam(stairs, name+"_stringer_%d" % side, (xx,y0,.08), (xx,y1,ztop), .055, steel_light)
        beam(stairs, name+"_handrail_%d" % side, (xx,y0,.95), (xx,y1,ztop+.95), .035, yellow)
        for j in range(4):
            t = j/3
            yy = y0+(y1-y0)*t
            zz = .08+ztop*t
            beam(stairs, name+"_post_%d_%d" % (side,j), (xx,yy,zz), (xx,yy,zz+.92), .03, yellow)
stair_run("right_stair", 5.65, -.45, 2.65, 1.05, 11)
stair_run("middle_stair", -.45, -.35, 2.65, .9, 11)
stair_run("left_stair", -5.2, -.10, 2.65, .85, 10)
scene.include("stairs", stairs)

# Green vertical pressure vessel in front of the operating deck.
tank = Asset("green_vertical_tank")
add(tank, "cylindrical_shell", rod(.51, start=(-2.8,1.0,.43), end=(-2.8,1.0,1.95), color=green))
add(tank, "domed_top", ball(.51, center=(-2.8,1.0,1.95), color=green))
add(tank, "lower_head", ball(.49, center=(-2.8,1.0,.45), color=green))
for i, (dx,dy) in enumerate(((-.3,-.25),(.3,-.25),(-.3,.25),(.3,.25))):
    add(tank, "leg_%d" % i, box((.08,.08,.43), center=(-2.8+dx,1+dy,.22), color=steel))
beam(tank, "top_nozzle", (-2.8,1.0,2.3), (-2.8,1.0,2.58), .08, silver)
beam(tank, "side_pipe", (-2.3,1.0,1.35), (-1.8,1.0,1.35), .055, silver)
scene.include("vertical_vessel", tank)

# Low conveyor beds cross the foreground; rollers and blue strips are visible.
conveyor = Asset("foreground_conveyor")
for line, y in enumerate((-6.1, -4.65, -3.2)):
    xmid = -2.3
    length = 9.5
    width = 1.05
    add(conveyor, "blue_bed_%d" % line, box((length,width,.12), center=(xmid,y,.72), color=blue))
    for side in (-1,1):
        add(conveyor, "side_rail_%d_%d" % (line,side), box((length+.2,.09,.17), center=(xmid,y+side*.55,.79), color=silver_light))
    for k in range(13):
        x = xmid-length/2+.35+k*.72
        beam(conveyor, "roller_%d_%d" % (line,k), (x,y-.48,.81), (x,y+.48,.81), .027, silver_light)
    for x in (-6.3,-2.4,1.6):
        for side in (-1,1):
            add(conveyor, "leg_%d_%s_%d" % (line,x,side), box((.075,.075,.7), center=(x,y+side*.46,.35), color=silver))
    add(conveyor, "drive_motor_%d" % line, box((.45,.32,.3), center=(2.55,y,.45), color=steel_light))
# A cross conveyor at the far end links the foreground runs.
add(conveyor, "cross_bed", box((1.0,4.2,.12), center=(2.1,-4.65,.72), color=silver))
for y in (-6.45,-5.75,-5.05,-4.35,-3.65,-2.95):
    beam(conveyor, "cross_roller_%s" % y, (1.65,y,.81), (2.55,y,.81), .035, blue)
scene.include("conveyor_line", conveyor)

realize(scene)

# Configure the new factory scene after SceneAct realization.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.68, 0.77, 0.82, 1)
background.inputs["Strength"].default_value = .6

# SceneAct color finishes are adjusted as shared material families when possible.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    r,g,b = c[0],c[1],c[2]
    if g > r*1.3 and g > b*1.1:
        bsdf.inputs["Roughness"].default_value = .25
        bsdf.inputs["Metallic"].default_value = .2
    elif abs(r-g)<.08 and abs(g-b)<.08:
        bsdf.inputs["Metallic"].default_value = .62
        bsdf.inputs["Roughness"].default_value = .32
    else:
        bsdf.inputs["Roughness"].default_value = .42

set_view((11, -20, 8.1), (0, 2.6, 2.7), lens=34)
area_emitter((-7,-3,7), power=1800, size=7, target=(0,3,1.5), color=(.84,.91,1))
area_emitter((1,2,5.7), power=1300, size=7, target=(0,3,0), color=(1,1,1))
area_emitter((6,9,5.5), power=1100, size=6, target=(1,3,1), color=(1,1,1))

# Output is handled by the external runner.
try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
