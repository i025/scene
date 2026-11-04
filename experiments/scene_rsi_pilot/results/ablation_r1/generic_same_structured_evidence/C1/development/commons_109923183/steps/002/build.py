import bpy, math, random
from sceneact import *

random.seed(12)

# Review: chaise was too small and too far right; move camera closer,
# preserving focal length. Target anchors: crest (.06,.25), foot (.82,.70).
# Wall lines descended too much to the right: reduce camera azimuth and
# apply a small camera roll. Increase downward view for the broad seat.
# Floor and upholstery were washed out: darker walnut, lower window power,
# and explicit world-coordinate rose motifs on every upholstered surface.
CAMERA_POSITION = (1.22, -4.90, 3.65)
CAMERA_TARGET = (.12, .08, .96)
CAMERA_LENS = 48
CAMERA_ROLL = -5.0
WALL_Y = 1.02
WINDOW_POWER = 390
SEAT_LENGTH = 2.65
SEAT_WIDTH = .98
SEAT_HEIGHT = .735

cream = (.65,.605,.51)
paint = (.29,.36,.31)
gold = (.56,.47,.31)
fabric = (.77,.70,.59)

scene = Scene('French sitting room')

room = Asset('Paneled architecture')
room.include('floor_base', box((16,12,.12), center=(0,0,-.08),
                               color=(.105,.049,.028)))
room.include('wall', box((11,.18,4), center=(0,WALL_Y+.09,2),
                         color=cream))
scene.include('architecture', room)

parquet = Asset('Walnut parquet')
L,W = .63,.14
idx = 0
for i in range(-9,10):
    for j in range(-23,24):
        ox,oy = i*L-j*W, i*L+j*W
        for cx,cy,sx,sy in [(ox+L/2,oy+W/2,L,W),
                            (ox+L+W/2,oy+L/2,W,L)]:
            if abs(cx)>5.5 or abs(cy)>5:
                continue
            s=random.uniform(.75,1.16)
            parquet.include('board_%04d'%idx,
                box((sx-.003,sy-.003,.025),center=(cx,cy,-.006),
                    color=(.135*s,.065*s,.037*s)))
            idx+=1
scene.include('parquet',parquet)

trim=Asset('Wall molding')
for k,(z,d,h) in enumerate([
    (.10,.075,.15),(.22,.055,.035),(.30,.032,.025),
    (1.88,.04,.035),(1.97,.065,.035),(2.13,.055,.045),
    (2.36,.035,.025),(2.55,.065,.055)]):
    trim.include('horizontal_%d'%k,
        box((10,d,h),center=(0,WALL_Y-d/2,z),color=cream))
for p,(xa,xb) in enumerate([(-3.2,-1.65),(-1.58,1.90),(2.0,3.4)]):
    for layer,(inset,depth,width) in enumerate([
        (0,.028,.026),(.045,.018,.014)]):
        left,right=xa+inset,xb-inset
        bottom,top=.40+inset,1.81-inset
        for n,x in enumerate([left,right]):
            trim.include('panel_%d_%d_side_%d'%(p,layer,n),
                box((width,depth,top-bottom),
                    center=(x,WALL_Y-.025,(top+bottom)/2),color=cream))
        for n,z in enumerate([bottom,top]):
            trim.include('panel_%d_%d_cross_%d'%(p,layer,n),
                box((right-left,depth,width),
                    center=((left+right)/2,WALL_Y-.025,z),color=cream))
for k,x in enumerate([-1.15,.27,2.25]):
    trim.include('joint_%d'%k,box((.006,.008,3.2),
        center=(x,WALL_Y-.007,1.6),color=(.36,.32,.26)))
# Two small dark fittings visible high on the wall.
for k,x in enumerate([-1.02,-.94]):
    fitting=ball(.018,center=(x,WALL_Y-.04,2.01),color=(.075,.065,.045))
    fitting.resize((.6,.5,1.6))
    trim.include('wall_fitting_%d'%k,fitting)
scene.include('wall_details',trim)

pier=Asset('Right projecting pier')
pier.include('body',box((.42,.42,3.1),center=(2.30,.89,1.55),
                        color=(.69,.69,.61)))
