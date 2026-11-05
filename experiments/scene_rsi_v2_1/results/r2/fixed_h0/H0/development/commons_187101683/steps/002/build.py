from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(17)
scene = Scene("Golden sofa sitting room")
gold = (.67, .355, .105)
seatgold = (.73, .407, .145)
pillowgold = (.79, .49, .205)
wood = (.075, .049, .034)
blackwood = (.035, .024, .018)
white = (.89, .91, .87)

scene.include("wall", box((12, .15, 6), center=(0, 1.65, 2.8), color=(.80, .79, .745)))
scene.include("carpet", box((14, 14, .12), center=(0, 0, -.07), color=(.30, .285, .27)))

sofa = Asset("ochre velvet sofa")
sofa.include("lower upholstered plinth",
             fillet_box((3.72, 1.32, .42), .065, center=(0, .38, .28), color=gold))
sofa.include("front apron",
             fillet_box((3.40, .22, .30), .035, center=(0, -.247, .43), color=seatgold))
sofa.include("back structure",
             fillet_box((3.53, .33, 1.31), .075, center=(0, .91, 1.00), color=gold))
for i, x in enumerate((-.82, .82)):
    sofa.include("seat cushion " + str(i),
                 fillet_box((1.62, 1.05, .29), .115, center=(x, .205, .695), color=seatgold))
    back = fillet_box((1.64, .32, .97), .085, center=(x, .823, 1.235), color=seatgold)
    back.turn("x", -5)
    sofa.include("back cushion " + str(i), back)

for x in (-1.77, 1.77):
    sofa.include("broad padded arm " + str(x),
                 fillet_box((.37, 1.45, 1.16), .092, center=(x, .30, .66), color=gold))
    sofa.include("arm upper pad " + str(x),
                 fillet_box((.38, 1.37, .17), .075, center=(x, .29, 1.18), color=seatgold))
for x in (-1.43, 1.43):
    sofa.include("low foot " + str(x),
                 box((.12, .13, .08), center=(x, .65, .045), color=(.10, .065, .035)))

pillow = fillet_box((.68, .235, .70), .10, center=(-1.16, .48, 1.225), color=pillowgold)
pillow.turn(euler=(11, -12, -10))
sofa.include("loose left pillow", pillow)
pillow2 = fillet_box((.63, .23, .67), .095, center=(1.24, .63, 1.23), color=(.76, .46, .17))
pillow2.turn(euler=(13, 8, -9))
sofa.include("right loose cushion", pillow2)
scene.include("sofa", sofa)

table = Asset("dark rectangular coffee table")
table.include("solid walnut top", box((2.73, 1.12, .105), center=(.67, -1.36, .795), color=wood))
table.include("front apron", box((2.58, .065, .16), center=(.67, -1.845, .682), color=blackwood))
table.include("back apron", box((2.58, .065, .16), center=(.67, -.875, .682), color=blackwood))
for x in (-.58, 1.92):
    table.include("side apron " + str(x),
                  box((.065, .98, .16), center=(x, -1.36, .682), color=blackwood))
    for y in (-1.82, -.90):
        table.include("square leg " + str((x, y)),
                      box((.105, .105, .735), center=(x, y, .368), color=blackwood))
scene.include("table", table)

cup_positions = [(-.02, -1.40), (1.12, -1.45)]
for i, (x, y) in enumerate(cup_positions):
    nap = box((.62, .42, .012), center=(x + .015, y - .005, .855), color=(.60, .68, .62))
    nap.turn("z", -12 if i == 0 else 9)
    scene.include("sage folded napkin " + str(i), nap)
    fold = box((.51, .325, .009), center=(x - .025, y - .025, .866), color=(.74, .77, .69))
    fold.turn("z", -12 if i == 0 else 9)
    scene.include("linen fold " + str(i), fold)
    scene.include("saucer " + str(i), rod(.183, length=.016, center=(x, y, .881), color=white))
    scene.include("saucer raised center " + str(i),
                  rod(.116, length=.014, center=(x, y, .894), color=white))
    scene.include("spoon handle " + str(i),
                  rod(.009, start=(x + .12, y - .10, .903),
                      end=(x + .27, y + .035, .903), color=(.52, .54, .51)))
    spoon = ball(.034, center=(x + .285, y + .049, .903), color=(.60, .62, .59))
    spoon.resize((1, .60, .15))
    scene.include("spoon bowl " + str(i), spoon)

