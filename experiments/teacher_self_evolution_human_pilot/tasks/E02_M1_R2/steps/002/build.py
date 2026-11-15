from sceneact import *
import bpy

scene = Scene('Woodworking room')
dark = (0.16, 0.095, 0.052)
edge = (0.115, 0.066, 0.035)
panel = (0.205, 0.125, 0.071)
topwood = (0.58, 0.37, 0.18)
wall = (0.68, 0.80, 0.76)
glass = (0.45, 0.61, 0.58)
metal = (0.14, 0.13, 0.11)

floor = Asset('Continuous warm wood floor')
floor.include('floor substrate', box((18,18,.10), center=(0,0,-.065), color=(.40,.25,.14)))
colors = [(.47,.30,.17),(.51,.33,.19),(.45,.28,.16),(.53,.34,.19),(.48,.31,.18)]
for i in range(32):
    x = -7.75 + i*.5
    floor.include('floor plank %02d' % i, box((.494,16,.016), center=(x,0,-.008), color=colors[i%5]))
    for j in range(-3,4):
        y = j*2.4 + (i%3)*.8
        floor.include('staggered joint %02d %02d' % (i,j+3), box((.49,.008,.003), center=(x,y,.002), color=(.32,.20,.11)))
scene.include('floor', floor)

room = Asset('Pale walls and trim')
room.include('rear wall', box((13,.12,4.7), center=(0,3.25,2.35), color=wall))
room.include('rear skirting', box((13,.12,.20), center=(0,3.16,.10), color=edge))
scene.include('room', room)

island = Asset('Central work island')
island.include('solid honey oak top', fillet_box((2.18,3.42,.105), radius=.018, center=(0,-.28,1.045), color=topwood))
for x in (-.73,-.37,0,.37,.73):
    island.include('top board seam %.2f' % x, box((.003,3.37,.0015), center=(x,-.28,1.098), color=(.49,.31,.15)))
island.include('base cabinet core', box((1.62,2.72,.81), center=(-.12,-.29,.49), color=dark))
for x in (-.94,.70):
    for y in (-1.68,1.10):
        island.include('corner stile %.2f %.2f' % (x,y), box((.105,.105,.97), center=(x,y,.485), color=edge))
island.include('near end recessed panel', box((1.43,.025,.62), center=(-.12,-1.667,.50), color=panel))
for x in (-.88,.64):
    island.include('end vertical frame %.2f' % x, box((.105,.06,.80), center=(x,-1.70,.50), color=dark))
for z in (.14,.84):
    island.include('end horizontal frame %.2f' % z, box((1.58,.06,.105), center=(-.12,-1.70,z), color=dark))
island.include('end center panel divider', box((.075,.04,.62), center=(-.12,-1.705,.49), color=dark))
for idx, y in enumerate((-1.18,-.29,.60)):
    island.include('side door panel %d' % idx, box((.025,.76,.52), center=(-.958,y,.43), color=panel))
    for yy in (y-.38,y+.38):
        island.include('side door stile %d %.2f' % (idx,yy), box((.035,.055,.57), center=(-.98,yy,.43), color=dark))
    for z in (.16,.70):
        island.include('side door rail %d %.2f' % (idx,z), box((.035,.78,.055), center=(-.98,y,z), color=dark))
    island.include('drawer front %d' % idx, box((.04,.78,.16), center=(-.98,y,.835), color=panel))
    island.include('drawer pull %d' % idx, rod(.018, start=(-1.018,y-.07,.84), end=(-1.018,y+.07,.84), color=metal))
    island.include('door handle %d' % idx, rod(.018, start=(-1.02,y+.25,.45), end=(-1.02,y+.25,.55), color=metal))
    for z in (.25,.61):
        island.include('door hinge %d %.2f' % (idx,z), box((.018,.025,.10), center=(-1.014,y-.34,z), color=(.42,.40,.34)))
scene.include('work island', island)

