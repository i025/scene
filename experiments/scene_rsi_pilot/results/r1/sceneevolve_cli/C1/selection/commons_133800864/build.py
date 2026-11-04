from sceneact import *
import bpy
import math

# Comparison with step 2:
# 1. Broad surfaces remain too pale: warm and darken the cabinet, wall and stone.
# 2. The sink and faucet sit too low: move the sink rearward and raise the faucet.
# 3. Countertop silhouettes need correction: move the jug left/back, enlarge the
#    pitcher slightly, and give the blender cup a visible transparent shell.
# Retain the camera and the cabinet's successful overall framing.

COUNTER_Z = .86
CABINET_BOTTOM = 1.62
CABINET_WIDTH = .82
CABINET_DEPTH = .75
CABINET_HEIGHT = 1.47
CAMERA_POSITION = (-1.55, -2.45, 1.99)
CAMERA_TARGET = (-.07, .12, 1.66)
CAMERA_LENS = 50

scene = Scene("Kitchen corner")
cream = (.53, .44, .31)
cabinet_color = (.62, .53, .38)
white = (.78, .77, .68)
chrome = (.48, .47, .40)
STONE = (.22, .19, .135)

architecture = Asset("Architecture")
architecture.include("wall_right",
    box((2.24,.09,3.3),center=(.70,.81,1.65),color=cream))
architecture.include("wall_left",
    box((.35,.09,3.3),center=(-1.555,.81,1.65),color=cream))
architecture.include("wall_below_window",
    box((.96,.09,.75),center=(-.90,.81,.375),color=cream))
architecture.include("wall_above_window",
    box((.96,.09,.20),center=(-.90,.81,3.20),color=cream))
architecture.include("counter",
    box((2.8,1.75,.065),center=(-.25,-.055,COUNTER_Z-.0325),color=STONE))
architecture.include("backsplash",
    box((2.8,.035,.17),center=(-.25,.72,COUNTER_Z+.085),color=STONE))
scene.include("Architecture",architecture)

window = Asset("Window and blinds")
window.include("glass",
    box((.96,.025,2.35),center=(-.90,.835,1.925),color=(.59,.74,.77)))
for i,x in enumerate((-1.38,-.42)):
    window.include(f"jamb_{i}",
        box((.055,.10,2.46),center=(x,.725,1.94),color=white))
window.include("sill",
    box((1.09,.20,.065),center=(-.90,.69,.75),color=white))
window.include("top_frame",
    box((1.09,.08,.055),center=(-.90,.725,3.13),color=white))
window.include("central_mullion",
    box((.033,.065,2.35),center=(-.94,.75,1.94),color=white))
window.include("horizontal_mullion",
    box((.96,.065,.035),center=(-.90,.75,1.83),color=white))
for i in range(31):
    slat = box((1.03,.082,.014),center=(-.90,.63,.79+i*.077),
               color=(.78,.79,.71))
    slat.turn(axis="+x",degrees=-12)
    window.include(f"slat_{i}",slat)
for i,x in enumerate((-1.24,-.89,-.49)):
    window.include(f"tape_{i}",
        box((.016,.008,2.35),center=(x,.581,1.94),color=(.75,.74,.64)))
for i,x in enumerate((-.66,-.63)):
    window.include(f"pull_cord_{i}",
        rod(.002,start=(x,.575,2.60),end=(x,.575,1.97),color=white))
    window.include(f"cord_weight_{i}",
        rod(.009,length=.047,center=(x,.575,1.95),color=white))
scene.include("Window and blinds",window)

cabinet = Asset("Upper cabinet")
cabinet.include("body",
    box((CABINET_WIDTH,CABINET_DEPTH,CABINET_HEIGHT),
        center=(.32,.35,CABINET_BOTTOM+CABINET_HEIGHT/2),color=cabinet_color))
cabinet.include("door",
    box((.75,.035,1.37),center=(.32,-.043,2.355),color=(.61,.51,.36)))
for i,x in enumerate((-.025,.665)):
    cabinet.include(f"stile_{i}",
        box((.038,.024,1.33),center=(x,-.071,2.355),color=(.67,.57,.42)))
