from sceneact import *
import bpy, math, random
random.seed(8)

# Approximate reference / step-2 landmarks:
# large wheel center (.67,.25) / (.67,.25); anvil (.42,.40) / (.43,.44);
# bin (.69,.90) / (.73,.90); small wheel (.36,.28) / (.32,.22).
# Framing and foreground cropping are substantially improved.
# Largest remaining broad error: pale machinery and timber merge together.
# Revision family: regional surface colors, keeping camera and lighting fixed.
# Darker iron and timber should recover the reference's dark machine silhouettes
# and shadowed bench strip without moving landmarks.
# Preserve bright window regions and the lower-left floor's open coverage.
# Solid regions: bench slabs/aprons, anvil, drawer walls.
# Open regions: flywheels, drawer mouth, bins, spaces below benches.
# Assemblies and inferred dimensions remain unchanged; fine proportions uncertain.

scene = Scene('Historic metalworking shop')
wood = (.105,.075,.038)
edgewood = (.075,.055,.029)
iron = (.042,.048,.043)
worniron = (.105,.12,.11)
rust = (.17,.105,.050)
lightwood = (.25,.185,.105)
plaster = (.52,.55,.49)

WALL_Y = 1.52
BENCH_Z = 1.02
CAMERA = (4.5,-3.8,3.5)
TARGET = (-.35,.45,.95)
LENS = 39

def B(parent,name,size,pos,col):
    parent.include(name,box(size,center=pos,color=col))

def R(parent,name,a,b,radius=.025,col=iron):
    parent.include(name,rod(radius,start=a,end=b,color=col))

def S(parent,name,p,radius,col):
    parent.include(name,ball(radius,center=p,color=col))

room = Asset('Architecture')
B(room,'plank_floor',(17,9,.12),(-2,-2,-.07),(.43,.35,.24))
B(room,'old_plaster_wall',(16,.20,4.5),(-2,WALL_Y,2.1),plaster)
B(room,'wall_base',(16,.09,.18),(-2,1.37,.14),(.30,.31,.25))
scene.include('architecture',room)

for i,x in enumerate([-6.5,-4.1,-1.7,.7]):
    win = Asset('Window_%d'%i)
    B(win,'dark_recess',(2.04,.07,2.35),(x,1.395,2.77),(.20,.24,.23))
    B(win,'daylight_glass',(1.88,.035,2.20),(x,1.34,2.78),(.82,.88,.88))
    for j,xx in enumerate([x-1,x,x+1]):
        B(win,'vertical_%d'%j,(.065,.10,2.35),(xx,1.28,2.77),(.30,.33,.30))
    for j,z in enumerate([1.62,2.68,3.94]):
        B(win,'crossbar_%d'%j,(2.08,.12,.065),(x,1.27,z),(.32,.34,.29))
    B(win,'stone_sill',(2.27,.39,.12),(x,1.27,1.58),(.36,.37,.31))
    scene.include('window_%d'%i,win)

def bench(name,x,length,depth=1.13):
    a = Asset(name)
    B(a,'thick_top',(length,depth,.17),(x,.53,BENCH_Z),wood)
    B(a,'front_edge',(length,.10,.20),(x,-.04,BENCH_Z-.025),lightwood)
    B(a,'front_apron',(length,.11,.37),(x,.015,.75),edgewood)
    B(a,'back_apron',(length,.10,.29),(x,1.01,.78),edgewood)
    for k,xx in enumerate([x-length/2+.17,x+length/2-.17]):
        for j,yy in enumerate([.10,.94]):
            B(a,'leg_%d_%d'%(k,j),(.16,.17,.90),(xx,yy,.45),wood)
        B(a,'foot_%d'%k,(.36,.96,.11),(xx,.54,.07),edgewood)
    B(a,'low_stretcher',(length-.15,.13,.13),(x,.80,.25),edgewood)
    return a

scene.include('foreground_bench',bench('Foreground lathe bench',1.55,3.38))
scene.include('middle_bench',bench('Anvil and lathe bench',-1.75,2.95))
scene.include('far_bench',bench('Distant workbench',-4.7,2.75))
scene.include('last_bench',bench('Back workshop bench',-6.7,1.1))

def ring(parent,name,center,radius,tube=.025,col=iron,segments=20):
    x,y,z = center
    for k in range(segments):
        a = 2*math.pi*k/segments
        b = 2*math.pi*(k+1)/segments
        R(parent,name+'_rim_%d'%k,
          (x,y+radius*math.cos(a),z+radius*math.sin(a)),
          (x,y+radius*math.cos(b),z+radius*math.sin(b)),tube,col)

