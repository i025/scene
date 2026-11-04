import bpy, math, random
from mathutils import Vector
from sceneact import *

# Assemblies: paneled cream wall, parquet floor, left curtains, carved chaise,
# loose pillow, green seat label, and a cropped cane chair at lower left.
# Approximate image landmarks: head crown (.09,.25), seat/head junction (.36,.49),
# foot (.82,.70), front feet (.33,.84), (.78,.94), wall/floor corner (.91,.50).
# Upholstered head and side wings are FILLED panels; space below the apron is open.
# Uncertain: hidden rear feet, head curvature, and wall distance behind the chaise.

random.seed(12)
LENGTH, WIDTH, SEAT_Z = 2.65, 1.02, .67
CAMERA = (3.15, -5.4, 3.65)
TARGET = (-.08, .03, .89)
LENS = 47
FRAME = (.40, .46, .38)
EDGE = (.63, .63, .48)
CREAM = (.78, .74, .63)
WALL = (.70, .68, .60)

scene = Scene('French chaise interior')
architecture = Asset('Architecture')
architecture.include('floor', box((12, 12, .12), center=(0, 0, -.07),
                                  color=(.20, .105, .058)))
architecture.include('back_wall', box((10, .16, 4), center=(0, 1.12, 2), color=WALL))
architecture.include('right_pilaster', box((.43, .42, 3.4),
                     center=(2.17, .96, 1.7), color=(.75, .74, .67)))

def trim(name, size, pos, color=CREAM):
    architecture.include(name, box(size, center=pos, color=color))

for z, depth, height in [(.08,.12,.16),(.21,.09,.055),(.28,.065,.035),
                         (1.64,.055,.045),(1.72,.075,.04),(1.91,.045,.025),
                         (2.13,.065,.04)]:
    trim('horizontal_'+str(z), (8, depth, height), (0,1.005-depth/2,z))
# Broad rectangular raised wall molding.
for x in [-1.91, 1.91]:
    trim('panel_side_'+str(x), (.027,.035,1.20), (x,1.005,.96))
    trim('panel_side_inner_'+str(x), (.012,.045,1.12), (x + (.043 if x<0 else -.043),.988,.96))
for z in [.36,1.56]:
    trim('panel_edge_'+str(z), (3.83,.035,.028), (0,1.005,z))
for z in [.40,1.52]:
    trim('panel_inner_'+str(z), (3.74,.042,.013), (0,.992,z))
trim('pilaster_inner', (.024,.025,2.3), (2.07,.733,1.60))
scene.include('architecture', architecture)

chaise = Asset('Chaise_longue')
# Solid carved apron below the upholstery.
chaise.include('front_apron', box((2.38,.075,.18), center=(.03,-.502,.535),color=FRAME))
chaise.include('back_apron', box((2.38,.065,.15), center=(.03,.49,.55),color=FRAME))
chaise.include('foot_apron', box((.08,.91,.16),center=(1.25,0,.54),color=FRAME))

def tube(parent, name, pts, radius, color):
    parent.include(name, sweep_tube(points=pts,radius=radius,color=color))

# Short, continuous cabriole paths with outward feet.
for x in [-1.00,1.17]:
    for y in [-.46,.43]:
        s = -1 if x<0 else 1
        t = -1 if y<0 else 1
        pts=[(x,y,.55),(x+.025*s,y+.018*t,.44),
             (x-.025*s,y+.035*t,.29),(x-.045*s,y+.06*t,.11),
             (x+.01*s,y+.09*t,.045)]
        tube(chaise,'leg_'+str(x)+'_'+str(y),pts,.039,FRAME)
        tube(chaise,'leg_gilt_'+str(x)+'_'+str(y),
             [(p[0],p[1]-.033,p[2]) for p in pts],.008,EDGE)

# Upholstered front wing rises steeply into the left head.
wing_outline=[(-1.37,.64),(-1.43,1.34),(-1.32,1.43),(-1.15,1.29),
              (-.99,1.16),(-.81,1.04),(-.65,.96),(-.54,.83),
              (-.53,.61),(-.73,.51),(-1.12,.53)]
