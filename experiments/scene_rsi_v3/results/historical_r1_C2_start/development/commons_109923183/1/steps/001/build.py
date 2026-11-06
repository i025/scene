# Reference inventory, normalized image bounds (approximate):
# - Chaise longue: x .04-.83, y .23-.94. Long pale striped upholstered seat,
#   raised rounded back at left, two curved wooden arms, carved edge and legs.
#   The rear legs and portions of the back are partly occluded.
# - Cream paneled wall and cabinet: x .02-1, y 0-.57. Broad rectangular molding,
#   horizontal top seams, two small dark handles, right corner and baseboard.
# - Dark reddish wood floor: x 0-1, y .49-1, with subtle plank seams.
# - Pale pillow: x .08-.31, y .26-.55, leaning against chaise back.
# - Small dark green rectangular label on seat: x .68-.71, y .53-.58.
# - Curtain and window edge at far left: x 0-.08, y 0-.67.
# - Partial cane chair at bottom left: x 0-.19, y .80-1; mostly occluded.
# Estimated expanded primitive count: about 250, including tube segments and
# upholstery stripes. Fine carved details and woven pattern remain approximate.

from sceneact import *
import bpy
import math

scene = Scene('Cream paneled room with chaise')
cream = (0.72, 0.69, 0.63)
molding = (0.79, 0.76, 0.69)
floor = (0.22, 0.085, 0.055)
wood = (0.31, 0.28, 0.21)
wood_light = (0.50, 0.46, 0.35)
fabric = (0.78, 0.69, 0.64)
stripe = (0.58, 0.43, 0.40)
pillow_col = (0.81, 0.72, 0.61)

architecture = Asset('Architecture')
architecture.include('floor', box((10, 10, .12), center=(0, 0, -.08), color=floor))
architecture.include('back_wall', box((8, .12, 3.5), center=(0, 1.55, 1.7), color=cream))
architecture.include('right_wall', box((.12, 3, 3.5), center=(3.1, .1, 1.7), color=(.75,.73,.68)))
architecture.include('baseboard', box((8, .09, .18), center=(0, 1.46, .13), color=molding))
architecture.include('upper_horizontal_trim', box((8, .07, .045), center=(0, 1.46, 2.43), color=molding))
architecture.include('cabinet_seam_horizontal', box((8, .018, .012), center=(0, 1.476, 2.18), color=(.48,.46,.42)))
architecture.include('cabinet_seam_vertical', box((.012, .018, 2.1), center=(.18, 1.474, 2.4), color=(.47,.44,.40)))
# Broad raised rectangular wall panel and inset linework.
for name, size, center in [
    ('panel_top',(5.65,.06,.045),(-.2,1.453,1.95)),
    ('panel_bottom',(5.65,.06,.045),(-.2,1.453,.38)),
    ('panel_left',(.045,.06,1.57),(-3.025,1.453,1.165)),
    ('panel_right',(.045,.06,1.57),(2.625,1.453,1.165)),
    ('inner_top',(5.42,.025,.018),(-.2,1.418,1.85)),
    ('inner_bottom',(5.42,.025,.018),(-.2,1.418,.47)),
    ('inner_left',(.018,.025,1.38),(-2.91,1.418,1.16)),
    ('inner_right',(.018,.025,1.38),(2.51,1.418,1.16)),
]:
    architecture.include(name, box(size, center=center, color=molding))
for i,x in enumerate((-.96,-.82)):
    architecture.include('cabinet_handle_%d'%i, rod(.025, start=(x,1.405,2.15), end=(x+.025,1.405,2.06), color=(.14,.12,.10)))
for i,x in enumerate((-3,-2.15,-1.3,-.45,.4,1.25,2.1,2.95)):
    architecture.include('floor_plank_seam_%d'%i, box((.009,7,.004), center=(x,-1.0,-.016), color=(.14,.055,.035)))
scene.include('architecture', architecture)

