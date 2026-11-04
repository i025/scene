from sceneact import *
import bpy
import math
from mathutils import Vector

CAMERA_POSITION = (-1.20, -2.70, 2.00)
CAMERA_TARGET = (.34, 0, 1.62)
CAMERA_LENS = 60
CABINET_SIZE = (.81, .37, 1.33)
COUNTER_SIZE = (2.65, 1.30, .055)

scene = Scene("Kitchen corner")
cream = (.77, .71, .57)
doorcream = (.83, .77, .64)
white = (.88, .87, .80)
chrome = (.52, .55, .53)

def add(parent, name, node):
    parent.include(name, node)
    return node

def ring(parent, name, center, radius, tube, plane="xz",
         color=chrome, steps=24):
    pts = []
    for i in range(steps):
        a = 2 * math.pi * i / steps
        c, s = radius * math.cos(a), radius * math.sin(a)
        if plane == "yz":
            p = (center[0], center[1]+c, center[2]+s)
        elif plane == "xy":
            p = (center[0]+c, center[1]+s, center[2])
        else:
            p = (center[0]+c, center[1], center[2]+s)
        pts.append(p)
    result = Asset(name)
    for i in range(steps):
        add(result, "segment_%d" % i,
            rod(radius=tube, start=pts[i],
                end=pts[(i+1) % steps], color=color))
    add(parent, name, result)
    return result

architecture = Asset("Walls and counter")
add(architecture, "rear_wall",
    box((3.6, .08, 3.25), center=(.05, .39, 1.62),
        color=(.70, .66, .53)))
add(architecture, "counter",
    box(COUNTER_SIZE, center=(.05, -.28, .89),
        color=(.31, .29, .23)))
add(architecture, "backsplash",
    box((2.65, .025, .16), center=(.05, .345, .995),
        color=(.32, .30, .24)))
scene.include("architecture", architecture)

window = Asset("Window and blinds")
add(window, "glass",
    box((1.04, .025, 1.78), center=(-.52, .325, 1.97),
        color=(.66, .81, .84)))
for i, x in enumerate((-1.065, .025)):
    add(window, "jamb_%d" % i,
        box((.055, .10, 1.90), center=(x, .28, 1.97),
            color=white))
add(window, "sill",
    box((1.15, .18, .055), center=(-.52, .24, 1.065),
        color=white))
add(window, "middle_sash",
    box((1.04, .055, .045), center=(-.52, .265, 1.86),
        color=white))
add(window, "vertical_sash",
    box((.032, .045, 1.78), center=(-.65, .27, 1.97),
        color=white))
for i in range(32):
    slat = box((1.075, .065, .012),
               center=(-.52, .195, 1.105+i*.054),
               color=(.86, .86, .78))
    slat.turn(axis="+x", degrees=-12)
    add(window, "slat_%02d" % i, slat)
for i, x in enumerate((-.87, -.25)):
    add(window, "blind_tape_%d" % i,
        box((.012, .008, 1.75), center=(x, .155, 1.97),
            color=(.75, .75, .66)))
add(window, "pull_cord",
    rod(radius=.002, start=(-.13, .13, 2.48),
        end=(-.13, .13, 1.84), color=(.79, .77, .66)))
add(window, "cord_end",
    rod(radius=.009, length=.045, center=(-.13, .13, 1.83),
        color=(.77, .69, .49)))
scene.include("window", window)

cabinet = Asset("Cream upper cabinet")
add(cabinet, "carcase",
    box(CABINET_SIZE, center=(.58, .145, 2.205), color=cream))
add(cabinet, "door",
    box((.715, .035, 1.24), center=(.605, -.058, 2.225),
        color=doorcream))
add(cabinet, "inset_panel",
    box((.575, .012, 1.08), center=(.605, -.080, 2.235),
        color=(.79, .73, .60)))
for i, x in enumerate((.282, .928)):
    add(cabinet, "door_stile_%d" % i,
        box((.037, .024, 1.20), center=(x, -.09, 2.225),
            color=doorcream))
for i, z in enumerate((1.635, 2.815)):
    add(cabinet, "door_rail_%d" % i,
        box((.66, .024, .045), center=(.605, -.09, z),
            color=doorcream))
