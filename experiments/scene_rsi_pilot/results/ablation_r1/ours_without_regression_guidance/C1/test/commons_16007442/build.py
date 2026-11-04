import math
import random
import bpy
from sceneact import *

# Observations: the successful image shows the complete desk front, while the
# reference crops it; the reference equipment occupies more of the frame.
# Reference landmarks, estimated visually: monitor (14,12)-(179,176),
# scope (110,161)-(231,225), lamp (251,65)-(424,113), keyboard (48,240)-(274,350).
# Main correction family: camera framing. Increasing focal length should enlarge
# equipment and crop the peripheral desk. Geometry and support heights are kept.
# Remaining hypotheses: the monitor may need a taller silhouette, and the
# reference lighting is darker. Those are not used to compensate for framing.
# Inventory includes cropped calculator and organizer, tools, papers, containers,
# drawers, monitors, instruments, keyboard, probes, and foreground wire tangles.
# Semantic mapping: SceneAct assets build structural silhouettes and supports;
# inexpensive batched meshes and curves supply their attached surface details.

random.seed(19)
scene = Scene("Electronics bench")
BLACK=(.023,.028,.027)
DARK=(.065,.075,.071)
CREAM=(.65,.66,.56)
GRAY=(.48,.49,.44)
RED=(.60,.018,.012)
YELLOW=(.94,.61,.015)
SILVER=(.49,.53,.52)
PAPER=(.86,.85,.76)
TOP=.7675
details={}
curves=[]

def asset(name):
    return scene.include(name,Asset(name))

def boxpart(a,key,size,center,color):
    return a.include(key,box(size=size,center=center,color=color))

def cylinder(a,key,r,p,q,color):
    return a.include(key,rod(radius=r,start=p,end=q,color=color))

def detail(group,size,center,color,angle=0):
    key=(group,tuple(color))
    verts,faces=details.setdefault(key,([],[]))
    x,y,z=center
    sx,sy,sz=[v/2 for v in size]
    c,s=math.cos(angle),math.sin(angle)
    n=len(verts)
    for dx,dy,dz in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
                     (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]:
        verts.append((x+c*dx-s*dy,y+s*dx+c*dy,z+dz))
    faces.extend(tuple(n+i for i in f) for f in
                 [(0,3,2,1),(4,5,6,7),(0,1,5,4),
                  (1,2,6,5),(2,3,7,6),(3,0,4,7)])

def wire(group,points,r,color):
    curves.append((group,points,r,tuple(color)))

def loop(group,center,rx,ry,color,r=.003,phase=0):
    x,y,z=center
    pts=[]
    for j in range(33):
        t=phase+2*math.pi*j/32
        pts.append((x+rx*math.cos(t),y+ry*math.sin(t),
                    z+.002*math.sin(3*t)))
    wire(group,pts,r,color)

def knob(a,key,x,y,z,r=.014,color=CREAM):
    cylinder(a,key,r,(x,y,z),(x,y-.015,z),color)

room=asset("Room")
boxpart(room,"back_wall",(4,.08,3),(0,.86,1.5),(.57,.565,.49))
boxpart(room,"left_wall",(.07,2.4,3),(-1.15,-.25,1.5),(.43,.44,.39))
desk=asset("Desk")
boxpart(desk,"top",(2.28,1.66,.065),(0,-.04,.735),(.37,.205,.115))
boxpart(desk,"front_edge",(2.28,.035,.09),(0,-.86,.71),(.25,.125,.065))

