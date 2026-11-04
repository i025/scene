from sceneact import *
import bpy

# Observations: the rendered berth's near upright is around x115 and reaches
# y388; the reference upright is nearer x150 and ends around y350. Its bedding
# also occupies too much foreground. Column and far equipment remain anchors.
# Hypothesis: the berth extends too far toward the camera. Revise only its
# longitudinal dimensions and attached parts; retain camera and other assets.
#
# Evidence/ownership ledger, approximate reference pixel bounds:
# Architecture: ceiling 0:384,0:175; floor 0:384,340:512; right bulkhead
# 290:384,90:351. Main two-tone column 264:309,0:435 occludes bulkhead.
# Berth 48:157,187:351: black frame, three pale mattress support surfaces.
# Left equipment 0:78,245:368 rests on cropped green shelf.
# Rear lockers 158:239,190:288; chair 162:202,270:340; utility cabinet
# 205:269,275:351 (identity uncertain). Rear pipes overlap these objects.
# Wall board 299:346,178:240; red emergency fixture 296:325,255:312.
# Right bench 307:384,388:512 and brown upright crop at right edge.
# Lamps and ceiling pipes overlap rear architecture; long berth/shelf edges
# recede rearward, while posts remain approximately vertical.
# Builders below use one semantic Asset per object, nested Parts for bedding.
# Architecture supports floor objects at z=0. Mattress support heights are
# explicit. Shelf equipment rests at z=.605; bench legs meet seat underside.
# No duplicate missing objects are added: the wall fixtures already exist
# and their current visibility is affected by column/bulkhead overlap.

scene = Scene("Shipboard compartment")
CAMERA_POSITION = (.05, -3.85, 1.64)
CAMERA_TARGET = (-.02, 3.8, 1.72)
CAMERA_LENS = 23.5

cream = (.59,.59,.46)
pale = (.70,.70,.60)
brown = (.28,.105,.065)
black = (.045,.055,.045)
green = (.075,.16,.125)
white = (.73,.74,.66)

def cube(owner, name, size, center, color):
    return owner.include(name, box(size, center=center, color=color))

def pipe(owner, name, a, b, radius=.025, color=cream):
    return owner.include(name, rod(radius=radius, start=a, end=b, color=color))

# Architecture owner; fixed room dimensions and beam anchors.
arch = Asset("architecture")
cube(arch,"floor",(5.4,11.6,.13),(0,1.8,-.065),(.32,.135,.087))
cube(arch,"left_wall",(.15,10.8,3.25),(-2.22,2,1.625),cream)
cube(arch,"far_wall",(4.5,.16,3.25),(0,6.3,1.625),cream)
cube(arch,"ceiling",(4.6,11.2,.15),(0,1.7,3.32),(.39,.36,.26))
cube(arch,"right_bulkhead",(1.58,.15,3.23),(1.78,3.35,1.615),pale)
cube(arch,"right_side",(.14,7,3.23),(2.51,2,1.615),cream)
cube(arch,"bulkhead_base",(1.58,.05,.23),(1.78,3.245,.115),brown)
for j,y in enumerate((-1.3,.9,3.15,5.5)):
    cube(arch,f"ceiling_beam_{j}",(4.5,.16,.28),(0,y,3.13),(.42,.30,.19))
for j,x in enumerate((-1.8,-.65,.6,1.8)):
    cube(arch,f"ceiling_longitudinal_{j}",(.105,10.4,.14),(x,1.8,3.14),(.45,.35,.23))
for j,y in enumerate((-.8,1.2,3.2,5.2)):
    cube(arch,f"floor_seam_{j}",(4.4,.012,.002),(0,y,.003),(.24,.105,.07))
scene.include("architecture",arch)

column = Asset("two tone structural column")
pipe(column,"brown_lower",(.94,.10,.03),(.94,.10,1.58),.105,brown)
pipe(column,"cream_upper",(.94,.10,1.58),(.94,.10,3.3),.105,(.65,.60,.43))
pipe(column,"foot_ring",(.94,.10,.015),(.94,.10,.055),.14,(.36,.24,.15))
scene.include("main_column",column)

post = Asset("cropped right post")
cube(post,"post",(.18,.22,3.3),(2.02,-1.65,1.65),brown)
scene.include("right_foreground_post",post)

