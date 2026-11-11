# Reference inventory and estimated image anchors:
# Roof and dark beams occupy y=0.00–0.35, with shallow diagonal edges.
# Tall strip windows occupy x=0.00–0.23, y=0.34–0.64.
# Raised machines and platform extend across x=0.20–0.94, y=0.30–0.75.
# Main machine: x=0.61–0.79, y=0.30–0.64; duct rises to y=0.22.
# Yellow rails cross the machine fronts around y=0.44–0.60.
# Green receiver tank: x=0.36–0.45, y=0.53–0.79, overlapping platform.
# Blue/silver conveyor fills x=0.00–0.62, y=0.73–1.00 and is cropped.
# Left, middle and right stairways create prominent diagonal yellow contours.
# Far-side machinery and connections are partially occluded and uncertain.
#
# Comparison with first render:
# 1. The first render shows the whole building exterior against gray, while the
#    reference fills the frame with the interior. The roof and columns frame a
#    small distant equipment line. Move the camera inside the hall and closer.
# 2. The first render's machine top is about (0.62,0.41), versus (0.68,0.31);
#    the near conveyor endpoint is about (0.07,0.67), versus (0.02,0.94).
#    Moving closer enlarges foreground and machinery, with foreground changing
#    more strongly; aim and lens are checked below with actual projections.
# 3. The first render's window top is about (0.38,0.35), versus (0.10,0.34).
#    Place the glazing along the left wall, where it is visible from inside.
# 4. Roof edges in the render form an exterior outline; the photograph has
#    continuous ceiling and interior beams. Extend roof beyond the camera.
# 5. The rendered equipment has excessive empty floor in front and dark posts
#    occluding the line. The closer viewpoint and removal of foreground posts
#    from the sightline enlarge the conveyor and restore the observed overlaps.
# Projection points below are world-space geometry points; their numerical
# projections are separate from these observed silhouette estimates.
#
# Estimated primitive meshes: architecture 61, platform and stairs 140,
# machines 55, ductwork 27, tank 8, foreground conveyor and tables 100:
# approximately 391. Each primitive creates one mesh; no Boolean operations.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Steel workshop installation")

steel = (0.42, 0.46, 0.46)
silver = (0.65, 0.68, 0.67)
bright = (0.79, 0.82, 0.81)
dark = (0.105, 0.125, 0.13)
beam = (0.07, 0.085, 0.085)
wall = (0.19, 0.21, 0.21)
roof = (0.27, 0.29, 0.28)
yellow = (0.95, 0.64, 0.015)
green = (0.012, 0.32, 0.22)
floor_green = (0.12, 0.31, 0.24)
blue = (0.055, 0.25, 0.61)
white = (0.78, 0.81, 0.79)
window = (0.68, 0.79, 0.84)

