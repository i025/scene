# Reference inventory, approximate normalized image bounds:
# Cream partition x=.13-.81, full height; red door x=0-.16.
# Framed display x=.25-.78, y=.06-.63, with pale backing, a large open
# spoked wheel, four small pulleys, horizontal bars, hooks and dark machinery.
# Black rail and yellow label y=.62-.72; two large circular plates y=.73-.91
# and a short stand beneath the right plate.
# Right background: bright divided window x=.79-1, bench, wall and floor.
# Teal ceiling pipe crosses the upper edge. Mechanical functions and the
# areas obscured by the partition are uncertain.
# The first render showed the entire scene much too small, with excess empty
# space. This revision enlarges the camera framing and raises its target.
# Approximate expanded count: 145 primitive meshes; no boolean operations.

import math
import bpy
from sceneact import *

scene = Scene('Museum machinery')
cream = (.62, .59, .48)
backing = (.62, .64, .59)
dark = (.055, .055, .047)
black = (.028, .030, .026)
iron = (.11, .105, .09)
rust = (.19, .17, .14)
red = (.40, .13, .085)
glass = (.73, .82, .82)

architecture = Asset('Architecture')
architecture.include('partition', box((2.06,.16,3.50), center=(-.35,.10,1.75), color=cream))
architecture.include('top_cap', box((2.13,.22,.10), center=(-.35,.08,3.47), color=(.54,.51,.41)))
architecture.include('door', box((.53,.10,3.35), center=(-1.65,-.01,1.65), color=red))
architecture.include('door_edge', box((.035,.05,3.36), center=(-1.375,-.075,1.66), color=(.25,.08,.05)))
for x in (-1.87,-1.48):
    architecture.include('door_panel_side_'+str(x), box((.025,.025,2.42), center=(x,-.075,1.57), color=(.48,.19,.12)))
architecture.include('door_panel_top', box((.40,.025,.025), center=(-1.675,-.075,2.77), color=(.48,.19,.12)))
architecture.include('floor', box((7,6,.08), center=(.4,1.5,-.05), color=(.54,.53,.45)))
architecture.include('right_wall', box((1.75,.14,3.5), center=(1.47,1.05,1.75), color=(.64,.65,.59)))
scene.include('architecture', architecture)

window = Asset('Right window')
window.include('recess', box((.90,.06,2.48), center=(1.26,.955,2.06), color=(.10,.12,.11)))
window.include('glass', box((.77,.025,2.31), center=(1.26,.916,2.07), color=glass))
for x in (.865,1.26,1.655):
    window.include('vertical_'+str(x), box((.035,.05,2.39), center=(x,.88,2.07), color=(.09,.11,.10)))
for z in (.88,1.62,2.36,3.26):
    window.include('horizontal_'+str(z), box((.82,.05,.035), center=(1.26,.88,z), color=(.09,.11,.10)))
window.include('sill', box((1.04,.25,.08), center=(1.25,.84,.83), color=(.35,.36,.32)))
scene.include('window', window)

bench = Asset('Background bench')
bench.include('seat', box((1.6,.40,.09), center=(1.36,.64,.65), color=(.27,.16,.10)))
bench.include('front_rail', box((1.6,.06,.13), center=(1.36,.40,.53), color=(.12,.09,.07)))
bench.include('leg', box((.08,.08,.49), center=(1.68,.60,.27), color=(.12,.10,.08)))
scene.include('bench', bench)

pipe = Asset('Ceiling pipe')
pipe.include('main', rod(.042,start=(-.14,-.12,3.44),end=(1.25,-.12,3.44),color=(.09,.19,.18)))
pipe.include('elbow', rod(.045,start=(-.28,-.12,3.48),end=(-.14,-.12,3.44),color=(.09,.19,.18)))
pipe.include('collar', rod(.054,start=(-.12,-.12,3.44),end=(-.04,-.12,3.44),color=(.08,.15,.14)))
scene.include('pipe',pipe)

