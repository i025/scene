# Reference inventory and visual anchors (normalized image coordinates; estimates):
# Back wall and two windows: left window partly cropped at x=0-.13, y=.07-.52;
# central window x=.23-.43, y=.08-.48. Dark patterned walls meet at x=.63 near top.
# Bed: x=.50-.98, y=.46-.99; dark wooden headboard, white pillows and bedding;
# footboard crosses in front of the bedding. Its long edges run down-right in image.
# Olive upholstered chair: x=.28-.53, y=.50-.99, overlapping bed foot and rug.
# Folding screen: x=.42-.61, y=.33-.63, blue and gold, behind the bed.
# Small table with white cloth: x=.14-.26, y=.47-.64. Dark cabinet at far left.
# Framed portraits on the back wall at x=.13-.25 and x=.47-.54, and on right wall
# x=.66-.70. Floor is light beige; patterned rugs appear below chair and bed.
# White ceiling cornice and skirting; the room continues outside the image.
# Occluded bed legs, screen support, and wall areas are uncertain.
# Primitive estimate: architecture/windows ~30, bed ~19, chair ~14, screen ~15,
# tables and objects ~20, pictures ~14, rugs ~8, total roughly 120 meshes.
from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene('Historic bedroom')

# Major dimensions and camera are independent, so the scene remains readily editable.
room_w, room_d, room_h = 6.8, 6.3, 3.35
cam_pos = (-4.7, -7.7, 3.0)
cam_target = (0.05, 0.15, 1.30)
cam_lens = 34

wood = (0.105, 0.045, 0.026)
wood_hi = (0.17, 0.075, 0.04)
cream = (0.77, 0.75, 0.68)
white = (0.89, 0.88, 0.82)
olive = (0.30, 0.29, 0.065)
gold = (0.63, 0.42, 0.12)
blue = (0.025, 0.105, 0.57)
wall = (0.30, 0.19, 0.14)

def add(asset, name, node):
    asset.include(name, node)

def block(asset, name, size, center, color):
    add(asset, name, box(size=size, center=center, color=color))

def ellipsoid(asset, name, center, size, color):
    node = ball(1, center=center, color=color)
    node.resize((size[0]/2, size[1]/2, size[2]/2), pivot=center)
    add(asset, name, node)

# Room shell, with window openings represented by shallow white framed recesses.
arch = Asset('architecture')
block(arch, 'floor', (room_w, room_d, .12), (0, -.5, -.06), (0.49, .46, .40))
block(arch, 'back_wall', (room_w, .12, room_h), (0, 2.65, room_h/2), wall)
block(arch, 'right_wall', (.12, room_d, room_h), (3.4, -.5, room_h/2), wall)
block(arch, 'ceiling', (room_w, room_d, .10), (0, -.5, room_h+.05), (.83,.83,.79))
block(arch, 'back_cornice', (room_w, .16, .13), (0, 2.54, 3.25), (.86,.86,.82))
block(arch, 'right_cornice', (.16, room_d, .13), (3.30, -.5, 3.25), (.86,.86,.82))
block(arch, 'back_skirt', (room_w, .10, .14), (0, 2.55, .08), (.77,.76,.70))
block(arch, 'right_skirt', (.10, room_d, .14), (3.30, -.5, .08), (.77,.76,.70))
scene.include('architecture', arch)

def window(name, x, width):
    a = Asset(name)
    # Placed in front of the wall: white casing, bright glass and dark green shade.
    block(a, 'outer_casing', (width+.19,.08,2.35), (x,2.54,1.91), (.88,.89,.85))
    block(a, 'inner_recess', (width,.045,2.16), (x,2.48,1.91), (.30,.37,.32))
    block(a, 'lower_glass', (width-.09,.025,.70), (x,2.445,1.21), (.76,.91,.87))
    block(a, 'green_blind', (width-.09,.03,1.40), (x,2.43,2.00), (.16,.36,.29))
    block(a, 'top_frame', (width+.1,.08,.075), (x,2.39,3.025), (.94,.94,.9))
    block(a, 'left_frame', (.075,.08,2.26), (x-width/2,2.39,1.91), (.94,.94,.9))
    block(a, 'right_frame', (.075,.08,2.26), (x+width/2,2.39,1.91), (.94,.94,.9))
    block(a, 'sill', (width+.22,.18,.09), (x,2.36,.78), (.91,.91,.86))
    scene.include(name, a)
window('left_window', -2.72, 1.15)
window('center_window', -.72, 1.25)

# Framed pictures hung on back and right walls.
def back_picture(name, x, z, w, h, frame, inside):
    a=Asset(name)
    block(a,'frame',(w,.075,h),(x,2.49,z),frame)
    block(a,'mat',(w*.80,.025,h*.83),(x,2.438,z),(.86,.82,.70))
    block(a,'image',(w*.62,.018,h*.68),(x,2.418,z),inside)
    scene.include(name,a)
