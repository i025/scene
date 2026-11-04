from sceneact import *
import bpy
import random

random.seed(8)
scene = Scene("Industrial kitchen")

def cube(name, size, center, color):
    node = box(size=size, center=center, color=color)
    scene.include(name, node)
    return node

cabinet = (.055, .062, .059)
island_color = (.57, .59, .565)

cube("floor foundation", (16, 15, .12), (0, 0, -.09), (.43, .43, .40))
for i in range(-7, 8):
    for j in range(-6, 8):
        shade = .69 + random.uniform(-.025, .025)
        cube("porcelain_%s_%s" % (i, j),
             (1.195, 1.195, .035), (i*1.2, j*1.2, -.012),
             (shade, shade*.995, shade*.958))

cube("back wall", (10, .18, 4.4), (0, 2.43, 2.2), (.39, .405, .385))
cube("left return wall", (.16, 8, 4.4), (-3.25, 1, 2.2), (.45, .46, .43))
cube("ceiling darkness", (13, 13, .16), (0, 0, 4.23), (.027, .033, .032))
for x in [-4, -2.8, -1.6, -.4, .8, 2, 3.2, 4.4]:
    cube("ceiling joist"+str(x), (.075, 10, .16), (x, .2, 4.09), (.045, .052, .05))
for y in [-2.4, -.8, .85, 2.5]:
    cube("transverse ceiling beam"+str(y), (11, .20, .27), (0, y, 3.98), (.07, .08, .077))
cube("prominent overhead girder", (.30, 11, .38), (1.9, .3, 3.91), (.095, .11, .105))

cube("foreground oak post", (.34, .37, 4.35), (-2, -1.03, 2.175), (.40, .265, .145))
cube("distant oak post", (.19, .23, 3.8), (3.02, 1.80, 1.9), (.48, .34, .21))

cube("rear toe kick", (5.25, .58, .12), (-.08, 1.87, .08), (.018, .021, .020))
cube("rear lower cupboards", (5.2, .65, .83), (-.08, 1.87, .515), cabinet)
cube("rear dark worktop", (5.30, .74, .055), (-.08, 1.82, .96), (.075, .08, .075))
for x in [-2.15, -1.5, -.85, -.2, .45, 1.10, 1.75]:
    cube("rear door joint"+str(x), (.011, .012, .77), (x, 1.539, .515), (.019, .022, .02))

cube("dark stone backsplash", (5.28, .07, 1.05), (-.07, 2.085, 1.49), (.065, .073, .069))
for x in [-2.6, -1.78, -.96, -.14, .68, 1.5, 2.32]:
    cube("backsplash vertical seam"+str(x), (.009, .009, .93), (x, 2.043, 1.47), (.035, .041, .038))
cube("backsplash horizontal seam", (5.22, .01, .009), (-.07, 2.041, 1.57), (.035, .04, .037))
cube("upper dark cabinets", (4.42, .44, .53), (-.34, 2.03, 2.225), (.045, .052, .048))
cube("under cabinet luminous strip", (3.35, .025, .013), (-.64, 1.805, 1.955), (.80, .64, .46))

cube("left tall cabinet carcass", (.93, .83, 2.53), (-2.74, 1.71, 1.285), (.035, .041, .038))
cube("left tall cabinet door", (.90, .035, 2.48), (-2.74, 1.275, 1.29), (.085, .092, .085))
cube("left cabinet top division", (.89, .012, .009), (-2.74, 1.25, 2.16), (.038, .043, .039))
cube("left cabinet vertical split", (.009, .012, 2.43), (-2.65, 1.249, 1.285), (.035, .04, .036))

cube("oven tower", (.83, .79, 2.49), (1.92, 1.90, 1.27), (.035, .041, .038))
cube("right tall cabinet", (.91, .80, 2.55), (2.80, 1.90, 1.30), (.048, .055, .051))
cube("right cabinet door line", (.012, .01, 2.49), (2.79, 1.492, 1.29), (.021, .026, .023))
for k, z in enumerate([1.14, 1.72]):
    cube("oven metal surround"+str(k), (.69, .035, .51), (1.92, 1.486, z), (.28, .30, .28))
    cube("oven black glass"+str(k), (.62, .018, .35), (1.92, 1.459, z-.035), (.025, .042, .046))
    cube("oven control band"+str(k), (.64, .025, .095), (1.92, 1.45, z+.195), (.23, .25, .235))
    cube("oven horizontal handle"+str(k), (.57, .065, .025), (1.92, 1.413, z+.087), (.47, .49, .46))
    scene.include("oven knob"+str(k), rod(radius=.018,
        start=(2.15, 1.425, z+.197), end=(2.15, 1.404, z+.197),
        color=(.48, .49, .46)))

ix, iy = .10, -.23
length, depth = 2.32, 1.12
cube("island recessed plinth", (2.20, 1, .13), (ix+.025, iy+.02, .095), (.19, .205, .19))
cube("island cabinet body", (length, depth, .86), (ix, iy, .57), island_color)
cube("island slab worktop", (length+.035, depth+.035, .045), (ix, iy, 1.022), (.76, .78, .735))
cube("island left end panel", (.055, depth+.012, .94),
     (ix-length/2-.015, iy, .535), (.56, .58, .55))
front_y = iy-depth/2-.018
for i, (zc, height) in enumerate([(.833, .274), (.540, .272), (.247, .272)]):
    cube("wide island drawer "+str(i), (length-.052, .033, height),
         (ix+.015, front_y, zc), (.60, .62, .59))
    cube("drawer recessed grip "+str(i), (length-.06, .020, .017),
         (ix+.015, front_y-.004, zc+height/2+.008), (.23, .26, .24))

