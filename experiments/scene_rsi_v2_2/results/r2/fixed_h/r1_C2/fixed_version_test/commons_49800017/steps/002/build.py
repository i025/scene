from sceneact import *
import bpy
import math

# Reference inventory, normalized image bounds:
# Floor (.03,.61)-(.97,.95): pale, uninterrupted, mildly reflective.
# Ceiling (.03,.04)-(.97,.37): timber boards, seams and scattered dark knots.
# Main branching support (.11,.03)-(.69,.73): continuous curved laminated
# timber, broad upright foot, asymmetric arms, large open fork.
# Cross beam (.03,.20)-(.97,.43): grey wood, three inset rectangular grilles.
# Plaster enclosure (.03,.42)-(.97,.65), with dark narrow skirting.
# Vertical wood infills (.30,.43)-(.40,.63), (.79,.43)-(.92,.66).
# Pendant lights (.56,.11)-(.61,.28), (.91,.20)-(.96,.33).
# Small wall grille, outlets and exit marker retained below.
# Hidden wall connections and column rear construction remain uncertain.
#
# Feedback comparison: first build had a low, angular fork, conspicuous
# exposed lamination rods, insufficient beam perspective, and pale materials.
# Enabling material nodes had discarded the SceneAct diffuse colors.
# Revised arms are taller and smoothly sampled; unions remove internal joints.
#
# Expanded geometry estimate: approximately 225 primitive meshes:
# 68 column sections, 45 ceiling seams, 24 knots, roughly 88 other boxes/rods.
# Two column unions; no repeated cutters, fillet boxes or tube expansions.

scene = Scene('Grey timber hall')
WOOD = (.37,.385,.35)
LIGHTWOOD = (.60,.615,.57)
PLASTER = (.74,.75,.71)
FLOOR = (.73,.75,.71)
DARK = (.17,.19,.16)

floor = Asset('uninterrupted pale floor')
floor.include('floor slab', box((28,32,.14), center=(0,5,-.07), color=FLOOR))
scene.include('floor', floor)

walls = Asset('plaster rear enclosure')
walls.include('left rear plaster', box((11,.20,6.1), center=(-5.3,8,3.05), color=PLASTER))
walls.include('right rear plaster', box((8.8,.20,6.1), center=(4.6,9,3.05), color=PLASTER))
walls.include('corner return', box((.16,1.1,3.5), center=(.2,8.5,1.75), color=PLASTER))
walls.include('far right return', box((.18,10,7), center=(9,5,3.5), color=PLASTER))
walls.include('left skirting', box((11,.045,.105), center=(-5.3,7.875,.0525), color=DARK))
walls.include('right skirting', box((8.8,.045,.105), center=(4.6,8.875,.0525), color=DARK))
walls.include('corner skirting', box((.04,1,.105), center=(.10,8.5,.0525), color=DARK))
scene.include('walls', walls)

roof = Asset('pale boarded roof')
roof_height = 7.90
roof_angle = -7.0
roof.include('ceiling backing', box((25,29,.16), center=(0,4,roof_height), color=LIGHTWOOD))
for i in range(45):
    x = -11 + i*.5
    roof.include('board seam %02d' % i,
                 box((.009,29,.006), center=(x,4,roof_height-.083),
                     color=(.43,.45,.40)))
