from sceneact import *
import bpy, math, random

# Evidence ledger (512x384 image; approximate visual hypotheses):
# Chaise: (18,91)-(426,356); head at upper left, long seat toward lower right.
# Seat top: (128,179)-(423,290); cream fabric with fine pink longitudinal motifs.
# Curved upholstered head and arms: (20,94)-(202,280); sage timber and pale gilt trim.
# Loose cream pillow: (40,101)-(166,201), supported by seat and leaning into head.
# Wall: upper half, ivory rectangular mouldings; floor: lower half, brown parquet.
# Curtain/window: cropped left edge. Partial cane chair: (0,305)-(105,384).
# Green museum label: (347,204)-(360,224), resting on seat.
# Occlusion: foreground chair / chaise legs / chaise body / wall and curtain.
#
# Ownership map:
# architecture -> wall, mouldings, floor; static support at z=0.
# chaise -> cushion, upholstery panels, timber frame, trim and four feet.
# pillow -> loose cushion, explicitly placed on seat top z=.795.
# label -> card and pale strokes, supported on seat.
# foreground_chair -> cane, rails and legs. Curtain -> hanging folds.
# Camera is independent of all object dimensions.

random.seed(8)
scene = Scene("Ivory room with antique chaise")

cream = (.78,.72,.59)
fabric = (.84,.79,.68)
pink = (.48,.27,.27)
sage = (.29,.36,.29)
gilt = (.64,.57,.40)
ivory = (.71,.69,.60)
trim = (.81,.78,.68)

def add(parent, name, node):
    return parent.include(name, node)

def tube(parent, name, points, radius, color):
    return add(parent, name, sweep_tube(points=points, radius=radius, color=color))

def ellipsoid(parent, name, center, dims, color):
    n = ball(1, center=center, color=color)
    n.resize(tuple(d/2 for d in dims))
    return add(parent, name, n)

# Architecture and near/far anchors.
arch = Asset("architecture")
add(arch, "subfloor", box((12,12,.10), center=(0,0,-.065), color=(.19,.105,.063)))
floor = Part("parquet")
# Basket parquet, rotated as a whole: individual boards retain visible seams.
for ix in range(-7,8):
    for iy in range(-7,8):
        for k in range(4):
            tone = random.uniform(.85,1.12)
            c = (.255*tone,.139*tone,.077*tone)
            if (ix+iy)%2 == 0:
                dims=(.636,.156,.018)
                pos=(ix*.64,iy*.64+(k-1.5)*.16,-.007)
            else:
                dims=(.156,.636,.018)
                pos=(ix*.64+(k-1.5)*.16,iy*.64,-.007)
            add(floor,f"board_{ix}_{iy}_{k}",box(dims,center=pos,color=c))
floor.turn("z",38,pivot=(0,0,0))
add(arch,"parquet",floor)
add(arch,"rear_wall",box((9,.16,4.5),center=(0,1.12,2.20),color=ivory))
for z,h,depth in [(.07,.14,.09),(.20,.065,.055),(.27,.035,.035),(2.20,.055,.035),(2.32,.025,.025)]:
    add(arch,f"horizontal_moulding_{z}",box((8,depth,h),center=(0,1.005-depth/2,z),color=trim))

def wall_rectangle(name,x0,x1,z0,z1):
    for j,(inset,r) in enumerate([(0,.015),(.036,.009)]):
        xa,xb=x0+inset,x1-inset
        za,zb=z0+inset,z1-inset
        tube(arch,f"{name}_{j}",[(xa,.999,za),(xb,.999,za),(xb,.999,zb),(xa,.999,zb),(xa,.999,za)],r,trim)

wall_rectangle("large_wall_panel",-1.72,1.78,.40,1.99)
add(arch,"wall_joint",box((.009,.014,4),center=(.28,1.025,2),color=(.46,.44,.37)))
add(arch,"right_pilaster",box((.27,.32,3.8),center=(2.02,.99,1.9),color=(.80,.79,.70)))
add(arch,"right_return",box((1.3,.13,4),center=(2.80,1.23,2),color=(.74,.75,.68)))
wall_rectangle("right_panel",2.23,2.93,.35,2.1)
# Small dark wall hardware visible above the head.
ellipsoid(arch,"wall_hook_a",(-1.38,.987,2.08),(.024,.03,.065),(.16,.14,.10))
ellipsoid(arch,"wall_hook_b",(-1.28,.982,2.07),(.047,.03,.055),(.12,.13,.10))
add(scene,"architecture",arch)

curtain=Asset("left_curtains")
for i in range(12):
    x=-2.06+i*.038
    y=.77+.045*math.sin(i*1.8)
    col=(.78,.72,.60) if i%3 else (.90,.86,.76)
    add(curtain,f"fold_{i}",rod(.035,start=(x,y,.04),end=(x,y,3.35),color=col))
