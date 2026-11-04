from sceneact import *
import bpy
import math

# Evidence / ownership ledger. Coordinates below are visual estimates.
# Reference: blinds x0..116 y0..409; cabinet x143..383 y0..272;
# paper roll x232..320 y44..216; ring/cloth x98..175 y167..424;
# jug x226..300 y332..453; pitcher x283..370 y307..431;
# blender x188..242 y289..423; sink cropped x0..162 y440..512.
# Step 2: roll approximately x263..356 y57..209; cabinet bottom y310;
# ring approximately x138..176 y221..305; jug x254..311 y307..425.
# Near sink is cropped, but its rim remains too bright. Cabinet side is visible.
# Camera alignment remains uncertain: cabinet/ring are low and roll is rightward.
# Measured facts: both prior executions returned valid images; reported elapsed
# execution times were 5.577 and 5.597 seconds. These do not isolate render time.
#
# Selected family: material appearance, with camera, geometry and lights fixed.
# Across cabinet, wall, towel and counter, step 2 is much paler than reference.
# Prediction: warmer cream architecture, less brilliant paper/cloth and a dark,
# speckled counter restore broad light/dark ordering and object separation.
# Screen-space anchors, owner silhouettes and occlusion should remain unchanged.
# Counter shading now resolves its exact component markers, avoiding dependence
# on a mesh's immediate parent. This is a material-scope correction.
#
# Ownership / support mapping:
# architecture: walls, slab, backsplash, counter fascia; slab surface z=.90.
# window: glass/frame/blinds/cords, attached to rear opening.
# cabinet: carcass/side/bottom/door/knob, rear wall attachment.
# paper_towels: roll/spindle/brackets, attached to cabinet front.
# towel: mount/ring/cloth; rear-wall attachment, hanging cloth has no counter bind.
# sink: dark basin/rim, inset in counter; foreground crop retained.
# faucet: base/upright/spout/handles, counter contact.
# blender: motor/socket/jar/lip, counter contact.
# small_can: cylinder/lid/label, counter contact; identity uncertain.
# water_jug: body/shoulder/neck/cap/handle/marks, counter contact.
# filter_pitcher: reservoir/shell/lid/spout/handle, counter contact.
# small_cup: body/rim/opening, counter contact.
# sponge_dish: dish/sponge, counter contact.
# Jug occludes blender and pitcher; cloth occludes can and may obscure blender
# in this view. All already exist: no absent-looking inventory is duplicated.
# Cloth shape and pitcher translucency remain uncertain.

scene = Scene('Kitchen corner')

# Camera parameters retained from successful step 2.
CAMERA = dict(position=(-2.60, -1.50, 2.12),
              target=(-.03, .47, 1.55), lens=65)

# Appearance parameters: estimated linear surface colors, not photographed RGB.
cream = (.49, .385, .245)
trim = (.59, .48, .325)
wall = (.46, .415, .315)
white = (.72, .675, .565)
metal = (.29, .275, .205)
dark = (.018, .021, .017)
blue = (.012, .032, .085)
granite = (.15, .125, .085)

def B(owner, slot, size, center, color):
    return owner.include(slot, box(size=size, center=center, color=color))

def R(owner, slot, radius, start, end, color):
    return owner.include(slot, rod(radius=radius, start=start, end=end, color=color))

def E(owner, slot, center, radii, color):
    node = ball(1, center=center, color=color)
    node.resize(radii, pivot=center)
    return owner.include(slot, node)

def tube(owner, slot, points, radius, color):
    return owner.include(slot, sweep_tube(points=points, radius=radius, color=color))

def ring(owner, slot, center, rx, rz, radius, color, count=28):
    x, y, z = center
    points = [(x + rx*math.cos(2*math.pi*i/count), y,
               z + rz*math.sin(2*math.pi*i/count)) for i in range(count+1)]
    return tube(owner, slot, points, radius, color)

# Architecture dimensions and placement unchanged.
architecture = Asset('Architecture')
B(architecture, 'back_wall', (3.6,.10,3.2), (0,.88,1.6), wall)
B(architecture, 'right_return', (.10,2.2,3.2), (1.20,-.17,1.6), wall)
B(architecture, 'counter_slab', (3.1,1.22,.075), (0,.24,.8625), granite)
B(architecture, 'backsplash', (3.1,.055,.13), (0,.792,.965), granite)
B(architecture, 'counter_front', (3.1,.055,.13), (0,-.36,.81), granite)
scene.include('architecture', architecture)

