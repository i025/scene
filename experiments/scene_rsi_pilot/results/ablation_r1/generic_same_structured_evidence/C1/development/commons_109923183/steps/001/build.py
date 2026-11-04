import bpy, math, random
from sceneact import *

random.seed(12)

# Estimated image anchors: crest (.065,.245), pillow (.19,.39),
# seat foot (.82,.66), front feet (.33,.84), (.78,.91).
# Camera looks down from the open front-right of a long chaise.
CHAISE_LENGTH = 2.65
SEAT_HEIGHT = .70
WALL_Y = 1.02
CAMERA_POSITION = (3.15, -5.7, 3.35)
CAMERA_TARGET = (0.0, .12, .94)
CAMERA_LENS = 48
WINDOW_POWER = 680

scene = Scene('French sitting room')
cream = (.70,.665,.56)
paint = (.40,.46,.40)
gold = (.64,.56,.39)
fabric = (.80,.75,.65)

room = Asset('Paneled architecture')
room.include('floor_base', box((18,14,.12), center=(0,0,-.08), color=(.19,.105,.065)))
room.include('back_wall', box((11,.18,4), center=(0,WALL_Y+.09,2), color=cream))
scene.include('architecture', room)

# Real parquet boards, in a repeating herringbone arrangement.
floor = Asset('Walnut parquet')
L,W = .63,.14
idx = 0
for i in range(-9,10):
    for j in range(-23,24):
        ox,oy = i*L-j*W, i*L+j*W
        for cx,cy,sx,sy in [(ox+L/2,oy+W/2,L,W),
                              (ox+L+W/2,oy+L/2,W,L)]:
            if abs(cx)>5.5 or abs(cy)>5.0:
                continue
            shade = random.uniform(.78,1.16)
            board = box((sx-.006,sy-.006,.025), center=(cx,cy,-.006),
                        color=(.235*shade,.132*shade,.079*shade))
            floor.include('board_%04d'%idx,board)
            idx += 1
scene.include('parquet',floor)

trim = Asset('Wall molding')
for k,(z,depth,height) in enumerate([
    (.10,.075,.15),(.22,.055,.035),(.30,.032,.025),
    (1.88,.04,.035),(1.97,.065,.035),(2.13,.055,.045),
    (2.36,.035,.025),(2.55,.065,.055)]):
    trim.include('horizontal_%d'%k,
                 box((10,depth,height),center=(0,WALL_Y-depth/2,z),color=cream))
for p,(xa,xb) in enumerate([(-3.2,-1.65),(-1.58,1.90),(2.0,3.4)]):
    for layer,(inset,depth,width) in enumerate([(0,.028,.026),(.045,.018,.014)]):
        left,right=xa+inset,xb-inset
        bottom,top=.40+inset,1.81-inset
        for n,x in enumerate([left,right]):
            trim.include('panel_%d_%d_side_%d'%(p,layer,n),
                         box((width,depth,top-bottom),center=(x,WALL_Y-.025,bottom+(top-bottom)/2),color=cream))
        for n,z in enumerate([bottom,top]):
            trim.include('panel_%d_%d_cross_%d'%(p,layer,n),
                         box((right-left,depth,width),center=((left+right)/2,WALL_Y-.025,z),color=cream))
# Narrow joints between historic wall sections.
for k,x in enumerate([-1.15, .27, 2.25]):
    trim.include('panel_joint_%d'%k,box((.008,.008,2.8),center=(x,WALL_Y-.007,1.4),color=(.37,.34,.28)))
scene.include('wall_details',trim)

# A shallow projecting pale pier at the far right.
pier=Asset('Right projecting pier')
pier.include('body',box((.42,.42,3.1),center=(2.65,.89,1.55),color=(.73,.73,.65)))
for k,x in enumerate([2.50,2.79]):
    pier.include('vertical_trim_%d'%k,box((.018,.022,2.3),center=(x,.665,1.5),color=cream))
scene.include('pier',pier)

