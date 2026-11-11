# Reference versus first render, approximate normalized image coordinates:
# - Roof: reference is an interior ceiling filling y=0.00–0.33; render shows
#   the exterior roof and empty background above the building, y=0.00–0.32.
# - Left windows: reference x=0.00–0.23, y=0.34–0.65; render windows are
#   largely x=0.00–0.28, y=0.36–0.75 and appear too oblique.
# - Main machine: reference x=0.61–0.79, y=0.30–0.70; render roughly
#   x=0.52–0.72, y=0.34–0.67. Its upper housing looks too broad and plain.
# - Tank: reference x=0.36–0.45, y=0.53–0.77; render x=0.34–0.39,
#   y=0.59–0.79. It is too narrow and low in the image.
# - Conveyor: reference enters across the entire bottom left and reaches about
#   x=0.65, y=0.72; render occupies x=0.00–0.55, y=0.72–1.00, with too
#   much uninterrupted blue and insufficient silver transfer equipment.
# - Yellow rails occupy x=0.07–0.96 in the reference; render occupies roughly
#   x=0.25–0.75. Stairs and the platform need a wider visible spread.
# Largest discrepancies: (1) exterior roof and high viewing angle; (2) machine
# and platform occupy too little width and sit too far left; (3) foreground
# conveyor lacks the light-colored transfer frames and the tank is undersized.
# Roof beams should run almost horizontally, the stair rails diagonally, and
# windows vertically. Tank overlaps platform and conveyor overlaps tank base.
# Rear duct connections and some conveyor depth are occluded and approximate.
#
# Corrections: lower CAM_POS inside the hall and extend the roof toward the
# camera, moving roof contours above the view and exposing its underside.
# Reduce camera's lateral offset so platform front edges become more horizontal.
# Enlarge the platform span and place the main machine to the right; its head
# and platform should move right in frame. Increase tank radius and height.
# Add a silver transfer section over the right end of the blue foreground line.
# Camera trial projections are checked individually below; projected points and
# observed silhouettes are different measurements.
#
# Expanded primitive estimate: hall 65; platform and rails 85; machines 35;
# pipes 25; stairs 72; tank 10; conveyor 78; services 8: about 378 meshes.
# Each box, rod, and ball is one mesh. No fillets or Boolean operations.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene("Production hall")
W, D, H = 17.0, 30.0, 6.8
PZ = 2.05
MX, MY = 3.0, 2.25
TX, TY = -1.35, -2.0
CAM_POS = (5.0, -16.5, 5.25)
CAM_TARGET = (0.0, 1.6, 2.85)
CAM_LENS = 37.0

dark = (0.09, 0.105, 0.105)
wall = (0.28, 0.30, 0.29)
roof = (0.25, 0.26, 0.25)
green = (0.07, 0.29, 0.20)
steel = (0.61, 0.65, 0.64)
lightsteel = (0.78, 0.80, 0.77)
midsteel = (0.37, 0.41, 0.40)
black = (0.075, 0.09, 0.09)
yellow = (0.95, 0.66, 0.018)
tankcolor = (0.012, 0.34, 0.22)
blue = (0.07, 0.26, 0.55)
glass = (0.76, 0.85, 0.89)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def rail(parent, name, a, b, base, height=0.95, posts=5):
    ax, ay = a
    bx, by = b
    R(parent, name+"_top", (ax,ay,base+height), (bx,by,base+height), .028, yellow)
    R(parent, name+"_middle", (ax,ay,base+height*.52), (bx,by,base+height*.52), .022, yellow)
    for i in range(posts):
        t = i / (posts-1)
        x, y = ax+(bx-ax)*t, ay+(by-ay)*t
        R(parent, name+"_post_%d"%i, (x,y,base), (x,y,base+height), .026, yellow)

# Steel hall. The camera is inside the extended roof and the walls.
hall = Asset("steel_frame_hall")
B(hall, "floor", (W,D,.14), (0,-3,-.07), green)
B(hall, "left_wall", (.16,D,H), (-W/2,-3,H/2), wall)
B(hall, "back_wall", (W,.16,H), (0,12,H/2), wall)
B(hall, "roof_sheet", (W,D,.13), (0,-3,H), roof)
for i,y in enumerate((-15,-10,-5,0,5,10,11.8)):
    for side in (-1,1):
        x = side*(W/2-.18)
        B(hall, "column_%d_%d"%(i,side), (.24,.27,H), (x,y,H/2), dark)
        B(hall, "column_flange_%d_%d"%(i,side), (.48,.08,H), (x,y,H/2), dark)
    B(hall, "roof_cross_beam_%d"%i, (W,.24,.26), (0,y,H-.28), dark)
for i,x in enumerate((-7,-4,-1,2,5,8)):
    B(hall, "roof_purlin_%d"%i, (.11,D,.12), (x,-3,H-.18), dark)
