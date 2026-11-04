from sceneact import *
import bpy, math, random

# Evidence / ownership ledger, approximate image bounds:
# Architecture: ivory panelled wall above brown parquet; curtain cropped left.
# Chaise: reference (18,91)-(426,356), high head left, long seat right.
# Pillow: (40,101)-(166,201), supported by seat and head.
# Label: (347,204)-(360,224), supported by cushion.
# Foreground cane chair: cropped at left and bottom, (0,305)-(105,384).
# Occlusion: foreground chair / chaise and pillow / curtain and wall.
# Owners: architecture/static support; chaise/all attached upholstery, frame,
# ornament; pillow/loose textile; label/card; curtain/folds;
# foreground_chair/cane, perimeter and legs.
#
# Observations from supplied step 2:
# Wall horizontal edges descend noticeably rightward, unlike the reference.
# Chaise head lies farther right; the right seat edge is already near its
# reference position. Foreground chair remains cropped at lower left.
# Hypothesis: excessive camera azimuth contributes to both wall-edge slope
# and head/foot perspective. Revise only camera parameters; retain geometry,
# materials, lighting, object ownership and all support heights.
# These are visual hypotheses, not measured calibration.

random.seed(8)
scene = Scene("Antique chaise room")
cream = (.78,.72,.59)
fabric = (.84,.79,.68)
sage = (.29,.36,.29)
gilt = (.64,.57,.40)
ivory = (.71,.69,.60)
trim = (.81,.78,.68)

def add(owner, name, node):
    return owner.include(name, node)

def tube(owner, name, points, radius, color):
    return add(owner, name, sweep_tube(points=points, radius=radius, color=color))

def ellipsoid(owner, name, center, dims, color):
    n = ball(1, center=center, color=color)
    n.resize(tuple(d/2 for d in dims))
    return add(owner, name, n)

arch = Asset("architecture")
add(arch, "floor_support", box((12,12,.10), center=(0,0,-.065),
                              color=(.19,.105,.063)))
parquet = Part("parquet")
for ix in range(-3,4):
    for iy in range(-3,4):
        for k in range(2):
            tone = random.uniform(.85,1.12)
            c = (.255*tone,.139*tone,.077*tone)
            if (ix+iy) % 2 == 0:
                size = (.796,.396,.014)
                pos = (ix*.8,iy*.8+(k-.5)*.4,-.005)
            else:
                size = (.396,.796,.014)
                pos = (ix*.8+(k-.5)*.4,iy*.8,-.005)
            add(parquet, f"board_{ix}_{iy}_{k}", box(size,center=pos,color=c))
parquet.turn("z",38,pivot=(0,0,0))
add(arch,"parquet",parquet)
add(arch,"rear_wall",box((9,.16,4.5),center=(0,1.12,2.20),color=ivory))
for i,(z,h,d) in enumerate([
    (.07,.14,.09),(.20,.065,.055),(.27,.035,.035),
    (2.20,.055,.035),(2.32,.025,.025)
]):
    add(arch,f"horizontal_moulding_{i}",
        box((8,d,h),center=(0,1.005-d/2,z),color=trim))

def wall_rectangle(name,x0,x1,z0,z1):
    for j,(inset,r) in enumerate([(0,.015),(.036,.009)]):
        xa,xb=x0+inset,x1-inset
        za,zb=z0+inset,z1-inset
        tube(arch,f"{name}_{j}",
             [(xa,.999,za),(xb,.999,za),(xb,.999,zb),
              (xa,.999,zb),(xa,.999,za)],r,trim)

wall_rectangle("large_panel",-1.72,1.78,.40,1.99)
add(arch,"wall_joint",box((.009,.014,4),center=(.28,1.025,2),
                          color=(.46,.44,.37)))
add(arch,"right_pilaster",box((.27,.32,3.8),center=(2.02,.99,1.9),
                              color=(.80,.79,.70)))
add(arch,"right_return",box((1.3,.13,4),center=(2.80,1.23,2),
                            color=(.74,.75,.68)))
wall_rectangle("right_panel",2.23,2.93,.35,2.1)
ellipsoid(arch,"wall_hook_a",(-1.38,.987,2.08),(.024,.03,.065),(.16,.14,.10))
ellipsoid(arch,"wall_hook_b",(-1.28,.982,2.07),(.047,.03,.055),(.12,.13,.10))
add(scene,"architecture",arch)

curtain = Asset("curtain")
for i in range(9):
    x=-2.06+i*.05
    y=.77+.045*math.sin(i*1.8)
    c=(.78,.72,.60) if i%3 else (.90,.86,.76)
    add(curtain,f"fold_{i}",
        rod(.038,start=(x,y,.04),end=(x,y,3.35),color=c))
