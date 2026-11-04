from sceneact import *
import bpy

# Reference/render-2 visual estimates:
# island right edge .90/.90, countertop right .57/.56, base right .70/.73.
# Reference hood occupies x .42-.73; render-2 hood is largely hidden.
# Largest supported error: LeftWall crosses the camera's sightlines and
# fills x 0-.70 with a pale foreground occluder absent from the photograph.
# Correction family: local architecture placement. Move this wall outside
# the viewing corridor; preserve camera, island geometry and rear cabinetry.
# Preserve the matching right island silhouette and dark ceiling region.
# Foreground timber should span about x .17-.31; position is uncertain after
# camera revision, so relocate laterally to maintain that foreground framing.
# Assemblies: architecture/tiles/ceiling, timber columns, solid drawer island,
# suspended solid hood, fitted rear cabinets/niche, oven tower and small red pot.
# All broad panels are filled meshes; backsplash niche is a shallow recess.

CAM_POS = (-5.62, -5.72, 2.13)
CAM_TARGET = (0.0, 0.0, 1.47)
LENS = 48
ISLAND_LENGTH, ISLAND_DEPTH, ISLAND_HEIGHT = 2.30, 1.10, 1.02
HOOD_BOTTOM, HOOD_TOP = 2.05, 3.72
HOOD_X, HOOD_Y = .55, .20
LEFT_WALL_X = -6.5
POST_POSITION = (-2.28, -1.00, 2.0)
KEY_POWER, FILL_POWER, NICHE_POWER = 780, 340, 32

scene = Scene('Kitchen')
ivory = (.68, .69, .66)
counter = (.80, .81, .76)
black = (.027, .033, .031)
wood = (.36, .23, .13)

def block(parent, name, size, center, color):
    node = box(size=size, center=center, color=color)
    node.name = name
    parent.include(name, node)
    return node

architecture = Asset('Architecture')
block(architecture, 'Subfloor', (16,12,.12), (0,0,-.085), (.38,.39,.37))
for i in range(-5,5):
    for j in range(-4,5):
        c = .012*((i+j)%3)
        block(architecture, 'FloorTile_%d_%d'%(i,j),
              (1.19,1.19,.035), (i*1.20,j*1.20,-.012),
              (.57+c,.575+c,.55+c))
block(architecture, 'RearWall', (14,.16,3.85), (0,2.37,1.90), (.34,.36,.33))
block(architecture, 'LeftWall', (.16,7,3.85), (LEFT_WALL_X,.2,1.90), (.46,.47,.43))
block(architecture, 'Ceiling', (16,12,.15), (0,0,3.88), (.025,.031,.028))
for i,x in enumerate([-4,-2.2,-.65,1.05,2.7]):
    block(architecture, 'CeilingBeam_%d'%i, (.17,10,.30),
          (x,0,3.67), (.035,.045,.041))
for i in range(10):
    block(architecture, 'CeilingRib_%d'%i, (12,.034,.07),
          (0,-2.7+i*.56,3.77), (.065,.074,.067))
block(architecture, 'CrossGirder', (12,.24,.35), (0,1.0,3.56), (.055,.067,.063))
scene.include('Architecture', architecture)

columns = Asset('TimberColumns')
block(columns, 'ForegroundTimber', (.33,.34,4.8), POST_POSITION, wood)
block(columns, 'RearTimber', (.19,.22,3.6), (2.65,1.5,1.8), (.43,.29,.17))
scene.include('TimberColumns', columns)

island = Asset('Island')
cx,cy = .38,-.30
front = cy-ISLAND_DEPTH/2
block(island, 'RecessedPlinth', (2.16,.94,.13), (cx,cy,.105), (.20,.22,.21))
block(island, 'Carcass', (2.30,1.08,.84), (cx,cy,.57), ivory)
block(island, 'LeftEndPanel', (.045,1.10,.95), (cx-1.15,cy,.555), (.61,.63,.61))
block(island, 'RightEndPanel', (.035,1.10,.95), (cx+1.15,cy,.555), ivory)
for i,(z,h) in enumerate([(.277,.275),(.565,.275),(.850,.265)]):
    block(island, 'DrawerShadow_%d'%i, (2.255,.018,h+.012),
          (cx,front-.009,z), (.23,.25,.24))
    block(island, 'DrawerFront_%d'%i, (2.25,.037,h),
          (cx,front-.028,z), (.69,.71,.68))
