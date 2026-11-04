import math
import random
import bpy
from sceneact import *

# Visible inventory: brown electronics bench, blue monitor at upper left,
# oscilloscope and power supply below it, keyboard, two meters, calculator,
# black overhead lamp, soldering station, storage drawers, pliers, papers,
# bottles, solder reels, circuit boards, probes, and tangled foreground leads.
# Approximate image landmarks: monitor (20,40)-(178,175), scope (110,163)-(231,228),
# yellow meter (297,154)-(345,244), keyboard (48,248)-(272,350),
# lamp shade (251,66)-(421,113). These are visual estimates.
# World scale is arbitrary. Camera elevation and focal length are uncertain;
# camera parameters are kept separate from all object dimensions.

random.seed(19)
scene = Scene("Electronics workbench")
wood = (.37, .205, .115)
black = (.023, .028, .027)
dark = (.065, .075, .071)
gray = (.48, .49, .44)
cream = (.65, .66, .56)
red = (.60, .018, .012)
yellow = (.94, .61, .015)
silver = (.49, .53, .52)
paper = (.86, .85, .76)

def B(a, key, size, center, color):
    return a.include(key, box(size=size, center=center, color=color))

def R(a, key, radius, start, end, color):
    return a.include(key, rod(radius=radius, start=start, end=end, color=color))

def T(a, key, pts, radius, color):
    return a.include(key, sweep_tube(points=pts, radius=radius, color=color))

def dial(a, key, x, y, z, radius=.016, color=cream):
    R(a, key, radius, (x,y,z), (x,y-.015,z), color)
    B(a, key+"_mark", (.002,.003,radius*.65),
      (x,y-.017,z+radius*.25), dark)

def loop(a, key, center, rx, ry, color, radius=.003, phase=0, n=44):
    cx,cy,cz=center
    points=[]
    for j in range(n+1):
        t=phase+2*math.pi*j/n
        points.append((cx+rx*math.cos(t),cy+ry*math.sin(t),
                       cz+.0025*math.sin(3*t)))
    T(a,key,points,radius,color)

# Architecture and supporting worktop.
room=Asset("Room")
B(room,"wall",(4,.08,3),(0,.86,1.5),(.57,.565,.49))
B(room,"left_wall",(.07,2.4,3),(-1.15,-.25,1.5),(.43,.44,.39))
scene.include("room",room)
desk=Asset("Desk")
B(desk,"wood_top",(2.28,1.66,.065),(0,-.04,.735),wood)
B(desk,"front_edge",(2.28,.035,.09),(0,-.86,.71),(.25,.125,.065))
for x in [-1.02,1.02]:
    B(desk,"leg_"+str(x),(.075,.075,.70),(x,.48,.35),dark)
scene.include("desk",desk)
top=.7675

# Monitor: local assembly with blue display facing the viewer.
monitor=Asset("Monitor")
B(monitor,"foot",(.32,.23,.025),(-.74,.43,top+.013),black)
B(monitor,"pedestal",(.055,.055,.21),(-.74,.48,.88),black)
B(monitor,"housing",(.70,.065,.535),(-.74,.48,1.30),black)
B(monitor,"screen_blue",(.646,.009,.455),(-.74,.442,1.313),(.025,.38,.81))
B(monitor,"screen_upper_glow",(.64,.004,.035),(-.74,.435,1.521),(.12,.65,.94))
B(monitor,"taskbar",(.644,.005,.018),(-.74,.434,1.096),(.015,.19,.60))
B(monitor,"taskbar_light",(.018,.004,.007),(-1.043,.430,1.097),(.44,.77,.86))
# Small login marks in the middle of the screen.
for i in range(2):
    x=-.77+i*.075
    B(monitor,"login_icon_"+str(i),(.019,.004,.020),(x,.431,1.315),
      (.85,.77,.65) if i==0 else (.73,.15,.19))
    B(monitor,"login_caption_"+str(i),(.045,.004,.003),(x,.430,1.292),(.64,.80,.88))
B(monitor,"brand",(.037,.004,.004),(-.74,.442,1.055),gray)
monitor.turn("z",13,pivot=(-.74,.48,top))
scene.include("monitor",monitor)

