from sceneact import *
import bpy
import math

COUNTER_Z = .86
CABINET_BOTTOM = 1.62
CABINET_WIDTH = .82
CABINET_DEPTH = .75
CABINET_HEIGHT = 1.47
CAMERA_POSITION = (-1.55, -2.45, 1.99)
CAMERA_TARGET = (-.07, .12, 1.66)
CAMERA_LENS = 50

scene = Scene("Kitchen corner")
cream = (.61, .54, .41)
cabinet_color = (.72, .65, .51)
white = (.82, .80, .70)
chrome = (.48, .47, .40)

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
    box((2.8,1.75,.065),center=(-.25,-.055,COUNTER_Z-.0325),
        color=(.30,.28,.22)))
architecture.include("backsplash",
    box((2.8,.035,.17),center=(-.25,.72,COUNTER_Z+.085),
        color=(.30,.28,.22)))
scene.include("Architecture",architecture)

window = Asset("Window and blinds")
window.include("glass",
    box((.96,.025,2.35),center=(-.90,.835,1.925),
        color=(.59,.74,.77)))
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
        box((.016,.008,2.35),center=(x,.581,1.94),
            color=(.75,.74,.64)))
for i,x in enumerate((-.66,-.63)):
    window.include(f"pull_cord_{i}",
        rod(.002,start=(x,.575,2.60),end=(x,.575,1.97),color=white))
    window.include(f"cord_weight_{i}",
        rod(.009,length=.047,center=(x,.575,1.95),color=white))
scene.include("Window and blinds",window)

cabinet = Asset("Upper cabinet")
cabinet.include("body",
    box((CABINET_WIDTH,CABINET_DEPTH,CABINET_HEIGHT),
        center=(.32,.35,CABINET_BOTTOM+CABINET_HEIGHT/2),
        color=cabinet_color))
cabinet.include("door",
    box((.75,.035,1.37),center=(.32,-.043,2.355),
        color=(.70,.63,.49)))
for i,x in enumerate((-.025,.665)):
    cabinet.include(f"stile_{i}",
        box((.038,.024,1.33),center=(x,-.071,2.355),
            color=(.76,.69,.55)))
for i,z in enumerate((1.71,3.00)):
    cabinet.include(f"rail_{i}",
        box((.73,.024,.043),center=(.32,-.071,z),
            color=(.76,.69,.55)))
cabinet.include("knob_stem",
    rod(.012,start=(.65,-.084,1.87),end=(.65,-.12,1.87),color=chrome))
cabinet.include("knob",
    ball(.023,center=(.65,-.135,1.87),color=chrome))
scene.include("Upper cabinet",cabinet)

paper = Asset("Paper towel holder")
PAPER_X, PAPER_Y = .11,-.24
paper.include("shaft",
    rod(.016,start=(PAPER_X,PAPER_Y,1.88),
        end=(PAPER_X,PAPER_Y,2.57),color=chrome))
paper.include("top_finial",
    ball(.033,center=(PAPER_X,PAPER_Y,2.565),color=chrome))
paper.include("roll",
    rod(.145,length=.625,center=(PAPER_X,PAPER_Y,2.225),
        color=(.88,.84,.72)))
paper.include("lower_cap",
    rod(.045,length=.024,center=(PAPER_X,PAPER_Y,1.903),color=chrome))
paper.include("bracket",
    rod(.020,start=(PAPER_X,-.06,1.91),
        end=(PAPER_X,PAPER_Y,1.91),color=chrome))
scene.include("Paper towel holder",paper)

ring = Asset("Towel ring")
ring.include("mount",
    rod(.052,start=(-.092,.40,1.96),
        end=(-.145,.40,1.96),color=chrome))
ring.include("arm",
    rod(.014,start=(-.145,.40,1.96),
        end=(-.17,.40,1.985),color=chrome))
