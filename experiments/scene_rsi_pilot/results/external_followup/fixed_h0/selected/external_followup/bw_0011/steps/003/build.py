from sceneact import *
import bpy
import math
import random

random.seed(19)
scene = Scene('Modular clean laboratory')

def block(name, size, center, color):
    scene.include(name, box(size=size, center=center, color=color))

blue = (.075, .46, .64)
steel = (.58, .64, .61)
trim = (.84, .89, .86)

# Blue modular walls, with narrow recessed vertical joints.
block('Rear joint backing', (6.45, .07, 3.48), (-1.20, 3.65, 1.74), (.055, .29, .38))
for i in range(8):
    block('Rear blue panel %02d' % i, (.790, .07, 3.46),
          (-4.4 + (i+.5)*.8, 3.59, 1.73), blue)
block('Side joint backing', (.07, 4.76, 3.48), (2.06, 1.25, 1.74), (.055, .29, .38))
for i in range(6):
    block('Side blue panel %02d' % i, (.07, .781, 3.46),
          (2.005, -1.12+(i+.5)*.79, 1.73), blue)
block('Exposed white end post', (.07, .075, 3.5), (2.00, -1.15, 1.75), trim)
block('Self levelling gray floor', (6.5, 7.6, .10), (-1.21, -.20, -.055), (.48, .53, .51))

# Coving is formed with simple quarter-round strips after realization.
block('Rear cove backing', (6.43, .045, .09), (-1.22, 3.515, .045), trim)
block('Side cove backing', (.045, 4.68, .09), (1.94, 1.19, .045), trim)

# Stainless steel cabinet. Separate shelves remain visible behind the glazing.
cab = Asset('Double glazed stainless cabinet')
def cabinet_piece(name, size, center, color=steel):
    cab.include(name, box(size=size, center=center, color=color))

cabinet_piece('Cabinet back', (1.50, .035, 2.55), (-2.8, 3.48, 1.275), (.33, .39, .35))
for x in (-3.525, -2.075):
    cabinet_piece('Cabinet side %.3f' % x, (.05, .46, 2.55), (x, 3.27, 1.275))
for z in (.035, 2.515):
    cabinet_piece('Cabinet cap %.3f' % z, (1.50, .46, .07), (-2.8, 3.27, z))
for z in (.25, .65, 1.05, 1.45, 1.85, 2.25):
    cabinet_piece('Internal shelf %.2f' % z, (1.40, .39, .022), (-2.8, 3.245, z), (.67, .73, .68))
for cx in (-3.17, -2.43):
    for dx in (-.34, .34):
        cabinet_piece('Door upright %.2f %.2f' % (cx, dx),
                      (.065, .055, 2.43), (cx+dx, 3.00, 1.28))
    for z in (.09, 2.47):
        cabinet_piece('Door rail %.2f %.2f' % (cx, z),
                      (.72, .055, .12), (cx, 3.00, z), (.73, .78, .74))
    cabinet_piece('Glass pane %.2f' % cx, (.595, .012, 2.25),
                  (cx, 3.012, 1.28), (.65, .76, .70))
for x in (-2.90, -2.70):
    cabinet_piece('Door handle %.2f' % x, (.024, .042, .25),
                  (x, 2.94, 1.28), (.76, .80, .76))
scene.include('Cabinet', cab)

# Botanical wall mural substrate.
block('Botanical mural', (2.80, .022, 3.43), (.05, 3.531, 1.725), (.78, .89, .81))

# Exposed concrete and suspended T ceiling.
block('Concrete slab', (7.4, 9.0, .15), (-1.3, -.4, 3.99), (.26, .29, .27))
for y in (-3.0, -.7, 1.6, 3.6):
    block('Concrete beam %.1f' % y, (7.2, .12, .18), (-1.3, y, 3.85), (.31, .34, .31))
for x in (-4.4, -3.3, -2.2, -1.1, 0, 1.1, 2.05):
    block('Ceiling longitudinal T %.1f' % x, (.027, 8.0, .042),
          (x, -.43, 3.47), (.51, .64, .64))
for y in (-4.3, -3.25, -2.2, -1.15, -.10, .95, 2.0, 2.85, 3.56):
    block('Ceiling cross T %.2f' % y, (6.5, .026, .035),
          (-1.2, y, 3.46), (.62, .71, .68))
for i, x in enumerate((-3.85, -2.75, -1.65, -.55, .55, 1.58)):
    block('Rear perimeter ceiling tile %d' % i, (1.065, .68, .035),
          (x, 3.20, 3.475), (.82, .86, .83))
for y in (-.65, .42, 1.48, 2.45):
    block('Side perimeter ceiling tile %.2f' % y, (.88, 1.015, .035),
          (1.58, y, 3.475), (.82, .86, .83))

