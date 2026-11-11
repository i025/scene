# Visual comparison, estimated in the interior visible on the phone screen:
# - The rendered far arcade is centered near (.50,.58); the reference is
#   brighter and has more open, layered arches around approximately (.40,.60).
# - The rendered large sphere spans about (.53,.38)-(.76,.78), while the
#   reference bubble is cropped by the right edge of the phone screen and spans
#   roughly (.68,.37)-(1.0,.95) in the interior view.
# - The rendered magenta sphere is near (.47,.58), close to the reference
#   position, but the reference has a darker shaded side and glossier edge.
# - The rendered railing appears almost vertical at x=.46 and the staircase
#   largely disappears. The reference railing crosses the lower foreground
#   diagonally, descending toward image right, with pale stair treads behind it.
# - The rendered ceiling has large gray gaps and pale flat panels. The reference
#   has continuous warm stone vault surfaces with dark ribs and graded shadows.
# - The rendered columns are broad and repetitive with little visible depth.
#   Reference piers are narrower and the arcades retain more dark gaps.
#
# Largest discrepancies by visible extent and contrast:
# 1. Missing continuous vault surfaces: correct the panel rotation and extend
#    the ceiling panels. This fills the gray upper areas with warm stone.
# 2. Staircase and railing orientation: orient the flight across the foreground.
#    The rail should run from lower left toward lower right, revealing stair
#    treads and red ironwork. This is a local geometry correction.
# 3. Bubble appearance and placement: move it right and closer, enlarge it
#    slightly, and assign the thin-film material by matching the mesh position.
#    Its right contour should be cropped; the magenta sphere remains behind it.
# 4. Narrow the side piers and brighten the far opening to preserve arcade gaps.
# Camera parameters are retained from the previous build because the bubble,
# railing, and missing roof errors are local. A small trial aim adjustment is
# still projected and restored below; computed projections are not silhouettes.
#
# Inventory / semantic assets:
# Vaults: ceiling, rib crossings, side walls, far opening and floor.
# Columns: clustered shafts, capitals, pointed arcades on both sides.
# Staircase & railing: stone treads, landing, handrails, posts and open ironwork.
# Chandelier: suspended stem, brass arms and warm bulbs.
# Spheres: magenta solid and larger thin-film bubble, partly overlapping hall.
# The unseen lower stair and far end are uncertain. Image anchors are visual
# estimates in the phone's interior view, not ground-truth calibration.
# Primitive estimate: vaults ~245 including tube expansions, columns ~240,
# stairs and rails ~95, chandelier ~19, spheres 2; total approximately 601.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, sweep_tube, realize, set_view, area_emitter

# Camera and major proportions are independent parameters.
CAM_POS = (0.15, -7.9, 3.05)
CAM_TARGET = (0.0, 4.5, 3.55)
CAM_LENS = 25.0
BAY = 3.0
BAYS = 5
SPRING = 4.1
VAULT_TOP = 6.65
PIER_X = 2.85
BUBBLE_CENTER = (2.35, -0.15, 2.86)
BUBBLE_RADIUS = 1.45
MAGENTA_CENTER = (-0.28, 1.0, 2.82)
MAGENTA_RADIUS = 0.46

stone = (0.67, 0.59, 0.47)
stone_light = (0.79, 0.73, 0.62)
stone_shadow = (0.37, 0.32, 0.26)
floor_color = (0.65, 0.59, 0.50)
red = (0.24, 0.025, 0.025)
gold = (0.58, 0.33, 0.075)
magenta = (0.72, 0.008, 0.38)

scene = Scene("Heritage gallery")
vaults = Asset("Vaults")
columns = Asset("Columns")
stairs = Asset("Staircase & railing")
chandelier = Asset("Chandelier")
spheres = Asset("Spheres")

vaults.include("floor", box((7.6, 22.0, .18), center=(0,4,-.10), color=floor_color))
vaults.include("left wall", box((.20,20,4.3), center=(-3.17,4.2,2.1), color=stone))
vaults.include("right wall", box((.20,20,4.3), center=(3.17,4.2,2.1), color=stone))
vaults.include("far wall", box((6.2,.16,6.7), center=(0,12.4,3.3), color=stone_light))
vaults.include("far daylight opening", box((2.1,.08,3.5), center=(0,12.28,2.12), color=(.98,.92,.77)))

