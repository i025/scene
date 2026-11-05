from sceneact import *
import bpy, math, random

random.seed(21)
scene = Scene('Quiet classroom')

scene.include('wall', box((9,.18,5), center=(0,.13,2.5), color=(.79,.78,.70)))
scene.include('blue_lower_wall', box((9,.025,1.31), center=(0,.023,.655), color=(.015,.105,.28)))
scene.include('floor', box((10,12,.12), center=(0,-4,-.065), color=(.56,.37,.19)))
scene.include('skirting', box((9,.035,.045), center=(0,-.005,.026), color=(.51,.40,.28)))

board = Asset('chalkboard')
board.include('backing', box((5.03,.075,1.69), center=(0,-.045,1.88), color=(.12,.17,.105)))
board.include('left_panel', box((2.49,.018,1.655), center=(-1.255,-.092,1.88), color=(.055,.18,.105)))
board.include('right_panel', box((2.49,.018,1.655), center=(1.255,-.092,1.88), color=(.055,.15,.083)))
board.include('center_seam', box((.012,.018,1.665), center=(0,-.108,1.88), color=(.15,.22,.13)))
for x in (-2.512,2.512):
    board.include('edge'+str(x), box((.016,.026,1.69), center=(x,-.096,1.88), color=(.19,.23,.15)))
scene.include('board',board)

marks=Asset('chalk residue')
def stroke(name,points,radius,color):
    if len(points)>1:
        marks.include(name,sweep_tube(points=points,radius=radius,color=color))

for i in range(300):
    x=random.uniform(.025,2.47)
    z0=random.uniform(1.06,2.54)
    z1=min(2.697,z0+random.uniform(.12,1.1))
    intensity=max(0,1-x/2.65)
    c=random.choice([
        (.12,.235,.145),(.17,.27,.175),(.22,.30,.205),
        (.27,.34,.24),(.10,.205,.12)])
    c=tuple(v*(.65+.35*intensity) for v in c)
    bend=random.uniform(-.04,.04)
    pts=[(x+bend*math.sin(t*2.7),-.109-random.random()*.001,z0+(z1-z0)*t)
         for t in (0,.15,.35,.55,.75,1)]
    stroke('vertical_wipe_%d'%i,pts,random.uniform(.001,.009),c)

for i in range(260):
    x=random.uniform(-2.46,-.04)
    z=random.uniform(1.08,2.67)
    length=random.uniform(.025,.42)
    if random.random()<.62:
        pts=[(x+.009*math.sin(t*5+i),-.112,z-t*length)
             for t in (0,.25,.5,.75,1) if z-t*length>1.06]
    else:
        pts=[(min(-.025,x+t*length),-.112,z+.009*math.sin(t*7+i))
             for t in (0,.25,.5,.75,1)]
    stroke('left_smear_%d'%i,pts,random.uniform(.001,.005),
           random.choice([(.17,.31,.205),(.23,.36,.25),(.32,.42,.29),(.12,.27,.17)]))

for i in range(48):
    cx=random.uniform(-1.28,-.75)
    cz=random.uniform(2.12,2.30)
    rx=random.uniform(.25,.72)
    rz=random.uniform(.16,.40)
    a0=random.uniform(-1.2,3.0)
    span=random.uniform(.55,2.9)
    pts=[]
    for j in range(24):
        a=a0+span*j/23
        x=cx+rx*math.cos(a)
        z=cz+rz*math.sin(a)
        if -2.46<x<-.035 and 1.07<z<2.69:
            pts.append((x,-.117,z))
    stroke('eraser_arc_%d'%i,pts,random.uniform(.003,.014),
           random.choice([(.17,.29,.19),(.23,.34,.23),(.30,.39,.27),(.12,.25,.16)]))

for row in range(7):
    z=1.37+row*.145
    for k in range(random.randint(9,19)):
        x=random.uniform(-2.39,-1.02)
        h=random.uniform(.018,.059)
        pts=[(x,-.121,z),(x+.012,-.121,z+h),
             (x+.034,-.121,z+h*.3),(x+.046,-.121,z+h*.65)]
        stroke('faded_letter_%d_%d'%(row,k),pts,.0018,(.32,.43,.30))
