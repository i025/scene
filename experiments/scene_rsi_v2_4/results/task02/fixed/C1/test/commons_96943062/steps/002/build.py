from sceneact import *
import bpy
import math
import random

# Reference inventory, approximate normalized bounds:
# Cream back wall (.12,.38)-(.53,.61), right wall extends to all right edges.
# Dark carpet occupies lower .40; black skirting outlines the floor.
# Whiteboard (.59,.26)-(.91,.58): two unequal visible panels, thin silver frame.
# Bright left windows (0,.33)-(.12,.67); missing ceiling tiles above their edge.
# Ceiling grid fills upper left; fluorescent panels and small detector visible.
# Flag (.45,.33)-(.51,.43), diagonal pole, narrow folded striped cloth.
# Back vent (.15,.44)-(.24,.47), electrical recess and tilted hanging cover.
# Gray debris at left and center; yellow layered sheets (.56,.68)-(.90,.79);
# silver rails extend from these sheets through the lower-right crop.
# Observed projection anchors: back floor corners around (46,310),(201,303);
# board corners around (227,205),(343,133),(350,296),(228,277).
# Right-wall floor and ceiling edges converge approximately near (138,266).
# Hidden wall lengths and debris thicknesses remain inferred.
#
# Review: prior execution succeeded and emitted meshes, but semantic completeness
# was not independently verified. Its back wall was too wide and shifted right;
# board depth coverage was too small, and carpet was too pale.
# Competing explanations include focal length, room depth and lateral camera pose.
# Selected coherent projection revision retains focal length, increases room depth
# and moves the camera toward the right wall, preserving a plausible vanishing point.
# Board endpoints are then fitted to the observed perspective expansion.
# This is an unverified revision, not a measured improvement.
# Expanded count: approximately 235 simple meshes; no booleans or fillet expansion.

random.seed(12)
scene = Scene(name="Vacant classroom")

# Separately editable camera, architecture, components and finishes.
W, D, H = 4.45, 10.8, 3.15
CAMERA = (2.50, -.42, 1.20)
YAW = .14
cream = (.72, .69, .61)
ceiling_color = (.62, .65, .65)
silver = (.49, .55, .56)
black = (.035, .043, .038)

def asset(name, parent=None):
    a = Asset(name=name)
    (scene if parent is None else parent).include(name, a)
    return a

def bx(parent, name, size, center, color, rotation=None):
    obj = box(size=size, center=center, color=color)
    if rotation is not None:
        obj.turn(euler=rotation, pivot=center)
    parent.include(name, obj)
    return obj

def rd(parent, name, start, end, radius, color):
    obj = rod(radius=radius, start=start, end=end, color=color)
    parent.include(name, obj)
    return obj

room = asset("Room shell")
bx(room, "Carpet", (W+1,D+3,.12), (W/2,D/2-.8,-.07), (.105,.115,.090))
bx(room, "Right plaster wall", (.12,D+2,H), (W+.06,D/2-.7,H/2), cream)
bx(room, "Back plaster wall", (W,.12,H), (W/2,D+.06,H/2), cream)
bx(room, "Left wall", (.12,D,H), (-.06,D/2,H/2), (.75,.76,.72))
bx(room, "Right black skirting", (.035,D+.5,.115), (W-.025,D/2-.25,.057), black)
bx(room, "Back black skirting", (W,.035,.115), (W/2,D-.025,.057), black)
bx(room, "Left black skirting", (.035,D,.10), (.02,D/2,.05), black)

windows = asset("Left translucent window wall")
for j in range(6):
    yy = .78+j*1.55
    bx(windows, "Glowing pane %d"%j, (.025,1.51,2.78),
       (.022,yy,1.59), (.88,.92,.93))
    bx(windows, "Window mullion %d"%j, (.05,.022,2.86),
       (.043,yy+.77,1.59), (.70,.76,.77))
for zz in (.2,1.57,2.98):
    bx(windows, "Horizontal window rail %.2f"%zz, (.055,9.5,.023),
       (.05,4.75,zz), (.72,.78,.78))

ceiling = asset("Suspended acoustic ceiling")
bx(ceiling, "Dark plenum", (W+.2,D+.5,.05),
   (W/2,D/2,H+.19), (.065,.085,.080))
sx, sy = .75, 1.22
for i in range(6):
    for j in range(10):
        xx, yy = (i+.5)*sx, (j+.5)*sy-.6
        if xx > W or yy > D:
            continue
        if i == 0 and j in (0,1,3,4,5,6):
            continue
        col = ceiling_color
        if (i,j) in ((1,3),(1,4),(1,6)):
            col = (.76,.79,.79)
        bx(ceiling, "Acoustic tile %d %d"%(i,j),
           (sx-.018,sy-.018,.025), (xx,yy,H), col)
for i in range(7):
    xx = i*sx
    if xx <= W:
        bx(ceiling, "Long grid runner %d"%i, (.014,D+.8,.022),
           (xx,D/2-.3,H-.016), (.54,.59,.59))
