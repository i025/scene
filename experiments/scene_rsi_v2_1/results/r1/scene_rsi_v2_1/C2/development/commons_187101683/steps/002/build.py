from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized image bounds:
# Ochre sofa (.02,.28)-(.97,.96): two broad back cushions, two seats,
# low upholstered base, thick arms. Right lower portion is table-occluded.
# Pale gold pillow (.12,.31)-(.32,.53), softly bulging with tilted corners.
# Dark table (.32,.61)-(1,1): rectangular top, apron, square legs cropped below.
# White cup sets (.40,.54)-(.60,.68) and (.68,.55)-(.87,.70):
# open tapered cups, lateral handles, saucers, overlapping folded linens.
# Plant (.56,.33)-(.73,.65): dark tapered pot, spreading leafy branches,
# separate blue-gray flower heads with fine irregular outlines.
# Ivory wall, gray carpet, bright right window and gray drape (.80,0)-(.98,.43).
# Hidden furniture and window geometry remain uncertain.
#
# Feedback comparison: first sofa was too small; camera was too high.
# Table and cups had excessive visible top surfaces. Curtain was narrow,
# light, and rigid; foliage occupied too little lateral space.
# Preserve the hierarchy while enlarging framing and lowering the viewpoint.
#
# Expanded mesh estimate: 10 rounded upholstery parts *26 =260;
# architecture 3; table 7; two cup sets ~48 including Boolean operands;
# plant 174; curtain 99. Total approximately 591 primitives.
# No repeated Boolean slicing or subpixel geometric fabric texture.

random.seed(12)
scene = Scene('Warm sitting room')
ochre = (.59,.275,.065)
seatgold = (.69,.35,.095)
backgold = (.73,.39,.12)
pillowgold = (.83,.53,.23)
wood = (.045,.030,.022)
white = (.88,.90,.87)
green = (.14,.26,.09)
leaflight = (.26,.37,.14)

architecture = Asset('architecture')
architecture.include('carpet', box((200,200,.12), center=(0,0,-.07),
                                  color=(.29,.28,.275)))
architecture.include('ivory_wall', box((12,.12,7), center=(0,1.9,3.4),
                                       color=(.78,.765,.72)))
architecture.include('window_light_surface', box((1.3,.04,3.8),
    center=(2.12,1.805,2.25), color=(.98,.99,1)))
scene.include('architecture', architecture)

sofa = Asset('ochre_two_seat_sofa')
sofa.include('lower_front_base', fillet_box((3.48,1.02,.45), .065,
    center=(0,.55,.31), color=ochre))
sofa.include('seat_support', fillet_box((3.42,1.10,.27), .065,
    center=(0,.53,.62), color=seatgold))
sofa.include('back_frame', fillet_box((3.30,.26,1.16), .075,
    center=(0,1.02,1.01), color=ochre))
for i,x in enumerate((-.77,.77)):
    sofa.include('back_cushion_%d'%i, fillet_box((1.52,.31,.84), .075,
        center=(x,.865,1.235), color=backgold))
    sofa.include('seat_cushion_%d'%i, fillet_box((1.48,.91,.255), .085,
        center=(x,.39,.785), color=seatgold))
for side,x in [('left',-1.68),('right',1.68)]:
    sofa.include(side+'_arm', fillet_box((.37,1.20,1.23), .10,
        center=(x,.48,.735), color=ochre))
scene.include('sofa', sofa)

pillow = Asset('left_throw_pillow')
p = fillet_box((.67,.24,.66), .095,
               center=(-1.17,.49,1.24), color=pillowgold)
p.turn(axis='+y',degrees=-13)
p.turn(axis='+x',degrees=13)
pillow.include('soft_square_body',p)
scene.include('throw_pillow', pillow)

# Table support and its supported objects share this height correction.
table_shift_y = .14
table_shift_z = .055
table = Asset('dark_wood_coffee_table')
tx,ty=.78,-1.04+table_shift_y
table.include('tabletop', box((2.78,.97,.095),
    center=(tx,ty,.665+table_shift_z),color=wood))
for i,x in enumerate((tx-1.27,tx+1.27)):
    for j,y in enumerate((ty-.37,ty+.37)):
        table.include('square_leg_%d_%d'%(i,j),
            box((.085,.085,.64+table_shift_z),
                center=(x,y,(.64+table_shift_z)/2-.015),
                color=(.025,.020,.017)))
table.include('front_apron',box((2.62,.055,.12),
    center=(tx,ty-.39,.555+table_shift_z),color=wood))
table.include('left_apron',box((.055,.82,.12),
    center=(tx-1.27,ty,.555+table_shift_z),color=wood))
scene.include('coffee_table', table)

def cup_set(name,x,y,handle_side):
    y += table_shift_y
    zoff = table_shift_z
    a=Asset(name)
    napkin=box((.64,.39,.012),center=(x,y,.723+zoff),
                color=(.58,.68,.61))
    napkin.turn(axis='+z',degrees=-9)
    a.include('folded_sage_napkin',napkin)
    fold=box((.53,.34,.008),center=(x+.015,y-.012,.732+zoff),
             color=(.80,.83,.76))
    fold.turn(axis='+z',degrees=8)
    a.include('napkin_upper_fold',fold)
    a.include('saucer',rod(.205,length=.019,
        center=(x,y,.748+zoff),color=white))
    a.include('saucer_inner',rod(.154,length=.012,
        center=(x,y,.762+zoff),color=(.92,.935,.90)))
    # One hollow solid, with a slightly flared outer silhouette.
    body=rod(.113,length=.213,center=(x,y,.88+zoff),color=white)
    cavity=rod(.095,length=.24,center=(x,y,.914+zoff),color=white)
    a.include('open_cup',subtract(body,cavity))
    a.include('coffee_interior',rod(.092,length=.005,
        center=(x,y,.821+zoff),color=(.24,.18,.115)))
    pts=[]
    for k in range(9):
        angle=math.radians(-100+k*25)
        pts.append((x+handle_side*(.111+.090*math.cos(angle)),y,
                    .89+zoff+.073*math.sin(angle)))
    a.include('loop_handle',sweep_tube(points=pts,radius=.012,color=white))
    scene.include(name,a)

