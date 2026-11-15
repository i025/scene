from sceneact import *
import bpy, random
random.seed(11)
scene = Scene('Woodworking room')
wood=(0.16,0.085,0.043)
frame=(0.21,0.115,0.060)
panel=(0.235,0.135,0.072)
edge=(0.105,0.057,0.029)
gold=(0.52,0.315,0.125)
metal=(0.105,0.10,0.085)
wall=(0.72,0.79,0.75)
glass=(0.52,0.69,0.66)

def add(parent,name,size,center,color):
    parent.include(name,box(size=size,center=center,color=color))

def framed_panel(parent,name,axis,pos,u,z,width,height,depth=0.025):
    rail=0.055
    if axis=='y':
        add(parent,name+' inset',(width-0.07,depth,height-0.07),(u,pos,z),panel)
        for side in (-1,1):
            add(parent,name+' stile '+str(side),(rail,depth+0.02,height),(u+side*(width-rail)/2,pos-0.012,z),frame)
            add(parent,name+' rail '+str(side),(width-2*rail,depth+0.02,rail),(u,pos-0.012,z+side*(height-rail)/2),frame)
    else:
        add(parent,name+' inset',(depth,width-0.07,height-0.07),(pos,u,z),panel)
        for side in (-1,1):
            add(parent,name+' stile '+str(side),(depth+0.02,rail,height),(pos+0.012,u+side*(width-rail)/2,z),frame)
            add(parent,name+' rail '+str(side),(depth+0.02,width-2*rail,rail),(pos+0.012,u,z+side*(height-rail)/2),frame)

def knob(parent,name,center):
    parent.include(name,ball(0.023,center=center,color=metal))

def drawer(parent,name,x,y,z,w,h):
    add(parent,name+' face',(w,0.035,h),(x,y,z),frame)
    add(parent,name+' inset',(w-0.045,0.018,h-0.04),(x,y-0.023,z),panel)
    add(parent,name+' pull',(0.13,0.027,0.016),(x,y-0.047,z),metal)
    for dx in (-0.06,0.06):
        add(parent,name+' pull end '+str(dx),(0.017,0.027,0.03),(x+dx,y-0.047,z+0.008),metal)

floor=Asset('Long plank wood floor')
for i in range(21):
    x=-5.7+i*0.57
    c=random.uniform(-0.028,0.028)
    add(floor,'floorboard %02d'%i,(0.566,11,0.045),(x,0,-0.035),(0.43+c,0.275+c,0.145+c))
    for j in range(4):
        y=-4.7+j*2.8+(i%2)*1.3
        add(floor,'end joint %02d %02d'%(i,j),(0.565,0.006,0.002),(x,y,-0.011),(0.29,0.18,0.09))
scene.include('floor',floor)
add(scene,'back plaster wall',(11,0.12,4.2),(0,3.15,2.1),wall)
add(scene,'left plaster wall',(0.12,7,4.2),(-4.8,-0.3,2.1),wall)
add(scene,'back baseboard',(11,0.07,0.20),(0,3.06,0.1),edge)
add(scene,'left baseboard',(0.07,7,0.20),(-4.73,-0.3,0.1),edge)

island=Asset('Central wood work island')
add(island,'honey oak thick worktop',(3.85,1.75,0.12),(0,-0.45,0.99),gold)
add(island,'worktop long edge',(3.85,0.018,0.105),(0,-1.333,0.987),(0.46,0.27,0.105))
add(island,'worktop near end edge',(0.018,1.75,0.105),(1.93,-0.45,0.987),(0.47,0.28,0.11))
add(island,'cabinet body',(2.87,1.30,0.69),(-0.32,-0.45,0.49),wood)
for x in (-1.73,1.08):
    for y in (-1.10,0.20):
        add(island,'corner post %.2f %.2f'%(x,y),(0.105,0.105,0.87),(x,y,0.435),frame)
add(island,'long lower side rail',(2.79,0.07,0.105),(-0.32,-1.13,0.18),frame)
add(island,'long upper side rail',(2.79,0.07,0.10),(-0.32,-1.13,0.88),frame)
for i,x in enumerate((-1.25,-0.32,0.61)):
    drawer(island,'island drawer %d'%i,x,-1.145,0.77,0.83,0.18)
    framed_panel(island,'island cupboard door %d'%i,'y',-1.15,x,0.445,0.83,0.48)
    knob(island,'island door knob %d'%i,(x+0.28,-1.20,0.48))
    for z in (0.31,0.55):
        add(island,'island hinge %d %.2f'%(i,z),(0.014,0.02,0.09),(x-0.375,-1.19,z),(0.50,0.50,0.46))
framed_panel(island,'island near end panel','x',1.135,-0.45,0.49,1.22,0.66,0.035)
add(island,'end bottom rail',(0.08,1.30,0.12),(1.14,-0.45,0.19),frame)
scene.include('island',island)