monitor=asset("Monitor")
boxpart(monitor,"foot",(.32,.23,.025),(-.74,.43,TOP+.013),BLACK)
boxpart(monitor,"stem",(.055,.055,.21),(-.74,.48,.88),BLACK)
boxpart(monitor,"housing",(.70,.065,.535),(-.74,.48,1.30),BLACK)
boxpart(monitor,"blue_screen",(.646,.009,.455),(-.74,.442,1.313),(.025,.38,.81))
boxpart(monitor,"screen_top",(.64,.004,.035),(-.74,.435,1.521),(.12,.65,.94))
boxpart(monitor,"taskbar",(.644,.005,.018),(-.74,.434,1.096),(.015,.19,.60))
for i in range(2):
    boxpart(monitor,f"login_icon_{i}",(.019,.004,.020),
            (-.77+i*.075,.431,1.315),(.85,.77,.65) if i==0 else (.73,.15,.19))
    boxpart(monitor,f"login_caption_{i}",(.045,.004,.003),
            (-.77+i*.075,.430,1.292),(.64,.80,.88))
monitor.turn("z",13,pivot=(-.74,.48,TOP))

scope=asset("Oscilloscope")
sx,sy=-.43,.30
boxpart(scope,"body",(.55,.29,.285),(sx,sy,TOP+.151),CREAM)
boxpart(scope,"face",(.55,.018,.278),(sx,sy-.154,TOP+.151),(.70,.70,.62))
boxpart(scope,"bezel",(.282,.018,.219),(sx-.112,sy-.17,TOP+.158),(.35,.38,.34))
boxpart(scope,"screen",(.245,.009,.179),(sx-.112,sy-.183,TOP+.158),(.075,.105,.10))
for row in range(4):
    for col in range(3):
        knob(scope,f"control_{row}_{col}",sx+.063+col*.054,sy-.174,
             TOP+.062+row*.055,.013 if row else .019)
for i in range(6):
    detail("Oscilloscope",(.017,.007,.008),
           (sx+.04+i*.028,sy-.182,TOP+.257),DARK)
for i in range(1,5):
    detail("Oscilloscope",(.235,.001,.0007),
           (sx-.112,sy-.189,TOP+.07+i*.033),(.16,.20,.17))
for i in range(1,7):
    detail("Oscilloscope",(.0007,.001,.171),
           (sx-.235+i*.035,sy-.190,TOP+.158),(.16,.20,.17))

supply=asset("Power supply")
boxpart(supply,"case",(.23,.25,.215),(-.91,.26,TOP+.115),(.40,.43,.36))
boxpart(supply,"face",(.23,.012,.205),(-.91,.129,TOP+.115),CREAM)
boxpart(supply,"display_border",(.15,.009,.07),(-.91,.120,TOP+.163),DARK)
boxpart(supply,"display",(.124,.005,.044),(-.91,.113,TOP+.163),(.16,.22,.18))
for i in range(3):
    knob(supply,f"control_{i}",-.98+i*.067,.117,TOP+.067,.022)
boxpart(supply,"top_device",(.16,.14,.045),(-.91,.26,1.015),CREAM)
boxpart(supply,"top_display",(.075,.065,.003),(-.91,.245,1.039),DARK)

unit=asset("Rear instrument")
boxpart(unit,"case",(.34,.22,.13),(0,.39,TOP+.07),BLACK)
boxpart(unit,"top",(.32,.20,.013),(0,.39,TOP+.14),(.13,.16,.17))
for i,c in enumerate([YELLOW,SILVER,SILVER,RED]):
    knob(unit,f"terminal_{i}",-.115+i*.077,.272,TOP+.065,.014,c)
loop("Rear instrument",(-.02,.39,TOP+.158),.115,.057,BLACK,.006)

meter=asset("Yellow multimeter")
mx,my=.29,.28
boxpart(meter,"case",(.205,.067,.365),(mx,my,TOP+.208),YELLOW)
boxpart(meter,"panel",(.168,.009,.316),(mx,my-.039,TOP+.217),(.17,.19,.16))
boxpart(meter,"lcd_frame",(.148,.007,.095),(mx,my-.046,TOP+.315),GRAY)
boxpart(meter,"lcd",(.128,.004,.065),(mx,my-.051,TOP+.317),(.39,.46,.37))
knob(meter,"selector",mx,my-.048,TOP+.178,.043,BLACK)
for i,c in enumerate([BLACK,BLACK,RED]):
    knob(meter,f"socket_{i}",mx-.054+i*.054,my-.048,TOP+.075,.010,c)
