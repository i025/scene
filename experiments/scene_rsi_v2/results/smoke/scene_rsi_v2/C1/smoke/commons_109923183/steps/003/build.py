from sceneact import *
import bpy, math

# Reference bounds, measured from top left:
# chaise (.035,.24)-(.83,.94), crest (.08,.25), pillow (.20,.34),
# arm low point (.27,.54), seat toe (.82,.66), front foot (.78,.93).
# Near seat edge runs approximately (.30,.69) to (.80,.78).
# Wall mouldings rise slightly toward the right; floor is dark walnut.
# Cropped cane chair occupies (0,.80)-(.20,1). Curtains behind head at left.
# Review: previous chaise was too small and centered too far right; floor
# seams were oversized, wall slope excessive, and apron lacked a broad surface.
# Revise framing, wall orientation, apron coverage and shared texture coordinates.

scene=Scene('Salon')
ivory=(.76,.69,.57)
sage=(.27,.34,.29)
gilt=(.61,.53,.36)

floor=Asset('Parquet floor')
floor.include('surface',box((14,14,.12),center=(0,0,-.07),color=(.16,.075,.035)))
scene.include('floor',floor)

wall=Asset('Ivory panelled wall')
wall.include('plaster',box((10,.16,4.5),center=(0,1.20,2.18),color=(.68,.65,.56)))
wall.include('skirting',box((10,.12,.17),center=(0,1.07,.085),color=(.68,.65,.56)))
for i,z in enumerate((.20,.25,1.43,1.48,1.64,1.70,1.94,2.04)):
    wall.include('moulding_'+str(i),box((10,.055,.025),center=(0,1.075,z),color=(.76,.73,.64)))
for i,x in enumerate((-2.25,.30,2.85)):
    for j,dx in enumerate((0,.045)):
        wall.include('panel_stile_%d_%d'%(i,j),
                     box((.018,.055,1.02),center=(x+dx,1.075,.85),color=(.76,.73,.64)))
for i,z in enumerate((.33,.375,1.34,1.385)):
    wall.include('panel_border_'+str(i),box((5.10,.055,.018),center=(.30,1.075,z),color=(.76,.73,.64)))
wall.turn('z',13,pivot=(0,0,0))
scene.include('wall',wall)

# The right edge of the room has a shallow projecting door surround.
door=Asset('Right doorway surround')
door.include('upright',box((.27,.29,3.1),center=(2.30,1.02,1.55),color=(.72,.71,.65)))
door.include('inner_line',box((.018,.025,2.7),center=(2.17,.86,1.55),color=(.60,.59,.53)))
door.turn('z',13,pivot=(0,0,0))
scene.include('door',door)

chaise=Asset('Antique chaise longue')
chaise.include('seat',fillet_box((2.35,1.03,.27),radius=.125,center=(0,0,.755),color=ivory))
chaise.include('seat_crown',resized(ball(.5,center=(0,0,.825),color=ivory),(2.26,.99,.16)))

front=[(-1.15,-.53,.66),(-.98,-.55,.59),(-.68,-.55,.565),
       (-.23,-.55,.55),(.19,-.55,.535),(.65,-.53,.52),
       (1.04,-.48,.50),(1.17,-.40,.53)]
for label,sign in [('near',1),('far',-1)]:
    pts=[(x,y*sign,z) for x,y,z in front]
    chaise.include(label+'_apron',sweep_tube(pts,radius=.035,color=sage))
    chaise.include(label+'_apron_upper_gilt',
                   sweep_tube([(x,y-sign*.012,z+.040) for x,y,z in pts],radius=.010,color=gilt))
    chaise.include(label+'_apron_lower_gilt',
                   sweep_tube([(x,y-sign*.013,z-.042) for x,y,z in pts],radius=.010,color=gilt))

# Curved foot-end frame connects the two long aprons.
toe=[(1.12,-.45,.53),(1.20,-.27,.55),(1.22,0,.56),
     (1.20,.27,.55),(1.12,.45,.53)]
chaise.include('toe_rail',sweep_tube(toe,radius=.041,color=sage))
chaise.include('toe_gilt',sweep_tube([(x+.018,y,z+.023) for x,y,z in toe],radius=.011,color=gilt))

