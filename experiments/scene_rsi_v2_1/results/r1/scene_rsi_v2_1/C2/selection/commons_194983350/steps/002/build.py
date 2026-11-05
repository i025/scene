from sceneact import *
import bpy, math, random
random.seed(12)

# Reference inventory, normalized image bounds:
# Stained colored ceiling (0,0)-(1,.20), dark rectangular perspective grid.
# Open partition (0,.19)-(1,.56): four charcoal bands, pale piers,
# three rows of small leafy potted plants and bright room visible through gaps.
# Magenta sofa (0,.55)-(.91,.90): shallow scalloped tufted back, broad seat,
# orange circular pillow at (.26,.66), plum pillow at (.80,.69).
# Oak circular table (.33,.64)-(.71,.71), black narrow supports below;
# bottle, napkins and shallow glass dish occupy its center.
# Emerald chair (.13,.75)-(.58,1), curved thin back and exposed dark legs.
# Cropped tan chairs at left (.0,.69)-(.07,.82) and right (.75,.84)-(1,1).
# Dark cabinet (.89,.56)-(1,1), with large foliage extending upward.
# Pale tiled floor visible around foreground furniture.
# Hidden sofa ends and rear-room furnishings remain uncertain.
#
# Render comparison: first camera magnified foreground objects, clipping cabinet
# and tan chair. Widen field; retain shelf arrangement. Reduce table diameter,
# lower sofa back locally, move green chair right, and use a thin curved shell.
# Reduce plant leaf size and lighting washout; retain all inventory assets.
#
# Expanded count estimate: architecture/floor 48, ceiling 81,
# 19 plants * 17 = 323, sofa 87, table/props 19,
# chairs 34, cabinet/foliage 18: approximately 610 primitive meshes.
# No booleans, fillet boxes, cloned microgeometry, or long sweep paths.

scene=Scene('Cafe reconstruction revised')
dark=(.035,.055,.06)
cream=(.77,.75,.60)
pink=(.39,.012,.19)
green=(.016,.115,.063)
wood=(.43,.205,.065)

def asset(name):
    a=Asset(name)
    scene.include(name,a)
    return a

def boxpart(a,n,s,c,col):
    p=box(size=s,center=c,color=col)
    a.include(n,p)
    return p

def ell(a,n,c,s,col):
    p=ball(1,center=c,color=col)
    p.resize(s)
    a.include(n,p)
    return p

def rodpart(a,n,r,p,q,col):
    v=rod(radius=r,start=p,end=q,color=col)
    a.include(n,v)
    return v

floor=asset('pale tiled floor')
boxpart(floor,'floor',(12,13,.12),(0,1,-.08),(.60,.58,.49))
for i in range(-3,4):
    boxpart(floor,'long grout '+str(i),(.012,11,.004),(i,0,-.016),(.28,.28,.25))
for i in range(-4,5):
    boxpart(floor,'cross grout '+str(i),(10,.012,.004),(0,i,-.015),(.28,.28,.25))

rear=asset('bright cafe behind partition')
boxpart(rear,'warm wall',(10,.12,3.8),(0,3.4,1.9),(.75,.64,.37))
for i,x in enumerate([-2.2,-1.1,0,1.1,2.2]):
    boxpart(rear,'bright window '+str(i),(.93,.035,2.4),(x,3.31,1.62),(.87,.96,.94))
    boxpart(rear,'window mullion '+str(i),(.045,.09,2.6),(x-.51,3.24,1.7),(.20,.26,.25))
boxpart(rear,'ochre fascia',(6,.12,.22),(0,3.17,2.63),(.58,.34,.075))
for i,x in enumerate([-1.65,-.75,.5,1.55]):
    rodpart(rear,'pendant cord '+str(i),.008,(x,2.8,2.74),(x,2.8,2.42),dark)
    ell(rear,'pendant globe '+str(i),(x,2.8,2.40),(.047,.047,.065),(1,.95,.76))