curtain = Asset('Window and drapery')
curtain.include('bright_window', box((.45,.035,3.1), center=(-3.13,1.37,1.58), color=(.92,.91,.86)))
curtain.include('side_curtain', box((.24,.10,3.1), center=(-2.89,1.30,1.56), color=(.64,.57,.49)))
for i in range(4):
    curtain.include('curtain_fold_%d'%i, rod(.017, start=(-2.99+i*.055,1.235,.08), end=(-2.99+i*.055,1.235,3.05), color=(.50,.43,.36)))
scene.include('window_and_drapery', curtain)

chaise = Asset('Antique upholstered chaise')
# Main seat is elongated along X, with a gently rounded foot.
seat = Asset('Striped upholstered seat')
seat.include('seat_body', fillet_box((2.86,1.12,.27), radius=.12, center=(.18,-.03,.65), color=fabric))
seat.include('rounded_foot', resized(ball(.55, center=(1.53,-.03,.65), color=fabric), (0.48,1.0,.25)))
# Parallel woven stripes and restrained short rose-colored marks on top.
for i in range(16):
    y = -.54 + i*.067
    seat.include('woven_stripe_%02d'%i, rod(.004, start=(-1.13,y,.792), end=(1.65,y,.792), color=stripe))
for j in range(7):
    x = -.85+j*.37
    for i in range(8):
        y = -.48+i*.135
        seat.include('small_woven_dash_%d_%d'%(j,i), rod(.006, start=(x,y,.796), end=(x+.035,y,.796), color=(.66,.49,.46)))
chaise.include('seat', seat)

frame = Asset('Carved wooden frame')
frame.include('front_apron', sweep_tube(points=[(-1.27,-.60,.57),(-.75,-.61,.48),(.2,-.61,.47),(1.15,-.61,.46),(1.56,-.55,.49),(1.68,-.40,.55)], radius=.037, color=wood))
frame.include('front_apron_highlight', sweep_tube(points=[(-1.26,-.62,.60),(-.72,-.63,.52),(.2,-.63,.51),(1.18,-.63,.50),(1.55,-.57,.53)], radius=.012, color=wood_light))
frame.include('rear_apron', sweep_tube(points=[(-1.28,.52,.57),(-.5,.53,.50),(.7,.53,.50),(1.53,.47,.54)], radius=.027, color=wood))
# Four curved cabriole legs, some hidden by the seat.
for i,(x,y) in enumerate(((-1.13,-.49),(1.47,-.43),(-1.10,.43),(1.45,.38))):
    frame.include('curved_leg_%d'%i, sweep_tube(points=[(x,y,.54),(x+.035,y,.40),(x-.025,y,.20),(x-.04,y,.075),(x+.025,y-.015,.045)], radius=.035, color=wood))
    frame.include('leg_joint_%d'%i, ball(.065, center=(x,y,.52), color=wood_light))
# A small central carved ornament.
frame.include('apron_medallion', resized(ball(.10, center=(.2,-.646,.49), color=wood_light), (1.4,.3,.55)))
for i in range(3):
    frame.include('medallion_line_%d'%i, rod(.009, start=(.10+i*.09,-.68,.48), end=(.15+i*.09,-.68,.52), color=wood))
chaise.include('frame', frame)

back = Asset('Raised upholstered back')
# The back slopes slightly away from the seat and has a rounded upholstered silhouette.
back.include('back_cushion', fillet_box((.29,1.10,1.04), radius=.13, center=(-1.26,-.03,1.10), color=fabric))
back.include('rounded_back_top', resized(ball(.52, center=(-1.30,-.03,1.59), color=fabric), (.30,1.0,.33)))
back.include('outer_back_crest', sweep_tube(points=[(-1.29,-.59,.68),(-1.38,-.59,1.13),(-1.39,-.53,1.54),(-1.38,-.34,1.72),(-1.38,0,1.77),(-1.38,.36,1.70),(-1.36,.53,1.52),(-1.30,.53,1.05)], radius=.036, color=wood))
back.include('crest_highlight', sweep_tube(points=[(-1.41,-.47,1.58),(-1.41,-.30,1.75),(-1.41,0,1.80),(-1.41,.33,1.73),(-1.40,.50,1.56)], radius=.012, color=wood_light))
for i in range(9):
    y=-.45+i*.112
    back.include('back_stripe_%d'%i, rod(.004, start=(-1.104,y,.84), end=(-1.104,y,1.53), color=stripe))
