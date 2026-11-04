from sceneact import *
import bpy, math, random
random.seed(12)

# Canopy occupies approximately (0.08,0.00)-(0.50,0.85).
# Bed front and upholstered bench overlap around (0.24,0.65)-(0.58,0.92).
# Paneled door is centered near (0.61,0.47).
# Green wallpaper meets gray paneling near image height 0.48.
# Carpet covers the foreground, with a chair cropped at lower right.
# Warm lamps flank the bed; the room's right side is relatively dim.

scene = Scene(name='Yellow state bedroom')
gold = (.70,.45,.065)
yellow = (.76,.58,.12)
silk = (.79,.66,.29)
cream = (.76,.73,.61)
wood = (.105,.065,.035)
sage = (.25,.34,.27)
panel = (.36,.37,.31)
ivory = (.77,.76,.67)

def add(parent, name, node):
    parent.include(name, node)
    return node

architecture = Asset('Architecture')
add(architecture,'floor',box((8,8,.14),center=(0,2,-.08),color=(.14,.095,.055)))
add(architecture,'back_wall',box((8,.15,4.7),center=(0,5.5,2.35),color=sage))
add(architecture,'left_wall',box((.15,8,4.7),center=(-3.75,1.6,2.35),color=sage))
add(architecture,'right_wall',box((.15,8,4.7),center=(3.75,1.6,2.35),color=sage))
add(architecture,'ceiling',box((7.6,8,.12),center=(0,1.6,4.55),color=ivory))
for axis in ['back','left','right']:
    if axis=='back':
        c=(0,5.39,.58); size=(7.5,.10,1.16)
    else:
        c=((-3.64 if axis=='left' else 3.64),1.6,.58); size=(.10,7.7,1.16)
    add(architecture,axis+'_wainscot',box(size,center=c,color=panel))
    for h,th in [(.12,.12),(1.10,.065),(1.19,.045),(4.27,.12),(4.40,.15)]:
        s=(7.5,.16,th) if axis=='back' else (.16,7.7,th)
        cc=(0,5.29,h) if axis=='back' else ((-3.55 if axis=='left' else 3.55),1.6,h)
        add(architecture,axis+'_molding_'+str(h),box(s,center=cc,color=ivory if h>4 else panel))
for i in range(17):
    add(architecture,'panel_stile_'+str(i),box((.035,.045,.78),center=(-3.5+i*.43,5.22,.61),color=(.27,.29,.25)))
scene.include('room',architecture)

door=Asset('Paneled gray door')
dx=.75
add(door,'outer_frame',box((1.14,.12,2.70),center=(dx,5.21,1.35),color=(.19,.23,.19)))
add(door,'frame',box((1.04,.10,2.60),center=(dx,5.12,1.32),color=(.48,.49,.42)))
add(door,'leaf',box((.91,.09,2.48),center=(dx,5.04,1.26),color=(.37,.39,.34)))
for i in range(2):
    for j in range(3):
        x=dx+(i-.5)*.42; z=.46+j*.77
        add(door,f'panel_border_{i}_{j}',box((.36,.035,.65),center=(x,4.98,z),color=(.48,.49,.43)))
        add(door,f'panel_inset_{i}_{j}',box((.29,.04,.56),center=(x,4.95,z),color=(.36,.38,.33)))
add(door,'lock',box((.085,.06,.14),center=(dx-.34,4.88,1.08),color=gold))
add(door,'handle',rod(.018,start=(dx-.35,4.83,1.13),end=(dx-.23,4.83,1.13),color=wood))
scene.include('door',door)

bed=Asset('Four poster bed')
bx=-1.65
add(bed,'base',box((2.32,3.02,.43),center=(bx,3.20,.43),color=yellow))
add(bed,'mattress',box((2.23,2.94,.22),center=(bx,3.19,.76),color=silk))
add(bed,'coverlet',box((2.26,2.87,.09),center=(bx,3.15,.91),color=yellow))
add(bed,'foot_drape',box((2.30,.09,.65),center=(bx,1.70,.55),color=yellow))
for i in range(12):
    add(bed,'foot_pleat_'+str(i),rod(.025,start=(bx-1.06+i*.19,1.63,.26),end=(bx-1.06+i*.19,1.63,.88),color=silk))
add(bed,'head_panel',box((2.30,.13,3.00),center=(bx,4.77,2.30),color=(.77,.75,.65)))
for x in [bx-1.10,bx-.96,bx+.96,bx+1.10]:
    add(bed,'head_trim_'+str(x),rod(.018,start=(x,4.68,.85),end=(x,4.68,3.73),color=gold))
for x in [bx-.65,bx+.65]:
    pts=[(x,4.65,1.23),(x+.12,4.65,1.35),(x+.05,4.65,1.58),
         (x+.05,4.65,2.95),(x+.18,4.65,3.12),(x,4.65,3.35),(x-.15,4.65,3.15)]
    add(bed,'head_ornament_'+str(x),sweep_tube(points=pts,radius=.018,color=gold))
for x in [bx-.57,bx+.57]:
    pillow=box((.91,.49,.19),center=(x,4.25,1.05),color=silk)
    pillow.turn('x',14)
    add(bed,'pillow_'+str(x),pillow)