chaise=Asset('Antique chaise longue')
# Main seat and its carved apron.
chaise.include('seat',fillet_box((2.65,.94,.25),radius=.12,
                               center=(.04,0,.735),color=fabric))
chaise.include('seat_underframe',fillet_box((2.64,.96,.115),radius=.052,
                               center=(.025,0,.574),color=paint))
for y in [-.477,.477]:
    chaise.include('long_gilt_edge_'+str(y),
        sweep_tube(points=[(-1.24,y,.624),(-.90,y,.613),(.2,y,.61),
                           (1.15,y,.60),(1.32,y*.91,.585)],radius=.013,color=gold))
    chaise.include('lower_apron_'+str(y),
        sweep_tube(points=[(-1.22,y,.54),(-.95,y,.50),(-.42,y,.51),
                           (.1,y,.478),(.65,y,.49),(1.20,y,.51),(1.31,y*.91,.54)],
                   radius=.026,color=paint))
    chaise.include('apron_fine_line_'+str(y),
        sweep_tube(points=[(-1.22,y-.006,.54),(-.85,y-.006,.523),
                           (-.15,y-.006,.52),(.12,y-.006,.493),
                           (.65,y-.006,.514),(1.24,y-.006,.54)],
                   radius=.009,color=gold))

# Four slender cabriole legs, with curved knees and turned-out feet.
for ix,x in enumerate([-1.08,1.17]):
    for iy,y in enumerate([-.37,.37]):
        sign=-1 if x<0 else 1
        pts=[(x,y,.58),(x+.035*sign,y,.49),
             (x-.04*sign,y,.34),(x-.055*sign,y,.18),
             (x+.015*sign,y-.016,.075)]
        chaise.include('leg_%d_%d'%(ix,iy),sweep_tube(points=pts,radius=.035,color=paint))
        chaise.include('leg_gilding_%d_%d'%(ix,iy),
            sweep_tube(points=[(a,b-.031,c) for a,b,c in pts],radius=.008,color=gold))
        chaise.include('foot_%d_%d'%(ix,iy),
            fillet_box((.095,.075,.045),radius=.019,center=(pts[-1][0],pts[-1][1],.057),color=paint))

# Tall upholstered head end; its sculptural rim is built from editable sweeps.
# The back leans away from the foot and has an arched crown.
head_outline=[
    (-1.12,-.46,.65),(-1.30,-.47,.84),(-1.41,-.46,1.20),
    (-1.48,-.41,1.55),(-1.44,-.30,1.69),(-1.43,-.12,1.72),
    (-1.43,.13,1.67),(-1.40,.36,1.56),(-1.31,.47,1.35),
    (-1.19,.47,.77),(-1.12,-.46,.65)]
chaise.include('head_frame',sweep_tube(points=head_outline,radius=.037,color=paint))
chaise.include('head_gilt_rim',sweep_tube(points=[(x+.025,y,z+.008) for x,y,z in head_outline],
                                       radius=.011,color=gold))

# The near upholstered side rises steeply at the head and drops to the seat.
near_profile=[
    (-1.40,-.455,1.39),(-1.27,-.48,1.20),(-1.10,-.49,1.08),
    (-.85,-.49,1.00),(-.70,-.48,1.03),(-.68,-.47,.88),
    (-.58,-.465,.69),(-.69,-.47,.60),(-1.12,-.47,.61),
    (-1.28,-.47,.73),(-1.40,-.455,1.39)]
far_profile=[
    (-1.42,.455,1.54),(-1.20,.47,1.38),(-.96,.47,1.27),
    (-.68,.47,1.23),(-.57,.47,1.26),(-.57,.47,1.13),
    (-.43,.46,.85),(-.35,.45,.76)]
chaise.include('near_arm_frame',sweep_tube(points=near_profile,radius=.028,color=paint))
chaise.include('near_arm_gilt',sweep_tube(points=[(x,y-.022,z+.009) for x,y,z in near_profile],
                                       radius=.009,color=gold))
