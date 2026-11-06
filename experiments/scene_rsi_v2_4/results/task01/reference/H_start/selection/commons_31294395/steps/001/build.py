from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory (normalized bounds, approximate):
# Room: pale floor below .62; patterned ochre walls; white cornice at top.
# Back windows: left (-.03,.06,.13,.60), middle (.23,.07,.44,.60);
# white deep frames, green roller shades, bright exposed lower panes.
# Portraits: oval gold (.13,.16,.25,.36), small pale (.47,.15,.54,.28),
# and right-wall miniature (.66,.16,.71,.30).
# Bed (.51,.47,.99,.97): dark sleigh frame, high head at right,
# cream mattress and rumpled cover, two overlapping pillows.
# Olive upholstered chair (.28,.50,.54,.94), obscuring bed foot and screen.
# Painted folding screen (.41,.33,.62,.67), blue/gold with sparse figurative motifs.
# Left cabinet (.00,.47,.12,.67), lace-covered small table (.15,.48,.26,.65),
# little wastebasket, black spindle chair behind bed, bedside round dark cabinet.
# Two patterned rugs, lower rug cut by image edge. Hidden furniture backs uncertain.
# Assets below retain semantic parts. Estimated expanded count ~370 meshes,
# including ~100 portrait-frame rods, ~50 chair/bed parts, ~45 screen decorations,
# ~45 carpet strips, ~55 architecture/window parts, and other furnishings.
random.seed(13)
scene=Scene('Historic bedroom')
C={
'wood':(.075,.035,.022),'woodlight':(.15,.075,.037),
'white':(.87,.87,.81),'trim':(.91,.92,.89),
'linen':(.78,.78,.68),'olive':(.29,.29,.065),
'gold':(.55,.34,.08),'wall':(.43,.29,.16)
}
def asset(name):
    a=Asset(name); scene.include(name,a); return a
def bx(a,n,s,p,c):
    v=box(s,center=p,color=c); a.include(n,v); return v
def ell(a,n,p,s,c):
    v=ball(1,center=p,color=c); v.resize(s); a.include(n,v); return v
def rd(a,n,p,q,r,c):
    v=rod(r,start=p,end=q,color=c);a.include(n,v);return v
def oval(a,n,x,y,z,rx,rz,r,c):
    pts=[(x+rx*math.cos(2*math.pi*i/28),y,z+rz*math.sin(2*math.pi*i/28)) for i in range(29)]
    for i in range(28): rd(a,n+str(i),pts[i],pts[i+1],r,c)

room=asset('architecture')
bx(room,'stone_floor',(8,10,.12),(0,0,-.08),(.53,.52,.45))
bx(room,'back_wall',(7,.16,3.45),(-.2,3.50,1.71),C['wall'])
bx(room,'right_wall',(.16,9,3.45),(3.22,-.90,1.71),C['wall'])
bx(room,'ceiling',(7.2,9,.12),(-.25,-.8,3.49),(.85,.86,.83))
for z,depth,height in [(3.29,.15,.08),(3.37,.23,.09),(3.43,.30,.06)]:
    bx(room,'back_cornice_'+str(z),(7,depth,height),(-.2,3.37,z),C['trim'])
    bx(room,'right_cornice_'+str(z),(depth,9,height),(3.08,-.8,z),C['trim'])
bx(room,'back_skirt',(7,.10,.16),(-.2,3.36,.08),(.29,.20,.13))
bx(room,'right_skirt',(.10,9,.16),(3.09,-.8,.08),(.29,.20,.13))

for k,x in enumerate([-3.03,-.97]):
    w=1.29 if k==0 else 1.35
    a=asset('window_'+str(k))
    bx(a,'dark_recess',(w+.15,.10,2.61),(x,3.37,1.85),(.15,.20,.17))
    bx(a,'luminous_glazing',(w-.11,.045,2.37),(x,3.29,1.87),(.77,.91,.89))
    for xx in [x-w/2,x+w/2]:
        bx(a,'jamb_'+str(xx),(.105,.22,2.66),(xx,3.23,1.86),C['trim'])
        bx(a,'molding_'+str(xx),(.035,.25,2.78),(xx+(-.085 if xx<x else .085),3.24,1.86),(.72,.74,.71))
    for zz in [.54,3.16]:
        bx(a,'cross_frame_'+str(zz),(w+.13,.25,.11),(x,3.22,zz),C['trim'])
    bx(a,'sill',(w+.23,.37,.09),(x,3.15,.53),C['trim'])
    bx(a,'green_roller_blind',(w-.17,.035,1.42),(x,3.16,2.36),(.13,.32,.28))
    bx(a,'blind_bottom',(w-.15,.045,.025),(x,3.135,1.65),(.32,.48,.41))