leds = [(-.55, 2.39), (.55, 1.47), (-3.85, 2.39)]
for i, (x, y) in enumerate(leds):
    block('LED metal frame %d' % i, (1.075, .88, .04),
          (x, y, 3.44), (.73, .80, .76))
    block('LED diffuser %d' % i, (1.025, .83, .014),
          (x, y, 3.412), (.93, 1.0, .98))

# Wall-mounted information screen.
block('Clock bezel', (.060, 1.40, .77), (1.922, .70, 2.37), (.29, .37, .41))
block('Clock screen', (.012, 1.30, .67), (1.884, .70, 2.37), (.018, .055, .13))

realize(scene)

def material(name, color, roughness=.5, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m

# Assign distinct, economical materials.
metal_mat = material('Brushed stainless steel', (.59, .65, .60), .31, .75)
glass_mat = material('Clear lightly tinted cabinet glass', (.70, .80, .74), .14)
p = glass_mat.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = .86
p.inputs['IOR'].default_value = 1.45
blue_mat = material('Blue powder coated steel', blue, .40, .18)
led_mat = material('LED luminous opal', (.85, .97, .96), .3)
p = led_mat.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (.82, .97, 1, 1)
p.inputs['Emission Strength'].default_value = 3.5

for ob in list(bpy.context.scene.objects):
    if ob.type != 'MESH':
        continue
    name = ob.name.lower()
    replacement = None
    if 'blue panel' in name:
        replacement = blue_mat
    elif any(k in name for k in ('cabinet side', 'cabinet cap', 'door upright',
                                 'door rail', 'door handle', 'internal shelf')):
        replacement = metal_mat
    elif 'glass pane' in name:
        replacement = glass_mat
    elif 'led diffuser' in name:
        replacement = led_mat
    if replacement:
        ob.data.materials.clear()
        ob.data.materials.append(replacement)

# A procedural mint and cream ground, with subtle organic clouding.
mural_mat = material('Botanical mural ground', (.8, .9, .82), .85)
n = mural_mat.node_tree.nodes
l = mural_mat.node_tree.links
p = n.get('Principled BSDF')
tc = n.new('ShaderNodeTexCoord')
sep = n.new('ShaderNodeSeparateXYZ')
l.new(tc.outputs['Generated'], sep.inputs[0])
ramp = n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0
ramp.color_ramp.elements[0].color = (.53, .34, .19, 1)
ramp.color_ramp.elements[1].position = 1
ramp.color_ramp.elements[1].color = (.80, .92, .86, 1)
for pos, col in [
    (.17, (.83, .76, .46, 1)),
    (.40, (.79, .88, .74, 1)),
    (.72, (.72, .88, .83, 1))
]:
    e = ramp.color_ramp.elements.new(pos)
    e.color = col
l.new(sep.outputs['Z'], ramp.inputs[0])
noise = n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 8
noise.inputs['Detail'].default_value = 2
l.new(tc.outputs['Generated'], noise.inputs['Vector'])
mix = n.new('ShaderNodeMixRGB')
mix.blend_type = 'MULTIPLY'
mix.inputs[0].default_value = .13
l.new(ramp.outputs[0], mix.inputs[1])
l.new(noise.outputs['Fac'], mix.inputs[2])
l.new(mix.outputs[0], p.inputs['Base Color'])
for ob in bpy.context.scene.objects:
    if 'Botanical mural' in ob.name:
        ob.data.materials.clear()
        ob.data.materials.append(mural_mat)

# Lightweight planar botanical artwork: tapered stalks and fine curved seed hairs.
# All strands share three small meshes, avoiding expensive solid tube operations.
stem_mat = material('Photographic dark plum stems', (.19, .065, .16), .95)
hair_mat = material('Soft olive seed filaments', (.42, .48, .37), 1)
fine_mat = material('Pale fine seed filaments', (.59, .65, .51), 1)

def ribbon_mesh(name, paths, mat, y):
    vertices, faces = [], []
    for points, width in paths:
        start = len(vertices)
        for j, (x, z) in enumerate(points):
            before = points[max(0, j-1)]
            after = points[min(len(points)-1, j+1)]
            dx, dz = after[0]-before[0], after[1]-before[1]
            length = max(.00001, math.hypot(dx, dz))
            w = width * (1-.60*j/max(1, len(points)-1))
            nx, nz = -dz/length*w/2, dx/length*w/2
            vertices.extend([(x+nx, y, z+nz), (x-nx, y, z-nz)])
            if j:
                k = start+2*j
                faces.append((k-2, k-1, k+1, k))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)