chaise.include('far_arm_frame',sweep_tube(points=far_profile,radius=.030,color=paint))
chaise.include('far_arm_gilt',sweep_tube(points=[(x,y-.016,z+.015) for x,y,z in far_profile],
                                      radius=.009,color=gold))

# Economical carved ornaments, concentrated on the visible apron and crest.
for group,center,scale in [('apron',(.16,-.506,.51),.11),
                            ('crest',(-1.445,-.22,1.70),.085)]:
    cx,cy,cz=center
    for k in range(5):
        a=k*math.pi*2/5
        ornament=ball(scale*.28,center=(cx+math.cos(a)*scale*.57,cy,
                                       cz+math.sin(a)*scale*.36),color=gold)
        ornament.resize((1,.36,.75))
        chaise.include(group+'_petal_%d'%k,ornament)
    chaise.include(group+'_center',ball(scale*.23,center=center,color=cream))
for k,x in enumerate([-.86,-.44,.68,1.05]):
    chaise.include('apron_leaf_%d'%k,
        sweep_tube(points=[(x-.055,-.506,.535),(x,-.514,.51),(x+.045,-.505,.535)],
                   radius=.009,color=gold))
scene.include('chaise',chaise)

pillow=Asset('Loose ivory pillow')
pillow.include('cushion',fillet_box((.31,.66,.67),radius=.145,
                                 center=(-1.075,-.015,1.205),color=(.84,.79,.67)))
pillow.turn('y',-16,pivot=(-1.075,-.015,1.205))
pillow.turn('x',-7,pivot=(-1.075,-.015,1.205))
scene.include('pillow',pillow)

# Small green museum label resting on the seat.
label=Asset('Green information card')
label.include('card',box((.095,.17,.006),center=(.89,.095,.868),color=(.055,.19,.145)))
for k in range(3):
    label.include('printed_line_%d'%k,box((.045,.004,.001),center=(.89,.12-k*.015,.872),color=(.70,.76,.63)))
scene.include('label',label)

# A cropped cane chair intrudes at the bottom left.
chair=Asset('Foreground cane chair')
chair.include('seat_rim',fillet_box((.69,.69,.10),radius=.045,
                                  center=(-1.87,-1.50,.49),color=paint))
chair.include('cane_seat',fillet_box((.57,.57,.025),radius=.012,
                                   center=(-1.87,-1.50,.55),color=(.49,.35,.21)))
for k in range(27):
    v=-.265+k*.020
    chair.include('cane_x_%d'%k,rod(.003,start=(-2.135,-1.50+v,.568),end=(-1.605,-1.50+v,.568),color=(.68,.53,.32)))
    chair.include('cane_y_%d'%k,rod(.003,start=(-1.87+v,-1.765,.568),end=(-1.87+v,-1.235,.568),color=(.68,.53,.32)))
chair.turn('z',-13,pivot=(-1.87,-1.50,.5))
scene.include('foreground_chair',chair)

curtains=Asset('Window curtains')
for k in range(10):
    curtains.include('fold_%d'%k,
        rod(.032,start=(-1.99+k*.032,.61,.03),
            end=(-2.08+k*.032,.68,3.0),
            color=(.77+.012*(k%3),.73+.012*(k%3),.62+.012*(k%3))))
scene.include('curtains',curtains)

# All fillets are <= half the smallest dimension; all sweep points differ.
# Sibling keys are unique. Materials below are explicitly copied/assigned.
realize(scene)

def group_object(name):
    return bpy.data.objects.get(name)

def descendants(obj):
    if obj is None:
        return []
    out=[]
    for child in obj.children:
        if child.type=='MESH':
            out.append(child)
        out.extend(descendants(child))
    return out

