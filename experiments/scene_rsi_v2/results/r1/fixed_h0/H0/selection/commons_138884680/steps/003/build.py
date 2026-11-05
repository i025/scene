from sceneact import *
import bpy, math

scene = Scene("Rail carriage vestibule")
rounded = {}
wall=(.57,.58,.55)
steel=(.48,.53,.54)
orange=(.96,.33,.018)
yellow=(1,.57,.005)
dark=(.075,.09,.095)
blue=(.06,.22,.32)

def B(name,size,center,color,r=0):
    scene.include(name,box(size,center=center,color=color))
    if r:
        rounded[name]=(size,center,r)

def R(name,a,b,r=.018,color=steel):
    scene.include(name,rod(r,start=a,end=b,color=color))

def T(name,points,r=.018,color=steel):
    scene.include(name,sweep_tube(points=points,radius=r,color=color))

def loop(name,x1,x2,z1,z2,y,r=.09,th=.018,color=steel):
    p=[]
    for x,z,a in [(x2-r,z2-r,0),(x1+r,z2-r,90),
                  (x1+r,z1+r,180),(x2-r,z1+r,270)]:
        for i in range(7):
            t=math.radians(a+90*i/6)
            p.append((x+r*math.cos(t),y,z+r*math.sin(t)))
    T(name,p+[p[0]],th,color)

# Main enclosure.
B("floor",(5,6,.10),(-.8,.1,-.06),(.035,.041,.040))
B("rear left",(1.30,.12,3.10),(-2.20,2.77,1.50),wall)
B("rear right",(.62,.12,3.10),(.35,2.77,1.50),wall)
B("rear sill",(1.62,.12,1.20),(-.76,2.77,.60),wall)
B("rear header",(1.62,.12,.64),(-.76,2.77,2.84),wall)
B("side wall",(.13,5.8,3.2),(.73,0,1.50),(.43,.47,.48))
B("left wall",(.12,5.8,3.2),(-2.35,0,1.50),wall)
B("ceiling",(4.5,6,.12),(-1.3,0,3.08),(.46,.47,.43))
B("rear corner",(.085,.13,3.10),(.65,2.64,1.50),(.39,.43,.43))
R("rear top seam",(-2.8,2.697,2.96),(.63,2.697,2.96),.005,(.25,.27,.25))

# Rounded rectangular window, layered gaskets and exterior shapes.
B("window rubber",(1.65,.07,1.36),(-.76,2.675,1.86),(.035,.045,.05),.15)
B("window rim",(1.575,.035,1.285),(-.76,2.625,1.86),(.65,.69,.69),.13)
B("window gasket",(1.53,.025,1.24),(-.76,2.596,1.86),(.09,.12,.13),.115)
B("daylight",(1.475,.018,1.185),(-.76,2.573,1.86),(.91,.96,.97),.105)
B("outside train",(.60,.012,.53),(-.34,2.555,1.54),(.68,.75,.76),.05)
B("outside glazing",(.53,.01,.29),(-.34,2.541,1.60),(.39,.50,.53),.035)
B("outside red stripe",(.27,.008,.035),(-.37,2.528,1.39),(.76,.32,.29))
B("outside white base",(.60,.008,.12),(-.34,2.528,1.31),(.82,.85,.84))
for i in range(7):
    R("outside mullion "+str(i),(-.58+i*.078,2.527,1.47),
      (-.58+i*.078,2.527,1.73),.003,(.63,.72,.73))
R("outside post",(-1.40,2.535,1.31),(-1.40,2.535,2.27),.016,(.71,.76,.76))
R("outside cable",(-1.43,2.532,2.26),(-.72,2.532,2.23),.006,(.46,.54,.56))

# Yellow grab rail across the window.
for i,x in enumerate([-1.80,.23]):
    B("rail mounting "+str(i),(.065,.025,.14),(x,2.62,1.56),yellow,.018)
    R("rail bracket "+str(i),(x,2.62,1.56),(x,2.45,1.56),.024,yellow)
