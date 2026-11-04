import bpy, math, random
from mathutils import Vector
from sceneact import *

random.seed(12)
scene = Scene("French chaise room")

# Inventory: paneled cream wall, left curtain, parquet, green/gilt chaise,
# ivory pillow, green label, and cropped foreground cane chair.
# Reference landmarks estimated by eye: crest (30,100), seat tip (420,246),
# front foot (398,347), and wall/floor junction (450,195).
# Observation: the successful image has stronger diagonal wall and seat edges.
# Hypothesis: excessive camera displacement toward the foot causes this.
# Main correction family: camera azimuth and framing. A more frontal view
# should flatten those edges and expose more of the upholstered head panel.
# Furniture geometry, support contacts, materials and semantic groups are retained.
cream=(.77,.72,.61)
green=(.29,.35,.29)
gold=(.55,.47,.30)
wall=(.69,.66,.57)

def smooth(points,steps=5):
    p=[Vector(points[0])]+[Vector(q) for q in points]+[Vector(points[-1])]
    out=[]
    for i in range(1,len(p)-2):
        a,b,c,d=p[i-1:i+3]
        for j in range(steps):
            t=j/steps
            v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+
                  (-a+3*b-3*c+d)*t*t*t)
            q=tuple(v)
            if not out or (Vector(q)-Vector(out[-1])).length>1e-7:
                out.append(q)
    q=tuple(p[-2])
    if (Vector(q)-Vector(out[-1])).length>1e-7:
        out.append(q)
    return out

def rail(parent,name,points,radius,color):
    return parent.include(name,sweep_tube(points=points,radius=radius,color=color))

# architecture maps to the room shell, panel mouldings and pilaster.
room=scene.include("architecture",Asset("architecture"))
room.include("floor_base",box((12,12,.10),center=(0,0,-.07),color=(.15,.075,.035)))
room.include("back_wall",box((10,.16,4),center=(0,1.10,2),color=wall))
for i,(z,h,depth) in enumerate([
    (.09,.14,.08),(.20,.045,.055),(1.91,.045,.055),
    (2.02,.06,.07),(2.15,.035,.05)]):
    room.include(f"horizontal_moulding_{i}",
        box((9,depth,h),center=(0,.985-depth/2,z),color=cream))
for k,(xl,xr) in enumerate([(-3,-1.55),(-1.48,1.72),(1.84,3.1)]):
    for j,inset in enumerate([0,.037]):
        xa,xb=xl+inset,xr-inset
        za,zb=.35+inset,1.79-inset
        y=.989-j*.012
        for n,(a,b) in enumerate([
            ((xa,y,za),(xb,y,za)),((xa,y,zb),(xb,y,zb)),
            ((xa,y,za),(xa,y,zb)),((xb,y,za),(xb,y,zb))]):
            rail(room,f"panel_{k}_{j}_{n}",[a,b],.012 if j==0 else .006,cream)
for i,x in enumerate([-.97,.47]):
    room.include(f"wall_joint_{i}",
        box((.006,.008,2.8),center=(x,1.009,1.4),color=(.40,.37,.30)))
room.include("right_pilaster",
    box((.40,.43,3.4),center=(2.22,.91,1.7),color=(.76,.75,.67)))
for i,x in enumerate([2.07,2.35]):
    room.include(f"pilaster_trim_{i}",
        box((.018,.022,2.9),center=(x,.682,1.6),color=cream))

# chaise maps to the complete movable frame and all attached upholstery.
chaise=scene.include("chaise",Asset("chaise"))
chaise.include("seat_support",
    fillet_box((2.49,1.00,.15),radius=.07,center=(.10,0,.585),color=green))
front=[]
for i in range(29):
    x=-1.11+2.48*i/28
    z=.505-.035*math.cos((x-.10)*math.pi/1.25)
    front.append((x,-.515,z))
rail(chaise,"front_apron_lower",front,.045,green)
rail(chaise,"front_apron_gold",[(x,y-.026,z-.025) for x,y,z in front],.009,gold)
rail(chaise,"front_top_edge",
    [(-1.12,-.515,.665),(1.25,-.515,.665),(1.38,-.42,.62)],.025,gold)
rail(chaise,"back_under_edge",
    [(-1.12,.49,.58),(1.24,.49,.58),(1.38,.38,.57)],.036,green)
