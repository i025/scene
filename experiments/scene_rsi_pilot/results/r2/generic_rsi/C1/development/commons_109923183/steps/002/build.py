from sceneact import *
import bpy, math

# Reference anchors: back crown (.04,.24), arm (.25,.51), seat foot (.82,.65),
# front foot (.78,.93), cropped cane chair (.00,.81), wall base (.86,.50).
# Previous build was globally too small, with overly diagonal wall perspective.
# Move camera closer and toward the front; preserve the chaise assembly.
scene = Scene('French chaise interior')
CAMERA = (1.05, -4.25, 3.15)
TARGET = (-.06, .02, .86)
LENS = 50
linen = (.80,.73,.62)
wood = (.25,.30,.245)
gilt = (.55,.48,.34)
wall = (.66,.64,.57)

architecture = Asset('Paneled cream room')
architecture.include('floor', box((10,10,.12),center=(0,0,-.07),color=(.19,.085,.038)))
wallparts = Asset('Wall and applied moldings')
wallparts.include('back_wall',box((8,.15,3.5),center=(0,1.14,1.7),color=wall))
for i,(z,h,d) in enumerate(((.08,.12,.07),(.20,.035,.042),(.37,.045,.035),(1.54,.055,.048),(1.65,.03,.035),(1.94,.07,.05),(2.12,.035,.04))):
    wallparts.include('horizontal_molding_%d'%i,box((8,d,h),center=(0,1.035,z),color=(.73,.70,.62)))
for j,(left,right) in enumerate(((-3,-1.45),(-1.40,1.82))):
    for k,delta in enumerate((0,.026)):
        yy=1.048-.012*k
        for n,z in enumerate((.43+delta,1.48-delta)):
            wallparts.include('panel_%d_%d_h%d'%(j,k,n),box((right-left-2*delta,.025,.018),center=((left+right)/2,yy,z),color=(.74,.71,.63)))
        for n,x in enumerate((left+delta,right-delta)):
            wallparts.include('panel_%d_%d_v%d'%(j,k,n),box((.018,.025,1.05-2*delta),center=(x,yy,.955),color=(.74,.71,.63)))
for i,x in enumerate((-1.55,.22,1.96)):
    wallparts.include('wall_seam_%d'%i,box((.006,.007,3),center=(x,1.056,1.5),color=(.41,.39,.33)))
wallparts.turn('z',11,pivot=(0,1.14,0))
architecture.include('paneled_wall',wallparts)
architecture.include('right_return',box((.18,1.9,3.5),center=(2.08,1.96,1.7),color=(.73,.71,.64)))
scene.include('architecture',architecture)

# Close fitting wood parquet, avoiding the previous tile-like wide seams.
parquet=Asset('Dark oak parquet')
for i in range(9):
    for j in range(6):
        c=(.185+.014*((i+2*j)%4),.082+.008*((i+j)%3),.038+.004*(j%3))
        board=box((.79,.395,.012),center=(-3.2+i*.8,-2+j*.4,-.003),color=c)
        board.turn('z',35,pivot=(0,0,0))
        parquet.include('oak_board_%d_%d'%(i,j),board)
scene.include('parquet',parquet)

chaise=Asset('Antique painted chaise longue')
chaise.include('seat_cushion',fillet_box((2.28,.91,.27),radius=.132,center=(.03,0,.735),color=linen))
chaise.include('under_seat',fillet_box((2.22,.88,.12),radius=.055,center=(0,0,.575),color=wood))
back=ball(1,center=(-1.04,.025,1.12),color=linen)
back.resize((.14,.49,.49))
back.turn('y',-13)
chaise.include('padded_back',back)
bow=[(-.98,-.46,.71),(-1.11,-.48,1.12),(-1.20,-.43,1.49),
     (-1.23,-.22,1.62),(-1.23,.10,1.64),(-1.18,.38,1.54),
     (-1.08,.46,1.27),(-.94,.46,.78)]
chaise.include('back_frame',sweep_tube(points=bow,radius=.032,color=wood))
chaise.include('back_gilded_edge',sweep_tube(points=[(x+.016,y-.014,z+.014) for x,y,z in bow],radius=.010,color=gilt))
arm=ball(1,center=(-.81,-.433,.965),color=linen)
arm.resize((.36,.063,.30))
arm.turn('y',-24)
chaise.include('near_side_upholstery',arm)
armline=[(-1.18,-.47,1.43),(-1.07,-.49,1.24),(-.91,-.49,1.12),
         (-.63,-.49,1.045),(-.50,-.49,.80),(-.44,-.49,.61)]
chaise.include('near_arm_wood',sweep_tube(points=armline,radius=.030,color=wood))
chaise.include('near_arm_trim',sweep_tube(points=[(x,y-.023,z+.012) for x,y,z in armline],radius=.009,color=gilt))
chaise.include('far_arm',sweep_tube(points=[(-1.17,.45,1.47),(-.98,.46,1.26),(-.70,.46,1.16),(-.61,.46,.87)],radius=.026,color=wood))
for side in (-1,1):
    yy=side*.443
    pts=[(-1.02,yy,.60),(-.77,yy,.57),(-.36,yy,.565),(.12,yy,.535),(.58,yy,.54),(1.02,yy,.56),(1.13,yy,.49)]
    chaise.include('apron_%d'%side,sweep_tube(points=pts,radius=.043,color=wood))
    chaise.include('apron_edge_%d'%side,sweep_tube(points=[(x,y+side*.031,z+.025) for x,y,z in pts],radius=.009,color=gilt))
