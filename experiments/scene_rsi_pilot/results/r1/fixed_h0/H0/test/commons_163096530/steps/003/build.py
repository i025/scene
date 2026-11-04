from sceneact import *
import bpy, math, random
random.seed(21)
scene=Scene("Historic dormitory")
iron=(.075,.092,.088)
wood=(.20,.105,.043)

def B(n,s,c,col,p=scene):
    a=box(s,center=c,color=col)
    p.include(n,a)
    return a

def R(n,a,b,r=.023,col=iron,p=scene):
    o=rod(radius=r,start=a,end=b,color=col)
    p.include(n,o)
    return o

B("floor foundation",(12,16,.12),(0,0,-.10),(.12,.065,.025))
for i in range(36):
    x=-5+i*.31
    y=-8
    j=0
    while y<5:
        le=min(random.uniform(2,3.8),5-y)
        v=random.uniform(-.025,.045)
        B("board%d_%d"%(i,j),(.303,le-.008,.07),(x,y+le/2,-.025),
          (.205+v,.115+v*.65,.048+v*.35))
        for yy in (y+.07,y+le-.07):
            for xx in (x-.10,x+.10):
                R("nail%d_%d_%s_%s"%(i,j,xx,yy),(xx,yy,.011),(xx,yy,.014),.005,(.075,.06,.04))
        y+=le
        j+=1

B("rear plaster",(10,.18,3.5),(0,4.65,1.71),(.65,.66,.40))
B("left plaster",(.18,13,3.5),(-3.65,-1.7,1.71),(.67,.66,.46))
B("right plaster",(.18,13,3.5),(5,-1.7,1.71),(.64,.65,.40))
B("ceiling",(10,14,.15),(0,-1.7,3.49),(.53,.56,.36))
B("rear skirting",(9,.07,.12),(0,4.51,.06),wood)
for y in (-4.1,-2.25,-.45,1.30,3.15,4.48):
    B("wall upright"+str(y),(.16,.16,3.46),(-3.51,y,1.72),wood)
for z in (1.12,2.37,3.34):
    B("wall beam"+str(z),(.17,13,.145),(-3.49,-1.7,z),wood)
for y in (-2.4,2):
    B("ceiling beam"+str(y),(9,.20,.24),(0,y,3.33),(.135,.073,.027))

B("window reveal",(.04,1.7,1.65),(-3.539,.15,1.76),(.18,.20,.15))
B("window glass",(.045,1.49,1.47),(-3.51,.15,1.77),(.8,.85,.84))
for y in (-.64,.15,.94):
    B("window vertical"+str(y),(.07,.055,1.56),(-3.47,y,1.77),(.67,.69,.60))
for z in (1.02,1.77,2.52):
    B("window horizontal"+str(z),(.07,1.65,.065),(-3.47,.15,z),(.67,.69,.60))
B("sill",(.24,1.83,.075),(-3.42,.15,.98),(.48,.43,.29))

def bunk(name,x0,x1,y0,y1):
    p=Asset(name)
    for x in (x0,x1):
        for y in (y0,y1):
            R("post%s%s"%(x,y),(x,y,.04),(x,y,2.29),.027,iron,p)
            p.include("cap%s%s"%(x,y),ball(.031,center=(x,y,2.29),color=iron))
            R("foot%s%s"%(x,y),(x,y,.02),(x,y,.04),.057,(.25,.26,.22),p)
    for z in (.47,1.64):
        B("base"+str(z),(x1-x0,y1-y0,.06),((x0+x1)/2,(y0+y1)/2,z),(.14,.17,.15),p)
        for y in (y0,y1):
            R("rail%s%s"%(z,y),(x0,y,z+.03),(x1,y,z+.03),.029,iron,p)
            R("lower%s%s"%(z,y),(x0,y,z-.08),(x1,y,z-.08),.018,iron,p)
        p.include("mattress"+str(z),fillet_box((x1-x0-.065,y1-y0-.055,.16),radius=.06,
            center=((x0+x1)/2,(y0+y1)/2,z+.115),color=(.84,.86,.83)))
        B("blue hem"+str(z),(x1-x0-.06,.026,.045),
          ((x0+x1)/2,y0-.015,z+.065),(.25,.38,.59),p)
        p.include("duvet"+str(z),fillet_box((x1-x0-.15,y1-y0-.08,.10),radius=.045,
            center=((x0+x1)/2+.025,(y0+y1)/2,z+.225),color=(.91,.92,.89)))
        p.include("pillow"+str(z),fillet_box((.48,y1-y0-.16,.14),radius=.065,
            center=(x0+.32,(y0+y1)/2,z+.295),color=(.9,.91,.87)))
    for x in (x0,x1):
        for z in (.75,.94,1.95,2.12):
            R("end%s%s"%(x,z),(x,y0,z),(x,y1,z),.021,iron,p)
    for y in (y0,y1):
        for z in (1.98,2.13):
            R("guard%s%s"%(y,z),(x0,y,z),(x1,y,z),.02,iron,p)
    for y in (y0+.09,y0+.47):
        R("ladder"+str(y),(x1+.055,y,.13),(x1+.055,y,1.94),.022,iron,p)
    for z in (.31,.59,.87,1.15,1.43,1.71):
        R("rung"+str(z),(x1+.063,y0+.09,z),(x1+.063,y0+.47,z),.019,(.22,.25,.23),p)
    B("number plate",(.105,.026,.14),(x1,y0-.031,2.21),(.29,.36,.29),p)
    B("number",(.025,.006,.06),(x1,y0-.048,2.21),(.74,.76,.64),p)
    scene.include(name,p)