def wheel(parent,name,center,radius):
    x,y,z = center
    ring(parent,name,center,radius,.034,worniron)
    ring(parent,name+'_inner',(x+.025,y,z),radius*.86,.015,iron,16)
    R(parent,name+'_hub',(x-.09,y,z),(x+.11,y,z),radius*.15,worniron)
    for k in range(5):
        a = k*2*math.pi/5+.2
        p = (x,y+radius*.16*math.cos(a),z+radius*.16*math.sin(a))
        q = (x,y+radius*.56*math.cos(a+.35),z+radius*.56*math.sin(a+.35))
        t = (x,y+radius*.93*math.cos(a+.16),z+radius*.93*math.sin(a+.16))
        R(parent,name+'_spoke_a%d'%k,p,q,.034,iron)
        R(parent,name+'_spoke_b%d'%k,q,t,.030,iron)

def lathe(name,x,length,scale=1,wheel_radius=.48):
    a = Asset(name)
    z = BENCH_Z+.20
    for j,y in enumerate([.27,.64]):
        B(a,'bed_rail_%d'%j,(length,.115,.12),(x,y,z),worniron)
    for j,xx in enumerate([x-length*.38,x+length*.36]):
        B(a,'mount_foot_%d'%j,(.39,.65,.07),(xx,.45,BENCH_Z+.12),iron)
        B(a,'upright_%d'%j,(.19,.30,.42*scale),(xx,.48,z+.20*scale),iron)
    spindle_z = z+.38*scale
    head = x-length*.31
    tail = x+length*.35
    B(a,'headstock_body',(.43,.47,.29),(head,.47,spindle_z-.035),iron)
    R(a,'headstock_bearing',(head-.29,.47,spindle_z),
      (head+.28,.47,spindle_z),.13*scale,worniron)
    R(a,'main_spindle',(head-.42,.47,spindle_z),
      (tail+.32,.47,spindle_z),.045,worniron)
    for j,(dx,rr) in enumerate([(-.36,.17),(-.25,.13),(-.14,.105)]):
        R(a,'stepped_pulley_%d'%j,(head+dx-.04,.47,spindle_z),
          (head+dx+.04,.47,spindle_z),rr*scale,iron)
    B(a,'tailstock',(.37,.31,.22),(tail,.47,spindle_z-.06),iron)
    R(a,'tail_bearing',(tail-.20,.47,spindle_z),
      (tail+.23,.47,spindle_z),.09,worniron)
    R(a,'wood_handle',(tail+.25,.47,spindle_z),
      (tail+.64,.47,spindle_z),.06,lightwood)
    R(a,'tail_lock',(tail,.46,spindle_z+.06),(tail,.46,spindle_z+.24),.022,iron)
    R(a,'lock_cross',(tail-.10,.46,spindle_z+.24),
      (tail+.12,.46,spindle_z+.24),.023,iron)
    B(a,'carriage',(.44,.52,.10),(x+.1,.43,z+.12),worniron)
    R(a,'toolrest_stem',(x+.03,.17,z+.15),(x+.03,.17,z+.43),.036,iron)
    R(a,'toolrest',(x-.19,.17,z+.43),(x+.25,.17,z+.43),.032,worniron)
    wx = head-.20
    wz = spindle_z+.68*scale
    B(a,'flywheel_standard',(.14,.18,.88*scale),(wx,.89,wz-.43*scale),iron)
    R(a,'upper_axle',(wx-.13,.89,wz),(wx+.17,.89,wz),.05,worniron)
    wheel(a,'open_flywheel',(wx,.89,wz),wheel_radius)
    R(a,'belt_left',(wx,.89-wheel_radius*.83,wz-.13),
      (head-.27,.37,spindle_z),.014,(.16,.13,.08))
    R(a,'belt_right',(wx,.89+wheel_radius*.83,wz-.13),
      (head-.27,.57,spindle_z),.014,(.16,.13,.08))
    return a

scene.include('main_lathe',lathe('Large antique lathe',1.61,2.48,1,.51))
scene.include('middle_lathe',lathe('Small antique lathe',-2.50,1.52,.67,.32))
scene.include('distant_lathe',lathe('Distant lathe',-5.15,1.42,.52,.25))

