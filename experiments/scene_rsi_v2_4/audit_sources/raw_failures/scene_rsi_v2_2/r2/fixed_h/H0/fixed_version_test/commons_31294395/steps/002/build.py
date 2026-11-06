from sceneact import *
import bpy, math, random
random.seed(18)

scene = Scene("Victorian bedroom")
wood=(.075,.037,.023)
gold=(.55,.34,.10)

def add(name,node):
    scene.include(name,node)
    return node

def ell(name,center,scale,color):
    n=ball(1,center=center,color=color)
    n.resize(scale)
    return add(name,n)

# Architecture.
add("stone floor",box((8.2,9,.13),center=(0,0,-.085),color=(.61,.59,.52)))
add("back patterned wall",box((7.6,.16,3.55),center=(-.3,3.65,1.775),color=(.39,.29,.18)))
add("right patterned wall",box((.16,8.5,3.55),center=(3.45,-.5,1.775),color=(.39,.29,.18)))
add("back baseboard",box((7.6,.07,.17),center=(-.3,3.52,.085),color=(.27,.21,.15)))
add("right baseboard",box((.07,8.5,.17),center=(3.32,-.5,.085),color=(.27,.21,.15)))
for z,depth,height in [(3.38,.16,.12),(3.47,.24,.08),(3.53,.32,.06)]:
    add("back crown"+str(z),box((7.7,depth,height),center=(-.3,3.51,z),color=(.91,.91,.86)))
    add("right crown"+str(z),box((depth,8.5,height),center=(3.32,-.5,z),color=(.91,.91,.86)))
add("ceiling",box((7.7,8.5,.10),center=(-.3,-.5,3.61),color=(.86,.87,.84)))

# Tall windows and green roller shades.
for i,x in enumerate([-3.00,-.98]):
    add("window recess"+str(i),box((1.35,.06,2.66),center=(x,3.535,1.86),color=(.88,.91,.89)))
    add("daylight glass"+str(i),box((1.12,.035,2.39),center=(x,3.485,1.87),color=(.79,.92,.92)))
    for xx in [x-.68,x+.68]:
        add("window architrave",box((.11,.15,2.83),center=(xx,3.43,1.86),color=(.94,.93,.87)))
        add("inner sash edge",box((.045,.07,2.57),center=(xx+(.10 if xx<x else -.10),3.37,1.86),color=(.79,.82,.78)))
    for zz in [.47,3.25]:
        add("window horizontal trim",box((1.47,.16,.11),center=(x,3.43,zz),color=(.96,.94,.88)))
    add("sash crossbar",box((1.2,.085,.045),center=(x,3.37,1.43),color=(.86,.88,.81)))
    add("window sill",box((1.52,.30,.075),center=(x,3.35,.48),color=(.91,.89,.81)))
    add("green roller blind"+str(i),box((1.09,.035,1.25),center=(x,3.32,2.47),color=(.16,.34,.29)))
    add("blind bottom hem"+str(i),rod(.014,start=(x-.55,3.29,1.845),end=(x+.55,3.29,1.845),color=(.30,.43,.36)))

# Rear door.
add("door frame",box((.79,.10,2.35),center=(1.23,3.48,1.175),color=(.89,.89,.81)))
add("door slab",box((.65,.07,2.23),center=(1.23,3.40,1.15),color=(.79,.82,.77)))
for z,h in [(.65,.76),(1.67,.90)]:
    add("door inset",box((.49,.025,h),center=(1.23,3.35,z),color=(.85,.87,.82)))
add("door knob",ball(.032,center=(1.48,3.29,1.08),color=gold))

# Mahogany bed, its head against the right wall.
bed=Asset("dark mahogany sleigh bed")
bed.include("frame",box((2.66,1.80,.27),center=(1.94,.34,.36),color=wood))
bed.include("mattress",fillet_box((2.53,1.67,.27),radius=.12,center=(1.92,.34,.62),color=(.72,.72,.63)))
bed.include("white coverlet",fillet_box((2.46,1.69,.18),radius=.085,center=(1.88,.32,.77),color=(.84,.83,.73)))
bed.include("foot panel",box((.11,1.88,.70),center=(.56,.34,.57),color=wood))
bed.include("footboard cap",rod(.065,start=(.55,-.65,.97),end=(.55,1.33,.97),color=(.11,.061,.032)))
for yy in [-.61,1.29]:
    bed.include("foot post"+str(yy),box((.15,.15,1.02),center=(.54,yy,.53),color=wood))
    bed.include("post rounded top"+str(yy),ball(.10,center=(.54,yy,1.06),color=wood))
    bed.include("head post"+str(yy),box((.13,.13,1.31),center=(3.22,yy,.68),color=wood))