left = Asset('Left rear glass cupboard')
lx = -3.05
left.include('lower cupboard body', box((2.50,.65,1.02), center=(lx,2.78,.54), color=dark))
left.include('cupboard plinth', box((2.62,.73,.12), center=(lx,2.76,.07), color=edge))
for i in range(4):
    x = lx-.94+i*.625
    left.include('lower door inset %d' % i, box((.51,.025,.58), center=(x,2.438,.40), color=panel))
    for dx in (-.275,.275):
        left.include('lower door vertical frame %d %.2f' % (i,dx), box((.055,.045,.66), center=(x+dx,2.415,.40), color=dark))
    for z in (.085,.72):
        left.include('lower door horizontal frame %d %.2f' % (i,z), box((.59,.045,.06), center=(x,2.415,z), color=dark))
    left.include('lower drawer %d' % i, box((.57,.05,.20), center=(x,2.41,.88), color=panel))
    left.include('lower drawer pull %d' % i, rod(.014, start=(x-.075,2.375,.88), end=(x+.075,2.375,.88), color=metal))
left.include('lower crown ledge', box((2.65,.76,.09), center=(lx,2.76,1.06), color=edge))
left.include('upper cupboard backing', box((2.48,.10,2.60), center=(lx,3.11,2.38), color=(.39,.54,.50)))
for i in range(4):
    x = lx-.94+i*.625
    left.include('glass pane %d' % i, box((.52,.022,2.40), center=(x,2.47,2.40), color=glass))
    for dx in (-.285,.285):
        left.include('glass door stile %d %.2f' % (i,dx), box((.065,.10,2.58), center=(x+dx,2.42,2.40), color=dark))
    for z in (1.14,1.87,2.60,3.32,3.68):
        left.include('glass door crossbar %d %.2f' % (i,z), box((.59,.10,.065), center=(x,2.42,z), color=dark))
    left.include('glass door handle %d' % i, rod(.013, start=(x+.22,2.35,1.85), end=(x+.22,2.35,2.05), color=(.48,.43,.28)))
scene.include('left tall cupboard', left)

back = Asset('Right rear cabinet run')
back.include('base cabinet body', box((5.8,.75,.91), center=(1.35,2.76,.51), color=dark))
back.include('base plinth', box((5.88,.83,.12), center=(1.35,2.75,.08), color=edge))
back.include('dark countertop', box((5.96,.91,.10), center=(1.35,2.73,1.00), color=(.14,.095,.06)))
for i in range(7):
    x = -1.14+i*.83
    back.include('base door inset %d' % i, box((.70,.03,.52), center=(x,2.36,.40), color=panel))
    for dx in (-.38,.38):
        back.include('base door stile %d %.2f' % (i,dx), box((.06,.05,.60), center=(x+dx,2.33,.40), color=dark))
    for z in (.11,.69):
        back.include('base door rail %d %.2f' % (i,z), box((.78,.05,.06), center=(x,2.33,z), color=dark))
    back.include('base drawer %d' % i, box((.76,.05,.17), center=(x,2.33,.82), color=panel))
    back.include('base drawer pull %d' % i, rod(.016, start=(x-.09,2.29,.82), end=(x+.09,2.29,.82), color=metal))
back.include('upper backing', box((5.8,.10,1.85), center=(1.35,3.10,2.63), color=(.35,.47,.43)))
for i in range(7):
    x = -1.14+i*.83
    back.include('upper glass %d' % i, box((.73,.025,1.70), center=(x,2.64,2.64), color=glass))
    for dx in (-.395,.395):
        back.include('upper vertical frame %d %.2f' % (i,dx), box((.075,.12,1.83), center=(x+dx,2.58,2.64), color=dark))
    for z in (1.76,2.62,3.53):
        back.include('upper horizontal frame %d %.2f' % (i,z), box((.83,.12,.085), center=(x,2.58,z), color=dark))
    back.include('upper handle %d' % i, rod(.013, start=(x+.30,2.50,2.30), end=(x+.30,2.50,2.47), color=metal))
back.include('right cabinet end', box((.13,.85,3.38), center=(4.27,2.76,1.75), color=edge))
scene.include('rear cabinet run', back)

realize(scene)
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new('Interior ambient world')
bpy.context.scene.world.color = (.26,.26,.26)
set_view((-4.8,-6.5,3.3), (-.15,.15,1.15), lens=45)
area_emitter((-4.5,-3.0,6.5), power=1050, size=5.0, target=(0,0,0.8), color=(1.0,.91,.79))
area_emitter((2.5,1.0,5.0), power=250, size=4.0, target=(0,1,1.0), color=(.79,.88,1.0))