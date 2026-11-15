from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(17)
scene = Scene('Bright office')
white=(0.86,0.87,0.85); wall=(0.84,0.85,0.82); beige=(0.68,0.58,0.51); floor=(0.31,0.34,0.33); trim=(0.91,0.92,0.89); wood=(0.53,0.32,0.18); dark=(0.10,0.105,0.10); metal=(0.35,0.37,0.36)
def add(name,node): scene.include(name,node)
def block(name,size,center,color): add(name,box(size=size,center=center,color=color))
def rounded(name,size,center,color,r=.04): add(name,fillet_box(size=size,radius=min(r,min(size)*.45),center=center,color=color))
# Room shell, kept open toward the camera
block('large gray tiled floor',(7.1,10,.12),(0,0,-.06),floor)
block('back white wall',(7.0,.14,3.55),(0,4.0,1.77),wall)
block('right warm wall',(.14,9,3.55),(3.5,-.45,1.77),beige)
block('left foreground wall',(.18,4.2,3.55),(-3.5,-2.85,1.77),white)
block('left rear window wall',(.16,1.0,3.55),(-3.5,3.5,1.77),white)
block('ceiling',(7.1,8,.12),(0,.1,3.55),(0.85,0.86,0.83))
block('wide ceiling cross beam',(7.0,.52,.38),(0,-1.65,3.35),(0.86,0.87,0.84))
block('right ceiling edge trim',(.12,8,.12),(3.42,.1,3.43),trim)
block('back skirting',(7,.08,.13),(0,3.9,.065),(.30,.31,.29))
block('left skirting',(.08,4.2,.13),(-3.39,-2.8,.065),(.30,.31,.29))
# Quiet floor tile seams
for x in [-2.4,-1.2,0,1.2,2.4]: block('floor tile seam x '+str(x),(.012,8,.005),(x,0,.003),(.28,.30,.29))
for y in [-3,-1.8,-.6,.6,1.8,3.0]: block('floor tile seam y '+str(y),(7,.012,.005),(0,y,.004),(.28,.30,.29))
# Glazed door/window in left wall
block('window bright glazing',(.035,2.4,2.65),(-3.43,1.32,1.50),(.72,.83,.85))
for y in [.12,1.28,2.52]: block('window vertical white frame '+str(y),(.12,.085,2.75),(-3.37,y,1.52),trim)
for z in [.17,2.88]: block('window horizontal white frame '+str(z),(.12,2.48,.10),(-3.37,1.32,z),trim)
block('window narrow mullion',(.13,.045,2.65),(-3.34,1.55,1.52),(.82,.85,.83))
block('window blind headrail',(.20,2.55,.12),(-3.36,1.30,3.02),(.67,.58,.48))
block('window sill',(.25,2.55,.08),(-3.35,1.32,.15),trim)
block('wall switch plate',(.035,.22,.23),(-3.38,-.72,1.22),(.75,.76,.74))
block('wall switch',(.04,.11,.13),(-3.35,-.72,1.22),(.87,.87,.85))
# Ceiling light
block('ceiling square light frame',(1.03,.85,.045),(-.35,1.1,3.46),(.75,.76,.73))
block('ceiling luminous diffuser',(.90,.72,.035),(-.35,1.1,3.43),(1,1,.96))
# Long right wall cabinetry, continuing beyond the frame
block('wood cabinet main body',(.58,6.6,1.35),(3.16,.35,.71),wood)
block('wood cabinet top',(.67,6.6,.055),(3.11,.35,1.41),(.57,.36,.21))
for i in range(4):
 z=.23+i*.345
 block('cabinet horizontal joint '+str(i),(.014,6.58,.014),(2.86,.35,z),(.24,.16,.10))
for y in [-2.7,-.65,1.4,3.45]: block('cabinet vertical joint '+str(y),(.014,.015,1.34),(2.85,y,.72),(.27,.17,.10))
# understated wood streaks on cabinet fronts
for i in range(60):
 y=random.uniform(-2.9,3.55); z=random.uniform(.12,1.34); length=random.uniform(.15,.8)
 block('wood grain %02d'%i,(.006,length,.006),(2.847,y,z),random.choice([(.46,.27,.14),(.61,.39,.23),(.49,.29,.16)]))
