from sceneact import *
import bpy
import math
import random

# Evidence / ownership ledger (image coordinates are approximate visual hypotheses):
# Desk: entire lower image, brown top, foreground cropped; back wall above it.
# Monitor: (12,12)-(181,178), black frame, blue display; rear-left desk support.
# Oscilloscope: (107,158)-(231,227), cream body, dark screen and right controls.
# Small bench supply: (44,195)-(111,268), cream/gray, supported by desk.
# Keyboard: (45,239)-(272,354); calculator: (3,302)-(62,377), foreground-left.
# Yellow meter: (295,154)-(347,245); small meter: (267,248)-(314,298).
# Lamp: black head (248,63)-(433,115), right upright and desktop base.
# Drawer cabinets: top-right and upper-center, cropped; supported against rear wall.
# Wall pliers: red handles beneath monitor/cabinets; paper sheets behind equipment.
# Right soldering station, iron stand, bottle, aerosol, spools, loose hand tools.
# Leads overlap keyboard edge, meters, paper and tools, dominating foreground.
# World: x right, y rear, z up. Relative scale only; desk top z=.76.
# Each movable semantic owner below is an Asset; components retain owner transforms.
# Support is explicitly located at tabletop or wall face, not composite AABB tops.

random.seed(12)
scene = Scene("Electronics workbench")

# Camera is independent of object dimensions.
CAMERA = dict(position=(0.05, -3.25, 2.65),
              target=(0.0, 0.14, 1.10), lens=43)
TOP = .76
C = {
    'wood': (.35,.20,.13), 'wall': (.62,.62,.56),
    'black': (.018,.022,.021), 'dark': (.055,.065,.065),
    'cream': (.64,.64,.52), 'silver': (.48,.51,.49),
    'paper': (.82,.83,.76), 'red': (.55,.025,.018),
    'yellow': (.94,.60,.015), 'blue': (.025,.16,.32),
    'wireblack': (.012,.014,.014)
}

def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def bx(a, name, size, pos, color):
    a.include(name, box(size=size, center=pos, color=color))

def rd(a, name, radius, start, end, color):
    a.include(name, rod(radius=radius, start=start, end=end, color=color))

def tube(a, name, points, radius, color):
    a.include(name, sweep_tube(points=points, radius=radius, color=color))

def oval(a, name, pos, scale, color):
    a.include(name, ball(radius=1, center=pos, color=color).resize(scale, pivot=pos))

def local_box(a, name, size, pos, color, rotation=None):
    node = box(size=size, center=pos, color=color)
    if rotation:
        node.turn(euler=rotation)
    a.include(name, node)

# Architecture anchors: rear wall, broad tabletop, cropped foreground contact.
room = asset("architecture")
bx(room, "rear_wall", (3.3,.08,2.7), (0,.82,1.35), C['wall'])
bx(room, "left_return", (.07,1.6,2.7), (-1.36,.04,1.35), (.40,.41,.36))
desk = asset("workbench")
bx(desk, "wood_top", (2.65,1.65,.065), (0,-.015,TOP-.0325), C['wood'])
bx(desk, "front_edge", (2.65,.045,.12), (0,-.82,TOP-.065), (.27,.15,.10))

# Wall papers: separate loose sheets attached to wall face.
for i,(x,z,w,h) in enumerate([(-.08,1.39,.43,.33),(.37,1.38,.40,.37),
                              (.82,1.38,.42,.30)]):
    a=asset("wall_paper_%d"%i)
    bx(a,"sheet",(w,.006,h),(x,.768,z),C['paper'])
    for j in range(3):
        bx(a,"faint_rule_%d"%j,(w*.65,.002,.002),
           (x,.763,z+.06-j*.028),(.65,.68,.64))

