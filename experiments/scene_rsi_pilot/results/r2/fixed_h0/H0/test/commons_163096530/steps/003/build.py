from sceneact import *
import bpy, math, random

random.seed(19)
scene = Scene('Historic dormitory')
iron = (.045, .057, .053)
oak = (.095, .052, .020)
stone = (.32, .305, .245)

def B(parent, name, size, center, color):
    parent.include(name, box(size, center=center, color=color))

def R(parent, name, radius, start, end, color=iron):
    parent.include(name, rod(radius, start=start, end=end, color=color))

# Dark, wide, individually jointed wooden boards.
floor = Asset('Worn oak floor')
for i in range(30):
    x = -3.6 + i*.245
    y = -6.0
    j = 0
    while y < 4.25:
        length = min(random.uniform(1.6, 3.5), 4.25-y)
        v = random.uniform(.80, 1.30)
        B(floor, f'board{i}_{j}', (.239, length-.009, .085),
          (x, y+length/2, -.047), (.135*v, .076*v, .032*v))
        for k in range(4):
            B(floor, f'grain{i}_{j}_{k}',
              (random.uniform(.001, .003), length*random.uniform(.3,.95), .001),
              (x+random.uniform(-.10,.10), y+length/2, -.003),
              (.047*v, .027*v, .012*v))
        for k, yy in enumerate((y+.045, y+length-.045)):
            for side in (-1,1):
                R(floor, f'nail{i}_{j}_{k}_{side}', .005,
                  (x+side*.078,yy,-.002), (x+side*.078,yy,.001),
                  (.025,.023,.018))
        y += length
        j += 1
scene.include('floor', floor)

B(scene,'back plaster',(7.2,.16,3.35),(0,4.32,1.65),(.65,.66,.37))
B(scene,'left plaster',(.15,10.8,3.35),(-3.6,-1,1.65),(.64,.64,.43))
B(scene,'ceiling',(7.3,10.8,.12),(0,-1,3.36),(.47,.51,.32))

frame = Asset('Exposed dark timber')
for j,y in enumerate((-4.1,-2.55,-.85,.8,2.45,4.18)):
    B(frame,f'vertical{j}',(.16,.145,3.31),(-3.48,y,1.66),oak)
for j,z in enumerate((.12,1.05,2.38,3.23)):
    B(frame,f'horizontal{j}',(.17,10.8,.145),(-3.47,-1,z),oak)
B(frame,'ceiling edge',(.20,10.8,.18),(-3.4,-1,3.26),oak)
B(frame,'main ceiling beam',(.22,10.8,.23),(.38,-1,3.27),(.065,.041,.017))
scene.include('timber framing',frame)

