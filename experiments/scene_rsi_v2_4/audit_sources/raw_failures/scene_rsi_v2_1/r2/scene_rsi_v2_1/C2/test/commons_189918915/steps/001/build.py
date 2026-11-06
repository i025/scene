from sceneact import *
import bpy
import math
import random
from mathutils import Quaternion, Vector

# Estimated reference inventory, normalized image coordinates (origin top left):
# Main pallet rack: overall (0,.02)-(.94,1), recedes toward (.91,.86).
# Near uprights: (.02,.88)-(.19,.18); further uprights cluster toward right.
# Four visible load bands: centers about (.08,.12), (.19,.45),
# (.20,.68), and (.20,.97), with increasingly compressed bays at right.
# Large wrapped loads occupy roughly .15-.23 image width near the camera;
# yellow pallet corners extend beyond the cartons, separated by dark open gaps.
# Rack interiors contain closely spaced silver crossbars and deep dark voids.
# Ceiling: whole upper/right region; long strip lights from (.36,0) to (.86,.65).
# Skylight: approximately (.60,.19)-(.84,.37), with a dense dark rectangular grid.
# Hidden rear rack geometry and the bottom floor are uncertain and mostly cropped.
# Placement, bay spacing, and component dimensions are kept independent below.

random.seed(8)
scene = Scene("High warehouse aisle")

steel = (.24,.265,.22)
edge = (.39,.40,.32)
dark = (.105,.125,.105)
yellow = (.73,.48,.055)
yellow_light = (.92,.66,.13)
ceiling = (.28,.285,.22)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# Architecture.
arch = Asset("Warehouse structure")
roof_z = 11.5
add_box(arch, "roof backing", (16,40,.18), (0,13,roof_z+.15), ceiling)
for i in range(54):
    x = -7.8 + i*.29
    add_box(arch, "roof rib %02d" % i, (.055,40,.11),
            (x,13,roof_z-.015), (.34,.34,.27))
for j,y in enumerate(range(-5,34,4)):
    add_box(arch, "roof girder %02d" % j, (16,.22,.42),
            (0,y,roof_z-.28), (.27,.28,.22))
    add_box(arch, "girder flange %02d" % j, (16,.38,.065),
            (0,y,roof_z-.50), (.36,.36,.28))
    for x in (-5,4.8):
        arch.include("bolt %s %s"%(j,x),
                     rod(.055,start=(x,y-.23,roof_z-.38),
                         end=(x,y+.23,roof_z-.38),color=edge))
add_box(arch, "far warehouse wall", (17,.3,13), (0,32,5.5), (.42,.43,.34))
add_box(arch, "floor", (18,42,.2), (0,12,-.15), (.30,.29,.23))
scene.include("Architecture",arch)

# Left rack: its long aisle-facing edge is x=-1.95.
rack = Asset("Left steel pallet rack")
front_x = -1.95
back_x = -4.35
bay_pitch = 2.75
bay_positions = [-2.6 + bay_pitch*i for i in range(13)]
levels = [.55,3.05,5.55,8.05]
rack_top = 10.35

for j,y in enumerate(bay_positions):
    for k,x in enumerate((front_x,back_x)):
        add_box(rack, "upright %d %d"%(j,k), (.115,.14,rack_top),
                (x,y,rack_top/2),steel)
        add_box(rack, "post lip %d %d"%(j,k), (.035,.185,rack_top),
                (x+.055,y,rack_top/2),edge)
        # Rows of dark holes visibly punctuate the metal uprights.
        for h in range(55):
            add_box(rack, "post slot %d %d %d"%(j,k,h),
                    (.006,.048,.057),(x+.075,y,.25+h*.18),(.065,.075,.06))
    for z in (1.1,4.5,7.8,10.1):
        rack.include("cross brace %s %s"%(j,z),
                     rod(.025,start=(front_x,y,z),
                         end=(back_x,y,z+1.5),color=edge))
    for z in levels:
        add_box(rack, "end tie %s %s"%(j,z),(2.5,.10,.12),
                ((front_x+back_x)/2,y,z),steel)

