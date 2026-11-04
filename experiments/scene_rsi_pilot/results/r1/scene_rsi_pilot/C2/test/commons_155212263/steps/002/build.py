from sceneact import *
import bpy
import math

# Evidence / ownership ledger, visual estimates in 512x384 image coordinates:
# Reference bench runs from (0,100) toward (512,280); foreground end is cropped.
# Render 1 bench runs approximately (50,177)-(505,268), too shallow and distant.
# Reference large wheel: center ~(342,96), vertical radius ~45.
# Render 1 large wheel: center ~(339,151), vertical radius ~33.
# Reference blue wheel: center ~(181,108); render 1 ~(191,149).
# Reference anvil body: ~(228,150); render 1 ~(235,187).
# Reference floor marker ~(68,271); render 1 ~(96,285).
# These are visual hypotheses, not measured calibration.
# Measured evidence: step 1 returned a valid image; reported execute elapsed 42.891 s.
#
# Selected family: CAMERA ONLY. Move closer and farther along bench direction,
# lower the look-at point. Prediction: stronger near/far size gradient, steeper
# bench edges, higher wheel/window anchors, near bench and bins cropped at right.
# Geometry, material palette, shaders and lighting remain as in successful step 1.
# Three independent anchors supporting correction: shallow architectural sill /
# bench edge direction, undersized low rear wheel, insufficient near bench crop.
#
# Inventory: architecture and floor; heavy continuous workbench; near lathe;
# blue-wheel lathe; tall flywheel machine; anvil and stump; three far lathes;
# two upright drills; open drawer; pale scrap bin; green container and lid;
# loose tools and plates; sill vessels; wall tools/pipe; floor arrow marker.
# Foreground lathe occludes drawer/frame; bench occludes back legs.
# Some far machine identities and wheel planes remain uncertain.
# Relative world scale: actual bench support surface z=1.04.

CAMERA = dict(position=(4.35, -4.55, 3.15),
              target=(-0.55, 0.10, 0.70), lens=39)
BENCH = dict(xmin=-5.4, xmax=3.0, front=-0.53, back=0.72, top=1.04)
WALL_Y = 0.94
WOOD = (0.25, 0.20, 0.12)
TOP = (0.39, 0.34, 0.23)
EDGE = (0.20, 0.17, 0.11)
IRON = (0.14, 0.155, 0.15)
WORN = (0.34, 0.35, 0.32)
RUST = (0.27, 0.205, 0.14)
BLUE = (0.18, 0.29, 0.31)
PLASTER = (0.51, 0.54, 0.47)
PALE = (0.68, 0.69, 0.61)

scene = Scene("Historic metalworking workshop")

def cube(owner, name, size, pos, col):
    return owner.include(name, box(size, center=pos, color=col))

def bar(owner, name, a, b, r, col=IRON):
    return owner.include(name, rod(radius=r, start=a, end=b, color=col))

def ring(owner, name, center, radius, tube, color, segments=24, plane="xz"):
    p = Part(name)
    cx, cy, cz = center
    pts = []
    for i in range(segments):
        t = 2*math.pi*i/segments
        if plane == "xz":
            pts.append((cx+radius*math.cos(t), cy, cz+radius*math.sin(t)))
        elif plane == "yz":
            pts.append((cx, cy+radius*math.cos(t), cz+radius*math.sin(t)))
        else:
            pts.append((cx+radius*math.cos(t), cy+radius*math.sin(t), cz))
    for i in range(segments):
        bar(p, "rim_%02d" % i, pts[i], pts[(i+1) % segments], tube, color)
    return owner.include(name, p)

def wheel(owner, name, center, radius, color, spokes=5):
    p = Part(name)
    x, y, z = center
    ring(p, "outer", center, radius, .025, color)
    ring(p, "inner_edge", (x,y+.022,z), radius-.035, .011, WORN)
    bar(p, "hub", (x,y-.065,z), (x,y+.075,z), .068, color)
    for i in range(spokes):
        a = 2*math.pi*i/spokes+.2
        b = a+.20
        start = (x+.055*math.cos(a), y, z+.055*math.sin(a))
        bend = (x+radius*.57*math.cos(b), y, z+radius*.57*math.sin(b))
        end = (x+(radius-.025)*math.cos(a+.12),
               y, z+(radius-.025)*math.sin(a+.12))
        bar(p, "spoke_%d_a" % i, start, bend, .024, color)
        bar(p, "spoke_%d_b" % i, bend, end, .024, color)
    bar(p, "crank_pin", (x+radius*.68,y,z-.08),
        (x+radius*.68,y-.13,z-.08), .024, WORN)
    return owner.include(name, p)

