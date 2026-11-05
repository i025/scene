from sceneact import *
import bpy
import math
import random

# Reference inventory (estimated normalized image bounds):
# Sofa: (.02,.28)-(.97,.96), ochre fabric, two back and seat cushions,
# broad rounded arms, low front plinth; lower right is hidden by the table.
# Throw pillow: (.12,.31)-(.32,.53), pale gold, tilted, softly bulging.
# Coffee table: (.32,.61)-(1,1), dark wood, thin rectangular top and square
# legs; right edge and some legs continue outside the image.
# Two cups/saucers: (.40,.54)-(.60,.68), (.68,.55)-(.87,.70),
# white open cups with lateral loop handles, on pale folded napkins.
# Plant: (.56,.33)-(.73,.65), charcoal tapered pot, branching green leaves,
# separated pale blue/lilac flower heads with irregular clustered contours.
# Architecture: ivory wall, gray carpet, bright window at upper right,
# gathered gray curtain (.80,0)-(.98,.43). Hidden room geometry is uncertain.
#
# Named SceneAct assets below preserve all these visible object groups.
# Expanded primitive estimate: sofa/pillow ~210, table 9, cup sets ~40,
# plant ~150, curtain ~100, architecture 5: approximately 515 meshes.
# Curtain tubes and flower clusters are deliberately coarse at pixel scale.

random.seed(12)
scene = Scene('Warm sitting room')
ochre = (.64,.325,.085)
seatgold = (.72,.405,.135)
backgold = (.77,.445,.17)
pillowgold = (.84,.57,.27)
wood = (.055,.039,.028)
white = (.86,.89,.86)
green = (.17,.29,.105)
leaflight = (.29,.39,.16)

architecture = Asset('architecture')
architecture.include('carpet', box((200,200,.12), center=(0,0,-.07), color=(.32,.31,.30)))
architecture.include('ivory_wall', box((12,.12,7), center=(0,1.9,3.4), color=(.79,.775,.72)))
architecture.include('window_light_surface', box((1.3,.04,3.8), center=(2.12,1.805,2.25), color=(.98,.99,1)))
scene.include('architecture', architecture)

sofa = Asset('ochre_two_seat_sofa')
sofa.include('lower_front_base', fillet_box((3.48,1.02,.45), .065, center=(0,.55,.31), color=ochre))
sofa.include('seat_support', fillet_box((3.42,1.10,.27), .065, center=(0,.53,.62), color=seatgold))
sofa.include('back_frame', fillet_box((3.30,.26,1.16), .075, center=(0,1.02,1.01), color=ochre))
for i,x in enumerate((-.77,.77)):
    sofa.include('back_cushion_%d'%i, fillet_box((1.52,.31,.84), .075,
                 center=(x,.865,1.235), color=backgold))
    sofa.include('seat_cushion_%d'%i, fillet_box((1.48,.91,.255), .085,
                 center=(x,.39,.785), color=seatgold))
for side,x in [('left',-1.68),('right',1.68)]:
    sofa.include(side+'_arm', fillet_box((.37,1.20,1.23), .10,
                 center=(x,.48,.735), color=ochre))
scene.include('sofa',sofa)

pillow = Asset('left_throw_pillow')
p = fillet_box((.63,.22,.65), .095, center=(-1.17,.52,1.24), color=pillowgold)
p.turn(axis='+y',degrees=-13)
p.turn(axis='+x',degrees=13)
pillow.include('soft_square_body',p)
scene.include('throw_pillow', pillow)

table = Asset('dark_wood_coffee_table')
tx,ty=.78,-1.04
table.include('tabletop', box((2.58,.97,.095), center=(tx,ty,.665),color=wood))
for i,x in enumerate((tx-1.17,tx+1.17)):
    for j,y in enumerate((ty-.37,ty+.37)):
        table.include('square_leg_%d_%d'%(i,j),box((.085,.085,.64),center=(x,y,.305),color=(.032,.026,.022)))
table.include('front_apron',box((2.42,.055,.12),center=(tx,ty-.39,.555),color=wood))
table.include('left_apron',box((.055,.82,.12),center=(tx-1.17,ty,.555),color=wood))
scene.include('coffee_table', table)

def cup_set(name,x,y,handle_side):
    a=Asset(name)
    napkin=box((.64,.39,.012),center=(x,y,.723),color=(.65,.74,.68))
    napkin.turn(axis='+z',degrees=-9)
    a.include('folded_sage_napkin',napkin)
    fold=box((.53,.34,.008),center=(x+.015,y-.012,.732),color=(.79,.82,.74))
    fold.turn(axis='+z',degrees=8)
    a.include('napkin_upper_fold',fold)
    a.include('saucer',rod(.205,length=.019,center=(x,y,.748),color=white))
    a.include('saucer_inner',rod(.154,length=.012,center=(x,y,.762),color=(.92,.935,.90)))
    # Hollow cup preserves the visible opening, thick rim and deep inner shadow.
    body=rod(.112,length=.213,center=(x,y,.88),color=white)
    cavity=rod(.095,length=.24,center=(x,y,.914),color=white)
    a.include('open_cup',subtract(body,cavity))
    a.include('coffee_interior',rod(.092,length=.005,center=(x,y,.821),color=(.23,.17,.105)))
    pts=[]
    for k in range(9):
        angle=math.radians(-100+k*25)
        pts.append((x+handle_side*(.111+.090*math.cos(angle)),y,.89+.073*math.sin(angle)))
    a.include('loop_handle',sweep_tube(points=pts,radius=.012,color=white))
    scene.include(name,a)
