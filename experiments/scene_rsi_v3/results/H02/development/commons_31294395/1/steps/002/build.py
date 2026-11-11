from sceneact import *
import bpy

# Reference versus first render, estimated normalized image coordinates:
# Back-wall corner: reference x≈0.63; render x≈0.71. The render has a large
# gray empty band above y≈0.25; the reference ceiling meets the image top.
# Center window: reference (0.23,0.08)-(0.44,0.52); render roughly
# (0.33,0.29)-(0.44,0.55). It is too small and too low in the frame.
# Bed: reference (0.43,0.46)-(1.00,0.98), with its long edges diagonal;
# render (0.53,0.48)-(0.83,0.87), facing almost directly toward the camera.
# Chair: reference (0.28,0.51)-(0.53,1.00); render (0.27,0.51)-(0.47,0.87).
# Screen: reference (0.41,0.33)-(0.62,0.63); render (0.41,0.40)-(0.56,0.62).
# Largest discrepancies: (1) empty upper crop and undersized background,
# (2) bed orientation, silhouette and white bedding coverage, (3) chair
# shape and foreground scale. The render's room edges are too horizontal.
# Corrections: move CAMERA_POSITION left and closer, aim toward the room corner,
# and use a wider CAMERA_LENS. This should enlarge the windows and foreground,
# raise the wall/ceiling boundary, and make the right-wall edges recede.
# Remove the ceiling slab that obscured the camera; retain visible crown trim.
# Rotate and reposition the BED asset so its head lies at the right wall; its
# footboard should move toward the center and its long side extend rightward.
# Raise and deepen the chair's curved back and hide its square front skirt.
# The screen remains behind both chair and bed. Small picture details and
# obscured furniture are approximate.
#
# Reference inventory: wallpapered back and right walls, two windows, door,
# framed pictures, cabinet, draped table, folding screen, small chair, dark
# wooden bed with two pillows and pale cover, olive armchair, rugs, nightstand.
# Approximate expanded primitive count: room 7, windows 14, door 4, bed 14,
# screen 20, armchair 12, cabinet/table 17, small chair 11, pictures 13,
# rugs 14, nightstand 2: about 138 primitives.

scene = Scene("Historic bedroom")
CAMERA_POSITION = (-4.25, -6.8, 2.75)
CAMERA_TARGET = (-0.1, 1.65, 1.45)
CAMERA_LENS = 29
BACK_Y = 3.5
RIGHT_X = 2.65
H = 3.05

wall = (.29, .19, .13)
trim = (.88, .87, .82)
wood = (.085, .038, .022)
wood_hi = (.14, .065, .036)
linen = (.84, .83, .78)
gold = (.65, .45, .16)

def block(parent, name, center, size, color):
    node = box(size=size, center=center, color=color)
    parent.include(name, node)
    return node

def oval(parent, name, center, size, color):
    node = ball(1, center=center, color=color)
    node.resize((size[0]/2, size[1]/2, size[2]/2), pivot=center)
    parent.include(name, node)
    return node

def rodpart(parent, name, a, b, radius, color):
    node = rod(radius=radius, start=a, end=b, color=color)
    parent.include(name, node)
    return node

room = Asset("Architecture")
block(room, "carpet", (-.65, -.5, -.06), (8, 9, .12), (.52,.50,.46))
block(room, "back_wall", (-.65, BACK_Y, H/2), (6.7,.12,H), wall)
block(room, "right_wall", (RIGHT_X,-.5,H/2), (.12,8,H), wall)
block(room, "back_crown", (-.65,3.39,3.00), (6.6,.17,.13), trim)
block(room, "right_crown", (2.55,-.45,3.00), (.17,7.8,.13), trim)
block(room, "back_baseboard", (-.65,3.39,.10), (6.6,.12,.20), (.30,.21,.15))
block(room, "right_baseboard", (2.55,-.45,.10), (.12,7.8,.20), (.30,.21,.15))
scene.include("room", room)

windows = Asset("Windows")
def window(name, x, width):
    block(windows, name+"_opening", (x,3.415,1.80), (width,.035,2.15), (.91,.94,.91))
    block(windows, name+"_blind", (x,3.385,2.15), (width-.16,.025,1.35), (.16,.36,.29))
    block(windows, name+"_lower_light", (x,3.37,1.12), (width-.16,.025,.62), (.96,.98,.96))
    for side in (-1,1):
        block(windows, name+"_jamb_"+str(side), (x+side*width/2,3.34,1.82), (.09,.12,2.22), trim)
    block(windows, name+"_header", (x,3.34,2.94), (width+.13,.12,.10), trim)
    block(windows, name+"_sill", (x,3.31,.72), (width+.16,.18,.10), trim)
window("left", -3.65, 1.12)
window("center", -1.52, 1.22)
scene.include("windows", windows)

door = Asset("Back door")
block(door,"door_panel",(.93,3.405,1.30),(.58,.04,2.28),(.81,.82,.78))
for x in (.60,1.26):
    block(door,"jamb_"+str(x),(x,3.34,1.33),(.07,.13,2.40),trim)
