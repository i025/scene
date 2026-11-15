from sceneact import *
import bpy, random
random.seed(7)
scene = Scene('Old woodworking room')
wall=(.64,.73,.69); wood=(.17,.095,.050); frame=(.22,.125,.065); dark=(.105,.058,.030); panel=(.145,.078,.039); honey=(.52,.32,.14); glass=(.46,.64,.62); metal=(.075,.067,.052)
room=Asset('Room architecture')
room.include('back pale plaster wall',box((18,.12,5),center=(0,3.2,2.45),color=wall))
room.include('left wall',box((.12,9,5),center=(-4.3,-1.2,2.45),color=wall))
room.include('back wood baseboard',box((12,.09,.20),center=(0,3.1,.1),color=dark))
room.include('left wood baseboard',box((.09,8,.20),center=(-4.22,-.8,.1),color=dark))
scene.include('architecture',room)
floor=Asset('Aged narrow plank floor')
for i in range(34):
 x=-4.25+i*.29; y=-6-(i%3)*.53; j=0
 while y<3.1:
  length=min(2.05+random.uniform(-.25,.25),3.15-y)
  if length<=.05: break
  c=random.uniform(-.025,.025)
  floor.include('plank %02d %02d'%(i,j),box((.285,length-.008,.045),center=(x,y+length/2,-.025),color=(.36+c,.245+c,.145+c)))
  y+=length; j+=1
scene.include('floorboards',floor)
island=Asset('Central work island')
island.include('thick honey oak worktop',fillet_box((2.55,3.55,.14),radius=.018,center=(0,-.42,1.00),color=honey))
island.include('dark cabinet carcass',box((1.95,2.95,.78),center=(0,-.40,.48),color=wood))
for x in (-.91,.91):
 for y in (-1.78,.98):
  island.include('corner leg %.2f %.2f'%(x,y),box((.13,.14,.88),center=(x,y,.44),color=frame))
yfront=-1.91
island.include('near end recessed panel',box((1.66,.025,.57),center=(0,yfront,.48),color=panel))
for x in (-.84,.84): island.include('near end vertical frame %.2f'%x,box((.11,.07,.72),center=(x,yfront-.025,.48),color=frame))
for z in (.17,.79): island.include('near end horizontal rail %.2f'%z,box((1.75,.07,.10),center=(0,yfront-.025,z),color=frame))
xside=-1.0
for k,y in enumerate((-1.34,-.38,.58)):
 island.include('side inset door %d'%k,box((.025,.80,.47),center=(xside,y,.40),color=panel))
 for dy in (-.42,.42): island.include('side door stile %d %.2f'%(k,dy),box((.055,.075,.53),center=(xside-.015,y+dy,.40),color=frame))
 for z in (.15,.65): island.include('side door rail %d %.2f'%(k,z),box((.055,.88,.065),center=(xside-.015,y,z),color=frame))
 island.include('side drawer %d'%k,box((.045,.84,.16),center=(xside-.012,y,.75),color=frame))
 island.include('drawer dark pull %d'%k,rod(.018,start=(xside-.055,y-.085,.75),end=(xside-.055,y+.085,.75),color=metal))
 island.include('door knob %d'%k,ball(.023,center=(xside-.06,y+.27,.43),color=metal))
 for z in (.24,.52): island.include('door hinge %d %.2f'%(k,z),box((.018,.028,.12),center=(xside-.05,y-.39,z),color=(.38,.38,.34)))
scene.include('island',island)
left=Asset('Left tall glass cabinet')
lx=-2.20
left.include('cabinet dark back',box((2.65,.53,3.90),center=(lx,2.84,1.95),color=dark))
left.include('lower body',box((2.65,.67,1.10),center=(lx,2.75,.57),color=wood))
left.include('lower toe plinth',box((2.74,.73,.13),center=(lx,2.74,.08),color=dark))
left.include('lower ledge',box((2.74,.72,.10),center=(lx,2.72,1.13),color=frame))
for k in range(4):
 x=lx-.975+k*.65
 left.include('lower drawer %d'%k,box((.60,.045,.21),center=(x,2.395,1.00),color=frame))
 left.include('lower drawer pull %d'%k,rod(.016,start=(x-.075,2.36,1.00),end=(x+.075,2.36,1.00),color=metal))
 left.include('lower inset door %d'%k,box((.56,.045,.67),center=(x,2.39,.49),color=panel))
 for dx in (-.285,.285): left.include('lower door stile %d %.2f'%(k,dx),box((.055,.06,.72),center=(x+dx,2.36,.49),color=frame))
 for z in (.15,.83): left.include('lower door rail %d %.2f'%(k,z),box((.60,.06,.06),center=(x,2.36,z),color=frame))
 left.include('lower door knob %d'%k,ball(.022,center=(x+.19,2.31,.51),color=metal))
