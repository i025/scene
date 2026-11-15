from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(8)
scene = Scene('Classical green room')
wall=(0.36,0.43,0.34); trim=(0.59,0.56,0.49); wood=(0.25,0.095,0.035); dark=(0.12,0.045,0.023); ivory=(0.72,0.70,0.64)

def add(name,node): scene.include(name,node)
def B(name,size,center,color): add(name,box(size,center=center,color=color))
def R(name,r,a,b,color): add(name,rod(r,start=a,end=b,color=color))
def T(name,pts,r,color): add(name,sweep_tube(points=pts,radius=r,color=color))
# Room shell, with real openings in the rear wall
B('Pale plank floor',(7.5,9,.12),(0,0,-.08),(.57,.56,.52))
for i in range(22):
    x=-3.6+i*.34
    B('Floor plank %02d'%i,(.333,9,.025),(x,0,-.005),(.63+random.uniform(-.035,.035),.62+random.uniform(-.025,.025),.58+random.uniform(-.025,.025)))
    for j in range(2):
        xx=x+random.uniform(-.12,.12)
        B('Plank grain %02d %d'%(i,j),(.004,9,.002),(xx,0,.009),(.51,.50,.47))
B('Left wall',(.16,9,4.25),(-3.68,0,2.08),wall)
B('Right wall',(.16,9,4.25),(3.68,0,2.08),wall)
B('White ceiling',(7.5,9,.12),(0,0,4.2),(.77,.77,.73))
B('Back wall left',(1.48,.16,4.2),(-2.96,3.5,2.1),wall)
B('Back wall middle',(1.06,.16,4.2),(-.39,3.5,2.1),wall)
B('Back wall right',(1.34,.16,4.2),(3.03,3.5,2.1),wall)
# window positions and pointed arch profiles
windows=[(-1.70,1.04,3.37),(1.02,.98,3.22)]
for k,(cx,w,peak) in enumerate(windows):
    low=1.05; spring=2.55
    B('Rear wall below window %d'%k,(w,.16,low),(cx,3.5,low/2),wall)
    # wall strips over each curved opening
    n=20
    for i in range(n):
        u=-1+(i+.5)*2/n
        arch=spring+(peak-spring)*(1-abs(u)**1.65)**.72
        B('Arch wall %d %02d'%(k,i),(w/n+.006,.16,4.2-arch),(cx+u*w/2,3.5,(4.2+arch)/2),wall)
    # thick reveals and sill
    for s in (-1,1):
        B('Window reveal %d %d'%(k,s),(.085,.28,spring-low),(cx+s*(w/2-.035),3.43,(spring+low)/2),trim)
    B('Window sill %d'%k,(w+.20,.35,.11),(cx,3.38,1.02),(.68,.66,.60))
    pts=[(cx-w/2,3.375,low),(cx-w/2,3.375,spring)]
    for i in range(21):
        u=-1+2*i/20
        arch=spring+(peak-spring)*(1-abs(u)**1.65)**.72
        pts.append((cx+u*w/2,3.375,arch))
    pts.extend([(cx+w/2,3.375,low),(cx-w/2,3.375,low)])
    T('Pointed window frame %d'%k,pts,.045,(.51,.49,.44))
    # pane backing sits beyond the wall and is clipped to a pointed shape below
    B('Lower window glazing %d'%k,(w-.11,.025,spring-low),(cx,3.57,(spring+low)/2),(.69,.77,.73))
    R('Window center mullion %d'%k,.019,(cx,3.34,1.06),(cx,3.34,2.55),(.48,.46,.40))
    R('Window cross rail %d'%k,.022,(cx-w/2,3.34,1.65),(cx+w/2,3.34,1.65),(.50,.48,.43))
    for s in (-1,1):
        pts=[]
        for i in range(11):
            t=i/10
            pts.append((cx+s*(w*.46*(1-t)),3.34,2.55+(peak-2.55)*(.10+.78*t**.65)))
        T('Curved Gothic glazing bar %d %d'%(k,s),pts,.018,(.49,.48,.43))
    B('Linen roller blind %d'%k,(w-.09,.07,.44),(cx,3.25,2.23),(.52,.51,.46))
    R('Blind lower hem %d'%k,.018,(cx-w*.46,3.20,2.01),(cx+w*.46,3.20,2.01),(.42,.41,.37))
    B('Radiator %d'%k,(w+.18,.12,.62),(cx,3.25,.67),(.79,.79,.76))
    B('Radiator top %d'%k,(w+.24,.15,.035),(cx,3.23,.99),(.68,.68,.65))