for ix,x in enumerate((-.97,1.02)):
    for iy,y in enumerate((-.43,.40)):
        s=1 if x>0 else -1
        pts=[(x,y,.56),(x+s*.035,y,.44),(x-s*.025,y,.29),
             (x-s*.075,y-.015,.12),(x-s*.025,y-.035,.045)]
        chaise.include('leg_%d_%d'%(ix,iy),sweep_tube(pts,radius=.035,color=sage))
        chaise.include('leg_gilt_%d_%d'%(ix,iy),
                       sweep_tube([(a,b-.030,c) for a,b,c in pts],radius=.008,color=gilt))

crest=[(-1.15,-.49,1.35),(-1.20,-.41,1.55),(-1.21,-.21,1.65),
       (-1.20,.05,1.66),(-1.18,.30,1.61),(-1.12,.49,1.45)]
chaise.include('head_crest',sweep_tube(crest,radius=.038,color=sage))
chaise.include('head_crest_gilt',
               sweep_tube([(x+.018,y,z+.020) for x,y,z in crest],radius=.011,color=gilt))
for i,y in enumerate((-.50,.50)):
    pts=[(-.85,y,.58),(-1.09,y,.68),(-1.19,y,1.01),(-1.18,y,1.37)]
    chaise.include('head_post_'+str(i),sweep_tube(pts,radius=.038,color=sage))
    top=[(-1.18,y,1.40),(-1.06,y,1.25),(-.86,y,1.13),
         (-.65,y,1.065),(-.49,y,1.07),(-.47,y,1.13)]
    chaise.include('arm_rail_'+str(i),sweep_tube(top,radius=.031,color=sage))
    chaise.include('arm_gilt_'+str(i),
                   sweep_tube([(x,y-.015,z+.020) for x,y,z in top],radius=.009,color=gilt))
    bottom=[(-1.13,y,.71),(-1.02,y,.63),(-.82,y,.59),(-.62,y,.61),(-.53,y,.76)]
    chaise.include('arm_lower_'+str(i),sweep_tube(bottom,radius=.025,color=sage))
    chaise.include('arm_lower_gilt_'+str(i),
                   sweep_tube([(x,y-.018,z+.017) for x,y,z in bottom],radius=.008,color=gilt))

pillow=fillet_box((.25,.74,.65),radius=.095,center=(-.87,-.005,1.20),color=(.82,.74,.59))
pillow.turn('y',-19)
pillow.turn('x',-8)
chaise.include('pillow',pillow)
label=box((.082,.16,.008),center=(.66,.18,.913),color=(.025,.15,.115))
label.turn('z',-6)
chaise.include('museum_label',label)
scene.include('chaise',chaise)

chair=Asset('Cropped foreground cane chair')
rim=[(-1.83,-2.08,.54),(-1.84,-1.48,.54),(-1.32,-1.42,.54),
     (-1.18,-1.55,.54),(-1.20,-2.08,.54),(-1.83,-2.08,.54)]
chair.include('rim',sweep_tube(rim,radius=.042,color=sage))
chair.include('rim_gilt',sweep_tube([(x,y,z+.027) for x,y,z in rim],radius=.012,color=gilt))
chair.include('cane',box((.53,.58,.023),center=(-1.52,-1.75,.535),color=(.42,.29,.16)))
for i,x in enumerate((-1.76,-1.25)):
    chair.include('leg_'+str(i),rod(.030,start=(x,-1.55,.02),end=(x,-1.55,.54),color=sage))
scene.include('chair',chair)

curtain=Asset('Left curtains')
for i in range(8):
    curtain.include('fold_'+str(i),
                    resized(ball(.5,center=(-1.70+i*.041,.42,1.64),color=(.79,.75,.64)),
                            (.075,.12,3.40)))
curtain.include('window',box((.54,.025,3.6),center=(-1.91,.60,1.8),color=(.96,.96,.91)))
scene.include('curtain',curtain)

realize(scene)

def group(slot):
    ob=bpy.data.objects.get(slot)
    if ob is not None:
        return ob
    candidates=[o for o in bpy.data.objects if o.type=='EMPTY' and
                (o.name.split('/')[-1]==slot or o.name.endswith('.'+slot))]
    if not candidates:
        candidates=[o for o in bpy.data.objects if o.type=='EMPTY' and slot in o.name]
    if not candidates:
        raise RuntimeError('Missing semantic include slot: '+slot)
    return min(candidates,key=lambda o:len(o.name))

