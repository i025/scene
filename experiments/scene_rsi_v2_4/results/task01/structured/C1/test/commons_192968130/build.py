import bpy, math
from sceneact import *

# Reference inventory, normalized image coordinates:
# Pale ceiling (0,0)-(.46,.12); brown vertical slats (0,.11)-(.46,.76);
# beige tiled floor (0,.76)-(.42,1); white door (.31,.29)-(.45,.77),
# including frame, left lever, hinges, switch and low outlet.
# Black low cabinet (0,.65)-(.205,.80), inset white front and thin top trim.
# Kitchen counter (.36,.59)-(1,1), supporting black sink (.46,.64)-(.62,.71)
# and cropped four-ring hob (.40,.77)-(.83,1). Pale reflective backsplash
# occupies right background. Walnut overhead cabinets (.46,0)-(1,.43),
# stainless extractor and warm continuous strip light beneath.
# Door and slats are upright. Counter left contour runs (235,205)->(186,342);
# upper cabinet underside runs approximately (281,145)->(512,80).
# Rear wood end panel separates door from counter. Hidden cabinet interiors
# and the unseen room beyond the image are represented simply.
#
# Revision observations, ranked:
# 1. Feedback shows a large pale right field and almost no walnut fronts.
#    Camera lies behind their front plane; this is a local visibility issue.
#    Move viewpoint slightly left, reduce upper depth, and align view along Y.
# 2. Counter near edge is too far left although rear door matches closely.
#    Its principal direction differs from reference. The modest lateral camera
#    change plus removal of yaw addresses this while preserving rear door.
# 3. Sink is too distant/small; move its complete asset toward the camera and
#    increase its fore-aft opening. Preserve its supporting countertop.
# 4. Rear slats and cabinet finishes are too light. Reduce direct illumination
#    and darken wood independently of the geometry corrections.
# These explanations are inferred from the supplied view, not measured probes.
# Expanded primitive estimate: approximately 285 meshes; one sink Boolean,
# 112 ring segments, approximately 60 floor seams. No fillet expansion.

scene = Scene("Revised warm kitchen")

def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def cube(parent, name, size, center, color):
    n = box(size=size, center=center, color=color)
    parent.include(name, n)
    return n

oak = (.255,.120,.047)
walnut = (.135,.057,.023)
black = (.009,.011,.009)
metal = (.43,.44,.41)
stone = (.68,.635,.54)

room = asset("Room architecture")
cube(room,"Rear backing",(7,.12,3.65),(-3,3.72,1.825),(.072,.044,.025))
cube(room,"Right wall",(.12,10,4.2),(-.14,-.2,2.1),(.78,.77,.72))
cube(room,"Ceiling",(8,11,.13),(-3,-.2,3.48),(.82,.81,.77))
cube(room,"Floor",(8,11,.10),(-3,-.2,-.065),(.54,.51,.45))

slats = asset("Rear oak slat cladding")
for i in range(65):
    x = -6 + i*.071
    if -2.49 < x < -1.32:
        continue
    cube(slats,"Oak batten %02d"%i,(.047,.055,2.92),
         (x,3.615,1.77),oak)
cube(slats,"Top termination",(5.0,.065,.025),(-3.5,3.61,3.23),walnut)

door = asset("White rear door")
dx, dw, dh = -1.91, 1.08, 2.45
cube(door,"Door leaf",(dw,.065,dh),(dx,3.565,dh/2),(.79,.80,.77))
cube(door,"Left frame",(.065,.10,dh+.08),
     (dx-dw/2-.038,3.52,(dh+.08)/2),(.85,.85,.81))
cube(door,"Right frame",(.065,.10,dh+.08),
     (dx+dw/2+.038,3.52,(dh+.08)/2),(.85,.85,.81))
cube(door,"Head frame",(dw+.14,.10,.07),(dx,3.52,dh+.045),(.85,.85,.81))
cube(door,"Inset panel",(dw-.13,.012,dh-.15),
     (dx,3.523,dh/2),(.775,.785,.755))
door.include("Handle rose",rod(radius=.027,
    start=(dx-.40,3.49,1.24),end=(dx-.40,3.465,1.24),color=metal))
door.include("Lever",rod(radius=.012,
    start=(dx-.40,3.45,1.24),end=(dx-.27,3.45,1.24),color=metal))
door.include("Keyhole",rod(radius=.009,
    start=(dx-.40,3.49,1.13),end=(dx-.40,3.47,1.13),color=(.11,.11,.10)))
for z in (.32,2.10):
    cube(door,"Hinge %.2f"%z,(.021,.025,.085),(dx+dw/2,3.515,z),metal)
cube(room,"Light switch",(.10,.025,.09),(-2.66,3.545,1.29),(.84,.84,.80))
cube(room,"Low outlet",(.075,.025,.085),(-2.66,3.545,.29),(.84,.84,.80))

bench = asset("Low black cabinet")
cube(bench,"Carcass",(1.66,.48,.47),(-4.10,3.23,.245),(.015,.019,.017))
cube(bench,"White inset front",(1.50,.028,.31),(-4.10,2.977,.24),(.80,.81,.77))
cube(bench,"Black top",(1.72,.53,.045),(-4.10,3.23,.49),(.018,.021,.018))
cube(bench,"Oak lip",(1.67,.025,.035),(-4.10,2.96,.475),oak)