add(cabinet, "knob_stem",
    rod(radius=.009, start=(.947, -.105, 1.845),
        end=(.947, -.137, 1.845), color=(.40, .35, .23)))
add(cabinet, "knob",
    ball(.018, center=(.947, -.145, 1.845),
         color=(.47, .42, .28)))
scene.include("cabinet", cabinet)

paper = Asset("Mounted paper towel roll")
rollx, rolly, rollz = .565, -.228, 2.085
add(paper, "paper",
    rod(radius=.112, length=.56,
        center=(rollx, rolly, rollz), color=(.94, .91, .81)))
add(paper, "loose_sheet",
    box((.148, .006, .535),
        center=(rollx-.014, rolly-.105, rollz-.007),
        color=(.94, .91, .82)))
for i, z in enumerate((rollz-.309, rollz+.309)):
    add(paper, "axle_%d" % i,
        rod(radius=.017, length=.06, center=(rollx, rolly, z),
            color=(.36, .35, .29)))
    add(paper, "wall_arm_%d" % i,
        rod(radius=.018, start=(rollx, -.09, z),
            end=(rollx, rolly, z), color=(.34, .34, .29)))
add(paper, "top_finial",
    ball(.025, center=(rollx, rolly, rollz+.33), color=chrome))
scene.include("paper", paper)

towel = Asset("Ring and hanging towel")
add(towel, "mount",
    rod(radius=.035, start=(.145, .075, 1.925),
        end=(.187, .075, 1.925), color=chrome))
add(towel, "mount_neck",
    rod(radius=.012, start=(.145, .075, 1.925),
        end=(.112, .025, 1.925), color=chrome))
r = ring(towel, "ring", (.110, -.018, 1.815),
         .113, .006, "yz")
r.turn(axis="+z", degrees=-36, pivot=(.110, -.018, 1.815))

# A rounded proxy receives a continuous folded surface after realization.
add(towel, "cloth",
    box((.24, .045, .55), center=(.10, -.145, 1.43),
        color=(.89, .87, .78)))
backcloth = box((.13, .025, .34),
                center=(.225, -.045, 1.47),
                color=(.80, .77, .66))
backcloth.turn(axis="+y", degrees=-18)
add(towel, "rear_drape", backcloth)
scene.include("towel", towel)

sink = Asset("Sink and faucet")
add(sink, "rim",
    box((.66, .48, .018), center=(-.64, -.415, .925),
        color=(.38, .40, .35)))
add(sink, "basin_dark",
    box((.58, .405, .023), center=(-.64, -.43, .928),
        color=(.035, .043, .032)))
add(sink, "inner_bottom",
    box((.46, .31, .014), center=(-.64, -.43, .936),
        color=(.045, .055, .04)))
add(sink, "faucet_base",
    rod(radius=.04, length=.023, center=(-.56, -.185, .94),
        color=chrome))
add(sink, "faucet_stem",
    rod(radius=.013, start=(-.56, -.185, .95),
        end=(-.56, -.185, 1.205), color=chrome))
add(sink, "faucet_top",
    rod(radius=.013, start=(-.56, -.185, 1.205),
        end=(-.56, -.255, 1.235), color=chrome))
add(sink, "spout",
    rod(radius=.012, start=(-.56, -.255, 1.235),
        end=(-.56, -.315, 1.205), color=chrome))
for i, x in enumerate((-.67, -.44)):
    add(sink, "tap_base_%d" % i,
        rod(radius=.026, length=.018, center=(x, -.19, .946),
            color=chrome))
    add(sink, "tap_handle_%d" % i,
        rod(radius=.009, start=(x, -.19, .956),
            end=(x+.032, -.18, .986), color=chrome))
add(sink, "soap_dish",
    box((.13, .10, .025), center=(-.89, -.22, .944),
        color=(.59, .57, .43)))
add(sink, "soap",
    box((.09, .065, .023), center=(-.89, -.22, .969),
        color=(.82, .79, .64)))
sink.move((.51, .425, 0))
scene.include("sink", sink)

blender = Asset("Blender and small canister")
add(blender, "motor",
    rod(radius=.077, length=.19, center=(.36, .018, 1.02),
        color=(.035, .043, .038)))