# Architecture Asset owns floorboards, wall, glazing, window frames and sills.
architecture = Asset("architecture")
cube(architecture, "floor_base", (14,10,.09), (-1,-2,-.065), WOOD)
for i in range(43):
    y = -6.2+i*.175
    cube(architecture, "floorboard_%02d" % i, (13,.169,.035),
         (-1,y,-.005),
         (.43+.014*(i%4), .355+.01*(i%3), .235+.008*(i%4)))
cube(architecture, "rear_plaster", (12,.18,4.1),
     (-1,WALL_Y+.12,2.0), PLASTER)
cube(architecture, "left_return", (.18,5,4.1),
     (-6.0,-1.45,2.0), (.48,.49,.43))
for i, (x,w) in enumerate([(-4.65,1.45),(-2.55,1.65),
                            (-.25,1.85),(1.75,1.35)]):
    win = Part("window_%d" % i)
    cube(win, "recess", (w+.17,.12,2.2), (x,.815,2.91), (.25,.28,.25))
    cube(win, "glass", (w,.035,2.04), (x,.728,2.94), (.76,.86,.89))
    for sx in (-1,1):
        cube(win, "jamb_%d" % sx, (.065,.14,2.18),
             (x+sx*w/2,.67,2.94), PALE)
    for z in (1.86,3.98):
        cube(win, "horizontal_%.2f" % z, (w+.13,.17,.065),
             (x,.65,z), PALE)
    cube(win, "central_mullion", (.048,.105,2.06),
         (x,.65,2.94), (.48,.52,.48))
    cube(win, "crossbar", (w,.09,.042), (x,.64,2.72), PALE)
    cube(win, "deep_sill", (w+.30,.39,.095),
         (x,.68,1.81), (.29,.30,.25))
    architecture.include("window_%d" % i, win)
scene.include("architecture", architecture)

# Workbench owner includes top, front edge, legs, rails and attached braces.
bench = Asset("continuous_workbench")
cube(bench, "top", (8.4,1.25,.15), (-1.2,.095,.965), TOP)
cube(bench, "front_worn_edge", (8.4,.11,.20), (-1.2,-.53,.93), EDGE)
for i,x in enumerate([-5.1,-3.65,-2.15,-.55,1.1,2.7]):
    for j,y in enumerate([-.40,.57]):
        cube(bench, "post_%d_%d" % (i,j), (.15,.17,.91), (x,y,.46), WOOD)
    cube(bench, "crossfoot_%d" % i, (.24,1.12,.12), (x,.06,.12), EDGE)
    bar(bench, "diagonal_%d" % i, (x-.02,-.37,.19),
        (x+.47,.51,.85), .055, WOOD)
cube(bench, "low_front_rail", (8.1,.12,.13), (-1.2,-.40,.28), EDGE)
cube(bench, "rear_rail", (8.1,.12,.13), (-1.2,.57,.34), EDGE)
scene.include("workbench", bench)

