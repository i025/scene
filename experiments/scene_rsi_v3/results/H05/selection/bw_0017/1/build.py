# Reference versus second render, estimated normalized image coordinates:
# 1. The reference has bright strip windows at x=0.00–0.23, y=0.34–0.65;
#    the render has mostly dark, barely visible strips at x=0.00–0.22.
#    The chosen window-top point in the prior projection was off-frame, so
#    its correspondence was uncertain rather than evidence of a camera error.
# 2. Reference ceiling occupies roughly y=0.00–0.33 with several horizontal
#    dark beams. The render ceiling is a shallow dark band above y=0.20.
# 3. Reference main housing occupies about x=0.61–0.79, y=0.30–0.62;
#    the render housing is roughly x=0.57–0.77, y=0.34–0.53. Its large
#    blank face lacks the reference's dark processing slot and lower structure.
# 4. Reference tank occupies x=0.36–0.45, y=0.53–0.77; render tank is about
#    x=0.32–0.39, y=0.58–0.79. Its top needs to move upward and slightly right.
# 5. The reference foreground contains pale open transfer frames from about
#    x=0.00–0.65, y=0.70–1.00; the render has a broad uninterrupted blue
#    area largely below y=0.82. The light frames should reach farther upward.
# 6. Reference stairs have strong diagonal outlines, especially at right;
#    the rendered right stair is almost vertical. The reference has open dark
#    gaps under its platform, while the render shows a broad empty green area.
#
# Corrections ranked by extent and contrast: brighten the window panes and
# make the ceiling structure legible; add the pale foreground transfer frame
# and open machine understructure; adjust the stair direction and tank.
# Raising the ceiling panel's visible brightness and adding narrow roof-light
# strips affects the upper image without moving equipment. Moving TX right
# and raising the tank shell moves its silhouette right and up. Moving transfer
# frames farther toward the platform and increasing their height brings their
# far edges upward. Angling the stair run sideways moves its foot left of its
# top. These are local geometry changes; the camera remains close to the
# previously rendered camera, since its machine and platform anchors are near
# their estimates and a global shift would disturb those anchors.
# Brightness is controlled by both material and lighting. Window panes use a
# restrained emissive component to represent daylight; ceiling lights supplement
# the window-facing area light. Rear equipment and pipe connections are uncertain.
#
# Inventory: steel-frame hall, roof, purlins and side windows; green epoxy floor;
# raised steel decks, three processing units, ducts and hangers; yellow rails
# and three stair flights; green vessel; blue roller conveyor and pale transfer
# frames; a cabinet and service pipes. The conveyor hides the tank base; rails
# overlap machines. Roof and platform edges are nearly horizontal; stairs are
# diagonal and columns vertical. The conveyor is cropped at the bottom and left.
#
# Expanded primitive estimate: hall 95, platform/rails 68, machines 40,
# ductwork 23, stairs 72, vessel 10, conveyor/transfer 100, services 6:
# approximately 414 separate meshes. No Boolean or fillet expansion.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene("Production hall")
W, D, H = 17.0, 30.0, 6.8
PZ = 2.05
MX, MY = 3.0, 2.25
TX, TY, TR = -0.95, -2.0, 0.56
CAM_POS = (5.0, -16.5, 5.25)
CAM_TARGET = (0.0, 1.6, 2.85)
CAM_LENS = 37.0

dark = (0.075, 0.09, 0.09)
wall = (0.22, 0.24, 0.23)
roof = (0.30, 0.31, 0.29)
green = (0.055, 0.26, 0.17)
steel = (0.59, 0.63, 0.62)
lightsteel = (0.78, 0.80, 0.77)
midsteel = (0.35, 0.39, 0.38)
black = (0.055, 0.065, 0.065)
yellow = (0.95, 0.65, 0.015)
tankcolor = (0.008, 0.32, 0.20)
blue = (0.055, 0.25, 0.55)
glass = (0.70, 0.83, 0.92)
rooflight = (0.68, 0.71, 0.66)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def rail(parent, name, a, b, base, height=0.95, posts=5):
    ax, ay = a
    bx, by = b
    R(parent, name+"_top", (ax, ay, base+height),
      (bx, by, base+height), .028, yellow)
    R(parent, name+"_mid", (ax, ay, base+height*.52),
      (bx, by, base+height*.52), .022, yellow)
    for i in range(posts):
        t = i/(posts-1)
        x, y = ax+(bx-ax)*t, ay+(by-ay)*t
        R(parent, name+"_post_%d"%i, (x,y,base),
          (x,y,base+height), .025, yellow)