block(island, 'Countertop', (2.34,1.14,.045), (cx,cy,1.035), counter)
sx,sy = .62,-.02
block(island, 'SinkRim', (.64,.41,.009), (sx,sy,1.062), (.68,.70,.66))
block(island, 'SinkBasin', (.575,.35,.011), (sx,sy,1.068), (.43,.47,.45))
block(island, 'SinkInner', (.51,.29,.013), (sx,sy,1.075), (.56,.59,.56))
for n,size,pos in [
    ('SinkFrontLip',(.62,.018,.018),(sx,sy-.195,1.074)),
    ('SinkRearLip',(.62,.018,.018),(sx,sy+.195,1.074)),
    ('SinkLeftLip',(.018,.39,.018),(sx-.31,sy,1.074)),
    ('SinkRightLip',(.018,.39,.018),(sx+.31,sy,1.074))]:
    block(island,n,size,pos,(.76,.78,.74))
faucet = Part('Faucet')
faucet.include('CurvedSpout', sweep_tube(points=[
    (sx+.20,sy+.27,1.06),(sx+.20,sy+.27,1.27),
    (sx+.18,sy+.25,1.31),(sx+.12,sy+.18,1.32),
    (sx+.07,sy+.10,1.30),(sx+.07,sy+.07,1.25)],
    radius=.012,color=(.65,.69,.68)))
faucet.include('TapLever', rod(.008,start=(sx+.25,sy+.27,1.09),
                            end=(sx+.28,sy+.27,1.17),color=(.65,.69,.68)))
island.include('Faucet',faucet)
scene.include('Island',island)

hood = Asset('SuspendedHood')
block(hood, 'HoodBody', (1.00,.94,HOOD_TOP-HOOD_BOTTOM),
      (HOOD_X,HOOD_Y,(HOOD_TOP+HOOD_BOTTOM)/2), (.73,.73,.67))
block(hood, 'BottomPlate', (.97,.91,.025),
      (HOOD_X,HOOD_Y,HOOD_BOTTOM), (.54,.56,.52))
block(hood, 'GreaseFilter', (.68,.56,.008),
      (HOOD_X,HOOD_Y,HOOD_BOTTOM-.017), (.37,.39,.36))
for i in range(2):
    block(hood, 'UnderLamp_%d'%i, (.055,.07,.009),
          (HOOD_X-.31+i*.60,HOOD_Y-.32,HOOD_BOTTOM-.021), (.85,.86,.75))
scene.include('SuspendedHood',hood)

kitchen = Asset('RearCabinetry')
block(kitchen, 'LeftTallCabinet', (.84,.73,2.66), (-1.87,1.46,1.33), black)
block(kitchen, 'LeftTallDoor', (.81,.025,2.59), (-1.87,1.08,1.34), (.039,.046,.043))
block(kitchen, 'TallUpperSeam', (.80,.012,.009), (-1.87,1.061,2.31), (.019,.023,.021))
block(kitchen, 'BackBase', (3.10,.65,.94), (-.08,1.58,.47), (.025,.030,.027))
block(kitchen, 'BackCounter', (3.12,.70,.045), (-.08,1.53,.965), (.16,.18,.16))
for i in range(5):
    block(kitchen, 'BaseDoor_%d'%i, (.60,.025,.80),
          (-1.30+i*.62,1.241,.47), (.036,.043,.039))
block(kitchen, 'Backsplash', (3.15,.055,.86), (-.06,1.92,1.40), (.069,.080,.069))
for i in range(5):
    block(kitchen, 'BacksplashJoint_%d'%i, (.008,.006,.83),
          (-1.5+i*.63,1.888,1.40), (.036,.045,.039))