for k,x in enumerate([2.15,2.44]):
    pier.include('vertical_trim_%d'%k,box((.018,.022,2.3),
        center=(x,.665,1.5),color=cream))
scene.include('pier',pier)

chaise=Asset('Antique chaise longue')
chaise.include('seat',fillet_box((SEAT_LENGTH,SEAT_WIDTH,.25),
    radius=.12,center=(.04,0,SEAT_HEIGHT),color=fabric))
chaise.include('seat_underframe',fillet_box((2.64,1.0,.115),
    radius=.052,center=(.025,0,.574),color=paint))

for iy,y in enumerate([-.497,.497]):
    chaise.include('long_gilt_edge_%d'%iy,sweep_tube(
        points=[(-1.24,y,.624),(-.90,y,.613),(.2,y,.61),
                (1.15,y,.60),(1.32,y*.91,.585)],
        radius=.012,color=gold))
    chaise.include('lower_apron_%d'%iy,sweep_tube(
        points=[(-1.22,y,.54),(-.95,y,.50),(-.42,y,.51),
                (.1,y,.478),(.65,y,.49),(1.20,y,.51),(1.31,y*.91,.54)],
        radius=.029,color=paint))
    chaise.include('apron_fine_line_%d'%iy,sweep_tube(
        points=[(-1.22,y-.006,.54),(-.85,y-.006,.523),
                (-.15,y-.006,.52),(.12,y-.006,.493),
                (.65,y-.006,.514),(1.24,y-.006,.54)],
        radius=.008,color=gold))

for ix,x in enumerate([-1.08,1.17]):
    for iy,y in enumerate([-.39,.39]):
        sign=-1 if x<0 else 1
        pts=[(x,y,.58),(x+.035*sign,y,.49),
             (x-.04*sign,y,.34),(x-.055*sign,y,.18),
             (x+.015*sign,y-.016,.075)]
        chaise.include('leg_%d_%d'%(ix,iy),
            sweep_tube(points=pts,radius=.035,color=paint))
        chaise.include('leg_gilding_%d_%d'%(ix,iy),
            sweep_tube(points=[(a,b-.031,c) for a,b,c in pts],
                       radius=.007,color=gold))
        chaise.include('foot_%d_%d'%(ix,iy),
            fillet_box((.095,.075,.045),radius=.019,
                center=(pts[-1][0],pts[-1][1],.057),color=paint))

head_outline=[
    (-1.12,-.48,.65),(-1.30,-.49,.84),(-1.41,-.48,1.20),
    (-1.48,-.43,1.55),(-1.44,-.32,1.69),(-1.43,-.12,1.72),
    (-1.43,.13,1.67),(-1.40,.38,1.56),(-1.31,.49,1.35),
    (-1.19,.49,.77),(-1.12,-.48,.65)]
near_profile=[
    (-1.40,-.475,1.39),(-1.27,-.50,1.20),(-1.10,-.51,1.08),
    (-.85,-.51,1.00),(-.70,-.50,1.03),(-.68,-.49,.88),
    (-.58,-.485,.69),(-.69,-.49,.60),(-1.12,-.49,.61),
    (-1.28,-.49,.73),(-1.40,-.475,1.39)]
far_profile=[
    (-1.42,.475,1.54),(-1.20,.49,1.38),(-.96,.49,1.27),
    (-.68,.49,1.23),(-.57,.49,1.26),(-.57,.49,1.13),
    (-.43,.48,.85),(-.35,.47,.76)]
chaise.include('head_frame',sweep_tube(points=head_outline,radius=.037,color=paint))
chaise.include('head_gilt_rim',sweep_tube(
    points=[(x+.025,y,z+.008) for x,y,z in head_outline],
    radius=.010,color=gold))
chaise.include('near_arm_frame',sweep_tube(
    points=near_profile,radius=.029,color=paint))
chaise.include('near_arm_gilt',sweep_tube(
    points=[(x,y-.022,z+.009) for x,y,z in near_profile],
    radius=.009,color=gold))
chaise.include('far_arm_frame',sweep_tube(
    points=far_profile,radius=.030,color=paint))