# Oscilloscope: cream case, large dark CRT, dense control panel.
scope=Asset("Oscilloscope")
sx,sy=-.43,.30
B(scope,"body",(.55,.29,.285),(sx,sy,top+.151),cream)
B(scope,"front",(.55,.018,.278),(sx,sy-.154,top+.151),(.70,.70,.62))
B(scope,"screen_bezel",(.282,.018,.219),(sx-.112,sy-.17,top+.158),(.35,.38,.34))
B(scope,"screen",(.245,.009,.179),(sx-.112,sy-.183,top+.158),(.075,.105,.10))
for i in range(1,5):
    B(scope,"grid_h_"+str(i),(.235,.001,.0007),(sx-.112,sy-.189,top+.07+i*.033),(.16,.20,.17))
for i in range(1,7):
    B(scope,"grid_v_"+str(i),(.0007,.001,.171),(sx-.235+i*.035,sy-.190,top+.158),(.16,.20,.17))
for row in range(4):
    for col in range(3):
        dial(scope,f"knob_{row}_{col}",sx+.063+col*.054,sy-.174,
             top+.062+row*.055,.013 if row else .019)
for i in range(6):
    B(scope,"small_button_"+str(i),(.017,.007,.008),
      (sx+.04+i*.028,sy-.182,top+.257),dark)
for x in [sx-.19,sx+.19]:
    B(scope,"foot_"+str(x),(.052,.12,.019),(x,sy,.777),black)
scene.include("oscilloscope",scope)

supply=Asset("Power supply")
B(supply,"case",(.23,.25,.215),(-.91,.26,top+.115),(.40,.43,.36))
B(supply,"face",(.23,.012,.205),(-.91,.129,top+.115),cream)
B(supply,"display_border",(.15,.009,.07),(-.91,.120,top+.163),dark)
B(supply,"display",(.124,.005,.044),(-.91,.113,top+.163),(.16,.22,.18))
for i in range(3):
    dial(supply,"control_"+str(i),-.98+i*.067,.117,top+.067,.022)
B(supply,"top_device",(.16,.14,.045),(-.91,.26,1.015),(.63,.64,.54))
B(supply,"top_display",(.075,.065,.003),(-.91,.245,1.039),dark)
scene.include("power_supply",supply)

# Rear black instrument with colored output terminals and coiled lead.
unit=Asset("Rear black unit")
B(unit,"case",(.34,.22,.13),(.0,.39,top+.07),black)
B(unit,"top",(.32,.20,.013),(.0,.39,top+.14),(.13,.16,.17))
for i,c in enumerate([yellow,silver,silver,red]):
    dial(unit,"terminal_"+str(i),-.115+i*.077,.272,top+.065,.014,c)
loop(unit,"top_cable",(-.02,.39,top+.158),.115,.057,black,.006)
scene.include("rear_instrument",unit)

# Upright yellow multimeter, with all parts tilted together.
meter=Asset("Yellow multimeter")
mx,my=.29,.28
B(meter,"rubber_case",(.205,.067,.365),(mx,my,top+.208),yellow)
B(meter,"front_panel",(.168,.009,.316),(mx,my-.039,top+.217),(.17,.19,.16))
B(meter,"lcd_frame",(.148,.007,.095),(mx,my-.046,top+.315),gray)
B(meter,"lcd",(.128,.004,.065),(mx,my-.051,top+.317),(.39,.46,.37))
for i in range(4):
    B(meter,"lcd_digit_"+str(i),(.018,.003,.003),
      (mx-.045+i*.029,my-.055,top+.322),(.12,.16,.13))
dial(meter,"selector",mx,my-.048,top+.178,.043,black)
R(meter,"selector_stripe",.003,(mx-.008,my-.067,top+.18),
  (mx+.018,my-.067,top+.205),cream)
for i,c in enumerate([black,black,red]):
    dial(meter,"socket_"+str(i),mx-.054+i*.054,my-.048,top+.075,.010,c)
