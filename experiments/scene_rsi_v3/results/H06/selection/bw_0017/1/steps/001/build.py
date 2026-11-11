# Reference inventory and image anchors (normalized image coordinates, visual estimates):
# - Hall: dark roof and beams span (0,0)-(1,.36); green floor appears mostly below .65.
# - Left wall: narrow bright vertical windows at x=.02-.32, y=.33-.65.
# - Main raised processing platforms and yellow rails: x=.08-.96, y=.44-.82.
#   The largest stainless machine is at x=.60-.80, y=.30-.66; smaller machines
#   and silver ductwork continue leftward and into the right background.
# - Green vertical tank: x=.36-.45, y=.53-.83, in front of the platform.
# - Blue and silver foreground conveyor: x=0-.64, y=.76-1, cropped by the frame.
# - Two yellow-railed stairs descend toward the camera: approximately x=.19-.32
#   and x=.72-.87, overlapping the platforms and conveyor.
# - Major edges: roof beams run broadly left-right, receding toward the right;
#   floor and conveyor edges recede diagonally; rail posts and columns are vertical.
# - The far wall and equipment behind the platforms are partly occluded and uncertain.
#
# Approximate expanded primitive count: architecture 55, platforms/rails/stairs 130,
# machines and ducts 65, tank 14, conveyor 65, miscellaneous 15: about 344 meshes.
# Every box, rod and ball is one primitive; each short pipe bend is made of rods.
#
# Camera parameters and equipment dimensions are deliberately independent. Projection
# anchors below are estimates of physical points, not calibrated correspondences.

from sceneact import *
import bpy
from mathutils import Vector
from math import sin, cos, pi

scene = Scene('Production hall')
steel = (0.30, 0.33, 0.34)
darksteel = (0.105, 0.125, 0.13)
roof = (0.16, 0.18, 0.18)
wall = (0.31, 0.34, 0.34)
silver = (0.63, 0.67, 0.67)
brightmetal = (0.78, 0.81, 0.80)
black = (0.09, 0.105, 0.105)
yellow = (0.95, 0.62, 0.015)
green = (0.015, 0.34, 0.23)
floorcol = (0.12, 0.32, 0.24)
blue = (0.06, 0.25, 0.61)
white = (0.78, 0.81, 0.78)
glass = (0.64, 0.79, 0.85)

def B(parent, name, size, loc, color):
    parent.include(name, box(size=size, center=loc, color=color))

