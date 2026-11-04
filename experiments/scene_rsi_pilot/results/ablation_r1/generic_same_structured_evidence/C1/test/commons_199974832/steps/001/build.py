from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(18)

# Estimated image anchors: rear shelf ends (0.18,0.34), (0.77,0.33);
# rear shelf levels y=.44,.57,.68; bench back edge y=.73.
# Camera looks slightly downward into a narrow workshop; side shelves crop at frame edges.
CAMERA = (0.05, -5.25, 2.60)
TARGET = (0.0, 1.65, 2.02)
LENS = 31
ROOM_WIDTH = 6.0
BACK_Y = 2.45
SHELF_HEIGHTS = [1.05, 1.64, 2.23, 2.88]
KEY_POWER = 1100
scene = Scene('Old woodworking tool room')
ivory=(.74,.76,.70)
wood=(.43,.24,.085)
edgewood=(.66,.40,.16)
darkwood=(.23,.115,.045)
iron=(.105,.12,.115)
steel=(.34,.36,.34)

def B(parent,key,size,pos,col):
    return parent.include(key,box(size=size,center=pos,color=col))
def R(parent,key,a,b,r,col):
    return parent.include(key,rod(radius=r,start=a,end=b,color=col))
def rounded(parent,key,size,pos,col,r=.015):
    return parent.include(key,fillet_box(size=size,radius=min(r,min(size)*.4),center=pos,color=col))
def group(name):
    return Asset(name)

architecture=group('Plaster room and window')
B(architecture,'back',(6.15,.14,4.8),(0,2.65,2.35),ivory)
B(architecture,'right',(.14,6.7,4.8),(3.08,-.55,2.35),(.70,.73,.68))
B(architecture,'left',(.14,6.7,4.8),(-3.08,-.55,2.35),(.76,.78,.73))
B(architecture,'floor',(6.1,7,.12),(0,-.5,-.08),(.29,.25,.18))
# Tall cool daylight opening on left, divided into glass panes.
B(architecture,'window_dark',(.035,2.0,2.95),(-2.995,.52,2.35),(.10,.19,.21))
for iy in range(3):
    for iz in range(3):
        B(architecture,f'glass_{iy}_{iz}',(.04,.58,.88),
          (-2.965,-.12+iy*.65,1.40+iz*.94),(.43,.66,.74))
for y in [-.47,.17,.82,1.47]:
    B(architecture,f'window_upright{y}',(.10,.055,2.98),(-2.91,y,2.34),(.66,.66,.57))
for z in [.88,1.85,2.8,3.83]:
    B(architecture,f'window_cross{z}',(.10,2.05,.065),(-2.91,.5,z),(.68,.68,.59))
scene.include('room',architecture)

shelves=group('Continuous timber shelves')
for i,z in enumerate(SHELF_HEIGHTS):
    B(shelves,f'back_shelf_{i}',(5.85,.50,.075),(0,2.29,z),edgewood)
    B(shelves,f'back_front_edge_{i}',(5.85,.045,.055),(0,2.025,z-.025),(.75,.49,.23))
    B(shelves,f'right_shelf_{i}',(.58,3.65,.085),(2.75,.58,z),edgewood)
    # Slender brackets beneath each shelf.
    for x in [-2.35,-.75,.8,2.3]:
        R(shelves,f'bracket_{i}_{x}',(x,2.57,z-.32),(x,2.1,z-.04),.019,iron)
for z in [1.75,2.90,3.81]:
    B(shelves,f'left_rack_{z}',(.38,2.15,.065),(-2.82,.52,z),edgewood)
scene.include('shelving',shelves)

def plane(name, pos, length=.48, width=.19, height=.16, yaw=0, metal=False):
    a=group(name)
    bodycol=random.choice([(.40,.22,.075),(.50,.29,.12),(.31,.16,.06),(.59,.35,.12)])
    rounded(a,'body',(length,width,height),(0,0,height/2),iron if metal else bodycol,.018)
    B(a,'sole',(length+.018,width+.008,.018),(0,0,.015),steel if metal else darkwood)
    # Angled iron, wedge and projecting wooden rear handle.
    blade=B(a,'sloping_iron',(.055,width*.73,height*.95),(length*.05,0,height*.95),steel)
    blade.turn('y',-29,pivot=(length*.05,0,height*.8))
    wedge=B(a,'wedge',(.095,width*.64,.075),(-length*.045,0,height*.83),darkwood)
    wedge.turn('y',-22)
    if length>.37:
        R(a,'rear_handle',(length*.30,0,height*.85),(length*.38,0,height*1.75),.029,darkwood)
        rounded(a,'grip',(.105,.065,.055),(length*.365,0,height*1.67),darkwood)
        R(a,'front_knob',(-length*.33,0,height),(-length*.33,0,height*1.33),.031,bodycol)
        a.include('knob_cap',ball(.039,center=(-length*.33,0,height*1.35),color=bodycol))
    a.turn('z',yaw,pivot=(0,0,0))
    a.move(pos)
    scene.include(name,a)

