# Reference inventory and anchors, estimated in normalized image coordinates:
# - Reddish brown floor occupies the lower half, receding to about y=.66.
# - Cream back wall and ceiling: back wall around y=.30-.68; exposed ceiling
#   and red-brown beams occupy the upper .23 of the image.
# - Left black metal bunk, x=.02-.40, y=.35-.70: two pale mattresses,
#   narrow horizontal rails and dark upright posts; partly hidden by foreground.
# - Gray lockers at the rear, x=.40-.64, y=.39-.62, behind the bunk frame.
# - Center dark worktable and pale chair, x=.43-.70, y=.51-.69.
# - Cream support column with reddish lower section, x=.68-.79, y=.00-.85,
#   overlaps the rear wall and worktable.
# - Left foreground dark slatted equipment and long dark green bench, x=0-.38,
#   y=.47-.90; right foreground green bench, x=.80-1, y=.75-1.
# - Wall heater upper left, x=0-.20, y=.22-.37; dark wall panel and red
#   extinguisher housing at right, x=.77-.91, y=.34-.61.
# - Three white hanging lamps recede from x=.39,y=.16 toward the rear.
# Dominant edges: vertical posts are nearly vertical; floor and bench edges
# converge toward the rear center; ceiling pipes run mostly left-to-right.
# Occluded rear contents and the exact depth of the bunk are uncertain.
# Approximate expanded primitive count: architecture 20, bunk 24, mattresses 6,
# lockers 35, furniture and benches 25, heater and wall details 18,
# ceiling beams/pipes/lights 35: approximately 163 meshes.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene('Utility bunk room')

cream = (0.68, 0.67, 0.58)
wall_light = (0.76, 0.75, 0.67)
ceiling = (0.48, 0.40, 0.31)
floor_col = (0.30, 0.105, 0.067)
brown = (0.27, 0.105, 0.065)
dark = (0.055, 0.067, 0.057)
black = (0.028, 0.035, 0.029)
metal = (0.38, 0.41, 0.38)
pale = (0.67, 0.68, 0.62)
green = (0.035, 0.105, 0.075)
red = (0.75, 0.12, 0.09)

def add(asset, name, node):
    asset.include(name, node)

# Room envelope, with the front and right side open to the camera.
room = Asset('Architecture')
add(room, 'floor', box((5.8, 10.0, .12), center=(0, 1.1, -.06), color=floor_col))
add(room, 'rear_wall', box((5.8, .14, 3.35), center=(0, 5.0, 1.675), color=cream))
add(room, 'left_wall', box((.14, 10, 3.35), center=(-2.9, 1.1, 1.675), color=cream))
add(room, 'right_wall_back', box((.14, 4.2, 3.35), center=(2.9, 2.9, 1.675), color=wall_light))
add(room, 'ceiling', box((5.8, 10, .12), center=(0, 1.1, 3.36), color=ceiling))
add(room, 'rear_baseboard', box((5.8, .06, .28), center=(0, 4.91, .14), color=brown))
add(room, 'left_baseboard', box((.06, 9.7, .27), center=(-2.81, 1.0, .135), color=brown))
# Near right wall creates the cropped vertical edge.
add(room, 'near_right_wall', box((.19, 1.3, 3.4), center=(2.87, -2.5, 1.7), color=wall_light))
scene.include('architecture', room)

# Pillar: pale upper shaft, dark red lower shaft and a small floor foot.
pillar = Asset('Front support column')
add(pillar, 'upper', rod(.145, start=(1.12, .25, 1.45), end=(1.12, .25, 3.33), color=(.77,.75,.65)))
add(pillar, 'lower', rod(.145, start=(1.12, .25, .05), end=(1.12, .25, 1.45), color=brown))
add(pillar, 'foot', rod(.20, start=(1.12,.25,.015), end=(1.12,.25,.07), color=(.36,.25,.19)))
scene.include('support_column', pillar)

# Bunk beds run in depth along the left wall.
bunk = Asset('Left bunk bed')
bx0, bx1 = -2.50, -.84
by0, by1 = .55, 4.12
for x in (bx0, bx1):
    for y in (by0, by1):
        add(bunk, 'post_%s_%s' % (x,y), rod(.035, start=(x,y,.05), end=(x,y,2.05), color=black))
