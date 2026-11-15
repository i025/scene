from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(12)
scene = Scene('Bright consultation office')
white=(0.88,0.89,0.87); wall=(0.84,0.85,0.83); beige=(0.69,0.60,0.54); floor=(0.37,0.39,0.38); wood=(0.60,0.40,0.25); dark=(0.10,0.11,0.10); metal=(0.34,0.36,0.35)
# Architecture: the open front permits the entrance view.
room=Asset('Room architecture')
room.include('large grey tiled floor',box((7.4,9,.12),center=(0,1,-.08),color=floor))
room.include('white rear wall',box((7.4,.15,3.55),center=(0,5,1.72),color=wall))
room.include('right warm wall',box((.15,9,3.55),center=(3.7,.5,1.72),color=beige))
room.include('left entrance wall',box((.16,3.5,3.55),center=(-3.7,-2.25,1.72),color=white))
room.include('left rear wall',box((.16,1.15,3.55),center=(-3.7,4.48,1.72),color=white))
room.include('ceiling',box((7.4,9,.12),center=(0,.5,3.55),color=(.90,.90,.87)))
room.include('wide ceiling cross beam',box((7.4,.66,.35),center=(0,-1.2,3.37),color=(.88,.88,.85)))
room.include('right skirting',box((.07,8.8,.14),center=(3.59,.55,.09),color=(.27,.28,.27)))
room.include('rear skirting',box((7.2,.06,.14),center=(0,4.88,.09),color=(.28,.29,.28)))
for x in (-2.45,-1.22,0,1.22,2.45): room.include('floor joint x '+str(x),box((.012,9,.003),center=(x,.5,-.017),color=(.30,.32,.31)))
for y in (-3,-1.6,-.2,1.2,2.6,4): room.include('floor joint y '+str(y),box((7.4,.012,.003),center=(0,y,-.016),color=(.30,.32,.31)))
scene.include('Architecture',room)
# Window and glass doors on the left wall.
windows=Asset('Tall glazed doors')
windows.include('blue grey glazing',box((.035,3.0,2.55),center=(-3.68,2.15,1.58),color=(.67,.78,.80)))
for y in (.62,1.62,2.64,3.66): windows.include('vertical white frame '+str(y),box((.11,.075,2.66),center=(-3.60,y,1.58),color=(.93,.94,.91)))
for z in (.28,2.90): windows.include('horizontal white frame '+str(z),box((.11,3.12,.09),center=(-3.60,2.15,z),color=(.93,.94,.91)))
windows.include('blind housing',box((.22,3.16,.16),center=(-3.57,2.15,3.05),color=(.83,.82,.77)))
windows.include('door handle',rod(.022,start=(-3.49,1.57,1.05),end=(-3.49,1.57,1.34),color=metal))
scene.include('Window and door frames',windows)
# Long low timber cabinetry on the right.
cab=Asset('Long timber cabinet')
cab.include('cabinet body',box((.60,6.1,1.18),center=(3.30,2.0,.65),color=wood))
cab.include('cabinet top',box((.68,6.2,.06),center=(3.29,2,1.27),color=(.68,.48,.31)))
for y in (-.95,.25,1.45,2.65,3.85,4.95): cab.include('vertical panel joint '+str(y),box((.008,.018,1.13),center=(2.991,y,.65),color=(.25,.19,.14)))
for z in (.42,.83): cab.include('horizontal drawer reveal '+str(z),box((.009,6.08,.012),center=(2.99,2,z),color=(.29,.22,.16)))
# sparse fine horizontal grain lines
for i in range(22):
 y=random.uniform(-.9,4.9); z=random.uniform(.15,1.2); length=random.uniform(.25,1.1)
 cab.include('wood grain %02d'%i,box((.005,length,.006),center=(2.983,y,z),color=(.48,.30,.18)))