px, py = .60, -1.135
for j in range(34):
    t = j / 33
    scene.include("planter band %02d" % j,
                  rod(.112 + .042 * t, length=.010,
                      center=(px, py, .854 + .0087 * j),
                      color=(.075 + .012 * (j % 2), .082 + .012 * (j % 2), .070 + .012 * (j % 2))))
scene.include("soil", rod(.139, length=.013, center=(px, py, 1.141), color=(.055, .044, .028)))

plant = Asset("flowers and leafy stems")
clusters = [
    (-.24, .01, 1.51, .095),
    (-.13, .06, 1.65, .095),
    (.015, .045, 1.77, .087),
    (.15, .04, 1.66, .09),
    (.26, .005, 1.61, .11),
    (.075, -.025, 1.55, .077)
]
for i, (dx, dy, z, rad) in enumerate(clusters):
    top = (px + dx, py + dy, z - .035)
    plant.include("flower stem " + str(i),
                  rod(.008, start=(px, py, 1.12), end=top, color=(.22, .31, .10)))
    for j in range(37):
        a = random.random() * 2 * math.pi
        zz = random.uniform(-1, 1)
        rr = math.sqrt(1 - zz * zz)
        q = (px + dx + rad * rr * math.cos(a),
             py + dy + rad * rr * math.sin(a),
             z + rad * .80 * zz)
        pet = ball(random.uniform(.014, .023), center=q,
                   color=random.choice([
                       (.49, .57, .65), (.62, .69, .72),
                       (.73, .77, .77), (.44, .53, .63)
                   ]))
        pet.resize((1, .8, .65))
        plant.include("tiny floret %d %d" % (i, j), pet)

for i in range(48):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(.08, .29)
    z = random.uniform(1.20, 1.48)
    end = (px + r * math.cos(a), py + r * .60 * math.sin(a), z)
    plant.include("twig " + str(i),
                  rod(.0035, start=(px, py, 1.13), end=end, color=(.22, .31, .105)))
    for k in range(2):
        leaf = ball(.043,
                    center=(end[0] + .026 * math.cos(a + k),
                            end[1] + .026 * math.sin(a + k), z + .015 * k),
                    color=random.choice([
                        (.22, .33, .13), (.31, .42, .19), (.38, .46, .22)
                    ]))
        leaf.resize((1, .34, .19))
        leaf.turn(euler=(random.uniform(-35, 35), random.uniform(-30, 30),
                         math.degrees(a) + k * 60))
        plant.include("leaf %d %d" % (i, k), leaf)
scene.include("bouquet", plant)

scene.include("window glow",
              box((1.5, .035, 3.7), center=(2.70, 1.53, 2.00), color=(.94, .96, .95)))
scene.include("window side trim",
              box((.065, .09, 3.8), center=(3.40, 1.47, 2.00), color=(.86, .86, .81)))

realize(scene)

def lathe(name, profile, center, material, segments=64):
    vertices = []
    for r, z in profile:
        for j in range(segments):
            a = j * 2 * math.pi / segments
            vertices.append((center[0] + r * math.cos(a),
                             center[1] + r * math.sin(a), center[2] + z))
    faces = []
    for i in range(len(profile) - 1):
        for j in range(segments):
            k = (j + 1) % segments
            faces.append((i * segments + j, i * segments + k,
                          (i + 1) * segments + k, (i + 1) * segments + j))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth = True
    return obj

porcelain = bpy.data.materials.new("warm white glazed porcelain")
porcelain.diffuse_color = (*white, 1)
porcelain.use_nodes = True
pbs = porcelain.node_tree.nodes.get("Principled BSDF")
pbs.inputs["Base Color"].default_value = (*white, 1)
pbs.inputs["Roughness"].default_value = .22