# Portraits, with flattened painted figures behind oval gilt moldings.
a=asset('large_oval_portrait')
ell(a,'black_oval',(-2.02,3.20,2.38),(.39,.035,.51),(.035,.025,.018))
oval(a,'outer_gilt_',-2.02,3.145,2.38,.42,.54,.027,C['gold'])
oval(a,'inner_gilt_',-2.02,3.12,2.38,.365,.475,.012,(.76,.55,.22))
ell(a,'coat',(-2.02,3.10,2.20),(.21,.012,.22),(.045,.035,.028))
ell(a,'face',(-2.03,3.08,2.48),(.075,.013,.11),(.45,.28,.16))
ell(a,'hair',(-2.05,3.07,2.56),(.08,.014,.05),(.075,.045,.025))
bx(a,'collar',(.075,.018,.045),(-2.00,3.075,2.37),(.65,.60,.48))
a=asset('small_back_portrait')
bx(a,'gilt_frame',(.50,.08,.66),(.64,3.24,2.69),(.62,.49,.24))
bx(a,'ivory_mat',(.44,.035,.60),(.64,3.18,2.69),(.81,.79,.67))
ell(a,'gray_picture',(.64,3.15,2.69),(.145,.015,.225),(.40,.40,.35))
ell(a,'head',(.64,3.125,2.76),(.055,.012,.075),(.58,.56,.48))
a=asset('right_wall_miniature')
bx(a,'frame',(.065,.37,.60),(3.08,2.15,2.63),(.68,.51,.23))
bx(a,'mat',(.025,.32,.54),(3.035,2.15,2.63),(.85,.83,.73))
ell(a,'oval_image',(3.015,2.15,2.63),(.014,.10,.20),(.42,.39,.34))

# White narrow door partly concealed by screen.
a=asset('back_door')
bx(a,'door_surround',(.67,.13,2.30),(1.56,3.27,1.22),C['trim'])
bx(a,'door_leaf',(.55,.04,2.15),(1.56,3.18,1.20),(.76,.79,.74))
for z in [.64,1.66]:
    bx(a,'panel_'+str(z),(.43,.025,.80),(1.56,3.145,z),(.82,.84,.79))

a=asset('left_chest')
bx(a,'body',(1.03,.51,.65),(-3.12,2.73,.37),C['wood'])
bx(a,'top',(1.12,.60,.065),(-3.12,2.73,.73),C['woodlight'])
for x in [-3.55,-2.69]:
    for y in [2.52,2.95]:
        rd(a,'turned_leg'+str((x,y)),(x,y,.02),(x,y,.28),.047,C['wood'])
for z in [.27,.49]:
    bx(a,'drawer_'+str(z),(.94,.025,.18),(-3.12,2.46,z),(.13,.065,.032))
    for x in [-3.37,-2.87]: ell(a,'knob'+str((z,x)),(x,2.425,z),(.025,.025,.025),C['gold'])
bx(a,'small_picture_frame',(.29,.055,.35),(-3.23,2.70,.94),C['gold'])
bx(a,'small_picture',(.24,.025,.30),(-3.23,2.66,.94),(.12,.15,.10))

a=asset('small_lace_table')
bx(a,'top',(.74,.52,.055),(-1.91,2.74,.73),C['wood'])
for x in [-2.19,-1.63]:
    for y in [2.56,2.91]:
        rd(a,'leg'+str((x,y)),(x,y,.05),(x,y,.72),.025,C['wood'])
bx(a,'linen_top',(.77,.55,.015),(-1.91,2.72,.77),(.83,.81,.71))
# triangular hanging tablecloth, flattened mesh generated after SceneAct.
cloth=bx(a,'hanging_lace',(.64,.025,.30),(-1.91,2.425,.61),(.80,.79,.69))
cloth.turn('y',0)
for x in [-2.08,-1.78]:
    ell(a,'teacup'+str(x),(x,2.70,.805),(.065,.055,.035),(.78,.73,.55))
    ell(a,'saucer'+str(x),(x,2.70,.78),(.085,.075,.008),(.88,.83,.66))
a=asset('wastebasket')
bx(a,'basket',(.24,.23,.30),(-2.47,2.65,.15),(.31,.19,.10))