for j in range(11):
    yy = j*sy-.6
    if yy <= D:
        bx(ceiling, "Cross grid runner %d"%j, (W,.014,.022),
           (W/2,yy,H-.016), (.55,.60,.60))
for j in (3,5,7):
    bx(ceiling, "Fluorescent frame %d"%j, (.65,1.12,.025),
       (1.125,j*sy+.01,H-.033), (.48,.54,.55))
    bx(ceiling, "Fluorescent diffuser %d"%j, (.60,1.06,.012),
       (1.125,j*sy+.01,H-.051), (.77,.82,.83))
rd(ceiling, "Loose ceiling wire", (.18,8.3,H+.02),
   (.24,8.17,2.56), .007, (.12,.14,.14))
detector = asset("Ceiling smoke detector", ceiling)
bx(detector, "Detector base", (.13,.13,.025), (1.55,3.5,H-.035), (.75,.76,.70))
cap = ball(radius=.065, center=(1.55,3.5,H-.065), color=(.75,.76,.70))
cap.resize((1,1,.45), pivot=(1.55,3.5,H-.065))
detector.include("Detector cap", cap)

board = asset("Right wall whiteboard")
board_y, board_len = 5.25, 4.70
board_z, board_h = 1.705, 1.55
bx(board, "Backing", (.035,board_len,board_h),
   (W-.045,board_y,board_z), (.68,.72,.72))
bx(board, "Writing surface", (.012,board_len-.065,board_h-.065),
   (W-.069,board_y,board_z), (.78,.82,.84))
for zz, name in ((board_z-board_h/2,"Bottom frame"),
                 (board_z+board_h/2,"Top frame")):
    bx(board, name, (.045,board_len+.035,.022),
       (W-.08,board_y,zz), silver)
for yy, name in ((board_y-board_len/2,"Near end frame"),
                 (board_y+board_len/2,"Far end frame")):
    bx(board, name, (.045,.022,board_h+.03),
       (W-.08,yy,board_z), silver)
bx(board, "Panel divider", (.021,.012,board_h-.04),
   (W-.082,board_y+.65,board_z), (.60,.66,.68))
bx(board, "Marker tray", (.085,board_len,.023),
   (W-.095,board_y,board_z-board_h/2-.025), silver)
for yy in (board_y-board_len/2+.08,board_y+board_len/2-.08):
    bx(board, "Mounting clip %.2f"%yy, (.027,.050,.075),
       (W-.08,yy,board_z+board_h/2+.025), (.43,.49,.50))

fixtures = asset("Back wall fixtures")
bx(fixtures, "Vent dark opening", (.91,.025,.37),
   (.93,D-.03,2.13), (.23,.29,.30))
for k in range(9):
    bx(fixtures, "Vent louver %d"%k, (.85,.028,.012),
       (.93,D-.051,1.98+k*.036), (.30,.37,.38))
bx(fixtures, "Electrical panel surround", (.28,.035,.41),
   (2.08,D-.035,1.89), (.47,.53,.52))
bx(fixtures, "Electrical panel cavity", (.22,.016,.32),
   (2.08,D-.063,1.90), (.085,.12,.115))