block(kitchen, 'UpperCabinet', (3.12,.52,.61), (-.08,1.77,2.13), (.055,.064,.057))
block(kitchen, 'UpperSoffit', (3.13,.55,.035), (-.08,1.75,1.81), (.022,.028,.023))
block(kitchen, 'WarmRecessPanel', (2.03,.018,.37), (-.45,1.865,1.23), (.31,.26,.23))
block(kitchen, 'LightStrip', (2.04,.025,.013), (-.45,1.80,1.425), (.95,.79,.57))
block(kitchen, 'CoffeeMachineFoot', (.20,.16,.025), (0,1.60,.99), (.018,.02,.018))
kitchen.include('RedCoffeeMachine',ball(.091,center=(0,1.64,1.105),color=(.68,.008,.019)))
block(kitchen, 'CoffeeMachineFace', (.12,.025,.13), (0,1.554,1.095), (.025,.029,.027))
scene.include('RearCabinetry',kitchen)

ovens = Asset('OvenTower')
block(ovens, 'TowerBody', (.80,.77,2.51), (1.91,1.55,1.255), (.034,.042,.038))
block(ovens, 'RightSurround', (.19,.85,2.75), (2.40,1.56,1.375), (.046,.054,.048))
block(ovens, 'TowerUpperDoor', (.75,.025,.65), (1.91,1.15,2.15), (.032,.039,.035))
for i,z in enumerate([1.04,1.55]):
    block(ovens, 'OvenFrame_%d'%i, (.66,.045,.455), (1.91,1.135,z), (.25,.28,.27))
    block(ovens, 'OvenGlass_%d'%i, (.58,.018,.315), (1.91,1.105,z-.025), (.023,.043,.048))
    block(ovens, 'ControlBar_%d'%i, (.64,.025,.065), (1.91,1.093,z+.173), (.34,.36,.34))
    block(ovens, 'OvenHandle_%d'%i, (.52,.045,.022), (1.91,1.066,z+.10), (.52,.55,.53))
block(ovens, 'LowerDoor', (.75,.035,.73), (1.91,1.14,.38), (.04,.047,.042))
block(ovens, 'RightWallReturn', (.55,.17,3.0), (2.65,2.02,1.5), (.39,.42,.39))
scene.include('OvenTower',ovens)

# API audit: positive dimensions/radii, distinct tube points, unique child
# names, no Boolean operations, semantic assemblies retained.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.50,.55,.59,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .23

def descendants(group):
    ob = bpy.data.objects.get(group)
    return [q for q in ob.children_recursive if q.type == 'MESH'] if ob else []

woodmat = bpy.data.materials.new('Natural vertical oak')
woodmat.use_nodes = True
nt = woodmat.node_tree
bs = nt.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value = .53
tex = nt.nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value = 3.8
tex.inputs['Detail'].default_value = 3.5
coord = nt.nodes.new('ShaderNodeTexCoord')
mapping = nt.nodes.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (9,9,.35)
nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
nt.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .18
ramp.color_ramp.elements[0].color = (.12,.065,.028,1)
ramp.color_ramp.elements[1].position = .82
ramp.color_ramp.elements[1].color = (.53,.34,.18,1)
nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
bump = nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .16
bump.inputs['Distance'].default_value = .025
nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs[0],bs.inputs['Normal'])
for ob in descendants('TimberColumns'):
    ob.data.materials.clear()
    ob.data.materials.append(woodmat)
for mat in bpy.data.materials:
    if mat.use_nodes and mat != woodmat:
        shader = mat.node_tree.nodes.get('Principled BSDF')
        if shader:
            shader.inputs['Roughness'].default_value = .44
for ob in descendants('Faucet'):
    for slot in ob.material_slots:
        if slot.material:
            slot.material = slot.material.copy()
            p = slot.material.node_tree.nodes.get('Principled BSDF')
            if p:
                p.inputs['Metallic'].default_value = .85
                p.inputs['Roughness'].default_value = .19

set_view(CAM_POS,CAM_TARGET,lens=LENS,sensor=36)
sc.camera.data.sensor_fit = 'VERTICAL'
sc.camera.data.sensor_height = 32
area_emitter((-3,-3.8,3.25),power=KEY_POWER,size=4,
             target=(.1,0,.8),color=(1,.94,.83))
area_emitter((1.3,-.8,3.45),power=FILL_POWER,size=3,
             target=(.5,-.2,.5),color=(.88,.94,1))
area_emitter((-.6,1.49,1.45),power=NICHE_POWER,size=1.7,
             target=(-.6,1.84,1.12),color=(1,.70,.48))
sc.view_settings.view_transform = 'AgX'
