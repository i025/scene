from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(23)

# DISCREPANCY LEDGER, normalized image coordinates, top-left origin:
# High confidence, shared framing error: rendered partition has only ~3 openings
# across the frame, reference ~5; table width .64 versus .38; ceiling ends at
# y~.07 versus .19. Widen lens 72->48, preserving camera position and direction.
# This should shrink independent architectural and furniture landmarks together.
# Sofa upper anchor: rendered y~.57, reference .55; wider framing preserves it
# approximately while revealing the seat, floor, cabinet and foreground chairs.
# Table: rendered center (~.57,.87), reference (~.52,.67). Widening corrects
# width but leaves its top too low (~.75). Raise the top .34 world units, extend
# stems from their existing floor anchors, and reduce top radius .615->.56.
# Table contents retain their support on the raised top.
# Green chair: rendered shell only visible along bottom, reference .13-.58,
# y .75-.95. Wider framing reveals it; increase shell upper height .20 and seat
# height .10 while retaining leg floor contacts. Shell width is kept unchanged.
# Orange pillow: rendered center (~.07,.76), reference (~.26,.66). Wider lens
# gives (~.21,.67); move pillow .15 world units right, retain its seat contact.
# Sofa fabric: rendered bright hot pink, reference darker purple-magenta.
# Lower upholstery base values; retain tuft spacing and back support anchor.
# Ceiling: reference irregular colored panels, render mostly pale narrow strips.
# Correct framing first, then attach procedural glass materials by ceiling
# geometry position, since primitive names do not retain SceneAct member names.
# Hidden chair orientations, rear-room depth and sofa end geometry remain uncertain.
#
# INVENTORY / COMPONENT MASSES:
# Ceiling (0,0)-(1,.19); dark rails at y .20,.31,.43,.54.
# Partition posts near x .08,.39,.57,.77; plants rest on each horizontal rail.
# Sofa (-.08,.55)-(.90,.90), continuous back .55-.73, seat .73-.83,
# base .81-.88. Orange pillow center (.26,.66), purple (.79,.70).
# Table top (.33,.64)-(.71,.70), props supported above, thin stems below.
# Green chair (.13,.75)-(.58,1), curved shell above four floor-supported legs.
# Cabinet (.89,.56)-(1,.94); tan chair cropped at lower right.
# Named Parts separate support anchors, upholstery, tops, legs and shell masses.

scene = Scene('Colorful cafe corrected')
pink = (.39,.018,.205)
pink_light = (.46,.028,.255)
dark = (.065,.082,.083)
leaf_specs = []
shell_specs = []

def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def part(a,name):
    p=Part(name)
    a.include(name,p)
    return p

def add(a,name,node):
    a.include(name,node)
    return node

architecture=asset('Architecture')
add(architecture,'floor',box((12,12,.12),center=(0,1,-.08),color=(.65,.59,.47)))
for x in range(-5,6):
    add(architecture,'floor joint x%d'%x,box((.012,10,.004),center=(x*.75,0,-.015),color=(.43,.40,.34)))
for j in range(-5,7):
    add(architecture,'floor joint y%d'%j,box((10,.012,.004),center=(0,j*.8,-.014),color=(.43,.40,.34)))

rear=asset('Room beyond partition')
add(rear,'rear wall',box((7,.15,4),center=(0,3.55,1.95),color=(.82,.78,.62)))
for i,x in enumerate([-2.35,-1.32,-.25,.82,1.89]):
    add(rear,'window%d'%i,box((.76,.035,2.7),center=(x,3.44,2.1),color=(.9,.98,.94)))
    add(rear,'gold pier%d'%i,box((.10,.22,2.8),center=(x+.47,3.35,2.1),color=(.68,.45,.12)))
    add(rear,'mullion%d'%i,box((.025,.08,2.6),center=(x,3.38,2.1),color=(.35,.43,.39)))
