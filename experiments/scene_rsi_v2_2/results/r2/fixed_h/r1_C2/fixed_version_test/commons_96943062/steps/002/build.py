from sceneact import *
import bpy, math, random

# Reference inventory, approximate normalized image bounds:
# Architecture: ivory back wall (.11,.38)-(.53,.61), right wall,
# bright left panels (0,.34)-(.12,.67), carpet (0,.59)-(1,1).
# Ceiling tiles, thin suspension grid, two light panels and small detector;
# missing tiles expose dark cavities predominantly along the left edge.
# Whiteboard (.59,.26)-(.92,.59): two pale panels, aluminum perimeter,
# middle seam and bottom tray. It overlaps the right wall.
# Back utilities: vent (.15,.44)-(.25,.48), open electrical box,
# tilted cover (.30,.46)-(.39,.54), and two small labels.
# Flag (.45,.33)-(.51,.43): diagonal pole, blue canton, striped folds.
# Floor: three groups of broken ceiling panels, a thin central rail,
# yellow bent sheet (.56,.67)-(.90,.79), long foreground metal strips.
# Unseen room continuation and cavity interiors remain uncertain.
#
# Review of first render: the back wall was displaced right; the left
# wall occupied too much image area. The whiteboard was too distant,
# too short in projection, and the foreground debris was too large.
# Revised camera position and elevation match the room junctions;
# the whiteboard retains its editable parts with revised extent.
#
# Expanded primitive estimate: architecture 13, ceiling 96,
# board 8, utilities 16, flag 24, debris 35, outlet 2: about 194 meshes.
# No booleans, fillet expansions, or dense repeated decoration.

random.seed(18)
scene = Scene('Abandoned classroom')
cream = (.72,.70,.63)
metal = (.52,.56,.55)
dark = (.065,.075,.070)
floor_color = (.105,.115,.102)

def addbox(parent, name, size, center, color, rotation=None):
    node = box(size=size, center=center, color=color)
    if rotation is not None:
        node.turn(euler=rotation)
    parent.include(name, node)
    return node

room = Asset('room_architecture')
addbox(room,'carpet',(4.8,10.7,.10),(0,4.15,-.05),floor_color)
addbox(room,'right_ivory_wall',(.13,10.7,3.12),(2.36,4.15,1.54),cream)
addbox(room,'back_ivory_wall',(4.8,.13,3.12),(0,8.48,1.54),cream)
addbox(room,'left_bright_wall',(.12,10.7,3.12),(-2.36,4.15,1.54),(.85,.86,.83))
addbox(room,'back_black_baseboard',(4.7,.035,.13),(0,8.39,.065),dark)
addbox(room,'right_black_baseboard',(.035,10.7,.14),(2.28,4.15,.07),dark)
addbox(room,'left_black_baseboard',(.035,10.7,.11),(-2.28,4.15,.055),dark)
for y in (2.0,4.0,6.0):
    addbox(room,'left_vertical_seam_'+str(y),(.012,.014,2.9),
           (-2.288,y,1.5),(.69,.72,.70))
for z in (.78,1.55,2.32):
    addbox(room,'left_horizontal_seam_'+str(z),(.012,8,.012),
           (-2.287,4.4,z),(.73,.75,.73))
scene.include('architecture',room)

ceiling = Asset('suspended_acoustic_ceiling')
addbox(ceiling,'dark_plenum',(4.8,10.7,.08),(0,4.15,3.20),(.10,.13,.12))
missing = {(0,2),(0,3),(0,5),(0,6),(1,6),(5,7)}
for ix in range(8):
    for iy in range(9):
        if (ix,iy) in missing:
            continue
        c = .675 + random.uniform(-.019,.019)
        addbox(ceiling,f'tile_{ix}_{iy}',(.586,1.145,.035),
               (-2.1+ix*.6,-1.1+iy*1.16,3.055),(c,c+.015,c+.01))
for ix in range(9):
    addbox(ceiling,f'long_rail_{ix}',(.016,10.5,.021),
           (-2.4+ix*.6,4,3.035),(.63,.67,.65))
for iy in range(10):
    addbox(ceiling,f'cross_rail_{iy}',(4.8,.016,.021),
           (0,-1.68+iy*1.16,3.034),(.63,.67,.65))
for k,y in enumerate((2.0,5.48)):
    addbox(ceiling,'light_frame_'+str(k),(.62,1.17,.032),
           (-1.2,y,3.028),(.56,.60,.59))
    addbox(ceiling,'light_diffuser_'+str(k),(.565,1.10,.015),
           (-1.2,y,3.005),(.79,.82,.82))
