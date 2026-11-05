from sceneact import *
import bpy
import math
import random

scene = Scene("Kitchen")
ivory = (.79, .80, .735)
metal = (.52, .55, .49)

def add(name, node):
    scene.include(name, node)
    return node

# Floor and its pale wood boards.
add("floor", box((7, 7, .08), center=(0, 0, -.05),
                 color=(.80, .79, .68)))
random.seed(14)
for i in range(28):
    x = -3.1 + i * .225
    for j in range(5):
        y = -3.7 + j * 1.35 + (i % 3) * .36
        c = random.uniform(.76, .86)
        add("plank_%d_%d" % (i, j),
            box((.223, 1.347, .012), center=(x, y, .001),
                color=(c + .025, c + .015, c - .055)))

add("back_wall", box((5, .12, 2.8), center=(0, .435, 1.35),
                     color=(.63, .64, .57)))
add("left_wall", box((.13, 3.4, 2.8), center=(-1.40, -.98, 1.35),
                     color=(.83, .84, .76)))
add("left_door_trim", box((.075, .11, 2.3), center=(-1.31, -.36, 1.1),
                          color=(.82, .81, .70)))
add("left_baseboard", box((.045, 3, .10), center=(-1.315, -1, .05),
                          color=(.76, .75, .63)))

# Navy ceramic tiles separated by light grout.
for row in range(7):
    for col in range(24):
        x = -2.55 + col * .181
        z = .927 + row * .181
        add("tile_%d_%d" % (row, col),
            box((.176, .018, .176), center=(x, .362, z),
                color=(.012, .035, .044)))

# Cabinet carcass and recessed plinth.
add("cabinet_body", box((2.48, .60, .74), center=(0, .005, .49),
                        color=ivory))
add("toe_shadow", box((2.45, .46, .105), center=(0, .065, .105),
                      color=(.47, .47, .39)))
add("plinth", box((2.39, .045, .105), center=(0, -.243, .075),
                  color=(.75, .75, .65)))
add("left_end", box((.045, .61, .72), center=(-1.236, 0, .49),
                    color=ivory))

front_y = -.311
for k, (low, high) in enumerate(((.145, .425), (.431, .654), (.660, .858))):
    add("drawer_%d" % k,
        box((.775, .035, high-low),
            center=(-.825, front_y, (low+high)/2), color=ivory))

add("middle_door", box((.775, .035, .713),
                       center=(-.039, front_y, .5015),
                       color=(.82, .825, .765)))
add("sink_door", box((.765, .035, .713),
                     center=(.740, front_y, .5015),
                     color=(.805, .81, .747)))
add("right_filler", box((.104, .035, .713),
                        center=(1.181, front_y, .5015), color=ivory))

def handle(name, x, z, width=.215):
    a = Asset(name)
    for k, dx in enumerate((-width/2, width/2)):
        a.include("mount_%d" % k,
                  rod(.009, start=(x+dx, -.337, z+.004),
                      end=(x+dx, -.365, z-.006), color=(.63, .65, .57)))
    a.include("grip",
              rod(.010, start=(x-width/2, -.366, z-.007),
                  end=(x+width/2, -.366, z-.007), color=(.68, .69, .60)))
    add(name, a)

for k, z in enumerate((.785, .600, .375)):
    handle("drawer_handle%d" % k, -.825, z)
handle("middle_handle", -.039, .786)
handle("right_handle", .740, .786)

# Worktop with openings for both sink bowls.
counter = box((2.59, .705, .039), center=(0, -.012, .895),
              color=(.45, .44, .38))
main_cut = fillet_box((.435, .435, .35), radius=.052,
                      center=(.650, .035, .875))
small_cut = fillet_box((.215, .365, .35), radius=.037,
                       center=(1.002, .062, .875))
add("countertop", subtract(counter, main_cut, small_cut))

# A thin rounded steel flange. Its bevel respects the flange thickness.
rim = fillet_box((.905, .542, .015), radius=.006,
                  center=(.875, .030, .923), color=metal)
rim = subtract(
    rim,
    fillet_box((.429, .427, .15), radius=.055,
               center=(.650, .035, .925)),
    fillet_box((.213, .359, .12), radius=.037,
               center=(1.002, .062, .925))
)
add("sink_rim", rim)