add(rear,'counter',box((6,.45,.13),center=(0,3.13,2.18),color=(.38,.36,.27)))
for i in range(8):
    x=-2.5+i*.7
    add(rear,'pendant wire%d'%i,rod(.008,start=(x,3.1,3.6),end=(x,3.1,2.74),color=(.2,.2,.17)))
    add(rear,'pendant globe%d'%i,ball(.052,center=(x,3.1,2.7),color=(1,.86,.57)))

partition=asset('Open shelving partition')
rails=part(partition,'Horizontal supporting rails')
posts=part(partition,'Cream vertical dividers')
for i,z in enumerate([1.64,2.29,2.94,3.57]):
    add(rails,'rail%d'%i,box((5.7,.27,.145),center=(0,2.18,z),color=dark))
for i,x in enumerate([-2.35,-1.51,-.65,.22,1.09,1.96,2.8]):
    add(posts,'post%d'%i,box((.215,.22,1.9),center=(x,2.205,2.61),color=(.77,.76,.64)))
    add(posts,'shadow%d'%i,box((.023,.255,1.9),center=(x-.114,2.18,2.61),color=(.14,.18,.17)))

def plant(name,x,y,z,scale=1,potcolor=(.07,.12,.10),count=13):
    p=asset(name)
    pot=part(p,'Pot and support')
    stems=part(p,'Foliage stems')
    add(pot,'pot',rod(.082*scale,length=.13*scale,center=(x,y,z+.065*scale),color=potcolor))
    add(pot,'rim',rod(.091*scale,length=.025*scale,center=(x,y,z+.135*scale),color=potcolor))
    for k in range(count):
        ang=random.random()*math.tau
        length=random.uniform(.20,.38)*scale
        spread=random.uniform(.045,.18)*scale
        start=(x+random.uniform(-.04,.04)*scale,y+random.uniform(-.035,.035)*scale,z+.12*scale)
        end=(x+math.cos(ang)*spread,y+math.sin(ang)*spread,z+.12*scale+length)
        add(stems,'stem%d'%k,rod(.004*scale,start=start,end=end,color=(.12,.28,.07)))
        col=random.choice([(.065,.29,.10),(.12,.39,.12),(.025,.23,.12),(.22,.43,.12)])
        leaf_specs.append((name+'_leaf%d'%k,start,end,.025*scale,ang,col))
        if k%3==0:
            mid=tuple(start[q]+(end[q]-start[q])*.55 for q in range(3))
            tip=(end[0]+.07*scale*math.cos(ang+1),end[1]+.07*scale*math.sin(ang+1),end[2]-.04*scale)
            leaf_specs.append((name+'_sideleaf%d'%k,mid,tip,.035*scale,ang+1,col))

for row,z in enumerate([1.715,2.365,3.015]):
    for col,x in enumerate([-2.05,-1.10,-.22,.66,1.52,2.35]):
        plant('Shelf plant %d %d'%(row,col),x,2.10,z,random.uniform(.78,1.02),
              (.055,.095,.08) if (row+col)%3 else (.68,.75,.67),14)
plant('Broad lower foliage',.87,2.04,1.715,1.05,count=20)
plant('Left lower foliage',-1.75,2.04,1.715,.95,count=20)

ceiling=asset('Colored glass ceiling')
panels=part(ceiling,'Colored panels')
bars=part(ceiling,'Dark grid')
palette=[(.07,.36,.43),(.11,.35,.65),(.19,.48,.24),(.77,.48,.07),
         (.62,.08,.26),(.20,.19,.55),(.47,.64,.47),(.81,.64,.25)]
for iy in range(10):
    for ix in range(10):
        col=palette[(ix+iy*3+random.randrange(4))%len(palette)]
        add(panels,'panel%d_%d'%(ix,iy),box((.637,.637,.027),
            center=(-3.3+ix*.66,-3.4+iy*.66,3.78),color=col))
for i in range(11):
    add(bars,'long bar%d'%i,box((.027,6.7,.055),center=(-3.63+i*.66,-.1,3.752),color=(.025,.045,.044)))
