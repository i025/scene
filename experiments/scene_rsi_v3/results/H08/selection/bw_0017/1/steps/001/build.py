from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory and visual anchors, normalized image coordinates:
# - Dark roof and steel frame: (0,0)-(1,.42); long beams run nearly horizontally
#   and converge toward the right rear. Roof overlaps the machines and ducts.
# - Left wall and five bright vertical strip windows: (0,.30)-(.27,.65).
# - Stainless processing machines and raised decks: (.22,.30)-(.99,.77).
#   Main right machine has a tall rectangular silver body, dark horizontal mouth,
#   and a curved silver exhaust duct. More machinery is partly hidden behind rails.
# - Yellow platforms, guardrails, and diagonal stairs: (.06,.43)-(.97,.91).
#   Their horizontal rails cross in front of the machines; stairs descend toward us.
# - Green vertical tank: (.36,.53)-(.45,.77), in front of the central platform.
# - Blue and silver conveyor: (0,.72)-(.66,1), cropped by the bottom and left edges.
# - Green reflective floor: visible mainly at lower right and between the supports.
# Camera landmarks below are visual estimates; machine interiors and rear connections
# are partially occluded and their exact positions remain uncertain.
#
# Primitive budget: architecture ~40, machines/platforms ~50, railings/stairs ~105,
# ducts ~35, tank ~10, conveyors ~90, ancillary equipment ~15: approximately 345
# individual primitives. Tube paths use a small number of rods and balls.

scene = Scene("Workshop")

# Major dimensions and camera parameters are independent for later adjustments.
HALL_W, HALL_D, HALL_H = 15.0, 24.0, 7.0
CAM_POS = (11.5, -17.5, 8.1)
CAM_TARGET = (0.0, 2.0, 2.8)
CAM_LENS = 37

C = {
    "floor": (0.12, 0.34, 0.26),
    "wall": (0.19, 0.22, 0.23),
    "steel": (0.10, 0.12, 0.12),
    "roof": (0.20, 0.22, 0.21),
    "window": (0.72, 0.85, 0.88),
    "frame": (0.16, 0.17, 0.17),
    "silver": (0.58, 0.61, 0.60),
    "brightmetal": (0.72, 0.74, 0.72),
    "darkmetal": (0.27, 0.30, 0.29),
    "yellow": (0.95, 0.64, 0.025),
    "green": (0.025, 0.32, 0.23),
    "blue": (0.10, 0.30, 0.60),
    "black": (0.055, 0.065, 0.065),
    "white": (0.76, 0.79, 0.76),
}

