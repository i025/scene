from sceneact import *
import bpy, math, random
random.seed(12)

# The foreground right wall hides nearly one third of the room; shorten it.
# The canopy is too small and low in frame; bring the camera closer and inside.
# Yellow textiles and the rug appear pale and plain; deepen color and add patterns.

scene = Scene(name='Golden state bedroom')
gold=(.62,.39,.045)
yellow=(.67,.46,.055)
silk=(.72,.55,.20)
cream=(.75,.72,.60)
wood=(.10,.052,.025)
sage=(.235,.32,.25)
panel=(.31,.33,.28)
ivory=(.72,.71,.61)
rugcolor=(.251,.231,.221)

def add(parent,name,node):
    parent.include(name,node)
    return node

room=Asset('Architecture')
add(room,'floor',box((10,13,.14),center=(0,.5,-.08),color=(.12,.075,.04)))
add(room,'back_wall',box((8,.15,4.7),center=(0,5.5,2.35),color=sage))
add(room,'left_wall',box((.15,12,4.7),center=(-3.75,-.4,2.35),color=sage))
add(room,'right_wall',box((.15,3.4,4.7),center=(3.75,3.9,2.35),color=sage))
add(room,'ceiling',box((7.6,12,.12),center=(0,-.4,4.55),color=ivory))
for side in ['back','left','right']:
    if side=='back':
        c=(0,5.39,.58); size=(7.5,.10,1.16)
    elif side=='left':
        c=(-3.64,-.4,.58); size=(.10,11.7,1.16)
    else:
        c=(3.64,3.9,.58); size=(.10,3.4,1.16)
    add(room,side+'_paneling',box(size,center=c,color=panel))
    for h,th in [(.12,.12),(1.10,.065),(1.19,.045),(4.27,.12),(4.40,.15)]:
        if side=='back':
            s=(7.5,.16,th); cc=(0,5.29,h)
        elif side=='left':
            s=(.16,11.7,th); cc=(-3.55,-.4,h)
        else:
            s=(.16,3.4,th); cc=(3.55,3.9,h)
        add(room,side+'_molding_'+str(h),box(s,center=cc,color=ivory if h>4 else panel))
for i in range(17):
    add(room,'stile_'+str(i),box((.035,.045,.78),center=(-3.5+i*.43,5.22,.61),color=(.24,.26,.22)))
scene.include('room',room)

door=Asset('Paneled door')
dx=.75
add(door,'outer_frame',box((1.14,.12,2.70),center=(dx,5.21,1.35),color=(.16,.19,.16)))
add(door,'frame',box((1.04,.10,2.60),center=(dx,5.12,1.32),color=(.43,.44,.38)))
add(door,'leaf',box((.91,.09,2.48),center=(dx,5.04,1.26),color=(.32,.34,.29)))
for i in range(2):
    for j in range(3):
        x=dx+(i-.5)*.42; z=.46+j*.77
        add(door,f'border_{i}_{j}',box((.36,.035,.65),center=(x,4.98,z),color=(.43,.44,.38)))
        add(door,f'inset_{i}_{j}',box((.29,.04,.56),center=(x,4.95,z),color=(.31,.33,.28)))
add(door,'lock',box((.085,.06,.14),center=(dx-.34,4.88,1.08),color=gold))
add(door,'handle',rod(.018,start=(dx-.35,4.83,1.13),end=(dx-.23,4.83,1.13),color=wood))
scene.include('door',door)

bed=Asset('Four poster canopy bed')
bx=-1.65
add(bed,'base',box((2.32,3.02,.43),center=(bx,3.20,.43),color=yellow))
add(bed,'mattress',box((2.23,2.94,.22),center=(bx,3.19,.76),color=silk))
add(bed,'coverlet',box((2.26,2.87,.09),center=(bx,3.15,.91),color=yellow))
add(bed,'foot_drape',box((2.30,.09,.65),center=(bx,1.70,.55),color=yellow))
for i in range(12):
    add(bed,'foot_pleat_'+str(i),rod(.022,start=(bx-1.06+i*.19,1.63,.26),end=(bx-1.06+i*.19,1.63,.88),color=silk))