meter.turn("x",-12,pivot=(mx,my,top+.025))
meter.turn("z",-8,pivot=(mx,my,top))
scene.include("yellow_meter",meter)

# Keyboard and calculator in the foreground.
keyboard=Asset("Keyboard")
kx,ky=-.43,-.38
B(keyboard,"base",(.91,.30,.032),(kx,ky,top+.023),(.035,.043,.043))
B(keyboard,"keybed",(.86,.27,.010),(kx,ky,top+.043),(.075,.085,.08))
for row in range(5):
    for col in range(16):
        if row==0 and 4<=col<=8:
            continue
        B(keyboard,f"key_{row}_{col}",(.042,.037,.016),
          (kx-.391+col*.052,ky-.108+row*.052,top+.055),(.018,.024,.024))
        if row>0 and (col+row)%3==0:
            B(keyboard,f"legend_{row}_{col}",(.010,.008,.001),
              (kx-.391+col*.052,ky-.108+row*.052,top+.064),(.43,.46,.43))
B(keyboard,"spacebar",(.245,.036,.016),(kx-.05,ky-.108,top+.055),black)
keyboard.turn("z",15,pivot=(kx,ky,top))
scene.include("keyboard",keyboard)

calc=Asset("Calculator")
cx,cy=-.94,-.65
B(calc,"body",(.18,.285,.027),(cx,cy,top+.025),(.045,.06,.06))
B(calc,"face",(.16,.262,.005),(cx,cy,top+.041),(.63,.65,.58))
B(calc,"lcd",(.126,.055,.003),(cx,cy+.083,top+.045),(.28,.38,.33))
for row in range(6):
    for col in range(4):
        B(calc,f"button_{row}_{col}",(.026,.019,.007),
          (cx-.057+col*.038,cy-.104+row*.029,top+.047),
          (.19,.25,.25) if col<3 else (.28,.39,.42))
calc.turn("z",12,pivot=(cx,cy,top))
scene.include("calculator",calc)

# Second handheld meter lying among the leads.
small=Asset("Small handheld meter")
B(small,"body",(.15,.245,.055),(.18,-.285,top+.037),black)
B(small,"yellow_front",(.125,.214,.009),(.18,-.285,top+.068),(.72,.59,.035))
B(small,"display",(.097,.057,.004),(.18,-.219,top+.075),(.38,.47,.38))
R(small,"rotary",.034,(.18,-.30,top+.071),(.18,-.30,top+.083),black)
for i in range(2):
    R(small,"port_"+str(i),.012,(.145+i*.06,-.365,top+.072),
      (.145+i*.06,-.365,top+.080),red if i else black)
small.turn("z",-14,pivot=(.18,-.285,top))
scene.include("small_meter",small)

# Back-wall parts drawers, with individual trays and pale label plates.
drawers=Asset("Parts cabinets")
for cabinet,(x,w,cols) in enumerate([(-.01,.56,4),(.64,.70,5)]):
    B(drawers,f"cabinet_{cabinet}",(w,.19,.48),(x,.745,1.80),(.035,.045,.04))
    for row in range(5):
        for col in range(cols):
            xx=x-w/2+.014+(col+.5)*(w-.028)/cols
            zz=1.59+row*.087
            ww=(w-.040)/cols
            B(drawers,f"tray_{cabinet}_{row}_{col}",(ww,.022,.071),
              (xx,.638,zz),(.15+.018*(row%2),.175,.16))
            B(drawers,f"lip_{cabinet}_{row}_{col}",(ww*.87,.012,.008),
              (xx,.620,zz-.025),(.29,.31,.28))
            B(drawers,f"label_{cabinet}_{row}_{col}",(ww*.51,.003,.018),
              (xx,.611,zz-.004),(.66,.67,.58))
            B(drawers,f"label_mark_{cabinet}_{row}_{col}",(ww*.29,.002,.003),
              (xx,.608,zz-.004),(.20,.23,.21))
scene.include("drawers",drawers)

