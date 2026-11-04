from sceneact import *
import bpy, math

# Image estimates: window left 0-.29, cabinet .29-.89 above .53;
# paper roll .61-.83 x .09-.42; towel .25-.47 x .48-.83;
# jug .59-.79 x .65-.89; pitcher .73-.98 x .60-.85.
# Rear edges recede toward upper right. Camera sees cabinet front and left side.
# Counter supports all small objects; towel overlaps window and cabinet side.
scene = Scene("Kitchen corner")
C = {
    "wall": (.70,.65,.52), "cabinet": (.76,.71,.58),
    "trim": (.82,.77,.65), "paper": (.91,.88,.78),
    "chrome": (.48,.49,.45), "dark": (.035,.042,.036),
    "blue": (.035,.075,.16), "plastic": (.57,.59,.51)
}
counter_z = .86
cab_left, cab_right = -.30, .86
cab_front, cab_back = .27, .83
cab_bottom, cab_top = 1.48, 2.94

def add(parent, name, node):
    parent.include(name, node)
    return node

def oval(radius, center, scale, color):
    return resized(ball(radius, center=center, color=color), scale)

# Architecture
room = Asset("Architecture")
add(room,"rear plaster wall",box((4,.12,3.6),center=(.25,.94,1.8),color=C["wall"]))
add(room,"left wall",box((.12,3.5,3.6),center=(-1.12,-.6,1.8),color=C["trim"]))
add(room,"counter slab",box((2.8,1.75,.065),center=(.15,.065,.8275),color=(.30,.29,.24)))
add(room,"rear granite upstand",box((2.8,.045,.12),center=(.15,.86,.91),color=(.30,.29,.24)))
add(room,"left granite upstand",box((.045,1.73,.13),center=(-1.045,.06,.915),color=(.30,.29,.24)))
scene.include("room",room)

# Window and off-white venetian blinds on the left wall.
window=Asset("Window and blinds")
add(window,"daylit glass",box((.025,1.55,2.02),center=(-1.042,-.02,1.97),color=(.67,.80,.81)))
for y in (-.81,.77):
    add(window,"vertical frame "+str(y),box((.09,.075,2.20),center=(-.997,y,1.97),color=C["trim"]))
for z in (.91,2.00,3.04):
    add(window,"cross frame "+str(z),box((.10,1.65,.065),center=(-.99,-.02,z),color=C["trim"]))
for i in range(32):
    z=.96+i*.065
    slat=box((.115,1.60,.018),center=(-.942,-.02,z),color=(.78,.79,.71))
    slat.turn("y",-12)
    add(window,f"blind slat {i}",slat)
for y in (-.54,.47):
    add(window,"blind tape "+str(y),box((.012,.023,2.08),center=(-.873,y,2.0),color=(.80,.79,.69)))
add(window,"sill",box((.23,1.77,.075),center=(-.98,-.02,.915),color=C["trim"]))
scene.include("window",window)

# Raised-panel upper cabinet, broad front with visible left side.
cab=Asset("Upper cream cabinet")
add(cab,"case",box((cab_right-cab_left,cab_back-cab_front,cab_top-cab_bottom),
                   center=((cab_left+cab_right)/2,(cab_front+cab_back)/2,(cab_top+cab_bottom)/2),color=C["cabinet"]))
add(cab,"bottom lip",box((1.20,.60,.045),center=(.28,.54,1.48),color=C["trim"]))
add(cab,"door",box((1.045,.035,1.38),center=(.29,.245,2.22),color=C["trim"]))
add(cab,"recessed door panel",box((.83,.018,1.16),center=(.29,.219,2.22),color=C["cabinet"]))
for x in (-.16,.74):
    add(cab,"door stile "+str(x),box((.065,.025,1.29),center=(x,.200,2.22),color=C["trim"]))
for z in (1.59,2.85):
    add(cab,"door rail "+str(z),box((.94,.025,.055),center=(.29,.20,z),color=C["trim"]))
add(cab,"round knob",ball(.025,center=(.746,.157,1.79),color=(.37,.33,.22)))
add(cab,"knob stem",rod(.012,start=(.746,.18,1.79),end=(.746,.14,1.79),color=C["chrome"]))
scene.include("cabinet",cab)

# Vertical paper towel roll on cabinet front.
paper=Asset("Wall mounted paper towel roll")
add(paper,"lower bracket",rod(.024,start=(.41,.19,1.76),end=(.41,.027,1.76),color=(.25,.25,.20)))
add(paper,"spindle",rod(.018,start=(.41,.020,1.75),end=(.41,.020,2.53),color=C["chrome"]))
add(paper,"paper cylinder",rod(.145,length=.67,center=(.41,.012,2.11),color=C["paper"]))
add(paper,"top metal finial",oval(.033,(.41,.012,2.49),(.75,.75,1.45),C["chrome"]))
add(paper,"loose paper edge",box((.021,.10,.61),center=(.548,-.012,2.09),color=(.88,.85,.75)))
scene.include("paper towels",paper)

