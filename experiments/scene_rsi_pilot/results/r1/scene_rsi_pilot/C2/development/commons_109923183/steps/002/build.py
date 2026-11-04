from sceneact import *
import bpy
import math

# Evidence / revision ledger:
# Measured: step 1 returned a valid render; reported execution elapsed 12.415 s.
# The following image coordinates are visual estimates, not calibration.
# Reference chaise bounds approximately (18,90)-(424,358);
# step 1 approximately (120,97)-(392,314): whole owner is too small.
# Near anchor: foreground cane chair reference (0,307)-(96,384),
# render approximately (0,237)-(90,352); its crop/contact needs comparison again.
# Far anchor: wall baseboard reference near y=190, render near y=216.
# Architectural horizontal edges are nearly horizontal in both images.
# Head reference upper silhouette near (30,96), render near (137,100).
# Foot reference near (405,351), render near (340,309).
# Chosen family: camera only. Increase focal length and modestly raise the
# look target to enlarge furniture while keeping its head inside the frame.
# Prediction: chaise foot and chair crop move outward; wall junction moves up.
# Relative geometry, all material assignments and lighting remain fixed.
# Residual head/pillow shape discrepancies are deliberately left for inspection.
#
# Inventory and ownership:
# chaise/build_chaise owns platform, cushion, head, wings, apron, feet and trim.
# pillow owns its rounded body/face, inclined against the head and seat.
# card owns paper/print, supported on actual cushion surface z=.845.
# architecture owns rear wall, panel outlines, moldings and right return.
# curtain owns window surface and hanging folds; floor supports furniture.
# foreground_chair owns cane seat, rails and cropped legs.
# Front apron occludes rear feet; near wing overlaps head and pillow.
# Reference bounds: pillow (40,101)-(165,207), card (347,204)-(361,224).
# Curtain is cropped at left. Head curvature and chair placement remain uncertain.

CAMERA = dict(position=(3.25, -6.0, 3.65),
              target=(.12, 0.0, 1.00), lens=64)
ROOM_ANGLE = 24
CHAISE_LENGTH = 2.65
SEAT_Z = .72
SEAT_TOP = .845

ivory = (.70, .675, .59)
wall_color = (.76, .735, .66)
molding = (.81, .785, .70)
fabric = (.83, .775, .66)
seat_fabric = (.84, .785, .705)
pink = (.59, .38, .37)
sage = (.34, .39, .33)
worn_gold = (.57, .51, .36)
wood = (.19, .105, .065)
cane = (.48, .37, .21)

scene = Scene('French chaise room')

def ellipsoid(size, center, color):
    return ball(1, center=center, color=color).resize(size, pivot=center)

def tube(parent, name, points, radius, color):
    parent.include(name, sweep_tube(points=points, radius=radius, color=color))

