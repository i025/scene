from sceneact import *
import bpy
import math
import random

# Reference inventory (normalized image bounds, approximate):
# room: gray carpet (0,.59)-(1,1), beige back wall (.11,.38)-(.53,.61),
# beige right wall (.52,0)-(1,.83), suspended tile ceiling (0,0)-(1,.39).
# Bright left window wall (0,.32)-(.12,.67); its outer extent is occluded.
# Whiteboard (.59,.26)-(.91,.58): silver surround, tray, two white sections.
# Flag (.45,.32)-(.51,.43): angled support, blue canton, narrow red/white folds.
# Back fixtures: vent (.15,.44)-(.25,.48), open electrical box
# (.30,.46)-(.34,.51), dangling cover (.31,.48)-(.39,.54), small wall plates.
# Ceiling: rectangular light panels, thin grid, several dark missing tiles
# along the upper left; exposed cavities are uncertain.
# Floor debris: gray broken panels at (0,.64)-(.40,.80), narrow metal strips
# (.15,.72)-(.43,.75), yellow fallen insulation (.56,.67)-(.90,.79),
# long silver tracks (.77,.77)-(1,.89), and scattered small fragments.
# Each item is represented by the named SceneAct asset below.
#
# Estimated expansion: architecture 14 boxes, ceiling/grid/lights ~65 boxes,
# board 9, flag/support/stars ~36, back fixtures ~22, debris ~35:
# approximately 185 primitive meshes; no booleans or fillet expansions.

random.seed(18)
scene = Scene("Vacant damaged classroom")

BEIGE = (.66, .645, .585)
CEILING = (.62, .65, .65)
GRID = (.47, .51, .51)
CARPET = (.105, .117, .106)
BASE = (.065, .082, .078)
SILVER = (.52, .56, .55)
WHITE = (.78, .80, .78)
DARK = (.045, .059, .058)

def cube(parent, name, size, center, color, rotation=None):
    node = box(size=size, center=center, color=color)
    if rotation:
        node.turn(euler=rotation)
    parent.include(name, node)
    return node

architecture = Asset("room_architecture")
cube(architecture, "carpet_floor", (4.5, 10.4, .10), (-.35, 2.5, -.05), CARPET)
cube(architecture, "back_plaster", (4.3, .12, 2.78), (-.35, 7.08, 1.39), BEIGE)
cube(architecture, "right_plaster", (.12, 10.4, 2.78), (1.86, 2.0, 1.39), (.72, .70, .64))
cube(architecture, "back_dark_baseboard", (4.3, .045, .105), (-.35, 7.005, .052), BASE)
cube(architecture, "right_dark_baseboard", (.045, 10.4, .105), (1.785, 2., .052), BASE)
scene.include("architecture", architecture)

windows = Asset("bright_left_window_wall")
cube(windows, "translucent_glazing", (.045, 9.7, 2.65), (-2.48, 2.2, 1.355), (.89, .93, .93))
for j, y in enumerate([-1.8, -.2, 1.4, 3.0, 4.6, 6.2]):
    cube(windows, "vertical_mullion_%d" % j, (.07, .023, 2.65),
         (-2.445, y, 1.355), (.71, .76, .76))
cube(windows, "horizontal_window_seam", (.07, 9.7, .018),
     (-2.44, 2.2, 1.12), (.76, .80, .79))
scene.include("left_windows", windows)

ceiling = Asset("suspended_ceiling")
cube(ceiling, "continuous_tile_surface", (4.3, 10.5, .065), (-.35, 2.0, 2.815), CEILING)
for i in range(9):
    x = -2.45 + .535*i
    cube(ceiling, "long_grid_%02d" % i, (.012, 10.5, .012),
         (x, 2.0, 2.775), GRID)
for j in range(19):
    y = -3.0 + .56*j
    cube(ceiling, "cross_grid_%02d" % j, (4.3, .012, .012),
         (-.35, y, 2.775), GRID)

# Dark openings occupy only a narrow strip of the left ceiling.
for k, y in enumerate([3.2, 3.76, 4.88, 5.44, 6.56]):
    cube(ceiling, "missing_tile_cavity_%d" % k, (.51, .535, .016),
         (-2.17, y, 2.764), (.035, .050, .050))
    cube(ceiling, "cavity_inner_rail_%d" % k, (.43, .028, .024),
         (-2.17, y+.10, 2.745), (.24, .28, .27))
for k, (x, y, sx, sy) in enumerate([
    (-1.35, 2.10, .50, 1.07),
    (-1.35, 4.34, .50, 1.07),
    (-1.35, 6.02, .50, .52),
    (-1.35, -.70, .50, 1.07)
]):
    cube(ceiling, "light_fixture_rim_%d" % k, (sx+.035, sy+.035, .027),
         (x, y, 2.754), (.48, .53, .53))
    cube(ceiling, "light_diffuser_%d" % k, (sx, sy, .014),
         (x, y, 2.735), (.79, .84, .83))
