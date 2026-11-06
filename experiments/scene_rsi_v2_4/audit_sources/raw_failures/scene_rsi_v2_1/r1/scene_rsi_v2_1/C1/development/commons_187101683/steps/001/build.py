# Reference inventory (normalized image bounds, estimated):
# sofa (.02,.28)-(.97,.96): ochre upholstered base, two broad back cushions,
# two seat cushions, thick arms; a loose golden pillow overlaps the left back.
# table (.32,.60)-(1,1): dark rectangular wood top and square legs, right cropped.
# left cup (.46,.55)-(.57,.65), right cup (.72,.55)-(.83,.66):
# white open cups, curved handles, saucers, overlapping pale napkins.
# plant (.56,.33)-(.73,.65): charcoal tapered pot, green branching foliage,
# several pale blue flower heads with open gaps between stems.
# wall (0,0)-(1,.74), grey carpet below; grey folded curtain at upper right.
# Hidden sofa feet, rear table legs and the window beyond the curtain are uncertain.
# Named assets below preserve these objects and their meaningful component parts.
import bpy
import math
import random
from sceneact import *

random.seed(12)
scene = Scene('Warm living room')
ochre = (.65,.335,.095)
gold = (.76,.43,.15)
seatgold = (.70,.375,.115)
wood = (.055,.033,.022)
white = (.91,.92,.88)

def rounded(asset, name, size, center, color, radius=.06):
    n = fillet_box(size=size, radius=min(radius,min(size)*.45),
                   center=center, color=color)
    asset.include(name,n)
    return n

room = Asset('room')
room.include('plaster_wall',box((13,.15,7),center=(0,1.37,3.3),color=(.78,.77,.72)))
room.include('grey_carpet',box((14,15,.12),center=(0,-3,-.07),color=(.30,.285,.275)))
scene.include('room',room)

sofa = Asset('ochre_velvet_sofa')
rounded(sofa,'lower_upholstered_base',(3.78,1.04,.44),(0,.32,.30),ochre,.095)
rounded(sofa,'front_base_panel',(3.47,.18,.37),(0,-.205,.31),(.59,.295,.083),.045)
rounded(sofa,'rear_back_structure',(3.46,.30,1.26),(0,.80,1.03),ochre,.08)
# Broad back pads meet near the middle; their tops are softly rounded.
for i,x in enumerate((-.82,.82)):
    back = rounded(sofa,'back_cushion_%d'%i,(1.64,.29,.89),(x,.61,1.31),gold,.075)
    back.turn('x',-5)
for i,x in enumerate((-.81,.81)):
    rounded(sofa,'seat_cushion_%d'%i,(1.60,.91,.245),(x,.08,.705),seatgold,.085)
for name,x in [('left',-1.78),('right',1.78)]:
    rounded(sofa,name+'_arm',( .39,1.15,1.05),(x,.27,.70),ochre,.09)
    rounded(sofa,name+'_arm_top',(.40,1.10,.20),(x,.25,1.18),seatgold,.075)
# Loose pillow, visibly tilted and plump.
pillow = rounded(sofa,'loose_left_pillow',(.65,.24,.66),(-1.20,.30,1.25),(.82,.51,.22),.10)
pillow.turn('y',-12)
pillow.turn('x',-12)
pillow.turn('z',-7)
# A fine welt follows its four sides.
welt = Asset('pillow_edge_welt')
for a,b in [
    ((-1.52,.155,.94),(-.90,.155,.99)),
    ((-.90,.155,.99),(-.98,.155,1.59)),
    ((-.98,.155,1.59),(-1.60,.155,1.54)),
    ((-1.60,.155,1.54),(-1.52,.155,.94))]:
    welt.include('edge_%d'%len(welt.members),rod(.008,start=a,end=b,color=(.69,.39,.12)))
sofa.include('pillow_welt',welt)
scene.include('sofa',sofa)

table = Asset('dark_wood_coffee_table')
tx,ty,tz = .69,-1.24,.77
tw,td = 2.66,.91
table.include('solid_rectangular_top',box((tw,td,.105),center=(tx,ty,tz),color=wood))
for i,x in enumerate((tx-tw/2+.105,tx+tw/2-.105)):
    for j,y in enumerate((ty-td/2+.10,ty+td/2-.10)):
        table.include('square_leg_%d_%d'%(i,j),
                      box((.105,.105,.72),center=(x,y,.36),color=(.033,.022,.017)))
table.include('front_apron',box((tw-.15,.075,.17),center=(tx,ty-td/2+.055,.665),color=wood))
scene.include('coffee_table',table)

