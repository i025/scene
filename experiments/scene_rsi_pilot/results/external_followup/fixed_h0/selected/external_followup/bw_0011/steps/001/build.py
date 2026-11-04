from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(19)
scene = Scene('Clean laboratory')
blue = (.075, .48, .66)
seam = (.055, .30, .40)
white = (.85, .89, .87)
steel = (.54, .60, .59)

def add(name, size, center, color):
    node = box(size=size, center=center, color=color)
    scene.include(name, node)
    return node

# Modular room envelope.
add('seam backing', (6.45, .10, 3.48), (-1.2, 3.66, 1.74), seam)
for i in range(8):
    x = -4.4 + (i + .5) * .8
    add('rear blue panel %02d' % i, (.789, .09, 3.46),
        (x, 3.59, 1.73), blue)
add('right wall backing', (.10, 4.76, 3.48), (2.055, 1.25, 1.74), seam)
for i in range(6):
    y = -1.12 + (i + .5) * .79
    add('right blue panel %02d' % i, (.09, .78, 3.46),
        (2.005, y, 1.73), blue)
add('right exposed white jamb', (.075, .075, 3.5), (2.015, -1.155, 1.75), white)
add('floor', (6.6, 6.6, .12), (-1.23, .35, -.075), (.48, .53, .52))

# Rounded hygienic floor coves.
scene.include('back cove', sweep_tube(
    points=[(-4.43, 3.51, .075), (1.97, 3.51, .075)],
    radius=.075, color=(.86, .90, .88)))
scene.include('side cove', sweep_tube(
    points=[(1.93, -1.15, .075), (1.93, 3.52, .075)],
    radius=.075, color=(.86, .90, .88)))

# Stainless steel cabinet, inset glass doors and visible shelving.
cabinet = Asset('Stainless double door cabinet')
cabinet.include('body', box((1.50, .44, 2.55),
                           center=(-2.80, 3.29, 1.275), color=(.56, .61, .59)))
cabinet.include('dark interior', box((1.34, .025, 2.35),
                                   center=(-2.80, 3.045, 1.27), color=(.19, .25, .23)))
for z in (.25, .64, 1.03, 1.42, 1.81, 2.20):
    cabinet.include('shelf %.2f' % z, box((1.30, .34, .025),
                    center=(-2.80, 3.19, z), color=(.68, .73, .69)))
for cx in (-3.17, -2.43):
    for dx in (-.345, .345):
        cabinet.include('door upright %.2f %.2f' % (cx, dx),
            box((.065, .065, 2.44), center=(cx + dx, 3.00, 1.28), color=steel))
    for z in (.08, 2.49):
        cabinet.include('door horizontal %.2f %.2f' % (cx, z),
            box((.71, .065, .075), center=(cx, 3.00, z), color=(.72, .76, .73)))
    cabinet.include('glass %.2f' % cx, fillet_box(
        (.565, .018, 2.23), radius=.085, center=(cx, 3.006, 1.28),
        color=(.39, .49, .46), opacity=.28))
for x in (-2.90, -2.70):
    cabinet.include('handle %.2f' % x, rod(
        radius=.018, start=(x, 2.943, 1.13), end=(x, 2.943, 1.39),
        color=(.79, .82, .78)))
scene.include('cabinet', cabinet)

# Full-height botanical feature panel, built from colored geometry and fibers.
mural = add('botanical backdrop', (2.80, .028, 3.43),
            (.05, 3.525, 1.725), (.78, .88, .79))

