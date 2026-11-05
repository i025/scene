from sceneact import *
import bpy, math

scene = Scene("Train vestibule")
C = {
    "wall": (.57,.58,.55), "right": (.43,.47,.48),
    "steel": (.52,.56,.57), "dark": (.075,.095,.10),
    "orange": (.94,.34,.025), "yellow": (1,.55,.005),
    "blue": (.08,.27,.39)
}

def add(name, obj):
    scene.include(name, obj)
    return obj

def bx(name, size, center, color, radius=0):
    # Thin panels need rounded corners in their broad plane.
    # Construct those explicitly so the radius never exceeds the
    # thickness limit imposed by fillet_box.
    if radius <= 0:
        return add(name, box(size, center=center, color=color))
    if radius <= min(size) / 2:
        return add(name, fillet_box(size, radius, center=center, color=color))
    thin = min(range(3), key=lambda i: size[i])
    axes = [i for i in range(3) if i != thin]
    a, b = axes
    r = min(radius, size[a]*.499, size[b]*.499)
    pieces = []
    s = list(size)
    s[a] -= 2*r
    pieces.append(box(tuple(s), center=center, color=color))
    s = list(size)
    s[b] -= 2*r
    pieces.append(box(tuple(s), center=center, color=color))
    for sa in (-1,1):
        for sb in (-1,1):
            p = list(center)
            p[a] += sa*(size[a]/2-r)
            p[b] += sb*(size[b]/2-r)
            q = list(p)
            p[thin] -= size[thin]/2
            q[thin] += size[thin]/2
            pieces.append(rod(r, start=tuple(p), end=tuple(q), color=color))
    return add(name, assemble(pieces, name=name))

def tube(name, points, radius=.018, color=None):
    return add(name, sweep_tube(points=points, radius=radius,
                               color=color or C["steel"]))

def line(name, a, b, radius=.015, color=None):
    return add(name, rod(radius, start=a, end=b, color=color or C["steel"]))

def loop(name, xmin, xmax, zmin, zmax, y, r=.10, thickness=.019, color=None):
    pts=[]
    for cx,cz,start in [
        (xmax-r,zmax-r,0), (xmin+r,zmax-r,90),
        (xmin+r,zmin+r,180), (xmax-r,zmin+r,270)
    ]:
        for i in range(9):
            t=math.radians(start+i*90/8)
            pts.append((cx+r*math.cos(t), y, cz+r*math.sin(t)))
    pts.append(pts[0])
    return tube(name, pts, thickness, color)

# Architecture.
bx("floor",(6,7,.10),(-.9,.1,-.055),(.045,.052,.051))
bx("back left panel",(1.30,.12,2.98),(-2.20,2.77,1.49),C["wall"])
bx("back right panel",(.62,.12,2.98),(.35,2.77,1.49),C["wall"])
bx("back window sill",(1.62,.12,1.20),(-.76,2.77,.60),C["wall"])
bx("back window header",(1.62,.12,.48),(-.76,2.77,2.76),C["wall"])
bx("right wall",(.13,5.7,3.0),(.73,.0,1.50),C["right"])
bx("ceiling",(4.5,6,.12),(-1.35,.2,3.02),(.48,.49,.46))
line("back horizontal seam",(-2.8,2.695,2.95),(.65,2.695,2.95),
     .006,(.24,.26,.25))
bx("corner post",(.105,.13,2.92),(.65,2.64,1.46),(.40,.43,.43),.018)
bx("right rear panel seam",(.008,.014,2.8),(.654,1.95,1.43),(.30,.34,.35))
bx("right forward seam",(.012,.018,2.95),(.653,-1.05,1.48),(.23,.27,.28))

# Rounded end-wall window.
bx("window rubber",(1.65,.075,1.36),(-.76,2.675,1.86),(.055,.07,.075),.16)
bx("window aluminium lip",(1.575,.04,1.285),(-.76,2.626,1.86),(.67,.70,.69),.135)
bx("window inner gasket",(1.525,.035,1.235),(-.76,2.600,1.86),(.12,.15,.16),.12)
bx("window daylight",(1.465,.025,1.175),(-.76,2.575,1.86),(.89,.95,.96),.105)
bx("outside white vehicle",(.58,.012,.50),(-.36,2.553,1.54),(.63,.72,.74),.055)
bx("outside dark window",(.51,.008,.28),(-.35,2.543,1.60),(.39,.51,.55),.025)
for i in range(7):
    line("outside mullion "+str(i),(-.585+i*.077,2.531,1.47),
         (-.585+i*.077,2.531,1.73),.0035,(.63,.72,.74))
