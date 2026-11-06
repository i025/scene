import bpy, math
from sceneact import *

# Reference inventory (normalized image bounds):
# Architecture: pale ceiling (0,0)-(0.46,.12), slatted rear wall
# (0,.11)-(.46,.76), light tiled floor (0,.75)-(.42,1).
# White door (.31,.29)-(.455,.77), with thin frame, lever and lock.
# Low black bench/cabinet (0,.65)-(.205,.80), white inset front.
# Right kitchen: stone worktop (.36,.59)-(1,1), dark lower cabinetry,
# glossy pale backsplash (.57,.30)-(1,1), brown upper cabinets
# (.46,0)-(1,.43), silver extractor beneath, continuous warm task light.
# Black inset sink (.46,.63)-(.62,.71), black ceramic hob
# (.40,.76)-(.85,1), cropped along bottom. Faucet is not clearly visible.
# Main contours: door verticals remain upright; worktop left edge goes
# from (.36,1) to (.46,.60); overhead fronts run toward (.54,.42).
# Rear wall supports door and slats; worktop supports sink and hob.
# Unseen cabinetry and room beyond frame are deliberately simple.
# Primitive estimate: about 135 boxes/rods, 5 sink solids, 5 hob rings.
# All composites have named parts and explicit world-frame dimensions.

scene = Scene("Warm narrow kitchen")

def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def cube(parent, name, size, center, color):
    n = box(size=size, center=center, color=color)
    parent.include(name, n)
    return n

cream = (.79,.77,.71)
wood = (.24,.105,.042)
darkwood = (.14,.060,.026)
black = (.012,.014,.013)
stone = (.69,.65,.54)
chrome = (.48,.49,.46)

room = asset("Room architecture")
cube(room, "Rear wall backing", (6,.12,3.6), (-2.7,3.72,1.8), (.085,.057,.037))
cube(room, "Right wall", (.12,9,4.0), (-.14,.0,2), (.82,.81,.76))
cube(room, "Ceiling", (7,10,.13), (-2.6,.0,3.48), (.87,.86,.82))
cube(room, "Floor foundation", (7,10,.10), (-2.6,.0,-.07), (.58,.56,.49))

# Rear wall slats: narrow dark grooves, warmer illuminated wood faces.
slats = asset("Rear vertical oak slat cladding")
for i in range(54):
    x = -5.0 + i*.071
    # Door opening interrupts all slats through its width.
    if -2.48 < x < -1.32:
        continue
    cube(slats, "Oak batten %02d" % i, (.048,.055,2.92),
         (x,3.615,1.77), (.34,.18,.080))
cube(slats, "Upper termination", (4.45,.065,.025), (-3.0,3.61,3.23), darkwood)

door = asset("White rear door")
door_cx = -1.91
door_w = 1.08
door_h = 2.45
cube(door,"Door leaf",(door_w,.065,door_h),(door_cx,3.565,door_h/2),(.82,.83,.80))
cube(door,"Left frame",(.065,.10,door_h+.08),(door_cx-door_w/2-.038,3.52,(door_h+.08)/2),(.88,.88,.83))
cube(door,"Right frame",(.065,.10,door_h+.08),(door_cx+door_w/2+.038,3.52,(door_h+.08)/2),(.88,.88,.83))
cube(door,"Frame head",(door_w+.14,.10,.07),(door_cx,3.52,door_h+.045),(.88,.88,.83))
cube(door,"Subtle inset panel",(door_w-.13,.012,door_h-.15),(door_cx,3.523,door_h/2),(.79,.80,.77))
door.include("Handle rose",rod(radius=.027,start=(door_cx-.40,3.49,1.24),end=(door_cx-.40,3.465,1.24),color=chrome))
door.include("Lever",rod(radius=.012,start=(door_cx-.40,3.45,1.24),end=(door_cx-.27,3.45,1.24),color=chrome))
door.include("Keyhole",rod(radius=.009,start=(door_cx-.40,3.49,1.13),end=(door_cx-.40,3.47,1.13),color=(.13,.13,.12)))
for z in (.32,2.10):
    cube(door,"Hinge %.2f"%z,(.021,.025,.085),(door_cx+door_w/2,3.515,z),chrome)
cube(room,"Light switch",(.10,.025,.09),(-2.66,3.545,1.29),(.87,.87,.82))
cube(room,"Low outlet",(.075,.025,.085),(-2.66,3.545,.29),(.85,.86,.82))

bench = asset("Low black cabinet with white front")
cube(bench,"Carcass",(1.66,.48,.47),(-4.10,3.23,.245),(.018,.022,.020))
cube(bench,"Inset pale drawer",(1.50,.028,.31),(-4.10,2.977,.24),(.82,.83,.79))
cube(bench,"Dark top",(1.72,.53,.045),(-4.10,3.23,.49),(.023,.025,.022))
cube(bench,"Wood top trim",(1.67,.025,.035),(-4.10,2.96,.475),(.30,.16,.067))