# Pinned papers and red-handled pliers on the wall.
wallbits=Asset("Wall tools and papers")
for i in range(3):
    B(wallbits,"paper_"+str(i),(.30,.004,.25),
      (-.01+i*.295,.789,1.36),paper)
    for j in range(5):
        B(wallbits,f"paper_rule_{i}_{j}",(.25,.002,.001),
          (-.01+i*.295,.785,1.29+j*.032),(.62,.63,.57))
for i,x in enumerate([-.67,-.53,-.30]):
    z=1.26+(i%2)*.015
    R(wallbits,f"plier_jaw_a_{i}",.008,(x-.012,.75,z+.025),(x-.023,.75,z+.12),dark)
    R(wallbits,f"plier_jaw_b_{i}",.008,(x+.012,.75,z+.025),(x+.022,.75,z+.12),silver)
    T(wallbits,f"plier_left_{i}",[(x,.75,z+.04),(x-.027,.746,z-.015),
      (x-.037,.742,z-.09),(x-.021,.741,z-.105)],.009,red)
    T(wallbits,f"plier_right_{i}",[(x,.75,z+.04),(x+.025,.746,z-.015),
      (x+.037,.742,z-.09),(x+.025,.741,z-.105)],.009,red)
    R(wallbits,f"plier_pivot_{i}",.012,(x,.739,z+.028),(x,.755,z+.028),silver)
scene.include("wall_objects",wallbits)

# Overhead bench lamp, dark wide head with articulated arm and desk clamp.
lamp=Asset("Bench lamp")
B(lamp,"base",(.17,.14,.038),(.73,.31,top+.025),black)
R(lamp,"upright",.013,(.73,.35,top+.035),(.76,.45,1.53),black)
R(lamp,"upper_arm",.014,(.76,.45,1.53),(.64,.47,1.59),black)
R(lamp,"brace",.006,(.70,.36,1.02),(.78,.46,1.49),silver)
R(lamp,"head_joint",.028,(.62,.43,1.58),(.68,.43,1.58),black)
B(lamp,"wide_shade",(.65,.205,.058),(.30,.42,1.615),(.018,.022,.022))
B(lamp,"right_cap",(.16,.18,.075),(.66,.42,1.604),black)
B(lamp,"diffuser",(.56,.156,.008),(.28,.42,1.582),(.69,.70,.61))
for i in range(3):
    B(lamp,"head_rib_"+str(i),(.007,.20,.004),
      (.07+i*.032,.42,1.646),gray)
T(lamp,"power_cord",[(.68,.47,1.59),(.83,.52,1.57),(.86,.47,1.40),
  (.82,.39,1.14),(.77,.30,.82),(.89,.20,.78)],.005,black)
scene.include("lamp",lamp)

# Solder station, iron holder, rear bottle, aerosol cans.
station=Asset("Soldering station")
B(station,"base",(.29,.27,.065),(.85,.28,top+.039),(.24,.19,.10))
B(station,"top",(.25,.23,.014),(.85,.28,top+.079),(.36,.39,.35))
R(station,"coil_axis",.050,(.83,.32,.88),(.92,.43,1.02),dark)
for i in range(9):
    yy=.31+i*.013
    zz=.88+i*.016
    # Narrow rings read as the coiled metal holder.
    pts=[(.85+.049*math.cos(t),yy+.025*math.sin(t),zz+.040*math.sin(t))
         for t in [2*math.pi*j/20 for j in range(21)]]
    T(station,"holder_ring_"+str(i),pts,.003,silver)
R(station,"iron_handle",.023,(.75,.18,.91),(.85,.31,1.00),(.12,.42,.42))
R(station,"iron_collar",.027,(.845,.305,.995),(.865,.333,1.014),black)
R(station,"iron_shaft",.008,(.75,.18,.91),(.66,.07,.84),silver)
T(station,"iron_cable",[(.86,.32,1.01),(.99,.29,.93),(1.01,.06,.80),
  (.86,-.08,.785),(.76,-.21,.785)],.006,black)
scene.include("solder_station",station)