ceiling.include("smoke_detector_base",
                rod(.065, length=.025, center=(-1.05, .6, 2.735), color=(.74,.75,.70)))
ceiling.include("smoke_detector_cap",
                rod(.043, length=.025, center=(-1.05, .6, 2.711), color=(.71,.72,.67)))
scene.include("ceiling", ceiling)

board = Asset("large_two_section_whiteboard")
board_y0, board_y1 = 2.55, 6.12
board_z0, board_z1 = .99, 2.27
cube(board, "white_writing_surface", (.032, board_y1-board_y0, board_z1-board_z0),
     (1.766, (board_y0+board_y1)/2, (board_z0+board_z1)/2), (.79,.81,.80))
for name, y in [("near_vertical_frame",board_y0),("far_vertical_frame",board_y1)]:
    cube(board, name, (.047,.025,board_z1-board_z0+.055),
         (1.741,y,(board_z0+board_z1)/2), SILVER)
for name, z in [("top_frame",board_z1),("bottom_frame",board_z0)]:
    cube(board,name,(.047,board_y1-board_y0+.035,.025),
         (1.741,(board_y0+board_y1)/2,z),SILVER)
cube(board,"section_divider",(.037,.013,board_z1-board_z0),
     (1.738,4.91,(board_z0+board_z1)/2),(.60,.64,.63))
cube(board,"shallow_marker_tray",(.075,board_y1-board_y0,.018),
     (1.715,(board_y0+board_y1)/2,board_z0-.025),(.56,.59,.57))
for k,y in enumerate([2.69,5.92]):
    cube(board,"top_mount_%d"%k,(.045,.045,.065),(1.74,y,2.30),(.42,.46,.45))
scene.include("whiteboard",board)

fixtures = Asset("back_wall_service_fixtures")
cube(fixtures,"vent_dark_recess",(.87,.025,.43),(-1.62,6.997,1.79),(.27,.32,.32))
for x in [-2.065,-1.175]:
    cube(fixtures,"vent_side_"+str(x),(.025,.027,.45),(x,6.975,1.79),(.48,.51,.48))
for z in [1.565,2.015]:
    cube(fixtures,"vent_edge_"+str(z),(.91,.027,.022),(-1.62,6.975,z),(.48,.51,.48))
for i in range(5):
    cube(fixtures,"vent_louver_%d"%i,(.82,.015,.011),(-1.62,6.963,1.64+i*.065),(.34,.39,.38))
cube(fixtures,"electrical_box_rim",(.35,.05,.44),(-.39,6.97,1.50),(.47,.51,.48))
cube(fixtures,"electrical_box_open_interior",(.265,.022,.355),(-.39,6.932,1.50),(.10,.15,.15))
cube(fixtures,"electrical_internal_component",(.065,.035,.23),(-.39,6.91,1.52),(.60,.62,.57))
cube(fixtures,"electrical_internal_wire",(.024,.03,.23),(-.47,6.903,1.48),(.20,.23,.20))
cover = cube(fixtures,"loose_diagonal_metal_cover",(.49,.045,.42),(-.11,6.81,1.14),(.40,.46,.44))
cover.turn(axis="+y", degrees=42)
cube(fixtures,"cover_dark_fastener",(.026,.012,.027),(-.12,6.776,1.18),(.15,.21,.20))
for i,x in enumerate([.23,.48]):
    cube(fixtures,"small_wall_plate_%d"%i,(.14,.024,.22),(x,6.985,1.26),(.77,.76,.69))
    cube(fixtures,"plate_switch_%d"%i,(.035,.015,.063),(x,6.964,1.27),(.43,.46,.42))
scene.include("back_fixtures",fixtures)

flag = Asset("hanging_American_flag")
flag.include("angled_support_pole",rod(.012,start=(1.78,6.20,2.56),
                                      end=(.91,6.18,3.00),color=(.24,.26,.22)))
# Narrow folded stripes hang vertically from the sloping supported edge.
for i in range(13):
    x=.965+i*.032
    top=2.98-(x-.94)*.57
    bottom=2.22+(x-.94)*.12
    col=(.56,.065,.055) if i%2==0 else (.82,.81,.73)
    stripe=cube(flag,"hanging_fold_stripe_%02d"%i,
                (.033,.018,top-bottom),(x,6.15+math.sin(i*1.5)*.017,(top+bottom)/2),col)
cube(flag,"blue_canton",(.205,.026,.275),(1.025,6.126,2.785),(.075,.12,.16))
for row in range(4):
    for col in range(3):
        cube(flag,"canton_star_%d_%d"%(row,col),(.009,.008,.009),
             (.95+.054*col,6.108,2.69+.055*row),(.77,.78,.72))
scene.include("flag",flag)

debris = Asset("fallen_ceiling_material")
def panel(name, center, size, angle, color, tilt=0):
    return cube(debris,name,size,center,color,(tilt,0,angle))