chaise.include('far_arm_gilt',sweep_tube(
    points=[(x,y-.016,z+.015) for x,y,z in far_profile],
    radius=.009,color=gold))

for group,center,scale in [
    ('apron',(.16,-.526,.51),.12),
    ('crest',(-1.445,-.22,1.70),.085)]:
    cx,cy,cz=center
    for k in range(7):
        a=k*math.pi*2/7
        ornament=ball(scale*.28,
            center=(cx+math.cos(a)*scale*.62,cy,
                    cz+math.sin(a)*scale*.37),color=gold)
        ornament.resize((1,.36,.75))
        chaise.include(group+'_petal_%d'%k,ornament)
    chaise.include(group+'_center',ball(scale*.23,center=center,color=cream))
for k,x in enumerate([-.86,-.44,.68,1.05]):
    chaise.include('apron_leaf_%d'%k,sweep_tube(
        points=[(x-.055,-.526,.535),(x,-.534,.51),(x+.045,-.525,.535)],
        radius=.009,color=gold))
scene.include('chaise',chaise)

pillow=Asset('Loose ivory pillow')
pillow.include('cushion',fillet_box((.32,.75,.76),radius=.115,
    center=(-1.035,-.035,1.245),color=(.83,.76,.62)))
pillow.turn('y',-18,pivot=(-1.035,-.035,1.245))
pillow.turn('x',-12,pivot=(-1.035,-.035,1.245))
scene.include('pillow',pillow)

label=Asset('Green information card')
label.include('card',box((.095,.17,.006),
    center=(.89,.095,.864),color=(.035,.14,.105)))
for k in range(3):
    label.include('printed_line_%d'%k,box((.045,.004,.001),
        center=(.89,.12-k*.015,.868),color=(.67,.72,.60)))
scene.include('label',label)

chair=Asset('Foreground cane chair')
CHAIR_CENTER=(-1.55,-1.52,.49)
chair.include('seat_rim',fillet_box((.69,.69,.10),radius=.045,
    center=CHAIR_CENTER,color=paint))
chair.include('cane_seat',fillet_box((.57,.57,.025),radius=.012,
    center=(-1.55,-1.52,.55),color=(.28,.17,.085)))
for k in range(27):
    v=-.265+k*.020
    chair.include('cane_x_%d'%k,rod(.003,
        start=(-1.815,-1.52+v,.568),end=(-1.285,-1.52+v,.568),
        color=(.52,.36,.20)))
    chair.include('cane_y_%d'%k,rod(.003,
        start=(-1.55+v,-1.785,.568),end=(-1.55+v,-1.255,.568),
        color=(.52,.36,.20)))
chair.turn('z',-13,pivot=CHAIR_CENTER)
scene.include('foreground_chair',chair)

curtains=Asset('Window curtains')
for k in range(14):
    curtains.include('fold_%d'%k,rod(.036,
        start=(-2.13+k*.030,.43,.03),
        end=(-2.22+k*.030,.50,3.2),
        color=(.77+.012*(k%3),.73+.012*(k%3),.63+.012*(k%3))))
scene.include('curtains',curtains)

# API audit: positive sizes; fillet radii never exceed half the thinnest
# dimension; sweep neighbors differ; all sibling include keys are unique.
realize(scene)

def descendants(obj):
    if obj is None:
        return []
    result=[]
    for child in obj.children:
        if child.type=='MESH':
            result.append(child)
        result.extend(descendants(child))
    return result

def assign_group(name,material):
    for ob in descendants(bpy.data.objects.get(name)):
        ob.data.materials.clear()
        ob.data.materials.append(material)

