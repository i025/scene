from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(23)

scene = Scene('Damaged classroom')
cream=(.72,.70,.62)
trim=(.065,.075,.073)
metal=(.55,.59,.59)

def add(name,size,center,color,rotation=None):
    ob=box(size=size,center=center,color=color)
    if rotation:
        ob.turn(euler=rotation)
    scene.include(name,ob)
    return ob

# Room shell.
add('Carpet',(4.6,10,.12),(0,3.5,-.065),(.18,.19,.165))
add('Back plaster',(4.65,.16,3.15),(0,7.65,1.52),cream)
add('Right plaster',(.15,10,3.15),(2.32,3.5,1.52),(.77,.75,.68))
add('Left wall',(.12,10,3.15),(-2.32,3.5,1.52),(.76,.77,.73))
add('Back black skirting',(4.6,.045,.115),(0,7.55,.057),trim)
add('Right black skirting',(.045,10,.13),(2.225,3.5,.065),trim)
add('Left black skirting',(.04,10,.115),(-2.245,3.5,.057),trim)

# Pale daylight through the tall translucent glazing on the left.
for j in range(7):
    yy=-.55+j*.96
    add('Window glass %02d'%j,(.025,.925,2.66),(-2.245,yy,1.56),(.89,.93,.93))
    add('Window vertical mullion %02d'%j,(.045,.026,2.7),(-2.21,yy+.47,1.56),(.75,.78,.77))
for z in (.31,1.15,2.08,2.91):
    add('Window horizontal rail '+str(z),(.045,6.8,.025),(-2.20,2.25,z),(.78,.80,.79))

# Suspended ceiling: thin individual tiles and exposed dark bays.
add('Dark ceiling void',(4.65,10,.04),(0,3.5,3.17),(.075,.09,.087))
for i in range(8):
    xx=-2.1+i*.6
    for j in range(9):
        yy=-.65+j*1.05
        missing = (i==0 and j in (2,3,4,5)) or (i==1 and j in (3,4))
        if not missing:
            c=.69+random.uniform(-.025,.025)
            add('Ceiling panel %d %d'%(i,j),(.585,1.034,.026),(xx,yy,3.065),(c,c+.014,c+.006))
for i in range(9):
    add('Ceiling main tee %d'%i,(.016,9.5,.018),(-2.4+i*.6,3.5,3.045),(.60,.64,.63))
for j in range(10):
    add('Ceiling cross tee %d'%j,(4.6,.014,.018),(0,-1.175+j*1.05,3.044),(.62,.65,.64))

# Recessed rectangular fluorescent diffusers.
for yy in (1.45,4.60):
    add('Light frame '+str(yy),(.63,1.08,.035),(-.9,yy,3.031),(.55,.59,.58))
    add('Light diffuser '+str(yy),(.565,.995,.017),(-.9,yy,3.007),(.79,.84,.83))
    add('Diffuser central seam '+str(yy),(.565,.012,.01),(-.9,yy,2.996),(.65,.70,.69))

# Small ceiling smoke detector.
scene.include('Smoke detector base',rod(radius=.068,length=.028,center=(-1.35,1.45,3.002),color=(.77,.78,.72)))
scene.include('Smoke detector',ball(radius=.047,center=(-1.35,1.45,2.98),color=(.78,.79,.74)))

# Large blank whiteboard on the right wall.
board_y=3.76
board_len=3.8
board_z=1.91
board_h=1.42
add('Whiteboard backing',(.047,board_len,board_h),(2.209,board_y,board_z),(.70,.73,.72))
add('Whiteboard writing face',(.014,board_len-.065,board_h-.065),(2.176,board_y,board_z),(.83,.85,.84))
for yy in (board_y-board_len/2,board_y+board_len/2):
    add('Whiteboard end frame '+str(yy),(.045,.026,board_h+.035),(2.157,yy,board_z),metal)
for zz in (board_z-board_h/2,board_z+board_h/2):
    add('Whiteboard long frame '+str(zz),(.045,board_len+.035,.026),(2.157,board_y,zz),metal)
add('Whiteboard central joint',(.019,.012,board_h-.04),(2.158,board_y+.53,board_z),(.67,.70,.70))
add('Board marker ledge',(.09,board_len,.022),(2.135,board_y,board_z-board_h/2-.025),(.54,.59,.59))
for yy in (board_y-1.75,board_y+1.75):
    add('Whiteboard upper bracket '+str(yy),(.035,.042,.10),(2.18,yy,board_z+board_h/2+.035),(.49,.51,.49))

# Back-wall utility fixtures.
add('Vent outer frame',(.83,.035,.39),(-1.31,7.545,1.79),(.49,.53,.52))
add('Vent dark opening',(.76,.018,.32),(-1.31,7.52,1.79),(.26,.31,.32))
for i in range(9):
    add('Vent slat %02d'%i,(.735,.023,.012),(-1.31,7.505,1.65+i*.033),(.37,.42,.42))