# Revised semantic berth family: near end recedes, far end remains anchored.
# All rails, decks, mattresses and bedding use the same longitudinal bounds.
bunk = Asset("three tier berth")
BERTH_FRONT = 1.60
BERTH_BACK = 3.55
BERTH_LENGTH = BERTH_BACK - BERTH_FRONT
BERTH_CENTER = (BERTH_FRONT + BERTH_BACK) / 2
for i,x in enumerate((-2.02,-.91)):
    for j,y in enumerate((BERTH_FRONT,BERTH_BACK)):
        pipe(bunk,f"upright_{i}_{j}",(x,y,.07),(x,y,2.41),.026,black)
for level,z in enumerate((.57,1.12,1.67)):
    deck = Part(f"berth_level_{level}")
    cube(deck,"steel_deck",(1.1,BERTH_LENGTH-.05,.045),
         (-1.47,BERTH_CENTER,z),(.20,.24,.20))
    cube(deck,"mattress",(1.02,BERTH_LENGTH-.17,.115),
         (-1.47,BERTH_CENTER,z+.08),white)
    cube(deck,"folded_blanket",(1.025,.43,.055),
         (-1.47,BERTH_FRONT+.33,z+.165),(.57,.59,.51))
    cube(deck,"pillow",(.77,.43,.13),
         (-1.47,BERTH_BACK-.34,z+.2025),(.79,.78,.68))
    pipe(deck,"outer_edge",(-.91,BERTH_FRONT,z+.02),
         (-.91,BERTH_BACK,z+.02),.025,black)
    bunk.include(f"level_{level}",deck)
pipe(bunk,"top_side_rail",(-.91,BERTH_FRONT,1.98),(-.91,BERTH_BACK,1.98),.018,black)
pipe(bunk,"head_rail",(-2.02,BERTH_BACK,2.16),(-.91,BERTH_BACK,2.16),.023,black)
scene.include("left_bunk",bunk)

# Foreground shelf and its separately owned equipment.
shelf = Asset("left equipment shelf")
cube(shelf,"long_top",(.73,3,.07),(-1.95,-.9,.57),(.045,.12,.095))
cube(shelf,"front_lip",(.045,3,.11),(-1.56,-.9,.53),(.075,.12,.10))
for j,y in enumerate((-1.8,-.1)):
    pipe(shelf,f"support_{j}",(-2.17,y,.08),(-1.62,y,.55),.025,black)
scene.include("equipment_shelf",shelf)
for j,y in enumerate((-1.7,-.92,-.16)):
    machine = Asset(f"ventilated equipment {j}")
    cube(machine,"body",(.52,.64,.76),(-1.96,y,.985),green)
    cube(machine,"front_recess",(.025,.53,.61),(-1.685,y,.99),(.045,.065,.055))
    for k in range(15):
        cube(machine,f"louver_{k}",(.035,.49,.017),
             (-1.663,y,.715+k*.038),(.25,.31,.26))
    for k,yy in enumerate((y-.29,y+.29)):
        cube(machine,f"edge_trim_{k}",(.045,.035,.76),
             (-1.66,yy,.985),(.12,.19,.15))
    scene.include(f"green_equipment_{j}",machine)

vent = Asset("left wall ventilation box")
cube(vent,"case",(.23,.68,.73),(-2.055,.28,2.25),(.64,.63,.51))
cube(vent,"dark_opening",(.035,.52,.49),(-1.922,.28,2.25),(.055,.065,.055))
for k in range(6):
    cube(vent,f"slat_{k}",(.055,.53,.035),(-1.897,.28,2.04+k*.078),(.58,.59,.48))
scene.include("left_wall_vent",vent)

for j,x in enumerate((-.62,-.12,.38)):
    locker = Asset(f"gray locker {j}")
    cube(locker,"body",(.48,.58,1.64),(x,4.88,.96),(.43,.46,.42))
    cube(locker,"door",(.44,.035,1.53),(x,4.573,.98),(.49,.52,.47))
    cube(locker,"handle",(.035,.035,.13),(x+.14,4.544,1.03),(.18,.21,.18))
    for k in range(5):
        cube(locker,f"upper_vent_{k}",(.25,.014,.015),
             (x,4.548,1.43+k*.048),(.27,.31,.28))
    for k in range(3):
        cube(locker,f"lower_vent_{k}",(.25,.014,.014),
             (x,4.548,.45+k*.045),(.30,.34,.30))
    cube(locker,"foot",(.42,.49,.12),(x,4.88,.08),(.23,.26,.23))
    scene.include(f"rear_locker_{j}",locker)

