# Reference inventory, approximate normalized bounds:
# Chaise x .04-.83, y .23-.94: pale striped long cushion, high curved
# upholstered left end, curved side arms, carved grey-green frame and legs.
# Pillow x .08-.31, y .26-.55, overlaps the raised back.
# Dark green label x .68-.71, y .53-.58, rests on the seat.
# Cream paneled wall x .02-1, y 0-.57, with molding, seams and two handles.
# Dark reddish wood floor x 0-1, y .49-1. Window and curtain at far left.
# A partly cropped cane chair enters at bottom left; its hidden shape is uncertain.
#
# Review of the first render: the chaise occupied too little of the frame, the
# floor was too light, the wall ended visibly at left, and the foreground chair
# appeared as a separate small stool. The chaise arms were too boxlike.
# This revision brings the camera closer, extends the wall, darkens the floor,
# crops the foreground chair, and gives the chaise a fuller upholstered side.
# Estimated expanded primitive count: roughly 390, including fillet boxes,
# tube segments, upholstery stripes, and foreground cane. No booleans.

from sceneact import *
import bpy

scene = Scene('Paneled room and antique chaise')

wall = (0.67, 0.64, 0.58)
trim = (0.72, 0.69, 0.62)
groove = (0.49, 0.46, 0.40)
floor_col = (0.105, 0.037, 0.023)
floor_seam = (0.075, 0.025, 0.016)
frame_col = (0.27, 0.28, 0.22)
frame_high = (0.43, 0.42, 0.32)
fabric = (0.71, 0.63, 0.59)
fabric_side = (0.65, 0.56, 0.51)
stripe = (0.53, 0.40, 0.38)
pillow_col = (0.79, 0.69, 0.56)

architecture = Asset('Architecture')
architecture.include('floor', box((12, 12, .12), center=(0, 0, -.08), color=floor_col))
architecture.include('paneled_wall', box((12, .12, 4), center=(0, 1.55, 1.95), color=wall))
architecture.include('right_return', box((.12, 3.5, 4), center=(3.25, .3, 1.95), color=(.70,.68,.62)))
architecture.include('baseboard', box((12, .09, .18), center=(0, 1.46, .13), color=trim))
architecture.include('upper_trim', box((12, .07, .045), center=(0, 1.46, 2.43), color=trim))
architecture.include('horizontal_seam', box((12, .018, .012), center=(0, 1.476, 2.18), color=groove))
architecture.include('vertical_cabinet_seam', box((.012, .018, 2.4), center=(.18, 1.474, 2.4), color=groove))

for name, size, center in [
    ('panel_top', (5.65,.06,.045), (-.2,1.453,1.95)),
    ('panel_bottom', (5.65,.06,.045), (-.2,1.453,.38)),
    ('panel_left', (.045,.06,1.57), (-3.025,1.453,1.165)),
    ('panel_right', (.045,.06,1.57), (2.625,1.453,1.165)),
    ('inner_top', (5.42,.025,.018), (-.2,1.418,1.85)),
    ('inner_bottom', (5.42,.025,.018), (-.2,1.418,.47)),
    ('inner_left', (.018,.025,1.38), (-2.91,1.418,1.16)),
    ('inner_right', (.018,.025,1.38), (2.51,1.418,1.16)),
]:
    architecture.include(name, box(size, center=center, color=trim))

for i, x in enumerate((-.96, -.82)):
    architecture.include('handle_%d' % i,
        rod(.022, start=(x,1.405,2.15), end=(x+.025,1.405,2.06),
            color=(.11,.095,.075)))

for i, x in enumerate((-4,-3.2,-2.4,-1.6,-.8,0,.8,1.6,2.4,3.2,4)):
    architecture.include('floorboard_joint_%d' % i,
        box((.007,9,.004), center=(x,-1,-.016), color=floor_seam))
scene.include('architecture', architecture)