add(bed,'head_panel',box((2.30,.13,3.00),center=(bx,4.77,2.30),color=(.73,.70,.60)))
for i,x in enumerate([bx-1.10,bx-.96,bx+.96,bx+1.10]):
    add(bed,'head_trim_'+str(i),rod(.015,start=(x,4.68,.85),end=(x,4.68,3.73),color=gold))
for i,x in enumerate([bx-.65,bx+.65]):
    pts=[(x,4.65,1.23),(x+.12,4.65,1.35),(x+.05,4.65,1.58),
         (x+.05,4.65,2.95),(x+.18,4.65,3.12),(x,4.65,3.35),(x-.15,4.65,3.15)]
    add(bed,'head_ornament_'+str(i),sweep_tube(points=pts,radius=.016,color=gold))
for i,x in enumerate([bx-.57,bx+.57]):
    add(bed,'pillow_'+str(i),turned(box((.91,.49,.19),center=(x,4.25,1.05),color=silk),'x',14))
add(bed,'small_pillow',turned(box((.48,.35,.16),center=(bx+.15,3.97,1.12),color=cream),'z',-22))
for i,x in enumerate([bx-1.24,bx+1.24]):
    for j,y in enumerate([1.54,4.77]):
        add(bed,f'post_{i}_{j}',rod(.043,start=(x,y,.12),end=(x,y,4.12),color=gold))
add(bed,'canopy_ceiling',box((2.62,3.39,.10),center=(bx,3.16,4.09),color=(.58,.50,.30)))
add(bed,'front_valance',box((2.65,.12,.29),center=(bx,1.48,3.98),color=yellow))
add(bed,'left_valance',box((.12,3.42,.29),center=(bx-1.29,3.14,3.98),color=yellow))
for i in range(13):
    n=ball(.13,center=(bx-1.18+i*.196,1.46,3.82),color=silk)
    n.resize((1,.45,.7))
    add(bed,'front_scallop_'+str(i),n)
for i in range(15):
    n=ball(.125,center=(bx-1.31,1.62+i*.21,3.83),color=silk)
    n.resize((.45,1,.7))
    add(bed,'side_scallop_'+str(i),n)
for k,(x,y,w) in enumerate([(bx-1.20,1.57,.43),(bx+1.20,1.57,.25),
                           (bx-1.20,4.55,.34),(bx+1.20,4.55,.35)]):
    add(bed,'curtain_'+str(k),box((w,.10,3.36),center=(x,y,2.13),color=yellow))
    for j in range(5):
        xx=x-w/2+(j+.5)*w/5
        add(bed,f'fold_{k}_{j}',rod(w/11,start=(xx,y-.07,.46),end=(xx,y-.07,3.81),color=silk if j%2 else yellow))
    add(bed,'white_band_'+str(k),box((w+.015,.14,.31),center=(x,y-.025,.86),color=(.78,.77,.68)))
scene.include('bed',bed)

def leg(parent,name,x,y,h=.43,col=wood):
    add(parent,name,rod(.03,start=(x,y,.08),end=(x+.035,y,h),color=col))

bench=Asset('Upholstered foot chaise')
add(bench,'seat',fillet_box((2.48,.76,.23),.09,center=(-1.18,1.03,.57),color=silk))
add(bench,'frame',box((2.40,.66,.11),center=(-1.18,1.03,.41),color=wood))
for i,x in enumerate([-2.25,-.12]):
    for j,y in enumerate([.78,1.28]):
        leg(bench,f'leg_{i}_{j}',x,y)
add(bench,'raised_end',fillet_box((.20,.77,.85),.085,center=(.04,1.06,.95),color=silk))
add(bench,'bolster',rod(.14,start=(-.37,.76,.83),end=(-.37,1.34,.83),color=silk))
scene.include('bench',bench)

sofa=Asset('Back wall settee')
add(sofa,'seat',fillet_box((1.85,.66,.23),.09,center=(2.40,4.42,.62),color=yellow))
add(sofa,'back',fillet_box((1.76,.19,.65),.085,center=(2.40,4.72,.96),color=silk))
for i,x in enumerate([1.53,3.27]):
    add(sofa,'arm_'+str(i),rod(.15,start=(x,4.15,.84),end=(x,4.68,.84),color=silk))
    for j,y in enumerate([4.18,4.65]):
        leg(sofa,f'leg_{i}_{j}',x,y,.53)