storage = Asset("rear overhead storage")
cube(storage,"shelf",(1.7,.64,.045),(-.25,4.93,1.86),(.31,.34,.28))
for j in range(5):
    x = -.94+j*.34
    pipe(storage,f"roll_{j}",(x,4.70,2),(x,5.12,2),.13,(.56,.59,.51))
scene.include("rear_storage",storage)

chair = Asset("pale tubular chair")
cx,cy = -.10,3.10
for j,(x,y) in enumerate(((cx-.25,cy-.24),(cx+.25,cy-.24),
                          (cx-.25,cy+.24),(cx+.25,cy+.24))):
    pipe(chair,f"leg_{j}",(x,y,.02),(x,y,.50),.021,(.59,.60,.49))
cube(chair,"seat",(.54,.53,.065),(cx,cy,.51),(.40,.43,.33))
for j,x in enumerate((cx-.26,cx+.26)):
    pipe(chair,f"back_post_{j}",(x,cy+.23,.43),(x,cy+.29,1.02),.023,(.62,.64,.53))
    pipe(chair,f"arm_front_{j}",(x,cy-.15,.50),(x,cy-.15,.72),.019,(.62,.64,.53))
    pipe(chair,f"arm_rail_{j}",(x,cy-.15,.72),(x,cy+.25,.77),.021,(.62,.64,.53))
cube(chair,"back_pad",(.46,.07,.30),(cx,cy+.27,.86),(.37,.39,.30))
scene.include("chair",chair)

utility = Asset("dark utility cabinet")
cube(utility,"cabinet",(.76,.71,.89),(.75,3.48,.51),(.23,.26,.22))
cube(utility,"front_panel",(.64,.025,.70),(.75,3.107,.52),(.27,.29,.25))
cube(utility,"counter",(.84,.78,.075),(.75,3.48,.995),(.38,.40,.33))
cube(utility,"basin_dark",(.49,.43,.016),(.72,3.43,1.038),(.16,.19,.16))
pipe(utility,"faucet_vertical",(.99,3.68,1.04),(.99,3.68,1.31),.018,(.34,.36,.30))
pipe(utility,"faucet_spout",(.99,3.68,1.31),(.81,3.68,1.31),.018,(.34,.36,.30))
scene.include("utility_cabinet",utility)

service = Asset("exposed service pipework")
for j,x in enumerate((.30,.64,1.02)):
    pipe(service,f"riser_{j}",(x,4.2,.15),(x,4.2,2.78),.022,(.14,.17,.13))
for j,z in enumerate((.40,1.24,1.82,2.56)):
    pipe(service,f"crosspipe_{j}",(.30,4.2,z),(1.02,4.2,z),.021,(.18,.20,.16))
pipe(service,"black_overhead_horizontal",(-1.4,4.2,2.73),(1.02,4.2,2.73),.039,black)
scene.include("rear_pipe_frame",service)

board = Asset("dark wall board")
cube(board,"frame",(.85,.065,.79),(1.65,3.24,2.05),(.40,.40,.31))
cube(board,"face",(.77,.025,.71),(1.65,3.195,2.05),(.18,.23,.21))
scene.include("wall_board",board)

phone = Asset("red wall emergency fixture")
cube(phone,"backplate",(.31,.075,.56),(1.56,3.205,1.18),(.68,.075,.038))
phone.include("rounded_top",ball(.155,center=(1.56,3.205,1.42),color=(.70,.08,.045)))
cube(phone,"lower_cover",(.27,.11,.22),(1.56,3.14,1.06),(.73,.09,.045))
pipe(phone,"receiver_left",(1.49,3.095,1.22),(1.47,3.095,1.40),.035,(.85,.15,.08))
pipe(phone,"receiver_top",(1.47,3.095,1.40),(1.61,3.095,1.43),.038,(.88,.17,.09))
pipe(phone,"receiver_right",(1.61,3.095,1.43),(1.65,3.095,1.30),.035,(.85,.15,.08))
cube(phone,"label",(.10,.008,.07),(1.56,3.074,1.08),(.69,.44,.27))
scene.include("red_emergency_fixture",phone)