bed.include("head board",box((.13,1.85,1.02),center=(3.21,.34,.85),color=wood))
bed.include("head upper rail",rod(.065,start=(3.20,-.65,1.40),end=(3.20,1.33,1.40),color=(.11,.061,.033)))
for xx in [.69,3.08]:
    for yy in [-.49,1.17]:
        bed.include("bed leg",box((.13,.13,.30),center=(xx,yy,.16),color=wood))
scene.include("bed",bed)

for i,yy in enumerate([-.12,.77]):
    p=fillet_box((.64,.77,.25),radius=.12,center=(2.76,yy,1.04),color=(.89,.88,.79))
    p.turn("y",-29)
    add("plump pillow "+str(i),p)
    q=fillet_box((.68,.79,.10),radius=.045,center=(2.86,yy,.91),color=(.76,.76,.68))
    q.turn("y",-18)
    add("pillow under edge "+str(i),q)

for i in range(24):
    xx=random.uniform(.78,2.48)
    yy=random.uniform(-.39,1.08)
    pts=[(xx+j*.055,yy+math.sin(j*.65+i)*.016,.866+math.sin(j*.7)*.007) for j in range(random.randint(3,7))]
    add("linen crease"+str(i),sweep_tube(points=pts,radius=.0035,color=(.75,.75,.66)))

# Olive velvet armchair.
chair=Asset("olive velvet armchair")
def cp(name,n):
    chair.include(name,n)
def ce(name,c,s,col):
    n=ball(1,center=c,color=col)
    n.resize(s)
    cp(name,n)
cp("lower upholstered body",fillet_box((1.23,1.09,.48),radius=.20,center=(-.65,-.22,.45),color=(.24,.25,.035)))
ce("rounded tall back",(-.65,.20,1.00),(.59,.20,.69),(.29,.30,.055))
ce("back inner cushion",(-.65,.027,1.04),(.46,.09,.52),(.34,.35,.066))
ce("seat cushion",(-.65,-.38,.70),(.49,.48,.14),(.36,.36,.063))
for xx in [-1.20,-.10]:
    ce("curved arm side"+str(xx),(xx,-.24,.70),(.14,.57,.43),(.23,.24,.035))
    cp("rolled arm"+str(xx),sweep_tube(points=[(xx,.17,1.13),(xx,-.05,1.05),(xx,-.32,.93),(xx,-.61,.87),(xx,-.75,.84)],radius=.065,color=(.32,.32,.060)))
for xx in [-1.10,-.20]:
    for yy in [-.63,.18]:
        cp("small wooden foot",rod(.035,start=(xx,yy,.05),end=(xx,yy,.30),color=(.13,.09,.035)))
for zz,xs in [(1.29,[-.88,-.62,-.36]),(1.06,[-1.0,-.75,-.49,-.25]),(.84,[-.87,-.61,-.35])]:
    for xx in xs:
        ce("velvet button",(xx,-.065,zz),(.025,.018,.024),(.18,.20,.025))
        cp("tuft fold",sweep_tube(points=[(xx-.07,-.057,zz+.09),(xx,-.083,zz),(xx+.065,-.057,zz-.09)],radius=.009,color=(.24,.26,.035)))
chair.turn("z",-15,pivot=(-.65,-.22,0))
scene.include("chair",chair)

