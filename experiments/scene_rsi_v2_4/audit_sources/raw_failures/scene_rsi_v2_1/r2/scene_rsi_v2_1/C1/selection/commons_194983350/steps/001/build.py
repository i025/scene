from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(23)

# Inventory, normalized image coordinates:
# Ceiling (.00,.00)-(1,.20): colored rectangular panels in a black grid.
# Shelving (.00,.20)-(1,.56): dark horizontal rails, pale dividers,
# bright rear openings, three orderly rows of small potted plants.
# Sofa (.00,.55)-(.91,.87): magenta tufted back, seat and base;
# orange round cushion at (.25,.66), purple cushion at (.80,.70).
# Table (.33,.63)-(.71,.87): round timber top, slender black pedestal,
# small glassware. It overlaps the sofa and is partly hidden by the chair.
# Green chair (.13,.75)-(.59,1): curved upholstered back and thin legs.
# Right dark cabinet (.88,.57)-(1,1), foliage above; tan chair bottom right.
# Hidden furniture backs and room depth are uncertain.
scene = Scene('Colorful cafe')
dark=(.035,.055,.06)
pink=(.57,.035,.29)
wood=(.43,.23,.085)

def addasset(name):
    a=Asset(name); scene.include(name,a); return a
def bx(a,n,size,c,col,r=0):
    a.include(n,fillet_box(size,r,center=c,color=col) if r else box(size,center=c,color=col))
def sphere(a,n,c,scale,col):
    p=ball(1,center=c,color=col); p.resize(scale); a.include(n,p)
def line(a,n,p,q,r,col):
    a.include(n,rod(r,start=p,end=q,color=col))

arch=addasset('Room architecture')
bx(arch,'floor',(12,15,.12),(0,0,-.08),(.55,.52,.43))
# Discrete large floor tiles and visible grout lines.
for x in range(-6,7):
    bx(arch,'floor_joint_x'+str(x),(.012,14,.003),(x*.72,0,-.015),(.29,.29,.27))
for j in range(-7,6):
    bx(arch,'floor_joint_y'+str(j),(12,.012,.003),(0,j*.72,-.014),(.29,.29,.27))
bx(arch,'back wall',(10,.15,4.7),(0,2.65,2.3),(.81,.80,.68))
# Light-filled glazed openings behind the display.
for i,x in enumerate([-2.3,-1.15,0,1.15,2.3]):
    bx(arch,'window_'+str(i),(.94,.045,2.65),(x,2.53,2.44),(.84,.94,.92))
    bx(arch,'gold pier_'+str(i),(.14,.21,2.8),(x+.54,2.40,2.46),(.62,.43,.13))
    bx(arch,'window mullion_'+str(i),(.035,.06,2.6),(x,2.48,2.4),(.38,.47,.44))
bx(arch,'upper shadow',(9,.5,.24),(0,2.2,4.0),(.035,.08,.10))

ceiling=addasset('Stained multicolor ceiling')
palette=[(.05,.28,.42),(.08,.37,.23),(.63,.19,.22),(.73,.52,.12),
         (.24,.14,.43),(.10,.43,.46),(.45,.075,.28),(.35,.48,.22)]
for i in range(-6,7):
    for j in range(-7,5):
        x=i*.64; y=j*.73
        col=palette[(i*3+j*5)%len(palette)]
        bx(ceiling,f'panel_{i}_{j}',(.622,.712,.035),(x,y,4.13),col)
        # Irregular abstract pigment masses contained within each pane.
        for k in range(5):
            px=x+random.uniform(-.22,.22); py=y+random.uniform(-.24,.24)
            tint=tuple(min(1,c*random.uniform(1.3,2.0)+.08) for c in col)
            sphere(ceiling,f'pigment_{i}_{j}_{k}',(px,py,4.105),
                   (random.uniform(.065,.18),random.uniform(.04,.13),.004),tint)
for i in range(-7,8):
    bx(ceiling,'long grid'+str(i),(.027,10,.055),(i*.64-.32,-1,4.08),dark)
for j in range(-8,6):
    bx(ceiling,'cross grid'+str(j),(9,.029,.055),(0,j*.73-.365,4.08),dark)

shelf=addasset('Open plant display shelving')
for k,z in enumerate([1.79,2.49,3.19,3.91]):
    bx(shelf,'thick dark shelf '+str(k),(7.8,.46,.145),(0,1.82,z),(.065,.092,.10))
for row,z in enumerate([2.14,2.84,3.55]):
    for j,x in enumerate([-2.55,-1.42,-.28,.86,2.0,3.12]):
        bx(shelf,f'pale upright {row}_{j}',(.20,.35,.58),(x,1.85,z),(.77,.78,.69))
# A second line of warm interior trim shows through the openings.
for z in [2.32,3.03]:
    bx(arch,'rear brass rail'+str(z),(8,.08,.055),(0,2.38,z),(.56,.40,.19))