def B(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def R(asset, name, a, b, radius, color):
    asset.include(name, rod(radius=radius, start=a, end=b, color=color))

# A long hall surrounds the viewpoint. Columns are at the side and rear
# rather than across the camera's immediate sightline.
arch = Asset("Steel framed workshop")
B(arch, "green epoxy floor", (32, 35, .14), (0, 3, -.08), floor_green)
B(arch, "profiled roof", (32, 35, .16), (0, 3, 7.35), roof)
B(arch, "far wall", (32, .18, 7.3), (0, 20.4, 3.65), wall)
B(arch, "window wall", (.18, 35, 7.3), (-12.0, 3, 3.65), wall)
B(arch, "right side wall", (.18, 35, 7.3), (15.9, 3, 3.65), wall)

# Vertical strip windows run along the left exterior wall.
for i, y in enumerate([-8, -4.8, -1.6, 1.6, 4.8, 8.0, 11.2, 14.4, 17.6]):
    B(arch, "strip glazing %d" % i, (.045, .85, 3.3),
      (-11.88, y, 3.0), window)
    B(arch, "window central mullion %d" % i, (.06, .035, 3.3),
      (-11.84, y, 3.0), beam)
    for j, z in enumerate([1.8, 2.6, 3.4, 4.2]):
        B(arch, "window crossbar %d %d" % (i, j),
          (.06, .85, .035), (-11.82, y, z), beam)

for i, y in enumerate([-11, -4, 3, 10, 17]):
    for j, x in enumerate([-11.8, 15.7]):
        B(arch, "wall column %d %d" % (i, j),
          (.28, .28, 7.25), (x, y, 3.62), beam)
    B(arch, "transverse roof girder %d" % i,
      (27.5, .24, .30), (1.95, y, 7.05), beam)
for i, x in enumerate([-11.5, -6, -.5, 5, 10.5, 15.5]):
    B(arch, "longitudinal roof beam %d" % i,
      (.22, 34, .24), (x, 3, 7.05), beam)
for i, y in enumerate([-6, 0, 6, 12, 18]):
    B(arch, "ceiling light strip %d" % i,
      (2.4, .12, .035), (2, y, 7.22), white)
scene.include("workshop structure", arch)

# Raised platform and open railings.
platform = Asset("Raised steel operating platform")
B(platform, "steel deck", (17.2, 3.1, .18), (.1, 3.8, 2.38), steel)
B(platform, "front edge beam", (17.2, .15, .38), (.1, 2.25, 2.20), dark)
B(platform, "rear edge beam", (17.2, .15, .32), (.1, 5.34, 2.23), steel)
for i, x in enumerate([-8.2, -5.5, -2.8, 0, 2.8, 5.5, 8.3]):
    for j, y in enumerate([2.4, 5.2]):
        B(platform, "deck support %d %d" % (i, j),
          (.15, .15, 2.30), (x, y, 1.15), steel)

for seg, (x1, x2) in enumerate([(-8.4,-6.8), (-5.4,-2.1),
                                 (-.8,3.0), (4.4,8.6)]):
    for j, z in enumerate([2.92, 3.48]):
        R(platform, "front handrail %d %d" % (seg,j),
          (x1,2.20,z), (x2,2.20,z), .035, yellow)
    n = max(1, int((x2-x1)/.70))
    for j in range(n+1):
        x = x1+(x2-x1)*j/n
        R(platform, "front rail post %d %d" % (seg,j),
          (x,2.20,2.46), (x,2.20,3.49), .029, yellow)
for z in [2.92,3.48]:
    R(platform, "rear handrail %.2f" % z, (-8.4,5.36,z),
      (8.6,5.36,z), .03, yellow)
for i in range(18):
    x = -8.4+i
    R(platform, "rear rail post %d" % i,
      (x,5.36,2.46), (x,5.36,3.48), .025, yellow)

def stairs(label, x, y0, y1, width):
    z0, z1 = .10, 2.45
    for side in [-1,1]:
        xx = x+side*width/2
        R(platform, label+" stringer "+str(side),
          (xx,y0,z0), (xx,y1,z1), .055, yellow)
        R(platform, label+" handrail "+str(side),
          (xx,y0,z0+.95), (xx,y1,z1+.95), .035, yellow)
        for j in range(4):
            t = j/3
            y = y0+(y1-y0)*t
            z = z0+(z1-z0)*t
            R(platform, label+" baluster %d %d"%(side,j),
              (xx,y,z), (xx,y,z+.95), .025, yellow)
    for j in range(9):
        t = (j+.5)/9
        y = y0+(y1-y0)*t
        z = z0+(z1-z0)*t
        B(platform, label+" tread %d"%j, (width,.26,.055),
          (x,y,z), bright)

stairs("left staircase", -6.1, -.75, 2.20, 1.15)
stairs("center staircase", -1.45, -.75, 2.20, 1.10)
stairs("right staircase", 3.7, -.85, 2.20, 1.18)
scene.include("platform and stairs", platform)

machines = Asset("Stainless processing line")
def machine(label, x, y, width, depth, height):
    base = 2.48
    fy = y-depth/2-.02
    B(machines, label+" housing", (width,depth,height),
      (x,y,base+height/2), silver)
    B(machines, label+" base", (width+.15,depth+.1,.21),
      (x,y,base+.10), dark)
    B(machines, label+" top cap", (width*.92,depth*.94,.20),
      (x,y,base+height+.10), bright)
    B(machines, label+" front opening", (width*.76,.04,height*.39),
      (x,fy,base+height*.48), dark)
    B(machines, label+" lower roller", (width*.70,.08,.14),
      (x,fy-.04,base+height*.33), steel)
    for j in range(5):
        B(machines, label+" face slat %d"%j, (width*.70,.045,.027),
          (x,fy-.045,base+height*.37+j*.105), bright)
    for j, dx in enumerate([-.44,.44]):
        B(machines, label+" vertical trim %d"%j, (.065,.06,height*.75),
          (x+width*dx,fy-.02,base+height*.52), bright)
    B(machines, label+" control box", (.42,.22,.65),
      (x+width*.42,fy-.15,base+height*.52), white)

machine("main machine", 3.0, 4.1, 3.0, 2.1, 1.75)
machine("left machine", -5.4, 4.15, 2.7, 1.9, 1.35)
machine("center machine", -1.1, 4.2, 2.0, 1.7, 1.05)
machine("far right machine", 7.0, 4.25, 1.45, 1.5, 1.15)
scene.include("processing machines", machines)

ducts = Asset("Insulated duct and process piping")
def tube(label, points, radius):
    for i in range(len(points)-1):
        R(ducts, label+" section %d"%i, points[i],points[i+1],
          radius, bright)
    for i,p in enumerate(points[1:-1]):
        ducts.include(label+" elbow %d"%i,
                      ball(radius, center=p, color=silver))

tube("main duct", [(3.0,4.2,4.25),(3.0,4.2,5.25),
                   (3.2,4.2,5.52),(3.9,4.2,5.25),
                   (4.15,4.2,4.95)], .22)
tube("left duct", [(-5.4,4.3,3.85),(-5.4,4.3,4.75),
                   (-5.1,4.3,4.95),(-3.6,4.3,4.70),
                   (-3.1,4.3,4.10)], .17)
tube("connecting duct", [(-3.1,4.4,4.0),(-2.0,4.4,4.35),
                         (1.0,4.4,4.35),(1.7,4.4,4.15)], .12)
tube("rear process pipe", [(-8.0,5.6,3.8),(8.0,5.6,3.8)], .085)
for i,x in enumerate([-5,-1,3,7]):
    R(ducts, "pipe hanger %d"%i, (x,4.4,4.4), (x,4.4,7.0),
      .025, steel)
scene.include("ducts and hangers", ducts)

tank = Asset("Green vertical receiver")
tx, ty = -3.4, .65
R(tank, "cylindrical shell", (tx,ty,.43), (tx,ty,2.18), .56, green)
tank.include("rounded upper head", ball(.56, center=(tx,ty,2.18), color=green))
tank.include("rounded lower head", ball(.56, center=(tx,ty,.43), color=green))
for i,dx in enumerate([-.35,.35]):
    B(tank, "support foot %d"%i, (.14,.17,.38),
      (tx+dx,ty,.19), dark)
R(tank, "top nozzle", (tx,ty,2.65), (tx,ty,2.90), .09, steel)
R(tank, "side outlet", (tx+.50,ty,1.65), (tx+.90,ty,1.65), .07, steel)
scene.include("vertical green tank", tank)

conveyor = Asset("Foreground blue conveyor")
for lane,cy in enumerate([-4.7,-3.35]):
    B(conveyor, "blue belt %d"%lane, (13.2,1.08,.12),
      (-3.0,cy,.88), blue)
    for side in [-1,1]:
        yy = cy+side*.60
        B(conveyor, "side guide %d %d"%(lane,side),
          (13.4,.085,.21), (-3.0,yy,1.0), bright)
        for j,x in enumerate([-8.8,-5.4,-2.0,1.4,3.3]):
            B(conveyor, "leg %d %d %d"%(lane,side,j),
              (.09,.10,.87), (x,yy,.43), steel)
    for j in range(19):
        x = -9.2+j*.68
        R(conveyor, "roller %d %d"%(lane,j),
          (x,cy-.51,.96), (x,cy+.51,.96), .036, bright)
    B(conveyor, "end member %d"%lane, (.12,1.3,.16),
      (3.55,cy,.83), steel)
B(conveyor, "drive motor", (.65,.44,.38), (2.4,-2.62,.56), dark)
scene.include("conveyor line", conveyor)

utilities = Asset("Transfer tables and electrical utilities")
for i,(x,y) in enumerate([(-7.5,-1.5),(-3.0,-1.4),(.7,-1.25),(7.2,1.6)]):
    B(utilities, "transfer table frame %d"%i, (2.4,1.15,.15),
      (x,y,1.05), bright)
    for j,dx in enumerate([-.95,.95]):
        for k,dy in enumerate([-.44,.44]):
            B(utilities, "transfer table support %d %d %d"%(i,j,k),
              (.075,.075,1.0), (x+dx,y+dy,.5), steel)
B(utilities, "right electrical cabinet", (.75,.50,2.1),
  (8.0,3.8,3.52), white)
scene.include("transfer equipment", utilities)

realize(scene)

# Camera parameters are independent from asset positions and dimensions.
# A camera inside the hall removes the exterior outline and increases the
# foreground conveyor and platform's occupied image area.
CAMERA_POSITION = (4.2, -13.8, 5.4)
CAMERA_TARGET = (-.1, 3.5, 3.65)
CAMERA_LENS = 35
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

landmarks = [
    ("window top", (-11.88,1.6,4.65), (.10,.34)),
    ("machine top", (3.0,3.05,4.43), (.68,.31)),
    ("tank top", (tx,ty,2.74), (.40,.53)),
    ("near conveyor corner", (-9.6,-5.3,.99), (.02,.94)),
]

def projected():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = []
    for name, point, ref in landmarks:
        clip = proj @ cam.matrix_world.inverted() @ Vector((*point,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        result.append(None if uv is None else tuple(round(v,3) for v in uv))
    return result

# Compare the chosen view against a small upward-aim trial. The trial should
# move stationary features down; restore it so it cannot silently change framing.
base = projected()
cam = sc.camera
old_rotation = cam.rotation_euler.copy()
trial_target = Vector((CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2]+.20))
cam.rotation_euler = (trial_target - cam.location).to_track_quat('-Z','Y').to_euler()
trial = projected()
cam.rotation_euler = old_rotation
bpy.context.view_layer.update()
print("Landmark | reference estimate | chosen projection | upward-aim trial")
for i,(name,point,ref) in enumerate(landmarks):
    print(name, ref, base[i], trial[i])

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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68,.75,.78,1)
background.inputs["Strength"].default_value = .65

area_emitter((-9,-1,5.5), power=2200, size=7, target=(0,2,1.5))
area_emitter((0,-1,6.8), power=1600, size=8, target=(0,3,1.5))
area_emitter((8,5,6.8), power=1500, size=7, target=(3,3,1.5))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = tuple(mat.diffuse_color[:3])
    if max(abs(c[i]-floor_green[i]) for i in range(3)) < .03:
        bsdf.inputs["Roughness"].default_value = .20
        bsdf.inputs["Metallic"].default_value = .10
    elif any(max(abs(c[i]-v[i]) for i in range(3)) < .03
             for v in [steel,silver,bright]):
        bsdf.inputs["Metallic"].default_value = .68
        bsdf.inputs["Roughness"].default_value = .30
    elif max(abs(c[i]-yellow[i]) for i in range(3)) < .03:
        bsdf.inputs["Metallic"].default_value = .22
        bsdf.inputs["Roughness"].default_value = .38

sc.render.engine = "CYCLES"
sc.cycles.samples = 32
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