# Rear shelves hold densely packed bench planes, moulding planes and wooden stock.
for row,z in enumerate(SHELF_HEIGHTS[:-1]):
    x=-2.64
    j=0
    while x<2.7:
        length=random.uniform(.32,.62)
        plane(f'rear_plane_{row}_{j}',(x+length/2,2.22,z+.045),
              length,.17,random.uniform(.13,.22),random.uniform(-7,7),
              metal=(row==1 and j%3==0))
        x+=length+random.uniform(.02,.08)
        j+=1
# Top row: narrow upright moulding planes, irregular stepped silhouettes.
for i in range(43):
    x=-2.76+i*.127
    h=random.uniform(.19,.35)
    a=group(f'top_moulding_plane_{i}')
    c=random.choice([wood,darkwood,(.50,.32,.16),(.34,.22,.12)])
    ob=B(a,'wooden_stock',(.095,.25,h),(x,2.28,2.925+h/2),c)
    ob.turn('y',random.uniform(-10,12))
    R(a,'cutter',(x,2.22,2.96+h*.6),(x+.015,2.22,3.00+h),.009,steel)
    scene.include(f'moulding_{i}',a)

# Right-hand shelves recede along the side wall.
for row,z in enumerate(SHELF_HEIGHTS):
    for j in range(8):
        y=-1.05+j*.43
        if row==3 and j<3:
            continue
        plane(f'right_plane_{row}_{j}',(2.72,y,z+.046),
              random.uniform(.31,.48),.20,random.uniform(.17,.27),90,
              metal=(j%4==0 and row<3))
# Loose large timber planes at top right.
for j in range(5):
    a=group(f'right_high_block_{j}')
    y=.4+j*.39
    B(a,'block',(.30,.33,.42),(2.74,y,3.13),random.choice([wood,darkwood,edgewood]))
    B(a,'top_iron',(.035,.17,.21),(2.73,y,3.40),steel)
    scene.include(f'right_high_{j}',a)

# Wall-mounted framing squares: thick dark Ls and narrow metallic inset strips.
def wall_square(name, x,z,length,angle):
    a=group(name)
    B(a,'long_arm',(.075,.035,length),(0,0,length/2),iron)
    B(a,'short_arm',(length*.70,.035,.075),(length*.35,0,.038),iron)
    B(a,'bright_long',(.013,.012,length*.94),(.025,-.024,length*.5),(.47,.48,.43))
    B(a,'bright_short',(length*.64,.012,.013),(length*.35,-.024,.060),(.47,.48,.43))
    a.turn('y',angle,pivot=(0,0,0))
    a.move((x,2.535,z))
    scene.include(name,a)
wall_square('largest_diagonal_square',-1.88,3.75,1.50,44)
wall_square('middle_diagonal_square',-1.50,3.55,1.15,44)
wall_square('inner_diagonal_square',-1.13,3.40,.86,44)
wall_square('upright_square',-.02,3.75,.95,0)
wall_square('small_square',.29,3.75,.70,24)
# Hanging dividers and calipers, upper center.
for i,(x,z,h) in enumerate([(.75,3.47,.72),(.88,3.79,.94),(1.04,4.02,1.10),(.64,3.14,.30)]):
    a=group(f'wall_divider_{i}')
    R(a,'left_leg',(x,2.51,z+h),(x-.17,2.51,z),.016,darkwood)
    R(a,'right_leg',(x,2.51,z+h),(x+.17,2.51,z),.016,darkwood)
    a.include('hinge',ball(.036,center=(x,2.51,z+h),color=steel))
    R(a,'cross',(x-.10,2.505,z+.22),(x+.10,2.505,z+.22),.009,steel)
    scene.include(f'divider_{i}',a)
for j,(x,z) in enumerate([(1.57,3.88),(2.02,3.61)]):
    a=group(f'hanging_mallet_{j}')
    R(a,'shaft',(x,2.49,z-.35),(x,2.49,z+.32),.033,wood)
    rounded(a,'head',(.39,.12,.13),(x,2.49,z+.29),darkwood)
    scene.include(f'mallet_{j}',a)

