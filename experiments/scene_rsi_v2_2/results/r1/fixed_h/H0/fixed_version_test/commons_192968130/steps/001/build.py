from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(11)
scene = Scene("Warm compact kitchen")

def add(name, size, center, color):
    node = box(size=size, center=center, color=color)
    scene.include(name, node)
    return node

# Room shell and the pale, lightly grained tiled floor.
add("floor", (7,9,.12), (-.8,.3,-.07), (.54,.50,.43))
add("back_wall", (5,.12,2.9), (-1,3.5,1.45), (.30,.19,.105))
add("right_wall", (.12,8,3), (1.42,.1,1.5), (.87,.85,.78))
add("ceiling", (6,9,.10), (-1,.1,2.88), (.88,.87,.82))
for j in range(19):
    for i in range(11):
        x=-3.7+i*.49+(j%2)*.245
        y=-4+j*.42
        c=random.uniform(.50,.63)
        add("stone_tile_%d_%d"%(j,i),(.485,.414,.016),(x,y,.002),
            (c,c*.955,c*.86))
        for k in range(2):
            xx=x+random.uniform(-.2,.2)
            yy=y+random.uniform(-.17,.17)
            add("floor_grain_%d_%d_%d"%(j,i,k),
                (random.uniform(.12,.38),.002,.001),
                (xx,yy,.011),(c*.85,c*.83,c*.76))

# Narrow vertical timber battens on the far wall.
for i in range(69):
    x=-3.0+i*.062
    if -.015 < x < .965:
        continue
    t=random.uniform(.67,1.13)
    add("wall_batten_%02d"%i,(.040,.070,2.35),(x,3.399,1.19),
        (.42*t,.225*t,.105*t))

# White door, reveal and simple silver hardware.
add("door_dark_reveal",(.96,.035,2.08),(.47,3.335,1.04),(.34,.32,.28))
add("door_leaf",(.83,.045,1.99),(.47,3.292,1.015),(.84,.845,.81))
add("door_left_trim",(.055,.065,2.12),(.015,3.275,1.06),(.87,.87,.83))
add("door_right_trim",(.055,.065,2.12),(.925,3.275,1.06),(.87,.87,.83))
add("door_top_trim",(.965,.065,.06),(.47,3.275,2.09),(.88,.88,.84))
scene.include("handle_plate",rod(radius=.025,start=(.15,3.257,1.035),
                                  end=(.15,3.235,1.035),color=(.5,.52,.50)))
scene.include("door_handle",rod(radius=.012,start=(.15,3.218,1.042),
                                 end=(.275,3.218,1.042),color=(.58,.60,.58)))
scene.include("keyhole",rod(radius=.010,start=(.15,3.26,.948),
                             end=(.15,3.235,.948),color=(.25,.26,.24)))
for z in (.40,1.03):
    add("wall_switch_"+str(z),(.078,.026,.082),(-.15,3.31,z),(.87,.87,.81))
    add("switch_inner_"+str(z),(.045,.006,.05),(-.15,3.291,z),(.74,.74,.69))

# Low black framed unit at the left edge.
add("low_unit", (1.23,.40,.43),(-1.64,3.10,.235),(.022,.025,.024))
add("low_unit_front",(1.10,.023,.29),(-1.64,2.884,.225),(.80,.83,.81))
add("low_unit_top",(1.29,.44,.045),(-1.64,3.08,.47),(.035,.033,.027))
add("low_unit_left_edge",(.04,.035,.36),(-2.20,2.87,.25),(.025,.025,.021))
add("low_unit_right_edge",(.04,.035,.36),(-1.08,2.87,.25),(.025,.025,.021))

# Base cabinets along the right wall.
add("base_cabinet_body",(.84,6.0,.80),(.99,.10,.44),(.22,.115,.055))
for j in range(8):
    y=-2.6+j*.76
    add("base_front_%d"%j,(.027,.744,.73),(.555,y,.455),(.285,.16,.078))
add("toe_kick",(.08,6.0,.105),(.60,.10,.065),(.075,.054,.035))

# Stone countertop is built around the actual sink opening.
stone=(.72,.665,.55)
# Counter bounds x .49..1.43, y -3..3.30.
sink_y=2.02
add("counter_front_section",(.96,4.61,.055),(.96,-.695,.895),stone)
add("counter_back_section",(.96,.78,.055),(.96,2.91,.895),stone)
add("counter_sink_outer_strip",(.14,.92,.055),(1.37,sink_y,.895),stone)
add("counter_sink_inner_strip",(.12,.92,.055),(.54,sink_y,.895),stone)
add("counter_sink_near_strip",(.76,.10,.055),(.98,1.61,.895),stone)
add("counter_sink_far_strip",(.76,.10,.055),(.98,2.43,.895),stone)

# Restrained irregular dark veins and mineral flecks in the stone.
for i in range(210):
    x=random.uniform(.50,1.41)
    y=random.uniform(-2.95,3.27)
    if .61<x<1.30 and 1.66<y<2.38:
        continue
    if .58<x<1.36 and -1.77<y<-.55:
        continue
    length=random.uniform(.008,.065)
    node=box((length,.0025,.0015),center=(x,y,.924),
             color=(.28,.24,.18))
    node.turn(axis="+z",degrees=random.uniform(-70,70))
    scene.include("stone_fleck_%d"%i,node)