for y in [-.515,.48]:
    pts=[(x,y,z) for x,z in wing_outline]
    tube(chaise,'wing_border_'+str(y),pts+[pts[0]],.031,FRAME)
    tube(chaise,'wing_beading_'+str(y),
         [(x,y-.025,z+.009) for x,z in wing_outline]+
         [(wing_outline[0][0],y-.025,wing_outline[0][1]+.009)],.008,EDGE)

# Head frame across the width, with an irregular arched crown.
head_top=[(-1.40,-.50,1.34),(-1.43,-.38,1.58),(-1.44,-.18,1.69),
          (-1.43,.06,1.70),(-1.39,.30,1.62),(-1.34,.48,1.48)]
tube(chaise,'head_crown',head_top,.038,FRAME)
tube(chaise,'head_crown_bead',[(x+.022,y,z+.018) for x,y,z in head_top],.009,EDGE)
for y in [-.50,.48]:
    tube(chaise,'head_post_'+str(y),
         [(-1.32,y,.50),(-1.37,y,.86),(-1.41,y,1.24),(-1.40,y,1.48)],.035,FRAME)
# Upholstery-edge piping along the long seat.
for y in [-.51,.51]:
    tube(chaise,'seat_piping_'+str(y),
         [(-1.09,y,.72),(-.55,y,.73),(.25,y,.73),(1.06,y,.72),(1.29,y*.85,.69)],.011,EDGE)
tube(chaise,'apron_lower_bead',
     [(-1.13,-.548,.49),(-.70,-.548,.47),(-.23,-.548,.48),
      (.20,-.548,.46),(.72,-.548,.48),(1.22,-.51,.49)],.012,EDGE)
# Modest central carved floral relief.
for i in range(7):
    a=2*math.pi*i/7
    chaise.include('apron_rosette_'+str(i),
       ball(.025,center=(.08+.064*math.cos(a),-.557,.49+.037*math.sin(a)),color=EDGE))
scene.include('chaise',chaise)

# Cropped foreground chair: cane seat, frame, and a little side rail.
chair = Asset('Foreground_cane_chair')
chair.include('seat_base',box((.71,.70,.065),center=(-1.63,-1.90,.45),color=FRAME))
for y in [-2.25,-1.55]:
    chair.include('rail_'+str(y),box((.79,.045,.065),center=(-1.63,y,.49),color=EDGE))
for x in [-2.02,-1.24]:
    chair.include('side_'+str(x),box((.05,.74,.065),center=(x,-1.90,.49),color=FRAME))
tube(chair,'curved_back_visible',[(-2.02,-1.55,.49),(-2.05,-1.55,.63),
     (-2.08,-1.55,.82)],.025,FRAME)
scene.include('foreground_chair',chair)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.75,.78,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32

def material(name,color,roughness=.75):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    return m

fabric=material('Ivory woven fabric with faded rose stripes',(.84,.79,.67))
n=fabric.node_tree.nodes; l=fabric.node_tree.links
p=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexCoord')
sep=n.new('ShaderNodeSeparateXYZ'); l.new(tex.outputs['Generated'],sep.inputs[0])
wave=n.new('ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='Y'
wave.inputs['Scale'].default_value=28
wave.inputs['Distortion'].default_value=.3
l.new(tex.outputs['Generated'],wave.inputs['Vector'])
r=n.new('ShaderNodeValToRGB')
r.color_ramp.elements.remove(r.color_ramp.elements[1])
for pos,col in [(0,(.78,.72,.61,1)),(.36,(.89,.84,.73,1)),
                (.78,(.88,.83,.72,1)),(.86,(.64,.43,.40,1)),(.91,(.87,.81,.69,1))]:
    e=r.color_ramp.elements[0] if pos==0 else r.color_ramp.elements.new(pos)
    e.color=col
l.new(wave.outputs['Fac'],r.inputs[0]); l.new(r.outputs[0],p.inputs['Base Color'])
noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=190
l.new(tex.outputs['Generated'],noise.inputs['Vector'])
bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.17
bump.inputs['Distance'].default_value=.009
l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],p.inputs['Normal'])
plain=material('Pillow warm ivory',(.88,.82,.69))
n=plain.node_tree.nodes; l=plain.node_tree.links
no=n.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value=95
bu=n.new('ShaderNodeBump'); bu.inputs['Strength'].default_value=.23
bu.inputs['Distance'].default_value=.012
l.new(no.outputs['Fac'],bu.inputs['Height'])
l.new(bu.outputs[0],n.get('Principled BSDF').inputs['Normal'])