for j in range(11):
    add(bars,'cross bar%d'%j,box((6.7,.027,.055),center=(-.3,-3.73+j*.66,3.752),color=(.025,.045,.044)))

sofa=asset('Magenta tufted sofa')
base=part(sofa,'Base and floor contacts')
back=part(sofa,'Back support and buttons')
seats=part(sofa,'Seat cushions and arms')
add(base,'base',fillet_box((4.25,1.05,.43),radius=.09,center=(-.38,1.04,.43),color=pink))
add(back,'back mass',fillet_box((4.25,.30,1.02),radius=.12,center=(-.38,1.54,1.20),color=pink))
for i,x in enumerate([-1.8,-.45,.9]):
    add(seats,'seat%d'%i,fillet_box((1.37,.88,.23),radius=.105,center=(x,.93,.73),color=pink_light))
for x in [-2.24,1.48]:
    add(seats,'arm%s'%x,fillet_box((.28,.93,.56),radius=.13,center=(x,1.02,.90),color=pink))
for x in [-2.1,1.3]:
    for y in [.72,1.4]:
        add(base,'foot%s_%s'%(x,y),rod(.033,length=.19,center=(x,y,.115),color=(.07,.055,.04)))
tufts=[]
for j in range(4):
    z=.92+j*.235
    for i in range(13):
        x=-2.37+i*.335+(j%2)*.1675
        if x<1.74:
            tufts.append((x,z))
            add(back,'button%d_%d'%(j,i),ball(.020,center=(x,1.298,z),color=(.26,.008,.12)))

def pillow(name,center,col,scale,tilt):
    a=asset(name)
    p=part(a,'Padded cushion')
    n=ball(1,center=center,color=col)
    n.resize(scale)
    n.turn('y',tilt)
    add(p,'cushion',n)

pillow('Burnt orange round pillow',(-.83,.87,1.13),(.65,.245,.065),(.31,.15,.36),-12)
pillow('Purple round pillow',(1.15,.81,1.00),(.44,.025,.235),(.32,.15,.35),20)
pillow('Orange pillow behind table',(.57,1.02,.91),(.67,.27,.075),(.29,.13,.23),-16)

table=asset('Round cafe table')
top=part(table,'Raised wood top')
legs=part(table,'Floor anchored metal supports')
tx,ty,tz=.12,-.13,1.385
add(top,'top',rod(.56,length=.065,center=(tx,ty,tz),color=(.49,.285,.115)))
add(top,'rim',rod(.565,length=.025,center=(tx,ty,tz-.025),color=(.40,.205,.065)))
for i,(dx,dy) in enumerate([(-.14,-.12),(.14,-.12),(-.14,.12),(.14,.12)]):
    add(legs,'stem%d'%i,rod(.017,start=(tx+dx,ty+dy,.12),end=(tx+dx,ty+dy,tz-.06),color=(.025,.045,.043)))
    add(legs,'foot%d'%i,rod(.018,start=(tx+dx,ty+dy,.14),end=(tx+dx*2.6,ty+dy*2.6,.055),color=(.025,.045,.043)))
add(legs,'bracket',box((.46,.30,.045),center=(tx,ty,tz-.10),color=dark))
props=asset('Table objects')
add(props,'napkin box',box((.19,.115,.085),center=(tx-.16,ty+.03,tz+.075),color=(.055,.065,.065)))
add(props,'napkin',box((.11,.015,.075),center=(tx-.16,ty+.04,tz+.13),color=(.85,.82,.72)))
add(props,'bottle',rod(.027,length=.17,center=(tx+.015,ty+.03,tz+.12),color=(.64,.72,.65)))
add(props,'neck',rod(.012,length=.10,center=(tx+.015,ty+.03,tz+.245),color=(.75,.80,.76)))
add(props,'cap',rod(.017,length=.02,center=(tx+.015,ty+.03,tz+.303),color=(.5,.53,.49)))
add(props,'ashtray',rod(.095,length=.021,center=(tx+.20,ty-.025,tz+.047),color=(.60,.65,.61)))
for k in range(20):
    a=k*math.tau/20
    add(props,'rim%d'%k,ball(.017,center=(tx+.20+.078*math.cos(a),ty-.025+.078*math.sin(a),tz+.068),color=(.70,.74,.69)))