# Inset black sink with a shallow metallic rim and recessed basin.
add("sink_bottom",(.62,.65,.022),(.95,2.02,.735),(.035,.032,.023))
add("sink_left",(.025,.70,.17),(.625,2.02,.82),(.10,.085,.052))
add("sink_right",(.025,.70,.17),(1.275,2.02,.82),(.10,.085,.052))
add("sink_near",(.67,.025,.17),(.95,1.68,.82),(.10,.085,.052))
add("sink_far",(.67,.025,.17),(.95,2.36,.82),(.10,.085,.052))
for x in (.60,1.30):
    add("sink_rim_x_"+str(x),(.027,.76,.012),(x,2.02,.931),(.32,.26,.15))
for y in (1.64,2.40):
    add("sink_rim_y_"+str(y),(.72,.027,.012),(.95,y,.931),(.32,.26,.15))
# Small draining ribs along the back edge.
for j in range(6):
    add("drain_rib_%d"%j,(.20,.011,.008),(1.16,1.78+j*.075,.939),(.34,.29,.19))

# Glossy black glass cooktop near the camera.
add("cooktop_glass",(.79,1.24,.018),(.955,-1.00,.939),(.009,.012,.011))
def ring(name,x,y,r):
    pts=[]
    for i in range(97):
        a=i*2*math.pi/96
        pts.append((x+r*math.cos(a),y+r*math.sin(a),.951))
    scene.include(name,sweep_tube(points=pts,radius=.0016,color=(.17,.18,.15)))
ring("burner_near_large",.91,-1.36,.226)
ring("burner_near_inner",.91,-1.36,.178)
ring("burner_far_left",.76,-.70,.171)
ring("burner_far_right",1.17,-.69,.123)
ring("burner_mid",1.18,-1.12,.135)

# Glossy ivory backsplash.
add("backsplash",(.024,6.25,.82),(1.352,.13,1.335),(.79,.79,.72))
for y in (-2.2,-.9,.4,1.7,2.95):
    add("backsplash_joint_"+str(y),(.028,.004,.82),(1.335,y,1.335),(.69,.69,.63))
add("backsplash_outlet",(.013,.145,.085),(1.326,1.83,1.32),(.84,.84,.78))

# Dark walnut overhead cupboards, with projecting bottom and long seams.
add("upper_cabinet_mass",(.61,6.25,.91),(1.095,.13,2.25),(.16,.075,.031))
for j in range(9):
    y=-2.64+j*.735
    t=random.uniform(.85,1.12)
    add("upper_door_%d"%j,(.028,.72,.85),(.775,y,2.27),
        (.205*t,.103*t,.046*t))
    add("upper_vertical_grain_%d"%j,(.004,.005,.77),(.757,y-.23,2.27),(.26,.14,.063))
add("upper_bottom_rail",(.66,6.28,.045),(1.07,.13,1.803),(.12,.069,.029))
add("upper_low_front_edge",(.035,6.28,.025),(.735,.13,1.775),(.29,.18,.08))
# Stainless hood underside, flush with cabinetry.
add("hood_underside",(.58,1.00,.027),(1.04,-.13,1.767),(.46,.46,.40))
for i in range(7):
    add("hood_vent_%d"%i,(.25,.013,.006),(1.07,-.38+i*.065,1.749),(.18,.19,.17))
add("hood_control",(.085,.13,.007),(.85,-.40,1.745),(.21,.22,.19))
add("under_cabinet_strip",(.018,5.9,.018),(1.29,.05,1.757),(.98,.85,.55))

realize(scene)

# Materials retain the individual geometry and add the surface responses.
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Roughness'].default_value=.48
            if "cooktop" in obj.name:
                bs.inputs['Roughness'].default_value=.12
                bs.inputs['Metallic'].default_value=.28
            if "backsplash" in obj.name:
                bs.inputs['Roughness'].default_value=.18
            if "sink" in obj.name or "handle" in obj.name or "hood" in obj.name:
                bs.inputs['Metallic'].default_value=.65
                bs.inputs['Roughness'].default_value=.3
            if "upper" in obj.name:
                bs.inputs['Roughness'].default_value=.31
            if "under_cabinet_strip" in obj.name:
                bs.inputs['Emission Color'].default_value=(1,.73,.35,1)
                bs.inputs['Emission Strength'].default_value=4

set_view(position=(-.32,-3.62,1.60),target=(.46,3.18,1.30),
         lens=26,sensor=36)
area_emitter(position=(-2.0,-.4,2.6),power=450,size=3.5,
             target=(.0,2.0,.6),color=(1,.94,.84))
area_emitter(position=(-1.5,2.0,2.7),power=180,size=2.0,
             target=(-.4,3.3,1.2),color=(1,.95,.88))
area_emitter(position=(1.16,.35,1.73),power=85,size=2.7,
             target=(1.30,.35,1.12),color=(1,.77,.44))
area_emitter(position=(1.12,2.5,1.72),power=28,size=.7,
             target=(.9,2.5,.95),color=(1,.72,.35))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.59,.63,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.26
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.35
