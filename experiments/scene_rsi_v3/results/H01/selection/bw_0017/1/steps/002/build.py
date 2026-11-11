# Discrepancy ledger, comparing the 512 x 267 reference and first render:
# 1. Roof and viewpoint: reference ceiling occupies approximately y=0.00–0.34,
#    with its underside visible; render shows the exterior roof at y=0.20–0.53
#    and gray space around the building. The camera is outside and above the
#    roof. Move it inside the hall and lower it, aiming toward the equipment.
#    Ceiling beams should then run across the upper frame.
# 2. Processing equipment and platform: reference machines and yellow rails
#    occupy approximately x=0.17–0.98, y=0.30–0.78; in the render they are
#    mostly occluded by the roof at x=0.27–0.75, y=0.44–0.77. The camera and
#    roof occlusion are the main supported causes. The main machine, ducts, and
#    stair runs remain separate and editable.
# 3. Foreground conveyor: reference occupies approximately x=0.00–0.64,
#    y=0.72–1.00, with substantial silver frame sections and blue strips.
#    Render occupies x=0.04–0.50, y=0.65–0.94 and looks like a distant,
#    continuous blue slab. Lowering the viewpoint and enlarging the conveyor
#    locally should bring it into the lower foreground; use narrower blue strips
#    and visible silver frames. Cropped machinery at the right edge is retained.
# Architectural slopes: the reference roof beams are nearly horizontal and the
# left wall recedes into depth; the rendered roof perimeter is a visible outside
# edge. The tank and conveyor are both too small, at different depths, consistent
# with the overly distant exterior framing. Keep the left window wall, green
# tank in front of the deck, yellow stairs, and platform-to-machine relations.
# Hidden machine interiors and the exact far-end layout remain uncertain.
#
# Inventory, normalized reference bounds: dark framed hall and roof (full frame);
# tall left windows (0.00–0.22, 0.34–0.66); green floor (lower right);
# stainless machines and insulated ducts (0.22–0.81, 0.22–0.72);
# yellow-railed elevated platform and stairs (0.06–0.97, 0.42–0.98);
# green pressure vessel (0.36–0.45, 0.53–0.80);
# blue and silver conveyor (0.00–0.64, 0.72–1.00); partial equipment at right.
# Estimated expanded primitive count: hall ~55, platforms/rails ~75,
# machines ~45, ducts ~30, stairs ~75, tank ~10, conveyor ~100;
# total approximately 390. Tube paths count as 2*n-1 primitives.

from sceneact import *
import bpy

scene = Scene("Production workshop")

darksteel = (0.085, 0.105, 0.105)
steel = (0.20, 0.23, 0.23)
roofcolor = (0.27, 0.29, 0.28)
wallcolor = (0.25, 0.27, 0.27)
silver = (0.59, 0.63, 0.62)
bright = (0.77, 0.80, 0.78)
shadow = (0.065, 0.075, 0.073)
yellow = (1.0, 0.62, 0.012)
green = (0.015, 0.30, 0.20)
floorcolor = (0.13, 0.35, 0.27)
blue = (0.035, 0.19, 0.49)
windowcolor = (0.71, 0.84, 0.93)

def put(parent, name, node):
    parent.include(name, node)

def bar(parent, name, a, b, radius, color):
    put(parent, name, rod(radius, start=a, end=b, color=color))

# Hall: the camera is inside the envelope, looking toward the processing line.
hall = Asset("Hall")
put(hall, "epoxy_floor", box((22, 30, .14), center=(0, 2, -.08), color=floorcolor))
put(hall, "left_wall", box((.18, 30, 6.3), center=(-8.5, 2, 3.15), color=wallcolor))
put(hall, "far_wall", box((17, .18, 6.3), center=(0, 16.8, 3.15), color=wallcolor))
put(hall, "roof_sheet", box((17.3, 30, .18), center=(0, 2, 6.15), color=roofcolor))

for i, y in enumerate((-10, -6, -2, 2, 6, 10, 14)):
    for side, x in enumerate((-8.32, 8.32)):
        put(hall, "column_%d_%d" % (i, side),
            box((.24, .26, 6.0), center=(x, y, 3), color=darksteel))
    put(hall, "roof_crossbeam_%d" % i,
        box((16.8, .26, .30), center=(0, y, 5.92), color=darksteel))
for i, x in enumerate((-6, -3, 0, 3, 6)):
    put(hall, "roof_purlin_%d" % i,
        box((.12, 30, .12), center=(x, 2, 6.02), color=steel))
for i, y in enumerate((-10, -7.4, -4.8, -2.2, .4, 3, 5.6, 8.2, 10.8, 13.4)):
    put(hall, "window_%d" % i,
        box((.035, 1.05, 2.55), center=(-8.385, y, 3.03), color=windowcolor))
    put(hall, "window_vertical_frame_%d" % i,
        box((.055, .045, 2.55), center=(-8.35, y, 3.03), color=darksteel))
    put(hall, "window_cross_frame_%d" % i,
        box((.055, 1.07, .045), center=(-8.35, y, 3.03), color=darksteel))