# Chrome towel ring attached to the cabinet side, with a draped cream cloth.
towel=Asset("Towel ring and hanging towel")
add(towel,"round wall plate",rod(.052,start=(-.302,.43,1.83),end=(-.33,.43,1.83),color=C["chrome"]))
add(towel,"mounting post",rod(.017,start=(-.33,.43,1.83),end=(-.40,.36,1.83),color=C["chrome"]))
pts=[]
for i in range(17):
    a=2*math.pi*i/16
    pts.append((-.409,.30+.112*math.cos(a),1.665+.155*math.sin(a)))
add(towel,"oval ring",sweep_tube(points=pts,radius=.008,color=C["chrome"]))
# Cloth assembled from softly rounded overlapping folds, below the ring.
for i in range(7):
    y=.225+i*.025
    bottom=1.01 + .045*math.sin(i*1.9)
    top=1.58-.022*abs(i-3)
    add(towel,f"cloth fold {i}",fillet_box((.043,.046,top-bottom),radius=.018,
        center=(-.444-.013*math.cos(i),y,(top+bottom)/2),color=(.84+.008*i,.81+.007*i,.71+.006*i)))
add(towel,"fold over ring",oval(.10,(-.442,.30,1.57),(.35,1.0,.40),C["paper"]))
add(towel,"rear cloth flap",box((.025,.19,.38),center=(-.385,.38,1.31),color=(.77,.74,.63)))
scene.include("hand towel",towel)

# Sink in foreground lower left, with dark basin and metal rim.
sink=Asset("Sink and faucet")
add(sink,"dark basin",box((.68,.55,.035),center=(-.63,-.48,.865),color=(.045,.055,.047)))
for x in (-.99,-.27):
    add(sink,"side rim "+str(x),box((.035,.61,.018),center=(x,-.48,.88),color=C["chrome"]))
for y in (-.78,-.18):
    add(sink,"cross rim "+str(y),box((.75,.025,.018),center=(-.63,y,.88),color=C["chrome"]))
add(sink,"faucet base",rod(.055,length=.025,center=(-.61,-.09,.889),color=C["chrome"]))
add(sink,"faucet lower",rod(.019,start=(-.61,-.09,.90),end=(-.61,-.09,1.15),color=C["chrome"]))
add(sink,"high bent spout",sweep_tube(points=[(-.61,-.09,1.14),(-.61,-.09,1.29),
    (-.61,-.14,1.32),(-.61,-.24,1.30),(-.61,-.27,1.24)],radius=.014,color=C["chrome"]))
for x in (-.76,-.46):
    add(sink,"tap foot "+str(x),rod(.032,length=.035,center=(x,-.09,.90),color=C["chrome"]))
    add(sink,"tap lever "+str(x),rod(.009,start=(x,-.09,.92),end=(x+.03,-.12,.98),color=C["chrome"]))
scene.include("sink",sink)

# Translucent gallon water jug with shoulders, cap, and loop handle.
jug=Asset("Filtered water gallon")
jx,jy=.40,-.31
add(jug,"rounded jug body",fillet_box((.29,.245,.34),radius=.065,center=(jx,jy,1.045),color=C["plastic"]))
add(jug,"sloped shoulders",oval(.155,(jx,jy,1.205),(1,.80,.88),C["plastic"]))
add(jug,"neck",rod(.040,length=.065,center=(jx,jy,1.325),color=(.66,.67,.59)))
add(jug,"white screw cap",rod(.042,length=.036,center=(jx,jy,1.367),color=(.83,.82,.71)))
add(jug,"handle loop",sweep_tube(points=[(jx-.10,jy+.012,1.28),(jx-.16,jy+.012,1.24),
    (jx-.17,jy+.012,1.14),(jx-.11,jy+.012,1.12)],radius=.018,color=(.66,.67,.59)))
scene.include("water jug",jug)

# Blue filter pitcher, behind and to the right of the gallon.
pitcher=Asset("Blue water filter pitcher")
px,py=.78,.19
add(pitcher,"blue vessel",oval(.18,(px,py,1.065),(1,.76,1.50),C["blue"]))
add(pitcher,"flat blue base",rod(.135,length=.035,center=(px,py,.895),color=(.05,.09,.16)))
add(pitcher,"upper rim",rod(.172,length=.04,center=(px,py,1.30),color=(.20,.24,.24)))
add(pitcher,"sloping lid",oval(.172,(px-.008,py-.003,1.327),(1,.78,.18),color=(.36,.37,.32)))
add(pitcher,"pouring lip",box((.075,.075,.045),center=(px-.15,py-.03,1.32),color=(.31,.33,.30)))
add(pitcher,"clear handle",sweep_tube(points=[(px+.15,py,1.27),(px+.24,py,1.23),
    (px+.28,py,1.12),(px+.25,py,.98),(px+.15,py,.95)],radius=.023,color=(.44,.48,.43)))