window = Asset('Window and curtain')
window.include('bright_window', box((.5,.035,3.5), center=(-3.25,1.36,1.75), color=(.91,.90,.84)))
window.include('curtain', box((.24,.10,3.4), center=(-2.94,1.30,1.7), color=(.56,.48,.39)))
for i in range(4):
    window.include('curtain_fold_%d' % i,
        rod(.016, start=(-3.03+i*.055,1.235,.08),
            end=(-3.03+i*.055,1.235,3.3), color=(.44,.37,.30)))
scene.include('window_and_curtain', window)

chaise = Asset('Antique upholstered chaise')
seat = Asset('Long striped cushion')
seat.include('main_cushion',
    fillet_box((2.86,1.12,.30), radius=.14, center=(.18,-.03,.66), color=fabric))
seat.include('rounded_foot',
    resized(ball(.55, center=(1.53,-.03,.66), color=fabric), (.48,1,.27)))
for i in range(16):
    y = -.54 + i*.067
    seat.include('stripe_%02d' % i,
        rod(.0035, start=(-1.13,y,.817), end=(1.65,y,.817), color=stripe))
for j in range(8):
    for i in range(8):
        x = -.9+j*.34
        y = -.47+i*.135
        seat.include('woven_dash_%d_%d' % (j,i),
            rod(.005, start=(x,y,.820), end=(x+.027,y,.820),
                color=(.61,.46,.43)))
chaise.include('seat', seat)

frame = Asset('Carved frame and legs')
frame.include('front_apron',
    sweep_tube(points=[(-1.27,-.60,.58),(-.75,-.61,.49),(.2,-.61,.48),
                       (1.15,-.61,.47),(1.56,-.55,.50),(1.68,-.40,.56)],
               radius=.043, color=frame_col))
frame.include('front_apron_highlight',
    sweep_tube(points=[(-1.26,-.625,.60),(-.72,-.635,.53),(.2,-.635,.52),
                       (1.18,-.635,.51),(1.55,-.575,.54)],
               radius=.012, color=frame_high))
frame.include('rear_apron',
    sweep_tube(points=[(-1.28,.52,.57),(-.5,.53,.50),(.7,.53,.50),(1.53,.47,.54)],
               radius=.028, color=frame_col))
for i, (x,y) in enumerate(((-1.13,-.49),(1.47,-.43),(-1.10,.43),(1.45,.38))):
    frame.include('cabriole_leg_%d' % i,
        sweep_tube(points=[(x,y,.54),(x+.035,y,.40),(x-.025,y,.20),
                           (x-.04,y,.075),(x+.025,y-.015,.045)],
                   radius=.037, color=frame_col))
    frame.include('leg_joint_%d' % i, ball(.065, center=(x,y,.52), color=frame_high))
frame.include('apron_medallion',
    resized(ball(.10, center=(.2,-.65,.49), color=frame_high), (1.4,.3,.55)))
for i in range(3):
    frame.include('medallion_mark_%d' % i,
        rod(.009, start=(.10+i*.09,-.68,.48),
            end=(.15+i*.09,-.68,.52), color=frame_col))
chaise.include('frame', frame)

back = Asset('Raised upholstered back')
back.include('back_cushion',
    fillet_box((.31,1.12,1.04), radius=.14, center=(-1.27,-.03,1.10), color=fabric_side))
back.include('rounded_back_top',
    resized(ball(.52, center=(-1.30,-.03,1.59), color=fabric_side), (.31,1,.33)))
back.include('crest',
    sweep_tube(points=[(-1.29,-.59,.68),(-1.38,-.59,1.13),(-1.39,-.53,1.54),
                       (-1.38,-.34,1.72),(-1.38,0,1.77),(-1.38,.36,1.70),
                       (-1.36,.53,1.52),(-1.30,.53,1.05)],
               radius=.038, color=frame_col))
back.include('crest_highlight',
    sweep_tube(points=[(-1.41,-.47,1.58),(-1.41,-.30,1.75),(-1.41,0,1.80),
                       (-1.41,.33,1.73),(-1.40,.50,1.56)],
               radius=.012, color=frame_high))
for i in range(9):
    y = -.45+i*.112
    back.include('back_stripe_%d' % i,
        rod(.004, start=(-1.105,y,.84), end=(-1.105,y,1.53), color=stripe))
