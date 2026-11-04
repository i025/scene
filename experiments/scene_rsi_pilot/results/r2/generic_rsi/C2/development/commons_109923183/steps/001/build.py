from sceneact import *
import bpy, math, random
from mathutils import Vector

# VISUAL LEDGER (normalized image bounds, approximate):
# Chaise .03,.24–.84,.94: raised left back, filled side wings, long upholstered
# seat, scalloped apron and four curved legs. Pillow overlaps the back and seat.
# Pillow .07,.26–.33,.51; green museum card .68,.53–.71,.59.
# Paneled ivory wall .04,0–1,.55, with plinth and nested molding rectangles.
# Curtain/window sliver 0,0–.08,.78, behind chaise; parquet fills lower image.
# Cropped cane chair 0,.80–.19,1, in front of the chaise.
# Anchors: back crest (.09,.25), pillow apex (.22,.26), seat head (.29,.49),
# foot tip (.82,.64), front foot (.77,.92), wall panel corner (.85,.40),
# foreground chair corner (.16,.82), wall/floor boundary (.91,.50).
# Perspective: wall rails nearly horizontal, receding slightly upward right;
# floor visible substantially from above. Camera is above the front long side.
# Hierarchy audit: every independently movable object has its own Asset.
# Broad upholstery and wing surfaces are filled; trims accompany their panels.

P = {
    'camera': (2.45, -5.6, 3.65), 'target': (0.0, .12, .91), 'lens': 47,
    'wood': (.34,.40,.32), 'edge': (.63,.60,.44),
    'cloth': (.79,.73,.62), 'wall': (.75,.72,.63),
    'pillow': (.83,.76,.61), 'floor': (.22,.105,.052)
}
scene = Scene('French chaise room')
random.seed(19)

def add(parent, name, node):
    return parent.include(name, node)

def tube(parent, name, points, radius, color):
    return add(parent, name, sweep_tube(points=points, radius=radius, color=color))

def ellipsoid(size, center, color):
    return ball(1, center=center, color=color).resize(size, pivot=center)

def beam(parent, name, a, b, width, depth, color):
    a,b = Vector(a),Vector(b)
    mid=(a+b)/2
    n=box((width,depth,(b-a).length), center=tuple(mid),color=color)
    axis=Vector((0,0,1)).cross(b-a)
    angle=Vector((0,0,1)).angle(b-a)
    if axis.length > .00001:
        n.turn(tuple(axis),math.degrees(angle),pivot=tuple(mid))
    return add(parent,name,n)

# Architecture and individually colored parquet boards.
floor = Asset('parquet_floor')
add(floor,'foundation',box((12,10,.12),center=(0,0,-.08),color=P['floor']))
for i in range(-12,13):
    for j in range(-8,9):
        # Alternating blocks of narrow boards, with only hairline joints.
        cx=i*.48; cy=j*.48
        vertical=(i+j)%2
        for k in range(3):
            color=(.23+random.uniform(-.035,.035),
                   .115+random.uniform(-.018,.018),
                   .062+random.uniform(-.01,.01))
            if vertical:
                sz=(.157,.477,.018); pos=(cx+(k-1)*.16,cy,-.009)
            else:
                sz=(.477,.157,.018); pos=(cx,cy+(k-1)*.16,-.009)
            add(floor,f'board_{i}_{j}_{k}',box(sz,center=pos,color=color))
scene.include('parquet_floor',floor)

wall=Asset('paneled_wall')
add(wall,'wall_body',box((9,.16,3.8),center=(0,1.02,1.9),color=P['wall']))
for z,d,h in [(.10,.10,.18),(.235,.065,.045),(.31,.045,.035),
              (1.91,.065,.055),(2.01,.07,.045),(2.26,.045,.035)]:
    add(wall,f'horizontal_{z}',box((9,d,h),center=(0,.907-d/2,z),
                                 color=(.80,.77,.68)))
