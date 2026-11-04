from sceneact import *
import bpy

# Evidence ledger: reference estimates refer to the classroom inset only.
# Reference: island x~.33-.84,y~.52-.95; round rug partly behind/below it;
# rear windows occupy upper background; left cabinets recede toward the sill.
# Step 2 visibly returned a valid image. Coordinates below are visual estimates:
# near island x~.35-.87,y~.60->1.0, with its lower shelf cropped;
# far window row x~.40->1.0,y~.07-.43; left shelf x~.02-.40,y~.47-.84.
# Reference island is completely readable; step 2 over-enlarges the near owner.
# Window sill and island edges slope down to the right in both images.
# Left shelves remain visible, with negative spaces; no absent object is inferred.
# Dominant surfaces are paler and shadows softer than the reference, but this
# revision holds appearance fixed to isolate the stronger foreground framing issue.
#
# Chosen family: camera only. Retreat moderately and aim slightly lower.
# Prediction: complete island base and more rug become visible, rear windows
# become modestly smaller; architecture, supports, materials and lights stay fixed.
# Far-window lateral alignment remains uncertain and is not claimed calibrated.

CAMERA = dict(position=(2.6, -6.2, 3.0),
              target=(-.45, 1.1, .85), lens=31)
ROOM = dict(width=7.4, depth=7.0, height=3.25, back=4.2, front=-2.8)

WOOD = (.62, .43, .22)
LIGHT_WOOD = (.76, .59, .34)
EDGE = (.68, .49, .26)
BACKING = (.49, .36, .20)
CREAM = (.87, .85, .73)
FLOOR = (.68, .49, .31)
RED = (.39, .065, .045)
WHITE = (.90, .88, .75)
GREEN = (.22, .36, .14)
BLUE = (.10, .32, .43)
YELLOW = (.89, .65, .16)

scene = Scene("Montessori_classroom")

# Ownership/support mapping:
# room: floor, wall returns, ceiling, baseboards; fixed architectural owner.
# window_i: glazing/frame/sill at rear opening; exterior: distant geometry.
# cabinet slots: cabinet() builds attached sides/back/boards/toes, floor z=0.
# table/stool slots: attached tops/aprons/legs, floor z=0.
# rug: two concentric thin discs, floor-supported, island is its near occluder.
# tray slots: tray() owns rims and contents; explicit z is the board support plane.
# stacking_material: attached tower tiers supported at island top z=.98.
# plant slots: pot/stem/leaves supported at specified cabinet top.
# wall_display: attached frame/paper/cards at back wall, uncertain exact placement.
# Relative scale uses child furniture; ceiling height and rear inventory uncertain.

architecture = Asset("room")
architecture.include("floor", box((7.6,7.2,.12),(0,.7,-.06),FLOOR))
architecture.include("left_wall", box((.16,7,3.25),(-3.78,.7,1.625),CREAM))
architecture.include("back_lower", box((7.4,.16,1.10),(0,4.28,.55),CREAM))
architecture.include("back_upper", box((7.4,.16,.37),(0,4.28,3.065),CREAM))
architecture.include("ceiling", box((7.5,7.1,.10),(0,.7,3.30),(.91,.90,.82)))
architecture.include("back_baseboard", box((7.4,.035,.10),(0,4.175,.05),EDGE))
architecture.include("left_baseboard", box((.035,7,.10),(-3.68,.7,.05),EDGE))
architecture.include("right_return", box((.16,1.65,3.25),(3.78,3.375,1.625),CREAM))
scene.include("room", architecture)

