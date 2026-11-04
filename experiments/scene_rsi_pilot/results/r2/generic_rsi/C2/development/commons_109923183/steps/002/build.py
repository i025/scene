from sceneact import *
import bpy, math, random

# REVISION LEDGER
# Reference / step-1 anchors:
# head crest (.09,.25) / (.29,.29): subject too small and too far right.
# seat foot (.82,.64) / (.75,.62): increase subject framing.
# front foot (.77,.92) / (.67,.82): increase framing while preserving floor contact.
# label (.69,.56) / (.66,.54): preserve its position on the mattress.
# wall panel right corner (.85,.40) / (.90,.66): wall perspective is incorrect.
# foreground chair (.16,.82) / (.16,.73): preserve lower-left crop, lower its projection.
# Camera residual: wall rails descend right instead of rising slightly right.
# Highest priority is coherent camera/framing correction: move viewpoint left,
# narrow framing, and preserve chaise orientation relative to the photograph.
# Coupled placement correction: chaise is angled slightly relative to the wall.
# Local geometry residual: visible black joints in segmented upholstery/aprons;
# remove coplanar overlap. Pillow needs a larger, square silhouette.
# Appearance residual: parquet is too bright/orange; fabric pattern too faint.
# Preserve all semantic objects, complete filled wings, four legs, apron, label.
#
# Object inventory, normalized reference bounds:
# chaise .03,.24-.84,.94; pillow .07,.26-.33,.51;
# label .68,.53-.71,.59; paneled wall .04,0-1,.55;
# curtain/window 0,0-.08,.78; parquet lower half;
# cropped cane chair 0,.80-.19,1; right wall return .85,0-1,.56.
# Occlusion: wall/window -> chaise frame -> mattress/pillow/card -> foreground chair.
# Supports: chaise's four cabriole feet and chair legs meet parquet at z=0.
# Perspective hypothesis: elevated front view, almost normal to wall,
# with chaise yaw producing its slight downward-right mattress edge.

P = {
    'camera': (-.72,-5.65,3.68),
    'target': (.18,.08,.91),
    'lens': 63,
    'yaw': -13,
    'wood': (.27,.33,.27),
    'edge': (.58,.54,.39),
    'cloth': (.79,.72,.61),
    'pillow': (.83,.74,.58),
    'wall': (.70,.66,.57),
    'floor': (.115,.052,.027),
    'key_power': 360
}
random.seed(19)
scene=Scene('French chaise room')

def add(p,n,v):
    return p.include(n,v)

def tube(p,n,pts,r,c):
    return add(p,n,sweep_tube(points=pts,radius=r,color=c))

def ellipsoid(size,center,color):
    return ball(1,center=center,color=color).resize(size,pivot=center)

floor=Asset('parquet_floor')
add(floor,'foundation',box((12,10,.12),center=(0,0,-.08),color=P['floor']))
for i in range(-10,11):
    for j in range(-7,7):
        for k in range(3):
            v=random.uniform(-.012,.012)
            col=(.125+v,.060+v*.55,.032+v*.3)
            if (i+j)%2:
                size=(.159,.479,.018)
                pos=(i*.48+(k-1)*.16,j*.48,-.009)
            else:
                size=(.479,.159,.018)
                pos=(i*.48,j*.48+(k-1)*.16,-.009)
            add(floor,f'board_{i}_{j}_{k}',box(size,center=pos,color=col))
scene.include('parquet_floor',floor)

wall=Asset('paneled_wall')
add(wall,'wall_body',box((9,.16,3.8),center=(0,1.02,1.9),color=P['wall']))
for z,d,h in [(.10,.10,.18),(.235,.065,.045),(.31,.045,.035),
              (1.91,.065,.055),(2.01,.07,.045),(2.26,.045,.035)]:
    add(wall,f'horizontal_{z}',box((9,d,h),
        center=(0,.907-d/2,z),color=(.77,.73,.64)))
for inset,w in [(0,.022),(.045,.011)]:
    x0,x1=-1.90+inset,1.92-inset
    z0,z1=.43+inset,1.79-inset
    for name,c,s in [
        ('bottom',((x0+x1)/2,.902,z0),(x1-x0,.037,w)),
        ('top',((x0+x1)/2,.902,z1),(x1-x0,.037,w)),
        ('left',(x0,.902,(z0+z1)/2),(w,.037,z1-z0)),
        ('right',(x1,.902,(z0+z1)/2),(w,.037,z1-z0))]:
        add(wall,f'panel_{inset}_{name}',box(s,center=c,color=(.79,.75,.66)))