# Hall, with I-section columns assembled from webs and flanges.
hall = Asset("steel_frame_hall")
B(hall, "epoxy_floor", (W,D,.14), (0,-3,-.07), green)
B(hall, "left_wall", (.16,D,H), (-W/2,-3,H/2), wall)
B(hall, "back_wall", (W,.16,H), (0,12,H/2), wall)
B(hall, "roof_sheet", (W,D,.13), (0,-3,H), roof)
for i,y in enumerate((-15,-10,-5,0,5,10,11.8)):
    for side in (-1,1):
        x = side*(W/2-.18)
        B(hall, "column_web_%d_%d"%(i,side), (.15,.28,H),
          (x,y,H/2), dark)
        for k,dx in enumerate((-.16,.16)):
            B(hall, "column_flange_%d_%d_%d"%(i,side,k), (.08,.44,H),
              (x+dx,y,H/2), dark)
    B(hall, "cross_beam_%d"%i, (W,.24,.28), (0,y,H-.30), dark)
for i,x in enumerate((-7,-4,-1,2,5,8)):
    B(hall, "purlin_%d"%i, (.11,D,.12), (x,-3,H-.18), dark)
for i,y in enumerate((-12,-9.7,-7.4,-5.1,-2.8,-.5,1.8,4.1,6.4,8.7,11)):
    # This face sits just inside the wall surface.
    B(hall, "daylight_pane_%d"%i, (.04,.72,2.55),
      (-W/2+.105,y,3.1), glass)
    B(hall, "window_mullion_%d"%i, (.05,.035,2.55),
      (-W/2+.14,y,3.1), dark)
    for j,z in enumerate((2.1,3.1,4.1)):
        B(hall, "window_crossbar_%d_%d"%(i,j), (.06,.73,.035),
          (-W/2+.15,y,z), midsteel)
for i,x in enumerate((-5.5,0,5.5)):
    B(hall, "ceiling_light_strip_%d"%i, (.22,7.0,.035),
      (x,0,H-.11), rooflight)
scene.include("hall", hall)

platform = Asset("operating_platform")
B(platform, "deck", (10.8,3.5,.16), (.1,2.0,PZ), midsteel)
for i,x in enumerate((-5.2,-3.1,-1.0,1.1,3.2,5.4)):
    for j,y in enumerate((.32,3.68)):
        B(platform, "leg_%d_%d"%(i,j), (.14,.14,PZ),
          (x,y,PZ/2), midsteel)
B(platform, "front_beam", (10.8,.15,.24), (.1,.25,1.90), steel)
B(platform, "rear_beam", (10.8,.15,.24), (.1,3.75,1.90), midsteel)
rail(platform,"front_left",(-5.25,.22),(-1.0,.22),PZ+.08,posts=6)
rail(platform,"front_right",(-.15,.22),(5.45,.22),PZ+.08,posts=8)
rail(platform,"left_side",(-5.25,.22),(-5.25,3.75),PZ+.08,posts=4)
rail(platform,"right_side",(5.45,.22),(5.45,3.75),PZ+.08,posts=4)
rail(platform,"rear",(-5.25,3.75),(5.45,3.75),PZ+.08,posts=9)
scene.include("platform", platform)