scene.include("architecture", hall)

# Elevated platform, with continuous deck, open support frame and yellow guards.
platform = Asset("Operating platform")
put(platform, "deck", box((13.2, 3.4, .16), center=(.25, 4.2, 2.3), color=steel))
for i, x in enumerate((-6, -3, 0, 3, 6.5)):
    for j, y in enumerate((2.7, 5.7)):
        put(platform, "leg_%d_%d" % (i, j),
            box((.16, .16, 2.30), center=(x, y, 1.15), color=darksteel))
for i, y in enumerate((2.6, 5.8)):
    put(platform, "deck_edge_%d" % i,
        box((13.4, .16, .26), center=(.25, y, 2.22), color=steel))
    for j, z in enumerate((2.87, 3.42)):
        bar(platform, "horizontal_guard_%d_%d" % (i, j),
            (-6.35, y, z), (6.85, y, z), .035, yellow)
    for j in range(13):
        x = -6.35 + 13.2 * j / 12
        bar(platform, "guard_post_%d_%d" % (i, j),
            (x, y, 2.37), (x, y, 3.43), .032, yellow)
for i, x in enumerate((-6.35, 6.85)):
    for j, z in enumerate((2.87, 3.42)):
        bar(platform, "end_guard_%d_%d" % (i, j),
            (x, 2.6, z), (x, 5.8, z), .035, yellow)
scene.include("operating_platform", platform)

# Equipment shells retain individually named front openings and panels.
machines = Asset("Processing machines")
machine_specs = [
    (-4.4, 4.35, 2.1, 1.7, 1.55),
    (-1.2, 4.55, 2.5, 1.7, 1.15),
    (2.9, 4.35, 3.15, 1.95, 2.15),
    (6.25, 5.05, 1.2, 1.3, 1.45),
]
for i, (x, y, w, d, h) in enumerate(machine_specs):
    base = 2.38
    front = y - d / 2 - .025
    put(machines, "machine_%d_body" % i,
        box((w, d, h), center=(x, y, base+h/2), color=silver))
    put(machines, "machine_%d_top_cap" % i,
        box((w+.12, d+.12, .12), center=(x, y, base+h), color=bright))
    put(machines, "machine_%d_dark_opening" % i,
        box((w*.78, .04, h*.27), center=(x, front, base+h*.58), color=shadow))
    for k in range(4):
        put(machines, "machine_%d_grille_%d" % (i, k),
            box((w*.73, .05, .027),
                center=(x, front-.025, base+h*(.48+.065*k)), color=bright))
    put(machines, "machine_%d_lower_panel" % i,
        box((w*.9, .055, .23), center=(x, front-.03, base+.18), color=steel))
# A small circular inspection mark on the main housing.
bar(machines, "main_inspection_port", (2.9, 3.34, 4.34),
    (2.9, 3.28, 4.34), .11, darksteel)
bar(machines, "main_inspection_inner", (2.9, 3.27, 4.34),
    (2.9, 3.24, 4.34), .055, silver)
scene.include("processing_equipment", machines)

ducts = Asset("Insulated ducts and hangers")
put(ducts, "left_bent_duct",
    sweep_tube(points=[(-4.8, 5.0, 3.7), (-4.8, 5.0, 4.35),
                       (-4.58, 5.0, 4.57), (-3.45, 5.0, 4.57),
                       (-3.18, 5.0, 4.39), (-2.8, 5.0, 3.72)],
               radius=.15, color=bright))
put(ducts, "main_bent_duct",
    sweep_tube(points=[(2.65, 4.6, 4.4), (2.65, 4.6, 4.97),
                       (2.82, 4.6, 5.15), (3.1, 4.6, 5.15),
                       (3.7, 4.6, 4.91), (3.9, 4.6, 4.56)],
               radius=.17, color=bright))
bar(ducts, "horizontal_header", (-6, 5.85, 3.85),
    (6.8, 5.85, 3.85), .13, silver)
for i, x in enumerate((-5.5, -3.4, -1.1, 1.2, 3.5, 5.7)):
    bar(ducts, "hanger_%d" % i, (x, 5.85, 3.85),
        (x, 5.85, 5.82), .025, steel)
scene.include("ductwork", ducts)