kitchen = asset("Kitchen base and stone countertop")
left_x, right_x = -1.25, -.20
front_y, back_y, top_z = -4.2, 3.55, .91
cube(kitchen,"Base carcass",(1.01,7.70,.82),(-.715,-.325,.43),(.17,.10,.046))
cube(kitchen,"Toe recess",(.94,7.70,.10),(-.68,-.325,.065),(.039,.030,.020))

# The sink opening belongs to the supporting worktop and the basin sits below.
sx, sy, sw, sd = -.75, 1.40, .84, 1.05
slab = box(size=(1.10,7.82,.055),center=(-.725,-.325,top_z),color=stone)
cut = box(size=(.63,.84,.22),center=(sx-.055,sy,.91),color=stone)
kitchen.include("Stone slab with sink opening",subtract(slab,cut))
for i in range(8):
    y=-3.70+i*.95
    cube(kitchen,"Oak base front %02d"%i,(.023,.925,.72),
         (-1.233,y,.46),(.19,.108,.047))

backsplash = asset("Ivory glass backsplash")
cube(backsplash,"Glossy glass",(.022,7.85,1.50),
     (-.212,-.32,1.68),(.76,.755,.70))
for y in (1.85,3.48,-1.4):
    cube(backsplash,"Vertical joint %.2f"%y,(.008,.006,1.48),
         (-.228,y,1.68),(.64,.63,.58))
cube(backsplash,"Outlet",(.025,.12,.10),(-.244,2.75,1.31),(.82,.82,.77))

end = asset("Rear walnut wall end panel")
cube(end,"Tall walnut backing",(1.04,.055,3.15),
     (-.75,3.57,2.50),(.155,.065,.025))
cube(end,"Left dark edge",(.035,.08,3.15),
     (-1.28,3.54,2.50),(.080,.032,.012))

# Upper cabinet parent dimensions: shallower than the worktop, front x=-.63.
# Camera now views its fronts from the room side rather than through its back.
uppers = asset("Walnut overhead cabinet run")
ub, ut = 2.44, 3.95
uf, uw = -.63, -.20
cube(uppers,"Carcass",(uw-uf,7.85,ut-ub),
     ((uw+uf)/2,-.325,(ut+ub)/2),walnut)
for i in range(7):
    y=-3.7+i*1.07
    cube(uppers,"Walnut door %02d"%i,(.032,1.045,1.46),
         (uf-.014,y,3.195),(.155,.072,.030))
    cube(uppers,"Finger rail %02d"%i,(.025,1.045,.024),
         (uf-.026,y,2.475),(.046,.024,.011))
cube(uppers,"Rear end face",(.46,.055,1.53),
     (-.425,3.51,3.205),(.14,.060,.022))
cube(uppers,"Underside",(.46,7.83,.032),
     (-.425,-.325,2.43),(.23,.16,.086))
cube(uppers,"Task light housing",(.025,7.70,.022),
     (-.31,-.325,2.405),(.48,.41,.29))
cube(uppers,"Continuous warm luminous strip",(.017,7.69,.012),
     (-.32,-.325,2.389),(1,.72,.30))

hood = asset("Integrated stainless extractor")
cube(hood,"Lower steel plate",(.43,1.33,.035),
     (-.425,-.85,2.393),(.47,.48,.44))
cube(hood,"Filter recess",(.30,.84,.008),
     (-.425,-.85,2.371),(.19,.20,.18))
for i in range(9):
    cube(hood,"Vent slot %02d"%i,(.27,.012,.006),
         (-.425,-1.19+i*.085,2.365),(.095,.105,.092))
cube(hood,"Control strip",(.035,.37,.012),
     (-.615,-.82,2.369),(.30,.31,.28))

sink = asset("Black inset sink and drainer")
# Four rim sections retain an actual dark opening, rather than a solid lid.
cube(sink,"Left rim",(.035,sd,.022),(sx-sw/2+.018,sy,.949),(.035,.029,.018))
cube(sink,"Front rim",(sw,.035,.022),(sx,sy-sd/2+.018,.949),(.035,.029,.018))
cube(sink,"Rear rim",(sw,.035,.022),(sx,sy+sd/2-.018,.949),(.035,.029,.018))
cube(sink,"Draining ledge",(.16,sd-.04,.020),(sx+sw/2-.08,sy,.949),(.030,.027,.018))
cube(sink,"Deep basin bottom",(.61,.82,.018),(sx-.055,sy,.78),(.008,.010,.008))
cube(sink,"Left basin wall",(.018,.84,.16),(sx-.365,sy,.86),(.025,.023,.016))
cube(sink,"Right basin wall",(.018,.84,.16),(sx+.255,sy,.86),(.025,.023,.016))
cube(sink,"Rear basin wall",(.63,.018,.16),(sx-.055,sy+.42,.86),(.034,.029,.018))
cube(sink,"Front basin wall",(.63,.018,.16),(sx-.055,sy-.42,.86),(.025,.023,.016))
for j in range(7):
    cube(sink,"Drainer ridge %02d"%j,(.12,.012,.006),
         (sx+.34,sy-.40+j*.13,.962),(.115,.090,.045))