detector = ball(.075,center=(-1.25,1.8,2.995),color=(.79,.79,.73))
detector.resize((1,1,.38))
ceiling.include('smoke_detector',detector)
scene.include('ceiling',ceiling)

board = Asset('large_right_wall_whiteboard')
board_y0, board_y1 = 2.00,6.20
board_z0, board_z1 = .84,2.49
yc=(board_y0+board_y1)/2
zc=(board_z0+board_z1)/2
addbox(board,'backing',(.055,board_y1-board_y0,board_z1-board_z0),
       (2.255,yc,zc),(.71,.74,.72))
addbox(board,'writing_face',(.018,board_y1-board_y0-.07,board_z1-board_z0-.065),
       (2.216,yc,zc),(.80,.83,.84))
for name,y in (('near',board_y0),('far',board_y1)):
    addbox(board,name+'_aluminum_upright',(.045,.027,board_z1-board_z0+.03),
           (2.193,y,zc),metal)
for name,z in (('top',board_z1),('bottom',board_z0)):
    addbox(board,name+'_aluminum_rail',(.045,board_y1-board_y0+.04,.027),
           (2.194,yc,z),metal)
addbox(board,'center_division',(.021,.014,board_z1-board_z0-.04),
       (2.196,4.92,zc),(.66,.70,.70))
addbox(board,'lower_marker_tray',(.105,board_y1-board_y0,.027),
       (2.17,yc,board_z0-.016),(.59,.62,.60))
scene.include('whiteboard',board)

fixtures = Asset('back_wall_utilities')
addbox(fixtures,'vent_frame',(.88,.035,.41),(-1.38,8.386,1.82),(.52,.55,.52))
addbox(fixtures,'vent_dark_opening',(.79,.025,.33),(-1.38,8.36,1.82),(.23,.28,.28))
for i in range(5):
    addbox(fixtures,'vent_louver_'+str(i),(.77,.025,.012),
           (-1.38,8.34,1.70+i*.057),(.32,.36,.35))
addbox(fixtures,'electrical_box_rim',(.34,.045,.45),(.02,8.37,1.55),(.54,.56,.51))
addbox(fixtures,'electrical_box_interior',(.265,.025,.37),(.02,8.333,1.55),(.16,.19,.17))
addbox(fixtures,'electric_pale_component',(.07,.025,.20),(-.04,8.31,1.58),(.67,.68,.60))
addbox(fixtures,'electric_wire',(.025,.03,.21),(.07,8.30,1.59),
       (.36,.39,.33),rotation=(0,12,0))
addbox(fixtures,'loose_hanging_metal_cover',(.48,.05,.39),(.21,8.24,1.22),
       (.43,.49,.46),rotation=(0,-38,0))
for k,x in enumerate((.65,.89)):
    addbox(fixtures,'wall_label_'+str(k),(.16,.015,.20),(x,8.39,1.38),(.76,.75,.66))
    addbox(fixtures,'label_mark_'+str(k),(.095,.008,.025),(x,8.375,1.42),(.42,.44,.38))
scene.include('back_utilities',fixtures)

flag = Asset('hanging_american_flag')
flag.include('angled_flagpole',rod(.012,
    start=(2.24,6.60,2.66),end=(1.23,6.10,3.12),color=(.30,.31,.27)))
for i in range(13):
    x=1.205+i*.034
    z=2.675-.035*math.sin(i*.45)
    col=(.64,.065,.055) if i%2==0 else (.86,.83,.75)
    addbox(flag,'fabric_stripe_'+str(i),(.034,.018,.85),
           (x,6.10+.026*math.sin(i*1.1),z),col,rotation=(0,-5,0))
addbox(flag,'blue_canton',(.19,.024,.32),(1.30,6.075,2.93),
       (.11,.17,.24),rotation=(0,-5,0))
for ix in range(3):
    for iz in range(3):
        addbox(flag,f'canton_star_{ix}_{iz}',(.011,.008,.011),
               (1.24+ix*.048,6.057,2.83+iz*.080),(.85,.85,.78))
scene.include('flag',flag)

debris = Asset('fallen_ceiling_and_floor_debris')
def panel(name,x,y,sx,sy,angle,color,z=.026):
    return addbox(debris,name,(sx,sy,.025),(x,y,z),color,rotation=(0,0,angle))

