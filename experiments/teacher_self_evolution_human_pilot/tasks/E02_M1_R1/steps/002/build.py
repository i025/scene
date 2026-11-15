from sceneact import *
import bpy
import random

random.seed(12)
scene = Scene('Woodworking interior')
wall = (0.73, 0.82, 0.79)
dark = (0.19, 0.115, 0.068)
dark_edge = (0.135, 0.078, 0.045)
midwood = (0.24, 0.15, 0.09)
panelwood = (0.215, 0.13, 0.075)
topwood = (0.57, 0.38, 0.19)
glass = (0.48, 0.65, 0.62)
metal = (0.12, 0.12, 0.105)

def addbox(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def bar(parent, name, a, b, radius=0.012, color=metal):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

floor = Asset('Warm plank floor')
for j in range(28):
    y = -3.9 + j * 0.29
    x = -5.1 - (j % 3) * 0.72
    k = 0
    while x < 6.0:
        length = min(2.15 + random.uniform(-0.3, 0.3), 6.1-x)
        if length > 0.08:
            shade = random.uniform(0.91, 1.09)
            addbox(floor, 'board_%02d_%02d' % (j,k), (length-0.009,0.284,0.07), (x+length/2,y,-0.045), (0.47*shade,0.30*shade,0.17*shade))
        x += length
        k += 1
scene.include('floor', floor)

architecture = Asset('Back wall and skirting')
addbox(architecture, 'back wall', (0.12,8.2,3.8), (-3.19,0,1.9), wall)
addbox(architecture, 'back wall skirting', (0.10,8.0,0.22), (-3.09,0,0.11), dark)
scene.include('architecture', architecture)

island = Asset('Central work island')
addbox(island, 'cabinet carcass', (2.70,1.38,0.74), (-0.12,-0.10,0.47), dark)
addbox(island, 'thick honey oak worktop', (3.35,1.94,0.14), (0,0.09,0.91), topwood)
addbox(island, 'worktop lower edge', (3.32,1.92,0.025), (0,0.09,0.837), (0.43,0.27,0.13))
for x in (-1.42,1.18):
    for y in (-0.74,0.54):
        addbox(island, 'corner post %.2f %.2f' % (x,y), (0.10,0.10,0.87), (x,y,0.435), midwood)
addbox(island, 'side lower rail', (2.55,0.055,0.12), (-0.12,-0.811,0.16), midwood)
addbox(island, 'side upper rail', (2.55,0.055,0.09), (-0.12,-0.811,0.77), midwood)
for x in (-1.0,-0.12,0.76):
    addbox(island, 'side divider %.2f' % x, (0.065,0.06,0.60), (x,-0.818,0.46), midwood)
for i,x in enumerate((-0.57,0.32)):
    addbox(island, 'side drawer %d' % i, (0.77,0.045,0.18), (x,-0.846,0.665), panelwood)
    addbox(island, 'side door %d' % i, (0.77,0.045,0.42), (x,-0.846,0.355), midwood)
    addbox(island, 'side inset panel %d' % i, (0.64,0.018,0.30), (x,-0.876,0.355), panelwood)
    bar(island, 'drawer pull %d' % i, (x-0.09,-0.89,0.67), (x+0.09,-0.89,0.67), 0.015)
    bar(island, 'door pull %d' % i, (x+0.25,-0.893,0.37), (x+0.25,-0.893,0.47), 0.012)
addbox(island, 'end recessed field', (0.035,1.15,0.50), (1.253,-0.10,0.43), panelwood)
for y in (-0.70,0.50):
    addbox(island, 'end vertical frame %.2f' % y, (0.065,0.095,0.63), (1.28,y,0.45), midwood)
for z in (0.17,0.73):
    addbox(island, 'end horizontal frame %.2f' % z, (0.065,1.25,0.10), (1.28,-0.10,z), midwood)
scene.include('work island', island)

left = Asset('Left tall glass cabinet')
ly0, ly1 = -3.25, -0.52
lc = (ly0+ly1)/2
lw = ly1-ly0
addbox(left, 'lower cabinet body', (0.58,lw,0.89), (-2.79,lc,0.47), dark)
addbox(left, 'cabinet plinth', (0.66,lw+0.06,0.12), (-2.76,lc,0.08), dark_edge)
addbox(left, 'lower cabinet top molding', (0.68,lw+0.10,0.09), (-2.74,lc,0.94), midwood)
for i in range(4):
    y = ly0 + (i+0.5)*lw/4
    w = lw/4-0.035
    addbox(left, 'lower drawer %d' % i, (0.035,w,0.18), (-2.477,y,0.79), midwood)
    addbox(left, 'lower door %d' % i, (0.04,w,0.55), (-2.473,y,0.395), midwood)
    addbox(left, 'lower recessed panel %d' % i, (0.018,w-0.12,0.42), (-2.447,y,0.395), panelwood)
    bar(left, 'lower drawer handle %d' % i, (-2.438,y-0.075,0.79), (-2.438,y+0.075,0.79), 0.013)
    bar(left, 'lower door handle %d' % i, (-2.435,y+w*0.30,0.43), (-2.435,y+w*0.30,0.52), 0.011)
addbox(left, 'upper cabinet back', (0.12,lw,1.94), (-3.02,lc,1.95), midwood)
for i in range(4):
    y = ly0 + (i+0.5)*lw/4
    w = lw/4
    addbox(left, 'upper glass %d' % i, (0.035,w-0.09,1.76), (-2.52,y,1.96), glass)
    for yy in (y-w/2+0.025,y+w/2-0.025):
        addbox(left, 'glass stile %d %.2f' % (i,yy), (0.085,0.055,1.88), (-2.48,yy,1.96), midwood)
    for z in (1.04,1.61,2.21,2.88):
        addbox(left, 'glass rail %d %.2f' % (i,z), (0.085,w,0.055), (-2.48,y,z), midwood)
    bar(left, 'upper handle %d' % i, (-2.425,y+w*0.33,1.30), (-2.425,y+w*0.33,1.43), 0.009, (0.50,0.46,0.35))
scene.include('left tall cabinet', left)

rear = Asset('Right back wall cabinetry')
ry0, ry1 = -0.18, 3.80
rc = (ry0+ry1)/2
rw = ry1-ry0
addbox(rear, 'lower cabinet carcass', (0.68,rw,0.88), (-2.77,rc,0.47), dark)
addbox(rear, 'lower cabinet toe plinth', (0.72,rw+0.04,0.12), (-2.75,rc,0.075), dark_edge)
addbox(rear, 'dark countertop', (0.83,rw+0.10,0.10), (-2.72,rc,0.95), (0.19,0.13,0.09))
for i in range(6):
    y = ry0+(i+0.5)*rw/6
    w = rw/6-0.025
    addbox(rear, 'base drawer %d' % i, (0.035,w,0.19), (-2.408,y,0.78), midwood)
    addbox(rear, 'base door %d' % i, (0.035,w,0.51), (-2.408,y,0.38), midwood)
    addbox(rear, 'base inset %d' % i, (0.018,w-0.10,0.38), (-2.383,y,0.38), panelwood)
    bar(rear, 'base pull %d' % i, (-2.37,y-0.075,0.78), (-2.37,y+0.075,0.78), 0.012)
addbox(rear, 'upper cabinet back', (0.10,rw,1.19), (-3.03,rc,2.39), dark)
for i in range(6):
    y = ry0+(i+0.5)*rw/6
    w = rw/6
    addbox(rear, 'upper glass %d' % i, (0.035,w-0.09,1.08), (-2.69,y,2.39), glass)
    for yy in (y-w/2+0.025,y+w/2-0.025):
        addbox(rear, 'upper stile %d %.2f' % (i,yy), (0.075,0.055,1.18), (-2.65,yy,2.39), midwood)
    for z in (1.81,2.94):
        addbox(rear, 'upper rail %d %.2f' % (i,z), (0.075,w,0.065), (-2.65,y,z), midwood)
    bar(rear, 'upper glass pull %d' % i, (-2.60,y+w*0.33,2.08), (-2.60,y+w*0.33,2.19), 0.009, (0.48,0.43,0.32))
addbox(rear, 'right tall cabinet side', (0.78,0.12,2.95), (-2.73,ry1,1.475), dark)
scene.include('right rear cabinetry', rear)

realize(scene)
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new('Soft interior world')
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.72,0.78,0.75,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.4
set_view((5.4,-6.8,3.8), (-0.35,0.0,0.85), lens=46)
area_emitter((1.0,-4.5,6.5), power=1000, size=5.0, target=(-0.5,0,0.6), color=(1.0,0.91,0.78))
area_emitter((-1.5,1.5,5.0), power=350, size=4.0, target=(-1,0,1), color=(0.82,0.92,1.0))