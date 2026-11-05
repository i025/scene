from sceneact import *
import bpy
import math
import random
from mathutils import Quaternion

# Reference inventory, approximate normalized image bounds:
# Left pallet rack: (0,0)-(.96,1), open dark undersides, slim olive posts,
# yellow projecting pallet shoes, irregular tan wrapped loads.
# Prominent loads: (0,.06)-(.16,.25), (.11,.40)-(.26,.55),
# (.05,.56)-(.27,.82), (0,.87)-(.27,1), with smaller loads receding right.
# Roof: (.12,0)-(1,.83), corrugated panels, cross beams and thin conduits.
# Skylight: (.59,.20)-(.83,.37), bright rectangular glazing with dark grid.
# Fluorescent strips: (.32,0)-(.88,.66), white cores and yellow bloom.
# Right rack: narrow upper-right edge; end wall: small lower-right region.
# Back faces and concealed cargo remain uncertain.
#
# Feedback comparison:
# First image had pale cargo and framework, insufficient dark open shelf space,
# an oversized end wall and too much opposite rack. Restore material colors
# explicitly when enabling shader nodes; narrow cargo, retain gaps, extend aisle,
# and turn the camera farther toward the left rack while looking higher.
#
# Expanded primitive estimate: roof 70; skylight 22; fixtures 28;
# left rack ~420; right rack ~115; 27 loads * 10 = 270; wall 6.
# Approximately 930 simple meshes, no Booleans, fillets or dense curved paths.
# All dimensions positive. Relationships are explicit in named parent assets.

random.seed(23)
scene = Scene('Warm industrial warehouse revised')

olive = (.20, .22, .145)
darksteel = (.065, .085, .067)
yellow = (.76, .48, .035)
wood = (.37, .27, .105)
roofcolor = (.235, .24, .175)

def B(a, name, size, center, color):
    a.include(name, box(size=size, center=center, color=color))

roof = Asset('Roof structure and corrugated panels')
B(roof, 'roof decking', (19, 43, .15), (1, 15, 11.75), roofcolor)
for i in range(39):
    B(roof, 'raised corrugation %02d' % i,
      (.065, 43, .12), (-8+i*.49, 15, 11.62), (.29,.29,.21))
for i,y in enumerate([-3,2.5,8,13.5,19,24.5,30]):
    B(roof, 'cross beam web %d'%i, (18,.19,.43),
      (1,y,11.29), olive)
    B(roof, 'cross beam flange %d'%i, (18,.32,.065),
      (1,y,11.055), (.26,.27,.18))
for i,x in enumerate([-.25,3.9]):
    B(roof,'ceiling conduit %d'%i,(.045,42,.045),
      (x,15,11.13),(.35,.34,.21))
scene.include('roof',roof)

sky=Asset('Gridded roof skylight')
sx,sy,sz=2.65,3.6,11.52
B(sky,'bright glazing',(2.3,3.25,.035),(sx,sy,sz),(.74,.85,.82))
for i,x in enumerate([sx-1.2,sx+1.2]):
    B(sky,'side frame %d'%i,(.10,3.45,.12),(x,sy,sz-.06),darksteel)
for i,y in enumerate([sy-1.69,sy+1.69]):
    B(sky,'end frame %d'%i,(2.5,.10,.12),(sx,y,sz-.06),darksteel)
for i in range(1,7):
    B(sky,'long glazing bar %d'%i,(.033,3.25,.065),
      (sx-1.15+i*2.3/7,sy,sz-.07),olive)
for i in range(1,10):
    B(sky,'cross glazing bar %d'%i,(2.3,.033,.065),
      (sx,sy-1.625+i*3.25/10,sz-.07),olive)
scene.include('skylight',sky)

