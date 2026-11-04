from sceneact import *
import bpy

# Evidence ledger: image-space bounds are visual estimates, not measurements.
# Reference / step-1 render:
# foreground post: x64..119 / x55..130, reference foot near y500, render cropped;
# island: x127..345,y280..434 / x129..369,y310..474;
# hood: x160..279,y23..224 / x124..269,y69..259;
# far oven: approximately x258..299,y220..290 / x225..260,y250..323.
# Island and hood are consistently too low. Hood also has a local horizontal
# mismatch; the foreground post is too broad. Those are retained for this probe.
# Selected family: camera framing only. Negative vertical lens shift predicts
# an upward image translation of roughly 35-40 pixels, without changing edge
# directions, relative occlusion, geometry, lighting or material assignments.
# Island bottom and hood bottom should approach reference y434 and y224.
# Independent anchors considered: foreground post crop, hood architectural
# verticals, island floor contact, and distant oven. Estimates are uncertain.
# Measured evidence: step 1 returned a valid render; execute elapsed was 3.396s.
# That duration does not isolate construction or rendering.

CAMERA = dict(position=(-6.2, -4.6, 2.65),
              target=(0.25, 0.40, 1.72), lens=49, sensor=32,
              shift=(0, -0.075))
ISLAND = dict(cx=0.35, cy=-0.35, width=2.45, depth=1.22,
              top=0.96, slab=0.045, base=0.075)
HOOD = dict(cx=-0.08, cy=0.05, width=1.12, depth=0.88,
            bottom=1.83, top=3.62)
PALETTE = dict(
    floor=(0.60, 0.59, 0.55),
    wall=(0.29, 0.30, 0.28),
    black=(0.025, 0.031, 0.030),
    cabinet=(0.045, 0.052, 0.050),
    island=(0.62, 0.64, 0.61),
    stone=(0.79, 0.80, 0.74),
    hood=(0.78, 0.77, 0.68),
    wood=(0.40, 0.23, 0.11),
    metal=(0.43, 0.46, 0.44),
    glass=(0.012, 0.024, 0.028)
)
scene = Scene("Industrial kitchen")

def cube(owner, name, size, center, color):
    return owner.include(name, box(size=size, center=center, color=color))

# Ownership/support ledger:
# architecture -> structural surfaces, beams and floor joints; floor top z=0.
# timber_posts -> foreground and far structural posts, supported at z=0.
# rear_cabinetry -> carcase, doors, worktop, backsplash and attached strip.
# left_tall_cupboard -> body and attached doors, supported at floor.
# oven_stack -> housing and all appliance components, supported at floor.
# right_partition -> upright and fascia; uncertain doorway geometry behind.
# island -> carcase, fronts, counter, sink, hob and faucet; floor-supported.
# extractor_hood -> ceiling-suspended enclosure, filter, lip and switch.
# red_kettle -> body, lid, base, handle and spout; worktop support z=.92.
# Front-to-back: foreground timber, island, rear worktop/appliances, rear wall.
# Pale island and hood dominate the middle; dark cabinetry and ceiling surround
# them. Step 1 is flatter/lighter than the photograph; appearance is held fixed.
# The kettle is constructed behind foreground occluders, so it is not duplicated.

arch = scene.include("architecture", Asset("Architecture"))
cube(arch, "floor", (14, 13, .12), (0, 0, -.06), PALETTE["floor"])
cube(arch, "rear_wall", (8.8, .16, 3.65), (0, 2.13, 1.825), PALETTE["wall"])
cube(arch, "right_return", (.17, 2.3, 2.75), (3.23, 1.12, 1.375), (.13,.15,.14))
cube(arch, "ceiling", (12, 10, .15), (0, 0, 3.75), (.022,.028,.027))
for i, x in enumerate([-3.4, -2.1, -.8, .5, 1.8, 3.1]):
    cube(arch, f"ceiling_beam_{i}", (.16, 8, .24),
         (x, .1, 3.57), (.035,.043,.041))
