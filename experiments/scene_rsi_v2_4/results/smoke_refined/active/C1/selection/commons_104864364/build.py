from sceneact import *
import bpy, math

# Reference inventory (normalized image coordinates):
# Cream classroom shell; yellow dado boundaries near (.00,.43), (1,.46).
# Tan square-tiled floor occupies the lower half, with clear foreground gaps.
# Rear dark stage (.37,.24)-(.67,.45), green side curtains, scalloped valance,
# green board (.48,.33)-(.58,.41), and narrow blue display to its right.
# Desks and separate benches span (.00,.42)-(.93,.89). Thin wooden legs,
# aprons, open under-table regions, papers, and bags remain separate parts.
# Foreground desk left (.14,.60)-(.36,.89), right (.51,.55)-(.70,.81).
# Windows, shutters, doors, speakers and small portraits line both walls.
# Six ceiling fans, with prominent foreground hubs around (.19,.05),(.73,.04).
# Bags: navy (.10,.72), blue (.67,.77), dark (.52,.69), cyan (.79,.66).
# Uncertain: rear furniture membership, stage depth, exact camera intrinsics.
#
# Revision rationale based on the full rendered image:
# Foreground furniture, bags, rear board and ceiling junctions project too low.
# A modest increase in downward camera pitch should move these upward together.
# Foreground desk horizontal centers are already useful anchors; retain them.
# The stage valance is additionally too low relative to the rear ceiling,
# and the stage opening is too narrow. Adjust that assembly locally.
# Board height and stage geometry remain ambiguous with camera calibration;
# these coupled changes are visual estimates, not controlled causal tests.
# The left foreground desktop is too wide; narrow it without shifting its center.
# Foreground fans are emitted but cropped, so move them deeper into the room.
# Wood and yellow paint are washed out; darken their material colors while
# retaining bright cream walls and luminous window regions.
# Expected: raised furniture/bag projections, visible fan hubs, taller dark stage,
# darker desktop silhouettes, and preservation of central aisle and side walls.
# Expanded primitive estimate: architecture/stage 39, openings/fittings 105,
# 21 desks x 10 parts = 210, bags/items 38, fans 30: approximately 422 meshes.
# All changes below remain unverified until the runner renders this revision.

scene = Scene('Classroom')
cream = (.84,.82,.68)
yellow = (.84,.56,.006)
topwood = (.075,.055,.031)
edge = (.125,.092,.047)
legwood = (.16,.12,.061)

def asset(name):
    a = Asset(name=name)
    scene.include(name,a)
    return a

def cube(a,name,size,center,color):
    n = box(size=size,center=center,color=color)
    a.include(name,n)
    return n

def ellipsoid(a,name,center,size,color):
    n = ball(radius=1,center=center,color=color)
    n.resize(size,pivot=center)
    a.include(name,n)
    return n

shell = asset('room_architecture')
cube(shell,'tiled_floor',(8.4,15.4,.12),(0,6.5,-.06),(.62,.49,.29))
cube(shell,'left_upper_wall',(.16,15,3.05),(-4.15,6.5,2.83),cream)
cube(shell,'right_upper_wall',(.16,15,3.05),(4.15,6.5,2.83),(.9,.88,.75))
cube(shell,'left_yellow_dado',(.18,15,1.3),(-4.14,6.5,.65),yellow)
cube(shell,'right_yellow_dado',(.18,15,1.3),(4.14,6.5,.65),yellow)
cube(shell,'rear_wall',(8.4,.15,4.35),(0,14,2.175),cream)
cube(shell,'ceiling',(8.4,15,.12),(0,6.5,4.4),(.92,.91,.83))
for i,y in enumerate([1.2,5.4,9.6]):
    cube(shell,'ceiling_cross_beam_'+str(i),(8.3,.19,.23),(0,y,4.23),(.9,.89,.81))
for i,x in enumerate([-2,2]):
    cube(shell,'ceiling_long_beam_'+str(i),(.18,14,.23),(x,6.8,4.24),(.94,.92,.84))

stage = asset('rear_stage')
sx = .35
cube(stage,'raised_platform',(5.8,1.2,.30),(sx,13.25,.15),(.24,.17,.075))
cube(stage,'dark_stage_recess',(5.8,.12,3.4),(sx,13.91,2.18),(.018,.016,.01))
cube(stage,'left_green_curtain',(.48,.18,3.4),(sx-2.7,13.65,2.18),(.035,.18,.035))
cube(stage,'right_green_curtain',(.43,.18,3.4),(sx+2.7,13.65,2.18),(.022,.18,.045))
cube(stage,'curtain_valance',(5.8,.23,.22),(sx,13.56,3.94),(.75,.72,.53))
for i in range(15):
    ellipsoid(stage,'valance_scallop_'+str(i),
              (sx-2.7+i*.385,13.51,3.78),(.22,.09,.17),(.83,.79,.61))
