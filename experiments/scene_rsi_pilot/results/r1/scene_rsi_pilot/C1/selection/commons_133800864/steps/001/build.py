from sceneact import *
import bpy
import math

# Evidence ledger, approximate image bounds in a 384 x 512 image:
# Window/blinds x0–113,y0–411, cropped left/top; cabinet x110–384,y0–272.
# Paper roll x230–323,y26–222; towel ring x110–170,y166–264.
# Ivory towel x99–181,y244–423, covering several countertop canisters.
# Counter fills bottom quarter; sink and faucet are cropped lower left.
# Blender (model uncertain) x195–244,y293–417, behind foreground jug.
# Jug x226–302,y334–452; blue filter pitcher x280–373,y307–435.
# Cabinet verticals are nearly upright; counter/back-wall edges rise rightward.
# Support: countertop z=.80; cabinet side/front support towel ring/paper holder.
# Occlusion order: wall/window, cabinet, canisters/blender, towel/jug/pitcher.
#
# Ownership ledger:
# architecture owns walls, window, blinds and cabinet with nested editable parts.
# counter owns stone slab, backsplash and lower cabinetry.
# sink_and_faucet owns basin, rim, faucet and tap handles.
# paper_roll owns brackets, axle, paper and finial; cabinet-front attachment.
# towel_ring owns mounting plate, stem and ring; cabinet-side attachment.
# towel owns cloth folds/flaps, hanging from ring.
# Each canister, blender, water_jug and filter_pitcher has a separate Asset.
# Countertop objects use explicit bottom heights relative to COUNTER_Z.
# Shader changes select include-slot EMPTY descendants and copy mesh/material data.
# Camera parameters are independent of architecture and object dimensions.

scene = Scene("Kitchen corner")
CAMERA_POSITION = (-1.14, -2.43, 1.96)
CAMERA_TARGET = (.035, .045, 1.64)
CAMERA_LENS = 56
COUNTER_Z = .80

cream = (.77, .725, .60)
trim = (.86, .815, .70)
wall_color = (.76, .72, .62)
chrome = (.55, .57, .55)
paper = (.94, .915, .83)
ivory = (.86, .835, .74)
granite = (.30, .28, .235)

def add(parent, name, node):
    return parent.include(name, node)

def ellipsoid(parent, name, center, scale, color, opacity=1):
    node = ball(1, center=center, color=color, opacity=opacity)
    node.resize(scale, pivot=center)
    return add(parent, name, node)

def tube(parent, name, points, radius, color):
    return add(parent, name, sweep_tube(points=points, radius=radius, color=color))

architecture = Asset("architecture")
add(architecture, "back_wall",
    box((4.5, .10, 3.5), center=(.1, .48, 1.65), color=wall_color))
add(architecture, "right_wall",
    box((.10, 2.1, 3.5), center=(1.24, -.45, 1.65), color=wall_color))

window = Asset("window")
add(window, "glazing",
    box((1.25, .035, 2.65), center=(-.84, .405, 1.78),
        color=(.64, .77, .77)))
for i, x in enumerate((-1.47, -.22)):
    add(window, f"side_frame_{i}",
        box((.045, .095, 2.75), center=(x, .345, 1.78), color=trim))
for i, z in enumerate((.43, 1.62, 3.12)):
    add(window, f"horizontal_frame_{i}",
        box((1.30, .095, .055), center=(-.845, .34, z), color=trim))
for i, x in enumerate((-1.06, -.61)):
    add(window, f"window_mullion_{i}",
        box((.027, .065, 2.65), center=(x, .35, 1.78), color=trim))