# A large panel behind the chaise, with double beveled-looking borders.
for inset,w in [(0,.022),(.045,.011)]:
    x0,x1=-1.75+inset,1.92-inset
    z0,z1=.43+inset,1.79-inset
    for name,c,s in [
        ('bottom',((x0+x1)/2,.902,z0),(x1-x0,.037,w)),
        ('top',((x0+x1)/2,.902,z1),(x1-x0,.037,w)),
        ('left',(x0,.902,(z0+z1)/2),(w,.037,z1-z0)),
        ('right',(x1,.902,(z0+z1)/2),(w,.037,z1-z0))]:
        add(wall,f'panel_{inset}_{name}',box(s,center=c,color=(.82,.79,.70)))
for x in [-1.25,.55]:
    add(wall,f'vertical_joint_{x}',box((.006,.005,3.3),center=(x,.934,1.66),
                                    color=(.44,.42,.36)))
scene.include('paneled_wall',wall)

pier=Asset('right_wall_return')
add(pier,'body',box((.43,.62,3.5),center=(2.36,.84,1.75),color=(.79,.78,.70)))
add(pier,'base',box((.47,.69,.20),center=(2.36,.80,.10),color=(.83,.81,.73)))
for x in [2.19,2.50]:
    add(pier,f'molding_{x}',box((.018,.025,2.55),center=(x,.516,1.70),
                              color=(.86,.84,.76)))
scene.include('right_wall_return',pier)

curtain=Asset('window_and_curtains')
add(curtain,'bright_window',box((.6,.05,3.4),center=(-2.25,.48,1.7),
                              color=(.96,.95,.87)))
for k in range(10):
    x=-2.03+k*.041
    col=(.70,.64,.51) if k%3==0 else (.85,.81,.70)
    add(curtain,f'fold_{k}',rod(.045,start=(x,.43,.03),
                              end=(x-.20,.53,3.5),color=col))
scene.include('window_and_curtains',curtain)

chaise=Asset('chaise_longue')
# Main mattress, its piping, and a wood seat frame.
add(chaise,'seat_cushion',fillet_box((2.43,1.0,.24),radius=.115,
    center=(.12,0,.755),color=P['cloth']))
add(chaise,'seat_foundation',fillet_box((2.40,1.015,.12),radius=.055,
    center=(.10,0,.605),color=P['wood']))
for y in [-.503,.503]:
    pts=[(-1.03,y,.70),(-.75,y,.683),(.20,y,.68),(1.12,y,.68),(1.27,y,.72)]
    tube(chaise,f'seat_welting_{y}',pts,.012,(.64,.59,.46))

# Shaped broad apron is made from overlapping solid segments, with attached edging.
for y in [-.515,.515]:
    apron=Part(f'apron_{y}')
    xs=[-1.01,-.80,-.47,-.13,.20,.53,.86,1.12,1.25]
    lower=[.49,.47,.485,.46,.43,.46,.48,.46,.48]
    for i in range(len(xs)-1):
        mid=(xs[i]+xs[i+1])/2
        bottom=(lower[i]+lower[i+1])/2
        add(apron,f'filled_rail_{i}',box((xs[i+1]-xs[i]+.015,.055,.61-bottom),
                                      center=(mid,y,(.61+bottom)/2),color=P['wood']))
    tube(apron,'upper_gilt_line',[(x,y-.032 if y<0 else y+.032,.603) for x in xs],
         .009,P['edge'])
    tube(apron,'lower_gilt_line',[(x,y-.033 if y<0 else y+.033,z) for x,z in zip(xs,lower)],
         .012,P['edge'])
    add(chaise,f'apron_{y}',apron)

# Cabriole legs: continuous curved silhouettes and modest carved collars.
for ix,x in enumerate([-.92,1.10]):
    for iy,y in enumerate([-.43,.43]):
        out=-1 if x<0 else 1
        pts=[(x,y,.56),(x+out*.065,y,.44),(x+out*.025,y,.30),
             (x-out*.035,y,.13),(x-out*.012,y,.055)]
        tube(chaise,f'cabriole_{ix}_{iy}',pts,.034,P['wood'])
        tube(chaise,f'leg_edge_{ix}_{iy}',[(a,b-.024,c) for a,b,c in pts],.007,P['edge'])
        add(chaise,f'foot_{ix}_{iy}',ellipsoid((.050,.041,.027),
                                            (pts[-1][0],y,.045),P['wood']))