for x in [-1.25,.05]:
    add(wall,f'vertical_joint_{x}',box((.004,.005,3.3),
        center=(x,.934,1.66),color=(.40,.37,.30)))
for x in [-1.09,-.99]:
    add(wall,f'small_dark_fixture_{x}',ellipsoid((.018,.018,.033),
        (x,.889,1.99),(.075,.068,.048)))
scene.include('paneled_wall',wall)

pier=Asset('right_wall_return')
add(pier,'body',box((.43,.62,3.5),center=(2.36,.84,1.75),color=(.76,.75,.67)))
add(pier,'base',box((.47,.69,.20),center=(2.36,.80,.10),color=(.81,.79,.70)))
for x in [2.19,2.50]:
    add(pier,f'molding_{x}',box((.018,.025,2.55),
        center=(x,.516,1.70),color=(.82,.80,.71)))
scene.include('right_wall_return',pier)

curtain=Asset('window_and_curtains')
add(curtain,'bright_window',box((.65,.05,3.4),
    center=(-2.25,.48,1.7),color=(.96,.95,.87)))
for k in range(10):
    x=-2.03+k*.041
    col=(.58,.49,.36) if k%3==0 else (.79,.72,.60)
    add(curtain,f'fold_{k}',rod(.045,start=(x,.43,.03),
        end=(x-.20,.53,3.5),color=col))
scene.include('window_and_curtains',curtain)

chaise=Asset('chaise_longue')
add(chaise,'seat_cushion',fillet_box((2.43,1.03,.24),radius=.115,
    center=(.12,0,.755),color=P['cloth']))
add(chaise,'seat_foundation',fillet_box((2.40,1.045,.12),radius=.055,
    center=(.10,0,.605),color=P['wood']))
for y in [-.518,.518]:
    tube(chaise,f'seat_welting_{y}',
        [(-1.03,y,.70),(-.75,y,.683),(.20,y,.68),(1.12,y,.68),(1.27,y,.72)],
        .012,(.64,.57,.44))

for y in [-.535,.535]:
    apron=Part(f'apron_{y}')
    xs=[-1.01,-.80,-.47,-.13,.20,.53,.86,1.12,1.25]
    lower=[.49,.47,.485,.46,.43,.46,.48,.46,.48]
    for i in range(len(xs)-1):
        mid=(xs[i]+xs[i+1])/2
        bottom=(lower[i]+lower[i+1])/2
        add(apron,f'filled_rail_{i}',box(
            (xs[i+1]-xs[i],.055,.61-bottom),
            center=(mid,y,(.61+bottom)/2),color=P['wood']))
    front=y+(-.033 if y<0 else .033)
    tube(apron,'upper_gilt_line',[(x,front,.603) for x in xs],.009,P['edge'])
    tube(apron,'lower_gilt_line',[(x,front,z) for x,z in zip(xs,lower)],.012,P['edge'])
    add(chaise,f'apron_{y}',apron)

for ix,x in enumerate([-.92,1.10]):
    for iy,y in enumerate([-.45,.45]):
        out=-1 if x<0 else 1
        pts=[(x,y,.56),(x+out*.065,y,.44),(x+out*.025,y,.30),
             (x-out*.035,y,.13),(x-out*.012,y,.055)]
        tube(chaise,f'cabriole_{ix}_{iy}',pts,.036,P['wood'])
        tube(chaise,f'leg_edge_{ix}_{iy}',
             [(a,b-.025,c) for a,b,c in pts],.007,P['edge'])
        add(chaise,f'foot_{ix}_{iy}',ellipsoid((.050,.041,.027),
            (pts[-1][0],y,.045),P['wood']))

# Contiguous narrow slices provide the filled curved head without overlapping faces.
back=Part('upholstered_head')
for k in range(16):
    y=-.50+(k+.5)/16
    s=(k+.5)/16
    crest=1.49+.10*math.sin(s*math.pi)
    x=-1.065-.13*math.sin(s*math.pi)
    panel=box((.14,1/16,crest-.75),
        center=(x,y,(crest+.75)/2),color=P['cloth'])
    panel.turn('y',-12,pivot=(x,y,.75))
    add(back,f'filled_back_{k}',panel)
