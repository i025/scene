from sceneact import *
import bpy, math

# Chaise bounds approximately (0.035,.24)-(.83,.93); tall back at upper left,
# rounded foot at lower right. Wall panels behind; cropped cane chair at lower left.
# Long rails recede toward image left. Camera looks downward from front/right.
scene = Scene('French chaise interior')
CAMERA = (3.0, -5.5, 3.7)
TARGET = (-.02, .12, .86)
cream = (.69,.66,.55)
linen = (.82,.77,.65)
wood = (.30,.36,.29)
gilt = (.59,.54,.39)
wall = (.72,.70,.63)

architecture = Asset('Paneled cream room')
architecture.include('floor', box((9,8,.12), center=(0,0,-.075), color=(.24,.125,.065)))
architecture.include('back_wall', box((8,.15,3.5), center=(0,1.14,1.7), color=wall))
architecture.include('right_return', box((.17,2.3,3.5), center=(2.27,2.2,1.7), color=(.77,.75,.68)))
for i,(z,h,d) in enumerate(((.08,.12,.07),(.20,.035,.042),(.37,.045,.035),(1.54,.055,.048),(1.65,.03,.035),(1.94,.07,.05),(2.12,.035,.04))):
    architecture.include('horizontal_molding_%d'%i, box((8,d,h),center=(0,1.035,z),color=(.80,.78,.70)))
# Large recessed rectangular panel outlines.
for j,(left,right) in enumerate(((-3.0,-1.45),(-1.40,1.82))):
    for k,delta in enumerate((0,.026)):
        yy=1.048-.012*k
        for n,z in enumerate((.43+delta,1.48-delta)):
            architecture.include('panel_%d_%d_h%d'%(j,k,n),box((right-left-2*delta,.025,.018),center=((left+right)/2,yy,z),color=(.79,.77,.69)))
        for n,x in enumerate((left+delta,right-delta)):
            architecture.include('panel_%d_%d_v%d'%(j,k,n),box((.018,.025,1.05-2*delta),center=(x,yy,.955),color=(.79,.77,.69)))
for i,x in enumerate((-1.55,.22,1.96)):
    architecture.include('wall_seam_%d'%i,box((.009,.007,3.0),center=(x,1.056,1.5),color=(.43,.42,.35)))
scene.include('architecture',architecture)

# Restrained parquet boards, with alternating grain directions.
floorboards=Asset('Parquet surface')
for i in range(10):
    for j in range(6):
        x=-3.6+i*.72
        y=-2.5+j*.60
        c=(.255+.012*((i+2*j)%4),.143+.009*((i+j)%3),.083)
        p=box((.70,.585,.012),center=(x,y,-.007),color=c)
        floorboards.include('board_%d_%d'%(i,j),p)
scene.include('parquet',floorboards)

chaise=Asset('Antique painted chaise longue')
# Upholstered seat with softly rounded end.
chaise.include('seat_cushion',fillet_box((2.28,.91,.27),radius=.132,center=(.03,0,.735),color=linen))
chaise.include('under_seat',fillet_box((2.22,.88,.12),radius=.055,center=(0,0,.575),color=wood))
# Upholstered tall curved headboard.
back=ball(1,center=(-1.04,.025,1.12),color=linen)
back.resize((.14,.49,.49))
back.turn('y',-13)
chaise.include('padded_back',back)
# Top bow and side posts around the back.
bow=[(-.98,-.46,.71),(-1.11,-.48,1.12),(-1.20,-.43,1.49),
     (-1.23,-.22,1.62),(-1.23,.10,1.64),(-1.18,.38,1.54),
     (-1.08,.46,1.27),(-.94,.46,.78)]
chaise.include('back_frame',sweep_tube(points=bow,radius=.032,color=wood))
chaise.include('back_gilded_edge',sweep_tube(points=[(x+.016,y-.014,z+.014) for x,y,z in bow],radius=.010,color=gilt))
# The near upholstered arm rises at the head, then sweeps into the seat.
arm=ball(1,center=(-.81,-.433,.965),color=linen)
arm.resize((.36,.063,.30))
arm.turn('y',-24)
chaise.include('near_side_upholstery',arm)
armline=[(-1.18,-.47,1.43),(-1.07,-.49,1.24),(-.91,-.49,1.12),
         (-.63,-.49,1.045),(-.50,-.49,.80),(-.44,-.49,.61)]
chaise.include('near_arm_wood',sweep_tube(points=armline,radius=.030,color=wood))
chaise.include('near_arm_trim',sweep_tube(points=[(x,y-.023,z+.012) for x,y,z in armline],radius=.009,color=gilt))
fararm=[(-1.17,.45,1.47),(-.98,.46,1.26),(-.70,.46,1.16),(-.61,.46,.87)]
chaise.include('far_arm',sweep_tube(points=fararm,radius=.026,color=wood))
# Carved apron follows the visible long edge.
for side in (-1,1):
    yy=side*.443
    pts=[(-1.02,yy,.60),(-.77,yy,.57),(-.36,yy,.565),(.12,yy,.535),(.58,yy,.54),(1.02,yy,.56),(1.13,yy,.49)]
    chaise.include('apron_%d'%side,sweep_tube(points=pts,radius=.043,color=wood))
    chaise.include('apron_edge_%d'%side,sweep_tube(points=[(x,y+side*.031,z+.025) for x,y,z in pts],radius=.009,color=gilt))