add(bed,'small_pillow',turned(box((.48,.35,.16),center=(bx+.15,3.97,1.12),color=cream),'z',-22))
for i,x in enumerate([bx-1.24,bx+1.24]):
    for j,y in enumerate([1.54,4.77]):
        add(bed,f'post_{i}_{j}',rod(.043,start=(x,y,.12),end=(x,y,4.12),color=gold))
        add(bed,f'finial_{i}_{j}',ball(.075,center=(x,y,4.17),color=gold))
add(bed,'canopy_ceiling',box((2.62,3.39,.10),center=(bx,3.16,4.09),color=(.70,.64,.42)))
add(bed,'front_valance',box((2.65,.12,.29),center=(bx,1.48,3.98),color=yellow))
add(bed,'left_valance',box((.12,3.42,.29),center=(bx-1.29,3.14,3.98),color=yellow))
for i in range(13):
    scallop=ball(.13,center=(bx-1.18+i*.196,1.46,3.82),color=silk)
    scallop.resize((1,.45,.7))
    add(bed,'front_scallop_'+str(i),scallop)
for i in range(15):
    scallop=ball(.125,center=(bx-1.31,1.62+i*.21,3.83),color=silk)
    scallop.resize((.45,1,.7))
    add(bed,'side_scallop_'+str(i),scallop)
for k,(x,y,w) in enumerate([(bx-1.20,1.57,.43),(bx+1.20,1.57,.25),(bx-1.20,4.55,.34),(bx+1.20,4.55,.35)]):
    add(bed,'curtain_body_'+str(k),box((w,.10,3.36),center=(x,y,2.13),color=yellow))
    for j in range(5):
        xx=x-w/2+(j+.5)*w/5
        add(bed,f'curtain_fold_{k}_{j}',rod(w/11,start=(xx,y-.07,.46),end=(xx,y-.07,3.81),color=silk if j%2 else yellow))
    add(bed,'curtain_white_band_'+str(k),box((w+.015,.14,.31),center=(x,y-.025,.86),color=(.79,.78,.68)))
scene.include('bed',bed)

def leg(parent,name,x,y,h=.43):
    add(parent,name,rod(.035,start=(x,y,.10),end=(x+.04,y,h),color=wood))
    add(parent,name+'_foot',ball(.045,center=(x,y,.11),color=wood))

bench=Asset('Bed foot chaise')
add(bench,'seat',fillet_box((2.48,.76,.23),.10,center=(-1.18,1.03,.57),color=silk))
add(bench,'seat_frame',box((2.40,.66,.11),center=(-1.18,1.03,.41),color=wood))
for i,x in enumerate([-2.25,-.12]):
    for j,y in enumerate([.78,1.28]):
        leg(bench,f'leg_{i}_{j}',x,y)
add(bench,'raised_end',fillet_box((.20,.77,.85),.085,center=(.04,1.06,.95),color=silk))
add(bench,'end_bolster',rod(.14,start=(-.37,.76,.83),end=(-.37,1.34,.83),color=silk))
scene.include('bench',bench)

sofa=Asset('Back wall settee')
add(sofa,'seat',fillet_box((1.85,.66,.23),.10,center=(2.40,4.42,.62),color=yellow))
add(sofa,'back',fillet_box((1.76,.19,.65),.09,center=(2.40,4.72,.96),color=silk))
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
            add(a,f'leg_{i}_{j}',rod(.026,start=(xx,yy,.08),end=(xx,yy,.51),color=ivory))
        add(a,'arm_'+str(i),sweep_tube(points=[(xx,y-.29,.61),(xx,y-.31,.90),(xx,y+.24,1.01)],radius=.025,color=ivory))
    a.turn('z',angle,pivot=(x,y,0))
    scene.include(name,a)
chair('Right armchair',2.98,2.56,-12)
chair('Foreground cropped chair',3.22,-.25,-24)

table=Asset('Bedside cabinet')
add(table,'body',box((.57,.53,.64),center=(-3.13,1.86,.35),color=wood))
add(table,'top',box((.65,.60,.07),center=(-3.13,1.86,.71),color=(.22,.12,.055)))
for j in range(2):
    add(table,'drawer_'+str(j),box((.48,.025,.23),center=(-3.13,1.58,.25+j*.28),color=(.19,.105,.055)))
    add(table,'pull_'+str(j),ball(.025,center=(-3.13,1.55,.25+j*.28),color=gold))
scene.include('cabinet',table)

def lamp(name,x,y,z):
    a=Asset(name)
    add(a,'base',rod(.10,length=.04,center=(x,y,z),color=gold))
    add(a,'stem',rod(.018,length=.43,center=(x,y,z+.23),color=gold))
    # A ring of tapered-looking pleats forms the warm lampshade.
    add(a,'shade',rod(.19,length=.28,center=(x,y,z+.52),color=(.94,.80,.42)))
    for i in range(12):
        t=i*math.tau/12
        add(a,'shade_rib_'+str(i),rod(.008,start=(x+.19*math.cos(t),y+.19*math.sin(t),z+.38),
            end=(x+.13*math.cos(t),y+.13*math.sin(t),z+.67),color=cream))
    scene.include(name,a)
