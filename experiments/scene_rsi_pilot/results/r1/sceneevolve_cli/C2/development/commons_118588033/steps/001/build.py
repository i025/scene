from sceneact import *
import bpy
import math

# World: X across the room, Y toward its rear, Z upward.
CAMERA_POSITION = (0.90, -3.60, 1.65)
CAMERA_TARGET = (-0.15, 4.50, 1.60)
CAMERA_LENS = 28
ROOM_WIDTH = 4.25
ROOM_DEPTH = 9.2
CEILING_HEIGHT = 3.85
BUNK_LENGTH = 3.35
BUNK_WIDTH = 1.08
COLUMN_POSITION = (1.45, -1.00)

scene = Scene("Shipboard compartment")

cream = (0.57, 0.56, 0.43)
wallcream = (0.66, 0.66, 0.54)
ceilingcream = (0.47, 0.46, 0.35)
rust = (0.29, 0.105, 0.065)
floorred = (0.32, 0.135, 0.09)
black = (0.035, 0.045, 0.039)
steel = (0.32, 0.35, 0.32)
pale = (0.66, 0.68, 0.61)
green = (0.035, 0.105, 0.085)
bluegreen = (0.075, 0.15, 0.17)

def block(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def pipe(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

architecture = Asset("Room shell")
block(architecture, "Painted deck", (4.8, 10.5, .12),
      (0, 1.65, -.08), floorred)
block(architecture, "Left wall", (.16, 10.5, 3.9),
      (-2.05, 1.65, 1.9), wallcream)
block(architecture, "Rear wall", (4.3, .16, 3.9),
      (0, 6.8, 1.9), wallcream)
block(architecture, "Right wall", (.16, 10.5, 3.9),
      (2.2, 1.65, 1.9), wallcream)
block(architecture, "Ceiling", (4.5, 10.5, .16),
      (.05, 1.65, CEILING_HEIGHT+.08), ceilingcream)
block(architecture, "Right lower wall paint", (.025, 10.5, .64),
      (2.106, 1.65, .32), rust)
block(architecture, "Rear skirting", (4.2, .035, .32),
      (0, 6.70, .16), rust)
block(architecture, "Left skirting", (.035, 10.5, .24),
      (-1.95, 1.65, .12), rust)

# Broad structural members and exposed overhead framing.
for i, y in enumerate((-1.4, .55, 2.5, 4.5, 6.3)):
    block(architecture, f"Transverse ceiling beam {i}",
          (4.25, .16, .28), (.02, y, 3.69), (.39, .29, .18))
for i, x in enumerate((-1.5, -.6, .35, 1.25)):
    block(architecture, f"Long ceiling rib {i}",
          (.075, 9.2, .19), (x, 1.8, 3.75), (.50, .40, .27))
for i, y in enumerate((-.8, 1.4, 3.6)):
    pipe(architecture, f"Diagonal brace {i}",
         (-1.9, y, 2.93), (-1.15, y, 3.70), .045, cream)
scene.include("Architecture", architecture)

column = Asset("Prominent support column")
cx, cy = COLUMN_POSITION
pipe(column, "Upper cream column", (cx, cy, 1.48),
     (cx, cy, 4.12), .107, (.64, .52, .29))
pipe(column, "Lower brown column", (cx, cy, .06),
     (cx, cy, 1.48), .109, (.26, .105, .055))
pipe(column, "Foot collar", (cx, cy, .025),
     (cx, cy, .075), .145, (.36, .20, .12))
pipe(column, "Paint boundary collar", (cx, cy, 1.46),
     (cx, cy, 1.49), .112, (.72, .66, .45))
scene.include("Column", column)

# Three stacked berths, with open space between their thin frames.
bunks = Asset("Three tier left berths")
front_y, rear_y = .88, .88 + BUNK_LENGTH
for i, x in enumerate((-1.88, -.70)):
    for j, y in enumerate((front_y, rear_y)):
        pipe(bunks, f"Upright {i} {j}", (x, y, .06),
             (x, y, 2.58), .025, black)
for level, z in enumerate((.60, 1.26, 1.93)):
    block(bunks, f"Berth base {level}",
          (BUNK_WIDTH, BUNK_LENGTH, .055),
          (-1.30, 2.555, z), (.16, .19, .17))
    block(bunks, f"Off white mattress {level}",
          (1.02, 3.20, .115),
          (-1.30, 2.56, z+.085), (.64, .66, .59))
    block(bunks, f"Folded bedding {level}",
          (.94, .62, .075),
          (-1.30, 3.67, z+.175), (.76, .75, .65))
    block(bunks, f"Pillow {level}",
          (.70, .40, .14),
          (-1.30, 3.97, z+.19), (.73, .73, .65))
    for side, x in enumerate((-1.85, -.73)):
        pipe(bunks, f"Side rail {level} {side}",
             (x, front_y-.03, z+.02),
             (x, rear_y+.03, z+.02), .023, black)
    pipe(bunks, f"Front crossbar {level}",
         (-1.87, front_y, z+.02), (-.69, front_y, z+.02),
         .023, black)
# Long dark fabric hanging near rear bunk post.
block(bunks, "Hanging dark garment", (.25, .15, .64),
      (-.77, 3.77, 1.91), (.055, .075, .074))
scene.include("Bunks", bunks)

equipment = Asset("Foreground left vented equipment")
block(equipment, "Long dark support shelf", (.88, 2.10, .10),
      (-1.60, -.26, .53), green)
for i, y in enumerate((-.84, -.12, .57)):
    block(equipment, f"Equipment body {i}", (.58, .60, .90),
          (-1.64, y, 1.03), bluegreen)
    block(equipment, f"Recessed front {i}", (.022, .49, .76),
          (-1.337, y, 1.04), (.035, .065, .07))
    for j in range(12):
        block(equipment, f"Vent slat {i} {j}",
              (.035, .43, .019), (-1.316, y, .72+j*.052),
              (.22, .29, .28))
    block(equipment, f"Upper rim {i}", (.63, .64, .055),
          (-1.64, y, 1.51), (.095, .14, .14))
    pipe(equipment, f"Handle {i}",
         (-1.29, y-.10, 1.42), (-1.29, y+.10, 1.42),
         .013, (.48, .48, .38))
for i, y in enumerate((-1.1, .65)):
    pipe(equipment, f"Shelf leg {i}", (-1.30, y, .04),
         (-1.30, y, .5), .025, black)
block(equipment, "Lower long green ledge", (.90, 3.1, .075),
      (-1.60, -.20, .30), green)
scene.include("Left equipment", equipment)

# Wall-mounted louvered ventilation box above the foreground machines.
vent = Asset("Left wall ventilation housing")
block(vent, "Housing", (.26, .65, .88),
      (-1.82, .10, 2.49), (.53, .55, .47))
block(vent, "Dark louver opening", (.025, .51, .53),
      (-1.677, .10, 2.43), (.045, .065, .065))
for i in range(6):
    block(vent, f"Louver {i}", (.08, .53, .035),
          (-1.64, .10, 2.21+i*.085), (.62, .64, .55))
block(vent, "Small label", (.018, .21, .085),
      (-1.676, .10, 2.81), (.26, .31, .30))
scene.include("Wall vent", vent)

machines = Asset("Rear machinery and lockers")
block(machines, "Tall gray cabinet", (1.13, .57, 1.69),
      (-.12, 4.83, 1.27), (.42, .45, .41))
block(machines, "Cabinet top", (1.19, .62, .075),
      (-.12, 4.83, 2.14), (.51, .53, .47))
for i, x in enumerate((-.43, .05, .37)):
    block(machines, f"Door seam {i}", (.012, .016, 1.47),
          (x, 4.533, 1.29), (.18, .22, .20))
for i in range(9):
    block(machines, f"Cabinet vents {i}", (.24, .025, .023),
          (-.40, 4.524, 1.20+i*.075), (.64, .66, .58))
for i in range(5):
    pipe(machines, f"Door fastener {i}", (.36, 4.50, .77+i*.25),
         (.36, 4.47, .77+i*.25), .025, (.17, .20, .18))
for i, x in enumerate((-.47, -.12, .23)):
    pipe(machines, f"Top pipe stub {i}", (x, 4.83, 2.14),
         (x, 4.83, 2.36), .078, (.44, .47, .43))
block(machines, "Foreground machine pedestal", (.91, .74, .87),
      (.60, 3.93, .51), (.20, .23, .21))
block(machines, "Pedestal top plate", (.99, .80, .065),
      (.60, 3.93, .98), (.31, .32, .27))
for i, x in enumerate((.27, .65, .91)):
    pipe(machines, f"Vertical control pipe {i}",
         (x, 3.91, .99), (x, 3.91, 1.76+i*.13),
         .024, black)
    pipe(machines, f"Valve crossbar {i}",
         (x-.09, 3.91, 1.58), (x+.09, 3.91, 1.58),
         .018, (.38, .38, .29))
scene.include("Rear machinery", machines)

chair = Asset("Pale chair")
block(chair, "Seat", (.48, .46, .075),
      (-.36, 3.70, .49), (.55, .56, .43))
block(chair, "Back pad", (.43, .07, .37),
      (-.36, 3.93, .88), (.62, .61, .47))
for i, x in enumerate((-.56, -.16)):
    for j, y in enumerate((3.51, 3.89)):
        pipe(chair, f"Leg {i} {j}", (x, y, .03),
             (x, y, .48), .018, (.54, .54, .42))
    pipe(chair, f"Back support {i}", (x, 3.91, .43),
         (x, 3.96, 1.07), .019, (.63, .62, .46))
scene.include("Chair", chair)

wall_objects = Asset("Right wall fixtures")
# Fixtures face into the room from the right wall.
block(wall_objects, "Dark rectangular notice board", (.055, 1.18, .88),
      (2.075, 2.19, 2.03), (.21, .25, .23))
for i, z in enumerate((1.57, 2.49)):
    block(wall_objects, f"Board horizontal border {i}",
          (.075, 1.23, .027), (2.037, 2.19, z),
          (.43, .43, .33))
block(wall_objects, "White instruction placard", (.025, .60, .72),
      (2.065, .81, 1.78), (.76, .75, .63))
for i in range(6):
    block(wall_objects, f"Placard printed line {i}",
          (.012, .38, .012), (2.045, .81, 1.62+i*.055),
          (.39, .41, .36))
block(wall_objects, "Emergency red backing", (.07, .38, .61),
      (2.02, 1.50, 1.04), (.66, .065, .035))
pipe(wall_objects, "Red extinguisher cylinder",
     (1.93, 1.50, .86), (1.93, 1.50, 1.25),
     .10, (.73, .085, .037))
block(wall_objects, "Extinguisher pale label", (.025, .12, .16),
      (1.823, 1.50, 1.08), (.80, .73, .52))
pipe(wall_objects, "Extinguisher neck",
     (1.93, 1.50, 1.25), (1.93, 1.50, 1.34),
     .035, (.22, .23, .18))
pipe(wall_objects, "Extinguisher handle",
     (1.89, 1.40, 1.34), (1.89, 1.58, 1.34),
     .025, (.10, .12, .10))
scene.include("Wall fixtures", wall_objects)

bench = Asset("Cropped right foreground bench")
block(bench, "Green seat", (.58, 2.06, .075),
      (2.00, -1.52, .48), green)
for i, y in enumerate((-2.30, -.76)):
    for j, x in enumerate((1.78, 2.20)):
        pipe(bench, f"Bench leg {i} {j}",
             (x, y, .015), (x, y, .45), .021, black)
block(bench, "Right foreground brown edge", (.15, .22, 2.4),
      (2.25, -2.10, 1.20), (.30, .14, .07))
scene.include("Foreground bench", bench)

services = Asset("Exposed pipes cables and lamps")
# Pale pipes follow the upper left side.
for i, x in enumerate((-1.70, -1.25)):
    pipe(services, f"Long overhead pipe {i}",
         (x, -2.0, 3.16+i*.17),
         (x, 5.90, 3.16+i*.17), .042, (.69, .70, .60))
for i, y in enumerate((-.25, 1.90, 4.00)):
    pipe(services, f"Pipe cross connection {i}",
         (-1.76, y, 3.17), (.90, y, 3.17),
         .034, (.62, .64, .55))
    pipe(services, f"Pipe hanger {i}",
         (-1.25, y, 3.30), (-1.25, y, 3.75),
         .018, (.25, .28, .24))
# Black utility runs and rear risers.
pipe(services, "Black horizontal utility",
     (-1.50, 3.90, 2.89), (1.32, 3.90, 2.89), .035, black)
for i, x in enumerate((.70, 1.07)):
    pipe(services, f"Rear black riser {i}",
         (x, 5.20, .55), (x, 5.20, 3.42), .031, black)
    pipe(services, f"Rear riser elbow {i}",
         (x, 5.20, 3.42), (x-.38, 5.20, 3.42), .031, black)
for i, x in enumerate((-.40, .05, .50)):
    pipe(services, f"Rear pale service {i}",
         (x, 6.46, 1.90), (x, 6.46, 3.66),
         .045, (.55, .56, .46))

lamp_positions = [(-.82, -.20, 3.12),
                  (-.55, 2.32, 2.97),
                  (-.20, 4.35, 2.91)]
for i, (x, y, z) in enumerate(lamp_positions):
    pipe(services, f"Lamp suspension {i}",
         (x, y, z+.11), (x, y, 3.78), .018, black)
    # Broad shallow cone with a white underside.
    services.include(f"Enamel shade {i}",
        rod(radius=.22 if i == 0 else .16,
            start=(x, y, z), end=(x, y, z+.065),
            color=(.64, .68, .64)))
    services.include(f"White lamp underside {i}",
        rod(radius=.205 if i == 0 else .15,
            start=(x, y, z-.012), end=(x, y, z),
            color=(.96, .98, .91)))
    pipe(services, f"Shade cap {i}",
         (x, y, z+.06), (x, y, z+.16), .07,
         (.24, .29, .28))
scene.include("Overhead services", services)

realize(scene)
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

# Broad lighting preserves the dim, warm industrial interior.
area_emitter((-.55, -.5, 3.30), power=170, size=2.1,
             target=(-.6, 1.0, .4), color=(1.0, .88, .70))
area_emitter((-.35, 2.55, 3.12), power=130, size=1.4,
             target=(-.2, 3.3, .5), color=(.86, .94, 1.0))
area_emitter((.2, 5.75, 3.20), power=110, size=1.7,
             target=(0, 4.3, 1.2), color=(1.0, .94, .79))
area_emitter((.45, -3.0, 2.65), power=100, size=3.0,
             target=(.3, 1.6, 1.2), color=(1.0, .89, .75))

bs = bpy.context.scene
if bs.world is None:
    bs.world = bpy.data.worlds.new("Compartment ambient")
bs.world.use_nodes = True
bs.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
    .34, .38, .39, 1)
bs.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .20

# Modest material roughness; a slightly reflective painted deck.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat is None:
            continue
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Roughness"].default_value = .69
            base = shader.inputs["Base Color"].default_value
            if base[0] > .9 and base[1] > .9 and base[2] > .8:
                if "Emission Color" in shader.inputs:
                    shader.inputs["Emission Color"].default_value = (
                        .9, .96, 1.0, 1)
                    shader.inputs["Emission Strength"].default_value = 1.6
            if .27 < base[0] < .35 and .10 < base[1] < .16:
                shader.inputs["Roughness"].default_value = .38