window = Asset('Window and blinds')
wx, wy = -.92, .803
B(window, 'daylight_glass', (.90,.018,2.35), (wx,wy,1.91), (.66,.80,.82))
for i,x in enumerate((wx-.47, wx+.47)):
    B(window, f'outer_vertical_{i}', (.055,.075,2.48), (x,.747,1.91), white)
for i,z in enumerate((.67,1.88,3.15)):
    B(window, f'cross_frame_{i}', (.99,.09,.055), (wx,.739,z), white)
B(window, 'central_mullion', (.035,.045,2.38), (wx-.12,.735,1.92), white)
for i in range(35):
    z=.72+i*.066
    slat=box((.94,.092,.019), center=(wx,.681,z), color=white)
    slat.turn('x', -13, pivot=(wx,.681,z))
    window.include(f'blind_slat_{i:02d}', slat)
for i,x in enumerate((wx-.31,wx+.31)):
    R(window, f'blind_cord_{i}', .004, (x,.613,.70),
      (x,.613,3.05), (.54,.52,.43))
B(window, 'window_sill', (1.04,.17,.055), (wx,.701,.655), trim)
scene.include('window', window)

cabinet = Asset('Upper cabinet')
cx=.36
B(cabinet, 'carcass', (.94,.36,1.61), (cx,.624,2.185), cream)
B(cabinet, 'left_side', (.045,.42,1.64), (cx-.47,.601,2.20), trim)
B(cabinet, 'bottom', (.99,.43,.045), (cx,.595,1.38), trim)
B(cabinet, 'door_panel', (.81,.025,1.45), (cx,.424,2.19), cream)
for i,x in enumerate((cx-.424,cx+.424)):
    B(cabinet, f'door_stile_{i}', (.055,.048,1.55), (x,.398,2.19), trim)
for i,z in enumerate((1.442,2.94)):
    B(cabinet, f'door_rail_{i}', (.85,.048,.055), (cx,.398,z), trim)
for i,x in enumerate((cx-.365,cx+.365)):
    B(cabinet, f'inner_bead_{i}', (.011,.014,1.36),
      (x,.394,2.19), (.43,.33,.20))
R(cabinet, 'knob_stem', .014, (.727,.369,1.63), (.727,.334,1.63), metal)
E(cabinet, 'knob', (.727,.322,1.63), (.023,.016,.023), metal)
scene.include('cabinet', cabinet)

paper = Asset('Paper towel dispenser')
px,py,pz=.375,.264,1.984
R(paper,'paper_roll',.143,(px,py,pz-.265),(px,py,pz+.265),white)
R(paper,'spindle',.018,(px,py,pz-.309),(px,py,pz+.309),metal)
E(paper,'top_finial',(px,py,pz+.302),(.027,.027,.038),metal)
for i,z in enumerate((pz-.294,pz+.294)):
    R(paper,f'bracket_{i}',.017,(px,.411,z),(px,py,z),metal)
    E(paper,f'mount_{i}',(px,.413,z),(.048,.013,.043),metal)
B(paper,'loose_paper_edge',(.249,.009,.48),
  (px+.013,py-.138,pz-.013),(.76,.71,.60))
scene.include('paper_towels', paper)

towel = Asset('Towel and ring')
tx,ty=-.31,.407
R(towel,'mount_stem',.018,(tx,.801,1.69),(tx,.476,1.69),metal)
E(towel,'mount_plate',(tx,.788,1.69),(.052,.016,.052),metal)
ring(towel,'metal_ring',(tx,ty,1.575),.091,.133,.008,metal)
E(towel,'fold_over_ring',(tx-.012,ty-.025,1.46),(.070,.045,.055),white)
cloth_sections=[
    ((tx-.024,ty-.032,1.285),(.075,.031,.185)),
    ((tx-.043,ty-.043,1.125),(.090,.034,.156)),
    ((tx+.027,ty+.006,1.24),(.060,.029,.200)),
    ((tx+.047,ty+.025,1.12),(.057,.026,.119))]
