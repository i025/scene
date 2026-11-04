from sceneact import *
import bpy

# Stable anchors from the second render: island and hood lower edge are close.
# Reference: timber x=.16-.31; hood x=.42-.73, y=.05-.44;
# island x=.33-.90, y=.56-.85. Main residuals are the cropped hood top,
# a small horizontal framing offset, and the missing dark right cabinet mass.
# Preserve the camera perspective, island geometry, and foreground occlusion.
P = dict(camera=(-4.6, -2.5, 1.65), target=(0, .4, 1.45),
         lens=40, shift=(-.030, 0), island_center=(.35, .10),
         island_size=(2.20, 1.04), hood_bottom=1.85, hood_height=1.40)

scene = Scene("Editable modern kitchen showroom")
WHITE = (.61, .63, .60)
TOP = (.75, .77, .72)
BLACK = (.014, .018, .016)
WOOD = (.40, .255, .135)
HOOD = (.66, .65, .59)
METAL = (.38, .40, .39)

def cube(asset, name, size, center, color):
    asset.include(name, box(size, center=center, color=color))

architecture = Asset("Architecture")
cube(architecture, "floor", (14, 13, .12), (0, 0, -.07), (.63, .62, .58))
cube(architecture, "rear_wall", (10, .16, 3.7), (0, 2.42, 1.80), (.19, .21, .20))
cube(architecture, "left_wall", (.15, 8, 3.7), (-5.8, 1, 1.80), (.34, .35, .32))
cube(architecture, "dark_ceiling", (12, 10, .12), (0, 0, 3.71), (.012, .017, .016))
for i in range(-6, 7):
    cube(architecture, "tile_x_%d" % i, (.005, 12, .002),
         (i * 1.15, 0, -.008), (.44, .44, .41))
for i in range(-5, 6):
    cube(architecture, "tile_y_%d" % i, (13, .005, .002),
         (0, i * 1.15, -.007), (.44, .44, .41))
scene.include("architecture", architecture)

ceiling = Asset("Exposed dark ceiling structure")
for i, x in enumerate([-3, -1.6, 0, 1.6, 3.2]):
    cube(ceiling, "long_beam_%d" % i, (.14, 8, .19),
         (x, 0, 3.54), (.018, .025, .023))
for i, y in enumerate([-2.4, -.7, 1, 2.7]):
    cube(ceiling, "cross_beam_%d" % i, (9, .12, .13),
         (0, y, 3.59), (.022, .029, .027))
for i in range(13):
    cube(ceiling, "roof_seam_%d" % i, (.018, 8, .025),
         (-3.6 + i * .6, 0, 3.635), (.035, .040, .035))
cube(ceiling, "overhead_girder", (.28, 8, .26),
     (2.15, -.3, 3.51), (.065, .080, .077))
scene.include("ceiling_structure", ceiling)

posts = Asset("Natural oak structural posts")
cube(posts, "foreground_post", (.25, .28, 3.76), (-1.95, 0, 1.87), WOOD)
cube(posts, "distant_post", (.19, .20, 3.65), (2.48, 1.55, 1.825), WOOD)
scene.include("timber_posts", posts)

rear = Asset("Rear black kitchen cabinetry")
cube(rear, "left_tall_case", (.88, .64, 2.12), (-2.02, 1.95, 1.06), BLACK)
for i in range(2):
    cube(rear, "left_door_%d" % i, (.427, .025, 2.04),
         (-2.245 + i * .439, 1.615, 1.075), (.020, .024, .021))
cube(rear, "rear_base", (3.35, .62, .88), (.02, 1.93, .46), BLACK)
cube(rear, "rear_worktop", (3.42, .69, .045), (.02, 1.895, .922), (.065, .070, .060))
for i in range(5):
    cube(rear, "base_door_%d" % i, (.65, .027, .79),
         (-1.31 + i * .67, 1.603, .46), (.021, .025, .022))
cube(rear, "niche_back", (2.64, .035, .52), (-.22, 2.226, 1.23), (.17, .13, .115))
cube(rear, "niche_bottom", (2.65, .63, .025), (-.22, 1.92, .963), (.085, .080, .070))
cube(rear, "niche_upper_band", (2.76, .60, .40), (-.20, 1.96, 1.72), (.020, .027, .023))
cube(rear, "niche_led", (2.55, .025, .014), (-.22, 2.05, 1.512), (.95, .77, .56))
for i in range(4):
    cube(rear, "upper_panel_%d" % i, (.69, .035, .40),
         (-1.245 + i * .70, 1.635, 1.72), (.024, .032, .027))
