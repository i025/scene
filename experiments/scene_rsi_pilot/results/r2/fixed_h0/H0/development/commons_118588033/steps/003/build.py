from sceneact import *
import bpy
import random

random.seed(8)
scene = Scene("Shipboard sleeping compartment")
iron = (.035, .045, .040)
wall = (.59, .60, .48)
ivory = (.72, .73, .61)
floorcolor = (.235, .074, .038)
serial = 0

def add(name, node):
    global serial
    serial += 1
    scene.include(f"{name}_{serial}", node)
    return node

def cube(name, size, center, color):
    return add(name, box(size, center=center, color=color))

def pipe(name, a, b, radius=.025, color=iron):
    return add(name, rod(radius, start=a, end=b, color=color))

def sphere(name, center, radius, color, scale=None):
    node = ball(radius, center=center, color=color)
    if scale:
        node.resize(scale)
    return add(name, node)

# Steel shell and continuous painted deck.
cube("red brown deck", (4.65, 11.8, .13), (0, 2.25, -.085), floorcolor)
cube("port bulkhead", (.14, 11.6, 3.95), (-2.12, 2.25, 1.93), wall)
cube("starboard bulkhead", (.14, 11.6, 3.95), (2.12, 2.25, 1.93), wall)
cube("aft bulkhead", (4.3, .15, 3.95), (0, 7.3, 1.93), wall)
cube("overhead", (4.5, 11.8, .16), (0, 2.25, 3.87), (.30, .24, .145))
cube("port skirting", (.035, 11.5, .25), (-2.025, 2.2, .115), (.24, .085, .045))
cube("aft skirting", (4.2, .035, .24), (0, 7.2, .11), (.24, .095, .05))
for y in [-2.8, -.9, 1.05, 3, 4.95, 6.9]:
    cube("fine deck seam", (4.1, .004, .003), (0, y, -.018), (.18, .055, .028))

# Deep painted beams overhead.
for y in [-2.1, -.3, 1.6, 3.6, 5.6, 7]:
    cube("transverse overhead beam", (4.15, .15, .28), (0, y, 3.61), (.43, .265, .12))
for x in [-1.7, -.85, .05, 1.05, 1.85]:
    cube("longitudinal rib", (.09, 11.5, .23), (x, 2.2, 3.67), (.43, .29, .16))
for y in [-2.3, -.6, 1.3, 3.4]:
    pipe("diagonal brace", (-1.7, y, 2.92), (-1.02, y+.75, 3.73), .040, (.58, .43, .27))
pipe("large port pipe", (-1.8, -3.3, 2.92), (-1.8, 6.9, 2.92), .064, ivory)
pipe("parallel port pipe", (-1.36, -2.6, 3.15), (-1.36, 6.9, 3.15), .042, (.56, .58, .47))
pipe("dark overhead pipe", (1.45, -3, 3.55), (1.45, 7.1, 3.55), .08, iron)
for y in [-1.5, 0, 1.8, 3.8, 5.8]:
    pipe("pipe suspension", (-1.8, y, 2.92), (-1.8, y, 3.75), .016, (.35, .38, .31))
    pipe("pipe coupling", (-1.8, y-.045, 2.92), (-1.8, y+.045, 2.92), .079, (.50, .53, .43))
pipe("bent white service line", (-1.42, -.65, 2.91), (-1.10, -.65, 2.63), .045, ivory)
pipe("bent white service line", (-1.10, -.65, 2.63), (-1.10, 1.2, 2.63), .045, ivory)

# Main round support column.
px, py = .86, -.12
pipe("pillar red lower section", (px, py, .03), (px, py, 1.86), .112, (.285, .092, .043))
pipe("pillar ochre upper section", (px, py, 1.86), (px, py, 3.83), .112, (.63, .48, .265))
pipe("pillar foot ring", (px, py, .015), (px, py, .055), .135, (.42, .22, .105))
pipe("pillar collar", (px, py, 3.60), (px, py, 3.71), .145, (.44, .28, .13))