# Explicit parent dimensions: worktop left x=-1.25, right x=-.20;
# long axis +Y, back edge y=3.55, height=.91.
kitchen = asset("Long kitchen base")
left_x, right_x = -1.25, -.20
front_y, back_y = -4.2, 3.55
top_z = .91
cube(kitchen,"Base cabinet mass",(1.01,7.70,.82),(-.715,-.325,.43),(.19,.13,.078))
cube(kitchen,"Recessed toe kick",(.94,7.70,.10),(-.68,-.325,.065),(.055,.043,.029))
cube(kitchen,"Stone worktop",(1.10,7.82,.055),(-.725,-.325,top_z),stone)
for i in range(8):
    y = -3.70+i*.95
    cube(kitchen,"Front oak door %02d"%i,(.023,.925,.72),(-1.233,y,.46),(.23,.14,.071))

backsplash = asset("Glossy ivory glass backsplash")
cube(backsplash,"Continuous glass sheet",(.022,7.85,1.50),(-.212,-.32,1.68),(.80,.79,.71))
for y in (1.85,3.48,-1.4):
    cube(backsplash,"Panel joint %.2f"%y,(.008,.006,1.48),(-.228,y,1.68),(.67,.66,.59))
cube(backsplash,"Socket face",(.025,.12,.10),(-.244,2.75,1.31),(.84,.84,.79))

uppers = asset("Dark walnut upper cabinets")
upper_bottom = 2.44
upper_top = 3.95
cube(uppers,"Upper carcass",(.77,7.85,upper_top-upper_bottom),
     (-.585,-.325,(upper_top+upper_bottom)/2),darkwood)
for i in range(7):
    y=-3.7+i*1.07
    cube(uppers,"Walnut front %02d"%i,(.032,1.045,1.46),
         (-.985,y,3.195),(.21,.105,.050))
    cube(uppers,"Lower finger rail %02d"%i,(.025,1.045,.028),
         (-1.008,y,2.475),(.065,.038,.022))
cube(uppers,"Rear deep end panel",(.31,.075,1.88),(-1.12,3.49,3.19),(.17,.073,.028))
cube(uppers,"Rear end face",(.72,.055,1.53),(-.60,3.51,3.205),(.23,.111,.044))
cube(uppers,"Underside",(.78,7.83,.032),(-.60,-.325,2.43),(.30,.22,.13))
cube(uppers,"Task light housing",(.025,7.70,.022),(-.39,-.325,2.405),(.65,.59,.42))
led = cube(uppers,"Warm continuous task light",(.016,7.69,.012),(-.405,-.325,2.389),(1,.76,.36))

hood = asset("Integrated stainless extractor")
cube(hood,"Extractor lower plate",(.67,1.33,.035),(-.61,-.85,2.393),(.50,.50,.44))
cube(hood,"Filter recess",(.43,.84,.008),(-.59,-.85,2.371),(.22,.23,.21))
for i in range(9):
    cube(hood,"Filter slot %02d"%i,(.37,.012,.006),(-.59,-1.19+i*.085,2.365),(.12,.13,.12))
cube(hood,"Control strip",(.045,.37,.012),(-.91,-.82,2.369),(.37,.38,.34))

sink = asset("Black rectangular inset sink")
sx, sy = -.75, 2.70
cube(sink,"Black outer flange",(.84,.66,.018),(sx,sy,.949),(.028,.025,.018))
cube(sink,"Basin dark bottom",(.58,.48,.012),(sx-.07,sy,.955),(.008,.010,.008))
cube(sink,"Basin left inner wall",(.025,.48,.055),(sx-.365,sy,.976),(.055,.047,.030))
cube(sink,"Basin back inner wall",(.60,.025,.055),(sx-.065,sy+.245,.976),(.065,.050,.027))
cube(sink,"Basin front inner wall",(.60,.025,.055),(sx-.065,sy-.245,.976),(.050,.042,.026))
cube(sink,"Right draining ledge",(.14,.56,.018),(sx+.32,sy,.964),(.055,.047,.026))
for j in range(5):
    cube(sink,"Drainer groove %02d"%j,(.11,.012,.006),(sx+.32,sy-.20+j*.10,.977),(.17,.13,.062))