# High left back: gently curved filled upholstery, rising toward the far corner.
back=Part('upholstered_head')
for k in range(10):
    y=-.45+k*.10
    crest=1.48+.10*math.sin((k/9)*math.pi)
    x=-1.035-.13*math.sin((k/9)*math.pi)
    panel=box((.13,.112,crest-.75),center=(x,y,(crest+.75)/2),color=P['cloth'])
    panel.turn('y',-12,pivot=(x,y,.75))
    add(back,f'filled_back_{k}',panel)
top=[(-1.08-.13*math.sin(k/12*math.pi),-.5+k/12,
      1.49+.10*math.sin(k/12*math.pi)) for k in range(13)]
tube(back,'crest_wood',top,.037,P['wood'])
tube(back,'crest_highlight',[(x+.006,y-.018,z+.017) for x,y,z in top],.010,P['edge'])
add(chaise,'head_back',back)

# Filled curved side wings; the front wing is strongly visible in the photograph.
for side in [-1,1]:
    wing=Part(f'wing_{side}')
    xs=[-1.03,-.92,-.78,-.62,-.47]
    tops=[1.46,1.26,1.16,1.12,1.15]
    bottoms=[.70,.68,.65,.64,.67]
    for k in range(4):
        x=(xs[k]+xs[k+1])/2
        top=(tops[k]+tops[k+1])/2
        bot=(bottoms[k]+bottoms[k+1])/2
        add(wing,f'filled_side_{k}',box((xs[k+1]-xs[k]+.025,.075,top-bot),
                        center=(x,side*.48,(top+bot)/2),color=P['cloth']))
    tube(wing,'arm_rail',[(x,side*.49,z) for x,z in zip(xs,tops)],.031,P['wood'])
    tube(wing,'arm_gilt',[(x,side*.515,z+.011) for x,z in zip(xs,tops)],.009,P['edge'])
    tube(wing,'lower_frame',[(x,side*.50,z) for x,z in zip(xs,bottoms)],.027,P['wood'])
    add(chaise,f'side_wing_{side}',wing)

# Small carving at the central apron and at head crest.
for y in [-.55,.55]:
    for i in range(7):
        a=(i-3)*.035
        add(chaise,f'apron_leaf_{y}_{i}',
            ellipsoid((.027,.012,.047),(a+.18,y,.475+abs(i-3)*.008),P['edge']))
for i in range(5):
    add(chaise,f'crest_leaf_{i}',ellipsoid((.025,.022,.045),
        (-1.18,-.09+i*.045,1.60+(.035 if i==2 else 0)),P['edge']))
scene.include('chaise_longue',chaise)

pillow=Asset('loose_pillow')
p=fillet_box((.58,.64,.20),radius=.095,center=(-.78,-.01,1.12),color=P['pillow'])
p.turn('y',-61,pivot=(-.78,-.01,1.12))
p.turn('x',-7,pivot=(-.78,-.01,1.12))
add(pillow,'soft_cushion',p)
# Soft edge roll follows the same complete cushion transform.
edge=Part('pillow_edge')
tube(edge,'piping',[(-1.06,-.30,1.22),(-.50,-.30,1.22),
                   (-.50,.28,1.22),(-1.06,.28,1.22),(-1.06,-.30,1.22)],
     .009,(.88,.81,.66))
edge.turn('y',-61,pivot=(-.78,-.01,1.12))
edge.turn('x',-7,pivot=(-.78,-.01,1.12))
add(pillow,'piping',edge)
scene.include('loose_pillow',pillow)

card=Asset('green_museum_label')
add(card,'card',box((.082,.16,.004),center=(.84,.15,.882),color=(.035,.19,.16)))
for k in range(3):
    add(card,f'printed_line_{k}',box((.039,.003,.001),
        center=(.84,.18-k*.018,.885),color=(.73,.77,.65)))
scene.include('green_museum_label',card)

chair=Asset('cropped_foreground_cane_chair')
add(chair,'seat_rim',fillet_box((.65,.64,.065),radius=.031,
                               center=(-1.37,-1.70,.49),color=P['wood']))