# Four cabriole legs, including splayed feet.
for i,x in enumerate((-.91,.98)):
    for j,y in enumerate((-.36,.36)):
        pts=[(x,y,.58),(x+.035,y,.43),(x-.035,y,.24),(x-.06,y-.025,.085),(x+.005,y-.035,.055)]
        chaise.include('leg_%d_%d'%(i,j),sweep_tube(points=pts,radius=.031,color=wood))
        chaise.include('leg_inlay_%d_%d'%(i,j),sweep_tube(points=[(a,b-.025,c) for a,b,c in pts[:-1]],radius=.008,color=gilt))
# Small carved floral medallions.
for i,x in enumerate((-.96,.12,1.04)):
    z=.55 if i!=1 else .515
    for k in range(5):
        a=k*math.tau/5
        node=ball(.025,center=(x+math.cos(a)*.038,-.487,z+math.sin(a)*.027),color=gilt)
        node.resize((1,.42,.8))
        chaise.include('carving_%d_%d'%(i,k),node)
# Pillow resting diagonally against the tall back.
pillow=fillet_box((.27,.64,.65),radius=.125,center=(-.87,-.015,1.18),color=(.86,.80,.67))
pillow.turn('y',-22)
pillow.turn('x',-9)
chaise.include('loose_cream_pillow',pillow)
# Green museum label on the seat.
label=box((.085,.15,.005),center=(.72,.10,.877),color=(.055,.22,.18))
label.turn('z',-7)
chaise.include('green_label',label)
for k in range(3):
    chaise.include('label_print_%d'%k,box((.037,.004,.002),center=(.72,.07+k*.019,.881),color=(.73,.75,.60)))
scene.include('chaise',chaise)

curtains=Asset('Window and ivory drapes')
curtains.include('window_glow',box((.035,1.4,3.3),center=(-1.66,.28,1.6),color=(.94,.94,.86)))
for i in range(8):
    x=-1.61+.027*math.sin(i*1.4)
    y=-.55+i*.092
    curtains.include('curtain_fold_%d'%i,rod(.052,start=(x,y,.07),end=(x-.07,y,2.8),color=(.80+.012*(i%3),.77+.013*(i%3),.67+.02*(i%3))))
scene.include('curtains',curtains)

foreground=Asset('Cropped cane chair')
# A partial secondary chair enters the lower left corner.
chairseat=fillet_box((.64,.63,.07),radius=.033,center=(-1.28,-1.32,.45),color=wood)
foreground.include('seat_frame',chairseat)
foreground.include('woven_seat',box((.54,.53,.022),center=(-1.28,-1.32,.494),color=(.47,.33,.20)))
for i in range(15):
    x=-1.53+i*.035
    foreground.include('cane_x_%d'%i,rod(.003,start=(x,-1.565,.510),end=(x,-1.075,.510),color=(.70,.57,.36)))
for i in range(14):
    y=-1.55+i*.035
    foreground.include('cane_y_%d'%i,rod(.003,start=(-1.535,y,.513),end=(-1.025,y,.513),color=(.68,.54,.34)))
for i,x in enumerate((-1.53,-1.03)):
    foreground.include('leg_%d'%i,rod(.028,start=(x,-1.50,.03),end=(x,-1.50,.46),color=wood))
scene.include('foreground_chair',foreground)

print('Primitive count:',sum(n.solid is not None for n in scene.traverse()))
realize(scene)

# Procedural woven fabric; small rose motifs on parallel upholstery stripes.
fabric=bpy.data.materials.new('Ivory woven striped floral upholstery')
fabric.diffuse_color=(*linen,1)
fabric.use_nodes=True
nodes=fabric.node_tree.nodes
links=fabric.node_tree.links
bs=nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.86
tex=nodes.new('ShaderNodeTexCoord')
sep=nodes.new('ShaderNodeSeparateXYZ')
links.new(tex.outputs['Generated'],sep.inputs[0])
wave=nodes.new('ShaderNodeTexWave')
wave.wave_type='BANDS'
wave.bands_direction='Y'
wave.inputs['Scale'].default_value=18
wave.inputs['Distortion'].default_value=.3
links.new(tex.outputs['Generated'],wave.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.68
ramp.color_ramp.elements[0].color=(.81,.76,.65,1)
ramp.color_ramp.elements[1].position=.78
ramp.color_ramp.elements[1].color=(.59,.46,.40,1)
links.new(wave.outputs['Color'],ramp.inputs[0])
noise=nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=150
noise.inputs['Detail'].default_value=2
links.new(tex.outputs['Generated'],noise.inputs['Vector'])
bump=nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.15
bump.inputs['Distance'].default_value=.008
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs['Normal'],bs.inputs['Normal'])
links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and any(s in obj.name.lower() for s in ('seat_cushion','padded_back','near_side_upholstery')):
        obj.data.materials.clear()
        obj.data.materials.append(fabric)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.68,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
set_view(CAMERA,TARGET,lens=48)
area_emitter((-3,-1,3.4),power=650,size=3.0,target=(0,0,.7),color=(1,.94,.82))
area_emitter((1,-3,3.6),power=130,size=3,target=(0,0,.8),color=(1,.95,.88))
sc.view_settings.view_transform='AgX'
