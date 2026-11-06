from sceneact import *
import bpy, math

# Reference inventory, normalized image bounds:
# Cream classroom shell with yellow lower walls; tiled tan floor (0,.49)-(1,1).
# Dark rear stage and green curtains (.37,.24)-(.67,.45), central green board.
# Wooden desks/benches occupy (.00,.42)-(.93,.89), with open gaps and thin legs.
# Foreground left desk (.13,.59)-(.37,.89); right desk (.51,.55)-(.70,.81).
# Side windows and wooden shutters, left (.02,.13)-(.33,.53), right (.69,.10)-(1,.61).
# Ceiling beams and dark fans across the upper quarter; wall-mounted dark speakers.
# Blue and navy schoolbags touch the floor beside foreground desks.
# Anchors: rear board center (.53,.37), rear stage corners (.37,.43),(.67,.43);
# yellow wall boundary at left (.00,.43), right (1,.46);
# foreground left tabletop corners (.14,.61),(.35,.60), leg contact (.34,.89).
# Occluded furniture spacing and the exact rear stage depth remain uncertain.
# Expanded mesh estimate: shell/stage 28, windows/doors 80, desks/benches 220,
# fans 36, bags 28, miscellaneous 25: approximately 417 simple primitives.

scene = Scene('Classroom')
cream=(.84,.82,.64)
yellow=(.91,.68,.015)
wood=(.24,.18,.105)
topwood=(.25,.205,.14)
edge=(.32,.27,.17)
dark=(.065,.07,.055)
green=(.035,.19,.10)

def asset(name):
    a=Asset(name=name)
    scene.include(name,a)
    return a

def cube(a,name,size,center,color):
    n=box(size=size,center=center,color=color)
    a.include(name,n)
    return n

def ellipsoid(a,name,center,size,color):
    n=ball(radius=1,center=center,color=color)
    n.resize(size,pivot=center)
    a.include(name,n)
    return n

shell=asset('room_architecture')
cube(shell,'tiled_floor',(8.4,15.4,.12),(0,6.5,-.06),(.64,.53,.33))
cube(shell,'left_upper_wall',(.16,15,3.05),(-4.15,6.5,2.83),cream)
cube(shell,'right_upper_wall',(.16,15,3.05),(4.15,6.5,2.83),(.9,.88,.72))
cube(shell,'left_yellow_dado',(.18,15,1.3),(-4.14,6.5,.65),yellow)
cube(shell,'right_yellow_dado',(.18,15,1.3),(4.14,6.5,.65),yellow)
cube(shell,'rear_wall',(8.4,.15,4.35),(0,14,2.175),cream)
cube(shell,'ceiling',(8.4,15,.12),(0,6.5,4.4),(.9,.89,.79))
for i,y in enumerate([1.2,5.4,9.6]):
    cube(shell,'ceiling_cross_beam_'+str(i),(8.3,.19,.23),(0,y,4.23),(.89,.87,.74))
for i,x in enumerate([-2.0,2.0]):
    cube(shell,'ceiling_long_beam_'+str(i),(.18,14,.23),(x,6.8,4.24),(.91,.89,.78))

stage=asset('rear_stage')
cube(stage,'raised_platform',(5.3,1.2,.30),(0,13.25,.15),(.34,.26,.13))
cube(stage,'dark_stage_recess',(5.25,.12,2.7),(0,13.91,1.83),(.035,.032,.022))
cube(stage,'left_green_curtain',(.46,.18,2.7),(-2.45,13.65,1.83),(.08,.25,.075))
cube(stage,'right_green_curtain',(.42,.18,2.7),(2.45,13.65,1.83),(.045,.24,.09))
cube(stage,'curtain_valance',(5.2,.23,.22),(0,13.56,3.24),(.75,.72,.48))
for i in range(13):
    ellipsoid(stage,'valance_scallop_'+str(i),(-2.4+i*.4,13.51,3.08),(.23,.09,.17),(.8,.77,.57))
cube(stage,'board_frame',(2.28,.12,1.2),(.10,13.13,1.55),(.38,.36,.24))
cube(stage,'green_chalkboard',(2.16,.045,1.08),(.10,13.045,1.56),(.075,.22,.16))
cube(stage,'chalk_tray',(2.3,.17,.055),(.1,12.97,1.00),(.48,.42,.25))
for i,x in enumerate([-.92,1.12]):
    rodpart=rod(radius=.025,start=(x,12.98,.3),end=(x,13.08,1.06),color=(.22,.20,.14))
    stage.include('board_support_'+str(i),rodpart)
cube(stage,'blue_display',(.48,.09,1.08),(1.92,13.17,1.1),(.27,.67,.72))