bx("outside red marking",(.26,.008,.035),(-.37,2.526,1.40),(.76,.32,.29))
bx("outside lower white",(.60,.009,.12),(-.35,2.527,1.31),(.79,.82,.81))
bx("outside left upright",(.045,.012,.89),(-1.40,2.54,1.83),(.67,.73,.74))
line("outside overhead line",(-1.43,2.53,2.26),(-.72,2.53,2.23),
     .008,(.47,.56,.58))
line("glass glint",(-1.36,2.51,2.36),(-.73,2.51,1.83),
     .010,(.96,.98,.98))

# Horizontal yellow handrail.
for x in [-1.80,.23]:
    bx("yellow mounting plate "+str(x),(.065,.025,.15),
       (x,2.62,1.56),C["yellow"],.018)
    line("yellow mounting peg "+str(x),(x,2.63,1.56),
         (x,2.45,1.56),.026,C["yellow"])
line("window grab rail",(-1.84,2.44,1.56),(.27,2.44,1.56),.023,C["yellow"])

# Stainless kick panel.
bx("back kick plate",(3.35,.065,.39),(-1.02,2.62,.235),(.49,.53,.53),.012)
bx("kickplate upper lip",(3.35,.09,.035),(-1.02,2.58,.445),(.66,.69,.68))
bx("kickplate lower lip",(3.35,.07,.035),(-1.02,2.57,.045),(.23,.27,.27))
for group, center in enumerate([-1.63,-.14]):
    for row in range(5):
        for col in range(13):
            x=center+(col-6)*.030+(row%2)*.013
            z=.12+row*.028
            bx("vent %s %s %s"%(group,row,col),(.012,.009,.009),
               (x,2.579,z),(.08,.11,.11),.003)
for x in [-2.48,-1.65,.42]:
    add("plate screw "+str(x),
        ball(.011,center=(x,2.57,.425),color=(.25,.28,.28)))

# Folded metal fittings above and below the window.
loop("upper rack outer",-1.08,.48,2.61,2.91,2.47,.13,.024,(.18,.21,.21))
line("upper rack inner rail",(-.94,2.43,2.73),(.34,2.43,2.73),
     .022,(.27,.30,.30))
line("upper rack silver rail",(-.92,2.45,2.86),(.33,2.45,2.86),
     .015,(.55,.58,.56))
for i,x in enumerate([-.83,-.27,.22]):
    tube("upper support "+str(i),[
        (x-.07,2.46,2.68),(x-.07,2.43,2.89),
        (x-.04,2.44,2.96),(x+.055,2.49,2.97),
        (x+.09,2.57,2.91)],.023,(.24,.27,.26))
loop("lower rack outer",-1.00,.28,.68,.94,2.43,.11,.022,(.25,.29,.29))
line("lower rack crossbar",(-.94,2.40,.85),(.24,2.40,.85),
     .018,(.57,.61,.61))
for i,x in enumerate([-.86,-.38,.08]):
    bx("rack attachment "+str(i),(.15,.045,.20),
       (x,2.60,.81),(.32,.36,.36),.018)
    tube("rack bent clip "+str(i),[
        (x-.06,2.47,.92),(x-.065,2.35,.91),
        (x-.06,2.34,.72),(x-.035,2.39,.62),
        (x+.035,2.48,.61),(x+.06,2.53,.67),
        (x+.05,2.53,.79)],.018,(.39,.43,.44))

# Orange folding seat on the side wall.
bx("fold seat metal backing",(.095,.87,1.30),(.57,.84,1.45),
   (.39,.42,.41),.055)
bx("orange upright folding cushion",(.13,.84,1.30),(.485,.82,1.47),
   C["orange"],.065)
bx("fold seat darker edge",(.085,.055,1.20),(.505,.39,1.47),
   (.72,.245,.018),.018)