# Three-panel painted folding screen.
for k in range(3):
    x=-.05+k*.48
    y=2.46+(.08 if k==1 else 0)
    add("screen panel"+str(k),box((.49,.055,1.74),center=(x,y,1.18),color=(.60,.44,.19)))
    for xx in [x-.24,x+.24]:
        add("screen edge",rod(.012,start=(xx,y-.035,.30),end=(xx,y-.035,2.06),color=(.17,.12,.05)))
    add("screen top",rod(.012,start=(x-.24,y-.035,2.055),end=(x+.24,y-.035,2.055),color=(.17,.12,.05)))
    for j in range(3):
        n=ball(1,center=(x+random.uniform(-.12,.12),y-.036,.56+j*.47),color=(.018,.075,.40))
        n.resize((.25,.014,.19))
        n.turn("y",random.uniform(-40,40))
        add("blue painted cloud",n)
    add("blue serpentine motif",sweep_tube(points=[(x-.20,y-.059,.42),(x+.12,y-.059,.79),(x-.10,y-.059,1.11),(x+.17,y-.059,1.44),(x+.13,y-.059,1.91)],radius=.060,color=(.025,.10,.43)))
    for j in range(8):
        add("painted gold fleck",ball(.016,center=(x+random.uniform(-.20,.20),y-.083,random.uniform(.42,1.96)),color=(.78,.61,.26)))

# Cabinet at left.
add("antique chest",box((1.04,.47,.65),center=(-3.07,2.99,.54),color=(.105,.061,.033)))
add("chest top",box((1.12,.55,.07),center=(-3.07,2.98,.90),color=(.17,.10,.055)))
for xx in [-3.51,-2.63]:
    for yy in [2.79,3.17]:
        add("cabinet turned leg",rod(.035,start=(xx,yy,.05),end=(xx,yy,.29),color=wood))
for zz in [.42,.67]:
    add("drawer line",box((.95,.018,.016),center=(-3.07,2.743,zz),color=(.04,.025,.018)))
    for xx in [-3.32,-2.83]:
        add("brass drawer pull",ball(.027,center=(xx,2.72,zz+.08),color=gold))
add("small frame",box((.28,.05,.37),center=(-3.13,2.98,1.12),color=gold))
add("small picture",box((.22,.018,.30),center=(-3.13,2.943,1.12),color=(.075,.085,.056)))

# Tea table and accessories.
tx,ty=-1.98,2.92
add("tea table top",rod(.36,length=.055,center=(tx,ty,.88),color=(.28,.17,.075)))
for dx,dy in [(-.21,-.17),(.21,-.17),(0,.22)]:
    add("tea table leg",rod(.022,start=(tx+dx,ty+dy,.06),end=(tx+dx*.55,ty+dy*.55,.86),color=wood))
for xx in [tx-.16,tx+.11]:
    add("tea cup",rod(.048,length=.065,center=(xx,ty-.04,.955),color=(.85,.82,.66)))
    add("saucer",rod(.072,length=.012,center=(xx,ty-.04,.914),color=(.88,.85,.73)))
add("little pot",ball(.065,center=(tx+.03,ty+.10,.98),color=(.78,.72,.48)))
add("wastebasket",rod(.105,length=.24,center=(-2.43,3.12,.12),color=(.26,.13,.065)))

# Framed pictures.
def back_frame(name,x,z,w,h,oval=False):
    if oval:
        ell(name+" outer",(x,3.48,z),(w/2,.052,h/2),(.67,.45,.16))
        ell(name+" inner",(x,3.417,z),(w/2-.045,.021,h/2-.045),(.85,.67,.28))
        ell(name+" canvas",(x,3.388,z),(w/2-.075,.014,h/2-.075),(.042,.031,.025))
        ell(name+" face",(x,3.363,z+.10),(.073,.012,.096),(.40,.26,.15))
        ell(name+" coat",(x,3.363,z-.12),(.17,.014,.19),(.035,.029,.024))
        add(name+" collar",box((.08,.015,.035),center=(x+.01,3.341,z-.015),color=(.69,.63,.49)))
    else:
        add(name+" frame",box((w,.055,h),center=(x,3.46,z),color=(.63,.48,.25)))
        add(name+" mat",box((w-.045,.018,h-.045),center=(x,3.42,z),color=(.85,.82,.70)))
        add(name+" image",box((w*.62,.012,h*.70),center=(x,3.40,z),color=(.46,.45,.39)))
        ell(name+" portrait",(x,3.387,z+.025),(w*.18,.009,h*.23),(.28,.29,.26))
