from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory (estimated normalized image bounds):
# Wall (0,0)-(.83,.44), warm off-white; gray carpet (0,.85)-(1,1).
# Ochre sofa (.02,.28)-(.97,.96): two back cushions, two seat cushions,
# thick arms and low upholstered apron; table obscures its lower right.
# Pale golden pillow (.12,.31)-(.32,.53), leaning against left back.
# Dark coffee table (.32,.60)-(1,1): rectangular top, apron, square legs.
# Two white cups and saucers (.46,.55)-(.57,.68), (.71,.55)-(.84,.69),
# with visible openings and outward handles, on layered pale napkins.
# Flowering plant (.56,.33)-(.74,.65): dark pot, branching foliage,
# separated blue-gray flower clusters with irregular contours.
# Gray curtain (.80,0)-(1,.43): vertical pleats and gathered curved folds.
# Hidden furniture construction and curtain attachment remain uncertain.
#
# Previous execution failed before realization: bind received strings rather
# than scene member nodes. Corrected below using plant and table objects.
# No rendered image was produced; camera and geometry remain unverified.
#
# Expanded primitive estimate: 10 fillet boxes ~260; architecture/table ~13;
# pillow piping 9; tea settings ~50 including Boolean operands;
# plant ~187; curtain ~66; total approximately 585 primitive meshes.
# All dimensions positive; curved paths have distinct adjacent points.

random.seed(12)
scene = Scene('Warm living room')
ochre = (.68,.355,.105)
seatgold = (.74,.405,.145)
backgold = (.80,.463,.19)
pillowgold = (.89,.63,.31)
wood = (.055,.036,.025)
white = (.88,.90,.87)

architecture = Asset('architecture')
architecture.include('wall', box((15,.13,7), center=(0,2.05,3), color=(.76,.75,.71)))
architecture.include('carpet', box((15,15,.10), center=(0,0,-.065), color=(.29,.275,.26)))
scene.include('architecture', architecture)

sofa = Asset('ochre sofa')
sofa.include('lower upholstered apron',
             fillet_box((4.42,1.50,.48), .07, center=(0,.98,.30), color=ochre))
sofa.include('back foundation',
             fillet_box((4.04,.34,1.36), .08, center=(0,1.59,.96), color=ochre))
for i,x in enumerate((-1.0,1.0)):
    sofa.include('back cushion '+str(i),
                 fillet_box((1.98,.34,1), .095, center=(x,1.345,1.20), color=backgold))
    sofa.include('seat cushion '+str(i),
                 fillet_box((1.96,1.13,.29), .10, center=(x,.79,.66), color=seatgold))
for i,x in enumerate((-2.10,2.10)):
    sofa.include('rounded arm '+str(i),
                 fillet_box((.43,1.48,1.06), .105, center=(x,.94,.76), color=ochre))
sofa.include('seat front seam',
             rod(.011, start=(-1.91,.205,.555), end=(1.91,.205,.555),
                 color=(.46,.25,.075)))
scene.include('sofa', sofa)

pillow = Asset('loose left pillow')
p = fillet_box((.79,.23,.76), .105, center=(-1.36,1.035,1.205), color=pillowgold)
p.turn('y',-12)
p.turn('x',-12)
pillow.include('soft cushion', p)
corners = [(-.38,-.135,-.35),(.38,-.135,-.35),(.38,-.135,.35),
           (-.38,-.135,.35),(-.38,-.135,-.35)]
pipe = sweep_tube(points=[(x-1.36,y+1.035,z+1.205) for x,y,z in corners],
                  radius=.008, color=(.74,.49,.22))
pipe.turn('y',-12,pivot=(-1.36,1.035,1.205))
pipe.turn('x',-12,pivot=(-1.36,1.035,1.205))
pillow.include('perimeter piping',pipe)
scene.include('left pillow',pillow)

table = Asset('dark coffee table')
table.include('solid rectangular top',
              box((3.10,1.24,.12),center=(.72,-.86,.715),color=wood))
table.include('front apron',
              box((3,.085,.20),center=(.72,-1.405,.57),color=wood))
table.include('left apron',
              box((.085,1.13,.20),center=(-.735,-.86,.57),color=wood))
for i,x in enumerate((-.69,2.13)):
    for j,y in enumerate((-1.36,-.36)):
        table.include('square leg %s %s'%(i,j),
                      box((.125,.125,.66),center=(x,y,.325),color=wood))
scene.include('coffee table',table)

for i,(x,y) in enumerate(((.13,-.91),(1.36,-.91))):
    setting = Asset('tea setting '+str(i))
    nap = box((.69,.44,.012),center=(x,y,.783),color=(.56,.65,.60))
    nap.turn('z',-9 if i==0 else 8)
    setting.include('sage napkin',nap)
    paper = box((.60,.36,.009),center=(x+.02,y-.025,.795),color=(.84,.84,.75))
    paper.turn('z',7 if i==0 else -7)
    setting.include('cream folded napkin',paper)
    setting.include('saucer',rod(.205,length=.018,center=(x,y,.811),color=white))
    setting.include('saucer inner disk',
                    rod(.146,length=.009,center=(x,y,.824),color=(.80,.84,.82)))
    outer = rod(.108,length=.245,center=(x,y,.958),color=white)
    inner = rod(.092,length=.25,center=(x,y,.982),color=white)
    setting.include('hollow cup',subtract(outer,inner))
    setting.include('tea surface',
                    rod(.088,length=.004,center=(x,y,1.060),color=(.16,.105,.045)))
    side = -1 if i==0 else 1
    pts = [(x+side*(.105+.079*math.sin(math.pi*k/8)),y,1.035-.155*k/8)
           for k in range(9)]
    setting.include('ceramic loop handle',
                    sweep_tube(points=pts,radius=.012,color=white))
    scene.include('tea setting '+str(i),setting)