# Drawer racks: black casings with inset muted translucent fronts and pale labels.
for rackname, x, width, cols, rows in [
    ("left_parts_cabinet",.20,.64,4,4),
    ("right_parts_cabinet",.94,.77,5,6)]:
    a=asset(rackname)
    height=.64 if rows==4 else .88
    z=1.98
    bx(a,"outer_case",(width,.20,height),(x,.68,z),C['black'])
    cw=(width-.025)/cols
    ch=(height-.025)/rows
    for row in range(rows):
        for col in range(cols):
            xx=x-width/2+.014+cw*(col+.5)
            zz=z-height/2+.014+ch*(row+.5)
            bx(a,f"drawer_{row}_{col}",(cw-.012,.025,ch-.012),
               (xx,.567,zz),(.16,.19,.18))
            bx(a,f"label_{row}_{col}",(cw*.52,.003,ch*.22),
               (xx,.551,zz-.015),(.57,.59,.51))
            bx(a,f"pull_{row}_{col}",(cw*.30,.015,.009),
               (xx,.543,zz+.025),(.09,.10,.095))

# Monitor assembly: whole owner posed as one object.
monitor=asset("monitor")
bx(monitor,"foot",(.39,.23,.025),(-.83,.40,TOP+.015),C['black'])
rd(monitor,"pedestal",.033,(-.83,.45,TOP+.02),(-.83,.47,1.10),C['dark'])
bx(monitor,"housing",(.77,.065,.59),(-.83,.45,1.43),C['black'])
bx(monitor,"display",(.694,.008,.489),(-.83,.413,1.444),(.035,.39,.77))
bx(monitor,"taskbar",(.694,.009,.026),(-.83,.407,1.210),(.015,.20,.62))
bx(monitor,"display_glow",(.66,.009,.36),(-.83,.407,1.49),(.11,.48,.82))
for i,x in enumerate([-.87,-.80]):
    bx(monitor,"login_icon_%d"%i,(.025,.011,.023),(x,.400,1.43),
       (.85,.76,.69) if i==0 else (.74,.14,.15))
bx(monitor,"login_text",(.13,.010,.005),(-.84,.399,1.395),(.58,.77,.88))
bx(monitor,"power_led",(.009,.008,.005),(-.53,.409,1.165),(.12,.40,.30))
monitor.turn('z',-11,pivot=(-.83,.45,1.43))

# Oscilloscope, supported at z=TOP.
scope=asset("oscilloscope")
bx(scope,"case",(.58,.31,.285),(-.37,.41,TOP+.153),C['cream'])
bx(scope,"front_bezel",(.56,.014,.26),(-.37,.245,TOP+.153),(.73,.72,.62))
bx(scope,"screen_rim",(.265,.018,.218),(-.485,.232,TOP+.158),(.26,.29,.27))
bx(scope,"screen",(.229,.008,.181),(-.485,.219,TOP+.158),(.035,.07,.075))
for i in range(4):
    for j in range(3):
        x=-.285+i*.049
        z=TOP+.065+j*.068
        rd(scope,f"knob_{i}_{j}",.017,(x,.218,z),(x,.194,z),(.63,.65,.58))
for i in range(5):
    bx(scope,f"top_button_{i}",(.025,.013,.008),(-.28+i*.035,.224,TOP+.264),(.29,.32,.29))
for x in [-.59,-.15]:
    bx(scope,"foot_"+str(x),(.045,.12,.018),(x,.39,TOP+.009),C['dark'])

supply=asset("small_bench_supply")
bx(supply,"body",(.29,.27,.25),(-.91,.14,TOP+.13),(.57,.59,.49))
bx(supply,"front",(.28,.013,.235),(-.91,-.002,TOP+.13),C['cream'])
bx(supply,"readout",(.19,.010,.070),(-.91,-.012,TOP+.198),(.07,.10,.09))
for i in range(3):
    rd(supply,f"knob_{i}",.022,(-.99+i*.08,-.013,TOP+.09),
       (-.99+i*.08,-.04,TOP+.09),(.50,.52,.46))
bx(supply,"top_instrument",(.20,.18,.045),(-.91,.15,TOP+.278),(.63,.65,.53))
bx(supply,"top_window",(.13,.08,.003),(-.91,.125,TOP+.303),(.13,.19,.15))

