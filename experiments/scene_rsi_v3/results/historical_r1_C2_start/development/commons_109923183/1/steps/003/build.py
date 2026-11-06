# Reference inventory, approximate normalized image bounds:
# Chaise x .04-.83, y .23-.94: long pale upholstered seat, raised curved
# back at left, pillow, sloping side panels, carved grey-green frame and legs.
# The far legs and part of the back are occluded.
# Small dark green label x .68-.71, y .53-.58 on the seat.
# Cream paneled cabinet wall x .02-1, y 0-.57, with moldings and two handles.
# Dark reddish wooden floor x 0-1, y .49-1.
# Bright window and curtain at the far left; a cropped cane chair at bottom left.
# The unseen portions of the window and foreground chair remain uncertain.
#
# Review of the second render: the chaise is displaced right, its seat appears
# too narrow in depth, and the front upholstered side is too rectangular.
# The foreground chair is almost entirely missing, the wall is too bright,
# and the floorboards are too light and too conspicuously outlined.
# This revision changes the camera angle and framing, enlarges the seat depth,
# makes the arm panel follow its curved outline, and restores the foreground
# chair fragment. The wall and floor retain editable architectural parts.
#
# Estimated expanded primitive count: approximately 350: architecture 32,
# window 7, chaise cushion and stripes 85, frame and legs 95, back and arms
# 85, pillow and label 31, foreground chair 35. Fillet boxes expand to 26
# primitives and tube paths to 2*n-1. No Boolean operations.

from sceneact import *
import bpy

scene = Scene('Paneled room with antique chaise')

wall = (.62, .59, .53)
trim = (.70, .67, .60)
groove = (.43, .40, .35)
floor_col = (.075, .024, .014)
floor_seam = (.057, .019, .012)
frame_col = (.24, .25, .20)
frame_high = (.42, .40, .31)
fabric = (.70, .61, .57)
fabric_side = (.62, .52, .47)
stripe = (.53, .40, .38)
pillow_col = (.76, .65, .51)

architecture = Asset('Architecture')
architecture.include('floor', box((12,12,.12), center=(0,0,-.08), color=floor_col))
architecture.include('cabinet_wall', box((12,.12,4), center=(0,1.55,1.95), color=wall))
architecture.include('right_return', box((.12,3.5,4), center=(3.25,.3,1.95), color=(.66,.64,.59)))
architecture.include('baseboard', box((12,.09,.18), center=(0,1.46,.13), color=trim))
architecture.include('upper_trim', box((12,.07,.045), center=(0,1.46,2.43), color=trim))
architecture.include('horizontal_seam', box((12,.018,.012), center=(0,1.476,2.18), color=groove))
architecture.include('vertical_door_seam', box((.012,.018,2.4), center=(.18,1.474,2.4), color=groove))

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
    architecture.include(name, box(size, center=center, color=trim))
for i,x in enumerate((-.96,-.82)):
    architecture.include('handle_%d'%i,
        rod(.022,start=(x,1.405,2.15),end=(x+.025,1.405,2.06),color=(.11,.095,.075)))
for i,x in enumerate((-4,-3.2,-2.4,-1.6,-.8,0,.8,1.6,2.4,3.2,4)):
    architecture.include('floorboard_joint_%d'%i,
        box((.003,9,.003),center=(x,-1,-.017),color=floor_seam))
scene.include('architecture',architecture)

window = Asset('Window and curtain')
window.include('bright_window',box((.52,.035,3.5),center=(-3.25,1.36,1.75),color=(.90,.89,.84)))
window.include('curtain',box((.24,.10,3.4),center=(-2.94,1.30,1.7),color=(.56,.48,.39)))
for i in range(4):
    window.include('fold_%d'%i,rod(.016,start=(-3.03+i*.055,1.235,.08),
        end=(-3.03+i*.055,1.235,3.3),color=(.44,.37,.30)))
scene.include('window_and_curtain',window)

chaise = Asset('Antique upholstered chaise')
seat = Asset('Long striped cushion')
seat.include('main_cushion',fillet_box((2.86,1.30,.30),radius=.14,
    center=(.18,-.03,.66),color=fabric))
seat.include('rounded_foot',resized(ball(.64,center=(1.53,-.03,.66),color=fabric),(.42,1,.235)))
for i in range(18):
    y=-.64+i*.071
    seat.include('stripe_%02d'%i,rod(.0025,start=(-1.13,y,.817),
        end=(1.62,y,.817),color=stripe))
for j in range(8):
    for i in range(7):
        x=-.86+j*.34
        y=-.55+i*.17
        seat.include('woven_dash_%d_%d'%(j,i),rod(.004,start=(x,y,.820),
            end=(x+.028,y,.820),color=(.60,.44,.42)))
chaise.include('seat',seat)

frame = Asset('Carved frame and legs')
frame.include('front_apron',sweep_tube(points=[
    (-1.27,-.69,.58),(-.75,-.70,.49),(.2,-.70,.48),
    (1.15,-.70,.47),(1.56,-.64,.50),(1.68,-.49,.56)],
    radius=.043,color=frame_col))
frame.include('front_apron_highlight',sweep_tube(points=[
    (-1.26,-.715,.60),(-.72,-.725,.53),(.2,-.725,.52),
    (1.18,-.725,.51),(1.55,-.665,.54)],radius=.012,color=frame_high))
frame.include('rear_apron',sweep_tube(points=[
    (-1.28,.61,.57),(-.5,.62,.50),(.7,.62,.50),(1.53,.56,.54)],
    radius=.028,color=frame_col))