def assign(root,mat):
    count=0
    for ob in [root]+list(root.children_recursive):
        if ob.type=='MESH':
            ob.data.materials.clear()
            ob.data.materials.append(mat)
            count+=1
    assert count>0

def material(name,color,rough=.65):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    return mat

reference=bpy.data.objects.new('Shared world texture coordinates',None)
bpy.context.collection.objects.link(reference)
fabric=material('Cream woven upholstery with rose motifs',ivory)
n=fabric.node_tree.nodes
l=fabric.node_tree.links
p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
tc.object=reference
noise=n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=220
noise.inputs['Detail'].default_value=2
l.new(tc.outputs['Object'],noise.inputs['Vector'])
bump=n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.13
bump.inputs['Distance'].default_value=.004
l.new(noise.outputs['Fac'],bump.inputs['Height'])
l.new(bump.outputs['Normal'],p.inputs['Normal'])
cuts=[]
for direction,scale,threshold in [('X',12,.94),('Y',20,.89)]:
    wave=n.new('ShaderNodeTexWave')
    wave.wave_type='BANDS'
    wave.bands_direction=direction
    wave.inputs['Scale'].default_value=scale
    wave.inputs['Distortion'].default_value=.35
    l.new(tc.outputs['Object'],wave.inputs['Vector'])
    cut=n.new('ShaderNodeMath')
    cut.operation='GREATER_THAN'
    cut.inputs[1].default_value=threshold
    l.new(wave.outputs['Fac'],cut.inputs[0])
    cuts.append(cut)
mul=n.new('ShaderNodeMath')
mul.operation='MULTIPLY'
l.new(cuts[0].outputs[0],mul.inputs[0])
l.new(cuts[1].outputs[0],mul.inputs[1])
mix=n.new('ShaderNodeMixRGB')
mix.inputs[1].default_value=(.77,.705,.605,1)
mix.inputs[2].default_value=(.43,.20,.20,1)
l.new(mul.outputs[0],mix.inputs[0])
l.new(mix.outputs[0],p.inputs['Base Color'])
assign(group('seat'),fabric)
assign(group('seat_crown'),fabric)

parent=group('chaise')
woodmat=material('Aged sage painted wood',sage)
giltmat=material('Worn warm gilt',gilt)

