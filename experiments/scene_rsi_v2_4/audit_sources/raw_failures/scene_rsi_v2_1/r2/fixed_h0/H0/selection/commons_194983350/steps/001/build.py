from sceneact import *
import bpy, math, random
random.seed(18)

scene = Scene('Colorful cafe')
charcoal=(.105,.135,.14)
pink=(.57,.045,.29)
wood=(.43,.225,.085)
green=(.025,.19,.105)

def add(name,node):
    scene.include(name,node)
    return node

def ellipsoid(name,center,scale,color):
    n=ball(1,center=center,color=color)
    n.resize(scale)
    return add(name,n)

def cylinder(name,r,h,center,color):
    return add(name,rod(r,length=h,center=center,color=color))

# Pale stone floor and bright room beyond the open shelving.
add('floor',box((12,13,.12),center=(0,0,-.08),color=(.63,.61,.55)))
for x in range(-6,7):
    add('floor joint x'+str(x),box((.012,12,.003),center=(x*.7,0,-.015),color=(.43,.43,.39)))
for y in range(-5,8):
    add('floor joint y'+str(y),box((12,.012,.003),center=(0,y*.8,-.013),color=(.46,.45,.40)))
add('back cream wall',box((11,.15,3.3),center=(0,3.5,1.65),color=(.83,.81,.68)))
for x in [-2.7,-1.65,-.55,.55,1.65,2.7]:
    add('bright rear glazing'+str(x),box((.82,.04,2.45),center=(x,3.38,1.75),color=(.85,.94,.92)))
    add('rear window mullion'+str(x),box((.035,.08,2.65),center=(x-.44,3.3,1.7),color=(.26,.31,.29)))
add('rear counter',box((7,.6,.12),center=(0,3.05,1.02),color=(.36,.31,.22)))
for x in [-2.1,-.7,.7,2.1]:
    add('warm rear column'+str(x),box((.14,.21,2.9),center=(x,3.1,1.5),color=(.73,.48,.12)))
for x in [-1.4,-.4,.5,1.3]:
    cylinder('pendant wire'+str(x),.008,.62,(x,2.95,2.83),(.2,.19,.13))
    ellipsoid('warm pendant bulb'+str(x),(x,2.95,2.49),(.045,.045,.065),(1,.87,.56))

# Dark open divider, with three rows of staggered rectangular niches.
for i,z in enumerate([1.48,2.00,2.53,3.04]):
    add('horizontal shelf '+str(i),box((7,.35,.115),center=(0,2.12,z),color=charcoal))
rows=[[-2.6,-1.65,-.65,.46,1.62,2.65],
      [-2.6,-1.95,-.63,.55,1.9,2.7],
      [-2.6,-1.75,-.60,.48,1.68,2.7]]
for row,z in enumerate([1.74,2.265,2.785]):
    for j,x in enumerate(rows[row]):
        add('shelf upright %s %s'%(row,j),
            box((.115,.35,.43),center=(x,2.12,z),color=(.31,.33,.30)))

def plant(name,x,y,z,size=.32):
    potcol=random.choice([(.07,.10,.085),(.19,.22,.17),(.31,.33,.25)])
    cylinder(name+' pot',size*.19,size*.33,(x,y,z+size*.165),potcol)
    cylinder(name+' rim',size*.215,size*.045,(x,y,z+size*.32),potcol)
    cylinder(name+' soil',size*.175,.012,(x,y,z+size*.34),(.065,.048,.027))
    for k in range(random.randint(8,13)):
        a=random.uniform(0,2*math.pi)
        spread=random.uniform(.14,.5)*size
        h=random.uniform(.48,1.05)*size
        end=(x+math.cos(a)*spread,y+math.sin(a)*spread,z+size*.29+h)
        start=(x,y,z+size*.28)
        add(name+' stem'+str(k),rod(.006,start=start,end=end,color=(.12,.26,.065)))
        col=random.choice([(.06,.28,.10),(.12,.37,.12),(.16,.40,.18),(.055,.23,.12)])
        leaf=ball(1,center=end,color=col)
        leaf.resize((size*.07,size*.035,size*.28))
        leaf.turn(euler=(math.sin(a)*31,math.cos(a)*35,math.degrees(a)))
        add(name+' leaf'+str(k),leaf)
        if k%2==0:
            mid=tuple(start[i]*.35+end[i]*.65 for i in range(3))
            l=ball(1,center=mid,color=col)
            l.resize((size*.12,size*.04,size*.19))
            l.turn(euler=(25,40,math.degrees(a)+35))
            add(name+' side leaf'+str(k),l)

for row,z in enumerate([1.54,2.06,2.59]):
    xs=[-2.3,-1.25,-.25,.83,1.45,2.23] if row!=1 else [-2.25,-1.35,-.15,.45,1.29,2.25]
    for j,x in enumerate(xs):
        plant('niche plant %d %d'%(row,j),x,2.04,z,random.uniform(.27,.40))