back_frame("oval ancestral portrait",-1.98,2.45,.78,.98,True)
back_frame("small monochrome print",.49,2.65,.44,.60)
add("right wall picture frame",box((.055,.40,.59),center=(3.32,2.15,2.62),color=(.65,.47,.22)))
add("right wall picture mat",box((.019,.35,.54),center=(3.28,2.15,2.62),color=(.84,.80,.68)))
ell("oval print",(3.263,2.15,2.62),(.012,.10,.19),(.44,.40,.32))

# Small side chair.
for xx in [1.70,2.12]:
    for yy in [2.04,2.46]:
        add("side chair leg",rod(.022,start=(xx,yy,.02),end=(xx,yy,.57),color=wood))
add("side chair seat",box((.49,.48,.055),center=(1.91,2.25,.58),color=(.20,.16,.10)))
for xx in [1.68,2.14]:
    add("side chair back upright",rod(.022,start=(xx,2.46,.56),end=(xx,2.46,1.18),color=wood))
add("side chair crest",rod(.035,start=(1.66,2.46,1.18),end=(2.16,2.46,1.18),color=wood))
for xx in [1.78,1.90,2.02]:
    add("side chair spindle",rod(.012,start=(xx,2.46,.64),end=(xx,2.46,1.15),color=wood))
add("round bedside top",rod(.43,length=.075,center=(3.30,-1.15,.67),color=(.065,.038,.026)))
add("round bedside pedestal",rod(.12,length=.55,center=(3.30,-1.15,.32),color=wood))
add("round bedside foot",rod(.34,length=.075,center=(3.30,-1.15,.06),color=wood))

# Woven rugs.
def rug(name,cx,cy,w,h):
    add(name,box((w,h,.013),center=(cx,cy,.006),color=(.38,.16,.10)))
    for k,col in enumerate([(.68,.49,.27),(.17,.23,.24),(.66,.44,.24),(.28,.12,.08)]):
        inset=.025+k*.042
        for sy in [-1,1]:
            add(name+" border",box((w-2*inset,.024,.005),center=(cx,cy+sy*(h/2-inset),.016),color=col))
        for sx in [-1,1]:
            add(name+" border",box((.024,h-2*inset,.005),center=(cx+sx*(w/2-inset),cy,.016),color=col))
    for ix in range(7):
        for iy in range(5):
            xx=cx+(ix-3)*(w-.38)/7
            yy=cy+(iy-2)*(h-.35)/5
            q=box((.072,.072,.004),center=(xx,yy,.019),color=(.64,.46,.26))
            q.turn("z",45)
            add(name+" woven motif",q)
rug("rear Persian rug",-1.12,1.57,1.72,.89)
rug("foreground rug",1.59,-1.48,2.27,.93)

realize(scene)

# Procedural wallpaper.
wallmat=bpy.data.materials.new("ochre and faded blue floral wallpaper")
wallmat.use_nodes=True
nt=wallmat.node_tree
bs=nt.nodes.get("Principled BSDF")
bs.inputs["Roughness"].default_value=.92
tex=nt.nodes.new("ShaderNodeTexCoord")
noise=nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=83
noise.inputs["Detail"].default_value=3
noise.inputs["Roughness"].default_value=.76
nt.links.new(tex.outputs["Generated"],noise.inputs["Vector"])
ramp=nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for i,(pos,col) in enumerate([
    (.20,(.11,.12,.105,1)),(.36,(.25,.25,.19,1)),
    (.48,(.43,.29,.16,1)),(.58,(.57,.40,.23,1)),
    (.73,(.30,.29,.23,1)),(.85,(.64,.46,.27,1))]):
    el=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(pos)
    el.position=pos
    el.color=col
nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
bump=nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.17
bump.inputs["Distance"].default_value=.016
nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
for ob in bpy.data.objects:
    if ob.type=="MESH" and "patterned wall" in ob.name:
        ob.data.materials.clear()
        ob.data.materials.append(wallmat)