def addbox(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def addrod(parent, name, a, b, radius, color):
    if sum((a[i]-b[i])**2 for i in range(3)) > 1e-10:
        parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def beam(parent, name, a, b, width, color):
    # Rectangular structural members may be represented by circular rods when diagonal.
    addrod(parent, name, a, b, width/2, color)

# Hall shell: the open camera-side end permits an unobstructed interior view.
hall = Asset("Hall_structure")
addbox(hall, "green_epoxy_floor", (HALL_W,HALL_D,.12), (0,2,-.06), C["floor"])
addbox(hall, "left_wall", (.16,HALL_D,HALL_H), (-7.5,2,3.5), C["wall"])
addbox(hall, "far_wall", (HALL_W,.16,HALL_H), (0,14,3.5), C["wall"])
addbox(hall, "roof_sheet", (HALL_W,HALL_D,.15), (0,2,7), C["roof"])
for i, y in enumerate([-9,-5,-1,3,7,11,14]):
    addbox(hall, "left_column_%d"%i, (.25,.25,7), (-7.32,y,3.5), C["steel"])
    addbox(hall, "roof_crossbeam_%d"%i, (14.8,.20,.25), (0,y,6.76), C["steel"])
    if i < 6:
        addbox(hall, "right_column_%d"%i, (.22,.22,7), (7.32,y,3.5), C["steel"])
for x in [-5,-2.5,0,2.5,5]:
    addbox(hall, "roof_purlin_%s"%x, (.12,24,.13), (x,2,6.82), C["steel"])
# Luminous panes set just inside the side wall; thin mullions give the strip pattern.
for i, y in enumerate([-8,-5.7,-3.4,-1.1,1.2,3.5,5.8,8.1,10.4,12.7]):
    addbox(hall, "window_%d"%i, (.055,.72,2.65), (-7.39,y,3.50), C["window"])
    addbox(hall, "window_mullion_%d"%i, (.07,.035,2.7), (-7.34,y,3.50), C["frame"])
    addbox(hall, "window_crossbar_%d"%i, (.07,.72,.035), (-7.33,y,3.25), C["frame"])
scene.include("architecture", hall)

# Elevated steel platforms, separate from machinery and guardrails.
platform = Asset("Raised_platforms")
addbox(platform, "main_deck", (10.3,4.5,.20), (.2,3.4,2.05), C["darkmetal"])
for x in [-4.7,-2.2,.5,3.1,5.1]:
    for y in [1.45,5.25]:
        addbox(platform, "support_%s_%s"%(x,y), (.15,.15,2), (x,y,1.0), C["darkmetal"])
addbox(platform, "front_edge", (10.5,.18,.25), (.2,1.1,2.0), C["silver"])
addbox(platform, "rear_edge", (10.5,.16,.22), (.2,5.65,2.0), C["darkmetal"])
scene.include("equipment_platforms", platform)

machines = Asset("Stainless_processing_machines")
# Large front-right machine, with a dark mouth and layered stainless fascias.
addbox(machines, "main_lower_body", (3.0,2.15,1.15), (2.65,3.2,2.66), C["silver"])
addbox(machines, "main_upper_body", (2.7,1.95,1.25), (2.65,3.25,3.78), C["silver"])
addbox(machines, "main_top_hood", (2.55,1.85,.30), (2.65,3.25,4.55), C["brightmetal"])
addbox(machines, "main_front_dark_opening", (2.40,.055,.42), (2.65,2.15,3.65), C["black"])
for z in [3.48,3.59,3.70,3.81]:
    addbox(machines, "main_opening_slat_%s"%z, (2.27,.07,.035), (2.65,2.10,z), C["silver"])
addbox(machines, "main_front_lower_panel", (2.8,.08,.45), (2.65,2.08,2.73), C["brightmetal"])
# Rear-left machinery appears as a second raised stainless housing.
addbox(machines, "left_machine_base", (2.2,1.8,1.15), (-3.0,4.05,2.68), C["silver"])
addbox(machines, "left_machine_head", (1.85,1.55,.7), (-3.0,4.05,3.60), C["brightmetal"])
addbox(machines, "left_machine_front", (1.9,.06,.35), (-3.0,3.12,2.96), C["darkmetal"])
addbox(machines, "center_machine", (2.0,1.7,1.45), (-.35,4.45,2.83), C["silver"])
addbox(machines, "center_machine_top", (1.9,1.5,.16), (-.35,4.45,3.63), C["brightmetal"])
# Right-hand tall control cabinet.
addbox(machines, "control_cabinet", (.75,.7,2.5), (5.1,4.9,3.32), C["white"])
addbox(machines, "control_screen", (.36,.04,.32), (5.1,4.53,3.70), C["darkmetal"])
scene.include("processing_machines", machines)

# Yellow railings: front runs have deliberate breaks where stairs attach.
rails = Asset("Yellow_platform_guardrails")
rail_z = [2.45,2.95,3.40]
for segment, (x0,x1) in enumerate([(-5.0,-3.6),(-1.75,1.0),(3.0,5.35)]):
    for z in rail_z:
        addrod(rails, "front_rail_%d_%s"%(segment,z), (x0,1.0,z),(x1,1.0,z),.035,C["yellow"])
    n = max(1, round((x1-x0)/.72))
    for i in range(n+1):
        x=x0+(x1-x0)*i/n
        addrod(rails, "front_post_%d_%d"%(segment,i), (x,1.0,2.12),(x,1.0,3.43),.037,C["yellow"])
for side,x in [("left",-5.0),("right",5.35)]:
    for z in rail_z:
        addrod(rails, side+"_side_rail_"+str(z),(x,1.0,z),(x,5.6,z),.032,C["yellow"])
    for i,y in enumerate([1.0,1.9,2.8,3.7,4.6,5.6]):
        addrod(rails, side+"_post_"+str(i),(x,y,2.12),(x,y,3.43),.035,C["yellow"])
for z in rail_z:
    addrod(rails, "rear_rail_"+str(z),(-5,5.6,z),(5.35,5.6,z),.03,C["yellow"])
for i,x in enumerate([-5,-4,-3,-2,-1,0,1,2,3,4,5.35]):
    addrod(rails, "rear_post_"+str(i),(x,5.6,2.1),(x,5.6,3.42),.033,C["yellow"])
scene.include("platform_guardrails", rails)

stairs = Asset("Access_stairs")
# Two flights descend toward the viewer, crossing the platform foreground.
def make_stair(label, xcenter):
    width=1.05
    bottom_y=-2.25
    top_y=1.05
    steps=9
    for i in range(steps):
        t=(i+.5)/steps
        y=bottom_y+(top_y-bottom_y)*t
        z=.12+2.0*t
        addbox(stairs, label+"_tread_%02d"%i,(width,.34,.07),(xcenter,y,z),C["silver"])
    for side in [-1,1]:
        x=xcenter+side*width*.55
        addrod(stairs,label+"_stringer_"+str(side),(x,bottom_y,.08),(x,top_y,2.10),.065,C["yellow"])
        addrod(stairs,label+"_handrail_"+str(side),(x,bottom_y,1.05),(x,top_y,3.12),.038,C["yellow"])
        for j in range(4):
            t=j/3
            y=bottom_y+(top_y-bottom_y)*t
            z=.10+2*t
            addrod(stairs,label+"_post_%s_%d"%(side,j),(x,y,z),(x,y,z+1.0),.03,C["yellow"])
make_stair("left_stair",-2.65)
make_stair("right_stair",2.0)
scene.include("stairs", stairs)

# Insulated duct routes are made with a few large segments and elbow junctions.
ducts = Asset("Insulated_ducts_and_process_pipes")
def ductpath(name, pts, radius):
    for i in range(len(pts)-1):
        addrod(ducts,name+"_segment_%d"%i,pts[i],pts[i+1],radius,C["brightmetal"])
    for i,p in enumerate(pts[1:-1]):
        ducts.include(name+"_elbow_%d"%i, ball(radius=radius,center=p,color=C["brightmetal"]))
ductpath("main_exhaust",[(2.65,3.7,4.6),(2.65,3.7,5.35),(2.65,4.25,5.85),(1.45,4.25,5.85)],.23)
ductpath("left_exhaust",[(-3,4.2,3.95),(-3,4.2,4.75),(-2.6,4.2,5.10),(-1.4,4.2,5.10),(-.8,4.2,4.3)],.19)
ductpath("back_process_pipe",[(-4.5,5.2,3.8),(-1.4,5.2,3.8),(.1,5.2,4.1),(3.7,5.2,4.1)],.13)
for x in [-3,0,3]:
    addrod(ducts,"hanger_"+str(x),(x,5.2,4.05),(x,5.2,6.75),.025,C["darkmetal"])
scene.include("ductwork", ducts)

# Floor-standing painted tank with rounded upper head, outlet and legs.
tank = Asset("Green_vertical_tank")
addrod(tank,"cylindrical_shell",(-1.3,-1.1,.42),(-1.3,-1.1,1.75),.50,C["green"])
tank.include("domed_top", ball(radius=.50,center=(-1.3,-1.1,1.75),color=C["green"]))
addrod(tank,"top_neck",(-1.3,-1.1,2.13),(-1.3,-1.1,2.32),.11,C["green"])
for i,(dx,dy) in enumerate([(-.30,-.22),(.30,-.22),(-.30,.22),(.30,.22)]):
    addbox(tank,"tank_leg_%d"%i,(.08,.08,.40),(-1.3+dx,-1.1+dy,.20),C["darkmetal"])
addrod(tank,"side_nozzle",(-.85,-1.1,1.15),(-.62,-1.1,1.15),.09,C["silver"])
scene.include("green_tank",tank)

# Foreground blue roller conveyor and silver framework. Its long direction leads
# from the lower left of the view toward the equipment, with open spaces underneath.
conveyor = Asset("Foreground_blue_roller_conveyors")
for line, (xcenter,width,y0,y1) in enumerate([(-3.6,2.0,-9.0,-3.0),(-.9,2.0,-8.4,-3.6),(1.75,1.75,-7.0,-3.6)]):
    for dx in [-width/2,width/2]:
        addbox(conveyor,"line%d_side_%s"%(line,dx),(.11,y1-y0,.18),(xcenter+dx,(y0+y1)/2,.95),C["brightmetal"])
        for yy in [y0+.4,(y0+y1)/2,y1-.4]:
            addbox(conveyor,"line%d_leg_%s_%s"%(line,dx,yy),(.10,.10,.87),(xcenter+dx,yy,.44),C["silver"])
    count=int((y1-y0)/.38)
    for i in range(count):
        y=y0+.19+i*.38
        addrod(conveyor,"line%d_blue_roller_%02d"%(line,i),(xcenter-width/2+.06,y,1.02),(xcenter+width/2-.06,y,1.02),.055,C["blue"])
    addbox(conveyor,"line%d_underframe"%line,(width,.12,.12),(xcenter,(y0+y1)/2,.50),C["darkmetal"])
    addbox(conveyor,"line%d_motor"%line,(.35,.42,.32),(xcenter+width/2+.22,y1-.8,.64),C["darkmetal"])
# Silver transverse transfer belt and its visible frame.
addbox(conveyor,"transfer_bed",(6.7,1.1,.16),(-1.1,-3.25,1.03),C["white"])
for x in [-4.1,-2.8,-1.5,-.2,1.1,2.1]:
    addbox(conveyor,"transfer_support_"+str(x),(.10,.10,.95),(x,-3.25,.49),C["silver"])
scene.include("conveyors", conveyor)

# Small equipment at the right rear, visible between the guardrail and wall.
ancillary = Asset("Rear_equipment")
addbox(ancillary,"rear_cabinet",(1.25,1.0,1.8),(5.9,8.4,.9),C["white"])
addbox(ancillary,"rear_machine",(2.0,1.3,1.1),(3.2,9.4,.55),C["silver"])
for x in [2.5,3.2,3.9]:
    addrod(ancillary,"rear_pipe_"+str(x),(x,9.4,1.1),(x,9.4,2.25),.09,C["silver"])
scene.include("rear_equipment",ancillary)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.67,0.75,0.78,1)
background.inputs["Strength"].default_value = .55