window_centers = [-2.95,-1.48,0,1.48,2.95]
for i,x in enumerate(window_centers):
    window = Asset("rear_window")
    w,bottom,top = 1.27,1.10,2.88
    window.include("glass",box((w,.025,top-bottom),
                              (x,4.285,(bottom+top)/2),(.70,.82,.79),opacity=.30))
    for j,xx in enumerate((x-w/2,x+w/2)):
        window.include(f"jamb_{j}",box((.065,.16,top-bottom+.08),
                                     (xx,4.19,(bottom+top)/2),WHITE))
    for j,zz in enumerate((bottom,top)):
        window.include(f"rail_{j}",box((w+.10,.16,.065),(x,4.19,zz),WHITE))
    window.include("meeting_rail",box((w,.06,.045),(x,4.16,2.02),WHITE))
    window.include("sill",box((w+.15,.30,.065),(x,4.10,1.085),LIGHT_WOOD))
    scene.include(f"window_{i}",window)
    if i < 4:
        architecture.include(f"window_pier_{i}",box(
            (.20,.16,1.80),((x+window_centers[i+1])/2,4.28,1.99),CREAM))

outside = Asset("daylight_view")
outside.include("sky",box((12,.08,5),(0,6.2,2.5),(.78,.87,.89)))
outside.include("ground",box((12,2,.08),(0,5.25,.50),(.48,.57,.29)))
for i,x in enumerate([-3.6,-2.1,-.4,1.1,2.7,3.8]):
    outside.include(f"trunk_{i}",rod(.055,start=(x,5.5,.5),
                                   end=(x+.12,5.5,3.4),color=(.39,.38,.28)))
    crown = ball(.65,center=(x,5.5,2.65),color=(.43,.57,.28))
    crown.resize((.85,.45,1.35))
    outside.include(f"foliage_{i}",crown)
scene.include("exterior",outside)

def cabinet(slot,position,size,bays=2,levels=2,angle=0):
    w,d,h = size
    x,y,z = position
    a = Asset(slot)
    t = .055
    for key,zz in (("bottom",z+.10),("top",z+h-t/2)):
        a.include(key,box((w,d,t),(x,y,zz),LIGHT_WOOD))
    for j,xx in enumerate((x-w/2+t/2,x+w/2-t/2)):
        a.include(f"end_{j}",box((t,d,h-.10),(xx,y,z+(h+.10)/2),WOOD))
    a.include("back",box((w-.10,.035,h-.15),
                         (x,y+d/2-.025,z+(h+.10)/2),BACKING))
    for j in range(1,levels):
        zz = z+.10+(h-.13)*j/levels
        a.include(f"shelf_{j}",box((w-.08,d-.015,t),(x,y,zz),LIGHT_WOOD))
    for j in range(1,bays):
        xx = x-w/2+w*j/bays
        a.include(f"divider_{j}",box((t,d-.04,h-.15),
                                    (xx,y,z+(h+.10)/2),WOOD))
    for j,xx in enumerate((x-w*.38,x+w*.38)):
        a.include(f"toe_{j}",box((.11,d*.78,.10),(xx,y,z+.05),WOOD))
    if angle:
        a.turn('z',angle,pivot=(x,y,z))
    return scene.include(slot,a)

cabinet("foreground_island",(.55,-.45,0),(2.65,.95,.98),3,2)
cabinet("left_mid_shelf",(-2.65,1.03,0),(1.95,.63,.90),3,2,90)
cabinet("left_front_shelf",(-3.05,-.50,0),(1.35,.60,.82),2,2,90)
cabinet("back_left_shelf",(-2.30,3.66,0),(2.25,.64,.83),3,2)
cabinet("back_middle_shelf",(.20,3.68,0),(1.70,.60,.82),2,2)
cabinet("right_back_shelf",(2.82,3.35,0),(1.35,.58,.88),2,2)
cabinet("right_side_shelf",(3.03,1.05,0),(1.35,.58,.85),2,2,90)

rug = Asset("round_red_rug")
rug.include("woven_disc",rod(1.65,length=.018,center=(.55,-.55,.014),
                             axis='+z',color=RED))
rug.include("inner_field",rod(1.48,length=.005,center=(.55,-.55,.026),
                              axis='+z',color=(.46,.10,.065)))
scene.include("rug",rug)

