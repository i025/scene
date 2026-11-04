from sceneact import *
import bpy, math

# Reference bounds, normalized from top left:
# Chaise (.035,.24)-(.83,.94), crest (.08,.25), pillow (.20,.30),
# arm dip (.26,.53), toe (.82,.65), right foot (.78,.93).
# Seat edges slope down to the right; broad seat top and near arm are visible.
# Wall fills upper half; curtain at left; cane chair cropped at (0,.80)-(.20,1).
# Pillow overlaps head panel; upholstery overlaps apron; legs overlap parquet.
# Previous execution failed before rendering: use include-slot names for hierarchy lookup.

scene=Scene('Salon')
ivory=(.79,.74,.64)
sage=(.32,.39,.34)
gilt=(.65,.58,.42)

floor=Asset('Floor')
floor.include('surface',box((12,12,.12),center=(0,0,-.07),color=(.23,.115,.065)))
scene.include('floor',floor)

wall=Asset('Paneled wall')
wall.include('plaster',box((9,.16,4.2),center=(0,1.08,2.0),color=(.73,.71,.64)))
wall.include('skirting',box((9,.11,.16),center=(0,.95,.08),color=(.71,.69,.61)))
for i,z in enumerate((.22,.28,1.42,1.49,1.65,1.73,2.08)):
    wall.include('horizontal_'+str(i),box((9,.055,.025),center=(0,.963,z),color=(.80,.78,.70)))
for i,x in enumerate((-2.65,-.08,2.49)):
    wall.include('panel_side_'+str(i),box((.025,.045,1.05),center=(x,.967,.85),color=(.81,.79,.71)))
    wall.include('panel_side_inner_'+str(i),box((.012,.045,1.00),center=(x+.045,.962,.85),color=(.78,.76,.68)))
for i,z in enumerate((.33,1.36)):
    wall.include('panel_edge_'+str(i),box((5.13,.045,.024),center=(-.08,.963,z),color=(.81,.79,.71)))
scene.include('wall',wall)

chaise=Asset('Antique chaise longue')
chaise.include('seat',fillet_box((2.35,.99,.24),radius=.115,center=(0,0,.735),color=ivory))
chaise.include('seat_dome',resized(ball(.5,center=(0,0,.805),color=ivory),(2.27,.94,.14)))

front=[(-1.15,-.51,.65),(-.97,-.53,.58),(-.67,-.53,.55),
       (-.23,-.53,.54),(.19,-.53,.515),(.65,-.51,.50),
       (1.04,-.46,.48),(1.17,-.39,.51)]
for side,sign in [('near',1),('far',-1)]:
    pts=[(x,sign*y,z) for x,y,z in front]
    chaise.include(side+'_apron',sweep_tube(pts,radius=.052,color=sage))
    chaise.include(side+'_apron_gilt',sweep_tube([(x,y-sign*.018,z+.032) for x,y,z in pts],radius=.012,color=gilt))
    chaise.include(side+'_apron_lower',sweep_tube([(x,y,z-.032) for x,y,z in pts],radius=.009,color=gilt))

for ix,x in enumerate((-.96,1.00)):
    for iy,y in enumerate((-.40,.37)):
        s=1 if x>0 else -1
        pts=[(x,y,.54),(x+s*.035,y,.43),(x-s*.025,y,.28),
             (x-s*.075,y-.015,.12),(x-s*.025,y-.035,.055)]
        chaise.include('leg_%s_%s'%(ix,iy),sweep_tube(pts,radius=.033,color=sage))
        chaise.include('leg_gilt_%s_%s'%(ix,iy),sweep_tube([(a,b-.028,c) for a,b,c in pts],radius=.008,color=gilt))

crest=[(-1.15,-.47,1.33),(-1.20,-.40,1.54),(-1.21,-.20,1.64),
       (-1.20,.05,1.65),(-1.18,.29,1.60),(-1.12,.47,1.44)]
