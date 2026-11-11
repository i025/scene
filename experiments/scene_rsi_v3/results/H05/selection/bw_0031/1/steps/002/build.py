# Reference and feedback comparison (normalized image coordinates):
# The reference is a collage; the room photograph occupies x=.03-.94, y=.65-1.
# Within that photograph the instrument wall spans most of the upper left, the
# long console extends from the cropped near-left toward x~.70, and the smaller
# console sits at the right. The yellow GRID panel is separately photographed;
# its exact position in the room is uncertain.
# In the previous render the room occupied approximately x=0-1, y=.33-.84,
# with a large empty upper area and a ceiling slab obscuring the upper wall.
# The grille appeared near (.33,.46), the near console corner near (.22,.65),
# and its far end near (.73,.50). The small console was partly obscured at
# roughly (.68,.47). Those are observed estimates, not projected landmarks.
# The long console edge rose only mildly toward the right; in the photograph it
# rises more strongly. The previous main desk was also too narrow in apparent
# depth and its wall instruments too sparse. The room's far end is uncertain.
#
# Ranked corrections:
# 1. Remove the obstructing ceiling slab and place the camera inside the room;
#    increase the lens to fill the portrait image with the console and wall.
#    This moves foreground corners outward and reduces the large empty region.
# 2. Move the camera toward the left end of the desk. Its near end should move
#    left and down relative to its far end, strengthening the diagonal.
# 3. Deepen the console and enlarge its dark fascia; add an actual writing ledge,
#    varied controls, and a denser regular instrument bank.
# 4. Keep the smaller desk on the right and the yellow board as a separate,
#    editable wall feature. The board's exact wall position remains uncertain.
# Projection targets below refer to an adapted full-frame room composition,
# since the supplied photograph is a landscape inset in a portrait collage.
# Primitive estimate: architecture 5, wall bank ~125, main console ~180,
# small console ~25, GRID panel ~35, total ~370. No Boolean operations.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s_Control_Room")

# Independent dimensions, camera pose, target and lens.
ROOM_W, ROOM_D, ROOM_H = 10.0, 7.0, 3.5
X0, X1 = -4.3, 2.15
DESK_Y = -0.05
DESK_LENGTH = X1 - X0
DESK_CX = (X0 + X1) / 2
CAMERA_POSITION = (-6.7, -7.2, 3.35)
CAMERA_TARGET = (-0.35, 1.4, 1.35)
CAMERA_LENS = 32

ivory = (0.76, 0.75, 0.71)
wall = (0.79, 0.78, 0.74)
panel = (0.74, 0.73, 0.68)
paper = (0.88, 0.86, 0.79)
floor_color = (0.32, 0.30, 0.27)
base = (0.18, 0.17, 0.15)
dark = (0.085, 0.08, 0.07)
metal = (0.40, 0.39, 0.36)
yellow = (0.92, 0.67, 0.10)
red = (0.75, 0.025, 0.018)
amber = (0.96, 0.44, 0.025)

architecture = Asset("Architecture")
architecture.include("Floor", box((ROOM_W, ROOM_D, .12),
                                 (0, 0, -.06), floor_color))
architecture.include("Back_wall", box((ROOM_W, .12, ROOM_H),
                                     (0, 3.45, ROOM_H/2), wall))
architecture.include("Right_wall", box((.12, ROOM_D, ROOM_H),
                                      (4.95, 0, ROOM_H/2), wall))
architecture.include("Baseboard", box((ROOM_W, .05, .15),
                                      (0, 3.36, .075), base))
scene.include("Architecture", architecture)

# Cabinet faces and regular square meter arrays. The central dark grille interrupts
# the array, as in the photograph.
bank = Asset("Wall_instrument_bank")
bank.include("Cabinet_back", box((6.85, .16, 2.55),
                                 (-1.28, 3.30, 1.52), ivory))
for i in range(10):
    x = -4.55 + i * .70
    bank.include("Cabinet_joint_%02d" % i,
                 box((.014, .016, 2.45), (x, 3.205, 1.54), metal))
for col in list(range(5)) + list(range(8, 12)):
    x = -4.25 + col * .46
    for row in range(4):
        z = 1.05 + row * .42
        bank.include("Meter_frame_%02d_%02d" % (col, row),
                     box((.32, .035, .30), (x, 3.18, z), dark))
        bank.include("Meter_face_%02d_%02d" % (col, row),
                     box((.255, .014, .235), (x, 3.155, z), paper))
        bank.include("Meter_needle_%02d_%02d" % (col, row),
                     box((.012, .009, .085), (x+.025, 3.144, z), metal))