machines = Asset("stainless_processing_machines")
B(machines,"main_base",(3.3,1.95,.40),(MX,MY,2.37),midsteel)
B(machines,"main_body",(3.3,1.85,1.02),(MX,MY,3.10),steel)
B(machines,"front_opening",(2.85,.045,.43),(MX,MY-.94,3.25),black)
B(machines,"opening_inner",(2.61,.04,.25),(MX,MY-.97,3.24),midsteel)
B(machines,"opening_upper_lip",(3.0,.12,.08),(MX,MY-1.00,3.49),lightsteel)
B(machines,"opening_lower_lip",(3.1,.17,.10),(MX,MY-1.00,3.01),lightsteel)
B(machines,"upper_head",(3.15,1.65,.65),(MX,MY,3.94),lightsteel)
B(machines,"upper_cap",(2.85,1.45,.13),(MX,MY,4.32),steel)
B(machines,"lower_ledge",(3.5,.25,.12),(MX,MY-1.00,2.70),lightsteel)
for i in range(6):
    x = MX-1.22+i*.49
    B(machines,"front_divider_%d"%i,(.035,.045,.28),
      (x,MY-1.00,3.24),steel)
R(machines,"indicator_rim",(MX,MY-.84,4.0),(MX,MY-.90,4.0),.11,midsteel)
R(machines,"indicator",(MX,MY-.91,4.0),(MX,MY-.94,4.0),.058,tankcolor)
# Open chassis beneath the machine creates the dark gaps and cross-members.
for i,x in enumerate((MX-1.45,MX-.5,MX+.5,MX+1.45)):
    B(machines,"chassis_post_%d"%i,(.10,.12,.80),(x,1.24,1.65),steel)
for i,z in enumerate((1.38,1.80)):
    B(machines,"chassis_cross_%d"%i,(3.15,.12,.10),(MX,1.24,z),midsteel)
for i,(x,y,w) in enumerate(((-4.1,2.5,1.45),(-2.2,2.7,1.55),(-.45,2.85,1.55))):
    B(machines,"aux_body_%d"%i,(w,1.4,.92),(x,y,2.75),steel)
    B(machines,"aux_head_%d"%i,(w*.87,1.22,.46),(x,y,3.42),lightsteel)
    B(machines,"aux_front_%d"%i,(w*.78,.035,.25),(x,y-.72,2.83),midsteel)
    B(machines,"aux_base_%d"%i,(w+.12,1.52,.13),(x,y,2.23),midsteel)
scene.include("machines", machines)

ducts = Asset("insulated_ducts")
def pipe(name, points, radius):
    for i in range(len(points)-1):
        R(ducts,name+"_segment_%d"%i,points[i],points[i+1],radius,lightsteel)
    for i,p in enumerate(points[1:-1]):
        ducts.include(name+"_elbow_%d"%i,
                      ball(radius=radius,center=p,color=lightsteel))
pipe("main_duct",[(MX,2.8,4.3),(MX,2.8,4.85),(MX+.18,2.8,5.05),
                  (MX+.78,2.8,5.05),(MX+.96,2.8,4.85),(MX+.96,2.8,4.35)],.17)
pipe("left_duct",[(-4.1,2.7,3.6),(-4.1,2.7,4.25),(-3.9,2.7,4.43),
                  (-3.0,2.7,4.43),(-2.8,2.7,4.22),(-2.8,2.7,3.7)],.14)
pipe("process_run",[(-2.8,3.0,3.8),(-1.0,3.0,3.8),(.45,3.0,3.7)],.11)
for i,x in enumerate((-3.5,3.5)):
    R(ducts,"hanger_%d"%i,(x,2.8,5.04),(x,2.8,6.55),.025,midsteel)
scene.include("ducts", ducts)