for i in range(9):
    sphere(arch,'rear small light'+str(i),(-2.5+i*.6,2.30,2.94),(.035,.028,.035),(1,.91,.64))

def plant(name,x,y,z,scale=1,flowers=False):
    a=addasset(name)
    # Pots have a slightly wider lip and a dark soil surface.
    a.include('pot',rod(.085*scale,length=.17*scale,
                       center=(x,y,z+.085*scale),color=(.065,.16,.125)))
    a.include('rim',rod(.099*scale,length=.025*scale,
                       center=(x,y,z+.165*scale),color=(.13,.23,.18)))
    a.include('soil',rod(.084*scale,length=.008,
                        center=(x,y,z+.181*scale),color=(.055,.044,.022)))
    for k in range(10):
        ang=k*2.399
        h=random.uniform(.19,.36)*scale
        dx=math.cos(ang)*random.uniform(.07,.19)*scale
        dy=math.sin(ang)*random.uniform(.055,.14)*scale
        p=(x+dx,y+dy,z+.17*scale+h)
        line(a,'stem'+str(k),(x,y,z+.16*scale),p,.008*scale,(.09,.25,.08))
        leaf=ball(1,center=(x+dx*.85,y+dy*.85,z+.17*scale+h*.78),
                  color=random.choice([(.07,.28,.12),(.14,.38,.16),(.21,.43,.16)]))
        leaf.resize((.036*scale,.025*scale,.12*scale))
        leaf.turn(euler=(math.degrees(dy*3),math.degrees(-dx*3),k*37))
        a.include('leaf'+str(k),leaf)
        if flowers and k%2==0:
            for t in range(3):
                sphere(a,f'flower{k}_{t}',(p[0]+.022*t,p[1],p[2]),
                       (.025*scale,.022*scale,.025*scale),(.87,.92,.79))
    return a
for row,z in enumerate([1.87,2.57,3.27]):
    for j,x in enumerate([-2.12,-1.04,.11,1.27,2.43]):
        plant(f'Shelf plant {row} {j}',x,1.65,z,.8 if row==1 else .95,
              flowers=(j+row)%3==1)
        if j in [1,3]:
            plant(f'Companion plant {row} {j}',x+.23,1.78,z,.62,True)

sofa=addasset('Magenta tufted banquette')
bx(sofa,'lower upholstered plinth',(5.15,.98,.46),(0,.79,.39),pink,.085)
bx(sofa,'seat cushion',(5.12,1.02,.25),(0,.63,.73),(.66,.045,.34),.105)
bx(sofa,'back foundation',(5.2,.28,.91),(0,1.14,1.22),(.53,.029,.26),.12)
# Soft convex tuft panels and recessed button centers.
for row in range(3):
    for col in range(15):
        x=-2.52+col*.36+(row%2)*.16
        z=.98+row*.28
        sphere(sofa,f'tuft pad {row}_{col}',(x,.964,z),(.235,.115,.205),
               (.58+random.uniform(-.035,.035),.032,.29+random.uniform(-.025,.025)))
for row in range(3):
    for col in range(15):
        x=-2.4+col*.36+(row%2)*.17
        z=1.04+row*.27
        sphere(sofa,f'button {row}_{col}',(x,.837,z),(.022,.012,.021),(.35,.016,.16))
for x in [-2.35,2.35]:
    line(sofa,'short foot'+str(x),(x,.5,.03),(x,.5,.23),.045,(.11,.075,.045))
# Round velvet cushions, flattened toward the camera.
for name,x,z,r,col in [('ochre',-.97,1.15,.31,(.65,.255,.065)),
                       ('purple',1.16,1.03,.34,(.51,.045,.32)),
                       ('orange partly hidden',.51,.99,.27,(.63,.23,.055))]:
    sphere(sofa,name+' pillow',(x,.55,z),(r,.13,r),col)
    pts=[]
    for k in range(65):
        t=k*2*math.pi/64
        pts.append((x+math.cos(t)*r*.95,.416,z+math.sin(t)*r*.95))
    sofa.include(name+' piping',sweep_tube(points=pts,radius=.008,color=tuple(v*.8 for v in col)))

table=addasset('Round cafe table')
table.include('wooden top',rod(.66,length=.065,center=(.05,-.03,1.075),color=wood))
table.include('top honey surface',rod(.65,length=.012,center=(.05,-.03,1.114),color=(.56,.32,.12)))
for i in range(8):
    # restrained grain strips on the tabletop
    yy=-.54+i*.14
    width=2*math.sqrt(max(.01,.63**2-yy**2))
    bx(table,'wood grain'+str(i),(width,.006,.002),(.05,yy-.03,1.121),(.43,.25,.10))