cube(stage,'board_frame',(2.28,.12,1.2),(sx+.10,13.13,2.20),(.27,.25,.16))
cube(stage,'green_chalkboard',(2.16,.045,1.08),(sx+.10,13.045,2.21),(.055,.17,.115))
cube(stage,'chalk_tray',(2.3,.17,.055),(sx+.1,12.97,1.65),(.35,.30,.17))
for i,x in enumerate([sx-.92,sx+1.12]):
    stage.include('board_support_'+str(i),
                  rod(radius=.025,start=(x,12.98,.3),end=(x,13.08,1.71),
                      color=(.15,.14,.09)))
cube(stage,'blue_display',(.48,.09,1.08),(sx+1.92,13.17,1.64),(.18,.56,.65))

for side in [-1,1]:
    for j,y in enumerate([1.5,4.8,8,11]):
        w = asset(('left' if side<0 else 'right')+'_window_'+str(j))
        x = side*4.035
        cube(w,'bright_opening',(.035,1.40,1.95),(x,y,2.35),(.97,.98,.9))
        for k,dy in enumerate([-.76,.76]):
            cube(w,'jamb_'+str(k),(.17,.105,2.15),
                 (x-side*.04,y+dy,2.35),(.18,.12,.055))
        cube(w,'lintel',(.17,1.63,.10),(x-side*.04,y,3.39),(.2,.14,.065))
        cube(w,'sill',(.23,1.65,.11),(x-side*.09,y,1.34),(.24,.16,.07))
        cube(w,'transom',(.12,1.43,.07),(x-side*.08,y,3.02),(.20,.14,.07))
        cube(w,'central_mullion',(.13,.055,1.65),(x-side*.09,y,2.18),(.26,.18,.08))
        shutter = cube(w,'wooden_open_shutter',(.10,.66,1.90),
                       (x-side*.22,y+.84,2.30),(.22,.135,.055))
        shutter.turn('z',side*24)
        for k in [-1,1]:
            cube(w,'shutter_rail_'+str(k),(.13,.56,.065),
                 (x-side*.24,y+.84,2.30+k*.64),(.31,.21,.10))

decor = asset('wall_fittings')
for j,y in enumerate([3.35,9.65]):
    cube(decor,'right_door_'+str(j),(.12,1.13,2.6),(4,y,1.3),(.23,.14,.065))
    for k in range(4):
        cube(decor,'door_vertical_'+str(j)+'_'+str(k),(.045,.035,2.35),
             (3.92,y-.44+k*.29,1.29),(.35,.23,.11))
    cube(decor,'door_header_'+str(j),(.2,1.3,.12),(3.96,y,2.66),(.20,.13,.065))
for side,y in [(-1,1),(-1,10.2),(1,6.2)]:
    speaker = cube(decor,'speaker_'+str(side)+'_'+str(y),(.28,.55,.72),
                   (side*3.89,y,3.12),(.012,.027,.025))
    speaker.turn('y',-side*10)
for side,ys in [(-1,[4,8.8]),(1,[2.1,5.1,8.4,11.8])]:
    for j,y in enumerate(ys):
        cube(decor,'portrait_frame_'+str(side)+'_'+str(j),(.06,.40,.65),
             (side*4.025,y,3.63),(.18,.20,.15))
        cube(decor,'portrait_paper_'+str(side)+'_'+str(j),(.065,.32,.55),
             (side*3.984,y,3.63),(.8,.82,.70))
        ellipsoid(decor,'portrait_mark_'+str(side)+'_'+str(j),
                  (side*3.94,y,3.65),(.018,.085,.16),(.22,.27,.24))

def desk(name,x,y,width=1.72,height=1.02):
    a = asset(name)
    cube(a,'desktop',(width,.66,.095),(x,y,height),topwood)
    cube(a,'front_apron',(width,.075,.19),(x,y-.265,height-.16),edge)
    for ix in [-1,1]:
        for iy in [-1,1]:
            cube(a,'leg_%s_%s'%(ix,iy),(.065,.065,height-.06),
                 (x+ix*(width/2-.09),y+iy*.235,(height-.06)/2),legwood)
    cube(a,'lower_stretcher',(width-.12,.055,.065),(x,y+.23,.23),edge)
    by = y-.70
    cube(a,'bench_seat',(width,.27,.075),(x,by,.57),(.105,.073,.035))
    for ix in [-1,1]:
        cube(a,'bench_support_'+str(ix),(.065,.25,.54),
             (x+ix*(width/2-.16),by,.27),legwood)
    return a

desk('foreground_left_desk',-1.72,2.30,1.60,1.12)
desk('foreground_right_desk',1.18,3.55,1.85)
desk('right_edge_desk',3.22,4.75,1.45)
desk('left_clipped_desk',-3.67,3.65,1.52)
for col,x,ys in [
    ('left',-2.12,[4.55,6.25,7.90,9.48,10.95]),
    ('center',.45,[5.65,7.20,8.67,10.10,11.45]),
    ('right',2.85,[6.65,8.35,10,11.55]),
    ('farleft',-3.45,[7.35,9.05,10.65])]:
    for j,y in enumerate(ys):
        desk(col+'_desk_'+str(j),x,y,1.54 if col=='farleft' else 1.65)