for i in range(65):
    x=random.uniform(-2.46,2.45)
    z=random.uniform(1.08,2.67)
    stroke('chalk_speck_%d'%i,
           [(x,-.123,z),(x+.003,-.123,z+random.uniform(.004,.027))],
           .0018,(.48,.53,.37))
scene.include('residue',marks)

notice=Asset('wall notice')
notice.include('paper_edge',box((.91,.016,.718),center=(.21,-.004,3.325),color=(.62,.56,.43)))
notice.include('paper',box((.883,.008,.697),center=(.205,-.017,3.331),color=(.82,.79,.70)))
for col in range(3):
    x=-.185+col*.276
    for row in range(19):
        z=3.611-row*.029
        w=random.uniform(.09,.23)
        notice.include('print_%d_%d'%(col,row),
                       box((w,.002,random.choice([.002,.003,.004])),
                           center=(x+w/2,-.024,z),color=(.40,.39,.34)))
notice.include('heading',box((.47,.002,.009),center=(.22,-.026,3.647),color=(.39,.37,.31)))
notice.include('rule',box((.81,.002,.002),center=(.205,-.026,3.59),color=(.51,.47,.39)))
notice.include('left_string',rod(.0018,start=(-.24,-.013,3.69),end=(.20,.005,4.02),color=(.51,.47,.37)))
notice.include('right_string',rod(.0018,start=(.65,-.013,3.69),end=(.20,.005,4.02),color=(.51,.47,.37)))
for x in (-.225,.64):
    notice.include('pin'+str(x),ball(.011,center=(x,-.031,3.665),color=(.61,.39,.17)))
scene.include('notice',notice)
scene.include('wall_hook',ball(.047,center=(-.42,-.026,3.52),color=(.12,.095,.075)))
scene.include('hook_center',ball(.016,center=(-.423,-.067,3.531),color=(.40,.34,.26)))

def desk(name,x,y,width,depth,height,cream=False):
    a=Asset(name)
    topcolor=(.72,.63,.46) if cream else (.83,.56,.22)
    a.include('top',fillet_box((width,depth,.052),radius=.024,
                             center=(x,y,height),color=topcolor))
    a.include('front_edge',box((width-.055,.021,.027),
                              center=(x,y-depth/2-.001,height-.009),
                              color=(.57,.49,.36) if cream else (.68,.43,.16)))
    for sx in (-1,1):
        lx=x+sx*(width/2-.11)
        for sy in (-1,1):
            ly=y+sy*(depth/2-.075)
            a.include('leg_%s_%s'%(sx,sy),
                      rod(.017,start=(lx,ly,height-.035),
                          end=(lx+sx*.035,ly+sy*.05,.055),color=(.43,.47,.43)))
            a.include('foot_%s_%s'%(sx,sy),
                      box((.046,.055,.035),
                          center=(lx+sx*.035,ly+sy*.05,.037),color=(.16,.17,.15)))
        a.include('sidebar'+str(sx),
                  rod(.013,start=(lx,y-depth/2+.06,.30),
                      end=(lx,y+depth/2-.06,.30),color=(.41,.44,.40)))
    a.include('under_top_rail',
              box((width-.16,.035,.045),center=(x,y+.13,height-.093),color=(.39,.43,.40)))
    for i in range(19):
        xx=x+random.uniform(-width*.46,width*.46)
        yy=y+random.uniform(-depth*.4,depth*.4)
        a.include('woodgrain_%d'%i,
                  box((random.uniform(.04,.35),.001,.0006),
                      center=(xx,yy,height+.0264),
                      color=(.63,.56,.43) if cream else (.69,.46,.20)))
    scene.include(name,a)

desk('middle desk',-.54,-2.0,1.99,.58,.815)
desk('foreground desk',-.68,-3.33,2.10,.65,.72)
desk('right foreground desk',2.12,-3.30,1.64,.66,.71,True)

