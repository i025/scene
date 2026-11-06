# Reference inventory, estimated image bounds in normalized image coordinates:
# - Cream museum partition fills roughly x=.13-.82, y=.00-1.00; red door at
#   left x=0-.16. Its upper edge and lower edge are partly outside the image.
# - Dark framed machinery display x=.25-.78, y=.06-.63: pale backing, large
#   spoked wheel at upper left, four small wheels across top, horizontal bars,
#   and several dark hand-operated fittings. Their exact mechanisms are uncertain.
# - Black horizontal rail and small yellow label x=.25-.77, y=.62-.72.
# - Two dark circular machine plates x=.29-.78, y=.73-.91, with spokes and hubs;
#   a short vertical stand and foot are visible under the right plate.
# - Right background x=.79-1.00: tall bright divided window, dark framing,
#   wall, bench and pale floor. A dark teal pipe runs along the top.
# Approximate expanded primitive count: 150 meshes, including wheel spokes and
# fittings. Most small mechanical shapes are separate editable child parts.

import math
import bpy
from sceneact import *

scene = Scene('Museum machine display')

cream = (0.62, 0.59, 0.48)
cream_light = (0.72, 0.70, 0.60)
backing = (0.62, 0.64, 0.59)
dark = (0.075, 0.075, 0.065)
black = (0.035, 0.038, 0.033)
iron = (0.13, 0.13, 0.115)
rust = (0.22, 0.20, 0.16)
red = (0.42, 0.16, 0.105)
glass = (0.71, 0.79, 0.78)
yellow = (0.66, 0.50, 0.16)

# Architecture: front face is at y=0, with room extending to the right.
architecture = Asset('Architecture')
architecture.include('partition', box((2.06, .16, 3.50), center=(-.35, .10, 1.75), color=cream))
architecture.include('partition_top_cap', box((2.13, .22, .10), center=(-.35, .08, 3.47), color=(.54,.51,.41)))
architecture.include('left_door', box((.53, .10, 3.35), center=(-1.65, -.01, 1.65), color=red))
architecture.include('door_edge', box((.035, .05, 3.36), center=(-1.375, -.075, 1.66), color=(.27,.11,.075)))
architecture.include('door_panel_left', box((.025, .025, 2.42), center=(-1.87,-.075,1.57), color=(.50,.22,.15)))
architecture.include('door_panel_right', box((.025, .025, 2.42), center=(-1.48,-.075,1.57), color=(.50,.22,.15)))
architecture.include('door_panel_top', box((.40, .025, .025), center=(-1.675,-.075,2.77), color=(.50,.22,.15)))
architecture.include('floor', box((7, 6, .08), center=(.4, 1.5, -.05), color=(.54,.53,.45)))
architecture.include('right_wall', box((1.75,.14,3.5), center=(1.47,1.05,1.75), color=(.64,.65,.59)))
scene.include('architecture', architecture)

# Recessed tall window with a bright surface and narrow dark mullions.
window = Asset('Right window')
window.include('dark_recess', box((.90,.06,2.48), center=(1.26,.955,2.06), color=(.14,.16,.15)))
window.include('glazing', box((.77,.025,2.31), center=(1.26,.916,2.07), color=glass))
for x in (.865,1.26,1.655):
    window.include('vertical_frame_'+str(x), box((.035,.05,2.39), center=(x,.88,2.07), color=(.12,.14,.13)))
for z in (.88,1.62,2.36,3.26):
    window.include('horizontal_frame_'+str(z), box((.82,.05,.035), center=(1.26,.88,z), color=(.12,.14,.13)))
window.include('sill', box((1.04,.25,.08), center=(1.25,.84,.83), color=(.35,.36,.32)))
scene.include('window', window)

bench = Asset('Background bench')
bench.include('seat', box((1.6,.40,.09), center=(1.36,.64,.65), color=(.27,.16,.10)))
bench.include('front_rail', box((1.6,.06,.13), center=(1.36,.40,.53), color=(.12,.09,.07)))
bench.include('leg', box((.08,.08,.49), center=(1.68,.60,.27), color=(.12,.10,.08)))
scene.include('bench', bench)

pipe = Asset('Ceiling pipe')
pipe.include('horizontal', rod(.042,start=(-.14,-.12,3.44),end=(1.25,-.12,3.44),color=(.12,.22,.21)))
pipe.include('elbow', rod(.045,start=(-.28,-.12,3.48),end=(-.14,-.12,3.44),color=(.12,.22,.21)))
pipe.include('collar', rod(.054,start=(-.12,-.12,3.44),end=(-.04,-.12,3.44),color=(.11,.18,.17)))
scene.include('pipe',pipe)