def staircase(name,x0,x1,yt,yb,n,foot_dx):
    stair = Asset(name)
    for i in range(n):
        t=(i+.5)/n
        xshift=foot_dx*(1-t)
        B(stair,"tread_%d"%i,(x1-x0,abs(yt-yb)/n*.80,.06),
          ((x0+x1)/2+xshift,yb+(yt-yb)*t,PZ*t),lightsteel)
    for k,x in enumerate((x0,x1)):
        R(stair,"stringer_%d"%k,(x+foot_dx,yb,.05),(x,yt,PZ),.055,midsteel)
        R(stair,"top_rail_%d"%k,(x+foot_dx,yb,.95),(x,yt,PZ+.95),.028,yellow)
        R(stair,"mid_rail_%d"%k,(x+foot_dx,yb,.51),(x,yt,PZ+.51),.022,yellow)
        for j in range(5):
            t=j/4
            xx=x+foot_dx*(1-t)
            y=yb+(yt-yb)*t
            z=.05+(PZ-.05)*t
            R(stair,"post_%d_%d"%(k,j),(xx,y,z),(xx,y,z+.95),.025,yellow)
    scene.include(name,stair)

staircase("left_stair",-5.2,-4.25,.3,-2.8,9,-.6)
staircase("middle_stair",-.9,.05,.3,-2.65,9,-.6)
staircase("right_stair",5.25,6.35,.3,-3.6,10,-1.0)

tank = Asset("green_pressure_tank")
R(tank,"shell",(TX,TY,.42),(TX,TY,2.18),TR,tankcolor)
tank.include("top_head",ball(radius=TR,center=(TX,TY,2.16),color=tankcolor))
tank.include("bottom_head",ball(radius=TR,center=(TX,TY,.44),color=tankcolor))
for i,(dx,dy) in enumerate(((-.32,-.24),(.32,-.24),(-.32,.24),(.32,.24))):
    B(tank,"foot_%d"%i,(.10,.10,.44),(TX+dx,TY+dy,.22),midsteel)
R(tank,"neck",(TX,TY,2.65),(TX,TY,2.80),.085,steel)
R(tank,"flange",(TX,TY,2.75),(TX,TY,2.80),.14,midsteel)
R(tank,"side_nozzle",(TX+.46,TY,1.65),(TX+.72,TY,1.65),.07,steel)
scene.include("tank",tank)

conv = Asset("foreground_conveyor_and_transfer")
for j,y in enumerate((-7.5,-6.35,-5.2)):
    B(conv,"blue_belt_%d"%j,(10.0,.83,.10),(-2.2,y,.95),blue)
    for side in (-1,1):
        yy=y+side*.48
        B(conv,"edge_%d_%d"%(j,side),(10,.08,.17),(-2.2,yy,1.04),lightsteel)
        for i,x in enumerate((-6.0,-3.0,0.0,2.3)):
            B(conv,"leg_%d_%d_%d"%(j,side,i),(.09,.09,.94),(x,yy,.47),steel)
    for i in range(11):
        x=-6.6+i*.9
        R(conv,"roller_%d_%d"%(j,i),(x,y-.4,1.03),(x,y+.4,1.03),.025,lightsteel)

# Parallel pale transfer tracks extend towards the tank and overlap its base.
for i,y in enumerate((-4.8,-4.1,-3.4,-2.7)):
    for s in (-1,1):
        B(conv,"transfer_rail_%d_%d"%(i,s),(5.5,.065,.16),
          (.35,y+s*.27,1.42),lightsteel)
    for j in range(8):
        x=-2.0+j*.65
        R(conv,"transfer_roller_%d_%d"%(i,j),(x,y-.24,1.43),
          (x,y+.24,1.43),.035,steel)
for i,x in enumerate((-1.9,.1,2.5)):
    B(conv,"transfer_cross_%d"%i,(.10,3.0,.10),(x,-3.75,1.32),lightsteel)
    for j,y in enumerate((-4.95,-2.55)):
        B(conv,"transfer_support_%d_%d"%(i,j),(.10,.10,1.30),
          (x,y,.65),steel)
B(conv,"transfer_side_housing",(1.6,.25,.72),(2.4,-4.9,1.05),lightsteel)
B(conv,"motor",(.50,.36,.34),(3.25,-4.3,.65),midsteel)
scene.include("conveyor",conv)

