from sceneact import *
import bpy
import random
from mathutils import Vector

random.seed(8)
scene = Scene("Industrial kitchen")

def cube(name, size, center, color):
    node = box(size=size, center=center, color=color)
    scene.include(name, node)
    return node

dark = (.035, .043, .039)
front = (.57, .59, .565)

# Pale porcelain floor.
cube("floor foundation", (18, 18, .10), (0, 0, -.08), (.45, .45, .42))
for i in range(-8, 9):
    for j in range(-7, 8):
        v = .69 + random.uniform(-.018, .018)
        cube("tile_%d_%d" % (i, j), (1.197, 1.197, .035),
             (i*1.2, j*1.2, -.012), (v, v*.995, v*.965))

# The camera looks into an open showroom.
cube("rear wall", (12, .18, 4.3), (0, 2.43, 2.15), (.36, .38, .355))
cube("black ceiling", (16, 16, .15), (0, 0, 4.13), (.023, .029, .027))
for x in [-4, -2.8, -1.6, -.4, .8, 2, 3.2, 4.4]:
    cube("ceiling joist "+str(x), (.07, 12, .15),
         (x, 0, 4.01), (.035, .045, .041))
for y in [-2.5, -.8, .85, 2.5]:
    cube("ceiling crossbeam "+str(y), (12, .18, .26),
         (0, y, 3.96), (.055, .068, .062))
cube("large overhead girder", (.30, 12, .35),
     (1.9, 0, 3.87), (.085, .105, .096))

post_center = (-3.28, -.90, 2.06)
cube("foreground timber column", (.26, .27, 4.12),
     post_center, (.43, .29, .17))
cube("right timber column", (.18, .22, 3.8),
     (3.02, 1.8, 1.9), (.43, .29, .17))

# Back counter and dark tiled recess.
cube("rear plinth", (5.25, .58, .12), (-.08, 1.87, .08), (.016, .020, .017))
cube("rear base cabinets", (5.2, .65, .83), (-.08, 1.87, .515), dark)
cube("rear stone countertop", (5.30, .74, .055),
     (-.08, 1.82, .96), (.065, .075, .067))
for x in [-2.15, -1.5, -.85, -.2, .45, 1.10, 1.75]:
    cube("rear cabinet seam "+str(x), (.009, .014, .77),
         (x, 1.539, .515), (.012, .016, .013))

cube("dark backsplash", (5.28, .07, 1.05),
     (-.07, 2.085, 1.49), (.055, .066, .058))
for x in [-2.6, -1.78, -.96, -.14, .68, 1.5, 2.32]:
    cube("stone vertical joint "+str(x), (.007, .01, .95),
         (x, 2.043, 1.47), (.025, .031, .027))
cube("stone horizontal joint", (5.22, .01, .007),
     (-.07, 2.041, 1.57), (.025, .031, .027))
cube("upper black cupboards", (4.42, .44, .53),
     (-.34, 2.03, 2.225), (.035, .044, .038))
cube("warm underside strip", (3.35, .025, .013),
     (-.64, 1.805, 1.955), (.8, .63, .45))

# Tall left cupboard.
cube("left cabinet carcass", (.93, .83, 2.53),
     (-2.74, 1.71, 1.285), (.028, .035, .030))
cube("left cabinet face", (.90, .035, 2.48),
     (-2.74, 1.275, 1.29), (.065, .075, .066))
cube("left upper door seam", (.89, .013, .007),
     (-2.74, 1.25, 2.16), (.022, .029, .024))
cube("left vertical door seam", (.007, .013, 2.43),
     (-2.65, 1.249, 1.285), (.022, .029, .024))

# Right appliance bank.
cube("oven cabinet", (.83, .79, 2.49),
     (1.92, 1.90, 1.27), (.027, .035, .029))
cube("right tall cabinet", (.91, .80, 2.55),
     (2.80, 1.90, 1.30), (.035, .045, .038))
cube("right door seam", (.009, .013, 2.49),
     (2.79, 1.492, 1.29), (.015, .022, .017))
for k, z in enumerate([1.14, 1.72]):
    cube("oven surround "+str(k), (.69, .035, .51),
         (1.92, 1.486, z), (.27, .29, .27))
    cube("oven glass "+str(k), (.62, .018, .35),
         (1.92, 1.459, z-.035), (.018, .033, .036))
    cube("oven controls "+str(k), (.64, .025, .095),
         (1.92, 1.45, z+.195), (.23, .25, .235))
    cube("oven handle "+str(k), (.57, .065, .025),
         (1.92, 1.413, z+.087), (.46, .49, .46))
    scene.include("oven knob "+str(k), rod(
        radius=.018, start=(2.15, 1.425, z+.197),
        end=(2.15, 1.404, z+.197), color=(.46, .49, .46)))

# Broad light-gray island.
ix, iy = .10, -.28
length, depth = 2.60, 1.18
cube("island inset plinth", (length-.12, depth-.13, .13),
     (ix+.025, iy+.02, .095), (.16, .18, .16))
cube("island carcass", (length, depth, .86),
     (ix, iy, .57), front)
cube("island countertop", (length+.035, depth+.035, .045),
     (ix, iy, 1.022), (.76, .78, .735))
cube("plain island end", (.055, depth+.012, .94),
     (ix-length/2-.015, iy, .535), (.54, .56, .53))