# Wooden-handled chisels in left window racks.
for row,z in enumerate([1.79,2.94,3.85]):
    for j in range(9):
        y=-.41+j*.225
        h=random.uniform(.25,.43)
        a=group(f'left_rack_chisel_{row}_{j}')
        R(a,'blade',(-2.76,y,z-.24),(-2.76,y,z+.03),.013,steel)
        rounded(a,'handle',(.068,.075,h),(-2.76,y,z+h/2+.025),
                random.choice([wood,darkwood,(.55,.32,.15)]),.025)
        R(a,'ferrule',(-2.76,y,z+.015),(-2.76,y,z+.07),.027,steel)
        scene.include(f'chisel_rack_{row}_{j}',a)

# Workbench occupies the whole foreground and runs beyond the image.
bench=group('Heavy scarred workbench')
B(bench,'top',(5.1,2.08,.16),(-.18,-.83,.79),(.36,.27,.145))
B(bench,'front_apron',(5.1,.12,.31),(-.18,-1.81,.60),wood)
for x in [-2.25,1.95]:
    for y in [-1.55,-.02]:
        B(bench,f'leg{x}_{y}',(.17,.17,.76),(x,y,.35),darkwood)
# Parallel plank joints and pale scars.
for i in range(7):
    B(bench,f'plank_joint_{i}',(5.0,.009,.004),(-.18,-1.69+i*.285,.874),(.17,.12,.07))
for i in range(38):
    x=random.uniform(-2.5,2.0); y=random.uniform(-1.75,.1)
    scar=B(bench,f'scar_{i}',(random.uniform(.06,.32),.007,.003),(x,y,.878),(.55,.44,.26))
    scar.turn('z',random.uniform(-35,35))
scene.include('bench',bench)

# Large loose planes and timber on bench behind foreground hand tools.
for i,(x,y,l,ang) in enumerate([(-1.65,-.06,.83,4),(-.45,.03,.78,-6),
                               (.65,-.02,.92,4),(1.60,-.25,.70,-18),
                               (.35,-.58,.70,12)]):
    plane(f'bench_plane_{i}',(x,y,.88),l,.26,.21,ang,metal=(i==4))
# Oversize wood plane at right, with long box body.
plane('large_foreground_plane',(1.50,-1.02,.89),1.02,.34,.30,-23)

# Saws spread across the lower left of the bench.
for i in range(5):
    a=group(f'foreground_saw_{i}')
    x=-2.12+i*.24; y=-1.08+i*.045
    blade=B(a,'flat_blade',(.17,.94,.018),(x,y,.902+i*.009),(.38,.40,.37))
    blade.turn('z',-13+i*5)
    for k in range(11):
        B(a,f'tooth_{k}',(.028,.028,.02),(x-.095,y-.40+k*.075,.912+i*.009),steel)
    rounded(a,'wood_grip',(.14,.25,.065),(x,y+.54,.94+i*.009),(.38,.20,.07),.025)
    B(a,'handle_slot',(.055,.12,.009),(x,y+.54,.978+i*.009),(.13,.12,.08))
    scene.include(f'saw_{i}',a)

# Chisels, files, rulers and yellow folding rules across foreground.
for i in range(13):
    a=group(f'loose_handtool_{i}')
    x=random.uniform(-2.13,.15); y=random.uniform(-1.8,-.7)
    R(a,'steel_shaft',(0,-.22,0),(0,.23,0),.013,steel)
    rounded(a,'wood_handle',(.071,.22,.067),(0,.30,.014),
            random.choice([edgewood,wood,darkwood]),.023)
    R(a,'collar',(0,.19,.01),(0,.22,.01),.029,steel)
    a.turn('z',random.uniform(-75,75),pivot=(0,0,0))
    a.move((x,y,.96))
    scene.include(f'loose_tool_{i}',a)
for i in range(4):
    a=group(f'folding_rule_{i}')
    B(a,'rule',(.90,.038,.018),(0,0,0),(.78,.57,.21))
    for k in range(20):
        B(a,f'tick_{k}',(.003,.015,.002),(-.42+k*.044,.009,.011),(.18,.15,.08))
    a.turn('z',[-12,18,36,-27][i],pivot=(0,0,0))
    a.move((-.17+i*.33,-1.48+i*.12,.99+i*.023))
    scene.include(f'ruler_{i}',a)

# Central oil pot with a loop handle and curved spout.
pot=group('Dark oil can')
R(pot,'body',(-.84,-.35,.89),(-.84,-.35,1.21),.155,iron)
R(pot,'top',(-.84,-.35,1.205),(-.84,-.35,1.23),.166,steel)
R(pot,'cap',(-.84,-.35,1.23),(-.84,-.35,1.28),.060,iron)
pot.include('handle',sweep_tube(points=[(-.98,-.35,1.15),(-1.09,-.35,1.31),
                                      (-1.03,-.35,1.48),(-.89,-.35,1.45),
                                      (-.86,-.35,1.28)],radius=.014,color=steel))
