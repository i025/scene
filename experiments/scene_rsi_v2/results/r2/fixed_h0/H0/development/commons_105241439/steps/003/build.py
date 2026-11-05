from sceneact import *
import bpy
import math
import random

random.seed(21)
scene = Scene('Classroom')

scene.include('plaster', box((9, .16, 5), center=(0, .14, 2.5), color=(.81, .79, .71)))
scene.include('blue paint', box((9, .025, 1.31), center=(0, .035, .655), color=(.015, .10, .29)))
scene.include('floor', box((10, 12, .08), center=(0, -4, -.045), color=(.62, .43, .24)))
scene.include('baseboard', box((9, .025, .035), center=(0, .005, .022), color=(.61, .49, .33)))

board = Asset('Board')
board.include('back', box((5.03, .065, 1.69), center=(0, -.035, 1.88), color=(.13, .19, .12)))
board.include('chalk_left', box((2.495, .012, 1.665), center=(-1.254, -.076, 1.88), color=(.06, .19, .105)))
board.include('chalk_right', box((2.495, .012, 1.665), center=(1.254, -.076, 1.88), color=(.055, .15, .075)))
board.include('seam', box((.012, .018, 1.68), center=(0, -.088, 1.88), color=(.16, .22, .13)))
for x in (-2.51, 2.51):
    board.include('side_' + str(x), box((.012, .018, 1.68), center=(x, -.084, 1.88), color=(.20, .25, .16)))
scene.include('blackboard', board)

# Sparse physical chalk marks complement procedural erased chalk dust.
chalk = Asset('Chalk traces')
for i in range(44):
    x = random.uniform(.04, 2.45)
    z = random.uniform(1.10, 2.61)
    h = min(random.uniform(.04, .9), 2.70-z)
    chalk.include('wipe_' + str(i),
                  box((random.uniform(.002, .009), .0015, h),
                      center=(x, -.085, z+h/2),
                      color=random.choice([(.17,.26,.16), (.22,.30,.19), (.12,.22,.13)])))
for i in range(38):
    x = random.uniform(-2.45, -.06)
    z = random.uniform(1.08, 2.66)
    h = random.uniform(.025, .25)
    h = min(h, z-1.055)
    chalk.include('left_streak_' + str(i),
                  box((random.uniform(.002, .007), .0015, h),
                      center=(x, -.087, z-h/2),
                      color=(.25, .37, .25)))
for i in range(12):
    cx = random.uniform(-1.25, -.9)
    cz = random.uniform(2.09, 2.28)
    rx = random.uniform(.30, .69)
    rz = random.uniform(.20, .37)
    start = random.uniform(-1.2, 1.9)
    span = random.uniform(1.0, 2.7)
    pts = []
    for j in range(11):
        a = start + span*j/10
        pts.append((cx+rx*math.cos(a), -.091, cz+rz*math.sin(a)))
    chalk.include('curved_eraser_' + str(i),
                  sweep_tube(points=pts, radius=random.uniform(.003,.008),
                             color=(.25,.35,.24)))
for i in range(20):
    x = random.uniform(-2.44, 2.43)
    z = random.uniform(1.08, 2.66)
    chalk.include('fleck_' + str(i), box((.004, .002, random.uniform(.005,.023)),
                  center=(x, -.095, z), color=(.49,.53,.37)))
scene.include('chalk', chalk)

notice = Asset('Notice')
notice.include('border', box((.91,.012,.718), center=(.21,-.005,3.325), color=(.64,.58,.47)))
notice.include('paper', box((.885,.006,.695), center=(.205,-.016,3.33), color=(.85,.82,.73)))
for col in range(3):
    for row in range(13):
        w = random.uniform(.11,.23)
        notice.include('print_%d_%d' % (col,row),
                       box((w,.001,.0025), center=(-.18+col*.279+w/2,-.020,3.60-row*.043),
                           color=(.43,.41,.36)))