def activity_table(slot,x,y,w,d,h):
    a = Asset(slot)
    a.include("top",box((w,d,.065),(x,y,h-.0325),LIGHT_WOOD))
    a.include("apron_front",box((w-.12,.05,.12),(x,y-d/2+.07,h-.12),WOOD))
    a.include("apron_back",box((w-.12,.05,.12),(x,y+d/2-.07,h-.12),WOOD))
    for i,xx in enumerate((x-w/2+.09,x+w/2-.09)):
        for j,yy in enumerate((y-d/2+.09,y+d/2-.09)):
            a.include(f"leg_{i}_{j}",box((.075,.075,h-.065),
                                       (xx,yy,(h-.065)/2),WOOD))
    scene.include(slot,a)

def stool(slot,x,y):
    a = Asset(slot)
    a.include("seat",rod(.21,length=.055,center=(x,y,.335),color=LIGHT_WOOD))
    for i,dx in enumerate((-.13,.13)):
        for j,dy in enumerate((-.13,.13)):
            a.include(f"leg_{i}_{j}",box((.045,.045,.307),
                                       (x+dx,y+dy,.1535),WOOD))
    scene.include(slot,a)

activity_table("center_activity_table",.30,1.92,1.45,.85,.59)
activity_table("right_activity_table",2.25,2.25,1.15,.75,.59)
for i,(x,y) in enumerate([(-.58,1.92),(.15,2.57),(.45,1.25),
                          (2.25,1.58),(2.85,2.35)]):
    stool(f"stool_{i}",x,y)

def tray(slot,x,y,z,w=.40,d=.26,contents="blocks"):
    a = Asset(slot)
    a.include("base",box((w,d,.025),(x,y,z+.0125),LIGHT_WOOD))
    for i,yy in enumerate((y-d/2,y+d/2)):
        a.include(f"rim_long_{i}",box((w,.018,.045),(x,yy,z+.035),EDGE))
    for i,xx in enumerate((x-w/2,x+w/2)):
        a.include(f"rim_end_{i}",box((.018,d,.045),(xx,y,z+.035),EDGE))
    if contents == "blocks":
        for i,c in enumerate((RED,BLUE,YELLOW)):
            h = .055+i*.016
            a.include(f"block_{i}",box((.065,.065,h),
                                      (x+(i-1)*.095,y,z+.025+h/2),c))
    elif contents == "bowls":
        for i in range(2):
            a.include(f"bowl_{i}",rod(.066,length=.045,
                      center=(x+(i-.5)*.16,y,z+.0475),color=WHITE))
    elif contents == "box":
        a.include("wooden_box",box((w*.65,d*.63,.09),(x,y,z+.07),WOOD))
        a.include("lid",box((w*.69,d*.67,.012),(x,y,z+.121),LIGHT_WOOD))
    scene.include(slot,a)

for i,x in enumerate([-.38,.45,1.30]):
    tray(f"island_top_tray_{i}",x,-.46,.98,.49,.33,
         ("blocks","bowls","box")[i])
for level,z in enumerate((.1275,.5525)):
    for j,x in enumerate([-.35,.53,1.40]):
        tray(f"island_shelf_tray_{level}_{j}",x,-.68,z,.50,.30,
             "box" if (level+j)%2 else "blocks")
for i,x in enumerate([-3.02,-2.28,-1.56]):
    tray(f"rear_shelf_material_{i}",x,3.62,.83,.45,.28,
         "box" if i == 1 else "blocks")
for i,x in enumerate([-.22,.58]):
    tray(f"middle_rear_material_{i}",x,3.60,.82,.43,.26,"bowls")
tray("table_work",.28,1.92,.59,.46,.30,"blocks")
tray("right_table_work",2.24,2.25,.59,.42,.28,"box")
tray("right_cabinet_material",2.85,3.30,.88,.45,.28,"blocks")

tower = Asset("stacking_material")
for i in range(5):
    side = .145-i*.018
    tower.include(f"tier_{i}",box((side,side,.045),
                                (.98,-.22,1.0025+i*.045),(.61,.23,.16)))
scene.include("stacking_material",tower)