scene.include("rear_cabinets", rear)

oven = Asset("Tall appliance tower")
cube(oven, "tower_body", (.86, .72, 2.18), (1.78, 1.92, 1.09), BLACK)
cube(oven, "left_stile", (.10, .025, 2.10), (1.39, 1.545, 1.10), (.045, .050, .046))
cube(oven, "right_stile", (.11, .025, 2.10), (2.15, 1.545, 1.10), (.042, .047, .043))
for i, z in enumerate([.59, 1.18]):
    cube(oven, "frame_%d" % i, (.65, .055, .49), (1.77, 1.535, z), (.24, .25, .23))
    cube(oven, "glass_%d" % i, (.57, .022, .32), (1.77, 1.497, z - .035), (.012, .022, .026))
    cube(oven, "controls_%d" % i, (.60, .025, .073), (1.77, 1.494, z + .185), (.31, .32, .30))
    cube(oven, "handle_%d" % i, (.53, .046, .024), (1.77, 1.46, z + .115), (.44, .46, .44))
cube(oven, "bottom_door", (.65, .03, .29), (1.77, 1.53, .19), (.022, .027, .023))
cube(oven, "upper_door", (.65, .03, .46), (1.77, 1.53, 1.78), (.018, .025, .021))
scene.include("oven_tower", oven)

partition = Asset("Right dark cabinet and partition")
cube(partition, "end_wall", (.18, 1.34, 2.38), (2.40, 1.97, 1.19), (.018, .025, .020))
cube(partition, "right_tall_cabinet", (1.24, .72, 2.38),
     (2.94, 1.94, 1.19), (.017, .023, .019))
for i in range(2):
    cube(partition, "right_front_%d" % i, (.599, .028, 2.29),
         (2.63 + i * .62, 1.565, 1.185), (.021, .027, .023))
cube(partition, "upper_fascia", (4.45, .22, .32),
     (1.40, 2.28, 2.48), (.25, .28, .27))
scene.include("right_partition", partition)

cx, cy = P["island_center"]
w, d = P["island_size"]
island = Asset("Pale gray island with three handleless drawers")
cube(island, "recessed_plinth", (w - .10, d - .10, .095), (cx, cy, .07), (.16, .17, .15))
cube(island, "carcass", (w, d, .81), (cx, cy, .505), (.49, .51, .48))
cube(island, "left_waterfall_end", (.055, d, .91), (cx - w / 2 - .005, cy, .505), WHITE)
cube(island, "right_end", (.035, d, .87), (cx + w / 2 - .012, cy, .49), WHITE)
cube(island, "stone_countertop", (w + .045, d + .035, .045), (cx, cy, .9725), TOP)
for i, (z, h) in enumerate([(.226, .245), (.491, .245), (.756, .245)]):
    cube(island, "drawer_%d" % i, (w - .07, .038, h),
         (cx + .012, cy - d / 2 - .008, z), (.61, .63, .60))
    cube(island, "drawer_reveal_%d" % i, (w - .075, .018, .016),
         (cx + .012, cy - d / 2 - .009, z + h / 2 + .008), (.22, .24, .21))
scene.include("island", island)

sink = Asset("Flush sink and chrome mixer")
sx, sy = .62, .305
cube(sink, "sink_rim", (.57, .40, .009), (sx, sy, .998), (.53, .57, .54))
cube(sink, "sink_inner", (.50, .33, .010), (sx, sy, 1.003), (.42, .47, .44))
cube(sink, "sink_basin", (.435, .266, .007), (sx, sy, 1.009), (.53, .58, .55))
sink.include("tap_base", rod(.033, start=(sx + .03, sy + .29, .997),
                            end=(sx + .03, sy + .29, 1.03), color=METAL))
sink.include("tap_upright", rod(.014, start=(sx + .03, sy + .29, 1.02),
                               end=(sx + .03, sy + .29, 1.25), color=(.60, .64, .62)))
sink.include("tap_neck", sweep_tube(
    points=[(sx + .03, sy + .29, 1.25), (sx + .03, sy + .27, 1.29),
            (sx + .03, sy + .13, 1.29), (sx + .03, sy + .10, 1.25)],
    radius=.014, color=(.62, .65, .63)))
sink.include("tap_handle", rod(.009, start=(sx + .075, sy + .29, 1.07),
                             end=(sx + .075, sy + .29, 1.16), color=(.52, .56, .54)))