def cup_setting(label,x,y):
    a=Asset(label)
    # Flat folded napkin and green-grey printed layer, rotated slightly.
    nap=box((.61,.35,.008),center=(x,y,.832),color=(.74,.80,.75))
    nap.turn('z',-9)
    a.include('folded_cloth_napkin',nap)
    nap2=box((.52,.33,.006),center=(x+.015,y-.012,.839),color=(.88,.89,.82))
    nap2.turn('z',8)
    a.include('upper_napkin_fold',nap2)
    a.include('napkin_green_edge',rod(.007,start=(x-.26,y-.165,.845),
                                    end=(x+.25,y-.12,.845),color=(.20,.37,.31)))
    a.include('saucer',rod(.205,length=.018,center=(x,y,.855),color=white))
    a.include('saucer_inner',rod(.156,length=.009,center=(x,y,.867),color=(.83,.85,.81)))
    # Tapered cup, constructed as a smoothly graduated set of hollow rings.
    bottom=.875
    h=.225
    steps=18
    for k in range(steps):
        z=bottom+(k+.5)*h/steps
        r=.087+.035*(k+.5)/steps
        outer=rod(r,length=h/steps+.001,center=(x,y,z),color=white)
        inner=rod(r-.009,length=h/steps+.005,center=(x,y,z+.002),color=white)
        a.include('porcelain_wall_%02d'%k,subtract(outer,inner))
    a.include('cup_floor',rod(.083,length=.012,center=(x,y,bottom+.008),color=white))
    # A dark warm interior seen through the open upper rim.
    a.include('tea',rod(.105,length=.004,center=(x,y,bottom+h-.037),color=(.19,.115,.051)))
    rimpoints=[(x+.122*math.cos(t*2*math.pi/64),
                y+.122*math.sin(t*2*math.pi/64),bottom+h) for t in range(65)]
    a.include('fine_round_lip',sweep_tube(points=rimpoints,radius=.004,color=white))
    side=-1 if label.startswith('left') else 1
    points=[]
    for j in range(25):
        t=math.pi/2+j*math.pi/24
        points.append((x+side*(.105+.095*math.cos(t)),y,bottom+.12+.075*math.sin(t)))
    # Handle outer edge bends away from the body.
    points=[(x+side*(.10+.092*math.sin(j*math.pi/24)),
             y,bottom+.193-.15*j/24) for j in range(25)]
    a.include('curved_handle',sweep_tube(points=points,radius=.012,color=white))
    scene.include(label,a)

cup_setting('left_cup_and_saucer',-.02,-1.23)
cup_setting('right_cup_and_saucer',1.05,-1.28)

plant=Asset('flower_arrangement')
px,py=.53,-1.10
potbottom=.825
# Explicit pot silhouette: narrow bottom, broader lip, softly ribbed charcoal ceramic.
pot_h=.285
for k in range(26):
    z=potbottom+(k+.5)*pot_h/26
    rr=.112+.041*(k+.5)/26
    plant.include('pot_rib_%02d'%k,rod(rr,length=pot_h/26+.002,
                  center=(px,py,z),color=(.072+.006*(k%2),.084+.006*(k%2),.077+.006*(k%2))))
plant.include('pot_rim',rod(.158,length=.018,center=(px,py,potbottom+pot_h),color=(.052,.061,.052)))
plant.include('visible_soil',rod(.142,length=.008,center=(px,py,potbottom+pot_h+.011),color=(.055,.042,.023)))

green=(.20,.34,.13)
def leaf(name,start,end,width):
    dx,dy,dz=(end[i]-start[i] for i in range(3))
    mid=tuple((start[i]+end[i])/2 for i in range(3))
    length=math.sqrt(dx*dx+dy*dy+dz*dz)
    n=ball(1,center=(0,0,0),color=(.23+random.uniform(-.04,.04),.37+random.uniform(-.04,.05),.15))
    n.resize((width,.012,length/2))
    n.turn('y',math.degrees(math.acos(dz/length)))
    n.turn('z',math.degrees(math.atan2(dy,dx)))
    n.move(mid)
    plant.include(name,n)

heads=[(-.27,.015,1.48,.074),(-.11,.04,1.63,.075),
       (.06,.055,1.55,.066),(.25,.045,1.48,.087),
       (.17,-.025,1.39,.063),(-.19,-.035,1.39,.056)]