# Each lathe is a separate Asset; all machine parts share that owner.
# Inputs x/y/length/scale control pose and dimensions independently of camera.
def lathe(name, x, y, length, scale=1, color=IRON):
    a = Asset(name)
    z = BENCH["top"]
    left, right = x-length/2, x+length/2
    for i,xx in enumerate([left+.14,right-.18]):
        cube(a, "foot_%d" % i, (.25*scale,.52*scale,.105*scale),
             (xx,y,z+.053*scale), color)
        cube(a, "upright_%d" % i, (.11*scale,.27*scale,.22*scale),
             (xx,y,z+.18*scale), color)
    for j,yy in enumerate([y-.14*scale,y+.14*scale]):
        cube(a, "bed_rail_%d" % j, (length,.065*scale,.10*scale),
             (x,yy,z+.28*scale), WORN)
    axisz = z+.48*scale
    cube(a, "headstock_base", (.33*scale,.38*scale,.16*scale),
         (right-.18,y,z+.35*scale), color)
    bar(a, "headstock_body", (right-.35*scale,y,axisz),
        (right-.01,y,axisz), .145*scale, color)
    bar(a, "spindle", (right-.59*scale,y,axisz),
        (right+.29*scale,y,axisz), .042*scale, WORN)
    bar(a, "chuck", (right-.49*scale,y,axisz),
        (right-.35*scale,y,axisz), .098*scale, color)
    cube(a, "tailstock_foot", (.31*scale,.35*scale,.09*scale),
         (left+.24,y,z+.34*scale), color)
    bar(a, "tailstock_barrel", (left+.08,y,axisz),
        (left+.38,y,axisz), .09*scale, color)
    bar(a, "tail_spindle", (left-.05,y,axisz),
        (left+.58,y,axisz), .028*scale, WORN)
    cube(a, "carriage", (.40*scale,.48*scale,.07*scale),
         (x-.1,y-.04,z+.355*scale), WORN)
    cube(a, "tool_holder", (.13*scale,.14*scale,.12*scale),
         (x-.05,y,z+.45*scale), color)
    bar(a, "tool_post", (x-.05,y,z+.46*scale),
        (x-.05,y,z+.65*scale), .023*scale, WORN)
    bar(a, "tool_handle", (x-.14,y,z+.63*scale),
        (x+.08,y,z+.63*scale), .015*scale, color)
    bar(a, "feed_screw", (left,y-.24*scale,z+.25*scale),
        (right+.10,y-.24*scale,z+.25*scale), .018*scale, WORN)
    bar(a, "right_crank", (right+.28,y,axisz),
        (right+.28,y,axisz-.20*scale), .023*scale, color)
    bar(a, "right_grip", (right+.28,y,axisz-.20*scale),
        (right+.28,y-.16*scale,axisz-.20*scale), .034*scale, WOOD)
    return scene.include(name, a)

near = lathe("foreground_lathe", 1.65,-.13,1.92,1.0)
middle = lathe("blue_wheel_lathe", -2.35,.12,1.30,.70,BLUE)
wheel(middle, "blue_flywheel", (-2.28,.27,1.66), .31, BLUE, 5)
bar(middle, "wheel_pedestal", (-2.28,.30,1.06),
    (-2.28,.30,1.65), .052, IRON)

drive = Asset("large_flywheel_machine")
cube(drive, "base", (.65,.56,.09), (.70,.43,1.085), IRON)
for i,x in enumerate([.48,.91]):
    bar(drive, "frame_leg_%d" % i, (x,.45,1.10),
        (.70,.46,1.92), .047, IRON)
bar(drive, "axle", (.70,.23,1.99), (.70,.68,1.99), .052, WORN)
wheel(drive, "large_flywheel", (.70,.31,1.99), .47, IRON, 5)
ring(drive, "rear_pulley", (.70,.58,1.99), .34,.027,RUST,20)
bar(drive, "lower_shaft", (.63,.42,1.17), (.63,.42,1.63), .06, IRON)
cube(drive, "bearing", (.22,.22,.14), (.70,.45,1.61), WORN)
scene.include("large_flywheel_machine", drive)

# Anvil and stump remain separate editable semantic owners.
stump = Asset("anvil_stump")
cube(stump, "block", (.60,.57,.68), (-.88,-.08,.70), (.26,.20,.12))
for i in range(3):
    cube(stump, "end_grain_line_%d" % i, (.018,.575,.65),
         (-1.10+i*.17,-.08,.70), (.20,.16,.10))
scene.include("anvil_stump", stump)
anvil = Asset("anvil")
cube(anvil, "foot", (.67,.43,.09), (-.88,-.08,1.07), RUST)
cube(anvil, "waist", (.30,.30,.24), (-.89,-.08,1.22), RUST)
cube(anvil, "shoulders", (.49,.36,.11), (-.89,-.08,1.36), RUST)
cube(anvil, "flat_face", (.69,.38,.11), (-.88,-.08,1.46), (.36,.31,.22))
for i in range(7):
    r = .15*(1-i/8)
    bar(anvil, "horn_%d" % i, (-.53+i*.068,-.08,1.43),
        (-.53+(i+1)*.068,-.08,1.43+.008*i), r, RUST)
cube(anvil, "square_heel", (.18,.35,.12), (-1.28,-.08,1.45), RUST)
scene.include("anvil", anvil)