def build_chaise():
    a = Asset('chaise')
    a.include('platform', fillet_box((2.69, 1.13, .14), .065,
                                    center=(.03, 0, .565), color=sage))
    a.include('seat_cushion', fillet_box((CHAISE_LENGTH, 1.08, .25), .12,
                                        center=(.03, 0, SEAT_Z), color=seat_fabric))
    for i in range(9):
        y = -.43 + i * .105
        tube(a, 'woven_stripe_%02d' % i,
             [(-1.12, y, .846), (1.12, y, .846)], .0025,
             (.67, .51, .48))

    a.include('head_upholstery',
              ellipsoid((.115, .555, .60), (-1.28, .015, 1.12), fabric))
    head_outline = [
        (-1.23,-.54,.65), (-1.35,-.58,1.03), (-1.40,-.49,1.48),
        (-1.40,-.31,1.67), (-1.40,.03,1.72), (-1.39,.35,1.60),
        (-1.34,.55,1.29), (-1.23,.57,.90), (-1.04,.55,.77)]
    tube(a, 'head_outer_frame', head_outline, .037, sage)
    tube(a, 'head_gilt_edge',
         [(x+.012,y-.012,z+.014) for x,y,z in head_outline], .011, worn_gold)

    wing = ellipsoid((.37,.075,.40), (-1.065,-.505,.995), fabric)
    wing.turn('y', -27, pivot=(-1.065,-.505,.995))
    a.include('near_wing_upholstery', wing)
    near_outline = [
        (-1.39,-.53,1.47), (-1.29,-.59,1.24), (-1.12,-.59,1.12),
        (-.91,-.59,1.04), (-.72,-.57,1.04), (-.69,-.57,.91),
        (-.67,-.57,.72), (-.56,-.56,.61)]
    tube(a, 'near_wing_crest', near_outline, .032, sage)
    tube(a, 'near_wing_inner_bead',
         [(x,y-.018,z-.028) for x,y,z in near_outline], .009, worn_gold)
    tube(a, 'near_wing_lower_border',
         [(-1.37,-.55,1.02),(-1.27,-.59,.72),(-1.08,-.59,.60),
          (-.82,-.59,.57),(-.58,-.56,.61)], .025, sage)
    tube(a, 'far_arm',
         [(-1.30,.53,1.40),(-1.08,.56,1.21),(-.85,.56,1.10),
          (-.66,.55,1.10),(-.69,.54,.93),(-.57,.53,.77)],
         .028, sage)
    tube(a, 'far_arm_gold',
         [(-1.29,.52,1.42),(-1.07,.55,1.23),(-.84,.55,1.12),
          (-.66,.54,1.12)], .008, worn_gold)

    apron = [(-1.12,-.565,.56),(-.83,-.575,.54),(-.45,-.58,.50),
             (0,-.58,.48),(.43,-.58,.49),(.88,-.57,.52),(1.26,-.53,.54)]
    tube(a, 'front_apron', apron, .057, sage)
    tube(a, 'apron_upper_gilt', [(x,y-.014,z+.041) for x,y,z in apron],
         .011, worn_gold)
    tube(a, 'apron_lower_gilt', [(x,y-.020,z-.037) for x,y,z in apron],
         .009, worn_gold)
    tube(a, 'foot_end_rail', [(1.26,-.53,.54),(1.36,-.32,.56),
                             (1.38,.0,.56),(1.35,.35,.56),(1.26,.53,.54)],
         .033, sage)
    for label, x, y in [('head_near',-1.03,-.47),
                        ('head_far',-1.12,.43),
                        ('foot_near',1.20,-.45),
                        ('foot_far',1.20,.44)]:
        sign = -1 if x < 0 else 1
        pts = [(x,y,.56),(x+sign*.04,y,.43),
               (x+sign*.015,y-.015,.27),(x-sign*.035,y-.03,.10),
               (x+sign*.025,y-.055,.035)]
        tube(a, label+'_leg', pts, .032, sage)
        tube(a, label+'_leg_highlight',
             [(px,py-.022,pz+.003) for px,py,pz in pts], .008, worn_gold)
    for j in range(7):
        t = 2*math.pi*j/7
        a.include('apron_rosette_%d' % j,
                  ellipsoid((.032,.018,.024),
                            (.05+.065*math.cos(t),-.645,.48+.040*math.sin(t)),
                            worn_gold))
    for j in range(3):
        a.include('crest_ornament_%d' % j,
                  ellipsoid((.031,.026,.024),
                            (-1.405,-.13+j*.075,1.715),worn_gold))
    return a

scene.include('chaise', build_chaise())

pillow = Asset('pillow')
pillow_center = (-1.025, -.045, 1.18)
pillow.include('soft_body', fillet_box((.25,.73,.72), .12,
                                     center=pillow_center,
                                     color=(.88,.825,.71)))
pillow.include('soft_face', ellipsoid((.16,.345,.325),
                                      (-.92,-.045,1.18),(.88,.825,.71)))
pillow.turn('y', -18, pivot=pillow_center)
pillow.turn('z', -19, pivot=pillow_center)
scene.include('pillow', pillow)

card = Asset('green_card')
card.include('paper', box((.105,.19,.006), center=(.84,.10,.852),
                          color=(.055,.235,.205)))
for i in range(3):
    card.include('print_%d'%i,
                 box((.042,.004,.001), center=(.84,.055+i*.025,.856),
                     color=(.72,.76,.66)))
card.turn('z', -8, pivot=(.84,.10,.852))
scene.include('card',card)

floor = Asset('floor')
floor.include('parquet_surface', box((14,14,.12),center=(0,0,-.065),color=wood))
scene.include('floor',floor)