shelf=asset('open architectural plant shelves')
shelf_y=1.85
shelf_levels=[1.58,2.18,2.77,3.35]
for i,z in enumerate(shelf_levels):
    boxpart(shelf,'charcoal shelf beam '+str(i),(5.7,.35,.13),(0,shelf_y,z),(.067,.095,.105))
for row in range(3):
    lo=shelf_levels[row]+.065
    hi=shelf_levels[row+1]-.065
    xs=[-2.10,-1.20,-.24,.82,1.83]
    if row==1:
        xs=[-2.10,-1.43,-.43,.65,1.63]
    for j,x in enumerate(xs):
        boxpart(shelf,'pale pier %d %d'%(row,j),(.19,.35,hi-lo),(x,shelf_y,(lo+hi)/2),cream)
boxpart(shelf,'top shadow',(6,.5,.10),(0,1.9,3.45),(.025,.045,.052))

def plant(name,x,y,z,s):
    a=asset(name)
    rodpart(a,'small tapered-looking dark pot',.057*s,(x,y,z),(x,y,z+.12*s),(.035,.105,.075))
    for k in range(8):
        ang=k*2.399
        spread=(.07+.035*(k%3))*s
        height=(.21+.065*random.random())*s
        end=(x+math.cos(ang)*spread,y+math.sin(ang)*spread,z+height)
        rodpart(a,'fine stem '+str(k),.0045*s,(x,y,z+.085*s),end,(.075,.24,.07))
        leaf=ell(a,'small leafy cluster '+str(k),end,(.028*s,.018*s,.061*s),
                 [(.025,.22,.065),(.075,.34,.10),(.11,.38,.13)][k%3])
        leaf.turn(axis='+y',degrees=math.sin(ang)*46)
        leaf.turn(axis='+z',degrees=ang*180/math.pi)
    return a

for row,z in enumerate([1.645,2.245,2.835]):
    xs=[-1.88,-1.05,-.49,.28,1.05,1.65]
    if row==1:
        xs=[-2.1,-1.42,-.90,-.06,.52,1.30,1.91]
    for j,x in enumerate(xs):
        plant('shelf plant %d %d'%(row,j),x,1.63,z,.83+random.random()*.15)

sofa=asset('magenta velvet banquette')
boxpart(sofa,'low dark upholstered plinth',(4.6,.81,.17),(0,.89,.20),(.18,.008,.07))
ell(sofa,'broad rounded front base',(0,.78,.43),(2.35,.54,.25),pink)
# Back compressed around seat height, leaving the matching seat unchanged.
def backz(z):
    return .64+(z-.64)*.84
boxpart(sofa,'continuous padded back',(4.65,.28,.78),(0,1.29,backz(1.10)),pink)
for i in range(15):
    x=-2.22+i*.32
    ell(sofa,'soft scalloped crown '+str(i),(x,1.245,backz(1.55)),
        (.205,.17,.115),(.42,.014,.21))
for row,z in enumerate([.87,1.16,1.42]):
    for j in range(14):
        x=-2.1+j*.33+(row%2)*.12
        ell(sofa,'tufted padded field %d %d'%(row,j),(x,1.105,backz(z)),
            (.215,.052,.151),(.40,.012,.198))
        ell(sofa,'recessed button %d %d'%(row,j),(x+.14,1.046,backz(z+.10)),
            (.018,.008,.018),(.20,.004,.075))
for j,x in enumerate([-1.52,-.51,.51,1.52]):
    ell(sofa,'broad seat cushion '+str(j),(x,.76,.64),(.56,.48,.13),(.44,.015,.22))
ell(sofa,'orange circular pillow',(-.81,.85,1.10),(.265,.115,.28),(.57,.18,.034))
ell(sofa,'plum circular pillow',(.91,.78,1.04),(.28,.115,.28),(.35,.013,.18))
ell(sofa,'partly hidden ochre pillow',(.38,1.00,.96),(.27,.105,.23),(.49,.15,.025))