# Three panel screen: gold fields and blue decorative silhouettes.
a=asset('painted_folding_screen')
for i,(x,y,ang) in enumerate([(-.12,2.52,-7),(.47,2.55,6),(1.05,2.50,-5)]):
    p=Asset('panel_'+str(i))
    bx(p,'gold_field',(.61,.065,1.68),(x,y,1.28),(.50,.37,.16))
    for xx in [x-.30,x+.30]:
        bx(p,'edge_'+str(xx),(.025,.085,1.72),(xx,y-.012,1.28),(.12,.095,.04))
    # Broad asymmetrical blue painted foliage and curved figure masses.
    for j in range(4):
        z=.66+j*.35
        ex=x+random.uniform(-.16,.16)
        ell(p,'blue_motif_'+str(j),(ex,y-.049,z),(.26,.012,.18),(.025,.075,.49))
    ell(p,'figure_head',(x+.12,y-.070,1.59),(.065,.009,.09),(.57,.37,.15))
    rd(p,'figure_body',(x+.12,y-.072,1.51),(x-.04,y-.072,1.08),.046,(.64,.35,.12))
    rd(p,'figure_arm',(x+.04,y-.075,1.37),(x-.19,y-.075,1.45),.022,(.71,.46,.20))
    for j in range(3):
        ell(p,'gold_leaf_'+str(j),(x-.16+j*.13,y-.075,.95+j*.10),(.07,.009,.035),(.71,.50,.20))
    p.turn('z',ang)
    a.include('panel_'+str(i),p)

# Bed runs from its tall head at right wall toward the center foreground.
a=asset('dark_sleigh_bed')
bedx,bedy=1.66,.36
bx(a,'base',(2.69,1.81,.34),(bedx,bedy,.35),C['wood'])
bx(a,'front_rail',(2.74,.105,.28),(bedx,bedy-.89,.41),(.095,.045,.028))
for x in [.33,2.98]:
    for y in [bedy-.81,bedy+.81]:
        bx(a,'foot_'+str((x,y)),(.13,.14,.29),(x,y,.145),C['wood'])
# Headboard broad dark panel with rounded crest.
bx(a,'headboard',(.13,1.91,.87),(3.00,bedy,.99),C['wood'])
rd(a,'head_crest',(2.98,bedy-.98,1.44),(2.98,bedy+.98,1.44),.065,C['wood'])
for y in [bedy-.98,bedy+.98]:
    rd(a,'head_post'+str(y),(2.97,y,.25),(2.97,y,1.49),.055,C['wood'])
# Low footboard obscures side of mattress.
bx(a,'footboard',(.13,1.87,.64),(.32,bedy,.70),C['wood'])
rd(a,'foot_crest',(.31,bedy-.94,1.04),(.31,bedy+.94,1.04),.065,C['wood'])
for y in [bedy-.94,bedy+.94]:
    ell(a,'foot_finial'+str(y),(.31,y,1.09),(.08,.08,.10),C['wood'])
ell(a,'mattress',(1.68,bedy,.67),(1.28,.85,.20),(.73,.73,.64))
ell(a,'cream_duvet',(1.48,bedy-.02,.82),(1.15,.84,.17),(.78,.78,.68))
# Broad overlapping folds, subdued and irregular.
for i in range(6):
    x=.73+i*.28
    fold=ell(a,'cover_fold_'+str(i),(x,bedy-.28+random.uniform(-.16,.16),.94),(.25,.57,.032),(.76+i*.004,.76+i*.004,.66))
    fold.turn('z',random.uniform(-15,15))
for j,y in enumerate([bedy+.43,bedy-.40]):
    p=ell(a,'pillow_'+str(j),(2.53,y,1.08),(.43,.40,.16),(.86,.86,.77))
    p.turn('y',-24)
    p.turn('z',-5+j*10)

# Olive chair, broad padded back, curving arms and deep seat.
a=asset('olive_armchair')
cx,cy=-.62,.08
for x in [cx-.45,cx+.45]:
    for y in [cy-.40,cy+.40]:
        rd(a,'leg'+str((x,y)),(x,y,.04),(x,y,.38),.042,C['wood'])
ell(a,'seat',(cx,cy,.51),(.59,.54,.18),(.31,.31,.071))
back=ell(a,'tall_rounded_back',(cx,cy+.38,.98),(.57,.16,.64),C['olive'])
back.turn('x',-9)
for s in [-1,1]:
    ell(a,'side_'+str(s),(cx+s*.49,cy,.68),(.145,.54,.35),(.25,.26,.052))
    rd(a,'arm_roll_'+str(s),(cx+s*.49,cy-.43,.83),(cx+s*.49,cy+.35,1.02),.075,(.34,.34,.09))
# A few shallow upholstered channels and buttons.
for i in [-1,0,1]:
    ell(a,'back_channel_'+str(i),(cx+i*.21,cy+.205,1.04),(.075,.025,.35),(.34,.34,.083))
