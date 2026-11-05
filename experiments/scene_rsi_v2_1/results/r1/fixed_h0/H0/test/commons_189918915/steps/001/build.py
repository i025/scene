from sceneact import *
import bpy
import math
import random
from mathutils import Quaternion

random.seed(23)
scene = Scene("Warehouse")
steel = (.19, .215, .16)
edge = (.30, .32, .23)
yellow = (.78, .51, .035)
dark = (.085, .105, .075)
ceiling = (.27, .28, .205)

def block(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Building")
block(architecture, "floor", (19, 49, .22), (0, 16, -.16), (.27, .26, .20))
block(architecture, "roof", (18, 49, .16), (0, 16, 12.5), ceiling)
block(architecture, "end_wall", (18, .25, 13), (0, 38, 6), (.37, .37, .28))

# Corrugated roof decking, structural purlins, and exposed service pipes.
for i in range(67):
    x = -8.6 + i * .265
    block(architecture, "roof_rib_%d" % i, (.045, 49, .11),
          (x, 16, 12.36), (.20, .225, .17))
for j, y in enumerate(range(-7, 40, 5)):
    block(architecture, "roof_girder_%d" % j, (18, .18, .43),
          (0, y, 12.02), (.23, .245, .175))
    block(architecture, "girder_flange_%d" % j, (18, .33, .065),
          (0, y, 11.82), edge)
for x in (-1.15, 2.6, 4.9):
    architecture.include("conduit_" + str(x),
                         rod(.026, start=(x, -8, 12.11),
                             end=(x, 40, 12.11), color=(.38, .39, .29)))
for j in range(8):
    y = -5 + j * 6
    block(architecture, "cross_service_%d" % j, (15, .035, .035),
          (0, y, 11.69), (.40, .41, .30))
scene.include("architecture", architecture)

def rack(name, front_x, back_x, ystart, count, pitch, levels):
    a = Asset(name)
    for j in range(count + 1):
        y = ystart + j * pitch
        for k, x in enumerate((front_x, back_x)):
            block(a, "upright_%d_%d" % (j, k), (.12, .13, 11.25),
                  (x, y, 5.625), edge)
            block(a, "post_channel_%d_%d" % (j, k), (.045, .16, 11.2),
                  (x + .065, y, 5.6), steel)
            block(a, "foot_%d_%d" % (j, k), (.29, .30, .07),
                  (x, y, .055), steel)
            # Closely spaced punched slots are conspicuous on the tall front posts.
            if k == 0:
                for h in range(66):
                    z = .22 + h * .165
                    block(a, "slot_%d_%d" % (j, h), (.008, .043, .063),
                          (x + (.066 if front_x > back_x else -.066), y, z), dark)
        for z in (1.1, 3.35, 5.6, 7.85, 10.1):
            block(a, "frame_tie_%d_%s" % (j, z),
                  (abs(front_x-back_x), .09, .085),
                  ((front_x+back_x)/2, y, z), steel)
        for h in range(4):
            z0 = .5 + h * 2.5
            a.include("diagonal_%d_%d" % (j, h),
                      rod(.027, start=(back_x, y, z0),
                          end=(front_x, y, z0+2.1), color=edge))
    for l, z in enumerate(levels):
        for side, x in enumerate((front_x, back_x)):
            block(a, "long_beam_%d_%d" % (l, side),
                  (.15, count*pitch, .19),
                  (x, ystart+count*pitch/2, z), steel)
            block(a, "beam_lip_%d_%d" % (l, side),
                  (.19, count*pitch, .035),
                  (x, ystart+count*pitch/2, z+.105), edge)
        for j in range(count):
            cy = ystart+(j+.5)*pitch
            # Open steel shelf grid.
            for n in range(8):
                yy = ystart+j*pitch+(n+.5)*pitch/8
                block(a, "shelf_bar_%d_%d_%d" % (l,j,n),
                      (abs(front_x-back_x)+.12, .065, .075),
                      ((front_x+back_x)/2, yy, z+.08), steel)
            for yy in (cy-.77, cy+.77):
                block(a, "yellow_socket_%d_%d_%s" % (l,j,yy),
                      (.34, .25, .26), (front_x, yy, z+.16), yellow)
                block(a, "socket_lip_%d_%d_%s" % (l,j,yy),
                      (.40, .29, .055), (front_x, yy, z+.30), yellow)
                block(a, "socket_dark_%d_%d_%s" % (l,j,yy),
                      (.012, .13, .095),
                      (front_x + (.207 if front_x>back_x else -.207), yy, z+.16), dark)
            # Small pale location labels attached to the aisle beam.
            block(a, "label_%d_%d" % (l,j), (.014, .30, .105),
                  (front_x + (.085 if front_x>back_x else -.085), cy, z-.005),
                  (.65, .62, .37))
            for t in range(5):
                block(a, "label_mark_%d_%d_%d" % (l,j,t),
                      (.016, .012, .052),
                      (front_x + (.094 if front_x>back_x else -.094),
                       cy-.10+t*.041, z), (.20,.22,.14))
    scene.include(name, a)

levels = [1.0, 3.2, 5.4, 7.6, 9.8]
rack("Left_racking", -1.72, -4.05, -4.1, 14, 2.65, levels)
rack("Right_racking", 4.0, 6.25, -1.8, 13, 2.65, levels)

def cargo(name, x, y, base, width, depth, height, tint, aisle_side=1):
    a = Asset(name)
    pallet_z = base+.19
    for yy in (y-depth*.37, y, y+depth*.37):
        block(a, "pallet_runner_"+str(yy), (width, .13, .13),
              (x, yy, pallet_z), (.43,.32,.13))
    for xx in (x-width*.39, x, x+width*.39):
        block(a, "pallet_top_"+str(xx), (.17, depth+.10, .06),
              (xx, y, pallet_z+.085), (.58,.44,.21))
    bottom = base+.31
    block(a, "wrapped_load", (width, depth, height),
          (x,y,bottom+height/2), tint)
    # Individual cardboard seams underneath the translucent wrapping.
    face_x = x+aisle_side*(width/2+.004)
    for k in range(1, 4):
        z = bottom+height*k/4
        block(a, "carton_joint_"+str(k), (.008, depth, .014),
              (face_x,y,z), tuple(v*.73 for v in tint))
    for j in range(2):
        yy = y-depth*.25+j*depth*.5
        block(a, "vertical_joint_"+str(j), (.009,.012,height),
              (face_x+.002*aisle_side,yy,bottom+height/2),
              tuple(v*.80 for v in tint))
    # Thin overlapping horizontal stretch-film bands.
    for k in range(max(7,int(height/.065))):
        z = bottom+.025+k*.065
        if z > bottom+height:
            break
        shade = random.choice([.86,.94,1.07,1.14])
        c = tuple(min(.91,v*shade) for v in tint)
        block(a, "film_line_"+str(k), (width+.012,depth+.016,random.uniform(.008,.021)),
              (x,y,z),c)
    for j in range(3):
        yy=y+random.uniform(-depth*.42,depth*.42)
        block(a, "film_fold_"+str(j), (.013,random.uniform(.014,.032),height*.92),
              (face_x+aisle_side*.008, yy,bottom+height/2),
              tuple(min(.94,v*1.16) for v in tint))
    # Broad cream packing straps and small shipping stickers.
    if random.random()<.65:
        yy=y+depth*.19
        block(a,"packing_strap",(.017,.045,height+.015),
              (face_x+aisle_side*.015,yy,bottom+height/2),(.68,.62,.40))
    if random.random()<.55:
        block(a,"paper_label",(.018,.25,.20),
              (face_x+aisle_side*.018,y-depth*.16,bottom+height*.63),
              (.75,.73,.55))
    scene.include(name,a)

for l,z in enumerate(levels):
    for j in range(14):
        if (l,j) in [(1,1),(2,2),(3,1),(2,4),(0,3)]:
            continue
        y=-4.1+(j+.5)*2.65
        h=random.uniform(1.25,1.77)
        w=random.uniform(1.45,1.95)
        dep=random.uniform(1.40,1.90)
        tint=random.choice([(.62,.54,.34),(.70,.63,.44),(.54,.47,.29),
                            (.74,.68,.48),(.58,.52,.36)])
        cargo("left_load_%d_%d"%(l,j),-2.80,y,z,w,dep,h,tint,1)

for l,z in enumerate(levels):
    for j in range(13):
        if random.random()<.20:
            continue
        cargo("right_load_%d_%d"%(l,j),5.10,-1.8+(j+.5)*2.65,z,
              1.8,1.8,random.uniform(1.25,1.8),(.58,.51,.32),-1)

fixtures = Asset("Ceiling_lights")
for j,y in enumerate([-5.0,-.7,3.6,7.9,12.2,16.5,20.8,25.1,29.4,33.7]):
    block(fixtures,"fixture_housing_%d"%j,(.29,2.55,.105),
          (.10,y,11.88),(.47,.48,.36))
    block(fixtures,"bright_tube_a_%d"%j,(.085,2.39,.04),
          (.025,y,11.806),(1.0,.975,.77))
    block(fixtures,"bright_tube_b_%d"%j,(.085,2.39,.04),
          (.17,y,11.806),(1.0,.975,.77))
    for yy in (y-1,y+1):
        fixtures.include("suspension_%s_%s"%(j,yy),
                         rod(.012,start=(.1,yy,11.94),end=(.1,yy,12.35),color=edge))
# Rectangular translucent roof light with a dense metal grid.
sx,sy=1.55,3.0
block(fixtures,"skylight",(2.35,3.7,.025),(sx,sy,12.365),(.84,.91,.86))
for n in range(9):
    block(fixtures,"skylight_grid_x_%d"%n,(.035,3.78,.045),
          (sx-1.175+n*2.35/8,sy,12.325),(.24,.28,.22))
for n in range(13):
    block(fixtures,"skylight_grid_y_%d"%n,(2.40,.035,.045),
          (sx,sy-1.85+n*3.7/12,12.32),(.24,.28,.22))
scene.include("fixtures", fixtures)

realize(scene)

# Give the luminous fixture surfaces physical emission.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    c=bsdf.inputs["Base Color"].default_value
    bsdf.inputs["Roughness"].default_value=.68
    if c[0]>.95 and c[1]>.9:
        bsdf.inputs["Emission Color"].default_value=(1.0,.94,.63,1)
        bsdf.inputs["Emission Strength"].default_value=7
    elif c[0]>.80 and c[1]>.87 and c[2]>.80:
        bsdf.inputs["Emission Color"].default_value=(.80,.91,1,1)
        bsdf.inputs["Emission Strength"].default_value=2.8

set_view((.50,-5.2,1.35),(-.20,8.5,8.45),lens=21.5,sensor=36)
cam=bpy.context.scene.camera
cam.rotation_euler=(cam.rotation_euler.to_quaternion() @
                    Quaternion((0,0,1),math.radians(13))).to_euler()

for y in [-3,3,9,15,22,30]:
    area_emitter((.1,y,11.65),power=1250,size=3.1,
                 target=(-1.9,y+1,4.4),color=(1,.83,.46))
area_emitter((1.55,3,12.12),power=1650,size=2.4,
             target=(-2,4,4.5),color=(.83,.91,1))
area_emitter((1,-6,7.5),power=450,size=4,
             target=(-3,0,6),color=(1,.78,.39))

sc=bpy.context.scene
sc.render.resolution_x=341
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.24,.27,.19,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.20
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.25
# A modest optical bloom captures the bright fluorescent strips.
sc.use_nodes=True
tree=sc.node_tree
tree.nodes.clear()
rl=tree.nodes.new("CompositorNodeRLayers")
glare=tree.nodes.new("CompositorNodeGlare")
glare.glare_type='FOG_GLOW'
glare.quality='HIGH'
glare.threshold=1.6
glare.mix=-.87
out=tree.nodes.new("CompositorNodeComposite")
tree.links.new(rl.outputs["Image"],glare.inputs["Image"])
tree.links.new(glare.outputs["Image"],out.inputs["Image"])
