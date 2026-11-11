from sceneact import *
import bpy
import math

# Reference inventory and visual anchors, estimated from the photograph:
# - Back wall and right wall meet around (0.63, 0.0)-(0.63, 0.42).
#   Dark patterned wallpaper covers most of both walls; the ceiling is a thin
#   white strip and the pale carpet occupies the lower left.
# - Two tall back-wall windows occupy approximately (0.00,0.07)-(0.13,0.50)
#   and (0.23,0.08)-(0.44,0.52); both have white trim and green shades.
# - Dark bed occupies (0.43,0.46)-(0.99,0.98); its head is against the
#   right-hand wall, with white pillows and a broad pale cover. The footboard
#   overlaps the foreground chair.
# - Olive upholstered chair occupies (0.28,0.50)-(0.53,0.98), with a high
#   curved back, rounded arms and a dark base.
# - Gold and blue folding screen occupies (0.41,0.32)-(0.62,0.63), behind
#   the bed and chair; its detailed painted figures are uncertain.
# - Small table and white cloth at (0.14,0.47)-(0.27,0.65); dark cabinet at
#   the far left; framed portraits and small pictures above.
# - A small chair is visible behind the bed near (0.62,0.46)-(0.70,0.62).
#   Portions of furniture behind the bed and screen are occluded.
# - Two red patterned rugs are visible near the chair and along the bottom edge.
# Dominant edges: the back wall is nearly horizontal; the right-wall ceiling
# and base recede downward toward the central corner. Bed rails run diagonally
# from the lower center toward the upper right.
# Approximate expanded primitive count: architecture 24, windows 17, bed 19,
# chair 10, screen 16, tables and small chair 25, pictures 14, rugs 16,
# accessories 10: roughly 151 meshes. Ellipsoids are each one ball primitive.

scene = Scene("Bedroom")

# Camera and main dimensions are kept separate for later adjustment.
CAMERA_POSITION = (0.0, -8.8, 3.15)
CAMERA_TARGET = (-0.05, 1.65, 1.35)
CAMERA_LENS = 35
ROOM_LEFT, ROOM_RIGHT = -4.0, 2.65
BACK_Y = 3.5
ROOM_HEIGHT = 3.05

wall_col = (0.31, 0.215, 0.16)
trim = (0.89, 0.88, 0.83)
wood = (0.105, 0.048, 0.028)
wood_hi = (0.18, 0.085, 0.047)
white = (0.84, 0.83, 0.78)
olive = (0.30, 0.31, 0.065)
gold = (0.65, 0.46, 0.18)

def add(parent, name, node):
    parent.include(name, node)
    return node

def ellipsoid(center, size, color):
    p = ball(1, center=center, color=color)
    p.resize((size[0]/2, size[1]/2, size[2]/2), pivot=center)
    return p

def block(parent, name, center, size, color):
    return add(parent, name, box(size=size, center=center, color=color))

def spherepart(parent, name, center, size, color):
    return add(parent, name, ellipsoid(center, size, color))

def beam(parent, name, a, b, radius, color):
    return add(parent, name, rod(radius=radius, start=a, end=b, color=color))

# Room shell
room = Asset("Architecture")
block(room, "carpet", (-0.65, -0.3, -0.055), (7.0, 8.0, 0.11), (0.56, 0.54, 0.50))
block(room, "back_wall", (-0.675, BACK_Y, 1.53), (6.65, 0.12, 3.06), wall_col)
block(room, "right_wall", (ROOM_RIGHT, -0.3, 1.53), (0.12, 7.7, 3.06), wall_col)
block(room, "ceiling", (-0.65, -0.2, 3.09), (6.7, 7.7, 0.10), (0.88, 0.88, 0.86))
block(room, "back_crown", (-0.65, 3.39, 2.99), (6.6, 0.15, 0.13), trim)
block(room, "right_crown", (2.55, -0.2, 2.99), (0.15, 7.4, 0.13), trim)
block(room, "back_baseboard", (-0.65, 3.39, 0.10), (6.6, 0.12, 0.20), (0.40, 0.31, 0.24))
block(room, "right_baseboard", (2.55, -0.2, 0.10), (0.12, 7.4, 0.20), (0.40, 0.31, 0.24))
scene.include("room", room)