hob = asset("Black glass four ring induction hob")
hx, hy = -.76, -.78
cube(hob,"Black glass surface",(.89,1.36,.017),(hx,hy,.951),(.006,.009,.009))
# Rings are real narrow circular curves, grouped as semantic SceneAct parts
# using polygonal rods, at a scale appropriate to their visible image size.
for index,(xx,yy,rr) in enumerate([
    (hx-.22,hy+.36,.185),(hx+.22,hy+.36,.155),
    (hx-.22,hy-.30,.205),(hx+.22,hy-.30,.185)]):
    ring=Asset("Cooking ring %d"%index)
    hob.include("Cooking ring %d"%index,ring)
    for j in range(28):
        a=2*math.pi*j/28
        b=2*math.pi*(j+1)/28
        ring.include("Arc %02d"%j,rod(radius=.0018,
            start=(xx+rr*math.cos(a),yy+rr*math.sin(a),.962),
            end=(xx+rr*math.cos(b),yy+rr*math.sin(b),.962),
            color=(.17,.16,.12)))

# Floor tiles, restrained grout lines and staggered rectangular pattern.
floor = asset("Light beige rectangular floor tiles")
for row in range(11):
    y=-3.8+row*.72
    cube(floor,"Cross grout %02d"%row,(6.4,.009,.003),(-3.25,y,-.014),(.35,.34,.29))
    for col in range(5):
        x=-6.1+col*1.30+(row%2)*.65
        cube(floor,"Short grout %02d %02d"%(row,col),(.009,.71,.003),(x,y+.36,-.014),(.37,.36,.31))

# Expanded estimate including polygonal hob rings and floor grout:
# approximately 280 separate primitives, no Boolean operations.
realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get("Background")
if background is None:
    background=nodes.new("ShaderNodeBackground")
output=nodes.get("World Output")
if output is None:
    output=nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.73,.77,.81,1)
background.inputs["Strength"].default_value=.32

# Camera derives from rear door height, floor/wall meeting, counter and cabinet
# convergence. The near worktop and hob intentionally continue below the frame.
set_view(position=(-.45,-3.35,1.65),
         target=(-.94,3.55,1.47),lens=31.4,sensor=36)
sc.camera.data.clip_start=.03
sc.camera.data.clip_end=100

area_emitter(position=(-3.7,-.7,3.05),power=650,size=4.0,
             target=(-1.5,2.1,1),color=(1,.91,.76))
area_emitter(position=(-3.6,2.0,2.7),power=240,size=2.0,
             target=(-3,3.6,1.4),color=(1,.83,.59))
area_emitter(position=(-.69,.3,2.33),power=110,size=2.8,
             target=(-.25,.5,1.25),color=(1,.74,.40))

# Shared finishes: subtly veined stone and directional walnut, without
# external image textures or photographic projection.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat is None:
            continue
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get("Principled BSDF")
        if bs is None:
            continue
        base=bs.inputs["Base Color"].default_value
        r,g,b=base[:3]
        bs.inputs["Roughness"].default_value=.48
        if max(r,g,b)<.035:
            bs.inputs["Roughness"].default_value=.18
        if .76<r<.86 and .68<b<.80:
            bs.inputs["Roughness"].default_value=.22
        if .60<r<.74 and .47<b<.60:
            tex=nt.nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value=8
            tex.inputs["Detail"].default_value=3
            ramp=nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position=.30
            ramp.color_ramp.elements[0].color=(.29,.25,.18,1)
            ramp.color_ramp.elements[1].position=.47
            ramp.color_ramp.elements[1].color=(.74,.70,.60,1)
            nt.links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
            bs.inputs["Roughness"].default_value=.36
        if .13<r<.36 and r>g*1.65 and g>b*1.35:
            tex=nt.nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value=5
            tex.inputs["Detail"].default_value=2
            coord=nt.nodes.new("ShaderNodeTexCoord")
            mapping=nt.nodes.new("ShaderNodeVectorMath")
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(8,8,.32)
            nt.links.new(coord.outputs["Generated"],mapping.inputs[0])
            nt.links.new(mapping.outputs["Vector"],tex.inputs["Vector"])
            ramp=nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].color=(r*.60,g*.57,b*.55,1)
            ramp.color_ramp.elements[1].color=(r*1.23,g*1.22,b*1.20,1)
            nt.links.new(tex.outputs["Fac"],ramp.inputs[0])
            nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])

# Warm line emission is added after realization.
for obj in bpy.data.objects:
    if obj.type=='MESH' and 'Warm continuous' in obj.name:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bs=mat.node_tree.nodes.get("Principled BSDF")
                if bs:
                    if "Emission Color" in bs.inputs:
                        bs.inputs["Emission Color"].default_value=(1,.68,.28,1)
                        bs.inputs["Emission Strength"].default_value=4
                    elif "Emission" in bs.inputs:
                        bs.inputs["Emission"].default_value=(1,.68,.28,1)

sc.view_settings.view_transform='AgX'