block(door,"header",(.93,3.34,2.52),(.72,.13,.07),trim)
scene.include("door",door)

# The bed's long axis runs toward the right wall. The near footboard is
# deliberately lower than the first render so the white cover remains visible.
bed = Asset("Dark wooden bed")
bx, by = .92, -.03
block(bed,"base",(bx,by,.36),(3.20,1.84,.38),wood)
block(bed,"mattress",(bx,by,.64),(3.08,1.78,.26),(.76,.75,.70))
oval(bed,"cover",(bx-.32,by,.79),(2.30,1.76,.35),(.87,.86,.81))
block(bed,"near_drape",(bx-.30,by-.85,.61),(2.25,.10,.37),(.77,.76,.71))
block(bed,"foot_drape",(bx-1.41,by,.60),(.10,1.72,.36),(.77,.76,.71))
for i,y in enumerate((by-.43,by+.43)):
    p = oval(bed,"pillow_"+str(i),(bx+1.03,y,.98),(.77,.79,.36),(.91,.91,.87))
    p.turn(axis="+y",degrees=-12)
block(bed,"headboard",(bx+1.60,by,1.00),(.15,1.96,.78),wood)
block(bed,"head_rail",(bx+1.61,by,1.42),(.20,2.06,.11),wood_hi)
for y in (by-.98,by+.98):
    block(bed,"head_post_"+str(y),(bx+1.61,y,.87),(.18,.14,1.22),wood)
block(bed,"footboard",(bx-1.61,by,.64),(.15,1.98,1.02),wood)
block(bed,"foot_rail",(bx-1.61,by,1.18),(.21,2.08,.10),wood_hi)
for y in (by-.99,by+.99):
    block(bed,"foot_post_"+str(y),(bx-1.61,y,.65),(.19,.15,1.25),wood)
scene.include("bed",bed)

screen = Asset("Painted folding screen")
for i,x in enumerate((-.78,-.20,.38)):
    block(screen,"panel_"+str(i),(x,2.20,1.25),(.59,.055,1.46),(.61,.43,.19))
    block(screen,"top_"+str(i),(x,2.16,1.99),(.60,.07,.035),(.16,.10,.055))
    block(screen,"bottom_"+str(i),(x,2.16,.52),(.60,.07,.035),(.16,.10,.055))
    block(screen,"edge_"+str(i),(x-.29,2.16,1.25),(.027,.07,1.47),(.18,.10,.05))
for i,(x,z,sx,sz) in enumerate(((-.64,1.73,.54,.36),(-.35,1.40,.70,.33),
                                 (.10,1.68,.63,.40),(.37,1.35,.38,.63),
                                 (-.42,.88,.53,.35),(.22,.82,.48,.30))):
    oval(screen,"blue_paint_"+str(i),(x,2.155,z),(sx,.012,sz),(.025,.12,.52))
oval(screen,"face",(.28,2.143,1.49),(.13,.012,.20),(.73,.47,.21))
oval(screen,"flower",(-.38,2.14,1.05),(.19,.012,.13),(.78,.72,.58))
scene.include("screen",screen)

chair = Asset("Olive upholstered armchair")
cx, cy = -1.25, -1.50
oval(chair,"rounded_back",(cx,cy+.40,1.03),(1.43,.45,1.45),(.25,.27,.055))
oval(chair,"back_cushion",(cx,cy+.16,1.02),(1.10,.28,1.14),(.32,.34,.075))
oval(chair,"seat",(cx,cy-.10,.63),(1.31,1.20,.39),(.35,.35,.075))
oval(chair,"left_arm",(cx-.60,cy-.07,.80),(.34,1.20,.61),(.29,.30,.06))
oval(chair,"right_arm",(cx+.60,cy-.07,.80),(.34,1.20,.61),(.25,.27,.05))
oval(chair,"front_apron",(cx,cy-.55,.43),(1.25,.23,.57),(.23,.24,.045))
for x in (cx-.49,cx+.49):
    for y in (cy-.42,cy+.39):
        block(chair,"leg_%.2f_%.2f"%(x,y),(x,y,.16),(.07,.07,.32),wood)
scene.include("armchair",chair)

cabinet = Asset("Left cabinet")
block(cabinet,"body",(-3.63,3.06,.49),(1.24,.58,.75),(.13,.065,.04))
block(cabinet,"top",(-3.63,3.04,.91),(1.36,.67,.09),(.19,.09,.05))
for x in (-4.13,-3.13):
    block(cabinet,"leg_"+str(x),(x,3.04,.16),(.09,.10,.32),wood)
for x in (-3.94,-3.33):
    block(cabinet,"drawer_"+str(x),(x,2.76,.68),(.55,.04,.22),(.19,.10,.06))
    oval(cabinet,"knob_"+str(x),(x,2.73,.68),(.045,.035,.045),gold)
scene.include("cabinet",cabinet)

