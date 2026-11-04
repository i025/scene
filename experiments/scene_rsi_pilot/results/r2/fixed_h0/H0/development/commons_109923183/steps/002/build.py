import bpy
import math
import random
from sceneact import *

random.seed(8)
scene = Scene(name="French chaise interior")

ivory = (.72, .695, .62)
trim = (.79, .765, .685)
sage = (.32, .39, .335)
edge = (.66, .63, .49)
cloth = (.83, .775, .66)
pillow_color = (.90, .84, .71)

def put(parent, name, node):
    parent.include(name, node)
    return node

def tube(parent, name, pts, radius, color):
    return put(parent, name, sweep_tube(points=pts, radius=radius, color=color))

put(scene, "floor foundation",
    box((12, 12, .10), center=(0, 0, -.07), color=(.15, .075, .042)))
floor = Asset("Herringbone parquet")
w = .115
n = 5
angle = math.radians(12)
count = 0
for i in range(-9, 10):
    for j in range(-48, 49):
        ox, oy = (n*i-j)*w, (n*i+j)*w
        for vertical in (False, True):
            if vertical:
                px, py = ox+(n+.5)*w, oy+n*w/2
                size = (w-.006, n*w-.006, .024)
            else:
                px, py = ox+n*w/2, oy+w/2
                size = (n*w-.006, w-.006, .024)
            x = px*math.cos(angle)-py*math.sin(angle)
            y = px*math.sin(angle)+py*math.cos(angle)
            if abs(x) > 4.7 or abs(y) > 4.7:
                continue
            v = random.uniform(.78, 1.25)
            plank = box(size, center=(x, y, -.008),
                        color=(.245*v, .132*v, .078*v))
            plank.turn('z', 12)
            put(floor, "board_%04d" % count, plank)
            count += 1
put(scene, "parquet", floor)

wall = Asset("Ivory paneling")
put(wall, "plaster",
    box((9, .18, 4.3), center=(0, 1.22, 2.1), color=ivory))
for z, depth, height in [
    (.09, .16, .17), (.22, .11, .055), (.29, .07, .035),
    (1.82, .07, .035), (1.88, .11, .055), (1.97, .075, .035),
    (2.18, .075, .035), (2.24, .10, .045), (2.52, .065, .035)
]:
    put(wall, "horizontal molding %.3f" % z,
        box((9, depth, height), center=(0, 1.08, z), color=trim))

for index, (left, right) in enumerate([
    (-3.9, -1.78), (-1.68, 1.38), (1.5, 3.9)
]):
    for k, inset in enumerate((0, .035, .066)):
        x1, x2 = left+inset, right-inset
        bottom, top = .39+inset, 1.73-inset
        thick = (.018, .012, .009)[k]
        yy = 1.105-.012*k
        col = trim if k != 1 else (.66, .64, .57)
        for xx in (x1, x2):
            put(wall, f"field_{index}_{k}_upright_{xx}",
                box((thick, .027, top-bottom),
                    center=(xx, yy, (top+bottom)/2), color=col))
        for zz in (bottom, top):
            put(wall, f"field_{index}_{k}_cross_{zz}",
                box((x2-x1, .027, thick),
                    center=((x1+x2)/2, yy, zz), color=col))

for xx in (-1.74, 1.44):
    put(wall, f"panel seam {xx}",
        box((.012, .012, 3.8), center=(xx, 1.118, 1.94),
            color=(.43, .415, .37)))

put(wall, "right pier",
    box((.36, .38, 3.5), center=(2.10, 1.05, 1.74), color=trim))
for xx in (1.98, 2.22):
    put(wall, "pier upright "+str(xx),
        box((.018, .025, 2.8), center=(xx, .846, 1.80), color=ivory))
put(wall, "pier foot",
    box((.43, .43, .20), center=(2.10, 1.03, .10), color=trim))
put(scene, "wall", wall)

curtains = Asset("Window and curtains")
put(curtains, "window light",
    box((.035, 1.85, 3.5), center=(-2.08, .15, 1.8),
        color=(.96, .95, .88)))
for k in range(16):
    yy = -.64+k*.105
    xx = -1.99+.032*math.sin(k*2.3)
    col = (.82+.045*math.sin(k), .77+.04*math.sin(k),
           .65+.045*math.sin(k))
    tube(curtains, "curtain fold %d" % k,
         [(xx, yy, .10), (xx-.015, yy+.015, .9),
          (xx+.01, yy, 2.0), (xx-.035, yy+.01, 3.55)],
         .055 if k > 3 else .042, col)