sx, sy = .48, -.02
cube("sink brushed rim", (.65, .45, .009), (sx, sy, 1.049), (.56, .59, .56))
cube("sink inner dark edge", (.59, .39, .011), (sx, sy, 1.054), (.37, .41, .38))
cube("sink pale basin interior", (.55, .35, .013), (sx, sy, 1.060), (.64, .67, .63))
scene.include("faucet", sweep_tube(
    points=[(sx+.26, sy+.30, 1.05), (sx+.26, sy+.30, 1.27),
            (sx+.24, sy+.28, 1.31), (sx+.08, sy+.24, 1.31),
            (sx+.055, sy+.21, 1.285), (sx+.055, sy+.21, 1.22)],
    radius=.012, color=(.61, .65, .63)))
scene.include("tap lever", rod(radius=.008, start=(sx+.29, sy+.30, 1.10),
    end=(sx+.35, sy+.30, 1.16), color=(.54, .58, .55)))
for xx in [-.64, -.27]:
    cube("hob outline "+str(xx), (.29, .35, .003), (xx, -.34, 1.048), (.67, .69, .65))
    cube("hob interior "+str(xx), (.278, .338, .004), (xx, -.34, 1.050), (.75, .77, .73))

hx, hy = -.30, -.04
cube("massive rectangular extractor", (.91, .95, 1.92), (hx, hy, 3.02), (.78, .785, .735))
cube("hood bottom metal lip", (.90, .94, .022), (hx, hy, 2.055), (.55, .57, .53))
cube("extractor underside", (.75, .77, .012), (hx, hy, 2.041), (.48, .50, .46))
cube("hood lower front edge", (.91, .012, .014), (hx, hy-.48, 2.07), (.64, .65, .60))

kx, ky = -.89, 1.72
scene.include("kettle red body", ball(radius=.093, center=(kx, ky, 1.075), color=(.68, .012, .025)))
cube("kettle dark base", (.16, .14, .025), (kx, ky, 1.002), (.026, .028, .025))
scene.include("kettle black handle", sweep_tube(
    points=[(kx-.055, ky, 1.09), (kx-.067, ky, 1.19), (kx+.008, ky, 1.225),
            (kx+.079, ky, 1.19), (kx+.074, ky, 1.09)],
    radius=.016, color=(.018, .023, .021)))
scene.include("kettle spout", rod(radius=.026, start=(kx-.062, ky-.015, 1.09),
    end=(kx-.117, ky-.026, 1.145), color=(.36, .38, .35)))

realize(scene)

def textured_material(name, color, roughness, scale, bump_strength, stretch=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 3
    coord = nodes.new("ShaderNodeTexCoord")
    if stretch:
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = stretch
        links.new(coord.outputs["Generated"], mapping.inputs[0])
        links.new(mapping.outputs[0], tex.inputs["Vector"])
    else:
        links.new(coord.outputs["Generated"], tex.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .18
    ramp.color_ramp.elements[0].color = (*(c*.65 for c in color), 1)
    ramp.color_ramp.elements[1].position = .82
    ramp.color_ramp.elements[1].color = (*(min(c*1.23, 1) for c in color), 1)
    links.new(tex.outputs["Fac"], ramp.inputs[0])
    links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = .012
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return mat

wood = textured_material("Natural oak long grain", (.43, .29, .17), .58, 4, .23, (8, 8, .13))
plaster = textured_material("Fine cream extractor plaster", (.79, .79, .735), .85, 85, .12)
stone = textured_material("Dark stone subtle variation", (.063, .073, .066), .57, 5, .07)

for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    nm = ob.name.lower()
    if "oak post" in nm:
        ob.data.materials.clear()
        ob.data.materials.append(wood)
    elif "massive rectangular extractor" in nm:
        ob.data.materials.clear()
        ob.data.materials.append(plaster)
    elif "dark stone backsplash" in nm:
        ob.data.materials.clear()
        ob.data.materials.append(stone)
    for mat in ob.data.materials:
        if mat and mat.use_nodes:
            bs = mat.node_tree.nodes.get("Principled BSDF")
            if bs and ("oven" in nm or "faucet" in nm or "tap " in nm):
                bs.inputs["Metallic"].default_value = .65
                bs.inputs["Roughness"].default_value = .24
            elif bs and "worktop" in nm:
                bs.inputs["Roughness"].default_value = .25

set_view(position=(-6.4, -4.5, 2.4), target=(0, .3, 2.4), lens=43)
cam = bpy.context.scene.camera
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 32
cam.data.shift_y = -.15
cam.data.clip_end = 150

area_emitter(position=(-3.7, -3.4, 4), power=1100, size=4,
             target=(0, 0, 1), color=(1, .95, .86))
area_emitter(position=(1, -1.8, 3.8), power=650, size=3,
             target=(.3, .2, 1.1), color=(.91, .95, 1))
area_emitter(position=(-.9, 1.68, 1.91), power=48, size=1.7,
             target=(-.9, 2.08, 1.35), color=(1, .70, .49))
area_emitter(position=(3.5, 1.5, 3.1), power=250, size=2,
             target=(1, 0, 1), color=(1, .96, .88))

sc = bpy.context.scene
world = sc.world
if world is None:
    world = bpy.data.worlds.new("Kitchen World")
    sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.20, .22, .21, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .30

sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = .25