scene.include('Right wall cabinets',cab)
# Desk with broad white modesty panel.
desk=Asset('White office desk')
desk.include('thin wide desktop',box((2.75,1.02,.09),center=(.85,2.52,1.22),color=(.94,.94,.91)))
desk.include('front modesty panel',box((2.53,.08,1.08),center=(.85,2.08,.65),color=(.87,.88,.85)))
for x in (-.35,2.05): desk.include('desk end support '+str(x),box((.10,.85,1.08),center=(x,2.54,.65),color=(.88,.89,.87)))
scene.include('Desk',desk)
# Chair behind desk.
office=Asset('Manager chair')
office.include('high taupe back',fillet_box((.69,.16,1.12),radius=.12,center=(.35,3.22,1.39),color=(.35,.33,.30)))
office.include('upper back cushion',fillet_box((.63,.06,.44),radius=.10,center=(.35,3.12,1.68),color=(.40,.38,.35)))
office.include('seat',fillet_box((.68,.57,.15),radius=.08,center=(.35,3.06,.85),color=(.31,.30,.28)))
scene.include('Desk chair',office)
# Monitor is viewed from its grey back.
monitor=Asset('Monitor and stand')
monitor.include('grey display back',box((.84,.075,.53),center=(1.55,2.75,1.77),color=(.65,.66,.66)))
monitor.include('lower display edge',box((.84,.08,.06),center=(1.55,2.75,1.49),color=(.77,.78,.77)))
monitor.include('stand stem',box((.07,.07,.30),center=(1.55,2.75,1.38),color=(.72,.73,.72)))
monitor.include('stand foot',box((.42,.24,.025),center=(1.55,2.70,1.275),color=(.75,.76,.74)))
scene.include('Monitor',monitor)
# Desk accessories kept small.
items=Asset('Desk accessories')
items.include('paper stack',box((.48,.31,.018),center=(.95,2.31,1.28),color=(.96,.96,.92)))
items.include('cup',fillet_box((.13,.13,.16),radius=.025,center=(.72,2.27,1.37),color=(.31,.38,.33)))
items.include('flower pot',box((.14,.14,.16),center=(.19,2.31,1.36),color=(.67,.67,.60)))
for i in range(7):
 x=.19+random.uniform(-.1,.1); y=2.31+random.uniform(-.07,.07); z=1.58+random.uniform(-.02,.13)
 items.include('flower stem %d'%i,rod(.007,start=(.19,2.31,1.42),end=(x,y,z),color=(.20,.35,.13)))
 items.include('flower blossom %d'%i,ball(.035,center=(x,y,z),color=(.93,.45+.06*(i%3),.69)))
scene.include('Desktop items',items)
# Foreground upholstered visitors chairs, with stems and splayed metal feet.
def visitor(name,x,y,col,angle):
 a=Asset(name)
 a.include('wide padded back',fillet_box((1.03,.21,1.06),radius=.13,center=(x,y,.99),color=col))
 a.include('padded seat',fillet_box((.97,.76,.18),radius=.10,center=(x,y+.34,.57),color=col))
 for side in (-1,1):
  a.include('upholstered arm '+str(side),fillet_box((.18,.72,.40),radius=.09,center=(x+side*.53,y+.32,.76),color=col))
 a.include('central chrome column',rod(.045,start=(x,y+.26,.12),end=(x,y+.26,.56),color=metal))
 for k in range(4):
  t=math.pi/4+k*math.pi/2
  a.include('splayed foot %d'%k,rod(.037,start=(x,y+.26,.12),end=(x+.64*math.cos(t),y+.26+.64*math.sin(t),.045),color=metal))
 a.turn('+z',angle,pivot=(x,y+.2,0))
 scene.include(name,a)