for k in range(4):
    tube(curtains, "gold curtain edge %d" % k,
         [(-1.86+k*.018, -.73, .05),
          (-1.90+k*.018, -.74, 1.4),
          (-1.96+k*.018, -.75, 3.5)], .015, (.48, .36, .22))
put(scene, "curtains", curtains)

chaise = Asset("Antique upholstered chaise")
put(chaise, "seat cushion",
    fillet_box((2.39, .96, .245), radius=.115,
               center=(.015, 0, .706), color=cloth))
put(chaise, "seat underside",
    fillet_box((2.22, .86, .105), radius=.045,
               center=(-.005, 0, .585), color=cloth))

def rounded_outline(x0, x1, y0, y1, radius, z):
    result = []
    for cx, cy, start in [
        (x1-radius, y1-radius, 0),
        (x0+radius, y1-radius, 90),
        (x0+radius, y0+radius, 180),
        (x1-radius, y0+radius, 270)
    ]:
        for j in range(9):
            a = math.radians(start+j*90/8)
            result.append((cx+radius*math.cos(a),
                           cy+radius*math.sin(a), z))
    result.append(result[0])
    return result

tube(chaise, "upper cushion piping",
     rounded_outline(-1.18, 1.21, -.475, .475, .16, .742),
     .009, (.77, .71, .59))
tube(chaise, "lower cushion piping",
     rounded_outline(-1.16, 1.19, -.457, .457, .15, .619),
     .008, (.75, .68, .55))

for side in (-1, 1):
    y = side*.455
    pts = [(-1.13, y, .57), (-.92, y, .535), (-.64, y, .515),
           (-.25, y, .51), (.16, y, .495), (.53, y, .515),
           (.91, y, .54), (1.12, y, .55), (1.20, y, .51)]
    tube(chaise, f"sage apron {side}", pts, .048, sage)
    for dz in (-.028, .031):
        tube(chaise, f"apron gilded edge {side} {dz}",
             [(x, yy+side*.031, z+dz) for x, yy, z in pts],
             .008, edge)

for x in (-1.12, 1.15):
    tube(chaise, "end rail "+str(x),
         [(x, -.44, .53), (x+.025, -.23, .51),
          (x+.035, 0, .50), (x+.025, .23, .51),
          (x, .44, .53)], .038, sage)

for end in (-1, 1):
    for side in (-1, 1):
        x = -1.02 if end == -1 else 1.07
        y = side*.385
        pts = [(x, y, .56),
               (x+end*.075, y+side*.045, .47),
               (x+end*.055, y+side*.065, .35),
               (x+end*.005, y+side*.075, .18),
               (x+end*.055, y+side*.09, .075),
               (x+end*.115, y+side*.085, .058)]
        tube(chaise, f"curved leg {end} {side}", pts, .034, sage)
        tube(chaise, f"leg gilt {end} {side}",
             [(xx, yy-.028, zz+.003) for xx, yy, zz in pts],
             .0065, edge)
        put(chaise, f"foot {end} {side}",
            fillet_box((.10, .075, .045), radius=.018,
                       center=(x+end*.085, y+side*.085, .048),
                       color=edge))

back = fillet_box((.19, .91, .82), radius=.093,
                  center=(-1.205, 0, 1.12), color=cloth)
back.turn('y', -15)
put(chaise, "upholstered head", back)

head_outline = [
    (-1.12, -.49, .64), (-1.22, -.49, 1.02),
    (-1.31, -.47, 1.34), (-1.34, -.39, 1.46),
    (-1.35, -.24, 1.505), (-1.35, -.08, 1.49),
    (-1.35, .09, 1.485), (-1.33, .27, 1.45),
    (-1.30, .43, 1.34), (-1.24, .49, 1.12),
    (-1.13, .49, .65)
]
tube(chaise, "head carved surround", head_outline, .038, sage)
tube(chaise, "head pale inner edge",
     [(x+.021, y*.97, z-.008) for x, y, z in head_outline],
     .010, edge)

for side in (-1, 1):
    wing = fillet_box((.72, .095, .46), radius=.045,
                     center=(-.89, side*.445, .865), color=cloth)
    wing.turn('y', -19)
    put(chaise, "padded side wing "+str(side), wing)
    outline = [
        (-1.28, side*.475, 1.32), (-1.18, side*.49, 1.17),
        (-1.03, side*.50, 1.08), (-.85, side*.50, 1.015),
        (-.66, side*.49, .995), (-.50, side*.47, 1.025),
        (-.46, side*.46, 1.075)
    ]
    tube(chaise, "swept arm crest "+str(side), outline, .031, sage)
    tube(chaise, "arm pale crest "+str(side),
         [(x, y-side*.018, z+.015) for x, y, z in outline],
         .008, edge)
    lower = [
        (-1.11, side*.48, .62), (-1.00, side*.50, .60),
        (-.82, side*.50, .585), (-.66, side*.48, .61),
        (-.57, side*.47, .69), (-.53, side*.47, .85),
        (-.46, side*.46, 1.07)
    ]
    tube(chaise, "wing lower carved rim "+str(side), lower, .028, sage)
    tube(chaise, "wing inner pale rim "+str(side),
         [(x+.01, y-side*.018, z+.013) for x, y, z in lower],
         .007, edge)
    pts = []
    for j in range(25):
        a = j*math.pi*1.55/24
        r = .025*(1-j/35)
        pts.append((-.46+r*math.cos(a), side*.46,
                    1.06+r*math.sin(a)))
    tube(chaise, "arm scroll "+str(side), pts, .009, edge)

