from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory (normalized image bounds, approximate):
# room: ceiling (0,0)-(1,.40), ivory walls, dark carpet (.0,.59)-(1,1).
# Right wall whiteboard (.59,.26)-(.92,.59): pale face, narrow aluminum
# perimeter, central seam and lower tray; near edge overlaps the wall.
# Back wall (.11,.38)-(.53,.61): dark vent, open electrical box, hanging
# cover, two small labels, black skirting.
# Ceiling: large acoustic tiles and narrow rails, missing tiles mainly
# at upper-left and above the flag; exposed dark cavities are uncertain.
# Flag (.45,.33)-(.51,.43): diagonal pole, blue canton, hanging red/white folds.
# Left wall (.0,.35)-(.12,.67): brightly lit pale panels with thin seams.
# Floor debris: dark broken panels at (.04,.63)-(.37,.72), (.05,.74)-(.41,.80);
# narrow rails (.15,.71)-(.43,.75), yellow bent panel (.56,.67)-(.90,.79),
# and long metal strips (.78,.77)-(1,.90). No furniture is visible.
# Named assets below preserve these groups. Hidden room extent is uncertain.
# Expanded estimate: architecture 16, ceiling tiles/rails/cavities 112,
# whiteboard 8, back fixtures 17, flag 23, debris 35: about 211 primitives.
# No fillets, booleans, or dense curve expansions.

random.seed(18)
scene = Scene('Abandoned classroom')
cream = (.72,.70,.63)
ceiling_color = (.68,.70,.69)
metal = (.52,.56,.55)
dark = (.065,.075,.070)
floor_color = (.105,.115,.102)

def addbox(parent, name, size, center, color, rotation=None):
    n = box(size=size, center=center, color=color)
    if rotation:
        n.turn(euler=rotation)
    parent.include(name,n)
    return n

room = Asset('room_architecture')
addbox(room,'carpet',(4.8,10.7,.10),(0,4.15,-.05),floor_color)
addbox(room,'right_ivory_wall',(.13,10.7,3.12),(2.36,4.15,1.54),cream)
addbox(room,'back_ivory_wall',(4.8,.13,3.12),(0,8.48,1.54),cream)
addbox(room,'left_bright_wall',(.12,10.7,3.12),(-2.36,4.15,1.54),(.82,.83,.79))
addbox(room,'back_black_baseboard',(4.7,.035,.13),(0,8.39,.065),dark)
addbox(room,'right_black_baseboard',(.035,10.7,.14),(2.28,4.15,.07),dark)
addbox(room,'left_black_baseboard',(.035,10.7,.11),(-2.28,4.15,.055),dark)
for y in [2.0,4.0,6.0]:
    addbox(room,'left_vertical_panel_seam_'+str(y),(.012,.014,2.9),(-2.288,y,1.5),(.66,.69,.67))
for z in [.78,1.55,2.32]:
    addbox(room,'left_horizontal_seam_'+str(z),(.012,8.0,.012),(-2.287,4.4,z),(.71,.73,.70))
scene.include('architecture',room)

ceiling = Asset('suspended_acoustic_ceiling')
addbox(ceiling,'dark_plenum',(4.8,10.7,.08),(0,4.15,3.20),(.12,.15,.14))
# Sparse missing panels expose the suspension cavities.
missing = {(0,2),(0,3),(0,5),(0,6),(1,6),(3,7)}
for ix in range(8):
    for iy in range(9):
        x=-2.1+ix*.6
        y=-1.1+iy*1.16
        if (ix,iy) in missing:
            continue
        c = .675 + random.uniform(-.025,.025)
        addbox(ceiling,f'tile_{ix}_{iy}',(.586,1.145,.035),(x,y,3.055),(c,c+.015,c+.01))
for ix in range(9):
    addbox(ceiling,f'long_rail_{ix}',(.018,10.5,.024),(-2.4+ix*.6,4.0,3.035),(.63,.67,.65))
for iy in range(10):
    addbox(ceiling,f'cross_rail_{iy}',(4.8,.018,.024),(0,-1.68+iy*1.16,3.034),(.63,.67,.65))
# Two subtly translucent rectangular ceiling light diffusers.
for k,y in enumerate([2.0,5.48]):
    addbox(ceiling,'light_frame_'+str(k),(.62,1.17,.032),(-1.2,y,3.028),(.56,.60,.59))
    addbox(ceiling,'light_diffuser_'+str(k),(.565,1.10,.015),(-1.2,y,3.005),(.78,.81,.80))