add(curtain,"window_glow",box((.36,.025,3.6),center=(-2.24,.96,1.8),color=(.98,.98,.93)))
add(scene,"curtain",curtain)

# Chaise ownership includes every rigidly attached frame and textile part.
chaise=Asset("chaise")
seat_z=.795
add(chaise,"seat_cushion",fillet_box((2.48,1.02,.23),radius=.108,
    center=(.045,0,.68),color=fabric))
# Thin welt around the upper and lower upholstery edge.
for zi in (.596,.755):
    pts=[]
    for i in range(65):
        a=2*math.pi*i/64
        # Rounded rectangle, sampled by superellipse.
        x=.045+1.225*math.copysign(abs(math.cos(a))**.29,math.cos(a))
        y=.495*math.copysign(abs(math.sin(a))**.45,math.sin(a))
        pts.append((x,y,zi))
    tube(chaise,f"seat_welt_{zi}",pts,.008,(.68,.61,.47))

# Restrained woven stripe pattern; independent geometry on actual seat surface.
for j in range(-7,8):
    y=j*.061
    add(chaise,f"seat_pinstripe_{j}",rod(.0018,start=(-1.07,y,.797),
        end=(1.13,y,.797),color=(.65,.57,.48)))
    for k in range(23):
        x=-1.035+k*.094
        add(chaise,f"rose_dash_{j}_{k}",box((.024,.010,.0018),
            center=(x,y+.015,.798),color=(.57,.36,.35)))
        if (j+k)%3==0:
            add(chaise,f"small_weave_{j}_{k}",box((.007,.018,.0018),
                center=(x+.035,y+.016,.798),color=(.66,.47,.43)))

# Head panel: softly curved vertical upholstered end.
ellipsoid(chaise,"head_upholstery",(-1.13,.025,1.115),(.21,1.01,1.03),cream)
head_outline=[]
for i in range(25):
    t=i/24
    y=-.46+t*.96
    z=1.48+.16*math.sin(math.pi*t)
    head_outline.append((-1.15,y,z))
tube(chaise,"head_crown",head_outline,.034,sage)
tube(chaise,"head_crown_gilt",[(x+.026,y,z+.013) for x,y,z in head_outline],.010,gilt)
# Side panels descend into the seat, preserving the visible curved front arm.
for side in (-1,1):
    pts_top=[]
    pts_bottom=[]
    for i in range(22):
        t=i/21
        x=-1.21+.69*t
        y=side*(.405+.105*math.sin(t*math.pi/2))
        top=1.37-.36*t+.035*math.sin(t*math.pi)
        bottom=.57-.035*math.sin(t*math.pi)
        add(chaise,f"side_panel_{side}_{i}",box((.037,.066,top-bottom),
            center=(x,y,(top+bottom)/2),color=cream))
        pts_top.append((x,y,top))
        pts_bottom.append((x,y,bottom))
        add(chaise,f"panel_stripe_{side}_{i}",rod(.0024,
            start=(x,y+side*.034,bottom+.025),
            end=(x,y+side*.034,top-.026),color=(.57,.44,.36)))
    tube(chaise,f"arm_top_{side}",pts_top,.035,sage)
    tube(chaise,f"arm_inlay_{side}",[(x,y+side*.017,z+.012) for x,y,z in pts_top],.010,gilt)
    tube(chaise,f"panel_bottom_{side}",pts_bottom,.033,sage)
    tube(chaise,f"bottom_inlay_{side}",[(x,y+side*.022,z) for x,y,z in pts_bottom],.009,gilt)
    ellipsoid(chaise,f"arm_end_{side}",pts_top[-1],(.082,.073,.085),gilt)

# Seat rails and shaped apron.
for side in (-1,1):
    pts=[]
    for i in range(35):
        x=-.58+i*1.79/34
        z=.505-.045*math.sin(math.pi*i/34)
        pts.append((x,side*.475,z))
    tube(chaise,f"apron_{side}",pts,.046,sage)
    tube(chaise,f"apron_lower_gilt_{side}",[(x,y+side*.026,z-.028) for x,y,z in pts],.009,gilt)
    tube(chaise,f"apron_upper_gilt_{side}",[(x,y+side*.028,z+.027) for x,y,z in pts],.009,gilt)
tube(chaise,"foot_end_rail",[(1.20,-.46,.50),(1.27,-.29,.51),(1.29,0,.52),(1.27,.29,.51),(1.20,.46,.50)],.038,sage)

for xi in (-.67,1.13):
    for side in (-1,1):
        y=side*.43
        sign=-1 if xi<0 else 1
        pts=[(xi,y,.53),(xi+sign*.035,y,.40),
             (xi-sign*.038,y+side*.027,.23),
             (xi-sign*.025,y+side*.045,.075),
             (xi+sign*.025,y+side*.06,.035)]
        tube(chaise,f"leg_{xi}_{side}",pts,.034,sage)
        tube(chaise,f"leg_gilt_{xi}_{side}",[(x,y-.022,z) for x,y,z in pts],.0085,gilt)
        ellipsoid(chaise,f"foot_{xi}_{side}",pts[-1],(.10,.075,.04),gilt)

