from sceneact import *
import bpy
import math
import random
from mathutils import Quaternion

# Reference inventory (normalized image estimates):
# Left storage rack: x 0-.83, y .02-1.00; tall perforated uprights,
# dark open shelf undersides, yellow supports and irregular pallet loads.
# Wrapped tan crates: left edge, y .05-.22, .40-.55, .57-.81 and .87-1;
# additional smaller loads recede toward the lower-right vanishing region.
# Opposite rack: narrow strip x .90-1, y 0-.35, mostly occluded.
# Corrugated industrial roof: x .10-1, y 0-.85; transverse steel beams,
# pipes, a gridded skylight around x .60-.84, y .20-.37.
# Bright linear fixtures run diagonally down the ceiling, x .32-.91.
# Distant end wall occupies a small lower-right region. Floor is outside frame.
# Hidden contents, rear rack faces and exact shelf occupancy remain uncertain.
#
# Editable assets correspond to roof, skylight, lighting, left/right racks,
# individual pallet loads, and distant wall. Expanded count about 650 boxes:
# racks ~280, loads/pallets/wrap bands ~220, ceiling and fixtures ~130.
# All dimensions are positive; no Booleans or expanded filleted primitives.

random.seed(23)
scene = Scene('Warm industrial warehouse')

olive = (.235, .245, .168)
darksteel = (.12, .145, .115)
yellow = (.70, .47, .075)
palletwood = (.43, .34, .16)
tan = (.57, .49, .30)
roofcolor = (.31, .31, .235)