anvil = Asset('Central anvil and stump')
B(anvil,'stump',(.53,.54,.89),(-.77,.12,.47),wood)
B(anvil,'base',(.76,.47,.14),(-.77,.12,1.16),rust)
B(anvil,'waist',(.38,.32,.35),(-.77,.12,1.38),rust)
B(anvil,'shoulders',(.68,.42,.21),(-.77,.12,1.57),rust)
B(anvil,'flat_face',(.77,.43,.10),(-.80,.12,1.70),(.26,.21,.13))
for j in range(5):
    xx = -.39+j*.12
    rr = .19*(1-j/5)+.018
    R(anvil,'tapered_horn_%d'%j,(xx,.12,1.62),(xx+.14,.12,1.62),rr,rust)
scene.include('anvil',anvil)

drawer = Asset('Open foreground drawer')
B(drawer,'bottom',(.91,.65,.07),(1.15,-.40,.60),(.09,.075,.042))
B(drawer,'front',(.99,.10,.31),(1.15,-.75,.73),(.105,.10,.060))
for j,x in enumerate([.68,1.62]):
    B(drawer,'side_%d'%j,(.06,.65,.29),(x,-.40,.72),(.16,.14,.08))
R(drawer,'handle',(1.04,-.817,.75),(1.27,-.817,.75),.025,iron)
for j in range(4):
    B(drawer,'contents_%d'%j,(.53,.07,.045),(1.13,-.56+j*.12,.66),(.43,.40,.28))
scene.include('open_drawer',drawer)

vice = Asset('Bench vice')
B(vice,'fixed_jaw',(.35,.18,.24),(.04,-.10,1.15),iron)
B(vice,'moving_jaw',(.34,.16,.23),(.04,-.35,1.14),worniron)
B(vice,'body',(.22,.32,.32),(.04,-.12,.94),iron)
R(vice,'screw',(.04,-.55,1.10),(.04,.05,1.10),.045,worniron)
R(vice,'sliding_handle',(.04,-.58,.70),(.04,-.58,1.24),.023,worniron)
S(vice,'handle_end',(.04,-.58,.70),.039,iron)
scene.include('front_vice',vice)

tools = Asset('Tools and workpieces')
for j in range(9):
    x = .31+j*.145
    y = .03+random.uniform(.02,.22)
    R(tools,'steel_tool_%d'%j,(x,y,1.16),(x-.22,y+.27,1.18),.015,worniron)
    R(tools,'tool_handle_%d'%j,(x-.22,y+.27,1.18),
      (x-.31,y+.37,1.18),.029,lightwood)
for j,(x,y) in enumerate([(1.70,.04),(2.52,.25),(-2.6,.05),(-3.6,.5)]):
    paper = box((.39,.29,.008),center=(x,y,1.115),color=(.69,.67,.57))
    paper.turn('z',-12+j*9)
    tools.include('paper_%d'%j,paper)
for j in range(5):
    B(tools,'wood_offcut_%d'%j,(.51,.075,.045),
      (-2.35,.15+j*.10,1.15+j*.026),lightwood)
for j in range(7):
    x = -5.9+j*.49
    R(tools,'rear_tool_%d'%j,(x,.43,1.15),(x+.12,.65,1.39),.024,iron)
scene.include('bench_tools',tools)

def bucket(name,c,r,h,color):
    a = Asset(name)
    x,y,z = c
    for k in range(12):
        t = 2*math.pi*k/12
        panel = box((2*r*math.sin(math.pi/12)*1.04,.045,h),
                    center=(x+r*math.cos(t),y+r*math.sin(t),z+h/2),
                    color=color)
        panel.turn('z',math.degrees(t)+90)
        a.include('wall_%d'%k,panel)
    R(a,'dark_bottom',(x,y,z+.015),(x,y,z+.045),r*.92,(.13,.14,.11))
    return a

scene.include('foreground_bin',
              bucket('Open cream metal bin',(1.96,-.12,0),.36,.63,(.47,.46,.34)))
B(scene,'bin_wood_block',(.38,.32,.19),(1.95,-.10,.57),(.29,.26,.17))
scene.include('green_barrel',
              bucket('Cropped green barrel',(3.06,.64,0),.47,.89,(.18,.26,.19)))
R(scene,'barrel_lid',(3.06,.64,.87),(3.06,.64,.92),.46,(.25,.28,.19))
scene.include('under_bench_pail',
              bucket('Small dark pail',(-3.30,.38,0),.23,.47,(.22,.25,.20)))