def panel(name,outline,axis,thickness,mat):
    if axis=='x':
        verts=[(x+d,y,z) for d in (-thickness/2,thickness/2) for x,y,z in outline]
    else:
        verts=[(x,y+d,z) for d in (-thickness/2,thickness/2) for x,y,z in outline]
    k=len(outline)
    faces=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]
    faces.extend((i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.parent=parent
    ob.matrix_parent_inverse=parent.matrix_world.inverted()
    ob.data.materials.append(mat)
    bevel=ob.modifiers.new('Soft edge','BEVEL')
    bevel.width=.016
    bevel.segments=3
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

panel('Padded head surface',[
    (-1.175,-.47,.70),(-1.175,-.48,1.35),
    (-1.175,-.39,1.53),(-1.175,-.20,1.62),
    (-1.175,.05,1.63),(-1.175,.29,1.58),
    (-1.175,.46,1.43),(-1.175,.47,.73)],'x',.055,fabric)
for y in (-.50,.50):
    outline=[(-1.16,y,.72),(-1.17,y,1.38),(-1.05,y,1.24),
             (-.85,y,1.12),(-.64,y,1.05),(-.49,y,1.055),
             (-.53,y,.76),(-.63,y,.60),(-.91,y,.62)]
    panel('Solid upholstered arm '+str(y),outline,'y',.045,fabric)

for side,sign in [('near',1),('far',-1)]:
    top=[(x,y*sign,z+.034) for x,y,z in front]
    lower=[(x,y*sign,z-.041) for x,y,z in reversed(front)]
    panel('Broad carved apron '+side,top+lower,'y',.035,woodmat)

pillowmat=material('Warm ivory loose pillow',(.83,.75,.60))
n=pillowmat.node_tree.nodes
l=pillowmat.node_tree.links
p=n.get('Principled BSDF')
nt=n.new('ShaderNodeTexNoise')
nt.inputs['Scale'].default_value=145
bu=n.new('ShaderNodeBump')
bu.inputs['Strength'].default_value=.18
bu.inputs['Distance'].default_value=.009
l.new(nt.outputs['Fac'],bu.inputs['Height'])
l.new(bu.outputs['Normal'],p.inputs['Normal'])
assign(group('pillow'),pillowmat)

fm=material('Dark walnut parquet',(.14,.06,.026),.31)
n=fm.node_tree.nodes
l=fm.node_tree.links
p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
tc.object=reference
mapping=n.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value[2]=math.radians(42)
l.new(tc.outputs['Object'],mapping.inputs['Vector'])
brick=n.new('ShaderNodeTexBrick')
brick.inputs['Color1'].default_value=(.145,.062,.028,1)
brick.inputs['Color2'].default_value=(.085,.031,.018,1)
brick.inputs['Mortar'].default_value=(.055,.026,.015,1)
brick.inputs['Scale'].default_value=1
brick.inputs['Mortar Size'].default_value=.0014
brick.inputs['Brick Width'].default_value=.60
brick.inputs['Row Height'].default_value=.14
l.new(mapping.outputs['Vector'],brick.inputs['Vector'])
grain=n.new('ShaderNodeTexNoise')
grain.inputs['Scale'].default_value=4
grain.inputs['Detail'].default_value=3
stretch=n.new('ShaderNodeVectorMath')
stretch.operation='MULTIPLY'
stretch.inputs[1].default_value=(3,65,2)
l.new(mapping.outputs['Vector'],stretch.inputs[0])
l.new(stretch.outputs[0],grain.inputs['Vector'])
mix=n.new('ShaderNodeMixRGB')
mix.blend_type='MULTIPLY'
mix.inputs[0].default_value=.20
l.new(brick.outputs['Color'],mix.inputs[1])
l.new(grain.outputs['Fac'],mix.inputs[2])
l.new(mix.outputs[0],p.inputs['Base Color'])
assign(group('floor'),fm)

cm=material('Fine woven cane',(.43,.29,.15))
n=cm.node_tree.nodes
l=cm.node_tree.links
p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
tc.object=reference
check=n.new('ShaderNodeTexChecker')
check.inputs['Scale'].default_value=120
check.inputs['Color1'].default_value=(.10,.052,.022,1)
check.inputs['Color2'].default_value=(.49,.33,.18,1)
l.new(tc.outputs['Object'],check.inputs['Vector'])
l.new(check.outputs['Color'],p.inputs['Base Color'])
assign(group('cane'),cm)

def detail(name,points,radius,mat):
    cu=bpy.data.curves.new(name,'CURVE')
    cu.dimensions='3D'
    cu.bevel_depth=radius
    cu.bevel_resolution=2
    sp=cu.splines.new('POLY')
    sp.points.add(len(points)-1)
    for point,co in zip(sp.points,points):
        point.co=(*co,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    ob.parent=parent
    ob.matrix_parent_inverse=parent.matrix_world.inverted()
    cu.materials.append(mat)

for offset in (-.10,-.05,0,.05,.10):
    points=[]
    for i in range(22):
        t=i/21*math.pi*1.85
        r=.047*(1-i/30)
        points.append((offset+math.cos(t)*r,-.587,.55+math.sin(t)*r))
    detail('Carved apron rosette',points,.008,giltmat)
for offset in (-.06,0,.06):
    points=[]
    for i in range(18):
        t=i/17*math.pi*1.8
        r=.032*(1-i/25)
        points.append((-1.19,offset+math.cos(t)*r,1.67+math.sin(t)*r))
    detail('Crest carving',points,.008,giltmat)

# A tiny pale mark gives the museum card its printed appearance.
detail('Museum card printing',[(.646,.155,.920),(.674,.155,.920)],.002,
       material('Card lettering',(.66,.72,.59)))

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.58,.62,.68,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.24
set_view((1.18,-5.65,4.02),(.18,.04,.98),lens=62)
area_emitter((-3.0,-.3,3.2),power=470,size=2.4,
             target=(-.3,0,.7),color=(1,.93,.83))
area_emitter((1,-3,4.0),power=95,size=4,
             target=(0,0,.8),color=(1,.96,.89))
sc.view_settings.view_transform='AgX'