for i,(x,y) in enumerate([(-.99,-.41),(-.99,.39),(1.22,-.39),(1.22,.39)]):
    side=1 if x>0 else -1
    pts=[(x,y,.60),(x+.035*side,y,.44),(x-.055*side,y-.018,.23),
         (x-.025*side,y-.04,.065),(x+.045*side,y-.055,.045)]
    rail(chaise,f"curved_leg_{i}",smooth(pts),.043,green)
    rail(chaise,f"leg_gilt_{i}",smooth([(a,b-.035,c) for a,b,c in pts]),.007,gold)
    chaise.include(f"foot_{i}",ball(.048,center=pts[-1],color=green))

top_end=[(-1.16,-.51,1.16),(-1.23,-.30,1.37),(-1.24,.04,1.56),
         (-1.14,.32,1.62),(-.99,.49,1.52)]
bottom_end=[(-1.06,-.50,.61),(-1.17,-.25,.59),(-1.20,.04,.61),
            (-1.10,.32,.66),(-.98,.49,.73)]
rail(chaise,"end_crest",smooth(top_end),.035,green)
rail(chaise,"end_crest_gilt",
    smooth([(x-.022,y,z+.014) for x,y,z in top_end]),.008,gold)
rail(chaise,"end_base",smooth(bottom_end),.035,green)
rail(chaise,"front_end_post",
    smooth([top_end[0],(-1.10,-.52,1.00),(-1.07,-.51,.79),bottom_end[0]]),.033,green)
rail(chaise,"rear_end_post",
    smooth([top_end[-1],(-1.02,.5,1.20),bottom_end[-1]]),.03,green)
backline=[(-.99,.49,1.52),(-.82,.50,1.38),(-.59,.50,1.24),
          (-.40,.50,1.22),(-.37,.49,1.02),(-.19,.48,.85)]
rail(chaise,"rear_swept_rail",smooth(backline),.033,green)
rail(chaise,"rear_rail_gilt",
    smooth([(x,y-.025,z+.012) for x,y,z in backline]),.008,gold)
for i in range(7):
    x=.10+(i-3)*.037
    z=.49+.035*math.cos((i-3)*.8)
    chaise.include(f"apron_rosette_{i}",ball(.032,center=(x,-.552,z),color=gold))
for side in [-1,1]:
    pts=[]
    for i in range(23):
        t=i/22*math.pi*2
        r=.015+.055*i/22
        pts.append((.10+side*(.12+r*math.cos(t)),-.556,.505+r*.55*math.sin(t)))
    rail(chaise,f"apron_scroll_{side}",pts,.009,gold)
for i in range(6):
    chaise.include(f"crest_leaf_{i}",
        ball(.024,center=(-1.23,.16+i*.047,1.605+.02*math.sin(i)),color=gold))

curtains=scene.include("curtains",Asset("curtains"))
for i in range(12):
    x=-2.02+i*.037
    y=.48+.035*math.sin(i*1.7)
    curtains.include(f"ivory_fold_{i}",
        rod(.033,start=(x,y,.02),end=(x,y,3.3),
            color=(.82+.035*math.sin(i),.78+.03*math.sin(i),.67+.025*math.sin(i))))
curtains.include("window_light",
    box((.5,.05,3.3),center=(-2.16,.72,1.65),color=(.94,.95,.89)))

chair=scene.include("foreground_cane_chair",Asset("foreground_cane_chair"))
chair.include("seat",
    fillet_box((.68,.65,.065),radius=.032,center=(-1.53,-1.43,.46),color=green))
for i,(a,b) in enumerate([
    ((-1.85,-1.75,.50),(-1.20,-1.75,.50)),
    ((-1.85,-1.12,.50),(-1.20,-1.12,.50)),
    ((-1.85,-1.75,.50),(-1.85,-1.12,.50)),
    ((-1.20,-1.75,.50),(-1.20,-1.12,.50))]):
    rail(chair,f"seat_rim_{i}",[a,b],.026,gold)

realize(scene)
root=bpy.data.objects.get("chaise")
chairroot=bpy.data.objects.get("foreground_cane_chair")
roomroot=bpy.data.objects.get("architecture")

def material(name,color,roughness=.7):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=roughness
    return m

def mesh_obj(name,verts,faces,mat,parent=None,smooth_faces=False):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    if parent:
        ob.parent=parent
    if smooth_faces:
        for p in me.polygons:
            p.use_smooth=True
    return ob