containers=Asset("Containers")
R(containers,"bottle_body",.055,(.98,.63,top),(.98,.63,1.02),(.34,.44,.44))
R(containers,"bottle_shoulder",.038,(.98,.63,1.02),(.98,.63,1.07),(.37,.47,.46))
R(containers,"bottle_neck",.019,(.98,.63,1.07),(.98,.63,1.13),(.40,.49,.48))
R(containers,"blue_cap",.023,(.98,.63,1.13),(.98,.63,1.155),(.055,.14,.27))
for i in range(2):
    x=.57+i*.11
    R(containers,"can_"+str(i),.038,(x,.52,top),(x,.52,1.03-i*.04),silver)
    R(containers,"can_top_"+str(i),.031,(x,.52,1.03-i*.04),(x,.52,1.044-i*.04),dark)
    B(containers,"can_label_"+str(i),(.055,.006,.11),
      (x,.481,.91),(.58,.61,.50))
scene.include("containers",containers)

# Papers below the lamp and instruments; small board beside the scope.
clutter=Asset("Desktop objects")
for i in range(4):
    page=B(clutter,"loose_sheet_"+str(i),(.36,.31,.0015),
      (.57,.10,top+.002+i*.002),(.86,.86,.79))
    page.turn("z",-12+i*5)
for j in range(7):
    B(clutter,"paper_writing_"+str(j),(.13,.0015,.0008),
      (.61,.03+j*.022,top+.012),(.47,.48,.44))