for i,z in enumerate((1.71,3.00)):
    cabinet.include(f"rail_{i}",
        box((.73,.024,.043),center=(.32,-.071,z),color=(.67,.57,.42)))
cabinet.include("knob_stem",
    rod(.012,start=(.65,-.084,1.87),end=(.65,-.12,1.87),color=chrome))
cabinet.include("knob",ball(.023,center=(.65,-.135,1.87),color=chrome))
scene.include("Upper cabinet",cabinet)

paper = Asset("Paper towel holder")
PAPER_X, PAPER_Y = .11,-.24
PAPER_DROP = .045
paper.include("shaft",
    rod(.016,start=(PAPER_X,PAPER_Y,1.88-PAPER_DROP),
        end=(PAPER_X,PAPER_Y,2.57-PAPER_DROP),color=chrome))
paper.include("top_finial",
    ball(.033,center=(PAPER_X,PAPER_Y,2.565-PAPER_DROP),color=chrome))
paper.include("roll",
    rod(.145,length=.625,center=(PAPER_X,PAPER_Y,2.225-PAPER_DROP),
        color=(.84,.78,.65)))
paper.include("lower_cap",
    rod(.045,length=.024,center=(PAPER_X,PAPER_Y,1.903-PAPER_DROP),color=chrome))
paper.include("bracket",
    rod(.020,start=(PAPER_X,-.06,1.91-PAPER_DROP),
        end=(PAPER_X,PAPER_Y,1.91-PAPER_DROP),color=chrome))
scene.include("Paper towel holder",paper)

ring = Asset("Towel ring")
ring.include("mount",
    rod(.052,start=(-.092,.40,1.96),end=(-.145,.40,1.96),color=chrome))
ring.include("arm",
    rod(.014,start=(-.145,.40,1.96),end=(-.22,.31,1.985),color=chrome))
ring_points = [
    (-.22+.065*math.cos(2*math.pi*i/90),
     .31-.123*math.cos(2*math.pi*i/90),
     1.805+.185*math.sin(2*math.pi*i/90))
    for i in range(91)]
ring.include("ring",sweep_tube(points=ring_points,radius=.008,color=chrome))
scene.include("Towel ring",ring)

sink = Asset("Sink")
SINK_X,SINK_Y = -.86,-.20
sink.include("rim",
    fillet_box((.76,.66,.025),radius=.012,
               center=(SINK_X,SINK_Y,.872),color=(.48,.47,.39)))
sink.include("basin",
    fillet_box((.67,.57,.035),radius=.017,
               center=(SINK_X,SINK_Y,.883),color=(.018,.026,.019)))
FX,FY = -.85,.10
sink.include("faucet_base",
    rod(.040,length=.03,center=(FX,FY,.891),color=chrome))
sink.include("faucet",
    sweep_tube(points=[
        (FX,FY,.90),(FX,FY,1.28),(FX,FY,1.39),
        (FX,FY-.025,1.42),(FX,FY-.075,1.41),
        (FX,FY-.095,1.37)
    ],radius=.010,color=chrome))
for i,x in enumerate((FX-.14,FX+.15)):
    sink.include(f"tap_{i}",
        rod(.022,length=.035,center=(x,FY,.90),color=chrome))
    sink.include(f"lever_{i}",
        rod(.009,start=(x,FY,.92),end=(x+.045,FY+.03,.98),color=chrome))
scene.include("Sink",sink)

small = Asset("Counter utensils")
small.include("canister",
    rod(.067,length=.235,center=(-.12,.27,.987),color=(.25,.28,.12)))
small.include("canister_lid",
    rod(.072,length=.018,center=(-.12,.27,1.113),color=chrome))
small.include("black_blender_base",
    fillet_box((.17,.18,.22),radius=.03,
               center=(.145,.29,.97),color=(.018,.025,.018)))