# Main framed display. All hardware lies just in front of the backing plane.
display = Asset('Framed tool display')
display.include('back_panel', box((1.37,.07,1.83), center=(-.32,-.115,2.12), color=backing))
for x in (-1.045,.405):
    display.include('frame_upright_'+str(x), box((.075,.14,1.98), center=(x,-.18,2.12), color=dark))
    display.include('inner_upright_'+str(x), box((.018,.03,1.87), center=(x+(.05 if x<0 else -.05),-.26,2.12), color=(.20,.20,.17)))
for z in (1.14,3.10):
    display.include('frame_crossbar_'+str(z), box((1.52,.14,.075), center=(-.32,-.18,z), color=dark))
display.include('inner_top_bar',box((1.18,.10,.08),center=(-.40,-.25,2.53),color=rust))
display.include('upper_bar_end',box((.49,.08,.055),center=(-.02,-.30,2.47),color=black))

# Disk and wheel helpers: cylinder axes run across the picture depth.
def disk(parent, name, x, z, radius, depth=.055, y=-.31, color=iron):
    parent.include(name, rod(radius, start=(x,y,z), end=(x,y-depth,z), color=color))

def wheel(parent, name, x, z, radius, spokes=5, y=-.35):
    part = Asset(name)
    # A segmented rim preserves its open center and visible spokes.
    n = 20
    for i in range(n):
        a = 2*math.pi*i/n
        b = 2*math.pi*(i+1)/n
        part.include('rim_%02d'%i, rod(.018,
            start=(x+radius*math.cos(a),y,z+radius*math.sin(a)),
            end=(x+radius*math.cos(b),y,z+radius*math.sin(b)), color=black))
    for i in range(spokes):
        a=2*math.pi*i/spokes + .15
        part.include('spoke_%02d'%i, rod(.025,
            start=(x,y-.005,z),
            end=(x+radius*.92*math.cos(a),y-.005,z+radius*.92*math.sin(a)),color=iron))
    disk(part,'hub',x,z,.050,.05,y-.015,black)
    parent.include(name,part)

wheel(display,'upper_spoked_wheel',-.77,2.84,.175,5)
for i,(x,r) in enumerate([(-.42,.073),(-.20,.063),(.00,.057),(.16,.052)]):
    disk(display,'upper_pulley_%d'%i,x,2.84,r,.06,-.30,black)
    disk(display,'upper_pulley_hub_%d'%i,x,2.84,r*.36,.015,-.37,(.27,.27,.23))

display.include('mid_horizontal_rod',rod(.014,start=(-.68,-.31,2.03),end=(-.05,-.31,2.03),color=iron))
display.include('central_mount',box((.065,.065,.13),center=(-.36,-.33,2.01),color=black))
display.include('central_hanging_pin',rod(.017,start=(-.36,-.36,2.03),end=(-.36,-.36,1.88),color=iron))
for i,x in enumerate((-.84,-.72)):
    display.include('small_left_bracket_%d'%i,box((.075,.055,.11),center=(x,-.32,1.91),color=black))
    display.include('small_left_pin_%d'%i,rod(.009,start=(x,-.36,1.85),end=(x,-.36,1.79),color=iron))
# Open loop at the lower left.
for i in range(12):
    a=2*math.pi*i/12
    b=2*math.pi*(i+1)/12
    display.include('hanging_ring_%02d'%i,rod(.012,
        start=(-.78+.052*math.cos(a),-.34,1.50+.052*math.sin(a)),
        end=(-.78+.052*math.cos(b),-.34,1.50+.052*math.sin(b)),color=iron))
display.include('ring_hook',rod(.012,start=(-.78,-.34,1.55),end=(-.78,-.34,1.59),color=iron))
# Pair of hand tools hanging at the center.
for i,dx in enumerate((-.02,.025)):
    display.include('tool_handle_%d'%i,rod(.018,start=(-.35+dx,-.36,1.59),end=(-.37+dx,-.36,1.40),color=black))
    disk(display,'tool_eye_%d'%i,-.35+dx,1.62,.026,.025,-.34,iron)
display.include('lower_left_tab',box((.11,.07,.025),center=(-.65,-.33,1.27),color=black))
display.include('lower_right_tab',box((.14,.07,.025),center=(.22,-.33,1.27),color=black))

