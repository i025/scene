# Reference inventory and normalized image estimates, 512 x 267:
# Hall: dark ceiling and beams across x=0..1, y=0..0.35; left wall with
# vertical windows at x=0..0.23, y=0.33..0.66. Green floor at lower right.
# Large right stainless machine: x=.61..80, y=.30..72; front opening and
# insulated duct above. Left machine: x=.23..43, y=.36..66; center machinery
# and connections are partly hidden. Yellow platform rails span x=.10.. .95,
# y=.43.. .70. Three stair runs descend toward the foreground.
# Green vessel: x=.36.. .45, y=.53.. .78, partly overlapped by conveyors.
# Blue and pale conveyor frames occupy x=0.. .72, y=.70..1.00.
# Roof and platform edges are nearly horizontal; stair rails slope downward
# toward the camera. Unseen machine connections and distant equipment remain
# uncertain.
#
# Comparison with the previous successful view:
# 1. The camera was outside and above the roof: roof exterior covered the upper
#    image and gray background appeared. The reference is inside the hall.
#    Lowering the camera below roof level and aiming more horizontally should
#    put the ceiling overhead and move foreground features downward.
# 2. The platform occupied about x=.25.. .78 in the rendering versus roughly
#    x=.10.. .95 in the reference. A longer lens and closer camera should
#    enlarge the equipment and reduce the large empty floor region.
# 3. Tank top projected at (.358,.491), versus estimated (.405,.53); platform
#    endpoints projected at (.257,.479) and (.767,.551), versus (.12,.57)
#    and (.89,.58). Their differing residuals indicate both framing and
#    local proportion differences; the viewpoint change also reduces the
#    overly steep platform edge. The stairs in the render stop much higher
#    than the reference; lowering the view should move their feet down.
# 4. Foreground conveyor anchor projected at (-.045,.761), versus (.02,.94);
#    it was partly cropped and the foreground had too much exposed floor.
#    The new camera changes its apparent location; extra transfer framing is
#    added only where the photograph shows overlapping pale equipment.
# The previous numerical points describe geometry, not visible coverage:
# tank bottom and conveyor corners can be occluded; the left platform anchor
# is a deck corner rather than the leftmost handrail. The roof is present but
# was viewed from outside, so it is retained rather than duplicated.
#
# Approximate expanded count: hall 75, platforms/stairs 145, machines 49,
# ductwork 22, tank 8, conveyor and transfer equipment 100; total ~399 meshes.
# Each box, ball and rod is one mesh; no booleans or fillet expansion.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

IMAGE_WIDTH, IMAGE_HEIGHT = 512, 267
ROOM_W, ROOM_D, ROOM_H = 21.0, 25.0, 7.2
PLATFORM_Z = 2.55
CAMERA_POSITION = (4.5, -17.5, 5.35)
CAMERA_TARGET = (0.0, 3.0, 3.05)
CAMERA_LENS = 40.0

steel = (.07, .085, .08)
roof = (.23, .24, .22)
wall = (.22, .24, .23)
silver = (.55, .59, .58)
light_silver = (.75, .78, .76)
dark_metal = (.16, .19, .18)
yellow = (.95, .61, .015)
green = (.015, .35, .25)
floor_green = (.08, .31, .23)
blue = (.035, .20, .50)
window = (.73, .85, .90)

scene = Scene("Workshop")

def b(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def r(parent, name, a, c, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=c, color=color))

hall = Asset("Steel_frame_hall")
b(hall, "green_epoxy_floor", (ROOM_W, ROOM_D, .12), (0, 3, -.06), floor_green)
b(hall, "roof_sheet", (ROOM_W, ROOM_D, .16), (0, 3, ROOM_H), roof)
b(hall, "left_wall", (.18, ROOM_D, 6.9), (-ROOM_W/2, 3, 3.45), wall)
b(hall, "far_wall", (ROOM_W, .18, 6.9), (0, 15.4, 3.45), wall)

for j, y in enumerate((-8, -3, 2, 7, 12, 15)):
    for side, x in enumerate((-10.25, 10.25)):
        b(hall, "column_web_%d_%d" % (j, side), (.20, .25, 7.0),
          (x, y, 3.5), steel)
        b(hall, "column_flange_%d_%d" % (j, side), (.48, .08, 7.0),
          (x, y, 3.5), steel)
    b(hall, "roof_crossbeam_%d" % j, (20.7, .28, .36),
      (0, y, 6.91), steel)