for y in [.49,1.14]:
    tube("fold seat leg "+str(y),[
        (.49,y,1.00),(.46,y,.70),(.42,y,.60),
        (.42,y,.055),(.34,y,.04)],.026,(.48,.53,.54))
    bx("fold seat foot "+str(y),(.16,.12,.025),(.40,y,.025),
       (.43,.48,.49),.012)
tube("seat lower cross frame",[
    (.43,.48,.49),(.43,.48,.58),(.43,.57,.64),
    (.43,1.05,.64),(.43,1.14,.57),(.43,1.14,.49)],
    .023,(.37,.42,.43))
bx("fold release black handle",(.075,.13,.13),(.40,.40,1.19),
   (.035,.045,.045),.022)
tube("fold release cable",[
    (.405,.42,1.15),(.405,.39,.94),(.43,.43,.88)],.011,(.07,.08,.08))
line("right wall support bar",(.63,.73,1.78),(.63,1.48,1.78),
     .027,(.23,.27,.28))
line("support bracket",(.62,1.45,1.78),(.47,1.45,1.78),
     .023,(.31,.35,.36))

# Left-hand seats and dividers.
bx("left seat shell",(.11,1.40,1.58),(-1.46,.77,1.20),(.62,.66,.65),.075)
bx("left orange partition",(.12,1.37,1.52),(-1.385,.78,1.24),
   (.90,.32,.025),.070)
bx("left partition edge",(.045,1.35,1.48),(-1.305,.78,1.24),
   (.98,.40,.045),.035)
for i,y in enumerate([1.28,1.67]):
    bx("adjacent orange seat "+str(i),(.115,.29,1.24),(-1.50,y,1.13),
       (.91,.34,.03),.07)
    bx("adjacent grey shell "+str(i),(.08,.33,1.30),(-1.58,y,1.13),
       (.46,.50,.49),.05)
bx("front seat cushion",(1.22,.78,.20),(-1.28,-.79,.34),
   (.99,.40,.025),.10)
bx("front seat back",(.17,.73,1.18),(-1.83,-.75,.86),
   (.93,.34,.018),.085)
bx("front cushion grey base",(1.18,.72,.09),(-1.28,-.77,.21),
   (.32,.36,.36),.035)
bx("left upper handgrip pedestal",(.16,.14,.48),(-1.38,.20,1.89),
   (.29,.33,.34),.07)
tube("left yellow hand loop",[
    (-1.35,.18,1.89),(-1.35,.18,2.23),
    (-1.35,.24,2.31),(-1.35,.36,2.30),
    (-1.35,.40,2.23),(-1.35,.40,1.97),
    (-1.35,.34,1.91),(-1.35,.18,1.89)],.025,C["yellow"])
line("left seat support",(-1.36,1.32,.50),(-1.36,1.32,.04),
     .026,(.41,.45,.45))

# Left wall, window and overhead luggage shelf.
bx("left side wall",(.12,5.6,3.0),(-2.35,.05,1.50),(.55,.56,.52))
bx("left window black surround",(.045,1.60,1.62),(-2.27,1.03,1.85),
   (.06,.075,.075),.10)
bx("left window light",(.025,1.46,1.47),(-2.24,1.03,1.85),
   (.85,.92,.93),.08)
bx("luggage shelf",(.92,1.85,.065),(-1.91,1.58,2.75),(.18,.20,.19))
bx("shelf front fascia",(.06,1.90,.21),(-1.44,1.58,2.81),
   (.28,.30,.28),.012)
for j in range(12):
    y=.72+j*.15
    line("luggage shelf slat "+str(j),(-2.32,y,2.80),(-1.47,y,2.80),
         .018,(.50,.52,.48))
line("shelf bracket",(-1.46,2.46,2.74),(-1.46,2.46,2.98),
     .022,(.34,.36,.33))

# Cropped right doorway.
bx("right doorway upright",(.12,.10,3.02),(.68,-1.19,1.51),
   (.65,.69,.69),.015)
bx("right door glass",(.045,.55,1.75),(.67,-1.48,1.80),(.21,.29,.31))
tube("door yellow vertical handle",[
    (.53,-1.28,1.03),(.49,-1.31,1.03),
    (.45,-1.31,1.09),(.45,-1.31,1.71),
    (.49,-1.31,1.77),(.56,-1.28,1.77)],.025,C["yellow"])