for i, y in enumerate([-1.5, .1, 1.7, 3.3]):
    cube(arch, f"cross_beam_{i}", (10, .13, .17),
         (0, y, 3.52), (.042,.049,.047))
for i, x in enumerate([-4, -2.4, -.8, .8, 2.4, 4]):
    cube(arch, f"floor_joint_x_{i}", (.005, 10, .0015),
         (x, 0, .001), (.39,.39,.36))
for i, y in enumerate([-3.2, -1.6, 0, 1.6, 3.2]):
    cube(arch, f"floor_joint_y_{i}", (12, .005, .0015),
         (0, y, .001), (.39,.39,.36))

posts = scene.include("timber_posts", Asset("TimberPosts"))
cube(posts, "foreground_post", (.38, .37, 3.85),
     (-1.92, -.32, 1.925), PALETTE["wood"])
cube(posts, "far_post", (.18, .20, 3.43),
     (3.10, .53, 1.715), PALETTE["wood"])

rear = scene.include("rear_cabinetry", Asset("RearCabinetry"))
cube(rear, "lower_carcase", (5.25, .62, .83),
     (-.15, 1.66, .465), PALETTE["cabinet"])
cube(rear, "recessed_toe", (5.22, .48, .08),
     (-.15, 1.72, .04), (.013,.017,.016))
cube(rear, "worktop", (5.35, .68, .04),
     (-.15, 1.63, .90), (.12,.13,.12))
for i, x in enumerate([-2.20, -1.32, -.44, .44, 1.32]):
    cube(rear, f"base_door_{i}", (.865, .025, .79),
         (x, 1.335, .475), PALETTE["cabinet"])
cube(rear, "backsplash", (5.5, .035, .67),
     (-.10, 2.025, 1.26), (.055,.066,.061))
for i, x in enumerate([-2.25, -1.32, -.39, .54, 1.47]):
    cube(rear, f"upper_door_{i}", (.918, .39, .69),
         (x, 1.80, 1.94), PALETTE["cabinet"])
cube(rear, "light_strip", (3.70, .035, .018),
     (-.65, 1.60, 1.584), (.84,.72,.57))

tall = scene.include("left_tall_cupboard", Asset("TallCupboard"))
cube(tall, "body", (.80, .76, 2.34), (-2.81, 1.43, 1.17), (.035,.042,.040))
cube(tall, "door", (.775, .025, 2.27), (-2.81, 1.037, 1.175), (.047,.054,.052))
cube(tall, "upper_joint", (.78, .009, .008), (-2.81, 1.020, 2.03), (.018,.023,.021))

ovens = scene.include("oven_stack", Asset("OvenStack"))
cube(ovens, "housing", (.80, .70, 2.43), (2.42, 1.62, 1.215), (.032,.040,.037))
for i, (z, h) in enumerate([(1.36, .55), (.81, .50)]):
    cube(ovens, f"oven_frame_{i}", (.68, .055, h),
         (2.42, 1.245, z), PALETTE["metal"])
    cube(ovens, f"oven_glass_{i}", (.59, .018, h-.14),
         (2.42, 1.208, z-.02), PALETTE["glass"])
    cube(ovens, f"oven_controls_{i}", (.61, .025, .065),
         (2.42, 1.197, z+h/2-.055), (.17,.18,.17))
    cube(ovens, f"oven_handle_{i}", (.49, .055, .025),
         (2.42, 1.167, z+h/2-.115), (.56,.58,.56))
cube(ovens, "lower_door", (.69,.03,.46), (2.42,1.247,.29), PALETTE["cabinet"])
cube(ovens, "upper_door", (.69,.03,.70), (2.42,1.247,2.02), PALETTE["cabinet"])

partition = scene.include("right_partition", Asset("RightPartition"))
cube(partition, "slab", (.26, .92, 2.26),
     (3.03, 1.23, 1.13), (.025,.032,.030))
cube(partition, "top_fascia", (1.2,.20,.26),
     (2.65,1.87,2.42), (.23,.26,.24))