# Right return wall and its fittings.
cube("right partition", (.98, .13, 3.77), (1.67, 2.10, 1.87), (.67, .67, .54))
cube("partition red base", (.98, .023, .32), (1.67, 2.022, .16), (.29, .11, .065))
cube("chalkboard surround", (.70, .045, .78), (1.62, 2.014, 2.05), (.34, .33, .265))
cube("dark chalkboard", (.64, .014, .71), (1.62, 1.984, 2.05), (.14, .19, .18))
for i in range(10):
    x = 1.36 + random.random()*.40
    z = 1.82 + random.random()*.40
    pipe("faint chalk mark", (x, 1.974, z), (x+.08, 1.974, z+.02), .002, (.28, .32, .285))
cube("paper notice", (.26, .014, .60), (2.015, 2.014, 1.71), (.76, .76, .65))
for j in range(11):
    cube("notice printing", (.20, .003, .006), (2.015, 2.003, 1.94-j*.034), (.44, .45, .38))

fx = 1.48
cube("red emergency mounting plate", (.32, .065, .54), (fx, 1.955, 1.10), (.73, .047, .018))
sphere("rounded emergency head", (fx, 1.91, 1.36), .16, (.79, .065, .026), (1, .40, .85))
cube("emergency body", (.235, .13, .38), (fx, 1.89, 1.12), (.80, .055, .022))
for x in [fx-.055, fx+.045]:
    pipe("emergency handle", (x, 1.803, 1.32), (x, 1.803, 1.43), .018, ivory)
pipe("handle crossbar", (fx-.055, 1.803, 1.43), (fx+.045, 1.803, 1.43), .018, ivory)
cube("small dark label", (.10, .008, .085), (fx, 1.818, 1.10), (.25, .16, .085))

# Three-tier berth rack.
rack = Asset("Three tier sleeping rack")
xl, xr = -1.97, -.65
yf, yb = 1.55, 4.36
for x in [xl, xr]:
    for y in [yf, yb]:
        rack.include(f"post_{x}_{y}", rod(.023, start=(x, y, .05), end=(x, y, 2.83), color=iron))
for tier, z in enumerate([.65, 1.25, 1.80]):
    for x in [xl, xr]:
        rack.include(f"side_{tier}_{x}", rod(.022, start=(x, yf, z-.055), end=(x, yb, z-.055), color=iron))
    for y in [yf, yb]:
        rack.include(f"end_{tier}_{y}", rod(.023, start=(xl, y, z-.055), end=(xr, y, z-.055), color=iron))
    rack.include(f"canvas_{tier}", box((1.28, 2.75, .045), center=(-1.31, 2.955, z-.025), color=(.30, .34, .28)))
    rack.include(f"mattress_{tier}", fillet_box((1.24, 2.72, .105), radius=.04, center=(-1.31, 2.955, z+.05), color=(.61, .65, .57)))
    rack.include(f"pillow_{tier}", fillet_box((.85, .45, .12), radius=.055, center=(-1.32, 4, z+.15), color=(.73, .75, .65)))
    for k in range(7):
        yy = 1.69+k*.35
        rack.include(f"seam_{tier}_{k}", rod(.005, start=(-.684, yy, z+.025), end=(-.684, yy+.16, z+.03), color=(.39, .43, .36)))
scene.include("bunks", rack)
pipe("rack upper rail", (-.65, yf, 2.81), (-.65, yb, 2.81), .024, iron)
pipe("rack upper crosspiece", (-1.97, yf, 2.81), (-.65, yf, 2.81), .024, iron)
cube("hanging coat", (.22, .32, .83), (-.78, 4.12, 1.91), (.035, .055, .059))
sphere("coat shoulder", (-.78, 4.12, 2.29), .17, (.045, .065, .061), (1, .8, .5))