def parent_obj(name):
    return bpy.data.objects.get(name)

def mesh_obj(name,vertices,faces,mat,parent=None):
    me=bpy.data.meshes.new(name)
    me.from_pydata(vertices,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); sc.collection.objects.link(ob)
    ob.data.materials.append(mat)
    if parent: ob.parent=parent
    return ob

# Extruded solid fabric panels; their broad surfaces remain visible inside rails.
def panel(name,outline,y,thickness):
    verts=[(x,y+dy,z) for dy in [-thickness/2,thickness/2] for x,z in outline]
    N=len(outline)
    faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
    faces += [(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    ob=mesh_obj(name,verts,faces,fabric,parent_obj('chaise'))
    be=ob.modifiers.new('Soft upholstery edges','BEVEL'); be.width=.022; be.segments=3
    ob.modifiers.new('Weighted upholstery normals','WEIGHTED_NORMAL')
    return ob
for y in [-.501,.47]:
    panel('Filled upholstered wing '+str(y),wing_outline,y,.055)

# Head panel curves across the full width behind the pillow.
verts=[]
for dz in [0,1]:
    for x,y,z in head_top:
        verts.append((x+.025,y,.62 if dz==0 else z-.035))
N=len(head_top)
faces=[(i,i+1,N+i+1,N+i) for i in range(N-1)]
head=mesh_obj('Broad upholstered head',verts,faces,fabric,parent_obj('chaise'))
sol=head.modifiers.new('Padded head thickness','SOLIDIFY'); sol.thickness=.09
be=head.modifiers.new('Head softness','BEVEL'); be.width=.035; be.segments=3

# Rounded continuous mattress with a gently domed top and rounded foot end.
verts=[]; faces=[]; count=64
for z,sx,sy in [(.61,.95,.92),(.66,1,1),(.76,.99,.98),(.795,.91,.88)]:
    for i in range(count):
        a=2*math.pi*i/count
        c,s=math.cos(a),math.sin(a)
        x=.005+1.345*sx*math.copysign(abs(c)**.40,c)
        y=.515*sy*math.copysign(abs(s)**.44,s)
        verts.append((x,y,z))
for j in range(3):
    for i in range(count):
        faces.append((j*count+i,j*count+(i+1)%count,
                      (j+1)*count+(i+1)%count,(j+1)*count+i))
faces.append(tuple(range(3*count,4*count)))
faces.append(tuple(range(count-1,-1,-1)))
seat=mesh_obj('Continuous upholstered seat cushion',verts,faces,fabric,parent_obj('chaise'))
for f in seat.data.polygons: f.use_smooth=True
seat.modifiers.new('Cushion weighted normals','WEIGHTED_NORMAL')

def soft_cube(name,loc,size,mat,bevel=.06,rotation=(0,0,0),parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object; ob.name=name
    ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.rotation_euler=rotation
    ob.data.materials.append(mat)
    be=ob.modifiers.new('Rounded sewn edges','BEVEL')
    be.width=bevel; be.segments=5
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: ob.parent=parent
    return ob

pillow=soft_cube('Loose square ivory pillow',(-.99,-.005,1.18),(.26,.75,.73),
                 plain,.115,(0,math.radians(-20),math.radians(-7)),parent_obj('chaise'))
# A narrow seam on the pillow perimeter.
seam_mat=material('Pillow seam',(.77,.70,.57))
curve=bpy.data.curves.new('Pillow piping','CURVE'); curve.dimensions='3D'
curve.bevel_depth=.006; curve.bevel_resolution=2
spline=curve.splines.new('POLY'); spline.points.add(8)
for p,co in zip(spline.points,[(.135,-.29,-.31),(.135,0,-.34),(.135,.29,-.31),
    (.135,.33,0),(.135,.29,.31),(.135,0,.34),(.135,-.29,.31),
    (.135,-.33,0),(.135,-.29,-.31)]):
    p.co=(*co,1)
ob=bpy.data.objects.new('Pillow sewn perimeter',curve); sc.collection.objects.link(ob)
ob.data.materials.append(seam_mat); ob.parent=pillow

labelmat=material('Dark green exhibit label',(.035,.18,.145))
label=soft_cube('Small green label',(.77,.13,.803),(.105,.225,.008),labelmat,.004,
                (0,0,math.radians(-8)),parent_obj('chaise'))
ink=material('Label cream print',(.76,.79,.65))
for i in range(3):
    soft_cube('Label printed stroke '+str(i),(.77,.105+i*.025,.809),
              (.055 if i==0 else .034,.004,.0015),ink,.0005,parent=parent_obj('chaise'))

# Window curtain, mostly cropped along the left border.
curtainmat=material('Curtain soft linen',(.83,.80,.71))
sheer=material('Bright window voile',(.96,.94,.86))
for index,(cx,mat,width) in enumerate([(-2.02,curtainmat,.35),(-2.26,sheer,.30)]):
    vv=[]; ff=[]; steps=24
    for z in [.02,2.9]:
        for i in range(steps+1):
            x=cx+width*(i/steps-.5)
            y=.35+.045*math.cos(i*math.pi*2/4)
            vv.append((x,y,z))
    for i in range(steps):
        ff.append((i,i+1,steps+i+2,steps+i+1))
    ob=mesh_obj('Hanging curtain '+str(index),vv,ff,mat)
    so=ob.modifiers.new('Linen thickness','SOLIDIFY'); so.thickness=.007

# Parquet reads as broad dark wooden regions with fine plank seams.
floor=parent_obj('architecture')
wood=material('Warm dark parquet',(.24,.125,.070),.38)
n=wood.node_tree.nodes; l=wood.node_tree.links; p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
mapping=n.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value[2]=math.radians(45)
mapping.inputs['Scale'].default_value=(1.8,1.8,1.8)
l.new(tc.outputs['Object'],mapping.inputs['Vector'])
brick=n.new('ShaderNodeTexBrick')
brick.inputs['Color1'].default_value=(.22,.105,.057,1)
brick.inputs['Color2'].default_value=(.32,.17,.095,1)
brick.inputs['Mortar'].default_value=(.105,.055,.031,1)
brick.inputs['Scale'].default_value=2.0
brick.inputs['Mortar Size'].default_value=.004
brick.inputs['Brick Width'].default_value=1
brick.inputs['Row Height'].default_value=.19
l.new(mapping.outputs[0],brick.inputs['Vector'])
l.new(brick.outputs['Color'],p.inputs['Base Color'])
b=n.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.16
b.inputs['Distance'].default_value=.006
l.new(brick.outputs['Fac'],b.inputs['Height']); l.new(b.outputs[0],p.inputs['Normal'])
floor_group=bpy.data.objects.get('floor')
if floor_group:
    for ob in floor_group.children_recursive:
        if ob.type=='MESH':
            ob.data.materials.clear(); ob.data.materials.append(wood)

# Cane weave on the cropped chair seat, expressed with a procedural material.
cane=material('Golden woven cane',(.47,.33,.18))
n=cane.node_tree.nodes; l=cane.node_tree.links; p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
w1=n.new('ShaderNodeTexWave'); w1.bands_direction='X'; w1.inputs['Scale'].default_value=42
w2=n.new('ShaderNodeTexWave'); w2.bands_direction='Y'; w2.inputs['Scale'].default_value=42
l.new(tc.outputs['Generated'],w1.inputs['Vector']); l.new(tc.outputs['Generated'],w2.inputs['Vector'])
mul=n.new('ShaderNodeMath'); mul.operation='MULTIPLY'
l.new(w1.outputs[0],mul.inputs[0]); l.new(w2.outputs[0],mul.inputs[1])
r=n.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].color=(.12,.075,.036,1)
r.color_ramp.elements[1].color=(.62,.46,.27,1)
l.new(mul.outputs[0],r.inputs[0]); l.new(r.outputs[0],p.inputs['Base Color'])
soft_cube('Cane woven seat insert',(-1.63,-1.9,.492),(.68,.62,.018),
          cane,.008,parent=parent_obj('foreground_chair'))

set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-3,-1,3.3),power=440,size=2.7,target=(-.4,0,.7),color=(1,.93,.82))
area_emitter((1,-3,4.1),power=105,size=4,target=(0,0,.8),color=(.86,.91,1))
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=.15