for side in (-1, 1):
    for j in range(BAYS):
        y = -3.0 + j * BAY
        vaults.include("window %s %s" % (side,j),
            box((.025,1.12,1.65), center=(side*3.045,y,2.95),
                color=(.88,.84,.73)))

# Continuous pitched vault infill. Each side rises toward the central ridge.
for j in range(BAYS):
    y0 = -4.5 + j*BAY
    ym = y0 + BAY/2
    y1 = y0 + BAY
    for side in (-1,1):
        panel = box((3.87,BAY+.10,.14),
                    center=(side*1.48,ym,5.39), color=stone_light)
        panel.turn(axis="y", degrees=side*40)
        vaults.include("ceiling panel %s %s" % (j,side), panel)
        transverse = [(side*2.92,y0,SPRING),(side*2.55,y0,5.05),
                      (side*1.55,y0,6.05),(0,y0,VAULT_TOP)]
        diagonal = [(side*2.92,y0,SPRING),(side*2.35,y0+.55,5.18),
                    (side*1.35,ym-.25,6.13),(0,ym,VAULT_TOP)]
        return_rib = [(side*2.92,y1,SPRING),(side*2.35,y1-.55,5.18),
                      (side*1.35,ym+.25,6.13),(0,ym,VAULT_TOP)]
        vaults.include("transverse rib %s %s" % (j,side),
                       sweep_tube(points=transverse,radius=.065,color=stone_shadow))
        vaults.include("diagonal rib %s %s" % (j,side),
                       sweep_tube(points=diagonal,radius=.055,color=stone_shadow))
        vaults.include("return rib %s %s" % (j,side),
                       sweep_tube(points=return_rib,radius=.055,color=stone_shadow))
    vaults.include("ridge %s" % j,
                   rod(.055,start=(0,y0,VAULT_TOP),end=(0,y1,VAULT_TOP),color=stone_shadow))

for side in (-1,1):
    x = side*PIER_X
    for j in range(BAYS+1):
        y = -4.5+j*BAY
        columns.include("pier %s %s" % (side,j),
            rod(.15,start=(x,y,.15),end=(x,y,SPRING),color=stone_light))
        for k,(dx,dy) in enumerate(((-.14,0),(.14,0),(0,-.14),(0,.14))):
            columns.include("clustered shaft %s %s %s" % (side,j,k),
                rod(.052,start=(x+dx,y+dy,.15),
                    end=(x+dx,y+dy,SPRING),color=stone))
        columns.include("base %s %s" % (side,j),
                        box((.52,.52,.18),center=(x,y,.12),color=stone_shadow))
        columns.include("capital %s %s" % (side,j),
                        box((.60,.60,.20),center=(x,y,SPRING-.04),color=stone_light))
        if j < BAYS:
            arch = [(x,y,3.65),(x,y+.32,4.25),(x,y+.78,4.78),
                    (x,y+BAY/2,5.12),(x,y+BAY-.78,4.78),
                    (x,y+BAY-.32,4.25),(x,y+BAY,3.65)]
            columns.include("pointed arcade %s %s" % (side,j),
                            sweep_tube(points=arch,radius=.072,color=stone_shadow))

# The flight runs laterally across the near view. The handrail slopes downward
# to the right in world space, and the open balusters expose the pale treads.
stairs.include("upper landing",
    box((2.2,2.0,.18),center=(-2.35,-2.2,1.60),color=stone_light))
for i in range(11):
    x = -2.15 + i*.38
    z = 1.54 - i*.125
    stairs.include("marble tread %02d" % i,
        box((.41,1.65,.13),center=(x,-2.25,z),color=stone_light))
    stairs.include("dark tread edge %02d" % i,
        box((.035,1.67,.035),center=(x+.19,-2.25,z+.07),color=stone_shadow))

rail_y = -3.10
for i in range(12):
    x = -2.30+i*.38
    z = 1.63-i*.125
    stairs.include("red upright %02d" % i,
        rod(.029,start=(x,rail_y,z),end=(x,rail_y,z+.95),color=red))
    if i < 11:
        stairs.include("diagonal iron %02d" % i,
            rod(.020,start=(x,rail_y,z+.14),
                end=(x+.38,rail_y,z+.74),color=red))
        stairs.include("cross iron %02d" % i,
            rod(.018,start=(x,rail_y,z+.76),
                end=(x+.38,rail_y,z+.02),color=red))
stairs.include("red handrail",
    rod(.060,start=(-2.30,rail_y,2.58),end=(1.88,rail_y,1.205),color=red))