for z in (.52, 1.23, 1.86):
    for x in (bx0,bx1):
        add(bunk, 'long_rail_%s_%s' % (z,x),
            rod(.026, start=(x,by0,z), end=(x,by1,z), color=dark))
    for y in (by0,by1):
        add(bunk, 'end_rail_%s_%s' % (z,y),
            rod(.025, start=(bx0,y,z), end=(bx1,y,z), color=dark))
for i,z in enumerate((.60,1.30)):
    add(bunk, 'mattress_%d'%i,
        box((1.52,3.24,.15), center=(-1.67,2.36,z), color=(.63,.65,.59)))
    add(bunk, 'pillow_%d'%i,
        box((1.18,.55,.12), center=(-1.67,3.68,z+.12), color=(.75,.76,.70)))
scene.include('bunk', bunk)

# Lockers on the far wall. Door seams, vents, and handles remain separate.
lockers = Asset('Rear gray lockers')
for i in range(4):
    x = -.90 + i*.42
    add(lockers, 'body_%d'%i, box((.40,.43,1.68), center=(x,4.65,1.15), color=metal))
    add(lockers, 'door_%d'%i, box((.36,.025,1.56), center=(x,4.425,1.17), color=(.47,.50,.46)))
    add(lockers, 'handle_%d'%i, box((.028,.035,.15), center=(x+.13,4.398,1.17), color=dark))
    for k in range(4):
        add(lockers, 'vent_%d_%d'%(i,k),
            box((.22,.016,.018), center=(x,4.394,1.61-k*.065), color=(.22,.25,.23)))
scene.include('lockers', lockers)

# Dark steel foreground cabinet with narrow louvers.
cabinet = Asset('Left foreground equipment')
add(cabinet, 'body', box((.86,1.82,1.28), center=(-2.43,-.15,.72), color=(.075,.10,.09)))
add(cabinet, 'top', box((.98,1.98,.08), center=(-2.43,-.15,1.39), color=dark))
for j in range(3):
    yy = -.75 + j*.57
    add(cabinet,'panel_%d'%j,box((.025,.48,.95),center=(-1.99,yy,.76),color=(.10,.14,.13)))
    for k in range(7):
        add(cabinet,'louver_%d_%d'%(j,k),
            box((.018,.39,.022),center=(-1.97,yy,.42+k*.10),color=(.21,.25,.22)))
scene.include('foreground_equipment',cabinet)

# Long benches, with narrow dark green tops and simple legs.
benches = Asset('Benches')
add(benches,'left_seat',box((.48,3.55,.075),center=(-1.94,-.70,.51),color=green))
for y in (-2.18,.65):
    for x in (-2.10,-1.77):
        add(benches,'left_leg_%s_%s'%(x,y),rod(.025,start=(x,y,.03),end=(x,y,.49),color=black))
add(benches,'right_seat',box((.57,2.65,.075),center=(2.42,-1.38,.49),color=green))
for y in (-2.44,-.36):
    for x in (2.20,2.62):
        add(benches,'right_leg_%s_%s'%(x,y),rod(.025,start=(x,y,.03),end=(x,y,.47),color=black))
scene.include('benches',benches)

# Worktable and chair are partly hidden behind the pillar.
furniture = Asset('Rear worktable and chair')
add(furniture,'table_top',box((1.18,.84,.10),center=(.42,3.38,.88),color=(.25,.27,.24)))
add(furniture,'table_body',box((.94,.68,.69),center=(.54,3.48,.47),color=(.22,.24,.21)))
for x in (-.08,.94):
    for y in (3.05,3.69):
        add(furniture,'table_leg_%s_%s'%(x,y),rod(.035,start=(x,y,.04),end=(x,y,.85),color=dark))
add(furniture,'chair_seat',box((.47,.43,.07),center=(-.52,3.09,.53),color=(.60,.60,.52)))
add(furniture,'chair_back',box((.47,.07,.43),center=(-.52,3.30,.81),color=(.55,.56,.49)))
for x in (-.72,-.32):
    for y in (2.92,3.27):
        add(furniture,'chair_leg_%s_%s'%(x,y),rod(.018,start=(x,y,.04),end=(x,y,.54),color=(.57,.58,.51)))
scene.include('worktable_and_chair',furniture)