table=asset('round oak cafe table')
tx,ty=.05,.01
table_z=1.12
rodpart(table,'thin oak tabletop',.49,(tx,ty,table_z-.06),(tx,ty,table_z),wood)
rodpart(table,'golden rounded tabletop edge',.492,(tx,ty,table_z-.017),(tx,ty,table_z),(.52,.27,.085))
rodpart(table,'black center column',.035,(tx,ty,.10),(tx,ty,table_z-.06),(.018,.025,.023))
for i,angle in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
    rodpart(table,'splayed foot '+str(i),.021,(tx,ty,.12),
            (tx+.31*math.cos(angle),ty+.31*math.sin(angle),.045),dark)
for i,x in enumerate([-.09,.12]):
    rodpart(table,'thin outer pedestal brace '+str(i),.014,(x,ty,.12),(x,ty,table_z-.06),dark)

props=asset('bottle napkin holder and glass ashtray')
boxpart(props,'dark napkin holder',(.14,.085,.075),(-.11,-.03,table_z+.038),(.035,.045,.04))
boxpart(props,'cream paper napkins',(.105,.018,.06),(-.11,-.033,table_z+.073),(.76,.75,.65))
rodpart(props,'bottle body',.026,(.025,.05,table_z),(.025,.05,table_z+.14),(.47,.61,.53))
rodpart(props,'bottle neck',.011,(.025,.05,table_z+.13),(.025,.05,table_z+.21),(.48,.61,.54))
rodpart(props,'small silver bottle cap',.013,(.025,.05,table_z+.20),(.025,.05,table_z+.22),(.28,.30,.25))
rodpart(props,'shallow glass ashtray',.080,(.17,-.035,table_z),(.17,-.035,table_z+.026),(.61,.64,.55))
rodpart(props,'ashtray recessed center',.058,(.17,-.035,table_z+.024),(.17,-.035,table_z+.028),(.36,.40,.34))

chair=asset('foreground curved emerald chair')
cx,cy=-.35,-1.42
ell(chair,'upholstered seat',(cx,cy,.52),(.46,.37,.075),green)
# Thin barrel shell: an arc with a broad center and wings curling toward table.
# Short individual panels preserve the open interior and avoid a solid pillow.
arc_count=11
for i in range(arc_count):
    angle=math.pi+math.pi*i/(arc_count-1)
    x=cx+.46*math.cos(angle)
    y=cy+.32*math.sin(angle)
    p=boxpart(chair,'curved shell panel '+str(i),(.151,.060,.38),
              (x,y,.83),green)
    p.turn(axis='+z',degrees=angle*180/math.pi+90)
    j=min(i+1,arc_count-1)
    nextangle=math.pi+math.pi*j/(arc_count-1)
    if i<arc_count-1:
        rodpart(chair,'soft continuous upper rim '+str(i),.025,
                (x,y,1.025),
                (cx+.46*math.cos(nextangle),cy+.32*math.sin(nextangle),1.025),
                (.020,.14,.078))
for i,(dx,dy) in enumerate([(-.32,-.21),(.32,-.21),(-.30,.21),(.30,.21)]):
    rodpart(chair,'slender dark leg '+str(i),.019,
            (cx+dx,cy+dy,.51),(cx+dx*1.16,cy+dy*1.16,-.02),(.025,.035,.026))

tan=asset('cropped right tan chair')
ell(tan,'tan seat',(1.30,-1.90,.66),(.49,.38,.12),(.53,.32,.14))
ell(tan,'curving tan back',(1.30,-2.12,.93),(.49,.065,.27),(.62,.39,.19))
for i,x in enumerate([1.0,1.60]):
    rodpart(tan,'black leg '+str(i),.022,(x,-1.9,.61),(x,-1.9,-.1),dark)
left=asset('cropped left tan chair')
ell(left,'visible tan chair edge',(-1.65,-.18,.65),(.33,.34,.14),(.47,.28,.08))

