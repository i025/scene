import bpy
import math
import random
from sceneact import *

random.seed(18)
scene = Scene("Kitchen reconstruction")

ivory = (.79, .80, .75)
stone = (.36, .36, .325)
steel = (.36, .40, .38)
chrome = (.57, .61, .57)
navy = (.006, .019, .027)

def add(name, node):
    scene.include(name, node)
    return node

def plate(size, center, radius, color):
    w, d, h = size
    thick = max(h, radius * 2.5)
    node = fillet_box((w, d, thick), radius=radius,
                      center=center, color=color)
    node.resize((1, 1, h / thick), pivot=center)
    return node

# Floorboards.
add("floor foundation", box((7, 7, .08), center=(0, 0, -.055),
                             color=(.75, .75, .69)))
for i in range(33):
    for j in range(5):
        x = -3.3 + i * .20
        y = -4 + j * 1.55 + (i % 3) * .44
        c = random.uniform(.74, .83)
        add("floorboard_%d_%d" % (i, j),
            box((.1985, 1.548, .018), center=(x, y, -.006),
                color=(c + .035, c + .025, c - .025)))

# Architecture and dark blue square tiles.
add("back wall", box((6, .12, 3.2), center=(0, .724, 1.55),
                     color=(.79, .79, .72)))
add("grout backing", box((6, .018, 1.9), center=(0, .649, 1.84),
                         color=(.48, .50, .43)))
for row in range(10):
    for col in range(31):
        t = random.uniform(.83, 1.15)
        add("tile_%d_%d" % (row, col),
            box((.197, .016, .197),
                center=(-3 + col * .202, .632, .997 + row * .202),
                color=tuple(v * t for v in navy)))

add("left wall", box((.12, 2.6, 3), center=(-1.38, .01, 1.48),
                     color=(.81, .81, .74)))
add("left door jamb", box((.055, .11, 2.35),
                          center=(-1.294, -.30, 1.175),
                          color=(.67, .66, .55)))
add("left skirting", box((.035, .58, .09),
                         center=(-1.306, .12, .055),
                         color=(.72, .71, .62)))

# Cabinet housing and recessed plinth.
add("cabinet body", box((2.64, .585, .755),
                        center=(.05, .303, .477),
                        color=(.63, .64, .58)))
add("recessed plinth", box((2.55, .47, .11),
                           center=(.05, .348, .071),
                           color=(.67, .68, .60)))
add("plinth face", box((2.54, .022, .078),
                       center=(.05, .104, .064),
                       color=(.74, .75, .67)))

left_x = -.823
for k, (bottom, top) in enumerate(((.675, .851),
                                  (.435, .670),
                                  (.116, .430))):
    add("drawer_%d" % k,
        box((.824, .035, top-bottom),
            center=(left_x, -.004, (bottom+top)/2), color=ivory))
add("middle cupboard", box((.803, .035, .735),
                           center=(.001, -.004, .484), color=ivory))
add("sink cupboard", box((.805, .035, .735),
                         center=(.812, -.004, .484), color=ivory))
add("right filler", box((.103, .036, .735),
                        center=(1.272, -.004, .484), color=ivory))

def handle(name, x, z):
    w = .215
    points = [(x-w/2, -.025, z+.009),
              (x-w/2, -.058, z-.004),
              (x-w/2+.014, -.066, z-.016),
              (x+w/2-.014, -.066, z-.016),
              (x+w/2, -.058, z-.004),
              (x+w/2, -.025, z+.009)]
    add(name, sweep_tube(points=points, radius=.009,
                         color=(.52, .54, .46)))

handle("upper drawer pull", left_x, .807)
handle("middle drawer pull", left_x, .644)
handle("lower drawer pull", left_x, .402)
handle("middle door pull", .001, .807)
handle("sink door pull", .812, .807)

# Worktop assembled around open sink apertures.
xmin, xmax = -1.35, 1.42
ymin, ymax = -.0305, .6565
a0, a1 = .478, .970
b0, b1 = .970, 1.238
af, ab = .095, .553
bf, bb = .170, .544
def counter_piece(name, x0, x1, y0, y1):
    add(name, box((x1-x0, y1-y0, .044),
                  center=((x0+x1)/2, (y0+y1)/2, .884),
                  color=stone))

counter_piece("unbroken left work surface", xmin, a0, ymin, ymax)
counter_piece("counter front of large bowl", a0, a1, ymin, af)
counter_piece("counter behind large bowl", a0, a1, ab, ymax)
counter_piece("counter front of small bowl", b0, b1, ymin, bf)
counter_piece("counter behind small bowl", b0, b1, bb, ymax)
counter_piece("counter beneath drainer", b1, xmax, ymin, ymax)