fy = iy-depth/2-.018
for i, (z, h) in enumerate([(.833, .274), (.540, .272), (.247, .272)]):
    cube("drawer "+str(i), (length-.052, .033, h),
         (ix+.015, fy, z), (.60, .62, .585))
    cube("drawer recessed rail "+str(i), (length-.06, .020, .014),
         (ix+.015, fy-.004, z+h/2+.008), (.23, .26, .235))

# Flush pale sink and slender chrome tap.
sx, sy = .58, -.04
cube("sink outer rim", (.65, .45, .007),
     (sx, sy, 1.048), (.53, .57, .53))
cube("sink inner edge", (.60, .40, .008),
     (sx, sy, 1.053), (.39, .43, .40))
cube("sink interior", (.565, .365, .009),
     (sx, sy, 1.058), (.66, .69, .65))
scene.include("chrome faucet", sweep_tube(
    points=[(sx+.26, sy+.30, 1.05), (sx+.26, sy+.30, 1.25),
            (sx+.24, sy+.28, 1.29), (sx+.08, sy+.24, 1.29),
            (sx+.055, sy+.21, 1.265), (sx+.055, sy+.21, 1.20)],
    radius=.011, color=(.61, .65, .63)))
scene.include("tap lever", rod(
    radius=.007, start=(sx+.29, sy+.30, 1.10),
    end=(sx+.35, sy+.30, 1.16), color=(.54, .58, .55)))
for x in [-.73, -.33]:
    cube("flush hob rim "+str(x), (.32, .36, .002),
         (x, -.38, 1.047), (.66, .69, .64))
    cube("flush hob surface "+str(x), (.309, .349, .003),
         (x, -.38, 1.049), (.75, .77, .73))

# Large suspended rectangular plaster hood.
hood_center = (-.18, -.11, 2.885)
cube("plaster extraction hood", (.91, .95, 1.93),
     hood_center, (.79, .79, .735))
cube("hood lower lip", (.91, .95, .018),
     (-.18, -.11, 1.919), (.59, .61, .56))
cube("hood underside", (.75, .77, .010),
     (-.18, -.11, 1.906), (.43, .46, .42))

# Red kettle in the illuminated rear recess.
kx, ky = -.89, 1.72
scene.include("red kettle", ball(
    radius=.093, center=(kx, ky, 1.075), color=(.72, .008, .019)))
cube("kettle base", (.16, .14, .025),
     (kx, ky, 1.002), (.018, .023, .019))
scene.include("kettle handle", sweep_tube(
    points=[(kx-.055, ky, 1.09), (kx-.067, ky, 1.19),
            (kx+.008, ky, 1.225), (kx+.079, ky, 1.19),
            (kx+.074, ky, 1.09)],
    radius=.016, color=(.015, .020, .016)))
scene.include("kettle spout", rod(
    radius=.026, start=(kx-.062, ky-.015, 1.09),
    end=(kx-.117, ky-.026, 1.145), color=(.34, .37, .34)))

realize(scene)

def finish(name, color, scale, stretch, roughness, variation, bump_amount):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    bs.inputs["Roughness"].default_value = roughness
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 3
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeVectorMath")
    mapping.operation = "MULTIPLY"
    mapping.inputs[1].default_value = stretch
    links.new(coord.outputs["Generated"], mapping.inputs[0])
    links.new(mapping.outputs[0], tex.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (
        *(c*(1-variation) for c in color), 1)
    ramp.color_ramp.elements[1].color = (
        *(min(1, c*(1+variation)) for c in color), 1)
    links.new(tex.outputs["Fac"], ramp.inputs[0])
    links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_amount
    bump.inputs["Distance"].default_value = .008
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return mat

wood = finish("Oak vertical grain", (.43, .29, .17),
              5, (9, 9, .12), .62, .43, .22)
plaster = finish("Cream mineral plaster", (.79, .79, .735),
                 95, (1, 1, 1), .85, .065, .10)

for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    points = [ob.matrix_world @ Vector(p) for p in ob.bound_box]
    low = Vector(tuple(min(p[k] for p in points) for k in range(3)))
    high = Vector(tuple(max(p[k] for p in points) for k in range(3)))
    center = (low+high)/2
    dims = high-low
    mat = None
    if dims.z > 3.5 and dims.x < .4 and dims.y < .4:
        mat = wood
    elif (center-Vector(hood_center)).length < .05 and dims.z > 1.8:
        mat = plaster
    if mat:
        ob.data.materials.clear()
        ob.data.materials.append(mat)

# Level camera keeps the architectural verticals parallel.
set_view(position=(-6.9, -3.8, 1.56),
         target=(0, .3, 1.56), lens=46)
cam = bpy.context.scene.camera
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 32
cam.data.shift_x = 0
cam.data.shift_y = 0
cam.data.clip_end = 150

area_emitter(position=(-4.0, -3.6, 3.8), power=1050, size=4,
             target=(0, 0, 1), color=(1, .95, .87))
area_emitter(position=(1, -1.8, 3.75), power=600, size=3,
             target=(.3, .2, 1.1), color=(.93, .96, 1))
area_emitter(position=(-.9, 1.65, 1.90), power=42, size=1.6,
             target=(-.9, 2.08, 1.3), color=(1, .69, .48))
area_emitter(position=(3.5, 1.5, 3.1), power=220, size=2,
             target=(1, 0, 1), color=(1, .96, .88))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Kitchen World")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (.20, .22, .21, 1)
background.inputs["Strength"].default_value = .25

sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = .15