scene.include('settee',sofa)

def chair(name,x,y,angle=0):
    a=Asset(name)
    add(a,'seat',fillet_box((.83,.77,.20),.09,center=(x,y,.57),color=yellow))
    add(a,'back_frame',fillet_box((.88,.15,1.00),.065,center=(x,y+.32,1.04),color=ivory))
    add(a,'back_cushion',fillet_box((.75,.17,.82),.075,center=(x,y+.22,1.09),color=silk))
    for i,xx in enumerate([x-.36,x+.36]):
        for j,yy in enumerate([y-.28,y+.28]):
            leg(a,f'leg_{i}_{j}',xx,yy,.51,ivory)
        add(a,'arm_'+str(i),sweep_tube(points=[(xx,y-.29,.61),(xx,y-.31,.90),(xx,y+.24,1.01)],radius=.025,color=ivory))
    a.turn('z',angle,pivot=(x,y,0))
    scene.include(name,a)
chair('Right armchair',2.98,2.56,-12)
chair('Foreground chair',3.05,-.45,-24)

cab=Asset('Bedside cabinet')
add(cab,'body',box((.57,.53,.64),center=(-3.13,1.86,.35),color=wood))
add(cab,'top',box((.65,.60,.07),center=(-3.13,1.86,.71),color=(.19,.10,.045)))
for j in range(2):
    add(cab,'drawer_'+str(j),box((.48,.025,.23),center=(-3.13,1.58,.25+j*.28),color=(.17,.085,.04)))
    add(cab,'pull_'+str(j),ball(.022,center=(-3.13,1.55,.25+j*.28),color=gold))
scene.include('cabinet',cab)

shadecolor=(.91,.72,.33)
def lamp(name,x,y,z):
    a=Asset(name)
    add(a,'base',rod(.10,length=.04,center=(x,y,z),color=gold))
    add(a,'stem',rod(.018,length=.43,center=(x,y,z+.23),color=gold))
    add(a,'shade',rod(.19,length=.28,center=(x,y,z+.52),color=shadecolor))
    for i in range(10):
        t=i*math.tau/10
        add(a,'rib_'+str(i),rod(.007,start=(x+.19*math.cos(t),y+.19*math.sin(t),z+.38),
            end=(x+.13*math.cos(t),y+.13*math.sin(t),z+.67),color=cream))
    scene.include(name,a)
lamp('Left lamp',-3.13,1.88,.76)
lamp('Far lamp',-.29,4.17,1.02)

rug=Asset('Persian carpet')
add(rug,'woven_field',box((5.85,4.9,.025),center=(.30,.3,.025),color=rugcolor))
for i,(w,d,col) in enumerate([(5.73,4.78,(.12,.19,.21)),(5.49,4.54,(.48,.32,.21)),
                             (5.27,4.32,(.14,.21,.23)),(4.94,3.99,(.43,.24,.18))]):
    for j,y in enumerate([.3-d/2,.3+d/2]):
        add(rug,f'border_h_{i}_{j}',box((w,.075,.009),center=(.3,y,.045+i*.001),color=col))
    for j,x in enumerate([.3-w/2,.3+w/2]):
        add(rug,f'border_v_{i}_{j}',box((.075,d,.009),center=(x,.3,.045+i*.001),color=col))
scene.include('rug',rug)

tea=Asset('Tea stand')
add(tea,'top',rod(.27,length=.045,center=(-2.73,-.05,.46),color=(.08,.07,.05)))
for i in range(3):
    t=i*math.tau/3
    add(tea,'leg_'+str(i),rod(.018,start=(-2.73+.20*math.cos(t),-.05+.20*math.sin(t),.04),
        end=(-2.73+.18*math.cos(t),-.05+.18*math.sin(t),.45),color=wood))
add(tea,'tray',rod(.20,length=.015,center=(-2.73,-.05,.49),color=(.66,.66,.61)))
add(tea,'teapot',ball(.075,center=(-2.74,-.04,.57),color=(.83,.83,.77)))
add(tea,'lid',ball(.034,center=(-2.74,-.04,.64),color=ivory))
for i,x in enumerate([-2.88,-2.60]):
    add(tea,'cup_'+str(i),rod(.045,length=.055,center=(x,-.10,.54),color=ivory))
