from sceneact import *
import bpy
import math

# ---------------------------------------------------------------------------
# Reference inventory (normalized image bounds are approximate):
#
# 1. room_shell [0.00,0.00]-[1.00,1.00]:
#    cream/yellow side walls, pale tiled floor, white ceiling, deep rectangular hall.
#    Side walls are partly hidden by desks; rear wall is mostly hidden by the stage.
# 2. desk_field [0.00,0.36]-[0.94,0.89]:
#    about 20-24 dark wooden desks/benches in four loose columns, with a central aisle.
#    Foreground desks overlap bags and obscure many rear legs.
# 3. stage [0.34,0.20]-[0.67,0.43]:
#    raised dark platform, maroon curtain opening, cream scalloped valance, green wings.
# 4. chalkboard [0.45,0.31]-[0.58,0.43]:
#    green rectangular board on a narrow support, overlapping the curtain opening.
# 5. side_openings [0.00,0.11]-[1.00,0.66]:
#    repeated tall windows and brown paneled doors on both walls; exact recess depth uncertain.
# 6. ceiling_fans [0.06,0.00]-[0.86,0.18]:
#    four visible dark fans, each with hub, down-rod and long blades.
# 7. fluorescent_lights [0.33,0.05]-[0.65,0.19]:
#    narrow white ceiling fixtures aligned along the room.
# 8. backpacks [0.08,0.55]-[0.86,0.91]:
#    several black/blue bags resting on the floor and overlapping desk legs.
# 9. wall_details [0.13,0.07]-[0.94,0.33]:
#    framed portraits and dark wall-mounted speaker/monitor boxes.
#
# Asset mapping:
# room_shell -> architecture; desk_field -> desk_row assets containing desk and bench parts;
# stage -> stage_asset; chalkboard -> chalkboard_asset; side_openings -> opening assets;
# ceiling_fans -> fan assets; fluorescent_lights -> light_fixture assets;
# backpacks -> backpack assets; wall_details -> frame and speaker assets.
#
# Primitive estimate:
# architecture ~35, 22 desk/bench units x 9 = 198, stage ~28,
# 4 fans x 6 = 24, 7 bags x 5 = 35, fixtures/details ~35.
# Estimated expanded total: ~355 mesh primitives plus hierarchy markers.
# No fillet_box, Boolean, cloning-layout, or long sweep_tube expansions are used.

scene = Scene("Indian_Classroom_Hall")

# Palette
CREAM = (0.84, 0.82, 0.66)
YELLOW = (0.93, 0.67, 0.02)
WHITE = (0.92, 0.92, 0.89)
WOOD = (0.27, 0.14, 0.065)
WOOD_DARK = (0.16, 0.075, 0.028)
WOOD_LIGHT = (0.42, 0.24, 0.10)
FLOOR = (0.69, 0.55, 0.36)
GREEN = (0.06, 0.28, 0.12)
BOARD = (0.08, 0.30, 0.23)
MAROON = (0.22, 0.025, 0.035)
BLACK = (0.018, 0.022, 0.025)
BLUE = (0.015, 0.22, 0.58)
CYAN = (0.02, 0.48, 0.75)
METAL = (0.22, 0.20, 0.18)

ROOM_W = 10.4
ROOM_D = 17.2
CEILING_Z = 4.75
WALL_T = 0.16

# Architecture
architecture = Asset("architecture")
architecture.include(
    "tiled_floor",
    box((ROOM_W, ROOM_D, 0.10), center=(0, 0, -0.05), color=FLOOR)
)
architecture.include(
    "ceiling",
    box((ROOM_W, ROOM_D, 0.12), center=(0, 0, CEILING_Z), color=WHITE)
)
architecture.include(
    "front_wall",
    box((ROOM_W, 0.18, CEILING_Z), center=(0, 8.50, CEILING_Z / 2), color=CREAM)
)
architecture.include(
    "rear_header",
    box((ROOM_W, 0.18, 0.65), center=(0, -8.50, 4.43), color=CREAM)
)