bench = Asset("right green bench")
cube(bench,"seat",(.61,1.75,.085),(1.80,-1.02,.54),(.045,.145,.10))
for i,x in enumerate((1.55,2.05)):
    for j,y in enumerate((-1.71,-.33)):
        pipe(bench,f"leg_{i}_{j}",(x,y,.02),(x,y,.50),.025,(.085,.12,.09))
pipe(bench,"lower_stretcher",(1.55,-1.71,.17),(1.55,-.33,.17),.021,green)
scene.include("right_bench",bench)

overhead = Asset("ceiling pipes and hangers")
pipe(overhead,"left_long_pipe",(-1.60,-2.8,2.84),(-1.60,5.8,2.84),.055,(.61,.63,.53))
pipe(overhead,"central_dark_pipe",(.06,-1.6,3.10),(.06,5.6,3.10),.047,(.13,.16,.13))
pipe(overhead,"rear_cross_pipe",(-2.1,3.8,2.65),(1.2,3.8,2.65),.045,(.29,.31,.25))
for j,y in enumerate((-1.7,.2,2.2)):
    pipe(overhead,f"diagonal_brace_{j}",(-1.95,y,3.2),(-1.23,y,2.62),.031,(.66,.63,.49))
    pipe(overhead,f"brace_tip_{j}",(-1.23,y,2.62),(-1.13,y,2.87),.025,(.66,.63,.49))
for j,x in enumerate((.65,.95,1.25)):
    pipe(overhead,f"back_ceiling_drop_{j}",(x,5.5,3.2),(x,5.5,2.66),.045,(.52,.53,.42))
scene.include("overhead_services",overhead)

lamp_locations = [(-.72,-.65,2.91),(-.48,2.18,2.74),(-.30,4.45,2.67)]
for j,(x,y,z) in enumerate(lamp_locations):
    lamp = Asset(f"hanging industrial lamp {j}")
    pipe(lamp,"stem",(x,y,z+.04),(x,y,3.22),.023,(.23,.25,.22))
    lamp.include("shade",rod(radius=.235 if j==0 else .18,length=.055,
                            center=(x,y,z),axis="+z",color=(.30,.34,.32)))
    lamp.include("white_diffuser",rod(radius=.215 if j==0 else .16,length=.018,
                            center=(x,y,z-.037),axis="+z",color=(.94,.96,.89)))
    scene.include(f"ceiling_lamp_{j}",lamp)

# All positive dimensions, distinct rod endpoints and unique sibling slots.
# No fillets are used. Geometry is complete before realization.
realize(scene)

for j in range(len(lamp_locations)):
    marker = bpy.data.objects.get(f"ceiling_lamp_{j}")
    if marker:
        meshes = [o for o in marker.children_recursive if o.type == "MESH"]
        assert meshes
        for ob in meshes:
            if ob.active_material and sum(ob.active_material.diffuse_color[:3]) > 2.5:
                ob.data = ob.data.copy()
                mat = ob.active_material.copy()
                ob.data.materials.clear()
                ob.data.materials.append(mat)
                mat.use_nodes = True
                bs = mat.node_tree.nodes.get("Principled BSDF")
                if bs:
                    bs.inputs["Emission Color"].default_value = (.91,.95,.88,1)
                    bs.inputs["Emission Strength"].default_value = 3

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.37,.39,.32,1)
world.node_tree.nodes["Background"].inputs[1].default_value = .35
area_emitter((-.7,-.5,2.82),power=160,size=1,target=(-.6,.4,.2),color=(1,.89,.72))
area_emitter((-.4,2.1,2.68),power=130,size=.75,target=(-.2,2.5,.4),color=(.86,.94,1))
area_emitter((-.2,4.5,2.60),power=110,size=.75,target=(0,4.5,.5),color=(.95,1,.89))
area_emitter((.2,-3,2.4),power=90,size=3,target=(0,2,1),color=(1,.91,.78))
sc = bpy.context.scene
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.view_settings.view_transform = "AgX"