chaise.include('head_crest',sweep_tube(crest,radius=.042,color=sage))
chaise.include('head_crest_gilt',sweep_tube([(x+.018,y,z+.025) for x,y,z in crest],radius=.012,color=gilt))
for i,y in enumerate((-.48,.48)):
    pts=[(-.85,y,.57),(-1.09,y,.67),(-1.19,y,1.00),(-1.18,y,1.36)]
    chaise.include('head_post_'+str(i),sweep_tube(pts,radius=.041,color=sage))
    top=[(-1.18,y,1.39),(-1.06,y,1.24),(-.86,y,1.12),
         (-.65,y,1.055),(-.49,y,1.06),(-.47,y,1.12)]
    chaise.include('arm_rail_'+str(i),sweep_tube(top,radius=.034,color=sage))
    chaise.include('arm_gilt_'+str(i),sweep_tube([(x,y-.015,z+.024) for x,y,z in top],radius=.010,color=gilt))
    bottom=[(-1.13,y,.69),(-1.02,y,.61),(-.82,y,.57),(-.62,y,.59),(-.53,y,.74)]
    chaise.include('arm_lower_'+str(i),sweep_tube(bottom,radius=.025,color=sage))

pillow=fillet_box((.24,.72,.65),radius=.095,center=(-.88,.005,1.18),color=(.87,.81,.68))
pillow.turn('y',-17)
chaise.include('pillow',pillow)
label=box((.084,.17,.006),center=(.66,.18,.879),color=(.035,.19,.16))
label.turn('z',-6)
chaise.include('museum_label',label)
scene.include('chaise',chaise)

chair=Asset('Foreground cane chair')
rim=[(-2.03,-1.44,.54),(-1.94,-1.00,.54),(-1.57,-.92,.54),
     (-1.40,-1.02,.54),(-1.42,-1.44,.54),(-2.03,-1.44,.54)]
chair.include('rim',sweep_tube(rim,radius=.043,color=sage))
chair.include('cane',box((.53,.49,.025),center=(-1.73,-1.20,.535),color=(.49,.36,.21)))
for i,x in enumerate((-1.96,-1.48)):
    chair.include('leg_'+str(i),rod(.029,start=(x,-1.05,.02),end=(x,-1.05,.54),color=sage))
scene.include('chair',chair)

curtain=Asset('Curtains')
for i in range(9):
    curtain.include('fold_'+str(i),resized(ball(.5,center=(-2.16+i*.055,.46,1.48),color=(.85,.82,.73)),(.095,.13,3.05)))
curtain.include('window',box((.65,.025,3.4),center=(-2.45,.64,1.7),color=(.97,.97,.94)))
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
    for o in [root]+list(root.children_recursive):
        if o.type=='MESH':
            o.data.materials.clear()
            o.data.materials.append(mat)
            count+=1
    assert count>0

def material(name,color,rough=.65):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    return m

# Shared coordinates keep the small woven motifs continuous over padded components.
reference=bpy.data.objects.new('Fabric coordinate reference',None)
bpy.context.collection.objects.link(reference)
fabric=material('Ivory textile with muted rose dots',ivory)
n=fabric.node_tree.nodes
l=fabric.node_tree.links
p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
tc.object=reference
noise=n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=190
noise.inputs['Detail'].default_value=2
l.new(tc.outputs['Object'],noise.inputs['Vector'])
bump=n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.10
bump.inputs['Distance'].default_value=.005
l.new(noise.outputs['Fac'],bump.inputs['Height'])
l.new(bump.outputs['Normal'],p.inputs['Normal'])
waves=[]
for direction,scale,threshold in [('X',19,.96),('Y',31,.92)]:
    w=n.new('ShaderNodeTexWave')
    w.wave_type='BANDS'
    w.bands_direction=direction
    w.inputs['Scale'].default_value=scale
    w.inputs['Distortion'].default_value=.45
    l.new(tc.outputs['Object'],w.inputs['Vector'])
    cut=n.new('ShaderNodeMath')
    cut.operation='GREATER_THAN'
    cut.inputs[1].default_value=threshold
    l.new(w.outputs['Fac'],cut.inputs[0])
    waves.append(cut)
mul=n.new('ShaderNodeMath')
mul.operation='MULTIPLY'
l.new(waves[0].outputs[0],mul.inputs[0])
l.new(waves[1].outputs[0],mul.inputs[1])
mix=n.new('ShaderNodeMixRGB')
mix.inputs[1].default_value=(.79,.74,.65,1)
mix.inputs[2].default_value=(.49,.28,.28,1)
l.new(mul.outputs[0],mix.inputs[0])
l.new(mix.outputs[0],p.inputs['Base Color'])
assign(group('seat'),fabric)
assign(group('seat_dome'),fabric)