table = Asset("Draped side table")
block(table,"top",(-2.55,2.96,.76),(.83,.58,.08),wood)
for x in (-2.90,-2.20):
    for y in (2.74,3.18):
        block(table,"leg_%.1f_%.1f"%(x,y),(x,y,.38),(.055,.055,.76),wood)
block(table,"cloth_top",(-2.55,2.96,.82),(.93,.67,.035),(.87,.86,.79))
block(table,"cloth_front",(-2.55,2.63,.68),(.68,.035,.27),(.85,.84,.77))
oval(table,"bowl",(-2.55,2.93,.87),(.30,.24,.08),(.89,.86,.73))
for i,x in enumerate((-2.80,-2.33)):
    oval(table,"small_object_"+str(i),(x,2.93,.87),(.12,.10,.12),(.64,.63,.54))
scene.include("side_table",table)

small = Asset("Small wooden chair")
block(small,"seat",(.70,2.25,.58),(.50,.46,.08),wood)
for x in (.48,.92):
    for y in (2.05,2.44):
        block(small,"leg_%.2f_%.2f"%(x,y),(x,y,.29),(.045,.045,.58),wood)
for x in (.48,.92):
    block(small,"back_post_"+str(x),(x,2.45,.91),(.045,.05,.72),wood)
block(small,"back_top",(.70,2.45,1.26),(.50,.06,.08),wood_hi)
for x in (.58,.70,.82):
    block(small,"spindle_"+str(x),(x,2.45,1.03),(.026,.04,.40),wood)
scene.include("small_chair",small)

pictures = Asset("Wall pictures")
oval(pictures,"portrait_gold_frame",(-2.64,3.32,2.16),(.77,.10,.97),(.67,.49,.19))
oval(pictures,"portrait_inner_rim",(-2.64,3.255,2.16),(.62,.035,.81),(.26,.16,.07))
oval(pictures,"portrait_dark",(-2.64,3.23,2.16),(.54,.025,.73),(.055,.045,.035))
oval(pictures,"portrait_head",(-2.64,3.21,2.24),(.13,.02,.20),(.56,.34,.20))
oval(pictures,"portrait_body",(-2.64,3.20,2.04),(.27,.02,.22),(.10,.08,.065))
def framed(name,x,z,w,h):
    block(pictures,name+"_frame",(x,3.31,z),(w,.09,h),(.69,.56,.31))
    block(pictures,name+"_mat",(x,3.25,z),(w-.08,.025,h-.08),(.86,.84,.74))
    block(pictures,name+"_image",(x,3.23,z),(w-.18,.02,h-.18),(.53,.53,.49))
    oval(pictures,name+"_figure",(x,3.21,z),((w-.18)*.42,.015,(h-.18)*.62),(.38,.38,.35))
framed("small_print",-.31,2.38,.43,.55)
framed("right_print",1.71,2.37,.34,.54)
scene.include("pictures",pictures)

rugs = Asset("Patterned rugs")
def rug(name,x,y,w,d):
    block(rugs,name+"_base",(x,y,.012),(w,d,.025),(.46,.15,.14))
    block(rugs,name+"_inner",(x,y,.027),(w-.12,d-.12,.008),(.13,.22,.29))
    block(rugs,name+"_field",(x,y,.034),(w-.20,d-.20,.008),(.56,.29,.22))
    for k in (-1,1):
        block(rugs,name+"_stripe_x_"+str(k),(x+k*(w/2-.075),y,.04),(.025,d-.10,.008),(.77,.68,.52))
        block(rugs,name+"_stripe_y_"+str(k),(x,y+k*(d/2-.075),.04),(w-.10,.025,.008),(.77,.68,.52))
rug("back_rug",-1.85,-.12,1.25,1.12)
rug("foreground_rug",1.25,-3.33,2.8,1.12)
scene.include("rugs",rugs)

nightstand = Asset("Bedside table")
block(nightstand,"body",(2.42,-1.35,.40),(.42,.66,.76),wood)
block(nightstand,"top",(2.42,-1.35,.80),(.50,.74,.08),wood_hi)
scene.include("nightstand",nightstand)

realize(scene)

# Fine shared procedural color variation suggests patterned wallpaper without
# representing the photograph or creating subpixel geometry.
for mat in bpy.data.materials:
    c = mat.diffuse_color
    if abs(c[0]-wall[0]) < .015 and abs(c[1]-wall[1]) < .015 and abs(c[2]-wall[2]) < .015:
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
            ramp.color_ramp.elements[0].color = (.085,.052,.037,1)
            ramp.color_ramp.elements[1].position = .78
            ramp.color_ramp.elements[1].color = (.38,.25,.16,1)
            links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
            links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
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
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.72,.75,.76,1)
background.inputs["Strength"].default_value = .38

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-2.0,2.5,2.7),power=480,size=3.0,target=(0,-.7,.5),color=(.85,.91,1.0))
area_emitter((-3.0,-4.0,3.2),power=350,size=5.0,target=(0,1.0,1.0),color=(1.0,.91,.80))
sc.render.resolution_x = 512
sc.render.resolution_y = 341
sc.render.resolution_percentage = 100