island = scene.include("island", Asset("KitchenIsland"))
cx, cy = ISLAND["cx"], ISLAND["cy"]
w, d, top = ISLAND["width"], ISLAND["depth"], ISLAND["top"]
cube(island, "plinth", (w-.12,d-.12,.10), (cx,cy,.05), (.16,.18,.17))
cube(island, "carcase", (w-.035,d-.035,.805),
     (cx,cy,.5025), PALETTE["island"])
cube(island, "left_end", (.055,d,.873),
     (cx-w/2+.0275,cy,.5115), (.57,.59,.56))
cube(island, "right_end", (.045,d,.873),
     (cx+w/2-.0225,cy,.5115), PALETTE["island"])
cube(island, "countertop", (w+.035,d+.035,ISLAND["slab"]),
     (cx,cy,top-ISLAND["slab"]/2), PALETTE["stone"])
for i, z in enumerate([.235,.510,.785]):
    cube(island, f"drawer_front_{i}", (w-.10,.045,.263),
         (cx,cy-d/2-.009,z), PALETTE["island"])
    cube(island, f"drawer_pull_reveal_{i}", (w-.12,.015,.014),
         (cx,cy-d/2-.034,z+.119), (.23,.25,.23))

sinkx, sinky = cx+.47, cy+.20
cube(island, "sink_inset", (.59,.37,.008),
     (sinkx,sinky,top+.001), (.36,.40,.37))
cube(island, "sink_bottom", (.49,.28,.009),
     (sinkx,sinky,top+.007), (.59,.62,.57))
for key, size, pos in [
    ("front",(.63,.018,.014),(sinkx,sinky-.195,top+.008)),
    ("back",(.63,.018,.014),(sinkx,sinky+.195,top+.008)),
    ("left",(.018,.38,.014),(sinkx-.307,sinky,top+.008)),
    ("right",(.018,.38,.014),(sinkx+.307,sinky,top+.008))]:
    cube(island,"sink_rim_"+key,size,pos,(.76,.78,.71))
tapx, tapy = sinkx+.03, sinky+.27
island.include("tap_upright", rod(
    .014, start=(tapx,tapy,top), end=(tapx,tapy,top+.235),
    color=(.56,.61,.58)))
island.include("tap_spout", sweep_tube(
    points=[(tapx,tapy,top+.235), (tapx,tapy-.025,top+.265),
            (tapx,tapy-.15,top+.265),(tapx,tapy-.18,top+.235)],
    radius=.013,color=(.58,.63,.60)))
cube(island, "tap_lever", (.055,.018,.014),
     (tapx+.026,tapy,top+.13),(.57,.61,.58))
cube(island, "flush_hob", (.66,.43,.003),
     (cx-.57,cy-.05,top+.002), (.73,.75,.69))
for i in [-1,1]:
    cube(island,f"hob_line_{i}",(.53,.007,.002),
         (cx-.57,cy-.05+i*.14,top+.004),(.82,.83,.76))

hood = scene.include("extractor_hood", Asset("ExtractorHood"))
h = HOOD
cube(hood,"enclosure",(h["width"],h["depth"],h["top"]-h["bottom"]),
     (h["cx"],h["cy"],(h["top"]+h["bottom"])/2), PALETTE["hood"])
cube(hood,"underside_filter",(.82,.57,.015),
     (h["cx"],h["cy"],h["bottom"]-.003),(.35,.37,.32))
cube(hood,"lower_lip",(h["width"]+.014,h["depth"]+.014,.018),
     (h["cx"],h["cy"],h["bottom"]+.009),(.68,.69,.61))
cube(hood,"small_switch",(.042,.013,.015),
     (h["cx"]-.30,h["cy"]-h["depth"]/2-.008,h["bottom"]+.025),(.22,.23,.20))