def fabric_material(name, patterned=True):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    nd=mat.node_tree.nodes
    lk=mat.node_tree.links
    bs=nd.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.87
    coord=nd.new('ShaderNodeTexCoord')
    sep=nd.new('ShaderNodeSeparateXYZ')
    lk.new(coord.outputs['Object'],sep.inputs[0])
    noise=nd.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=180
    noise.inputs['Roughness'].default_value=.8
    lk.new(coord.outputs['Object'],noise.inputs['Vector'])
    bump=nd.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.20
    bump.inputs['Distance'].default_value=.008
    lk.new(noise.outputs['Fac'],bump.inputs['Height'])
    lk.new(bump.outputs[0],bs.inputs['Normal'])
    if patterned:
        wave=nd.new('ShaderNodeTexWave')
        wave.wave_type='BANDS'
        wave.bands_direction='Y'
        wave.inputs['Scale'].default_value=19
        wave.inputs['Distortion'].default_value=.12
        lk.new(coord.outputs['Object'],wave.inputs['Vector'])
        ramp=nd.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.80
        ramp.color_ramp.elements[0].color=(.75,.685,.57,1)
        ramp.color_ramp.elements[1].position=.88
        ramp.color_ramp.elements[1].color=(.48,.29,.27,1)
        extra=ramp.color_ramp.elements.new(.96)
        extra.color=(.79,.73,.62,1)
        lk.new(wave.outputs['Color'],ramp.inputs[0])
        lk.new(ramp.outputs[0],bs.inputs['Base Color'])
    else:
        bs.inputs['Base Color'].default_value=(.80,.74,.60,1)
    return mat

striped=fabric_material('Ivory woven upholstery with rose pinstripes')
plain=fabric_material('Soft ivory pillow weave',False)
for obj in descendants(group_object('pillow')):
    obj.data.materials.clear()
    obj.data.materials.append(plain)

# Editable upholstered panels, attached to their meaningful chaise parent.
def panel(name,coords,material):
    mesh=bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(coords,[],[list(range(len(coords)))])
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.parent=group_object('chaise')
    ob.data.materials.append(material)
    solid=ob.modifiers.new('Upholstery thickness','SOLIDIFY')
    solid.thickness=.035
    bevel=ob.modifiers.new('Soft panel edges','BEVEL')
    bevel.width=.025
    bevel.segments=3
    return ob

panel('Near upholstered arm',near_profile[:-1],striped)
panel('Upholstered head end',[
    (-1.13,-.425,.72),(-1.30,-.425,1.02),(-1.43,-.38,1.53),
    (-1.40,-.28,1.64),(-1.40,-.10,1.67),(-1.40,.13,1.62),
    (-1.36,.34,1.51),(-1.28,.425,1.30),(-1.15,.425,.75)],striped)
panel('Far upholstered arm',far_profile+[
    (-.45,.46,.72),(-1.19,.45,.72)],striped)

seat_group=group_object('seat')
for ob in descendants(seat_group):
    ob.data.materials.clear()
    ob.data.materials.append(striped)

# A quiet irregular woven pillow surface without adding decorative geometry.
for ob in descendants(group_object('pillow')):
    for poly in ob.data.polygons:
        poly.use_smooth=True

# Slight grain and soft sheen on the individual parquet meshes.
woodmat=bpy.data.materials.new('Walnut grain')
woodmat.use_nodes=True
nodes=woodmat.node_tree.nodes
links=woodmat.node_tree.links
bs=nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.38
tc=nodes.new('ShaderNodeTexCoord')
mapping=nodes.new('ShaderNodeVectorMath')
mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(3,85,7)
links.new(tc.outputs['Generated'],mapping.inputs[0])
noise=nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=3
links.new(mapping.outputs[0],noise.inputs['Vector'])
bump=nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.13
bump.inputs['Distance'].default_value=.012
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs[0],bs.inputs['Normal'])
for ob in descendants(group_object('parquet')):
    old=ob.data.materials[0]
    mat=woodmat.copy()
    mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=old.diffuse_color
    ob.data.materials.clear()
    ob.data.materials.append(mat)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value=(.72,.75,.78,1)
background.inputs['Strength'].default_value=.26

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-3.8,-.4,3.0),power=WINDOW_POWER,size=2.8,
             target=(0,0,.6),color=(1.0,.93,.81))
area_emitter((1.0,-3.0,3.8),power=100,size=4,
             target=(0,0,.7),color=(.83,.88,1.0))

sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