# baseboards and fine ceiling trim
B('Back skirting',(7.2,.07,.17),(0,3.35,.085),(.52,.46,.38))
B('Left skirting',(.06,9,.16),(-3.56,0,.08),(.55,.50,.44))
B('Right skirting',(.06,9,.16),(3.56,0,.08),(.55,.50,.44))
B('Back ceiling molding',(7.25,.07,.045),(0,3.36,4.09),(.50,.50,.46))
B('Right ceiling molding',(.07,9,.045),(3.56,0,4.09),(.50,.50,.46))
B('Left ceiling molding',(.07,9,.045),(-3.56,0,4.09),(.50,.50,.46))
# Wardrobe: broad side faces camera, two doors face room
B('Wardrobe carcass',(1.27,1.92,3.18),(-2.85,.26,1.65),wood)
B('Wardrobe broad side',(1.25,.045,3.08),(-2.85,-.72,1.64),(.30,.13,.052))
B('Wardrobe base',(1.35,2.01,.15),(-2.84,.25,.20),(.19,.068,.026))
B('Wardrobe side cornice',(1.38,2.04,.13),(-2.84,.25,3.25),(.20,.07,.027))
for ix in range(14):
    x=-3.42+ix*.085
    B('Wardrobe side wood grain %02d'%ix,(.008,.009,2.85),(x,-.748,1.70),(.22+random.random()*.08,.075+random.random()*.05,.025))
# doors on x-facing side
for j,y in enumerate((-.24,.72)):
    B('Wardrobe door %d'%j,(.055,.91,2.83),(-2.19,y,1.77),(.31,.14,.055))
    B('Wardrobe recessed panel %d'%j,(.024,.69,2.40),(-2.15,y,1.75),(.26,.10,.034))
    for yy in (y-.36,y+.36): B('Wardrobe door stile %d'%j,(.035,.035,2.48),(-2.12,yy,1.75),(.43,.22,.08))
    for zz in (.51,2.98): B('Wardrobe door rail %d'%j,(.035,.74,.045),(-2.12,y,zz),(.43,.22,.08))
    for h in range(7):
        yy=y-.30+h*.10
        B('Door timber streak %d %d'%(j,h),(.006,.008,2.27),(-2.105,yy,1.75),(.37+random.random()*.08,.16,.055))
    R('Brass door handle %d'%j,.025,(-2.085,y+(.25 if j==0 else -.25),1.55),(-2.035,y+(.25 if j==0 else -.25),1.55),(.57,.42,.17))
# curved crown on door face
pts=[]
for i in range(25):
    y=-.70+i*1.9/24
    z=3.25+.23*max(0,1-((y-.25)/.95)**2)**.7
    pts.append((-2.14,y,z))
T('Wardrobe curved crown',pts,.055,(.30,.13,.045))
for x in (-3.36,-2.35):
    for y in (-.57,1.08): B('Wardrobe foot',( .20,.20,.20),(x,y,.10),dark)
# simple chair partly hidden behind cabinet
for x in (-2.05,-1.55):
    for y in (1.45,1.95): B('Rear chair leg',(.055,.055,.86),(x,y,.43),dark)
B('Rear chair pale seat',(.65,.58,.09),(-1.80,1.69,.79),(.63,.57,.47))
for x in (-2.07,-1.53): B('Rear chair back post',(.055,.055,.87),(x,2.00,1.13),dark)
B('Rear chair top rail',(.59,.07,.09),(-1.8,2.0,1.54),dark)
for x in (-1.95,-1.8,-1.65): B('Rear chair back slat',(.045,.05,.59),(x,2.0,1.18),dark)
# Oval table: scaled sphere gives a softly rounded edge
cx,cy=.93,1.05
node=ball(1,center=(cx,cy,1.00),color=(.29,.14,.065)); node.resize((1.12,.62,.065),pivot=(cx,cy,1.00)); add('Oval polished tabletop',node)
node=ball(1,center=(cx,cy,.94),color=(.13,.055,.026)); node.resize((1.08,.59,.035),pivot=(cx,cy,.94)); add('Table dark edge',node)
R('Table pedestal',.10,(cx,cy,.26),(cx,cy,.94),(.19,.075,.03))
for z,r in ((.30,.16),(.38,.13),(.65,.15),(.77,.12),(.87,.15)):
    node=ball(r,center=(cx,cy,z),color=(.25,.10,.037)); node.resize((1,1,.55),pivot=(cx,cy,z)); add('Turned pedestal collar',node)
for a in (0,90,180,270):
    q=math.radians(a); dx,dy=math.cos(q),math.sin(q)
    T('Carved table foot %d'%a,[(cx,cy,.36),(cx+dx*.18,cy+dy*.18,.26),(cx+dx*.42,cy+dy*.42,.13),(cx+dx*.58,cy+dy*.58,.12)],.055,(.19,.065,.025))
    node=ball(.075,center=(cx+dx*.57,cy+dy*.57,.12),color=dark); node.resize((1.4,.8,.55),pivot=(cx+dx*.57,cy+dy*.57,.12)); add('Pedestal foot',node)
