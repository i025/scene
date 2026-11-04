from sceneact import *
import bpy, math
from mathutils import Vector

# Anchors: reference crown (20,94), near arm (125,198), seat end (422,250),
# apron (275,295), front foot (398,355), wall base (445,192).
# Step 2 matches the seat and legs reasonably; its head is narrow and too high.
# Open the headboard toward the camera, lower its crown, preserve the seat camera.
scene = Scene('French chaise interior')
CAMERA = (1.05,-4.25,3.15)
TARGET = (-.06,.02,.89)
LENS = 50
linen = (.80,.73,.62)
wood = (.25,.30,.245)
gilt = (.55,.48,.34)
wall = (.66,.64,.57)

architecture = Asset('Paneled cream room')
architecture.include('oak_floor',box((10,10,.12),center=(0,0,-.065),color=(.16,.065,.028)))
wallparts = Asset('Wall and applied moldings')
wallparts.include('back_wall',box((8,.15,3.5),center=(0,1.14,1.7),color=wall))
for i,(z,h,d) in enumerate(((.08,.12,.07),(.20,.035,.042),(.37,.045,.035),
                           (1.54,.055,.048),(1.65,.03,.035),(1.94,.07,.05),(2.12,.035,.04))):
    wallparts.include('horizontal_molding_%d'%i,
        box((8,d,h),center=(0,1.035,z),color=(.73,.70,.62)))
for j,(left,right) in enumerate(((-3,-1.45),(-1.40,1.82))):
    for k,delta in enumerate((0,.026)):
        yy=1.048-.012*k
        for n,z in enumerate((.43+delta,1.48-delta)):
            wallparts.include('panel_%d_%d_h%d'%(j,k,n),
                box((right-left-2*delta,.025,.018),
                    center=((left+right)/2,yy,z),color=(.74,.71,.63)))
        for n,x in enumerate((left+delta,right-delta)):
            wallparts.include('panel_%d_%d_v%d'%(j,k,n),
                box((.018,.025,1.05-2*delta),
                    center=(x,yy,.955),color=(.74,.71,.63)))
for i,x in enumerate((-1.55,.22,1.96)):
    wallparts.include('wall_seam_%d'%i,
        box((.006,.007,3),center=(x,1.056,1.5),color=(.41,.39,.33)))
wallparts.turn('z',11,pivot=(0,1.14,0))
architecture.include('paneled_wall',wallparts)
architecture.include('right_return',
    box((.18,1.9,3.5),center=(2.08,1.96,1.7),color=(.73,.71,.64)))
scene.include('architecture',architecture)

chaise = Asset('Antique painted chaise longue')
chaise.include('seat_cushion',
    fillet_box((2.28,.91,.27),radius=.132,center=(.03,0,.735),color=linen))
chaise.include('under_seat',
    fillet_box((2.22,.88,.12),radius=.055,center=(0,0,.575),color=wood))

head = Asset('Broad curved upholstered headboard')
back = ball(1,center=(-1.04,.025,1.12),color=linen)
back.resize((.14,.49,.49))
back.turn('y',-13)
head.include('padded_back',back)
bow=[(-.98,-.46,.71),(-1.11,-.48,1.12),(-1.20,-.43,1.49),
     (-1.23,-.22,1.62),(-1.23,.10,1.64),(-1.18,.38,1.54),
     (-1.08,.46,1.27),(-.94,.46,.78)]
head.include('back_frame',sweep_tube(points=bow,radius=.032,color=wood))
head.include('back_gilded_edge',
    sweep_tube(points=[(x+.016,y-.014,z+.014) for x,y,z in bow],
               radius=.010,color=gilt))
# A small crest on the continuous painted frame.
for k in range(5):
    a=math.pi*k/4
    ornament=ball(.026,center=(-1.235,-.08+.075*math.cos(a),1.65+.028*math.sin(a)),color=gilt)
    ornament.resize((.55,1,.8))
    head.include('crest_%d'%k,ornament)
head.resize((1,1,.88),pivot=(-1.04,0,.72))
head.turn('z',-32,pivot=(-1.04,0,.75))
chaise.include('headboard',head)

# A broad, gently curved upholstered side panel rather than a circular pad.
panel=fillet_box((.60,.115,.44),radius=.052,
                 center=(-.87,-.433,.938),color=linen)
panel.turn('y',-18)
chaise.include('near_side_upholstery',panel)
armline=[(-1.38,-.43,1.32),(-1.21,-.49,1.18),(-.98,-.49,1.10),
         (-.69,-.49,1.045),(-.56,-.49,.80),(-.47,-.49,.61)]
chaise.include('near_arm_wood',sweep_tube(points=armline,radius=.030,color=wood))
chaise.include('near_arm_trim',
    sweep_tube(points=[(x,y-.023,z+.012) for x,y,z in armline],
               radius=.009,color=gilt))
chaise.include('far_arm',
    sweep_tube(points=[(-.94,.43,1.40),(-.82,.46,1.27),
                       (-.64,.46,1.16),(-.61,.46,.87)],
               radius=.026,color=wood))
for side in (-1,1):
    yy=side*.443
    pts=[(-1.02,yy,.60),(-.77,yy,.57),(-.36,yy,.565),
         (.12,yy,.535),(.58,yy,.54),(1.02,yy,.56),(1.13,yy,.49)]
    chaise.include('apron_%d'%side,sweep_tube(points=pts,radius=.043,color=wood))
    chaise.include('apron_edge_%d'%side,
        sweep_tube(points=[(x,y+side*.031,z+.025) for x,y,z in pts],
                   radius=.009,color=gilt))