# Clustered cast-metal apparatus at the lower right of the display.
machine = Asset('Display mounted machine')
machine.include('mounting_plate',box((.30,.07,.12),center=(.15,-.32,1.91),color=black))
machine.include('upper_horizontal_shaft',rod(.027,start=(.02,-.39,1.92),end=(.34,-.39,1.92),color=iron))
machine.include('vertical_post',rod(.025,start=(.22,-.40,1.82),end=(.22,-.40,2.04),color=iron))
disk(machine,'upper_gear',.22,1.92,.075,.06,-.40,black)
disk(machine,'upper_hub',.22,1.92,.024,.025,-.47,(.28,.28,.24))
machine.include('machine_tower',box((.12,.10,.23),center=(.08,-.37,1.63),color=iron))
machine.include('tower_top',rod(.035,start=(.08,-.39,1.73),end=(.08,-.39,1.84),color=black))
machine.include('body',box((.31,.14,.19),center=(.10,-.40,1.51),color=iron))
machine.include('body_upper',box((.22,.12,.12),center=(.10,-.40,1.63),color=(.19,.19,.16)))
disk(machine,'side_hub',.24,1.59,.085,.09,-.47,black)
disk(machine,'side_hub_center',.24,1.59,.030,.02,-.57,(.26,.26,.22))
machine.include('lower_base',box((.35,.16,.06),center=(.11,-.40,1.30),color=black))
machine.include('base_left',box((.065,.13,.19),center=(-.005,-.40,1.39),color=iron))
machine.include('base_right',box((.065,.13,.19),center=(.225,-.40,1.39),color=iron))
machine.include('base_arch',rod(.08,start=(.11,-.48,1.40),end=(.11,-.52,1.40),color=(.34,.35,.31)))
display.include('machine',machine)
scene.include('display',display)

# Below the case, a long dark mounting strip, label, and a short handle.
lower = Asset('Lower mounted equipment')
lower.include('black_rail',box((1.58,.06,.10),center=(-.32,-.12,.94),color=black))
lower.include('label',box((.27,.018,.15),center=(-.31,-.16,1.05),color=yellow))
lower.include('label_fold',box((.27,.025,.035),center=(-.31,-.17,.97),color=(.49,.37,.12)))
disk(lower,'rail_bolt',-.67,.94,.030,.02,-.16,iron)
lower.include('handle',rod(.035,start=(.03,-.18,1.08),end=(.16,-.28,.99),color=black))
lower.include('lower_rail',box((1.53,.06,.10),center=(-.30,-.12,.43),color=black))
# Large dark circular plates with radial cuts indicated as raised thin strips.
for j,(x,z,r) in enumerate([(-.65,.48,.27),(.09,.48,.24)]):
    disk(lower,'lower_disk_%d'%j,x,z,r,.075,-.19,(.15,.14,.12))
    for i in range(8):
        a=2*math.pi*i/8+.12
        lower.include('plate_%d_radial_%d'%(j,i),rod(.009,
            start=(x+r*.30*math.cos(a),-.28,z+r*.30*math.sin(a)),
            end=(x+r*.90*math.cos(a),-.28,z+r*.90*math.sin(a)),color=black))
    disk(lower,'lower_hub_%d'%j,x,z,.055,.025,-.28,(.29,.28,.23))
    disk(lower,'lower_center_%d'%j,x,z,.018,.015,-.31,black)
# Additional irregular jaws on the right-hand plate.
for i in range(5):
    a=2*math.pi*i/5
    x=.09+.15*math.cos(a)
    z=.48+.15*math.sin(a)
    lower.include('right_jaw_%d'%i,box((.11,.055,.09),center=(x,-.31,z),color=(.20,.19,.16)))
lower.include('stand_post',rod(.025,start=(.09,-.14,.29),end=(.09,-.14,.05),color=iron))
lower.include('stand_foot',box((.45,.06,.035),center=(.09,-.14,.045),color=iron))
scene.include('lower_equipment',lower)

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
background.inputs['Color'].default_value = (0.72,0.72,0.65,1)
background.inputs['Strength'].default_value = .7

set_view((2.0,-9.5,3.05),(-.25,0,1.76),lens=48)
area_emitter((-.8,-4.5,5.5),power=650,size=5,target=(-.3,0,1.6))
area_emitter((3,-1,3.8),power=300,size=3,target=(0,0,1.8))