notice.include('heading', box((.46,.001,.007), center=(.21,-.021,3.646), color=(.40,.38,.32)))
notice.include('string_left', rod(.0015, start=(-.24,-.008,3.684), end=(.20,.005,4.00), color=(.58,.53,.44)))
notice.include('string_right', rod(.0015, start=(.65,-.008,3.684), end=(.20,.005,4.00), color=(.58,.53,.44)))
scene.include('hanging notice',notice)
scene.include('dark wall fastener', ball(.045, center=(-.42,-.013,3.52), color=(.11,.085,.065)))
scene.include('fastener glint', ball(.010, center=(-.433,-.054,3.531), color=(.52,.45,.35)))

def desk(name, x, y, width, depth, height, pale=False):
    a=Asset(name)
    c=(.76,.70,.58) if pale else (.86,.60,.25)
    a.include('woodtop',box((width,depth,.045),center=(x,y,height),color=c))
    a.include('front lip',box((width,.018,.022),
                            center=(x,y-depth/2-.002,height-.011),
                            color=(.64,.56,.42) if pale else (.68,.43,.16)))
    for sx in (-1,1):
        lx=x+sx*(width/2-.10)
        for sy in (-1,1):
            ly=y+sy*(depth/2-.065)
            a.include('leg%d%d'%(sx,sy),
                      rod(.016,start=(lx,ly,height-.025),
                          end=(lx+sx*.025,ly+sy*.035,.03),color=(.45,.49,.44)))
        a.include('brace'+str(sx),
                  rod(.011,start=(lx,y-depth/2+.06,.28),
                      end=(lx,y+depth/2-.06,.28),color=(.40,.44,.40)))
    a.include('rail',box((width-.18,.025,.035),center=(x,y+.13,height-.08),color=(.40,.44,.40)))
    scene.include(name,a)

desk('middle desk',-.54,-2.0,1.99,.58,.815)
desk('front desk',-.57,-3.25,1.95,.65,.72)
desk('pale desk',1.83,-3.30,1.64,.66,.71,True)

def chair(name,x,y,width,top):
    a=Asset(name)
    a.include('seat',box((width,.42,.032),center=(x,y,.46),color=(.70,.43,.17)))
    back=box((width,.038,.245),center=(x,y+.19,top-.1225),color=(.68,.38,.13))
    back.turn('y',-3)
    a.include('backrest',back)
    for side in (-1,1):
        xx=x+side*(width/2-.035)
        a.include('back tube'+str(side),
                  rod(.012,start=(xx,y+.17,.035),end=(xx,y+.205,top-.025),color=(.43,.46,.40)))
        a.include('front tube'+str(side),
                  rod(.013,start=(xx,y-.15,.46),end=(xx+side*.02,y-.20,.025),color=(.43,.46,.40)))
    scene.include(name,a)

chair('rear chair',-.86,-1.29,.55,1.035)
chair('left cropped chair',-1.04,-4.08,.56,.77)
chair('right cropped chair',1.85,-4.03,.61,.74)

realize(scene)

def material_for(obj):
    mat=bpy.data.materials.new(obj.name+' surface')
    mat.use_nodes=True
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.88
    return mat,bs

def noise_material(obj,lo,hi,stretch=(1,1,1),scale=5):
    mat,bs=material_for(obj)
    n=mat.node_tree.nodes
    l=mat.node_tree.links
    coord=n.new('ShaderNodeTexCoord')
    mul=n.new('ShaderNodeVectorMath')
    mul.operation='MULTIPLY'
    mul.inputs[1].default_value=stretch
    l.new(coord.outputs['Generated'],mul.inputs[0])
    noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=scale
    noise.inputs['Detail'].default_value=3
    l.new(mul.outputs[0],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.15
    ramp.color_ramp.elements[0].color=(*lo,1)
    ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[1].color=(*hi,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0])
    l.new(ramp.outputs[0],bs.inputs['Base Color'])
    return mat,bs,coord