bunk("front left",-3.38,-.94,-1.12,.0)
bunk("middle left",-3.38,-.94,1.17,2.25)
bunk("rear left",-3.38,-.94,2.89,3.93)
bunk("cropped right",3.38,5.73,-3.55,-2.42)
B("close wooden edge",(.10,.13,3.12),(3.34,-2.54,1.56),(.36,.16,.042))

cx=-.55
cy=4.30
cab=Asset("oak cupboard")
# Open carcass, with a closed left door and a shadowed right compartment.
B("back",(.91,.055,1.90),(cx,cy+.19,1.01),(.22,.115,.037),cab)
for x in (cx-.43,cx+.43):
    B("side"+str(x),(.065,.44,1.90),(x,cy,1.01),(.29,.15,.046),cab)
B("left door",(.40,.065,1.78),(cx-.225,cy-.274,1.06),(.32,.175,.051),cab)
for z,h in ((.58,.67),(1.47,.81)):
    B("door panel"+str(z),(.285,.018,h),(cx-.225,cy-.312,z),(.255,.125,.028),cab)
for x in (cx-.445,cx-.02,cx+.445):
    B("stile"+str(x),(.055,.078,1.90),(x,cy-.27,1.04),(.34,.19,.065),cab)
B("shelf",(.43,.42,.045),(cx+.22,cy-.04,.89),(.35,.20,.065),cab)
B("lower panel",(.37,.035,.67),(cx+.22,cy-.23,.47),(.245,.115,.031),cab)
B("cornice",(1.04,.56,.075),(cx,cy,2),(.32,.18,.055),cab)
B("cornice top",(1.10,.59,.035),(cx,cy,2.052),(.36,.22,.08),cab)
B("bottom",(.99,.51,.075),(cx,cy,.10),(.28,.14,.033),cab)
for x in (cx-.36,cx+.36):
    B("foot"+str(x),(.12,.34,.12),(x,cy,.055),(.19,.085,.02),cab)
R("pull",(cx-.07,cy-.322,.99),(cx-.07,cy-.35,.99),.024,(.07,.065,.035),cab)
R("hanging rail",(cx+.05,cy-.09,1.83),(cx+.40,cy-.09,1.83),.013,(.19,.19,.14),cab)
for k in range(4):
    xx=cx+.09+k*.075
    R("hanger a"+str(k),(xx,cy-.11,1.78),(xx-.05,cy-.11,1.67),.007,(.11,.10,.06),cab)
    R("hanger b"+str(k),(xx-.05,cy-.11,1.67),(xx+.06,cy-.11,1.67),.007,(.11,.10,.06),cab)
scene.include("cupboard",cab)
R("wall clock",(-.40,4.535,2.50),(-.40,4.49,2.50),.115,(.43,.52,.43))
R("clock face",(-.40,4.485,2.50),(-.40,4.476,2.50),.095,(.57,.64,.53))
R("hand",(-.40,4.465,2.50),(-.40,4.465,2.56),.004,(.25,.30,.25))

