from sceneact import *
import bpy, math, random
from mathutils import Quaternion

random.seed(12)
scene = Scene("High warehouse aisle")

steel = (.135, .155, .135)
rail = (.22, .235, .18)
yellow = (.73, .49, .035)
gold = (.92, .65, .07)
roof = (.27, .275, .21)
cream = (.65, .59, .39)

def block(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Warehouse structure")
block(architecture, "floor", (15, 47, .22), (0, 17, -.16), (.28,.28,.23))
block(architecture, "far wall", (15,.25,12), (0,37,6), (.42,.42,.33))
block(architecture, "roof", (15,47,.17), (0,15.5,11.5), roof)

# Closely spaced roof corrugations and heavier transverse girders.
for i in range(67):
    x = -7.3 + i*.22
    block(architecture, "roof rib %d"%i, (.045,47,.085), (x,15.5,11.37), (.34,.345,.265))
for j,y in enumerate(range(-7,39,4)):
    block(architecture, "roof girder %d"%j, (15,.18,.39), (0,y,11.08), steel)
    block(architecture, "girder lower flange %d"%j, (15,.34,.06), (0,y,10.87), rail)
    for x in (-5.2, 3.9):
        block(architecture, "long purlin %d %s"%(j,x), (.12,4,.15), (x,y+2,11.15), rail)

# Roof window with a dense metal grille.
window = Asset("Rectangular roof skylight")
block(window, "white glazing", (2.05,3.7,.035), (1.0,4.7,11.31), (.77,.84,.78))
for x in (-.08,2.08):
    block(window,"window side "+str(x),(.11,3.9,.17),(x,4.7,11.22),steel)
for y in (2.78,6.62):
    block(window,"window end "+str(y),(2.2,.11,.17),(1,y,11.22),steel)
for i in range(9):
    block(window,"window crossbar "+str(i),(2.1,.045,.075),(1,2.9+i*.45,11.19),steel)
for i in range(5):
    block(window,"window length bar "+str(i),(.035,3.7,.075),(.15+i*.43,4.7,11.18),steel)
scene.include("skylight",window)
scene.include("building", architecture)

def make_rack(name, front, back, right=False):
    rack = Asset(name)
    bays = [-4 + 2.8*i for i in range(15)]
    levels = [1.05,3.35,5.65,7.95,10.25]
    for j,y in enumerate(bays):
        for k,x in enumerate((front,back)):
            block(rack,f"post {j} {k}",(.105,.105,10.65),(x,y,5.325),rail)
            block(rack,f"foot {j} {k}",(.26,.25,.065),(x,y,.035),steel)
            # Rows of small perforations on the exposed upright face.
            for h in range(48):
                block(rack,f"slot {j} {k} {h}",(.012,.041,.031),
                      (x + (.057 if not right else -.057),y,.27+h*.215),(.075,.085,.065))
        for z in levels:
            block(rack,f"cross tie {j} {z}",(abs(front-back),.09,.12),((front+back)/2,y,z),steel)
        # Diagonal bracing behind the cargo.
        for h in range(4):
            z0=.2+h*2.55
            rack.include(f"diagonal {j} {h}",rod(.025,start=(back,y,z0),
                        end=(back,y+2.8,z0+2.55),color=rail))
    for h,z in enumerate(levels):
        for k,x in enumerate((front,back)):
            block(rack,f"continuous rail {h} {k}",(.15,39.4,.19),(x,15.6,z),steel)
            block(rack,f"rail lip {h} {k}",(.19,39.4,.035),(x,15.6,z+.105),rail)
        for j in range(48):
            y=-3.8+j*.81
            block(rack,f"roller bed {h} {j}",(abs(front-back),.055,.075),
                  ((front+back)/2,y,z+.045),rail)
            # Heavy yellow pallet stops along the aisle edge.
            x=front+(.075 if not right else -.075)
            block(rack,f"yellow bracket {h} {j}",(.32,.25,.17),(x,y,z+.14),yellow)
            block(rack,f"raised stop {h} {j}",(.12,.13,.25),
                  (x+(.09 if not right else -.09),y+.09,z+.24),gold)
            block(rack,f"bracket dark end {h} {j}",(.018,.11,.075),
                  (x+(.17 if not right else -.17),y-.01,z+.12),steel)
    scene.include(name,rack)
    return bays,levels

left_bays,levels=make_rack("Left pallet storage",-1.45,-3.55)
make_rack("Right pallet storage",4.8,6.9,True)

def load(name, front, y, base, height, width, depth, tone, right=False):
    a=Asset(name)
    direction=1 if right else -1
    cx=front+direction*(depth/2+.12)
    pallet_z=base+.22
    wood=(.37,.29,.13)
    for yy in (-width*.37,0,width*.37):
        block(a,"pallet bearer "+str(yy),(depth,.15,.12),(cx,y+yy,pallet_z),wood)
    for n in range(7):
        xx=cx-depth/2+(n+.5)*depth/7
        block(a,"pallet board "+str(n),(depth/8,width,.055),(xx,y,pallet_z+.08),(.51,.41,.23))
    bottom=base+.35
    # Slightly irregular packages beneath taut wrapping.
    block(a,"wrapped rectangular load",(depth*.97,width*.97,height),
          (cx,y,bottom+height/2),tone)
    face_x=cx-direction*depth*.491
    for k in range(1,4):
        zz=bottom+height*k/4
        block(a,"carton horizontal seam "+str(k),(.009,width*.96,.012),
              (face_x,y,zz),tuple(v*.76 for v in tone))
    for k in (-1,1):
        block(a,"carton vertical seam "+str(k),(.01,.014,height*.96),
              (face_x,y+k*width*.165,bottom+height/2),tuple(v*.80 for v in tone))
    # Fine overlapping stretch-film bands catch the overhead light.
    for n in range(23):
        zz=bottom+.035+n*(height-.06)/23
        c=tuple(min(1,v*(1.08 if n%3 else .82)) for v in tone)
        block(a,"film band "+str(n),(.014,width*.983,.009 if n%3 else .017),
              (face_x-direction*.009,y,zz),c)
    for n in range(8):
        yy=y-width*.46+random.random()*width*.92
        block(a,"film crease "+str(n),(.017,.005,height*.9),
              (face_x-direction*.017,yy,bottom+height*.5),tuple(min(1,v*1.15) for v in tone))
    # Paper inventory label.
    if random.random()<.7:
        block(a,"paper label",(.019,.23,.16),(face_x-direction*.024,y+.15,bottom+height*.58),(.75,.73,.57))
        for n in range(7):
            block(a,"label mark "+str(n),(.022,.009,.07),
                  (face_x-direction*.028,y+.073+n*.023,bottom+height*.58),(.22,.23,.17))
    scene.include(name,a)

for side,front,right in (("left",-1.45,False),("right",4.8,True)):
    for j in range(14):
        y=-2.6+j*2.8
        for h,z in enumerate(levels[:-1]):
            if random.random() < (.12 if side=="left" else .22):
                continue
            height=random.uniform(1.15,1.77)
            tone=random.choice([(.66,.61,.43),(.71,.65,.45),(.56,.51,.33),(.76,.72,.54),(.61,.57,.42)])
            load(f"{side} cargo {j} {h}",front,y+random.uniform(-.13,.13),z,height,
                 random.uniform(1.8,2.35),random.uniform(1.48,1.83),tone,right)

# Small warehouse location plates along the foremost shelf.
signs=Asset("Rack location labels")
for j in range(18):
    y=-2.9+j*1.6
    block(signs,"plate "+str(j),(.025,.35,.15),(-1.345,y,1.03),(.66,.65,.46))
    for k in range(4):
        block(signs,f"plate print {j} {k}",(.028,.018,.075),
              (-1.327,y-.105+k*.06,1.03),(.17,.18,.13))
scene.include("labels",signs)

# Ceiling conduits and suspended linear fluorescent fixtures.
services=Asset("Ceiling utilities")
for x in (-.7,2.9):
    services.include("conduit "+str(x),rod(.025,start=(x,-7,10.97),end=(x,38,10.97),color=(.43,.44,.36)))
light_positions=[]
for j,y in enumerate((-4,1.7,7.4,13.1,18.8,24.5,30.2)):
    x=.20
    for yy in (y-1.12,y+1.12):
        services.include(f"hanger {j} {yy}",rod(.009,start=(x,yy,11.16),end=(x,yy,10.65),color=steel))
    block(services,"fixture housing "+str(j),(.36,2.65,.105),(x,y,10.61),(.49,.48,.34))
    for k,xx in enumerate((x-.085,x+.085)):
        block(services,f"fluorescent tube {j} {k}",(.075,2.48,.065),(xx,y,10.53),(.98,.99,.78))
    light_positions.append((x,y,10.45))
scene.include("utilities",services)

realize(scene)

# Give the light tubes and skylight luminous surfaces.
for obj in bpy.data.objects:
    if obj.type == 'MESH' and ("fluorescent tube" in obj.name or "white glazing" in obj.name):
        mat=bpy.data.materials.new("Luminous warm white "+obj.name)
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value=(1,.98,.74,1)
        bs.inputs["Emission Color"].default_value=(1,.97,.70,1)
        bs.inputs["Emission Strength"].default_value=6 if "tube" in obj.name else 2.3
        obj.data.materials.clear()
        obj.data.materials.append(mat)

set_view((.25,-3.6,1.65),(-.2,9.5,9.0),lens=28,sensor=32)
cam=bpy.context.scene.camera
cam.rotation_mode='QUATERNION'
cam.rotation_quaternion = cam.rotation_quaternion @ Quaternion((0,0,1),math.radians(-18))

for p in light_positions:
    area_emitter(p,power=400,size=2.6,target=(p[0]-1,p[1],3.4),color=(1,.86,.52))
area_emitter((1.0,4.7,11.05),power=1100,size=2.8,target=(-2,3,4),color=(.85,.93,1))
area_emitter((1,-5,7),power=600,size=5,target=(-2,3,4),color=(1,.78,.40))

sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.render.resolution_x=341
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.world.color=(.14,.14,.10)
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.2

# Restrained glow around the very bright strip lights.
sc.use_nodes=True
nt=sc.node_tree
nt.nodes.clear()
rl=nt.nodes.new('CompositorNodeRLayers')
gl=nt.nodes.new('CompositorNodeGlare')
gl.glare_type='FOG_GLOW'
gl.quality='HIGH'
gl.threshold=1.6
gl.size=7
out=nt.nodes.new('CompositorNodeComposite')
nt.links.new(rl.outputs['Image'],gl.inputs['Image'])
nt.links.new(gl.outputs['Image'],out.inputs['Image'])
