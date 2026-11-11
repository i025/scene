# Reference inventory and visual estimates, normalized to the 512 x 267 photograph:
# Hall: dark ceiling and beams y=0-.34; side windows x=0-.30, y=.33-.65.
# Equipment: yellow-railed platforms x=.08-.97, y=.43-.77; several stainless
# machines behind the rails, with the largest at x=.61-.79, y=.30-.67.
# Green tank: x=.36-.45, y=.53-.83, in front of the platform.
# Foreground conveyor and silver machinery: x=0-.68, y=.73-1, bottom cropped.
# Silver ducts rise above and link the processing units. Far equipment and the
# exact connections behind the machinery are partly occluded and uncertain.
# Roof and platform edges are approximately horizontal; stair rails slope down
# toward the foreground. The conveyor overlaps the tank base and platform legs.
#
# Comparison with step 2:
# 1. The rendered conveyor occupies approximately x=0-.57, y=.72-.94, while
#    the photograph has a much denser, brighter foreground reaching the bottom
#    crop. Add open silver frames and cross-conveyors closer to the camera.
# 2. The rendered platform spans approximately x=.27-.89, y=.43-.67, versus
#    about x=.08-.96, y=.44-.77 in the photo. Increase lens modestly and add
#    a left platform extension; the latter affects the left rail locally.
# 3. The rendered tank top is around (.39,.59), compared with (.40,.53).
#    Increase tank height about its fixed base, leaving the machine top protected.
# 4. The rendered windows are dark, around x=0-.30 and y=.35-.60; the reference
#    windows are bright and extend to about y=.65. Bright glazing and daylight
#    from the window side should make the background read more like the photo.
# 5. The rendered machinery appears as simple pale boxes, and has larger empty
#    gaps below it than the reference. Add dark machine openings, lower equipment
#    frames, side pipework and a third stair flight without closing every gap.
# The photo crops the foreground conveyor: its image-border intersection is not
# a physical endpoint. Exact individual conveyor correspondences are uncertain.
#
# Camera trial: a modest increase of lens from 35 to 38 expands the platform
# outward; raising the aim slightly offsets the resulting upward movement of the
# protected machine top. Baseline, trial and proposed projections are compared
# below, and the lens/aim change is reduced if it worsens the protected top too
# much. The camera itself remains below the roof.
# Tank height trial uses a fixed base pivot: its top moves upward while the base
# and the machine anchor remain fixed. The program checks both before building.
#
# Expanded primitive estimate: hall 90, platforms and stairs 135, machines and
# ducts 90, tank 10, conveyors and frames 125: roughly 450 meshes. Each box,
# rod and ball emits one mesh; short pipe paths use one rod per segment.

from sceneact import *
import bpy
from mathutils import Vector
from math import sin, cos, pi, sqrt

scene = Scene('Workshop progress')

dark = (.075, .085, .085)
beam = (.105, .12, .12)
roof = (.19, .21, .21)
wall = (.23, .25, .25)
floor_color = (.055, .26, .18)
silver = (.57, .61, .61)
lightmetal = (.76, .79, .78)
machine_dark = (.13, .15, .15)
yellow = (.96, .62, .012)
green = (.012, .31, .20)
blue = (.035, .19, .49)
white = (.81, .84, .82)
window = (.75, .86, .92)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, start, end, radius, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

def path(parent, name, points, radius, color):
    for i in range(len(points)-1):
        R(parent, name+'_'+str(i), points[i], points[i+1], radius, color)

# Shell and structural members.
hall = Asset('steel_frame_hall')
B(hall, 'epoxy_floor', (20,42,.15), (0,-2,-.075), floor_color)
B(hall, 'left_wall', (.18,42,6.8), (-9,-2,3.4), wall)
B(hall, 'rear_wall', (18,.18,6.8), (0,16,3.4), wall)
B(hall, 'roof_sheet', (18.2,42,.16), (0,-2,6.85), roof)