# The parent must be the scene include slot "chaise", not the Asset display name.
parent=group('chaise')
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
    ob.data.materials.append(mat)
    bevel=ob.modifiers.new('Padded edge','BEVEL')
    bevel.width=.022
    bevel.segments=3
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

panel('Padded head surface',[
    (-1.175,-.45,.68),(-1.175,-.46,1.33),
    (-1.175,-.38,1.52),(-1.175,-.19,1.61),
    (-1.175,.05,1.62),(-1.175,.28,1.57),
    (-1.175,.44,1.42),(-1.175,.45,.71)],'x',.055,fabric)
for y in (-.485,.485):
    outline=[(-1.16,y,.70),(-1.17,y,1.36),(-1.05,y,1.22),
             (-.85,y,1.10),(-.64,y,1.03),(-.49,y,1.035),
             (-.53,y,.74),(-.63,y,.58),(-.91,y,.60)]
    panel('Solid upholstered arm '+str(y),outline,'y',.045,fabric)

pillowmat=material('Plain ivory pillow',(.87,.81,.68))
n=pillowmat.node_tree.nodes
l=pillowmat.node_tree.links
p=n.get('Principled BSDF')
nt=n.new('ShaderNodeTexNoise')
nt.inputs['Scale'].default_value=145
bu=n.new('ShaderNodeBump')
bu.inputs['Strength'].default_value=.14
bu.inputs['Distance'].default_value=.007
l.new(nt.outputs['Fac'],bu.inputs['Height'])
l.new(bu.outputs['Normal'],p.inputs['Normal'])
assign(group('pillow'),pillowmat)

fm=material('Polished walnut parquet',(.22,.10,.045),.36)
n=fm.node_tree.nodes
l=fm.node_tree.links
p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
mapping=n.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value[2]=math.radians(42)
l.new(tc.outputs['Object'],mapping.inputs['Vector'])
brick=n.new('ShaderNodeTexBrick')
brick.inputs['Color1'].default_value=(.23,.115,.063,1)
brick.inputs['Color2'].default_value=(.135,.055,.026,1)
brick.inputs['Mortar'].default_value=(.065,.035,.018,1)
brick.inputs['Scale'].default_value=1
brick.inputs['Mortar Size'].default_value=.003
brick.inputs['Brick Width'].default_value=.62
brick.inputs['Row Height'].default_value=.15
l.new(mapping.outputs['Vector'],brick.inputs['Vector'])
l.new(brick.outputs['Color'],p.inputs['Base Color'])
assign(group('floor'),fm)

cm=material('Woven cane',(.48,.32,.17))
n=cm.node_tree.nodes
l=cm.node_tree.links
p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
check=n.new('ShaderNodeTexChecker')
check.inputs['Scale'].default_value=65
check.inputs['Color1'].default_value=(.16,.085,.035,1)
check.inputs['Color2'].default_value=(.58,.42,.24,1)
l.new(tc.outputs['Generated'],check.inputs['Vector'])
l.new(check.outputs['Color'],p.inputs['Base Color'])
assign(group('cane'),cm)

ornament=material('Worn gilt carving',gilt)
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
    cu.materials.append(mat)

for offset in (-.075,0,.075):
    pts=[]
    for i in range(20):
        t=i/19*math.pi*1.8
        r=.043*(1-i/26)
        pts.append((offset+math.cos(t)*r,-.586,.53+math.sin(t)*r))
    detail('Apron floral scroll',pts,.009,ornament)
for offset in (-.05,.0,.05):
    pts=[]
    for i in range(16):
        t=i/15*math.pi*1.8
        r=.028*(1-i/23)
        pts.append((-1.195,offset+math.cos(t)*r,1.65+math.sin(t)*r))
    detail('Crest floral carving',pts,.008,ornament)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.67,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.33
set_view((2.9,-5.5,3.45),(-.04,.05,.92),lens=47)
area_emitter((-3.3,-.1,3.1),power=650,size=2.6,target=(-.3,0,.7),color=(1,.92,.79))
area_emitter((1,-3,3.7),power=160,size=4,target=(0,0,.8),color=(1,.96,.89))
sc.view_settings.view_transform='AgX'