display = Asset('Framed tool display')
display.include('back_panel', box((1.37,.07,1.83), center=(-.32,-.115,2.12), color=backing))
for x in (-1.045,.405):
    display.include('upright_'+str(x), box((.075,.14,1.98), center=(x,-.18,2.12), color=dark))
    display.include('inner_upright_'+str(x), box((.018,.03,1.87), center=(x+(.05 if x<0 else -.05),-.26,2.12), color=(.16,.16,.13)))
for z in (1.14,3.10):
    display.include('crossbar_'+str(z), box((1.52,.14,.075), center=(-.32,-.18,z), color=dark))
display.include('inner_top_bar', box((1.18,.10,.08), center=(-.40,-.25,2.53), color=rust))
display.include('upper_bar_end', box((.49,.08,.055), center=(-.02,-.30,2.47), color=black))
display.include('upper_bar_drop', rod(.012,start=(.21,-.34,2.47),end=(.24,-.34,2.28),color=black))

def disk(parent,name,x,z,radius,depth=.055,y=-.31,color=iron):
    parent.include(name, rod(radius,start=(x,y,z),end=(x,y-depth,z),color=color))

def ring(parent,name,x,z,radius,y=-.35,tube=.018,segments=20,color=black):
    part = Asset(name)
    for i in range(segments):
        a = 2*math.pi*i/segments
        b = 2*math.pi*(i+1)/segments
        part.include('segment_%02d'%i, rod(tube,
            start=(x+radius*math.cos(a),y,z+radius*math.sin(a)),
            end=(x+radius*math.cos(b),y,z+radius*math.sin(b)),color=color))
    parent.include(name,part)

wheel = Asset('Upper spoked wheel')
ring(wheel,'rim',-.77,2.84,.175,segments=20,tube=.019)
for i in range(5):
    a=2*math.pi*i/5+.15
    wheel.include('spoke_%d'%i, rod(.025,start=(-.77,-.355,2.84),
        end=(-.77+.161*math.cos(a),-.355,2.84+.161*math.sin(a)),color=iron))
disk(wheel,'hub',-.77,2.84,.05,.05,-.365,black)
display.include('upper_wheel',wheel)

for i,(x,r) in enumerate([(-.42,.073),(-.20,.063),(.00,.057),(.16,.052)]):
    disk(display,'pulley_%d'%i,x,2.84,r,.06,-.30,black)
    disk(display,'pulley_hub_%d'%i,x,2.84,r*.36,.015,-.37,(.27,.27,.23))

display.include('middle_rod',rod(.014,start=(-.68,-.31,2.03),end=(-.05,-.31,2.03),color=iron))
display.include('middle_mount',box((.065,.065,.13),center=(-.36,-.33,2.01),color=black))
display.include('hanging_pin',rod(.017,start=(-.36,-.36,2.03),end=(-.36,-.36,1.88),color=iron))
for i,x in enumerate((-.84,-.72)):
    display.include('bracket_%d'%i,box((.075,.055,.11),center=(x,-.32,1.91),color=black))
    display.include('bracket_pin_%d'%i,rod(.009,start=(x,-.36,1.85),end=(x,-.36,1.79),color=iron))
ring(display,'hanging_ring',-.78,1.50,.052,y=-.34,tube=.012,segments=12,color=iron)
display.include('ring_hook',rod(.012,start=(-.78,-.34,1.55),end=(-.78,-.34,1.59),color=iron))
for i,dx in enumerate((-.02,.025)):
    display.include('tool_handle_%d'%i,rod(.018,start=(-.35+dx,-.36,1.59),end=(-.37+dx,-.36,1.40),color=black))
    disk(display,'tool_eye_%d'%i,-.35+dx,1.62,.026,.025,-.34,iron)
