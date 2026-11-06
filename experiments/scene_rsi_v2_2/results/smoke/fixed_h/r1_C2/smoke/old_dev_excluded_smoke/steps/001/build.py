from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory, normalized image bounds:
# Wall (.00,.00)-(.83,.44), warm off-white; floor (.00,.85)-(1,1).
# Sofa (.02,.28)-(.97,.96): ochre upholstery, two broad back cushions,
# two seat cushions, chunky arms, low front apron. Lower right is table-occluded.
# Loose pillow (.12,.31)-(.32,.53), pale golden, leaning against left back.
# Coffee table (.32,.60)-(1,1): dark rectangular top, apron and square legs;
# right edge and lower legs continue beyond frame.
# Two cups/saucers at (.46,.55)-(.57,.68) and (.71,.55)-(.84,.69);
# white cups with open rims and outward handles, on pale layered napkins.
# Plant (.56,.33)-(.74,.65): dark tapered pot, branching green foliage,
# pale blue-gray rounded flower heads with irregular silhouettes and gaps.
# Curtain (.80,0)-(1,.43): charcoal taupe folds, gathered on the right.
# Hidden sofa construction, curtain attachment and table's far legs uncertain.
#
# Named assets below retain semantic child parts.
# Estimated expanded geometry: 8 fillet boxes ~208 primitives, ~28 boxes/rods,
# cup booleans and handles ~40, foliage ~100, flower clusters ~91,
# curtain ~22: approximately 490 primitives. No per-petal microgeometry.

random.seed(12)
scene = Scene('Warm living room')
ochre = (.68,.355,.105)
seatgold = (.74,.405,.145)
backgold = (.80,.463,.19)
pillowgold = (.89,.63,.31)
wood = (.055,.036,.025)
white = (.88,.90,.87)

architecture = Asset('architecture')
architecture.include('wall', box((15,.13,7), center=(0,2.05,3.0), color=(.76,.75,.71)))
architecture.include('carpet', box((15,15,.10), center=(0,0,-.065), color=(.29,.275,.26)))
scene.include('architecture', architecture)

sofa = Asset('ochre sofa')
sofa.include('lower upholstered apron', fillet_box((4.42,1.50,.48), .07,
             center=(0,.98,.30), color=ochre))
sofa.include('back foundation', fillet_box((4.04,.34,1.36), .08,
             center=(0,1.59,.96), color=ochre))
for i,x in enumerate((-1.0,1.0)):
    sofa.include('back cushion '+str(i),
        fillet_box((1.98,.34,1.00), .095,
                   center=(x,1.345,1.20), color=backgold))
    sofa.include('seat cushion '+str(i),
        fillet_box((1.96,1.13,.29), .10,
                   center=(x,.79,.66), color=seatgold))
for i,x in enumerate((-2.10,2.10)):
    sofa.include('rounded arm '+str(i),
        fillet_box((.43,1.48,1.06), .105,
                   center=(x,.94,.76), color=ochre))
# Narrow shadow seams preserve the separate cushion silhouettes.
sofa.include('seat front seam', rod(.011,start=(-1.91,.205,.555),
                                    end=(1.91,.205,.555),color=(.46,.25,.075)))
scene.include('sofa',sofa)

pillow = Asset('loose left pillow')
p = fillet_box((.79,.23,.76), .105, center=(-1.36,1.035,1.205), color=pillowgold)
p.turn('y',-12)
p.turn('x',-12)
pillow.include('soft cushion',p)
# Soft piping around the visible square perimeter.
corners=[(-.38,-.135,-.35),(.38,-.135,-.35),(.38,-.135,.35),(-.38,-.135,.35),(-.38,-.135,-.35)]
pipe=sweep_tube(points=[(x-1.36,y+1.035,z+1.205) for x,y,z in corners],
                radius=.008,color=(.74,.49,.22))
pipe.turn('y',-12,pivot=(-1.36,1.035,1.205))
pipe.turn('x',-12,pivot=(-1.36,1.035,1.205))
pillow.include('perimeter piping',pipe)
scene.include('left pillow',pillow)