# Side walls are split into yellow lower and cream upper bands.
for side, x in (("left", -ROOM_W/2), ("right", ROOM_W/2)):
    architecture.include(
        f"{side}_yellow_band",
        box((WALL_T, ROOM_D, 1.30), center=(x, 0, 0.65), color=YELLOW)
    )
    architecture.include(
        f"{side}_cream_upper",
        box((WALL_T, ROOM_D, CEILING_Z-1.30),
            center=(x, 0, 1.30 + (CEILING_Z-1.30)/2), color=CREAM)
    )

# Ceiling beams running across the hall.
for i, y in enumerate((-5.7, -2.0, 2.0, 5.5)):
    architecture.include(
        f"ceiling_beam_{i}",
        box((ROOM_W-0.2, 0.22, 0.24), center=(0, y, 4.55), color=(0.83, 0.83, 0.80))
    )

scene.include("architecture", architecture)

# Subtle floor tile seams, limited to broad lines visible in the foreground.
tile_lines = Asset("floor_tile_seams")
for i, x in enumerate((-4, -3, -2, -1, 0, 1, 2, 3, 4)):
    tile_lines.include(
        f"long_seam_{i}",
        box((0.012, ROOM_D, 0.006), center=(x, 0, 0.006), color=(0.46, 0.35, 0.23))
    )
for i, y in enumerate((-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6)):
    tile_lines.include(
        f"cross_seam_{i}",
        box((ROOM_W, 0.012, 0.006), center=(0, y, 0.007), color=(0.46, 0.35, 0.23))
    )
scene.include("floor_tile_seams", tile_lines)

# Tall wooden side doors and bright window panels.
side_openings = Asset("side_openings")
door_y = (-5.9, -2.9, 0.2, 3.25, 6.15)
window_y = (-7.25, -4.45, -1.35, 1.75, 4.75, 7.3)

for side, x, face in (("left", -5.105, 1), ("right", 5.105, -1)):
    for i, y in enumerate(door_y):
        door = Asset(f"{side}_door_{i}")
        door.include(
            "door_slab",
            box((0.09, 1.02, 2.55), center=(x, y, 1.55), color=WOOD_LIGHT)
        )
        # Raised-looking panels laid on the interior face.
        px = x + face * 0.055
        for p, z in enumerate((0.68, 1.42, 2.18)):
            door.include(
                f"panel_{p}",
                box((0.025, 0.72, 0.54), center=(px, y, z), color=WOOD_DARK)
            )
        door.include(
            "handle",
            ball(0.055, center=(x + face*0.10, y-0.31, 1.42), color=METAL)
        )
        side_openings.include(f"{side}_door_{i}", door)

    for i, y in enumerate(window_y):
        win = Asset(f"{side}_window_{i}")
        win.include(
            "dark_recess",
            box((0.05, 1.10, 1.62), center=(x, y, 2.50), color=(0.09, 0.08, 0.055))
        )
        win.include(
            "bright_glass",
            box((0.035, 0.88, 1.34), center=(x + face*0.04, y, 2.50),
                color=(0.78, 0.90, 0.93))
        )
        win.include(
            "center_mullion",
            box((0.05, 0.07, 1.42), center=(x + face*0.065, y, 2.50),
                color=WOOD_LIGHT)
        )
        win.include(
            "cross_mullion",
            box((0.05, 0.94, 0.07), center=(x + face*0.065, y, 2.55),
                color=WOOD_LIGHT)
        )
        side_openings.include(f"{side}_window_{i}", win)

scene.include("side_openings", side_openings)

