from sceneact import *
import bpy
import math
import random

# Reference inventory, approximate normalized image bounds:
# Architecture: carpet (0,.59)-(1,1), back wall (.11,.38)-(.53,.61),
# right wall (.52,0)-(1,.83), ceiling (0,0)-(1,.39), luminous left
# glazing (0,.32)-(.12,.67). Hidden room extents remain uncertain.
# Whiteboard (.59,.26)-(.91,.58): two white areas, aluminum frame/tray.
# Flag (.45,.32)-(.51,.43): diagonal pole, blue canton, hanging stripes.
# Back fixtures: vent (.15,.44)-(.25,.48), electrical opening
# (.30,.46)-(.34,.51), diagonal loose cover (.31,.48)-(.39,.54),
# two small plates. Ceiling includes grid, lights, detector, dark openings.
# Floor: broken gray panels (0,.64)-(.40,.80), thin center strips,
# yellow insulation (.56,.67)-(.90,.79), long tracks at lower right,
# and small fragments. These map to named assets and child meshes below.
#
# Feedback comparison: back floor corner was close, but the left window
# wall was outside frame, board was too narrow, and debris was displaced
# left. Camera now sits farther left and lower, preserving the back corner.
# Ceiling height, board far edge, flag height, and nearest debris adjusted.
# Expanded estimate: approximately 165 boxes and 5 rods, under 190 meshes.
# No booleans, fillets, dense repeated microgeometry, rendering, or saving.

random.seed(18)
scene = Scene("Damaged vacant classroom")
BEIGE=(.66,.635,.56)
CEILING=(.59,.62,.62)
GRID=(.47,.50,.50)
BASE=(.045,.061,.057)
SILVER=(.51,.55,.54)

def cube(parent,name,size,center,color,rotation=None):
    n=box(size=size,center=center,color=color)
    if rotation:
        n.turn(euler=rotation)
    parent.include(name,n)
    return n

architecture=Asset("room_architecture")
cube(architecture,"carpet_floor",(4.5,10.4,.10),(-.35,2.5,-.05),(.09,.105,.09))
cube(architecture,"back_plaster",(4.3,.12,2.40),(-.35,7.08,1.20),BEIGE)
cube(architecture,"right_plaster",(.12,10.4,2.40),(1.86,2,1.20),(.70,.675,.60))
cube(architecture,"back_baseboard",(4.3,.045,.105),(-.35,7.005,.052),BASE)
cube(architecture,"right_baseboard",(.045,10.4,.105),(1.785,2,.052),BASE)
scene.include("architecture",architecture)

windows=Asset("bright_left_window_wall")
cube(windows,"glazing",(.045,9.7,2.40),(-2.48,2.2,1.20),(.88,.93,.94))
for j,y in enumerate([-1.8,-.2,1.4,3,4.6,6.2]):
    cube(windows,"mullion_%d"%j,(.07,.023,2.40),(-2.445,y,1.20),(.72,.77,.78))
cube(windows,"horizontal_seam",(.07,9.7,.018),(-2.44,2.2,1.02),(.75,.80,.80))
scene.include("left_windows",windows)

ceiling=Asset("suspended_ceiling")
cz=2.40
cube(ceiling,"tile_surface",(4.3,10.5,.065),(-.35,2,cz+.035),CEILING)
for i in range(9):
    cube(ceiling,"long_grid_%02d"%i,(.010,10.5,.009),
         (-2.45+.535*i,2,cz-.005),GRID)
for j in range(19):
    cube(ceiling,"cross_grid_%02d"%j,(4.3,.010,.009),
         (-.35,-3+.56*j,cz-.005),GRID)
for k,y in enumerate([3.2,3.76,4.88,5.44,6.56]):
    cube(ceiling,"missing_tile_%d"%k,(.51,.535,.016),
         (-2.17,y,cz-.016),(.025,.040,.040))
    cube(ceiling,"exposed_rail_%d"%k,(.43,.028,.024),
         (-2.17,y+.10,cz-.035),(.24,.28,.27))
for k,(x,y,sx,sy) in enumerate([
    (-1.35,2.10,.50,1.07),(-1.35,4.34,.50,1.07),
    (-1.35,6.02,.50,.52),(-1.35,-.70,.50,1.07)]):
    cube(ceiling,"light_rim_%d"%k,(sx+.035,sy+.035,.027),
         (x,y,cz-.026),(.48,.53,.53))
    cube(ceiling,"diffuser_%d"%k,(sx,sy,.014),
         (x,y,cz-.045),(.76,.81,.82))