patternmat=bpy.data.materials.new("faded floral ink")
patternmat.diffuse_color=(.23,.25,.20,1)
verts=[]
faces=[]
def leaf(x,y,z,sx,sz,wall):
    b=len(verts)
    if wall=="back":
        verts.extend([(x-sx,y,z),(x,y,z+sz),(x+sx,y,z),(x,y,z-sz)])
    else:
        verts.extend([(x,y-sx,z),(x,y,z+sz),(x,y+sx,z),(x,y,z-sz)])
    faces.append((b,b+1,b+2,b+3))
for row in range(36):
    z=.20+row*.088
    for col in range(75):
        x=-4.0+col*.102+(row%2)*.051
        occupied=any(abs(x-wx)<.76 and .42<z<3.3 for wx in [-3,-.98]) or (abs(x-1.23)<.44 and z<2.4)
        if not occupied:
            leaf(x,3.558,z,.014,.028,"back")
            leaf(x+.024,3.557,z+.021,.011,.017,"back")
    for col in range(88):
        yy=-4.45+col*.102+(row%2)*.051
        leaf(3.362,yy,z,.014,.028,"right")
        leaf(3.361,yy+.024,z+.021,.011,.017,"right")
mesh=bpy.data.meshes.new("wallpaper repeating leaf mesh")
mesh.from_pydata(verts,[],faces)
mesh.materials.append(patternmat)
ob=bpy.data.objects.new("tiny repeated wallpaper leaves",mesh)
bpy.context.collection.objects.link(ob)

# Hanging white cloth.
mesh=bpy.data.meshes.new("tea cloth mesh")
mesh.from_pydata([
    (tx-.38,ty-.28,.925),(tx+.38,ty-.28,.925),
    (tx+.34,ty+.24,.925),(tx-.34,ty+.24,.925),
    (tx,ty-.38,.48)],[],[(0,1,2,3),(0,4,1)])
cloth=bpy.data.materials.new("ivory cloth")
cloth.diffuse_color=(.88,.87,.79,1)
mesh.materials.append(cloth)
ob=bpy.data.objects.new("draped white tablecloth",mesh)
bpy.context.collection.objects.link(ob)
sol=ob.modifiers.new("cloth thickness","SOLIDIFY")
sol.thickness=.004

floormat=bpy.data.materials.new("old pale stone")
floormat.use_nodes=True
nt=floormat.node_tree
bs=nt.nodes.get("Principled BSDF")
bs.inputs["Roughness"].default_value=.87
noise=nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=5
noise.inputs["Detail"].default_value=4
r=nt.nodes.new("ShaderNodeValToRGB")
r.color_ramp.elements[0].color=(.39,.39,.34,1)
r.color_ramp.elements[1].color=(.72,.70,.61,1)
nt.links.new(noise.outputs["Fac"],r.inputs[0])
nt.links.new(r.outputs[0],bs.inputs["Base Color"])
for ob in bpy.data.objects:
    if ob.type=="MESH" and "stone floor" in ob.name:
        ob.data.materials.clear()
        ob.data.materials.append(floormat)
    if ob.type=="MESH" and any(s in ob.name for s in ["pillow","rounded tall back","seat cushion","curved arm","inner cushion"]):
        for poly in ob.data.polygons:
            poly.use_smooth=True

set_view(position=(-4.60,-6.85,2.73),target=(-.05,1.40,1.48),lens=35,sensor=36)
area_emitter(position=(-1.06,3.12,2.08),power=650,size=1.5,target=(.2,-.4,.6),color=(.85,.94,1))
area_emitter(position=(-3.01,3.12,2.05),power=420,size=1.4,target=(-1.8,0,.8),color=(.88,.95,1))
area_emitter(position=(-2,-3.1,3.2),power=115,size=4,target=(.7,1,1),color=(1,.91,.77))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.35,.40,.44,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.24
for ob in bpy.data.objects:
    if ob.type=="MESH" and "daylight glass" in ob.name:
        mat=bpy.data.materials.new("bright overcast outdoors")
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value=(.79,.91,.93,1)
        bs.inputs["Emission Color"].default_value=(.75,.91,.96,1)
        bs.inputs["Emission Strength"].default_value=2.6
        ob.data.materials.clear()
        ob.data.materials.append(mat)
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.look="AgX - Medium High Contrast"
sc.view_settings.exposure=-.25