R("yellow window rail",(-1.84,2.44,1.56),(.27,2.44,1.56),.021,yellow)

# Stainless lower wall.
B("kick plate",(3.35,.06,.39),(-1.02,2.62,.235),(.48,.52,.52))
B("kick upper lip",(3.35,.075,.025),(-1.02,2.578,.442),(.64,.68,.67))
B("kick lower lip",(3.35,.07,.025),(-1.02,2.578,.045),(.23,.27,.27))

# Folded tubular wall fittings.
loop("upper tubular frame",-1.08,.48,2.61,2.91,2.47,.125,.022,(.18,.21,.21))
R("upper internal bar",(-.94,2.43,2.73),(.34,2.43,2.73),.019,(.31,.34,.33))
R("upper silver bar",(-.92,2.45,2.86),(.33,2.45,2.86),.013,steel)
for i,x in enumerate([-.83,-.27,.22]):
    T("upper hook "+str(i),[(x-.07,2.46,2.68),(x-.07,2.43,2.89),
      (x-.035,2.44,2.965),(x+.055,2.49,2.965),(x+.09,2.57,2.91)],
      .021,(.23,.26,.25))
loop("lower tubular frame",-1.00,.28,.68,.94,2.43,.105,.021,(.25,.29,.29))
R("lower crossbar",(-.94,2.40,.85),(.24,2.40,.85),.016,steel)
for i,x in enumerate([-.86,-.38,.08]):
    B("lower mounting "+str(i),(.15,.035,.19),(x,2.60,.81),(.31,.35,.35))
    T("lower curved hook "+str(i),[(x-.06,2.47,.92),(x-.065,2.35,.91),
      (x-.06,2.34,.72),(x-.03,2.39,.62),(x+.035,2.48,.61),
      (x+.06,2.53,.68),(x+.05,2.53,.79)],.018,(.40,.44,.44))

# Side-wall folding seat.
B("fold backing",(.085,.87,1.31),(.57,.84,1.45),(.37,.41,.41),.055)
B("orange folding seat",(.13,.84,1.30),(.485,.82,1.47),orange,.065)
B("fold dark piping",(.075,.033,1.19),(.50,.395,1.47),(.75,.24,.01),.014)
for i,y in enumerate([.49,1.14]):
    T("fold leg "+str(i),[(.49,y,1.00),(.46,y,.70),(.42,y,.60),
      (.42,y,.055),(.34,y,.04)],.024,steel)
    B("fold foot "+str(i),(.15,.11,.023),(.40,y,.025),steel,.01)
T("fold frame",[(.43,.48,.48),(.43,.48,.58),(.43,.57,.64),
  (.43,1.05,.64),(.43,1.14,.57),(.43,1.14,.48)],.021,(.35,.40,.41))
B("release handle",(.075,.13,.12),(.40,.40,1.19),(.025,.035,.035),.019)
T("release cable",[(.405,.42,1.15),(.405,.39,.94),(.43,.43,.88)],.009,dark)
R("side support bar",(.62,.20,1.78),(.62,.76,1.78),.023,(.25,.29,.30))

# Left seat partitions.
B("left seat shell",(.11,1.40,1.58),(-1.46,.77,1.20),(.63,.67,.66),.065)
B("orange left divider",(.12,1.37,1.52),(-1.385,.78,1.24),(.91,.33,.025),.065)
B("orange divider edge",(.035,1.34,1.47),(-1.307,.78,1.24),(.98,.40,.035),.03)
for i,y in enumerate([1.40,1.76]):
    B("distant orange back "+str(i),(.12,.28,1.24),(-1.50,y,1.13),orange,.065)