# Batched parquet remains attached to architecture.
woodmats=[]
for i in range(8):
    c=.78+i*.063
    m=material(f"parquet tone {i}",(.215*c,.105*c,.049*c),.39)
    n,l=m.node_tree.nodes,m.node_tree.links
    tc=n.new("ShaderNodeTexCoord")
    scale=n.new("ShaderNodeVectorMath")
    scale.operation="MULTIPLY"
    scale.inputs[1].default_value=(7,90,3)
    noise=n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=3
    noise.inputs["Detail"].default_value=2
    bump=n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.13
    bump.inputs["Distance"].default_value=.006
    l.new(tc.outputs["Object"],scale.inputs[0])
    l.new(scale.outputs[0],noise.inputs["Vector"])
    l.new(noise.outputs["Fac"],bump.inputs["Height"])
    l.new(bump.outputs[0],n.get("Principled BSDF").inputs["Normal"])
    woodmats.append(m)
verts,faces,indices=[],[],[]
L,W=.66,.132
ca,sa=math.cos(math.pi/4),math.sin(math.pi/4)
for i in range(-7,8):
    for j in range(-24,25):
        ox,oy=i*L-j*W,i*L+j*W
        for typ in range(2):
            if typ==0:
                x,y,sx,sy=ox+L/2,oy+W/2,L-.006,W-.006
            else:
                x,y,sx,sy=ox+L+W/2,oy+L/2,W-.006,L-.006
            X,Y=ca*x-sa*y,sa*x+ca*y
            if abs(X)>4.8 or abs(Y)>4.8:
                continue
            k=len(verts)
            for dx,dy in [(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)]:
                verts.append((ca*(x+dx)-sa*(y+dy),sa*(x+dx)+ca*(y+dy),.009))
            faces.append((k,k+1,k+2,k+3))
            indices.append(random.randrange(8))
ob=mesh_obj("batched herringbone parquet",verts,faces,None,roomroot)
for m in woodmats:
    ob.data.materials.append(m)
for p,idx in zip(ob.data.polygons,indices):
    p.material_index=idx

upholstery=material("ivory rose striped upholstery",(.82,.76,.65))
n,l=upholstery.node_tree.nodes,upholstery.node_tree.links
bs=n.get("Principled BSDF")
tc=n.new("ShaderNodeTexCoord")
sep=n.new("ShaderNodeSeparateXYZ")
l.new(tc.outputs["Generated"],sep.inputs[0])
mult=n.new("ShaderNodeMath")
mult.operation="MULTIPLY"
mult.inputs[1].default_value=105
l.new(sep.outputs["Y"],mult.inputs[0])
sine=n.new("ShaderNodeMath")
sine.operation="SINE"
l.new(mult.outputs[0],sine.inputs[0])
threshold=n.new("ShaderNodeMath")
threshold.operation="GREATER_THAN"
threshold.inputs[1].default_value=.975
l.new(sine.outputs[0],threshold.inputs[0])
mix=n.new("ShaderNodeMixRGB")
mix.inputs[1].default_value=(.84,.79,.69,1)
mix.inputs[2].default_value=(.53,.31,.29,1)
l.new(threshold.outputs[0],mix.inputs[0])
l.new(mix.outputs[0],bs.inputs["Base Color"])
noise=n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=145
noise.inputs["Detail"].default_value=2
l.new(tc.outputs["Generated"],noise.inputs["Vector"])
bump=n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.17
bump.inputs["Distance"].default_value=.009
l.new(noise.outputs["Fac"],bump.inputs["Height"])
l.new(bump.outputs[0],bs.inputs["Normal"])

pillowmat=material("warm ivory pillow",(.82,.76,.63))
n,l=pillowmat.node_tree.nodes,pillowmat.node_tree.links
noise=n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=110
bump=n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.22
bump.inputs["Distance"].default_value=.012
l.new(noise.outputs["Fac"],bump.inputs["Height"])
l.new(bump.outputs[0],n.get("Principled BSDF").inputs["Normal"])

def spow(a,p):
    return math.copysign(abs(a)**p,a)

def softbox(name,center,radii,mat,exponents=(.34,.45),rotation=(0,0,0)):
    verts,faces=[],[]
    nu,nv=64,24
    for j in range(nv+1):
        v=-math.pi/2+math.pi*j/nv
        for i in range(nu):
            u=math.tau*i/nu
            cv=spow(math.cos(v),exponents[1])
            verts.append((radii[0]*spow(math.cos(u),exponents[0])*cv,
                          radii[1]*spow(math.sin(u),exponents[0])*cv,
                          radii[2]*spow(math.sin(v),exponents[1])))
    for j in range(nv):
        for i in range(nu):
            a,b=j*nu+i,j*nu+(i+1)%nu
            faces.append((a,b,b+nu,a+nu))
    ob=mesh_obj(name,verts,faces,mat,root,True)
    ob.location=center
    ob.rotation_euler=tuple(math.radians(v) for v in rotation)
    return ob

