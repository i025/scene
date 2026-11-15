from sceneact import *
import bpy, math, random
random.seed(11)
scene = Scene('Warm living room')
wall = (0.76,0.74,0.71)
cream = (0.93,0.91,0.86)
dark = (0.055,0.037,0.028)
scene.include('Warm plaster wall', box((12,.16,5), center=(0,1.15,2.45), color=wall))
scene.include('Grey carpet', box((12,10,.10), center=(0,-2,-.08), color=(.32,.31,.30)))

couch = Asset('Caramel upholstered sofa')
couch.include('Lower upholstered base', fillet_box((4.8,.96,.55), .12, center=(0,.25,.34), color=(.64,.32,.105)))
couch.include('Left broad arm', fillet_box((.64,1.12,1.46), .13, center=(-2.18,.19,.79), color=(.61,.30,.085)))
couch.include('Right broad arm', fillet_box((.64,1.12,1.46), .13, center=(2.18,.19,.79), color=(.74,.40,.14)))
for i,x in enumerate((-1.02,1.02)):
    couch.include('Back cushion %d'%i, fillet_box((1.98,.36,1.07), .13, center=(x,.64,1.57), color=(.72+.035*i,.38+.05*i,.12+.025*i)))
    couch.include('Seat cushion %d'%i, fillet_box((1.99,.92,.46), .16, center=(x,-.03,.91), color=(.72+.04*i,.37+.045*i,.12+.025*i)))
    couch.include('Seat front seam %d'%i, sweep_tube([(x-.91,-.515,.84),(x,-.53,.81),(x+.91,-.515,.84)], radius=.009, color=(.52,.26,.08)))
leftp = fillet_box((.80,.23,.79), .11, center=(-1.70,.23,1.60), color=(.88,.57,.27))
leftp.turn('y',-13)
leftp.turn('z',-8)
couch.include('Left loose pillow',leftp)
rightp = fillet_box((.78,.23,.65), .11, center=(1.70,.34,1.55), color=(.86,.57,.29))
rightp.turn('y',12)
rightp.turn('z',7)
couch.include('Right loose pillow',rightp)
scene.include('Sofa',couch)

table = Asset('Dark wood coffee table')
table.include('Thin tabletop', box((3.95,1.47,.095), center=(.72,-1.32,.86), color=dark))
for x in (-1.12,2.56):
    for y in (-1.96,-.68):
        table.include('Leg %.2f %.2f'%(x,y), box((.15,.15,.83), center=(x,y,.415), color=(.035,.025,.020)))
scene.include('Coffee table',table)

for i,x in enumerate((-.23,1.25)):
    n = box((.94,.56,.012), center=(x,-1.39,.916), color=(.59,.68,.63))
    n.turn('z',-7 if i==0 else 6)
    scene.include('Sage napkin %d'%i,n)
    n2 = box((.70,.46,.008), center=(x+.05,-1.38,.925), color=(.75,.70,.69))
    n2.turn('z',7 if i==0 else -8)
    scene.include('Pale napkin layer %d'%i,n2)
    scene.include('Square porcelain saucer %d'%i, fillet_box((.66,.52,.035), .017, center=(x,-1.39,.949), color=cream))
    scene.include('Saucer inset %d'%i, fillet_box((.52,.41,.018), .008, center=(x,-1.39,.974), color=(1,.985,.95)))

scene.include('Flower pot body', fillet_box((.39,.39,.39), .055, center=(.53,-.96,1.13), color=(.16,.17,.16)))
scene.include('Flower pot rim', fillet_box((.43,.43,.065), .032, center=(.53,-.96,1.34), color=(.12,.13,.12)))
scene.include('Dark potting soil', ball(.18,center=(.53,-.96,1.37),color=(.10,.10,.07)))
leafcolors=[(.23,.34,.15),(.32,.43,.20),(.42,.50,.26),(.29,.39,.19)]
for i in range(32):
    a=random.uniform(0,2*math.pi); r=random.uniform(.08,.42)
    z=random.uniform(1.40,1.75)
    end=(.53+math.cos(a)*r,-.96+math.sin(a)*r*.65,z)
    scene.include('Foliage stem %02d'%i,rod(.009,start=(.53,-.96,1.34),end=end,color=(.26,.34,.15)))
    leaf=ball(1,center=end,color=random.choice(leafcolors))
    leaf.resize((random.uniform(.065,.12),.034,random.uniform(.10,.16)))
    leaf.turn('y',random.uniform(-55,55))
    leaf.turn('z',math.degrees(a))
    scene.include('Leaf %02d'%i,leaf)
