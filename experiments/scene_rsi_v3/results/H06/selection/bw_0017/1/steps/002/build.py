# Reference inventory and visual anchors, normalized to the 512 x 267 image:
# Roof and dark steel beams occupy y=0-.34; the roof is seen from underneath.
# Tall windows line the left wall at x=0-.31, y=.33-.65.
# Yellow-railed platforms occupy x=.09-.96, y=.43-.77; stairs descend in front.
# Stainless machines sit behind the rails, with the largest at x=.61-.79, y=.30-.65.
# A green vertical tank overlaps the platform at x=.36-.45, y=.53-.83.
# Multiple silver and blue conveyor sections fill the foreground, cropped at the bottom.
# Silver ducts rise above and connect the machines. The far equipment is partly occluded.
# Major roof and platform edges are nearly horizontal, with modest perspective convergence;
# columns are vertical. Stair rails run diagonally down toward the foreground.
#
# Comparison with the supplied render:
# 1. The render shows the outside/top of the roof over about the upper third; the photo
#    shows the ceiling underside throughout. The camera was above the roof and outside
#    its front edge. Lowering it and extending the shell toward it should fix this.
# 2. Rendered platform and machines occupy roughly x=.30-.81 and y=.37-.67, much smaller
#    than the reference equipment spread. Moving the camera inside and closer should
#    enlarge them while keeping the machine-to-hall relationships intact.
# 3. The rendered foreground conveyor is a thin isolated strip around y=.68-.86; the
#    reference contains several overlapping sections from y=.73 to the bottom crop.
#    Additional parallel foreground sections and a lower viewpoint increase coverage.
# 4. The render's large exterior columns and open right side are not visible in the photo.
#    The revised shell encloses the viewpoint, keeping supports at the hall perimeter.
# The reference tank top is approximately (.40,.53); its previous computed projection was
# (.408,.572). Previous projections for a window top, machine top and conveyor point were
# (.163,.386), (.652,.340), and (.072,.705), respectively. These points are approximate
# correspondences, not measurements of rendered silhouettes.
#
# Camera parameters are independent of equipment dimensions. A numerical comparison below
# prints baseline, a small downward-camera trial, and the final camera projections. The
# changed camera is supported primarily by the visible roof exterior and low foreground
# coverage; the tank and machine landmarks are monitored as protected features.
# Estimated primitives: hall 90, platform/rails/stairs 125, machinery/ducts 80,
# tank 10, conveyor 100, total approximately 405. Each box/rod/ball is one primitive.

from sceneact import *
import bpy
from mathutils import Vector
from math import sin, cos, pi, sqrt

scene = Scene('Workshop progress')

dark = (.075, .085, .085)
beam = (.12, .14, .14)
roof = (.23, .25, .25)
wall = (.27, .29, .29)
floor_color = (.075, .28, .20)
silver = (.59, .63, .63)
lightmetal = (.76, .79, .78)
machine_dark = (.19, .22, .22)
yellow = (.96, .61, .015)
green = (.015, .32, .22)
blue = (.035, .20, .52)
white = (.80, .83, .82)
window = (.67, .81, .88)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, start, end, radius, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

def path(parent, name, points, radius, color):
    for i in range(len(points)-1):
        R(parent, name + '_' + str(i), points[i], points[i+1], radius, color)

# Architecture: the roof is extended forward around the camera, with columns and
# beams connected at the perimeter. Hidden continuation behind the view is uncertain.
hall = Asset('steel_frame_hall')
B(hall, 'epoxy_floor', (20, 42, .15), (0, -2, -.075), floor_color)
B(hall, 'left_wall', (.18, 42, 6.8), (-9, -2, 3.4), wall)
B(hall, 'rear_wall', (18, .18, 6.8), (0, 16, 3.4), wall)
B(hall, 'roof_sheet', (18.2, 42, .16), (0, -2, 6.85), roof)