ceiling.include("detector_base",rod(.065,length=.025,
    center=(-1.05,.6,cz-.045),color=(.74,.75,.70)))
ceiling.include("detector_cap",rod(.043,length=.025,
    center=(-1.05,.6,cz-.069),color=(.71,.72,.67)))
scene.include("ceiling",ceiling)

board=Asset("two_section_whiteboard")
y0,y1=2.55,5.65
z0,z1=.99,2.27
cube(board,"white_surface",(.032,y1-y0,z1-z0),
     (1.766,(y0+y1)/2,(z0+z1)/2),(.76,.79,.79))
for name,y in [("near_frame",y0),("far_frame",y1)]:
    cube(board,name,(.047,.025,z1-z0+.055),(1.741,y,(z0+z1)/2),SILVER)
for name,z in [("upper_frame",z1),("lower_frame",z0)]:
    cube(board,name,(.047,y1-y0+.035,.025),(1.741,(y0+y1)/2,z),SILVER)
cube(board,"section_divider",(.037,.013,z1-z0),(1.738,4.63,(z0+z1)/2),(.60,.64,.63))
cube(board,"marker_tray",(.075,y1-y0,.018),(1.715,(y0+y1)/2,z0-.025),SILVER)
for k,y in enumerate([2.69,5.45]):
    cube(board,"mount_%d"%k,(.045,.045,.065),(1.74,y,2.30),(.42,.46,.45))
scene.include("whiteboard",board)

fixtures=Asset("back_wall_service_fixtures")
# Vent proportions reduced vertically to match the shallow reference grille.
cube(fixtures,"vent_recess",(.87,.025,.34),(-1.62,6.997,1.55),(.27,.32,.32))
for i,x in enumerate([-2.065,-1.175]):
    cube(fixtures,"vent_side_%d"%i,(.025,.027,.36),(x,6.975,1.55),(.48,.51,.48))
for i,z in enumerate([1.37,1.73]):
    cube(fixtures,"vent_edge_%d"%i,(.91,.027,.022),(-1.62,6.975,z),(.48,.51,.48))
for i in range(5):
    cube(fixtures,"vent_louver_%d"%i,(.82,.015,.010),
         (-1.62,6.963,1.42+i*.065),(.34,.39,.38))
cube(fixtures,"electrical_rim",(.31,.05,.38),(-.39,6.97,1.34),(.47,.51,.48))
cube(fixtures,"electrical_opening",(.235,.022,.315),(-.39,6.932,1.34),(.10,.15,.15))
cube(fixtures,"internal_component",(.065,.035,.23),(-.39,6.91,1.36),(.60,.62,.57))
cube(fixtures,"internal_wire",(.024,.03,.23),(-.47,6.903,1.32),(.20,.23,.20))
cover=cube(fixtures,"diagonal_loose_cover",(.43,.045,.36),(-.11,6.81,1.04),(.36,.42,.40))
cover.turn(axis="+y",degrees=42)
cube(fixtures,"cover_fastener",(.026,.012,.027),(-.12,6.776,1.08),(.15,.21,.20))
for i,x in enumerate([.23,.48]):
    cube(fixtures,"wall_plate_%d"%i,(.14,.024,.20),(x,6.985,1.14),(.77,.76,.69))
    cube(fixtures,"switch_%d"%i,(.035,.015,.063),(x,6.964,1.15),(.43,.46,.42))
scene.include("back_fixtures",fixtures)

flag=Asset("hanging_American_flag")
flag.include("diagonal_pole",rod(.010,start=(1.78,6.20,2.20),
    end=(.91,6.18,2.64),color=(.20,.22,.19)))
for i in range(13):
    x=.965+i*.032
    top=2.62-(x-.94)*.57
    bottom=1.86+(x-.94)*.12
    color=(.53,.045,.035) if i%2==0 else (.80,.79,.72)
    cube(flag,"folded_stripe_%02d"%i,(.033,.018,top-bottom),
         (x,6.15+math.sin(i*1.5)*.017,(top+bottom)/2),color)
cube(flag,"blue_canton",(.205,.026,.275),(1.025,6.126,2.425),(.055,.09,.13))
for row in range(4):
    for col in range(3):
        cube(flag,"star_%d_%d"%(row,col),(.009,.008,.009),
             (.95+.054*col,6.108,2.33+.055*row),(.77,.78,.72))
scene.include("flag",flag)