# Black rear power/control unit with colored sockets.
unit=asset("rear_control_unit")
bx(unit,"case",(.35,.22,.12),(.19,.42,TOP+.067),C['black'])
for i in range(4):
    rd(unit,f"socket_{i}",.017,(.065+i*.078,.303,TOP+.065),
       (.065+i*.078,.292,TOP+.065),
       [C['yellow'],C['silver'],C['silver'],C['red']][i])
tube(unit,"coiled_top_cable",[(.04,.41,.91),(.01,.47,.95),(.12,.50,.97),
                            (.25,.47,.95),(.20,.39,.93),(.10,.39,.94)],.012,C['dark'])

# Keyboard: owner contains sloping slab and grouped key rows.
keyboard=asset("keyboard")
bx(keyboard,"base",(.89,.34,.035),(-.50,-.32,TOP+.023),C['black'])
for row in range(5):
    for col in range(14):
        bx(keyboard,f"key_{row}_{col}",(.041,.042,.013),
           (-.904+col*.060,-.46+row*.057,TOP+.048),(.055,.063,.062))
bx(keyboard,"spacebar",(.28,.037,.014),(-.58,-.475,TOP+.052),(.075,.08,.075))
keyboard.turn('z',13,pivot=(-.5,-.32,TOP))
mousepad=asset("mouse_pad")
bx(mousepad,"pad",(.35,.30,.005),(-.13,-.18,TOP+.003),(.11,.14,.15))
mouse=asset("mouse")
oval(mouse,"shell",(-.10,-.19,TOP+.036),(.065,.10,.035),(.045,.05,.047))
tube(mouse,"cord",[(-.10,-.10,.80),(-.08,.02,.79),(.03,.10,.79),(.13,.14,.80)],.005,C['black'])

calculator=asset("calculator")
bx(calculator,"housing",(.22,.36,.030),(-1.05,-.62,TOP+.022),(.58,.60,.54))
bx(calculator,"screen",(.16,.068,.004),(-1.05,-.505,TOP+.040),(.19,.25,.22))
for r in range(5):
    for c in range(4):
        bx(calculator,f"button_{r}_{c}",(.032,.032,.009),
           (-1.124+c*.049,-.57-r*.044,TOP+.043),
           (.12,.16,.16) if r<4 else (.15,.22,.25))
calculator.turn('z',15,pivot=(-1.05,-.62,TOP))

# Multimeters have complete housings, LCDs, dials, jacks and support stands.
def meter(name, position, size, yellow, tilt):
    a=asset(name)
    w,d,h=size
    bx(a,"rubber_shell",(w,d,h),(0,0,h/2),yellow)
    bx(a,"face",(w*.82,.012,h*.88),(0,-d/2-.007,h*.52),(.23,.25,.22))
    bx(a,"lcd",(w*.67,.006,h*.23),(0,-d/2-.016,h*.78),(.45,.54,.44))
    for i in range(3):
        bx(a,f"lcd_digit_{i}",(.014,.003,.022),
           (-w*.18+i*w*.17,-d/2-.021,h*.78),(.12,.18,.14))
    rd(a,"dial",w*.205,(0,-d/2-.018,h*.40),(0,-d/2-.037,h*.40),(.10,.12,.11))
    rd(a,"dial_pointer",.006,(0,-d/2-.040,h*.40),
       (w*.13,-d/2-.040,h*.50),(.64,.65,.56))
    for i in range(3):
        rd(a,f"jack_{i}",w*.048,(-w*.26+i*w*.26,-d/2-.01,h*.10),
           (-w*.26+i*w*.26,-d/2-.026,h*.10),C['black'])
    bx(a,"stand",(.025,d*1.8,h*.55),(0,d*.6,h*.28),C['dark'])
    a.turn('x',tilt,pivot=(0,0,0))
    a.move(position)
    return a