for i, x in enumerate((-8, -4, 0, 4, 8)):
    b(hall, "roof_purlin_%d" % i, (.16, 24.5, .16), (x, 3, 6.96), steel)
for i, y in enumerate((-7, -4.4, -1.8, .8, 3.4, 6, 8.6, 11.2, 13.8)):
    b(hall, "window_glazing_%d" % i, (.035, .92, 2.55),
      (-10.38, y, 3.05), window)
    for k, z in enumerate((1.76, 3.05, 4.34)):
        b(hall, "window_crossbar_%d_%d" % (i,k), (.055, 1.0, .055),
          (-10.34, y, z), dark_metal)
    for k, dy in enumerate((-.49,.49)):
        b(hall, "window_jamb_%d_%d" % (i,k), (.055,.055,2.65),
          (-10.34, y+dy, 3.05), dark_metal)
scene.include("building", hall)

platform = Asset("Operating_platforms")
b(platform, "main_deck", (15.3,3.0,.20), (-.2,4.1,PLATFORM_Z), silver)
b(platform, "deck_front_fascia", (15.3,.12,.35),
  (-.2,2.56,PLATFORM_Z-.12), dark_metal)
for i, x in enumerate((-7.4,-4.7,-1.9,1.0,3.8,6.9)):
    for j, y in enumerate((2.8,5.3)):
        b(platform, "support_%d_%d" % (i,j), (.17,.17,2.45),
          (x,y,1.22), dark_metal)
        b(platform, "foot_%d_%d" % (i,j), (.42,.42,.08),
          (x,y,.04), silver)
for k, (x0,x1) in enumerate(((-7.7,-5.0),(-3.8,-.8),(.8,4.3),(5.5,7.4))):
    for j, z in enumerate((3.12,3.65)):
        r(platform, "front_rail_%d_%d" % (k,j),
          (x0,2.48,z), (x1,2.48,z), .035, yellow)
    count = max(1, int((x1-x0)/1.1))
    for i in range(count+1):
        x = x0+(x1-x0)*i/count
        r(platform, "front_post_%d_%d" % (k,i),
          (x,2.48,2.62), (x,2.48,3.67), .032, yellow)
for j,z in enumerate((3.12,3.65)):
    r(platform, "rear_rail_%d" % j, (-7.8,5.58,z), (7.4,5.58,z), .035, yellow)
for i in range(15):
    x = -7.8+i*15.2/14
    r(platform, "rear_post_%d" % i, (x,5.58,2.62), (x,5.58,3.65), .03, yellow)

def stair(name, x, yfront, yback, width):
    for i in range(9):
        t = (i+.5)/9
        y = yfront+(yback-yfront)*t
        z = .12+(PLATFORM_Z-.12)*t
        b(platform, name+"_tread_%d" % i, (width,.32,.07), (x,y,z), light_silver)
    for side in (-1,1):
        xx = x+side*width*.54
        r(platform, name+"_stringer_%d" % side,
          (xx,yfront,.12), (xx,yback,PLATFORM_Z), .065, silver)
        r(platform, name+"_handrail_%d" % side,
          (xx,yfront,1.12), (xx,yback,PLATFORM_Z+1.03), .04, yellow)
        r(platform, name+"_midrail_%d" % side,
          (xx,yfront,.62), (xx,yback,PLATFORM_Z+.53), .027, yellow)
        for i in range(4):
            t = i/3
            y = yfront+(yback-yfront)*t
            z = .12+(PLATFORM_Z-.12)*t
            r(platform, name+"_post_%d_%d" % (side,i),
              (xx,y,z), (xx,y,z+1.03), .032, yellow)
stair("middle_stair",0,-.6,2.55,1.05)
stair("right_stair",5,-.6,2.55,1.05)
stair("left_stair",-4.4,-.15,2.55,.95)
scene.include("platforms_and_stairs",platform)

