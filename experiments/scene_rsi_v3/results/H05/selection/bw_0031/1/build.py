# Reference inventory, estimated from the room photograph in the collage:
# - The room photograph occupies approximately x=.03-.94, y=.65-1.00.
#   Within that inset, the pale instrument wall fills the upper-left background;
#   its grille is near (.34,.34), and square meters flank the grille.
# - The large console runs from the cropped lower-left foreground to about
#   (.70,.40), with a broad pale sloping face and a dark front/base. Its long
#   edges rise toward the right. It occludes the lower part of the meter wall.
# - The smaller independent console is at the right, around (.81-.99,.32-.65),
#   with a dark base. A tall dark doorway stands just to its left.
# - Floor fills the lower-right foreground. The ceiling and room corners are
#   cropped or uncertain. The separately pictured yellow GRID panel's precise
#   position in the room photograph cannot be established.
#
# Feedback comparison, using the room inset as the reference composition:
# 1. The previous render leaves roughly the top third empty and shows the outer
#    edges of a stage-like floor. The photograph is cropped inside the room.
#    Extend the enclosing walls and floor beyond the view, and increase the lens:
#    the console and wall should move outward while empty margins shrink.
# 2. The rendered console runs approximately (.08,.56)-(.89,.73), with a
#    shallow diagonal; the photo runs from the lower-left toward (.70,.40)
#    within the inset. Move the camera toward the near end of the console to
#    strengthen its diagonal and bring its near edge toward the lower left.
# 3. The rendered right console is partly hidden and the dark doorway is absent.
#    Move the small desk rightward and add the visible tall doorway; the desk
#    should separate from the large console and the doorway should appear between
#    the wall instruments and the small desk.
# 4. The rendered surfaces are much brighter than the photograph. Reduce light
#    strength and darken the floor and console base; brightness also depends on
#    surface orientation and illumination.
# Camera trials below print individual projected points. Reference coordinates
# are approximate portrait-frame adaptations of the landscape room inset; they
# are distinct from the observed contour estimates above and remain uncertain.
#
# Estimated expanded primitives: architecture 7, instrument bank 119,
# main desk 106, small console 19, GRID board 28, fixtures 3; about 282 total.
# Each box and rod is one primitive. No Boolean operations or filleted boxes.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s_Grid_Control_Room")

# Major dimensions and camera parameters are independent.
X0, X1 = -4.5, 2.15
DESK_Y = -0.05
DESK_CX = (X0 + X1) / 2
DESK_LENGTH = X1 - X0
FACE_Y, FACE_Z, FACE_ANGLE = DESK_Y + .18, 1.07, 22
CAMERA_POSITION = (-7.4, -6.0, 2.75)
CAMERA_TARGET = (-.3, 1.5, 1.35)
CAMERA_LENS = 37

wall = (.68, .66, .62)
ivory = (.70, .69, .65)
paper = (.83, .81, .75)
panel = (.72, .71, .67)
floor_color = (.25, .23, .20)
base = (.13, .12, .105)
dark = (.055, .052, .047)
metal = (.30, .29, .27)
yellow = (.88, .60, .065)
red = (.75, .025, .015)
amber = (.95, .38, .015)

# Large enclosing surfaces prevent room edges appearing as a stage.
architecture = Asset("Architecture")
architecture.include("Floor", box((30, 24, .12), (0, 0, -.06), floor_color))
architecture.include("Instrument_wall", box((24, .12, 5.0), (0, 3.45, 2.5), wall))
architecture.include("Right_wall", box((.12, 24, 5.0), (5.5, -4.0, 2.5), wall))
architecture.include("Back_baseboard", box((24, .05, .12), (0, 3.36, .06), base))
# Dark opening with a pale border, positioned beside the right console.
architecture.include("Door_opening", box((.70, .035, 1.85), (3.35, 3.36, 1.05), dark))
architecture.include("Door_frame_left", box((.08, .06, 1.98), (2.96, 3.32, 1.08), paper))
architecture.include("Door_frame_right", box((.08, .06, 1.98), (3.74, 3.32, 1.08), paper))
scene.include("Architecture", architecture)

bank = Asset("Wall_instrument_bank")
bank.include("Cabinet_back", box((6.9, .16, 2.6), (-1.35, 3.30, 1.55), ivory))
for i in range(10):
    x = -4.62 + i * .70
    bank.include("Cabinet_joint_%02d" % i,
                 box((.012, .016, 2.5), (x, 3.205, 1.55), metal))