for i,(x,y) in enumerate(((-1.13,-.58),(1.47,-.52),(-1.10,.52),(1.45,.47))):
    frame.include('cabriole_leg_%d'%i,sweep_tube(points=[
        (x,y,.54),(x+.035,y,.40),(x-.025,y,.20),
        (x-.04,y,.075),(x+.025,y-.015,.045)],radius=.037,color=frame_col))
    frame.include('leg_joint_%d'%i,ball(.065,center=(x,y,.52),color=frame_high))
frame.include('apron_medallion',resized(ball(.10,center=(.2,-.74,.49),
    color=frame_high),(1.4,.3,.55)))
for i in range(3):
    frame.include('medallion_mark_%d'%i,rod(.009,
        start=(.10+i*.09,-.77,.48),end=(.15+i*.09,-.77,.52),color=frame_col))
chaise.include('frame',frame)

back = Asset('Raised upholstered back')
back.include('back_cushion',fillet_box((.31,1.30,1.04),radius=.14,
    center=(-1.27,-.03,1.10),color=fabric_side))
back.include('rounded_back_top',resized(ball(.61,center=(-1.30,-.03,1.59),
    color=fabric_side),(.27,1,.28)))
back.include('crest',sweep_tube(points=[
    (-1.29,-.68,.68),(-1.38,-.68,1.13),(-1.39,-.62,1.54),
    (-1.38,-.40,1.72),(-1.38,0,1.77),(-1.38,.42,1.70),
    (-1.36,.62,1.52),(-1.30,.62,1.05)],radius=.038,color=frame_col))
back.include('crest_highlight',sweep_tube(points=[
    (-1.41,-.55,1.58),(-1.41,-.35,1.75),(-1.41,0,1.80),
    (-1.41,.38,1.73),(-1.40,.58,1.56)],radius=.012,color=frame_high))
for i in range(9):
    y=-.53+i*.13
    back.include('stripe_%d'%i,rod(.003,start=(-1.105,y,.84),
        end=(-1.105,y,1.53),color=stripe))
chaise.include('back',back)

arms = Asset('Curved upholstered side arms')
for side in (-1,1):
    y=side*.65
    # Overlapping rounded forms fill the sloping side beneath the curved rail.
    arms.include('lower_panel_%s'%side,fillet_box((.88,.10,.38),radius=.045,
        center=(-.94,y,.91),color=fabric_side))
    arms.include('rear_panel_%s'%side,fillet_box((.47,.10,.31),radius=.045,
        center=(-1.13,y,1.20),color=fabric_side))
    arms.include('rail_%s'%side,sweep_tube(points=[
        (-1.36,y,1.48),(-1.20,y,1.36),(-1.00,y,1.20),
        (-.76,y,1.13),(-.49,y,1.12),(-.43,y,1.06),(-.50,y,1.00)],
        radius=.037,color=frame_col))
    arms.include('rail_highlight_%s'%side,sweep_tube(points=[
        (-1.32,y-.012,1.48),(-1.13,y-.012,1.31),(-.91,y-.012,1.18),
        (-.58,y-.012,1.15),(-.46,y-.012,1.10)],radius=.011,color=frame_high))
    arms.include('front_support_%s'%side,sweep_tube(points=[
        (-.50,y,1.07),(-.48,y,.93),(-.53,y,.73),(-.45,y,.59)],
        radius=.035,color=frame_col))
    for i in range(6):
        x=-1.26+i*.12
        arms.include('panel_stripe_%s_%d'%(side,i),rod(.0025,
            start=(x,y-.057,.74),end=(x,y-.057,1.08),color=stripe))
chaise.include('arms',arms)

pillow = Asset('Loose cream pillow')
pillow_body=fillet_box((.24,.82,.76),radius=.10,
    center=(-1.00,-.09,1.30),color=pillow_col)
pillow_body.turn(axis='y',degrees=-16)
pillow.include('soft_pillow',pillow_body)
chaise.include('pillow',pillow)

label = Asset('Green label')
label.include('card',box((.18,.10,.008),center=(.97,-.16,.826),color=(.025,.14,.12)))
for i in range(3):
    label.include('mark_%d'%i,box((.012,.012,.003),
        center=(.92+i*.045,-.16,.832),color=(.72,.75,.66)))
chaise.include('label',label)
scene.include('chaise',chaise)

fragment = Asset('Foreground cane chair fragment')
fragment.include('cane_seat',fillet_box((1.05,.82,.07),radius=.035,
    center=(-2.10,-2.22,.50),color=(.43,.28,.19)))
fragment.include('near_rim',rod(.047,start=(-2.63,-2.63,.54),
    end=(-1.57,-2.63,.54),color=frame_high))
fragment.include('side_rim',rod(.047,start=(-1.57,-2.63,.54),
    end=(-1.57,-1.81,.54),color=frame_high))
fragment.include('back_rim',rod(.04,start=(-2.63,-1.81,.54),
    end=(-1.57,-1.81,.54),color=frame_high))
for i in range(11):
    x=-2.56+i*.09
    fragment.include('cane_warp_%d'%i,rod(.006,start=(x,-2.55,.545),
        end=(x,-1.87,.545),color=(.66,.51,.34)))
for i in range(8):
    y=-2.53+i*.09
    fragment.include('cane_weft_%d'%i,rod(.006,start=(-2.56,y,.548),
        end=(-1.65,y,.548),color=(.66,.51,.34)))
fragment.include('visible_leg',rod(.038,start=(-1.60,-2.55,.48),
    end=(-1.64,-2.55,.03),color=frame_col))
scene.include('foreground_chair',fragment)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.70,.68,.64,1)
background.inputs['Strength'].default_value=.40

set_view((-1.5,-6.7,4.5),(.12,0,.95),lens=55)
area_emitter((-3.8,-2.5,4.8),power=500,size=4.0,target=(0,0,.8))
area_emitter((2,-.5,4.5),power=130,size=3.0,target=(0,0,.5))