def plant(slot,x,y,z):
    a = Asset(slot)
    a.include("pot",rod(.10,length=.16,center=(x,y,z+.08),color=(.63,.32,.16)))
    a.include("stem",rod(.012,start=(x,y,z+.16),end=(x,y,z+.43),color=GREEN))
    for i,(dx,dy,dz) in enumerate([(-.12,0,.30),(.12,.02,.35),(0,.08,.43)]):
        leaf = ball(.11,center=(x+dx,y+dy,z+dz),color=GREEN)
        leaf.resize((1,.50,.60))
        a.include(f"leaves_{i}",leaf)
    scene.include(slot,a)

plant("back_left_plant",-3.10,3.65,.83)
plant("back_right_plant",3.12,3.34,.88)

display = Asset("classroom_wall_display")
display.include("frame",box((.48,.04,.65),(1.35,4.16,1.65),WOOD))
display.include("paper",box((.42,.012,.59),(1.35,4.132,1.65),WHITE))
for i in range(3):
    display.include(f"card_{i}",box((.25,.008,.08),
                                   (1.35,4.12,1.48+i*.15),(.52,.60,.37)))
scene.include("wall_display",display)

# Inline pre-execution review:
# Inventory and whole-owner dimensions/poses remain unchanged from step 2.
# Seven cabinets, five windows, two tables, five stools, rug and loose materials.
# Explicit tabletop/shelf support planes retained; no exposure-driven relocations.
# Approx. 315 primitives; tray rims/contents are the largest decorative family.
# No expanded fillets/sweeps; curved rug/stool outlines use individual rods.
# Dimensions positive/finite; endpoints distinct; include slots unique per parent.
# Camera near anchor: island base/rug; mid: left cabinets; far: window sill.
# Review is predictive, not a collision or structural-test certification.
# Realize precedes camera/world/lights; no geometry is made afterward.
# Known semantic markers and nonempty mesh descendants are checked below.
# Shader construction reproduces prior global palette setup; no local recoloring.
# Runner-owned render, sample, resolution and save settings remain untouched.

realize(scene)

wood_slots = [
    "foreground_island","left_mid_shelf","left_front_shelf",
    "back_left_shelf","back_middle_shelf","right_back_shelf",
    "right_side_shelf","center_activity_table","right_activity_table"
]
processed = set()
for slot in wood_slots:
    marker = bpy.data.objects.get(slot)
    assert marker is not None, "Missing semantic marker: "+slot
    meshes = [o for o in marker.children_recursive if o.type == 'MESH']
    assert meshes, "Empty semantic owner: "+slot
    for obj in meshes:
        for ms in obj.material_slots:
            mat = ms.material
            if mat is None or mat.as_pointer() in processed:
                continue
            processed.add(mat.as_pointer())
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Roughness"].default_value = .78
                nodes,links = mat.node_tree.nodes,mat.node_tree.links
                tex = nodes.new("ShaderNodeTexNoise")
                tex.inputs["Scale"].default_value = 7
                tex.inputs["Detail"].default_value = 2
                coord = nodes.new("ShaderNodeTexCoord")
                mapping = nodes.new("ShaderNodeVectorMath")
                mapping.operation = 'MULTIPLY'
                mapping.inputs[1].default_value = (1.5,28,5)
                links.new(coord.outputs["Generated"],mapping.inputs[0])
                links.new(mapping.outputs["Vector"],tex.inputs["Vector"])
                bump = nodes.new("ShaderNodeBump")
                bump.inputs["Strength"].default_value = .10
                bump.inputs["Distance"].default_value = .018
                links.new(tex.outputs["Fac"],bump.inputs["Height"])
                links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])

set_view(**CAMERA)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.78,.85,.91,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .48
area_emitter((0,3.9,2.7),power=1050,size=5.2,
             target=(0,-.6,.1),color=(1,.94,.81))
area_emitter((1,-2.2,3.05),power=230,size=4.5,
             target=(0,1.2,.3),color=(1,.97,.90))