meter("yellow_multimeter",(.39,.28,TOP+.02),(.205,.065,.36),C['yellow'],-12)
meter("foreground_multimeter",(.27,-.20,TOP+.012),(.145,.040,.205),(.62,.48,.035),-53)

# Wall hanging pliers retain the curved open handle silhouettes.
def pliers(name,x,z,scale=1):
    a=asset(name)
    y=.738
    paths=[
        [(x-.016,y,z),(x-.055,y,z-.055),(x-.07,y,z-.13),(x-.052,y,z-.17)],
        [(x+.016,y,z),(x+.055,y,z-.06),(x+.063,y,z-.13),(x+.048,y,z-.17)]]
    for i,p in enumerate(paths):
        tube(a,"red_handle_%d"%i,p,.011*scale,C['red'])
    rd(a,"left_jaw",.009,(x-.016,y,z),(x-.025,y,z+.085),C['silver'])
    rd(a,"right_jaw",.009,(x+.016,y,z),(x+.022,y,z+.08),C['silver'])
    rd(a,"hinge",.019,(x,y-.011,z),(x,y+.011,z),C['dark'])
pliers("wall_pliers_left",-.43,1.23)
pliers("wall_pliers_center",-.29,1.24)
pliers("wall_cutters",-.10,1.24,.8)

# Desktop papers under soldering equipment and wire.
for i,(x,y,w,d,ang) in enumerate([(.62,.12,.42,.38,-14),(.83,-.11,.24,.31,12)]):
    a=asset("desktop_paper_%d"%i)
    bx(a,"sheet",(w,d,.003),(x,y,TOP+.004),C['paper'])
    for j in range(5):
        bx(a,f"writing_{j}",(w*.62,.002,.001),(x,y-.09+j*.025,TOP+.006),
           (.52,.57,.55))
    a.turn('z',ang,pivot=(x,y,TOP))

# Lamp: broad black elongated shade, articulated upright and base.
lamp=asset("desk_lamp")
bx(lamp,"base",(.30,.23,.035),(.91,.25,TOP+.023),C['black'])
rd(lamp,"upright",.017,(.94,.29,TOP+.04),(.92,.36,1.64),C['black'])
rd(lamp,"angled_top",.019,(.92,.36,1.64),(.77,.36,1.80),C['black'])
rd(lamp,"shade_connector",.025,(.77,.36,1.80),(.55,.36,1.82),C['dark'])
local_box(lamp,"long_shade",(.75,.20,.075),(.35,.36,1.84),C['black'],(0,6,-10))
bx(lamp,"underside_diffuser",(.57,.145,.008),(.31,.35,1.797),(.54,.54,.45))
tube(lamp,"electric_cord",[(.94,.30,.79),(1.04,.34,.87),(.97,.36,1.28),
                          (.96,.37,1.62),(.82,.38,1.77)],.006,C['black'])

# Soldering station and iron holder at right.
station=asset("soldering_station")
bx(station,"body",(.29,.27,.16),(.98,.39,TOP+.085),(.12,.17,.16))
bx(station,"front_panel",(.27,.012,.13),(.98,.247,TOP+.086),(.17,.23,.22))
rd(station,"temperature_knob",.031,(.94,.233,TOP+.095),(.94,.207,TOP+.095),C['black'])
bx(station,"switch",(.025,.012,.035),(1.06,.232,TOP+.07),C['red'])
iron=asset("soldering_iron_and_holder")
bx(iron,"stand_base",(.22,.25,.022),(1.00,-.12,TOP+.016),(.22,.23,.20))
rd(iron,"holder_frame",.014,(.95,-.10,TOP+.03),(1.01,.02,TOP+.18),C['silver'])
rd(iron,"iron_grip",.026,(.91,-.10,TOP+.15),(1.04,.10,TOP+.31),(.035,.23,.25))
rd(iron,"iron_shaft",.009,(.91,-.10,TOP+.15),(.83,-.23,TOP+.05),C['silver'])
tube(iron,"power_cord",[(1.04,.10,1.07),(1.14,.16,1.03),(1.16,-.02,.81),
                      (1.04,-.26,.78),(.82,-.26,.78)],.009,C['black'])