panel("foreground_broken_gray_panel",(-.40,2.47,.035),(1.26,.55,.035),-11,(.32,.35,.32),2)
panel("foreground_panel_light_face",(-.53,2.48,.060),(.80,.43,.018),8,(.42,.44,.39),-2)
panel("foreground_panel_dark_overlap",(-.15,2.54,.075),(.58,.35,.016),-18,(.22,.25,.23),3)
panel("left_midground_tile",(-1.04,3.71,.024),(1.0,.43,.027),-17,(.40,.43,.38),1)
panel("left_midground_tile_overlap",(-1.30,3.85,.045),(.68,.30,.024),7,(.30,.33,.30),-3)
panel("back_scattered_tile",(-.94,5.19,.025),(.86,.36,.026),12,(.31,.34,.30),1)
panel("back_tile_pale_fragment",(-1.15,5.11,.045),(.31,.21,.016),-12,(.54,.55,.46),0)
panel("long_center_metal_strip",(-.03,3.25,.045),(1.43,.033,.025),-9,(.61,.65,.63),0)
panel("second_center_metal_strip",(-.13,3.29,.047),(.89,.019,.021),-12,(.76,.78,.72),0)

insulation = Asset("fallen_yellow_insulation_panels")
cube(insulation,"rear_thick_yellow_slab",(1.05,.91,.10),(1.13,3.44,.12),(.65,.54,.24),(0,-7,-7))
cube(insulation,"front_yellow_panel",(1.10,.84,.065),(1.28,2.91,.155),(.68,.57,.25),(13,-5,-7))
cube(insulation,"exposed_pale_fibrous_edge",(.90,.045,.105),(1.08,3.00,.085),(.73,.66,.40),(0,-7,-7))
cube(insulation,"small_insulation_flap",(.31,.63,.035),(.74,3.02,.12),(.63,.54,.28),(5,-10,-7))
scene.include("yellow_debris",insulation)

panel("right_long_aluminum_track",(1.62,1.65,.033),(.055,2.20,.025),-20,(.64,.66,.61),0)
panel("right_parallel_track",(1.83,1.59,.040),(.045,2.16,.024),-20,(.70,.71,.66),0)
panel("right_track_dark_channel",(1.64,1.64,.050),(.013,2.12,.010),-20,(.28,.32,.30),0)
for i in range(14):
    x=random.uniform(-1.85,1.65)
    y=random.uniform(1.0,6.5)
    panel("small_fragment_%02d"%i,(x,y,.012),
          (random.uniform(.025,.11),random.uniform(.018,.075),.012),
          random.uniform(-80,80),random.choice([(.43,.44,.37),(.30,.33,.29),(.57,.55,.43)]))
scene.include("gray_floor_debris",debris)

outlets = Asset("right_wall_small_outlets")
for i,y in enumerate([1.80,5.43]):
    cube(outlets,"cream_plate_%d"%i,(.018,.105,.15),(1.785,y,.66),(.68,.66,.55))
    cube(outlets,"socket_slot_%d"%i,(.009,.018,.043),(1.771,y,.67),(.39,.39,.32))
scene.include("right_outlets",outlets)

realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.72,.77,.79,1)
background.inputs["Strength"].default_value=.38

# Restrained procedural carpet variation supplies the unresolved fine texture.
carpet_mat=bpy.data.materials.new("mottled_dark_commercial_carpet")
carpet_mat.use_nodes=True
nodes=carpet_mat.node_tree.nodes
links=carpet_mat.node_tree.links
bsdf=nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value=.98
tex=nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value=155
tex.inputs["Detail"].default_value=2
ramp=nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.20
ramp.color_ramp.elements[0].color=(.045,.055,.049,1)
ramp.color_ramp.elements[1].position=.80
ramp.color_ramp.elements[1].color=(.155,.166,.139,1)
links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
bump=nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.23
bump.inputs["Distance"].default_value=.016
links.new(tex.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
for obj in bpy.data.objects:
    if obj.type=="MESH" and obj.dimensions.x>4 and obj.location.z<.01:
        obj.data.materials.clear()
        obj.data.materials.append(carpet_mat)

set_view(position=(.65,-.40,1.65),target=(1.52,7.0,1.13),lens=26.7,sensor=36)
area_emitter(position=(-2.15,2.0,2.05),power=430,size=4.5,
             target=(.6,4.0,.9),color=(.86,.93,1.0))
area_emitter(position=(-.6,3.0,2.65),power=125,size=3.0,
             target=(.3,3.5,0),color=(.95,.96,.90))
area_emitter(position=(-1.3,6.0,2.5),power=65,size=2,
             target=(.0,6.5,1.0),color=(.94,.95,.88))
sc.view_settings.view_transform="Standard"
sc.view_settings.exposure=0
sc.view_settings.gamma=1
