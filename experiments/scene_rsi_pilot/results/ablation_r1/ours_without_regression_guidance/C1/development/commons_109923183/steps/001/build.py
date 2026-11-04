import bpy, math, random
from mathutils import Vector
from sceneact import *

random.seed(12)
scene = Scene("French chaise room")

# Observations: ivory striped chaise, tall curved left end, green and gilt
# carved frame, four curved feet, loose pillow, green label, paneled wall,
# left curtain, dark parquet, and a cropped cane chair at lower left.
# Camera assumptions: elevated view from the front and foot of the chaise;
# absolute scale is arbitrary. Long furniture axis is world X.

cream = (.77, .72, .61)
wallcolor = (.69, .66, .57)
green = (.29, .35, .29)
gold = (.55, .47, .30)
fabriccolor = (.83, .77, .65)

room = scene.include("architecture", Asset("architecture"))
room.include("floor_base", box((12,12,.10), center=(0,0,-.07), color=(.15,.075,.035)))
room.include("back_wall", box((10,.16,4), center=(0,1.10,2), color=wallcolor))

def rail(asset, name, pts, radius, color):
    return asset.include(name, sweep_tube(points=pts, radius=radius, color=color))

def smooth(points, steps=8):
    p = [Vector(points[0])] + [Vector(q) for q in points] + [Vector(points[-1])]
    out = []
    for i in range(1,len(p)-2):
        a,b,c,d = p[i-1:i+3]
        for j in range(steps):
            t=j/steps
            v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            out.append(tuple(v))
    out.append(tuple(p[-2]))
    return out

# Architecture builder: layered, shallow wall mouldings and a right pilaster.
for i,(z,h,depth) in enumerate([(0.09,.14,.08),(.20,.045,.055),(1.91,.045,.055),(2.02,.06,.07),(2.15,.035,.05)]):
    room.include(f"horizontal_moulding_{i}", box((9,depth,h), center=(0,.985-depth/2,z), color=cream))
for k,(xl,xr) in enumerate([(-3,-1.55),(-1.48,1.72),(1.84,3.1)]):
    for j,inset in enumerate([0,.037]):
        xa,xb=xl+inset,xr-inset
        za,zb=.35+inset,1.79-inset
        y=.989-j*.012
        for n,pts in enumerate([
            [(xa,y,za),(xb,y,za)],[(xa,y,zb),(xb,y,zb)],
            [(xa,y,za),(xa,y,zb)],[(xb,y,za),(xb,y,zb)]
        ]):
            rail(room,f"panel_{k}_{j}_{n}",pts,.012 if j==0 else .006,cream)
for i,x in enumerate([-.97,.47]):
    room.include(f"wall_joint_{i}", box((.006,.008,2.8), center=(x,1.009,1.4), color=(.40,.37,.30)))
room.include("right_pilaster",box((.40,.43,3.4),center=(2.22,.91,1.7),color=(.76,.75,.67)))
for i,x in enumerate([2.07,2.35]):
    room.include(f"pilaster_trim_{i}",box((.018,.022,2.9),center=(x,.682,1.6),color=cream))

# Parquet builder: bounded herringbone mesh tiles with slight color variation.
floor = scene.include("parquet", Asset("parquet"))
L,W=.66,.132
ang=math.radians(45)
def rotxy(x,y):
    return (math.cos(ang)*x-math.sin(ang)*y, math.sin(ang)*x+math.cos(ang)*y)
for i in range(-8,9):
    for j in range(-17,18):
        ox=i*L-j*W
        oy=i*L+j*W
        for typ in range(2):
            if typ==0:
                x,y=ox+L/2,oy+W/2
                sx,sy=L-.006,W-.006
            else:
                x,y=ox+L+W/2,oy+L/2
                sx,sy=W-.006,L-.006
            X,Y=rotxy(x,y)
            if abs(X)>4.6 or abs(Y)>4.6:
                continue
            c=random.uniform(.78,1.22)
            p=box((sx,sy,.025),center=(X,Y,-.006),
                  color=(.215*c,.105*c,.049*c))
            p.turn("z",45,pivot=(X,Y,-.006))
            floor.include(f"plank_{i}_{j}_{typ}",p)

chaise=scene.include("chaise",Asset("chaise"))
# Frame builder: cushion support, sculpted apron, continuous gilt edging.
chaise.include("seat_support",fillet_box((2.49,1.00,.15),radius=.07,
               center=(.10,0,.585),color=green))

