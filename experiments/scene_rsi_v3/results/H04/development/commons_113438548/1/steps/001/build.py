# Reference inventory and anchors (normalized image coordinates, x right, y down):
# Main cream pillar/cabinet: x=.16-.82, y=.00-1.00. Its right edge overlaps
# the window and bench. Dark framed tool display: x=.25-.76, y=.06-.64.
# Upper handwheel: center (.37,.15), radius .075; four small dark wheels extend
# from (.49,.15) to (.70,.16). Horizontal tool rack occupies (.29,.23)-(.70,.28).
# Middle tools, rings and a bulky dark vise occupy (.33,.35)-(.73,.59).
# Lower black rails at y=.68 and .83; two dark circular chucks centered roughly
# (.42,.83) and (.67,.83), with a hanging crank below the right chuck.
# Red door fills the left edge x=0-.18; pale wall surrounds it. Bright arched
# window in background at x=.78-1, y=.04-.46, partly hidden by the cabinet.
# A dark wooden bench crosses the window below it. Floor appears at lower right.
# Top pipe crosses the upper edge and turns toward the back on the right.
# Vertical frame edges are nearly vertical; horizontal edges slope slightly down
# to the right. The cabinet front occludes the window and bench.
# Window's far-right boundary and some machinery are cropped or occluded.
#
# Estimated primitive expansion: about 170 meshes, including 64 wheel rim
# segments and spokes, and approximately 20 rods for window/pipe/rack details.
# All dimensions and camera values below are independently adjustable.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene('Workshop display')
cream = (0.66, 0.63, 0.51)
wall = (0.70, 0.66, 0.54)
dark = (0.055, 0.055, 0.046)
iron = (0.13, 0.13, 0.11)
iron_mid = (0.21, 0.20, 0.17)
rust = (0.42, 0.16, 0.10)
glass = (0.75, 0.85, 0.86)
wood = (0.28, 0.16, 0.105)

def add(asset, name, node):
    asset.include(name, node)

def segment(asset, name, a, b, radius, color):
    add(asset, name, rod(radius, start=a, end=b, color=color))

def wheel(asset, name, x, y, z, r, spoke_count=5, rim=.025, hub=.045, color=iron):
    part = Asset(name)
    n = 16
    for i in range(n):
        a = 2 * math.pi * i / n
        b = 2 * math.pi * (i + 1) / n
        segment(part, 'rim_%02d' % i,
                (x + r*math.cos(a), y, z + r*math.sin(a)),
                (x + r*math.cos(b), y, z + r*math.sin(b)), rim, color)
    for i in range(spoke_count):
        a = 2 * math.pi * i / spoke_count
        segment(part, 'spoke_%02d' % i, (x, y, z),
                (x + r*.91*math.cos(a), y, z + r*.91*math.sin(a)),
                rim*.80, color)
    segment(part, 'hub', (x, y-.018, z), (x, y+.025, z), hub, color)
    asset.include(name, part)

# Architectural envelope. The forward face of the principal pillar is at y=0.
architecture = Asset('architecture')
add(architecture, 'floor', box((10, 9, .08), center=(0, 1, -.045),
                                color=(.53, .53, .47)))
add(architecture, 'back_wall', box((7, .12, 4), center=(0, .72, 2),
                                    color=wall))
add(architecture, 'pillar_body', box((1.68, .40, 3.85),
                                      center=(0, .15, 1.925), color=cream))
add(architecture, 'pillar_right_return', box((.15, .47, 3.85),
                                               center=(.84, .17, 1.925),
                                               color=(.62,.60,.51)))
add(architecture, 'upper_beam', box((7, .28, .20), center=(0, .32, 3.72),
                                     color=(.61,.58,.47)))
scene.include('architecture', architecture)

door = Asset('red painted door')
add(door, 'door slab', box((.79, .06, 3.55), center=(-1.29, .58, 1.77), color=rust))
add(door, 'dark jamb', box((.07, .11, 3.6), center=(-.88, .50, 1.8), color=(.25,.12,.08)))
for x in (-1.60, -1.00):
    add(door, 'stile_%s' % x, box((.035,.035,3.10), center=(x,.525,1.81), color=(.48,.20,.13)))
for z in (.30, 1.68, 3.28):
    add(door, 'rail_%s' % z, box((.61,.035,.04), center=(-1.30,.525,z), color=(.48,.20,.13)))
scene.include('door', door)