chaise.include('back', back)

arms = Asset('Scrolled side arms')
# Swept arms descend from the crest to the front support.
for side in (-1,1):
    y=side*.56
    arms.include('arm_upholstery_%s'%side, fillet_box((.91,.08,.44), radius=.035, center=(-.92,y,1.02), color=fabric))
    arms.include('arm_rail_%s'%side, sweep_tube(points=[(-1.36,y,1.48),(-1.20,y,1.36),(-1.00,y,1.20),(-.76,y,1.13),(-.49,y,1.12),(-.43,y,1.06),(-.50,y,1.00)], radius=.035, color=wood))
    arms.include('arm_rail_highlight_%s'%side, sweep_tube(points=[(-1.32,y-.012,1.48),(-1.13,y-.012,1.31),(-.91,y-.012,1.18),(-.58,y-.012,1.15),(-.46,y-.012,1.10)], radius=.011, color=wood_light))
    arms.include('arm_front_support_%s'%side, sweep_tube(points=[(-.50,y,1.07),(-.48,y,.93),(-.53,y,.73),(-.45,y,.59)], radius=.032, color=wood))
chaise.include('arms', arms)

pillow = Asset('Loose cream pillow')
pillow_body = fillet_box((.22,.70,.69), radius=.085, center=(-1.02,-.06,1.29), color=pillow_col)
pillow_body.turn(axis='y', degrees=-16)
pillow.include('soft_square_cushion', pillow_body)
chaise.include('pillow', pillow)

label = Asset('Small green label')
label.include('tag', box((.18,.10,.008), center=(.97,-.16,.801), color=(.035,.18,.16)))
for i in range(3):
    label.include('tag_mark_%d'%i, box((.012,.012,.003), center=(.92+i*.045,-.16,.807), color=(.78,.80,.71)))
chaise.include('label', label)
scene.include('chaise', chaise)

# Foreground fragment of another cane-seated chair.
fragment = Asset('Partial foreground cane chair')
fragment.include('seat', fillet_box((.85,.68,.07), radius=.035, center=(-2.14,-1.54,.48), color=(.52,.36,.25)))
fragment.include('front_rim', rod(.04, start=(-2.57,-1.88,.51), end=(-1.72,-1.88,.51), color=wood_light))
fragment.include('side_rim', rod(.04, start=(-1.72,-1.88,.51), end=(-1.72,-1.20,.51), color=wood_light))
for i in range(9):
    x=-2.48+i*.085
    fragment.include('cane_warp_%d'%i, rod(.006, start=(x,-1.82,.52), end=(x,-1.25,.52), color=(.72,.57,.40)))
for i in range(7):
    y=-1.80+i*.085
    fragment.include('cane_weft_%d'%i, rod(.006, start=(-2.50,y,.523), end=(-1.79,y,.523), color=(.72,.57,.40)))
fragment.include('front_leg', rod(.035, start=(-1.75,-1.82,.47), end=(-1.78,-1.82,.03), color=wood))
scene.include('foreground_chair_fragment', fragment)

realize(scene)
sc = bpy.context.scene
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
background.inputs['Color'].default_value = (0.75,0.75,0.75,1)
background.inputs['Strength'].default_value = .7

set_view((3.4,-6.7,4.0), (-.15,.0,.90), lens=43)
area_emitter((-3.8,-2.5,4.8), power=850, size=4.0, target=(0,0,.8))
area_emitter((2,-.5,4.5), power=300, size=3.0, target=(0,0,.5))