# back wall low white heating unit
rounded('heater body',(1.28,.30,.95),(-2.00,3.70,.55),(.84,.86,.84),.025)
block('heater top dark vent',(1.05,.12,.025),(-2,3.53,1.03),(.16,.18,.17))
block('heater lower vent recess',(1.02,.018,.18),(-2,3.535,.19),(.45,.48,.46))
for i in range(12): block('heater grille bar %02d'%i,(.025,.018,.16),(-2.47+i*.085,3.52,.19),(.73,.75,.73))
for x in [-2.48,-1.52]: block('heater foot '+str(x),(.19,.26,.10),(x,3.65,.06),(.78,.79,.77))
# desk: top, modesty panel, side supports
rounded('white desktop',(2.65,1.04,.095),(1.05,2.15,.82),(.91,.92,.89),.035)
block('desk front modesty panel',(2.48,.09,.69),(1.05,1.69,.43),(.84,.86,.83))
block('desk right support',(.09,.93,.72),(2.26,2.14,.40),(.85,.87,.84))
block('desk left support',(.09,.93,.72),(-.16,2.14,.40),(.85,.87,.84))
# executive chair behind desk
rounded('executive chair tall back',(.70,.19,1.02),(.84,2.95,1.03),(.33,.32,.29),.09)
rounded('executive chair upper padded section',(.62,.04,.36),(.84,2.835,1.31),(.38,.37,.34),.018)
rounded('executive chair seat',(.67,.58,.13),(.84,2.65,.55),(.31,.30,.27),.05)
add('executive chair central post',rod(.035,start=(.84,2.75,.10),end=(.84,2.75,.54),color=metal))
# monitor rear panel faces viewer
rounded('monitor large light gray back',(.78,.09,.55),(1.95,2.30,1.29),(.58,.60,.59),.025)
block('monitor bottom dark edge',(.76,.10,.028),(1.95,2.30,1.03),(.33,.35,.34))
add('monitor angled support',rod(.035,start=(1.95,2.24,.85),end=(1.95,2.29,1.12),color=(.66,.68,.66)))
rounded('monitor base',(.42,.27,.025),(1.95,2.18,.88),(.68,.70,.68),.01)
# small desktop objects
for i in range(3): block('paper sheet '+str(i),(.52,.29,.009),(.62+i*.02,1.98+i*.03,.877+i*.009),(.94,.94,.91))
add('desk cup',rod(.075,length=.16,center=(1.34,1.99,.96),color=(.30,.35,.30)))
add('small flower vase',rod(.065,length=.18,center=(.36,1.99,.96),color=(.53,.63,.57)))
for i in range(8):
 x=.36+random.uniform(-.12,.12); y=1.99+random.uniform(-.09,.09); z=1.13+random.uniform(0,.15)
 add('flower stem %d'%i,rod(.006,start=(.36,1.99,1.02),end=(x,y,z),color=(.19,.35,.13)))
 add('flower blossom %d'%i,ball(.035,center=(x,y,z),color=random.choice([(.85,.36,.56),(.92,.76,.84),(.94,.90,.85)])))
# Visitor chairs. Local x is width and local y is depth; rotate complete chair around its center.
def visitor(name,cx,cy,color,angle):
 a=Asset(name)
 def inc(n,obj): a.include(n,obj)
 inc('thick upholstered back',fillet_box((1.05,.25,1.08),radius=.11,center=(cx,cy+.25,1.02),color=color))
 inc('padded seat',fillet_box((.94,.78,.18),radius=.075,center=(cx,cy-.12,.54),color=color))
 for s in [-1,1]:
  inc('wrapped arm '+str(s),fillet_box((.15,.72,.38),radius=.07,center=(cx+s*.53,cy-.09,.70),color=color))
 inc('chrome center post',rod(.045,start=(cx,cy,.08),end=(cx,cy,.52),color=(.43,.46,.45)))
 for dx,dy in [(-.65,-.40),(.65,-.40),(-.57,.38),(.57,.38)]:
  inc('splayed metal foot '+str((dx,dy)),rod(.035,start=(cx,cy,.09),end=(cx+dx,cy+dy,.035),color=(.32,.35,.34)))
 a.turn('+z',angle,pivot=(cx,cy,0)); scene.include(name,a)