def bunk(name,y,x0=-3.37,x1=-.72,width=.94):
    a=Asset(name)
    ya,yb=y-width/2,y+width/2
    for i,x in enumerate((x0,x1)):
        for j,yy in enumerate((ya,yb)):
            R(a,f'post{i}{j}',.025,(x,yy,.045),(x,yy,2.24))
            a.include(f'cap{i}{j}',ball(.030,center=(x,yy,2.24),color=iron))
            B(a,f'foot{i}{j}',(.085,.085,.019),(x,yy,.025),(.15,.16,.14))
    for level,z in enumerate((.43,1.66)):
        B(a,f'base{level}',(x1-x0+.035,width,.065),((x0+x1)/2,y,z),iron)
        a.include(f'mattress{level}',fillet_box(
            (x1-x0-.045,width-.05,.15),radius=.055,
            center=((x0+x1)/2,y,z+.10),color=(.76,.79,.76)))
        B(a,f'blue ticking{level}',(x1-x0-.035,width-.04,.045),
          ((x0+x1)/2,y,z+.035),(.16,.27,.40))
        a.include(f'sheet{level}',fillet_box(
            (x1-x0-.10,width-.065,.075),radius=.033,
            center=((x0+x1)/2-.01,y,z+.19),color=(.88,.90,.87)))
        a.include(f'pillow{level}',fillet_box(
            (.50,width*.74,.13),radius=.06,
            center=(x0+.35,y,z+.28),color=(.91,.92,.88)))
        a.include(f'folded duvet{level}',fillet_box(
            (.72,width-.05,.065),radius=.025,
            center=(x1-.45,y,z+.245),color=(.83,.85,.81)))
        for side,yy in enumerate((ya,yb)):
            R(a,f'bed edge{level}_{side}',.022,(x0,yy,z),(x1,yy,z))
        for end,x in enumerate((x0,x1)):
            for k,h in enumerate((z+.33,z+.53)):
                R(a,f'end rail{level}_{end}_{k}',.017,(x,ya,h),(x,yb,h))
            if level:
                B(a,f'end panel{end}',(.030,width-.09,.14),
                  (x,y,z+.36),(.075,.09,.075))
        if level:
            for side,yy in enumerate((ya,yb)):
                R(a,f'guard{side}',.017,(x0,yy,z+.42),(x1,yy,z+.42))
    for j,yy in enumerate((y-.29,y+.29)):
        R(a,f'ladder side{j}',.020,(x1+.055,yy,.12),(x1+.055,yy,1.98))
    for k in range(6):
        z=.35+k*.285
        R(a,f'rung{k}',.016,(x1+.06,y-.29,z),(x1+.06,y+.29,z))
    return a

scene.include('nearest bunk',bunk('Nearest iron bunk',-.55))
scene.include('middle bunk',bunk('Middle iron bunk',1.30))
scene.include('back bunk',bunk('Back iron bunk',2.90))

cab=Asset('Old wooden locker')
cx,cy,cw=-.18,4.01,1.08
for i,x in enumerate((cx-cw/2+.055,cx+cw/2-.055)):
    B(cab,f'side{i}',(.085,.51,1.79),(x,cy,1.04),(.255,.127,.037))
    for j,yy in enumerate((cy-.18,cy+.18)):
        B(cab,f'leg{i}_{j}',(.09,.09,.16),(x,yy,.13),(.18,.081,.020))
B(cab,'back',(cw,.045,1.78),(cx,cy+.23,1.05),(.115,.055,.015))
B(cab,'top cornice',(cw+.14,.60,.075),(cx,cy,1.97),(.30,.16,.051))
B(cab,'cornice rim',(cw+.19,.62,.035),(cx,cy,2.015),(.25,.12,.029))
B(cab,'bottom',(cw,.55,.09),(cx,cy,.22),(.26,.123,.030))
B(cab,'middle stile',(.065,.53,1.74),(cx,cy,1.08),(.29,.145,.040))
B(cab,'closed door',(.465,.055,1.64),(cx-.265,cy-.275,1.08),(.32,.17,.057))
for j,z in enumerate((.64,1.48)):
    B(cab,f'panel{j}',(.34,.018,.64),(cx-.265,cy-.31,z),(.265,.125,.031))
    for k,x in enumerate((cx-.465,cx-.065)):
        B(cab,f'frame{j}_{k}',(.035,.025,.69),(x,cy-.326,z),(.35,.185,.060))
B(cab,'door rail',(.45,.035,.07),(cx-.265,cy-.33,1.06),(.34,.17,.049))
cab.include('handle',ball(.021,center=(cx-.085,cy-.365,1.02),color=(.08,.065,.025)))
B(cab,'open shelf',(.47,.49,.055),(cx+.265,cy,1.04),(.30,.145,.036))
R(cab,'clothes rail',.013,(cx+.075,cy,1.83),(cx+.46,cy,1.83),(.13,.10,.055))
for j in range(4):
    x=cx+.13+j*.075
    R(cab,f'hanger{j}',.008,(x,cy,1.86),(x,cy-.035,1.69),(.12,.10,.06))
    B(cab,f'coat{j}',(.08,.17,.43),(x,cy+.04,1.51),
      (.035+j*.012,.030+j*.010,.019+j*.007))
