from sceneact import *
import bpy
import math
import random

random.seed(8)
scene = Scene("Shipboard sleeping compartment")

cream = (.57, .56, .43)
wall = (.64, .65, .53)
ivory = (.74, .75, .65)
ochre = (.47, .32, .17)
redfloor = (.28, .105, .065)
iron = (.055, .065, .059)
linen = (.61, .65, .59)
navy = (.055, .115, .125)
gray = (.35, .39, .36)

def cube(name, size, center, color):
    node = box(size, center=center, color=color)
    scene.include(name, node)
    return node

def pipe(name, a, b, radius=.025, color=iron):
    node = rod(radius, start=a, end=b, color=color)
    scene.include(name, node)
    return node

def sphere(name, center, radius, color, scale=None):
    node = ball(radius, center=center, color=color)
    if scale:
        node.resize(scale)
    scene.include(name, node)
    return node

# Painted steel shell.
cube("red painted deck", (4.65, 11.8, .13), (0, 2.25, -.085), redfloor)
cube("port bulkhead", (.14, 11.6, 3.32), (-2.12, 2.25, 1.61), wall)
cube("starboard bulkhead", (.14, 11.6, 3.32), (2.12, 2.25, 1.61), wall)
cube("aft bulkhead", (4.3, .15, 3.35), (0, 7.3, 1.62), wall)
cube("overhead", (4.5, 11.8, .16), (0, 2.25, 3.28), (.38, .36, .27))
cube("port red skirting", (.035, 11.5, .25), (-2.025, 2.2, .115), (.25, .12, .075))
cube("aft skirting", (4.2, .035, .24), (0, 7.2, .11), (.27, .13, .08))

for y in [-2.8, -.9, 1.05, 3.0, 4.95, 6.9]:
    cube("deck transverse joint", (4.1, .009, .006), (0, y, -.014), (.17, .075, .045))
for x in [-1.45, -.55, .4, 1.35]:
    cube("deck longitudinal joint", (.007, 11.4, .005), (x, 2.2, -.013), (.23, .09, .052))

# Exposed overhead structure, diagonals, and service lines.
for y in [-2.1, -.3, 1.6, 3.6, 5.6, 7.0]:
    cube("ceiling transverse beam", (4.15, .13, .22), (0, y, 3.08), ochre)
for x in [-1.7, -.85, .05, 1.05, 1.85]:
    cube("ceiling longitudinal rib", (.085, 11.5, .19), (x, 2.2, 3.11), (.43, .32, .20))
for y in [-1.9, .1, 2.2]:
    pipe("ceiling diagonal brace", (-1.7, y, 2.79), (-1.02, y+.75, 3.16), .042, (.56,.43,.28))

pipe("large port overhead pipe", (-1.8,-3.3,2.73), (-1.8,6.9,2.73), .064, ivory)
pipe("parallel overhead pipe", (-1.36,-2.6,2.92), (-1.36,6.9,2.92), .042, (.57,.60,.51))
pipe("dark starboard overhead pipe", (1.45,-3,3.02), (1.45,7.1,3.02), .08, iron)
for y in [-1.5, .0, 1.8, 3.8, 5.8]:
    pipe("pipe suspension", (-1.8,y,2.73), (-1.8,y,3.19), .016, gray)
    pipe("pipe coupling", (-1.8,y-.045,2.73), (-1.8,y+.045,2.73), .079, (.50,.53,.45))

# Foreground support, ochre above and oxblood below.
px, py = .94, .18
pipe("pillar lower red", (px,py,.03), (px,py,1.53), .112, (.29,.105,.057))
pipe("pillar upper cream", (px,py,1.53), (px,py,3.22), .112, (.64,.53,.33))
pipe("pillar foot ring", (px,py,.015), (px,py,.065), .14, (.43,.23,.12))
pipe("pillar upper collar", (px,py,3.02), (px,py,3.12), .145, ochre)