for i,(p,s) in enumerate(cloth_sections):
    E(towel,f'drape_{i}',p,s,white)
for i,x in enumerate((tx-.066,tx-.017,tx+.036)):
    R(towel,f'soft_fold_{i}',.009,(x,ty-.068,1.12),
      (x+.012,ty-.061,1.41),(.60,.55,.44))
scene.include('towel', towel)

sink=Asset('Sink')
B(sink,'basin_dark',(.67,.48,.018),(-.76,-.075,.907),(.012,.018,.014))
B(sink,'basin_bottom',(.55,.34,.012),(-.76,-.075,.914),(.022,.029,.022))
for i,x in enumerate((-1.105,-.415)):
    B(sink,f'side_rim_{i}',(.026,.54,.016),(x,-.075,.923),metal)
for i,y in enumerate((-.345,.195)):
    B(sink,f'end_rim_{i}',(.71,.026,.016),(-.76,y,.923),metal)
scene.include('sink', sink)

faucet=Asset('Faucet')
E(faucet,'base',(-.80,.286,.934),(.108,.060,.019),metal)
R(faucet,'upright',.014,(-.80,.286,.942),(-.80,.286,1.225),metal)
tube(faucet,'spout',[(-.80,.286,1.225),(-.80,.265,1.257),
                    (-.80,.207,1.25),(-.80,.153,1.201)],.014,metal)
for i,x in enumerate((-.885,-.713)):
    E(faucet,f'handle_base_{i}',(x,.275,.947),(.029,.028,.018),metal)
    R(faucet,f'handle_{i}',.009,(x,.275,.954),(x-.022,.238,.99),metal)
scene.include('faucet', faucet)

blender=Asset('Blender')
bx,by=-.015,.602
E(blender,'motor_base',(bx,by,1.018),(.092,.085,.118),dark)
R(blender,'upper_socket',.065,(bx,by,1.075),(bx,by,1.133),dark)
jar=box((.116,.105,.295),center=(bx,by,1.279),
        color=(.38,.43,.38),opacity=.23)
jar.turn('y',-8,pivot=(bx,by,1.13))
blender.include('clear_jar',jar)
for i,x in enumerate((bx-.058,bx+.058)):
    R(blender,f'jar_edge_{i}',.004,(x,by-.055,1.14),
      (x-.035,by-.055,1.424),metal)
B(blender,'jar_lip',(.12,.115,.013),(bx-.036,by,1.425),metal)
scene.include('blender', blender)

can=Asset('Small cylindrical container')
R(can,'body',.047,(-.225,.58,.905),(-.225,.58,1.125),(.21,.24,.115))
R(can,'lid',.051,(-.225,.58,1.125),(-.225,.58,1.14),metal)
B(can,'label',(.048,.006,.12),(-.225,.531,1.005),(.43,.40,.24))
scene.include('small_can', can)

jug=Asset('Gallon water jug')
jx,jy=.255,.259
E(jug,'lower_body',(jx,jy,1.042),(.135,.104,.142),(.44,.46,.39))
E(jug,'upper_body',(jx,jy,1.149),(.125,.097,.143),(.47,.49,.42))
E(jug,'shoulder',(jx,jy,1.241),(.089,.077,.091),(.51,.52,.44))
R(jug,'neck',.040,(jx,jy,1.262),(jx,jy,1.315),(.55,.56,.47))
R(jug,'cap',.043,(jx,jy,1.308),(jx,jy,1.332),(.69,.66,.54))
tube(jug,'molded_handle',[
    (jx+.067,jy-.071,1.245),(jx+.109,jy-.076,1.231),
    (jx+.119,jy-.076,1.18),(jx+.085,jy-.074,1.153)],
    .018,(.52,.53,.45))
for i,(dx,h) in enumerate(((-.045,.027),(-.021,.022),(.002,.025),
                            (.023,.022),(.044,.023))):
    R(jug,f'label_stroke_{i}',.0016,(jx+dx,jy-.105,1.002),
      (jx+dx-.002,jy-.106,1.002+h),(.16,.17,.14))
scene.include('water_jug', jug)