for col in list(range(5)) + list(range(8, 12)):
    x = -4.32 + col * .46
    for row in range(4):
        z = 1.04 + row * .42
        bank.include("Meter_frame_%02d_%02d" % (col, row),
                     box((.32, .035, .30), (x, 3.18, z), dark))
        bank.include("Meter_face_%02d_%02d" % (col, row),
                     box((.255, .014, .235), (x, 3.155, z), paper))
bank.include("Grille_mount", box((1.30, .04, .77), (-1.12, 3.16, 1.69), panel))
for i in range(8):
    bank.include("Vent_slot_%02d" % i,
                 box((1.16, .018, .036), (-1.12, 3.13, 1.40 + i*.075), dark))
scene.include("Wall_instrument_bank", bank)

desk = Asset("Main_control_console")
desk.include("Dark_base", box((DESK_LENGTH, 1.55, .76),
                              (DESK_CX, DESK_Y, .38), base))
desk.include("Front_fascia", box((DESK_LENGTH, .065, .44),
                                 (DESK_CX, DESK_Y-.80, .53), metal))
desk.include("Writing_ledge", box((DESK_LENGTH, .43, .075),
                                  (DESK_CX, DESK_Y-.67, .85), paper))
desk.include("Ledge_front_trim", box((DESK_LENGTH, .035, .065),
                                     (DESK_CX, DESK_Y-.88, .84), dark))
face = box((DESK_LENGTH, 1.12, .085), (DESK_CX, FACE_Y, FACE_Z), panel)
face.turn(axis="x", degrees=FACE_ANGLE)
desk.include("Inclined_control_surface", face)

a = math.radians(FACE_ANGLE)
def surface(x, v, lift=.055):
    return (x, FACE_Y + v*math.cos(a) - lift*math.sin(a),
            FACE_Z + v*math.sin(a) + lift*math.cos(a))

for bay in range(8):
    x = X0 + .42 + bay*.81
    seam = box((.018, 1.02, .01), surface(x-.35, 0), dark)
    seam.turn(axis="x", degrees=FACE_ANGLE)
    desk.include("Panel_division_%02d" % bay, seam)
    for row in range(3):
        for col in range(3):
            p = surface(x-.21+col*.20, -.34+row*.30, .065)
            desk.include("Control_%02d_%02d_%02d" % (bay, row, col),
                         rod(.030, start=p,
                             end=(p[0], p[1]-.025, p[2]+.055), color=dark))
    if bay % 2 == 0:
        rim = box((.35, .16, .018), surface(x, .42, .065), dark)
        rim.turn(axis="x", degrees=FACE_ANGLE)
        desk.include("Meter_rim_%02d" % bay, rim)
        face_piece = box((.28, .11, .02), surface(x, .42, .078), paper)
        face_piece.turn(axis="x", degrees=FACE_ANGLE)
        desk.include("Meter_face_%02d" % bay, face_piece)
scene.include("Main_control_console", desk)

small = Asset("Right_independent_console")
small_x, small_y = 4.60, 2.50
small.include("Dark_pedestal", box((1.25, .82, .72),
                                   (small_x, small_y, .36), base))
small.include("Writing_ledge", box((1.35, .38, .07),
                                   (small_x, small_y-.40, .82), paper))
sf = box((1.35, .68, .08), (small_x, small_y, 1.00), panel)
sf.turn(axis="x", degrees=22)
small.include("Inclined_face", sf)
for i in range(7):
    for j in range(2):
        x = small_x-.52+i*.17
        y = small_y-.18+j*.25
        z = 1.00+(y-small_y)*math.tan(math.radians(22))+.07
        small.include("Control_%d_%d" % (i,j),
                      rod(.025, start=(x,y,z), end=(x,y-.015,z+.05), color=dark))
scene.include("Right_independent_console", small)

# The separate yellow reference panel is mounted on the wall as an editable
# interpretive placement; its exact placement in the old photograph is unknown.
grid = Asset("GRID_single_line_mimic_board")
gx, gy, gz = 2.25, 3.25, 2.35
grid.include("Yellow_face", box((.90, .08, 1.30), (gx, gy, gz), yellow))
fy = gy - .055
grid.include("Vertical_bus", box((.027, .018, 1.13), (gx+.08, fy, gz), dark))
for i, z in enumerate((1.94, 2.30, 2.66)):
    grid.include("Bus_cross_%d" % i, box((.48, .018, .027), (gx+.08, fy, z), dark))
    for side in (-1, 1):
        x = gx+.08+side*.20
        grid.include("Branch_%d_%d" % (i, side),
                     box((.027, .018, .17), (x, fy, z+.07), dark))
        grid.include("Amber_lamp_%d_%d" % (i, side),
                     box((.07, .024, .07), (x, fy-.025, z+.07), amber))
