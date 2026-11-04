import bpy
import math
import random
from mathutils import Vector
from sceneact import *

random.seed(8)
scene = Scene("French chaise interior")
cream = (.73, .70, .63)
molding = (.80, .77, .69)
sage = (.30, .37, .32)
gilt = (.64, .59, .45)
linen = (.84, .78, .68)
pillowcol = (.91, .85, .73)

def add(parent, name, obj):
    parent.include(name, obj)
    return obj

add(scene, "parquet floor", box((12, 12, .12), center=(0, 0, -.07),
                               color=(.22, .105, .055)))
wall = Asset("Paneled ivory wall")
add(wall, "plaster", box((10, .16, 4.5), center=(0, 1.32, 2.2), color=cream))
for z, h, d in [(.09,.17,.15),(.21,.045,.10),(.29,.025,.065),
                 (1.77,.025,.055),(1.83,.055,.09),(1.91,.025,.06),
                 (2.12,.025,.05),(2.18,.04,.08),(2.48,.03,.05)]:
    add(wall, "horizontal "+str(z),
        box((10,d,h), center=(0,1.20,z), color=molding))
for k, (left,right) in enumerate([(-4,-1.6),(-1.5,1.65),(1.75,4)]):
    for j, inset in enumerate([0,.035,.065]):
        x0,x1=left+inset,right-inset
        z0,z1=.39+inset,1.67-inset
        thick=[.018,.011,.008][j]
        y=1.218-j*.012
        for x in (x0,x1):
            add(wall,f"panel upright {k} {j} {x}",
                box((thick,.025,z1-z0),center=(x,y,(z0+z1)/2),color=molding))
        for z in (z0,z1):
            add(wall,f"panel cross {k} {j} {z}",
                box((x1-x0,.025,thick),center=((x0+x1)/2,y,z),color=molding))
for x in (-1.55,.15):
    add(wall,"door seam "+str(x),
        box((.008,.009,3.6),center=(x,1.231,1.85),color=(.40,.38,.33)))
add(wall,"right projecting pier",
    box((.34,.40,3.7),center=(2.08,1.15,1.84),color=molding))
add(wall,"pier base",
    box((.42,.46,.18),center=(2.08,1.13,.09),color=molding))
for x in (1.97,2.19):
    add(wall,"pier molding "+str(x),
        box((.016,.025,3.1),center=(x,.937,1.80),color=cream))
add(scene,"wall",wall)

curtain=Asset("Window curtains")
add(curtain,"bright window",
    box((.035,1.65,3.6),center=(-2.05,.20,1.85),color=(.96,.96,.92)))
for k in range(12):
    add(curtain,"vertical curtain fold "+str(k),
        rod(.047,length=3.4,center=(-1.98+.025*math.sin(k*2),-.51+k*.12,1.78),
            color=(.77+.05*math.sin(k),.71+.05*math.sin(k),.59+.04*math.sin(k))))
add(scene,"curtains",curtain)

chaise=Asset("Antique chaise longue")
add(chaise,"upholstered seat",
    fillet_box((2.40,.96,.245),radius=.115,center=(.02,0,.72),color=linen))
add(chaise,"seat lower roll",
    fillet_box((2.29,.89,.10),radius=.045,center=(.01,0,.59),color=linen))
back=fillet_box((.20,.92,.84),radius=.095,
                 center=(-1.20,0,1.14),color=linen)
back.turn('y',-15)
add(chaise,"high upholstered back",back)
for side in (-1,1):
    wing=fillet_box((.69,.10,.48),radius=.045,
                    center=(-.91,side*.445,.875),color=linen)
    wing.turn('y',-18)
    add(chaise,"upholstered wing "+str(side),wing)
pillow=fillet_box((.27,.67,.65),radius=.125,
                 center=(-.99,-.045,1.115),color=pillowcol)
pillow.turn('y',-21)
pillow.turn('z',-7)
add(chaise,"cream loose pillow",pillow)
label=box((.14,.066,.004),center=(.65,.075,.846),color=(.035,.19,.145))
label.turn('z',-8)
add(chaise,"green museum label",label)
for k in range(3):
    add(chaise,"label lettering "+str(k),
        box((.037,.002,.001),center=(.65,.06+k*.012,.849),color=(.74,.80,.69)))

theta=math.radians(-43)
chaise.turn('z',-43,pivot=(0,0,0))
add(scene,"chaise",chaise)

chair=Asset("Partial foreground chair")
cx,cy=-1.85,-1.24
add(chair,"cane seat",fillet_box((.64,.63,.045),radius=.018,
                               center=(cx,cy,.49),color=(.46,.31,.17)))
for x in (cx-.30,cx+.30):
    for y in (cy-.28,cy+.28):
        add(chair,"chair leg "+str((x,y)),
            rod(.027,start=(x,y,.48),end=(x+.035,y,.025),color=sage))
add(scene,"foreground chair",chair)
realize(scene)

def material(name,color,roughness=.7):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=roughness
    return m