# Right return bulkhead, with its dark red lower band.
cube("right partition", (1.28,.13,3.13), (1.52,2.10,1.55), (.70,.70,.58))
cube("right partition base", (1.28,.022,.32), (1.52,2.022,.16), (.29,.13,.085))
cube("chalkboard surround", (.68,.045,.78), (1.34,2.014,2.05), (.37,.36,.29))
cube("chalkboard", (.62,.014,.71), (1.34,1.984,2.05), (.20,.25,.23))
for i in range(8):
    x=1.12+random.random()*.39
    z=1.83+random.random()*.38
    pipe("faint chalk scuff", (x,1.974,z), (x+.09,1.974,z+.015), .002, (.34,.38,.33))
cube("posted notice", (.32,.014,.60), (1.94,2.014,1.71), (.79,.79,.69))
for j in range(10):
    cube("notice printing", (.23,.003,.008), (1.94,2.003,1.92-j*.035), (.45,.46,.40))

# Red wall-mounted emergency apparatus.
cube("fire appliance mounting plate", (.32,.065,.54), (1.22,1.955,1.17), (.69,.055,.026))
sphere("rounded red appliance head", (1.22,1.91,1.43), .16, (.74,.075,.035), (1,.40,.85))
cube("red appliance body", (.235,.13,.38), (1.22,1.89,1.19), (.77,.065,.025))
pipe("fire handle left", (1.16,1.803,1.39), (1.16,1.803,1.50), .018, ivory)
pipe("fire handle right", (1.26,1.803,1.39), (1.26,1.803,1.50), .018, ivory)
pipe("fire handle cross", (1.16,1.803,1.50), (1.26,1.803,1.50), .018, ivory)
cube("fire appliance label", (.10,.008,.085), (1.22,1.818,1.17), (.25,.19,.12))

# Three-tier port sleeping rack.
rack = Asset("three tier steel bunks")
xleft, xright = -1.97, -.65
yfront, yback = 1.20, 4.36
for x in [xleft,xright]:
    for y in [yfront,yback]:
        rack.include("upright %.2f %.2f"%(x,y), rod(.025,start=(x,y,.05),end=(x,y,2.64),color=iron))
for tier,z in enumerate([.45,1.04,1.66]):
    for x in [xleft,xright]:
        rack.include("side rail %s %s"%(tier,x),rod(.022,start=(x,yfront,z-.055),end=(x,yback,z-.055),color=iron))
    for y in [yfront,yback]:
        rack.include("end rail %s %s"%(tier,y),rod(.024,start=(xleft,y,z-.055),end=(xright,y,z-.055),color=iron))
    rack.include("canvas base %s"%tier,box((1.28,3.08,.055),center=(-1.31,2.78,z-.025),color=(.34,.38,.33)))
    rack.include("mattress %s"%tier,fillet_box((1.24,3.01,.11),radius=.045,center=(-1.31,2.78,z+.055),color=linen))
    rack.include("pillow %s"%tier,fillet_box((.84,.46,.13),radius=.06,center=(-1.32,4.00,z+.16),color=(.73,.75,.67)))
    for k in range(6):
        yy=1.5+k*.43
        rack.include("mattress piping %s %s"%(tier,k),rod(.006,start=(-.681,yy,z+.025),end=(-.681,yy+.19,z+.035),color=(.40,.44,.39)))
scene.include("sleeping rack",rack)
pipe("rack upper longitudinal frame",(-.65,1.20,2.62),(-.65,4.36,2.62),.027,iron)
pipe("rack upper crosspiece",(-1.97,1.20,2.62),(-.65,1.20,2.62),.025,iron)
cube("hanging dark coat",(.22,.30,.82),(-.79,4.12,1.72),(.055,.080,.081))
sphere("coat shoulder",(-.78,4.12,2.10),.17,(.07,.09,.085),(1,.8,.5))