softbox("long upholstered mattress",(.12,0,.735),(1.28,.515,.155),
        upholstery,(.32,.50))
top,bot=smooth(top_end,8),smooth(bottom_end,8)
verts,faces=[],[]
for j in range(13):
    t=j/12
    for a,b in zip(bot,top):
        q=Vector(a).lerp(Vector(b),t)
        q.x-=.035*math.sin(math.pi*t)
        verts.append(tuple(q))
for j in range(12):
    for i in range(len(top)-1):
        a=j*len(top)+i
        faces.append((a,a+1,a+1+len(top),a+len(top)))
ob=mesh_obj("padded curved head end",verts,faces,upholstery,root,True)
sol=ob.modifiers.new("padded shell thickness","SOLIDIFY")
sol.thickness=.045

line=smooth(backline,6)
verts,faces=[],[]
for p in line:
    verts.extend([(p[0],p[1],.77),(p[0],p[1],p[2]-.025)])
for i in range(len(line)-1):
    faces.append((2*i,2*i+2,2*i+3,2*i+1))
ob=mesh_obj("rear upholstered wing",verts,faces,upholstery,root,True)
sol=ob.modifiers.new("wing thickness","SOLIDIFY")
sol.thickness=.05
softbox("loose ivory pillow",(-.77,-.055,1.15),(.14,.345,.355),
        pillowmat,(.35,.45),(0,-18,-7))

def curve_obj(name,pts,radius,mat,parent=root):
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions="3D"
    sp=cu.splines.new("POLY")
    sp.points.add(len(pts)-1)
    for p,q in zip(sp.points,pts):
        p.co=(*q,1)
    cu.bevel_depth=radius
    cu.bevel_resolution=2
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    ob.parent=parent
    return ob

pipingmat=material("ivory piping",(.69,.60,.44))
pts=[]
for i in range(97):
    a=i/96*math.tau
    pts.append((.12+1.28*spow(math.cos(a),.32),
                .515*spow(math.sin(a),.32),.72))
curve_obj("mattress welt",pts,.008,pipingmat)

labelmat=material("dark green label",(.055,.20,.16))
bpy.ops.mesh.primitive_cube_add(size=1,location=(.67,.12,.899))
label=bpy.context.object
label.name="green museum label"
label.dimensions=(.085,.23,.004)
label.rotation_euler[2]=math.radians(-7)
label.data.materials.append(labelmat)
label.parent=root
letter=material("label lettering",(.69,.76,.63))
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.671,.15+i*.019,.903))
    ob=bpy.context.object
    ob.name=f"label lettering {i}"
    ob.dimensions=(.039 if i==0 else .026,.004,.001)
    ob.data.materials.append(letter)
    ob.parent=root

canemat=material("woven cane",(.57,.42,.24))
verts,faces=[],[]
def strip(x1,y1,x2,y2,width,z):
    k=len(verts)
    d=Vector((x2-x1,y2-y1))
    d.normalize()
    px,py=-d.y*width/2,d.x*width/2
    verts.extend([(x1+px,y1+py,z),(x2+px,y2+py,z),
                  (x2-px,y2-py,z),(x1-px,y1-py,z)])
    faces.append((k,k+1,k+2,k+3))
for i in range(27):
    t=i*.021
    strip(-1.81,-1.71+t,-1.24,-1.71+t,.008,.501)
    strip(-1.81+t,-1.71,-1.81+t,-1.16,.008,.504)
mesh_obj("batched woven cane",verts,faces,canemat,chairroot)

# Audit: .07 <= .15/2 and .032 <= .065/2 for both fillet calls.
# Sibling inclusion keys are unique; all radii and segment lengths are positive.
# There are no bind dependencies. Frame, mattress and feet keep their contacts.
# Camera position, target, focal length and shift are independent parameters.
camera_position=(1.05,-5.8,3.90)
camera_target=(.25,0,.95)
camera_lens=58
camera_shift=(0,0)
set_view(camera_position,camera_target,lens=camera_lens,sensor=36,shift=camera_shift)
area_emitter((-3,-.6,3.0),power=450,size=2.4,target=(0,0,.7),color=(1,.94,.82))
area_emitter((1,-3,3.7),power=110,size=3.5,target=(0,0,.8),color=(1,.95,.88))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("World")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.48,.47,.43,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.35
sc.render.engine="CYCLES"
sc.cycles.samples=24
sc.cycles.use_denoising=True
sc.view_settings.view_transform="AgX"
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