for b in range(len(bay_positions)-1):
    ya,yb=bay_positions[b:b+2]
    mid=(ya+yb)/2
    for li,z in enumerate(levels):
        add_box(rack,"front rail %d %d"%(b,li),(.15,bay_pitch,.21),
                (front_x,mid,z),steel)
        add_box(rack,"back rail %d %d"%(b,li),(.13,bay_pitch,.19),
                (back_x,mid,z),dark)
        add_box(rack,"rail bright lip %d %d"%(b,li),(.025,bay_pitch,.04),
                (front_x+.086,mid,z+.10),edge)
        for n in range(10):
            yy=ya+.13+n*(bay_pitch-.26)/9
            add_box(rack,"shelf crossbar %d %d %d"%(b,li,n),
                    (2.43,.045,.065),(-3.15,yy,z+.10),(.40,.42,.35))
        for yy in (ya+.23,yb-.23):
            add_box(rack,"yellow bracket %d %d %s"%(b,li,yy),
                    (.35,.29,.28),(front_x+.08,yy,z+.15),yellow)
            add_box(rack,"bracket nose %d %d %s"%(b,li,yy),
                    (.13,.32,.10),(front_x+.27,yy,z+.29),yellow_light)
scene.include("Left rack",rack)

# Palletized cartons. Each load is an independent named asset.
for b in range(11):
    mid=(bay_positions[b]+bay_positions[b+1])/2
    for li,z in enumerate(levels):
        # Controlled gaps preserve the rack's open structure.
        if (b,li) in {(1,3),(3,2),(5,1),(7,3),(9,2)}:
            continue
        load=Asset("Pallet load bay %02d level %d"%(b,li))
        pallet_y=mid+random.uniform(-.10,.10)
        depth=1.85
        width=1.85 if b%3 else 2.03
        cx=-3.00
        base=z+.24
        for n in range(6):
            yy=pallet_y-width/2+.09+n*(width-.18)/5
            add_box(load,"pallet deck %d"%n,(depth,.16,.085),
                    (cx,yy,base+.09),(.55,.39,.13))
        for n,yy in enumerate((pallet_y-width*.38,pallet_y+width*.38)):
            add_box(load,"yellow pallet runner %d"%n,(depth,.19,.18),
                    (cx,yy,base-.015),yellow)
            add_box(load,"exposed yellow toe %d"%n,(.36,.25,.27),
                    (front_x+.02,yy,base+.015),yellow_light)
            add_box(load,"toe dark socket %d"%n,(.015,.115,.09),
                    (front_x+.21,yy,base+.015),(.16,.13,.045))
        height=[1.92,1.72,1.63,1.55][li]+random.uniform(-.19,.15)
        carton_width=width-.15
        carton_depth=depth-.10
        tan=(random.uniform(.54,.71),random.uniform(.45,.60),random.uniform(.26,.39))
        # Broad wrapped cuboid masses, occasionally divided into stacked cartons.
        split = b%4==2
        count=2 if split else 1
        for s in range(count):
            hh=height/count
            add_box(load,"carton mass %d"%s,
                    (carton_depth,carton_width-.03,hh-.025),
                    (cx,pallet_y,base+.16+s*hh+hh/2),tan)
        # Seams and cardboard tapes on exposed aisle-facing surface.
        face_x=cx+carton_depth/2+.008
        add_box(load,"vertical tape",(.012,.055,height),
                (face_x,pallet_y+.18,base+.16+height/2),
                (.67,.56,.34))
        for s in range(1,4):
            zz=base+.16+height*s/4
            add_box(load,"horizontal carton seam %d"%s,
                    (.014,carton_width,.012),(face_x,pallet_y,zz),
                    (.36,.31,.20))
        # Fine translucent wrapping bands, constrained to the load's bounds.
        for n in range(18):
            zz=base+.18+(height-.035)*n/18
            shade=(.73,.68,.46) if n%3 else (.85,.79,.54)
            add_box(load,"stretch film edge %02d"%n,
                    (.017,carton_width+.018,.006),
                    (face_x+.01,pallet_y,zz),shade)
        if (b+li)%3==0:
            add_box(load,"paper inventory label",(.022,.30,.22),
                    (face_x+.021,pallet_y-.35,base+.16+height*.62),
                    (.78,.76,.59))
            for t in range(7):
                add_box(load,"label barcode %d"%t,(.007,.012,.09),
                        (face_x+.035,pallet_y-.44+t*.025,base+.16+height*.62),
                        (.17,.18,.13))
        scene.include(load.name,load)

# A narrow opposing rack appears along the far right/top border.
right=Asset("Opposite rack edge")
for j,y in enumerate((-3,0,3,6,9,12,15,18,21,24)):
    add_box(right,"right upright %d"%j,(.15,.15,10.4),(4.2,y,5.2),steel)
    for k,z in enumerate((2.8,5.3,7.8,10.1)):
        add_box(right,"right beam %d %d"%(j,k),(.18,2.9,.20),
                (4.2,y+1.45,z),steel)
        if j<7:
            add_box(right,"right carton %d %d"%(j,k),(1.5,2.1,1.6),
                    (5.05,y+1.45,z+.94),(.60,.50,.30))