pitcher=Asset('Water filter pitcher')
qx,qy=.616,.515
E(pitcher,'blue_body',(qx,qy,1.075),(.116,.089,.166),blue)
E(pitcher,'clear_outer',(qx+.016,qy-.009,1.075),
  (.126,.101,.171),(.17,.22,.21))
E(pitcher,'front_blue',(qx-.015,qy-.086,1.086),
  (.087,.015,.144),(.016,.039,.10))
E(pitcher,'lid',(qx,qy,1.252),(.133,.102,.026),(.235,.25,.20))
tube(pitcher,'clear_handle',[
    (qx+.104,qy,1.228),(qx+.175,qy,1.205),
    (qx+.193,qy,1.137),(qx+.183,qy,1.047),
    (qx+.145,qy,1.003),(qx+.105,qy,1.019)],
    .017,(.32,.35,.29))
B(pitcher,'spout',(.057,.073,.034),(qx-.116,qy,1.24),(.235,.25,.20))
scene.include('filter_pitcher', pitcher)

cup=Asset('Small dark cup')
R(cup,'body',.039,(-.48,.205,.901),(-.48,.205,.953),(.085,.07,.04))
R(cup,'rim',.043,(-.48,.205,.953),(-.48,.205,.962),metal)
R(cup,'dark_opening',.034,(-.48,.205,.962),(-.48,.205,.964),dark)
scene.include('small_cup', cup)

sponge=Asset('Sink side sponge and dish')
B(sponge,'dish',(.15,.106,.018),(-1.17,-.015,.916),metal)
B(sponge,'sponge',(.12,.075,.024),(-1.17,-.018,.937),(.45,.42,.22))
scene.include('sponge_dish', sponge)

# Inline pre-execution self-review:
# Inventory, complete owners, dimensions, support and transforms preserved.
# Counter-supported bodies use z=.90; fascia/backsplash are not support anchors.
# About 250 expanded primitives; 35 slats and 28-segment ring are main repeats.
# Tubes expand to rods/balls; no dense textile or grain geometry is introduced.
# Positive finite dimensions; no fillet radii; adjacent tube endpoints distinct.
# Every repeated include slot is indexed and unique within its parent.
# All geometry remains in SceneAct; realize precedes camera/world/lights.
# Counter material changes use exact nonempty component descendants and copies.
# Other material edits are explicit palette choices in their original builders.
# Shader code preserves owner transforms and mesh topology.
# Review is not a claim of collision accuracy or passing regression tests.
realize(scene)

def meshes_under(slot):
    obj=bpy.data.objects.get(slot)
    assert obj is not None, slot
    meshes=[x for x in obj.children_recursive if x.type=='MESH']
    if obj.type=='MESH':
        meshes.append(obj)
    assert meshes, slot
    return meshes

# Procedural granite is restricted to the three counter components.
# No input image or external texture is used.
for component in ('counter_slab', 'backsplash', 'counter_front'):
    for obj in meshes_under(component):
        obj.data=obj.data.copy()
        for index,old in enumerate(list(obj.data.materials)):
            if old is None:
                continue
            mat=old.copy()
            obj.data.materials[index]=mat
            mat.use_nodes=True
            nt=mat.node_tree
            bs=nt.nodes.get('Principled BSDF')
            assert bs is not None
            tex=nt.nodes.new('ShaderNodeTexCoord')
            noise=nt.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=175
            noise.inputs['Detail'].default_value=2
            ramp=nt.nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.28
            ramp.color_ramp.elements[0].color=(.025,.021,.013,1)
            ramp.color_ramp.elements[1].position=.72
            ramp.color_ramp.elements[1].color=(.265,.225,.15,1)
            middle=ramp.color_ramp.elements.new(.50)
            middle.color=(.105,.085,.052,1)
            nt.links.new(tex.outputs['Object'],noise.inputs['Vector'])
            nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
            nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
            bs.inputs['Roughness'].default_value=.72

# Camera, illumination and world unchanged from step 2.
set_view(**CAMERA)
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new('World')
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.76,.79,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
area_emitter(position=(-1.8,.25,2.25),power=350,size=1.65,
             target=(.15,.35,1.25),color=(.82,.91,1.0))
area_emitter(position=(-.25,-2.2,2.9),power=105,size=2.5,
             target=(.1,.5,1.6),color=(1.0,.82,.59))