def addbox(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

roof = Asset('Roof structure and corrugated panels')
addbox(roof, 'roof decking', (17, 31, .15), (1, 10, 11.75), roofcolor)
# Long raised seams and deeper transverse beams leave large clear roof fields.
for i in range(31):
    x = -6.4 + i * .49
    addbox(roof, 'standing roof seam %02d' % i,
           (.065, 31, .105), (x, 10, 11.62), (.36, .36, .275))
for i, y in enumerate([-3, 2.5, 8, 13.5, 19, 24]):
    addbox(roof, 'transverse structural beam %02d' % i,
           (16, .22, .45), (1, y, 11.30), olive)
    addbox(roof, 'beam lower flange %02d' % i,
           (16, .34, .065), (1, y, 11.06), (.27, .28, .205))
for i, x in enumerate([-.25, 3.9]):
    addbox(roof, 'long ceiling conduit %d' % i,
           (.055, 29, .055), (x, 10, 11.15), (.36, .36, .26))
scene.include('roof', roof)

sky = Asset('Gridded roof skylight')
sx, sy, sz = 2.65, 3.4, 11.52
addbox(sky, 'translucent bright glazing', (2.3, 3.7, .035),
       (sx, sy, sz), (.79, .87, .80))
for i, x in enumerate([sx-1.2, sx+1.2]):
    addbox(sky, 'side steel frame %d' % i, (.12, 3.94, .13),
           (x, sy, sz-.065), darksteel)
for i, y in enumerate([sy-1.91, sy+1.91]):
    addbox(sky, 'end steel frame %d' % i, (2.5, .12, .13),
           (sx, y, sz-.065), darksteel)
for i in range(1, 7):
    addbox(sky, 'longitudinal glazing bar %d' % i, (.035, 3.7, .065),
           (sx-1.15+i*2.3/7, sy, sz-.065), olive)
for i in range(1, 11):
    addbox(sky, 'cross glazing bar %d' % i, (2.3, .035, .065),
           (sx, sy-1.85+i*3.7/11, sz-.07), olive)
scene.include('skylight', sky)

fixtures = Asset('Continuous aisle fluorescent fixtures')
for i, y in enumerate([-3.6, .1, 5.8, 11.4, 17.0, 22.2]):
    x = .7
    addbox(fixtures, 'metal fixture housing %d' % i,
           (.27, 2.45, .13), (x, y, 11.03), (.49, .48, .35))
    addbox(fixtures, 'luminous diffuser %d' % i,
           (.19, 2.30, .055), (x, y, 10.94), (1.0, .98, .76))
    for j, dy in enumerate([-.85, .85]):
        addbox(fixtures, 'fixture suspension %d %d' % (i,j),
               (.025, .025, .43), (x, y+dy, 11.36), darksteel)
scene.include('overhead lights', fixtures)

levels = [1.0, 3.35, 5.7, 8.05, 10.4]
baylength = 3.0
rack_depth = 2.25

def rack(name, front_x, side, bays):
    asset = Asset(name)
    back_x = front_x + side*rack_depth
    mid_x = (front_x+back_x)/2
    # Open frames with visible slender posts, flange strips and punched slots.
    for k in range(bays+1):
        y = -1.5+k*baylength
        for j, x in enumerate([front_x, back_x]):
            addbox(asset, 'upright %d %d' % (k,j),
                   (.115, .15, 10.9), (x,y,5.45), olive)
            addbox(asset, 'upright flange %d %d' % (k,j),
                   (.055,.21,10.9), (x-side*.065,y,5.45), (.32,.33,.235))
        if k < 5:
            for h in range(15):
                addbox(asset, 'visible upright slot %d %d' % (k,h),
                       (.012,.038,.065), (front_x-side*.096,y-.055,.6+h*.68),
                       (.075,.085,.06))
        for h, z in enumerate(levels):
            addbox(asset,'frame depth tie %d %d' % (k,h),
                   (rack_depth,.10,.11),(mid_x,y,z+.11),darksteel)
    for b in range(bays):
        y=-1.5+(b+.5)*baylength
        for h,z in enumerate(levels):
            for j,x in enumerate([front_x,back_x]):
                addbox(asset,'longitudinal shelf beam %d %d %d'%(b,h,j),
                       (.13,baylength,.21),(x,y,z),olive)
                # Distinct yellow end connectors are prominent on the front.
                if j == 0:
                    for q,dy in enumerate([-.5*baylength+.16,.5*baylength-.16]):
                        addbox(asset,'yellow beam connector %d %d %d'%(b,h,q),
                               (.24,.29,.29),(x-side*.045,y+dy,z+.035),yellow)
            for q in range(4):
                addbox(asset,'open shelf cross member %d %d %d'%(b,h,q),
                       (rack_depth,.075,.095),
                       (mid_x,y-1.1+q*.73,z+.12),darksteel)
    scene.include(name,asset)
    return front_x, back_x

rack('Left towering pallet rack', -.8, -1, 7)
rack('Opposite right rack', 5.4, 1, 5)

def load(name, front_x, side, y, shelf_z, height, width, depth, color):
    a=Asset(name)
    cx=front_x+side*(depth*.5+.12)
    # Pallet slats and feet remain visibly separate from wrapped cargo.
    for j,yy in enumerate([y-width*.39,y,y+width*.39]):
        addbox(a,'pallet transverse slat %d'%j,
               (depth+.1,.16,.09),(cx,yy,shelf_z+.22),palletwood)
    for j,xx in enumerate([cx-depth*.35,cx+depth*.35]):
        addbox(a,'pallet runner %d'%j,
               (.14,width,.14),(xx,y,shelf_z+.13),yellow)
    addbox(a,'wrapped rectangular cargo',(depth,width,height),
           (cx,y,shelf_z+.28+height/2),color)
    # Thin translucent-looking bands describe taut stretch wrap over rough boxes.
    for j, frac in enumerate([.12,.30,.49,.68,.87]):
        z=shelf_z+.28+height*frac
        addbox(a,'stretch wrap horizontal band %d'%j,
               (depth+.018,width+.018,.018),(cx,y,z),
               tuple(min(1,c*1.17) for c in color))
    # Several broad packing seams remain visible on the exposed aisle face.
    for j,dy in enumerate([-.26,.27]):
        addbox(a,'vertical packing seam %d'%j,
               (.015,.018,height*.94),
               (front_x+side*.108,y+width*dy,shelf_z+.28+height*.5),
               tuple(c*.82 for c in color))
    scene.include(name,a)

# Occupancy deliberately irregular; open rack undersides are a major image feature.
specs = [
    (0,0,1.95,2.36,1.80),(0,1,1.72,2.15,1.87),
    (0,2,1.50,2.00,1.75),(0,3,1.33,2.13,1.9),
    (1,0,1.85,2.35,1.85),(1,2,1.82,2.50,1.85),
    (1,3,1.25,2.23,1.75),(2,0,1.80,2.40,1.85),
    (2,1,1.56,2.10,1.75),(2,3,1.50,2.40,1.90),
    (3,0,1.85,2.25,1.85),(3,1,1.75,2.40,1.9),
    (3,2,1.65,2.30,1.8),(4,1,1.72,2.35,1.8),
    (4,2,1.55,2.35,1.85),(4,3,1.40,2.30,1.8),
    (5,0,1.75,2.40,1.85),(5,2,1.70,2.35,1.8),
    (5,3,1.50,2.30,1.8),(6,1,1.65,2.30,1.85),
    (6,2,1.60,2.30,1.8),(6,3,1.30,2.30,1.8)]
for n,(bay,level,h,w,d) in enumerate(specs):
    c=[(.59,.52,.33),(.67,.59,.40),(.46,.41,.27),(.72,.66,.46)][n%4]
    load('Left pallet load %02d'%n,-.8,-1,bay*3.0,levels[level],h,w,d,c)
for b in range(5):
    for h in [1,3]:
        load('Right pallet load %d %d'%(b,h),5.4,1,b*3,levels[h],
             1.55,2.35,1.85,(.55,.49,.32))

wall=Asset('Distant warehouse wall')
addbox(wall,'end wall',(14,.2,11.6),(1,21.7,5.8),(.47,.46,.35))
addbox(wall,'high dark ventilation opening',(1.6,.05,.7),(3,21.55,8.7),(.14,.16,.13))
for i in range(4):
    addbox(wall,'vent louver %d'%i,(1.6,.08,.035),(3,21.48,8.43+i*.17),olive)
scene.include('end wall',wall)

realize(scene)

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
background.inputs['Color'].default_value=(.36,.36,.25,1)
background.inputs['Strength'].default_value=.32

# Shared surface treatment: rough fibre/film variation without extra microgeometry.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    p=mat.node_tree.nodes.get('Principled BSDF')
    if p is None:
        continue
    col=p.inputs['Base Color'].default_value
    p.inputs['Roughness'].default_value=.66
    if col[0]>.92 and col[1]>.9:
        p.inputs['Emission Color'].default_value=(1.0,.94,.62,1)
        p.inputs['Emission Strength'].default_value=9
    elif col[0]>.75 and col[2]>.65:
        p.inputs['Emission Color'].default_value=(.74,.86,.84,1)
        p.inputs['Emission Strength'].default_value=2.7
    elif col[0]>.4 and col[0]>col[2]*1.3:
        nodes=mat.node_tree.nodes
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=24
        noise.inputs['Detail'].default_value=2
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.18
        bump.inputs['Distance'].default_value=.025
        mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
        p.inputs['Roughness'].default_value=.43

set_view((1.05,-3.65,1.55),(.42,6.5,9.15),lens=23.5,sensor=36)
cam=sc.camera
cam.rotation_mode='QUATERNION'
cam.rotation_quaternion=cam.rotation_quaternion @ Quaternion((0,0,1),math.radians(-14))

for y in [-2,3.5,9,15,20]:
    area_emitter((.8,y,10.65),power=650,size=3.0,
                 target=(-1,y+1,4),color=(1,.84,.48))
area_emitter((2.65,3.4,11.1),power=950,size=2.6,
             target=(-1,4,3.5),color=(.78,.87,1))
area_emitter((2,-4,6.5),power=420,size=5,
             target=(-2,3,5),color=(1,.84,.54))

sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.35
# A restrained glow reproduces the bright fluorescent bloom.
sc.use_nodes=True
tree=sc.node_tree
tree.nodes.clear()
rl=tree.nodes.new('CompositorNodeRLayers')
gl=tree.nodes.new('CompositorNodeGlare')
gl.glare_type='FOG_GLOW'
gl.quality='MEDIUM'
gl.threshold=1.5
gl.size=7
out=tree.nodes.new('CompositorNodeComposite')
tree.links.new(rl.outputs['Image'],gl.inputs['Image'])
tree.links.new(gl.outputs['Image'],out.inputs['Image'])