meter.turn("x",-12,pivot=(mx,my,TOP+.025))
meter.turn("z",-8,pivot=(mx,my,TOP))

keyboard=asset("Keyboard")
kx,ky=-.43,-.38
angle=math.radians(15)
def keyboard_point(x,y,z):
    return (kx+math.cos(angle)*x-math.sin(angle)*y,
            ky+math.sin(angle)*x+math.cos(angle)*y,z)
boxpart(keyboard,"base",(.91,.30,.032),(kx,ky,TOP+.023),(.035,.043,.043))
boxpart(keyboard,"bed",(.86,.27,.010),(kx,ky,TOP+.043),(.075,.085,.08))
keyboard.turn("z",15,pivot=(kx,ky,TOP))
for row in range(5):
    for col in range(16):
        if row==0 and 4<=col<=8:
            continue
        p=keyboard_point(-.391+col*.052,-.108+row*.052,TOP+.055)
        detail("Keyboard",(.042,.037,.016),p,BLACK,angle)
        if row>0 and (col+row)%3==0:
            detail("Keyboard",(.010,.008,.001),(p[0],p[1],TOP+.064),
                   (.43,.46,.43),angle)
detail("Keyboard",(.245,.036,.016),
       keyboard_point(-.05,-.108,TOP+.055),BLACK,angle)

calc=asset("Calculator")
cx,cy=-.94,-.65
boxpart(calc,"body",(.18,.285,.027),(cx,cy,TOP+.025),(.045,.06,.06))
boxpart(calc,"face",(.16,.262,.005),(cx,cy,TOP+.041),(.63,.65,.58))
boxpart(calc,"lcd",(.126,.055,.003),(cx,cy+.083,TOP+.045),(.28,.38,.33))
for row in range(6):
    for col in range(4):
        detail("Calculator",(.026,.019,.007),
               (cx-.057+col*.038,cy-.104+row*.029,TOP+.047),
               (.19,.25,.25) if col<3 else (.28,.39,.42))

small=asset("Small meter")
boxpart(small,"body",(.15,.245,.055),(.18,-.285,TOP+.037),BLACK)
boxpart(small,"front",(.125,.214,.009),(.18,-.285,TOP+.068),(.72,.59,.035))
boxpart(small,"display",(.097,.057,.004),(.18,-.219,TOP+.075),(.38,.47,.38))
cylinder(small,"dial",.034,(.18,-.30,TOP+.071),(.18,-.30,TOP+.083),BLACK)
small.turn("z",-14,pivot=(.18,-.285,TOP))

drawers=asset("Parts cabinets")
for cabinet,(x,w,cols) in enumerate([(-.01,.56,4),(.64,.70,5)]):
    boxpart(drawers,f"case_{cabinet}",(w,.19,.48),(x,.745,1.80),(.035,.045,.04))
    for row in range(5):
        for col in range(cols):
            xx=x-w/2+.014+(col+.5)*(w-.028)/cols
            zz=1.59+row*.087
            ww=(w-.040)/cols
            detail("Parts cabinets",(ww,.022,.071),(xx,.638,zz),(.15,.175,.16))
            detail("Parts cabinets",(ww*.87,.012,.008),
                   (xx,.620,zz-.025),(.29,.31,.28))
            detail("Parts cabinets",(ww*.51,.003,.018),
                   (xx,.611,zz-.004),(.66,.67,.58))
            detail("Parts cabinets",(ww*.29,.002,.003),
                   (xx,.608,zz-.004),(.20,.23,.21))

wall=asset("Wall objects")
for i in range(3):
    boxpart(wall,f"paper_{i}",(.30,.004,.25),(-.01+i*.295,.789,1.36),PAPER)
    for j in range(5):
        detail("Wall objects",(.25,.002,.001),
               (-.01+i*.295,.785,1.29+j*.032),(.62,.63,.57))