debris=Asset("fallen_gray_ceiling_material")
def panel(name,center,size,angle,color,tilt=0):
    return cube(debris,name,size,center,color,(tilt,0,angle))

panel("foreground_broken_panel",(-.40,2.87,.035),(1.26,.55,.035),-11,(.25,.28,.25),2)
panel("foreground_light_face",(-.53,2.88,.060),(.80,.43,.018),8,(.35,.37,.32),-2)
panel("foreground_overlap",(-.15,2.94,.075),(.58,.35,.016),-18,(.18,.21,.19),3)
panel("left_midground_tile",(-1.04,3.91,.024),(1,.43,.027),-17,(.32,.35,.30),1)
panel("left_midground_overlap",(-1.30,4.05,.045),(.68,.30,.024),7,(.25,.28,.25),-3)
panel("back_tile",(-.94,5.19,.025),(.86,.36,.026),12,(.25,.28,.24),1)
panel("back_pale_fragment",(-1.15,5.11,.045),(.31,.21,.016),-12,(.47,.48,.39))
panel("center_metal_strip",(-.03,3.45,.045),(1.43,.033,.025),-9,(.61,.65,.63))
panel("center_second_strip",(-.13,3.49,.047),(.89,.019,.021),-12,(.76,.78,.72))
panel("right_long_track",(1.62,1.65,.033),(.055,2.20,.025),-20,(.64,.66,.61))
panel("right_parallel_track",(1.83,1.59,.040),(.045,2.16,.024),-20,(.70,.71,.66))
panel("right_channel",(1.64,1.64,.050),(.013,2.12,.010),-20,(.28,.32,.30))
for i in range(14):
    panel("small_fragment_%02d"%i,
          (random.uniform(-1.85,1.65),random.uniform(1,6.5),.012),
          (random.uniform(.025,.11),random.uniform(.018,.075),.012),
          random.uniform(-80,80),
          random.choice([(.43,.44,.37),(.30,.33,.29),(.57,.55,.43)]))
scene.include("floor_debris",debris)

insulation=Asset("yellow_fallen_insulation")
cube(insulation,"rear_slab",(1.05,.91,.10),(1.13,3.44,.12),(.59,.46,.16),(0,-7,-7))
cube(insulation,"front_panel",(1.10,.84,.065),(1.28,2.91,.155),(.63,.50,.17),(13,-5,-7))
cube(insulation,"fibrous_edge",(.90,.045,.105),(1.08,3,.085),(.68,.59,.31),(0,-7,-7))
cube(insulation,"small_flap",(.31,.63,.035),(.74,3.02,.12),(.59,.48,.20),(5,-10,-7))
scene.include("yellow_debris",insulation)

outlets=Asset("right_wall_outlets")
for i,y in enumerate([1.80,5.43]):
    cube(outlets,"plate_%d"%i,(.018,.105,.15),(1.785,y,.66),(.68,.66,.55))
    cube(outlets,"socket_%d"%i,(.009,.018,.043),(1.771,y,.67),(.39,.39,.32))
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
background.inputs["Strength"].default_value=.23

mat=bpy.data.materials.new("dark_commercial_carpet")
mat.use_nodes=True
nodes=mat.node_tree.nodes
links=mat.node_tree.links
bsdf=nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value=.98
tex=nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value=145
tex.inputs["Detail"].default_value=2
ramp=nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.18
ramp.color_ramp.elements[0].color=(.030,.038,.032,1)
ramp.color_ramp.elements[1].position=.82
ramp.color_ramp.elements[1].color=(.105,.116,.092,1)
links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
bump=nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.15
bump.inputs["Distance"].default_value=.009
links.new(tex.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
for obj in bpy.data.objects:
    if obj.type=="MESH" and obj.dimensions.x>4 and obj.location.z<.01:
        obj.data.materials.clear()
        obj.data.materials.append(mat)

set_view(position=(-.45,-.40,1.52),target=(1.57,7,.96),lens=26.7,sensor=36)
area_emitter(position=(-2.15,2,2.05),power=315,size=4.5,
             target=(.6,4,.9),color=(.86,.93,1))
area_emitter(position=(-.6,3,2.30),power=70,size=3,
             target=(.3,3.5,0),color=(.95,.96,.90))
area_emitter(position=(-1.3,6,2.25),power=40,size=2,
             target=(0,6.5,1),color=(.94,.95,.88))
sc.view_settings.view_transform="Standard"
sc.view_settings.exposure=0
sc.view_settings.gamma=1