def chair(name,x,y,width=.51,backheight=1.03):
    a=Asset(name)
    a.include('seat',fillet_box((width,.43,.035),radius=.016,
                               center=(x,y,.46),color=(.69,.41,.15)))
    back=box((width,.045,.255),center=(x,y+.19,backheight-.1275),color=(.64,.35,.12))
    back.turn('y',-3)
    a.include('back',back)
    for sx in (-1,1):
        xx=x+sx*(width/2-.045)
        a.include('rear_support'+str(sx),
                  rod(.012,start=(xx,y+.18,.06),
                      end=(xx,y+.215,backheight-.025),color=(.46,.48,.42)))
        a.include('front_leg'+str(sx),
                  rod(.014,start=(xx,y-.16,.46),
                      end=(xx+sx*.025,y-.205,.025),color=(.46,.48,.42)))
    for i in range(6):
        xx=x+random.uniform(-width*.42,width*.42)
        a.include('backgrain'+str(i),
                  box((.002,.001,.19),center=(xx,y+.165,backheight-.13),color=(.51,.29,.11)))
    scene.include(name,a)

chair('chair behind middle desk',-.86,-1.29,.55,1.035)
chair('cropped left chair',-1.04,-4.08,.56,.77)
chair('cropped right chair',1.85,-4.03,.61,.74)

realize(scene)

def noise_finish(obj, low, high, scale=8, detail=3, stretch=None, bump=0):
    if obj.type!='MESH' or not obj.data.materials:
        return
    mat=obj.data.materials[0].copy()
    obj.data.materials[0]=mat
    mat.use_nodes=True
    n=mat.node_tree.nodes
    l=mat.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.9
    tex=n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=scale
    tex.inputs['Detail'].default_value=detail
    coord=n.new('ShaderNodeTexCoord')
    if stretch:
        vec=n.new('ShaderNodeVectorMath')
        vec.operation='MULTIPLY'
        vec.inputs[1].default_value=stretch
        l.new(coord.outputs['Generated'],vec.inputs[0])
        l.new(vec.outputs[0],tex.inputs['Vector'])
    else:
        l.new(coord.outputs['Generated'],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.15
    ramp.color_ramp.elements[0].color=(*low,1)
    ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[1].color=(*high,1)
    l.new(tex.outputs['Fac'],ramp.inputs[0])
    l.new(ramp.outputs[0],bs.inputs['Base Color'])
    if bump:
        b=n.new('ShaderNodeBump')
        b.inputs['Strength'].default_value=bump
        b.inputs['Distance'].default_value=.018
        l.new(tex.outputs['Fac'],b.inputs['Height'])
        l.new(b.outputs[0],bs.inputs['Normal'])

for obj in bpy.data.objects:
    name=obj.name.lower()
    if 'right_panel' in name:
        noise_finish(obj,(.025,.075,.038),(.13,.20,.105),5,3,(27,2,.6),.11)
    elif 'left_panel' in name:
        noise_finish(obj,(.027,.11,.055),(.10,.23,.13),5,4,(3,1,2),.08)
    elif 'blue_lower' in name:
        noise_finish(obj,(.009,.065,.22),(.019,.115,.32),5,4,None,.12)
    elif 'wall' in name and 'hook' not in name and 'notice' not in name:
        noise_finish(obj,(.72,.71,.64),(.85,.83,.75),5,3,None,.06)
    elif 'top' in name and 'rail' not in name:
        if 'right foreground' in name:
            noise_finish(obj,(.62,.56,.45),(.80,.74,.62),4,2,(.6,18,1),.035)
        else:
            noise_finish(obj,(.68,.42,.14),(.91,.66,.29),4,2,(.6,18,1),.035)

set_view((0,-8.5,1.80),(0,0,1.80),lens=48,sensor=36)
camera=bpy.context.scene.camera
camera.data.clip_start=.05
camera.data.clip_end=100

area_emitter((-3.8,-4.0,5.0),power=850,size=4.0,target=(0,0,1.4),color=(1.0,.94,.81))
area_emitter((2.5,-4.0,3.4),power=110,size=4,target=(0,0,1.4),color=(.84,.89,1.0))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.76,.80,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.42

render=bpy.context.scene
render.render.engine='CYCLES'
render.cycles.samples=64
render.render.resolution_x=512
render.render.resolution_y=337
render.render.resolution_percentage=100
render.view_settings.view_transform='Standard'
render.view_settings.look='Medium High Contrast'
render.view_settings.exposure=0
render.view_settings.gamma=1