stairs = Asset("Access stairs")
def stair_run(name, x, y0, y1, width, steps):
    ztop = 2.38
    for i in range(steps):
        t = (i + .5) / steps
        y = y0 + (y1-y0)*t
        z = .05 + (ztop-.05)*t
        put(stairs, name+"_tread_%d" % i,
            box((width, abs(y1-y0)/steps*.85, .055),
                center=(x, y, z), color=bright))
    for side in (-1, 1):
        xx = x + side*width*.53
        bar(stairs, name+"_stringer_%d" % side,
            (xx, y0, .06), (xx, y1, ztop), .052, steel)
        bar(stairs, name+"_upper_rail_%d" % side,
            (xx, y0, .95), (xx, y1, ztop+.95), .034, yellow)
        bar(stairs, name+"_middle_rail_%d" % side,
            (xx, y0, .52), (xx, y1, ztop+.52), .027, yellow)
        for j in range(4):
            t = j/3
            yy = y0 + (y1-y0)*t
            zz = .06 + (ztop-.06)*t
            bar(stairs, name+"_post_%d_%d" % (side, j),
                (xx, yy, zz), (xx, yy, zz+.93), .03, yellow)

stair_run("left_stair", -5.4, -.35, 2.6, .9, 10)
stair_run("middle_stair", -.55, -.45, 2.6, .95, 11)
stair_run("right_stair", 5.75, -.55, 2.6, 1.05, 11)
scene.include("access_stairs", stairs)

tank = Asset("Green vertical pressure vessel")
bar(tank, "cylindrical_shell", (-2.85, .9, .43), (-2.85, .9, 1.95), .53, green)
put(tank, "domed_top", resized(ball(.53, center=(-2.85, .9, 1.95), color=green),
                               (1, 1, .55)))
put(tank, "lower_head", resized(ball(.51, center=(-2.85, .9, .43), color=green),
                                (1, 1, .45)))
for i, (dx, dy) in enumerate(((-.3, -.25), (.3, -.25), (-.3, .25), (.3, .25))):
    put(tank, "support_leg_%d" % i,
        box((.09, .09, .43), center=(-2.85+dx, .9+dy, .22), color=steel))
bar(tank, "top_nozzle", (-2.85, .9, 2.20), (-2.85, .9, 2.45), .07, silver)
bar(tank, "side_nozzle", (-2.34, .9, 1.3), (-1.9, .9, 1.3), .055, silver)
scene.include("pressure_vessel", tank)

# Conveyor: three open-framed silver beds with narrow blue strips and rollers.
conveyor = Asset("Foreground roller conveyors")
for line, y in enumerate((-6.1, -4.6, -3.1)):
    xmid = -2.2
    length = 10.5
    width = 1.15
    put(conveyor, "bed_%d" % line,
        box((length, width, .09), center=(xmid, y, .76), color=steel))
    for strip in (-.37, 0, .37):
        put(conveyor, "blue_belt_%d_%s" % (line, str(strip)),
            box((length, .24, .035), center=(xmid, y+strip, .825), color=blue))
    for side in (-1, 1):
        put(conveyor, "side_rail_%d_%d" % (line, side),
            box((length+.15, .10, .20),
                center=(xmid, y+side*.61, .84), color=bright))
    for k in range(14):
        x = xmid-length/2+.3+k*.75
        bar(conveyor, "roller_%d_%d" % (line, k),
            (x, y-.54, .86), (x, y+.54, .86), .025, bright)
    for k, x in enumerate((-6.5, -2.8, .9, 2.7)):
        for side in (-1, 1):
            put(conveyor, "leg_%d_%d_%d" % (line, k, side),
                box((.08, .08, .75), center=(x, y+side*.49, .375), color=silver))
    put(conveyor, "drive_%d" % line,
        box((.48, .34, .32), center=(3.15, y, .47), color=steel))
put(conveyor, "cross_transfer_frame",
    box((1.05, 4.4, .12), center=(2.6, -4.6, .76), color=silver))
for i in range(7):
    y = -6.65 + .68*i
    bar(conveyor, "cross_roller_%d" % i,
        (2.12, y, .85), (3.08, y, .85), .035, bright)
scene.include("conveyor_system", conveyor)

realize(scene)

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
background.inputs["Color"].default_value = (.72, .79, .84, 1)
background.inputs["Strength"].default_value = .6

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    r, g, b = c[0], c[1], c[2]
    if g > r*1.3 and g > b*1.1:
        bsdf.inputs["Roughness"].default_value = .25
        bsdf.inputs["Metallic"].default_value = .18
    elif abs(r-g) < .08 and abs(g-b) < .08:
        bsdf.inputs["Metallic"].default_value = .55
        bsdf.inputs["Roughness"].default_value = .34
    else:
        bsdf.inputs["Roughness"].default_value = .4

set_view((5.8, -14.5, 4.45), (0, 3.5, 2.85), lens=30)
area_emitter((-7.5, -3, 4.8), power=1900, size=6,
             target=(0, 3, 1.7), color=(.85, .92, 1))
area_emitter((-2, 3, 5.7), power=1400, size=6,
             target=(0, 3, 1), color=(1, 1, 1))
area_emitter((6, 8, 5.7), power=1000, size=5,
             target=(1, 4, 1), color=(1, 1, 1))
try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