scene.include("Opposite rack",right)

# Ceiling fixtures: long luminous strips and a rectangular gridded skylight.
fixtures=Asset("Ceiling light fixtures")
lamp_positions=[]
for j,y in enumerate((-4.0,.3,4.6,8.9,13.2,17.5,21.8,26.1)):
    x=.45
    add_box(fixtures,"strip housing %d"%j,(.30,2.9,.10),
            (x,y,10.89),(.57,.57,.45))
    add_box(fixtures,"strip diffuser %d"%j,(.20,2.72,.055),
            (x,y,10.815),(.98,.98,.81))
    lamp_positions.append((x,y,10.72))
# The skylight is placed in the open roof to the right of the fixture line.
sx,sy=2.15,2.35
add_box(fixtures,"skylight luminous pane",(2.3,3.2,.045),
        (sx,sy,11.34),(.82,.91,.88))
for i in range(9):
    xx=sx-1.15+i*2.3/8
    add_box(fixtures,"skylight longitudinal mullion %d"%i,
            (.035,3.25,.065),(xx,sy,11.28),(.23,.29,.25))
for i in range(12):
    yy=sy-1.6+i*3.2/11
    add_box(fixtures,"skylight transverse mullion %d"%i,
            (2.34,.032,.065),(sx,yy,11.27),(.23,.29,.25))
for xx in (sx-1.20,sx+1.20):
    add_box(fixtures,"skylight outer side %s"%xx,(.09,3.4,.14),
            (xx,sy,11.23),edge)
for yy in (sy-1.68,sy+1.68):
    add_box(fixtures,"skylight outer end %s"%yy,(2.48,.09,.14),
            (sx,yy,11.23),edge)
scene.include("Ceiling fixtures",fixtures)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("World")
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value=(.29,.30,.23,1)
    bg.inputs["Strength"].default_value=.33

# Rough industrial surfaces with subtle cardboard and stretch-film variation.
for obj in list(sc.objects):
    if obj.type!='MESH':
        continue
    for mat in obj.data.materials:
        if not mat:
            continue
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if not bs:
            continue
        bs.inputs["Roughness"].default_value=.69
        name=obj.name.lower()
        if "carton mass" in name:
            nodes=mat.node_tree.nodes
            links=mat.node_tree.links
            noise=nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value=39
            noise.inputs["Detail"].default_value=2
            bump=nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value=.15
            bump.inputs["Distance"].default_value=.035
            links.new(noise.outputs["Fac"],bump.inputs["Height"])
            links.new(bump.outputs["Normal"],bs.inputs["Normal"])
            bs.inputs["Roughness"].default_value=.42
        if "stretch film" in name:
            bs.inputs["Roughness"].default_value=.24
        if "diffuser" in name or "luminous pane" in name:
            bs.inputs["Emission Color"].default_value=(
                (1,.94,.67,1) if "diffuser" in name else (.76,.90,1,1))
            bs.inputs["Emission Strength"].default_value=7 if "diffuser" in name else 3

set_view((.10,-5.3,1.65),(-.85,6.3,9.9),lens=24,sensor=36)
cam=sc.camera
# A slight roll reproduces the diagonal aisle and towering uprights.
cam.rotation_euler=(cam.rotation_euler.to_quaternion() @
                    Quaternion((0,0,1),math.radians(12))).to_euler()

for p in lamp_positions:
    area_emitter(p,power=390,size=2.1,target=(p[0]-1,p[1],3),
                 color=(1,.84,.48))
area_emitter((2.1,2.3,11.12),power=1100,size=2.7,
             target=(-2,3,4),color=(.79,.87,1))
area_emitter((.3,-4,7),power=350,size=4,
             target=(-3,1,5),color=(1,.81,.46))

sc.render.resolution_x=341
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.35

# Subtle photographic glow from the fluorescent strips.
sc.use_nodes=True
nt=sc.node_tree
nt.nodes.clear()
rl=nt.nodes.new("CompositorNodeRLayers")
gl=nt.nodes.new("CompositorNodeGlare")
gl.glare_type='FOG_GLOW'
gl.quality='MEDIUM'
gl.threshold=1.5
gl.size=7
comp=nt.nodes.new("CompositorNodeComposite")
nt.links.new(rl.outputs["Image"],gl.inputs["Image"])
nt.links.new(gl.outputs["Image"],comp.inputs["Image"])