pillow = fillet_box((.255, .68, .65), radius=.12,
                   center=(-.98, -.035, 1.075), color=pillow_color)
pillow.turn('y', -20)
pillow.turn('z', -6)
put(chaise, "loose cream pillow", pillow)

pillow_pipe = []
for j in range(81):
    a = 2*math.pi*j/80
    sy = math.copysign(abs(math.cos(a))**.42, math.cos(a))
    sz = math.copysign(abs(math.sin(a))**.42, math.sin(a))
    yy = -.035+.315*sy
    zz = 1.075+.300*sz
    xx = -.837-.34*(zz-1.075)
    pillow_pipe.append((xx, yy, zz))
tube(chaise, "pillow stitched edge", pillow_pipe, .0055, (.78, .71, .57))

medallion = ball(.069, center=(.10, -.498, .49), color=edge)
medallion.resize((1.15, .28, .80))
put(chaise, "front apron medallion", medallion)
for side in (-1, 1):
    for leaf in range(4):
        pts = []
        for j in range(17):
            t = j/16
            xx = .10+side*(.045+.20*t)
            zz = .495+.028*math.sin(t*math.pi*1.7+leaf*.45)-leaf*.009
            pts.append((xx, -.536, zz))
        tube(chaise, f"apron leaf {side} {leaf}", pts, .007, edge)
for j in range(8):
    a = j*2*math.pi/8
    pearl = ball(.012,
                 center=(.10+.043*math.cos(a), -.523,
                         .49+.038*math.sin(a)), color=trim)
    pearl.resize((1, .45, 1))
    put(chaise, "rosette petal %d" % j, pearl)

label = box((.145, .065, .004), center=(.64, .07, .834),
            color=(.055, .23, .18))
label.turn('z', -7)
put(chaise, "green paper label", label)
for k in range(3):
    put(chaise, "label print %d" % k,
        box((.052 if k == 0 else .037, .0025, .001),
            center=(.642, .052+k*.012, .837),
            color=(.69, .77, .65)))

chaise.turn('z', -43, pivot=(0, 0, 0))
put(scene, "chaise", chaise)

chair = Asset("Foreground cane chair")
cx, cy = -1.85, -1.24
put(chair, "cane seat base",
    fillet_box((.66, .65, .04), radius=.018,
               center=(cx, cy, .49), color=(.44, .30, .17)))
for y in (cy-.34, cy+.34):
    tube(chair, "seat long rim "+str(y),
         [(cx-.36, y, .50), (cx, y-.015, .50),
          (cx+.36, y, .50)], .033, sage)
    tube(chair, "seat long pale rim "+str(y),
         [(cx-.36, y-.025, .513), (cx, y-.03, .513),
          (cx+.36, y-.025, .513)], .009, edge)
for x in (cx-.35, cx+.35):
    tube(chair, "seat short rim "+str(x),
         [(x, cy-.34, .50), (x+.015, cy, .50),
          (x, cy+.34, .50)], .035, sage)
for k in range(35):
    t = -.30+k*.018
    tube(chair, "cane warp %d" % k,
         [(cx+t, cy-.30, .516), (cx+t, cy+.30, .516)],
         .0025, (.68, .51, .30))
    tube(chair, "cane weft %d" % k,
         [(cx-.30, cy+t, .519), (cx+.30, cy+t, .519)],
         .0025, (.61, .43, .24))
for x in (cx-.30, cx+.30):
    for y in (cy-.28, cy+.28):
        tube(chair, "chair leg "+str((x, y)),
             [(x, y, .48), (x+.025, y, .23), (x+.035, y, .02)],
             .028, sage)
chair.turn('z', -12, pivot=(cx, cy, 0))
put(scene, "foreground chair", chair)

realize(scene)