# two upholstered open-back chairs, turned toward the table
def chair(name,x,y,ang,striped=False):
    a=math.radians(ang)
    def p(xx,yy,zz): return (x+xx*math.cos(a)-yy*math.sin(a),y+xx*math.sin(a)+yy*math.cos(a),zz)
    def piece(n,sz,local,col):
        ob=box(sz,center=p(*local),color=col); ob.turn('+z',ang,pivot=p(*local)); add(name+' '+n,ob)
    def bar(n,r,u,v,col=dark): R(name+' '+n,r,p(*u),p(*v),col)
    piece('seat frame',(.64,.61,.10),(0,0,.55),dark)
    piece('upholstered seat',(.61,.58,.13),(0,-.015,.64),(.55,.54,.49))
    for xx in (-.27,.27):
        for yy in (-.24,.24): bar('leg',.033,(xx,yy,.55),(xx*1.13,yy*1.12,.05))
    for xx in (-.28,.28): bar('back post',.035,(xx,.25,.55),(xx*1.06,.29,1.30))
    bar('top crest',.045,(-.30,.29,1.30),(.30,.29,1.30))
    bar('lower back rail',.035,(-.28,.27,.85),(.28,.27,.85))
    for xx in (-.13,.13):
        T(name+' curved open back',[p(xx,.28,.85),p(xx*.5,.29,1.03),p(xx*1.4,.29,1.18),p(xx,.29,1.29)],.028,dark)
    if striped:
        for i in range(9): piece('cushion stripe %d'%i,(.025,.53,.009),(-.25+i*.062,-.02,.711),(.23,.23,.22))
chair('Left upholstered chair',.05,.38,-16,True)
chair('Right upholstered chair',2.48,.05,-25,False)
# floor lamp behind table
R('Lamp slender stem',.018,(1.85,2.60,.05),(1.85,2.60,1.68),(.52,.50,.43))
R('Lamp angled neck',.018,(1.85,2.60,1.68),(1.65,2.60,1.90),(.52,.50,.43))
node=ball(.12,center=(1.65,2.60,1.88),color=(.70,.70,.65)); node.resize((1,1,.45),pivot=(1.65,2.60,1.88)); add('Lamp shade',node)
# papers, cup, saucer, small vase and flowers
B('Paper on tabletop',(.55,.36,.006),(.95,1.02,1.075),(.79,.78,.72))
node=ball(.105,center=(.55,1.16,1.075),color=(.75,.74,.68)); node.resize((1,1,.12),pivot=(.55,1.16,1.075)); add('Saucer',node)
R('Small cup',.065,(.55,1.16,1.08),(.55,1.16,1.16),(.78,.77,.72))
R('Flower vase',.065,(1.15,1.35,1.07),(1.15,1.35,1.28),(.39,.47,.37))
for i in range(5):
    x=1.15+random.uniform(-.09,.09); y=1.35+random.uniform(-.07,.07); z=1.42+random.uniform(0,.13)
    R('Flower stem %d'%i,.009,(1.15,1.35,1.20),(x,y,z),(.19,.33,.12))
    add('Flower blossom %d'%i,ball(.035,center=(x,y,z),color=(.68,.12,.10) if i%2 else (.76,.52,.10)))
# picture on right wall
B('Picture frame',( .055,.72,.52),(3.55,2.07,2.38),(.49,.32,.16))
B('Picture mat',(.012,.63,.43),(3.51,2.07,2.38),(.79,.77,.67))
B('Picture artwork',(.014,.49,.30),(3.50,2.07,2.38),(.58,.64,.51))
realize(scene)
# Shape the pointed glazing as separate editable mesh surfaces.
for k,(cx,w,peak) in enumerate(windows):
    verts=[(cx-w/2,3.575,2.55)]
    for i in range(21):
        u=-1+2*i/20
        z=2.55+(peak-2.55)*(1-abs(u)**1.65)**.72
        verts.append((cx+u*w/2,3.575,z))
    verts.append((cx+w/2,3.575,2.55))
    mesh=bpy.data.meshes.new('Pointed glazing mesh %d'%k); mesh.from_pydata(verts,[],[list(range(len(verts)))]); mesh.update()
    obj=bpy.data.objects.new('Pointed upper glazing %d'%k,mesh); bpy.context.collection.objects.link(obj)
    mat=bpy.data.materials.new('Daylight glass %d'%k); mat.diffuse_color=(.72,.80,.76,1); obj.data.materials.append(mat)
# Give timber a modest sheen.
for mat in bpy.data.materials:
    if mat.diffuse_color[0] > mat.diffuse_color[1]*1.45 and mat.diffuse_color[0] > mat.diffuse_color[2]*2:
        mat.diffuse_color[3]=1
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs: bs.inputs['Roughness'].default_value=.29
world=bpy.data.worlds.new('Soft daylight world') if not bpy.data.worlds else bpy.data.worlds[0]
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.70,.74,.70,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
set_view((0,-9.3,3.0),(.05,2.2,1.75),lens=28)
area_emitter((-.8,2.7,3.3),power=450,size=3,target=(0,-1,0.7),color=(1.0,.94,.85))
area_emitter((1,-4,4),power=500,size=5,target=(0,1,1),color=(.86,.90,1.0))