for i, y in enumerate((-14, -11, -8, -5, -2, 1, 4, 7, 10, 13)):
    B(hall, 'window_glazing_%02d' % i, (.04, 1.12, 2.35),
      (-8.88, y, 3.05), window)
    for j, dy in enumerate((-.59, .59)):
        B(hall, 'window_side_%02d_%d' % (i,j), (.09,.065,2.48),
          (-8.82,y+dy,3.05), dark)
    B(hall, 'window_mid_%02d' % i, (.09,1.18,.045),
      (-8.81,y,2.45), beam)
for i, y in enumerate((-17,-12,-7,-2,3,8,13,16)):
    for j, x in enumerate((-8.77,8.77)):
        B(hall,'column_%d_%d'%(i,j),(.28,.30,6.75),(x,y,3.375),beam)
    B(hall,'roof_crossbeam_%d'%i,(17.8,.30,.32),(0,y,6.55),beam)
for i,x in enumerate((-7,-4,-1,2,5,8)):
    B(hall,'roof_purlin_%d'%i,(.11,41,.14),(x,-2,6.67),beam)
for i,y in enumerate((-13,-7,-1,5,11)):
    B(hall,'ceiling_strip_%d'%i,(3,.10,.035),(-1,y,6.69),white)
scene.include('hall',hall)

# Elevated open steel platform and yellow perimeter guards.
platform = Asset('processing_platform')
deck_z = 2.22
B(platform,'deck',(13.2,3.1,.20),(.3,3.55,deck_z),silver)
B(platform,'front_fascia',(13.2,.14,.22),(.3,1.98,2.18),lightmetal)
for i,x in enumerate((-6,-3.5,-1,1.5,4,6.5)):
    for j,y in enumerate((2.2,4.9)):
        B(platform,'support_%d_%d'%(i,j),(.14,.14,2.18),(x,y,1.09),beam)
for i,x in enumerate((-6.1,-4.8,-3.5,-2.2,-.9,.4,1.7,3.0,4.3,5.6,6.7)):
    R(platform,'front_guard_post_%d'%i,(x,1.94,2.3),(x,1.94,3.42),.035,yellow)
for i,z in enumerate((2.83,3.42)):
    R(platform,'front_guard_rail_%d'%i,(-6.2,1.94,z),(6.8,1.94,z),.036,yellow)
for i,y in enumerate((2.1,3.1,4.1,5.0)):
    R(platform,'end_post_%d'%i,(6.8,y,2.3),(6.8,y,3.42),.035,yellow)
for i,z in enumerate((2.83,3.42)):
    R(platform,'end_guard_%d'%i,(6.8,2,z),(6.8,5,z),.036,yellow)

def stairs(name,x,yfront=-1.1,yback=2.0):
    a = Asset(name)
    for i in range(9):
        t=(i+.5)/9
        B(a,'tread_%d'%i,(1.15,.32,.07),
          (x,yfront+(yback-yfront)*t,.12+2.12*t),silver)
    for side in (-1,1):
        xx=x+side*.61
        R(a,'stringer_%d'%side,(xx,yfront,.08),(xx,yback,2.24),.06,beam)
        R(a,'handrail_%d'%side,(xx,yfront,.98),(xx,yback,3.18),.04,yellow)
        R(a,'midrail_%d'%side,(xx,yfront,.53),(xx,yback,2.72),.026,yellow)
        for j in range(4):
            t=j/3
            yy=yfront+(yback-yfront)*t
            zz=.08+2.16*t
            R(a,'post_%d_%d'%(side,j),(xx,yy,zz),(xx,yy,zz+.94),.032,yellow)
    return a

platform.include('left_stairs',stairs('left_stairs',-4.5))
platform.include('right_stairs',stairs('right_stairs',5.3))
scene.include('platform',platform)

# Layered machine bodies, with front openings and gaps between units.
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

tank=Asset('green_receiver_tank')
tx,ty=-1.85,-.05
R(tank,'cylindrical_body',(tx,ty,.45),(tx,ty,1.98),.52,green)
tank.include('top_cap',resized(ball(.52,center=(tx,ty,1.98),color=green),(1,1,.3)))
tank.include('bottom_cap',resized(ball(.52,center=(tx,ty,.45),color=green),(1,1,.25)))
for i in range(3):
    a=i*2*pi/3
    x,y=tx+.35*cos(a),ty+.35*sin(a)
    R(tank,'leg_%d'%i,(x,y,.05),(x,y,.5),.055,beam)