for i,y in enumerate((-14,-11,-8,-5,-2,1,4,7,10,13)):
    B(hall,'window_glazing_%02d'%i,(.04,1.12,2.65),
      (-8.88,y,3.05),window)
    for j,dy in enumerate((-.59,.59)):
        B(hall,'window_side_%02d_%d'%(i,j),(.09,.065,2.78),
          (-8.82,y+dy,3.05),dark)
    for j,z in enumerate((2.15,3.1,4.0)):
        B(hall,'window_mullion_%02d_%d'%(i,j),(.09,1.18,.045),
          (-8.81,y,z),beam)

for i,y in enumerate((-17,-12,-7,-2,3,8,13,16)):
    for j,x in enumerate((-8.77,8.77)):
        B(hall,'column_%d_%d'%(i,j),(.28,.30,6.75),
          (x,y,3.375),beam)
    B(hall,'roof_crossbeam_%d'%i,(17.8,.30,.32),(0,y,6.55),beam)
for i,x in enumerate((-7,-4,-1,2,5,8)):
    B(hall,'roof_purlin_%d'%i,(.11,41,.14),(x,-2,6.67),beam)
for i,y in enumerate((-13,-7,-1,5,11)):
    B(hall,'ceiling_strip_%d'%i,(3,.10,.035),(-1,y,6.69),white)
scene.include('hall',hall)

# Raised platform, steel legs, continuous safety guards and staircase flights.
platform = Asset('processing_platform')
B(platform,'main_deck',(13.2,3.1,.20),(.3,3.55,2.22),silver)
B(platform,'left_deck_extension',(2.2,2.0,.20),(-7.25,3.0,2.22),silver)
B(platform,'front_fascia',(15.0,.14,.22),(-.6,1.98,2.18),lightmetal)
for i,x in enumerate((-7.5,-6,-3.5,-1,1.5,4,6.5)):
    for j,y in enumerate((2.2,4.9)):
        B(platform,'support_%d_%d'%(i,j),(.14,.14,2.18),
          (x,y,1.09),beam)
for i,x in enumerate((-7.8,-6.6,-5.4,-4.2,-3,-1.8,-.6,.6,1.8,3,4.2,5.4,6.7)):
    R(platform,'front_guard_post_%d'%i,(x,1.94,2.3),(x,1.94,3.42),
      .035,yellow)
for i,z in enumerate((2.83,3.42)):
    R(platform,'front_guard_rail_%d'%i,(-7.8,1.94,z),(6.8,1.94,z),
      .036,yellow)
for i,y in enumerate((2.1,3.1,4.1,5)):
    R(platform,'end_post_%d'%i,(6.8,y,2.3),(6.8,y,3.42),.035,yellow)
for i,z in enumerate((2.83,3.42)):
    R(platform,'end_guard_%d'%i,(6.8,2,z),(6.8,5,z),.036,yellow)

def stairs(name,x,yfront=-1.1,yback=2.0,width=1.15):
    a=Asset(name)
    for i in range(9):
        t=(i+.5)/9
        B(a,'tread_%d'%i,(width,.32,.07),
          (x,yfront+(yback-yfront)*t,.12+2.12*t),silver)
    for side in (-1,1):
        xx=x+side*(width/2+.035)
        R(a,'stringer_%d'%side,(xx,yfront,.08),(xx,yback,2.24),.06,beam)
        R(a,'handrail_%d'%side,(xx,yfront,.98),(xx,yback,3.18),.04,yellow)
        R(a,'midrail_%d'%side,(xx,yfront,.53),(xx,yback,2.72),.026,yellow)
        for j in range(4):
            t=j/3
            yy=yfront+(yback-yfront)*t
            zz=.08+2.16*t
            R(a,'post_%d_%d'%(side,j),(xx,yy,zz),(xx,yy,zz+.94),
              .032,yellow)
    return a

platform.include('left_stairs',stairs('left_stairs',-5.4))
platform.include('middle_stairs',stairs('middle_stairs',-1.7))
platform.include('right_stairs',stairs('right_stairs',5.3))
scene.include('platform',platform)