# Back-wall windows: green roller blinds with bright lower panes.
windows = Asset("Windows")
def window(name, x, width):
    z0, h = 0.80, 2.05
    block(windows, name+"_opening", (x, 3.415, z0+h/2), (width, .035, h), (0.91, .93, .89))
    block(windows, name+"_shade", (x, 3.385, 2.09), (width-.15, .028, 1.30), (.22, .42, .34))
    block(windows, name+"_lower_glass", (x, 3.375, 1.03), (width-.15, .028, .42), (.83, .91, .88))
    for side in (-1, 1):
        block(windows, name+"_jamb_"+str(side), (x+side*width/2, 3.34, 1.825), (.09, .12, 2.16), trim)
    block(windows, name+"_header", (x, 3.34, 2.90), (width+.12, .12, .10), trim)
    block(windows, name+"_sill", (x, 3.31, .76), (width+.16, .19, .10), trim)
window("left_window", -3.65, 1.12)
window("middle_window", -1.52, 1.22)
scene.include("windows", windows)

# White narrow door at the back, partly hidden by the screen.
door = Asset("Back door")
block(door, "panel", (0.93, 3.405, 1.30), (.58, .04, 2.28), (.82,.83,.79))
for x in (.60, 1.26):
    block(door, "frame_"+str(x), (x,3.34,1.33), (.07,.13,2.40), trim)
block(door, "top_frame", (.93,3.34,2.52), (.72,.13,.07), trim)
scene.include("door", door)

# Bed is oriented front to back, with its head against the right side of room.
bed = Asset("Dark wooden bed")
BED_X = 1.33
BED_Y = 0.10
block(bed, "base", (BED_X, BED_Y, .36), (1.83, 3.30, .36), wood)
block(bed, "mattress", (BED_X, BED_Y, .64), (1.80, 3.20, .31), (.83,.82,.76))
# Cover is a broad slightly rounded solid and two visible hanging edges.
spherepart(bed, "cover_top", (1.32, -.42, .84), (1.79, 2.22, .35), (.87,.86,.81))
block(bed, "cover_left_drape", (.48, -.45, .63), (.09, 2.05, .42), (.75,.74,.69))
block(bed, "cover_foot_drape", (1.32, -1.40, .60), (1.76, .12, .42), (.75,.74,.69))
for i, x in enumerate((.91,1.75)):
    p = spherepart(bed, "pillow_"+str(i), (x,1.16,1.02), (.78,.87,.33), (.91,.91,.88))
    p.turn(axis="+x", degrees=12)
# Headboard, raised posts, and top rail.
block(bed, "headboard", (BED_X, 1.78, .96), (1.96, .14, .78), wood)
block(bed, "headboard_cap", (BED_X, 1.80, 1.38), (2.05, .20, .11), wood_hi)
for x in (.34,2.31):
    block(bed, "head_post_"+str(x), (x,1.79,.85), (.14,.18,1.16), wood)
# Footboard makes the dark diagonal visible in front of bedding.
block(bed, "footboard", (BED_X, -1.57, .66), (2.02, .15, 1.10), wood)
block(bed, "footboard_top", (BED_X,-1.57,1.24), (2.10,.21,.10), wood_hi)
for x in (.31,2.35):
    block(bed, "foot_post_"+str(x), (x,-1.57,.70), (.15,.20,1.36), wood)
scene.include("bed", bed)

# Small blue and ochre three-panel screen, positioned behind the bed.
screen = Asset("Painted folding screen")
for i, x in enumerate((-.78, -.20, .38)):
    panel = block(screen, "panel_"+str(i), (x, 2.20, 1.25), (.59,.055,1.46), (.61,.43,.19))
    block(screen, "upper_border_"+str(i), (x,2.16,1.99), (.60,.07,.035), (.16,.10,.055))
    block(screen, "lower_border_"+str(i), (x,2.16,.52), (.60,.07,.035), (.16,.10,.055))
    block(screen, "edge_"+str(i), (x-.29,2.16,1.25), (.027,.07,1.47), (.18,.10,.05))