for i,x in enumerate([-.67,-.53,-.30]):
    z=1.26+(i%2)*.015
    wire("Wall objects",[(x-.012,.75,z+.025),(x-.023,.75,z+.12)],.008,DARK)
    wire("Wall objects",[(x+.012,.75,z+.025),(x+.022,.75,z+.12)],.008,SILVER)
    wire("Wall objects",[(x,.75,z+.04),(x-.027,.746,z-.015),
                        (x-.037,.742,z-.09),(x-.021,.741,z-.105)],.009,RED)
    wire("Wall objects",[(x,.75,z+.04),(x+.025,.746,z-.015),
                        (x+.037,.742,z-.09),(x+.025,.741,z-.105)],.009,RED)

lamp=asset("Bench lamp")
boxpart(lamp,"base",(.17,.14,.038),(.73,.31,TOP+.025),BLACK)
cylinder(lamp,"upright",.013,(.73,.35,TOP+.035),(.76,.45,1.53),BLACK)
cylinder(lamp,"arm",.014,(.76,.45,1.53),(.64,.47,1.59),BLACK)
boxpart(lamp,"shade",(.65,.205,.058),(.30,.42,1.615),(.018,.022,.022))
boxpart(lamp,"end_cap",(.16,.18,.075),(.66,.42,1.604),BLACK)
boxpart(lamp,"diffuser",(.56,.156,.008),(.28,.42,1.582),(.69,.70,.61))
for i in range(3):
    detail("Bench lamp",(.007,.20,.004),(.07+i*.032,.42,1.646),GRAY)
wire("Bench lamp",[(.68,.47,1.59),(.83,.52,1.57),(.86,.47,1.40),
                  (.82,.39,1.14),(.77,.30,.82),(.89,.20,.78)],.005,BLACK)

station=asset("Solder station")
boxpart(station,"base",(.29,.27,.065),(.85,.28,TOP+.039),(.24,.19,.10))
boxpart(station,"top",(.25,.23,.014),(.85,.28,TOP+.079),(.36,.39,.35))
cylinder(station,"iron_handle",.023,(.75,.18,.91),(.85,.31,1.00),(.12,.42,.42))
cylinder(station,"collar",.027,(.845,.305,.995),(.865,.333,1.014),BLACK)
cylinder(station,"shaft",.008,(.75,.18,.91),(.66,.07,.84),SILVER)
for i in range(9):
    yy=.31+i*.013
    zz=.88+i*.016
    pts=[(.85+.049*math.cos(2*math.pi*j/20),
          yy+.025*math.sin(2*math.pi*j/20),
          zz+.040*math.sin(2*math.pi*j/20)) for j in range(21)]
    wire("Solder station",pts,.003,SILVER)
wire("Solder station",[(.86,.32,1.01),(.99,.29,.93),(1.01,.06,.80),
                      (.86,-.08,.785),(.76,-.21,.785)],.006,BLACK)

containers=asset("Containers")
cylinder(containers,"bottle",.055,(.98,.63,TOP),(.98,.63,1.02),(.34,.44,.44))
cylinder(containers,"shoulder",.038,(.98,.63,1.02),(.98,.63,1.07),(.37,.47,.46))
cylinder(containers,"neck",.019,(.98,.63,1.07),(.98,.63,1.13),(.40,.49,.48))
cylinder(containers,"cap",.023,(.98,.63,1.13),(.98,.63,1.155),(.055,.14,.27))
for i in range(2):
    x=.57+i*.11
    cylinder(containers,f"can_{i}",.038,(x,.52,TOP),(x,.52,1.03-i*.04),SILVER)
    cylinder(containers,f"lid_{i}",.031,(x,.52,1.03-i*.04),(x,.52,1.044-i*.04),DARK)
    detail("Containers",(.055,.006,.11),(x,.481,.91),(.58,.61,.50))

