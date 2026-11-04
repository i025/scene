from sceneact import *
import bpy
import math

CAMERA_POSITION = (-6.1, -4.9, 1.95)
CAMERA_TARGET = (.05, .65, 1.95)
CAMERA_LENS = 47
CAMERA_SHIFT = (0, -.085)
ISLAND_WIDTH, ISLAND_DEPTH = 2.55, 1.08
HOOD_WIDTH, HOOD_DEPTH = 1.10, .87
HOOD_BOTTOM, HOOD_TOP = 2.02, 3.73

scene = Scene("Kitchen")
ivory = (.66, .67, .63)
counter = (.79, .80, .74)
black = (.004, .006, .005)
charcoal = (.009, .012, .010)
steel = (.36, .39, .38)
wood = (.22, .115, .046)

def B(asset, name, size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    asset.include(name, box(size=size, center=center, color=color))

architecture = Asset("Architecture")
B(architecture, "floor", (10, 9, .12), (0, .2, -.06), (.60, .59, .54))
B(architecture, "back_wall", (9, .16, 3.8),
  (0, 2.40, 1.9), (.26, .28, .26))
# Outside the camera's foreground rays.
B(architecture, "left_wall", (.15, 7, 3.8),
  (-6.8, .2, 1.9), (.36, .37, .33))
B(architecture, "ceiling", (10, 9, .12),
  (0, .2, 3.81), (.012, .017, .015))
for i, x in enumerate([-3, -1.8, -.6, .6, 1.8, 3]):
    B(architecture, "joint_x_%d" % i, (.008, 8.8, .002),
      (x, .2, .002), (.40, .41, .38))
for i, y in enumerate([-2.8, -1.6, -.4, .8, 2.0]):
    B(architecture, "joint_y_%d" % i, (9.8, .008, .002),
      (0, y, .002), (.40, .41, .38))
for i, y in enumerate([-1.6, -.75, .15, 1.05, 1.95]):
    B(architecture, "joist_%d" % i, (9, .095, .20),
      (0, y, 3.63), (.010, .015, .013))
for i, x in enumerate([-.9, 1.55]):
    B(architecture, "beam_%d" % i, (.25, 8.8, .32),
      (x, .2, 3.55), (.016, .021, .019))
scene.include("architecture", architecture)

posts = Asset("Timber supports")
POST_CENTER = (-2.95, -1.25, 1.90)
POST_SECTION = .30
B(posts, "foreground_post", (POST_SECTION, POST_SECTION, 3.8),
  POST_CENTER, wood)
B(posts, "far_post", (.19, .22, 3.65),
  (2.72, 2.0, 1.825), wood)
scene.include("posts", posts)

kitchen = Asset("Rear kitchen cabinetry")
B(kitchen, "left_tall_carcass", (.92, .66, 2.30),
  (-2.13, 1.89, 1.15), black)
for i, z in enumerate([.58, 1.72]):
    B(kitchen, "left_door_%d" % i, (.88, .035, 1.12),
      (-2.13, 1.54, z), charcoal)
B(kitchen, "toe", (3.45, .54, .13),
  (-.05, 1.91, .095), (.012, .016, .014))
B(kitchen, "base", (3.5, .64, .78), (-.05, 1.90, .51), black)
B(kitchen, "worktop", (3.56, .71, .045),
  (-.05, 1.86, .923), (.17, .18, .16))
for i, x in enumerate([-1.35, -.50, .35, 1.20]):
    B(kitchen, "base_front_%d" % i, (.825, .025, .72),
      (x, 1.564, .53), charcoal)
B(kitchen, "backsplash", (3.45, .045, .75),
  (-.05, 2.238, 1.32), (.012, .017, .014))
B(kitchen, "upper_run", (3.45, .43, .52),
  (-.05, 2.04, 1.99), black)
for i, x in enumerate([-1.34, -.48, .38, 1.24]):
    B(kitchen, "upper_front_%d" % i, (.84, .025, .49),
      (x, 1.812, 1.99), (.008, .013, .010))
B(kitchen, "warm_niche", (2.24, .025, .34),
  (-.54, 2.202, 1.12), (.31, .25, .21))
B(kitchen, "light_strip", (2.24, .035, .016),
  (-.54, 1.829, 1.435), (.94, .80, .59))
B(kitchen, "right_bank", (1.17, .76, 2.34),
  (1.90, 1.96, 1.17), black)
B(kitchen, "right_door", (.48, .035, 2.27),
  (2.23, 1.561, 1.17), charcoal)
B(kitchen, "oven_column", (.64, .035, 2.27),
  (1.64, 1.56, 1.17), (.012, .015, .012))
for i, z in enumerate([1.02, 1.51]):
    B(kitchen, "oven_frame_%d" % i, (.57, .05, .43),
      (1.64, 1.527, z), steel)
    B(kitchen, "oven_glass_%d" % i, (.48, .014, .29),
      (1.64, 1.495, z-.025), (.018, .034, .039))
    B(kitchen, "oven_control_%d" % i, (.49, .017, .055),
      (1.64, 1.480, z+.15), (.15, .17, .16))
    kitchen.include("oven_handle_%d" % i,
        rod(radius=.014, start=(1.42, 1.451, z+.095),
            end=(1.86, 1.451, z+.095), color=(.55, .57, .55)))
scene.include("kitchen", kitchen)

island = Asset("Island with drawers and sink")
ix, iy = .15, -.05
B(island, "plinth", (2.40, .93, .10),
  (ix, iy+.025, .08), (.15, .17, .16))
B(island, "body", (ISLAND_WIDTH, ISLAND_DEPTH, .83),
  (ix, iy, .545), ivory)
B(island, "left_end", (.035, 1.09, .88),
  (ix-1.283, iy, .55), (.59, .61, .58))
fy = iy-ISLAND_DEPTH/2-.015
for i, z in enumerate([.275, .55, .825]):
    B(island, "drawer_%d" % i, (2.48, .028, .259),
      (ix+.018, fy, z), ivory)
    B(island, "reveal_%d" % i, (2.47, .015, .012),
      (ix+.018, fy-.006, z+.134), (.27, .29, .27))

sx, sy, sw, sd = .60, .13, .60, .39
le, re = ix-1.30, ix+1.30
fe, be = iy-.565, iy+.565
B(island, "counter_left", (sx-sw/2-le, 1.13, .045),
  ((le+sx-sw/2)/2, iy, .985), counter)
B(island, "counter_right", (re-sx-sw/2, 1.13, .045),
  ((re+sx+sw/2)/2, iy, .985), counter)
B(island, "counter_front", (sw, sy-sd/2-fe, .045),
  (sx, (fe+sy-sd/2)/2, .985), counter)
B(island, "counter_back", (sw, be-sy-sd/2, .045),
  (sx, (be+sy+sd/2)/2, .985), counter)
B(island, "sink_bottom", (.57, .36, .015),
  (sx, sy, .915), (.37, .40, .38))
for i, x in enumerate([sx-.292, sx+.292]):
    B(island, "sink_side_%d" % i, (.015, .39, .073),
      (x, sy, .955), (.56, .59, .56))
for i, y in enumerate([sy-.187, sy+.187]):
    B(island, "sink_end_%d" % i, (.58, .015, .073),
      (sx, y, .955), (.56, .59, .56))
island.include("faucet", sweep_tube(
    points=[(.60,.40,1.005), (.60,.40,1.22),
            (.60,.36,1.27), (.60,.23,1.27), (.60,.20,1.22)],
    radius=.014, color=(.58,.62,.60)))
island.include("lever", rod(radius=.009,
    start=(.65,.40,1.025), end=(.65,.40,1.115),
    color=(.57,.60,.58)))
for i, y in enumerate([-.27, .12]):
    B(island, "hob_long_%d" % i, (.65,.008,.003),
      (-.56,y,1.010), (.49,.51,.47))
for i, x in enumerate([-.885, -.235]):
    B(island, "hob_short_%d" % i, (.008,.39,.003),
      (x,-.075,1.010), (.49,.51,.47))
scene.include("island", island)

hood = Asset("Suspended extractor")
B(hood, "enclosure", (HOOD_WIDTH, HOOD_DEPTH, HOOD_TOP-HOOD_BOTTOM),
  (-.10,.32,(HOOD_TOP+HOOD_BOTTOM)/2), (.73,.72,.65))
B(hood, "plate", (1.10,.87,.022),
  (-.10,.32,HOOD_BOTTOM), (.55,.56,.51))
B(hood, "filter", (.73,.51,.008),
  (-.10,.32,HOOD_BOTTOM-.014), (.22,.25,.23))
scene.include("hood", hood)

kettle = Asset("Red kettle")
kettle.include("body", ball(radius=.092,
    center=(-.52,1.82,1.035), color=(.62,.006,.025)))
B(kettle, "base", (.16,.13,.025), (-.52,1.82,.955), black)
kettle.include("handle", sweep_tube(
    points=[(-.60,1.82,1.07), (-.60,1.82,1.16),
            (-.48,1.82,1.18), (-.43,1.82,1.10)],
    radius=.012, color=(.035,.025,.025)))
kettle.include("spout", rod(radius=.022,
    start=(-.45,1.81,1.05), end=(-.40,1.81,1.10),
    color=(.13,.14,.13)))
scene.include("kettle", kettle)

realize(scene)
set_view(CAMERA_POSITION, CAMERA_TARGET,
         lens=CAMERA_LENS, shift=CAMERA_SHIFT)
camera = bpy.context.scene.camera
camera.data.sensor_fit = 'VERTICAL'
camera.data.sensor_height = 32

for mat in bpy.data.materials:
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value = .52

# Explicit timber assignment avoids relying on material names or color conversion.
timber = bpy.data.materials.new("Vertical brown timber grain")
timber.use_nodes = True
nodes, links = timber.node_tree.nodes, timber.node_tree.links
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value = .62
coords = nodes.new("ShaderNodeTexCoord")
mapping = nodes.new("ShaderNodeVectorMath")
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (7, 7, .28)
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 4
noise.inputs["Detail"].default_value = 3
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .18
ramp.color_ramp.elements[0].color = (.075,.031,.010,1)
ramp.color_ramp.elements[1].position = .82
ramp.color_ramp.elements[1].color = (.31,.17,.070,1)
links.new(coords.outputs["Generated"], mapping.inputs[0])
links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], ramp.inputs[0])
links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    dims = obj.dimensions
    if (abs(dims.z-3.8) < .015 and
        abs(dims.x-POST_SECTION) < .015 and
        abs(dims.y-POST_SECTION) < .015) or (
        abs(dims.z-3.65) < .015 and
        abs(dims.x-.19) < .015 and abs(dims.y-.22) < .015):
        obj.data.materials.clear()
        obj.data.materials.append(timber)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("Kitchen world")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.28,.31,.32,1)
world.node_tree.nodes["Background"].inputs[1].default_value = .32
area_emitter((-2.3,-3.5,3.35), power=850, size=4,
             target=(0,.2,1.2), color=(1,.95,.86))
area_emitter((2.7,-.4,3.2), power=450, size=2.5,
             target=(0,0,1), color=(.89,.94,1))
area_emitter((-.65,1.78,1.43), power=38, size=1.7,
             target=(-.65,2.18,1.07), color=(1,.72,.50))
area_emitter((-2.5,1,3.25), power=160, size=1.5,
             target=(-1,1.8,1.1), color=(1,.93,.80))

# Source checks: positive finite box sizes; distinct keyword rod endpoints;
# distinct consecutive sweep points; unique indexed repeated keys.
# No fillet_box, external assets, rendering, saving, or runner-setting changes.
# All geometry stays under meaningful assets; customization follows realize().