# Additional plants behind the shelving.
for i,x in enumerate([-2.0,-.9,.25,1.3,2.4]):
    plant('rear plant'+str(i),x,2.95,1.08,.35)

# Jewel-colored ceiling tiles and a fine black supporting grid.
add('ceiling dark backing',box((9,10,.08),center=(0,.7,3.18),color=(.035,.065,.065)))
palette=[(.04,.28,.40),(.045,.17,.41),(.10,.40,.29),(.60,.48,.08),
         (.58,.07,.25),(.15,.42,.49),(.32,.43,.19),(.43,.19,.40)]
for ix in range(-7,8):
    for iy in range(-7,7):
        x=ix*.58
        y=iy*.59
        c=random.choice(palette)
        add('ceiling panel %d %d'%(ix,iy),box((.555,.565,.022),center=(x,y,3.12),color=c))
        # Small irregular islands of color evoke the mottled translucent panels.
        for k in range(6):
            tint=tuple(min(1,v*random.uniform(1.2,1.9)+.03) for v in c)
            patch=ball(1,center=(x+random.uniform(-.21,.21),y+random.uniform(-.20,.20),3.102),color=tint)
            patch.resize((random.uniform(.035,.13),random.uniform(.025,.10),.003))
            add('tile mottling %d %d %d'%(ix,iy,k),patch)
for ix in range(-8,9):
    add('ceiling longitudinal rail'+str(ix),box((.025,10,.035),center=(ix*.58-.29,0,3.095),color=(.025,.055,.055)))
for iy in range(-8,9):
    add('ceiling cross rail'+str(iy),box((9,.025,.035),center=(0,iy*.59-.295,3.095),color=(.025,.055,.055)))

# Broad purple velvet banquette.
add('sofa bottom plinth',fillet_box((4.6,.91,.32),radius=.06,center=(-.18,1.12,.29),color=(.39,.025,.19)))
add('sofa upholstered back',fillet_box((4.65,.25,.99),radius=.10,center=(-.18,1.52,.98),color=pink))
for i in range(4):
    add('sofa seat cushion'+str(i),fillet_box((1.15,.88,.22),radius=.095,center=(-1.91+i*1.15,1.00,.58),color=(.60,.052,.30)))
    add('seat piping'+str(i),sweep_tube(points=[(-2.46+i*1.15,.567,.57),(-1.39+i*1.15,.567,.57)],radius=.009,color=(.40,.025,.19)))
for x in [-2.43,2.07]:
    add('sofa rounded arm'+str(x),fillet_box((.30,1.05,.60),radius=.14,center=(x,1.02,.69),color=pink))
for x in [-2.2,1.8]:
    cylinder('sofa foot'+str(x),.035,.2,(x,.9,.12),(.12,.10,.08))

# Closely spaced tuft buttons and soft diamond creases.
for row in range(4):
    z=.76+row*.20
    for j in range(16):
        x=-2.35+j*.30+(row%2)*.15
        if x>2.1: continue
        ellipsoid('velvet button %d %d'%(row,j),(x,1.376,z),(.020,.012,.019),(.34,.018,.16))
        for dx,dz in [(-.082,.075),(.082,.075),(-.072,-.075),(.072,-.075)]:
            add('tuft crease %d %d %s %s'%(row,j,dx,dz),
                rod(.0035,start=(x,1.374,z),end=(x+dx,1.377,z+dz),color=(.45,.030,.23)))

# Three loosely round velvet cushions.
for name,center,scale,col,angle in [
    ('ochre left pillow',(-.92,1.11,.98),(.28,.13,.34),(.59,.24,.065),-12),
    ('ochre right pillow',(.58,1.12,.92),(.30,.13,.30),(.62,.27,.075),14),
    ('purple round pillow',(1.45,1.10,.88),(.33,.15,.34),(.55,.045,.28),-16)]:
    p=ellipsoid(name,center,scale,col)
    p.turn(axis='+y',degrees=angle)

# Central small round wood table, with black slender metal pedestal.
cylinder('round oak tabletop',.62,.065,(.10,.10,.94),wood)
cylinder('table edge',.62,.022,(.10,.10,.906),(.27,.12,.035))
for x,y in [(-.08,.04),(.10,.16),(.25,.04)]:
    cylinder('table vertical iron %.2f'%x,.017,.84,(x,y,.46),(.025,.041,.038))
for a in [0,120,240]:
    t=math.radians(a)
    add('table splayed foot'+str(a),rod(.017,start=(.1,.1,.16),end=(.1+.36*math.cos(t),.1+.36*math.sin(t),.025),color=(.028,.040,.034)))