stalks = [
    [(1.40,.03),(.77,.42),(-.22,.90),(-1.34,1.47)],
    [(1.28,.03),(.51,.57),(-.33,1.52),(-1.02,2.17)],
    [(1.20,.03),(.81,.57),(.28,1.28),(.18,2.03)],
    [(.99,.03),(.59,.58),(.40,1.48),(.25,2.48)],
    [(.83,.03),(.36,.54),(-.19,1.42),(-.55,2.98)],
    [(-1.34,.25),(-.76,.43),(.04,.65),(.83,1.13)],
    [(-1.34,.64),(-.75,.71),(.10,.62),(.82,.30)],
    [(-1.34,1.50),(-.76,1.29),(-.21,1.13),(.46,1.09)],
    [(1.44,.17),(1.02,.46),(.67,.68),(.53,1.30)],
    [(1.43,.08),(1.23,.48),(.99,.73),(1.03,1.02)],
    [(-.10,.03),(.34,.38),(.85,.61),(1.44,.73)],
    [(-1.34,1.79),(-.78,1.52),(-.31,1.34),(.17,1.38)]
]
ribbon_mesh('Botanical branching stalks', [(s, .023 if i<5 else .014)
             for i, s in enumerate(stalks)], stem_mat, 3.507)
hairs, fine = [], []
for i, stalk in enumerate(stalks):
    tx, tz = stalk[-1]
    for j in range(60):
        angle = random.uniform(.04, math.pi-.04)
        length = random.uniform(.30, 1.13)
        dx, dz = math.cos(angle)*length, math.sin(angle)*length
        curve = []
        for k in range(7):
            t = k/6
            x = max(-1.345, min(1.445, tx+dx*t))
            z = max(.025, min(3.43, tz+dz*t+.12*math.sin(t*math.pi)))
            curve.append((x,z))
        (hairs if j % 3 == 0 else fine).append((curve, random.uniform(.0011,.0028)))
ribbon_mesh('Dandelion seed hairs', hairs, hair_mat, 3.503)
ribbon_mesh('Dandelion fine seed hairs', fine, fine_mat, 3.501)

# Small cylindrical ceiling services, created directly as inexpensive curves.
service_mat = material('Galvanized ceiling services', (.43, .54, .52), .43, .55)
def line_curve(name, points, radius, mat):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 1
    data.bevel_depth = radius
    data.bevel_resolution = 0
    spline = data.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    ob = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)

for x in (-4.4, -2.2, 0, 2.0):
    for y in (-1.0, 1.2, 3.3):
        line_curve('Suspension rod', [(x,y,3.49),(x,y,3.93)], .006, service_mat)
for x in (-3.9, -1.0):
    line_curve('Overhead conduit', [(x,-4.3,3.79),(x,3.55,3.79)], .017, service_mat)

# Quarter-round hygienic cove strips.
cove_mat = material('White hygienic cove', trim, .35)
def cove(name, along_x):
    vs, fs = [], []
    for end in (0,1):
        for i in range(9):
            a = i*math.pi/16
            offset = .09*(1-math.sin(a))
            z = .09*(1-math.cos(a))
            if along_x:
                vs.append((-4.43+6.40*end, 3.55-offset, z))
            else:
                vs.append((1.97-offset, -1.15+4.70*end, z))
    for i in range(8):
        fs.append((i,i+1,i+10,i+9))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vs,[],fs)
    mesh.update()
    ob = bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(cove_mat)
    for poly in mesh.polygons:
        poly.use_smooth=True
cove('Rounded rear cove', True)
cove('Rounded side cove', False)

text_mat = material('LCD blue lettering', (.34,.59,.76), .5)
p = text_mat.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (.23,.43,.65,1)
p.inputs['Emission Strength'].default_value = .5
def screen_text(name, body, y, z, size):
    data = bpy.data.curves.new(name, 'FONT')
    data.body = body
    data.align_x = 'CENTER'
    data.size = size
    ob = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(ob)
    ob.location = (1.873,y,z)
    ob.rotation_euler = (math.pi/2,0,-math.pi/2)
    ob.data.materials.append(text_mat)
screen_text('Time', '09:29:07', .70, 2.35, .22)
screen_text('Heading', 'CLEAN ROOM', .70, 2.61, .065)
screen_text('Date', '2026 / 10 / 20', .70, 2.18, .071)
screen_text('Conditions', '22.0 C      RH 45%', .70, 2.08, .052)

# Fine mottling on exposed concrete.
for ob in bpy.context.scene.objects:
    if 'Concrete slab' in ob.name:
        mat = ob.data.materials[0]
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 35
        noise.inputs['Detail'].default_value = 2
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .20
        bump.inputs['Distance'].default_value = .035
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], nodes.get('Principled BSDF').inputs['Normal'])

set_view(position=(-2.10,-8.0,1.85),
         target=(-.10,3.60,1.90), lens=39, sensor=36)

for x,y in leds:
    area_emitter((x,y,3.37), power=190, size=1.05,
                 target=(x,y,0), color=(.88,.96,1.0))
area_emitter((-2.5,-2.0,3.15), power=420, size=5,
             target=(-1,3,1.5), color=(.95,1,1))
area_emitter((-4.6,1.2,2.2), power=150, size=3,
             target=(-.2,3,1.4), color=(.95,1,1))

world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (1,1,1,1)
world.node_tree.nodes['Background'].inputs[1].default_value = .75

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6
sc.cycles.transmission_bounces = 4
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