clutter = Asset('Sill objects and hanging tools')
for j,x in enumerate([-6.2,-5.6,-4.6,-4.0,-3.1,-2.7,-1.4,-.9,.45]):
    h = random.uniform(.12,.27)
    R(clutter,'can_%d'%j,(x,1.19,1.65),(x,1.19,1.65+h),.045,(.36,.37,.33))
    R(clutter,'can_tool_%d'%j,(x,1.19,1.72),(x+.045,1.17,1.97+h),.012,iron)
for j,x in enumerate([-6.0,-3.25,-.25,2.45,3.15]):
    R(clutter,'hanging_shaft_%d'%j,(x,1.32,1.75),(x+.12,1.32,3.35),.023,rust)
    if j%2 == 0:
        R(clutter,'tool_cross_%d'%j,(x-.08,1.32,2.92),
          (x+.27,1.32,2.92),.025,iron)
R(clutter,'diagonal_long_pole',(2.58,1.20,1.08),
  (3.27,1.20,3.69),.037,(.26,.18,.11))
scene.include('sill_clutter',clutter)

# Audit: positive dimensions/radii, nonzero rods, unique include keys.
# All semantic assemblies remain separate; no decorative geometry added.
realize(scene)

def descendants(name):
    p = bpy.data.objects.get(name)
    return [o for o in p.children_recursive if o.type=='MESH'] if p else []

def texture_material(mat,kind):
    mat.use_nodes = True
    nt = mat.node_tree
    bs = nt.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value = .82
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 9 if kind=='wall' else 5
    tex.inputs['Detail'].default_value = 3
    coord = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (2,35,7) if kind=='wood' else (2,2,2)
    nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
    nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    base = bs.inputs['Base Color'].default_value[:3]
    ramp.color_ramp.elements[0].position = .18
    ramp.color_ramp.elements[0].color = (*[v*.65 for v in base],1)
    ramp.color_ramp.elements[1].position = .82
    ramp.color_ramp.elements[1].color = (*[min(v*1.2,1) for v in base],1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
    nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .25
    bump.inputs['Distance'].default_value = .025
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

for mat in list(bpy.data.materials):
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value = .76

for ob in descendants('architecture'):
    if ob.dimensions.x>15 and ob.dimensions.z<.2:
        mat = ob.data.materials[0].copy()
        ob.data.materials[0] = mat
        texture_material(mat,'wood')
        nt = mat.node_tree
        bs = nt.nodes.get('Principled BSDF')
        coord = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(coord.outputs['Object'],sep.inputs[0])
        mul = nt.nodes.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = 5.2
        nt.links.new(sep.outputs['Y'],mul.inputs[0])
        fract = nt.nodes.new('ShaderNodeMath')
        fract.operation = 'FRACT'
        nt.links.new(mul.outputs[0],fract.inputs[0])
        seam = nt.nodes.new('ShaderNodeMath')
        seam.operation = 'LESS_THAN'
        seam.inputs[1].default_value = .025
        nt.links.new(fract.outputs[0],seam.inputs[0])
        old = bs.inputs['Base Color'].links[0].from_socket
        mix = nt.nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MIX'
        mix.inputs[2].default_value = (.15,.115,.075,1)
        nt.links.new(old,mix.inputs[1])
        nt.links.new(seam.outputs[0],mix.inputs[0])
        nt.links.new(mix.outputs[0],bs.inputs['Base Color'])

for name,kind in [('foreground_bench','wood'),('middle_bench','wood'),
                  ('far_bench','wood'),('architecture','wall')]:
    for ob in descendants(name):
        if name=='architecture' and ob.dimensions.z<1:
            continue
        if ob.data.materials:
            m = ob.data.materials[0].copy()
            ob.data.materials[0] = m
            texture_material(m,kind)

for i in range(4):
    for ob in descendants('window_%d'%i):
        if ob.dimensions.y<.05:
            m = ob.data.materials[0].copy()
            ob.data.materials[0] = m
            m.use_nodes = True
            bs = m.node_tree.nodes.get('Principled BSDF')
            bs.inputs['Base Color'].default_value = (.80,.87,.88,1)
            bs.inputs['Emission Color'].default_value = (.80,.87,.89,1)
            bs.inputs['Emission Strength'].default_value = .65

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (.54,.62,.68,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value = .35
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-.8,.65,3.8),power=1050,size=5.0,
             target=(-1,-.4,.7),color=(.85,.92,1.0))
area_emitter((3,-3,4.7),power=420,size=5,
             target=(0,.3,1),color=(1,.88,.72))
sc.view_settings.view_transform = 'AgX'