hob = asset("Four ring black induction hob")
hx, hy = -.76, -.98
cube(hob,"Black glass",(.89,1.36,.017),(hx,hy,.951),(.006,.009,.009))
for index,(xx,yy,rr) in enumerate([
    (hx-.22,hy+.36,.185),(hx+.22,hy+.36,.155),
    (hx-.22,hy-.30,.205),(hx+.22,hy-.30,.185)]):
    ring=Asset("Cooking ring %d"%index)
    hob.include("Cooking ring %d"%index,ring)
    for j in range(28):
        a=2*math.pi*j/28
        b=2*math.pi*(j+1)/28
        ring.include("Arc %02d"%j,rod(radius=.0013,
            start=(xx+rr*math.cos(a),yy+rr*math.sin(a),.962),
            end=(xx+rr*math.cos(b),yy+rr*math.sin(b),.962),
            color=(.115,.105,.075)))

floor = asset("Beige tile floor seams")
for row in range(11):
    y=-3.8+row*.72
    cube(floor,"Long grout %02d"%row,(6.4,.007,.003),
         (-3.25,y,-.012),(.37,.35,.30))
    for col in range(5):
        x=-6.1+col*1.30+(row%2)*.65
        cube(floor,"Short grout %02d %02d"%(row,col),(.007,.71,.003),
             (x,y+.36,-.012),(.37,.35,.30))

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nt=sc.world.node_tree
background=nt.nodes.get("Background")
if background is None:
    background=nt.nodes.new("ShaderNodeBackground")
output=nt.nodes.get("World Output")
if output is None:
    output=nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.73,.77,.81,1)
background.inputs["Strength"].default_value=.20

# Rear door scale and height remain nearly fixed; longitudinal vanishing point
# moves toward image center, matching counter and overhead principal directions.
set_view(position=(-.925,-3.35,1.65),
         target=(-.925,3.55,1.47),lens=31.4,sensor=36)
sc.camera.data.clip_start=.03
sc.camera.data.clip_end=100

area_emitter(position=(-3.7,-.7,3.05),power=350,size=4.0,
             target=(-1.5,2.1,1),color=(1,.92,.80))
area_emitter(position=(-3.6,2.0,2.7),power=90,size=2.0,
             target=(-3,3.6,1.4),color=(1,.85,.66))
area_emitter(position=(-.55,.5,2.32),power=65,size=2.8,
             target=(-.23,.7,1.25),color=(1,.76,.44))

# Finishes use shared palette colors to identify surface families.
seen=set()
for obj in bpy.data.objects:
    if obj.type!='MESH':
        continue
    for mat in obj.data.materials:
        if mat is None or mat.as_pointer() in seen:
            continue
        seen.add(mat.as_pointer())
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get("Principled BSDF")
        if bs is None:
            continue
        r,g,b=bs.inputs["Base Color"].default_value[:3]
        bs.inputs["Roughness"].default_value=.43
        if max(r,g,b)<.04:
            bs.inputs["Roughness"].default_value=.16
        if .74<r<.79 and .68<b<.73:
            bs.inputs["Roughness"].default_value=.13
        if abs(r-.68)<.005 and abs(g-.635)<.005:
            coord=nt.nodes.new("ShaderNodeTexCoord")
            noise=nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value=5.5
            noise.inputs["Detail"].default_value=3
            nt.links.new(coord.outputs["Generated"],noise.inputs["Vector"])
            ramp=nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position=.30
            ramp.color_ramp.elements[0].color=(.20,.16,.11,1)
            ramp.color_ramp.elements[1].position=.39
            ramp.color_ramp.elements[1].color=(.69,.65,.55,1)
            nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
            nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
            bs.inputs["Roughness"].default_value=.28
        if .07<r<.27 and r>g*1.65 and g>b*1.35:
            coord=nt.nodes.new("ShaderNodeTexCoord")
            stretch=nt.nodes.new("ShaderNodeVectorMath")
            stretch.operation='MULTIPLY'
            stretch.inputs[1].default_value=(12,12,.40)
            noise=nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value=4
            noise.inputs["Detail"].default_value=2
            nt.links.new(coord.outputs["Generated"],stretch.inputs[0])
            nt.links.new(stretch.outputs["Vector"],noise.inputs["Vector"])
            ramp=nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].color=(r*.65,g*.62,b*.60,1)
            ramp.color_ramp.elements[1].color=(r*1.18,g*1.16,b*1.12,1)
            nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
            nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
            bs.inputs["Roughness"].default_value=.32
        if r>.98 and .69<g<.75 and .27<b<.33:
            if "Emission Color" in bs.inputs:
                bs.inputs["Emission Color"].default_value=(1,.72,.34,1)
                bs.inputs["Emission Strength"].default_value=5
            elif "Emission" in bs.inputs:
                bs.inputs["Emission"].default_value=(1,.72,.34,1)

sc.view_settings.view_transform='AgX'
