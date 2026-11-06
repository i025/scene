import bpy
import math
import random
from mathutils import Matrix
from sceneact import *

random.seed(8)
scene = Scene('White timber ceiling and brass chandelier')
roof = Asset('Painted timber roof')
white = (.72, .735, .70)
ribwhite = (.79, .795, .75)
wood = (.30, .235, .105)
gold = (.60, .405, .085)

def roof_z(x):
    return 5.75 - .125 * abs(x)

# Narrow painted boards, with fine horizontal joints.
for side in (-1, 1):
    slope = side * math.degrees(math.atan(.125))
    for i in range(43):
        y = -4.15 + i * .195
        panel = box((4.65, .190, .065),
                    center=(side * 2.30, y, roof_z(2.30)),
                    color=white)
        panel.turn('y', slope)
        roof.include('board_%s_%s' % (side, i), panel)

# Raised, closely spaced roof rafters.
for i in range(-6, 7):
    x = i * .755
    roof.include('white_rafter_%d' % i,
                 box((.105, 8.6, .17),
                     center=(x, 0, roof_z(x)-.105),
                     color=ribwhite))
    roof.include('rafter_edge_%d' % i,
                 box((.025, 8.6, .035),
                     center=(x+.062, 0, roof_z(x)-.075),
                     color=(.58,.59,.54)))

# Exposed brown cross ties beneath the white roof.
for k, y in enumerate((-.03, 3.22, -3.28)):
    for side in (-1, 1):
        p = box((4.78, .18, .205),
                center=(side*2.36, y, roof_z(2.36)-.26),
                color=wood)
        p.turn('y', side*math.degrees(math.atan(.125)))
        roof.include('cross_tie_%d_%d' % (k,side), p)
        roof.include('tie_front_lip_%d_%d' % (k,side),
                     box((4.72,.028,.047),
                         center=(side*2.36,y-.107,roof_z(2.36)-.28),
                         color=(.41,.32,.15)))

roof.include('ridge_timber',
             box((.17,8.6,.19),center=(0,0,5.55),color=(.34,.28,.15)))
roof.include('ridge_highlight',
             box((.032,8.6,.075),center=(-.10,0,5.59),color=(.49,.43,.28)))

for y in (-.03,3.22,-3.28):
    roof.include('ridge_joint_'+str(y),
                 box((.31,.29,.29),center=(0,y,5.49),color=(.32,.255,.12)))
    for x in (-4.18,4.18):
        roof.include('outer_joint_'+str((x,y)),
                     box((.56,.40,.29),
                         center=(x,y,roof_z(x)-.27),
                         color=(.37,.285,.13)))
        roof.include('joint_plate_'+str((x,y)),
                     box((.19,.45,.055),
                         center=(x,y,roof_z(x)-.44),
                         color=(.27,.215,.105)))

# A few tiny dark nail heads visible between the rafters.
for x,y in [(-1.9,-1.12),(1.91,-1.15),(-1.88,1.23),(1.90,1.18)]:
    roof.include('nail_'+str((x,y)),
                 ball(.014,center=(x,y,roof_z(x)-.045),
                      color=(.12,.13,.105)))
scene.include('ceiling',roof)

fixture = Asset('Polished brass starburst chandelier')
center = (0,0,3.63)
fixture.include('suspension',
                rod(.022,start=(0,0,3.72),end=(0,0,5.50),color=gold))
fixture.include('ceiling_canopy',
                ball(.09,center=(0,0,5.43),color=gold))
fixture.include('main_globe',ball(.205,center=center,color=gold))
fixture.include('front_boss',
                ball(.109,center=(0,0,3.463),color=(.71,.49,.12)))
fixture.include('boss_tip',
                ball(.036,center=(0,0,3.365),color=gold))

def ring(name, p, radius, tube, color):
    x,y,z=p
    points=[(x+radius*math.cos(2*math.pi*j/48),
             y+radius*math.sin(2*math.pi*j/48),z) for j in range(49)]
    fixture.include(name,sweep_tube(points=points,radius=tube,color=color))

ring('equatorial_seam',(0,0,3.61),.204,.009,(.76,.55,.16))
ring('front_collar',(0,0,3.465),.103,.012,(.77,.56,.17))

# Two staggered tiers of slender brass arms and small mirrored gold globes.
outer_angles=[-86,-51,-10,27,61,96,129,163,196,235]
for i, deg in enumerate(outer_angles):
    a=math.radians(deg)
    r=[1.00,1.02,1.04,1.03,1.02,1.04,1.05,1.02,1.01,1.02][i]
    z=3.67+(.055 if i%2 else -.025)
    ux,uy=math.cos(a),math.sin(a)
    start=(ux*.16,uy*.16,3.65)
    end=(ux*r,uy*r,z)
    fixture.include('long_arm_%02d'%i,
                    rod(.013,start=start,end=end,color=gold))
    fixture.include('long_socket_%02d'%i,
                    rod(.025,start=(ux*(r-.09),uy*(r-.09),z),
                        end=end,color=gold))
    fixture.include('outer_globe_%02d'%i,
                    ball(.079,center=end,color=(.65,.46,.12)))
    ring('outer_rim_%02d'%i,(end[0],end[1],z-.053),.054,.007,
         (.29,.235,.085))
    fixture.include('outer_reflection_%02d'%i,
                    ball(.025,center=(end[0]-.018,end[1]-.012,z-.066),
                         color=(.80,.65,.28)))

for i in range(10):
    a=math.radians(-89+i*36)
    ux,uy=math.cos(a),math.sin(a)
    r=.565 + (.045 if i%2 else 0)
    z=3.40
    end=(ux*r,uy*r,z)
    fixture.include('short_arm_%02d'%i,
                    rod(.010,start=(ux*.15,uy*.15,3.56),end=end,color=gold))
    fixture.include('inner_globe_%02d'%i,
                    ball(.064,center=end,color=(.67,.46,.10)))
    ring('inner_rim_%02d'%i,(end[0],end[1],z-.047),.043,.006,
         (.36,.28,.09))
    fixture.include('inner_glint_%02d'%i,
                    ball(.019,center=(end[0]-.012,end[1]-.011,z-.056),
                         color=(.82,.65,.27)))
scene.include('chandelier',fixture)

realize(scene)

# Looking almost vertically upward; image vertical follows the ridge.
set_view((.025,.015,0),(0,0,4.5),lens=26,sensor=36)
camera=bpy.context.scene.camera
camera.rotation_euler=Matrix(((1,0,0),(0,-1,0),(0,0,-1))).to_quaternion().to_euler()
camera.data.lens=26
camera.data.sensor_width=36

for mat in bpy.data.materials:
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        c=bsdf.inputs['Base Color'].default_value
        if c[0] > c[1]*1.20 and c[1] > c[2]*1.65:
            bsdf.inputs['Metallic'].default_value=.83
            bsdf.inputs['Roughness'].default_value=.23
        else:
            bsdf.inputs['Roughness'].default_value=.72

area_emitter((-3,-2,1.8),power=480,size=3.4,target=(0,0,4.4),color=(1,.93,.79))
area_emitter((3,1,2.3),power=350,size=3,target=(0,0,4.8),color=(.87,.92,1))
area_emitter((0,3,1.6),power=200,size=2.5,target=(0,0,3.7),color=(1,.98,.88))

sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.world.color=(.27,.27,.25)
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