add(chair,'woven_seat',box((.55,.54,.025),center=(-1.37,-1.70,.531),
                          color=(.46,.31,.17)))
for x in [-1.64,-1.10]:
    add(chair,f'leg_{x}',rod(.029,start=(x,-1.9,.02),end=(x,-1.9,.49),color=P['wood']))
scene.include('cropped_foreground_cane_chair',chair)

for name,node in scene.members.items():
    print(name, sum(n.solid is not None for n in node.traverse()))
print('whole_scene',sum(n.solid is not None for n in scene.traverse()))
realize(scene)

# Material targeting uses semantic EMPTY descendants, never primitive-name guesses.
def descendants(name):
    marker=bpy.data.objects.get(name)
    if marker is None:
        candidates=[o for o in bpy.data.objects if o.type=='EMPTY' and o.name.startswith(name)]
        assert candidates, name
        marker=candidates[0]
    meshes=[o for o in marker.children_recursive if o.type=='MESH']
    assert meshes, name
    return marker,meshes

def fabric_material(name,base,striped=False):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.88
    tex=n.new('ShaderNodeTexCoord')
    tex.object=bpy.data.objects.get('chaise_longue')
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=165
    noise.inputs['Detail'].default_value=2
    l.new(tex.outputs['Object'],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.16
    bump.inputs['Distance'].default_value=.008
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Base Color'].default_value=(*base,1)
    if striped:
        wave=n.new('ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='Y'
        wave.inputs['Scale'].default_value=17
        l.new(tex.outputs['Object'],wave.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.75
        ramp.color_ramp.elements[0].color=(*base,1)
        ramp.color_ramp.elements[1].position=.91
        ramp.color_ramp.elements[1].color=(.61,.43,.39,1)
        l.new(wave.outputs['Fac'],ramp.inputs[0])
        l.new(ramp.outputs[0],bs.inputs['Base Color'])
    return m

cloth=fabric_material('fine_cream_and_rose_woven_fabric',P['cloth'],True)
_,meshes=descendants('chaise_longue')
matched=0
for obj in meshes:
    if obj.active_material:
        c=obj.active_material.diffuse_color
        if sum(abs(c[i]-P['cloth'][i]) for i in range(3))<.035:
            obj.data.materials.clear(); obj.data.materials.append(cloth); matched+=1
assert matched
pm=fabric_material('pillow_linen',P['pillow'])
_,meshes=descendants('soft_cushion')
for obj in meshes:
    obj.data.materials.clear(); obj.data.materials.append(pm)

# Cane shader uses a common semantic coordinate object.
marker,meshes=descendants('woven_seat')
cane=bpy.data.materials.new('woven_cane'); cane.use_nodes=True
n=cane.node_tree.nodes; l=cane.node_tree.links
bs=n.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.85
tc=n.new('ShaderNodeTexCoord'); tc.object=marker
waves=[]
for direction in ['X','Y']:
    w=n.new('ShaderNodeTexWave'); w.bands_direction=direction
    w.inputs['Scale'].default_value=65
    l.new(tc.outputs['Object'],w.inputs['Vector']); waves.append(w)
mix=n.new('ShaderNodeMath'); mix.operation='MULTIPLY'
for i,w in enumerate(waves): l.new(w.outputs['Fac'],mix.inputs[i])
r=n.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].color=(.12,.068,.028,1)
r.color_ramp.elements[1].color=(.59,.41,.22,1)
l.new(mix.outputs[0],r.inputs[0]); l.new(r.outputs[0],bs.inputs['Base Color'])
for obj in meshes:
    obj.data.materials.clear(); obj.data.materials.append(cane)

sc=bpy.context.scene
if sc.world is None: sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.76,.81,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32
set_view(P['camera'],P['target'],lens=P['lens'])
area_emitter((-3.3,-.5,3.4),power=480,size=2.5,target=(0,0,.55),color=(1,.91,.77))
area_emitter((.5,-3.0,3.5),power=100,size=4,target=(0,0,.7),color=(.86,.91,1))
sc.view_settings.view_transform='AgX'
