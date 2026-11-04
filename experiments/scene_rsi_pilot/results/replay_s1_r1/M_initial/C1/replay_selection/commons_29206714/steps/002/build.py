from sceneact import *
import bpy, math, random
random.seed(8)

# Anchor: crown approximately (.26,.00)-(.76,.14).
# Anchor: cupboard cavity approximately (.32,.13)-(.68,.65).
# Anchor: right door approximately (.67,.09)-(.89,.66).
# Anchor: foreground wheel approximately (.23,.39)-(.37,1.00), cropped below.
# Anchor: counter front approximately (.36,.72)-(.68,.82).
# Anchor: white chimney and dark hearth occupy the far right edge.

# CAMERA/lens: cabinet and surrounding architecture appear too small with excess
# floor visible. Hypothesis: insufficient image scale; change focal length only.
# Predict tighter framing and cropped base; relative occlusions remain unchanged.
CAMERA = dict(position=(2.7,-7.5,2.85), target=(0,-.10,1.43), lens=65)
DIM = dict(width=1.88, depth=.55, counter=1.02, crown=2.72,
           wheel_radius=1.05, wheel_angle=-62)
PLACE = dict(cabinet=(0,0,0), wheel=(-.65,-1.02,.55))
FINISH = dict(wood=(.34,.135,.045), edge=(.25,.083,.025),
              panel=(.40,.18,.071), back=(.27,.12,.052),
              cream=(.77,.76,.66), china=(.83,.85,.79),
              blue=(.23,.32,.33), metal=(.29,.31,.29))
LIGHT = dict(position=(-3.5,-4.0,4.4), power=650, size=3.2)
scene = Scene('Historic kitchen')

def add(parent,key,node):
    parent.include(key,node)

def cube(parent,key,size,center,color):
    add(parent,key,box(size=size,center=center,color=color))

def line(parent,key,a,b,r,color):
    add(parent,key,rod(radius=r,start=a,end=b,color=color))

architecture=Asset('architecture')
cube(architecture,'floor',(8,7,.10),(0,0,-.075),(.36,.31,.23))
cube(architecture,'plaster_wall',(7,.16,4),(0,.78,1.8),(.69,.70,.65))
cube(architecture,'left_wall',(.14,5,4),(-2.45,-1.65,1.8),(.73,.72,.66))
cube(architecture,'dado',(4.1,.07,.49),(-.5,.665,.23),(.48,.43,.27))
cube(architecture,'dado_cap',(4.1,.10,.035),(-.5,.61,.49),(.60,.56,.42))
cube(architecture,'chimney',(1.12,.65,3.3),(1.83,.63,1.6),(.77,.78,.73))
cube(architecture,'hearth_opening',(.8,.08,.91),(2.02,.265,.40),(.045,.045,.035))
cube(architecture,'mantel_beam',(1.15,.52,.23),(1.95,.14,1.04),(.16,.105,.067))
for j in range(7):
    for i in range(3):
        cube(architecture,f'hearth_stone_{j}_{i}',(.265,.12,.113),
             (1.48+i*.29+(j%2)*.08,.18,.07+j*.135),(.17+j*.008,.16,.13))
for j in range(10):
    cube(architecture,f'chimney_mortar_{j}',(.32,.006,.008),
         (1.39,.296,.06+j*.105),(.62,.63,.58))
for i in range(13):
    x=random.uniform(-2.36,-1.5)
    z=random.uniform(.65,2.3)
    patch=ball(radius=random.uniform(.035,.11),center=(x,.684,z),color=(.62,.61,.53))
    patch.resize((.7,.035,1.5))
    add(architecture,f'plaster_wear_{i}',patch)
scene.include('architecture',architecture)

cabinet=Asset('cabinet')
w=DIM['width']
cube(cabinet,'lower_back',(w,.055,1.02),(0,.41,.52),FINISH['back'])
for x in (-.90,.90):
    cube(cabinet,f'lower_side_{x}',(.10,.56,1.03),(x,.15,.52),FINISH['wood'])
    cube(cabinet,f'foot_{x}',(.13,.43,.15),(x,.17,.075),FINISH['edge'])