back_picture('oval_portrait',-1.82,2.26,.72,.88,(.64,.46,.19),(.08,.055,.04))
back_picture('small_back_print',.53,2.52,.48,.62,(.63,.52,.32),(.56,.57,.53))
right_pic=Asset('right_wall_print')
block(right_pic,'frame',(.065,.43,.57),(3.32,1.72,2.52),(.67,.55,.35))
block(right_pic,'mat',(.025,.34,.47),(3.28,1.72,2.52),(.88,.85,.73))
block(right_pic,'image',(.02,.20,.31),(3.26,1.72,2.52),(.52,.53,.49))
scene.include('right_wall_print',right_pic)

# Far right white door, visible behind the painted screen.
door=Asset('door')
block(door,'casing',(.70,.07,2.12),(1.48,2.52,1.25),(.88,.89,.85))
block(door,'panel',(.58,.045,1.97),(1.48,2.46,1.25),(.72,.75,.72))
block(door,'panel_inset',(.47,.025,1.75),(1.48,2.42,1.25),(.84,.85,.82))
scene.include('door',door)

# Painted folding screen, immediately in front of the door.
screen=Asset('folding_screen')
block(screen,'left_panel',(1.02,.055,1.45),(.28,1.88,.84),(.67,.45,.17))
block(screen,'right_panel',(.65,.055,1.45),(1.11,1.88,.84),blue)
block(screen,'top_rail',(1.72,.07,.045),(.61,1.84,1.57),wood)
block(screen,'bottom_rail',(1.72,.07,.045),(.61,1.84,.12),wood)
block(screen,'hinge',(.025,.08,1.43),(.79,1.84,.84),wood)
# Large simplified landscape shapes retain the visible gold/blue distribution.
for i,(x,z,sx,sz,c) in enumerate([
    (.12,1.17,.58,.30,blue),(.55,.91,.57,.34,blue),
    (.24,.54,.58,.20,(.76,.63,.38)),(.64,.47,.43,.23,(.55,.30,.16)),
    (1.15,1.14,.26,.43,(.68,.44,.17)),(1.08,.66,.28,.36,(.66,.44,.22)),
    (.31,.73,.22,.15,(.81,.76,.57))]):
    ellipsoid(screen,'painted_form_%d'%i,(x,1.835,z),(sx,.025,sz),c)
scene.include('folding_screen',screen)

# Bed: length along Y, head toward back wall.
bed=Asset('bed')
bx, by = 1.70, -.05
block(bed,'base',(2.12,3.25,.32),(bx,by,.40),wood)
block(bed,'mattress',(2.02,3.05,.34),(bx,by,.67),(.78,.77,.70))
block(bed,'coverlet',(1.99,2.20,.19),(bx,by-.40,.89),(.79,.79,.73))
# Headboard and footboard are dark, with a broad raised top rail.
block(bed,'headboard',(2.18,.14,.82),(bx,1.57,.91),wood)
block(bed,'head_top',(2.26,.20,.10),(bx,1.57,1.34),wood_hi)
block(bed,'footboard',(2.18,.15,.93),(bx,-1.68,.69),wood)
block(bed,'foot_top',(2.27,.21,.10),(bx,-1.68,1.18),wood_hi)
for x in (bx-1.08,bx+1.08):
    for y in (-1.68,1.57):
        block(bed,'post_%s_%s'%(x,y),(.12,.13,1.19),(x,y,.61),wood)
for i,x in enumerate((1.17,2.23)):
    p=ball(1,center=(x,1.05,1.04),color=(.88,.88,.83))
    p.resize((.52,.43,.20),pivot=(x,1.05,1.04))
    p.turn(axis='+x',degrees=12,pivot=(x,1.05,1.04))
    add(bed,'pillow_%d'%i,p)
scene.include('bed',bed)

# Armchair in foreground left of bed, with rounded back and wide arms.
chair=Asset('olive_armchair')
cx,cy=-.75,-1.56
for x in (cx-.53,cx+.53):
    for y in (cy-.46,cy+.44):
        block(chair,'leg_%s_%s'%(x,y),(.075,.075,.38),(x,y,.19),wood)
ellipsoid(chair,'seat_base',(cx,cy,.52),(1.45,1.24,.48),olive)
ellipsoid(chair,'seat_cushion',(cx,cy-.05,.76),(1.18,.91,.25),(.38,.37,.095))
ellipsoid(chair,'rounded_back',(cx,cy+.48,1.05),(1.36,.38,1.30),olive)
ellipsoid(chair,'left_arm',(cx-.64,cy-.02,.87),(.32,1.15,.55),olive)
ellipsoid(chair,'right_arm',(cx+.64,cy-.02,.87),(.32,1.15,.55),olive)
# Sparse dark tuft marks on the chair back.
for i,(x,z) in enumerate([(-1.05,1.10),(-.75,1.22),(-.46,1.10),(-.90,.93),(-.60,.94)]):
    ellipsoid(chair,'tuft_%d'%i,(x,cy+.273,z),(.055,.025,.055),(.18,.18,.045))