# Adjust the shared material only where all objects with that finish have the same
# intended response. A copied material is assigned to the selected mesh subset.
def tune_by_color(label, rgb, metallic, roughness):
    selected=[]
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            mat=slot.material
            if not mat or not mat.use_nodes:
                continue
            bsdf=mat.node_tree.nodes.get("Principled BSDF")
            if not bsdf:
                continue
            col=bsdf.inputs["Base Color"].default_value
            if sum(abs(col[i]-rgb[i]) for i in range(3)) < .035:
                selected.append((obj,slot,mat))
    copies={}
    for obj,slot,mat in selected:
        key=mat.name
        if key not in copies:
            copied=mat.copy()
            copied.name=label+"_surface"
            node=copied.node_tree.nodes.get("Principled BSDF")
            node.inputs["Metallic"].default_value=metallic
            node.inputs["Roughness"].default_value=roughness
            copies[key]=copied
        slot.material=copies[key]
    print("MATERIAL",label,"meshes",len(selected),"metallic",metallic,"roughness",roughness,
          "assigned",",".join(m.name for m in copies.values()))
tune_by_color("epoxy_floor",C["floor"],0.0,.20)
tune_by_color("stainless_equipment",C["silver"],.72,.30)
tune_by_color("bright_insulated_metal",C["brightmetal"],.80,.22)
tune_by_color("painted_green_tank",C["green"],.18,.34)
tune_by_color("painted_yellow_rail",C["yellow"],.16,.38)