# Flat painted color fields stand in for the loose shapes on the screen.
for i, (x,z,sx,sz) in enumerate(((-.64,1.73,.54,.36),(-.35,1.40,.70,.33),
                                  (.10,1.68,.63,.40),(.37,1.35,.38,.63),
                                  (-.42,.88,.53,.35),(.22,.82,.48,.30))):
    spherepart(screen, "blue_paint_"+str(i), (x,2.155,z), (sx,.012,sz), (.025,.12,.52))
spherepart(screen, "painted_face", (.28,2.143,1.49), (.13,.012,.20), (.73,.47,.21))
spherepart(screen, "painted_flower", (-.38,2.14,1.05), (.19,.012,.13), (.78,.72,.58))
scene.include("screen", screen)

# Upholstered foreground armchair. Each part remains independently editable.
chair = Asset("Olive upholstered armchair")
CX, CY = -1.03, -1.23
spherepart(chair, "back", (CX,CY+.42,1.02), (1.46,.42,1.37), (.28,.30,.06))
spherepart(chair, "seat", (CX,CY-.06,.63), (1.38,1.12,.40), (.37,.37,.08))
spherepart(chair, "left_arm", (CX-.62,CY-.06,.83), (.31,1.14,.58), (.30,.32,.065))
spherepart(chair, "right_arm", (CX+.62,CY-.06,.83), (.31,1.14,.58), (.27,.29,.055))
block(chair, "front_skirt", (CX,CY-.60,.40), (1.22,.10,.38), (.20,.20,.045))
for x in (CX-.49,CX+.49):
    for y in (CY-.43,CY+.39):
        block(chair, "leg_%.2f_%.2f"%(x,y), (x,y,.18), (.07,.07,.36), wood)
scene.include("armchair", chair)

# A dark wooden cabinet below the left window.
cabinet = Asset("Left cabinet")
block(cabinet, "body", (-3.63,3.06,.49), (1.24,.58,.75), (.15,.075,.045))
block(cabinet, "top", (-3.63,3.04,.91), (1.36,.67,.09), (.20,.10,.055))
for x in (-4.13,-3.13):
    block(cabinet, "leg_"+str(x), (x,3.04,.16), (.09,.10,.32), wood)
for x in (-3.94,-3.33):
    block(cabinet, "drawer_"+str(x), (x,2.76,.68), (.55,.04,.22), (.19,.10,.06))
    spherepart(cabinet, "knob_"+str(x), (x,2.73,.68), (.045,.035,.045), gold)
scene.include("cabinet", cabinet)

# White-draped side table between the windows.
table = Asset("Draped side table")
block(table, "top", (-2.55,2.96,.76), (.83,.58,.08), wood)
for x in (-2.90,-2.20):
    for y in (2.74,3.18):
        block(table, "leg_%.1f_%.1f"%(x,y), (x,y,.38), (.055,.055,.76), wood)
block(table, "white_cloth_top", (-2.55,2.96,.82), (.93,.67,.035), (.87,.86,.79))
# Triangular folds suggested by overlapping pale cloth panels.
cloth = block(table, "hanging_cloth", (-2.55,2.63,.67), (.68,.035,.30), (.85,.84,.77))
spherepart(table, "bowl", (-2.55,2.93,.87), (.30,.24,.08), (.89,.86,.73))
for i,x in enumerate((-2.80,-2.33)):
    spherepart(table, "table_object_"+str(i), (x,2.93,.87), (.12,.10,.12), (.64,.63,.54))
scene.include("side_table", table)

# Small straight-backed chair visible just behind the bed.
small = Asset("Small wooden chair")
block(small, "seat", (.40,2.40,.58), (.50,.46,.08), wood)
for x in (.18,.62):
    for y in (2.20,2.59):
        block(small, "leg_%.2f_%.2f"%(x,y), (x,y,.29), (.045,.045,.58), wood)
for x in (.18,.62):
    block(small, "back_post_"+str(x), (x,2.60,.91), (.045,.05,.72), wood)
block(small, "back_top", (.40,2.60,1.26), (.50,.06,.08), wood_hi)
for x in (.28,.40,.52):
    block(small, "back_spindle_"+str(x), (x,2.60,1.03), (.026,.04,.40), wood)
scene.include("small_chair", small)

