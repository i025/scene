from sceneact import *
import bpy, math, random
from mathutils import Vector

# Image observations (top-left normalized coordinates):
# Chaise: (.035,.24)-(.83,.94); crown (.08,.25), head (.22,.27),
# arm dip (.27,.54), seat toe (.81,.61), front foot (.78,.93).
# Seat long edges slope downward toward the right; its broad top is visible.
# Wall occupies the upper half; floor begins near (.85,.50).
# Cropped cane chair at (0,.80)-(.20,1); curtain at left, behind chaise.
# Occlusion: pillow over head upholstery, seat over frame, frame over legs/floor.

scene = Scene('French salon chaise')
cream=(.77,.72,.60)
wood=(.31,.39,.34)
gold=(.63,.57,.39)

floor=Asset('Parquet floor')
floor.include('floor',box((12,12,.12),center=(0,0,-.08),color=(.23,.115,.065)))
scene.include('floor',floor)
wall=Asset('Ivory paneled wall')
wall.include('wall',box((9,.15,4.2),center=(0,1.05,2),color=(.72,.70,.62)))
wall.include('baseboard',box((9,.09,.17),center=(0,.94,.09),color=(.69,.67,.58)))
for z in (.25,1.48,1.56,1.72,1.81,2.12):
    wall.include('horizontal moulding '+str(z),box((9,.065,.027),center=(0,.939,z),color=(.79,.77,.68)))
for x in (-2.55,.0,2.55):
    wall.include('panel stile '+str(x),box((.025,.045,1.13),center=(x,.954,.865),color=(.80,.78,.70)))
for z in (.35,1.38):
    wall.include('panel border '+str(z),box((4.98,.04,.022),center=(0,.95,z),color=(.81,.79,.70)))
scene.include('wall',wall)

chaise=Asset('Antique upholstered chaise longue')
# Broad cushion, rounded at the foot and slightly swollen on top.
chaise.include('seat cushion',fillet_box((2.35,.99,.25),radius=.115,
                                       center=(.0,0,.72),color=cream))
chaise.include('seat crown',resized(ball(.5,center=(0,0,.80),color=cream),
                                   (2.31,.96,.15)))
# Curved carved rails, sampled only where the silhouette changes.
front=[(-1.15,-.51,.62),(-.91,-.53,.55),(-.62,-.53,.52),
       (-.23,-.53,.515),(.18,-.53,.49),(.62,-.52,.48),
       (1.04,-.47,.46),(1.17,-.40,.48)]
rear=[(x,-y,z) for x,y,z in front]
for label,pts in [('front',front),('rear',rear)]:
    chaise.include(label+' carved apron',sweep_tube(pts,radius=.051,color=wood))
    chaise.include(label+' gilded edge',sweep_tube([(x,y-.009 if label=='front' else y+.009,z+.031) for x,y,z in pts],radius=.012,color=gold))
# Cabriole legs taper and curl out near the floor.
for x in (-.96,1.00):
    for y in (-.40,.37):
        s=1 if x>0 else -1
        pts=[(x,y,.52),(x+s*.035,y,.42),(x-s*.025,y,.28),
             (x-s*.075,y-.015,.12),(x-s*.025,y-.035,.055)]
        chaise.include('cabriole leg '+str((x,y)),sweep_tube(pts,radius=.034,color=wood))
        chaise.include('leg highlight '+str((x,y)),sweep_tube([(a,b-.028,c) for a,b,c in pts],radius=.008,color=gold))
# Head-end frame: transverse crest and two curved uprights.
headcrest=[(-1.15,-.47,1.31),(-1.20,-.40,1.53),(-1.21,-.20,1.63),
           (-1.20,.05,1.64),(-1.18,.29,1.59),(-1.12,.47,1.43)]
chaise.include('head crest',sweep_tube(headcrest,radius=.042,color=wood))
chaise.include('crest highlight',sweep_tube([(x+.015,y,z+.022) for x,y,z in headcrest],radius=.013,color=gold))
for y in (-.48,.48):
    pts=[(-.85,y,.55),(-1.09,y,.65),(-1.19,y,.99),(-1.18,y,1.34)]
    chaise.include('head upright '+str(y),sweep_tube(pts,radius=.043,color=wood))