# Stage and curtain at the far end.
stage = Asset("stage_asset")
stage.include(
    "raised_platform",
    box((5.65, 2.35, 0.34), center=(0, 7.02, 0.17), color=WOOD_DARK)
)
stage.include(
    "platform_front",
    box((5.90, 0.18, 0.46), center=(0, 5.88, 0.23), color=(0.12, 0.065, 0.035))
)
stage.include(
    "green_left_wing",
    box((0.68, 1.80, 3.15), center=(-2.78, 7.34, 2.14), color=GREEN)
)
stage.include(
    "green_right_wing",
    box((0.68, 1.80, 3.15), center=(2.78, 7.34, 2.14), color=GREEN)
)
stage.include(
    "dark_backdrop",
    box((4.95, 0.16, 2.75), center=(0, 8.18, 2.18), color=(0.025, 0.022, 0.018))
)
stage.include(
    "left_curtain",
    box((1.18, 0.24, 2.75), center=(-1.88, 7.96, 2.25), color=MAROON)
)
stage.include(
    "right_curtain",
    box((1.18, 0.24, 2.75), center=(1.88, 7.96, 2.25), color=MAROON)
)
stage.include(
    "upper_curtain",
    box((4.95, 0.25, 0.58), center=(0, 7.96, 3.53), color=MAROON)
)
# Vertical folds on the two curtain panels.
for side, base_x in (("left", -1.88), ("right", 1.88)):
    for j, dx in enumerate((-0.43, -0.14, 0.15, 0.44)):
        stage.include(
            f"{side}_curtain_fold_{j}",
            box((0.12, 0.10, 2.58), center=(base_x+dx, 7.79, 2.23),
                color=(0.32, 0.035, 0.045))
        )
# Cream valance tabs.
for j, x in enumerate((-2.25, -1.75, -1.25, -0.75, -0.25,
                       0.25, 0.75, 1.25, 1.75, 2.25)):
    stage.include(
        f"valance_{j}",
        ball(0.27, center=(x, 7.70, 3.78), color=(0.84, 0.79, 0.61))
    )
stage.include(
    "valance_header",
    box((5.1, 0.20, 0.26), center=(0, 7.76, 3.92), color=(0.84, 0.79, 0.61))
)
scene.include("stage_asset", stage)

# Chalkboard in front of the curtain.
board = Asset("chalkboard_asset")
board.include(
    "green_board",
    box((2.15, 0.10, 1.18), center=(0, 6.52, 1.42), color=BOARD)
)
board.include(
    "top_frame",
    box((2.28, 0.15, 0.08), center=(0, 6.46, 2.05), color=WOOD_LIGHT)
)
board.include(
    "bottom_frame",
    box((2.28, 0.15, 0.08), center=(0, 6.46, 0.79), color=WOOD_LIGHT)
)
board.include(
    "left_frame",
    box((0.08, 0.15, 1.34), center=(-1.10, 6.46, 1.42), color=WOOD_LIGHT)
)
board.include(
    "right_frame",
    box((0.08, 0.15, 1.34), center=(1.10, 6.46, 1.42), color=WOOD_LIGHT)
)
for x in (-0.86, 0.86):
    board.include(
        f"support_{x}",
        box((0.07, 0.07, 0.75), center=(x, 6.53, 0.42), color=WOOD_DARK)
    )
board.include(
    "chalk_tray",
    box((1.72, 0.22, 0.07), center=(0, 6.34, 0.80), color=WOOD_LIGHT)
)
scene.include("chalkboard_asset", board)

# Teacher table and small covered lectern on stage.
teacher = Asset("teacher_area")
teacher.include(
    "teacher_top",
    box((1.75, 0.68, 0.10), center=(-1.85, 5.65, 0.98), color=WOOD)
)
for i, (x, y) in enumerate(((-2.62,5.39),(-1.08,5.39),(-2.62,5.91),(-1.08,5.91))):
    teacher.include(
        f"teacher_leg_{i}",
        box((0.08, 0.08, 0.92), center=(x, y, 0.49), color=WOOD_DARK)
    )
teacher.include(
    "covered_lectern",
    box((0.72, 0.62, 1.12), center=(1.72, 6.57, 0.90), color=CYAN)
)
teacher.include(
    "lectern_white_top",
    box((0.82, 0.72, 0.10), center=(1.72, 6.57, 1.49), color=WHITE)
)
scene.include("teacher_area", teacher)

