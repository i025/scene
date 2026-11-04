from sceneact import *
import bpy, math, random

# Visual estimates: crown (.13,.25), pillow (.20,.39), far seat (.67,.49),
# rounded end (.82,.65), front right foot (.78,.94), wall seam (.88,.50).
# Observed step 2: wall convergence is closer, but wall base remains too low.
# Chaise left silhouette is too far right; mattress appears too narrow.
# Foreground chair is present and cropped; feet, card and pillow are present.
# Hypotheses: excess camera distance limits framing; wall is too near furniture.
# Bounded revision: closer framing, deeper wall placement, wider chaise assembly.
# Chaise/pillow/card share the width transform, preserving relative placement.
# Lighting and floor reflectance are reduced to address observed washed-out tones.
# Arbitrary scale; hidden geometry and camera calibration remain uncertain.
# Inventory: paneling, parquet, window/drapes, chaise, pillow, card, cane chair.
# Supports: floor -> feet -> frame -> mattress -> pillow/card.

# Camera parameters.
CAMERA = (-.69, -5.04, 3.64)
TARGET = (-.19, .10, 1.02)
LENS = 48

# Architecture parameters.
WALL_Y = 1.85
WALL_OFFSET = WALL_Y - 1.05

# Furniture dimensions and placement, independent of camera.
SEAT_LENGTH = 2.86
SEAT_WIDTH = 1.12
SEAT_Z = .82
SEAT_THICKNESS = .26
CHAISE_WIDTH_FACTOR = 1.25
CHAISE_ANGLE = -16
PIVOT = (0, 0, 0)

# Materials.
cream = (.72,.68,.56)
wall = (.72,.70,.63)
trim = (.80,.77,.68)
sage = (.34,.40,.33)
sage_light = (.49,.53,.43)
gilt = (.65,.59,.42)
fabric = (.79,.73,.61)
pillow_color = (.84,.77,.64)
rose = (.56,.37,.34)
wood = (.10,.043,.026)

# Lighting parameters.
DAYLIGHT = 440
AMBIENT = .22

random.seed(11)
scene = Scene('French chaise room')

def attach(parent, key, node):
    assert key not in parent.members, key
    return parent.include(key, node)