cup_set('left_cup_and_linen',.10,-1.05,-1)
cup_set('right_cup_and_linen',1.00,-1.17,1)

plant=Asset('flower_arrangement')
px,py=.56,-.78+table_shift_y
zo=table_shift_z
for i in range(6):
    plant.include('pot_taper_%d'%i,
        rod(.103+i*.009,length=.045,
            center=(px,py,.75+zo+i*.038),color=(.057,.066,.054)))
plant.include('pot_lip',rod(.154,length=.025,
    center=(px,py,.972+zo),color=(.075,.085,.068)))
plant.include('soil',rod(.136,length=.01,
    center=(px,py,.986+zo),color=(.047,.035,.022)))

heads=[(-.23,.015,1.30,.096),(-.10,.09,1.43,.093),
       (.045,.065,1.48,.087),(.23,.035,1.34,.103),
       (.12,-.045,1.29,.085),(-.025,-.03,1.37,.087)]
for i,(dx,dy,z,r) in enumerate(heads):
    end=(px+dx,py+dy,z+zo)
    start=(px+dx*.15,py+dy*.15,.975+zo)
    plant.include('flower_stem_%d'%i,
        rod(.008,start=start,end=end,color=green))
    for k in range(16):
        phi=k*2.39996
        zz=1-2*(k+.5)/16
        rr=math.sqrt(1-zz*zz)
        pos=(end[0]+r*.72*rr*math.cos(phi),
             end[1]+r*.72*rr*math.sin(phi),end[2]+r*.72*zz)
        col=[(.59,.64,.72),(.70,.73,.78),
             (.49,.57,.68),(.77,.79,.80)][(i+k)%4]
        plant.include('flower_%d_cluster_%d'%(i,k),
            ball(r*.29,center=pos,color=col))

for i in range(30):
    angle=i*2.39996
    height=.99+zo+(i%6)*.043
    spread=.16+(i%4)*.029
    sx,sy=px+math.cos(angle)*.035,py+math.sin(angle)*.035
    ex,ey=px+math.cos(angle)*spread,py+math.sin(angle)*spread
    plant.include('leaf_branch_%d'%i,
        rod(.004,start=(sx,sy,height-.035),
            end=(ex,ey,height+.025),color=green))
    leaf=ball(.054,center=(ex,ey,height+.028),
              color=leaflight if i%3==0 else green)
    leaf.resize((1.0,.32,.23))
    leaf.turn(axis='+y',degrees=-25)
    leaf.turn(axis='+z',degrees=math.degrees(angle))
    plant.include('pointed_leaf_%d'%i,leaf)
scene.include('plant',plant)

curtain=Asset('gathered_gray_curtain')
# Broad folds remain full above the loose gather, with a curved hanging edge.
for i in range(9):
    topx=1.45+i*.075
    gatherx=1.68+(i-4)*.040
    bottomx=1.51+i*.074
    pts=[(topx,1.60,3.45),
         (topx-.035,1.58,2.75),
         (topx-.075,1.54,2.23),
         (gatherx,1.44,1.91),
         (gatherx-.055,1.40,1.72),
         (bottomx,1.48,1.35)]
    curtain.include('hanging_fabric_fold_%02d'%i,
        sweep_tube(points=pts,radius=.072,
            color=(.15+.017*(i%3),.15+.017*(i%3),.145+.017*(i%3))))
scene.include('curtain',curtain)

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if not bsdf:
        continue
    bsdf.inputs['Roughness'].default_value=.76
    r,g,b=bsdf.inputs['Base Color'].default_value[:3]
    if r>.48 and g<.65 and b<.35:
        noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=150
        noise.inputs['Detail'].default_value=2
        bump=mat.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.20
        bump.inputs['Distance'].default_value=.012
        mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    elif .25<r<.37 and abs(r-g)<.04:
        noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=210
        bump=mat.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.3
        bump.inputs['Distance'].default_value=.015
        mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    elif r>.82 and g>.82:
        bsdf.inputs['Roughness'].default_value=.23
    elif r<.06:
        bsdf.inputs['Roughness'].default_value=.43
        if abs(r-g)>.008:
            noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=6
            noise.inputs['Detail'].default_value=2
            tex=mat.node_tree.nodes.new('ShaderNodeTexCoord')
            mapping=mat.node_tree.nodes.new('ShaderNodeVectorMath')
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(2,65,5)
            mat.node_tree.links.new(tex.outputs['Generated'],mapping.inputs[0])
            mat.node_tree.links.new(mapping.outputs['Vector'],noise.inputs['Vector'])
            bump=mat.node_tree.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.13
            bump.inputs['Distance'].default_value=.009
            mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            mat.node_tree.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])

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
background.inputs['Color'].default_value=(.78,.81,.86,1)
background.inputs['Strength'].default_value=.20

set_view(position=(-.70,-5.20,1.30),
         target=(.08,.20,1.10),lens=52,sensor=36)
area_emitter(position=(3.5,-.1,4.2),power=720,size=2.8,
             target=(0,.1,.7),color=(1,.97,.91))
area_emitter(position=(-2,-3,3.3),power=65,size=4,
             target=(0,.4,.9),color=(1,.92,.81))
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=0.0