# Pale carving clusters at the center of the visible apron and joints.
for centerx,cz,scale in [(.25,.455,1.0),(-.65,.51,.65),(1.16,.49,.65)]:
    for k in range(7):
        a=2*math.pi*k/7
        ellipsoid(chaise,f"carving_{centerx}_{k}",
            (centerx+.067*scale*math.cos(a),-.520,cz+.037*scale*math.sin(a)),
            (.065*scale,.025,.037*scale),gilt)
    ellipsoid(chaise,f"carving_center_{centerx}",(centerx,-.542,cz),(.061*scale,.025,.046*scale),trim)
add(scene,"chaise",chaise)

pillow=Asset("loose_pillow")
add(pillow,"body",fillet_box((.70,.25,.73),radius=.115,
    center=(-.89,-.075,1.19),color=(.91,.85,.72)))
# Border follows the pillow face, with subtle woven lines.
tube(pillow,"pillow_seam",[(-1.19,-.206,.89),(-.59,-.206,.89),
    (-.57,-.206,1.49),(-1.20,-.206,1.49),(-1.19,-.206,.89)],.008,(.78,.70,.56))
for i in range(18):
    x=-1.19+i*.035
    add(pillow,f"woven_thread_{i}",rod(.0015,start=(x,-.202,.91),
        end=(x,-.202,1.47),color=(.83,.77,.65)))
pillow.turn("z",-21,pivot=(-.89,-.075,1.19))
pillow.turn("y",-13,pivot=(-.89,-.075,1.19))
add(scene,"pillow",pillow)

label=Asset("green_label")
add(label,"card",box((.095,.19,.006),center=(.75,.09,.802),color=(.035,.22,.18)))
for j in range(4):
    add(label,f"letter_stroke_{j}",box((.038,.003,.001),center=(.75,.05+j*.015,.806),color=(.75,.78,.64)))
label.turn("z",-9,pivot=(.75,.09,.802))
add(scene,"label",label)

# Cropped cane chair in the immediate lower left.
chair=Asset("foreground_chair")
cx,cy=-1.40,-1.57
add(chair,"seat_wood",fillet_box((.70,.69,.06),radius=.027,
    center=(cx,cy,.47),color=sage))
add(chair,"cane_surface",box((.59,.58,.009),center=(cx,cy,.505),color=(.49,.35,.20)))
for i in range(27):
    off=(i-13)*.021
    add(chair,f"cane_warp_{i}",rod(.0023,start=(cx-.28,cy+off,.512),
        end=(cx+.28,cy+off,.512),color=(.73,.57,.36)))
    add(chair,f"cane_weft_{i}",rod(.0023,start=(cx+off,cy-.275,.513),
        end=(cx+off,cy+.275,.513),color=(.73,.57,.36)))
for dx in (-.32,.32):
    for dy in (-.31,.31):
        add(chair,f"rim_{dx}_{dy}",rod(.014,start=(cx+dx,cy-.31,.518),
            end=(cx+dx,cy+.31,.518),color=gilt))
        add(chair,f"leg_{dx}_{dy}",rod(.026,start=(cx+dx,cy+dy,.46),
            end=(cx+dx*1.1,cy+dy*1.1,.02),color=sage))
for dy in (-.32,.32):
    add(chair,f"crossrim_{dy}",rod(.024,start=(cx-.32,cy+dy,.51),
        end=(cx+.32,cy+dy,.51),color=sage))
chair.turn("z",-12,pivot=(cx,cy,.47))
add(scene,"foreground_chair",chair)

realize(scene)

# Independent camera parameters, chosen for the oblique, elevated photographic view.
set_view(position=(2.45,-5.8,4.35),target=(-.02,.04,.98),lens=62,sensor=36)
scene_bpy=bpy.context.scene
if scene_bpy.world is None:
    scene_bpy.world=bpy.data.worlds.new("World")
scene_bpy.world.use_nodes=True
scene_bpy.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.72,.75,.79,1)
scene_bpy.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.32
area_emitter(position=(-3,-1.0,3.3),power=550,size=3.0,
             target=(-.3,.1,.7),color=(1,.91,.77))
area_emitter(position=(1,-2,4.5),power=120,size=3.5,
             target=(0,0,.7),color=(1,.96,.88))
scene_bpy.render.engine='CYCLES'
scene_bpy.cycles.samples=32
scene_bpy.view_settings.view_transform='AgX'
# All materials remain scoped to their SceneAct owners.
for mat in bpy.data.materials:
    if mat.use_nodes:
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Roughness"].default_value=.76
scene_bpy.render.resolution_x=512
scene_bpy.render.resolution_y=384
scene_bpy.render.resolution_percentage=100