cube(cabinet,'lower_bottom',(w,.55,.09),(0,.15,.12),FINISH['wood'])
cube(cabinet,'counter_top',(2.02,.73,.075),(0,.075,1.055),FINISH['wood'])
cube(cabinet,'counter_lip',(2.05,.06,.055),(0,-.31,1.026),FINISH['edge'])
cube(cabinet,'drawer_front',(1.85,.09,.21),(0,-.185,.87),FINISH['panel'])
cube(cabinet,'drawer_inset',(1.65,.025,.125),(0,-.24,.87),FINISH['wood'])
for x in (-.48,.48):
    line(cabinet,f'drawer_pull_{x}',(x,-.265,.856),(x,-.31,.856),.025,FINISH['edge'])
cube(cabinet,'lower_middle_stile',(.085,.11,.66),(0,-.15,.44),FINISH['edge'])
for i,x in enumerate((-.46,.46)):
    cube(cabinet,f'base_door_{i}',(.83,.075,.65),(x,-.16,.445),FINISH['wood'])
    cube(cabinet,f'base_panel_{i}',(.64,.028,.49),(x,-.211,.445),FINISH['panel'])
    for sx in (-1,1):
        cube(cabinet,f'base_stile_{i}_{sx}',(.045,.025,.57),
             (x+sx*.35,-.233,.445),FINISH['wood'])
    for z in (.17,.72):
        cube(cabinet,f'base_rail_{i}_{z}',(.73,.025,.045),(x,-.232,z),FINISH['wood'])
for z in (.27,.64):
    cube(cabinet,f'lower_hinge_{z}',(.035,.035,.09),(.87,-.225,z),FINISH['metal'])
cube(cabinet,'upper_back',(1.85,.055,1.49),(0,.39,1.84),FINISH['back'])
for i in range(10):
    cube(cabinet,f'back_board_{i}',(.177,.015,1.40),(-.81+i*.18,.35,1.83),
         (.29+random.random()*.035,.127+random.random()*.015,.05))
for x in (-.91,.91):
    cube(cabinet,f'upper_side_{x}',(.095,.47,1.58),(x,.18,1.86),FINISH['wood'])
    cube(cabinet,f'front_pilaster_{x}',(.115,.09,1.61),(x,-.078,1.86),FINISH['panel'])
for j,z in enumerate((1.12,1.68,2.18,2.59)):
    cube(cabinet,f'shelf_{j}',(1.85,.50,.045),(0,.14,z),FINISH['wood'])
    cube(cabinet,f'shelf_edge_{j}',(1.88,.045,.032),(0,-.12,z-.008),FINISH['edge'])
for j,(width,depth,height,z) in enumerate(
        ((2.01,.62,.10,2.65),(2.15,.67,.045,2.72),(2.22,.70,.035,2.755))):
    cube(cabinet,f'crown_{j}',(width,depth,height),(0,.16,z),FINISH['wood'])
cube(cabinet,'crown_frieze',(1.98,.06,.12),(0,-.14,2.59),FINISH['panel'])

def door(key,hinge,angle,width):
    d=Asset(key)
    cx=hinge[0]+width/2
    cy=hinge[1]
    cube(d,'body',(width,.065,1.59),(cx,cy,1.84),FINISH['wood'])
    cube(d,'raised_panel',(width-.16,.025,1.32),(cx,cy-.046,1.80),FINISH['panel'])
    arch=ball(radius=(width-.17)/2,center=(cx,cy-.051,2.24),color=FINISH['panel'])
    arch.resize((1,.065,1.16))
    add(d,'arched_crown',arch)
    for sx in (-1,1):
        cube(d,f'stile_{sx}',(.066,.035,1.47),
             (cx+sx*(width/2-.045),cy-.048,1.84),FINISH['wood'])
    for z in (1.10,2.57):
        cube(d,f'rail_{z}',(width,.035,.075),(cx,cy-.047,z),FINISH['wood'])
    for z in (1.30,2.33):
        cube(d,f'hinge_{z}',(.055,.025,.065),(hinge[0]+.015,cy-.07,z),FINISH['metal'])
    d.turn('z',angle,pivot=(hinge[0],cy,1.84))
    return d