for i,y in enumerate((-12,-9.7,-7.4,-5.1,-2.8,-.5,1.8,4.1,6.4,8.7,11)):
    B(hall, "window_%d"%i, (.035,.72,2.55), (-W/2+.09,y,3.1), glass)
    B(hall, "window_vertical_mullion_%d"%i, (.05,.04,2.55), (-W/2+.12,y,3.1), dark)
    for j,z in enumerate((2.1,3.1,4.1)):
        B(hall, "window_crossbar_%d_%d"%(i,j), (.06,.73,.035), (-W/2+.13,y,z), midsteel)
scene.include("hall", hall)

# Raised equipment platform and the gaps between its supporting columns.
platform = Asset("operating_platform")
B(platform, "deck", (10.8,3.5,.16), (.1,2.0,PZ), midsteel)
for i,x in enumerate((-5.2,-3.1,-1.0,1.1,3.2,5.4)):
    for j,y in enumerate((.32,3.68)):
        B(platform, "leg_%d_%d"%(i,j), (.14,.14,PZ), (x,y,PZ/2), midsteel)
B(platform, "front_beam", (10.8,.15,.24), (.1,.25,1.90), steel)
B(platform, "back_beam", (10.8,.15,.24), (.1,3.75,1.90), midsteel)
rail(platform,"front_left",(-5.25,.22),(-1.0,.22),PZ+.08,posts=6)
rail(platform,"front_right",(-.15,.22),(5.45,.22),PZ+.08,posts=8)
rail(platform,"left_side",(-5.25,.22),(-5.25,3.75),PZ+.08,posts=4)
rail(platform,"right_side",(5.45,.22),(5.45,3.75),PZ+.08,posts=4)
rail(platform,"rear",(-5.25,3.75),(5.45,3.75),PZ+.08,posts=9)
scene.include("platform", platform)

machines = Asset("stainless_processing_machines")
B(machines,"main_base",(3.3,1.95,.48),(MX,MY,2.37),midsteel)
B(machines,"main_body",(3.3,1.85,1.05),(MX,MY,3.10),steel)
B(machines,"main_front_opening",(2.85,.045,.43),(MX,MY-.94,3.25),black)
B(machines,"opening_inner",(2.61,.04,.26),(MX,MY-.97,3.24),midsteel)
B(machines,"opening_upper_lip",(3.0,.12,.08),(MX,MY-1.00,3.49),lightsteel)
B(machines,"opening_lower_lip",(3.1,.17,.10),(MX,MY-1.00,3.01),lightsteel)
B(machines,"upper_head",(3.15,1.65,.65),(MX,MY,3.94),lightsteel)
B(machines,"upper_cap",(2.85,1.45,.13),(MX,MY,4.32),steel)
B(machines,"lower_ledge",(3.5,.25,.12),(MX,MY-1.00,2.70),lightsteel)
for i in range(6):
    x = MX-1.22+i*.49
    B(machines,"front_divider_%d"%i,(.035,.045,.28),(x,MY-1.00,3.24),steel)
R(machines,"indicator_rim",(MX,MY-.84,4.0),(MX,MY-.90,4.0),.11,midsteel)
R(machines,"indicator",(MX,MY-.91,4.0),(MX,MY-.94,4.0),.058,tankcolor)
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
        ducts.include(name+"_elbow_%d"%i,ball(radius=radius,center=p,color=lightsteel))
pipe("main_duct",[(MX,2.8,4.3),(MX,2.8,4.85),(MX+.18,2.8,5.05),
                  (MX+.78,2.8,5.05),(MX+.96,2.8,4.85),(MX+.96,2.8,4.35)],.17)
pipe("left_duct",[(-4.1,2.7,3.6),(-4.1,2.7,4.25),(-3.9,2.7,4.43),
                  (-3.0,2.7,4.43),(-2.8,2.7,4.22),(-2.8,2.7,3.7)],.14)
pipe("process_run",[(-2.8,3.0,3.8),(-1.0,3.0,3.8),(.45,3.0,3.7)],.11)
for i,x in enumerate((-3.5,3.5)):
    R(ducts,"hanger_%d"%i,(x,2.8,5.04),(x,2.8,6.55),.025,midsteel)
scene.include("ducts", ducts)

def staircase(name,x0,x1,yt,yb,n):
    stair = Asset(name)
    for i in range(n):
        t=(i+.5)/n
        B(stair,"tread_%d"%i,(x1-x0,abs(yt-yb)/n*.80,.06),
          ((x0+x1)/2,yb+(yt-yb)*t,PZ*t),lightsteel)
    for k,x in enumerate((x0,x1)):
        R(stair,"stringer_%d"%k,(x,yb,.05),(x,yt,PZ),.055,midsteel)
        R(stair,"top_rail_%d"%k,(x,yb,.95),(x,yt,PZ+.95),.028,yellow)
        R(stair,"mid_rail_%d"%k,(x,yb,.51),(x,yt,PZ+.51),.022,yellow)
        for j in range(5):
            t=j/4
            y=yb+(yt-yb)*t
            z=.05+(PZ-.05)*t
            R(stair,"post_%d_%d"%(k,j),(x,y,z),(x,y,z+.95),.025,yellow)
    scene.include(name,stair)