# Layered stainless equipment and dark openings.
machines=Asset('stainless_machines')
def machine(name,x,y,w,d,h):
    a=Asset(name)
    base=2.34
    B(a,'bottom_frame',(w,d,.22),(x,y,base+.12),silver)
    for i,dx in enumerate((-w*.41,w*.41)):
        for j,dy in enumerate((-d*.38,d*.38)):
            B(a,'leg_%d_%d'%(i,j),(.12,.12,.62),
              (x+dx,y+dy,base+.50),beam)
    B(a,'body',(w,d,h*.57),(x,y,base+.62+h*.285),silver)
    B(a,'upper_housing',(w*.88,d*.89,h*.22),
      (x,y,base+.62+h*.68),lightmetal)
    fy=y-d/2-.018
    B(a,'dark_front_opening',(w*.76,.035,h*.18),
      (x,fy,base+.62+h*.53),machine_dark)
    for k in range(4):
        B(a,'front_slat_%d'%k,(w*.73,.025,.035),
          (x,fy-.025,base+.62+h*.47+k*h*.035),silver)
    B(a,'front_lip',(w*.94,.10,.09),
      (x,fy-.05,base+.62+h*.41),lightmetal)
    return a

machines.include('large_right',machine('large_right',2.95,3.85,2.65,1.8,2.0))
machines.include('left',machine('left',-3.65,3.95,2.15,1.75,1.55))
machines.include('middle',machine('middle',-.65,4.12,2.05,1.65,1.25))
machines.include('far_right',machine('far_right',7.25,6,1.35,1.3,1.25))
B(machines,'large_top',(1.55,1.36,.30),(2.95,3.85,4.85),silver)
R(machines,'large_front_disc',(2.9,2.91,4.51),(2.9,2.85,4.51),.13,beam)
B(machines,'left_top',(1.25,1.2,.28),(-3.65,3.95,4.27),silver)
B(machines,'control_cabinet',(.72,.65,1.8),(6.85,4.6,3.25),white)
B(machines,'cabinet_panel',(.46,.035,.55),(6.85,4.25,3.65),machine_dark)
# Visible equipment below the principal right machine.
B(machines,'lower_right_housing',(2.6,1.35,.65),(2.95,3.6,1.65),silver)
B(machines,'lower_right_dark_slot',(2.2,.035,.18),(2.95,2.91,1.71),machine_dark)
B(machines,'lower_right_trim',(2.55,.12,.09),(2.95,2.86,1.42),lightmetal)
scene.include('machines',machines)

ducts=Asset('insulated_ducts_and_hangers')
path(ducts,'large_exhaust',[(3.15,4,4.98),(3.15,4,5.5),(3.0,4,5.72),
                            (2.72,4,5.78),(1.85,4,5.78)],.21,lightmetal)
path(ducts,'left_exhaust',[(-3.7,4,4.42),(-3.7,4,5.05),(-3.45,4,5.28),
                           (-2.1,4,5.20),(-1.65,4,4.65)],.18,lightmetal)
path(ducts,'process_header',[(-6.6,5,4),(-4.7,5,4.2),(-2.5,5,4.1),
                             (-.2,5,4),(1.6,5,4)],.12,lightmetal)
path(ducts,'right_link',[(4.1,4.5,4.1),(5.1,4.5,4.1),(5.6,5,3.9),
                         (7.1,5.4,3.9)],.12,lightmetal)
for i,x in enumerate((-4,0,4)):
    R(ducts,'hanger_%d'%i,(x,5,4.2),(x,5,6.5),.025,beam)
scene.include('ducts',ducts)

# Fixed-base height correction to the receiver tank.
tank_base=.45
tank_top_old=1.98
tank_scale=1.22
tank_top=tank_base+(tank_top_old-tank_base)*tank_scale
tx,ty=-1.85,-.05
tank=Asset('green_receiver_tank')
R(tank,'cylindrical_body',(tx,ty,tank_base),(tx,ty,tank_top),.52,green)
tank.include('top_cap',resized(ball(.52,center=(tx,ty,tank_top),color=green),
                               (1,1,.3)))