left=Asset('Left rear glass hutch')
add(left,'lower cabinet body',(2.48,0.65,0.93),(-2.30,2.70,0.48),wood)
add(left,'lower plinth',(2.58,0.72,0.10),(-2.30,2.68,0.08),edge)
add(left,'counter molding',(2.58,0.73,0.09),(-2.30,2.67,0.97),frame)
for i,x in enumerate((-3.20,-2.60,-2.00,-1.40)):
    drawer(left,'left hutch drawer %d'%i,x,2.35,0.82,0.57,0.17)
    framed_panel(left,'left hutch lower door %d'%i,'y',2.34,x,0.45,0.56,0.54)
    knob(left,'left lower handle %d'%i,(x+0.19,2.29,0.48))
add(left,'upper cabinet back',(2.48,0.08,2.20),(-2.30,3.02,2.11),(0.42,0.57,0.53))
for x in (-3.56,-2.94,-2.30,-1.66,-1.04):
    add(left,'upper vertical frame %.2f'%x,(0.075,0.12,2.22),(x,2.48,2.11),frame)
for z in (1.01,3.20):
    add(left,'upper horizontal frame %.2f'%z,(2.60,0.12,0.09),(-2.30,2.48,z),frame)
for i,x in enumerate((-3.25,-2.62,-1.98,-1.34)):
    add(left,'glass panel %d'%i,(0.54,0.025,2.06),(x,2.52,2.11),glass)
    add(left,'glass crossbar %d'%i,(0.54,0.09,0.055),(x,2.45,1.90),frame)
    add(left,'upper handle %d'%i,(0.018,0.025,0.11),(x+0.23,2.42,1.43),metal)
scene.include('left hutch',left)

right=Asset('Right rear long cabinet')
add(right,'lower cabinet body',(3.20,0.68,0.92),(1.69,2.72,0.48),wood)
add(right,'lower plinth',(3.32,0.75,0.10),(1.69,2.68,0.07),edge)
add(right,'dark long counter',(3.36,0.78,0.09),(1.69,2.64,0.97),(0.13,0.075,0.04))
for i,x in enumerate((0.39,1.04,1.69,2.34,2.99)):
    drawer(right,'right drawer %d'%i,x,2.36,0.79,0.60,0.20)
    framed_panel(right,'right lower door %d'%i,'y',2.35,x,0.43,0.60,0.52)
    knob(right,'right door knob %d'%i,(x+0.20,2.30,0.44))
for x in (0.02,3.36):
    add(right,'full height end board %.2f'%x,(0.12,0.78,3.42),(x,2.70,1.71),frame)
add(right,'upper cabinet back',(3.20,0.08,1.15),(1.69,3.03,2.81),(0.30,0.41,0.37))
for x in (0.08,0.72,1.36,2.00,2.64,3.30):
    add(right,'upper vertical stile %.2f'%x,(0.075,0.13,1.27),(x,2.50,2.83),frame)
for z in (2.22,3.43):
    add(right,'upper rail %.2f'%z,(3.3,0.13,0.10),(1.69,2.50,z),frame)
for i,x in enumerate((0.40,1.04,1.68,2.32,2.97)):
    add(right,'upper glass door %d'%i,(0.56,0.025,1.13),(x,2.54,2.83),glass)
    add(right,'upper cabinet pull %d'%i,(0.015,0.025,0.105),(x+0.24,2.42,2.58),metal)
scene.include('right hutch',right)
add(scene,'separating wall strip',(0.21,0.08,3.7),(-0.88,3.06,1.85),wall)
add(scene,'vertical timber between hutches',(0.12,0.13,3.7),(-0.72,2.98,1.85),frame)

realize(scene)
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if not bs:
        continue
    bs.inputs['Roughness'].default_value=0.48
    color=tuple(bs.inputs['Base Color'].default_value)
    if color[0]>color[1]*1.2 and color[1]>color[2]*1.15 and color[0]>0.14:
        nodes=mat.node_tree.nodes
        links=mat.node_tree.links
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=3.8
        tex.inputs['Detail'].default_value=2.0
        tex.inputs['Roughness'].default_value=0.65
        coord=nodes.new('ShaderNodeTexCoord')
        mapping=nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(1.0,18.0,5.0)
        links.new(coord.outputs['Generated'],mapping.inputs[0])
        links.new(mapping.outputs[0],tex.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=0.18
        ramp.color_ramp.elements[0].color=(color[0]*0.72,color[1]*0.72,color[2]*0.72,1)
        ramp.color_ramp.elements[1].position=0.82
        ramp.color_ramp.elements[1].color=(min(color[0]*1.12,1),min(color[1]*1.12,1),min(color[2]*1.12,1),1)
        links.new(tex.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
if bpy.context.scene.world is None:
    bpy.context.scene.world=bpy.data.worlds.new('Room world')
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.72,0.79,0.78,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.38
set_view((6.8,-8.8,4.2),(-0.15,0.40,1.0),lens=52)
area_emitter((-3.8,-4.0,6.8),power=1000,size=5.0,target=(0,0,0.5),color=(1.0,0.88,0.73))
area_emitter((2.8,0.0,5.0),power=300,size=4.0,target=(0,1,1),color=(0.82,0.9,1.0))
bpy.context.scene.render.resolution_x=1280
bpy.context.scene.render.resolution_y=960
bpy.context.scene.render.resolution_percentage=100