# Bottle and aerosol, far-right desk.
bottle=asset("clear_bottle")
rd(bottle,"body",.062,(1.19,.59,TOP+.02),(1.19,.59,TOP+.25),(.43,.49,.46))
rd(bottle,"neck",.026,(1.19,.59,TOP+.25),(1.19,.59,TOP+.35),(.53,.57,.51))
rd(bottle,"blue_cap",.028,(1.19,.59,TOP+.35),(1.19,.59,TOP+.38),(.03,.12,.29))
can=asset("aerosol_can")
rd(can,"cylinder",.043,(.73,.46,TOP+.01),(.73,.46,TOP+.27),(.57,.60,.56))
rd(can,"top",.035,(.73,.46,TOP+.27),(.73,.46,TOP+.29),(.73,.74,.66))
bx(can,"dark_label",(.066,.008,.10),(.73,.414,TOP+.14),(.13,.18,.15))
bx(can,"red_label",(.04,.009,.025),(.73,.409,TOP+.20),C['red'])

# PCB and components left of keyboard.
pcb=asset("loose_circuit_board")
bx(pcb,"board",(.22,.15,.008),(-.65,.01,TOP+.012),(.025,.12,.22))
for i in range(5):
    bx(pcb,f"chip_{i}",(.035,.026,.012),(-.73+i*.038,.01+(i%2)*.043,TOP+.025),C['black'])
    rd(pcb,f"capacitor_{i}",.010,(-.72+i*.035,-.035,TOP+.018),
       (-.72+i*.035,-.035,TOP+.055),(.28,.37,.40))

# Spools and right hand-tools, all resting on table.
for name,x,y,r in [("solder_spool",1.11,-.30,.078),("small_wire_spool",-.29,-.50,.048)]:
    a=asset(name)
    rd(a,"core",r*.60,(x,y,TOP+.012),(x,y,TOP+.060),(.53,.56,.51))
    for j,z in enumerate([TOP+.011,TOP+.061]):
        rd(a,"flange_%d"%j,r,(x,y,z),(x,y,z+.006),(.58,.61,.55))
    rd(a,"center_hole",r*.24,(x,y,TOP+.067),(x,y,TOP+.069),C['dark'])

tools=asset("foreground_hand_tools")
for i,(x,y,dx,dy,col) in enumerate([
    (.15,-.69,.42,.03,C['red']),(.03,-.60,.48,-.08,C['black']),
    (.48,-.49,.28,.16,C['red']),(.62,-.34,.24,.12,C['blue'])]):
    rd(tools,f"handle_{i}",.018,(x,y,TOP+.022),(x+dx*.45,y+dy*.45,TOP+.022),col)
    rd(tools,f"shaft_{i}",.006,(x+dx*.45,y+dy*.45,TOP+.022),
       (x+dx,y+dy,TOP+.022),C['silver'])
rd(tools,"long_probe",.013,(-.14,-.74,TOP+.024),(.38,-.76,TOP+.024),C['black'])
rd(tools,"probe_tip",.004,(.38,-.76,TOP+.024),(.52,-.77,TOP+.024),C['silver'])