display.include('lower_tab_left',box((.11,.07,.025),center=(-.65,-.33,1.27),color=black))
display.include('lower_tab_right',box((.14,.07,.025),center=(.22,-.33,1.27),color=black))

machine = Asset('Display mounted machine')
machine.include('mount',box((.30,.07,.12),center=(.15,-.32,1.91),color=black))
machine.include('shaft',rod(.027,start=(.02,-.39,1.92),end=(.34,-.39,1.92),color=iron))
machine.include('post',rod(.025,start=(.22,-.40,1.82),end=(.22,-.40,2.04),color=iron))
disk(machine,'upper_gear',.22,1.92,.075,.06,-.40,black)
disk(machine,'upper_hub',.22,1.92,.024,.025,-.47,(.25,.25,.21))
machine.include('tower',box((.12,.10,.23),center=(.08,-.37,1.63),color=iron))
machine.include('tower_top',rod(.035,start=(.08,-.39,1.73),end=(.08,-.39,1.84),color=black))
machine.include('body',box((.31,.14,.19),center=(.10,-.40,1.51),color=iron))
machine.include('body_upper',box((.22,.12,.12),center=(.10,-.40,1.63),color=(.17,.17,.14)))
disk(machine,'side_hub',.24,1.59,.085,.09,-.47,black)
disk(machine,'side_hub_center',.24,1.59,.030,.02,-.57,(.26,.26,.22))
machine.include('lower_base',box((.35,.16,.06),center=(.11,-.40,1.30),color=black))
machine.include('base_left',box((.065,.13,.19),center=(-.005,-.40,1.39),color=iron))
machine.include('base_right',box((.065,.13,.19),center=(.225,-.40,1.39),color=iron))
disk(machine,'arch_opening',.11,1.40,.065,.04,-.49,(.34,.35,.31))
display.include('machine',machine)
scene.include('display',display)

lower = Asset('Lower mounted equipment')
lower.include('black_rail',box((1.58,.06,.10),center=(-.32,-.12,.94),color=black))
lower.include('label',box((.27,.018,.15),center=(-.31,-.16,1.05),color=(.66,.50,.16)))
lower.include('label_fold',box((.27,.025,.035),center=(-.31,-.17,.97),color=(.49,.37,.12)))
disk(lower,'rail_bolt',-.67,.94,.030,.02,-.16,iron)
lower.include('handle',rod(.035,start=(.03,-.18,1.08),end=(.16,-.28,.99),color=black))
lower.include('lower_rail',box((1.53,.06,.10),center=(-.30,-.12,.43),color=black))
for j,(x,z,r) in enumerate([(-.65,.48,.27),(.09,.48,.24)]):
    disk(lower,'plate_%d'%j,x,z,r,.075,-.19,(.13,.12,.10))
    for i in range(8):
        a=2*math.pi*i/8+.12
        lower.include('plate_%d_radial_%d'%(j,i),rod(.009,
            start=(x+r*.30*math.cos(a),-.28,z+r*.30*math.sin(a)),
            end=(x+r*.90*math.cos(a),-.28,z+r*.90*math.sin(a)),color=black))
    disk(lower,'plate_hub_%d'%j,x,z,.055,.025,-.28,(.25,.24,.19))
    disk(lower,'plate_center_%d'%j,x,z,.018,.015,-.31,black)
for i in range(5):
    a=2*math.pi*i/5
    x=.09+.15*math.cos(a)
    z=.48+.15*math.sin(a)
    lower.include('right_jaw_%d'%i,box((.11,.055,.09),center=(x,-.31,z),color=(.17,.16,.13)))
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
background.inputs['Color'].default_value = (.72,.72,.65,1)
background.inputs['Strength'].default_value = .55

set_view((1.25,-9.5,2.8),(-.28,0,2.00),lens=90)
area_emitter((-.8,-4.5,5.5),power=650,size=5,target=(-.3,0,1.6))
area_emitter((3,-1,3.8),power=300,size=3,target=(0,0,1.8))