fixtures=Asset('Aisle fluorescent fixtures')
for i,y in enumerate([-3.6,.1,5.8,11.4,17,22.2,28]):
    B(fixtures,'fixture housing %d'%i,(.25,2.45,.12),
      (.7,y,11.03),(.38,.37,.25))
    B(fixtures,'luminous diffuser %d'%i,(.17,2.3,.055),
      (.7,y,10.94),(1,.98,.79))
    for j,dy in enumerate([-.85,.85]):
        B(fixtures,'suspension %d %d'%(i,j),(.022,.022,.43),
          (.7,y+dy,11.36),darksteel)
scene.include('overhead lights',fixtures)

levels=[1.0,3.35,5.7,8.05,10.4]
bay_length=3.0
rack_depth=2.25

def rack(name,front,side,bays,detail=True):
    a=Asset(name)
    back=front+side*rack_depth
    mid=(front+back)/2
    for k in range(bays+1):
        y=-1.5+k*bay_length
        for j,x in enumerate([front,back]):
            B(a,'upright %d %d'%(k,j),(.105,.14,10.9),(x,y,5.45),olive)
        B(a,'front upright flange %d'%k,(.045,.19,10.9),
          (front-side*.065,y,5.45),(.30,.31,.205))
        if detail and k<4:
            for h in range(18):
                B(a,'upright perforation %d %d'%(k,h),(.012,.038,.075),
                  (front-side*.093,y-.045,.45+h*.57),(.055,.065,.04))
        for h,z in enumerate(levels):
            B(a,'depth tie %d %d'%(k,h),(rack_depth,.075,.085),
              (mid,y,z+.09),darksteel)
    for b in range(bays):
        y=b*3.
        for h,z in enumerate(levels):
            for j,x in enumerate([front,back]):
                B(a,'shelf longitudinal rail %d %d %d'%(b,h,j),
                  (.11,3,.16),(x,y,z),olive)
            for q in range(3):
                yy=y-1.10+q*1.10
                B(a,'open shelf cross member %d %d %d'%(b,h,q),
                  (rack_depth,.065,.075),(mid,yy,z+.08),darksteel)
            for q,dy in enumerate([-1.12,1.12]):
                yy=y+dy
                B(a,'yellow projecting support %d %d %d'%(b,h,q),
                  (.43,.25,.22),(front-side*.105,yy,z+.08),yellow)
                if detail and b<5:
                    B(a,'yellow support raised stop %d %d %d'%(b,h,q),
                      (.10,.25,.22),(front-side*.29,yy,z+.22),yellow)
    scene.include(name,a)

rack('Left towering pallet rack',-.8,-1,9,True)
rack('Opposite right rack',7.2,1,5,False)

def load(name,front,side,y,z,height,width,depth,color):
    a=Asset(name)
    cx=front+side*(depth/2+.12)
    for j,yy in enumerate([y-width*.39,y,y+width*.39]):
        B(a,'wood pallet slat %d'%j,(depth+.1,.14,.08),
          (cx,yy,z+.20),wood)
    for j,xx in enumerate([cx-depth*.34,cx+depth*.34]):
        B(a,'pallet runner %d'%j,(.13,width,.12),
          (xx,y,z+.12),wood)
    B(a,'wrapped cargo',(depth,width,height),
      (cx,y,z+.26+height/2),color)
    for j,frac in enumerate([.16,.43,.72]):
        B(a,'stretch film fold %d'%j,(depth+.014,width+.014,.012),
          (cx,y,z+.26+height*frac),
          tuple(min(1,c*1.12) for c in color))
    B(a,'exposed packing seam',(.014,.018,height*.95),
      (front+side*.109,y+width*.15,z+.26+height/2),
      tuple(c*.75 for c in color))
    scene.include(name,a)