scene.include('tea',tea)

land=Asset('Painted landscape frieze')
add(land,'back_frieze',box((7.4,.018,.60),center=(0,5.28,1.52),color=(.38,.44,.35)))
add(land,'right_frieze',box((.018,3.3,.60),center=(3.55,3.9,1.52),color=(.38,.44,.35)))
for i in range(11):
    x=-3.4+i*.65
    add(land,'tree_'+str(i),sweep_tube(points=[(x,5.26,1.25),(x+.035,5.26,1.55),
        (x-.04,5.26,1.87)],radius=.009,color=(.25,.31,.24)))
scene.include('landscape',land)

realize(scene)

# Match finishes by their actual shader color; realized meshes have generic names.
def near(a,b):
    return sum(abs(a[i]-b[i]) for i in range(3))<.012

for mat in list(bpy.data.materials):
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bs=nodes.get('Principled BSDF')
    if bs is None:
        continue
    c=tuple(bs.inputs['Base Color'].default_value)
    bs.inputs['Roughness'].default_value=.8
    if near(c,sage):
        tc=nodes.new('ShaderNodeTexCoord')
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=9
        tex.inputs['Detail'].default_value=3
        tex.inputs['Roughness'].default_value=.75
        links.new(tc.outputs['Object'],tex.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.56
        ramp.color_ramp.elements[0].color=(*sage,1)
        ramp.color_ramp.elements[1].position=.68
        ramp.color_ramp.elements[1].color=(.43,.48,.39,1)
        links.new(tex.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    if near(c,rugcolor):
        tc=nodes.new('ShaderNodeTexCoord')
        scale=nodes.new('ShaderNodeVectorMath')
        scale.operation='MULTIPLY'
        scale.inputs[1].default_value=(12,10,1)
        links.new(tc.outputs['Generated'],scale.inputs[0])
        vor=nodes.new('ShaderNodeTexVoronoi')
        vor.distance='MANHATTAN'
        vor.inputs['Scale'].default_value=1
        vor.inputs['Randomness'].default_value=.18
        links.new(scale.outputs['Vector'],vor.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        cr=ramp.color_ramp
        cr.elements[0].position=.10
        cr.elements[0].color=(.08,.14,.16,1)
        cr.elements[1].position=.65
        cr.elements[1].color=(.12,.20,.23,1)
        for p,col in [(.18,(.53,.35,.23,1)),(.24,(.12,.19,.22,1)),
                      (.32,(.48,.23,.15,1)),(.40,(.20,.26,.25,1)),
                      (.48,(.57,.38,.25,1)),(.54,(.11,.17,.19,1))]:
            cr.elements.new(p).color=col
        links.new(vor.outputs['Distance'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    if near(c,silk) or near(c,yellow):
        tc=nodes.new('ShaderNodeTexCoord')
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=32
        tex.inputs['Detail'].default_value=2
        links.new(tc.outputs['Object'],tex.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.37
        ramp.color_ramp.elements[0].color=(c[0]*.77,c[1]*.77,c[2]*.77,1)
        ramp.color_ramp.elements[1].position=.64
        ramp.color_ramp.elements[1].color=(min(c[0]*1.14,1),min(c[1]*1.14,1),min(c[2]*1.25,1),1)
        links.new(tex.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.13
        bump.inputs['Distance'].default_value=.01
        links.new(tex.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if near(c,shadecolor):
        bs.inputs['Emission Color'].default_value=(1,.67,.25,1)
        bs.inputs['Emission Strength'].default_value=.65

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.29,.32,.28,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.22
CAMERA_POSITION=(3.45,-7.0,2.85)
CAMERA_TARGET=(-.18,3.05,2.02)
set_view(position=CAMERA_POSITION,target=CAMERA_TARGET,lens=43,sensor=36)
area_emitter(position=(.5,-2.8,3.9),power=650,size=3.5,target=(-1,2.7,1.3),color=(1,.91,.76))
area_emitter(position=(-3.0,1.5,2.2),power=65,size=.5,target=(-1.6,2.7,1.2),color=(1,.66,.23))
area_emitter(position=(-.28,4.0,1.65),power=35,size=.3,target=(-1,3,1),color=(1,.65,.21))
sc.render.resolution_x=512
sc.render.resolution_y=340
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