for i,(x,s) in enumerate([(-3.50,.72),(-4.45,.56),(-5.16,.43)]):
    a = lathe("far_lathe_%d" % i, x,.10,.96*s,s,IRON)
    wheel(a, "small_handwheel", (x-.20,.12,1.04+.57*s), .18*s, IRON, 4)

for i,x in enumerate([-3.65,-4.72]):
    drill = Asset("upright_drill_%d" % i)
    cube(drill, "foot", (.30,.35,.08), (x,.51,1.08), IRON)
    bar(drill, "column", (x,.55,1.10), (x,.55,1.95-i*.08), .034, IRON)
    cube(drill, "head", (.27,.20,.16), (x-.08,.51,1.81-i*.08), WORN)
    bar(drill, "bit", (x-.16,.44,1.50),
        (x-.16,.44,1.77-i*.08), .015, IRON)
    cube(drill, "table", (.29,.25,.045), (x-.12,.43,1.36), IRON)
    scene.include("upright_drill_%d" % i, drill)

# Drawer owns its front, sides, handle and contents; supported by bench underside.
drawer = Asset("open_drawer")
cube(drawer, "bottom", (.99,.68,.055), (1.18,-.79,.64), (.24,.23,.16))
cube(drawer, "front", (.99,.09,.25), (1.18,-1.12,.76), EDGE)
for i,x in enumerate([.70,1.66]):
    cube(drawer, "side_%d" % i, (.055,.66,.24), (x,-.79,.76), WOOD)
bar(drawer, "handle", (1.04,-1.18,.76), (1.32,-1.18,.76), .025, IRON)
for i in range(4):
    cube(drawer, "contents_%d" % i, (.57,.045,.045),
         (1.10,-.95+i*.09,.70), WORN)
scene.include("open_drawer", drawer)

def bin_asset(name, x, y, r, h, col):
    a = Asset(name)
    bar(a, "bottom", (x,y,.025), (x,y,.065), r, col)
    for i in range(16):
        angle = 2*math.pi*i/16
        xx = x+r*.94*math.cos(angle)
        yy = y+r*.94*math.sin(angle)
        bar(a, "wall_%d" % i, (xx,yy,.06), (xx,yy,h), r*.19, col)
    ring(a, "lip", (x,y,h), r,.016,col,20,"xy")
    cube(a, "scrap", (.23,.12,.08), (x-.04,y,h-.07), WOOD)
    return scene.include(name, a)

bin_asset("pale_scrap_bin", 1.95,-.55,.29,.53, (.52,.51,.41))
bin_asset("dark_green_container", 2.89,-.30,.34,.52, (.20,.28,.21))
lid = Asset("container_lid")
bar(lid, "flat_lid", (2.91,-.30,.53), (2.91,-.30,.57), .35, (.29,.27,.16))
scene.include("container_lid", lid)

# Loose tools use the actual bench surface, independent of tall machine AABBs.
tools = Asset("loose_bench_tools")
for i in range(6):
    x = .30+i*.105
    y = -.25-(i%2)*.07
    bar(tools, "metal_tool_%d" % i, (x,y,1.065),
        (x+.26,y+.16,1.065), .018, WORN)
    bar(tools, "wood_grip_%d" % i, (x-.10,y-.06,1.065),
        (x,y,1.065), .026, WOOD)