add(curtain,"window_light_surface",
    box((.36,.025,3.6),center=(-2.24,.96,1.8),color=(.98,.98,.93)))
add(scene,"curtain",curtain)

# Chaise frame, decoration and upholstery share a single editable owner.
chaise = Asset("chaise")
seat_top = .795
add(chaise,"seat_cushion",
    fillet_box((2.48,1.02,.23),radius=.108,
               center=(.045,0,.68),color=fabric))
for index,z in enumerate((.596,.755)):
    pts=[]
    for i in range(41):
        a=2*math.pi*i/40
        x=.045+1.225*math.copysign(abs(math.cos(a))**.29,math.cos(a))
        y=.495*math.copysign(abs(math.sin(a))**.45,math.sin(a))
        pts.append((x,y,z))
    tube(chaise,f"seat_welt_{index}",pts,.008,(.68,.61,.47))

for j in range(-6,7):
    y=j*.07
    add(chaise,f"pinstripe_{j}",
        rod(.0016,start=(-1.07,y,.797),end=(1.13,y,.797),
            color=(.65,.57,.48)))
    for k in range(6):
        x=-.96+k*.39+(j%2)*.04
        add(chaise,f"woven_motif_{j}_{k}",
            box((.033,.009,.0015),center=(x,y+.015,.798),
                color=(.57,.36,.35)))

ellipsoid(chaise,"head_upholstery",(-1.13,.025,1.115),
          (.21,1.01,1.03),cream)
crown=[]
for i in range(19):
    t=i/18
    crown.append((-1.15,-.46+t*.96,1.48+.16*math.sin(math.pi*t)))
tube(chaise,"head_crown",crown,.034,sage)
tube(chaise,"head_crown_inlay",
     [(x+.026,y,z+.013) for x,y,z in crown],.010,gilt)

for side in (-1,1):
    top_pts=[]
    bottom_pts=[]
    for i in range(12):
        t=i/11
        x=-1.21+.69*t
        y=side*(.405+.105*math.sin(t*math.pi/2))
        top=1.37-.36*t+.035*math.sin(t*math.pi)
        bottom=.57-.035*math.sin(t*math.pi)
        add(chaise,f"side_upholstery_{side}_{i}",
            box((.068,.066,top-bottom),center=(x,y,(top+bottom)/2),
                color=cream))
        add(chaise,f"side_stripe_{side}_{i}",
            rod(.0024,start=(x,y+side*.034,bottom+.025),
                end=(x,y+side*.034,top-.026),color=(.57,.44,.36)))
        top_pts.append((x,y,top))
        bottom_pts.append((x,y,bottom))
    tube(chaise,f"arm_rail_{side}",top_pts,.035,sage)
    tube(chaise,f"arm_inlay_{side}",
         [(x,y+side*.017,z+.012) for x,y,z in top_pts],.010,gilt)
    tube(chaise,f"panel_base_{side}",bottom_pts,.033,sage)
    tube(chaise,f"panel_base_inlay_{side}",
         [(x,y+side*.022,z) for x,y,z in bottom_pts],.009,gilt)
    ellipsoid(chaise,f"arm_finial_{side}",top_pts[-1],(.082,.073,.085),gilt)

for side in (-1,1):
    pts=[]
    for i in range(23):
        t=i/22
        pts.append((-.58+t*1.79,side*.475,.505-.045*math.sin(math.pi*t)))
    tube(chaise,f"apron_{side}",pts,.046,sage)
    tube(chaise,f"apron_lower_trim_{side}",
         [(x,y+side*.026,z-.028) for x,y,z in pts],.009,gilt)
    tube(chaise,f"apron_upper_trim_{side}",
         [(x,y+side*.028,z+.027) for x,y,z in pts],.009,gilt)
tube(chaise,"foot_end_rail",
     [(1.20,-.46,.50),(1.27,-.29,.51),(1.29,0,.52),
      (1.27,.29,.51),(1.20,.46,.50)],.038,sage)

for i,xi in enumerate((-.67,1.13)):
    for side in (-1,1):
        y=side*.43
        sign=-1 if xi<0 else 1
        pts=[(xi,y,.53),(xi+sign*.035,y,.40),
             (xi-sign*.038,y+side*.027,.23),
             (xi-sign*.025,y+side*.045,.075),
             (xi+sign*.025,y+side*.06,.035)]
        tube(chaise,f"leg_{i}_{side}",pts,.034,sage)
        tube(chaise,f"leg_inlay_{i}_{side}",
             [(x,yy-.022,z) for x,yy,z in pts],.0085,gilt)
        ellipsoid(chaise,f"foot_{i}_{side}",pts[-1],(.10,.075,.04),gilt)