# Window assemblies retain openings, jambs, transoms, and open wooden shutters.
for side in [-1,1]:
    for j,y in enumerate([1.5,4.8,8.0,11.0]):
        w=asset(('left' if side<0 else 'right')+'_window_'+str(j))
        x=side*4.035
        cube(w,'bright_opening',(.035,1.40,1.95),(x,y,2.35),(.95,.96,.84))
        for k,dy in enumerate([-.76,.76]):
            cube(w,'jamb_'+str(k),(.17,.105,2.15),(x-side*.04,y+dy,2.35),(.35,.26,.14))
        cube(w,'lintel',(.17,1.63,.10),(x-side*.04,y,3.39),(.34,.27,.16))
        cube(w,'sill',(.23,1.65,.11),(x-side*.09,y,1.34),(.37,.28,.16))
        cube(w,'transom',(.12,1.43,.07),(x-side*.08,y,3.02),(.36,.28,.17))
        cube(w,'central_mullion',(.13,.055,1.65),(x-side*.09,y,2.18),(.4,.31,.16))
        shutter=cube(w,'wooden_open_shutter',(.10,.66,1.90),(x-side*.22,y+.84,2.30),(.35,.235,.12))
        shutter.turn('z',side*24)
        for k in [-1,1]:
            cube(w,'shutter_rail_'+str(k),(.13,.56,.065),(x-side*.24,y+.84,2.30+k*.64),(.46,.32,.17))

# Tall wooden door panels on the right, and visible wall decorations.
decor=asset('wall_fittings')
for j,y in enumerate([3.35,9.65]):
    cube(decor,'right_door_'+str(j),(.12,1.13,2.6),(4.00,y,1.3),(.34,.23,.13))
    for k in range(4):
        cube(decor,'door_vertical_'+str(j)+'_'+str(k),(.045,.035,2.35),(3.92,y-.44+k*.29,1.29),(.49,.36,.21))
    cube(decor,'door_header_'+str(j),(.2,1.3,.12),(3.96,y,2.66),(.28,.21,.14))
for side,y in [(-1,1.0),(-1,10.2),(1,6.2)]:
    speaker=cube(decor,'speaker_'+str(side)+'_'+str(y),(.28,.55,.72),(side*3.89,y,3.12),(.025,.055,.052))
    speaker.turn('y',-side*10)
for side,ys in [(-1,[4.0,8.8]),(1,[2.1,5.1,8.4,11.8])]:
    for j,y in enumerate(ys):
        cube(decor,'portrait_frame_'+str(side)+'_'+str(j),(.06,.40,.65),(side*4.025,y,3.63),(.26,.27,.21))
        cube(decor,'portrait_paper_'+str(side)+'_'+str(j),(.065,.32,.55),(side*3.984,y,3.63),(.8,.82,.70))
        ellipsoid(decor,'portrait_mark_'+str(side)+'_'+str(j),(side*3.94,y,3.65),(.018,.085,.16),(.31,.36,.33))

# Desks face the rear board. Each has a thin top, four legs, front rail,
# lower stretcher, and a separate narrow bench with two slab supports.
def desk(name,x,y,width=1.72):
    a=asset(name)
    cube(a,'desktop',(width,.66,.095),(x,y,1.02),topwood)
    cube(a,'front_apron',(width,.075,.19),(x,y-.265,.86),edge)
    for ix in [-1,1]:
        for iy in [-1,1]:
            cube(a,'leg_%s_%s'%(ix,iy),(.075,.075,.96),(x+ix*(width/2-.09),y+iy*.235,.49),(.32,.27,.17))
    cube(a,'lower_stretcher',(width-.12,.055,.065),(x,y+.23,.23),(.31,.26,.16))
    by=y-.70
    cube(a,'bench_seat',(width,.27,.075),(x,by,.57),(.28,.22,.13))
    for ix in [-1,1]:
        cube(a,'bench_support_'+str(ix),(.075,.25,.54),(x+ix*(width/2-.16),by,.27),(.32,.27,.17))
    return a

# Slight asymmetry and partial edge clipping are retained.
desk('foreground_left_desk',-1.72,2.30,1.88)
desk('foreground_right_desk',1.18,3.55,1.85)
desk('right_edge_desk',3.22,4.75,1.45)
desk('left_clipped_desk',-3.67,3.65,1.52)
for col,x,ys in [
    ('left',-2.12,[4.55,6.25,7.90,9.48,10.95]),
    ('center',.45,[5.65,7.20,8.67,10.10,11.45]),
    ('right',2.85,[6.65,8.35,10.0,11.55]),
    ('farleft',-3.45,[7.35,9.05,10.65])]:
    for j,y in enumerate(ys):
        desk(col+'_desk_'+str(j),x,y,1.54 if col=='farleft' else 1.65)