for i in range(4):
    z = 1.92+i*.27
    grid.include("Red_lamp_%d" % i,
                 rod(.048, start=(gx-.30, fy-.02, z),
                     end=(gx-.30, fy-.07, z), color=red))
    grid.include("Selector_%d" % i,
                 rod(.031, start=(gx-.17, fy-.02, z),
                     end=(gx-.17, fy-.07, z), color=dark))
for i, z in enumerate((1.80, 2.90)):
    grid.include("Label_plate_%d" % i,
                 box((.27, .02, .075), (gx+.24, fy-.025, z), paper))
scene.include("GRID_single_line_mimic_board", grid)

fixtures = Asset("Fluorescent_fixtures")
for i, x in enumerate((-3.0, 0, 3.0)):
    fixtures.include("Troffer_%d" % i,
                     box((1.55, .38, .035), (x, .8, 3.48), paper))
scene.include("Fluorescent_fixtures", fixtures)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .68, .64, 1)
background.inputs["Strength"].default_value = .32

# Preserve the input aspect while providing at least 1920 pixels in width.
sc.render.resolution_x = 1920
sc.render.resolution_y = 2629
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
panorama = sc.camera
panorama.name = "Camera_Panorama"
area_emitter((-2, -1, 3.3), power=320, size=4, target=(-1, 1, 1))
area_emitter((3, 1, 3.3), power=260, size=3, target=(2, 2, 1))

# Reference estimates are adapted to a portrait view and are uncertain because
# the original room photograph is a landscape inset. The points are on actual
# final geometry, not empty origins or room bounding boxes.
landmarks = [
    ("grille center", (-1.12, 3.12, 1.69), (.32, .36)),
    ("near ledge corner", (X0, DESK_Y-.88, .85), (.03, .76)),
    ("far face corner", (X1, FACE_Y+.52, FACE_Z+.23), (.72, .49)),
    ("door top", (3.35, 3.34, 1.975), (.80, .34)),
    ("small console top", (small_x, small_y+.28, 1.12), (.90, .48)),
]

def report(title):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = panorama.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print(title)
    result = []
    for name, p, ref in landmarks:
        clip = matrix @ panorama.matrix_world.inverted() @ Vector((*p, 1))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print("%-22s reference=%s projected=%s" %
              (name, ref, None if uv is None else tuple(round(v, 3) for v in uv)))
        result.append(uv)
    return result

initial = report("Initial camera")
# A modest wider-lens trial is used only if the foreground corner or both right
# background landmarks fall far outside the frame. Compare every anchor and
# restore the original lens if a previously visible anchor becomes cropped.
if (initial[1] is None or initial[1][0] < -.10 or initial[1][1] > 1.10 or
    all(initial[i] is None or initial[i][0] > 1.10 for i in (3, 4))):
    old_lens = panorama.data.lens
    panorama.data.lens = old_lens * .90
    trial = report("Candidate wider lens")
    def visible(u):
        return u is not None and -.03 <= u[0] <= 1.03 and -.03 <= u[1] <= 1.03
    if any(visible(initial[i]) and not visible(trial[i]) for i in range(len(initial))):
        panorama.data.lens = old_lens
        print("Restored initial lens after an anchor regression.")
report("Final active panorama")

# Second editable camera for the controls and the GRID board.
set_view((.7, -3.7, 2.5), (1.2, 2.2, 1.55), lens=40)
sc.camera.name = "Camera_Console_GRID_Detail"
sc.camera = panorama

def label(name, body, location):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = .028
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, 0)

label("Label_Fehlerstelle_top", "FEHLERSTELLE", (gx+.24, fy-.04, 2.90))
label("Label_Fehlerstelle_bottom", "FEHLERSTELLE", (gx+.24, fy-.04, 1.80))

# Give the small red and amber indicator materials a restrained self-emission.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    if c[0] > .7 and c[1] < .5 and c[2] < .1:
        bsdf.inputs["Emission Color"].default_value = (c[0], c[1], c[2], 1)
        bsdf.inputs["Emission Strength"].default_value = .35

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
sc.render.image_settings.file_format = "PNG"