R(tank,'top_nozzle',(tx,ty,2.1),(tx,ty,2.38),.10,green)
R(tank,'side_pipe',(tx+.45,ty,1.55),(tx+.78,ty,1.55),.07,silver)
scene.include('tank',tank)

# Three neighboring conveyor runs, with separate beds, rails, rollers and supports.
conveyor=Asset('foreground_roller_conveyors')
def conveyor_run(name,xcenter,y,length,width,z,roller_count):
    a=Asset(name)
    B(a,'bed',(length,width,.13),(xcenter,y,z),silver)
    B(a,'blue_surface',(length-.12,width-.16,.035),(xcenter,y,z+.08),blue)
    for j,side in enumerate((-1,1)):
        yy=y+side*width*.49
        B(a,'side_guide_%d'%j,(length+.1,.07,.16),(xcenter,yy,z+.15),lightmetal)
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
scene.include('conveyor',conveyor)

realize(scene)

for material in bpy.data.materials:
    if not material.use_nodes:
        material.use_nodes=True
    bsdf=material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        c=tuple(material.diffuse_color[:3])
        if c[1]>c[0]*1.5 and c[1]>c[2]*1.05:
            bsdf.inputs['Roughness'].default_value=.23
            bsdf.inputs['Metallic'].default_value=.16
        elif max(c)-min(c)<.09 and c[0]>.38:
            bsdf.inputs['Metallic'].default_value=.65
            bsdf.inputs['Roughness'].default_value=.32
        else:
            bsdf.inputs['Roughness'].default_value=.45
            bsdf.inputs['Metallic'].default_value=.14

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

# Preserve the original aspect for projection and the runner's final view.
sc.render.resolution_x=1920
sc.render.resolution_y=1001
sc.render.resolution_percentage=100
sc.render.pixel_aspect_x=1
sc.render.pixel_aspect_y=1

anchors=[
    ('window top',(-8.89,-1.2,4.175),(.14,.34)),
    ('machine top',(2.95,3.85,5.0),(.68,.30)),
    ('tank top',(-1.85,-.05,2.14),(.40,.53)),
    ('conveyor guide',(-7.7,-5.34,.94),(.08,.85)),
]
def project_table(position,target,lens):
    set_view(position,target,lens=lens)
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    projection=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    result=[]
    for name,p,ref in anchors:
        clip=projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv=None if clip.w<=1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        result.append(uv)
    return result

baseline_position=(11.8,-19.8,8.4)
baseline_target=(-.4,2.0,2.85)
baseline_lens=36
baseline=project_table(baseline_position,baseline_target,baseline_lens)
trial=project_table((11.8,-19.8,7.9),baseline_target,baseline_lens)

# Camera placed just inside the extended roof and aimed through the equipment.
camera_position=(8.2,-15.8,5.4)
camera_target=(-.4,2.0,2.85)
camera_lens=35
final=project_table(camera_position,camera_target,camera_lens)

print('Landmark: reference | baseline | lower-camera trial | final | error change')
for i,(name,p,ref) in enumerate(anchors):
    def fmt(v):
        return None if v is None else tuple(round(x,3) for x in v)
    if baseline[i] is not None and final[i] is not None:
        old=sqrt(sum((baseline[i][j]-ref[j])**2 for j in (0,1)))
        new=sqrt(sum((final[i][j]-ref[j])**2 for j in (0,1)))
        status='improves' if new<old else 'worsens'
    else:
        status='unavailable'
    print(name,ref,fmt(baseline[i]),fmt(trial[i]),fmt(final[i]),status)

# Daylight enters from the window side, with broad overhead fill.
area_emitter((-8,-3,4.8),power=1800,size=7,target=(0,2,1.5))
area_emitter((0,0,6.4),power=1400,size=7,target=(0,2,1.4))
area_emitter((4,7,6.4),power=1200,size=6,target=(0,3,1.5))