services = Asset("service_equipment")
B(services,"electrical_cabinet",(.75,.65,2.35),(7.0,4.0,1.175),lightsteel)
B(services,"cabinet_door",(.60,.035,2.05),(7.0,3.66,1.2),steel)
for i,x in enumerate((-6.2,-5.8,-5.4)):
    R(services,"process_pipe_%d"%i,(x,-1,.22),(x,4.8,.22),.055,steel)
scene.include("services",services)

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
background.inputs["Color"].default_value = (.74,.82,.86,1)
background.inputs["Strength"].default_value = .50

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c=bsdf.inputs["Base Color"].default_value
    r,g,b=c[0],c[1],c[2]
    if b > r*1.10 and g > r*1.08 and r > .45:
        # Bright daylight strips remain distinguishable from the dark wall.
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value=(.60,.75,.88,1)
            bsdf.inputs["Emission Strength"].default_value=.8
        bsdf.inputs["Roughness"].default_value=.35
    elif g>r*1.3 and g>b*1.05:
        bsdf.inputs["Roughness"].default_value=.24
        bsdf.inputs["Metallic"].default_value=.18
    elif abs(r-g)<.10 and abs(g-b)<.10 and r>.30:
        bsdf.inputs["Metallic"].default_value=.60
        bsdf.inputs["Roughness"].default_value=.32
    else:
        bsdf.inputs["Roughness"].default_value=.46

sc.render.resolution_x=512
sc.render.resolution_y=267
sc.render.resolution_percentage=100
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS)
area_emitter((-7,-3,5.4),power=2200,size=7,target=(0,1,1.8))
area_emitter((0,0,6.3),power=1100,size=7,target=(0,1,0))
area_emitter((5,7,6.3),power=900,size=6,target=(1,2,2))
try:
    sc.view_settings.view_transform="AgX"
except Exception:
    pass

# Reference estimates and actual corresponding geometry points are kept separate.
# Window identity and the transfer-frame corner are approximate associations.
landmarks=[
    ("machine head front top",(MX,MY-.825,4.265),(.68,.31)),
    ("platform front right",(5.45,.22,PZ),(.79,.61)),
    ("tank silhouette top",(TX,TY,2.16+TR),(.40,.53)),
    ("visible left window top",(-W/2+.105,1.8,4.375),(.10,.34)),
    ("transfer far right rail",(3.10,-2.43,1.50),(.60,.72)),
]
def project():
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    rows=[]
    for label,p,ref in landmarks:
        q=proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv=None if q.w<=1e-8 else (.5*(q.x/q.w+1),.5*(1-q.y/q.w))
        rows.append((label,ref,uv))
    return rows

initial=project()
print("Initial camera: label | reference estimate | computed")
for label,ref,uv in initial:
    print(label,ref,None if uv is None else tuple(round(v,3) for v in uv))

# Test a small downward aim only if the primary subject is substantially low.
# Each anchor is checked individually; foreground and background must remain
# visible and already close anchors may not regress by more than 0.03.
if initial[0][2] is not None and initial[0][2][1] > landmarks[0][2][1]+.07:
    old=sc.camera.rotation_euler.copy()
    trial_target=Vector(CAM_TARGET)+Vector((0,0,-.30))
    sc.camera.rotation_euler=(trial_target-sc.camera.location).to_track_quat("-Z","Y").to_euler()
    trial=project()
    valid=all(r[2] is not None and -.05<r[2][0]<1.05 and
              -.05<r[2][1]<1.05 for r in trial)
    no_regression=valid and all(
        abs(trial[i][2][1]-trial[i][1][1]) <=
        abs(initial[i][2][1]-initial[i][1][1])+.03
        for i in range(len(trial)))
    if not no_regression:
        sc.camera.rotation_euler=old
    print("Trial camera:",[(r[0],None if r[2] is None else
          tuple(round(v,3) for v in r[2])) for r in trial],
          "accepted",bool(no_regression))

print("Final active camera: label | reference estimate | computed")
for label,ref,uv in project():
    print(label,ref,None if uv is None else tuple(round(v,3) for v in uv))