panel('foreground_dark_tile',-.43,2.63,1.30,.46,-9,(.20,.23,.21))
panel('foreground_gray_facing',-.60,2.70,.91,.34,-9,(.36,.38,.33),.045)
panel('foreground_right_fragment',-.06,2.80,.54,.23,16,(.29,.32,.27),.061)
panel('foreground_small_flap',-.75,2.83,.42,.24,-26,(.43,.45,.38),.063)
panel('middle_left_dark_panel',-1.45,4.26,1.08,.38,-11,(.19,.22,.20))
panel('middle_left_light_fragment',-1.61,4.32,.69,.28,-11,(.43,.45,.38),.046)
panel('middle_panel_splinter',-1.02,4.33,.43,.16,21,(.30,.33,.28),.055)
panel('back_dark_panel',-.75,6.12,1.04,.33,15,(.16,.19,.17))
panel('back_light_fragment',-1.02,6.07,.45,.20,15,(.40,.42,.35),.046)
panel('back_small_chip',-.42,6.33,.31,.14,-20,(.31,.33,.27),.054)
addbox(debris,'long_center_aluminum_strip',(1.54,.040,.025),
       (-.50,3.83,.055),(.63,.68,.67),rotation=(0,1,-12))
addbox(debris,'center_strip_dark_side',(1.50,.016,.026),
       (-.50,3.80,.059),(.31,.36,.34),rotation=(0,1,-12))
addbox(debris,'rear_bent_strip',(.73,.025,.02),
       (-.50,6.37,.065),(.48,.53,.50),rotation=(0,0,21))
for k in range(7):
    panel('small_plaster_chip_'+str(k),
          random.uniform(-1.9,1.95),random.uniform(2.7,7.6),
          random.uniform(.04,.10),random.uniform(.03,.07),
          random.uniform(0,180),(.43,.43,.35),.025)

yellow=(.65,.53,.21)
panel('yellow_panel_underlayer',1.30,2.63,1.40,1.13,-5,(.56,.46,.19),.055)
for i,(x,z,tilt) in enumerate(((.86,.12,-5),(1.15,.16,-9),
                               (1.44,.23,-17),(1.72,.22,18))):
    addbox(debris,'yellow_bent_sheet_section_'+str(i),(.33,1.14,.035),
           (x,2.62,z),yellow,rotation=(0,tilt,-5))
addbox(debris,'yellow_torn_front_tab',(.19,.70,.028),(.77,2.40,.085),
       (.68,.56,.24),rotation=(0,8,-7))
addbox(debris,'yellow_fold_crease',(.022,1.13,.025),(1.30,2.61,.205),
       (.51,.43,.18),rotation=(0,-9,-5))
addbox(debris,'foreground_long_white_rail',(.075,2.27,.035),
       (1.89,1.30,.045),(.68,.69,.63),rotation=(0,0,-25))
addbox(debris,'foreground_parallel_metal_rail',(.045,1.87,.032),
       (2.15,1.56,.050),(.47,.52,.51),rotation=(0,0,-31))
scene.include('floor_debris',debris)

outlet=Asset('right_wall_outlet')
addbox(outlet,'ivory_plate',(.016,.10,.15),(2.278,4.75,.54),(.72,.68,.55))
addbox(outlet,'socket',(.019,.028,.045),(2.265,4.75,.54),(.48,.46,.36))
scene.include('outlet',outlet)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get('Background')
if background is None:
    background=nodes.new('ShaderNodeBackground')
output=nodes.get('World Output')
if output is None:
    output=nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.66,.72,.78,1)
background.inputs['Strength'].default_value=.40

for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Roughness'].default_value=.86
    c=bs.inputs['Base Color'].default_value
    if abs(c[0]-floor_color[0])<.018 and abs(c[1]-floor_color[1])<.018:
        nt=mat.node_tree
        coord=nt.nodes.new('ShaderNodeTexCoord')
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=110
        tex.inputs['Detail'].default_value=2
        nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(.065,.073,.061,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(.145,.153,.128,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.16
        bump.inputs['Distance'].default_value=.009
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view(position=(.10,-.85,1.17),target=(1.60,7.10,1.34),
         lens=23.5,sensor=36)
area_emitter(position=(-2.10,2.7,2.15),power=240,size=4.2,
             target=(1.0,5.0,1.0),color=(.91,.96,1.0))
area_emitter(position=(-.4,1.5,2.86),power=100,size=3.0,
             target=(0,5,.3),color=(1.0,.96,.89))
area_emitter(position=(-2.05,6.5,2.0),power=80,size=2.5,
             target=(1.8,6.8,1.4),color=(1.0,.98,.94))
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