# Foreground lead bundles. Loose wires are independent assets and drape across supports.
wire_paths=[
 [(.36,.23,.85),(.40,.02,.80),(.54,-.20,.79),(.44,-.48,.79),(.15,-.57,.79),(-.03,-.38,.79),(.21,-.29,.80)],
 [(.43,.23,.84),(.44,-.02,.79),(.19,-.12,.79),(.08,-.32,.80),(.21,-.45,.79),(.58,-.39,.79),(.64,-.62,.79),(.49,-.74,.79),(.15,-.70,.79)],
 [(.23,-.19,.81),(.14,-.31,.80),(-.04,-.29,.79),(-.20,-.35,.79),(-.09,-.46,.79),(.18,-.48,.79),(.37,-.35,.80)],
 [(.30,-.22,.81),(.47,-.29,.79),(.66,-.12,.79),(.74,-.23,.79),(.61,-.40,.79),(.29,-.47,.79)],
 [(-.62,-.22,.82),(-.45,-.20,.81),(-.36,-.40,.80),(-.46,-.61,.79),(-.34,-.75,.79),(-.07,-.77,.79)],
 [(-.54,-.24,.82),(-.44,-.36,.80),(-.28,-.31,.79),(-.06,-.42,.80),(.09,-.51,.79),(.45,-.56,.79)],
 [(.85,.23,.80),(.75,.11,.79),(.65,-.04,.79),(.47,-.08,.79),(.51,-.26,.80),(.73,-.32,.79)],
 [(-.88,.04,.82),(-.91,-.13,.79),(-.74,-.20,.79),(-.67,-.10,.79),(-.72,.01,.79)],
 [(.02,-.40,.80),(.15,-.60,.79),(.42,-.64,.79),(.54,-.73,.79),(.36,-.80,.79),(.07,-.76,.79)],
 [(-.31,-.49,.79),(-.51,-.57,.79),(-.54,-.72,.79),(-.42,-.85,.78)],
]
for i,pts in enumerate(wire_paths):
    a=asset("loose_test_lead_%02d"%i)
    col=C['red'] if i%2==0 else C['wireblack']
    tube(a,"flexible_cable",pts,.006 if i<7 else .0045,col)
    p=pts[-1]
    rd(a,"plug",.011,p,(p[0]+.038,p[1]+.012,p[2]+.004),col)

# Sticky labels and loose scraps at front-right.
scraps=asset("yellow_paper_scraps")
for i in range(9):
    x=.72+random.uniform(-.10,.22)
    y=-.47+random.uniform(-.25,.08)
    node=box((.062,.036,.002),center=(x,y,TOP+.008),color=(.95,.70,.06))
    node.turn('z',random.uniform(-45,45))
    scraps.include("scrap_%d"%i,node)

# Cropped translucent red screwdriver pack on far foreground right.
pack=asset("screwdriver_package")
bx(pack,"backing",(.32,.40,.012),(1.12,-.65,TOP+.012),(.16,.20,.23))
for i in range(5):
    x=1.00+i*.05
    rd(pack,f"red_handle_{i}",.015,(x,-.77,TOP+.035),(x,-.62,TOP+.035),(.48,.045,.025))
    rd(pack,f"steel_shaft_{i}",.004,(x,-.62,TOP+.035),(x,-.47,TOP+.035),C['silver'])
bx(pack,"blue_header",(.32,.075,.006),(1.12,-.46,TOP+.025),(.035,.14,.29))

# Inline pre-execution review:
# Inventory includes architecture, monitor, cabinets, hanging tools, instruments,
# keyboard, calculator, lamp, solder station, containers, PCB, papers, spools,
# loose tools, packaging and overlapping cables. Object owners carry all attachments.
# Actual desk support is TOP=.76; wall objects use y=.74-.77. Lamp shade elevation
# and hidden rear instrument depths are uncertain visual estimates.
# Near anchor: calculator and foreground leads; far anchors: monitor and cabinet rows;
# architectural anchor: tabletop/wall boundary. Camera remains independent of sizes.
# Repeated drawers/labels and keyboard keys are the largest decorative families.
# Tubes use sparse bends; roughly several hundred expanded primitives, no fillet boxes.
# All dimensions are positive, rods have distinct endpoints, include slots are unique.
# No post-realize geometry or local material selection is used.
realize(scene)
set_view(**CAMERA)

world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new("World")
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.37,.40,.43,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.45
area_emitter((-.5,-1.4,3.2),power=210,size=2.2,target=(0,.1,.8),color=(1,.94,.85))
area_emitter((1.2,.0,2.7),power=90,size=1.7,target=(0,0,.8),color=(.86,.92,1))