stairs.include("gold handrail",
    rod(.022,start=(-2.30,rail_y,2.64),end=(1.88,rail_y,1.265),color=gold))
stairs.include("lower rail",
    rod(.033,start=(-2.30,rail_y,1.80),end=(1.88,rail_y,.425),color=red))

chandelier.include("chain",
    rod(.024,start=(0,4,6.50),end=(0,4,4.65),color=gold))
chandelier.include("stem",
    rod(.05,start=(0,4,4.10),end=(0,4,4.70),color=gold))
chandelier.include("center",ball(.12,center=(0,4,4.18),color=gold))
for k in range(8):
    a=2*math.pi*k/8
    x=.67*math.cos(a)
    y=4+.67*math.sin(a)
    chandelier.include("arm %s" % k,
        rod(.025,start=(0,4,4.18),end=(x,y,4.30),color=gold))
    chandelier.include("bulb %s" % k,
        ball(.075,center=(x,y,4.39),color=(1,.82,.50)))

spheres.include("magenta solid",
                ball(MAGENTA_RADIUS,center=MAGENTA_CENTER,color=magenta))
spheres.include("iridescent bubble",
                ball(BUBBLE_RADIUS,center=BUBBLE_CENTER,color=(.6,.65,.8)))

for name,asset in (("Vaults",vaults),("Columns",columns),
                   ("Staircase & railing",stairs),("Chandelier",chandelier),
                   ("Spheres",spheres)):
    scene.include(name,asset)

realize(scene)
sc=bpy.context.scene

if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
wn=sc.world.node_tree.nodes
wl=sc.world.node_tree.links
background=wn.get("Background") or wn.new("ShaderNodeBackground")
output=wn.get("World Output") or wn.new("ShaderNodeOutputWorld")
wl.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.72,.76,.81,1)
background.inputs["Strength"].default_value=.45

# Stone receives a shared fine bump; lighting remains responsible for the
# broad variation between the lit far end and the shaded vault intersections.
for mat in list(bpy.data.materials):
    if not mat.use_nodes:
        continue
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c=bsdf.inputs["Base Color"].default_value
    if c[0]>.4 and .7<c[1]/max(c[0],.001)<1.1 and c[2]<c[0]:
        bsdf.inputs["Roughness"].default_value=.70
        noise=mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=17
        noise.inputs["Detail"].default_value=2
        bump=mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.10
        bump.inputs["Distance"].default_value=.025
        mat.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])

# Thin-film appearance: view-dependent colors plus a small distorted spatial
# variation evoke the broad oil-slick bands visible in the reference.
bubble=bpy.data.materials.new("Thin-film iridescent bubble")
bubble.use_nodes=True
n=bubble.node_tree.nodes
l=bubble.node_tree.links
n.clear()
out=n.new("ShaderNodeOutputMaterial")
mix=n.new("ShaderNodeMixShader")
transparent=n.new("ShaderNodeBsdfTransparent")
gloss=n.new("ShaderNodeBsdfPrincipled")
gloss.inputs["Metallic"].default_value=.22
gloss.inputs["Roughness"].default_value=.12
if "Coat Weight" in gloss.inputs:
    gloss.inputs["Coat Weight"].default_value=.8
layer=n.new("ShaderNodeLayerWeight")
noise=n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=2.8
noise.inputs["Detail"].default_value=2
tex=n.new("ShaderNodeTexCoord")
l.new(tex.outputs["Generated"],noise.inputs["Vector"])
mult=n.new("ShaderNodeMath")
mult.operation="MULTIPLY"
mult.inputs[1].default_value=.34
l.new(noise.outputs["Fac"],mult.inputs[0])
add=n.new("ShaderNodeMath")
add.operation="ADD"
l.new(layer.outputs["Facing"],add.inputs[0])
l.new(mult.outputs[0],add.inputs[1])
wave=n.new("ShaderNodeMath")
wave.operation="MULTIPLY"
wave.inputs[1].default_value=3.0
l.new(add.outputs[0],wave.inputs[0])
fract=n.new("ShaderNodeMath")
fract.operation="FRACT"
l.new(wave.outputs[0],fract.inputs[0])
ramp=n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
colors=[(0.0,(.10,.24,.95,1)),(.16,(.05,.88,.85,1)),
        (.32,(.90,.86,.12,1)),(.50,(1,.30,.06,1)),
        (.68,(.95,.03,.52,1)),(.84,(.44,.04,.85,1)),
        (1.0,(.12,.32,.95,1))]