kettle = scene.include("red_kettle", Asset("RedKettle"))
kx, ky, kz = -.38, 1.61, .922
kettle.include("body", ball(.092, center=(kx,ky,kz+.095), color=(.72,.008,.025)))
cube(kettle,"base",(.15,.13,.025),(kx,ky,kz+.013),(.015,.018,.017))
cube(kettle,"lid",(.10,.085,.018),(kx,ky,kz+.178),(.025,.027,.025))
kettle.include("handle", sweep_tube(
    points=[(kx-.068,ky,kz+.11),(kx-.085,ky,kz+.19),
            (kx-.025,ky,kz+.225),(kx+.055,ky,kz+.20),
            (kx+.075,ky,kz+.12)],
    radius=.012, color=(.025,.028,.026)))
kettle.include("spout", rod(.022,start=(kx+.062,ky,kz+.10),
                            end=(kx+.12,ky,kz+.145),color=(.10,.11,.10)))

# Inline pre-execution review:
# Camera shift is the only changed parameter; complete owner dimensions and
# transforms remain fixed. Upright edges, shadow contrast and overlaps persist.
# Floor z=0 supports posts and furniture; rear worktop top=.92 supports kettle.
# Island counter top=.96 supports attached tap, sink rim and flush hob.
# Hidden geometry/contact and absolute scale remain uncertain visual hypotheses.
# All include names are unique per parent; all dimensions positive and finite.
# No fillets; every rod and adjacent tube endpoint is distinct.
# Around 110 primitives overall: loops are mainly boxes; two curved tube families
# expand to 7 and 9 primitives. No dense ornament or new geometry after realize.
# Shader scopes below assert nonempty marker descendants and copy mesh data.
# This is a code review, not a claim of execution or regression-test success.
realize(scene)

def descendants(slot):
    marker = bpy.data.objects.get(slot)
    assert marker is not None, "Missing semantic marker: " + slot
    meshes = [o for o in marker.children_recursive if o.type == 'MESH']
    if marker.type == 'MESH':
        meshes.append(marker)
    assert meshes, "Empty material scope: " + slot
    return meshes

def scoped_material(slot, name, color, roughness=.6, metallic=0.0, texture=None):
    meshes = descendants(slot)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color,1)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    if texture:
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = texture["scale"]
        tex.inputs["Detail"].default_value = 2
        coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = texture["stretch"]
        links.new(coord.outputs["Generated"],mapping.inputs[0])
        links.new(mapping.outputs[0],tex.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .20
        ramp.color_ramp.elements[0].color = (*texture["dark"],1)
        ramp.color_ramp.elements[1].position = .80
        ramp.color_ramp.elements[1].color = (*texture["light"],1)
        links.new(tex.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .15
        bump.inputs["Distance"].default_value = .008
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    for obj in meshes:
        obj.data = obj.data.copy()
        obj.data.materials.clear()
        obj.data.materials.append(mat)

scoped_material("timber_posts", "Warm longitudinal timber",
                PALETTE["wood"], .68, texture={
                    "scale":5, "stretch":(3.5,3.5,.15),
                    "dark":(.22,.105,.038), "light":(.56,.37,.19)})
scoped_material("extractor_hood", "Pale mineral hood", PALETTE["hood"], .85,
                texture={"scale":65,"stretch":(1,1,1),
                         "dark":(.66,.65,.57),"light":(.83,.82,.74)})
scoped_material("tap_upright","Tap metal upright",(.58,.62,.59),.23,.8)
scoped_material("tap_spout","Tap metal spout",(.58,.62,.59),.23,.8)

set_view(**CAMERA)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.56,.61,.65,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .23
area_emitter((-3.5,-3.5,3.25), power=650, size=4.0,
             target=(.2,.1,.8), color=(1,.94,.84))
area_emitter((.8,-.4,3.32), power=190, size=2.4,
             target=(.3,-.3,.8), color=(.95,.98,1))
area_emitter((-.6,1.48,1.53), power=45, size=1.8,
             target=(-.6,1.98,1.12), color=(1,.72,.52))
area_emitter((3.6,-.1,2.7), power=220, size=2.3,
             target=(1,.6,1.0), color=(.88,.94,1))
# Runner owns render settings, saving and rendering.