scene.include("filter pitcher",pitcher)

# Small objects clustered in the corner behind the towel and jug.
objects=Asset("Countertop accessories")
add(objects,"blender black base",fillet_box((.18,.18,.15),radius=.025,center=(.10,.48,.955),color=(.025,.029,.024)))
add(objects,"blender collar",rod(.075,length=.08,center=(.10,.48,1.065),color=(.045,.045,.035)))
cup=rod(.062,length=.28,center=(.10,.48,1.235),color=(.29,.32,.28),opacity=.55)
cup.turn("x",9)
add(objects,"clear blending cup",cup)
add(objects,"cup upper rim",rod(.065,length=.012,center=(.10,.459,1.374),color=(.51,.53,.46)))
add(objects,"green canister",rod(.058,length=.25,center=(-.15,.49,.985),color=(.24,.27,.14)))
add(objects,"canister lid",rod(.064,length=.022,center=(-.15,.49,1.122),color=(.44,.43,.27)))
add(objects,"small steel cup",rod(.042,length=.065,center=(-.30,-.04,.895),color=(.29,.29,.23)))
add(objects,"cup dark opening",rod(.033,length=.004,center=(-.30,-.04,.93),color=(.04,.043,.03)))
add(objects,"soap dish",box((.16,.11,.018),center=(-.91,-.14,.88),color=(.52,.49,.33)))
add(objects,"cream soap",fillet_box((.12,.075,.025),radius=.011,center=(-.91,-.14,.902),color=(.78,.74,.57)))
scene.include("accessories",objects)

print("Primitive count:",sum(n.solid is not None for n in scene.traverse()))
realize(scene)

# Material customization stays procedural; no reference image is used as a texture.
def noise_material(name, base, scale, roughness=.6, strength=.12):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    n=mat.node_tree.nodes
    l=mat.node_tree.links
    bs=n.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*base,1)
    bs.inputs["Roughness"].default_value=roughness
    tex=n.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=scale
    tex.inputs["Detail"].default_value=2.5
    bump=n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=strength
    bump.inputs["Distance"].default_value=.012
    l.new(tex.outputs["Fac"],bump.inputs["Height"])
    l.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return mat

granite=noise_material("Fine mottled brown granite",(.31,.29,.23),150,.39,.23)
n=granite.node_tree.nodes
l=granite.node_tree.links
noise=next(nod for nod in n if nod.type=="TEX_NOISE")
ramp=n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.25
ramp.color_ramp.elements[0].color=(.075,.075,.055,1)
ramp.color_ramp.elements[1].position=.77
ramp.color_ramp.elements[1].color=(.61,.56,.43,1)
l.new(noise.outputs["Fac"],ramp.inputs[0])
l.new(ramp.outputs["Color"],n.get("Principled BSDF").inputs["Base Color"])
fabric=noise_material("Cream terrycloth",(.83,.79,.69),230,.93,.25)
paper_mat=noise_material("Paper soft grain",(.87,.84,.74),180,.86,.07)

for obj in bpy.context.scene.objects:
    if obj.type!="MESH":
        continue
    name=obj.name.lower()
    if any(s in name for s in ("counter slab","granite upstand")):
        obj.data.materials.clear()
        obj.data.materials.append(granite)
    elif "cloth fold" in name or "fold over ring" in name or "cloth flap" in name:
        obj.data.materials.clear()
        obj.data.materials.append(fabric)
    elif "paper cylinder" in name or "loose paper" in name:
        obj.data.materials.clear()
        obj.data.materials.append(paper_mat)
    for mat in obj.data.materials:
        if not mat or not mat.use_nodes:
            continue
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if not bs:
            continue
        if any(s in name for s in ("faucet","tap ","spout","ring","plate","spindle","finial","steel","rim")):
            bs.inputs["Metallic"].default_value=.72
            bs.inputs["Roughness"].default_value=.25
        if any(s in name for s in ("jug body","shoulders","handle loop")):
            bs.inputs["Roughness"].default_value=.32
            bs.inputs["Subsurface Weight"].default_value=.08
        if "blue vessel" in name:
            bs.inputs["Roughness"].default_value=.21
        if "daylit glass" in name:
            bs.inputs["Emission Color"].default_value=(.48,.66,.72,1)
            bs.inputs["Emission Strength"].default_value=.7

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.67,.69,.66,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.35

set_view(position=(-1.78,-3.12,2.20),target=(-.08,.28,1.70),lens=43,sensor=36)
area_emitter(position=(-1.0,-.35,2.35),power=170,size=1.65,target=(.35,.35,1.35),color=(.82,.91,1))
area_emitter(position=(.4,-1.9,2.8),power=65,size=2.0,target=(.1,.35,1.4),color=(1,.84,.64))
sc.view_settings.view_transform="AgX"