add(blender, "motor_top",
    rod(radius=.080, length=.022, center=(.36, .018, 1.12),
        color=(.10, .105, .085)))
cup = rod(radius=.060, length=.205, center=(.36, .018, 1.23),
          color=(.48, .51, .44), opacity=.30)
cup.turn(axis="+y", degrees=-9)
add(blender, "clear_cup", cup)
ring(blender, "cup_rim", (.344, .018, 1.332),
     .059, .004, "xy", color=(.63, .64, .54), steps=16)
add(blender, "can",
    rod(radius=.043, length=.18, center=(.18, .055, 1.005),
        color=(.32, .37, .20)))
add(blender, "can_lid",
    rod(radius=.045, length=.012, center=(.18, .055, 1.10),
        color=(.59, .57, .39)))
add(blender, "small_bottle",
    rod(radius=.020, length=.095, center=(.205, -.08, .982),
        color=(.45, .46, .32)))
scene.include("blender", blender)

jug = Asset("Translucent gallon jug")
jx, jy = .60, -.185
add(jug, "body",
    fillet_box((.235, .172, .225), radius=.044,
               center=(jx, jy, 1.037),
               color=(.73, .75, .67), opacity=.87))
add(jug, "shoulder",
    ball(.105, center=(jx, jy, 1.138),
         color=(.75, .77, .69), opacity=.87))
add(jug, "neck",
    rod(radius=.031, length=.062, center=(jx, jy, 1.218),
        color=(.77, .78, .70), opacity=.88))
add(jug, "cap",
    rod(radius=.034, length=.025, center=(jx, jy, 1.251),
        color=(.85, .84, .75)))
add(jug, "handle",
    sweep_tube(points=[
        (jx+.060, jy-.002, 1.174),
        (jx+.107, jy-.002, 1.156),
        (jx+.112, jy-.002, 1.111),
        (jx+.081, jy-.002, 1.088)],
        radius=.014, color=(.78, .79, .71)))
scene.include("jug", jug)

pitcher = Asset("Blue water filter pitcher")
px, py = .91, .075
add(pitcher, "blue_body",
    fillet_box((.235, .18, .315), radius=.047,
               center=(px, py, 1.077),
               color=(.032, .075, .16), opacity=.84))
add(pitcher, "water_lower",
    box((.18, .13, .105), center=(px, py, 1.001),
        color=(.045, .11, .19), opacity=.65))
lid = fillet_box((.245, .19, .036), radius=.014,
                 center=(px-.007, py, 1.245),
                 color=(.31, .33, .29))
lid.turn(axis="+y", degrees=9)
add(pitcher, "lid", lid)
add(pitcher, "spout",
    box((.058, .13, .042), center=(px-.123, py, 1.232),
        color=(.32, .34, .30)))
add(pitcher, "clear_handle",
    sweep_tube(points=[
        (px+.107, py, 1.22),
        (px+.170, py, 1.193),
        (px+.196, py, 1.105),
        (px+.178, py, 1.008),
        (px+.116, py, .976)],
        radius=.017, color=(.48, .51, .46)))
add(pitcher, "base_rim",
    box((.19, .15, .018), center=(px, py, .925),
        color=(.16, .19, .19)))
scene.include("pitcher", pitcher)

# Source checks: positive dimensions; legal fillet radii; distinct rod/sweep
# endpoints; unique repeated keys; explicit rotation pivot for mounted ring.
# Realization precedes all Blender customization. No render or save calls.
realize(scene)