for i,x in enumerate((-.91,.98)):
    for j,y in enumerate((-.36,.36)):
        pts=[(x,y,.58),(x+.035,y,.43),(x-.035,y,.24),(x-.06,y-.025,.085),(x+.005,y-.035,.055)]
        chaise.include('leg_%d_%d'%(i,j),sweep_tube(points=pts,radius=.031,color=wood))
        chaise.include('leg_inlay_%d_%d'%(i,j),sweep_tube(points=[(a,b-.025,c) for a,b,c in pts[:-1]],radius=.008,color=gilt))
for i,x in enumerate((-.96,.12,1.04)):
    z=.55 if i!=1 else .515
    for k in range(5):
        a=k*math.tau/5
        node=ball(.025,center=(x+math.cos(a)*.038,-.487,z+math.sin(a)*.027),color=gilt)
        node.resize((1,.42,.8))
        chaise.include('carving_%d_%d'%(i,k),node)
pillow=fillet_box((.29,.66,.65),radius=.125,center=(-.86,-.015,1.18),color=(.84,.76,.62))
pillow.turn('y',-22)
pillow.turn('x',-9)
chaise.include('loose_cream_pillow',pillow)
label=box((.085,.15,.005),center=(.72,.10,.877),color=(.055,.22,.18))
label.turn('z',-7)
chaise.include('green_label',label)
for k in range(3):
    chaise.include('label_print_%d'%k,box((.037,.004,.002),center=(.72,.07+k*.019,.881),color=(.73,.75,.60)))
scene.include('chaise',chaise)

curtains=Asset('Window and ivory drapes')
curtains.include('window_glow',box((.035,1.4,3.3),center=(-1.78,.28,1.6),color=(.94,.94,.86)))
for i in range(7):
    x=-1.73+.025*math.sin(i*1.4)
    y=-.44+i*.085
    curtains.include('curtain_fold_%d'%i,rod(.049,start=(x,y,.07),end=(x-.07,y,2.8),color=(.78+.012*(i%3),.74+.013*(i%3),.64+.02*(i%3))))
scene.include('curtains',curtains)

foreground=Asset('Cropped cane chair')
foreground.include('seat_frame',fillet_box((.64,.63,.07),radius=.033,center=(-1.18,-1.48,.45),color=wood))
foreground.include('woven_seat',box((.54,.53,.022),center=(-1.18,-1.48,.494),color=(.36,.23,.13)))
for i in range(15):
    x=-1.43+i*.035
    foreground.include('cane_x_%d'%i,rod(.003,start=(x,-1.725,.510),end=(x,-1.235,.510),color=(.61,.47,.28)))
for i in range(14):
    y=-1.71+i*.035
    foreground.include('cane_y_%d'%i,rod(.003,start=(-1.435,y,.513),end=(-.925,y,.513),color=(.61,.47,.28)))
for i,x in enumerate((-1.43,-.93)):
    foreground.include('leg_%d'%i,rod(.028,start=(x,-1.66,.03),end=(x,-1.66,.46),color=wood))
scene.include('foreground_chair',foreground)

print('Primitive count:',sum(n.solid is not None for n in scene.traverse()))
realize(scene)

# SceneAct primitive names are generic. Identify upholstery by its shared finish.
# World coordinates maintain one continuous fabric scale across separate meshes.
for mat in list(bpy.data.materials):
    c=mat.diffuse_color
    if max(abs(c[i]-linen[i]) for i in range(3)) < .015:
        mat.use_nodes=True
        n=mat.node_tree.nodes
        l=mat.node_tree.links
        bs=n.get('Principled BSDF')
        bs.inputs['Roughness'].default_value=.88
        coord=n.new('ShaderNodeTexCoord')
        wave=n.new('ShaderNodeTexWave')
        wave.wave_type='BANDS'
        wave.bands_direction='Y'
        wave.inputs['Scale'].default_value=10
        l.new(coord.outputs['Object'],wave.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.88
        ramp.color_ramp.elements[0].color=(.80,.73,.62,1)
        ramp.color_ramp.elements[1].position=.97
        ramp.color_ramp.elements[1].color=(.58,.40,.36,1)
        l.new(wave.outputs['Fac'],ramp.inputs[0])
        l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        noise=n.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=165
        noise.inputs['Detail'].default_value=2
        l.new(coord.outputs['Object'],noise.inputs['Vector'])
        bump=n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.13
        bump.inputs['Distance'].default_value=.005
        l.new(noise.outputs['Fac'],bump.inputs['Height'])
        l.new(bump.outputs['Normal'],bs.inputs['Normal'])

# Subtle grain makes the floor read as polished wood.
for mat in list(bpy.data.materials):
    c=mat.diffuse_color
    if .17<c[0]<.24 and .07<c[1]<.12 and c[2]<.065:
        mat.use_nodes=True
        n=mat.node_tree.nodes
        l=mat.node_tree.links
        bs=n.get('Principled BSDF')
        bs.inputs['Roughness'].default_value=.34
        tex=n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=7
        tex.inputs['Detail'].default_value=3
        coord=n.new('ShaderNodeTexCoord')
        mapping=n.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(2,65,4)
        l.new(coord.outputs['Generated'],mapping.inputs[0])
        l.new(mapping.outputs[0],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color=(c[0]*.65,c[1]*.65,c[2]*.65,1)
        ramp.color_ramp.elements[1].color=(c[0]*1.2,c[1]*1.2,c[2]*1.2,1)
        l.new(tex.outputs['Fac'],ramp.inputs[0])
        l.new(ramp.outputs['Color'],bs.inputs['Base Color'])

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.68,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-3,-1,3.4),power=650,size=3,target=(0,0,.7),color=(1,.94,.82))
area_emitter((1,-3,3.6),power=130,size=3,target=(0,0,.8),color=(1,.95,.88))
sc.view_settings.view_transform='AgX'