scene.include('locker',cab)

# Substantial stone surround with a shallow curved inner opening.
fire=Asset('Stone fireplace')
fx=1.83
B(fire,'dark firebox',(1.31,.04,1.27),(fx,4.20,.69),(.025,.022,.015))
for row in range(9):
    for col in range(5):
        x=fx-.58+col*.27+(row%2)*.105
        if x<fx+.62:
            v=random.uniform(.045,.12)
            B(fire,f'brick{row}_{col}',(.245,.055,.116),
              (x,4.155,.12+row*.133),(v,v*.83,v*.60))
B(fire,'left stone jamb',(.29,.31,1.26),(fx-.78,4.09,.66),stone)
B(fire,'right stone jamb',(.29,.31,1.26),(fx+.78,4.09,.66),stone)
B(fire,'stone lintel',(1.86,.35,.30),(fx,4.08,1.47),(.39,.38,.30))
B(fire,'top stone edge',(1.96,.38,.075),(fx,4.07,1.625),(.40,.39,.31))
for i in range(13):
    t=math.pi*(i+.5)/13
    x=fx+.65*math.cos(t)
    z=1.18+.20*math.sin(t)
    block=box((.17,.12,.12),center=(x,3.90,z),color=(.30,.29,.23))
    slope=math.atan2(.20*math.cos(t),-.65*math.sin(t))
    block.turn('y',-math.degrees(slope))
    fire.include(f'arch stone{i}',block)
for side in (-1,1):
    B(fire,f'inner edge{side}',(.075,.11,1.09),(fx+side*.65,3.91,.63),(.36,.34,.26))
    for j,z in enumerate((.32,.73,1.13)):
        B(fire,f'joint{side}_{j}',(.285,.012,.009),(fx+side*.78,3.925,z),(.22,.21,.17))
B(fire,'hearth',(2.02,.78,.055),(fx,3.89,.025),(.15,.145,.11))
B(fire,'hearth front',(1.76,.23,.045),(fx,3.59,.035),(.23,.21,.16))
scene.include('fireplace',fire)

guard=Asset('Pale leaning fire guard')
for i in range(9):
    x=2.25+i*.027
    R(guard,f'bar{i}',.009,(x,3.79,.10),(x-.075,3.88,.64),(.64,.67,.61))
R(guard,'top',.016,(2.175,3.88,.64),(2.40,3.88,.64),(.64,.67,.61))
R(guard,'bottom',.013,(2.25,3.79,.10),(2.475,3.79,.10),(.47,.50,.45))
scene.include('fire guard',guard)
R(scene,'coal bucket',.105,(2.91,3.91,.025),(2.91,3.91,.29),(.035,.037,.029))
R(scene,'poker',.011,(2.73,3.93,.04),(2.70,3.96,.77),(.045,.04,.025))

R(scene,'clock rim',.125,(-.15,4.205,2.48),(-.15,4.16,2.48),(.35,.43,.36))
R(scene,'clock face',.109,(-.15,4.155,2.48),(-.15,4.148,2.48),(.47,.55,.44))
R(scene,'hour hand',.004,(-.15,4.135,2.48),(-.177,4.135,2.516),(.20,.24,.19))
R(scene,'minute hand',.003,(-.15,4.132,2.48),(-.15,4.132,2.55),(.20,.24,.19))

right=Asset('Foreground cropped bunk')
dx=.36
for j,y in enumerate((-3.1,-.8)):
    for i,x in enumerate((3.0+dx,3.96+dx)):
        R(right,f'post{i}_{j}',.035,(x,y,.02),(x,y,2.75))
        right.include(f'cap{i}_{j}',ball(.039,center=(x,y,2.75),color=iron))