plum = (.20, .075, .19)
pale_fiber = (.43, .48, .39)
stem_paths = [
    [(1.30,.04),(.70,.40),(-.25,.86),(-1.34,1.30)],
    [(1.22,.05),(.48,.58),(-.35,1.48),(-1.02,2.15)],
    [(1.25,.04),(.82,.58),(.27,1.27),(.14,2.03)],
    [(.97,.04),(.57,.55),(.40,1.44),(.25,2.45)],
    [(.84,.04),(.37,.52),(-.19,1.35),(-.53,2.91)],
    [(-1.32,.25),(-.75,.43),(.04,.65),(.82,1.13)],
    [(-1.32,.65),(-.75,.71),(.10,.61),(.80,.29)],
    [(-1.32,1.50),(-.76,1.29),(-.21,1.13),(.46,1.09)],
    [(1.42,.18),(1.01,.46),(.66,.66),(.52,1.29)],
    [(1.40,.09),(1.22,.49),(.99,.72),(1.02,1.01)],
    [(-.10,.07),(.34,.38),(.85,.61),(1.38,.72)],
    [(-1.33,1.78),(-.78,1.51),(-.31,1.33),(.17,1.37)]
]
for i, path in enumerate(stem_paths):
    pts = [(x, 3.494 - i*.0003, z) for x,z in path]
    scene.include('botanical stem %02d' % i,
                  sweep_tube(points=pts, radius=.010 if i<5 else .007, color=plum))
    tx,tz = path[-1]
    # Fine, translucent-looking radiating seed filaments.
    for j in range(33):
        angle = random.uniform(.12, math.pi-.12)
        length = random.uniform(.24,.83)
        ex = tx + math.cos(angle)*length
        ez = tz + math.sin(angle)*length
        ex = max(-1.34,min(1.44,ex))
        ez = max(.03,min(3.43,ez))
        points = [
            (tx,3.481,tz),
            (tx+(ex-tx)*.43,3.479,tz+(ez-tz)*.58),
            (ex,3.480,ez)]
        scene.include('seed filament %02d %02d' % (i,j),
                      sweep_tube(points=points, radius=random.uniform(.001,.0024),
                                 color=pale_fiber))
    scene.include('seed node %02d' % i,
                  rod(radius=.014, start=(tx-.025,3.477,tz-.065),
                      end=(tx+.015,3.477,tz+.045), color=plum))

# Ceiling structure above an open suspended T grid.
add('concrete soffit', (7.1, 6.2, .16), (-1.35, .7, 4.04), (.25,.28,.27))
for y in (-1.7,.5,2.8):
    add('structural beam %.1f' % y, (7.0,.14,.23),
        (-1.35,y,3.88), (.30,.33,.31))
for x in (-4.4,-3.3,-2.2,-1.1,0,1.1,2.05):
    add('long ceiling T %.1f' % x, (.025,5.0,.045),
        (x,1.05,3.47), (.45,.60,.61))
    add('grid bottom flange %.1f' % x, (.044,5.0,.012),
        (x,1.05,3.445), (.67,.73,.71))
    for y in (-.7,1.3,3.3):
        scene.include('hanger %.1f %.1f' % (x,y),
            rod(radius=.007, start=(x,y,3.49), end=(x,y,3.98),
                color=(.44,.47,.45)))
for y in (-1.4,-.35,.70,1.75,2.80,3.56):
    add('cross ceiling T %.2f' % y, (6.5,.028,.04),
        (-1.2,y,3.465), (.59,.67,.65))
# Opaque perimeter panels and a few luminous inset panels.
for i,x in enumerate((-3.85,-2.75,-1.65,-.55,.55,1.58)):
    add('rear ceiling tile %d' % i, (1.065,.71,.035),
        (x,3.18,3.47), (.80,.84,.81))
for y in (-.88,.18,1.23,2.28):
    add('right ceiling tile %.2f' % y, (.89,1.015,.035),
        (1.58,y,3.47), (.81,.84,.82))
led_positions=[(-.55,2.25),(.55,1.23),(-3.85,2.25)]
for i,(x,y) in enumerate(led_positions):
    add('LED frame %d' % i, (1.07,1.015,.045),
        (x,y,3.435), (.74,.79,.76))
    add('LED luminous diffuser %d' % i, (1.015,.955,.018),
        (x,y,3.406), (.94,1.0,.99))
for x,z in ((-3.9,3.79),(-1.0,3.84)):
    scene.include('overhead conduit %.1f' % x,
        rod(radius=.018, start=(x,-1.6,z), end=(x,3.55,z),
            color=(.40,.48,.47)))

# Right-wall digital clock.
add('display metal housing', (.062,1.52,.79), (1.922,.70,2.36), (.31,.39,.43))
add('display dark glass', (.014,1.42,.69), (1.883,.70,2.36), (.025,.075,.16))

realize(scene)