for i in range(5):
    cube(tools, "flat_plate_%d" % i, (.19,.16,.018),
         (1.18+(i%3)*.19,-.27+(i//3)*.23,1.075+i*.004), WORN)
for i in range(5):
    bar(tools, "far_rod_%d" % i, (-3.08,-.30+i*.062,1.066),
        (-2.50,-.30+i*.062,1.066), .012, WORN)
scene.include("loose_bench_tools", tools)

for i,x in enumerate([-4.9,-4.65,-3.85,-3.55,-2.92,-2.70,-2.42,-1.75]):
    a = Asset("sill_vessel_%d" % i)
    h = .13+.035*(i%3)
    bar(a, "body", (x,.62,1.86), (x,.62,1.86+h), .041,
        WORN if i%3 else (.31,.25,.18))
    bar(a, "neck", (x,.62,1.86+h), (x,.62,1.91+h), .018, IRON)
    if i%2:
        bar(a, "inserted_tool", (x,.62,1.90+h),
            (x-.04,.62,2.14+h), .011, IRON)
    scene.include("sill_vessel_%d" % i, a)

walltools = Asset("wall_hung_tools")
for i,(x,z) in enumerate([(-3.55,2.25),(-1.48,2.35),(-1.16,2.21),
                            (2.64,2.30),(2.85,1.82)]):
    bar(walltools, "handle_%d" % i, (x,.78,z-.38),
        (x+.07,.78,z+.29), .026, WOOD)
    cube(walltools, "head_%d" % i, (.19,.065,.075),
         (x+.07,.77,z+.29), IRON)
bar(walltools, "long_leaning_rod", (2.67,.73,1.07),
    (3.04,.77,2.83), .026, RUST)
for i,(a,b) in enumerate([
    ((2.40,.75,3.1),(2.40,.75,2.13)),
    ((2.40,.75,2.13),(2.49,.75,1.91)),
    ((2.49,.75,1.91),(2.71,.75,1.83))
]):
    bar(walltools, "pipe_%d" % i, a,b,.019,IRON)
scene.include("wall_hung_tools", walltools)

marker = Asset("floor_arrow_marker")
bar(marker, "disc", (-1.97,-2.07,.016), (-1.97,-2.07,.025),
    .25, (.35,.42,.41))
cube(marker, "arrow_stem", (.10,.22,.008),
     (-1.97,-2.07,.033), (.72,.75,.70))
head = box((.20,.20,.008), center=(-1.97,-2.18,.033), color=(.72,.75,.70))
head.turn("+z",45)
marker.include("arrow_head", head)
scene.include("floor_marker", marker)

# Appearance comparison: render 1 is broadly paler and more evenly illuminated
# than the photograph, especially the bench and floor. That remains an appearance
# hypothesis for a later controlled revision; lights/materials are held fixed here.
#
# Inline pre-execution self-review (code review, not a regression-test claim):
# Inventory and ownership retained. Attached lathe nodes are returned by include,
# so wheels/pedestals stay descendants of their complete semantic owners.
# Actual supports: bench z=1.04, stump top z=1.04, sill top ~1.86,
# bins/posts at floor ~0. No new support or dependency transform is introduced.
# Expected negative space in wheel rims, between legs, and inside drawer retained.
# Approximately 700 primitive meshes; wheel rims/spokes are the largest repeated
# decorative family, followed by 43 floorboards and two 16-segment bin walls.
# Ring builder expands to one rod per segment; no fillets or dense straight sweeps.
# All dimensions/radii are positive and finite; all rod endpoints distinct.
# Include slots are unique within each owner. No geometry is created after realize.
# Camera/world/lights follow realize. Shader traversal below asserts nonempty
# semantic descendants and copies mesh/material state before scoped edits.
# Only CAMERA differs intentionally from the successful construction/appearance.

realize(scene)

def mesh_descendants(marker_name):
    root = bpy.data.objects.get(marker_name)
    if root is None:
        candidates = [o for o in bpy.data.objects
                      if o.type == "EMPTY" and o.name.split(".")[0] == marker_name]
        assert candidates, marker_name
        root = candidates[0]
    meshes = [o for o in root.children_recursive if o.type == "MESH"]
    assert meshes, marker_name
    return meshes

def add_surface_variation(marker_name, scale, strength):
    for ob in mesh_descendants(marker_name):
        ob.data = ob.data.copy()
        for idx,mat in enumerate(ob.data.materials):
            if mat is None:
                continue
            mat = mat.copy()
            ob.data.materials[idx] = mat
            mat.use_nodes = True
            nt = mat.node_tree
            bs = nt.nodes.get("Principled BSDF")
            if bs is None:
                continue
            bs.inputs["Roughness"].default_value = .87
            tex = nt.nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value = scale
            tex.inputs["Detail"].default_value = 2
            bump = nt.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = strength
            bump.inputs["Distance"].default_value = .035
            nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])

add_surface_variation("architecture", 7,.28)
add_surface_variation("workbench", 18,.34)

set_view(CAMERA["position"], CAMERA["target"], lens=CAMERA["lens"], sensor=36)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.65,.72,.77,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .32
area_emitter((-1.6,.15,3.8), power=1150, size=5.0,
             target=(-.7,-.9,.6), color=(.88,.94,1))
area_emitter((2,-3.8,3.5), power=280, size=4,
             target=(0,0,1), color=(1,.88,.72))