clutter=asset("Desktop objects")
for i in range(4):
    p=box((.36,.31,.0015),center=(.57,.10,TOP+.002+i*.002),color=PAPER)
    p.turn("z",-12+i*5)
    clutter.include(f"loose_sheet_{i}",p)
boxpart(clutter,"circuit_board",(.20,.14,.015),(-.65,-.04,TOP+.017),(.035,.15,.32))
for i in range(8):
    x=-.72+(i%4)*.045
    y=-.075+(i//4)*.06
    detail("Desktop objects",(.027,.018,.012),(x,y,TOP+.032),BLACK)
    for j in range(3):
        detail("Desktop objects",(.003,.027,.002),(x-.008+j*.008,y,TOP+.030),SILVER)
cylinder(clutter,"reel",.047,(-.29,-.55,TOP),(-.29,-.55,TOP+.025),(.75,.77,.66))
cylinder(clutter,"reel_core",.021,(-.29,-.55,TOP+.024),(-.29,-.55,TOP+.031),(.17,.40,.35))
cylinder(clutter,"spool",.041,(.59,-.30,TOP),(.59,-.30,TOP+.052),SILVER)
cylinder(clutter,"spool_hole",.016,(.59,-.30,TOP+.051),(.59,-.30,TOP+.054),BLACK)

tools=asset("Foreground tools")
boxpart(tools,"helping_base",(.18,.13,.035),(.87,-.25,TOP+.023),DARK)
cylinder(tools,"post",.010,(.87,-.25,TOP+.04),(.87,-.25,.98),SILVER)
cylinder(tools,"cross_arm",.008,(.73,-.25,.96),(1.00,-.25,.98),SILVER)
for i,x in enumerate([.75,.98]):
    wire("Foreground tools",[(x,-.25,.97),(x-.02,-.30,1.04)],.007,SILVER)
    detail("Foreground tools",(.045,.012,.014),(x-.02,-.31,1.04),SILVER)
cylinder(tools,"magnifier_rim",.072,(1,-.13,.96),(1,-.13,.97),DARK)
cylinder(tools,"magnifier_glass",.059,(1,-.13,.971),(1,-.13,.974),(.34,.40,.37))
for i in range(12):
    detail("Foreground tools",(.052,.024,.0015),
           (.60+random.uniform(-.10,.19),-.49+random.uniform(-.23,.11),TOP+.004),
           (.95,.70,.045),random.uniform(-1.1,1.1))

organizer=asset("Parts organizer")
boxpart(organizer,"case",(.25,.39,.055),(1.02,-.62,TOP+.034),(.10,.23,.38))
boxpart(organizer,"lid",(.245,.38,.012),(1.02,-.62,TOP+.070),(.30,.39,.44))
for i in range(5):
    detail("Parts organizer",(.004,.37,.014),(.92+i*.05,-.62,TOP+.079),(.46,.51,.49))
for i in range(4):
    detail("Parts organizer",(.24,.004,.014),(1.02,-.77+i*.10,TOP+.079),(.46,.51,.49))

cables=asset("Test leads")
for i in range(15):
    cx=random.uniform(-.08,.43)
    cy=random.uniform(-.54,-.19)
    rx=random.uniform(.10,.27)
    ry=random.uniform(.06,.17)
    pts=[]
    for j in range(40):
        t=2*math.pi*j/39
        pts.append((cx+rx*math.cos(t)+.025*math.sin(3*t+i),
                    cy+ry*math.sin(t),TOP+.016+i*.0012+.004*math.sin(2*t)))
    wire("Test leads",pts,.0032,[BLACK,RED,BLACK,RED,(.42,.19,.035)][i%5])
for pts,col,r in [
    ([(.35,.25,.86),(.40,.08,.79),(.51,-.15,.79),(.41,-.44,.795),
      (.20,-.65,.79),(-.06,-.61,.79)],RED,.004),
    ([(.27,.25,.86),(.23,.08,.79),(.36,-.08,.80),(.52,-.30,.80),
      (.38,-.65,.79),(.03,-.72,.79)],BLACK,.004),
    ([(-.26,-.20,.79),(-.36,-.07,.79),(-.15,.07,.79),(-.20,.17,.81),
      (-.36,.15,.87)],BLACK,.005),
    ([(-.91,.11,.80),(-.98,-.17,.79),(-.79,-.30,.80),(-.59,-.27,.83),
      (-.30,-.34,.81),(-.19,-.68,.79),(.25,-.77,.79)],RED,.0035),
    ([(-.43,-.38,.79),(-.50,-.66,.79),(-.33,-.78,.79),(.18,-.79,.79),
      (.54,-.74,.79),(.51,-.55,.80)],BLACK,.004)]:
    wire("Test leads",pts,r,col)
for i,(x,y,ang,col) in enumerate([
    (.14,-.73,-8,BLACK),(.35,-.69,-17,RED),(-.12,-.61,-35,BLACK),
    (.52,-.26,32,(.02,.13,.44)),(.58,-.23,32,RED)]):
    dx=.17*math.cos(math.radians(ang))
    dy=.17*math.sin(math.radians(ang))
    wire("Test leads",[(x,y,TOP+.025),(x+dx,y+dy,TOP+.025)],.010,col)
    wire("Test leads",[(x+dx,y+dy,TOP+.025),(x+dx*1.28,y+dy*1.28,TOP+.025)],.003,SILVER)

# API audit: no fillets; positive box sizes and radii; distinct rod endpoints.
# Indexed sibling inclusion keys are unique. Supports derive from TOP, and
# there are no bind dependencies. Parent references retain include's return.
realize(scene)

materials={}
def material(color):
    color=tuple(color)
    if color not in materials:
        m=bpy.data.materials.new("Finish")
        m.diffuse_color=(*color,1)
        m.use_nodes=True
        bs=m.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value=(*color,1)
        bs.inputs["Roughness"].default_value=.70
        materials[color]=m
    return materials[color]

parents={}
for group in set(k[0] for k in details) | set(c[0] for c in curves):
    p=next((o for o in bpy.data.objects if o.type=="EMPTY" and o.name==group),None)
    if p is None:
        p=bpy.data.objects.new(group+"_details",None)
        bpy.context.collection.objects.link(p)
    parents[group]=p

for (group,color),(verts,faces) in details.items():
    mesh=bpy.data.meshes.new(group+"_detail_mesh")
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(group+"_details",mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material(color))
    obj.parent=parents[group]
    obj.matrix_parent_inverse=parents[group].matrix_world.inverted()

curve_batches={}
for group,pts,r,color in curves:
    curve_batches.setdefault((group,r,color),[]).append(pts)
for (group,r,color),paths in curve_batches.items():
    data=bpy.data.curves.new(group+"_paths","CURVE")
    data.dimensions="3D"
    data.resolution_u=1
    data.bevel_depth=r
    data.bevel_resolution=1
    data.use_fill_caps=True
    for pts in paths:
        spline=data.splines.new("POLY")
        spline.points.add(len(pts)-1)
        for p,co in zip(spline.points,pts):
            p.co=(*co,1)
    obj=bpy.data.objects.new(group+"_leads",data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material(color))
    obj.parent=parents[group]
    obj.matrix_parent_inverse=parents[group].matrix_world.inverted()

# Focal length correction only: preserves perspective directions and parallax,
# enlarges the central instruments, and pushes foreground furniture out of frame.
set_view(position=(.10,-2.92,2.48),target=(0,.10,1.105),
         lens=49,sensor=36,shift=(0,0))

world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new("World")
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.32,.34,.30,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.55
area_emitter(position=(-.35,-1.0,2.9),power=170,size=2.1,target=(0,0,.8))
area_emitter(position=(1.1,-.2,2.1),power=75,size=1.2,target=(.3,.15,.8))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE_NEXT"
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
sc.view_settings.view_transform="Standard"
sc.view_settings.exposure=0
sc.view_settings.gamma=1
# The external runner performs saving and rendering.