# A hollow, open cup preserves the characteristic tall blender silhouette.
cup_outer = rod(.052,length=.245,center=(.125,.29,1.205),color=(.34,.41,.40))
cup_inner = rod(.047,length=.245,center=(.125,.29,1.215),color=(1,1,1))
cup = subtract(cup_outer,cup_inner)
cup.turn(axis="+y",degrees=-10)
small.include("blender_cup",cup)
small.include("cup_rim",
    sweep_tube(points=[
        (.104+.052*math.cos(2*math.pi*i/48),
         .29+.052*math.sin(2*math.pi*i/48),1.325)
        for i in range(49)],radius=.003,color=(.48,.49,.43)))
small.include("little_glass",
    rod(.046,length=.08,center=(-.43,-.065,.91),color=(.16,.15,.09)))
scene.include("Counter utensils",small)

pitcher = Asset("Blue water filter pitcher")
pitcher.include("body",
    fillet_box((.32,.245,.395),radius=.065,
               center=(.665,.19,1.065),color=(.018,.045,.115)))
pitcher.include("inner_filter",
    rod(.069,length=.24,center=(.64,.19,1.15),color=(.13,.16,.19)))
lid = fillet_box((.35,.27,.045),radius=.02,
                 center=(.665,.19,1.285),color=(.28,.29,.24))
lid.turn(axis="+y",degrees=-8)
pitcher.include("lid",lid)
pitcher.include("handle",
    sweep_tube(points=[
        (.805,.20,1.26),(.88,.20,1.22),(.92,.20,1.10),
        (.91,.20,.98),(.87,.20,.90),(.80,.20,.90)
    ],radius=.019,color=(.40,.43,.39),opacity=.72))
pitcher.include("spout",
    box((.07,.13,.035),center=(.485,.17,1.27),color=(.28,.29,.24)))
scene.include("Blue water filter pitcher",pitcher)

JUG_X,JUG_Y = .13,-.075
jug = Asset("Milk jug")
jug.include("cap",
    rod(.030,length=.035,center=(JUG_X,JUG_Y,1.299),color=(.72,.72,.62)))
jug.include("neck",
    rod(.028,length=.047,center=(JUG_X,JUG_Y,1.267),color=(.60,.63,.55)))
scene.include("Milk jug",jug)

realize(scene)