# Side arm panels descend from the high head to scrolls beside the seat.
for y in (-.49,.49):
    top=[(-1.18,y,1.37),(-1.06,y,1.22),(-.86,y,1.10),
         (-.65,y,1.035),(-.49,y,1.04),(-.47,y,1.11)]
    chaise.include('arm crest '+str(y),sweep_tube(top,radius=.035,color=wood))
    chaise.include('arm piping '+str(y),sweep_tube([(x,y-.01,z+.021) for x,y,z in top],radius=.011,color=gold))
# Pillow, tilted toward the head.
pillow=fillet_box((.22,.70,.66),radius=.09,center=(-.88,.02,1.15),color=(.86,.80,.66))
pillow.turn('y',-17)
chaise.include('loose ivory pillow',pillow)
# Small museum label on the far portion of the cushion.
label=box((.085,.17,.006),center=(.66,.18,.855),color=(.035,.19,.16))
label.turn('z',-6)
chaise.include('green museum label',label)
scene.include('chaise',chaise)

# Cropped cane chair in lower left foreground.
chair=Asset('Cropped foreground cane chair')
rim=[(-2.03,-1.44,.54),(-1.94,-1.00,.54),(-1.57,-.92,.54),
     (-1.40,-1.02,.54),(-1.42,-1.44,.54),(-2.03,-1.44,.54)]
chair.include('seat rim',sweep_tube(rim,radius=.043,color=wood))
chair.include('cane seat',box((.53,.49,.025),center=(-1.73,-1.20,.535),color=(.49,.36,.21)))
for x in (-1.96,-1.48):
    chair.include('chair leg '+str(x),rod(.029,start=(x,-1.05,.02),end=(x,-1.05,.54),color=wood))
scene.include('chair',chair)

curtain=Asset('Window curtains')
for i in range(9):
    x=-2.16+i*.055
    curtain.include('ivory curtain fold '+str(i),
                    resized(ball(.5,center=(x,.46,1.48),color=(.83,.80,.70)),
                            (.095,.13,3.05)))
curtain.include('window glow',box((.65,.025,3.4),center=(-2.45,.64,1.7),color=(.97,.97,.92)))
scene.include('curtain',curtain)

realize(scene)

def group(name):
    ob=bpy.data.objects.get(name)
    if ob: return ob
    return next(o for o in bpy.data.objects if o.type=='EMPTY' and name in o.name)

def meshpart(name,verts,faces,parent,mat):
    m=bpy.data.meshes.new(name)
    m.from_pydata(verts,[],faces); m.update()
    o=bpy.data.objects.new(name,m)
    bpy.context.collection.objects.link(o)
    o.parent=parent
    o.data.materials.append(mat)
    bevel=o.modifiers.new('Soft upholstered edges','BEVEL')
    bevel.width=.025; bevel.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def material(name,color,rough=.65):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    return m