cab=asset('right dark cabinet and broad foliage')
boxpart(cab,'tall black-brown cabinet',(.66,.64,1.49),(1.57,.41,.745),(.034,.025,.025))
boxpart(cab,'projecting dark top',(.76,.72,.055),(1.57,.41,1.515),(.055,.065,.037))
for i in range(8):
    ang=i*2.4
    base=(1.64,.62,1.55)
    tip=(1.64+math.cos(ang)*.43,.62+math.sin(ang)*.30,1.94+random.random()*.47)
    rodpart(cab,'broad foliage stem '+str(i),.011,base,tip,(.035,.17,.048))
    leaf=ell(cab,'large lance leaf '+str(i),tip,(.105,.027,.27),(.018,.15,.044))
    leaf.turn(axis='+y',degrees=43*math.cos(ang))
    leaf.turn(axis='+z',degrees=ang*180/math.pi)

ceiling=asset('colored mottled glass ceiling')
palette=[(.025,.28,.30),(.025,.105,.38),(.22,.48,.31),(.80,.40,.035),
         (.49,.012,.19),(.13,.36,.085),(.025,.29,.49),(.68,.62,.30)]
pw,pd=.70,.66
for ix in range(9):
    for iy in range(7):
        boxpart(ceiling,'glass panel %d %d'%(ix,iy),(pw-.029,pd-.029,.035),
                ((ix-4)*pw,-1.55+iy*pd,3.53),palette[(ix*3+iy*5)%len(palette)])
for ix in range(10):
    boxpart(ceiling,'long dark grid rail '+str(ix),(.029,4.68,.055),
            ((ix-4.5)*pw,.43,3.50),(.014,.025,.026))
for iy in range(8):
    boxpart(ceiling,'cross dark grid rail '+str(iy),(6.34,.029,.055),
            (0,-1.88+iy*pd,3.50),(.014,.025,.026))

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
bg=nodes.get('Background')
if bg is None:
    bg=nodes.new('ShaderNodeBackground')
out=nodes.get('World Output')
if out is None:
    out=nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(bg.outputs['Background'],out.inputs['Surface'])
bg.inputs['Color'].default_value=(.68,.76,.80,1)
bg.inputs['Strength'].default_value=.22

# Restrained material variation; colored ceiling receives cloudlike marbling.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nd=mat.node_tree.nodes
    links=mat.node_tree.links
    bs=nd.get('Principled BSDF')
    if bs is None:
        continue
    col=tuple(bs.inputs['Base Color'].default_value)
    bs.inputs['Roughness'].default_value=.65
    if col[0]>.28 and col[2]>.12 and col[1]<.04:
        bs.inputs['Roughness'].default_value=.9
        if 'Sheen Weight' in bs.inputs:
            bs.inputs['Sheen Weight'].default_value=.18
    noise=nd.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=42
    noise.inputs['Detail'].default_value=2
    bump=nd.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.065
    bump.inputs['Distance'].default_value=.009
    links.new(noise.outputs['Fac'],bump.inputs['Height'])
    links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if any(sum(abs(col[j]-p[j]) for j in range(3))<.015 for p in palette):
        noise.inputs['Scale'].default_value=6
        noise.inputs['Detail'].default_value=3
        ramp=nd.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.28
        ramp.color_ramp.elements[0].color=(col[0]*.40,col[1]*.40,col[2]*.40,1)
        ramp.color_ramp.elements[1].position=.70
        ramp.color_ramp.elements[1].color=tuple(min(1,c*.8+.30) for c in col[:3])+(1,)
        links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.37

set_view((0,-5.25,1.86),(0,1.0,1.84),lens=40)
sc.camera.data.sensor_fit='VERTICAL'
sc.camera.data.sensor_height=32
area_emitter((0,-2.3,3.25),power=180,size=4,target=(0,.9,1),color=(1,.88,.75))
area_emitter((-.7,3.05,2.45),power=480,size=3,target=(0,.4,1.4),color=(.86,.97,1))
area_emitter((-3,-.8,2.4),power=105,size=2.7,target=(0,.8,1),color=(1,.92,.82))
sc.render.resolution_x=342
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