# Daylight from the window side and broad overhead fill.
area_emitter((-5,-3,6.2),power=1800,size=7,target=(0,2,1.5),color=(.82,.91,1))
area_emitter((1,3,6.4),power=1700,size=8,target=(0,2,1),color=(1,.98,.94))
area_emitter((5,-5,5.8),power=900,size=6,target=(0,2,2),color=(1,1,1))

# Use the image aspect for both projection checks and the active camera.
sc.render.resolution_x=3840
sc.render.resolution_y=2003
sc.render.resolution_percentage=100
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS)

# Geometry landmarks, reference UV estimates in image coordinates (x right, y down).
# They are tentative correspondences and do not prove visibility or silhouette.
landmarks=[
    ("left window top",(-7.34,-1.1,4.825),(.16,.34)),
    ("main machine top",(1.375,2.325,4.70),(.62,.30)),
    ("tank top",(-1.3,-1.1,2.25),(.40,.54)),
    ("front conveyor corner",(-4.6,-8.6,1.04),(.08,.94)),
]
def projected(p):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
                               scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    return None if clip.w <= 1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
print("LANDMARK reference_uv projected_uv")
for name,p,ref in landmarks:
    uv=projected(p)
    print(name,ref,tuple(round(v,3) for v in uv) if uv else None)

# Leave final rendering and saving to the managed runner.
try:
    sc.view_settings.view_transform="AgX"
except Exception:
    pass
