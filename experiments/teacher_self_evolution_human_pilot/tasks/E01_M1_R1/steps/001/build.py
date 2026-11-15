from sceneact import *
import bpy, math
from mathutils import Vector

scene = Scene('Sage room')
wall = (0.43, 0.49, 0.39)
ceiling = (0.72, 0.72, 0.68)
trim = (0.52, 0.47, 0.39)
floorcol = (0.66, 0.65, 0.61)
wood = (0.20, 0.075, 0.025)
woodlight = (0.31, 0.13, 0.045)
dark = (0.10, 0.045, 0.025)
white = (0.78, 0.78, 0.73)

def add(name, node):
    scene.include(name, node)

def beam(name, a, b, radius, color):
    add(name, rod(radius, start=a, end=b, color=color))

# Room shell, with separately modeled boards and unobstructed front.
add('ceiling', box((8.2, 7.4, 0.12), center=(0, 0, 3.76), color=ceiling))
add('right sage wall', box((0.12, 7.4, 3.75), center=(4.06, 0, 1.875), color=wall))
add('left sage wall', box((0.12, 7.4, 3.75), center=(-4.06, 0, 1.875), color=wall))
add('floor foundation', box((8.2, 7.4, 0.10), center=(0, 0, -0.09), color=(0.54,0.53,0.50)))
for i in range(22):
    x = -3.97 + i * 0.37
    c = (0.67 + (i%4)*0.008, 0.66 + (i%4)*0.007, 0.62 + (i%4)*0.006)
    add('floor plank %02d' % i, box((0.364, 7.4, 0.045), center=(x,0,-0.022), color=c))
add('right baseboard', box((0.07,7.3,0.18), center=(3.97,0,0.10), color=trim))
add('back baseboard', box((8.0,0.07,0.18), center=(0,3.63,0.10), color=trim))
add('right ceiling molding', box((0.035,7.2,0.035), center=(3.96,0,3.67), color=(0.33,0.34,0.29)))
add('back ceiling molding', box((8,0.035,0.035), center=(0,3.56,3.67), color=(0.33,0.34,0.29)))

# Build the back wall as narrow horizontal courses around the two arched openings.
windows = [(-1.65,0.68,1.18,2.35,3.17), (0.75,0.55,1.18,2.34,2.99)]
def half_width(z, w, bottom, spring, peak):
    if z < bottom or z > peak:
        return 0.0
    if z <= spring:
        return w
    t = (z-spring)/(peak-spring)
    return w * math.sqrt(max(0, 1-t))
levels = sorted(set([0, 1.18, 2.34, 2.35, 2.99, 3.17, 3.72] + [1.18+i*0.055 for i in range(38)]))
levels = [z for z in levels if z <= 3.72]
if levels[-1] < 3.72: levels.append(3.72)
for j in range(len(levels)-1):
    lo, hi = levels[j], levels[j+1]
    mid=(lo+hi)/2
    openings=[]
    for cx,w,bot,spring,peak in windows:
        h=half_width(mid,w,bot,spring,peak)
        if h>0: openings.append((cx-h,cx+h))
    cursor=-4.0
    for left,right in sorted(openings):
        if left>cursor:
            add('back wall course %02d %.2f' % (j,cursor), box((left-cursor,0.13,hi-lo+0.003), center=((left+cursor)/2,3.65,mid), color=wall))
        cursor=max(cursor,right)
    if cursor<4:
        add('back wall course %02d end' % j, box((4-cursor,0.13,hi-lo+0.003), center=((cursor+4)/2,3.65,mid), color=wall))

for k,(cx,w,bot,spring,peak) in enumerate(windows):
    # Bright opening and thin stone-colored pointed arch surround.
    add('window %d bright lower glazing' % k, box((2*w,0.035,spring-bot), center=(cx,3.70,(bot+spring)/2), color=(0.85,0.89,0.84)))
    for n in range(14):
        z0=spring+(peak-spring)*n/14
        z1=spring+(peak-spring)*(n+1)/14
        hw=half_width((z0+z1)/2,w,bot,spring,peak)
        add('window %d upper glass %02d' % (k,n), box((2*hw,0.025,z1-z0+0.005), center=(cx,3.70,(z0+z1)/2), color=(0.91,0.94,0.89)))
    outline=[(cx-w,3.53,bot),(cx-w,3.53,spring)]
    for n in range(1,13):
        z=spring+(peak-spring)*n/12
        outline.append((cx-half_width(z,w,bot,spring,peak),3.53,z))
    for n in range(11,-1,-1):
        z=spring+(peak-spring)*n/12
        outline.append((cx+half_width(z,w,bot,spring,peak),3.53,z))
    outline.append((cx+w,3.53,bot))
    add('window %d pointed outer frame' % k, sweep_tube(points=outline,radius=0.045,color=(0.49,0.46,0.39)))
    add('window %d sill' % k, box((2*w+0.22,0.26,0.075),center=(cx,3.48,bot-0.03),color=(0.66,0.65,0.58)))
    beam('window %d lower central mullion' % k,(cx,3.49,bot),(cx,3.49,spring-0.12),0.018,(0.50,0.49,0.44))
    beam('window %d lower crossbar' % k,(cx-w,3.49,1.68),(cx+w,3.49,1.68),0.018,(0.50,0.49,0.44))
    # Forked tracery is visible above the roller blind.
    beam('window %d left fork' % k,(cx,3.50,spring+0.01),(cx-w*0.53,3.50,peak-0.22),0.018,(0.43,0.42,0.38))
    beam('window %d right fork' % k,(cx,3.50,spring+0.01),(cx+w*0.53,3.50,peak-0.22),0.018,(0.43,0.42,0.38))
    add('window %d grey roller blind' % k, box((2*w-0.07,0.045,0.39),center=(cx,3.44,2.20),color=(0.49,0.49,0.46)))
    add('radiator %d' % k, fillet_box((2*w+0.20,0.13,0.76),radius=0.035,center=(cx,3.40,0.58),color=(0.78,0.79,0.76)))
    add('radiator %d top lip' % k, box((2*w+0.20,0.16,0.035),center=(cx,3.39,0.98),color=(0.65,0.67,0.64)))