machines = Asset("Stainless_processing_machines")
def machine(name,x,y,width,depth,height):
    base = PLATFORM_Z+.12
    b(machines,name+"_frame",(width,depth,.26),(x,y,base+.13),dark_metal)
    for i,dx in enumerate((-width*.39,width*.39)):
        b(machines,name+"_pedestal_%d" % i,(.25,depth*.87,.7),
          (x+dx,y,base+.50),silver)
    b(machines,name+"_main_body",(width,depth,height*.64),
      (x,y,base+.7+height*.32),silver)
    b(machines,name+"_top_hood",(width*.93,depth*.95,height*.27),
      (x,y,base+.7+height*.77),light_silver)
    front = y-depth/2-.012
    b(machines,name+"_process_opening",(width*.78,.035,height*.24),
      (x,front,base+.7+height*.50),dark_metal)
    for k in range(5):
        z = base+.7+height*.39+k*height*.052
        b(machines,name+"_louver_%d" % k,(width*.77,.04,.035),
          (x,front-.025,z),light_silver)
    for i,dx in enumerate((-width*.44,width*.44)):
        b(machines,name+"_front_border_%d" % i,(.09,.08,height*.64),
          (x+dx,front-.025,base+.7+height*.32),light_silver)
machine("large_right_machine",3.5,4.35,3.4,1.8,2.0)
machine("left_machine",-4.7,4.45,2.7,1.65,1.55)
machine("center_machine",-.9,5.0,2.35,1.4,1.20)
b(machines,"far_right_cabinet",(1.25,1.2,2.25),(7.6,6.7,1.13),light_silver)
b(machines,"far_right_control",(.60,.08,.55),(7.6,6.06,1.6),dark_metal)
scene.include("machines",machines)

ducts = Asset("Insulated_ducts_and_pipework")
def duct(name,points,radius=.24):
    for i in range(len(points)-1):
        r(ducts,name+"_segment_%d" % i,points[i],points[i+1],radius,light_silver)
    for i,p in enumerate(points[1:-1]):
        ducts.include(name+"_elbow_%d" % i,ball(radius=radius,center=p,color=light_silver))
duct("right_exhaust",[(3.6,4.4,5.15),(3.6,4.4,5.9),
                      (3.3,4.4,6.22),(2.5,4.4,6.22)],.26)
duct("left_exhaust",[(-4.7,4.45,4.87),(-4.7,4.45,5.65),
                     (-4.35,4.45,5.95),(-3.2,4.45,5.85),
                     (-2.6,4.45,5.55),(-2.15,4.45,4.95)],.23)
duct("horizontal_process_pipe",[(-7.4,5,4.45),(-5.9,5,4.45),
                                (-5.5,5,4.1),(-1,5,4.1)],.12)
duct("right_side_pipe",[(5.35,4.7,4.5),(6,4.7,4.5),
                         (6,4.7,3.1),(7.6,4.7,3.1)],.12)
for i,x in enumerate((-5,-2.2,2.5,4,6)):
    r(ducts,"overhead_hanger_%d" % i,(x,4.4,6.1),(x,4.4,6.85),.028,dark_metal)
scene.include("ductwork",ducts)

tank = Asset("Green_vertical_tank")
tx,ty = -3.0,.1
r(tank,"cylindrical_shell",(tx,ty,.40),(tx,ty,2.65),.58,green)
tank.include("upper_dome",ball(radius=.58,center=(tx,ty,2.65),color=green))
tank.include("lower_dome",ball(radius=.58,center=(tx,ty,.40),color=green))
for i,(dx,dy) in enumerate(((-.37,-.26),(.37,-.26),(0,.40))):
    b(tank,"foot_%d" % i,(.12,.12,.42),(tx+dx,ty+dy,.21),dark_metal)
r(tank,"top_nozzle",(tx,ty,3.05),(tx,ty,3.42),.09,silver)
r(tank,"side_nozzle",(tx+.48,ty,1.8),(tx+.86,ty,1.8),.09,silver)
scene.include("green_tank",tank)

conveyors = Asset("Foreground_roller_conveyors")
def conveyor(name,x,y,length,width):
    z=.85
    b(conveyors,name+"_blue_bed",(length,width,.10),(x,y,z),blue)
    for side in (-1,1):
        b(conveyors,name+"_side_rail_%d" % side,(length,.10,.18),
          (x,y+side*width*.5,z+.06),light_silver)
    for j in range(11):
        xx=x-length/2+(j+.5)*length/11
        r(conveyors,name+"_roller_%d" % j,
          (xx,y-width*.46,z+.09),(xx,y+width*.46,z+.09),.035,light_silver)
    for j,dx in enumerate((-length*.42,0,length*.42)):
        for side in (-1,1):
            b(conveyors,name+"_leg_%d_%d" % (j,side),(.09,.09,.79),
              (x+dx,y+side*width*.39,.40),silver)
        b(conveyors,name+"_crossbrace_%d" % j,(.08,width*.85,.07),
          (x+dx,y,.25),silver)
    b(conveyors,name+"_drive_motor",(.35,.33,.28),
      (x+length*.32,y+width*.64,.62),dark_metal)