for i,(x,z,s) in enumerate([(.25,.455,1.0),(-.65,.51,.65),(1.16,.49,.65)]):
    for k in range(4):
        a=2*math.pi*k/4
        ellipsoid(chaise,f"carving_{i}_{k}",
                  (x+.056*s*math.cos(a),-.520,z+.029*s*math.sin(a)),
                  (.065*s,.025,.037*s),gilt)
    ellipsoid(chaise,f"carving_center_{i}",(x,-.542,z),
              (.061*s,.025,.046*s),trim)
add(scene,"chaise",chaise)

pillow = Asset("loose_pillow")
add(pillow,"body",
    fillet_box((.70,.25,.73),radius=.115,
               center=(-.89,-.075,1.19),color=(.91,.85,.72)))
tube(pillow,"seam",
     [(-1.19,-.206,.89),(-.59,-.206,.89),(-.57,-.206,1.49),
      (-1.20,-.206,1.49),(-1.19,-.206,.89)],.008,(.78,.70,.56))
for i in range(8):
    x=-1.17+i*.08
    add(pillow,f"woven_thread_{i}",
        rod(.0015,start=(x,-.202,.91),end=(x,-.202,1.47),
            color=(.83,.77,.65)))
pillow.turn("z",-21,pivot=(-.89,-.075,1.19))
pillow.turn("y",-13,pivot=(-.89,-.075,1.19))
add(scene,"pillow",pillow)

label = Asset("green_label")
add(label,"card",box((.095,.19,.006),center=(.75,.09,.802),
                     color=(.035,.22,.18)))
for j in range(4):
    add(label,f"letter_stroke_{j}",
        box((.038,.003,.001),center=(.75,.05+j*.015,.806),
            color=(.75,.78,.64)))
label.turn("z",-9,pivot=(.75,.09,.802))
add(scene,"label",label)

chair = Asset("foreground_chair")
cx,cy=-1.40,-1.57
add(chair,"seat_frame",
    fillet_box((.70,.69,.06),radius=.027,
               center=(cx,cy,.47),color=sage))
add(chair,"cane_ground",
    box((.59,.58,.009),center=(cx,cy,.505),color=(.49,.35,.20)))
for i in range(17):
    off=(i-8)*.033
    add(chair,f"cane_warp_{i}",
        rod(.0028,start=(cx-.28,cy+off,.512),
            end=(cx+.28,cy+off,.512),color=(.73,.57,.36)))
    add(chair,f"cane_weft_{i}",
        rod(.0028,start=(cx+off,cy-.275,.513),
            end=(cx+off,cy+.275,.513),color=(.73,.57,.36)))
for i,dx in enumerate((-.32,.32)):
    add(chair,f"side_rim_{i}",
        rod(.014,start=(cx+dx,cy-.31,.518),
            end=(cx+dx,cy+.31,.518),color=gilt))
    for j,dy in enumerate((-.31,.31)):
        add(chair,f"leg_{i}_{j}",
            rod(.026,start=(cx+dx,cy+dy,.46),
                end=(cx+dx*1.1,cy+dy*1.1,.02),color=sage))
for i,dy in enumerate((-.32,.32)):
    add(chair,f"cross_rim_{i}",
        rod(.024,start=(cx-.32,cy+dy,.51),
            end=(cx+.32,cy+dy,.51),color=sage))
chair.turn("z",-12,pivot=(cx,cy,.47))
add(scene,"foreground_chair",chair)

# Valid fillets: .108 <= .115; .115 <= .125; .027 <= .03.
# Rod and sweep adjacent endpoints are distinct; include keys are unique.
# No new meshes or material recoloring are applied after realization.
realize(scene)

# Camera-only correction; architecture and all semantic objects stay fixed.
camera_position = (-.60,-5.90,4.10)
camera_target = (.23,.04,.98)
camera_lens = 67
set_view(position=camera_position,target=camera_target,
         lens=camera_lens,sensor=36)

bs = bpy.context.scene
if bs.world is None:
    bs.world=bpy.data.worlds.new("World")
bs.world.use_nodes=True
background=bs.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.72,.75,.79,1)
background.inputs["Strength"].default_value=.32
area_emitter(position=(-3,-1.0,3.3),power=550,size=3.0,
             target=(-.3,.1,.7),color=(1,.91,.77))
area_emitter(position=(1,-2,4.5),power=120,size=3.5,
             target=(0,0,.7),color=(1,.96,.88))
bs.render.engine="CYCLES"
bs.cycles.samples=16
bs.cycles.use_denoising=True
bs.view_settings.view_transform="AgX"
for mat in bpy.data.materials:
    if mat.use_nodes:
        shader=mat.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Roughness"].default_value=.76
bs.render.resolution_x=512
bs.render.resolution_y=384
bs.render.resolution_percentage=100