# Student desk/bench generator.
def make_desk_unit(name, x, y, scale=1.0, skew=0.0):
    unit = Asset(name)
    top_z = 0.82
    desk_w = 1.42 * scale
    desk_d = 0.53 * scale
    leg_h = 0.78
    unit.include(
        "writing_top",
        box((desk_w, desk_d, 0.09), center=(x, y, top_z), color=WOOD)
    )
    unit.include(
        "under_shelf",
        box((desk_w*0.82, desk_d*0.74, 0.07),
            center=(x, y+0.02, 0.53), color=WOOD_DARK)
    )
    for i, (dx, dy) in enumerate((
        (-desk_w*0.43, -desk_d*0.37),
        ( desk_w*0.43, -desk_d*0.37),
        (-desk_w*0.43,  desk_d*0.37),
        ( desk_w*0.43,  desk_d*0.37),
    )):
        unit.include(
            f"desk_leg_{i}",
            box((0.065, 0.065, leg_h), center=(x+dx, y+dy, leg_h/2),
                color=WOOD_DARK)
        )

    # Separate backless bench behind the writing desk toward the camera.
    bench_y = y - 0.68 * scale
    unit.include(
        "bench_seat",
        box((desk_w*0.90, 0.30*scale, 0.08),
            center=(x, bench_y, 0.47), color=WOOD)
    )
    for i, dx in enumerate((-desk_w*0.37, desk_w*0.37)):
        unit.include(
            f"bench_leg_{i}",
            box((0.07, 0.07, 0.43), center=(x+dx, bench_y, 0.235),
                color=WOOD_DARK)
        )
    if abs(skew) > 0.01:
        unit.turn("+z", skew, pivot=(x, y, 0))
    return unit

desk_field = Asset("desk_field")
# Four columns leave a distinct central aisle. Rows tighten with depth.
x_columns = (-3.65, -1.55, 1.45, 3.55)
row_y = (-5.7, -3.75, -1.8, 0.15, 2.10, 4.02)
omitted = {(0,5), (3,4)}  # irregular gaps visible in the photograph
for r, y in enumerate(row_y):
    for c, x in enumerate(x_columns):
        if (c, r) in omitted:
            continue
        # Slight disorder prevents a mechanically perfect grid.
        dx = (0.10 if (r+c) % 3 == 0 else -0.05 if (r+c) % 4 == 0 else 0.0)
        dy = (0.08 if c in (0,3) else 0.0)
        angle = (-2.0 if (r+c) % 4 == 0 else 1.4 if (r+c) % 5 == 0 else 0.0)
        scale = 1.05 if r == 0 else 1.0
        desk_field.include(
            f"desk_r{r}_c{c}",
            make_desk_unit(f"desk_r{r}_c{c}", x+dx, y+dy, scale, angle)
        )
scene.include("desk_field", desk_field)

# Books and notebooks on a selection of desks.
desk_items = Asset("visible_desk_items")
item_specs = [
    (-3.65,-5.70,(0.65,0.12,0.035),(0.72,0.08,0.10)),
    (-1.55,-5.70,(0.50,0.15,0.045),(0.92,0.84,0.65)),
    ( 1.45,-5.70,(0.58,0.15,0.045),(0.66,0.06,0.18)),
    (-3.65,-3.75,(0.55,0.13,0.04),(0.90,0.90,0.88)),
    ( 1.45,-1.80,(0.62,0.14,0.04),(0.80,0.72,0.45)),
    ( 3.55, 0.15,(0.48,0.15,0.04),(0.06,0.24,0.62)),
]
for i, (x,y,size,col) in enumerate(item_specs):
    desk_items.include(
        f"notebook_{i}",
        box(size, center=(x+0.12, y-0.04, 0.89), color=col)
    )
scene.include("visible_desk_items", desk_items)