add('Open electrical cabinet',(.30,.06,.43),(-.17,7.53,1.53),(.50,.53,.50))
add('Electrical dark interior',(.235,.025,.35),(-.17,7.49,1.53),(.15,.18,.17))
for i in range(7):
    add('Cabinet interior component %d'%i,(.045,.02,.045),(-.23+(i%2)*.105,7.465,1.41+(i//2)*.075),(.65,.68,.62))
add('Loose electrical cover',(.43,.045,.37),(.08,7.42,1.20),(.45,.50,.48),(0,35,0))
add('Cover screw',(.025,.018,.025),(.08,7.385,1.21),(.19,.23,.22))
for xx,zz in ((.45,1.27),(.66,1.31)):
    add('Wall switch plate '+str(xx),(.13,.027,.19),(xx,7.54,zz),(.79,.79,.70))
    add('Wall switch '+str(xx),(.036,.012,.067),(xx,7.52,zz),(.59,.61,.55))
add('Right wall outlet',(.023,.09,.145),(2.232,4.64,.43),(.73,.71,.61))
for z in (.405,.455):
    add('Outlet hole '+str(z),(.012,.026,.012),(2.215,4.64,z),(.35,.35,.30))

# Flag mounted high near the rear corner.
scene.include('Flagpole',rod(radius=.013,start=(2.22,6.93,2.77),end=(1.42,6.61,2.98),color=(.28,.26,.22)))
for i in range(13):
    x=1.43+i*.034
    top=2.965-i*.012
    bottom=2.30 + .045*math.sin(i*.62)
    ob=box((.034,.014,top-bottom),center=(x,6.60+.035*math.sin(i*.8),(top+bottom)/2),
           color=(.57,.045,.045) if i%2==0 else (.85,.84,.75))
    scene.include('Flag stripe %02d'%i,ob)
add('Flag blue canton',(.19,.018,.255),(1.508,6.575,2.825),(.12,.17,.25))
for row in range(5):
    for col in range(5):
        scene.include('Flag star %d %d'%(row,col),ball(radius=.005,center=(1.431+col*.034+(row%2)*.012,6.562,2.925-row*.044),color=(.83,.84,.77)))

# Fallen ceiling debris and rails on the carpet.
def debris(name,x,y,w,d,a):
    ob=add(name,(w,d,.025),(x,y,.026),(.32,.34,.30),(1.5,-2,a))
    for k in range(7):
        px=x+random.uniform(-w*.37,w*.37)
        py=y+random.uniform(-d*.34,d*.34)
        add(name+' stain '+str(k),(random.uniform(.06,.25),random.uniform(.035,.13),.004),
            (px,py,.046),random.choice([(.42,.43,.36),(.22,.25,.22),(.52,.51,.41)]),(0,0,a+random.uniform(-15,15)))
debris('Large broken tile foreground',-.72,1.55,1.22,.63,-12)
debris('Overlapping broken tile',-.38,1.79,1.03,.50,13)
debris('Left middle tile',-1.49,3.12,.93,.47,-7)
debris('Small left fragment',-1.13,3.42,.45,.29,18)
debris('Distant tile',-.98,5.04,.79,.39,7)
debris('Distant broken piece',-.61,5.27,.52,.28,-13)
add('Long fallen silver runner',(1.66,.035,.022),(-.41,2.75,.038),(.61,.66,.65),(0,0,-12))
add('Black torn runner',(.81,.027,.026),(-.97,4.90,.05),(.08,.10,.09),(0,0,18))
add('Foreground white rail',(.045,2.45,.028),(1.78,.37,.033),(.66,.69,.67),(0,0,26))
add('Second foreground white rail',(.037,2.07,.024),(2.14,.58,.034),(.65,.67,.65),(0,0,25))

# Yellow fibrous panels lying in a loose overlapping pile beside the wall.
for name,sz,loc,rot,c in [
    ('Yellow panel lower',(1.16,.88,.036),(1.56,2.36,.052),(0,0,-9),(.58,.49,.22)),
    ('Yellow panel left',(.89,1.03,.042),(1.12,2.58,.090),(0,-5,-8),(.67,.58,.29)),
    ('Yellow panel upper',(1.10,.96,.045),(1.60,2.18,.14),(6,-7,-12),(.69,.59,.27)),
]:
    add(name,sz,loc,c,rot)
for i in range(18):
    x=random.uniform(1.07,1.96)
    y=random.uniform(1.88,2.68)
    add('Insulation surface mark %d'%i,(random.uniform(.03,.17),random.uniform(.03,.10),.002),
        (x,y,.203),(.59+random.random()*.08,.50+random.random()*.07,.25),(0,0,-10))
for i in range(42):
    x=random.uniform(-2.1,2.1)
    y=random.uniform(.6,7.1)
    s=random.uniform(.008,.037)
    add('Scattered plaster fleck %d'%i,(s,s*.6,.004),(x,y,.006),(.46,.46,.37))

realize(scene)

# Fine material variation on the carpet, acoustic tiles and painted walls.
for ob in bpy.data.objects:
    if ob.type!='MESH':
        continue
    for mat in ob.data.materials:
        if not mat:
            continue
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Roughness'].default_value=.88
        if 'Carpet' in ob.name:
            nt=mat.node_tree
            tex=nt.nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=155
            tex.inputs['Detail'].default_value=2.0
            ramp=nt.nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.20
            ramp.color_ramp.elements[0].color=(.075,.086,.071,1)
            ramp.color_ramp.elements[1].position=.8
            ramp.color_ramp.elements[1].color=(.245,.255,.218,1)
            nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
            nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
            bump=nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.27
            bump.inputs['Distance'].default_value=.018
            nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
        elif 'plaster' in ob.name:
            nt=mat.node_tree
            tex=nt.nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=100
            bump=nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.12
            bump.inputs['Distance'].default_value=.008
            nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view((1.52,-.64,1.61),(1.86,7.6,1.70),lens=25.5,sensor=36)
cam=bpy.context.scene.camera
cam.data.sensor_fit='HORIZONTAL'
area_emitter((-3.0,2.0,2.0),power=750,size=5.0,target=(1,3,1.1),color=(.88,.94,1))
area_emitter((-.6,.5,2.85),power=110,size=3.0,target=(0,4,.2),color=(1,.94,.82))
area_emitter((-1.5,6,2.7),power=75,size=2.0,target=(1,6,1),color=(1,.97,.88))
sc=bpy.context.scene
sc.world.color=(.22,.24,.25)
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.15