heads=[(.18,-.98,1.90),(.43,-.89,2.07),(.66,-1.01,1.96),(.94,-.94,1.91),(.58,-.78,1.82)]
for i,(x,y,z) in enumerate(heads):
    scene.include('Flower stalk %d'%i,rod(.012,start=(.53,-.96,1.36),end=(x,y,z),color=(.29,.39,.18)))
    scene.include('Flower core %d'%i,ball(.092,center=(x,y,z),color=(.49,.48,.64)))
    for j in range(20):
        a=j*2.399; zz=1-2*(j+.5)/20; rr=math.sqrt(1-zz*zz)
        p=(x+.105*rr*math.cos(a),y+.105*rr*math.sin(a),z+.105*zz)
        scene.include('Lavender flower %d %d'%(i,j),ball(.032,center=p,color=random.choice([(.62,.61,.75),(.72,.70,.81),(.53,.54,.69)])))

scene.include('Curtain shadow backing',box((.82,.12,2.85),center=(2.72,1.00,2.48),color=(.13,.13,.14)))
for i,(x,w,depth) in enumerate([(2.38,.23,.02),(2.56,.26,-.04),(2.76,.29,.02),(2.98,.26,-.05),(3.16,.23,.01)]):
    fold=fillet_box((w,.16,2.90),.079,center=(x,.89+depth,2.55),color=[(.19,.19,.20),(.27,.27,.28),(.16,.16,.17),(.31,.31,.32),(.17,.17,.18)][i])
    fold.turn('y',(-4,3,-5,5,-2)[i])
    scene.include('Curtain broad fold %d'%i,fold)

realize(scene)

def porcelain(name, location, handle_side):
    x,y,z=location
    n=32
    profile=[(.105,0),(.128,.018),(.143,.12),(.163,.31),(.165,.325),(.145,.325),(.128,.12),(.106,.035),(0,.035)]
    verts=[]
    for r,h in profile:
        for k in range(n):
            a=2*math.pi*k/n
            verts.append((x+r*math.cos(a),y+r*math.sin(a),z+h))
    faces=[]
    for j in range(len(profile)-1):
        for k in range(n):
            a=j*n+k; b=j*n+(k+1)%n
            faces.append((a,b,b+n,a+n))
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    ob=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(ob)
    mat=bpy.data.materials.get('Porcelain')
    if not mat:
        mat=bpy.data.materials.new('Porcelain'); mat.diffuse_color=(.93,.92,.88,1); mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.93,.92,.88,1); bs.inputs['Roughness'].default_value=.22
    ob.data.materials.append(mat)
    for p in mesh.polygons: p.use_smooth=True
    curve=bpy.data.curves.new(name+' handle curve','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.018; curve.bevel_resolution=3; curve.resolution_u=16
    sp=curve.splines.new('BEZIER'); sp.bezier_points.add(3)
    for bp,co in zip(sp.bezier_points,[(x+handle_side*.14,y,z+.25),(x+handle_side*.25,y,z+.27),(x+handle_side*.25,y,z+.16),(x+handle_side*.125,y,z+.09)]):
        bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    ho=bpy.data.objects.new(name+' handle',curve); bpy.context.collection.objects.link(ho); ho.data.materials.append(mat)
porcelain('Left white cup',(-.23,-1.39,.987),-1)
porcelain('Right white cup',(1.25,-1.39,.987),1)

set_view((0,-8.8,3.05),(0,-.1,1.25),lens=47)
area_emitter((3,-1,5.4),power=950,size=4,target=(0,0,1.0),color=(1.0,.87,.72))
area_emitter((-3,-4,3.2),power=310,size=5,target=(0,0,1),color=(.88,.90,1.0))
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new('Soft ambient world'); bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.64,.65,.67,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32