# Schoolbags: rounded cloth bodies, projecting pockets, handles and straps.
def bag(name,x,y,h,color,lean=0):
    a=asset(name)
    ellipsoid(a,'main_fabric',(x,y,h*.50),(.24,.15,h*.48),color)
    ellipsoid(a,'front_pocket',(x,y-.125,h*.34),(.195,.065,h*.22),tuple(c*.82 for c in color))
    ellipsoid(a,'top_handle',(x,y,h*.94),(.085,.035,.06),(.025,.055,.075))
    for s in [-1,1]:
        a.include('shoulder_strap_'+str(s),rod(radius=.022,start=(x+s*.14,y+.12,h*.79),end=(x+s*.25,y+.16,.08),color=(.025,.055,.075)))
    cube(a,'pocket_zipper',(.29,.015,.018),(x,y-.19,h*.47),(.3,.48,.49))
    if lean:
        a.turn('y',lean,pivot=(x,y,0))
bag('navy_bag_foreground',-2.61,1.58,.69,(.025,.055,.09),-10)
bag('blue_bag_foreground',1.42,2.30,.76,(.015,.28,.48),-6)
bag('dark_bag_middle',.15,4.02,.63,(.022,.045,.065),12)
bag('cyan_bag_right',2.95,4.12,.69,(.015,.35,.48),-13)
flatbag=asset('bag_under_left_table')
ellipsoid(flatbag,'flattened_black_bag',(-1.75,1.92,.12),(.42,.22,.12),(.025,.032,.03))

# A few visible books and cloth items.
items=asset('desktop_items')
for i,(x,y) in enumerate([(-2.2,6.2),(-3.45,3.6),(.4,8.7),(2.8,8.35)]):
    cube(items,'book_'+str(i),(.32,.23,.035),(x,y,1.09),(.72,.70,.55))
    cube(items,'book_pages_'+str(i),(.29,.22,.02),(x,y-.01,1.115),(.85,.85,.77))
ellipsoid(items,'pink_cloth',(-2.0,6.1,1.13),(.20,.15,.055),(.69,.43,.65))
cube(items,'white_paper',(.38,.28,.008),(-3.48,3.6,1.08),(.91,.91,.83))

# Six ceiling fans; blades are broad, thin, and visibly separated.
for j,(x,y) in enumerate([(-2.3,1.15),(2.05,1.3),(-2.1,6.1),(2.1,6.4),(-1.5,10.8),(1.85,11.0)]):
    fan=asset('ceiling_fan_'+str(j))
    fan.include('downrod',rod(radius=.022,start=(x,y,4.31),end=(x,y,3.93),color=(.16,.15,.12)))
    ellipsoid(fan,'motor',(x,y,3.91),(.12,.12,.065),(.20,.18,.14))
    for k in range(3):
        angle=math.radians(20+k*120)
        blade=cube(fan,'blade_'+str(k),(.85,.14,.025),(x+.47*math.cos(angle),y+.47*math.sin(angle),3.93),(.23,.22,.18))
        blade.turn('z',20+k*120)

realize(scene)

# Procedural floor variation and a restrained tile grid; no image textures.
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and ob.dimensions.x>8 and ob.dimensions.y>15 and ob.dimensions.z<.2:
        mat=bpy.data.materials.new('warm_ceramic_tile')
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get('Principled BSDF')
        tex=nt.nodes.new('ShaderNodeTexBrick')
        tex.inputs['Color1'].default_value=(.62,.46,.25,1)
        tex.inputs['Color2'].default_value=(.83,.71,.48,1)
        tex.inputs['Mortar'].default_value=(.57,.50,.37,1)
        tex.inputs['Scale'].default_value=1
        tex.inputs['Mortar Size'].default_value=.008
        tex.inputs['Brick Width'].default_value=.43
        tex.inputs['Row Height'].default_value=.43
        tex.offset=0
        coord=nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.46
        ob.data.materials.clear()
        ob.data.materials.append(mat)

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
background.inputs['Color'].default_value=(.78,.82,.72,1)
background.inputs['Strength'].default_value=.65

set_view(position=(.05,-2.45,2.45),target=(0,10.8,1.80),lens=23.8,sensor=36)
area_emitter(position=(0,5.5,4.08),power=950,size=7,target=(0,6,0))
area_emitter(position=(-3.6,3.7,3.0),power=800,size=4,target=(0,5,1.0),color=(1,.96,.83))
area_emitter(position=(3.6,8.2,3.2),power=650,size=4,target=(0,7,1.0),color=(1,.98,.86))
sc.render.resolution_x=512
sc.render.resolution_y=340
sc.render.resolution_percentage=100
sc.view_settings.view_transform='Standard'
sc.view_settings.look='Medium High Contrast'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
# Uncertainty: exact camera intrinsics, individual desk depths and far-side
# bench membership cannot be uniquely recovered from this single photograph.