ring_points = [
    (-.17,.40+.139*math.cos(2*math.pi*i/90),
     1.805+.185*math.sin(2*math.pi*i/90))
    for i in range(91)
]
ring.include("ring",
    sweep_tube(points=ring_points,radius=.008,color=chrome))
scene.include("Towel ring",ring)

sink = Asset("Sink")
sink.include("rim",
    fillet_box((.70,.62,.025),radius=.012,
               center=(-.73,-.48,.872),color=(.48,.47,.39)))
sink.include("basin",
    fillet_box((.61,.53,.035),radius=.017,
               center=(-.73,-.48,.883),color=(.025,.036,.028)))
sink.include("faucet_base",
    rod(.042,length=.03,center=(-.75,-.13,.891),color=chrome))
sink.include("faucet",
    sweep_tube(points=[
        (-.75,-.13,.90),(-.75,-.13,1.12),(-.75,-.14,1.20),
        (-.75,-.19,1.24),(-.75,-.26,1.23),(-.75,-.29,1.18)
    ],radius=.013,color=chrome))
for i,x in enumerate((-.89,-.60)):
    sink.include(f"tap_{i}",
        rod(.022,length=.035,center=(x,-.13,.90),color=chrome))
    sink.include(f"lever_{i}",
        rod(.009,start=(x,-.13,.92),end=(x+.045,-.10,.98),color=chrome))
scene.include("Sink",sink)

small = Asset("Counter utensils")
small.include("canister",
    rod(.067,length=.235,center=(-.12,.27,.987),color=(.31,.34,.17)))
small.include("canister_lid",
    rod(.072,length=.018,center=(-.12,.27,1.113),color=chrome))
small.include("black_blender_base",
    fillet_box((.17,.18,.22),radius=.03,
               center=(.145,.29,.97),color=(.025,.032,.025)))
cup = rod(.055,length=.245,center=(.145,.29,1.205),
          color=(.45,.48,.43),opacity=.28)
cup.turn(axis="+y",degrees=-10)
small.include("blender_cup",cup)
small.include("little_glass",
    rod(.046,length=.11,center=(-.43,-.065,.925),
        color=(.22,.22,.15),opacity=.8))
scene.include("Counter utensils",small)

pitcher = Asset("Blue water filter pitcher")
pitcher.include("body",
    fillet_box((.30,.225,.365),radius=.065,
               center=(.62,.19,1.055),color=(.025,.065,.15),opacity=.88))
pitcher.include("inner_filter",
    rod(.069,length=.24,center=(.60,.19,1.13),color=(.16,.19,.23)))
lid = fillet_box((.33,.25,.045),radius=.02,
                 center=(.62,.19,1.263),color=(.34,.35,.31))
lid.turn(axis="+y",degrees=-8)
pitcher.include("lid",lid)
pitcher.include("handle",
    sweep_tube(points=[
        (.755,.20,1.24),(.83,.20,1.20),(.87,.20,1.09),
        (.86,.20,.98),(.82,.20,.91),(.75,.20,.91)
    ],radius=.019,color=(.50,.53,.49),opacity=.6))
pitcher.include("spout",
    box((.07,.13,.035),center=(.45,.17,1.25),color=(.34,.35,.31)))
scene.include("Blue water filter pitcher",pitcher)

JUG_X,JUG_Y = .16,-.19
jug = Asset("Milk jug")
jug.include("cap",
    rod(.030,length=.035,center=(JUG_X,JUG_Y,1.299),
        color=(.78,.78,.69)))
jug.include("neck",
    rod(.028,length=.047,center=(JUG_X,JUG_Y,1.267),
        color=(.68,.70,.63),opacity=.8))
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

jug_material = make_material("Cloudy plastic",(.58,.61,.55),.42)
jug_shader = jug_material.node_tree.nodes.get("Principled BSDF")
transmission = jug_shader.inputs.get("Transmission Weight")
if transmission is not None:
    transmission.default_value = .08