def make_material(name,color,roughness=.5,metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color,1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat

def make_mesh(name,vertices,faces,material,parent_name):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj = bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    parent = bpy.data.objects.get(parent_name)
    if parent is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj

# Customize existing materials by their explicit source colors.
for mat in list(bpy.data.materials):
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    if shader is None:
        continue
    color = shader.inputs["Base Color"].default_value
    if all(abs(color[i]-STONE[i])<.012 for i in range(3)):
        nodes,links = mat.node_tree.nodes,mat.node_tree.links
        coordinates = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 210
        noise.inputs["Detail"].default_value = 2
        links.new(coordinates.outputs["Object"],noise.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .27
        ramp.color_ramp.elements[0].color = (.035,.029,.019,1)
        ramp.color_ramp.elements[1].position = .73
        ramp.color_ramp.elements[1].color = (.32,.27,.18,1)
        links.new(noise.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs[0],shader.inputs["Base Color"])
        shader.inputs["Roughness"].default_value = .64
    if abs(color[0]-.48)<.012 and abs(color[1]-.47)<.012:
        shader.inputs["Metallic"].default_value = .80
        shader.inputs["Roughness"].default_value = .24
    if abs(color[0]-.34)<.012 and abs(color[1]-.41)<.012:
        shader.inputs["Base Color"].default_value = (.64,.70,.68,1)
        shader.inputs["Transmission Weight"].default_value = .82
        shader.inputs["Roughness"].default_value = .12
        shader.inputs["IOR"].default_value = 1.46
    if abs(color[0]-.59)<.012 and abs(color[1]-.74)<.012:
        shader.inputs["Emission Color"].default_value = (.61,.78,.83,1)
        shader.inputs["Emission Strength"].default_value = .45
    if abs(color[0]-.84)<.012 and abs(color[1]-.78)<.012:
        nodes,links = mat.node_tree.nodes,mat.node_tree.links
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 145
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .13
        bump.inputs["Distance"].default_value = .003
        links.new(noise.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],shader.inputs["Normal"])
        shader.inputs["Roughness"].default_value = .9

jug_material = make_material("Cloudy plastic",(.45,.49,.42),.46)
jug_shader = jug_material.node_tree.nodes.get("Principled BSDF")
jug_shader.inputs["Transmission Weight"].default_value = .10
jug_shader.inputs["IOR"].default_value = 1.43
jug_rings = [
    (.866,.112,.086),(.878,.140,.105),(.920,.147,.109),
    (1.075,.141,.105),(1.160,.115,.090),
    (1.225,.064,.053),(1.250,.029,.029)]
vertices,faces = [],[]
segments = 64
for z,rx,ry in jug_rings:
    for i in range(segments):
        a = 2*math.pi*i/segments
        c,s = math.cos(a),math.sin(a)
        vertices.append((
            JUG_X+rx*math.copysign(abs(c)**.72,c),
            JUG_Y+ry*math.copysign(abs(s)**.72,s),z))
for j in range(len(jug_rings)-1):
    for i in range(segments):
        nxt = (i+1)%segments
        faces.append((j*segments+i,j*segments+nxt,
                      (j+1)*segments+nxt,(j+1)*segments+i))
faces.append(tuple(range(segments-1,-1,-1)))
faces.append(tuple((len(jug_rings)-1)*segments+i for i in range(segments)))
shell = make_mesh("Rounded jug shell",vertices,faces,jug_material,"Milk jug")
for polygon in shell.data.polygons:
    polygon.use_smooth = True

towel_material = make_material("Warm white terry cloth",(.76,.70,.58),.95)
nodes = towel_material.node_tree.nodes
links = towel_material.node_tree.links
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 220
noise.inputs["Detail"].default_value = 2
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .20
bump.inputs["Distance"].default_value = .003
links.new(noise.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs["Normal"],nodes.get("Principled BSDF").inputs["Normal"])

vertices,faces = [],[]
nx,nz = 32,45
for j in range(nz):
    t = j/(nz-1)
    z = 1.69-.66*t
    width = .12+.045*t
    for i in range(nx):
        u = 2*i/(nx-1)-1
        vertices.append((
            -.23+width*u+.025*math.sin(t*4),
            .27-.052*math.cos(u*math.pi*3)-.055*t,
            z+.025*math.sin(u*4+1)*t**7))
for j in range(nz-1):
    for i in range(nx-1):
        a = j*nx+i
        faces.append((a,a+1,a+1+nx,a+nx))
cloth = make_mesh("Hanging folded towel",vertices,faces,towel_material,"Towel ring")
solidify = cloth.modifiers.new("Cloth thickness","SOLIDIFY")
solidify.thickness = .006
subdivision = cloth.modifiers.new("Soft folds","SUBSURF")
subdivision.levels = 1
subdivision.render_levels = 1
for polygon in cloth.data.polygons:
    polygon.use_smooth = True

label_material = make_material("Pencil label",(.20,.22,.18),.8)
label_curve = bpy.data.curves.new("Filter label","FONT")
label_curve.body = "FILTER"
label_curve.size = .031
label_curve.extrude = 0
label = bpy.data.objects.new("FILTER handwritten label",label_curve)
bpy.context.collection.objects.link(label)
label.location = (JUG_X-.075,JUG_Y-.111,.945)
label.rotation_euler = (math.pi/2,0,-.035)
label.data.materials.append(label_material)

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-.95,.35,2.3),power=85,size=1.5,
             target=(.15,-.05,1.25),color=(.83,.89,1.0))
area_emitter((-.4,-1.8,2.9),power=60,size=2.1,
             target=(0,.2,1.4),color=(1.0,.80,.54))

blender_scene = bpy.context.scene
if blender_scene.world is None:
    blender_scene.world = bpy.data.worlds.new("World")
blender_scene.world.use_nodes = True
background = blender_scene.world.node_tree.nodes.get("Background")
if background is not None:
    background.inputs["Color"].default_value = (.64,.63,.57,1)
    background.inputs["Strength"].default_value = .18
blender_scene.view_settings.view_transform = "AgX"
blender_scene.view_settings.exposure = -.35