add(cabinet,'left_open_door',door('left_open_door',(-.95,-.07),-153,.72))
add(cabinet,'right_open_door',door('right_open_door',(.94,-.09),-20,.78))
scene.include('cabinet',cabinet)

def plate(key,x,y,z,r):
    p=Asset(key)
    add(p,'ceramic_body',rod(radius=r,length=.022,center=(x,y,z),
                            axis='+y',color=FINISH['china']))
    for k,rr in enumerate((r*.76,r*.88)):
        pts=[(x+rr*math.cos(a*math.tau/36),y-.015,z+rr*math.sin(a*math.tau/36))
             for a in range(37)]
        add(p,f'rim_{k}',sweep_tube(points=pts,radius=.004,color=FINISH['blue']))
    for j in range(7):
        a=j*math.tau/7+.3
        leaf=ball(radius=.017,
                  center=(x+r*.68*math.cos(a),y-.025,z+r*.68*math.sin(a)),
                  color=(.30,.39,.30))
        leaf.resize((.65,.24,1.7))
        add(p,f'floral_{j}',leaf)
    return p

china=Asset('china_display')
for i,(x,z,r) in enumerate(((-.48,1.925,.215),(.48,1.925,.215),
                           (-.68,1.39,.168),(-.31,1.39,.18),
                           (.17,1.39,.18),(.58,1.39,.18))):
    add(china,f'display_plate_{i}',plate(f'display_plate_{i}',x,.245,z,r))
for j in range(4):
    add(china,f'stacked_plate_{j}',rod(radius=.18-j*.008,length=.018,
        center=(-.05,.01,1.72+j*.018),color=FINISH['china']))

def vessel(key,x,y,z,r,color,handle=False,lid=False):
    v=Asset(key)
    belly=ball(radius=r,center=(x,y,z+r*.72),color=color)
    belly.resize((1,1,.85))
    add(v,'bowl',belly)
    add(v,'foot',rod(radius=r*.55,length=.025,center=(x,y,z+.015),color=color))
    add(v,'mouth',rod(radius=r*.91,length=.018,center=(x,y,z+r*1.22),color=color))
    if handle:
        pts=[(x+r*.88+r*.51*math.sin(a*math.pi/8),y,
              z+r*.73+r*.47*math.cos(a*math.pi/8)) for a in range(9)]
        add(v,'handle',sweep_tube(points=pts,radius=.014,color=color))
    if lid:
        add(v,'lid',rod(radius=r*.86,length=.025,center=(x,y,z+r*1.30),color=color))
        add(v,'knob',ball(radius=.026,center=(x,y,z+r*1.48),color=color))
    return v

add(china,'cream_teapot',vessel('cream_teapot',-.65,-.015,1.705,.145,
                              FINISH['china'],True,True))
line(china,'teapot_spout',(-.76,-.015,1.80),(-.88,-.015,1.91),.027,FINISH['china'])
add(china,'green_jug',vessel('green_jug',.57,.00,1.705,.14,(.025,.19,.19),True))
line(china,'jug_spout',(.48,0,1.84),(.44,0,1.94),.022,(.025,.19,.19))
for i,x in enumerate((-.83,.76)):
    add(china,f'cup_{i}',vessel(f'cup_{i}',x,-.025,1.15,.084,FINISH['china'],True))
for i in range(8):
    add(china,f'glass_{i}',rod(radius=.027,length=.11,
        center=(-.62+i*.083,.03,2.26),color=(.52,.57,.55),opacity=.62))
for i,x in enumerate((-.79,-.62)):
    add(china,f'bottle_body_{i}',rod(radius=.043,length=.17,
        center=(x,.18,2.29),color=(.53,.46,.30)))
    add(china,f'bottle_neck_{i}',rod(radius=.016,length=.17,
        center=(x,.18,2.45),color=(.48,.44,.32)))
add(china,'pewter_jug',vessel('pewter_jug',.68,.16,2.205,.125,FINISH['metal'],True,True))
add(china,'pewter_pot',vessel('pewter_pot',.01,.19,2.205,.105,FINISH['metal']))
scene.include('china_display',china)