for k,z in enumerate((.50,1.81)):
    B(right,f'base{k}',(.95,2.3,.07),(3.48+dx,-1.95,z),iron)
    B(right,f'mattress{k}',(.9,2.22,.17),(3.48+dx,-1.95,z+.11),(.83,.85,.81))
    for j,y in enumerate((-3.1,-.8)):
        for hi,h in enumerate((z+.31,z+.49)):
            R(right,f'end{k}_{j}_{hi}',.019,(3+dx,y,h),(3.96+dx,y,h))
    R(right,f'side{k}',.021,(3+dx,-3.1,z+.45),(3+dx,-.8,z+.45))
B(right,'wood end post',(.105,.095,2.60),(2.94+dx,-.81,1.32),(.36,.16,.035))
for i,y in enumerate((-2.89,-2.34)):
    R(right,f'ladder{i}',.024,(2.96+dx,y,.14),(2.96+dx,y,2.68))
for j in range(9):
    z=.27+j*.29
    R(right,f'rung{j}',.019,(2.96+dx,-2.89,z),(2.96+dx,-2.34,z))
scene.include('right foreground bunk',right)

for j,y in enumerate((-.55,1.30,2.90)):
    B(scene,f'wall lamp{j}',(.09,.14,.25),(-3.37,y,2.36),(.13,.18,.13))
    B(scene,f'lamp glass{j}',(.018,.095,.13),(-3.311,y,2.385),(.48,.57,.46))

# Small surface flakes on the old plaster ceiling.
for j in range(25):
    x=random.uniform(-3.1,.2)
    y=random.uniform(-1.8,3.7)
    B(scene,f'ceiling flake{j}',(random.uniform(.03,.12),random.uniform(.025,.10),.006),
      (x,y,3.293),(.56,.58,.39))

realize(scene)

# Procedural grain and gentle surface roughness.
seen=set()
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':
        continue
    for mat in obj.data.materials:
        if mat is None or mat.name in seen:
            continue
        seen.add(mat.name)
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs is None:
            continue
        bs.inputs['Roughness'].default_value=.77
        base=bs.inputs['Base Color'].default_value
        if base[0]<.07 and base[1]<.08:
            bs.inputs['Metallic'].default_value=.55
            bs.inputs['Roughness'].default_value=.36
        elif base[0]>.07 and base[0]>base[1]*1.35:
            nodes=mat.node_tree.nodes
            links=mat.node_tree.links
            tex=nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=4
            tex.inputs['Detail'].default_value=3
            coord=nodes.new('ShaderNodeTexCoord')
            mapping=nodes.new('ShaderNodeVectorMath')
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(65,2,9)
            links.new(coord.outputs['Generated'],mapping.inputs[0])
            links.new(mapping.outputs[0],tex.inputs['Vector'])
            ramp=nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.18
            ramp.color_ramp.elements[0].color=(base[0]*.52,base[1]*.52,base[2]*.52,1)
            ramp.color_ramp.elements[1].position=.82
            ramp.color_ramp.elements[1].color=(base[0]*1.18,base[1]*1.18,base[2]*1.18,1)
            links.new(tex.outputs['Fac'],ramp.inputs[0])
            links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
            bump=nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.13
            bump.inputs['Distance'].default_value=.016
            links.new(tex.outputs['Fac'],bump.inputs['Height'])
            links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view((3.28,-6.55,2.04),(-.59,2.32,1.20),lens=39.0)
area_emitter((-2.6,-3.0,2.75),power=850,size=3.0,
             target=(-.5,2.0,.65),color=(1,.96,.84))
area_emitter((1.7,-1.0,2.9),power=100,size=3.0,
             target=(-1.0,3.0,1.3),color=(.83,.89,1))

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.43,.47,.35,1)
bg.inputs['Strength'].default_value=.22
sc.render.engine='CYCLES'
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.10
sc.render.image_settings.file_format='PNG'