def block(size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    assert all(math.isfinite(v) for v in center)
    return box(size, center=center, color=color)

def rounded(size, radius, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    assert math.isfinite(radius) and 0 < radius <= min(size)/2
    assert all(math.isfinite(v) for v in center)
    return fillet_box(size, radius=radius, center=center, color=color)

def line(radius, start, end, color):
    assert math.isfinite(radius) and radius > 0
    assert all(math.isfinite(v) for v in (*start,*end))
    assert sum((a-b)**2 for a,b in zip(start,end)) > 1e-16
    return rod(radius, start=start, end=end, color=color)

def tube(points, radius, color):
    assert math.isfinite(radius) and radius > 0
    assert len(points) >= 2
    assert all(math.isfinite(v) for p in points for v in p)
    assert all(sum((a-b)**2 for a,b in zip(p,q)) > 1e-16
               for p,q in zip(points,points[1:]))
    return sweep_tube(points=points, radius=radius, color=color)

def sphere(radius, center, color):
    assert math.isfinite(radius) and radius > 0
    assert all(math.isfinite(v) for v in center)
    return ball(radius, center=center, color=color)

architecture = Asset('paneled room')
attach(architecture,'floor foundation',
       block((12,12,.10),(0,0,-.065),wood))
for j in range(-16,17):
    for i in range(-7,8):
        u = i*.91+(j%2)*.455
        v = j*.19
        x,y = (u-v)*.7071,(u+v)*.7071
        c = random.uniform(.82,1.16)
        plank = block((.902,.182,.018),(x,y,-.005),
                      (.115*c,.054*c,.033*c))
        plank.turn('z',45)
        attach(architecture,f'parquet_{j}_{i}',plank)

attach(architecture,'rear wall',
       block((10,.17,4.5),(0,WALL_Y+.085,2.2),wall))
for k,(z,h,d) in enumerate([
    (.10,.17,.11),(.23,.055,.08),
    (1.92,.045,.06),(2.03,.075,.085),
    (2.23,.045,.05),(2.31,.06,.065)]):
    attach(architecture,f'horizontal molding_{k}',
           block((9,d,h),(0,WALL_Y-d/2,z),trim))

for n,(a,b) in enumerate([
    (-3,-1.65),(-1.55,1.65),(1.78,3.4)]):
    for m,(inset,thickness) in enumerate([(0,.025),(.055,.016)]):
        left,right = a+inset,b-inset
        low,high = .35+inset,1.84-inset
        edges = [
            ((left,WALL_Y-.027,low),(left,WALL_Y-.027,high)),
            ((right,WALL_Y-.027,low),(right,WALL_Y-.027,high)),
            ((left,WALL_Y-.027,low),(right,WALL_Y-.027,low)),
            ((left,WALL_Y-.027,high),(right,WALL_Y-.027,high))]
        for k,(p,q) in enumerate(edges):
            attach(architecture,f'panel_{n}_{m}_{k}',
                   line(thickness,p,q,trim))
attach(architecture,'right pilaster',
       block((.38,.38,3.5),(2.40,.99+WALL_OFFSET,1.75),trim))
for k,x in enumerate([2.27,2.52]):
    attach(architecture,f'pilaster edge_{k}',
           block((.016,.018,2.7),(x,.79+WALL_OFFSET,1.65),wall))
# Fine vertical panel joints and two small dark wall fittings.
for k,x in enumerate([-.95,.35]):
    attach(architecture,f'wall joint_{k}',
           block((.007,.004,3.4),(x,WALL_Y-.004,1.7),(.40,.37,.30)))
for k,x in enumerate([-.82,-.72]):
    fitting = sphere(.024,(x,WALL_Y-.045,2.10),(.07,.065,.045))
    fitting.resize((.55,.55,1.4))
    attach(architecture,f'wall fitting_{k}',fitting)
attach(scene,'architecture',architecture)

window = Asset('left window and curtains')
attach(window,'bright glazing',
       block((.07,1.1,3.2),(-2.35,.35,1.6),(.94,.93,.85)))
for k in range(12):
    y = -.32+k*.093
    c = (.87+.025*(k%2),.85+.025*(k%2),.77+.025*(k%2))
    attach(window,f'sheer fold_{k}',
           line(.052,(-2.28,y,.10),(-2.28,y,3.35),c))
for k in range(5):
    y = .70+k*.055
    c = (.57+.025*k,.48+.024*k,.35+.022*k)
    attach(window,f'heavy drape_{k}',
           line(.055,(-2.18,y,.04),(-2.18,y,3.35),c))
attach(scene,'window',window)

chaise = Asset('carved chaise longue')
for i,x in enumerate([-1.12,1.20]):
    for j,y in enumerate([-.48,.45]):
        sign = -1 if x < 0 else 1
        pts = [(x,y,.65),(x+sign*.045,y,.50),
               (x-sign*.045,y,.28),(x-sign*.025,y,.10),
               (x+sign*.045,y-.015,.045)]
        attach(chaise,f'leg_{i}_{j}',tube(pts,.043,sage))
        attach(chaise,f'leg highlight_{i}_{j}',
               tube([(px,py-.036,pz) for px,py,pz in pts],.010,gilt))
        attach(chaise,f'foot_{i}_{j}',sphere(.045,pts[-1],sage_light))

attach(chaise,'seat frame',
       rounded((2.88,1.16,.15),.07,(.03,0,.64),sage))
for j,y in enumerate([-.585,.585]):
    for k,z in enumerate([.59,.70]):
        attach(chaise,f'apron edge_{j}_{k}',
               tube([(-1.35,y,z),(-.80,y,z-.015),
                     (0,y,z-.02),(.85,y,z-.015),
                     (1.40,y*.91,z+.025)],.016,gilt))
attach(chaise,'main upholstered mattress',
       rounded((SEAT_LENGTH,SEAT_WIDTH,SEAT_THICKNESS),
               .125,(.035,0,SEAT_Z),fabric))
for j,y in enumerate([-.556,.556]):
    attach(chaise,f'mattress piping_{j}',
           tube([(-1.28,y,.79),(-.60,y,.77),
                 (.3,y,.77),(1.30,y,.79)],.008,cream))

back = Asset('upholstered curved headrest')
panel = rounded((.19,1.08,.94),.09,(-1.36,0,1.18),fabric)
panel.turn('y',-13)
attach(back,'padded back',panel)
outline = [
    (-1.25,-.56,.79),(-1.39,-.59,1.10),
    (-1.48,-.57,1.46),(-1.47,-.47,1.65),
    (-1.45,-.24,1.70),(-1.43,0,1.65),
    (-1.43,.28,1.53),(-1.39,.48,1.44),
    (-1.30,.57,1.40),(-1.25,.58,1.18),(-1.10,.57,.91)]
attach(back,'carved back rim',tube(outline,.040,sage))
attach(back,'back rim gilt bead',
       tube([(x+.023,y,z+.012) for x,y,z in outline],.012,gilt))
front_panel = rounded((.67,.065,.46),.03,(-1.13,-.548,.96),fabric)
front_panel.turn('y',-15)
attach(back,'front upholstered wing',front_panel)
for j,y in enumerate([-.592,.57]):
    pts = [(-1.47,y,1.50),(-1.36,y,1.29),
           (-1.15,y,1.17),(-.91,y,1.12),(-.78,y,1.14)]
    attach(back,f'scrolled arm_{j}',tube(pts,.032,sage))
    attach(back,f'arm gilt_{j}',
           tube([(x,yy-.018,z+.022) for x,yy,z in pts],.009,gilt))
    attach(back,f'arm terminal_{j}',sphere(.044,pts[-1],gilt))
attach(chaise,'headrest',back)

for k in range(9):
    a = k*math.tau/9
    attach(chaise,f'crest leaf_{k}',
           sphere(.025,(-1.46+.023*math.cos(a),
                         -.45+.075*math.sin(a),
                         1.66+.05*math.cos(a)),gilt))
for j,cx in enumerate([-.95,.10,1.26]):
    for k in range(7):
        a = k*math.tau/7
        leaf = sphere(.031,(cx+.072*math.cos(a),-.606,
                             .625+.043*math.sin(a)),gilt)
        leaf.resize((1,.35,.7))
        attach(chaise,f'apron flower_{j}_{k}',leaf)
    attach(chaise,f'apron flower center_{j}',
           sphere(.028,(cx,-.617,.625),cream))
for j in range(32):
    y = -.51+j*.033
    attach(chaise,f'fine seat stripe_{j}',
           line(.0019,(-1.23,y,.951),(1.28,y,.951),(.63,.57,.49)))
for i in range(21):
    for j in range(9):
        x,y = -1.22+i*.121,-.46+j*.113
        if x > 1.25:
            continue
        attach(chaise,f'embroidered fleck_{i}_{j}',
               line(.004,(x,y,.953),(x+.022,y+.004,.953),rose))
        if (i+j)%3 == 0:
            attach(chaise,f'embroidered leaf_{i}_{j}',
                   line(.0028,(x+.010,y,.954),
                        (x+.020,y+.020,.954),(.47,.48,.36)))

pillow = Asset('loose cream pillow')
p = rounded((.30,.74,.65),.13,(-1.11,-.015,1.25),pillow_color)
p.turn('y',-22)
p.turn('x',9)
attach(pillow,'soft pillow body',p)
attach(pillow,'pillow seam',
       tube([(-.91,-.38,1.03),(-.96,-.40,1.51),
             (-1.04,-.29,1.59),(-1.05,.26,1.56),
             (-.94,.34,1.10),(-.91,-.38,1.03)],.007,(.73,.66,.53)))

label = Asset('green museum label')
card_z = SEAT_Z+SEAT_THICKNESS/2+.003
card_center = (.85,.20,card_z)
attach(label,'card',
       block((.105,.22,.006),card_center,(.055,.22,.18)))
for j in range(4):
    attach(label,f'tiny cream printing_{j}',
           block((.037,.003,.001),
                 (.85,.16+j*.015,card_z+.0035),(.70,.75,.61)))
label.turn('z',-9,pivot=card_center)

for key,asset in [('chaise',chaise),('pillow',pillow),('label',label)]:
    asset.resize((1,CHAISE_WIDTH_FACTOR,1),pivot=PIVOT)
    asset.turn('z',CHAISE_ANGLE,pivot=PIVOT)
    attach(scene,key,asset)

chair = Asset('cropped foreground cane chair')
attach(chair,'seat edge',
       rounded((.73,.70,.11),.05,(-1.78,-1.70,.48),sage))
attach(chair,'woven seat',
       block((.61,.58,.018),(-1.78,-1.70,.544),(.49,.37,.23)))
for i in range(21):
    x = -2.07+i*.029
    attach(chair,f'cane strand x_{i}',
           line(.004,(x,-1.97,.556),(x,-1.42,.556),(.68,.56,.37)))
for i in range(19):
    y = -1.96+i*.029
    attach(chair,f'cane strand y_{i}',
           line(.004,(-2.07,y,.558),(-1.49,y,.558),(.64,.51,.33)))
for j,y in enumerate([-2.04,-1.36]):
    attach(chair,f'seat border_{j}',
           line(.022,(-2.13,y,.56),(-1.43,y,.56),gilt))
# Hidden chair supports complete its floor contact without changing the crop.
for i,x in enumerate([-2.07,-1.49]):
    for j,y in enumerate([-1.96,-1.44]):
        attach(chair,f'chair leg_{i}_{j}',
               line(.025,(x,y,.025),(x,y,.48),sage))
attach(scene,'foreground chair',chair)

# Constructors validate positive dimensions, legal fillets and distinct paths.
# attach validates unique per-parent include keys.
realize(scene)

def subtree_meshes(parent_name):
    parent = bpy.data.objects.get(parent_name)
    assert parent is not None, parent_name
    stack,meshes = [parent],[]
    while stack:
        obj = stack.pop()
        if obj.type == 'MESH':
            meshes.append(obj)
        stack.extend(list(obj.children))
    assert meshes, parent_name
    return meshes

def local_roughness(parent_name,value):
    copies = {}
    for obj in subtree_meshes(parent_name):
        for slot in obj.material_slots:
            original = slot.material
            if original is None:
                continue
            key = original.as_pointer()
            if key not in copies:
                mat = original.copy()
                mat.name = f'{parent_name} / {original.name}'
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                if bsdf is not None:
                    bsdf.inputs['Roughness'].default_value = value
                copies[key] = mat
            slot.material = copies[key]

for name,value in [('architecture',.79),('window',.90),
                   ('chaise',.79),('pillow',.90),
                   ('label',.79),('foreground chair',.79)]:
    local_roughness(name,value)
for name in ('chaise','pillow','foreground chair','window'):
    for obj in subtree_meshes(name):
        if len(obj.data.polygons) > 12:
            for polygon in obj.data.polygons:
                polygon.use_smooth = True

set_view(CAMERA,TARGET,lens=LENS)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new('Room ambient')
    bpy.context.scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
if background is None:
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    output = world.node_tree.nodes.get('World Output')
    if output is None:
        output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'],
                              output.inputs['Surface'])
background.inputs['Color'].default_value = (.68,.72,.77,1)
background.inputs['Strength'].default_value = AMBIENT
area_emitter((-3,-.8,3.4),power=DAYLIGHT,size=3.1,
             target=(0,0,.7),color=(1,.92,.79))
area_emitter((1,-3,3.8),power=65,size=4,
             target=(0,0,.8),color=(1,.95,.88))
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 384
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.view_settings.view_transform = 'AgX'