winder=Asset('tabletop_yarn_winder')
for i,x in enumerate((-.46,.40)):
    cube(winder,f'foot_{i}',(.20,.38,.035),(x,-.11,1.12),(.45,.22,.07))
    cube(winder,f'upright_{i}',(.055,.075,.39),(x,-.02,1.32),(.46,.23,.08))
    cube(winder,f'cap_{i}',(.15,.09,.045),(x,-.02,1.53),(.44,.20,.06))
for j in range(4):
    z=1.17+j*.075
    line(winder,f'long_bar_{j}',(-.52,-.24,z),(.47,-.24,z+.015),.014,(.48,.32,.15))
    line(winder,f'diagonal_{j}',(-.52,-.24,z),(.47,.02,z+.06),.008,(.50,.53,.51))
for x in (-.52,.47):
    line(winder,f'end_rod_{x}',(x,-.24,1.17),(x,.02,1.46),.014,(.53,.54,.50))
scene.include('tabletop_yarn_winder',winder)

# foreground_spinning_wheel/builder: the existing wheel is broad, fully visible,
# and too far left. Hypothesis: local wheel pose and dimensions differ.
# Change this composite's placement, radius and azimuth; predict a narrow tall
# silhouette crossing the cabinet's left edge and cropped below.
# Risk: foreground occlusion changes; all wheel fittings follow its pivot.
wheel=Asset('foreground_spinning_wheel')
wx,wy,wz=PLACE['wheel']
R=DIM['wheel_radius']
for edge,yoff in enumerate((-.042,.042)):
    pts=[(wx+R*math.cos(i*math.tau/64),wy+yoff,wz+R*math.sin(i*math.tau/64))
         for i in range(65)]
    add(wheel,f'rim_{edge}',sweep_tube(points=pts,radius=.031,color=(.25,.20,.14)))
for i in range(12):
    a=i*math.tau/12
    line(wheel,f'spoke_{i}',(wx,wy,wz),
         (wx+(R-.03)*math.cos(a),wy,wz+(R-.03)*math.sin(a)),.016,(.30,.24,.16))
line(wheel,'hub',(wx,wy-.11,wz),(wx,wy+.13,wz),.065,(.36,.28,.18))
for i,xoff in enumerate((-.23,.23)):
    line(wheel,f'support_{i}',(wx+xoff,wy+.04,-.48),
         (wx+xoff*.4,wy+.04,wz+.01),.039,(.33,.25,.15))
cube(wheel,'stand_crossbar',(.65,.17,.065),(wx,wy+.04,-.30),(.31,.23,.14))
wheel.turn('z',DIM['wheel_angle'],pivot=(wx,wy,wz))
scene.include('foreground_spinning_wheel',wheel)

spindle=Asset('foreground_spindle')
line(spindle,'post',(-1.40,-1.50,-.12),(-1.40,-1.50,.71),.034,(.56,.43,.25))
for z in (.30,.53,.66):
    add(spindle,f'collar_{z}',ball(radius=.049,center=(-1.40,-1.50,z),color=(.62,.49,.30)))
line(spindle,'bright_spindle',(-1.25,-1.48,.24),(-1.25,-1.48,1.13),.014,(.79,.79,.70))
line(spindle,'crosspiece',(-1.48,-1.50,.40),(-1.12,-1.50,.40),.026,(.60,.47,.28))
scene.include('foreground_spindle',spindle)

assert all(math.isfinite(v) and v>0 for v in DIM.values() if v != DIM['wheel_angle'])
assert len(cabinet.members)>20 and len(china.members)>10
assert len(wheel.members)>10 and len(winder.members)>5
realize(scene)
set_view(**CAMERA)
area_emitter(**LIGHT,target=(0,0,1.4),color=(1,.91,.78))
area_emitter((1,-3,3.2),power=130,size=2.5,target=(0,0,1.4),color=(.82,.89,1))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.66,.70,.74,1)
sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.32
for material in bpy.data.materials:
    material.use_nodes=True
    shader=material.node_tree.nodes.get('Principled BSDF')
    if shader:
        shader.inputs['Roughness'].default_value=.62