lamp('Left glowing lamp',-3.13,1.88,.76)
lamp('Far bedside lamp',-.29,4.17,1.02)

rug=Asset('Large patterned carpet')
add(rug,'carpet',box((5.15,3.67,.025),center=(.30,.80,.025),color=(.29,.27,.25)))
for i,(w,d,col) in enumerate([(5.03,3.55,(.13,.19,.21)),(4.77,3.29,(.58,.43,.29)),(4.57,3.09,(.16,.23,.25)),(4.30,2.82,(.49,.31,.25))]):
    for j,y in enumerate([.80-d/2,.80+d/2]):
        add(rug,f'border_h_{i}_{j}',box((w,.075,.008),center=(.3,y,.043+i*.001),color=col))
    for j,x in enumerate([.30-w/2,.30+w/2]):
        add(rug,f'border_v_{i}_{j}',box((.075,d,.008),center=(x,.80,.043+i*.001),color=col))
scene.include('rug',rug)

tea=Asset('Small round tea stand')
add(tea,'top',rod(.27,length=.045,center=(-2.73,-.05,.46),color=(.12,.10,.075)))
for i in range(3):
    t=i*math.tau/3
    add(tea,'leg_'+str(i),rod(.018,start=(-2.73+.20*math.cos(t),-.05+.20*math.sin(t),.04),
        end=(-2.73+.18*math.cos(t),-.05+.18*math.sin(t),.45),color=wood))
add(tea,'tray',rod(.20,length=.015,center=(-2.73,-.05,.49),color=(.70,.70,.64)))
add(tea,'teapot',ball(.075,center=(-2.74,-.04,.57),color=(.87,.87,.80)))
add(tea,'lid',ball(.034,center=(-2.74,-.04,.64),color=ivory))
for i,x in enumerate([-2.88,-2.60]):
    add(tea,'cup_'+str(i),rod(.045,length=.055,center=(x,-.10,.54),color=ivory))
scene.include('tea_table',tea)

# Pale painted landscape panels on the right wall.
landscape=Asset('Wall landscape decoration')
add(landscape,'pale_landscape',box((.016,3.1,.69),center=(3.65,3.65,1.69),color=(.48,.53,.43)))
for i in range(8):
    yy=2.25+i*.39
    add(landscape,'tree_'+str(i),sweep_tube(points=[(3.628,yy,1.40),(3.628,yy+.04,1.74),(3.628,yy-.03,2.02)],radius=.012,color=(.30,.36,.29)))
scene.include('landscape',landscape)

realize(scene)

# Procedural cloth, wallpaper, and woven carpet materials.
def material_for(obj):
    return obj.active_material
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':
        continue
    name=obj.name.lower()
    mat=material_for(obj)
    if mat is None:
        continue
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bs=nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.78
    if 'wall' in name and 'wainscot' not in name and 'landscape' not in name:
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=28
        tex.inputs['Detail'].default_value=3
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.47
        ramp.color_ramp.elements[0].color=(.19,.28,.21,1)
        ramp.color_ramp.elements[1].position=.65
        ramp.color_ramp.elements[1].color=(.47,.53,.43,1)
        links.new(tex.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    if 'carpet' in name:
        tc=nodes.new('ShaderNodeTexCoord')
        mapping=nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(16,12,1)
        links.new(tc.outputs['Generated'],mapping.inputs[0])
        vor=nodes.new('ShaderNodeTexVoronoi')
        vor.distance='MANHATTAN'
        vor.inputs['Scale'].default_value=1
        vor.inputs['Randomness'].default_value=.24
        links.new(mapping.outputs['Vector'],vor.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        cr=ramp.color_ramp
        colors=[(.12,.19,.22,1),(.58,.42,.28,1),(.22,.27,.28,1),(.54,.29,.20,1),(.24,.31,.30,1)]
        cr.elements.remove(cr.elements[1])
        cr.elements[0].position=.12; cr.elements[0].color=colors[0]
        for p,c in zip([.23,.32,.44,.56],colors[1:]):
            cr.elements.new(p).color=c
        links.new(vor.outputs['Distance'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    if any(s in name for s in ['coverlet','seat','cushion','raised_end','back_cushion']):
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=95
        noise.inputs['Detail'].default_value=2
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.16
        bump.inputs['Distance'].default_value=.018
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.36,.38,.32,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32
set_view(position=(5.5,-9.2,3.15),target=(-.15,3.0,1.99),lens=47,sensor=36)
area_emitter(position=(1,-2.8,4.1),power=1100,size=4.0,target=(-1,2.7,1.3),color=(1,.91,.73))
area_emitter(position=(-3.0,1.5,2.2),power=95,size=.55,target=(-1.6,2.7,1.2),color=(1,.67,.24))
area_emitter(position=(-.28,4.0,1.65),power=45,size=.35,target=(-1,3.0,1.0),color=(1,.66,.22))
sc.render.resolution_x=512
sc.render.resolution_y=340
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.view_settings.view_transform='AgX'