table = Asset('dark coffee table')
table.include('solid rectangular top',box((3.10,1.24,.12),center=(.72,-.86,.715),color=wood))
table.include('front apron',box((3.0,.085,.20),center=(.72,-1.405,.57),color=wood))
table.include('left apron',box((.085,1.13,.20),center=(-.735,-.86,.57),color=wood))
for i,x in enumerate((-.69,2.13)):
    for j,y in enumerate((-1.36,-.36)):
        table.include('square leg %s %s'%(i,j),
                      box((.125,.125,.66),center=(x,y,.325),color=wood))
scene.include('coffee table',table)

# Napkins are slightly rotated pale squares, with a second visible folded layer.
for i,(x,y) in enumerate(((.13,-.91),(1.36,-.91))):
    setting=Asset('tea setting '+str(i))
    nap=box((.69,.44,.012),center=(x,y,.783),color=(.56,.65,.60))
    nap.turn('z',-9 if i==0 else 8)
    setting.include('sage napkin',nap)
    paper=box((.60,.36,.009),center=(x+.02,y-.025,.795),color=(.84,.84,.75))
    paper.turn('z',7 if i==0 else -7)
    setting.include('cream folded napkin',paper)
    setting.include('saucer',rod(.205,length=.018,center=(x,y,.811),color=white))
    setting.include('saucer inner disk',rod(.146,length=.009,center=(x,y,.824),color=(.80,.84,.82)))
    # Hollow ceramic vessel, open top. Slightly tapered in Blender below.
    outer=rod(.108,length=.245,center=(x,y,.958),color=white)
    inner=rod(.092,length=.25,center=(x,y,.982),color=white)
    setting.include('hollow cup',subtract(outer,inner))
    setting.include('tea surface',rod(.088,length=.004,center=(x,y,1.060),color=(.16,.105,.045)))
    side=-1 if i==0 else 1
    pts=[]
    for k in range(9):
        a=math.pi/2 + k*math.pi/8
        pts.append((x+side*(.103+.092*math.cos(a)), y, .967+.079*math.sin(a)))
    # Handle extends outward, using a nearly closed oval.
    pts=[(x+side*(.105+.079*math.sin(math.pi*k/8)), y,
          1.035-.155*k/8) for k in range(9)]
    setting.include('ceramic loop handle',sweep_tube(points=pts,radius=.012,color=white))
    scene.include('tea setting '+str(i),setting)

plant=Asset('flowering plant')
potx,poty=.77,-.68
# Pot cylinder profile is tapered after realization.
plant.include('dark tapered pot',rod(.178,length=.29,center=(potx,poty,.935),color=(.07,.075,.064)))
plant.include('pot rim',rod(.185,length=.026,center=(potx,poty,1.082),color=(.095,.10,.082)))
plant.include('dark soil',rod(.16,length=.008,center=(potx,poty,1.099),color=(.036,.028,.016)))
green=(.19,.30,.105)
leafcols=[(.23,.36,.13),(.29,.40,.16),(.35,.43,.19),(.16,.28,.095)]
# Explicit canopy parameters control occupied space and foliage gaps.
canopy_width=.73
for j in range(17):
    a=j*2.399
    reach=.18+.15*random.random()
    end=(potx+math.cos(a)*reach,poty+math.sin(a)*reach*.70,1.32+random.random()*.22)
    start=(potx+random.uniform(-.05,.05),poty+random.uniform(-.04,.04),1.07)
    plant.include('leaf branch '+str(j),rod(.008,start=start,end=end,color=green))
    for k in range(4):
        t=.40+.17*k
        base=Vector(start).lerp(Vector(end),t)
        angle=a+(-1 if k%2 else 1)*.95
        leaf=ball(1,center=(base.x+.043*math.cos(angle),
                                  base.y+.043*math.sin(angle),base.z+.012),
                  color=leafcols[(j+k)%4])
        leaf.resize((.077,.023,.012))
        leaf.turn('z',math.degrees(angle))
        leaf.turn('y',-18)
        plant.include('leaf %s %s'%(j,k),leaf)