conveyor("front_line",-3.5,-6.6,11.5,1.25)
conveyor("middle_line",-2.0,-4.25,10.5,1.10)
conveyor("short_line",2.6,-2.4,5.3,1.0)
b(conveyors,"transfer_frame",(3.6,1.5,.18),(-.3,-3.15,1.02),light_silver)
for i,dx in enumerate((-1.5,1.5)):
    b(conveyors,"transfer_leg_%d" % i,(.12,.12,.90),(-.3+dx,-3.15,.45),silver)
b(conveyors,"foreground_guard",(2.2,.12,.62),(-.3,-4.1,1.20),light_silver)
for i,x in enumerate((-2.0,-.8,.4,1.6,2.8)):
    b(conveyors,"junction_crossbar_%d" % i,(.08,2.2,.08),(x,-2.9,1.1),light_silver)
scene.include("conveyors",conveyors)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.72,.80,.84,1)
background.inputs["Strength"].default_value = .65

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    p = mat.node_tree.nodes.get("Principled BSDF")
    if not p:
        continue
    c = p.inputs["Base Color"].default_value
    if c[0] > .5 and abs(c[0]-c[1]) < .12:
        p.inputs["Metallic"].default_value = .62
        p.inputs["Roughness"].default_value = .34
    elif c[1] > c[0]*1.3 and c[1] > .2:
        p.inputs["Metallic"].default_value = .15
        p.inputs["Roughness"].default_value = .23
    else:
        p.inputs["Roughness"].default_value = .48

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-8,-2,6.1),power=2200,size=8,target=(0,3,1.5))
area_emitter((1,2,6.8),power=1600,size=8,target=(0,2,0))
area_emitter((6,-4,6.5),power=1000,size=7,target=(1,3,2))

# Project identified features with the actual camera matrix. The small lens
# perturbations provide a numerical framing comparison without a render.
anchors = [
    ("tank_top",(tx,ty,3.23),(.405,.53)),
    ("tank_bottom",(tx,ty,0.0),(.405,.78)),
    ("main_machine_top_left",(1.92,3.45,5.18),(.62,.30)),
    ("main_machine_top_right",(5.08,3.45,5.18),(.79,.30)),
    ("platform_front_left",(-7.85,2.56,2.65),(.12,.57)),
    ("platform_front_right",(7.45,2.56,2.65),(.89,.58)),
    ("front_conveyor_left",(-9.25,-7.225,.95),(.02,.94)),
    ("right_stair_foot",(5.0,-.6,.12),(.80,.94)),
]
cam = sc.camera
depsgraph = bpy.context.evaluated_depsgraph_get()

def projected_rows():
    bpy.context.view_layer.update()
    projection = cam.calc_matrix_camera(
        depsgraph,x=IMAGE_WIDTH,y=IMAGE_HEIGHT,scale_x=1,scale_y=1)
    view = cam.matrix_world.inverted()
    result=[]
    for name,xyz,ref in anchors:
        clip = projection @ view @ Vector((xyz[0],xyz[1],xyz[2],1))
        if clip.w <= 0:
            result.append(
                '{"name":"%s","reference":[%.4f,%.4f],'
                '"projection":null,"residual":null,"behind_camera":true}'
                % (name,ref[0],ref[1]))
        else:
            u=.5*(clip.x/clip.w+1)
            v=.5*(1-clip.y/clip.w)
            result.append(
                '{"name":"%s","reference":[%.4f,%.4f],'
                '"projection":[%.4f,%.4f],"residual":[%.4f,%.4f],'
                '"behind_camera":false}'
                % (name,ref[0],ref[1],u,v,u-ref[0],v-ref[1]))
    return result

for trial_lens in (38.0,42.0):
    cam.data.lens = trial_lens
    print("CAMERA_LENS_TRIAL %.1f [%s]" % (trial_lens,",".join(projected_rows())))
cam.data.lens = CAMERA_LENS
print("ANCHOR_DIAGNOSTIC ["+",".join(projected_rows())+"]")