for x in [-.11,.11]:
    for y in [-.12,.10]:
        line(table,f'pedestal {x}_{y}',(.05+x,-.03+y,.08),(.05+x,-.03+y,1.04),.019,dark)
table.include('foot ring',rod(.27,length=.025,center=(.05,-.03,.09),color=dark))
bx(table,'small black napkin holder',(.17,.12,.095),(-.16,-.02,1.17),(.07,.075,.07),.012)
bx(table,'napkins',(.12,.07,.02),(-.16,-.02,1.225),(.79,.78,.67))
table.include('clear tumbler',rod(.058,length=.10,center=(.16,-.06,1.17),color=(.72,.78,.74),opacity=.28))
table.include('saucer',rod(.095,length=.014,center=(.26,.01,1.132),color=(.75,.76,.66)))
table.include('small glass',rod(.052,length=.075,center=(.26,.01,1.175),color=(.8,.83,.77),opacity=.35))
line(table,'slim bud vase',(-.035,.17,1.13),(-.035,.17,1.34),.027,(.68,.73,.67))
line(table,'single twig',(-.035,.17,1.31),(-.04,.17,1.53),.004,(.25,.29,.12))

chair=addasset('Foreground green curved chair')
cx=-.49; cy=-1.61
chair.include('seat',rod(.46,length=.12,center=(cx,cy,.56),color=(.035,.19,.105)))
# Upright panels form a continuous rounded barrel back, open toward the table.
for k in range(33):
    angle=math.radians(183+k*174/32)
    x=cx+.49*math.cos(angle); y=cy+.39*math.sin(angle)
    p=fillet_box((.066,.095,.49),.025,center=(x,y,.86),color=(.035,.20,.12))
    p.turn(axis='+z',degrees=math.degrees(angle)+90)
    chair.include('curved back panel'+str(k),p)
pts=[(cx+.49*math.cos(math.radians(183+k*174/64)),
      cy+.39*math.sin(math.radians(183+k*174/64)),1.105) for k in range(65)]
chair.include('rounded top piping',sweep_tube(points=pts,radius=.022,color=(.045,.24,.145)))
for dx in [-.32,.32]:
    for dy in [-.24,.24]:
        line(chair,f'leg{dx}{dy}',(cx+dx*1.08,cy+dy*1.1,.0),(cx+dx,cy+dy,.55),.021,dark)
# Partial tan seats in the lower corners.
tan=addasset('Cropped tan chairs')
for side,x,y in [('right',1.45,-2.0),('left',-1.95,-.45)]:
    tan.include(side+' seat',rod(.43,length=.10,center=(x,y,.52),color=(.58,.38,.19)))
    for k in range(22):
        a=math.radians(185+k*160/21)
        p=fillet_box((.074,.08,.49),.025,
                     center=(x+.46*math.cos(a),y+.35*math.sin(a),.80),
                     color=(.63,.43,.24))
        p.turn(axis='+z',degrees=math.degrees(a)+90)
        tan.include(side+' curved back '+str(k),p)

cab=addasset('Dark right foreground cabinet')
bx(cab,'cabinet body',(.75,1.15,1.63),(1.95,.12,.82),(.055,.047,.046))
bx(cab,'projecting top',(.86,1.25,.09),(1.95,.10,1.69),(.055,.065,.05))
plant('Large plant on right cabinet',2.03,.42,1.73,1.45)
# Broad leaves projecting left from the cropped plant.
fol=addasset('Right broad foliage')
for k in range(7):
    p=(1.85+random.uniform(-.3,.25),.55+random.uniform(-.2,.2),2.25+random.uniform(-.2,.65))
    line(fol,'broad stem'+str(k),(2.1,.6,1.85),p,.016,(.10,.23,.085))
    leaf=ball(1,center=p,color=(.035,.21,.095))
    leaf.resize((.12,.035,.37)); leaf.turn(euler=(25,-45+k*12,k*20))
    fol.include('broad leaf'+str(k),leaf)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('World')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value=(.68,.75,.76,1)
    bg.inputs['Strength'].default_value=.38
set_view((0,-6.65,2.39),(0,.85,2.13),lens=47)
cam=sc.camera
cam.data.sensor_fit='VERTICAL'
cam.data.sensor_height=32
area_emitter((-.8,-2.6,3.7),power=430,size=4.0,target=(0,.7,1.3),color=(1,.86,.72))
area_emitter((0,2.2,3.25),power=600,size=3.5,target=(0,0,1.8),color=(.83,.97,1))
area_emitter((-3,0,2.8),power=220,size=2.5,target=(0,1,1.4))
# Materials stay separate for furniture, plants, architecture and colored panes.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.66
        if 'glass' in mat.name.lower():
            bs.inputs['Roughness'].default_value=.18
sc.render.resolution_x=342
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.view_settings.view_transform='AgX'