for i,(dx,dy,z,r) in enumerate(heads):
    start=(px+random.uniform(-.04,.04),py,potbottom+.28)
    tip=(px+dx,py+dy,z)
    plant.include('flower_stem_%d'%i,rod(.008,start=start,end=tip,color=green))
    for j in range(4):
        f=.20+j*.16
        p=tuple(start[q]+f*(tip[q]-start[q]) for q in range(3))
        s=(-1 if j%2 else 1)
        e=(p[0]+s*random.uniform(.085,.14),p[1]+random.uniform(-.075,.075),p[2]+.045)
        plant.include('leaf_stalk_%d_%d'%(i,j),rod(.003,start=p,end=e,color=green))
        leaf('pointed_leaf_%d_%d'%(i,j),p,e,.024)
    # Hydrangea-like heads comprise small pale blue florets and leave the stem gaps open.
    for j in range(48):
        u=random.uniform(-1,1)
        phi=random.uniform(0,2*math.pi)
        rad=r*math.sqrt(1-u*u)
        c=(tip[0]+rad*math.cos(phi),tip[1]+rad*math.sin(phi),tip[2]+r*u)
        flower=Part('floret_%d_%d'%(i,j))
        col=(.54+random.uniform(-.04,.06),.61+random.uniform(-.03,.07),.67+random.uniform(-.02,.06))
        for k in range(4):
            angle=k*math.pi/2
            pet=ball(.012,center=(c[0]+.008*math.cos(angle),
                                  c[1]+.008*math.sin(angle),c[2]),color=col)
            pet.resize((1,.85,.52))
            flower.include('petal_%d'%k,pet)
        plant.include('bloom_%d_%d'%(i,j),flower)
# Extra spreading foliage around the rim.
for i in range(15):
    a=random.uniform(0,2*math.pi)
    st=(px,py,1.13)
    en=(px+.25*math.cos(a),py+.15*math.sin(a),random.uniform(1.15,1.33))
    plant.include('low_branch_%d'%i,rod(.004,start=st,end=en,color=green))
    leaf('low_leaf_%d'%i,tuple((st[k]+en[k])/2 for k in range(3)),en,.026)
scene.include('flowers_in_charcoal_pot',plant)

curtain=Asset('right_window_and_grey_curtains')
curtain.include('bright_window',box((1.25,.035,3.5),center=(2.62,1.20,1.9),color=(.92,.94,.92)))
# Dense adjoining vertical folds describe the hanging cloth and its gathered sweep.
for i in range(43):
    f=i/42
    x=1.43+f*.88
    pts=[]
    for j in range(21):
        z=.76+j*.145
        # Gather at the lower-middle, then fan back out above.
        bend=-.19*math.exp(-((z-1.68)/.39)**2)*(1-f)
        xx=x+bend+.018*math.sin(z*2+f*4)
        yy=1.04+.065*math.cos(f*math.pi*18)
        pts.append((xx,yy,z))
    shade=.24+.12*(.5+.5*math.cos(f*math.pi*18))
    curtain.include('hanging_fold_%02d'%i,sweep_tube(points=pts,radius=.032,
                    color=(shade,shade*1.015,shade*1.01)))
# Pale inner curtain along the illuminated right edge.
for i in range(14):
    x=2.22+i*.026
    curtain.include('sheer_fold_%02d'%i,sweep_tube(
        points=[(x-.12*math.exp(-((z-1.75)/.5)**2),1.015+.025*math.sin(i),z)
                for z in [ .75+j*.15 for j in range(21)]],
        radius=.025,color=(.65,.69,.69)))
scene.include('curtain',curtain)

realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.72,.76,.80,1)
background.inputs['Strength'].default_value=.30

# Gentle surface variation gives upholstery, wood and carpet their characteristic response.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Roughness'].default_value=.73
    color=bs.inputs['Base Color'].default_value
    r,g,b=color[:3]
    if r>.4 and r>g*1.35 and g>b*1.5:
        bs.inputs['Roughness'].default_value=.87
        if 'Sheen Weight' in bs.inputs:
            bs.inputs['Sheen Weight'].default_value=.22
        noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=160
        noise.inputs['Detail'].default_value=2
        bump=mat.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.16
        bump.inputs['Distance'].default_value=.012
        mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif r>.8 and g>.8:
        bs.inputs['Roughness'].default_value=.22
    elif max(r,g,b)<.10:
        bs.inputs['Roughness'].default_value=.38

set_view((.62,-6.55,2.78),(.10,.05,1.13),lens=55,sensor=36)
area_emitter((3.4,-.1,4.0),power=650,size=3.0,target=(0,0,.8),color=(1,.95,.86))
area_emitter((-2.8,-3.0,3.2),power=110,size=4.0,target=(0,0,1),color=(.90,.94,1))
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.25
camera=sc.camera
camera.data.dof.use_dof=True
camera.data.dof.focus_distance=(camera.location-mathutils.Vector((.5,-.8,1.05))).length if False else 5.9
camera.data.dof.aperture_fstop=7.1