# Wall heater and its dark horizontal grilles.
heater = Asset('Wall heater')
add(heater,'housing',box((.72,.40,.78),center=(-2.49,2.15,2.30),color=(.54,.55,.48)))
add(heater,'front',box((.59,.035,.55),center=(-2.49,1.935,2.28),color=(.28,.30,.27)))
for j in range(5):
    add(heater,'grill_%d'%j,box((.52,.035,.055),center=(-2.49,1.91,2.08+j*.10),color=(.12,.14,.12)))
scene.include('wall_heater',heater)

# Back wall panel and red fire equipment.
wall_items = Asset('Wall mounted equipment')
add(wall_items,'dark_panel',box((.85,.045,.85),center=(1.70,4.90,2.02),color=(.24,.27,.25)))
add(wall_items,'panel_frame_top',box((.90,.06,.035),center=(1.70,4.86,2.46),color=dark))
add(wall_items,'red_housing',box((.38,.16,.62),center=(1.60,4.79,1.02),color=red))
add(wall_items,'red_top',ball(.18,center=(1.60,4.78,1.33),color=red))
add(wall_items,'label',box((.13,.015,.22),center=(1.60,4.70,1.12),color=(.83,.80,.71)))
add(wall_items,'white_notice',box((.62,.03,.76),center=(2.53,4.90,1.70),color=(.76,.76,.68)))
scene.include('wall_equipment',wall_items)

# Exposed ceiling joists, cross beams and pipes.
overhead = Asset('Ceiling structure')
for y in (-2.0,.05,2.10,4.10):
    add(overhead,'crossbeam_%s'%y,box((5.8,.20,.24),center=(0,y,3.15),color=(.38,.21,.14)))
for x in (-2.55,-1.55,-.55,.45,1.45,2.45):
    add(overhead,'joist_%s'%x,box((.13,9.5,.18),center=(x,1.05,3.25),color=(.42,.25,.18)))
for z in (2.72,2.89):
    add(overhead,'rear_pipe_%s'%z,rod(.035,start=(-2.8,4.22,z),end=(2.8,4.22,z),color=dark))
add(overhead,'left_pipe',rod(.055,start=(-2.65,-2.6,2.93),end=(-2.65,4.5,2.93),color=(.59,.59,.52)))
add(overhead,'rear_vertical_pipe',rod(.055,start=(.92,4.73,1.55),end=(.92,4.73,3.10),color=(.63,.63,.56)))
scene.include('ceiling_structure',overhead)

lamps = Asset('Hanging lamps')
for i,(x,y,z,r) in enumerate(((-.72,.05,2.82,.27),(-.54,2.72,2.72,.17),(-.52,4.05,2.65,.12))):
    add(lamps,'cord_%d'%i,rod(.015,start=(x,y,3.25),end=(x,y,z+.12),color=dark))
    add(lamps,'shade_%d'%i,ball(r,center=(x,y,z),color=(.20,.23,.21)))
    add(lamps,'diffuser_%d'%i,rod(r*.88,start=(x,y,z-.07),end=(x,y,z-.035),color=(.95,.94,.81)))
scene.include('hanging_lamps',lamps)

realize(scene)

# Camera parameters are independent of room and asset dimensions.
CAMERA_POSITION = (0.0,-7.7,2.05)
CAMERA_TARGET = (0.0,2.1,1.55)
CAMERA_LENS = 31
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)

sc = bpy.context.scene
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get('Background')
if background is None:
    background = nodes.new('ShaderNodeBackground')
output = nodes.get('World Output')
if output is None:
    output = nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value = (.36,.35,.31,1)
background.inputs['Strength'].default_value = .65
area_emitter((-.7,-1.0,3.04),power=450,size=2.5,target=(0,1,0))
area_emitter((-.6,3.0,2.8),power=220,size=2,target=(0,3,0))
area_emitter((1.8,-3.5,2.8),power=150,size=3,target=(0,2,1))

# Small projection table: reference estimates and computed image coordinates.
# Landmarks are points on visible geometry; this check does not verify occlusion.
landmarks = [
    ('column_foot', (1.12,.25,.07), (.72,.84)),
    ('column_color_boundary', (1.12,.25,1.45), (.72,.47)),
    ('locker_upper_left', (-1.10,4.425,1.93), (.40,.39)),
    ('rear_panel_upper_left', (1.275,4.86,2.445), (.77,.34)),
    ('left_bunk_front_upper', (-.84,.55,1.86), (.38,.36)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
                                    scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
print('Landmark                    reference       projected')
for name,p,ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv = None if clip.w <= 1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v,3) for v in uv))