visitor('left chartreuse visitor chair',.13,-.05,(.60,.63,.055),-3)
visitor('right olive visitor chair',2.00,.02,(.35,.40,.035),-13)
# Framed abstract floral artwork
block('art dark outer frame',(.83,.075,1.12),(.89,3.89,2.46),(.20,.11,.07))
block('art inner gold edge',(.76,.02,1.05),(.89,3.84,2.46),(.55,.35,.18))
block('art dark canvas',(.70,.018,.99),(.89,3.82,2.46),(.12,.105,.09))
for i in range(14):
 x=.61+random.random()*.56; z=2.06+random.random()*.82
 add('painted abstract stem %d'%i,rod(.009,start=(x,3.80,2.10),end=(x+random.uniform(-.15,.15),3.80,z),color=random.choice([(.61,.32,.12),(.72,.57,.36),(.42,.47,.37)])))
 leaf=ball(random.uniform(.045,.10),center=(x,3.78,z),color=random.choice([(.72,.61,.45),(.75,.37,.13),(.44,.50,.39),(.83,.75,.61)])); leaf.resize((1,.16,1.5)); add('art abstract leaf %d'%i,leaf)
# Plants with individually editable trunks and leaves
def plant(name,x,y,scale,foreground=False):
 a=Asset(name)
 potcol=(.075,.085,.075)
 a.include('black plant pot',rod(.22*scale,length=.43*scale,center=(x,y,.22*scale),color=potcol))
 a.include('pot rim',rod(.235*scale,length=.055*scale,center=(x,y,.43*scale),color=(.11,.12,.10)))
 for b in range(7):
  ang=b*2.4; ex=x+math.cos(ang)*random.uniform(.13,.35)*scale; ey=y+math.sin(ang)*random.uniform(.13,.35)*scale; ez=random.uniform(1.25,1.95)*scale
  a.include('branch %02d'%b,rod(.018*scale,start=(x+random.uniform(-.06,.06)*scale,y+random.uniform(-.06,.06)*scale,.39*scale),end=(ex,ey,ez),color=(.27,.19,.11)))
  for j in range(13):
   t=random.uniform(.45,1.0); lx=x+(ex-x)*t+random.uniform(-.25,.25)*scale; ly=y+(ey-y)*t+random.uniform(-.24,.24)*scale; lz=.4*scale+(ez-.4*scale)*t+random.uniform(-.1,.12)*scale
   leaf=ball(.105*scale,center=(lx,ly,lz),color=random.choice([(.09,.25,.055),(.13,.35,.07),(.20,.42,.09),(.10,.30,.07)])); leaf.resize((1.45,.48,.42)); leaf.turn('+z',random.uniform(0,180)); leaf.turn('+y',random.uniform(-35,35)); a.include('leaf %02d %02d'%(b,j),leaf)
 scene.include(name,a)
plant('tall plant beside desk',-1.02,3.12,1.0)
plant('large foreground plant',-3.0,-3.1,1.28,True)
realize(scene)
# Camera and lighting are created only after realization.
set_view((0,-8.9,2.45),(0,2.0,1.48),lens=31,sensor=36)
if bpy.context.scene.world is None: bpy.context.scene.world=bpy.data.worlds.new('Office world')
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.72,0.77,0.78,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
area_emitter((-3.1,.5,2.8),power=500,size=4,target=(.5,1.5,.8),color=(.85,.92,1.0))
area_emitter((-.35,1.1,3.30),power=300,size=2.0,target=(0,1,0),color=(1,.96,.88))
area_emitter((0,-4,3.4),power=320,size=5,target=(.3,2,1),color=(1,.98,.94))
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=48
bpy.context.scene.cycles.use_denoising=True
bpy.context.scene.view_settings.view_transform='AgX'