for k in range(4):
    bx(fixtures, "Breaker %d"%k, (.06,.025,.037),
       (2.06+(k%2)*.075,D-.083,1.82+(k//2)*.10), (.47,.49,.45))
bx(fixtures, "Tilted hanging cover", (.43,.035,.34),
   (2.25,D-.13,1.58), (.40,.48,.47), (0,39,0))
for xx,zz in ((2.69,1.64),(2.88,1.69)):
    bx(fixtures, "Wall plate %.2f"%xx, (.13,.02,.18),
       (xx,D-.035,zz), (.76,.76,.70))
    bx(fixtures, "Plate inset %.2f"%xx, (.05,.012,.045),
       (xx,D-.05,zz+.02), (.43,.46,.42))
bx(fixtures, "Right wall outlet", (.018,.085,.135),
   (W-.065,6.5,.50), (.67,.66,.57))

flag = asset("American flag and pole")
rd(flag, "Diagonal flagpole", (W-.03,7.0,2.66),
   (3.25,7.16,3.10), .012, (.25,.27,.25))
# Narrow hanging folds expose long red/white stripes in this view.
fx, fy, ft = 3.25, 7.12, 3.09
fw, fh = .32, .84
for k in range(13):
    x = fx+(k+.5)*fw/13
    drop = .10*k/12
    col = (.59,.045,.040) if k%2 == 0 else (.85,.83,.75)
    bx(flag, "Hanging stripe %d"%k, (fw/13+.002,.014,fh-drop),
       (x,fy+.020*math.sin(k*1.7),ft-drop-(fh-drop)/2), col)
bx(flag, "Blue canton", (.16,.018,.29),
   (fx+.078,fy-.029,ft-.16), (.075,.12,.21))
for r in range(5):
    for c in range(4):
        bx(flag, "Star %d %d"%(r,c), (.008,.005,.009),
           (fx+.022+c*.035,fy-.041,ft-.045-r*.050), (.82,.83,.77))

debris = asset("Scattered ceiling debris")
def fragment(name, center, size, angle, color):
    p = asset(name, debris)
    bx(p, "Broken panel", size, center, color, (0,0,angle))
    # Sparse raised edges retain the torn layered appearance.
    return p

fragment("Foreground torn panel", (2.00,3.25,.025),
         (1.28,.56,.028), -12, (.27,.29,.25))
fragment("Foreground overlapping piece", (2.22,3.44,.047),
         (.90,.34,.022), 17, (.34,.36,.30))
fragment("Left middle panel", (1.08,4.72,.022),
         (.96,.38,.025), -8, (.31,.33,.28))
fragment("Back scattered panel", (1.72,6.24,.025),
         (1.12,.35,.026), 9, (.25,.28,.24))
fragment("Small back panel", (1.49,6.39,.046),
         (.55,.26,.018), -19, (.39,.41,.35))
for k in range(13):
    xx = random.uniform(1.1,2.7)
    yy = random.uniform(3.1,6.5)
    rd(debris, "Torn dark edging %d"%k, (xx,yy,.045),
       (xx+random.uniform(.15,.48),yy+random.uniform(-.2,.2),.047),
       .008, (.08,.11,.09))
for k in range(25):
    xx, yy = random.uniform(.2,4.3), random.uniform(2.0,9.8)
    s = random.uniform(.012,.040)
    bx(debris, "Plaster chip %d"%k, (s,s*.65,.008),
       (xx,yy,.012), (.44,.44,.34))

yellow = asset("Collapsed yellow ceiling panels")
for k in range(4):
    ctr = (3.83-.09*k,3.55+.10*k,.075+.023*k)
    bx(yellow, "Layered yellow sheet %d"%k, (1.24,.95,.028),
       ctr, (.57+.035*k,.43+.035*k,.13+.018*k), (2,-4,-7))
bx(yellow, "Bent raised yellow panel", (.92,1.10,.035),
   (4.00,3.39,.19), (.70,.54,.18), (-13,7,-7))
for k in range(4):
    rd(yellow, "Exposed layered edge %d"%k,
       (3.16,3.17+.05*k,.08+.022*k),
       (3.21,3.93+.05*k,.11+.022*k), .010, (.52,.41,.16))

rails = asset("Fallen metal ceiling runners")
rd(rails, "Long silver foreground rail",
   (3.94,2.75,.035),(4.79,.20,.035), .023, (.59,.64,.64))
rd(rails, "Second silver foreground rail",
   (4.20,3.00,.03),(5.13,.60,.03), .018, (.67,.71,.69))
rd(rails, "Left pale cross rail",
   (1.56,4.18,.045),(2.99,3.88,.045), .016, (.57,.65,.67))
rd(rails, "Left rail dark flange",
   (1.58,4.20,.027),(3.01,3.90,.027), .010, (.21,.28,.27))

realize(scene)

# Match carpet by geometry because realized primitive names need not retain labels.
for obj in bpy.data.objects:
    if obj.type != 'MESH' or not obj.data.materials:
        continue
    mat = obj.data.materials[0]
    mat.use_nodes = True
    nt = mat.node_tree
    bs = nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    bs.inputs["Roughness"].default_value = .87
    if obj.dimensions.x > W and obj.dimensions.y > D and obj.location.z < .1:
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 145
        noise.inputs["Detail"].default_value = 2
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .18
        ramp.color_ramp.elements[0].color = (.035,.043,.035,1)
        ramp.color_ramp.elements[1].position = .82
        ramp.color_ramp.elements[1].color = (.105,.115,.088,1)
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .14
        bump.inputs["Distance"].default_value = .008
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nt = sc.world.node_tree
background = nt.nodes.get("Background")
if background is None:
    background = nt.nodes.new("ShaderNodeBackground")
output = nt.nodes.get("World Output")
if output is None:
    output = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.66,.72,.79,1)
background.inputs["Strength"].default_value = .26

area_emitter(position=(.25,5.8,2.1),power=440,size=5.7,
             target=(3.4,6.2,1.0),color=(.90,.95,1.0))
area_emitter(position=(2.2,6.4,2.94),power=90,size=4.5,
             target=(2.4,6.5,0),color=(1.0,.94,.82))

# Slight upward pitch places the shared vanishing point below image center.
set_view(position=CAMERA,
         target=(CAMERA[0]+math.sin(YAW)*10,
                 CAMERA[1]+math.cos(YAW)*10,
                 CAMERA[2]+.26),
         lens=24,sensor=32)
sc.camera.data.clip_start = .05
sc.camera.data.clip_end = 100
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'
sc.view_settings.exposure = 0
sc.view_settings.gamma = 1