specs=[
    (0,0,1.85,1.65,1.80),(0,1,1.65,1.55,1.87),
    (0,2,1.25,1.45,1.75),(0,3,1.28,1.65,1.9),
    (1,0,1.65,1.65,1.85),(1,2,1.62,1.65,1.85),
    (1,3,1.10,1.70,1.75),(2,0,1.60,1.75,1.85),
    (2,1,1.45,1.55,1.75),(2,3,1.35,1.70,1.9),
    (3,0,1.70,1.65,1.85),(3,1,1.50,1.65,1.9),
    (3,2,1.50,1.75,1.8),(4,1,1.55,1.7,1.8),
    (4,2,1.45,1.65,1.85),(4,3,1.3,1.75,1.8),
    (5,0,1.60,1.70,1.85),(5,2,1.5,1.7,1.8),
    (5,3,1.35,1.70,1.8),(6,1,1.50,1.70,1.85),
    (6,2,1.45,1.70,1.8),(6,3,1.20,1.70,1.8),
    (7,1,1.50,1.7,1.8),(7,3,1.3,1.7,1.8),
    (8,2,1.5,1.7,1.8)]
palette=[(.48,.38,.18),(.61,.52,.31),(.38,.32,.17),(.67,.59,.39)]
for n,(bay,level,h,w,d) in enumerate(specs):
    load('Left pallet load %02d'%n,-.8,-1,bay*3,levels[level],h,w,d,palette[n%4])
for b in [0,2]:
    load('Right pallet load %d'%b,7.2,1,b*3,8.05,1.5,1.8,1.85,(.49,.40,.22))

wall=Asset('Distant warehouse wall')
B(wall,'end wall',(18,.2,11.6),(1,31.7,5.8),(.36,.35,.25))
B(wall,'high ventilation opening',(1.6,.05,.7),(3,31.55,8.7),(.10,.12,.08))
for i in range(4):
    B(wall,'vent louver %d'%i,(1.6,.08,.035),(3,31.48,8.43+i*.17),olive)
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
background.inputs['Color'].default_value=(.30,.31,.19,1)
background.inputs['Strength'].default_value=.16

# SceneAct's display colors must be carried into newly enabled node materials.
for mat in bpy.data.materials:
    original=tuple(mat.diffuse_color)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get('Principled BSDF')
    if p is None:
        continue
    p.inputs['Base Color'].default_value=original
    p.inputs['Roughness'].default_value=.65
    r,g,b=original[:3]
    if r>.95 and g>.9:
        p.inputs['Emission Color'].default_value=(1,.96,.70,1)
        p.inputs['Emission Strength'].default_value=12
    elif b>.70 and g>.75:
        p.inputs['Emission Color'].default_value=(.76,.86,.84,1)
        p.inputs['Emission Strength'].default_value=3.2
    elif r>.34 and r>b*1.3:
        nodes=mat.node_tree.nodes
        tex=nodes.new('ShaderNodeTexCoord')
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=7
        noise.inputs['Detail'].default_value=2
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.16
        ramp.color_ramp.elements[0].color=(r*.58,g*.58,b*.58,1)
        ramp.color_ramp.elements[1].position=.84
        ramp.color_ramp.elements[1].color=(min(r*1.28,1),min(g*1.28,1),min(b*1.28,1),1)
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.14
        bump.inputs['Distance'].default_value=.018
        links=mat.node_tree.links
        links.new(tex.outputs['Generated'],noise.inputs['Vector'])
        links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],p.inputs['Base Color'])
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],p.inputs['Normal'])
        p.inputs['Roughness'].default_value=.40

set_view((1.05,-3.65,1.55),(-1.2,6.5,10.5),lens=24,sensor=36)
cam=sc.camera
cam.rotation_mode='QUATERNION'
cam.rotation_quaternion=cam.rotation_quaternion @ Quaternion((0,0,1),math.radians(-17))

for y in [-2,3.5,9,15,21,27]:
    area_emitter((.8,y,10.65),power=440,size=2.7,
                 target=(-1.7,y+1,4),color=(1,.82,.40))
area_emitter((2.65,3.6,11.1),power=750,size=2.4,
             target=(-1,4,3.5),color=(.80,.88,1))
area_emitter((2,-4,6.5),power=260,size=4,
             target=(-2,3,5),color=(1,.79,.38))

sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.45
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