B(clutter,"circuit_board",(.20,.14,.015),(-.65,-.04,top+.017),(.035,.15,.32))
for i in range(8):
    x=-.72+(i%4)*.045
    y=-.075+(i//4)*.06
    B(clutter,"chip_"+str(i),(.027,.018,.012),(x,y,top+.032),black)
    for j in range(3):
        B(clutter,f"pin_{i}_{j}",(.003,.027,.002),(x-.008+j*.008,y,top+.030),silver)
R(clutter,"solder_reel",.047,(-.29,-.55,top),(-.29,-.55,top+.025),(.75,.77,.66))
R(clutter,"reel_core",.021,(-.29,-.55,top+.024),(-.29,-.55,top+.031),(.17,.40,.35))
R(clutter,"small_spool",.041,(.59,-.30,top),(.59,-.30,top+.052),silver)
R(clutter,"spool_hole",.016,(.59,-.30,top+.051),(.59,-.30,top+.054),black)
scene.include("desktop_clutter",clutter)

# Helping-hands tool and a cropped blue plastic organizer on the right.
tools=Asset("Foreground tools")
B(tools,"helping_base",(.18,.13,.035),(.87,-.25,top+.023),dark)
R(tools,"helping_post",.010,(.87,-.25,top+.04),(.87,-.25,.98),silver)
R(tools,"cross_arm",.008,(.73,-.25,.96),(1.00,-.25,.98),silver)
for i,x in enumerate([.75,.98]):
    R(tools,"clip_arm_"+str(i),.007,(x,-.25,.97),(x-.02,-.30,1.04),silver)
    B(tools,"clip_"+str(i),(.045,.012,.014),(x-.02,-.31,1.04),silver)
R(tools,"magnifier_rim",.072,(1.0,-.13,.96),(1.0,-.13,.97),dark)
R(tools,"magnifier_glass",.059,(1.0,-.13,.971),(1.0,-.13,.974),(.34,.40,.37))
organizer=Asset("Parts organizer")
B(organizer,"case",(.25,.39,.055),(1.02,-.62,top+.034),(.10,.23,.38))
B(organizer,"clear_lid",(.245,.38,.012),(1.02,-.62,top+.070),(.30,.39,.44))
for i in range(5):
    B(organizer,"divider_"+str(i),(.004,.37,.014),(.92+i*.05,-.62,top+.079),(.46,.51,.49))
for i in range(4):
    B(organizer,"cross_divider_"+str(i),(.24,.004,.014),(1.02,-.77+i*.10,top+.079),(.46,.51,.49))
organizer.turn("z",-15,pivot=(1.02,-.62,top))
scene.include("organizer",organizer)

# Loose yellow tabs and small components on the right foreground.
for i in range(12):
    x=.60+random.uniform(-.10,.19)
    y=-.49+random.uniform(-.23,.11)
    node=B(tools,"yellow_tape_"+str(i),(.052,.024,.0015),(x,y,top+.004),(.95,.70,.045))
    node.turn("z",random.uniform(-65,65))
for i in range(5):
    x=.43+i*.052
    R(tools,"loose_resistor_"+str(i),.002,(x,-.35,top+.009),(x+.045,-.32,top+.009),silver)
    R(tools,"resistor_body_"+str(i),.005,(x+.016,-.339,top+.009),(x+.030,-.329,top+.009),(.39,.23,.11))
scene.include("foreground_tools",tools)

# Cable tangles: irregular planar loops plus explicit long connections and probes.
cables=Asset("Test leads")
for i in range(15):
    cx=random.uniform(-.08,.43)
    cy=random.uniform(-.54,-.19)
    rx=random.uniform(.10,.27)
    ry=random.uniform(.06,.17)
    col=[black,red,black,red,(.42,.19,.035)][i%5]
    pts=[]
    for j in range(48):
        t=2*math.pi*j/47
        pts.append((cx+rx*math.cos(t)+.025*math.sin(3*t+i),
                    cy+ry*math.sin(t),top+.016+i*.0012+.004*math.sin(2*t)))
    T(cables,"loop_"+str(i),pts,.0032,col)
T(cables,"yellow_meter_red",[(.35,.25,.86),(.40,.08,.79),(.51,-.15,.79),
  (.41,-.44,.795),(.20,-.65,.79),(-.06,-.61,.79)],.004,red)
T(cables,"yellow_meter_black",[(.27,.25,.86),(.23,.08,.79),(.36,-.08,.80),
  (.52,-.30,.80),(.38,-.65,.79),(.03,-.72,.79)],.004,black)
T(cables,"keyboard_wire",[(-.26,-.20,.79),(-.36,-.07,.79),(-.15,.07,.79),
  (-.20,.17,.81),(-.36,.15,.87)],.005,black)
T(cables,"left_long_wire",[(-.91,.11,.80),(-.98,-.17,.79),(-.79,-.30,.80),
  (-.59,-.27,.83),(-.30,-.34,.81),(-.19,-.68,.79),(.25,-.77,.79)],.0035,red)
T(cables,"front_black_loop",[(-.43,-.38,.79),(-.50,-.66,.79),(-.33,-.78,.79),
  (.18,-.79,.79),(.54,-.74,.79),(.51,-.55,.80)],.004,black)
for i,(x,y,ang,col) in enumerate([
    (.14,-.73,-8,black),(.35,-.69,-17,red),(-.12,-.61,-35,black),
    (.52,-.26,32,(.02,.13,.44)),(.58,-.23,32,red)]):
    dx=.17*math.cos(math.radians(ang))
    dy=.17*math.sin(math.radians(ang))
    R(cables,"probe_handle_"+str(i),.010,(x,y,top+.025),(x+dx,y+dy,top+.025),col)
    R(cables,"probe_tip_"+str(i),.003,(x+dx,y+dy,top+.025),
      (x+dx*1.28,y+dy*1.28,top+.025),silver)
scene.include("cables",cables)

# Audit: all box dimensions and rod radii are positive; tube points are distinct.
# No fillets are needed. Every repeated inclusion uses a unique indexed key.
# Objects derive contact from desktop height; there are no bind dependencies.
realize(scene)

# Camera is independent of object scale; elevated front view shows desktop tops.
set_view(position=(.10,-2.92,2.48), target=(0,.10,1.105),
         lens=43, sensor=36, shift=(0,0))

world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new("World")
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.32,.34,.30,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.55
area_emitter(position=(-.35,-1.0,2.9),power=170,size=2.1,target=(0,0,.8))
area_emitter(position=(1.1,-.2,2.1),power=75,size=1.2,target=(.3,.15,.8))

# Gentle rough surfaces preserve the photograph's utilitarian material palette.
for mat in bpy.data.materials:
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type=="BSDF_PRINCIPLED":
                node.inputs["Roughness"].default_value=.70

sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE_NEXT"
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
sc.view_settings.exposure=0
sc.view_settings.gamma=1
# Execution runner performs the sole save and render.