for i in range(24):
    x = -9 + (i%12)*1.55
    y = -3 + (i//12)*6.3 + (i%4)*.63
    knot = ball(.024, center=(x,y,roof_height-.084), color=(.29,.32,.27))
    knot.resize((1,.55,.12))
    roof.include('small knot %02d' % i,knot)
roof.turn('x',roof_angle,pivot=(0,4,roof_height))
scene.include('ceiling',roof)

beam = Asset('sloping transverse timber beam')
beam.include('main face',box((24,.70,.78),center=(0,5,4.62),color=WOOD))
beam.include('upper lip',box((24,.74,.045),center=(0,5,5.025),color=(.44,.46,.41)))
beam.include('lower timber edge',box((24,.73,.035),center=(0,5,4.215),color=(.31,.33,.29)))
beam.turn('y',5.2,pivot=(0,5,4.62))
scene.include('cross beam',beam)

overhead = Asset('longitudinal roof timbers')
overhead.include('left roof rail',box((.30,23,.38),center=(-6.1,3,7.03),color=WOOD))
overhead.include('right roof rail',box((.27,23,.32),center=(5.65,3,7.03),color=WOOD))
overhead.include('rear upright',box((.18,.22,2.56),center=(2.3,5,6.10),color=LIGHTWOOD))
scene.include('roof framing',overhead)

# Smooth centerline curves sampled into overlapping solid sections.
# Broad continuous faces and the open fork take precedence over tiny laminations.
column = Asset('laminated branching timber support')
column_y = .20
DEPTH = .78

def bezier(p0,p1,p2,p3,t):
    s=1-t
    return (s*s*s*p0[0]+3*s*s*t*p1[0]+3*s*t*t*p2[0]+t*t*t*p3[0],
            s*s*s*p0[1]+3*s*s*t*p1[1]+3*s*t*t*p2[1]+t*t*t*p3[1])

def curved_arm(name,controls,width,count):
    points=[bezier(*controls,i/count) for i in range(count+1)]
    pieces=[]
    for a,b in zip(points[:-1],points[1:]):
        dx,dz=b[0]-a[0],b[1]-a[1]
        piece=box((width,DEPTH,math.hypot(dx,dz)+.055),
                  center=((a[0]+b[0])/2,column_y,(a[1]+b[1])/2),color=WOOD)
        piece.turn('y',math.degrees(math.atan2(dx,dz)))
        pieces.append(piece)
    arm=Asset(name)
    arm.include('continuous curved timber',fuse(*pieces))
    return arm

column.include('upright trunk',
               box((.76,DEPTH,2.03),center=(-3.05,column_y,1.055),color=WOOD))
column.include('left rising arm',
               curved_arm('left curved arm',
                          ((-3.05,1.62),(-3.05,4.20),(-4.05,7.03),(-5.05,9.30)),
                          .68,32))
column.include('right sweeping arm',
               curved_arm('right curved arm',
                          ((-3.05,1.48),(-3.12,5.80),(-.75,7.72),(3.30,9.20)),
                          .74,36))
column.include('dark protective foot',
               box((.79,.82,.12),center=(-3.05,column_y,.06),color=(.16,.19,.15)))
scene.include('main branching column',column)

panels=Asset('vertical timber wall panels')
for label,x,y,width in [('left',-3.65,7.77,1.70),('right',6.72,8.77,2.15)]:
    panel=Asset(label+' timber infill')
    panel.include('boarded face',box((width,.18,3.12),center=(x,y,1.56),color=LIGHTWOOD))
    for i in range(11):
        px=x-width/2+(i+.5)*width/11
        panel.include('vertical seam %02d'%i,
                      box((.012,.012,3.12),center=(px,y-.098,1.56),
                          color=(.43,.46,.40)))
    panel.include('lintel',box((width+.15,.28,.20),center=(x,y,3.22),color=LIGHTWOOD))
    panels.include(label,panel)
scene.include('wall infills',panels)

grilles=Asset('ventilation fixtures')
for i,(x,width) in enumerate([(-7.6,1.35),(-.05,1.6),(6.85,1.20)]):
    z=4.62-math.sin(math.radians(5.2))*x
    grille=Asset('beam grille %d'%i)
    grille.include('thin pale frame',box((width,.028,.29),center=(x,4.632,z),color=(.66,.68,.62)))
    grille.include('dark opening',box((width-.07,.016,.225),center=(x,4.610,z),color=(.25,.28,.24)))
    for j in range(5):
        grille.include('vertical fin %d'%j,
                       box((.011,.012,.215),
                           center=(x+(j-2)*width/5.6,4.595,z),
                           color=(.41,.44,.38)))
    grilles.include('grille %d'%i,grille)
grilles.include('left wall grille',
                box((.76,.032,.22),center=(-7.4,7.86,3.12),color=(.37,.40,.34)))
grilles.include('low service grille',
                box((.48,.025,.18),center=(3.8,8.87,.35),color=(.57,.60,.54)))
scene.include('grilles',grilles)

fixtures=Asset('hanging cylindrical lights')
for label,x,y,z,r,h in [
    ('central',1.57,1.7,6.30,.30,1.03),
    ('right',7.40,3.1,5.84,.27,.89)]:
    lamp=Asset(label+' pendant')
    roof_z=roof_height-math.tan(math.radians(7))*(y-4)
    lamp.include('ceiling attachment',
                 rod(.047,start=(x,y,roof_z-.08),end=(x,y,roof_z+.01),color=DARK))
    lamp.include('suspension stem',
                 rod(.016,start=(x,y,z+h/2),end=(x,y,roof_z-.06),color=DARK))
    lamp.include('grey cylindrical shade',
                 rod(r,start=(x,y,z-h/2),end=(x,y,z+h/2),color=(.31,.34,.29)))
    lamp.include('white bottom diffuser',
                 rod(r*.94,start=(x,y,z-h/2-.018),end=(x,y,z-h/2-.002),
                     color=(.94,.96,.89)))
    fixtures.include(label,lamp)
scene.include('pendant fixtures',fixtures)

details=Asset('small wall fittings')
details.include('exit marker',box((.24,.032,.19),center=(5.15,8.83,2.85),color=(.31,.38,.30)))
details.include('exit symbol',box((.045,.012,.12),center=(5.15,8.807,2.85),color=(.80,.84,.75)))
details.include('right narrow door jamb',
                box((.045,.06,2.75),center=(5.20,8.83,1.375),color=(.51,.54,.48)))
for i,(x,y) in enumerate([(-1.0,7.865),(4.1,8.865)]):
    details.include('low outlet %d'%i,
                    box((.065,.025,.055),center=(x,y,.15),color=(.22,.25,.20)))
scene.include('wall fittings',details)

realize(scene)

# Preserve the actual SceneAct finish when introducing shader nodes.
for mat in bpy.data.materials:
    original=tuple(mat.diffuse_color)
    previously_used_nodes=mat.use_nodes
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    if not previously_used_nodes:
        bs.inputs['Base Color'].default_value=original
    color=tuple(bs.inputs['Base Color'].default_value)
    bs.inputs['Roughness'].default_value=.79
    is_wood=(abs(color[0]-WOOD[0])<.025 and abs(color[1]-WOOD[1])<.025)
    is_lightwood=(abs(color[0]-LIGHTWOOD[0])<.025 and abs(color[1]-LIGHTWOOD[1])<.025)
    if is_wood or is_lightwood:
        nodes=mat.node_tree.nodes
        links=mat.node_tree.links
        coords=nodes.new('ShaderNodeTexCoord')
        stretch=nodes.new('ShaderNodeVectorMath')
        stretch.operation='MULTIPLY'
        stretch.inputs[1].default_value=(14,14,.42)
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=3.8
        noise.inputs['Detail'].default_value=2
        links.new(coords.outputs['Generated'],stretch.inputs[0])
        links.new(stretch.outputs[0],noise.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        base=LIGHTWOOD if is_lightwood else WOOD
        ramp.color_ramp.elements[0].position=.12
        ramp.color_ramp.elements[0].color=tuple(v*.73 for v in base)+(1,)
        ramp.color_ramp.elements[1].position=.88
        ramp.color_ramp.elements[1].color=tuple(min(v*1.22,1) for v in base)+(1,)
        links.new(noise.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    if abs(color[0]-FLOOR[0])<.012 and abs(color[1]-FLOOR[1])<.012:
        bs.inputs['Roughness'].default_value=.30
    if color[0]>.90:
        bs.inputs['Emission Color'].default_value=(.9,.94,.84,1)
        bs.inputs['Emission Strength'].default_value=.35

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.79,.82,.76,1)
background.inputs['Strength'].default_value=.40

set_view((.3,-12.8,2.45),(.15,4.8,2.58),lens=31.5,sensor=36)
area_emitter((-7,-4,6.0),power=1600,size=8,target=(-1,4,.8))
area_emitter((6,-1,6.4),power=1050,size=7,target=(2,6,1))
area_emitter((0,7,6.5),power=450,size=5,target=(0,2,0))
sc.render.resolution_x=512
sc.render.resolution_y=406
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.15