for obj in list(bpy.data.objects):
    if obj.type!='MESH':
        continue
    name=obj.name.lower()
    if 'chalk_right' in name:
        mat,bs,coord=noise_material(obj,(.025,.072,.032),(.22,.29,.17),(36,1,.40),4)
        n=mat.node_tree.nodes
        l=mat.node_tree.links
        sep=n.new('ShaderNodeSeparateXYZ')
        l.new(coord.outputs['Generated'],sep.inputs[0])
        fade=n.new('ShaderNodeMapRange')
        fade.inputs['From Min'].default_value=0
        fade.inputs['From Max'].default_value=1
        fade.inputs['To Min'].default_value=1.25
        fade.inputs['To Max'].default_value=.38
        l.new(sep.outputs['X'],fade.inputs['Value'])
        old=bs.inputs['Base Color'].links[0].from_socket
        mix=n.new('ShaderNodeMixRGB')
        mix.blend_type='MULTIPLY'
        mix.inputs[0].default_value=1
        l.new(old,mix.inputs[1])
        l.new(fade.outputs[0],mix.inputs[2])
        l.new(mix.outputs[0],bs.inputs['Base Color'])
    elif 'chalk_left' in name:
        mat,bs,coord=noise_material(obj,(.025,.105,.05),(.12,.25,.14),(3,1,3),5)
        n=mat.node_tree.nodes
        l=mat.node_tree.links
        stretch=n.new('ShaderNodeVectorMath')
        stretch.operation='MULTIPLY'
        stretch.inputs[1].default_value=(70,1,1.5)
        l.new(coord.outputs['Generated'],stretch.inputs[0])
        fine=n.new('ShaderNodeTexNoise')
        fine.inputs['Scale'].default_value=3
        fine.inputs['Detail'].default_value=2
        l.new(stretch.outputs[0],fine.inputs[0])
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.40
        ramp.color_ramp.elements[0].color=(.01,.025,.012,1)
        ramp.color_ramp.elements[1].position=.72
        ramp.color_ramp.elements[1].color=(.12,.16,.09,1)
        l.new(fine.outputs['Fac'],ramp.inputs[0])
        old=bs.inputs['Base Color'].links[0].from_socket
        add=n.new('ShaderNodeMixRGB')
        add.blend_type='ADD'
        add.inputs[0].default_value=.55
        l.new(old,add.inputs[1])
        l.new(ramp.outputs[0],add.inputs[2])
        l.new(add.outputs[0],bs.inputs['Base Color'])
    elif 'blue paint' in name:
        noise_material(obj,(.008,.055,.21),(.019,.115,.32),(1,1,1),18)
    elif 'plaster' in name:
        noise_material(obj,(.74,.73,.66),(.86,.84,.76),(1,1,1),5)
    elif 'woodtop' in name:
        if 'pale' in name:
            noise_material(obj,(.69,.63,.52),(.84,.78,.66),(.5,16,1),5)
        else:
            noise_material(obj,(.76,.49,.17),(.95,.71,.34),(.4,20,1),5)
    elif 'backrest' in name:
        noise_material(obj,(.52,.27,.075),(.78,.47,.19),(13,1,.5),4)

set_view((0,-8.5,1.80),(0,0,1.80),lens=48,sensor=36)
bpy.context.scene.camera.data.clip_start=.05

area_emitter((-3.8,-4,5.0),power=850,size=4,target=(0,0,1.4),color=(1,.95,.84))
area_emitter((2.5,-4,3.5),power=95,size=4,target=(0,0,1.4),color=(.86,.91,1))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.74,.77,.80,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.42

s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.samples=24
s.cycles.use_denoising=True
s.render.resolution_x=512
s.render.resolution_y=337
s.render.resolution_percentage=100
s.view_settings.view_transform='Standard'
s.view_settings.look='Medium High Contrast'
s.view_settings.exposure=0
s.view_settings.gamma=1