detector = ball(.075,center=(-1.25,1.8,2.995),color=(.79,.79,.73))
detector.resize((1,1,.38))
ceiling.include('smoke_detector',detector)
scene.include('ceiling',ceiling)

board = Asset('large_right_wall_whiteboard')
board_y0,board_y1 = 3.60,7.48
board_z0,board_z1 = 1.03,2.61
addbox(board,'backing',(.055,board_y1-board_y0,board_z1-board_z0),
       (2.255,(board_y0+board_y1)/2,(board_z0+board_z1)/2),(.71,.74,.72))
addbox(board,'writing_face',(.018,board_y1-board_y0-.07,board_z1-board_z0-.065),
       (2.216,(board_y0+board_y1)/2,(board_z0+board_z1)/2),(.79,.82,.82))
for name,y in [('near',board_y0),('far',board_y1)]:
    addbox(board,name+'_aluminum_upright',(.045,.027,board_z1-board_z0+.03),(2.193,y,(board_z0+board_z1)/2),metal)
for name,z in [('top',board_z1),('bottom',board_z0)]:
    addbox(board,name+'_aluminum_rail',(.045,board_y1-board_y0+.04,.027),(2.194,(board_y0+board_y1)/2,z),metal)
addbox(board,'center_division',(.021,.014,board_z1-board_z0-.04),(2.196,5.67,(board_z0+board_z1)/2),(.65,.69,.69))
addbox(board,'lower_marker_tray',(.105,board_y1-board_y0,.027),(2.17,(board_y0+board_y1)/2,1.014),(.59,.62,.60))
scene.include('whiteboard',board)

fixtures=Asset('back_wall_utilities')
addbox(fixtures,'vent_frame',(.88,.035,.41),(-1.38,8.386,1.82),(.52,.55,.52))
addbox(fixtures,'vent_dark_opening',(.79,.025,.33),(-1.38,8.36,1.82),(.23,.28,.28))
for i in range(5):
    addbox(fixtures,'vent_louver_'+str(i),(.77,.025,.012),(-1.38,8.34,1.70+i*.057),(.32,.36,.35))
addbox(fixtures,'electrical_box_rim',(.34,.045,.45),(-.23,8.37,1.55),(.54,.56,.51))
addbox(fixtures,'electrical_box_interior',(.265,.025,.37),(-.23,8.333,1.55),(.16,.19,.17))
addbox(fixtures,'electric_pale_component',(.07,.025,.20),(-.29,8.31,1.58),(.67,.68,.60))
addbox(fixtures,'electric_wire',(.025,.03,.21),(-.18,8.30,1.59),(.36,.39,.33),rotation=(0,12,0))
addbox(fixtures,'loose_hanging_metal_cover',(.48,.05,.39),(-.04,8.24,1.22),(.43,.49,.46),rotation=(0,-38,0))
for k,x in enumerate([.40,.64]):
    addbox(fixtures,'wall_label_'+str(k),(.16,.015,.20),(x,8.39,1.38),(.76,.75,.66))
    addbox(fixtures,'label_mark_'+str(k),(.095,.008,.025),(x,8.375,1.42),(.42,.44,.38))
scene.include('back_utilities',fixtures)

flag = Asset('hanging_american_flag')
flag.include('angled_flagpole',rod(.012,start=(2.24,7.67,2.66),end=(1.23,7.55,2.91),color=(.30,.31,.27)))
# The flag hangs in narrow folds: the striped field is vertically oriented.
for i in range(13):
    x=1.205+i*.034
    z=2.54 - .04*math.sin(i*.45)
    col=(.60,.075,.065) if i%2==0 else (.82,.80,.70)
    addbox(flag,'fabric_stripe_'+str(i),(.034,.018,.62),
           (x,7.53+.026*math.sin(i*1.1),z),col,rotation=(0,-5,0))
addbox(flag,'blue_canton',(.19,.024,.25),(1.30,7.505,2.75),(.13,.19,.26),rotation=(0,-5,0))
for ix in range(3):
    for iz in range(3):
        addbox(flag,f'canton_star_{ix}_{iz}',(.011,.008,.011),
               (1.24+ix*.048,7.487,2.68+iz*.062),(.81,.81,.72))
scene.include('flag',flag)

debris=Asset('fallen_ceiling_and_floor_debris')
def panel(name,x,y,sx,sy,angle,color,z=.026):
    return addbox(debris,name,(sx,sy,.025),(x,y,z),color,rotation=(0,0,angle))