# Condiments, ashtray, folded menu and little bottle on the table.
add('small menu holder',box((.15,.07,.12),center=(-.13,.15,1.035),color=(.065,.085,.077)))
add('menu white edge',box((.105,.009,.085),center=(-.13,.108,1.055),color=(.69,.70,.61)))
cylinder('clear ashtray',.084,.025,(.25,.13,.988),(.58,.61,.55))
cylinder('ashtray inner',.059,.027,(.25,.13,1.0),(.36,.40,.36))
cylinder('bottle body',.026,.15,(.045,.20,1.052),(.62,.68,.61))
cylinder('bottle neck',.012,.065,(.045,.20,1.155),(.57,.64,.58))
cylinder('bottle metal cap',.015,.019,(.045,.20,1.197),(.26,.29,.26))
add('bottle white label',box((.042,.006,.060),center=(.045,.173,1.055),color=(.90,.90,.82)))
cylinder('small salt shaker',.024,.075,(.13,.22,1.013),(.84,.85,.76))

# Foreground green molded chair, seen from behind.
cx,cy=-.32,-1.54
ellipsoid('green chair seat',(cx,cy,.43),(.49,.40,.075),(.028,.18,.105))
# Curved bucket back as a continuous swept surface approximated with overlapping rounded strips.
for i in range(29):
    a=math.radians(195+i*150/28)
    x=cx+.48*math.cos(a)
    y=cy+.38*math.sin(a)
    z=.70+.035*math.cos(a)
    panel=fillet_box((.080,.075,.43),radius=.034,center=(x,y,z),color=(.035,.20,.12))
    panel.turn(axis='+z',degrees=math.degrees(a)+90)
    add('green bucket back strip'+str(i),panel)
rim=[]
for i in range(35):
    a=math.radians(195+i*150/34)
    rim.append((cx+.48*math.cos(a),cy+.38*math.sin(a),.925+.035*math.cos(a)))
add('green chair top rolled lip',sweep_tube(points=rim,radius=.022,color=(.025,.16,.086)))
for i,(dx,dy) in enumerate([(-.32,-.22),(.32,-.22),(-.29,.23),(.29,.23)]):
    add('green chair metal leg'+str(i),rod(.019,start=(cx+dx,cy+dy,.42),end=(cx+dx*1.17,cy+dy*1.15,.015),color=(.035,.06,.045)))

# Cropped tan chairs at either edge of the photograph.
for side,x,y in [('left',-1.85,-.55),('right',1.30,-2.05)]:
    ellipsoid(side+' tan seat',(x,y,.43),(.47,.38,.07),(.54,.34,.17))
    for i in range(19):
        a=math.radians(192+i*155/18)
        px=x+.46*math.cos(a)
        py=y+.36*math.sin(a)
        n=fillet_box((.10,.07,.49),radius=.035,center=(px,py,.70),color=(.61,.40,.21))
        n.turn(axis='+z',degrees=math.degrees(a)+90)
        add(side+' chair back'+str(i),n)
    for dx in [-.29,.29]:
        for dy in [-.23,.23]:
            add(side+' leg'+str(dx)+str(dy),rod(.018,start=(x+dx,y+dy,.42),end=(x+dx*1.1,y+dy*1.1,.02),color=(.17,.13,.075)))

# Tall dark planter cropping the right edge.
add('right tall planter',box((.59,.65,1.48),center=(1.79,-.10,.74),color=(.075,.065,.066)))
add('planter upper rim',box((.64,.70,.07),center=(1.79,-.10,1.48),color=(.09,.09,.073)))
plant('large right plant',1.88,-.02,1.50,.66)
for i in range(9):
    a=random.uniform(0,6.28)
    pos=(1.82+random.uniform(-.30,.28),.0+random.uniform(-.16,.18),1.75+random.uniform(.0,.55))
    leaf=ellipsoid('large broad leaf'+str(i),pos,(.15,.045,.40),(.035,.22,.085))
    leaf.turn(euler=(random.uniform(-45,45),random.uniform(-65,65),math.degrees(a)))

realize(scene)
set_view((0,-4.50,1.64),(0,1.9,1.73),lens=69,sensor=36)
area_emitter((0,-2.0,3.0),power=420,size=4.0,target=(0,1,1.1),color=(1,.91,.82))
area_emitter((-.8,3.1,2.3),power=650,size=3.5,target=(0,0,1.2),color=(.86,.96,1))
area_emitter((-3,-.1,2.4),power=180,size=2.8,target=(0,1,1),color=(1,.86,.68))
world=bpy.context.scene.world
world.color=(.22,.22,.22)
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.render.resolution_x=342
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
# Rough cloth, matte leaves, and gently polished tabletops.
for obj in bpy.data.objects:
    if obj.type=='MESH':
        for poly in obj.data.polygons:
            poly.use_smooth=True
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.66
        if 'Sheen Weight' in bs.inputs:
            bs.inputs['Sheen Weight'].default_value=.12