ramp.color_ramp.elements[0].position=colors[0][0]
ramp.color_ramp.elements[0].color=colors[0][1]
for p,c in colors[1:]:
    e=ramp.color_ramp.elements.new(p)
    e.color=c
l.new(fract.outputs[0],ramp.inputs["Fac"])
l.new(ramp.outputs["Color"],gloss.inputs["Base Color"])
l.new(transparent.outputs[0],mix.inputs[1])
l.new(gloss.outputs[0],mix.inputs[2])
mix.inputs[0].default_value=.76
l.new(mix.outputs[0],out.inputs["Surface"])

# SceneAct creates generic mesh names; select the two balls by their actual
# world-space mesh centers and dimensions instead of relying on those names.
bpy.context.view_layer.update()
mesh_objects=[o for o in sc.objects if o.type=="MESH"]
def nearest_mesh(center,diameter):
    target=Vector(center)
    candidates=[]
    for obj in mesh_objects:
        world_center=obj.matrix_world @ Vector((0,0,0))
        d=(world_center-target).length
        sz=max(obj.dimensions)
        candidates.append((d+abs(sz-diameter)*.4,obj))
    return min(candidates,key=lambda item:item[0])[1]

bubble_obj=nearest_mesh(BUBBLE_CENTER,2*BUBBLE_RADIUS)
bubble_obj.data.materials.clear()
bubble_obj.data.materials.append(bubble)
for poly in bubble_obj.data.polygons:
    poly.use_smooth=True

mag_obj=nearest_mesh(MAGENTA_CENTER,2*MAGENTA_RADIUS)
for poly in mag_obj.data.polygons:
    poly.use_smooth=True
if mag_obj.data.materials:
    mat=mag_obj.data.materials[0]
    if mat.use_nodes:
        bsdf=mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value=.42

# Collection names are available for organization in the saved scene.
for name in ("Vaults","Columns","Staircase & railing","Chandelier","Spheres"):
    if bpy.data.collections.get(name) is None:
        sc.collection.children.link(bpy.data.collections.new(name))
for obj in (bubble_obj,mag_obj):
    dest=bpy.data.collections["Spheres"]
    if obj.name not in dest.objects:
        dest.objects.link(obj)
    for collection in list(obj.users_collection):
        if collection != dest:
            collection.objects.unlink(obj)

sc.render.resolution_x=3840
sc.render.resolution_y=2160
sc.render.resolution_percentage=100
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)
area_emitter((0,3.4,4.5),power=850,size=2.2,target=(0,2,1),color=(1,.76,.52))
area_emitter((0,11.4,4.0),power=1800,size=4.0,target=(0,2,2.2),color=(1,.92,.78))
area_emitter((-2,-4,5.8),power=450,size=4.0,target=(0,2,3),color=(1,.88,.72))
sc.render.engine="CYCLES"
sc.cycles.use_denoising=True
sc.render.image_settings.file_format="PNG"
try:
    sc.view_settings.view_transform="Filmic"
except TypeError:
    pass

# Computed landmark positions are kept distinct from visual estimates. The
# small upward trial is printed and restored; it should move fixed features
# downward. No camera change is applied on the basis of this trial alone.
landmarks=[
    ("background opening top",(0,12.20,3.8),(.48,.45)),
    ("left pier capital",(-PIER_X,-1.5,SPRING),(.16,.45)),
    ("foreground rail left",(-2.30,rail_y,2.64),(.10,.75)),
    ("foreground rail right",(1.88,rail_y,1.265),(.85,.98)),
    ("magenta center",MAGENTA_CENTER,(.49,.52)),
    ("bubble center",BUBBLE_CENTER,(.90,.65)),
]
def project_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    matrix=cam.calc_matrix_camera(
        dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    print("Landmark projections:",label)
    for name,point,reference in landmarks:
        clip=matrix @ cam.matrix_world.inverted() @ Vector((*point,1))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print(name,"reference",reference,"computed",
              None if uv is None else tuple(round(v,3) for v in uv))

project_table("retained camera")
cam=sc.camera
saved_rotation=cam.rotation_euler.copy()
trial_target=Vector((CAM_TARGET[0],CAM_TARGET[1],CAM_TARGET[2]+.15))
cam.rotation_euler=(trial_target-Vector(CAM_POS)).to_track_quat("-Z","Y").to_euler()
project_table("trial aim upward")
cam.rotation_euler=saved_rotation
bpy.context.view_layer.update()