window = Asset('arched window')
# Bright rectangular glazing with upper curved outline approximated by short bars.
add(window, 'glazing', box((1.15,.045,1.48), center=(1.43,.635,2.50), color=glass))
add(window, 'left jamb', box((.065,.09,1.55), center=(.86,.58,2.50), color=dark))
add(window, 'right jamb', box((.065,.09,1.55), center=(2.00,.58,2.50), color=dark))
add(window, 'sill', box((1.25,.16,.085), center=(1.43,.56,1.74), color=(.18,.18,.16)))
add(window, 'top rail', box((.94,.075,.06), center=(1.43,.58,3.25), color=dark))
for x in (1.23, 1.62):
    add(window, 'mullion_%s' % x, box((.045,.065,1.47), center=(x,.57,2.50), color=dark))
for z in (2.12, 2.67):
    add(window, 'crossbar_%s' % z, box((1.1,.065,.035), center=(1.43,.57,z), color=dark))
segment(window, 'arch_left', (.86,.58,3.18), (1.05,.58,3.37), .033, dark)
segment(window, 'arch_center', (1.05,.58,3.37), (1.76,.58,3.37), .033, dark)
segment(window, 'arch_right', (1.76,.58,3.37), (2.00,.58,3.18), .033, dark)
scene.include('window', window)

bench = Asset('background bench')
add(bench, 'top', box((2.0,.52,.12), center=(1.65,.30,1.47), color=wood))
add(bench, 'dark front apron', box((2,.08,.19), center=(1.65,.02,1.34), color=(.12,.085,.06)))
add(bench, 'lower shelf', box((1.9,.45,.09), center=(1.65,.32,1.08), color=(.20,.13,.09)))
for x in (.94, 2.31):
    add(bench, 'leg_%s' % x, box((.11,.12,1.02), center=(x,.39,.55), color=(.16,.11,.08)))
scene.include('bench', bench)

display = Asset('framed tool display')
# Wide dark outer frame and inset pale backing.
add(display, 'backboard', box((1.32,.06,2.27), center=(0,-.083,2.34), color=(.69,.69,.61)))
for x in (-.70,.70):
    add(display, 'outer vertical %s' % x, box((.105,.12,2.46), center=(x,-.12,2.35), color=dark))
    add(display, 'inner vertical %s' % x, box((.025,.025,2.30), center=(x*.92,-.192,2.35), color=iron_mid))
for z in (1.13,3.57):
    add(display, 'outer horizontal %s' % z, box((1.49,.12,.10), center=(0,-.12,z), color=dark))
    add(display, 'inner horizontal %s' % z, box((1.33,.025,.025), center=(0,-.193,z+(.065 if z<2 else -.065)), color=iron_mid))

# Top row: open-spoked wheel and four small round pulley disks.
wheel(display, 'large upper handwheel', -.43,-.205,3.20,.215,5,.025,.040)
for i, (x,r) in enumerate(((-.06,.095),(.17,.078),(.37,.072),(.53,.063))):
    segment(display, 'pulley disk %d' % i, (x,-.202,3.19), (x,-.255,3.19), r, iron)
    segment(display, 'pulley hub %d' % i, (x,-.26,3.19), (x,-.275,3.19), r*.30, (.37,.35,.29))

# Upper long rack with hooks and a projecting black bar.
add(display, 'tool rack', box((1.12,.095,.105), center=(-.09,-.18,2.82), color=(.20,.15,.11)))
for i,x in enumerate((-.48,-.30,-.11,.09,.27)):
    segment(display, 'rack hook %d' % i, (x,-.25,2.79), (x,-.25,2.72), .012, iron_mid)
add(display, 'upper right horizontal bar', box((.43,.055,.065), center=(.34,-.24,2.73), color=dark))
segment(display, 'upper dangling tool', (.53,-.25,2.73), (.56,-.25,2.49), .015, dark)

# Individual hanging tools.
segment(display, 'middle horizontal handle', (-.35,-.25,2.30), (.30,-.25,2.30), .017, iron)
segment(display, 'central hanging shaft', (-.02,-.27,2.34), (-.02,-.27,2.07), .022, iron)
segment(display, 'central angled jaw', (-.02,-.27,2.20), (.025,-.27,2.34), .015, iron_mid)
add(display, 'left bracket', box((.22,.07,.12), center=(-.48,-.22,2.16), color=iron))
for x in (-.55,-.42):
    segment(display, 'left pin %s' % x, (x,-.26,2.21), (x,-.26,2.09), .022, dark)
wheel(display, 'hanging ring', -.49,-.25,1.66,.065,0,.014,.012,iron)
segment(display, 'pliers left', (-.05,-.25,1.79), (-.10,-.25,1.52), .018, iron)
segment(display, 'pliers right', (-.05,-.25,1.79), (.005,-.25,1.53), .018, iron)
segment(display, 'pliers pivot', (-.05,-.28,1.72), (-.05,-.30,1.72), .033, iron_mid)
add(display, 'bottom loose piece', box((.19,.07,.04), center=(-.34,-.23,1.31), color=dark))