for i, (x, y) in enumerate(cup_positions):
    lathe("open tapered teacup " + str(i),
          [(.069, 0), (.075, .012), (.096, .155), (.111, .225),
           (.109, .231), (.100, .231), (.087, .155), (.066, .021), (0, .021)],
          (x, y, .901), porcelain)
    side = -1 if i == 0 else 1
    pts = []
    for j in range(25):
        a = math.radians(-85 + 170 * j / 24)
        pts.append((x + side * (.092 + .073 * math.cos(a)),
                    y, .901 + .126 + .072 * math.sin(a)))
    curve = bpy.data.curves.new("cup handle curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = .010
    curve.bevel_resolution = 4
    spl = curve.splines.new("POLY")
    spl.points.add(len(pts) - 1)
    for p, q in zip(spl.points, pts):
        p.co = (*q, 1)
    ob = bpy.data.objects.new("porcelain loop handle " + str(i), curve)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(porcelain)

curtainmat = bpy.data.materials.new("gray taupe curtain fabric")
curtainmat.diffuse_color = (.245, .24, .22, 1)
curtainmat.use_nodes = True
cp = curtainmat.node_tree.nodes.get("Principled BSDF")
cp.inputs["Base Color"].default_value = (.245, .24, .22, 1)
cp.inputs["Roughness"].default_value = .91

verts, faces = [], []
nu, nv = 64, 70
for j in range(nv + 1):
    t = j / nv
    z = 3.65 - 3.48 * t
    gather = math.exp(-((t - .59) / .18) ** 2)
    left = 1.79 + .39 * gather
    width = .70 - .25 * gather
    for i in range(nu + 1):
        u = i / nu
        x = left + width * u
        y = 1.38 + .105 * math.sin(u * math.pi * 10 + .9 * t)
        y += .035 * math.sin(u * math.pi * 21)
        y -= .17 * gather * math.sin(u * math.pi)
        verts.append((x, y, z + .035 * math.sin(u * math.pi * 6) * t * t))
for j in range(nv):
    for i in range(nu):
        a = j * (nu + 1) + i
        faces.append((a, a + 1, a + nu + 2, a + nu + 1))
mesh = bpy.data.meshes.new("flowing curtain mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()
curtain = bpy.data.objects.new("gathered floor length curtain", mesh)
bpy.context.collection.objects.link(curtain)
curtain.data.materials.append(curtainmat)
for p in mesh.polygons:
    p.use_smooth = True
sol = curtain.modifiers.new("cloth thickness", "SOLIDIFY")
sol.thickness = .008

for mat in list(bpy.data.materials):
    if not mat.use_nodes:
        mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    c = bs.inputs["Base Color"].default_value
    if c[0] > .52 and .23 < c[1] < .57 and c[2] < .28:
        bs.inputs["Roughness"].default_value = .88
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 145
        noise.inputs["Detail"].default_value = 2
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .17
        bump.inputs["Distance"].default_value = .013
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    elif .26 < c[0] < .34 and abs(c[0] - c[1]) < .055:
        bs.inputs["Roughness"].default_value = 1
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 190
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .38
        bump.inputs["Distance"].default_value = .024
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    elif .05 < c[0] < .10 and c[1] < .065:
        bs.inputs["Roughness"].default_value = .4
        tex = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 5
        tex.inputs["Detail"].default_value = 3
        coord = mat.node_tree.nodes.new("ShaderNodeTexCoord")
        mapping = mat.node_tree.nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = (2, 85, 12)
        mat.node_tree.links.new(coord.outputs["Generated"], mapping.inputs[0])
        mat.node_tree.links.new(mapping.outputs[0], tex.inputs["Vector"])
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .16
        bump.inputs["Distance"].default_value = .009
        mat.node_tree.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bs.inputs["Normal"])

set_view((.20, -6.7, 2.55), (.05, 0, 1.13), lens=60, sensor=36)
area_emitter((3.0, -.05, 4.0), power=620, size=3.1,
             target=(0, -.1, .8), color=(1, .96, .88))
area_emitter((-2.2, -3.1, 3.7), power=115, size=4,
             target=(0, 0, 1), color=(1, .96, .90))

sc = bpy.context.scene
world = sc.world
if world is None:
    world = bpy.data.worlds.new("soft ambient daylight")
    sc.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (.77, .80, .82, 1)
background.inputs["Strength"].default_value = .27

sc.render.resolution_x = 512
sc.render.resolution_y = 342
sc.render.resolution_percentage = 100
sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.view_settings.exposure = .35

cam = sc.camera
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (cam.location - Vector((.5, -1.1, 1.15))).length
cam.data.dof.aperture_fstop = 7.0