# Backpacks: blocky silhouettes with pocket, top handle, and two shoulder straps.
def make_backpack(name, x, y, color, scale=1.0, lean=0.0):
    bag = Asset(name)
    bag.include(
        "main_body",
        box((0.48*scale, 0.25*scale, 0.67*scale),
            center=(x, y, 0.34*scale), color=color)
    )
    bag.include(
        "front_pocket",
        box((0.38*scale, 0.12*scale, 0.26*scale),
            center=(x, y-0.17*scale, 0.23*scale), color=tuple(v*0.72 for v in color))
    )
    bag.include(
        "left_strap",
        rod(0.025*scale,
            start=(x-0.16*scale, y+0.15*scale, 0.56*scale),
            end=(x-0.20*scale, y+0.16*scale, 0.08*scale),
            color=BLACK)
    )
    bag.include(
        "right_strap",
        rod(0.025*scale,
            start=(x+0.16*scale, y+0.15*scale, 0.56*scale),
            end=(x+0.20*scale, y+0.16*scale, 0.08*scale),
            color=BLACK)
    )
    bag.include(
        "top_handle",
        rod(0.025*scale,
            start=(x-0.10*scale, y, 0.70*scale),
            end=(x+0.10*scale, y, 0.70*scale),
            color=BLACK)
    )
    if abs(lean) > 0.01:
        bag.turn("+y", lean, pivot=(x,y,0))
    return bag

bags = Asset("backpacks")
bag_specs = [
    ("black_front_left", -3.90, -6.72, BLACK, 1.05, -5),
    ("black_front_center", -1.10, -5.10, BLACK, 0.96, 2),
    ("blue_front_center",  1.72, -6.02, BLUE, 1.12, -4),
    ("blue_right",         3.55, -4.42, CYAN, 0.92, 6),
    ("blue_mid_left",     -2.74, -2.90, BLUE, 0.72, -3),
    ("black_mid_right",    3.95, -1.15, BLACK, 0.70, 3),
    ("blue_rear",          1.66,  1.48, BLUE, 0.62, 0),
]
for spec in bag_specs:
    bags.include(spec[0], make_backpack(*spec))
scene.include("backpacks", bags)

# Ceiling fans.
fans = Asset("ceiling_fans")
fan_positions = [
    (-3.20, -5.65, 4.35, 18),
    ( 2.75, -5.00, 4.35, -8),
    (-1.75,  0.20, 4.35, 4),
    ( 2.15,  3.65, 4.35, 12),
]
for i, (x,y,z,ang) in enumerate(fan_positions):
    fan = Asset(f"fan_{i}")
    fan.include(
        "downrod",
        rod(0.035, start=(x,y,4.70), end=(x,y,z), color=METAL)
    )
    fan.include("hub", ball(0.13, center=(x,y,z), color=WOOD_DARK))
    for b, blade_angle in enumerate((ang, ang+120, ang+240)):
        a = math.radians(blade_angle)
        cx = x + math.cos(a)*0.52
        cy = y + math.sin(a)*0.52
        blade = box((0.90, 0.13, 0.045), center=(cx,cy,z), color=METAL)
        blade.turn("+z", blade_angle, pivot=(cx,cy,z))
        fan.include(f"blade_{b}", blade)
    fan.include(
        "motor_cap",
        rod(0.10, length=0.19, center=(x,y,z-0.04), axis="+z", color=WOOD_DARK)
    )
    fans.include(f"fan_{i}", fan)
scene.include("ceiling_fans", fans)

# Fluorescent ceiling fixtures.
fixtures = Asset("fluorescent_light_fixtures")
for i, (x,y) in enumerate(((0,-3.3),(0,1.25),(0,4.85),(-2.7,-0.8))):
    fixture = Asset(f"fixture_{i}")
    fixture.include(
        "housing",
        box((1.45,0.18,0.08), center=(x,y,4.61), color=(0.78,0.78,0.75))
    )
    fixture.include(
        "tube",
        box((1.27,0.07,0.045), center=(x,y,4.54), color=(1.0,0.98,0.88))
    )
    fixtures.include(f"fixture_{i}", fixture)
scene.include("fluorescent_light_fixtures", fixtures)