sage_mat=material("Worn sage painted wood",sage)
gilt_mat=material("Pale carved edges",gilt)
pipe_mat=material("Linen piping",(.75,.68,.56))
cane_mat=material("Natural cane",(.65,.47,.27))
dark_mat=material("Dark cane holes",(.22,.125,.065))
def transform(p):
    x,y,z=p
    return (x*math.cos(theta)-y*math.sin(theta),
            x*math.sin(theta)+y*math.cos(theta),z)

def curve(name,points,radius,mat,local=True,cyclic=False):
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D'
    data.resolution_u=12
    data.bevel_depth=radius
    data.bevel_resolution=2
    spline=data.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for b,p in zip(spline.bezier_points,points):
        b.co=transform(p) if local else p
        b.handle_left_type='AUTO'
        b.handle_right_type='AUTO'
    spline.use_cyclic_u=cyclic
    ob=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(ob)
    data.materials.append(mat)
    return ob

def outline(z,x0=-1.18,x1=1.21,y0=-.475,y1=.475,r=.15):
    pts=[]
    for x,y,a0 in [(x1-r,y1-r,0),(x0+r,y1-r,90),
                   (x0+r,y0+r,180),(x1-r,y0+r,270)]:
        for j in range(5):
            a=math.radians(a0+j*90/4)
            pts.append((x+r*math.cos(a),y+r*math.sin(a),z))
    return pts

curve("Upper cushion piping",outline(.755),.006,pipe_mat,cyclic=True)
curve("Lower cushion piping",outline(.625),.006,pipe_mat,cyclic=True)
for side in (-1,1):
    y=side*.45
    pts=[(-1.13,y,.58),(-.88,y,.54),(-.55,y,.525),(-.20,y,.52),
         (.14,y,.505),(.47,y,.525),(.86,y,.55),(1.13,y,.56),(1.20,y,.51)]
    curve("Carved seat apron",pts,.044,sage_mat)
    for dz in (-.028,.029):
        curve("Apron edge",[(x,yy+side*.027,z+dz) for x,yy,z in pts],.007,gilt_mat)
    crest=[(-1.29,side*.475,1.34),(-1.18,side*.49,1.18),
           (-1.02,side*.50,1.09),(-.84,side*.50,1.035),
           (-.65,side*.49,1.02),(-.48,side*.47,1.06)]
    lower=[(-1.13,side*.475,.64),(-.98,side*.50,.61),(-.78,side*.50,.61),
           (-.63,side*.48,.65),(-.56,side*.47,.78),(-.48,side*.47,1.06)]
    for name,pts in [("Sweeping arm crest",crest),("Wing lower edge",lower)]:
        curve(name,pts,.029,sage_mat)
        curve(name+" pale detail",[(x,y-side*.019,z+.014) for x,y,z in pts],.007,gilt_mat)
    for end in (-1,1):
        x=-1.02 if end==-1 else 1.08
        y=side*.385
        pts=[(x,y,.56),(x+end*.075,y+side*.04,.46),
             (x+end*.055,y+side*.065,.34),(x+end*.01,y+side*.075,.18),
             (x+end*.06,y+side*.09,.065),(x+end*.115,y+side*.085,.055)]
        curve("Cabriole leg",pts,.032,sage_mat)
        curve("Worn leg edge",[(xx,yy-.027,zz+.003) for xx,yy,zz in pts],.006,gilt_mat)

head=[(-1.12,-.49,.64),(-1.23,-.49,1.05),(-1.32,-.47,1.37),
      (-1.35,-.36,1.49),(-1.36,-.20,1.53),(-1.35,0,1.51),
      (-1.34,.22,1.49),(-1.30,.43,1.36),(-1.23,.49,1.10),(-1.13,.49,.65)]
curve("Carved high back surround",head,.032,sage_mat)
curve("Back inner pale edge",[(x+.02,y*.97,z-.008) for x,y,z in head],.008,gilt_mat)
for side in (-1,1):
    for k in range(4):
        pts=[]
        for j in range(12):
            t=j/11
            pts.append((.10+side*(.025+.22*t),-.496,
                        .505+.028*math.sin(t*math.pi*1.8+k*.4)-k*.009))
        curve("Apron floral carving",pts,.007,gilt_mat)
for j in range(8):
    a=j*math.pi/4
    curve("Rosette petal",[(.10,-.508,.50),
          (.10+.045*math.cos(a),-.516,.50+.041*math.sin(a)),
          (.10+.018*math.cos(a+.7),-.51,.50+.018*math.sin(a+.7))],.009,gilt_mat)

for y in (cy-.34,cy+.34):
    curve("Foreground chair rim",[(cx-.35,y,.51),(cx,y-.01,.51),(cx+.35,y,.51)],
          .03,sage_mat,local=False)
for x in (cx-.35,cx+.35):
    curve("Foreground chair rim",[(x,cy-.34,.51),(x+.01,cy,.51),(x,cy+.34,.51)],
          .03,sage_mat,local=False)