staircase("left_stair",-5.2,-4.25,.3,-2.8,9)
staircase("right_stair",5.25,6.35,.3,-3.6,10)
staircase("middle_stair",-.9,.05,.3,-2.65,9)

tank = Asset("green_pressure_tank")
TR = .54
R(tank,"shell",(TX,TY,.42),(TX,TY,2.00),TR,tankcolor)
tank.include("top_head",ball(radius=TR,center=(TX,TY,1.98),color=tankcolor))
tank.include("bottom_head",ball(radius=TR,center=(TX,TY,.44),color=tankcolor))
for i,(dx,dy) in enumerate(((-.32,-.24),(.32,-.24),(-.32,.24),(.32,.24))):
    B(tank,"foot_%d"%i,(.10,.10,.44),(TX+dx,TY+dy,.22),midsteel)
R(tank,"neck",(TX,TY,2.45),(TX,TY,2.63),.085,steel)
R(tank,"flange",(TX,TY,2.58),(TX,TY,2.63),.14,midsteel)
R(tank,"side_nozzle",(TX+.45,TY,1.65),(TX+.70,TY,1.65),.07,steel)
scene.include("tank",tank)

# Conveyor and the pale, open transfer frames seen over its right-hand portion.
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
for i,y in enumerate((-4.95,-4.25,-3.55)):
    B(conv,"transfer_bed_%d"%i,(4.5,.52,.10),(1.0,y,1.12),steel)
    for s in (-1,1):
        B(conv,"transfer_rail_%d_%d"%(i,s),(4.5,.055,.16),(1.0,y+s*.3,1.20),lightsteel)
    for j in range(7):
        x=-.9+j*.62
        R(conv,"transfer_roller_%d_%d"%(i,j),(x,y-.24,1.19),(x,y+.24,1.19),.023,lightsteel)
for i,x in enumerate((-.8,1.0,2.8)):
    B(conv,"transfer_support_%d"%i,(.10,2.2,1.05),(x,-4.25,.53),steel)
B(conv,"transfer_side_housing",(1.5,.25,.68),(2.5,-5.0,.90),lightsteel)
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
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
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
    if g>r*1.3 and g>b*1.05:
        bsdf.inputs["Roughness"].default_value=.24
        bsdf.inputs["Metallic"].default_value=.18
    elif abs(r-g)<.10 and abs(g-b)<.10 and r>.30:
        bsdf.inputs["Metallic"].default_value=.65
        bsdf.inputs["Roughness"].default_value=.30
    else:
        bsdf.inputs["Roughness"].default_value=.46

sc.render.resolution_x=512
sc.render.resolution_y=267
sc.render.resolution_percentage=100
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS)
area_emitter((-7,-3,5.4),power=1800,size=7,target=(0,1,1.8))
area_emitter((0,0,6.3),power=1200,size=7,target=(0,1,0))
area_emitter((5,7,6.3),power=1000,size=6,target=(1,2,2))
try:
    sc.view_settings.view_transform="AgX"
except Exception:
    pass

# All points below lie on actual geometry. The conveyor and window associations
# are approximate because the matching corners are partially cropped or unclear.
landmarks=[
    ("machine head front top",(MX,MY-.825,4.265),(.68,.31)),
    ("platform front right",(5.45,.22,PZ),(.79,.61)),
    ("tank silhouette top",(TX,TY,1.98+TR),(.40,.53)),
    ("left window top",(-W/2+.09,-5.1,4.375),(.10,.34)),
    ("foreground transfer near right",(3.25,-5.1,1.28),(.53,.83)),
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

# Try a modest camera aim correction only for a common horizontal displacement.
# Keep the window and foreground in frame and reject any large regression.
uvs=[row[2] for row in initial]
if all(p is not None for p in uvs):
    dx=sum(landmarks[i][2][0]-uvs[i][0] for i in (0,1,2))/3
    if abs(dx)>.08:
        old=sc.camera.rotation_euler.copy()
        trial_target=Vector(CAM_TARGET)+Vector((-0.55 if dx>0 else 0.55,0,0))
        sc.camera.rotation_euler=(trial_target-sc.camera.location).to_track_quat("-Z","Y").to_euler()
        trial=project()
        valid=all(row[2] is not None and -.05<row[2][0]<1.05 and
                  -.05<row[2][1]<1.05 for row in (trial[2],trial[3],trial[4]))
        background_ok=valid and abs(trial[3][2][0]-trial[3][1][0]) <= abs(initial[3][2][0]-initial[3][1][0])+.035
        main_better=valid and all(abs(trial[i][2][0]-trial[i][1][0]) <=
                                  abs(initial[i][2][0]-initial[i][1][0])+.015 for i in (0,1,2))
        if not (valid and background_ok and main_better):
            sc.camera.rotation_euler=old
        print("Trial camera:",[(r[0],None if r[2] is None else tuple(round(v,3) for v in r[2])) for r in trial],
              "accepted",bool(valid and background_ok and main_better))

print("Final active camera: label | reference estimate | computed")
for label,ref,uv in project():
    print(label,ref,None if uv is None else tuple(round(v,3) for v in uv))