plant = Asset('flowering plant')
potx,poty = .77,-.68
plant.include('dark pot',
              rod(.178,length=.29,center=(potx,poty,.935),color=(.07,.075,.064)))
plant.include('pot rim',
              rod(.185,length=.026,center=(potx,poty,1.082),color=(.095,.10,.082)))
plant.include('dark soil',
              rod(.16,length=.008,center=(potx,poty,1.099),color=(.036,.028,.016)))
green = (.19,.30,.105)
leafcols = [(.23,.36,.13),(.29,.40,.16),(.35,.43,.19),(.16,.28,.095)]
branch_count = 17
leaves_per_branch = 4
canopy_width = .73
for j in range(branch_count):
    a = j*2.399
    reach = .18+.15*random.random()
    end = (potx+math.cos(a)*reach,poty+math.sin(a)*reach*.70,
           1.32+random.random()*.22)
    start = (potx+random.uniform(-.05,.05),poty+random.uniform(-.04,.04),1.07)
    plant.include('leaf branch '+str(j),rod(.008,start=start,end=end,color=green))
    for k in range(leaves_per_branch):
        t = .40+.17*k
        base = Vector(start).lerp(Vector(end),t)
        angle = a+(-1 if k%2 else 1)*.95
        leaf = ball(1,center=(base.x+.043*math.cos(angle),
                              base.y+.043*math.sin(angle),base.z+.012),
                    color=leafcols[(j+k)%4])
        leaf.resize((.077,.023,.012))
        leaf.turn('z',math.degrees(angle))
        leaf.turn('y',-18)
        plant.include('leaf %s %s'%(j,k),leaf)

heads = [(-.27,.015,1.72,.105),(-.12,.05,1.86,.09),
         (.08,.055,1.75,.10),(.26,.04,1.69,.115),
         (.17,-.08,1.59,.086),(-.23,-.06,1.57,.085),
         (.02,-.09,1.66,.08)]
florets_per_head = 13
for j,(dx,dy,z,r) in enumerate(heads):
    end = (potx+dx,poty+dy,z)
    plant.include('flower stem '+str(j),
                  rod(.007,start=(potx,poty,1.11),end=end,color=green))
    for k in range(florets_per_head):
        a = k*2.4
        zz = 1-2*(k+.5)/florets_per_head
        rr = math.sqrt(1-zz*zz)
        c = (end[0]+r*.72*rr*math.cos(a),
             end[1]+r*.72*rr*math.sin(a),end[2]+r*.65*zz)
        plant.include('flower cluster %s floret %s'%(j,k),
                      ball(r*.32,center=c,
                           color=[(.57,.64,.69),(.69,.74,.75),(.47,.55,.62)][k%3]))
scene.include('flowering plant',plant)
# Constraint endpoints must be the actual scene members, not their name strings.
scene.bind(plant,table,source_anchor='bottom',target_anchor='top',
           offset=(.05,.18,0))

curtain = Asset('right gathered curtain')
for j in range(12):
    x = 1.78+j*.086
    y = 1.78+.075*math.sin(j*1.7)
    fold = rod(.077,length=3.75,center=(x,y,2.34),
               color=[(.20,.195,.18),(.30,.29,.265),(.39,.38,.35)][j%3])
    fold.resize((.75,1,1))
    curtain.include('vertical pleat '+str(j),fold)
for j in range(6):
    pts = [(2.20+j*.05,1.65,3.55),
           (2.16+j*.043,1.59,2.92),
           (2+j*.035,1.56,2.25),
           (1.94+j*.025,1.57,1.91),
           (2.13+j*.028,1.64,1.58)]
    curtain.include('gathered sweeping fold '+str(j),
                    sweep_tube(points=pts,radius=.052,
                               color=(.31+j*.017,.30+j*.017,.28+j*.016)))
scene.include('curtain',curtain)

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bs = nodes.get('Principled BSDF')
    if not bs:
        continue
    base = tuple(bs.inputs['Base Color'].default_value[:3])
    bs.inputs['Roughness'].default_value = .72
    if max(base)-min(base)>.15 and base[0]>.4:
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 125
        tex.inputs['Detail'].default_value = 2
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .16
        bump.inputs['Distance'].default_value = .018
        mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif min(base)>.75:
        bs.inputs['Roughness'].default_value = .22
    elif max(base)<.09:
        bs.inputs['Roughness'].default_value = .44
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 7
        tex.inputs['Detail'].default_value = 2
        mapping = nodes.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (1,32,7)
        coord = nodes.new('ShaderNodeTexCoord')
        mat.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0])
        mat.node_tree.links.new(mapping.outputs[0],tex.inputs['Vector'])
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .15
        bump.inputs['Distance'].default_value = .013
        mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True
        if len(obj.data.polygons)==6:
            bevel = obj.modifiers.new('small edge softness','BEVEL')
            bevel.width = .008
            bevel.segments = 2
            obj.modifiers.new('weighted corner normals','WEIGHTED_NORMAL')

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value = (.76,.79,.82,1)
background.inputs['Strength'].default_value = .30

set_view((-.12,-7.5,2.95),(.12,.45,1.02),lens=47,sensor=36)
area_emitter((3.4,-.05,4.3),power=650,size=3.3,target=(0,.5,.65),color=(1,.93,.82))
area_emitter((-3,-2,3.1),power=110,size=4,target=(0,1,1),color=(.87,.92,1))
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
