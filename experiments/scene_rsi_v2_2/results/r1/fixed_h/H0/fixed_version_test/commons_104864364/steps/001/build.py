import bpy, math, random
from sceneact import *

random.seed(12)
scene = Scene("School classroom")
cream = (.86,.84,.65)
yellow = (.94,.64,.025)
wood = (.24,.17,.085)
edge = (.34,.26,.13)
dark = (.075,.061,.045)

def add(name, node):
    scene.include(name, node)

def cube(name, size, pos, color):
    add(name, box(size, center=pos, color=color))

# Long schoolroom and raised performance platform.
cube("floor", (9.2,17.4,.14), (0,.3,-.07), (.69,.55,.32))
cube("left wall", (.18,17.4,4.7), (-4.6,.3,2.35), cream)
cube("right wall", (.18,17.4,4.7), (4.6,.3,2.35), cream)
cube("left yellow dado", (.025,17.4,1.12), (-4.495,.3,.56), yellow)
cube("right yellow dado", (.025,17.4,1.12), (4.495,.3,.56), yellow)
cube("rear wall", (9.2,.18,4.7), (0,8.95,2.35), cream)
cube("ceiling", (9.4,17.6,.16), (0,.3,4.75), (.92,.92,.84))
for y in [-5.5,-.8,3.9,8.4]:
    cube("ceiling cross beam "+str(y), (9.2,.23,.32), (0,y,4.53), (.94,.94,.85))
for x in [-2.8,2.8]:
    cube("ceiling longitudinal beam "+str(x), (.16,17.3,.19), (x,.3,4.62), (.94,.94,.85))

# Openings on both sides, with bright glazed upper sections and wooden shutters.
for side in [-1,1]:
    wallx = side*4.475
    for i,y in enumerate([-5.0,-1.6,1.65,4.75,7.25]):
        w = 1.28 if i < 4 else .9
        cube(f"window light {side} {i}", (.035,w,2.46), (wallx,y,2.52), (.91,.96,.88))
        for yy in [y-w/2,y+w/2]:
            cube(f"window jamb {side} {i} {yy}", (.13,.085,2.68), (wallx-side*.04,yy,2.5), (.31,.23,.12))
        for z in [1.18,3.23,3.83]:
            cube(f"window rail {side} {i} {z}", (.13,w+.14,.085), (wallx-side*.045,y,z), (.36,.26,.12))
        cube(f"window middle {side} {i}", (.10,.055,2.55), (wallx-side*.06,y,2.51), (.40,.30,.15))
        # Dark open wooden shutter panels beside each window.
        for j in [-1,1]:
            yy = y+j*(w/2+.19)
            cube(f"shutter {side} {i} {j}", (.12,.32,2.65), (wallx-side*.11,yy,2.49), (.29,.21,.12))
            for dz in [-.87,-.30,.30,.87]:
                cube(f"shutter inset {side} {i} {j} {dz}", (.035,.235,.44),
                     (wallx-side*.185,yy,2.49+dz), (.37,.28,.16))
    # Base skirting
    cube("skirting "+str(side), (.045,17.1,.12), (side*4.48,.3,.06), (.45,.32,.14))

# Dark stage opening and curtains.
cube("stage foundation", (6.6,2.0,.30), (0,7.88,.15), (.43,.30,.13))
cube("stage front edge", (6.75,.15,.15), (0,6.82,.30), (.62,.45,.21))
cube("stage darkness", (6.05,.12,3.12), (0,8.82,1.98), (.055,.038,.027))
for x in [-3.17,3.17]:
    cube("stage green side "+str(x), (.42,.32,3.30), (x,8.13,2.04), (.14,.30,.105))
    cube("stage cream pilaster "+str(x), (.16,.44,3.60), (x*1.10,7.95,2.12), (.89,.85,.61))
for i in range(16):
    x=-2.83+i*.377
    curtain=box((.41,.20,2.80), center=(x,8.66,2.08),
                color=(.105+.025*(i%3),.055,.028))
    add("rear folded curtain "+str(i),curtain)
cube("stage upper fascia", (6.6,.28,.24), (0,8.0,3.72), (.90,.88,.71))
for i in range(19):
    x=-3.03+i*.336
    add("scalloped valance "+str(i), ball(.22,center=(x,7.98,3.48),color=(.91,.88,.72)))
    cube("valance cloth "+str(i),(.34,.12,.32),(x,8.0,3.66),(.91,.88,.72))

# Blackboard on the stage, standing low on an easel.
cube("blackboard outer frame", (2.13,.12,1.17), (.22,7.62,1.40), (.43,.39,.24))
cube("blackboard green face", (2.00,.035,1.04), (.22,7.535,1.40), (.12,.25,.205))
cube("chalk tray",(2.13,.16,.045),(.22,7.48,.86),(.57,.50,.30))
for x in [-.64,1.08]:
    add("blackboard easel "+str(x),rod(.034,start=(x,7.68,.32),end=(x,7.72,2.02),color=(.35,.29,.16)))