# Abstract outdoor foliage consists only of geometry beyond glazing.
for i in range(12):
    x = -1.43 + (i % 4) * .32
    z = .65 + (i // 4) * .82
    ellipsoid(window, f"distant_foliage_{i}", (x, .425, z),
              (.18, .012, .28), (.39 + .035*(i % 3), .56, .49))

blinds = Asset("blinds")
for i in range(37):
    slat = box((1.25, .085, .016),
               center=(-.845, .265, .49 + i*.071),
               color=(.84, .84, .75))
    slat.turn("x", -12)
    add(blinds, f"slat_{i:02d}", slat)
for i, x in enumerate((-1.25, -.79, -.35)):
    add(blinds, f"ladder_tape_{i}",
        box((.016, .012, 2.62), center=(x, .208, 1.79),
            color=(.79, .78, .68)))
add(blinds, "bottom_rail",
    box((1.26, .075, .04), center=(-.845, .26, .47), color=trim))
for i, x in enumerate((-.33, -.29)):
    add(blinds, f"pull_cord_{i}",
        rod(.003, start=(x, .17, 2.05), end=(x, .17, 1.66), color=ivory))
    add(blinds, f"pull_knob_{i}",
        rod(.009, length=.065, center=(x, .17, 1.65), color=ivory))
add(architecture, "window", window)
add(architecture, "blinds", blinds)

cabinet = Asset("upper_cabinet")
add(cabinet, "left_side",
    box((.052, .57, 1.57), center=(-.075, .145, 2.415), color=cream))
add(cabinet, "bottom",
    box((1.19, .57, .055), center=(.493, .145, 1.657), color=cream))
add(cabinet, "right_side",
    box((.045, .57, 1.57), center=(1.075, .145, 2.415), color=cream))
add(cabinet, "door_panel",
    box((1.105, .044, 1.50), center=(.50, -.151, 2.435), color=cream))
for i, x in enumerate((-.013, 1.013)):
    add(cabinet, f"door_stile_{i}",
        box((.058, .025, 1.48), center=(x, -.183, 2.435), color=trim))
for i, z in enumerate((1.725, 3.145)):
    add(cabinet, f"door_rail_{i}",
        box((1.025, .025, .060), center=(.50, -.183, z), color=trim))
add(cabinet, "recessed_center",
    box((.90, .012, 1.28), center=(.50, -.179, 2.435),
        color=(.795, .75, .635)))
add(cabinet, "knob_stem",
    rod(.011, start=(.91, -.20, 1.895),
        end=(.91, -.237, 1.895), color=chrome))
ellipsoid(cabinet, "door_knob", (.91, -.246, 1.895),
          (.020, .017, .020), chrome)
add(architecture, "upper_cabinet", cabinet)
add(scene, "architecture", architecture)

counter = Asset("counter")
slab = box((2.85, 1.22, .075),
           center=(-.15, -.20, COUNTER_Z-.0375), color=granite)
hole = fillet_box((.69, .53, .21), radius=.075,
                  center=(-.88, -.48, COUNTER_Z-.05))
add(counter, "stone_slab", subtract(slab, hole))
add(counter, "backsplash",
    box((2.85, .045, .14), center=(-.15, .385, COUNTER_Z+.07),
        color=granite))
add(counter, "cabinet_below",
    box((2.8, 1.13, .75), center=(-.15, -.19, .35),
        color=(.35, .32, .25)))
add(scene, "counter", counter)

sink = Asset("sink_and_faucet")
# All fillet radii fit half the smallest dimension, including thin rim.
outer = fillet_box((.735, .575, .035), radius=.015,
                   center=(-.88, -.48, .808), color=(.33, .34, .29))
inner = fillet_box((.66, .50, .09), radius=.04,
                   center=(-.88, -.48, .808))
add(sink, "rim", subtract(outer, inner))
add(sink, "basin_bottom",
    fillet_box((.62, .46, .025), radius=.01,
               center=(-.88, -.48, .615), color=(.075, .082, .069)))
for i, x in enumerate((-1.20, -.56)):
    add(sink, f"basin_wall_x_{i}",
        box((.022, .48, .18), center=(x, -.48, .71),
            color=(.16, .17, .145)))
for i, y in enumerate((-.72, -.24)):
    add(sink, f"basin_wall_y_{i}",
        box((.65, .022, .18), center=(-.88, y, .71),
            color=(.16, .17, .145)))
add(sink, "faucet_base",
    rod(.038, length=.035, center=(-.88, -.175, .83), color=chrome))
tube(sink, "faucet_neck",
     [(-.88,-.175,.84), (-.88,-.175,1.16), (-.88,-.18,1.22),
      (-.88,-.22,1.245), (-.88,-.27,1.225), (-.88,-.29,1.18)],
     .012, chrome)
for i, x in enumerate((-1.02, -.74)):
    add(sink, f"tap_base_{i}",
        rod(.026, length=.035, center=(x, -.18, .83), color=chrome))
    tube(sink, f"tap_handle_{i}",
         [(x,-.18,.84), (x,-.18,.885), (x+.045,-.18,.91)], .011, chrome)
add(scene, "sink_and_faucet", sink)

roll = Asset("paper_roll")
for i, z in enumerate((1.89, 2.80)):
    ellipsoid(roll, f"mount_{i}", (.52, -.218, z),
              (.040, .022, .040), chrome)
    tube(roll, f"support_arm_{i}",
         [(.52,-.22,z), (.52,-.30,z), (.52,-.38,z)], .014, chrome)
add(roll, "axle",
    rod(.018, start=(.52,-.38,1.88), end=(.52,-.38,2.83), color=chrome))
add(roll, "paper_cylinder",
    rod(.163, length=.78, center=(.52,-.38,2.35), color=paper))
add(roll, "loose_paper_edge",
    box((.27,.013,.76), center=(.51,-.538,2.34), color=paper))
ellipsoid(roll, "top_finial", (.52,-.38,2.80),
          (.033,.033,.045), chrome)
add(scene, "paper_roll", roll)

ring = Asset("towel_ring")
add(ring, "wall_plate",
    rod(.051, start=(-.105,.095,2.07), end=(-.13,.095,2.07), color=chrome))
add(ring, "stem",
    rod(.017, start=(-.13,.095,2.07), end=(-.215,.095,2.07), color=chrome))
points = [
    (-.219, .085+.143*math.cos(2*math.pi*i/64),
     1.921+.166*math.sin(2*math.pi*i/64))
    for i in range(65)
]
tube(ring, "ring", points, .0085, chrome)
add(scene, "towel_ring", ring)

towel = Asset("towel")
for i in range(7):
    y = -.071+i*.029
    bottom = 1.015+.025*math.cos(i*1.7)
    top = 1.83-.019*abs(i-3)
    x = -.24-.018*math.cos(i*1.5)
    panel = fillet_box((.026,.044,top-bottom), radius=.011,
                       center=(x,y,(top+bottom)/2), color=ivory)
    panel.turn("x", -7+i*1.5)
    add(towel, f"cloth_fold_{i}", panel)
flap = fillet_box((.035,.225,.40), radius=.014,
                  center=(-.265,.025,1.245), color=(.88,.855,.77))
flap.turn("x", 8)
add(towel, "lower_flap", flap)
rear = fillet_box((.025,.19,.46), radius=.011,
                  center=(-.19,.16,1.49), color=ivory)
rear.turn("x", 18)
add(towel, "rear_drape", rear)
add(scene, "towel", towel)

for i, (x,y,h,r,c) in enumerate([
    (-.14,.20,.27,.075,(.39,.41,.24)),
    (-.29,.23,.24,.061,(.47,.43,.27)),
    (-.36,-.03,.065,.050,(.22,.20,.14))
]):
    obj = Asset(f"canister_{i}")
    add(obj, "body", rod(r, length=h, center=(x,y,COUNTER_Z+h/2), color=c))
    add(obj, "lid",
        rod(r*1.06, length=.018, center=(x,y,COUNTER_Z+h+.006),
            color=(.50,.48,.34)))
    add(scene, f"canister_{i}", obj)

blender = Asset("blender")
add(blender, "black_base",
    fillet_box((.20,.20,.235), radius=.035,
               center=(.135,.21,.9175), color=(.025,.032,.027)))
ellipsoid(blender, "base_shoulder", (.135,.21,1.02),
          (.105,.10,.065), (.025,.03,.025))
cup = rod(.062, length=.37, center=(.135,.21,1.255),
          color=(.55,.59,.52), opacity=.34)
cup.turn("y", -9)
add(blender, "clear_cup", cup)
add(blender, "cup_rim",
    rod(.064, length=.014, center=(.106,.21,1.438), color=(.33,.34,.29)))
add(scene, "blender", blender)

jug = Asset("water_jug")
jugx, jugy = .345, -.17
add(jug, "body",
    fillet_box((.265,.23,.245), radius=.055,
               center=(jugx,jugy,.9325), color=(.69,.72,.67)))
ellipsoid(jug, "rounded_shoulders", (jugx,jugy,1.045),
          (.129,.111,.135), (.72,.74,.69))
add(jug, "neck",
    rod(.039, length=.063, center=(jugx,jugy,1.167), color=(.78,.79,.72)))
add(jug, "cap",
    rod(.042, length=.025, center=(jugx,jugy,1.205), color=(.88,.87,.78)))
tube(jug, "handle",
     [(jugx+.068,jugy,1.145), (jugx+.123,jugy,1.13),
      (jugx+.145,jugy,1.078), (jugx+.125,jugy,1.048),
      (jugx+.10,jugy,1.07)], .015, (.76,.77,.71))
for i, x in enumerate((-.064,-.039,-.014,.011,.036,.061)):
    add(jug, f"label_stroke_{i}",
        rod(.0015, start=(jugx+x,jugy-.117,.885),
            end=(jugx+x-.003,jugy-.117,.915), color=(.32,.34,.29)))
    if i in (0,2,4):
        add(jug, f"label_crossbar_{i}",
            rod(.0012, start=(jugx+x-.004,jugy-.118,.908),
                end=(jugx+x+.011,jugy-.118,.908), color=(.32,.34,.29)))
add(scene, "water_jug", jug)

pitcher = Asset("filter_pitcher")
px, py = .735, .105
shell_outer = rod(.145, length=.35, center=(px,py,.995),
                  color=(.085,.15,.25), opacity=.74)
shell_inner = rod(.132, length=.36, center=(px,py,1.015))
add(pitcher, "blue_shell", subtract(shell_outer, shell_inner))
add(pitcher, "blue_bottom",
    rod(.136, length=.022, center=(px,py,.827),
        color=(.075,.13,.22), opacity=.85))
add(pitcher, "filter_reservoir",
    rod(.108, length=.21, center=(px,py,1.055),
        color=(.08,.12,.19), opacity=.86))
lid = fillet_box((.30,.255,.035), radius=.016,
                  center=(px-.014,py,1.184), color=(.40,.42,.37))
lid.turn("y", -7)
add(pitcher, "lid", lid)
spout = box((.095,.10,.036), center=(px-.153,py,1.178),
            color=(.42,.44,.38))
spout.turn("y", -16)
add(pitcher, "spout", spout)
hp = []
for i in range(33):
    a = math.pi/2-math.pi*i/32
    hp.append((px+.13+.105*math.cos(a), py, 1.00+.164*math.sin(a)))
tube(pitcher, "clear_handle", hp, .019, (.51,.55,.50))
add(scene, "filter_pitcher", pitcher)

realize(scene)

def owner_meshes(slot):
    root = bpy.data.objects.get(slot)
    if root is None or root.type != 'EMPTY':
        candidates = [
            o for o in bpy.data.objects
            if o.type == 'EMPTY' and o.name.split('.')[0] == slot
        ]
        assert candidates, f"Missing semantic marker: {slot}"
        root = candidates[0]
    meshes = [o for o in root.children_recursive if o.type == 'MESH']
    assert meshes, f"No mesh descendants: {slot}"
    return meshes

def customize(slot, metallic=None, roughness=None, texture=None):
    for obj in owner_meshes(slot):
        obj.data = obj.data.copy()
        for idx, original in enumerate(list(obj.data.materials)):
            if original is None:
                continue
            mat = original.copy()
            obj.data.materials[idx] = mat
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bs = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if bs is None:
                continue
            if metallic is not None:
                bs.inputs["Metallic"].default_value = metallic
            if roughness is not None:
                bs.inputs["Roughness"].default_value = roughness
            if texture == "stone":
                noise = nodes.new("ShaderNodeTexNoise")
                noise.inputs["Scale"].default_value = 185
                noise.inputs["Detail"].default_value = 2.5
                ramp = nodes.new("ShaderNodeValToRGB")
                ramp.color_ramp.elements[0].position = .22
                ramp.color_ramp.elements[0].color = (.065,.061,.047,1)
                ramp.color_ramp.elements[1].position = .77
                ramp.color_ramp.elements[1].color = (.57,.53,.42,1)
                middle = ramp.color_ramp.elements.new(.51)
                middle.color = (.255,.24,.19,1)
                links.new(noise.outputs["Fac"], ramp.inputs[0])
                links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
                bump = nodes.new("ShaderNodeBump")
                bump.inputs["Strength"].default_value = .25
                bump.inputs["Distance"].default_value = .006
                links.new(noise.outputs["Fac"], bump.inputs["Height"])
                links.new(bump.outputs["Normal"], bs.inputs["Normal"])
            elif texture == "fabric":
                noise = nodes.new("ShaderNodeTexNoise")
                noise.inputs["Scale"].default_value = 220
                noise.inputs["Detail"].default_value = 2
                bump = nodes.new("ShaderNodeBump")
                bump.inputs["Strength"].default_value = .20
                bump.inputs["Distance"].default_value = .002
                links.new(noise.outputs["Fac"], bump.inputs["Height"])
                links.new(bump.outputs["Normal"], bs.inputs["Normal"])

customize("stone_slab", roughness=.62, texture="stone")
customize("backsplash", roughness=.62, texture="stone")
customize("towel_ring", metallic=.82, roughness=.23)
customize("sink_and_faucet", metallic=.70, roughness=.27)
customize("towel", roughness=.96, texture="fabric")
customize("paper_cylinder", roughness=.92, texture="fabric")
customize("loose_paper_edge", roughness=.92, texture="fabric")
customize("water_jug", roughness=.48)
customize("filter_pitcher", roughness=.25)

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((-1.5,-.15,2.55), power=210, size=1.5,
             target=(.15,.0,1.30), color=(.88,.95,1.0))
area_emitter((-.45,-2.0,3.1), power=95, size=2.6,
             target=(.15,.05,1.6), color=(1.0,.86,.65))

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.66,.71,.75,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .30

sc = bpy.context.scene
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .25
sc.render.image_settings.file_format = 'PNG'