green=asset('Foreground green chair')
gseat=part(green,'Seat and shell anchor')
glegs=part(green,'Floor contacts and legs')
cx,cy=-.42,-1.48
add(gseat,'seat',rod(.43,length=.11,center=(cx,cy,.62),color=(.025,.19,.13)))
for i,(dx,dy) in enumerate([(-.31,-.27),(.31,-.27),(-.31,.25),(.31,.25)]):
    add(glegs,'leg%d'%i,rod(.025,start=(cx+dx*1.23,cy+dy*1.23,.015),end=(cx+dx,cy+dy,.64),color=(.045,.075,.066)))
shell_specs.append(('Green chair curved back',cx,cy,.65,1.32,.43,.59,(.025,.205,.145),155,385))
for name,x,y,col in [('Right cropped tan chair',1.56,-2.35,(.58,.35,.17)),
                      ('Left cropped tan chair',-1.92,-.47,(.57,.37,.16))]:
    ch=asset(name)
    add(ch,'seat',rod(.42,length=.11,center=(x,y,.48),color=col))
    shell_specs.append((name+' shell',x,y,.48,1.04,.36,.49,col,160,380))
    for dx in [-.27,.27]:
        add(ch,'leg%s'%dx,rod(.025,start=(x+dx,y-.23,0),end=(x+dx,y-.20,.5),color=dark))

cabinet=asset('Right dark cabinet')
add(cabinet,'body',box((.66,1.56,1.42),center=(1.85,.17,.71),color=(.055,.045,.045)))
add(cabinet,'top',box((.79,1.65,.075),center=(1.82,.17,1.44),color=(.075,.083,.067)))
plant('Large right plant',1.98,.85,1.48,1.7,count=17)
for k in range(5):
    start=(1.95,.77,1.70)
    end=(1.30+random.random()*.50,.70+random.random()*.2,2.15+random.random()*.4)
    leaf_specs.append(('Large broad leaf%d'%k,start,end,.13,k*.7,(.025,.24,.105)))

realize(scene)

def material(name,col,rough=.5):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*col,1)
    bs.inputs['Roughness'].default_value=rough
    return m

def mesh_object(name,verts,faces,mat):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for p in me.polygons:
        p.use_smooth=True
    return ob

# Continuous upholstered front preserves the measured back anchor and tuft spacing.
verts=[]; faces=[]
nx,nz=180,64
for j in range(nz+1):
    z=.76+j*.95/nz
    for i in range(nx+1):
        x=-2.49+i*4.23/nx
        dent=0
        for xx,zz in tufts:
            d=((x-xx)/.065)**2+((z-zz)/.065)**2
            if d<10:
                dent+=.075*math.exp(-d*1.5)
        u=(x+2.37)/.335
        v=(z-.92)/.235
        diagonal=min(abs(u+v-round(u+v)),abs(u-v-round(u-v)))
        seam=.012*math.exp(-(diagonal/.060)**2)
        verts.append((x,1.275+dent+seam-.025*math.sin(math.pi*(z-.76)/.95),z))
for j in range(nz):
    for i in range(nx):
        a=j*(nx+1)+i
        faces.append((a,a+1,a+nx+2,a+nx+1))
velvet=material('Magenta velvet',pink_light,.83)
bs=velvet.node_tree.nodes.get('Principled BSDF')
if 'Sheen Weight' in bs.inputs:
    bs.inputs['Sheen Weight'].default_value=.32