add("chalk diagonal",rod(.009,start=(-.60,7.508,1.03),end=(-.28,7.508,1.84),color=(.72,.77,.63)))
cube("stage blue display",(.72,.07,1.3),(2.15,7.75,1.25),(.40,.72,.82))
cube("stage display white center",(.49,.025,1.10),(2.15,7.70,1.25),(.68,.85,.84))

# Traditional wooden desks, with narrow benches behind them.
def desk(name,x,y,width=1.65):
    a=Asset(name)
    a.include("top",box((width,.69,.095),center=(x,y,1.03),color=(.235,.183,.105)))
    a.include("front apron",box((width-.10,.055,.19),center=(x,y+.28,.89),color=(.31,.24,.13)))
    a.include("shelf",box((width-.17,.49,.045),center=(x,y,.73),color=(.25,.19,.10)))
    for xx in [-width/2+.09,width/2-.09]:
        for yy in [-.255,.255]:
            a.include(f"leg {xx} {yy}",box((.065,.065,.96),center=(x+xx,y+yy,.49),color=(.36,.285,.16)))
        a.include("low side rail "+str(xx),box((.055,.54,.055),center=(x+xx,y,.24),color=(.37,.29,.16)))
    add(name,a)
    b=Asset(name+" bench")
    by=y-.73
    b.include("seat",box((width-.05,.29,.065),center=(x,by,.57),color=(.29,.22,.12)))
    for xx in [-width/2+.13,width/2-.13]:
        for yy in [-.095,.095]:
            b.include(f"leg {xx} {yy}",box((.055,.055,.54),center=(x+xx,by+yy,.27),color=(.37,.29,.16)))
    b.include("stretcher",box((width-.2,.045,.05),center=(x,by,.22),color=(.32,.24,.12)))
    add(name+" bench",b)

for r,y in enumerate([-3.15,-1.15,.80,2.55,4.10,5.42]):
    desk("left central desk "+str(r),-1.65,y,1.76 if r<3 else 1.57)
    desk("right central desk "+str(r),1.17,y+.28,1.75 if r<3 else 1.55)
for r,y in enumerate([-1.25,1.05,3.12,4.93]):
    desk("right side desk "+str(r),3.48,y,1.40)
for r,y in enumerate([-2.05,.20,2.30,4.35]):
    desk("left side desk "+str(r),-3.58,y,1.37)
# Extra prominent foreground table at left.
desk("foreground left desk",-1.77,-5.22,1.92)

# Books and loose pale papers.
for i,(x,y,z) in enumerate([(-1.9,-5.22,1.093),(-3.55,-2.05,1.09),
                            (-1.7,.8,1.09),(1.2,2.83,1.09),
                            (3.5,1.05,1.09),(-3.5,2.3,1.09)]):
    cube("exercise book "+str(i),(.43,.30,.025),(x,y,z),(.78,.76,.67))
    cube("book spine "+str(i),(.035,.30,.03),(x-.21,y,z+.006),(.22,.29,.36))
cube("pink book",(.48,.30,.025),(-3.65,.17,1.095),(.74,.26,.37))

# Soft school bags placed beneath and beside desks.
def bag(name,x,y,color,scale=1):
    a=Asset(name)
    a.include("body",fillet_box((.43*scale,.26*scale,.61*scale),radius=.10*scale,
                               center=(x,y,.33*scale),color=color))
    a.include("front pocket",fillet_box((.35*scale,.085*scale,.28*scale),radius=.055*scale,
                                       center=(x,y-.15*scale,.22*scale),
                                       color=tuple(min(1,c*1.18) for c in color)))
    a.include("top handle",sweep_tube(points=[(x-.09*scale,y,.60*scale),
                                             (x-.08*scale,y,.70*scale),
                                             (x+.08*scale,y,.70*scale),
                                             (x+.09*scale,y,.60*scale)],
                                     radius=.018*scale,color=(.025,.035,.04)))
    for s in [-1,1]:
        a.include("strap "+str(s),sweep_tube(points=[(x+s*.15*scale,y+.12*scale,.53*scale),
                                                   (x+s*.26*scale,y+.21*scale,.13*scale),
                                                   (x+s*.23*scale,y+.03*scale,.04)],
                                           radius=.025*scale,color=(.025,.04,.055)))
    add(name,a)