def noise_material(name, colors, scale, roughness=.7, bump_strength=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    n, links = mat.node_tree.nodes, mat.node_tree.links
    bs = n.get("Principled BSDF")
    bs.inputs["Roughness"].default_value = roughness
    tex = n.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 2
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .35
    ramp.color_ramp.elements[0].color = (*colors[0], 1)
    ramp.color_ramp.elements[1].position = .65
    ramp.color_ramp.elements[1].color = (*colors[1], 1)
    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    if bump_strength:
        bump = n.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = .001
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return mat

granite = noise_material(
    "Warm granular granite",
    ((.055, .045, .033), (.48, .40, .29)), 175, .70, .18)
paper_mat = noise_material(
    "Paper surface", ((.83, .80, .70), (.96, .93, .84)),
    145, .92, .08)
cloth_mat = noise_material(
    "Ivory terrycloth", ((.76, .73, .64), (.91, .88, .79)),
    190, .95, .12)

def world_bounds(obj):
    points = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    return (low+high)*.5, high-low

for obj in list(bpy.context.scene.objects):
    if obj.type != "MESH":
        continue
    center, dims = world_bounds(obj)
    counter = (abs(dims.x-2.65)<.015 and
               abs(dims.y-1.30)<.015 and abs(center.z-.89)<.015)
    splash = (abs(dims.x-2.65)<.015 and
              abs(dims.y-.025)<.01 and abs(center.z-.995)<.015)
    if counter or splash:
        obj.data.materials.clear()
        obj.data.materials.append(granite)
    elif (abs(center.x-rollx)<.12 and abs(center.z-rollz)<.08
          and dims.z>.45):
        obj.data.materials.clear()
        obj.data.materials.append(paper_mat)

    # Replace the cloth proxy within its existing assembly by a folded surface.
    if (abs(center.x-.10)<.005 and abs(center.y+.145)<.005
        and abs(dims.x-.24)<.005 and abs(dims.z-.55)<.005):
        verts, faces = [], []
        cols, rows = 24, 18
        for j in range(rows+1):
            v = j/rows
            for i in range(cols+1):
                u = i/cols
                width = .145 + .095*math.sin(math.pi*v*.78)
                x = .10 + (u-.5)*width - .035*v
                hem = .045*math.cos(u*math.pi*2) + .02*u
                z = 1.72 - v*(.57+hem)
                y = -.145 + .022*math.sin(u*math.pi*7+.5*v)
                y -= .018*math.sin(math.pi*v)
                verts.append((x, y, z))
        for j in range(rows):
            for i in range(cols):
                a = j*(cols+1)+i
                faces.append((a, a+1, a+cols+2, a+cols+1))
        mesh = bpy.data.meshes.new("Continuous draped towel")
        mesh.from_pydata(
            [tuple(obj.matrix_world.inverted() @ Vector(p)) for p in verts],
            [], faces)
        mesh.update()
        obj.data = mesh
        mesh.materials.append(cloth_mat)
        for polygon in mesh.polygons:
            polygon.use_smooth = True
        solid = obj.modifiers.new("Cloth thickness", "SOLIDIFY")
        solid.thickness = .004
        sub = obj.modifiers.new("Soft cloth folds", "SUBSURF")
        sub.levels = 1
        sub.render_levels = 1

    for mat in obj.data.materials:
        if mat and mat.use_nodes and mat not in (granite, paper_mat, cloth_mat):
            bs = mat.node_tree.nodes.get("Principled BSDF")
            if bs:
                col = bs.inputs["Base Color"].default_value
                if max(col[:3])-min(col[:3])<.08 and .3<col[0]<.65:
                    bs.inputs["Metallic"].default_value = .70
                    bs.inputs["Roughness"].default_value = .26

font = bpy.data.curves.new("Filter label", "FONT")
font.body = "FILTER"
font.align_x = "CENTER"
font.size = .027
font.extrude = .0001
label = bpy.data.objects.new("Jug label", font)
bpy.context.collection.objects.link(label)
label.location = (jx, jy-.088, 1.001)
label.rotation_euler = (math.pi/2, 0, 0)
ink = bpy.data.materials.new("Muted label ink")
ink.diffuse_color = (.24, .26, .22, 1)
font.materials.append(ink)

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("Kitchen daylight")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.69,.73,.76,1)
world.node_tree.nodes["Background"].inputs[1].default_value = .38
area_emitter((-1.3,-.02,2.15), power=130, size=1.15,
             target=(.45,.05,1.3), color=(.83,.91,1))
area_emitter((-.25,-1.6,2.8), power=80, size=2.5,
             target=(.4,0,1.6), color=(1,.83,.62))
bpy.context.scene.view_settings.view_transform = "AgX"
bpy.context.scene.view_settings.exposure = -.65