noise=velvet.node_tree.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=160
bump=velvet.node_tree.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.12
bump.inputs['Distance'].default_value=.012
velvet.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
velvet.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
mesh_object('Sofa continuous diamond tuft upholstery',verts,faces,velvet)

for name,x,y,z0,z1,r0,r1,col,a0,a1 in shell_specs:
    verts=[]; faces=[]
    steps=64
    for level in range(4):
        for i in range(steps+1):
            a=math.radians(a0+(a1-a0)*i/steps)
            if level==0: r,z=r0,z0
            elif level==1: r,z=r1,z1
            elif level==2: r,z=r1-.045,z1-.012
            else: r,z=r0-.045,z0+.025
            verts.append((x+r*math.cos(a),y+r*math.sin(a),z))
    for level in range(4):
        nxt=(level+1)%4
        for i in range(steps):
            a=level*(steps+1)+i
            b=nxt*(steps+1)+i
            faces.append((a,a+1,b+1,b))
    for i in [0,steps]:
        faces.append(tuple(level*(steps+1)+i for level in range(4)))
    ob=mesh_object(name,verts,faces,material(name+' upholstery',col,.65))
    bevel=ob.modifiers.new('Soft upholstered edges','BEVEL')
    bevel.width=.018
    bevel.segments=3

leaf_mats={}
for name,start,end,width,angle,col in leaf_specs:
    if col not in leaf_mats:
        leaf_mats[col]=material('Foliage '+str(col),col,.46)
    s,e=Vector(start),Vector(end)
    side=Vector((math.cos(angle+math.pi/2),math.sin(angle+math.pi/2),.15))
    verts=[]; faces=[]
    for i in range(9):
        t=i/8
        p=s.lerp(e,t)
        p+=Vector((math.cos(angle),math.sin(angle),.1))*math.sin(math.pi*t)*.045
        w=width*math.sin(math.pi*t)**.7
        verts.extend([tuple(p-side*w),tuple(p+Vector((0,-.008,0))),tuple(p+side*w)])
    for i in range(8):
        a=i*3
        faces.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
    mesh_object(name,verts,faces,leaf_mats[col])

# Identify actual panel meshes by world-space bounds, independently of object names.
for ob in list(bpy.data.objects):
    if ob.type!='MESH' or not ob.data.materials:
        continue
    corners=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    zmin=min(c.z for c in corners)
    zmax=max(c.z for c in corners)
    dx=max(c.x for c in corners)-min(c.x for c in corners)
    dy=max(c.y for c in corners)-min(c.y for c in corners)
    if zmin>3.75 and zmax<3.81 and .60<dx<.67 and .60<dy<.67:
        col=tuple(ob.data.materials[0].diffuse_color[:3])
        m=material('Mottled colored ceiling glass',col,.31)
        nodes=m.node_tree.nodes
        bs=nodes.get('Principled BSDF')
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=7
        tex.inputs['Detail'].default_value=3
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.28
        ramp.color_ramp.elements[0].color=(*(v*.48 for v in col),1)
        ramp.color_ramp.elements[1].position=.70
        ramp.color_ramp.elements[1].color=(*(min(1,v*.55+.42) for v in col),1)
        m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac'])
        m.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        if 'Emission Color' in bs.inputs:
            m.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Emission Color'])
            bs.inputs['Emission Strength'].default_value=.12
        ob.data.materials.clear()
        ob.data.materials.append(m)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('World')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value=(.72,.78,.76,1)
    bg.inputs['Strength'].default_value=.35
set_view((0,-6.0,2.63),(0,1.0,2.04),lens=48,sensor=36)
area_emitter((-.8,-3.4,4.1),power=650,size=4,target=(0,1,1),color=(1,.92,.81))
area_emitter((0,3.0,3.0),power=900,size=3.8,target=(0,0,1.4),color=(.84,.98,1))
area_emitter((-3,0,2.7),power=220,size=2.5,target=(0,1,1.3))
sc.render.resolution_x=342
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.15