def make_fabric(name, base, patterned=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*base, 1)
    bs.inputs["Roughness"].default_value = .85
    if "Sheen Weight" in bs.inputs:
        bs.inputs["Sheen Weight"].default_value = .18
    geo = nodes.new("ShaderNodeNewGeometry")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 260
    noise.inputs["Detail"].default_value = 2
    links.new(geo.outputs["Position"], noise.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .17
    bump.inputs["Distance"].default_value = .0017
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bs.inputs["Normal"])

    if patterned:
        def mathnode(op, a=None, value=None):
            q = nodes.new("ShaderNodeMath")
            q.operation = op
            if a is not None:
                links.new(a, q.inputs[0])
            if value is not None:
                q.inputs[1].default_value = value
            return q.outputs[0]

        dx = nodes.new("ShaderNodeVectorMath")
        dx.operation = "DOT_PRODUCT"
        dx.inputs[1].default_value = (.73135, -.682, 0)
        links.new(geo.outputs["Position"], dx.inputs[0])
        dy = nodes.new("ShaderNodeVectorMath")
        dy.operation = "DOT_PRODUCT"
        dy.inputs[1].default_value = (.682, .73135, 0)
        links.new(geo.outputs["Position"], dy.inputs[0])

        yphase = mathnode("MULTIPLY", dy.outputs["Value"], 138)
        ysin = mathnode("SINE", yphase)
        yabs = mathnode("ABSOLUTE", ysin)
        stripe = mathnode("LESS_THAN", yabs, .055)
        stripe = mathnode("MULTIPLY", stripe, .22)

        rows = mathnode("MULTIPLY", dy.outputs["Value"], 69)
        rows = mathnode("SINE", rows)
        rows = mathnode("GREATER_THAN", rows, .94)
        dashes = mathnode("MULTIPLY", dx.outputs["Value"], 108)
        dashes = mathnode("SINE", dashes)
        dashes = mathnode("GREATER_THAN", dashes, .55)
        marks = nodes.new("ShaderNodeMath")
        marks.operation = "MULTIPLY"
        links.new(rows, marks.inputs[0])
        links.new(dashes, marks.inputs[1])
        marks2 = mathnode("MULTIPLY", marks.outputs[0], .47)
        total = nodes.new("ShaderNodeMath")
        total.operation = "MAXIMUM"
        links.new(stripe, total.inputs[0])
        links.new(marks2, total.inputs[1])
        mix = nodes.new("ShaderNodeMixRGB")
        mix.inputs[1].default_value = (*base, 1)
        mix.inputs[2].default_value = (.52, .245, .24, 1)
        links.new(total.outputs[0], mix.inputs[0])
        links.new(mix.outputs[0], bs.inputs["Base Color"])
    return mat

upholstery_mat = make_fabric("Ecru linen with faded rose woven stripes", cloth, True)
pillow_mat = make_fabric("Soft ivory pillow linen", pillow_color)

for ob in bpy.context.scene.objects:
    if ob.type != 'MESH':
        continue
    for slot in ob.material_slots:
        old = slot.material
        if old is None:
            continue
        c = tuple(old.diffuse_color[:3])
        if old.use_nodes:
            p = old.node_tree.nodes.get("Principled BSDF")
            if p:
                c = tuple(p.inputs["Base Color"].default_value[:3])
        if sum((c[k]-cloth[k])**2 for k in range(3)) < .0001:
            slot.material = upholstery_mat
        elif sum((c[k]-pillow_color[k])**2 for k in range(3)) < .0001:
            slot.material = pillow_mat
        elif old.use_nodes:
            p = old.node_tree.nodes.get("Principled BSDF")
            if p:
                p.inputs["Roughness"].default_value = .67
    if "board" in ob.name.lower():
        for slot in ob.material_slots:
            if slot.material and slot.material.use_nodes:
                p = slot.material.node_tree.nodes.get("Principled BSDF")
                if p:
                    p.inputs["Roughness"].default_value = .37

set_view(position=(-2.2, -4.4, 3.1), target=(.12, -.02, .84),
         lens=60, sensor=36)
area_emitter(position=(-2.8, -.4, 3.0), power=430, size=2.5,
             target=(0, 0, .7), color=(1.0, .95, .83))
area_emitter(position=(.5, -3.4, 3.7), power=95, size=3.0,
             target=(0, 0, .65), color=(1.0, .95, .88))

world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.75, .79, .85, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .24

s = bpy.context.scene
s.render.resolution_x = 512
s.render.resolution_y = 384
s.render.resolution_percentage = 100
s.render.engine = 'CYCLES'
s.cycles.samples = 48
s.cycles.use_denoising = True
s.view_settings.view_transform = 'AgX'
try:
    s.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass
s.view_settings.exposure = .15
s.render.image_settings.file_format = 'PNG'
s.camera.data.dof.use_dof = False