bank.include("Grille_mount", box((1.30, .04, .77),
                                 (-1.12, 3.16, 1.69), panel))
for i in range(8):
    bank.include("Vent_slot_%02d" % i,
                 box((1.16, .018, .036),
                     (-1.12, 3.13, 1.40+i*.075), dark))
scene.include("Wall_instrument_bank", bank)

# Main desk: dark supporting cabinet, horizontal writing surface, and sloped
# control surface. Positive y runs toward the wall.
desk = Asset("Main_control_console")
desk.include("Dark_base", box((DESK_LENGTH, 1.55, .76),
                              (DESK_CX, DESK_Y, .38), base))
desk.include("Front_fascia", box((DESK_LENGTH, .065, .44),
                                 (DESK_CX, DESK_Y-.80, .53), metal))
desk.include("Writing_ledge", box((DESK_LENGTH, .43, .075),
                                 (DESK_CX, DESK_Y-.67, .85), paper))
desk.include("Ledge_front_trim", box((DESK_LENGTH, .035, .065),
                                    (DESK_CX, DESK_Y-.88, .84), dark))
slope = 22
face_y, face_z = DESK_Y+.18, 1.08
face = box((DESK_LENGTH, 1.12, .085), (DESK_CX, face_y, face_z), panel)
face.turn(axis="x", degrees=slope)
desk.include("Inclined_control_surface", face)
a = math.radians(slope)
def surface(x, v, lift=.055):
    return (x, face_y + v*math.cos(a)-lift*math.sin(a),
            face_z + v*math.sin(a)+lift*math.cos(a))

for bay in range(8):
    x = X0 + .40 + bay*.79
    seam = box((.018, 1.02, .01), surface(x-.35, 0), dark)
    seam.turn(axis="x", degrees=slope)
    desk.include("Panel_division_%02d" % bay, seam)
    # Three rows of knobs. Small dark control elements retain their spatial gaps.
    for row in range(3):
        for col in range(3):
            px = x-.21+col*.20
            v = -.34+row*.30
            p = surface(px, v, .065)
            desk.include("Knob_%02d_%02d_%02d" % (bay,row,col),
                         rod(.032, start=p,
                             end=(p[0],p[1]-.025,p[2]+.055), color=dark))
    # Wide pale meter at the back of alternate bays.
    if bay % 2 == 0:
        m = box((.35,.16,.018), surface(x,.42,.065), dark)
        m.turn(axis="x", degrees=slope)
        desk.include("Meter_rim_%02d" % bay, m)
        m = box((.28,.11,.02), surface(x,.42,.078), paper)
        m.turn(axis="x", degrees=slope)
        desk.include("Meter_face_%02d" % bay, m)
scene.include("Main_control_console", desk)

small = Asset("Right_independent_console")
small_x, small_y = 3.85, 2.23
small.include("Dark_pedestal", box((1.35,.82,.72),
                                   (small_x,small_y,.36), base))
small.include("Writing_ledge", box((1.45,.38,.07),
                                   (small_x,small_y-.40,.82), paper))
sf = box((1.45,.68,.08), (small_x,small_y,1.00), panel)
sf.turn(axis="x", degrees=22)
small.include("Inclined_face", sf)
for i in range(7):
    for j in range(2):
        x = small_x-.57+i*.19
        y = small_y-.18+j*.25
        z = 1.00+(y-small_y)*math.tan(math.radians(22))+.07
        small.include("Control_%d_%d" % (i,j),
                      rod(.025,start=(x,y,z),end=(x,y-.015,z+.05),color=dark))
scene.include("Right_independent_console", small)

# The pictured yellow board is an independent item in the source collage;
# its placement here is an interpretive, adjustable choice.
grid = Asset("GRID_single_line_mimic_board")
gx, gy, gz = 2.65, 3.25, 2.25
grid.include("Yellow_face", box((1.18,.08,1.65),(gx,gy,gz),yellow))
fy = gy-.055
grid.include("Vertical_bus",box((.035,.018,1.42),(gx+.10,fy,gz),dark))
for i,z in enumerate((1.72,2.18,2.64)):
    grid.include("Bus_cross_%d" % i,
                 box((.64,.018,.035),(gx+.10,fy,z),dark))
    for side in (-1,1):
        x = gx+.10+side*.27
        grid.include("Branch_%d_%d" % (i,side),
                     box((.035,.018,.22),(x,fy,z+.09),dark))
        grid.include("Amber_lamp_%d_%d" % (i,side),
                     box((.095,.024,.095),(x,fy-.025,z+.09),amber))