# Wardrobe: broad side faces the viewer, paneled doors face into the room.
wardrobe=Asset('large antique wardrobe')
wardrobe.include('main cabinet', box((1.45,1.65,3.22),center=(-3.12,-0.15,1.70),color=woodlight))
wardrobe.include('visible broad side', box((1.41,0.035,3.04),center=(-3.12,-0.99,1.72),color=(0.29,0.12,0.035)))
wardrobe.include('top cornice', box((1.57,1.76,0.13),center=(-3.12,-0.15,3.35),color=dark))
wardrobe.include('upper cornice trim', box((1.58,1.77,0.045),center=(-3.12,-0.15,3.43),color=(0.32,0.14,0.055)))
wardrobe.include('lower plinth', box((1.50,1.72,0.18),center=(-3.12,-0.15,0.19),color=dark))
for y in (-0.58,0.23):
    wardrobe.include('door panel %.2f' % y, box((0.035,0.73,2.60),center=(-2.37,y,1.76),color=(0.27,0.105,0.028)))
    for yy in (y-0.31,y+0.31):
        wardrobe.include('door vertical molding %.2f' % yy,box((0.055,0.035,2.48),center=(-2.34,yy,1.76),color=(0.43,0.23,0.095)))
    for zz in (0.53,2.98):
        wardrobe.include('door horizontal molding %.2f %.2f' % (y,zz),box((0.055,0.65,0.035),center=(-2.34,y,zz),color=(0.43,0.23,0.095)))
    wardrobe.include('door handle %.2f' % y,ball(0.04,center=(-2.29,y+0.23,1.65),color=(0.67,0.52,0.26)))
for xx in (-3.68,-2.58):
    for yy in (-0.77,0.49):
        wardrobe.include('foot %.2f %.2f' % (xx,yy),box((0.18,0.18,0.20),center=(xx,yy,0.10),color=dark))
scene.include('wardrobe',wardrobe)
add('wardrobe curved crest', sweep_tube(points=[(-2.34,-0.94,3.25),(-2.34,-0.65,3.31),(-2.34,-0.35,3.43),(-2.34,-0.05,3.48),(-2.34,0.25,3.41),(-2.34,0.60,3.23)],radius=0.055,color=(0.22,0.09,0.035)))

# Small straight chair partially concealed behind the wardrobe.
add('back chair seat',box((0.70,0.65,0.10),center=(-2.10,2.08,0.77),color=(0.68,0.62,0.50)))
for x in (-2.40,-1.80):
    for y in (1.83,2.32):
        beam('back chair leg %.2f %.2f' % (x,y),(x,y,0.05),(x,y,0.78),0.035,dark)
for x in (-2.40,-1.80):
    beam('back chair back post %.2f' % x,(x,2.34,0.74),(x,2.34,1.52),0.04,dark)
beam('back chair top rail',(-2.40,2.34,1.52),(-1.80,2.34,1.52),0.045,dark)
for x in (-2.26,-2.10,-1.94):
    beam('back chair back slat %.2f' % x,(x,2.34,0.84),(x,2.34,1.47),0.018,dark)

# Oval tabletop and central pedestal.
tx,ty=1.50,0.77
top=ball(1,center=(tx,ty,1.02),color=woodlight)
top.resize((1.22,0.63,0.075),pivot=(tx,ty,1.02))
add('oval polished tabletop',top)
rim=ball(1,center=(tx,ty,0.985),color=dark)
rim.resize((1.24,0.65,0.055),pivot=(tx,ty,0.985))
add('oval table dark edge',rim)
beam('table pedestal',(tx,ty,0.22),(tx,ty,0.98),0.115,wood)
for z,r in [(0.31,0.17),(0.43,0.15),(0.79,0.14),(0.91,0.17)]:
    add('pedestal turning %.2f' % z,ball(r,center=(tx,ty,z),color=wood))