pot.include('spout',sweep_tube(points=[(-.72,-.35,1.20),(-.63,-.35,1.35),
                                     (-.64,-.35,1.51)],radius=.021,color=iron))
scene.include('oil_can',pot)

bottle=group('Cloudy pale bottle')
R(bottle,'body',(-.23,-.40,.89),(-.23,-.40,1.25),.094,(.59,.59,.46))
R(bottle,'shoulder',(-.23,-.40,1.25),(-.23,-.40,1.30),.068,(.61,.62,.51))
R(bottle,'neck',(-.23,-.40,1.30),(-.23,-.40,1.39),.042,(.66,.66,.55))
R(bottle,'stopper',(-.23,-.40,1.39),(-.23,-.40,1.42),.045,(.53,.44,.30))
B(bottle,'label',(.13,.009,.16),(-.23,-.492,1.12),(.73,.71,.56))
scene.include('bottle',bottle)

# Shallow round metal trays full of curls and small fasteners.
for idx,(x,y,r) in enumerate([(.80,-1.27,.35),(.68,-.91,.27)]):
    a=group(f'round_parts_tray_{idx}')
    R(a,'bottom',(x,y,.89),(x,y,.92),r,steel)
    # Thin continuous rim built as a swept closed circle.
    pts=[(x+r*math.cos(k*math.tau/40),y+r*math.sin(k*math.tau/40),1.01) for k in range(41)]
    a.include('rim',sweep_tube(points=pts,radius=.018,color=(.47,.49,.46)))
    for k in range(25):
        px=x+random.uniform(-r*.68,r*.68)
        py=y+random.uniform(-r*.68,r*.68)
        R(a,f'nail_{k}',(px,py,.937),(px+random.uniform(-.075,.075),py+random.uniform(.025,.10),.969),.007,steel)
    for k in range(7):
        px=x+random.uniform(-r*.6,r*.6); py=y+random.uniform(-r*.6,r*.6)
        pts=[(px+.045*math.cos(t*.55),py+.045*math.sin(t*.55),.95+t*.001) for t in range(13)]
        a.include(f'curl_{k}',sweep_tube(points=pts,radius=.005,color=(.64,.64,.56)))
    scene.include(f'tray_{idx}',a)

# Crossed pale mallet handles in the lower right.
mallet=group('Foreground wooden mallet')
R(mallet,'handle',(1.13,-1.88,.94),(1.92,-.86,1.02),.034,(.72,.51,.25))
head=B(mallet,'head',(.49,.16,.15),(1.25,-1.70,1.03),(.65,.44,.19))
head.turn('z',-34)
R(mallet,'second_stick',(1.23,-.93,1.04),(2.03,-1.77,.95),.023,(.78,.59,.30))
scene.include('mallet',mallet)

# Little shelf tickets provide the visible pale interruptions along timber edges.
labels=group('Shelf labels')
for i in range(12):
    z=random.choice(SHELF_HEIGHTS[:-1])
    x=random.uniform(-2.6,2.6)
    B(labels,f'label_{i}',(.15,.008,.034),(x,1.996,z-.009),(.88,.85,.70))
    for k in range(3):
        B(labels,f'ink_{i}_{k}',(.025,.003,.004),(x-.042+k*.036,1.989,z-.006),(.24,.23,.19))
scene.include('labels',labels)

# API audit: all positive sizes; rounded radii bounded by 0.4*thinnest side;
# distinct rod ends and sweep vertices; unique repeated sibling keys.
realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.70,.77,.81,1)
sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.42

# Add restrained wood grain through shared finishes, without editing semantic mesh names.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    if bs is None:
        continue
    c=bs.inputs['Base Color'].default_value
    bs.inputs['Roughness'].default_value=.72
    if c[0]>c[1]*1.22 and c[1]>c[2]*1.2:
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=5
        tex.inputs['Detail'].default_value=2
        coord=nt.nodes.new('ShaderNodeTexCoord')
        mapping=nt.nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(3,38,9)
        nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(c[0]*.56,c[1]*.56,c[2]*.56,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(min(c[0]*1.20,1),min(c[1]*1.20,1),min(c[2]*1.20,1),1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.13
        bump.inputs['Distance'].default_value=.018
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
    elif max(c[:3])-min(c[:3])<.06 and c[0]<.55:
        bs.inputs['Metallic'].default_value=.65
        bs.inputs['Roughness'].default_value=.43

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
area_emitter((-2.6,-.7,3.4),power=KEY_POWER,size=3.0,target=(0,1.1,1.5),color=(.83,.93,1.0))
area_emitter((.1,-1.0,4.5),power=650,size=4,target=(0,1.3,1.4),color=(1,.91,.75))
area_emitter((2.1,1.4,4.4),power=350,size=2.5,target=(0,1,1.6))
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.25