jug_shader.inputs["IOR"].default_value = 1.43

jug_rings = [
    (.866,.112,.086),(.878,.140,.105),(.920,.147,.109),
    (1.075,.141,.105),(1.160,.115,.090),
    (1.225,.064,.053),(1.250,.029,.029)
]
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

towel_material = make_material("Warm white terry cloth",(.79,.75,.64),.95)
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
    z = 1.69-.64*t
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

def mesh_descendants(marker_name):
    marker = bpy.data.objects.get(marker_name)
    if marker is None:
        return []
    result,pending = [],[marker]
    while pending:
        obj = pending.pop()
        if obj.type == "MESH":
            result.append(obj)
        pending.extend(list(obj.children))
    return result

def customize_asset_materials(marker_name,callback):
    for obj in mesh_descendants(marker_name):
        for slot in obj.material_slots:
            if slot.material is None:
                continue
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            shader = mat.node_tree.nodes.get("Principled BSDF")
            if shader is not None:
                callback(mat,shader)

def architecture_finish(mat,shader):
    color = shader.inputs["Base Color"].default_value
    if abs(color[0]-.30)<.025 and abs(color[1]-.28)<.025:
        nodes,links = mat.node_tree.nodes,mat.node_tree.links
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 240
        noise.inputs["Detail"].default_value = 2
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .30
        ramp.color_ramp.elements[0].color = (.065,.055,.038,1)
        ramp.color_ramp.elements[1].position = .70
        ramp.color_ramp.elements[1].color = (.43,.38,.28,1)
        links.new(noise.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs[0],shader.inputs["Base Color"])
        shader.inputs["Roughness"].default_value = .64

def metal_finish(mat,shader):
    color = shader.inputs["Base Color"].default_value
    if abs(color[0]-.48)<.02 and abs(color[1]-.47)<.02:
        shader.inputs["Metallic"].default_value = .78
        shader.inputs["Roughness"].default_value = .25

def paper_finish(mat,shader):
    color = shader.inputs["Base Color"].default_value
    metal_finish(mat,shader)
    if abs(color[0]-.88)<.02 and abs(color[1]-.84)<.02:
        nodes,links = mat.node_tree.nodes,mat.node_tree.links
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 145
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .13
        bump.inputs["Distance"].default_value = .003
        links.new(noise.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],shader.inputs["Normal"])
        shader.inputs["Roughness"].default_value = .9

customize_asset_materials("Architecture",architecture_finish)
for name in ("Sink","Towel ring","Upper cabinet","Counter utensils"):
    customize_asset_materials(name,metal_finish)
customize_asset_materials("Paper towel holder",paper_finish)

def window_finish(mat,shader):
    color = shader.inputs["Base Color"].default_value
    if abs(color[0]-.59)<.02 and abs(color[1]-.74)<.02:
        emission = shader.inputs.get("Emission Color")
        if emission is not None:
            emission.default_value = (.61,.78,.83,1)
        strength = shader.inputs.get("Emission Strength")
        if strength is not None:
            strength.default_value = .45
customize_asset_materials("Window and blinds",window_finish)

label_material = make_material("Pencil label",(.25,.28,.24),.8)
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
area_emitter((-.95,.35,2.3),power=95,size=1.5,
             target=(.15,-.05,1.25),color=(.79,.88,1.0))
area_emitter((-.4,-1.8,2.9),power=65,size=2.1,
             target=(0,.2,1.4),color=(1.0,.82,.58))

blender_scene = bpy.context.scene
if blender_scene.world is None:
    blender_scene.world = bpy.data.worlds.new("World")
blender_scene.world.use_nodes = True
background = blender_scene.world.node_tree.nodes.get("Background")
if background is not None:
    background.inputs["Color"].default_value = (.64,.66,.63,1)
    background.inputs["Strength"].default_value = .20
blender_scene.view_settings.view_transform = "AgX"
blender_scene.view_settings.exposure = -.25