front=[]
for i in range(45):
    x=-1.11+2.48*i/44
    z=.505-.035*math.cos((x-.10)*math.pi/1.25)
    front.append((x,-.515,z))
rail(chaise,"front_apron_lower",smooth(front,2),.045,green)
rail(chaise,"front_apron_gold",[(x,y-.026,z-.025) for x,y,z in front],.009,gold)
rail(chaise,"front_top_edge",[(-1.12,-.515,.665),(1.25,-.515,.665),(1.38,-.42,.62)],.025,gold)
rail(chaise,"back_under_edge",[(-1.12,.49,.58),(1.24,.49,.58),(1.38,.38,.57)],.036,green)

for index,(x,y) in enumerate([(-.99,-.41),(-.99,.39),(1.22,-.39),(1.22,.39)]):
    side=1 if x>0 else -1
    pts=[(x,y,.60),(x+.035*side,y,.44),(x-.055*side,y-.018,.23),
         (x-.025*side,y-.04,.065),(x+.045*side,y-.055,.045)]
    rail(chaise,f"curved_leg_{index}",smooth(pts,7),.043,green)
    rail(chaise,f"leg_gilt_{index}",smooth([(a,b-.035,c) for a,b,c in pts],7),.007,gold)
    chaise.include(f"foot_{index}",ball(.048,center=pts[-1],color=green))

# End shell outline: high rear crest, scooped front arm, and bowed lower panel.
top_end=[(-1.16,-.51,1.16),(-1.23,-.30,1.37),(-1.24,.04,1.56),
         (-1.14,.32,1.62),(-.99,.49,1.52)]
bottom_end=[(-1.06,-.50,.61),(-1.17,-.25,.59),(-1.20,.04,.61),
            (-1.10,.32,.66),(-.98,.49,.73)]
rail(chaise,"end_crest",smooth(top_end,10),.035,green)
rail(chaise,"end_crest_gilt",smooth([(x-.022,y,z+.014) for x,y,z in top_end],10),.008,gold)
rail(chaise,"end_base",smooth(bottom_end,10),.035,green)
rail(chaise,"front_end_post",smooth([top_end[0],(-1.10,-.52,1.00),(-1.07,-.51,.79),bottom_end[0]],10),.033,green)
rail(chaise,"rear_end_post",smooth([top_end[-1],(-1.02,.5,1.20),bottom_end[-1]],10),.03,green)
backline=[(-.99,.49,1.52),(-.82,.50,1.38),(-.59,.50,1.24),
          (-.40,.50,1.22),(-.37,.49,1.02),(-.19,.48,.85)]
rail(chaise,"rear_swept_rail",smooth(backline,10),.033,green)
rail(chaise,"rear_rail_gilt",smooth([(x,y-.025,z+.012) for x,y,z in backline],10),.008,gold)

# Small, economical carved ornaments on the frame.
for i in range(7):
    x=.10+(i-3)*.037
    z=.49+.035*math.cos((i-3)*.8)
    chaise.include(f"apron_rosette_{i}",ball(.032,center=(x,-.552,z),color=gold))
for side in [-1,1]:
    pts=[]
    for i in range(30):
        t=i/29*math.pi*2
        r=.015+.055*i/29
        pts.append((.10+side*(.12+r*math.cos(t)),-.556,.505+r*.55*math.sin(t)))
    rail(chaise,f"apron_scroll_{side}",pts,.009,gold)
for i in range(6):
    y=.16+i*.047
    chaise.include(f"crest_leaf_{i}",ball(.024,center=(-1.23,y,1.605+ .02*math.sin(i)),color=gold))

# Peripheral furniture and curtains are included before textile detail.
curtains=scene.include("curtains",Asset("curtains"))
for i in range(12):
    x=-2.02+i*.037
    y=.48+.035*math.sin(i*1.7)
    curtains.include(f"ivory_fold_{i}",rod(.033,start=(x,y,.02),end=(x,y,3.3),
                       color=(.82+.035*math.sin(i),.78+.03*math.sin(i),.67+.025*math.sin(i))))
curtains.include("window_light",box((.5,.05,3.3),center=(-2.16,.72,1.65),color=(.94,.95,.89)))

chair=scene.include("foreground_cane_chair",Asset("foreground_cane_chair"))
chair.include("seat",fillet_box((.68,.65,.065),radius=.032,center=(-1.53,-1.43,.46),color=green))
for i,(a,b) in enumerate([
    ((-1.85,-1.75,.50),(-1.20,-1.75,.50)),
    ((-1.85,-1.12,.50),(-1.20,-1.12,.50)),
    ((-1.85,-1.75,.50),(-1.85,-1.12,.50)),
    ((-1.20,-1.75,.50),(-1.20,-1.12,.50))
]):
    rail(chair,f"seat_rim_{i}",[a,b],.026,gold)