# Near-left ventilation cabinets.
for index, yy in enumerate([-.67,.02,.71]):
    cube("blue machinery cabinet",(.48,.59,1.05),(-1.80,yy,.78),navy)
    cube("cabinet top lip",(.54,.64,.055),(-1.80,yy,1.32),(.10,.14,.14))
    cube("cabinet facing panel",(.022,.49,.88),(-1.546,yy,.78),(.065,.12,.13))
    for k in range(19):
        cube("cabinet vent slat",(.027,.37,.012),(-1.530,yy,.39+k*.041),(.29,.35,.33))
    pipe("cabinet vertical trim",(-1.512,yy-.24,.34),(-1.512,yy-.24,1.21),.011,(.12,.18,.17))
cube("machinery support shelf",(.74,2.34,.09),(-1.74,.03,.20),(.07,.11,.095))
for yy in [-1.02,1.02]:
    pipe("shelf leg",(-1.43,yy,.03),(-1.43,yy,.21),.032,iron)

# Wall heater and small fittings on port bulkhead.
cube("cream wall heater",(.25,.63,.78),(-1.905,.16,2.10),(.63,.64,.54))
cube("heater dark opening",(.022,.49,.52),(-1.766,.16,2.10),(.075,.105,.09))
for z in [1.88,1.98,2.08,2.18,2.28]:
    cube("heater grille",(.035,.52,.033),(-1.747,.16,z),(.60,.61,.51))
cube("heater upper badge",(.025,.20,.055),(-1.746,.16,2.40),(.33,.34,.28))
pipe("wall heater conduit",(-1.99,.18,1.68),(-1.99,.18,1.29),.022,gray)
sphere("wall valve",(-1.98,.72,1.42),.09,(.22,.25,.21),(.4,1,1))

# Rear bank of metal lockers.
for idx,x in enumerate([-.51,.05,.61]):
    cube("rear locker",(.54,.54,1.88),(x,5.52,1.09),(.43,.47,.43))
    cube("locker door",(.49,.035,1.77),(x,5.228,1.10),(.48,.51,.46))
    for z in [1.73,1.80,1.87,1.94]:
        cube("locker upper vent",(.28,.012,.013),(x,5.204,z),(.25,.29,.26))
    for z in [.33,.40,.47]:
        cube("locker lower vent",(.28,.012,.013),(x,5.204,z),(.28,.32,.28))
    cube("locker latch",(.035,.034,.15),(x+.17,5.192,1.11),(.17,.20,.18))
    cube("locker label frame",(.14,.013,.064),(x,5.196,1.59),(.68,.68,.57))
    for z in [.38,1.66]:
        cube("door hinge",(.035,.03,.09),(x-.235,5.20,z),(.29,.32,.29))
    sphere("stowed bedding",(x,5.5,2.09),.23,(.54,.55,.44),(1,.8,.48))

# Rear equipment and black pipe framework.
for x in [.96,1.28]:
    pipe("vertical rear service pipe",(x,4.71,.10),(x,4.71,3.04),.031,iron)
pipe("upper pipe crossover",(.96,4.71,3.04),(-.91,4.71,3.04),.033,iron)
pipe("lower equipment pipe",(.96,4.71,1.05),(1.71,4.71,1.05),.025,iron)
cube("rear equipment housing",(.77,.65,.93),(.69,4.37,.51),(.24,.26,.23))
cube("equipment top",(.86,.73,.065),(.69,4.37,1.00),(.34,.35,.30))
cube("equipment front inset",(.57,.018,.66),(.69,4.032,.52),(.28,.30,.26))
for x in [.34,1.04]:
    pipe("equipment corner frame",(x,4.01,.07),(x,4.01,.98),.022,(.16,.18,.16))
sphere("rear brass valve",(.99,4.67,1.18),.065,(.47,.40,.21))