scene.include('olive_armchair',chair)

# Small table and objects beneath the portrait.
table=Asset('side_table')
tx,ty=-1.93,1.80
block(table,'top',(.82,.64,.09),(tx,ty,.75),wood)
for x in (tx-.32,tx+.32):
    for y in (ty-.23,ty+.23):
        block(table,'leg_%s_%s'%(x,y),(.065,.065,.72),(x,y,.36),wood)
block(table,'white_cloth',(.89,.70,.035),(tx,ty,.81),(.88,.87,.80))
# Front cloth hangs as an angled diamond-like flap.
cloth=box((.57,.035,.43),center=(tx,ty-.355,.63),color=(.85,.84,.77))
cloth.turn(axis='+y',degrees=45,pivot=(tx,ty-.355,.63))
add(table,'hanging_cloth',cloth)
for i,(x,y) in enumerate([(-2.14,1.77),(-1.94,1.84),(-1.72,1.76)]):
    ellipsoid(table,'small_ornament_%d'%i,(x,y,.85),(.12,.10,.08),(.70,.68,.56))
scene.include('side_table',table)

cabinet=Asset('left_cabinet')
block(cabinet,'body',(1.08,.47,.67),(-3.0,2.02,.43),wood)
block(cabinet,'top',(1.18,.56,.09),(-3.0,2.02,.79),wood_hi)
for x in (-3.4,-2.6):
    block(cabinet,'leg_%s'%x,(.10,.10,.23),(x,1.87,.12),wood)
scene.include('left_cabinet',cabinet)

# Flat woven rugs: broad red/blue borders and a light center.
def rug(name,x,y,w,d):
    a=Asset(name)
    block(a,'outer',(w,d,.018),(x,y,.012),(.37,.17,.13))
    block(a,'blue_border',(w-.08,d-.08,.020),(x,y,.024),(.14,.21,.31))
    block(a,'cream_border',(w-.18,d-.18,.021),(x,y,.037),(.70,.59,.43))
    block(a,'field',(w-.29,d-.29,.022),(x,y,.049),(.48,.24,.19))
    scene.include(name,a)
rug('small_rug',-1.60,-.40,1.60,1.05)
rug('foreground_rug',1.45,-2.60,2.8,1.00)

realize(scene)

# A restrained procedural wallpaper texture supplies the small-scale mottled pattern.
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and ('back_wall' in obj.name or 'right_wall' in obj.name):
        mat=bpy.data.materials.new('Mottled antique wallpaper')
        mat.diffuse_color=(.29,.19,.14,1)
        mat.use_nodes=True
        nodes=mat.node_tree.nodes
        bs=nodes.get('Principled BSDF')
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=115
        tex.inputs['Detail'].default_value=2
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.26
        ramp.color_ramp.elements[0].color=(.075,.085,.09,1)
        ramp.color_ramp.elements[1].position=.73
        ramp.color_ramp.elements[1].color=(.48,.29,.18,1)
        mat.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac'])
        mat.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        obj.data.materials.clear()
        obj.data.materials.append(mat)

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
background.inputs['Color'].default_value=(.75,.78,.79,1)
background.inputs['Strength'].default_value=.35

sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
set_view(cam_pos,cam_target,lens=cam_lens)
area_emitter((-2.0,1.4,2.8),power=500,size=2.4,target=(0,-.5,.5))
area_emitter((-3,-4,4.5),power=450,size=5,target=(0,0,1))

# Projection check: measured reference estimates are separate from world coordinates.
# The printed values are diagnostic only, not proof of visibility or silhouette.
landmarks=[
    ('window upper left',(-1.345,2.39,3.025),(.23,.08)),
    ('screen upper right',(1.44,1.84,1.57),(.61,.33)),
    ('bed foot upper left',(.62,-1.68,1.18),(.50,.61)),
    ('chair left arm',(-1.55,-1.58,.90),(.28,.67)),
]
bpy.context.view_layer.update()
cam=sc.camera
dg=bpy.context.evaluated_depsgraph_get()
proj=cam.calc_matrix_camera(dg,x=512,y=341,scale_x=sc.render.pixel_aspect_x,
                            scale_y=sc.render.pixel_aspect_y)
print('Landmark: reference -> projected')
for name,p,ref in landmarks:
    clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv=None if clip.w<=1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
    print(name,ref,uv)