# Wall pictures: layered shallow ellipsoids and framed rectangles.
pictures = Asset("Wall pictures")
spherepart(pictures, "oval_gold_frame", (-2.64,3.32,2.16), (.77,.10,.97), (.67,.49,.19))
spherepart(pictures, "oval_inner_rim", (-2.64,3.255,2.16), (.62,.035,.81), (.26,.16,.07))
spherepart(pictures, "oval_portrait", (-2.64,3.23,2.16), (.54,.025,.73), (.055,.045,.035))
spherepart(pictures, "portrait_head", (-2.64,3.21,2.24), (.13,.02,.20), (.56,.34,.20))
spherepart(pictures, "portrait_body", (-2.64,3.20,2.04), (.27,.02,.22), (.10,.08,.065))
def framed_picture(name,x,z,w,h):
    block(pictures, name+"_frame", (x,3.31,z), (w,.09,h), (.69,.56,.31))
    block(pictures, name+"_mat", (x,3.25,z), (w-.08,.025,h-.08), (.86,.84,.74))
    block(pictures, name+"_image", (x,3.23,z), (w-.18,.02,h-.18), (.53,.53,.49))
    spherepart(pictures, name+"_figure", (x,3.21,z), ((w-.18)*.42,.015,(h-.18)*.62), (.38,.38,.35))
framed_picture("small_print", -.31, 2.38, .43,.55)
framed_picture("right_print", 1.71, 2.37, .34,.54)
scene.include("pictures", pictures)

# Low rugs, with broad contrasting borders and restrained stripes.
rugs = Asset("Patterned rugs")
def rug(name, x, y, w, d):
    block(rugs, name+"_base", (x,y,.012), (w,d,.025), (.46,.15,.14))
    block(rugs, name+"_inner", (x,y,.027), (w-.12,d-.12,.008), (.13,.22,.29))
    block(rugs, name+"_field", (x,y,.034), (w-.20,d-.20,.008), (.56,.29,.22))
    for k in (-1,1):
        block(rugs, name+"_stripe_x_"+str(k), (x+k*(w/2-.075),y,.04), (.025,d-.10,.008), (.77,.68,.52))
        block(rugs, name+"_stripe_y_"+str(k), (x,y+k*(d/2-.075),.04), (w-.10,.025,.008), (.77,.68,.52))
rug("back_rug", -1.85, -.12, 1.25, 1.12)
rug("foreground_rug", 1.25, -3.33, 2.8, 1.12)
scene.include("rugs", rugs)

# Small dark bedside unit at the extreme right.
nightstand = Asset("Bedside table")
block(nightstand, "body", (2.43,-.24,.43), (.43,.70,.80), wood)
block(nightstand, "top", (2.42,-.24,.86), (.53,.78,.08), wood_hi)
scene.include("nightstand", nightstand)

realize(scene)

# Replace the plain wall color with a shared subtle, fine-grained wallpaper.
# Matching the color rather than object names keeps SceneAct's hierarchy intact.
for mat in bpy.data.materials:
    if not mat.diffuse_color:
        continue
    c = mat.diffuse_color
    if abs(c[0] - wall_col[0]) < .015 and abs(c[1] - wall_col[1]) < .015 and abs(c[2] - wall_col[2]) < .015:
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            tex = nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value = 155.0
            tex.inputs["Detail"].default_value = 2.0
            tex.inputs["Roughness"].default_value = .72
            ramp = nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = .24
            ramp.color_ramp.elements[0].color = (.095,.065,.050,1)
            ramp.color_ramp.elements[1].position = .78
            ramp.color_ramp.elements[1].color = (.40,.29,.20,1)
            links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
            links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
            bsdf.inputs["Roughness"].default_value = .9

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
background.inputs["Color"].default_value = (.72,.75,.76,1)
background.inputs["Strength"].default_value = .38

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((-2.0, 2.5, 2.65), power=480, size=3.0, target=(0,-.7,.5), color=(.85,.91,1.0))
area_emitter((-1.0,-4.0,3.0), power=350, size=5.0, target=(0,1.0,1.0), color=(1.0,.91,.80))
sc.render.resolution_x = 512
sc.render.resolution_y = 341
sc.render.resolution_percentage = 100