def textile(name,patterned=False):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    n=mat.node_tree.nodes
    l=mat.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(.76,.68,.55,1)
    bs.inputs['Roughness'].default_value=.86
    geo=n.new('ShaderNodeNewGeometry')
    noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=240
    noise.inputs['Detail'].default_value=2
    l.new(geo.outputs['Position'],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.16
    bump.inputs['Distance'].default_value=.002
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if patterned:
        wy=n.new('ShaderNodeTexWave')
        wy.wave_type='BANDS'
        wy.bands_direction='Y'
        wy.inputs['Scale'].default_value=10
        l.new(geo.outputs['Position'],wy.inputs['Vector'])
        wx=n.new('ShaderNodeTexWave')
        wx.wave_type='BANDS'
        wx.bands_direction='X'
        wx.inputs['Scale'].default_value=13
        l.new(geo.outputs['Position'],wx.inputs['Vector'])
        ty=n.new('ShaderNodeMath')
        ty.operation='GREATER_THAN'
        ty.inputs[1].default_value=.94
        l.new(wy.outputs['Fac'],ty.inputs[0])
        tx=n.new('ShaderNodeMath')
        tx.operation='GREATER_THAN'
        tx.inputs[1].default_value=.78
        l.new(wx.outputs['Fac'],tx.inputs[0])
        mul=n.new('ShaderNodeMath')
        mul.operation='MULTIPLY'
        l.new(tx.outputs[0],mul.inputs[0])
        l.new(ty.outputs[0],mul.inputs[1])
        mix=n.new('ShaderNodeMixRGB')
        mix.inputs[1].default_value=(.78,.71,.61,1)
        mix.inputs[2].default_value=(.43,.20,.19,1)
        l.new(mul.outputs[0],mix.inputs[0])
        l.new(mix.outputs[0],bs.inputs['Base Color'])
    return mat

striped=textile('Ivory linen with repeated rose dashes',True)
plain=textile('Ivory pillow weave')
assign_group('seat',striped)
assign_group('pillow',plain)

def panel(name,coords,material):
    mesh=bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(coords,[],[list(range(len(coords)))])
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.parent=bpy.data.objects.get('chaise')
    ob.data.materials.append(material)
    solid=ob.modifiers.new('Upholstery thickness','SOLIDIFY')
    solid.thickness=.035
    bevel=ob.modifiers.new('Soft panel edges','BEVEL')
    bevel.width=.025
    bevel.segments=3
    return ob

panel('Near upholstered arm',near_profile[:-1],striped)
panel('Upholstered head end',[
    (-1.13,-.445,.72),(-1.30,-.445,1.02),(-1.43,-.40,1.53),
    (-1.40,-.30,1.64),(-1.40,-.10,1.67),(-1.40,.13,1.62),
    (-1.36,.36,1.51),(-1.28,.445,1.30),(-1.15,.445,.75)],striped)
panel('Far upholstered arm',
      far_profile+[(-.45,.48,.72),(-1.19,.47,.72)],striped)

for ob in descendants(bpy.data.objects.get('pillow')):
    for face in ob.data.polygons:
        face.use_smooth=True

# Shared wood finishes keep fine detail economical.
wood_palette=[]
for k in range(12):
    mat=bpy.data.materials.new('Walnut finish %02d'%k)
    mat.use_nodes=True
    n=mat.node_tree.nodes
    l=mat.node_tree.links
    bs=n.get('Principled BSDF')
    shade=.77+k*.035
    bs.inputs['Base Color'].default_value=(.135*shade,.064*shade,.036*shade,1)
    bs.inputs['Roughness'].default_value=.32
    tc=n.new('ShaderNodeTexCoord')
    vec=n.new('ShaderNodeVectorMath')
    vec.operation='MULTIPLY'
    vec.inputs[1].default_value=(3,85,7)
    l.new(tc.outputs['Generated'],vec.inputs[0])
    noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=3
    l.new(vec.outputs[0],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.08
    bump.inputs['Distance'].default_value=.004
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs[0],bs.inputs['Normal'])
    wood_palette.append(mat)
for ob in descendants(bpy.data.objects.get('parquet')):
    ob.data.materials.clear()
    ob.data.materials.append(random.choice(wood_palette))

# World is initialized only after realize; assignments target named groups.
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.72,.75,.78,1)
bg.inputs['Strength'].default_value=.20

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
sc.camera.rotation_euler.rotate_axis('Z',math.radians(CAMERA_ROLL))
area_emitter((-3.8,-.4,3.0),power=WINDOW_POWER,size=2.8,
    target=(0,0,.6),color=(1,.93,.83))
area_emitter((1,-3,3.8),power=65,size=4,
    target=(0,0,.7),color=(.83,.88,1))

sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.25
sc.render.image_settings.file_format='PNG'