# Differentiated physically based finishes.
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat is None:
            continue
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if not bs:
            continue
        name=obj.name.lower()
        bs.inputs['Roughness'].default_value=.46
        if 'blue panel' in name:
            bs.inputs['Metallic'].default_value=.32
            bs.inputs['Roughness'].default_value=.32
        if any(s in name for s in ('cabinet','door','handle','shelf')):
            bs.inputs['Metallic'].default_value=.78
            bs.inputs['Roughness'].default_value=.29
        if 'glass ' in name:
            bs.inputs['Metallic'].default_value=.10
            bs.inputs['Roughness'].default_value=.15
            bs.inputs['Transmission Weight'].default_value=.42
            bs.inputs['Alpha'].default_value=.60
        if 'LED luminous' in obj.name:
            bs.inputs['Emission Color'].default_value=(.80,.96,1,1)
            bs.inputs['Emission Strength'].default_value=4.0

# A softly mottled, mint-to-cream background for the modeled botanical mural.
for obj in bpy.context.scene.objects:
    if 'botanical backdrop' not in obj.name:
        continue
    mat=bpy.data.materials.new('Botanical paper pale mint and warm cream')
    mat.use_nodes=True
    n=mat.node_tree.nodes
    l=mat.node_tree.links
    bs=n.get('Principled BSDF')
    tc=n.new('ShaderNodeTexCoord')
    sep=n.new('ShaderNodeSeparateXYZ')
    l.new(tc.outputs['Generated'],sep.inputs[0])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    colors=[
        (0.0,(.53,.36,.21,1)),
        (.16,(.78,.73,.48,1)),
        (.40,(.76,.88,.74,1)),
        (.70,(.73,.88,.83,1)),
        (1.0,(.81,.92,.88,1))]
    for k,(p,c) in enumerate(colors):
        e=ramp.color_ramp.elements[0] if k==0 else ramp.color_ramp.elements.new(p)
        e.position=p
        e.color=c
    l.new(sep.outputs['Z'],ramp.inputs[0])
    noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=9
    noise.inputs['Detail'].default_value=3
    l.new(tc.outputs['Generated'],noise.inputs['Vector'])
    mix=n.new('ShaderNodeMixRGB')
    mix.blend_type='MULTIPLY'
    mix.inputs[0].default_value=.15
    l.new(ramp.outputs[0],mix.inputs[1])
    l.new(noise.outputs['Fac'],mix.inputs[2])
    l.new(mix.outputs[0],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.83
    obj.data.materials.clear()
    obj.data.materials.append(mat)

# Readable clock graphics lie just in front of the screen.
screen_mat=bpy.data.materials.new('LCD pale blue text')
screen_mat.diffuse_color=(.38,.69,.86,1)
screen_mat.use_nodes=True
bs=screen_mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.30,.58,.76,1)
bs.inputs['Emission Color'].default_value=(.25,.48,.67,1)
bs.inputs['Emission Strength'].default_value=.55

def screen_text(name, text, y, z, size):
    curve=bpy.data.curves.new(name,'FONT')
    curve.body=text
    curve.align_x='CENTER'
    curve.size=size
    curve.extrude=0
    ob=bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(ob)
    ob.location=(1.870,y,z)
    # Text local X runs along -Y; its normal points into the room.
    ob.rotation_euler=(math.pi/2,0,-math.pi/2)
    ob.data.materials.append(screen_mat)
    return ob

screen_text('clock time','09:29:07',.70,2.35,.235)
screen_text('clock heading','CLEAN ROOM',.70,2.62,.070)
screen_text('clock date','2026 / 10 / 20',.70,2.18,.077)
screen_text('clock status','TEMP 22.0 C     RH 45%',.70,2.07,.053)

# Subtle concrete texture.
for obj in bpy.context.scene.objects:
    if 'concrete soffit' in obj.name:
        for mat in obj.data.materials:
            bs=mat.node_tree.nodes.get('Principled BSDF')
            noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=17
            noise.inputs['Detail'].default_value=3
            bump=mat.node_tree.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.25
            bump.inputs['Distance'].default_value=.055
            mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view(position=(-2.10,-8.0,1.85), target=(-.10,3.60,1.90), lens=39, sensor=36)
for x,y in led_positions:
    area_emitter((x,y,3.36), power=180, size=1.00,
                 target=(x,y,0), color=(.86,.95,1.0))
area_emitter((-2.5,-2,3.2), power=450, size=5,
             target=(-1,3,1.5), color=(.94,1,1))
area_emitter((-4.6,1.2,2.1), power=170, size=3,
             target=(-.2,3,1.5), color=(.93,1,1))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.75
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=64
bpy.context.scene.view_settings.view_transform='AgX'
bpy.context.scene.view_settings.look='AgX - Medium High Contrast'