def basin(name, x, y, w, d, depth, radius):
    outer = fillet_box((w, d, depth), radius=radius,
                       center=(x, y, .925-depth/2), color=metal)
    inner = fillet_box((w-.016, d-.016, depth+.03),
                       radius=radius-.005,
                       center=(x, y, .925-depth/2+.023), color=metal)
    add(name, subtract(outer, inner))
    z = .925-depth+.012
    add(name+"_drain", rod(.039, length=.004,
                           center=(x, y-.05, z), color=(.27, .29, .25)))
    add(name+"_drain_ring", rod(.031, length=.006,
                                center=(x, y-.05, z+.003),
                                color=(.66, .67, .60)))
    add(name+"_drain_dark", rod(.023, length=.007,
                                center=(x, y-.05, z+.005),
                                color=(.16, .18, .16)))
    for a in range(8):
        ang = a*math.pi/4
        add(name+"_hole%d" % a,
            rod(.0026, length=.008,
                center=(x+.014*math.cos(ang),
                        y-.05+.014*math.sin(ang), z+.009),
                color=(.045, .05, .045)))

basin("large_bowl", .650, .035, .443, .441, .185, .058)
basin("small_bowl", 1.002, .062, .226, .373, .119, .040)

for i in range(8):
    x = 1.165+i*.027
    add("drainer_ridge%d" % i,
        rod(.0045, start=(x, -.18, .936), end=(x, .244, .936),
            color=(.56, .58, .51)))

# Chrome mixer faucet and lever.
add("tap_base", rod(.035, length=.022, center=(.835, .256, .941),
                     color=metal))
tap_points = [
    (.835, .256, .948), (.835, .256, 1.075),
    (.837, .256, 1.201), (.842, .251, 1.292),
    (.856, .235, 1.329), (.879, .205, 1.348),
    (.906, .164, 1.350), (.932, .123, 1.340),
    (.946, .092, 1.317), (.949, .078, 1.269)
]
add("tap_arch", sweep_tube(points=tap_points, radius=.0125,
                           color=(.60, .65, .61)))
add("tap_nozzle", rod(.016, start=(.949, .078, 1.275),
                      end=(.949, .078, 1.252), color=metal))
add("mixer_body", rod(.023, start=(.835, .256, .969),
                      end=(.800, .229, 1.040), color=metal))
add("mixer_lever", rod(.008, start=(.800, .229, 1.040),
                       end=(.789, .215, 1.101), color=metal))

# Cropped oven at the right edge.
add("oven_side", box((.57, .61, .84), center=(1.57, -.005, .43),
                     color=(.65, .67, .61)))
add("oven_dark_front", box((.51, .028, .51), center=(1.57, -.329, .448),
                           color=(.014, .030, .033)))
add("oven_lower_trim", box((.52, .04, .075), center=(1.57, -.34, .157),
                           color=(.58, .61, .58)))

realize(scene)

for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat is None:
            continue
        mat.use_nodes = True
        bs = mat.node_tree.nodes.get("Principled BSDF")
        if bs is None:
            continue
        bs.inputs["Roughness"].default_value = .38
        if any(s in obj.name for s in
               ("bowl", "sink_rim", "drain", "tap", "mixer", "drainer")):
            bs.inputs["Metallic"].default_value = .86
            bs.inputs["Roughness"].default_value = .23
        elif "handle" in obj.name:
            bs.inputs["Metallic"].default_value = .55
            bs.inputs["Roughness"].default_value = .29

def stone_surface(obj):
    mat = bpy.data.materials.new("Mottled_grey_worktop")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    bs.inputs["Roughness"].default_value = .79
    coord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 75
    noise.inputs["Detail"].default_value = 4
    noise.inputs["Roughness"].default_value = .72
    links.new(coord.outputs["Object"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .20
    ramp.color_ramp.elements[0].color = (.265, .265, .234, 1)
    ramp.color_ramp.elements[1].position = .80
    ramp.color_ramp.elements[1].color = (.53, .51, .45, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .20
    bump.inputs["Distance"].default_value = .008
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    obj.data.materials.clear()
    obj.data.materials.append(mat)

for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    if "countertop" in obj.name:
        stone_surface(obj)
    if "plank_" in obj.name and obj.data.materials:
        mat = obj.data.materials[0]
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bs = nodes.get("Principled BSDF")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 4
        noise.inputs["Detail"].default_value = 3
        coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = (100, 3, 5)
        links.new(coord.outputs["Generated"], mapping.inputs[0])
        links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .14
        bump.inputs["Distance"].default_value = .006
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bs.inputs["Normal"])
        bs.inputs["Roughness"].default_value = .65

set_view((-.29, -2.61, 2.15), (0, .005, .655), lens=37, sensor=36)
area_emitter((-2, -2, 3.4), power=450, size=3.2,
             target=(0, 0, .5), color=(1, .97, .88))
area_emitter((1, -1, 2.9), power=110, size=2.5,
             target=(.5, 0, .8), color=(.89, .94, 1))

world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.72, .76, .79, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .28

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 48
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 384
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.view_settings.view_transform = 'AgX'