def bag(name,x,y,h,color,lean=0):
    a = asset(name)
    ellipsoid(a,'main_fabric',(x,y,h*.50),(.24,.15,h*.48),color)
    ellipsoid(a,'front_pocket',(x,y-.125,h*.34),
              (.195,.065,h*.22),tuple(c*.75 for c in color))
    ellipsoid(a,'top_handle',(x,y,h*.94),(.085,.035,.06),(.012,.028,.04))
    for s in [-1,1]:
        a.include('shoulder_strap_'+str(s),
                  rod(radius=.022,start=(x+s*.14,y+.12,h*.79),
                      end=(x+s*.25,y+.16,.08),color=(.012,.028,.04)))
    cube(a,'pocket_zipper',(.29,.015,.018),(x,y-.19,h*.47),(.15,.28,.3))
    if lean:
        a.turn('y',lean,pivot=(x,y,0))
bag('navy_bag_foreground',-2.61,1.58,.69,(.008,.022,.045),-10)
bag('blue_bag_foreground',1.42,2.30,.76,(.006,.16,.34),-6)
bag('dark_bag_middle',.15,4.02,.63,(.009,.018,.03),12)
bag('cyan_bag_right',2.95,4.12,.69,(.005,.23,.34),-13)
flatbag = asset('bag_under_left_table')
ellipsoid(flatbag,'flattened_black_bag',(-1.75,1.92,.12),
          (.42,.22,.12),(.012,.016,.015))

items = asset('desktop_items')
for i,(x,y) in enumerate([(-2.2,6.2),(-3.45,3.6),(.4,8.7),(2.8,8.35)]):
    cube(items,'book_'+str(i),(.32,.23,.035),(x,y,1.09),(.61,.59,.44))
    cube(items,'book_pages_'+str(i),(.29,.22,.02),(x,y-.01,1.115),(.85,.85,.77))
ellipsoid(items,'pink_cloth',(-2,6.1,1.13),(.20,.15,.055),(.60,.30,.50))
cube(items,'white_paper',(.38,.28,.008),(-3.48,3.6,1.08),(.91,.91,.83))

for j,(x,y) in enumerate([
    (-2.1,2.1),(1.65,2.2),(-2.1,6.1),(2.1,6.4),
    (-1.5,10.8),(1.85,11)]):
    fan = asset('ceiling_fan_'+str(j))
    fan.include('downrod',rod(radius=.022,start=(x,y,4.31),
                             end=(x,y,3.93),color=(.085,.07,.045)))
    ellipsoid(fan,'motor',(x,y,3.91),(.12,.12,.065),(.10,.075,.045))
    for k in range(3):
        ang = 20+k*120
        angle = math.radians(ang)
        blade = cube(fan,'blade_'+str(k),(.85,.14,.025),
                     (x+.47*math.cos(angle),y+.47*math.sin(angle),3.93),
                     (.12,.10,.075))
        blade.turn('z',ang)

realize(scene)

# Select the floor by its unique structural dimensions, not realization order.
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and ob.dimensions.x>8 and ob.dimensions.y>15 and ob.dimensions.z<.2:
        mat = bpy.data.materials.new('warm_ceramic_tile')
        mat.use_nodes = True
        nt = mat.node_tree
        bs = nt.nodes.get('Principled BSDF')
        tex = nt.nodes.new('ShaderNodeTexBrick')
        tex.inputs['Color1'].default_value = (.48,.34,.17,1)
        tex.inputs['Color2'].default_value = (.74,.61,.39,1)
        tex.inputs['Mortar'].default_value = (.44,.38,.27,1)
        tex.inputs['Scale'].default_value = 1
        tex.inputs['Mortar Size'].default_value = .006
        tex.inputs['Brick Width'].default_value = .43
        tex.inputs['Row Height'].default_value = .43
        tex.offset = 0
        coord = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value = .48
        ob.data.materials.clear()
        ob.data.materials.append(mat)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value = (.80,.84,.77,1)
background.inputs['Strength'].default_value = .45

# Camera position and focal length retained; pitch is changed independently.
set_view(position=(.05,-2.45,2.45),target=(0,10.8,.55),lens=23.8,sensor=36)
area_emitter(position=(0,5.5,4.08),power=650,size=7,target=(0,6,0))
area_emitter(position=(-3.6,3.7,3),power=550,size=4,
             target=(0,5,1),color=(1,.97,.88))
area_emitter(position=(3.6,8.2,3.2),power=450,size=4,
             target=(0,7,1),color=(1,.99,.92))
sc.render.resolution_x = 512
sc.render.resolution_y = 340
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'Medium High Contrast'
sc.view_settings.exposure = 0
sc.view_settings.gamma = 1
# No render or save: managed by the external runner.