# Louvered machinery cabinets on the left shelf.
for yy in [-.07, .62, 1.31]:
    cube("blue green machinery cabinet", (.48, .59, .89), (-1.76, yy, .94), (.040, .085, .095))
    cube("cabinet top lip", (.54, .64, .045), (-1.76, yy, 1.40), (.07, .12, .12))
    cube("cabinet door", (.022, .49, .78), (-1.506, yy, .94), (.045, .095, .11))
    for k in range(18):
        cube("louver", (.026, .37, .010), (-1.490, yy, .59+k*.039), (.22, .29, .27))
    pipe("cabinet trim", (-1.478, yy-.24, .53), (-1.478, yy-.24, 1.33), .010, (.11, .17, .16))
cube("long green shelf", (.74, 3.08, .075), (-1.74, .04, .43), (.035, .075, .057))
for yy in [-1.28, 1.4]:
    pipe("shelf leg", (-1.43, yy, .03), (-1.43, yy, .43), .025, iron)

# High cream heater with broad dark grille.
cube("wall heater", (.25, .63, .78), (-1.905, .36, 2.24), (.61, .61, .49))
cube("heater dark opening", (.022, .49, .52), (-1.766, .36, 2.24), (.035, .055, .047))
for z in [2.02, 2.12, 2.22, 2.32, 2.42]:
    cube("heater grille bar", (.035, .52, .033), (-1.747, .36, z), (.60, .61, .49))
cube("heater badge", (.025, .20, .055), (-1.746, .36, 2.54), (.29, .30, .24))
pipe("heater conduit", (-1.99, .38, 1.82), (-1.99, .38, 1.43), .022, (.34, .37, .30))
sphere("wall valve", (-1.98, .92, 1.56), .09, (.20, .23, .18), (.4, 1, 1))

# Rear metal lockers.
for x in [-.51, .05, .61]:
    cube("locker body", (.54, .54, 1.88), (x, 5.52, 1.09), (.36, .40, .35))
    cube("locker door", (.49, .035, 1.77), (x, 5.228, 1.10), (.41, .45, .39))
    for z in [1.73, 1.80, 1.87, 1.94, .33, .40, .47]:
        cube("locker vent", (.28, .012, .013), (x, 5.204, z), (.20, .24, .20))
    cube("locker latch", (.035, .034, .15), (x+.17, 5.192, 1.11), (.12, .15, .12))
    cube("locker nameplate", (.14, .013, .064), (x, 5.196, 1.59), (.62, .63, .51))
    for z in [.38, 1.66]:
        cube("locker hinge", (.035, .03, .09), (x-.235, 5.20, z), (.25, .28, .24))
    sphere("bedding above lockers", (x, 5.5, 2.09), .23, (.43, .45, .35), (1, .8, .48))

# Black pipework around the equipment.
for x in [.96, 1.28]:
    pipe("rear vertical service pipe", (x, 4.71, .10), (x, 4.71, 3.35), .031, iron)
pipe("rear pipe crossover", (.96, 4.71, 3.35), (-.91, 4.71, 3.35), .033, iron)
pipe("bent rear line", (-.91, 4.71, 3.35), (-.91, 4.71, 2.47), .029, iron)
pipe("equipment pipe", (.96, 4.71, 1.05), (1.71, 4.71, 1.05), .025, iron)
pipe("equipment horizontal service", (.96, 4.71, 1.65), (1.67, 4.71, 1.65), .020, iron)
cube("rear equipment housing", (.77, .65, .93), (.69, 4.37, .51), (.18, .20, .17))
cube("equipment top", (.86, .73, .065), (.69, 4.37, 1), (.28, .29, .24))
cube("equipment front inset", (.57, .018, .66), (.69, 4.032, .52), (.22, .24, .20))
for x in [.34, 1.04]:
    pipe("equipment corner frame", (x, 4.01, .07), (x, 4.01, .98), .022, (.12, .14, .11))
sphere("brass valve", (.99, 4.67, 1.18), .065, (.42, .34, .16))