# Thin broken ceiling sheets, with dark undersides and offset fragments.
panel('foreground_dark_tile',-1.11,2.36,1.48,.58,-9,(.20,.23,.21))
panel('foreground_gray_facing',-1.30,2.44,1.05,.43,-9,(.40,.42,.37),.045)
panel('foreground_right_fragment',-.68,2.57,.61,.28,16,(.32,.35,.30),.061)
panel('foreground_small_flap',-1.47,2.64,.48,.29,-26,(.49,.50,.43),.063)
panel('middle_left_dark_panel',-1.75,4.26,1.08,.48,-11,(.19,.22,.20))
panel('middle_left_light_fragment',-1.91,4.32,.69,.35,-11,(.49,.50,.43),.046)
panel('middle_panel_splinter',-1.32,4.33,.43,.19,21,(.34,.37,.32),.055)
panel('back_dark_panel',-.98,6.12,1.04,.39,15,(.16,.19,.17))
panel('back_light_fragment',-1.25,6.07,.45,.23,15,(.44,.46,.39),.046)
panel('back_small_chip',-.65,6.33,.31,.16,-20,(.35,.37,.31),.054)
# Reflective exposed ceiling strips across the carpet.
addbox(debris,'long_center_aluminum_strip',(1.54,.052,.025),(-.50,3.83,.055),(.63,.68,.67),rotation=(0,1,-12))
addbox(debris,'center_strip_dark_side',(1.5,.016,.026),(-.50,3.80,.059),(.31,.36,.34),rotation=(0,1,-12))
addbox(debris,'rear_bent_strip',(.73,.025,.02),(-.73,6.37,.065),(.48,.53,.50),rotation=(0,0,21))
for k in range(7):
    x=random.uniform(-1.9,1.95)
    y=random.uniform(2.7,7.6)
    panel('small_plaster_chip_'+str(k),x,y,random.uniform(.05,.13),random.uniform(.04,.09),random.uniform(0,180),(.49,.49,.40),.025)

# Yellow fiberglass/ceiling panel on right, with a lifted arched outer end.
yellow=(.63,.51,.19)
panel('yellow_panel_underlayer',1.30,3.03,1.40,1.13,-5,(.56,.46,.19),.055)
# Adjacent broad sections form a bent, continuous sheet silhouette.
for i,(x,z,tilt) in enumerate([(0.86,.12,-5),(1.15,.16,-9),(1.44,.23,-17),(1.72,.22,18)]):
    addbox(debris,'yellow_bent_sheet_section_'+str(i),(.33,1.14,.035),(x,3.02,z),yellow,rotation=(0,tilt,-5))
addbox(debris,'yellow_torn_front_tab',(.19,.70,.028),(.77,2.80,.085),(.68,.56,.24),rotation=(0,8,-7))
addbox(debris,'yellow_fold_crease',(.028,1.13,.025),(1.30,3.01,.205),(.48,.40,.17),rotation=(0,-9,-5))
# Two long rails extend diagonally toward the right foreground edge.
addbox(debris,'foreground_long_white_rail',(.075,2.27,.035),(1.89,1.30,.045),(.68,.69,.63),rotation=(0,0,-25))
addbox(debris,'foreground_parallel_metal_rail',(.045,1.87,.032),(2.15,1.56,.050),(.47,.52,.51),rotation=(0,0,-31))
scene.include('floor_debris',debris)

# A small outlet below the board.
outlet=Asset('right_wall_outlet')
addbox(outlet,'ivory_plate',(.016,.10,.15),(2.278,6.10,.54),(.72,.68,.55))
addbox(outlet,'socket',(.019,.028,.045),(2.265,6.10,.54),(.48,.46,.36))
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
background.inputs['Strength'].default_value=.36

# Restrained procedural carpet and plaster detail, without image textures.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Roughness'].default_value=.86
    c=bs.inputs['Base Color'].default_value
    if abs(c[0]-floor_color[0])<.018 and abs(c[1]-floor_color[1])<.018:
        nt=mat.node_tree
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=155
        tex.inputs['Detail'].default_value=2
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.19
        ramp.color_ramp.elements[0].color=(.055,.065,.057,1)
        ramp.color_ramp.elements[1].position=.81
        ramp.color_ramp.elements[1].color=(.19,.20,.17,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.28
        bump.inputs['Distance'].default_value=.018
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view(position=(-1.65,-.85,1.69),target=(.25,7.1,1.52),lens=23.5,sensor=36)
area_emitter(position=(-3.5,2.7,2.15),power=750,size=4.2,target=(.5,5.0,1.0),color=(.88,.94,1.0))
area_emitter(position=(-.4,1.5,2.86),power=130,size=3.0,target=(0,5,.3),color=(1.0,.96,.87))
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