for k in range(31):
    t=-.29+k*.0193
    curve("Cane weave",[(cx+t,cy-.29,.516),(cx+t,cy+.29,.516)],
          .0024,cane_mat,local=False)
    curve("Cane weave",[(cx-.29,cy+t,.518),(cx+.29,cy+t,.518)],
          .0024,cane_mat,local=False)

def fabric(name,color,pattern):
    m=material(name,color,.87)
    ns=m.node_tree.nodes
    lk=m.node_tree.links
    bs=ns.get("Principled BSDF")
    tex=ns.new("ShaderNodeTexCoord")
    noise=ns.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=230
    noise.inputs["Detail"].default_value=2
    lk.new(tex.outputs["Generated"],noise.inputs["Vector"])
    bump=ns.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.19
    bump.inputs["Distance"].default_value=.002
    lk.new(noise.outputs["Fac"],bump.inputs["Height"])
    lk.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if pattern:
        geo=ns.new("ShaderNodeNewGeometry")
        dot=ns.new("ShaderNodeVectorMath")
        dot.operation='DOT_PRODUCT'
        dot.inputs[1].default_value=(.682,.73135,0)
        lk.new(geo.outputs["Position"],dot.inputs[0])
        mult=ns.new("ShaderNodeMath")
        mult.operation='MULTIPLY'
        mult.inputs[1].default_value=210
        lk.new(dot.outputs["Value"],mult.inputs[0])
        sine=ns.new("ShaderNodeMath")
        sine.operation='SINE'
        lk.new(mult.outputs[0],sine.inputs[0])
        threshold=ns.new("ShaderNodeMath")
        threshold.operation='GREATER_THAN'
        threshold.inputs[1].default_value=.975
        lk.new(sine.outputs[0],threshold.inputs[0])
        mix=ns.new("ShaderNodeMixRGB")
        mix.inputs[1].default_value=(*color,1)
        mix.inputs[2].default_value=(.68,.44,.40,1)
        lk.new(threshold.outputs[0],mix.inputs[0])
        lk.new(mix.outputs[0],bs.inputs["Base Color"])
    return m

clothmat=fabric("Woven cream and rose upholstery",linen,True)
pillowmat=fabric("Ivory textured pillow",pillowcol,False)
for ob in list(bpy.context.scene.objects):
    if ob.type!='MESH':
        continue
    for slot in ob.material_slots:
        m=slot.material
        if not m:
            continue
        p=m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        c=tuple(p.inputs["Base Color"].default_value[:3]) if p else tuple(m.diffuse_color[:3])
        if sum((c[i]-linen[i])**2 for i in range(3))<.0001:
            slot.material=clothmat
        elif sum((c[i]-pillowcol[i])**2 for i in range(3))<.0001:
            slot.material=pillowmat

# One inexpensive mesh contains all the parquet boards.
verts=[]
faces=[]
indices=[]
woodmats=[]
for k in range(9):
    v=.78+k*.065
    woodmats.append(material("Parquet tone "+str(k),(.25*v,.125*v,.073*v),.40))
w=.13
n=5
a=math.radians(12)
for i in range(-7,8):
    for j in range(-34,35):
        ox,oy=(n*i-j)*w,(n*i+j)*w
        for vertical in (False,True):
            if vertical:
                x0,y0=ox+n*w,oy
                dx,dy=w,n*w
            else:
                x0,y0=ox,oy
                dx,dy=n*w,w
            if abs(x0)>4.2 or abs(y0)>4.2:
                continue
            gap=.002
            corners=[(x0+gap,y0+gap),(x0+dx-gap,y0+gap),
                     (x0+dx-gap,y0+dy-gap),(x0+gap,y0+dy-gap)]
            start=len(verts)
            for x,y in corners:
                verts.append((x*math.cos(a)-y*math.sin(a),
                              x*math.sin(a)+y*math.cos(a),-.004))
            faces.append(tuple(range(start,start+4)))
            indices.append(random.randrange(len(woodmats)))
mesh=bpy.data.meshes.new("Parquet board surfaces")
mesh.from_pydata(verts,[],faces)
mesh.update()
ob=bpy.data.objects.new("Herringbone parquet boards",mesh)
bpy.context.collection.objects.link(ob)
for m in woodmats:
    mesh.materials.append(m)
for p,k in zip(mesh.polygons,indices):
    p.material_index=k

set_view(position=(-2.2,-4.4,3.1),target=(.12,-.02,.84),lens=60,sensor=36)
area_emitter(position=(-2.8,-.4,3.0),power=430,size=2.5,
             target=(0,0,.7),color=(1,.95,.85))
area_emitter(position=(.5,-3.4,3.7),power=95,size=3,
             target=(0,0,.65),color=(1,.96,.90))
s=bpy.context.scene
s.world.use_nodes=True
s.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.75,.79,.85,1)
s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.24
s.render.engine='CYCLES'
s.cycles.samples=24
s.cycles.use_denoising=True
s.render.resolution_x=512
s.render.resolution_y=384
s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
s.view_settings.exposure=.15
s.camera.data.dof.use_dof=False