# Slightly angled chair in the narrow aisle.
chair = Asset("Pale metal chair")
cx, cy = -.19, 3.77
chair.include("seat", box((.47, .45, .07), center=(cx, cy, .48), color=(.43, .43, .31)))
for i, x in enumerate([cx-.20, cx+.20]):
    for j, y in enumerate([cy-.18, cy+.18]):
        chair.include(f"leg_{i}_{j}", rod(.020, start=(x, y, .035), end=(x, y, .47), color=(.49, .49, .36)))
    chair.include(f"back_post_{i}", rod(.022, start=(x, cy+.18, .44), end=(x, cy+.25, 1.05), color=(.52, .52, .39)))
chair.include("back", box((.44, .065, .24), center=(cx, cy+.238, .91), color=(.32, .35, .27)))
for i, x in enumerate([cx-.245, cx+.245]):
    chair.include(f"arm_{i}", rod(.022, start=(x, cy-.13, .68), end=(x, cy+.20, .72), color=(.54, .53, .39)))
    chair.include(f"arm_support_{i}", rod(.018, start=(x, cy-.13, .48), end=(x, cy-.13, .68), color=(.49, .49, .36)))
chair.turn("+z", 12)
scene.include("chair", chair)

# Cropped bench and dark doorway edge.
cube("right bench seat", (.59, 2.14, .075), (1.63, -1.01, .47), (.020, .070, .045))
for yy in [-1.92, -.13]:
    for xx in [1.40, 1.86]:
        pipe("bench leg", (xx, yy, .015), (xx, yy, .44), .027, iron)
pipe("bench stretcher", (1.64, -1.92, .18), (1.64, -.13, .18), .022, iron)
cube("right doorway jamb", (.17, .20, 3.85), (1.81, -1.38, 1.91), (.25, .105, .045))

# Suspended lamps, with fully visible glowing lower surfaces.
lamps = [(-.31, -.64, 2.96), (-.40, 2.85, 2.93), (.02, 5.22, 2.94)]
for x, y, z in lamps:
    pipe("lamp suspension", (x, y, z+.12), (x, y, 3.76), .019, (.09, .11, .085))
    sphere("lamp metal shade", (x, y, z), .235, (.22, .25, .21), (1, 1, .35))
    pipe("lamp neck", (x, y, z+.015), (x, y, z+.17), .047, (.22, .24, .19))
    sphere("lamp bright underside", (x, y, z-.087), .218, (1, .99, .87), (1, 1, .10))

realize(scene)

for material in bpy.data.materials:
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    bsdf.inputs["Roughness"].default_value = .65
    if c[0] > .95 and c[1] > .9:
        bsdf.inputs["Emission Color"].default_value = (1, .98, .86, 1)
        bsdf.inputs["Emission Strength"].default_value = 7
    if abs(c[0]-floorcolor[0]) < .01 and abs(c[1]-floorcolor[1]) < .01:
        bsdf.inputs["Roughness"].default_value = .32
        noise = material.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 110
        noise.inputs["Detail"].default_value = 2
        bump = material.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .10
        bump.inputs["Distance"].default_value = .012
        material.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        material.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

set_view(position=(.10, -3.72, 1.75), target=(-.10, 3.40, 1.40), lens=27.5, sensor=36)
area_emitter((-.31, -.64, 2.82), power=125, size=.48, target=(-.4, .1, 0), color=(1, .95, .83))
area_emitter((-.4, 2.85, 2.79), power=95, size=.40, target=(-.4, 3, .1), color=(.88, .96, 1))
area_emitter((.02, 5.22, 2.80), power=70, size=.36, target=(0, 5.4, .4), color=(1, .97, .85))
area_emitter((.4, -2.5, 2.8), power=55, size=3, target=(0, 2, 1), color=(1, .85, .65))
area_emitter((-1.6, 3.5, 2.65), power=35, size=1.8, target=(-.3, 3.7, 1.2), color=(.85, .91, 1))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Compartment ambient")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (.18, .20, .16, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = .16
sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = -.30
sc.render.image_settings.file_format = "PNG"