top=[(-1.105-.13*math.sin(k/12*math.pi),-.5+k/12,
      1.49+.10*math.sin(k/12*math.pi)) for k in range(13)]
tube(back,'crest_wood',top,.037,P['wood'])
tube(back,'crest_highlight',[(x+.006,y-.018,z+.017) for x,y,z in top],
     .010,P['edge'])
add(chaise,'head_back',back)

for side in [-1,1]:
    wing=Part(f'wing_{side}')
    xs=[-1.07,-.95,-.82,-.68,-.53,-.43]
    tops=[1.47,1.31,1.20,1.15,1.13,1.16]
    bottoms=[.70,.68,.65,.64,.65,.69]
    # Exactly adjoining strips eliminate the previous coplanar intersections.
    for k in range(len(xs)-1):
        for q in range(3):
            t0=q/3
            t1=(q+1)/3
            x0=xs[k]+(xs[k+1]-xs[k])*t0
            x1=xs[k]+(xs[k+1]-xs[k])*t1
            t=(t0+t1)/2
            ztop=tops[k]*(1-t)+tops[k+1]*t
            bot=bottoms[k]*(1-t)+bottoms[k+1]*t
            add(wing,f'filled_side_{k}_{q}',box((x1-x0,.078,ztop-bot),
                center=((x0+x1)/2,side*.495,(ztop+bot)/2),color=P['cloth']))
    tube(wing,'arm_rail',[(x,side*.50,z) for x,z in zip(xs,tops)],.033,P['wood'])
    tube(wing,'arm_gilt',[(x,side*.525,z+.011) for x,z in zip(xs,tops)],.009,P['edge'])
    tube(wing,'lower_frame',[(x,side*.51,z) for x,z in zip(xs,bottoms)],.027,P['wood'])
    tube(wing,'front_upright',
        [(-.43,side*.51,1.16),(-.44,side*.51,1.00),(-.43,side*.51,.83),
         (-.43,side*.51,.69)],.026,P['wood'])
    add(chaise,f'side_wing_{side}',wing)

for y in [-.57,.57]:
    for i in range(7):
        a=(i-3)*.035
        add(chaise,f'apron_leaf_{y}_{i}',ellipsoid((.027,.012,.047),
            (a+.18,y,.475+abs(i-3)*.008),P['edge']))
for i in range(5):
    add(chaise,f'crest_leaf_{i}',ellipsoid((.025,.022,.045),
        (-1.22,-.09+i*.045,1.60+(.035 if i==2 else 0)),P['edge']))

pillow=Asset('loose_pillow')
pc=(-.80,-.025,1.17)
p=fillet_box((.72,.72,.22),radius=.105,center=pc,color=P['pillow'])
p.turn('y',-64,pivot=pc)
p.turn('x',-7,pivot=pc)
add(pillow,'soft_cushion',p)
edge=Part('pillow_edge')
pts=[(-1.15,-.37,1.27),(-.45,-.37,1.27),(-.45,.32,1.27),
     (-1.15,.32,1.27),(-1.15,-.37,1.27)]
tube(edge,'piping',pts,.008,(.85,.76,.60))
edge.turn('y',-64,pivot=pc)
edge.turn('x',-7,pivot=pc)
add(pillow,'piping',edge)

card=Asset('green_museum_label')
add(card,'card',box((.082,.16,.004),center=(.84,.15,.882),color=(.025,.14,.11)))
for k in range(3):
    add(card,f'printed_line_{k}',box((.039,.003,.001),
        center=(.84,.18-k*.018,.885),color=(.73,.77,.65)))

# Apply the same meaningful floor-origin rotation to the three independent objects.
for name,node in [('chaise_longue',chaise),('loose_pillow',pillow),
                  ('green_museum_label',card)]:
    node.turn('z',P['yaw'],pivot=(0,0,0))
    scene.include(name,node)

chair=Asset('cropped_foreground_cane_chair')
cx,cy=-1.57,-1.55
add(chair,'seat_rim',fillet_box((.65,.64,.065),radius=.031,
    center=(cx,cy,.49),color=P['wood']))