for i in range(4):
    z = 1.68+i*.35
    grid.include("Red_lamp_%d" % i,
                 rod(.065,start=(gx-.40,fy-.02,z),
                     end=(gx-.40,fy-.07,z),color=red))
    grid.include("Selector_%d" % i,
                 rod(.040,start=(gx-.22,fy-.02,z),
                     end=(gx-.22,fy-.07,z),color=dark))
for i,z in enumerate((1.55,2.91)):
    grid.include("Label_plate_%d" % i,
                 box((.35,.02,.10),(gx+.32,fy-.025,z),paper))
scene.include("GRID_single_line_mimic_board",grid)

# Small ceiling fixtures are positioned above the view; the ceiling itself is
# left open toward the camera to avoid the erroneous opaque slab in the feedback.
fixtures = Asset("Fluorescent_fixtures")
for i,x in enumerate((-2.8,0,2.8)):
    fixtures.include("Troffer_%d" % i,
                     box((1.55,.38,.035),(x,.8,ROOM_H-.04),paper))
scene.include("Fluorescent_fixtures",fixtures)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.72,.70,.66,1)
background.inputs["Strength"].default_value = .55

sc.render.resolution_x = 374
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
panorama = sc.camera
panorama.name = "Camera_Panorama"
area_emitter((-2,-1,3.25),power=550,size=4,target=(-1,1,1))
area_emitter((3,1,3.25),power=450,size=3,target=(2,2,1))

# Small numerical check: actual geometric points and approximate full-frame
# targets. The targets are estimates for adapting the landscape room image to a
# portrait frame, not measurements of the collage.
landmarks = [
    ("grille center", (-1.12,3.12,1.69), (.32,.35)),
    ("near desk ledge corner", (X0,DESK_Y-.88,.85), (.05,.78)),
    ("far desk face corner", (X1,face_y+.52,1.30), (.72,.51)),
    ("small desk top", (small_x,small_y+.28,1.12), (.85,.45)),
    ("GRID top center", (gx,gy-.06,gz+.825), (.75,.20)),
]
def report(title):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = sc.camera.calc_matrix_camera(
        dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    print(title)
    result = []
    for name,p,ref in landmarks:
        clip = matrix @ sc.camera.matrix_world.inverted() @ Vector((*p,1))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print("%-26s ref=%s projected=%s" %
              (name,ref,None if uv is None else tuple(round(v,3) for v in uv)))
        result.append(uv)
    return result

initial = report("Initial camera landmarks")
# Test one modest lens change only when a foreground or background anchor is
# substantially outside the frame. Revert if it moves a previously visible
# console corner out of frame; this does not establish actual visibility.
if any(u is not None and (u[0]<-.08 or u[0]>1.08 or u[1]<-.08 or u[1]>1.08)
       for u in initial):
    old_lens = panorama.data.lens
    panorama.data.lens = old_lens*.90
    trial = report("Candidate wider lens")
    def inside(u):
        return u is not None and -.03 <= u[0] <= 1.03 and -.03 <= u[1] <= 1.03
    if any(inside(initial[i]) and not inside(trial[i]) for i in (0,1,2,3)):
        panorama.data.lens = old_lens
        print("Restored initial lens because a visible anchor regressed.")
report("Final active panorama landmarks")

# A second editable camera looks toward the console and the GRID board.
set_view((1.2,-3.6,2.5),(1.4,2.1,1.45),lens=40)
sc.camera.name = "Camera_Console_GRID_Detail"
sc.camera = panorama

# German labels are real editable text objects.
def label(name, text, location):
    curve = bpy.data.curves.new(name,"FONT")
    curve.body = text
    curve.size = .035
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name,curve)
    sc.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90),0,0)
    return obj

label("Label_Fehlerstelle_top","FEHLERSTELLE",(gx+.32,fy-.04,2.91))
label("Label_Fehlerstelle_bottom","FEHLERSTELLE",(gx+.32,fy-.04,1.55))

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
sc.render.image_settings.file_format = "PNG"