tank.include('bottom_cap',resized(ball(.52,center=(tx,ty,tank_base),color=green),
                                  (1,1,.25)))
for i in range(3):
    ang=i*2*pi/3
    x,y=tx+.35*cos(ang),ty+.35*sin(ang)
    R(tank,'leg_%d'%i,(x,y,.05),(x,y,.5),.055,beam)
R(tank,'top_nozzle',(tx,ty,tank_top+.12),(tx,ty,tank_top+.36),.10,green)
R(tank,'side_pipe',(tx+.45,ty,1.55),(tx+.78,ty,1.55),.07,silver)
scene.include('tank',tank)

# Multiple foreground conveyor sections, with open frames and blue roller beds.
conveyor=Asset('foreground_roller_conveyors')
def conveyor_run(name,xcenter,y,length,width,z,roller_count):
    a=Asset(name)
    B(a,'bed',(length,width,.13),(xcenter,y,z),silver)
    B(a,'blue_surface',(length-.12,width-.16,.035),(xcenter,y,z+.08),blue)
    for j,side in enumerate((-1,1)):
        yy=y+side*width*.49
        B(a,'side_guide_%d'%j,(length+.1,.07,.16),
          (xcenter,yy,z+.15),lightmetal)
    for i in range(roller_count):
        xx=xcenter-length*.47+i*(length*.94/(roller_count-1))
        R(a,'roller_%02d'%i,(xx,y-width*.42,z+.12),
          (xx,y+width*.42,z+.12),.032,lightmetal)
    for i,xx in enumerate((xcenter-length*.40,xcenter,xcenter+length*.40)):
        for j,side in enumerate((-1,1)):
            B(a,'leg_%d_%d'%(i,j),(.09,.09,z),
              (xx,y+side*width*.38,z/2),silver)
    return a

conveyor.include('main_line',conveyor_run('main_line',-3,-4.7,10.5,1.25,.78,19))
conveyor.include('near_line',conveyor_run('near_line',-3.7,-6.25,9.8,1.15,.72,17))
conveyor.include('return_line',conveyor_run('return_line',-.3,-2.6,5.7,1.0,.85,10))
B(conveyor,'drive_motor',(.55,.40,.38),(2,-3.35,.48),beam)

# Bright framing and machinery around the return line, extending into the crop.
for i,y in enumerate((-7.4,-5.7,-3.8,-2.1)):
    B(conveyor,'cross_frame_%d'%i,(.11,3.1,.12),(1.6,y,.93),lightmetal)
for i,x in enumerate((.65,2.35)):
    B(conveyor,'long_frame_%d'%i,(.10,6.2,.14),(x,-4.7,.93),lightmetal)
    for j,y in enumerate((-7.2,-5,-2.5)):
        B(conveyor,'cross_support_%d_%d'%(i,j),(.1,.1,.88),(x,y,.44),silver)
B(conveyor,'foreground_machine_side',(1.5,1.25,.72),(1.7,-4.1,.57),lightmetal)
B(conveyor,'foreground_machine_top',(1.55,1.3,.08),(1.7,-4.1,.97),silver)
for i in range(6):
    y=-4.6+i*.20
    R(conveyor,'short_roller_%d'%i,(.9,y,1.03),(2.4,y,1.03),.035,lightmetal)
scene.include('conveyor',conveyor)

realize(scene)

# Use the shared color palette to give the metal, paint and floor different finishes.
for material in bpy.data.materials:
    if not material.use_nodes:
        material.use_nodes=True
    bsdf=material.node_tree.nodes.get('Principled BSDF')
    if not bsdf:
        continue
    c=tuple(material.diffuse_color[:3])
    if c[1]>c[0]*1.5 and c[1]>c[2]*1.05:
        bsdf.inputs['Roughness'].default_value=.23
        bsdf.inputs['Metallic'].default_value=.16
    elif max(c)-min(c)<.09 and c[0]>.38:
        bsdf.inputs['Metallic'].default_value=.58
        bsdf.inputs['Roughness'].default_value=.34
    else:
        bsdf.inputs['Roughness'].default_value=.45
        bsdf.inputs['Metallic'].default_value=.14
    # The glazing is a bright daytime source in the otherwise opaque wall.
    if abs(c[0]-window[0])<.015 and abs(c[1]-window[1])<.015:
        bsdf.inputs['Emission Color'].default_value=(*window,1)
        bsdf.inputs['Emission Strength'].default_value=.8

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.70,.76,.82,1)
background.inputs['Strength'].default_value=.65