B("foreground cushion",(1.24,.84,.20),(-1.05,-.02,.29),(.99,.39,.018),.09)
B("foreground back",(.17,.78,1.13),(-1.72,-.12,.83),orange,.075)
B("cushion base",(1.18,.78,.07),(-1.05,-.02,.17),(.33,.37,.37))
B("grey handle pedestal",(.16,.14,.48),(-1.38,.20,1.89),(.28,.32,.33),.065)
T("left yellow handle",[(-1.35,.18,1.89),(-1.35,.18,2.23),
  (-1.35,.24,2.31),(-1.35,.36,2.30),(-1.35,.40,2.23),
  (-1.35,.40,1.97),(-1.35,.34,1.91),(-1.35,.18,1.89)],.023,yellow)
R("left seat leg",(-1.36,1.32,.50),(-1.36,1.32,.04),.024,steel)

# Cropped side window and luggage shelf.
B("left window frame",(.04,1.60,1.62),(-2.27,1.03,1.85),dark,.09)
B("left daylight",(.02,1.46,1.47),(-2.24,1.03,1.85),(.87,.94,.95),.075)
B("luggage shelf",(.92,1.85,.055),(-1.91,1.58,2.75),(.16,.18,.17))
B("shelf fascia",(.055,1.90,.20),(-1.44,1.58,2.81),(.28,.30,.28))
for j in range(10):
    y=.76+j*.17
    R("shelf slat "+str(j),(-2.32,y,2.80),(-1.47,y,2.80),.015,(.47,.50,.46))
R("shelf bracket",(-1.46,2.46,2.74),(-1.46,2.46,2.98),.020,steel)

# Foreground door edge.
B("door upright",(.10,.10,3.15),(.68,-1.02,1.52),(.62,.67,.67))
B("door glass",(.04,.46,1.75),(.67,-1.29,1.80),(.23,.30,.32))
T("door yellow handle",[(.53,-.91,1.30),(.49,-.94,1.30),
  (.45,-.94,1.36),(.45,-.94,1.99),(.49,-.94,2.05),
  (.56,-.91,2.05)],.024,yellow)
B("upper side channel",(.23,4.5,.17),(.59,.4,2.99),(.29,.33,.34))

# Signs.
B("upper instruction plate",(.20,.014,.37),(-1.27,2.596,2.80),(.84,.86,.80))
B("accessible plate",(.13,.014,.15),(.30,2.596,2.10),(.85,.87,.82))
B("exit sign",(.25,.016,.105),(-2.08,2.58,2.09),(.10,.32,.19))
R("exit arrow",(-2.16,2.562,2.09),(-2.00,2.562,2.09),.006,(.87,.92,.80))
B("side instruction plate",(.013,.20,.22),(.652,.02,1.91),(.85,.88,.84))
for i,yy in enumerate([-.045,.045]):
    for j,zz in enumerate([1.87,1.95]):
        B("side icon %d %d"%(i,j),(.016,.052,.043),(.641,yy,zz),blue)

realize(scene)

# Round the broad faces of thin panels with lightweight extruded meshes.
# SceneAct supplies their placement and individual object identity.
for name,(size,center,r) in rounded.items():
    ob=bpy.data.objects.get(name)
    if ob is None:
        continue
    thin=min(range(3),key=lambda k:size[k])
    a,b=[k for k in range(3) if k!=thin]
    r=min(r,size[a]*.49,size[b]*.49)
    outline=[]
    for ca,cb,ang in [(size[a]/2-r,size[b]/2-r,0),
                     (-size[a]/2+r,size[b]/2-r,90),
                     (-size[a]/2+r,-size[b]/2+r,180),
                     (size[a]/2-r,-size[b]/2+r,270)]:
        for j in range(7):
            t=math.radians(ang+j*15)
            outline.append((ca+r*math.cos(t),cb+r*math.sin(t)))
    verts=[]
    inv=ob.matrix_world.inverted()
    from mathutils import Vector
    for side in [-1,1]:
        for u,v in outline:
            p=list(center)
            p[a]+=u
            p[b]+=v
            p[thin]+=side*size[thin]/2
            verts.append(tuple(inv@Vector(p)))
    n=len(outline)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name+" rounded")
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    for m in ob.data.materials:
        mesh.materials.append(m)
    ob.data=mesh