for i in range(27):
    t=i*.021
    rail(chair,f"cane_x_{i}",[(-1.81,-1.71+t,.50),(-1.24,-1.71+t,.50)],.0045,(.54,.39,.21))
    rail(chair,f"cane_y_{i}",[(-1.81+t,-1.71,.502),(-1.81+t,-1.16,.502)],.0045,(.62,.48,.28))

realize(scene)

# Mesh upholstery is parented to the semantic chaise marker.
root=bpy.data.objects.get("chaise")
def material(name,color,roughness=.7):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=roughness
    return m

upholstery=material("woven ivory with faded rose pinstripes",(.82,.76,.65))
n=upholstery.node_tree.nodes
l=upholstery.node_tree.links
bs=n.get("Principled BSDF")
tex=n.new("ShaderNodeTexCoord")
sep=n.new("ShaderNodeSeparateXYZ")
l.new(tex.outputs["Generated"],sep.inputs[0])
mult=n.new("ShaderNodeMath");mult.operation="MULTIPLY";mult.inputs[1].default_value=105
l.new(sep.outputs["Y"],mult.inputs[0])
sine=n.new("ShaderNodeMath");sine.operation="SINE";l.new(mult.outputs[0],sine.inputs[0])
threshold=n.new("ShaderNodeMath");threshold.operation="GREATER_THAN";threshold.inputs[1].default_value=.975
l.new(sine.outputs[0],threshold.inputs[0])
noise=n.new("ShaderNodeTexNoise");noise.inputs["Scale"].default_value=145
noise.inputs["Detail"].default_value=2
l.new(tex.outputs["Generated"],noise.inputs["Vector"])
mix=n.new("ShaderNodeMixRGB")
mix.inputs[1].default_value=(.84,.79,.69,1)
mix.inputs[2].default_value=(.53,.31,.29,1)
l.new(threshold.outputs[0],mix.inputs[0])
l.new(mix.outputs[0],bs.inputs["Base Color"])
bump=n.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.17;bump.inputs["Distance"].default_value=.009
l.new(noise.outputs["Fac"],bump.inputs["Height"]);l.new(bump.outputs[0],bs.inputs["Normal"])

pillowmat=material("pillow warm ivory",(.82,.76,.63))
pn=pillowmat.node_tree.nodes;pl=pillowmat.node_tree.links
noise2=pn.new("ShaderNodeTexNoise");noise2.inputs["Scale"].default_value=110
bump2=pn.new("ShaderNodeBump");bump2.inputs["Strength"].default_value=.22;bump2.inputs["Distance"].default_value=.012
pl.new(noise2.outputs["Fac"],bump2.inputs["Height"])
pl.new(bump2.outputs[0],pn.get("Principled BSDF").inputs["Normal"])

def mesh_obj(name,verts,faces,mat,parent=root):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    if parent:ob.parent=parent
    for p in mesh.polygons:p.use_smooth=True
    return ob

def spow(a,p):
    return math.copysign(abs(a)**p,a)

def softbox(name,center,radii,mat,exponents=(.34,.45),rotation=(0,0,0)):
    verts=[];faces=[]
    nu,nv=96,40
    for j in range(nv+1):
        v=-math.pi/2+math.pi*j/nv
        for i in range(nu):
            u=2*math.pi*i/nu
            cv=spow(math.cos(v),exponents[1])
            verts.append((radii[0]*spow(math.cos(u),exponents[0])*cv,
                          radii[1]*spow(math.sin(u),exponents[0])*cv,
                          radii[2]*spow(math.sin(v),exponents[1])))
    for j in range(nv):
        for i in range(nu):
            a=j*nu+i;b=j*nu+(i+1)%nu
            faces.append((a,b,b+nu,a+nu))
    ob=mesh_obj(name,verts,faces,mat)
    ob.location=center
    ob.rotation_euler=tuple(math.radians(v) for v in rotation)
    return ob

softbox("long upholstered mattress",(.12,0,.735),(1.28,.515,.155),upholstery,(.32,.50))
# End upholstery surface between the bowed base and crest.
top=smooth(top_end,12);bot=smooth(bottom_end,12)
verts=[];faces=[]
for j in range(17):
    t=j/16
    for i in range(len(top)):
        a=Vector(bot[i]);b=Vector(top[i])
        q=a.lerp(b,t)
        q.x-=.035*math.sin(math.pi*t)
        verts.append(tuple(q))