bx("right ceiling channel",(.24,4.5,.17),(.59,.4,2.93),
   (.29,.33,.34),.018)

# Instruction plates and simple pictograms.
def back_sign(name,x,z,w,h):
    bx(name,(w,.014,h),(x,2.596,z),(.84,.86,.80),.004)
    for dx in [-w/2+.008,w/2-.008]:
        line(name+" border "+str(dx),
             (x+dx,2.582,z-h/2+.005),(x+dx,2.582,z+h/2-.005),
             .003,C["blue"])

back_sign("upper instruction sign",-1.27,2.80,.20,.37)
back_sign("small accessible sign",.30,2.10,.13,.15)
for z in [2.72,2.87]:
    for x in [-1.31,-1.23]:
        pts=[(x+.026*math.cos(t*math.pi/10),2.574,
              z+.026*math.sin(t*math.pi/10)) for t in range(21)]
        tube("instruction wheel "+str(x)+str(z),pts,.003,C["blue"])
    line("instruction symbol "+str(z),(-1.31,2.574,z),
         (-1.25,2.574,z+.065),.003,C["blue"])
    line("instruction bar "+str(z),(-1.25,2.574,z+.065),
         (-1.22,2.574,z),.003,C["blue"])
bx("green exit label",(.25,.018,.105),(-2.08,2.58,2.09),(.12,.35,.22))
line("exit arrow",(-2.16,2.564,2.09),(-2.00,2.564,2.09),
     .006,(.87,.91,.78))
line("exit arrow tip",(-2.16,2.564,2.09),(-2.11,2.564,2.12),
     .006,(.87,.91,.78))
bx("right instruction sticker",(.013,.20,.22),(.652,.02,1.91),
   (.84,.87,.83))
for yy in [-.045,.045]:
    for zz in [1.87,1.95]:
        bx("right sticker icon "+str(yy)+str(zz),(.016,.060,.050),
           (.641,yy,zz),C["blue"],.005)
# Small wheelchair symbol on the end wall.
tube("accessible wheel",[
    (.30+.027*math.cos(t*math.pi/10),2.573,
     2.085+.027*math.sin(t*math.pi/10)) for t in range(21)],
    .003,C["blue"])
add("accessible head",ball(.009,center=(.29,2.573,2.143),color=C["blue"]))
tube("accessible seated figure",[
    (.29,2.573,2.129),(.29,2.573,2.098),
    (.319,2.573,2.098),(.334,2.573,2.071)],.004,C["blue"])

realize(scene)

# Surface finishes.
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat is None:
            continue
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if bs is None:
            continue
        bs.inputs["Roughness"].default_value=.55
        name=obj.name.lower()
        if any(s in name for s in ["rail","rack","leg","steel","plate","shelf slat"]):
            bs.inputs["Metallic"].default_value=.60
            bs.inputs["Roughness"].default_value=.32
        if "orange" in name or "cushion" in name:
            bs.inputs["Roughness"].default_value=.66
        if "daylight" in name or "left window light" in name:
            bs.inputs["Emission Color"].default_value=(.78,.87,.90,1)
            bs.inputs["Emission Strength"].default_value=.55
        if name == "floor":
            nodes=mat.node_tree.nodes
            noise=nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value=180
            noise.inputs["Detail"].default_value=2
            ramp=nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].color=(.016,.021,.021,1)
            ramp.color_ramp.elements[1].color=(.095,.105,.103,1)
            mat.node_tree.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
            mat.node_tree.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
            bump=nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value=.16
            bump.inputs["Distance"].default_value=.008
            mat.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
            mat.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

set_view((0,-1.70,1.50),(0,2.70,1.26),lens=26,sensor=36)
area_emitter((-1.0,1.8,2.75),power=270,size=2.3,
             target=(-.4,.0,.8),color=(.91,.96,1))
area_emitter((-2.0,-1.1,2.6),power=190,size=2.4,
             target=(.2,1.8,1.2),color=(1,.94,.83))
area_emitter((-.8,2.4,2.0),power=100,size=1.4,
             target=(.0,-1,1.0),color=(.85,.94,1))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.53,.59,.63,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.33
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=.25