cube(sink, "flush_hob", (.62, .46, .006), (-.29, .08, 1), (.71, .74, .69))
for i, x in enumerate([-.46, -.16]):
    cube(sink, "hob_mark_%d" % i, (.19, .006, .002), (x, -.02, 1.005), (.87, .88, .82))
scene.include("sink_and_hob", sink)

hood = Asset("Suspended plaster extractor")
hz = P["hood_bottom"]
hh = P["hood_height"]
cube(hood, "plaster_body", (1.10, .88, hh), (.02, .09, hz + hh / 2), HOOD)
cube(hood, "underside", (1.075, .85, .025), (.02, .09, hz - .005), (.48, .48, .43))
cube(hood, "filter", (.65, .46, .009), (.02, .09, hz - .021), (.28, .29, .26))
cube(hood, "control", (.055, .015, .018), (.02, -.357, hz + .02), (.30, .31, .28))
scene.include("suspended_hood", hood)

kettle = Asset("Small red kettle")
kettle.include("body", ball(.104, center=(-.35, 1.84, 1.065), color=(.65, .012, .025)))
cube(kettle, "base", (.18, .15, .035), (-.35, 1.84, .974), (.016, .018, .017))
cube(kettle, "front", (.13, .055, .12), (-.35, 1.754, 1.035), (.013, .018, .017))
kettle.include("handle", sweep_tube(
    points=[(-.43, 1.84, 1.085), (-.43, 1.84, 1.17),
            (-.32, 1.84, 1.195), (-.25, 1.84, 1.14)],
    radius=.014, color=(.80, .015, .025)))
scene.include("red_kettle", kettle)

track = Asset("Ceiling track lighting")
cube(track, "track", (.045, 3.7, .045), (-1.80, .35, 3.38), (.025, .030, .026))
for i, y in enumerate([-.40, 1.15]):
    track.include("stem_%d" % i, rod(.013, start=(-1.8, y, 3.38),
                                    end=(-1.8, y, 3.27), color=(.1, .11, .10)))
    track.include("spot_%d" % i, rod(.047, start=(-1.8, y, 3.28),
                                    end=(-1.76, y - .06, 3.20), color=(.43, .45, .42)))
scene.include("ceiling_lights", track)

print("SceneAct primitive count:", sum(n.solid is not None for n in scene.traverse()))
realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes = True
    nt = mat.node_tree
    bs = nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    rgb = tuple(bs.inputs["Base Color"].default_value[:3])
    bs.inputs["Roughness"].default_value = .52
    if sum(abs(rgb[i] - WOOD[i]) for i in range(3)) < .025:
        coords = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = (8, 8, .32)
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 4
        noise.inputs["Detail"].default_value = 3
        nt.links.new(coords.outputs["Generated"], mapping.inputs[0])
        nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .20
        ramp.color_ramp.elements[0].color = (.16, .082, .033, 1)
        ramp.color_ramp.elements[1].position = .80
        ramp.color_ramp.elements[1].color = (.57, .37, .20, 1)
        nt.links.new(noise.outputs["Fac"], ramp.inputs[0])
        nt.links.new(ramp.outputs[0], bs.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .17
        bump.inputs["Distance"].default_value = .012
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    elif sum(abs(rgb[i] - HOOD[i]) for i in range(3)) < .020:
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 105
        noise.inputs["Detail"].default_value = 2
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .12
        bump.inputs["Distance"].default_value = .008
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
        bs.inputs["Roughness"].default_value = .85
    elif min(rgb) > .35 and max(rgb) - min(rgb) < .09:
        bs.inputs["Roughness"].default_value = .30

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (.32, .35, .36, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = .28

set_view(P["camera"], P["target"], lens=P["lens"], sensor=36, shift=P["shift"])
area_emitter((-3, -3.3, 3.2), power=850, size=4,
             target=(.1, 0, .7), color=(1, .94, .83))
area_emitter((1.8, -.7, 3.3), power=450, size=3,
             target=(.3, .3, .8), color=(.89, .94, 1))
area_emitter((-.25, 1.94, 1.49), power=45, size=1.6,
             target=(-.25, 1.91, .95), color=(1, .69, .48))
area_emitter((-2.7, .8, 2.8), power=160, size=1.8,
             target=(-1, 1.5, 1.1), color=(1, .94, .82))
sc.view_settings.view_transform = "AgX"