# Bulky bench vise on the lower right of the framed display.
vise = Asset('mounted vise')
add(vise, 'back plate', box((.22,.07,.12), center=(.46,-.23,2.17), color=iron))
add(vise, 'vertical post', box((.075,.10,.46), center=(.49,-.29,1.98), color=iron))
add(vise, 'upper jaw', box((.39,.21,.10), center=(.42,-.34,1.85), color=dark))
add(vise, 'left jaw cheek', box((.10,.22,.19), center=(.27,-.34,1.74), color=iron))
add(vise, 'right jaw cheek', box((.10,.22,.19), center=(.57,-.34,1.74), color=iron))
add(vise, 'body', box((.32,.22,.15), center=(.42,-.34,1.63), color=iron))
add(vise, 'pedestal', box((.20,.16,.22), center=(.42,-.32,1.48), color=iron))
add(vise, 'foot', box((.42,.25,.08), center=(.42,-.32,1.35), color=dark))
segment(vise, 'screw axle', (.42,-.47,1.75), (.42,-.58,1.75), .055, iron_mid)
segment(vise, 'cross handle', (.26,-.58,1.75), (.58,-.58,1.75), .014, iron)
wheel(vise, 'small right lever wheel', .58,-.29,2.17,.070,4,.012,.022)
display.include('vise', vise)
scene.include('display', display)

lower = Asset('lower machine display')
for z in (1.02,.43):
    add(lower, 'black rail %s' % z, box((1.56,.055,.13), center=(0,-.10,z), color=dark))
add(lower, 'brass label', box((.28,.025,.19), center=(.05,-.145,1.12), color=(.57,.41,.15)))
segment(lower, 'projecting handle', (.38,-.17,1.11), (.54,-.35,1.02), .045, dark)

# Broad solid chucks with radial slots and projecting jaws.
for idx,(x,z,r) in enumerate(((-.34,.46,.34),(.42,.46,.30))):
    segment(lower, 'chuck disk %d' % idx, (x,-.15,z), (x,-.23,z), r, iron)
    segment(lower, 'chuck hub %d' % idx, (x,-.25,z), (x,-.29,z), .075, iron_mid)
    for j in range(6):
        a = 2*math.pi*j/6 + .18
        segment(lower, 'chuck groove %d %d' % (idx,j),
                (x+.11*math.cos(a),-.245,z+.11*math.sin(a)),
                (x+r*.86*math.cos(a),-.245,z+r*.86*math.sin(a)), .013, dark)
for i,(dx,dz) in enumerate(((-.13,.09),(.13,.09),(-.13,-.09),(.13,-.09))):
    add(lower, 'right chuck jaw %d' % i,
        box((.13,.09,.11), center=(.42+dx,-.30,.46+dz), color=iron_mid))
segment(lower, 'hanging crank stem', (.42,-.22,.20), (.42,-.22,.02), .016, dark)
segment(lower, 'hanging crank foot', (.21,-.22,.02), (.61,-.22,.02), .018, dark)
scene.include('lower machinery', lower)

pipe = Asset('overhead pipe')
segment(pipe, 'long horizontal', (-1.8,.12,3.82), (.10,.12,3.82), .045, (.15,.22,.20))
segment(pipe, 'elbow', (.10,.12,3.82), (.25,.16,3.78), .047, (.15,.22,.20))
segment(pipe, 'rightward run', (.25,.16,3.78), (1.54,.42,3.88), .047, (.15,.22,.20))
scene.include('overhead pipe', pipe)

realize(scene)

# Camera and major asset dimensions are independent parameters.
CAMERA_POSITION = (2.15, -9.8, 2.72)
CAMERA_TARGET = (0.08, 0.0, 1.90)
CAMERA_LENS = 43
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

sc = bpy.context.scene
sc.render.resolution_x = 341
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
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
background.inputs['Color'].default_value = (.72,.72,.67,1)
background.inputs['Strength'].default_value = .65

area_emitter((0,-4,5.5), power=550, size=5, target=(0,0,1.8))
area_emitter((3,-1,4), power=250, size=3, target=(.5,0,1.7))

# Geometry landmarks, independently estimated from the photograph.
landmarks = [
    ('frame top left', (-.75,-.18,3.57), (.25,.06)),
    ('frame bottom right', (.75,-.18,1.13), (.76,.64)),
    ('large wheel center', (-.43,-.21,3.20), (.37,.15)),
    ('lower left chuck', (-.34,-.24,.46), (.42,.83)),
    ('window sill right', (2.0,.56,1.74), (1.0,.46)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
    y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
print('landmark | reference | projected')
for name, point, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v,3) for v in uv))