for j in range(16):
    for i in range(len(top)-1):
        a=j*len(top)+i
        faces.append((a,a+1,a+1+len(top),a+len(top)))
ob=mesh_obj("upholstered curved head end",verts,faces,upholstery)
solid=ob.modifiers.new("padded shell thickness","SOLIDIFY");solid.thickness=.045
bev=ob.modifiers.new("soft upholstery edges","BEVEL");bev.width=.025;bev.segments=3

# Low upholstered wing beneath the curved far-side frame.
line=smooth(backline,10)
verts=[];faces=[]
for i,p in enumerate(line):
    verts.extend([(p[0],p[1],.77),(p[0],p[1],p[2]-.025)])
for i in range(len(line)-1):
    faces.append((2*i,2*i+2,2*i+3,2*i+1))
ob=mesh_obj("rear upholstered wing",verts,faces,upholstery)
sol=ob.modifiers.new("wing thickness","SOLIDIFY");sol.thickness=.05
softbox("loose square ivory pillow",(-.77,-.055,1.15),(.14,.345,.355),
        pillowmat,(.35,.45),(0,-18,-7))

# Narrow piping follows the seat perimeter.
def curve_obj(name,pts,radius,mat):
    cu=bpy.data.curves.new(name,"CURVE");cu.dimensions="3D"
    sp=cu.splines.new("POLY");sp.points.add(len(pts)-1)
    for p,q in zip(sp.points,pts):p.co=(*q,1)
    cu.bevel_depth=radius;cu.bevel_resolution=2
    ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat);ob.parent=root
    return ob
pipingmat=material("ivory piping",(.69,.60,.44))
pts=[]
for i in range(161):
    a=i/160*math.tau
    pts.append((.12+1.28*spow(math.cos(a),.32),.515*spow(math.sin(a),.32),.72))
curve_obj("mattress welt",pts,.008,pipingmat)

# Small green museum label on the top of the seat.
labelmat=material("dark green label",(.055,.20,.16))
bpy.ops.mesh.primitive_cube_add(size=1,location=(.67,.12,.899))
label=bpy.context.object;label.name="green museum label"
label.dimensions=(.085,.23,.004);label.rotation_euler[2]=math.radians(-7)
label.data.materials.append(labelmat);label.parent=root
letter=material("label lettering",(.69,.76,.63))
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.671,.15+i*.019,.903))
    o=bpy.context.object;o.name=f"label lettering {i}"
    o.dimensions=(.039 if i==0 else .026,.004,.001)
    o.data.materials.append(letter);o.parent=root

# Gentle wood grain on the parquet, preserving the individual plank colors.
for ob in bpy.data.objects:
    if ob.type=="MESH" and ob.parent and "parquet" in ob.parent.name.lower():
        for old in ob.data.materials:
            old.use_nodes=True
            ns=old.node_tree.nodes;ls=old.node_tree.links
            b=ns.get("Principled BSDF")
            b.inputs["Roughness"].default_value=.36
            no=ns.new("ShaderNodeTexNoise");no.inputs["Scale"].default_value=7;no.inputs["Detail"].default_value=3
            tc=ns.new("ShaderNodeTexCoord")
            mapping=ns.new("ShaderNodeVectorMath");mapping.operation="MULTIPLY"
            mapping.inputs[1].default_value=(3,90,4)
            ls.new(tc.outputs["Generated"],mapping.inputs[0]);ls.new(mapping.outputs[0],no.inputs["Vector"])
            bu=ns.new("ShaderNodeBump");bu.inputs["Strength"].default_value=.12;bu.inputs["Distance"].default_value=.008
            ls.new(no.outputs["Fac"],bu.inputs["Height"]);ls.new(bu.outputs[0],b.inputs["Normal"])

# Audit: every fillet radius is <= half the smallest dimension; sibling keys
# are indexed; no bind cycles or floating support dependencies are used.
# Mattress rests on frame, legs reach floor, pillow intersects its support softly.
set_view((2.6,-5.0,3.8),(0,0,.95),lens=61,sensor=36)
area_emitter((-3,-.6,3.0),power=450,size=2.4,target=(0,0,.7),color=(1,.94,.82))
area_emitter((1,-3,3.7),power=110,size=3.5,target=(0,0,.8),color=(1,.95,.88))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("World")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.48,.47,.43,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.35
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.view_settings.view_transform="AgX"
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