def R(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def pipe(parent, name, points, radius=.14):
    for i in range(len(points)-1):
        R(parent, '%s_%02d' % (name, i), points[i], points[i+1], radius, brightmetal)

# Building shell, with an open front for the camera.
hall = Asset('steel_frame_hall')
B(hall, 'green_epoxy_floor', (22, 25, .16), (0, 3, -.08), floorcol)
B(hall, 'left_wall', (.18, 25, 6.8), (-9, 3, 3.4), wall)
B(hall, 'far_wall', (18, .18, 6.8), (0, 15.4, 3.4), wall)
B(hall, 'roof_sheet', (18.2, 25, .16), (0, 3, 6.85), roof)
# Thin window bays are placed just inside the left wall.
for i, y in enumerate((-7.4, -4.3, -1.2, 1.9, 5.0, 8.1, 11.2, 14.2)):
    B(hall, 'window_%d' % i, (.04, 1.05, 2.35), (-8.89, y, 3.0), glass)
    for dy in (-.56, .56):
        B(hall, 'window_frame_%d_%s' % (i,dy), (.10,.07,2.5),
          (-8.82,y+dy,3), darksteel)
    B(hall, 'window_mid_%d' % i, (.10,1.15,.045), (-8.80,y,2.4), darksteel)
for i, y in enumerate((-8, -3, 2, 7, 12, 15)):
    for x in (-8.75, 8.75):
        B(hall, 'column_%d_%s' % (i,x), (.28,.32,6.8), (x,y,3.4), darksteel)
    B(hall, 'roof_crossbeam_%d' % i, (17.8,.35,.32), (0,y,6.55), darksteel)
for x in (-6,-3,0,3,6):
    B(hall, 'roof_purlin_%s' % x, (.12,24,.14), (x,3,6.68), steel)
for y in (-5, 1, 7, 13):
    B(hall, 'overhead_light_%s' % y, (4,.16,.035), (-1,y,6.69), white)
scene.include('hall', hall)

# Shared platform with open steel legs and contrasting yellow railings.
platform = Asset('processing_platforms')
platform_z = 2.22
B(platform, 'main_deck', (13.2,3.1,.20), (.3,3.55,platform_z), steel)
B(platform, 'front_edge', (13.2,.15,.22), (.3,1.99,2.18), brightmetal)
for x in (-6,-3.5,-1,1.5,4,6.5):
    for y in (2.2,4.9):
        B(platform, 'support_%s_%s' % (x,y), (.14,.14,2.18), (x,y,1.09), darksteel)
for x in (-6.1,-4.8,-3.5,-2.2,-.9,.4,1.7,3.0,4.3,5.6,6.7):
    R(platform, 'front_post_%s' % x, (x,1.94,2.30), (x,1.94,3.42), .035, yellow)
for z in (2.83,3.42):
    R(platform, 'front_rail_%s' % z, (-6.2,1.94,z), (6.8,1.94,z), .036, yellow)
for y in (2.1,3.1,4.1,5.0):
    R(platform, 'end_post_%s' % y, (6.8,y,2.30), (6.8,y,3.42), .035, yellow)
for z in (2.83,3.42):
    R(platform, 'end_rail_%s' % z, (6.8,2,z), (6.8,5,z), .035, yellow)

# Two straight stair flights, with treads and diagonal handrails.
def stairs(name, x, yfront, yback):
    asset = Asset(name)
    width = 1.15
    n = 9
    for i in range(n):
        t = (i+0.5)/n
        y = yfront + (yback-yfront)*t
        z = .12 + 2.12*t
        B(asset, 'tread_%d' % i, (width,.32,.07), (x,y,z), silver)
    for side in (-1,1):
        xx = x + side*.61
        R(asset, 'stringer_%s' % side, (xx,yfront,.08), (xx,yback,2.24), .065, steel)
        R(asset, 'handrail_%s' % side, (xx,yfront,.95), (xx,yback,3.18), .045, yellow)
        R(asset, 'middle_rail_%s' % side, (xx,yfront,.52), (xx,yback,2.72), .025, yellow)
        for j in range(4):
            t = j/3
            yy = yfront+(yback-yfront)*t
            zz = .08+2.16*t
            R(asset, 'post_%s_%d' % (side,j), (xx,yy,zz), (xx,yy,zz+.94), .035, yellow)
    return asset
platform.include('left_stair', stairs('left_stair', -4.5,-1.1,2.0))
platform.include('right_stair', stairs('right_stair', 5.3,-1.1,2.0))
scene.include('platform', platform)

# Raised stainless machinery. Boxes are deliberately layered to leave visible dark
# openings, machine legs, railings and gaps between separate processing units.
machines = Asset('stainless_processing_machines')
def machine(name,x,y,w,d,h):
    a = Asset(name)
    base = 2.34
    B(a,'lower_frame',(w,d,.22),(x,y,base+.12),silver)
    for dx in (-w*.41,w*.41):
        for dy in (-d*.38,d*.38):
            B(a,'machine_leg_%s_%s'%(dx,dy),(.12,.12,.62),
              (x+dx,y+dy,base+.50),steel)
    B(a,'body',(w,d,h*.57),(x,y,base+.62+h*.285),silver)
    B(a,'upper_housing',(w*.88,d*.89,h*.22),
      (x,y,base+.62+h*.68),brightmetal)
    # Front face is on the camera-facing, negative-Y side.
    fy = y-d/2-.018
    B(a,'dark_access_opening',(w*.76,.035,h*.18),
      (x,fy,base+.62+h*.53),black)
    for k in range(4):
        B(a,'opening_slats_%d'%k,(w*.73,.025,.035),
          (x,fy-.025,base+.62+h*.47+k*h*.035),steel)
    B(a,'front_lip',(w*.94,.10,.09),(x,fy-.05,base+.62+h*.41),brightmetal)
    return a
machines.include('large_right_machine', machine('large_right_machine',2.95,3.85,2.65,1.8,2.0))
machines.include('left_machine', machine('left_machine',-3.65,3.95,2.15,1.75,1.55))
machines.include('middle_machine', machine('middle_machine',-.65,4.12,2.05,1.65,1.25))
machines.include('far_right_machine', machine('far_right_machine',7.25,6.0,1.35,1.3,1.25))
# Raised housings and round vent-like details.
B(machines,'large_machine_top',(1.55,1.36,.30),(2.95,3.85,4.85),silver)
R(machines,'large_front_disc',(2.9,2.91,4.51),(2.9,2.85,4.51),.13,darksteel)
B(machines,'left_top',(1.25,1.2,.28),(-3.65,3.95,4.27),silver)
B(machines,'control_cabinet',(0.72,.65,1.8),(6.85,4.6,3.25),white)
B(machines,'cabinet_panel',(.46,.035,.55),(6.85,4.25,3.65),darksteel)
scene.include('machines', machines)

# Reflective insulated process ductwork with compact bend paths.
ducts = Asset('insulated_ductwork')
pipe(ducts,'large_exhaust',[(3.15,4.0,4.98),(3.15,4.0,5.5),
                            (3.0,4.0,5.72),(2.72,4.0,5.78),
                            (1.85,4.0,5.78)],.21)
pipe(ducts,'left_exhaust',[(-3.7,4.0,4.42),(-3.7,4.0,5.05),
                           (-3.45,4.0,5.28),(-2.1,4.0,5.20),
                           (-1.65,4.0,4.65)],.18)
pipe(ducts,'long_process',[(-6.6,5.0,4.0),(-4.7,5.0,4.2),
                            (-2.5,5.0,4.1),(-.2,5.0,4.0),
                            (1.6,5.0,4.0)],.12)
pipe(ducts,'right_link',[(4.1,4.5,4.1),(5.1,4.5,4.1),(5.6,5,3.9),
                          (7.1,5.4,3.9)],.12)
for x in (-4, 0, 4):
    R(ducts,'hanger_%s'%x,(x,5.0,4.2),(x,5.0,6.5),.025,darksteel)
scene.include('ducts',ducts)

# Green receiver tank standing in front of the platform.
tank = Asset('green_vertical_receiver')
tx, ty = -1.85, -.05
R(tank,'cylindrical_body',(tx,ty,.45),(tx,ty,1.98),.52,green)
tank.include('top_cap', resized(ball(.52, center=(tx,ty,1.98), color=green), (1,1,.30)))
tank.include('bottom_cap', resized(ball(.52, center=(tx,ty,.45), color=green), (1,1,.25)))
for i in range(3):
    ang = i*2*pi/3
    x = tx+.35*cos(ang)
    y = ty+.35*sin(ang)
    R(tank,'leg_%d'%i,(x,y,.05),(x,y,.5),.055,steel)
R(tank,'top_nozzle',(tx,ty,2.1),(tx,ty,2.38),.10,green)
R(tank,'side_pipe',(tx+.45,ty,1.55),(tx+.78,ty,1.55),.07,silver)
scene.include('tank',tank)

# Foreground conveyor: open frame, blue roller beds, side guide rails and legs.
conveyor = Asset('blue_roller_conveyor')
# Main line runs across the foreground, with several short transverse rollers.
B(conveyor,'main_bed',(10.5,1.25,.13),(-3.0,-4.7,.78),silver)
B(conveyor,'blue_belt',(10.3,1.05,.035),(-3.0,-4.7,.86),blue)
for y in (-5.34,-4.06):
    B(conveyor,'long_guide_%s'%y,(10.6,.07,.16),(-3.0,y,.94),brightmetal)
for i in range(19):
    x=-8.0+i*.55
    R(conveyor,'roller_%02d'%i,(x,-5.25,.90),(x,-4.15,.90),.035,brightmetal)
for x in (-7.7,-5.0,-2.3,0.4,2.0):
    for y in (-5.20,-4.20):
        B(conveyor,'frame_leg_%s_%s'%(x,y),(.10,.10,.78),(x,y,.39),silver)
# Return line behind, connecting into the equipment area.
B(conveyor,'return_bed',(5.7,1.0,.14),(-.3,-2.6,.85),silver)
B(conveyor,'return_blue',(5.5,.83,.035),(-.3,-2.6,.94),blue)
for y in (-3.12,-2.08):
    B(conveyor,'return_guide_%s'%y,(5.8,.06,.15),(-.3,y,1.02),brightmetal)
for i in range(10):
    x=-2.8+i*.55
    R(conveyor,'return_roller_%d'%i,(x,-3.05,.98),(x,-2.15,.98),.03,brightmetal)
for x in (-2.5,0,2.2):
    for y in (-2.98,-2.22):
        B(conveyor,'return_leg_%s_%s'%(x,y),(.09,.09,.85),(x,y,.425),silver)
B(conveyor,'drive_motor',(.55,.40,.38),(2.0,-3.35,.48),steel)
scene.include('conveyor',conveyor)

realize(scene)

# Material families: preserve SceneAct object colors while adding representative finishes.
for material in bpy.data.materials:
    if not material.use_nodes:
        material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        color = tuple(material.diffuse_color[:3])
        if color[1] > color[0]*1.5 and color[1] > color[2]*1.05:
            bsdf.inputs['Roughness'].default_value = .24
            bsdf.inputs['Metallic'].default_value = .18
        elif max(color)-min(color) < .09 and color[0] > .38:
            bsdf.inputs['Metallic'].default_value = .68
            bsdf.inputs['Roughness'].default_value = .29
        else:
            bsdf.inputs['Roughness'].default_value = .43
            bsdf.inputs['Metallic'].default_value = .16

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.65,.72,.78,1)
background.inputs['Strength'].default_value = .65

# Original photograph aspect is retained for both projection and final framing.
sc.render.resolution_x = 1920
sc.render.resolution_y = 1001
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
camera_position = (11.8,-19.8,8.4)
camera_target = (-.4,2.0,2.85)
camera_lens = 36
set_view(camera_position,camera_target,lens=camera_lens)
area_emitter((-6,-4,6.3), power=1800, size=7, target=(0,2,1.5))
area_emitter((3,3,6.4), power=1300, size=6, target=(0,2,1.5))
area_emitter((-7,4,4.7), power=1100, size=5, target=(0,3,2.0))

# Small projection check. These physical landmarks are approximate and not forced
# to image-border intersections. There is no prior camera or geometry edit.
anchors = [
    ('left window top', (-8.89,-1.2,4.175), (.14,.34)),
    ('large machine top', (2.95,3.85,5.0), (.68,.30)),
    ('tank top', (tx,ty,2.14), (.40,.53)),
    ('near conveyor guide', (-7.7,-5.34,.94), (.08,.85)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
    y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
print('Landmark: reference -> projected')
for name, p, ref in anchors:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, '->', None if uv is None else tuple(round(v,3) for v in uv))