for a in (25,115,205,295):
    q=math.radians(a)
    p=[(tx,ty,0.32),(tx+0.25*math.cos(q),ty+0.25*math.sin(q),0.23),(tx+0.53*math.cos(q),ty+0.53*math.sin(q),0.09)]
    add('table curved foot %d' % a,sweep_tube(points=p,radius=0.065,color=dark))
    add('table foot tip %d' % a,ball(0.075,center=p[-1],color=dark))

# Two carved chairs with different headings. Local y points toward the backrest.
def chair(name, cx, cy, angle, cloth):
    a=math.radians(angle)
    def tr(x,y,z): return (cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)
    def stick(label,p,q,r=0.035): beam(name+' '+label,tr(*p),tr(*q),r,dark)
    cushion=fillet_box((0.68,0.62,0.15),radius=0.07,center=(cx,cy,0.64),color=cloth)
    cushion.turn('+z',angle,pivot=(cx,cy,0.64))
    add(name+' upholstered seat',cushion)
    for x in (-0.27,0.27):
        for y in (-0.24,0.24):
            stick('leg %.2f %.2f' % (x,y),(x*1.12,y*1.16,0.04),(x,y,0.59),0.037)
    for x in (-0.27,0.27):
        stick('back upright %.2f' % x,(x,0.24,0.63),(x*0.88,0.30,1.40),0.045)
    stick('upper carved rail',(-0.24,0.30,1.39),(0.24,0.30,1.39),0.048)
    stick('lower back rail',(-0.25,0.26,0.85),(0.25,0.26,0.85),0.032)
    add(name+' pierced back ornament',sweep_tube(points=[tr(-0.17,0.29,1.34),tr(-0.10,0.28,1.19),tr(0,0.28,1.07),tr(0.10,0.28,1.19),tr(0.17,0.29,1.34)],radius=0.025,color=woodlight))
    add(name+' crest',ball(0.065,center=tr(0,0.30,1.41),color=woodlight))
chair('left dining chair',0.37,0.55,-18,(0.57,0.55,0.52))
chair('right dining chair',3.05,-0.20,-35,(0.58,0.58,0.53))

# Slender floor lamp, framed print, and small tabletop accessories.
beam('floor lamp pole',(1.63,2.58,0.08),(1.63,2.58,1.96),0.018,(0.38,0.39,0.35))
add('floor lamp foot',ball(0.17,center=(1.63,2.58,0.05),color=(0.37,0.38,0.34)))
add('floor lamp shade',ball(1,center=(1.63,2.58,1.99),color=(0.75,0.76,0.70)).resize((0.18,0.18,0.09),pivot=(1.63,2.58,1.99)))
add('right wall picture frame',box((0.08,0.85,0.58),center=(3.94,2.10,2.43),color=(0.39,0.28,0.14)))
add('right wall picture mat',box((0.025,0.72,0.45),center=(3.89,2.10,2.43),color=(0.83,0.81,0.72)))
add('right wall picture image',box((0.02,0.52,0.29),center=(3.87,2.10,2.43),color=(0.57,0.63,0.52)))
add('table papers',box((0.64,0.39,0.012),center=(1.50,0.80,1.105),color=(0.82,0.81,0.74)))
add('small dish',ball(1,center=(0.98,0.90,1.11),color=(0.73,0.72,0.65)).resize((0.13,0.10,0.025),pivot=(0.98,0.90,1.11)))
add('flower vase',ball(1,center=(1.64,0.98,1.20),color=(0.40,0.42,0.31)).resize((0.075,0.075,0.14),pivot=(1.64,0.98,1.20)))
for i,(dx,dy,h) in enumerate([(-0.06,0,0.42),(0.03,0.02,0.49),(0.08,-0.01,0.37)]):
    beam('flower stem %d' % i,(1.64,0.98,1.27),(1.64+dx,0.98+dy,1.27+h),0.008,(0.18,0.34,0.12))
    add('red flower %d' % i,ball(0.042,center=(1.64+dx,0.98+dy,1.27+h),color=(0.65,0.05,0.07)))

realize(scene)
set_view((0.1,-9.4,3.05),(0.15,2.2,1.65),lens=27,sensor=36)
if bpy.context.scene.world is None:
    bpy.context.scene.world=bpy.data.worlds.new('Soft daylight world')
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.72,0.77,0.72,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.55
area_emitter((0,-3,5.2),power=500,size=7,target=(0,1,0),color=(1.0,0.96,0.88))
area_emitter((-1.0,3.0,2.7),power=280,size=3,target=(0,0,1),color=(0.85,0.91,1.0))