# Framed portraits and dark wall-mounted monitor/speaker boxes.
wall_details = Asset("wall_details")
for side, x, face in (("left",-5.00,1),("right",5.00,-1)):
    for i, y in enumerate((-4.2, -0.7, 2.8, 5.8)):
        frame = Asset(f"{side}_frame_{i}")
        frame.include(
            "outer_frame",
            box((0.065,0.50,0.70), center=(x+face*0.03,y,3.55), color=WOOD_DARK)
        )
        frame.include(
            "picture",
            box((0.035,0.38,0.57), center=(x+face*0.075,y,3.55),
                color=(0.70,0.73,0.66) if i%2==0 else (0.22,0.42,0.65))
        )
        wall_details.include(f"{side}_frame_{i}", frame)

# Angled-looking black wall boxes represented as shallow dark blocks.
for i, (x,y,z,side) in enumerate((
    (-4.86,1.9,3.35,1), (4.86,-2.2,3.28,-1),
    (-4.86,5.3,3.30,1), (4.86,4.5,3.35,-1)
)):
    monitor = box((0.22,0.72,0.62), center=(x,y,z), color=(0.025,0.055,0.055))
    monitor.turn("+x", 8 if i%2==0 else -7, pivot=(x,y,z))
    wall_details.include(f"wall_monitor_{i}", monitor)

scene.include("wall_details", wall_details)

# Realize all SceneAct geometry before configuring Blender.
realize(scene)

# Configure the world exactly after realize.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
if not background.outputs["Background"].is_linked:
    sc.world.node_tree.links.new(
        background.outputs["Background"], output.inputs["Surface"]
    )
background.inputs["Color"].default_value = (0.74, 0.76, 0.71, 1.0)
background.inputs["Strength"].default_value = 0.42

# Camera: eye-height viewpoint near the rear center, with broad perspective.
camera = set_view(
    position=(0.12, -8.18, 2.03),
    target=(0.02, 2.25, 1.78),
    lens=25.5,
    sensor=36,
    shift=(0.0, 0.025)
)
camera.data.dof.use_dof = False
camera.data.lens = 25.5

# Soft daylight from both window walls and fill from the ceiling.
area_emitter(
    position=(-4.55, -2.1, 3.35), power=760, size=5.2,
    target=(0, -1.0, 1.0), color=(0.84, 0.91, 1.0)
)
area_emitter(
    position=(4.55, 1.5, 3.25), power=680, size=4.8,
    target=(0, 1.0, 1.0), color=(1.0, 0.91, 0.72)
)
area_emitter(
    position=(0, 2.4, 4.35), power=640, size=5.0,
    target=(0, 2.3, 0.4), color=(1.0, 0.92, 0.75)
)
area_emitter(
    position=(0, -5.5, 4.25), power=520, size=4.0,
    target=(0, -3.0, 0.5), color=(0.86, 0.90, 1.0)
)

# Add a weak sun for long, soft directional structure.
sun_data = bpy.data.lights.new("WindowSun", "SUN")
sun_data.energy = 1.15
sun_data.color = (1.0, 0.86, 0.66)
sun = bpy.data.objects.new("WindowSun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(34), math.radians(-18), math.radians(-42))

# Rendering setup; the fixed runner performs the actual render.
sc.render.engine = "BLENDER_EEVEE_NEXT"
sc.render.resolution_x = 960
sc.render.resolution_y = 640
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.render.film_transparent = False

# Natural photographic color management.
sc.view_settings.look = "AgX - Medium High Contrast"
sc.view_settings.exposure = 0.25

# Contact shadows and restrained material response.
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Roughness"].default_value = 0.72
                    if "Specular IOR Level" in bsdf.inputs:
                        bsdf.inputs["Specular IOR Level"].default_value = 0.28

# Slight bevels catch light on the otherwise simple wooden and architectural boxes.
for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and len(obj.data.vertices) <= 8:
        bevel = obj.modifiers.new("SubtleEdgeBevel", "BEVEL")
        bevel.width = 0.012
        bevel.segments = 1