chaise.include('back', back)

arms = Asset('Curved upholstered arms')
for side in (-1, 1):
    y = side*.56
    # Low rounded panel fills the visible area below the sloping arm rail.
    panel = fillet_box((.88,.105,.49), radius=.05,
                       center=(-.94,y,.94), color=fabric_side)
    arms.include('upholstered_panel_%s' % side, panel)
    arms.include('arm_rail_%s' % side,
        sweep_tube(points=[(-1.36,y,1.48),(-1.20,y,1.36),(-1.00,y,1.20),
                           (-.76,y,1.13),(-.49,y,1.12),(-.43,y,1.06),(-.50,y,1.00)],
                   radius=.037, color=frame_col))
    arms.include('rail_highlight_%s' % side,
        sweep_tube(points=[(-1.32,y-.012,1.48),(-1.13,y-.012,1.31),
                           (-.91,y-.012,1.18),(-.58,y-.012,1.15),(-.46,y-.012,1.10)],
                   radius=.011, color=frame_high))
    arms.include('front_support_%s' % side,
        sweep_tube(points=[(-.50,y,1.07),(-.48,y,.93),(-.53,y,.73),(-.45,y,.59)],
                   radius=.035, color=frame_col))
    for i in range(6):
        x = -1.26+i*.12
        arms.include('panel_stripe_%s_%d' % (side,i),
            rod(.003, start=(x,y-.057,.72), end=(x,y-.057,1.10), color=stripe))
chaise.include('arms', arms)

pillow = Asset('Loose cream pillow')
pillow_body = fillet_box((.24,.74,.72), radius=.10,
                         center=(-1.00,-.09,1.30), color=pillow_col)
pillow_body.turn(axis='y', degrees=-16)
pillow.include('pillow_body', pillow_body)
chaise.include('pillow', pillow)

label = Asset('Green label')
label.include('card', box((.18,.10,.008), center=(.97,-.16,.826), color=(.025,.14,.12)))
for i in range(3):
    label.include('mark_%d' % i,
        box((.012,.012,.003), center=(.92+i*.045,-.16,.832), color=(.72,.75,.66)))
chaise.include('label', label)
scene.include('chaise', chaise)

# A close foreground fragment; the rest of this chair is outside the view.
fragment = Asset('Foreground cane chair fragment')
fragment.include('cane_seat',
    fillet_box((1.05,.82,.07), radius=.035,
               center=(-2.10,-2.22,.50), color=(.43,.28,.19)))
fragment.include('near_rim',
    rod(.047, start=(-2.63,-2.63,.54), end=(-1.57,-2.63,.54), color=frame_high))
fragment.include('side_rim',
    rod(.047, start=(-1.57,-2.63,.54), end=(-1.57,-1.81,.54), color=frame_high))
fragment.include('back_rim',
    rod(.04, start=(-2.63,-1.81,.54), end=(-1.57,-1.81,.54), color=frame_high))
for i in range(11):
    x = -2.56+i*.09
    fragment.include('cane_warp_%d' % i,
        rod(.006, start=(x,-2.55,.545), end=(x,-1.87,.545), color=(.66,.51,.34)))
for i in range(8):
    y = -2.53+i*.09
    fragment.include('cane_weft_%d' % i,
        rod(.006, start=(-2.56,y,.548), end=(-1.65,y,.548), color=(.66,.51,.34)))
fragment.include('visible_leg',
    rod(.038, start=(-1.60,-2.55,.48), end=(-1.64,-2.55,.03), color=frame_col))
scene.include('foreground_chair', fragment)

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
background.inputs['Color'].default_value = (.70,.68,.64,1)
background.inputs['Strength'].default_value = .48

set_view((1.9,-6.7,3.9), (-.15,0,.94), lens=61)
area_emitter((-3.8,-2.5,4.8), power=650, size=4.0, target=(0,0,.8))
area_emitter((2,-.5,4.5), power=180, size=3.0, target=(0,0,.5))