left.include('pale cabinet interior',box((2.45,.025,2.65),center=(lx,3.09,2.52),color=(.43,.57,.53)))
for z in (1.58,2.24,2.90,3.56): left.include('interior shelf %.2f'%z,box((2.43,.43,.035),center=(lx,2.82,z),color=frame))
for k in range(4):
 x=lx-.975+k*.65
 left.include('glass door pane %d'%k,box((.55,.025,2.58),center=(x,2.49,2.49),color=glass,opacity=.48))
 for dx in (-.30,.30): left.include('glass door stile %d %.2f'%(k,dx),box((.075,.09,2.75),center=(x+dx,2.43,2.52),color=frame))
 for z in (1.18,1.88,2.58,3.28,3.89): left.include('glass door rail %d %.2f'%(k,z),box((.64,.09,.075),center=(x,2.43,z),color=frame))
 left.include('glass door pull %d'%k,rod(.012,start=(x+.23,2.37,1.60),end=(x+.23,2.37,1.75),color=metal))
scene.include('left tall cabinet',left)
right=Asset('Right long built in cabinet')
rx=1.22
right.include('lower cabinet body',box((3.75,.69,1.13),center=(rx,2.76,.59),color=wood))
right.include('lower base molding',box((3.85,.76,.13),center=(rx,2.74,.10),color=dark))
right.include('deep brown counter',box((3.90,.82,.11),center=(rx,2.70,1.20),color=dark))
for k in range(5):
 x=rx-1.50+k*.75
 right.include('lower drawer %d'%k,box((.69,.05,.24),center=(x,2.39,.99),color=frame))
 right.include('lower drawer pull %d'%k,rod(.017,start=(x-.08,2.35,.99),end=(x+.08,2.35,.99),color=metal))
 right.include('lower door inset %d'%k,box((.66,.035,.68),center=(x,2.395,.51),color=panel))
 for dx in (-.33,.33): right.include('lower door frame %d %.2f'%(k,dx),box((.055,.06,.71),center=(x+dx,2.36,.51),color=frame))
 for z in (.18,.84): right.include('lower door rail %d %.2f'%(k,z),box((.70,.06,.065),center=(x,2.36,z),color=frame))
right.include('right full height end panel',box((.18,.76,4),center=(3.16,2.76,2),color=wood))
right.include('upper cupboard dark back',box((3.70,.45,1.85),center=(rx,2.91,3.07),color=dark))
right.include('upper cupboard bottom ledge',box((3.83,.58,.11),center=(rx,2.84,2.15),color=frame))
for k in range(5):
 x=rx-1.47+k*.735
 right.include('upper glass pane %d'%k,box((.63,.025,1.68),center=(x,2.65,3.05),color=glass,opacity=.52))
 for dx in (-.34,.34): right.include('upper door stile %d %.2f'%(k,dx),box((.075,.08,1.80),center=(x+dx,2.59,3.05),color=frame))
 for z in (2.19,3.91): right.include('upper door rail %d %.2f'%(k,z),box((.73,.08,.08),center=(x,2.59,z),color=frame))
 right.include('upper handle %d'%k,rod(.012,start=(x+.26,2.54,2.56),end=(x+.26,2.54,2.70),color=metal))
scene.include('right long cabinet',right)
scene.include('between cabinets upright',box((.13,.12,4),center=(-.70,3.04,2),color=frame))
realize(scene)
for mat in list(bpy.data.materials):
 if not mat.use_nodes or not mat.node_tree: continue
 bs=mat.node_tree.nodes.get('Principled BSDF')
 if not bs: continue
 rgba=tuple(bs.inputs['Base Color'].default_value)
 if rgba[0]>rgba[1]*1.12 and rgba[1]>rgba[2]*1.12 and rgba[0]>.12:
  nt=mat.node_tree
  tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3.8; tex.inputs['Detail'].default_value=2.0; tex.inputs['Roughness'].default_value=.7
  mapping=nt.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(5.0,.65,4.0)
  coord=nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(coord.outputs['Generated'],mapping.inputs[0]); nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
  ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=(rgba[0]*.72,rgba[1]*.72,rgba[2]*.72,1); ramp.color_ramp.elements[1].position=.82; ramp.color_ramp.elements[1].color=(min(rgba[0]*1.1,1),min(rgba[1]*1.1,1),min(rgba[2]*1.1,1),1)
  nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']); bs.inputs['Roughness'].default_value=.48
if bpy.context.scene.world is None: bpy.context.scene.world=bpy.data.worlds.new('Soft ambient world')
bpy.context.scene.world.use_nodes=True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.72,.69,1)
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
set_view((-3.9,-6.2,3.2),(0,.15,1.25),lens=37)
area_emitter((-4,-3,5.5),power=900,size=5,target=(0,0,.5),color=(1,.91,.77))
area_emitter((1,-1,4.8),power=450,size=4,target=(0,1,1),color=(.8,.9,1))