# A pale metal chair in the aisle.
cx,cy=-.19,3.77
cube("chair seat",(.47,.45,.07),(cx,cy,.48),(.48,.47,.35))
for x in [cx-.20,cx+.20]:
    for y in [cy-.18,cy+.18]:
        pipe("chair leg",(x,y,.035),(x,y,.47),.022,(.54,.54,.42))
    pipe("chair back upright",(x,cy+.18,.44),(x,cy+.25,1.05),.023,(.57,.57,.44))
cube("chair backrest",(.44,.065,.24),(cx,cy+.238,.91),(.40,.42,.34))
pipe("chair left arm",(cx-.245,cy-.13,.68),(cx-.245,cy+.20,.72),.023,(.60,.59,.46))
pipe("chair right arm",(cx+.245,cy-.13,.68),(cx+.245,cy+.20,.72),.023,(.60,.59,.46))
for x in [cx-.245,cx+.245]:
    pipe("arm support",(x,cy-.13,.48),(x,cy-.13,.68),.019,(.54,.54,.42))

# Foreground right bench, cropped by the photograph.
cube("right bench seat",(.59,2.14,.075),(1.63,-1.01,.47),(.035,.105,.079))
for yy in [-1.92,-.13]:
    for xx in [1.40,1.86]:
        pipe("bench leg",(xx,yy,.015),(xx,yy,.44),.027,iron)
pipe("bench stretcher",(1.64,-1.92,.18),(1.64,-.13,.18),.022,iron)
cube("right foreground door jamb",(.17,.20,3.18),(2.02,-1.38,1.57),(.31,.16,.085))

# Hanging lamps, progressively smaller with distance.
lamp_positions=[(-.61,-.64,2.73),(-.40,2.85,2.75),(.02,5.22,2.78)]
for i,(x,y,z) in enumerate(lamp_positions):
    pipe("lamp suspension",(x,y,z+.12),(x,y,3.22),.019,(.12,.14,.12))
    sphere("lamp dark shade",(x,y,z),.235,(.22,.25,.22),(1,1,.35))
    pipe("lamp upper neck",(x,y,z+.015),(x,y,z+.17),.047,(.24,.26,.22))
    sphere("lamp luminous underside",(x,y,z-.051),.215,(1.0,.99,.87),(1,1,.10))

realize(scene)

# Mildly worn painted metal and a reflective reddish deck.
for material in bpy.data.materials:
    material.use_nodes=True
    bsdf=material.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    c=bsdf.inputs["Base Color"].default_value
    bsdf.inputs["Roughness"].default_value=.68
    if c[0]>.95 and c[1]>.9:
        bsdf.inputs["Emission Color"].default_value=(1,.98,.85,1)
        bsdf.inputs["Emission Strength"].default_value=5
    if abs(c[0]-redfloor[0])<.015 and abs(c[1]-redfloor[1])<.015:
        bsdf.inputs["Roughness"].default_value=.29
        noise=material.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=95
        noise.inputs["Detail"].default_value=2
        bump=material.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.13
        bump.inputs["Distance"].default_value=.015
        material.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        material.node_tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])

set_view(position=(.10,-3.72,1.63),target=(-.10,3.40,1.66),lens=27.5,sensor=36)
area_emitter((-.61,-.64,2.60),power=145,size=.48,target=(-.7,.1,.0),color=(1,.93,.77))
area_emitter((-.4,2.85,2.62),power=120,size=.40,target=(-.4,3,.1),color=(.88,.96,1))
area_emitter((.02,5.22,2.66),power=90,size=.36,target=(0,5.4,.4),color=(1,.97,.85))
area_emitter((.4,-2.5,2.6),power=110,size=3,target=(0,2,1),color=(1,.86,.68))
area_emitter((-1.6,3.5,2.55),power=55,size=1.8,target=(-.3,3.7,1.2),color=(.85,.91,1))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.22,.24,.20,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.22
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.25
sc.render.image_settings.file_format="PNG"