# Small repeated perforations share one mesh.
verts=[]
faces=[]
for xc in [-1.63,-.14]:
    for row in range(5):
        for col in range(13):
            x=xc+(col-6)*.030+(row%2)*.013
            z=.12+row*.028
            k=len(verts)
            for j in range(6):
                a=2*math.pi*j/6
                verts.append((x+.005*math.cos(a),2.584,z+.005*math.sin(a)))
            faces.append(tuple(range(k,k+6)))
mesh=bpy.data.meshes.new("vent perforations")
mesh.from_pydata(verts,[],faces)
ob=bpy.data.objects.new("vent perforations",mesh)
bpy.context.collection.objects.link(ob)
mat=bpy.data.materials.new("dark vent holes")
mat.diffuse_color=(.055,.07,.07,1)
ob.data.materials.append(mat)

# Simple small printed blue symbols, built as curves.
def ink(name,points,r=.003,color=blue):
    curve=bpy.data.curves.new(name,'CURVE')
    curve.dimensions='3D'
    curve.bevel_depth=r
    curve.bevel_resolution=1
    sp=curve.splines.new('POLY')
    sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):
        p.co=(*co,1)
    obj=bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(obj)
    m=bpy.data.materials.get("sign blue")
    if m is None:
        m=bpy.data.materials.new("sign blue")
        m.diffuse_color=(*color,1)
    curve.materials.append(m)

for z in [2.70,2.85]:
    for x in [-1.31,-1.23]:
        ink("bicycle wheel",[(x+.025*math.cos(i*math.pi/8),2.579,
                             z+.025*math.sin(i*math.pi/8)) for i in range(17)])
    ink("bicycle frame",[(-1.31,2.579,z),(-1.26,2.579,z+.06),
                        (-1.23,2.579,z),(-1.31,2.579,z)])
for x in [-1.358,-1.182]:
    ink("sign border",[(x,2.579,2.625),(x,2.579,2.975)],.0025)
ink("wheelchair wheel",[(.30+.027*math.cos(i*math.pi/8),2.579,
                        2.085+.027*math.sin(i*math.pi/8)) for i in range(17)])
ink("wheelchair figure",[(.29,2.579,2.14),(.29,2.579,2.10),
                        (.32,2.579,2.10),(.335,2.579,2.07)],.004)

for ob in bpy.context.scene.objects:
    if ob.type!='MESH':
        continue
    name=ob.name.lower()
    for mat in ob.data.materials:
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if not bs:
            continue
        bs.inputs["Roughness"].default_value=.58
        if any(s in name for s in ["tubular","crossbar","hook","fold leg","kick","shelf slat"]):
            bs.inputs["Metallic"].default_value=.65
            bs.inputs["Roughness"].default_value=.32
        if "daylight" in name:
            bs.inputs["Emission Color"].default_value=(.85,.94,.96,1)
            bs.inputs["Emission Strength"].default_value=.7
        if name=="floor":
            nt=mat.node_tree
            noise=nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value=210
            ramp=nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].color=(.017,.021,.020,1)
            ramp.color_ramp.elements[1].color=(.075,.082,.078,1)
            nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])

set_view((0,-1.70,1.50),(0,2.70,1.26),lens=26,sensor=36)
area_emitter((-1,1.8,2.78),power=230,size=2.2,target=(-.4,0,.8),color=(.93,.97,1))
area_emitter((-1.8,-.9,2.65),power=170,size=2.1,target=(.2,1.8,1.2),color=(1,.94,.84))
area_emitter((-.8,2.40,2.0),power=85,size=1.3,target=(.1,-1,1),color=(.86,.94,1))

sc=bpy.context.scene
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.53,.59,.63,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.30
sc.render.engine='CYCLES'
sc.cycles.samples=16
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=.25