cup_set('left_cup_and_linen',-.02,-1.05,-1)
cup_set('right_cup_and_linen',1.02,-1.17,1)

plant=Asset('flower_arrangement')
px,py=.56,-.78
# A gently stepped taper retains a distinct dark pot silhouette.
for i in range(6):
    radius=.103+i*.009
    plant.include('pot_taper_%d'%i,rod(radius,length=.045,
                  center=(px,py,.75+i*.038),color=(.073,.082,.068)))
plant.include('pot_lip',rod(.154,length=.025,center=(px,py,.972),color=(.095,.105,.085)))
plant.include('soil',rod(.136,length=.01,center=(px,py,.986),color=(.047,.035,.022)))
heads=[(-.20,.015,1.30,.096),(-.09,.09,1.43,.093),
       (.06,.065,1.48,.087),(.22,.035,1.34,.103),
       (.10,-.045,1.31,.085),(-.02,-.03,1.37,.087)]
for i,(dx,dy,z,r) in enumerate(heads):
    end=(px+dx,py+dy,z)
    start=(px+dx*.15,py+dy*.15,.975)
    plant.include('flower_stem_%d'%i,rod(.009,start=start,end=end,color=green))
    # Compact flowerlets form lobed, airy flower-head silhouettes.
    for k in range(12):
        phi=k*2.39996
        zz=1-2*(k+.5)/12
        rr=math.sqrt(1-zz*zz)
        pos=(end[0]+r*.68*rr*math.cos(phi),
             end[1]+r*.68*rr*math.sin(phi),end[2]+r*.68*zz)
        col=[(.64,.68,.73),(.72,.74,.77),(.55,.62,.70),(.79,.80,.78)][(i+k)%4]
        plant.include('flower_%d_cluster_%d'%(i,k),ball(r*.34,center=pos,color=col))
for i in range(24):
    angle=i*2.39996
    height=.99+(i%6)*.043
    spread=.13+(i%4)*.028
    sx,sy=px+math.cos(angle)*.035,py+math.sin(angle)*.035
    ex,ey=px+math.cos(angle)*spread,py+math.sin(angle)*spread
    plant.include('leaf_branch_%d'%i,rod(.004,start=(sx,sy,height-.035),end=(ex,ey,height+.025),color=green))
    leaf=ball(.048,center=(ex,ey,height+.028),color=leaflight if i%3==0 else green)
    leaf.resize((1.0,.35,.27))
    leaf.turn(axis='+y',degrees=-25)
    leaf.turn(axis='+z',degrees=math.degrees(angle))
    plant.include('pointed_leaf_%d'%i,leaf)
scene.include('plant',plant)

curtain=Asset('gathered_gray_curtain')
# Variable paths narrow into the gathered fold, then drape outward below.
for i in range(11):
    topx=1.61+i*.060
    gatherx=1.90+(i-5)*.027
    bottomx=1.64+i*.062
    pts=[(topx,1.60,3.45),(topx-.02,1.59,2.90),
         (topx-.035,1.56,2.35),(gatherx,1.54,1.96),
         (gatherx-.035,1.52,1.78),(bottomx,1.49,1.35)]
    tube=sweep_tube(points=pts,radius=.062,color=(.24+.014*(i%3),.235+.014*(i%3),.215+.014*(i%3)))
    curtain.include('hanging_fabric_fold_%02d'%i,tube)
scene.include('curtain',curtain)

realize(scene)

# Shared procedural surface shading supplies fabric and carpet grain without
# adding geometric microstructure.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Roughness'].default_value=.73
        color=bsdf.inputs['Base Color'].default_value
        r,g,b=color[:3]
        if r>.48 and g<.65 and b<.35:
            noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=145
            noise.inputs['Detail'].default_value=2
            bump=mat.node_tree.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.16
            bump.inputs['Distance'].default_value=.018
            mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            mat.node_tree.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
        elif .28<r<.37 and abs(r-g)<.04:
            noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=210
            bump=mat.node_tree.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.3
            bump.inputs['Distance'].default_value=.02
            mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            mat.node_tree.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
        elif r>.82 and g>.82:
            bsdf.inputs['Roughness'].default_value=.24
        elif r<.08:
            bsdf.inputs['Roughness'].default_value=.42

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
background.inputs['Strength'].default_value=.32

set_view(position=(-.50,-6.8,2.83),target=(.13,.20,1.04),lens=47,sensor=36)
area_emitter(position=(3.5,-.1,4.2),power=650,size=3.0,target=(0,.1,.7),color=(1,.97,.91))
area_emitter(position=(-2,-3,3.3),power=100,size=4,target=(0,.4,.9),color=(1,.92,.81))
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=0.1