heads=[(-.27,.015,1.72,.105),(-.12,.05,1.86,.09),
       (.08,.055,1.75,.10),(.26,.04,1.69,.115),
       (.17,-.08,1.59,.086),(-.23,-.06,1.57,.085),
       (.02,-.09,1.66,.08)]
for j,(dx,dy,z,r) in enumerate(heads):
    end=(potx+dx,poty+dy,z)
    plant.include('flower stem '+str(j),rod(.007,start=(potx,poty,1.11),end=end,color=green))
    for k in range(13):
        # A compact irregular cluster, represented at the visible floret scale.
        a=k*2.4
        zz=1-2*(k+.5)/13
        rr=math.sqrt(1-zz*zz)
        c=(end[0]+r*.72*rr*math.cos(a),
           end[1]+r*.72*rr*math.sin(a),
           end[2]+r*.65*zz)
        floret=ball(r*.32,center=c,color=[(.57,.64,.69),(.69,.74,.75),(.47,.55,.62)][k%3])
        plant.include('flower cluster %s floret %s'%(j,k),floret)
scene.include('flowering plant',plant)
scene.bind('flowering plant','coffee table',source_anchor='bottom',target_anchor='top',
           offset=(.05,.18,.0))

# Curtain forms: tall irregular vertical pleats and an inward gathered drape.
curtain=Asset('right gathered curtain')
for j in range(12):
    x=1.78+j*.086
    y=1.78+.075*math.sin(j*1.7)
    fold=rod(.077,length=3.75,center=(x,y,2.34),
             color=[(.20,.195,.18),(.30,.29,.265),(.39,.38,.35)][j%3])
    fold.resize((.75,1,1))
    curtain.include('vertical pleat '+str(j),fold)
for j in range(6):
    pts=[(2.20+j*.05,1.65,3.55),
         (2.16+j*.043,1.59,2.92),
         (2.00+j*.035,1.56,2.25),
         (1.94+j*.025,1.57,1.91),
         (2.13+j*.028,1.64,1.58)]
    curtain.include('gathered sweeping fold '+str(j),
                    sweep_tube(points=pts,radius=.052,
                               color=(.31+j*.017,.30+j*.017,.28+j*.016)))
scene.include('curtain',curtain)

realize(scene)

# Shared procedural surface finishes give fabric and wood restrained variation.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bs=nodes.get('Principled BSDF')
    if not bs:
        continue
    base=tuple(bs.inputs['Base Color'].default_value[:3])
    bs.inputs['Roughness'].default_value=.72
    if max(base)-min(base)>.15 and base[0]>.4:
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=125
        tex.inputs['Detail'].default_value=2
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.16
        bump.inputs['Distance'].default_value=.018
        mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif min(base)>.75:
        bs.inputs['Roughness'].default_value=.22
    elif max(base)<.09:
        bs.inputs['Roughness'].default_value=.44
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=7
        tex.inputs['Detail'].default_value=2
        mapping=nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(1,32,7)
        coord=nodes.new('ShaderNodeTexCoord')
        mat.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0])
        mat.node_tree.links.new(mapping.outputs[0],tex.inputs['Vector'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.15
        bump.inputs['Distance'].default_value=.013
        mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

# Soften edges of inexpensive box geometry.
for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        for poly in obj.data.polygons:
            poly.use_smooth=True
        if len(obj.data.polygons)==6:
            bevel=obj.modifiers.new('small edge softness','BEVEL')
            bevel.width=.008
            bevel.segments=2
            norm=obj.modifiers.new('weighted corner normals','WEIGHTED_NORMAL')

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
background.inputs['Color'].default_value=(.76,.79,.82,1)
background.inputs['Strength'].default_value=.30

set_view((-.12,-7.5,2.95),(.12,.45,1.02),lens=47,sensor=36)
area_emitter((3.4,-.05,4.3),power=650,size=3.3,target=(0,.5,.65),color=(1,.93,.82))
area_emitter((-3,-2.0,3.1),power=110,size=4,target=(0,1,1),color=(.87,.92,1))
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