bag("bright blue foreground backpack",1.65,-4.91,(.015,.28,.48),1.20)
bag("black foreground backpack",-2.68,-5.97,(.012,.022,.035),1.05)
bag("bag beneath middle table",.26,-2.49,(.025,.035,.045),.92)
bag("cyan right bag",3.22,-2.11,(.015,.40,.55),1.03)
bag("small distant blue bag",-2.6,1.0,(.025,.30,.51),.8)
bag("far right bag",2.40,3.37,(.025,.25,.38),.75)
add("flat black school bag",fillet_box((.76,.32,.16),radius=.08,
                                      center=(-1.45,-5.65,.13),color=(.014,.02,.023)))

# Wall-mounted black speakers and small framed pictures.
for side,y,z in [(-1,-5.9,3.45),(-1,5.7,3.38),(1,1.1,3.43),(1,6.3,3.35)]:
    speaker=box((.27,.48,.70),center=(side*4.28,y,z),color=(.025,.047,.043))
    speaker.turn('y',-side*12)
    add("speaker "+str(side)+str(y),speaker)
for side in [-1,1]:
    for i,y in enumerate([-3.2,2.7,5.0,7.2]):
        cube(f"picture frame {side} {i}",(.045,.45,.68),(side*4.46,y,3.96),(.39,.31,.13))
        cube(f"picture paper {side} {i}",(.055,.37,.59),(side*4.425,y,3.96),(.85,.85,.70))
        cube(f"picture portrait {side} {i}",(.062,.19,.37),(side*4.39,y,3.96),(.20,.27,.27))

# Suspended three-bladed ceiling fans.
def fan(name,x,y,z,phase):
    add(name+" suspension",rod(.025,start=(x,y,4.60),end=(x,y,z+.08),color=(.22,.20,.15)))
    add(name+" motor",ball(.13,center=(x,y,z),color=(.22,.20,.16)))
    for k in range(3):
        angle=phase+k*120
        rad=math.radians(angle)
        blade=box((.93,.16,.035),center=(x+.50*math.cos(rad),y+.50*math.sin(rad),z+.025),
                  color=(.25,.235,.20))
        blade.turn('z',angle)
        add(name+" blade "+str(k),blade)
fan("front left fan",-2.75,-4.65,4.30,22)
fan("front right fan",2.45,-4.60,4.32,8)
fan("middle left fan",-2.10,.75,4.23,18)
fan("middle right fan",2.38,.85,4.23,40)
fan("back fan",0,5.50,4.18,5)
for x,y in [(-2.0,-2.5),(1.7,3.4)]:
    cube("fluorescent fixture "+str(x),(.12,1.65,.07),(x,y,4.53),(.98,.98,.89))

realize(scene)

# Beige square tiles with fine irregularities and grout.
floor_obj = next((o for o in bpy.context.scene.objects if o.type=='MESH' and 'floor' in o.name.lower()),None)
if floor_obj:
    mat=bpy.data.materials.new("Warm mottled square floor tiles")
    mat.use_nodes=True
    n=mat.node_tree.nodes
    n.clear()
    out=n.new("ShaderNodeOutputMaterial")
    bs=n.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Roughness"].default_value=.76
    tc=n.new("ShaderNodeTexCoord")
    brick=n.new("ShaderNodeTexBrick")
    brick.offset=0
    brick.inputs["Scale"].default_value=1
    brick.inputs["Brick Width"].default_value=.29
    brick.inputs["Row Height"].default_value=.29
    brick.inputs["Mortar Size"].default_value=.006
    brick.inputs["Mortar Smooth"].default_value=.004
    brick.inputs["Color1"].default_value=(.66,.49,.25,1)
    brick.inputs["Color2"].default_value=(.88,.76,.51,1)
    brick.inputs["Mortar"].default_value=(.62,.54,.36,1)
    noise=n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=33
    noise.inputs["Detail"].default_value=2
    bump=n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.12
    bump.inputs["Distance"].default_value=.018
    links=mat.node_tree.links
    links.new(tc.outputs["Object"],brick.inputs["Vector"])
    links.new(tc.outputs["Object"],noise.inputs["Vector"])
    links.new(brick.outputs["Color"],bs.inputs["Base Color"])
    links.new(noise.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    links.new(bs.outputs["BSDF"],out.inputs["Surface"])
    floor_obj.data.materials.clear()
    floor_obj.data.materials.append(mat)

set_view((-.25,-9.05,2.63),(0,5.3,1.95),lens=25.5,sensor=36)
area_emitter((0,-2,4.35),power=1350,size=7,target=(0,1,0),color=(1,.96,.80))
area_emitter((-4.1,-2,3.0),power=1550,size=5,target=(0,1,1),color=(1,.98,.87))
area_emitter((4.05,2,3.2),power=1250,size=5,target=(0,1,1),color=(1,1,.91))
area_emitter((0,6,4.3),power=500,size=4,target=(0,5,0),color=(1,.92,.73))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.76,.80,.78,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.5
sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=340
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.35