# Sink surround. Its openings remain actual open spaces.
rim_color = steel
def rim_piece(name, x0, x1, y0, y1):
    add(name, box((x1-x0, y1-y0, .012),
                  center=((x0+x1)/2, (y0+y1)/2, .914),
                  color=rim_color))

rim_piece("sink front flange", .452, 1.555, .064, .102)
rim_piece("sink rear flange", .452, 1.555, .550, .606)
rim_piece("sink left flange", .452, .491, .102, .550)
rim_piece("bowl dividing bridge", .955, .989, .102, .550)
rim_piece("small bowl front surround", .989, 1.240, .102, .188)
rim_piece("small bowl rear surround", .989, 1.240, .528, .550)
rim_piece("draining board", 1.226, 1.555, .102, .550)

def rounded_loop(cx, cy, w, d, radius, z):
    points = []
    for px, py, start in (
        (cx+w/2-radius, cy+d/2-radius, 0),
        (cx-w/2+radius, cy+d/2-radius, 90),
        (cx-w/2+radius, cy-d/2+radius, 180),
        (cx+w/2-radius, cy-d/2+radius, 270)):
        for k in range(7):
            a = math.radians(start + k*15)
            points.append((px+radius*math.cos(a),
                           py+radius*math.sin(a), z))
    points.append(points[0])
    return points

# Sloped metal walls and rounded floors for the two inset bowls.
def basin(name, cx, cy, w, d, depth):
    top = .913
    bottom = top-depth
    inset = .047
    add(name+" floor",
        plate((w-2*inset, d-2*inset, .013),
              (cx, cy, bottom), .035, steel))
    height = depth-.008
    angle = math.degrees(math.atan(inset/height))
    length = math.sqrt(height*height + inset*inset)
    for sign in (-1, 1):
        wall = box((w-.030, .012, length),
                   center=(cx, cy+sign*(d/2-inset/2),
                           (top+bottom)/2), color=steel)
        wall.turn('x', -sign*angle)
        add(name+" wall y "+str(sign), wall)
        wall = box((.012, d-.065, length),
                   center=(cx+sign*(w/2-inset/2), cy,
                           (top+bottom)/2), color=steel)
        wall.turn('y', sign*angle)
        add(name+" wall x "+str(sign), wall)
    add(name+" rolled lip",
        sweep_tube(points=rounded_loop(cx, cy, w, d, .052, .919),
                   radius=.006, color=chrome))
    # Shadowed curved corners close small gaps between the sloping panels.
    for sx in (-1, 1):
        for sy in (-1, 1):
            add(name+" corner %s %s" % (sx, sy),
                rod(radius=.025,
                    start=(cx+sx*(w/2-.031), cy+sy*(d/2-.031), top-.010),
                    end=(cx+sx*(w/2-inset-.018),
                         cy+sy*(d/2-inset-.018), bottom+.010),
                    color=steel))
    return bottom

za = basin("large basin", .724, .326, .470, .446, .178)
zb = basin("small basin", 1.103, .358, .242, .346, .143)

for name, x, y, z, r in (
    ("large", .746, .280, za+.009, .043),
    ("small", 1.105, .319, zb+.009, .030)):
    add(name+" drain flange",
        rod(radius=r, length=.004, center=(x, y, z), color=chrome))
    add(name+" drain recess",
        rod(radius=r*.76, length=.005,
            center=(x, y, z+.003), color=(.055, .070, .057)))
    add(name+" strainer",
        rod(radius=r*.55, length=.006,
            center=(x, y, z+.005), color=steel))
    for n in range(8):
        a = n*math.tau/8
        add(name+" drain hole "+str(n),
            rod(radius=.0024, length=.0015,
                center=(x+r*.38*math.cos(a),
                        y+r*.38*math.sin(a), z+.0085),
                color=(.025, .035, .028)))

for i in range(11):
    x = 1.257+i*.026
    add("drainer groove "+str(i),
        rod(radius=.003, start=(x, .117, .922),
            end=(x, .544, .922), color=(.13, .17, .15)))
    add("drainer ridge "+str(i),
        rod(radius=.0018, start=(x+.005, .117, .924),
            end=(x+.005, .544, .924), color=chrome))

# Arched chrome mixer.
add("tap mounting foot",
    rod(radius=.034, length=.018, center=(.969, .570, .932),
        color=chrome))