architecture = Asset('architecture')
architecture.include('wall',box((9,.16,3.7), center=(0,1.55,1.85),color=wall_color))
for i,(z,h,d) in enumerate([(.095,.17,.10),(.24,.045,.07),
                             (.39,.035,.045),(2.10,.045,.055),
                             (2.25,.055,.06),(2.49,.045,.055)]):
    architecture.include('horizontal_molding_%d'%i,
                         box((9,d,h),center=(0,1.435,z),color=molding))
for idx,(left,right) in enumerate([(-3.7,-1.72),(-1.65,.45),(.52,2.65)]):
    z0,z1=.54,1.98
    for side,x in [('left',left),('right',right)]:
        architecture.include('panel_%d_%s'%(idx,side),
                             box((.027,.031,z1-z0),center=(x,1.445,(z0+z1)/2),
                                 color=molding))
    for side,z in [('bottom',z0),('top',z1)]:
        architecture.include('panel_%d_%s'%(idx,side),
                             box((right-left,.031,.027),center=((left+right)/2,1.445,z),
                                 color=molding))
architecture.include('right_return',box((.16,1.35,3.7),
                                        center=(2.88,1.00,1.85),color=(.79,.78,.70)))
architecture.include('return_vertical_trim',box((.035,.045,2.6),
                                               center=(2.785,.45,1.52),color=molding))
architecture.turn('z',ROOM_ANGLE,pivot=(0,0,0))
scene.include('architecture',architecture)

curtain=Asset('curtain')
curtain.include('window_light_surface',
                box((.10,1.12,3.15),center=(-2.35,.50,1.575),
                    color=(.92,.92,.84)))
for i in range(6):
    x=-2.32+i*.062
    curtain.include('fold_%d'%i,
                    ellipsoid((.065,.10,1.57),(x,.28,1.60),
                              (.79+i*.012,.755+i*.012,.66+i*.013)))
curtain.turn('z',ROOM_ANGLE,pivot=(0,0,0))
scene.include('curtain',curtain)

chair=Asset('foreground_cane_chair')
cx,cy=-1.55,-1.77
for label,y in [('front',cy-.36),('back',cy+.36)]:
    chair.include(label+'_rail',box((.78,.055,.065),
                                   center=(cx,y,.49),color=worn_gold))
for label,x in [('left',cx-.39),('right',cx+.39)]:
    chair.include(label+'_rail',box((.055,.76,.065),
                                   center=(x,cy,.49),color=sage))
for i in range(15):
    t=-.33+i*.047
    chair.include('cane_x_%02d'%i,
                  rod(.005,start=(cx-.35,cy+t,.50),end=(cx+.35,cy+t,.50),color=cane))
    chair.include('cane_y_%02d'%i,
                  rod(.005,start=(cx+t,cy-.33,.505),end=(cx+t,cy+.33,.505),color=cane))
for i,x in enumerate([cx-.34,cx+.34]):
    chair.include('leg_%d'%i,rod(.025,start=(x,cy-.28,.015),
                                end=(x,cy-.28,.48),color=sage))
chair.turn('z',-15,pivot=(cx,cy,0))
scene.include('foreground_chair',chair)

# Inline pre-execution self-review:
# Every semantic owner and all attachments retained; no duplication or visibility moves.
# Supports remain floor near z=0, platform top=.635, cushion top=.845.
# Pillow contact remains an approximation; camera revision cannot certify contact.
# Render has pale wall/seat and darker floor/shadows in the correct broad ordering,
# but appears less richly contrasted than reference; appearance remains unchanged.
# Sweep expansion is 2*n-1; straight decorative stripes use two points.
# Four fillet boxes expand to 92 primitives; cane contributes 30 straight rods;
# curved paired frame tubes are the other expensive family. Tiny textile marks deferred.
# Sizes finite and positive; radii fit half minimum dimensions; all tube segments
# have distinct endpoints; loops assign unique slots. Composites retain their transforms.
# No local Blender material changes: all non-target materials and mesh data preserved.
# Realize precedes camera/world/lights. No runner-owned settings, saving or rendering.

realize(scene)
set_view(**CAMERA)
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new('World')
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.70,.73,.77,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.33
area_emitter(position=(-3.4,-1.2,3.4),power=650,size=3.2,
             target=(-.3,0,.65),color=(1.0,.93,.81))
area_emitter(position=(1.4,-3.7,4.6),power=170,size=4,
             target=(0,0,.6),color=(.94,.96,1.0))