fx=1.48
B("hearth slab",(2.04,.90,.065),(fx,4.12,.025),(.20,.19,.145))
B("dark firebox",(1.45,.055,1.20),(fx,4.535,.65),(.045,.039,.025))
for row in range(9):
    for col in range(6):
        x=fx-.64+col*.235+(row%2)*.115
        if x>fx+.66:
            continue
        v=random.uniform(-.025,.025)
        B("brick%d_%d"%(row,col),(.219,.06,.100),(x,4.483,.12+row*.115),
          (.13+v,.112+v,.073+v))
for side in (-1,1):
    for j in range(4):
        v=random.uniform(-.025,.025)
        B("jamb%d_%d"%(side,j),(.29,.36,.285),(fx+side*.86,4.34,.16+j*.285),
          (.34+v,.33+v,.245+v))
for k in range(9):
    off=-.84+k*.21
    top=1.48+.055*(1-(off/.93)**2)
    bottom=1.19+.10*(1-(off/.93)**2)
    v=random.uniform(-.025,.025)
    B("lintel"+str(k),(.207,.37,top-bottom),(fx+off,4.34,(top+bottom)/2),
      (.37+v,.355+v,.27+v))
for side in (-1,1):
    R("inner rim"+str(side),(fx+side*.67,4.105,.09),(fx+side*.67,4.105,1.12),
      .018,(.13,.12,.08))
for k in range(8):
    R("grate"+str(k),(fx-.48+k*.13,4.19,.09),(fx-.48+k*.13,4.19,.28),
      .012,(.065,.06,.04))
R("grate rail",(fx-.56,4.18,.14),(fx+.52,4.18,.14),.019,(.08,.07,.045))
for k in range(9):
    xx=fx+.38+k*.031
    R("fireguard slat"+str(k),(xx,4.055,.11),(xx-.09,4.10,.57),.009,(.58,.63,.57))
R("fireguard top",(fx+.29,4.10,.57),(fx+.57,4.10,.57),.016,(.63,.66,.60))
R("fireguard bottom",(fx+.38,4.055,.11),(fx+.66,4.055,.11),.012,(.44,.48,.42))
R("coal bucket",(fx+1.16,4.06,.02),(fx+1.16,4.06,.26),.105,(.065,.08,.065))
R("poker",(fx+1.05,4.17,.04),(fx+1.05,4.17,.65),.011,(.07,.08,.055))
B("wall plate",(.055,.025,.12),(fx+1.04,4.54,1.46),(.25,.27,.19))

realize(scene)
for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    col=tuple(bs.inputs["Base Color"].default_value)
    bs.inputs["Roughness"].default_value=.78
    if col[0]<.11 and col[1]<.12:
        bs.inputs["Metallic"].default_value=.65
        bs.inputs["Roughness"].default_value=.32
    noise=nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=35
    noise.inputs["Detail"].default_value=3
    bump=nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.12
    bump.inputs["Distance"].default_value=.012
    nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if .12<col[0]<.42 and col[0]>col[1]*1.3:
        coord=nt.nodes.new("ShaderNodeTexCoord")
        mapping=nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation="MULTIPLY"
        mapping.inputs[1].default_value=(7,.24,4)
        nt.links.new(coord.outputs["Generated"],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],noise.inputs["Vector"])
        noise.inputs["Scale"].default_value=5
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.15
        ramp.color_ramp.elements[0].color=(col[0]*.45,col[1]*.45,col[2]*.45,1)
        ramp.color_ramp.elements[1].position=.85
        ramp.color_ramp.elements[1].color=(col[0]*1.23,col[1]*1.23,col[2]*1.23,1)
        nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])

set_view((3.25,-6.65,1.80),(-.36,2.70,1.18),lens=43,sensor=36,shift=(-.077,0))
area_emitter((-3.13,-.10,2.17),power=740,size=2.4,target=(0,1,.7),color=(.91,.95,1))
area_emitter((.3,-3.2,3.1),power=95,size=4,target=(0,2,1),color=(1,.92,.76))
area_emitter((1.1,3.4,3.17),power=65,size=2.2,target=(0,2,0),color=(1,.94,.78))
sc=bpy.context.scene
world=bpy.data.worlds.new("Ambient")
sc.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.45,.51,.59,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.16
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=0