fabric=material('Ivory woven fabric with muted rose sprigs',(.79,.74,.63))
n=fabric.node_tree.nodes;l=fabric.node_tree.links
p=n.get('Principled BSDF')
coord=n.new('ShaderNodeTexCoord')
mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(1,1,1)
l.new(coord.outputs['Object'],mapping.inputs[0])
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=180
noise.inputs['Detail'].default_value=2
l.new(mapping.outputs[0],noise.inputs['Vector'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14
bump.inputs['Distance'].default_value=.009
l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
# Small restrained red woven marks on an orderly ivory ground.
wave=n.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='X'
wave.inputs['Scale'].default_value=19;wave.inputs['Distortion'].default_value=.8
l.new(coord.outputs['Object'],wave.inputs['Vector'])
wave2=n.new('ShaderNodeTexWave');wave2.wave_type='BANDS';wave2.bands_direction='Y'
wave2.inputs['Scale'].default_value=31
l.new(coord.outputs['Object'],wave2.inputs['Vector'])
a=n.new('ShaderNodeMath');a.operation='GREATER_THAN';a.inputs[1].default_value=.96
b=n.new('ShaderNodeMath');b.operation='GREATER_THAN';b.inputs[1].default_value=.91
l.new(wave.outputs['Fac'],a.inputs[0]);l.new(wave2.outputs['Fac'],b.inputs[0])
mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY'
l.new(a.outputs[0],mult.inputs[0]);l.new(b.outputs[0],mult.inputs[1])
mix=n.new('ShaderNodeMixRGB')
mix.inputs[1].default_value=(.79,.735,.63,1)
mix.inputs[2].default_value=(.47,.25,.25,1)
l.new(mult.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Base Color'])

def assign_recursive(root,mat):
    count=0
    for o in [root]+list(root.children_recursive):
        if o.type=='MESH':
            o.data.materials.clear();o.data.materials.append(mat);count+=1
    assert count
for nm in ('seat cushion','seat crown'):
    assign_recursive(group(nm),fabric)

upholstery_parent=group('Antique upholstered chaise longue')
# Solid head panel follows its crest, rather than merely outlining it.
outline=[(-1.175,-.45,.66),(-1.175,-.46,1.31),
         (-1.175,-.38,1.50),(-1.175,-.19,1.59),
         (-1.175,.05,1.60),(-1.175,.28,1.55),
         (-1.175,.44,1.40),(-1.175,.45,.69)]
verts=[(x+d,y,z) for d in (-.025,.025) for x,y,z in outline]
k=len(outline)
faces=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]
faces += [(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
meshpart('Padded head end',verts,faces,upholstery_parent,fabric)
for y in (-.485,.485):
    outline=[(-1.16,.68),(-1.17,1.34),(-1.05,1.20),(-.85,1.08),
             (-.64,1.01),(-.49,1.015),(-.53,.72),(-.63,.56),(-.91,.58)]
    verts=[(x,y+d,z) for d in (-.018,.018) for x,z in outline]
    k=len(outline)
    faces=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]
    faces += [(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
    meshpart('Upholstered curved arm '+str(y),verts,faces,upholstery_parent,fabric)

# Fine parquet material: large brown regions with narrow staggered board seams.
fm=material('Dark polished walnut parquet',(.22,.10,.045),.36)
n=fm.node_tree.nodes;l=fm.node_tree.links;p=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexCoord')
mapping=n.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=math.radians(42)
l.new(tex.outputs['Object'],mapping.inputs['Vector'])
brick=n.new('ShaderNodeTexBrick')
brick.inputs['Color1'].default_value=(.23,.115,.063,1)
brick.inputs['Color2'].default_value=(.135,.055,.026,1)
brick.inputs['Mortar'].default_value=(.065,.035,.018,1)
brick.inputs['Scale'].default_value=1
brick.inputs['Mortar Size'].default_value=.004
brick.inputs['Brick Width'].default_value=.62
brick.inputs['Row Height'].default_value=.15
l.new(mapping.outputs['Vector'],brick.inputs['Vector'])
l.new(brick.outputs['Color'],p.inputs['Base Color'])
assign_recursive(group('Parquet floor'),fm)

# Delicate cane weave, modeled in the material.
cm=material('Woven cane',(.48,.32,.17))
n=cm.node_tree.nodes;l=cm.node_tree.links;p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord')
check=n.new('ShaderNodeTexChecker');check.inputs['Scale'].default_value=65
check.inputs['Color1'].default_value=(.16,.085,.035,1)
check.inputs['Color2'].default_value=(.58,.42,.24,1)
l.new(tc.outputs['Generated'],check.inputs['Vector'])
l.new(check.outputs['Color'],p.inputs['Base Color'])
assign_recursive(group('cane seat'),cm)

# Small scroll ornaments on the visible apron, kept shallow.
ornament=material('Worn gilt carving',(.62,.56,.39))
def curvedetail(name,points,radius,mat):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D'
    cu.bevel_depth=radius;cu.bevel_resolution=2
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob)
    ob.parent=upholstery_parent;ob.data.materials.append(mat)
for offset in (-.075,0,.075):
    pts=[]
    for i in range(20):
        t=i/19*math.pi*1.8
        r=.043*(1-i/26)
        pts.append((offset+math.cos(t)*r,-.586,.50+math.sin(t)*r))
    curvedetail('Apron floral scroll',pts,.009,ornament)

sc=bpy.context.scene
if sc.world is None:sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.67,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.33
set_view((2.9,-5.5,3.45),(-.04,.05,.92),lens=47)
area_emitter((-3.3,-.1,3.1),power=650,size=2.6,target=(-.3,0,.7),color=(1,.92,.79))
area_emitter((1,-3,3.7),power=160,size=4,target=(0,0,.8),color=(1,.96,.89))
sc.view_settings.view_transform='AgX'
