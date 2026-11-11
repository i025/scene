# Reference inventory and estimated normalized bounds:
# Central window (.23-.43, .08-.47), left window cropped at left; white trim,
# green blinds, bright lower panes. Wall corner approximately (.63,.02).
# Bed (.50-.98,.47-1.00): dark wood headboard at right, white pillows and
# bedding, footboard diagonally across the foreground. Olive chair
# (.28-.53,.51-1.00) overlaps its footboard. Gold and blue folding screen
# (.42-.61,.33-.63) stands behind the bed. Small draped table (.14-.26,
# .47-.64), dark cabinet at left, three wall pictures, and two partly occluded
# rugs. The bed's hidden supports and lower screen are uncertain.
#
# Review of the second render against the reference:
# Central window approximately (.22-.40,.19-.64), reference (.23-.43,.08-.47).
# Wall corner approximately (.71,.16), reference (.63,.02). Chair approximately
# (.27-.60,.57-1.00), reference (.28-.53,.51-1.00). Bed approximately
# (.50-1.00,.48-.97), but its headboard is at the back and its footboard
# crosses the right side; the reference headboard lies along the right wall,
# with the footboard extending diagonally from the screen toward the foreground.
# Screen top is around y=.46 instead of .33 and is largely hidden by the bed.
# The reference ceiling edge slopes gently downward to the right on the back
# wall and upward on the right wall; the render has a deeper ceiling band.
#
# Ranked changes: (1) lower camera target z from 1.58 to .90, predicting that
# window, screen, and ceiling edge move upward together; the small trial below
# checks that direction. Keep lens and position fixed to preserve the crop.
# (2) rotate and reposition the bed so the headboard is on the right and the
# footboard faces the left foreground; this changes local bed edges and opens
# the screen silhouette. (3) make the chair narrower and give it connected,
# tall upholstered sides, moving its right contour left while retaining its
# foreground overlap. (4) enlarge and raise the screen locally. (5) use a
# fine mottled wall shader, brighter lower window panes, and darker wood.
# Illumination and surface orientation also affect observed brightness.
#
# Approximate expanded primitive count: architecture/windows 25, pictures 10,
# door/screen 15, bed 13, chair 15, tables/chairs 22, rugs 8: about 108 meshes.
from sceneact import *
import bpy
from mathutils import Vector

scene = Scene('Historic bedroom')
room_w, room_d, room_h = 8.4, 8.0, 3.35
cam_pos = (-3.8, -8.0, 2.85)
old_target = (0.05, 0.35, 1.58)
cam_target = (0.05, 0.35, 0.90)
cam_lens = 47

wood = (.065, .025, .014)
wood_hi = (.13, .050, .024)
wall = (.27, .17, .12)
olive = (.24, .24, .045)
blue = (.012, .055, .52)