visitor('Left lime visitor chair',.25,.02,(.61,.64,.08),-3)
visitor('Right olive visitor chair',1.98,.08,(.37,.42,.035),-12)
# Low heater on back wall.
heater=Asset('Low white heater')
heater.include('heater casing',box((1.12,.27,.82),center=(-2.05,4.73,.47),color=(.88,.89,.87)))
heater.include('dark top slot',box((.83,.04,.012),center=(-2.05,4.57,.89),color=(.18,.19,.18)))
heater.include('lower grille',box((.87,.015,.16),center=(-2.05,4.58,.22),color=(.55,.57,.57)))
for i in range(9): heater.include('grille bar %d'%i,box((.008,.009,.14),center=(-2.44+i*.098,4.565,.22),color=(.79,.80,.78)))
scene.include('Heater',heater)
# Framed abstract floral artwork, made as layered editable shapes.
art=Asset('Framed abstract flower painting')
art.include('dark outer frame',box((.84,.09,1.10),center=(.43,4.89,2.40),color=(.22,.13,.09)))
art.include('canvas',box((.74,.025,1.00),center=(.43,4.83,2.40),color=(.18,.16,.14)))
for i in range(5):
 x=.14+i*.14
 art.include('painted vertical line %d'%i,box((.025,.012,.92),center=(x,4.81,2.40),color=(.40,.25,.17)))
for i in range(12):
 x=.43+random.uniform(-.25,.25); z=2.4+random.uniform(-.38,.38)
 petal=ball(.12,center=(x,4.79,z),color=random.choice([(0.76,.67,.52),(.49,.37,.22),(.73,.40,.17),(.55,.57,.47)]))
 petal.resize((.7,.12,1.25)); art.include('abstract petal %d'%i,petal)
scene.include('Wall artwork',art)
# Two layered potted trees; leaves are individual flattened ellipsoids.
def plant(name,x,y,scale):
 a=Asset(name)
 a.include('dark planter',fillet_box((.52*scale,.52*scale,.53*scale),radius=.07*scale,center=(x,y,.265*scale),color=(.08,.10,.085)))
 for j in range(4):
  dx=random.uniform(-.17,.17)*scale; dy=random.uniform(-.13,.13)*scale
  end=(x+dx,y+dy,1.85*scale)
  a.include('slender trunk %d'%j,rod(.025*scale,start=(x,y,.48*scale),end=end,color=(.24,.19,.12)))
 for j in range(13):
  t=random.uniform(0,6.283); h=random.uniform(.9,2.12)*scale; reach=random.uniform(.20,.65)*scale
  ex=x+math.cos(t)*reach; ey=y+math.sin(t)*reach
  a.include('branch %d'%j,rod(.009*scale,start=(x,y,h*.65),end=(ex,ey,h),color=(.24,.21,.13)))
  for k in range(4):
   lx=ex+random.uniform(-.17,.17)*scale; ly=ey+random.uniform(-.17,.17)*scale; lz=h+random.uniform(-.12,.17)*scale
   leaf=ball(.13*scale,center=(lx,ly,lz),color=random.choice([(.12,.30,.08),(.17,.38,.09),(.24,.44,.12),(.10,.25,.08)]))
   leaf.resize((1.0,.43,.22)); leaf.turn('+z',random.uniform(0,180)); leaf.turn('+y',random.uniform(-40,40)); a.include('leaf %d %d'%(j,k),leaf)
 scene.include(name,a)
plant('Rear potted tree',-1.05,4.05,.95)
plant('Large foreground plant',-3.45,-2.40,1.30)
# Bright square ceiling panel.
scene.include('Ceiling light panel',box((1.0,.85,.025),center=(-.35,2.1,3.47),color=(1,1,.96)))
realize(scene)
# Add soft light after realization.
if bpy.context.scene.world is None: bpy.context.scene.world=bpy.data.worlds.new('Office world')
bpy.context.scene.world.use_nodes=True
bg=bpy.context.scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.80,0.85,0.89,1); bg.inputs['Strength'].default_value=.45
set_view((0,-7.8,2.35),(0,2.4,1.55),lens=30,sensor=36)
area_emitter((-3.1,1.2,2.8),power=650,size=4.0,target=(0,2,1.0),color=(.83,.90,1.0))
area_emitter((-.3,2.0,3.35),power=500,size=2.3,target=(0,2,0),color=(1.0,.96,.89))
area_emitter((1,-4,3.0),power=300,size=5,target=(0,2,1),color=(1,1,1))