for i in [-1,1]:
    for z in [.91,1.18]:
        ell(a,'tuft'+str((i,z)),(cx+i*.20,cy+.17,z),(.023,.015,.023),(.20,.21,.039))
a.turn('z',-13)

a=asset('black_spindle_chair')
x,y=2.03,2.14
bx(a,'seat',(.49,.44,.055),(x,y,.49),(.06,.045,.025))
for xx in [x-.20,x+.20]:
    for yy in [y-.17,y+.17]:
        rd(a,'leg'+str((xx,yy)),(xx,yy,.02),(xx,yy,.50),.024,C['wood'])
for xx in [x-.22,x+.22]:
    rd(a,'backpost'+str(xx),(xx,y+.18,.45),(xx,y+.18,1.10),.025,(.035,.028,.02))
rd(a,'toprail',(x-.23,y+.18,1.10),(x+.23,y+.18,1.10),.032,C['wood'])
for i in range(4):
    xx=x-.15+i*.10
    rd(a,'spindle'+str(i),(xx,y+.18,.58),(xx,y+.18,1.07),.012,C['wood'])

a=asset('round_bedside_cabinet')
ell(a,'round_body',(3.00,-.97,.36),(.40,.40,.36),C['wood'])
ell(a,'top',(3.00,-.97,.72),(.43,.43,.045),(.10,.05,.03))
for z in [.19,.43]:
    # Arc-like horizontal seams visible on the near side.
    for i in range(6):
        t0=math.pi+i*math.pi/6;t1=math.pi+(i+1)*math.pi/6
        rd(a,'seam'+str((z,i)),(3+.398*math.cos(t0),-.97+.398*math.sin(t0),z),
           (3+.398*math.cos(t1),-.97+.398*math.sin(t1),z),.006,(.24,.16,.09))

def rug(name,cx,cy,w,h):
    a=asset(name)
    bx(a,'red_field',(w,h,.018),(cx,cy,.016),(.33,.12,.085))
    for inset,col,th in [(.045,(.65,.59,.41),.04),(.11,(.18,.25,.28),.045),(.19,(.67,.48,.27),.035)]:
        bx(a,'left_'+str(inset),(th,h-2*inset,.022),(cx-w/2+inset,cy,.03),col)
        bx(a,'right_'+str(inset),(th,h-2*inset,.022),(cx+w/2-inset,cy,.03),col)
        bx(a,'near_'+str(inset),(w-2*inset,th,.022),(cx,cy-h/2+inset,.03),col)
        bx(a,'far_'+str(inset),(w-2*inset,th,.022),(cx,cy+h/2-inset,.03),col)
    for j in range(7):
        xx=cx-w*.37+j*w*.123
        v=bx(a,'border_motif'+str(j),(.075,.075,.025),(xx,cy-h*.35,.035),(.72,.58,.36));v.turn('z',45)
    return a
rug('back_small_carpet',-.98,1.30,1.60,1.02)
rug('foreground_carpet',1.42,-1.56,2.38,1.02)

realize(scene)

# Shared wallpaper shading creates the small dense ochre, rust and green pattern.
for mat in bpy.data.materials:
    col=mat.diffuse_color
    if abs(col[0]-.43)<.015 and abs(col[1]-.29)<.015:
        mat.use_nodes=True
        nt=mat.node_tree; bs=nt.nodes.get('Principled BSDF')
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=62
        tex.inputs['Detail'].default_value=2.5
        tex.inputs['Roughness'].default_value=.8
        coord=nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(coord.outputs['Generated'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.25
        ramp.color_ramp.elements[0].color=(.13,.16,.12,1)
        ramp.color_ramp.elements[1].position=.77
        ramp.color_ramp.elements[1].color=(.53,.37,.19,1)
        e=ramp.color_ramp.elements.new(.46);e.color=(.29,.18,.11,1)
        e=ramp.color_ramp.elements.new(.59);e.color=(.46,.32,.18,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.92
    # Bright window glazing.
    if col[0]>.74 and col[1]>.88 and col[2]>.85:
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value=(.65,.83,.85,1)
            bs.inputs['Emission Strength'].default_value=1.5

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.58,.65,.70,1)
background.inputs['Strength'].default_value=.30

set_view((-4.25,-6.45,2.90),(.00,1.36,1.52),lens=39,sensor=36)
area_emitter((-1.8,2.92,2.25),power=550,size=2.1,target=(.3,-.5,.5),color=(.85,.94,1))
area_emitter((-3.2,1.0,3.1),power=160,size=3.0,target=(1,1,1),color=(1,.91,.77))
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.15
# The runtime manages resolution, rendering and saving.