add("tap mixer body",
    rod(radius=.023, start=(.969, .570, .932),
        end=(.969, .570, 1.057), color=chrome))
tap_points = [
    (.969, .570, 1.025), (.972, .574, 1.120),
    (.974, .575, 1.238), (.972, .568, 1.304),
    (.959, .549, 1.335), (.935, .517, 1.345),
    (.912, .475, 1.345), (.895, .432, 1.333),
    (.886, .399, 1.310), (.882, .376, 1.275),
    (.882, .374, 1.239)]
add("arched spout", sweep_tube(points=tap_points,
                               radius=.013, color=chrome))
add("tap nozzle",
    rod(radius=.017, start=(.882, .374, 1.252),
        end=(.882, .374, 1.226), color=steel))
add("mixer housing",
    rod(radius=.024, start=(.980, .568, .972),
        end=(1.022, .568, .995), color=chrome))
add("mixer lever",
    rod(radius=.008, start=(1.017, .568, .995),
        end=(1.062, .570, 1.065), color=chrome))

# Appliance cropped by the right edge.
add("oven housing", box((.57, .62, .83),
                        center=(1.646, .29, .443),
                        color=(.65, .68, .62)))
add("oven glass", box((.49, .026, .57),
                      center=(1.646, -.038, .48),
                      color=(.012, .025, .026)))
add("oven bottom trim", box((.51, .04, .075),
                            center=(1.646, -.047, .155),
                            color=(.60, .64, .58)))
add("oven handle",
    rod(radius=.013, start=(1.433, -.094, .738),
        end=(1.858, -.094, .738), color=chrome))

realize(scene)

# Preserve the SceneAct finish when initializing shader nodes.
for mat in bpy.data.materials:
    rgba = tuple(mat.diffuse_color)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:
        continue
    bs.inputs["Base Color"].default_value = rgba
    rgb = rgba[:3]
    bs.inputs["Roughness"].default_value = .49

    def matches(color):
        return all(abs(rgb[i]-color[i]) < .015 for i in range(3))

    if matches(steel) or matches(chrome) or matches((.52, .54, .46)):
        bs.inputs["Metallic"].default_value = .88
        bs.inputs["Roughness"].default_value = .21 if matches(chrome) else .29

    if matches(stone):
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        coord = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 48
        noise.inputs["Detail"].default_value = 4
        noise.inputs["Roughness"].default_value = .75
        links.new(coord.outputs["Object"], noise.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .16
        ramp.color_ramp.elements[0].color = (.22, .23, .208, 1)
        ramp.color_ramp.elements[1].position = .84
        ramp.color_ramp.elements[1].color = (.43, .42, .37, 1)
        links.new(noise.outputs["Fac"], ramp.inputs[0])
        links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .12
        bump.inputs["Distance"].default_value = .001
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bs.inputs["Normal"])
        bs.inputs["Roughness"].default_value = .72

    if rgb[0] < .012 and rgb[2] < .045:
        bs.inputs["Roughness"].default_value = .24

    if rgb[0] > .72 and rgb[1] > .72 and rgb[2] < rgb[0]-.035:
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        coord = nodes.new("ShaderNodeTexCoord")
        scale = nodes.new("ShaderNodeVectorMath")
        scale.operation = 'MULTIPLY'
        scale.inputs[1].default_value = (65, 2.5, 3)
        links.new(coord.outputs["Generated"], scale.inputs[0])
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 3
        tex.inputs["Detail"].default_value = 2
        links.new(scale.outputs["Vector"], tex.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .10
        bump.inputs["Distance"].default_value = .0007
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bs.inputs["Normal"])

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("SceneWorld")
    bpy.context.scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
if background is None:
    background = world.node_tree.nodes.new("ShaderNodeBackground")
output = world.node_tree.nodes.get("World Output")
if output is None:
    output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
world.node_tree.links.new(background.outputs["Background"],
                          output.inputs["Surface"])
background.inputs["Color"].default_value = (.72, .77, .80, 1)
background.inputs["Strength"].default_value = .32

set_view(position=(.045, -2.55, 2.65),
         target=(.045, .28, .45), lens=41, sensor=36)
area_emitter(position=(-2, -1.7, 3.8), power=350, size=2.7,
             target=(0, .2, .65), color=(1, .965, .88))
area_emitter(position=(1, -1.4, 3.2), power=65, size=2.3,
             target=(.5, .2, .6), color=(.88, .94, 1))

sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 384
sc.render.resolution_percentage = 100
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = 0
sc.render.image_settings.file_format = 'PNG'