add(chair,'woven_seat',box((.55,.54,.025),center=(cx,cy,.531),
    color=(.46,.31,.17)))
for ix,x in enumerate([cx-.27,cx+.27]):
    for iy,y in enumerate([cy-.24,cy+.24]):
        add(chair,f'leg_{ix}_{iy}',rod(.029,
            start=(x,y,.02),end=(x,y,.49),color=P['wood']))
scene.include('cropped_foreground_cane_chair',chair)

# Audit complete semantic memberships, including all attached subassemblies.
for name,node in scene.members.items():
    print(name,sum(n.solid is not None for n in node.traverse()))
print('whole_scene',sum(n.solid is not None for n in scene.traverse()))
realize(scene)

def descendants(name):
    marker=bpy.data.objects.get(name)
    if marker is None:
        found=[o for o in bpy.data.objects if o.type=='EMPTY' and o.name.startswith(name)]
        assert found,name
        marker=found[0]
    meshes=[o for o in marker.children_recursive if o.type=='MESH']
    assert meshes,name
    return marker,meshes

def fabric_material(name,base,striped=False):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes
    l=m.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.88
    bs.inputs['Base Color'].default_value=(*base,1)
    tc=n.new('ShaderNodeTexCoord')
    tc.object=bpy.data.objects.get('chaise_longue')
    noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=180
    noise.inputs['Detail'].default_value=2
    l.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.10
    bump.inputs['Distance'].default_value=.004
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if striped:
        wave=n.new('ShaderNodeTexWave')
        wave.wave_type='BANDS'
        wave.bands_direction='Y'
        wave.inputs['Scale'].default_value=12
        l.new(tc.outputs['Object'],wave.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.92
        ramp.color_ramp.elements[0].color=(*base,1)
        ramp.color_ramp.elements[1].position=.975
        ramp.color_ramp.elements[1].color=(.57,.36,.33,1)
        l.new(wave.outputs['Fac'],ramp.inputs[0])
        l.new(ramp.outputs[0],bs.inputs['Base Color'])
    return m

cloth=fabric_material('cream_and_rose_woven_fabric',P['cloth'],True)
_,meshes=descendants('chaise_longue')
matched=0
for obj in meshes:
    if obj.active_material:
        c=obj.active_material.diffuse_color
        if sum(abs(c[i]-P['cloth'][i]) for i in range(3))<.035:
            obj.data.materials.clear()
            obj.data.materials.append(cloth)
            matched+=1
assert matched>0
pm=fabric_material('pillow_linen',P['pillow'])
_,meshes=descendants('soft_cushion')
for obj in meshes:
    obj.data.materials.clear()
    obj.data.materials.append(pm)

marker,meshes=descendants('woven_seat')
cane=bpy.data.materials.new('woven_cane')
cane.use_nodes=True
n=cane.node_tree.nodes
l=cane.node_tree.links
bs=n.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.85
tc=n.new('ShaderNodeTexCoord')
tc.object=marker
waves=[]
for direction in ['X','Y']:
    w=n.new('ShaderNodeTexWave')
    w.bands_direction=direction
    w.inputs['Scale'].default_value=65
    l.new(tc.outputs['Object'],w.inputs['Vector'])
    waves.append(w)
mix=n.new('ShaderNodeMath')
mix.operation='MULTIPLY'
for i,w in enumerate(waves):
    l.new(w.outputs['Fac'],mix.inputs[i])
r=n.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].color=(.085,.042,.018,1)
r.color_ramp.elements[1].color=(.46,.29,.14,1)
l.new(mix.outputs[0],r.inputs[0])
l.new(r.outputs[0],bs.inputs['Base Color'])
for obj in meshes:
    obj.data.materials.clear()
    obj.data.materials.append(cane)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.76,.81,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.25
set_view(P['camera'],P['target'],lens=P['lens'])
area_emitter((-3.3,-.5,3.4),power=P['key_power'],size=2.5,
    target=(0,0,.55),color=(1,.91,.77))
area_emitter((.5,-3.0,3.5),power=65,size=4,
    target=(0,0,.7),color=(.86,.91,1))
sc.view_settings.view_transform='AgX'