for i,x in enumerate((-.91,.98)):
    for j,y in enumerate((-.36,.36)):
        pts=[(x,y,.58),(x+.035,y,.43),(x-.035,y,.24),
             (x-.06,y-.025,.085),(x+.005,y-.035,.055)]
        chaise.include('leg_%d_%d'%(i,j),sweep_tube(points=pts,radius=.031,color=wood))
        chaise.include('leg_inlay_%d_%d'%(i,j),
            sweep_tube(points=[(a,b-.025,c) for a,b,c in pts[:-1]],
                       radius=.008,color=gilt))
for i,x in enumerate((-.96,.12,1.04)):
    z=.55 if i!=1 else .515
    for k in range(5):
        a=k*math.tau/5
        node=ball(.025,center=(x+math.cos(a)*.038,-.487,z+math.sin(a)*.027),color=gilt)
        node.resize((1,.42,.8))
        chaise.include('carving_%d_%d'%(i,k),node)

# The loose square pillow presents its broad face toward the viewer.
pillow=fillet_box((.59,.23,.62),radius=.105,
                  center=(-1.00,-.015,1.16),color=(.84,.76,.62))
pillow.turn('y',-18)
pillow.turn('x',12)
pillow.turn('z',-16)
chaise.include('loose_cream_pillow',pillow)
label=box((.085,.15,.005),center=(.72,.10,.877),color=(.055,.22,.18))
label.turn('z',-7)
chaise.include('green_label',label)
for k in range(3):
    chaise.include('label_print_%d'%k,
        box((.037,.004,.002),center=(.72,.07+k*.019,.881),color=(.73,.75,.60)))
scene.include('chaise',chaise)

curtains=Asset('Window and ivory drapes')
curtains.include('window_glow',
    box((.035,1.4,3.3),center=(-1.95,.28,1.6),color=(.94,.94,.86)))
for i in range(7):
    x=-1.90+.025*math.sin(i*1.4)
    y=-.44+i*.085
    curtains.include('curtain_fold_%d'%i,
        rod(.049,start=(x,y,.07),end=(x-.07,y,2.8),
            color=(.78+.012*(i%3),.74+.013*(i%3),.64+.02*(i%3))))
scene.include('curtains',curtains)

foreground=Asset('Cropped cane chair')
foreground.include('seat_frame',
    fillet_box((.64,.63,.07),radius=.033,center=(-1.18,-1.48,.45),color=wood))
foreground.include('woven_seat',
    box((.54,.53,.022),center=(-1.18,-1.48,.494),color=(.36,.23,.13)))
for i in range(15):
    x=-1.43+i*.035
    foreground.include('cane_x_%d'%i,
        rod(.003,start=(x,-1.725,.510),end=(x,-1.235,.510),color=(.61,.47,.28)))
for i in range(14):
    y=-1.71+i*.035
    foreground.include('cane_y_%d'%i,
        rod(.003,start=(-1.435,y,.513),end=(-.925,y,.513),color=(.61,.47,.28)))
for i,x in enumerate((-1.43,-.93)):
    foreground.include('leg_%d'%i,
        rod(.028,start=(x,-1.66,.03),end=(x,-1.66,.46),color=wood))
scene.include('foreground_chair',foreground)

print('Primitive count:',sum(n.solid is not None for n in scene.traverse()))
realize(scene)

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

# Continuous narrow oak boards with subtle seams and longitudinal grain.
oak=bpy.data.materials.new('Polished dark oak boards')
oak.use_nodes=True
n=oak.node_tree.nodes
l=oak.node_tree.links
bs=n.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.32
coord=n.new('ShaderNodeTexCoord')
rotate=n.new('ShaderNodeVectorRotate')
rotate.rotation_type='AXIS_ANGLE'
rotate.inputs['Axis'].default_value=(0,0,1)
rotate.inputs['Angle'].default_value=math.radians(35)
l.new(coord.outputs['Object'],rotate.inputs['Vector'])
brick=n.new('ShaderNodeTexBrick')
brick.inputs['Scale'].default_value=1
brick.inputs['Brick Width'].default_value=.8
brick.inputs['Row Height'].default_value=.13
brick.inputs['Mortar Size'].default_value=.0012
brick.inputs['Mortar Smooth'].default_value=.001
brick.inputs['Color1'].default_value=(.105,.038,.016,1)
brick.inputs['Color2'].default_value=(.205,.088,.039,1)
brick.inputs['Mortar'].default_value=(.055,.021,.009,1)
l.new(rotate.outputs['Vector'],brick.inputs['Vector'])
stretch=n.new('ShaderNodeVectorMath')
stretch.operation='MULTIPLY'
stretch.inputs[1].default_value=(3,160,3)
l.new(rotate.outputs['Vector'],stretch.inputs[0])
noise=n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=3
noise.inputs['Detail'].default_value=2
l.new(stretch.outputs[0],noise.inputs['Vector'])
mix=n.new('ShaderNodeMixRGB')
mix.blend_type='MULTIPLY'
mix.inputs[0].default_value=.28
l.new(brick.outputs['Color'],mix.inputs[1])
l.new(noise.outputs['Fac'],mix.inputs[2])
l.new(mix.outputs[0],bs.inputs['Base Color'])
for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        corners=[obj.matrix_world @ Vector(v) for v in obj.bound_box]
        if max(v.z for v in corners)<.01:
            obj.data.materials.clear()
            obj.data.materials.append(oak)

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