# Use the source image aspect for the camera and the numerical projections.
sc.render.resolution_x=1920
sc.render.resolution_y=1001
sc.render.resolution_percentage=100
sc.render.pixel_aspect_x=1
sc.render.pixel_aspect_y=1

anchors=[
    ('window top',(-8.89,-1.2,4.175),(.14,.34)),
    ('machine top protected',(2.95,3.85,5.0),(.68,.30)),
    ('tank old top',(tx,ty,2.14),(.40,.53)),
    ('foreground guide',(-7.7,-5.34,.94),(.08,.85)),
]
def project_points(position,target,lens,points):
    set_view(position,target,lens=lens)
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    values=[]
    for p in points:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        values.append(None if clip.w<=1e-8 else
                      (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w)))
    return values

def distance(uv,ref):
    return 1e6 if uv is None else sqrt(sum((uv[j]-ref[j])**2 for j in (0,1)))

position=(8.2,-15.8,5.4)
baseline_target=(-.4,2.0,2.85)
baseline_lens=35
points=[a[1] for a in anchors]
baseline=project_points(position,baseline_target,baseline_lens,points)
trial=project_points(position,baseline_target,36,points)
candidate_target=(-.4,2.0,3.05)
candidate_lens=38
candidate=project_points(position,candidate_target,candidate_lens,points)
# The machine top is already close to its estimated reference location.
# Limit degradation to a small tolerance; use the smaller lens trial if needed.
if distance(candidate[1],anchors[1][2]) > distance(baseline[1],anchors[1][2])+.035:
    camera_target=baseline_target
    camera_lens=36
else:
    camera_target=candidate_target
    camera_lens=candidate_lens
final=project_points(position,camera_target,camera_lens,points)

def fmt(value):
    return None if value is None else tuple(round(x,3) for x in value)

print('Camera landmark: reference | baseline | small lens trial | final | change')
for i,(name,p,ref) in enumerate(anchors):
    status='improves' if distance(final[i],ref)<distance(baseline[i],ref) else 'worsens'
    print(name,ref,fmt(baseline[i]),fmt(trial[i]),fmt(final[i]),status)

# Check actual tank points under the fixed-base scale, with the protected machine.
tank_points=[
    (tx,ty,tank_base),
    (tx,ty,2.14),
    (tx,ty,tank_base+(2.14-tank_base)*tank_scale),
    (2.95,3.85,5.0),
]
tp=project_points(position,camera_target,camera_lens,tank_points)
print('Tank geometry: base fixed',fmt(tp[0]),'top old',fmt(tp[1]),
      'top final',fmt(tp[2]),'reference',(.40,.53),
      'protected machine',fmt(tp[3]))
# The scaling direction is checked against the approximate reference.
# Revert the tank height if it moves farther from that point.
if distance(tp[2],(.40,.53)) > distance(tp[1],(.40,.53)):
    # Geometry has already been realized; scale the named tank subtree's meshes
    # about the fixed base only if the proposed scale was unsupported.
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and 'green_receiver_tank' in obj.name:
            obj.location.z=tank_base+(obj.location.z-tank_base)/tank_scale
            obj.scale.z/=tank_scale
    print('Tank height proposal rejected by projection check')

# Restore the selected active camera after the projection checks.
set_view(position,camera_target,lens=camera_lens)
area_emitter((-8,-3,4.8),power=2200,size=7,target=(0,2,1.5))
area_emitter((0,0,6.4),power=1700,size=7,target=(0,2,1.4))
area_emitter((4,7,6.4),power=1400,size=6,target=(0,3,1.5))