def block(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def oval(asset, name, center, size, color):
    n = ball(1, center=center, color=color)
    n.resize((size[0]/2, size[1]/2, size[2]/2), pivot=center)
    asset.include(name, n)

arch = Asset('architecture')
block(arch,'floor',(room_w,room_d,.12),(0,-.9,-.06),(.50,.48,.43))
block(arch,'back_wall',(room_w,.12,room_h),(0,2.65,room_h/2),wall)
block(arch,'right_wall',(.12,room_d,room_h),(3.4,-.9,room_h/2),wall)
block(arch,'ceiling',(room_w,room_d,.10),(0,-.9,3.40),(.84,.84,.80))
block(arch,'back_cornice',(room_w,.17,.13),(0,2.54,3.25),(.91,.91,.88))
block(arch,'right_cornice',(.17,room_d,.13),(3.30,-.9,3.25),(.91,.91,.88))
block(arch,'back_skirt',(room_w,.10,.13),(0,2.55,.08),(.77,.76,.70))
block(arch,'right_skirt',(.10,room_d,.13),(3.30,-.9,.08),(.77,.76,.70))
scene.include('architecture',arch)

def window(name,x,width):
    a=Asset(name)
    block(a,'casing',(width+.20,.08,2.35),(x,2.54,1.91),(.90,.91,.88))
    block(a,'dark_recess',(width,.045,2.16),(x,2.48,1.91),(.12,.22,.19))
    block(a,'lower_glass',(width-.09,.025,.70),(x,2.445,1.21),(.97,1.0,.98))
    block(a,'green_blind',(width-.09,.03,1.40),(x,2.43,2.00),(.12,.31,.25))
    block(a,'top_frame',(width+.1,.08,.075),(x,2.39,3.025),(.96,.96,.93))
    for side in (-1,1):
        block(a,'side_frame_'+str(side),(.075,.08,2.26),
              (x+side*width/2,2.39,1.91),(.96,.96,.93))
    block(a,'sill',(width+.22,.18,.09),(x,2.36,.78),(.94,.94,.90))
    scene.include(name,a)

window('left_window',-2.72,1.15)
window('center_window',-.72,1.25)

portrait=Asset('oval_portrait')
oval(portrait,'gold_frame',(-1.82,2.48,2.26),(.76,.085,.94),(.62,.42,.12))
oval(portrait,'dark_oval',(-1.82,2.425,2.26),(.58,.035,.75),(.035,.025,.020))
oval(portrait,'face',(-1.82,2.399,2.31),(.115,.020,.15),(.46,.28,.16))
oval(portrait,'clothing',(-1.82,2.397,2.13),(.24,.020,.17),(.10,.065,.045))
scene.include('oval_portrait',portrait)

def back_picture(name,x,z,w,h):
    a=Asset(name)
    block(a,'frame',(w,.07,h),(x,2.49,z),(.63,.52,.31))
    block(a,'mat',(w*.83,.025,h*.85),(x,2.44,z),(.89,.87,.79))
    block(a,'print',(w*.56,.018,h*.64),(x,2.418,z),(.48,.49,.45))
    scene.include(name,a)
back_picture('back_print',.53,2.52,.48,.62)

a=Asset('right_wall_print')
block(a,'frame',(.065,.43,.57),(3.32,1.72,2.52),(.66,.53,.30))
block(a,'mat',(.025,.34,.47),(3.28,1.72,2.52),(.91,.88,.78))
oval(a,'print',(3.26,1.72,2.52),(.02,.20,.31),(.49,.50,.46))
scene.include('right_wall_print',a)

door=Asset('door')
block(door,'casing',(.70,.07,2.12),(1.48,2.52,1.25),(.91,.91,.88))
block(door,'panel',(.58,.045,1.97),(1.48,2.46,1.25),(.79,.81,.78))
block(door,'inset',(.47,.025,1.75),(1.48,2.42,1.25),(.89,.90,.87))
scene.include('door',door)

screen=Asset('painted_folding_screen')
block(screen,'gold_panel',(1.02,.055,1.70),(.28,1.88,1.00),(.65,.43,.15))
block(screen,'blue_panel',(.65,.055,1.70),(1.11,1.88,1.00),blue)
block(screen,'top_rail',(1.72,.07,.045),(.61,1.84,1.86),wood)
block(screen,'bottom_rail',(1.72,.07,.045),(.61,1.84,.14),wood)
block(screen,'hinge',(.025,.08,1.68),(.79,1.84,1.00),wood)
for i,(x,z,sx,sz,c) in enumerate([
    (.12,1.40,.58,.30,blue),(.55,1.12,.57,.34,blue),
    (.24,.66,.58,.20,(.76,.63,.38)),(.64,.56,.43,.23,(.55,.30,.16)),
    (1.15,1.35,.26,.43,(.68,.44,.17)),(1.08,.82,.28,.36,(.66,.44,.22)),
    (.31,.90,.22,.15,(.81,.76,.57))]):
    oval(screen,'painted_form_%d'%i,(x,1.835,z),(sx,.025,sz),c)
scene.include('folding_screen',screen)

# Bed long axis runs along X, with the head against the right wall.
bed=Asset('bed')
bx,by=1.55,-.18
block(bed,'base',(3.30,2.08,.31),(bx,by,.39),wood)
block(bed,'mattress',(3.12,1.98,.33),(bx,by,.64),(.78,.78,.73))
block(bed,'coverlet',(2.22,1.95,.20),(1.16,by,.86),(.81,.81,.76))
block(bed,'headboard',(.15,2.19,.84),(3.20,by,.91),wood)
block(bed,'head_top',(.20,2.26,.10),(3.20,by,1.35),wood_hi)
block(bed,'footboard',(.15,2.19,.92),(-.10,by,.70),wood)
block(bed,'foot_top',(.21,2.26,.10),(-.10,by,1.18),wood_hi)
for x in (-.10,3.20):
    for y in (by-1.07,by+1.07):
        block(bed,'post_%s_%s'%(x,y),(.13,.12,1.14),(x,y,.58),wood)
for i,y in enumerate((by-.48,by+.48)):
    n=ball(1,center=(2.63,y,1.03),color=(.91,.91,.86))
    n.resize((.46,.50,.22),pivot=(2.63,y,1.03))
    n.turn(axis='+y',degrees=-12,pivot=(2.63,y,1.03))
    bed.include('pillow_%d'%i,n)
scene.include('bed',bed)

chair=Asset('olive_armchair')
cx,cy=-1.38,-1.91
for x in (cx-.43,cx+.43):
    for y in (cy-.42,cy+.40):
        block(chair,'leg_%s_%s'%(x,y),(.07,.07,.31),(x,y,.16),wood)
oval(chair,'lower_upholstery',(cx,cy,.48),(1.22,1.25,.60),olive)
oval(chair,'back',(cx,cy+.43,.99),(1.19,.48,1.40),olive)
oval(chair,'left_arm',(cx-.50,cy-.03,.80),(.32,1.16,.76),olive)
oval(chair,'right_arm',(cx+.50,cy-.03,.80),(.32,1.16,.76),olive)
oval(chair,'seat',(cx,cy-.12,.74),(.94,.88,.24),(.34,.33,.075))
for i,(dx,z) in enumerate([(-.27,1.13),(0,1.23),(.27,1.13),
                           (-.15,.98),(.15,.98)]):
    oval(chair,'tuft_%d'%i,(cx+dx,cy+.185,z),(.045,.025,.045),(.15,.15,.025))
scene.include('olive_armchair',chair)

table=Asset('draped_side_table')
tx,ty=-1.93,1.80
block(table,'top',(.82,.64,.09),(tx,ty,.75),wood)
for x in (tx-.32,tx+.32):
    for y in (ty-.23,ty+.23):
        block(table,'leg_%s_%s'%(x,y),(.065,.065,.72),(x,y,.36),wood)
block(table,'cloth_top',(.89,.70,.035),(tx,ty,.81),(.91,.90,.84))
cloth=box((.57,.035,.43),center=(tx,ty-.355,.63),color=(.88,.87,.81))
cloth.turn(axis='+y',degrees=45,pivot=(tx,ty-.355,.63))
table.include('hanging_cloth',cloth)
for i,(x,y) in enumerate([(-2.14,1.77),(-1.94,1.84),(-1.72,1.76)]):
    oval(table,'ornament_%d'%i,(x,y,.85),(.12,.10,.08),(.72,.70,.58))
scene.include('side_table',table)

cab=Asset('left_cabinet')
block(cab,'body',(1.08,.47,.67),(-3.0,2.02,.43),wood)
block(cab,'top',(1.18,.56,.09),(-3.0,2.02,.79),wood_hi)
for x in (-3.4,-2.6):
    block(cab,'leg_'+str(x),(.10,.10,.23),(x,1.87,.12),wood)
scene.include('left_cabinet',cab)

small=Asset('small_wooden_chair')
block(small,'seat',(.47,.42,.07),(2.38,1.93,.54),wood)
for x in (2.19,2.57):
    for y in (1.77,2.10):
        block(small,'leg_%s_%s'%(x,y),(.045,.045,.53),(x,y,.27),wood)
for x in (2.19,2.57):
    block(small,'back_post_'+str(x),(.05,.05,.88),(x,2.10,.88),wood)
block(small,'back_rail',(.43,.05,.08),(2.38,2.10,1.29),wood)
scene.include('small_wooden_chair',small)

def rug(name,x,y,w,d):
    a=Asset(name)
    block(a,'outer',(w,d,.018),(x,y,.012),(.35,.15,.12))
    block(a,'blue_border',(w-.08,d-.08,.020),(x,y,.024),(.11,.18,.28))
    block(a,'cream_border',(w-.18,d-.18,.021),(x,y,.037),(.70,.58,.43))
    block(a,'field',(w-.29,d-.29,.022),(x,y,.049),(.46,.22,.17))
    scene.include(name,a)
rug('small_rug',-1.60,-.40,1.60,1.05)
rug('foreground_rug',1.45,-2.80,2.8,1.00)

realize(scene)

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
background.inputs['Color'].default_value=(.70,.72,.72,1)
background.inputs['Strength'].default_value=.28

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    c=bs.inputs['Base Color'].default_value
    if abs(c[0]-wall[0])<.01 and abs(c[1]-wall[1])<.01 and abs(c[2]-wall[2])<.01:
        tex=mat.node_tree.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=155
        tex.inputs['Detail'].default_value=2
        ramp=mat.node_tree.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.25
        ramp.color_ramp.elements[0].color=(.035,.042,.043,1)
        ramp.color_ramp.elements[1].position=.75
        ramp.color_ramp.elements[1].color=(.42,.24,.14,1)
        mat.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac'])
        mat.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])

sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100

# Reference estimates and calculated geometry-point projections remain separate.
landmarks=[
    ('window upper left',(-1.345,2.39,3.025),(.23,.08)),
    ('screen upper right',(1.44,1.84,1.86),(.61,.33)),
    ('bed foot upper near',(-.10,-1.25,1.18),(.50,.61)),
    ('chair left arm',(-2.04,-1.94,.80),(.28,.67)),
]
def project_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    projection=cam.calc_matrix_camera(
        dg,x=512,y=341,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip=projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print(name,'reference',ref,'projected',uv)

set_view(cam_pos,old_target,lens=cam_lens)
project_table('Previous camera')
set_view(cam_pos,(old_target[0],old_target[1],old_target[2]-.10),lens=cam_lens)
project_table('Trial: lower aim by 0.10')
set_view(cam_pos,cam_target,lens=cam_lens)
project_table('Selected camera')

area_emitter((-2.0,1.4,2.8),power=500,size=2.4,target=(0,-.5,.5))
area_emitter((-3,-4,4.5),power=350,size=5,target=(0,0,1))
