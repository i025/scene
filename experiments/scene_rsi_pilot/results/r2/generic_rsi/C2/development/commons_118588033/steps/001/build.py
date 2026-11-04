from sceneact import *
import bpy
import math

# Visual ledger, normalized reference bounds (x0,y0,x1,y1):
# room: floor (0,.65,1,1), cream walls (0,.10,1,.70), exposed ceiling (0,0,1,.30).
# left three-tier berth (.00,.39,.43,.80): thin dark frames, white mattresses,
#   supported by vertical black posts; foreground electrical cabinets obscure its foot.
# electrical cabinets (.00,.47,.21,.70): two blue-gray louvered rectangular enclosures.
# rear lockers (.40,.37,.64,.58): tall pale-gray doors, vents, handles, short plinth.
# chair (.41,.53,.53,.66): pale tubular legs, broad back and seat, in front of lockers.
# utility cabinet (.53,.52,.70,.69): charcoal box, upper rim and exposed pipework.
# pillar (.69,0,.80,.85): round cream upper shaft, oxblood lower shaft, floor collar.
# right wall board (.78,.34,.92,.48), red emergency fitting (.77,.50,.85,.61).
# right foreground bench (.80,.75,1,1): dark green thick seat and slender legs.
# overhead: cream joists, crossing pipes, hanging white industrial lamps.
# Occlusion: foreground cabinets > berth; chair > lockers; pillar > utility area/wall.
# Anchors: main lamp (.39,.16), pillar foot (.72,.83), locker top (.49,.39),
# chair seat (.48,.60), rear floor (.51,.68), bench corner (.81,.76),
# berth forward edge (.02,.74), right board center (.84,.41).
# Perspective: aisle edges converge around (.48,.42); verticals nearly vertical.
# Camera hypothesis: eye height 1.6 m, broad portrait view down a narrow ship compartment.
# All geometry uses SceneAct; no image textures and no per-mesh generated patterns.

scene = Scene("Ship compartment")
P = {
    'cream': (.62,.59,.46), 'wall': (.66,.66,.56),
    'red': (.26,.065,.037), 'floor': (.29,.105,.055),
    'steel': (.055,.075,.069), 'bedding': (.66,.69,.63),
    'locker': (.43,.47,.44), 'blue': (.075,.145,.17),
    'green': (.025,.095,.074), 'pipe': (.55,.57,.49)
}
CAM = ((.48,-5.9,1.64), (.02,2.9,1.65), 25)
def asset(name):
    a = Asset(name)
    scene.include(name,a)
    return scene.members[name]
def b(a,n,s,c,col):
    return a.include(n,box(s,center=c,color=col))
def r(a,n,p,q,rad,col):
    return a.include(n,rod(rad,start=p,end=q,color=col))
def sphere(a,n,c,rad,col,scale=None):
    v=ball(rad,center=c,color=col)
    if scale:
        v.resize(scale,pivot=c)
    return a.include(n,v)

room=asset("Architecture")
b(room,"Deck",(4.65,12,.15),(0,1,-.075),P['floor'])
b(room,"Port bulkhead",(.14,11,3.45),(-2.23,1,1.725),P['wall'])
b(room,"Starboard bulkhead",(.14,11,3.45),(2.23,1,1.725),P['wall'])
b(room,"Aft bulkhead",(4.6,.16,3.45),(0,5.25,1.725),P['wall'])
b(room,"Ceiling",(4.6,11,.13),(0,1,3.49),(.36,.31,.23))
for side in (-1,1):
    b(room,"Lower painted wall "+str(side),(.035,11,.46),
      (side*2.145,1,.23),P['red'])
    b(room,"Base skirting "+str(side),(.065,11,.07),
      (side*2.12,1,.045),(.18,.075,.045))
b(room,"Rear lower paint",(4.4,.04,.46),(0,5.14,.23),P['red'])
# Restrained deck plating seams.
for y in (-2.6,-.7,1.2,3.1,5):
    b(room,"Deck joint "+str(y),(4.35,.008,.002),(0,y,.002),(.19,.075,.04))
for x in (-1.3,.25,1.6):
    b(room,"Deck length joint "+str(x),(.006,11,.002),(x,1,.002),(.23,.085,.045))

ceiling=asset("Ceiling structure")
for i,y in enumerate((-2.2,-.15,2.0,4.2)):
    b(ceiling,"Transverse beam "+str(i),(4.35,.17,.32),(0,y,3.28),P['cream'])
for i,x in enumerate((-1.75,-.9,.15,1.2)):
    b(ceiling,"Longitudinal beam "+str(i),(.10,10,.19),(x,1,3.32),(.53,.45,.32))
for i,y in enumerate((-1.9,.15,2.2)):
    for j,x in enumerate((-1.6,-.65)):
        r(ceiling,"Diagonal brace %d %d"%(i,j),(x,y,2.85),(x+.48,y,3.45),.035,P['cream'])

pillar=asset("Foreground support pillar")
px,py=1.05,-1.13
r(pillar,"Upper cream shaft",(px,py,1.53),(px,py,3.52),.105,(.66,.59,.41))
r(pillar,"Lower oxblood shaft",(px,py,.04),(px,py,1.53),.108,P['red'])
r(pillar,"Foot collar",(px,py,.015),(px,py,.06),.143,(.36,.17,.10))
r(pillar,"Top collar",(px,py,3.28),(px,py,3.40),.14,P['cream'])

berth=asset("Port three tier berths")
for i,z in enumerate((.53,1.16,1.80)):
    b(berth,"Bed pan "+str(i),(1.05,3.72,.065),(-1.56,1.52,z),P['steel'])
    b(berth,"Mattress "+str(i),(.99,3.62,.13),(-1.55,1.53,z+.095),P['bedding'])
    b(berth,"Folded bedding "+str(i),(.92,.55,.12),(-1.55,2.90,z+.19),(.71,.73,.66))
    for x in (-2.08,-1.03):
        r(berth,"Side rail %d %s"%(i,x),(x,-.36,z-.015),(x,3.40,z-.015),.027,P['steel'])
    b(berth,"Mattress end seam "+str(i),(.98,.025,.065),(-1.55,-.28,z+.12),(.52,.56,.50))
for x in (-2.09,-1.02):
    for y in (-.43,3.45):
        r(berth,"Upright %s %s"%(x,y),(x,y,.03),(x,y,2.28),.028,P['steel'])
for z in (.87,1.51,2.14):
    r(berth,"Wall restraint "+str(z),(-2.10,3.44,z),(-1.02,3.44,z),.023,P['steel'])

cabinets=asset("Port electrical cabinets")
for i,y in enumerate((-1.62,-.91)):
    b(cabinets,"Enclosure "+str(i),(.48,.58,.86),(-1.91,y,.96),P['blue'])
    b(cabinets,"Front inset "+str(i),(.025,.48,.72),(-1.654,y,.96),(.11,.18,.20))
    for j in range(13):
        b(cabinets,"Vent %d %d"%(i,j),(.025,.37,.018),
          (-1.635,y,.65+j*.047),(.24,.30,.29))
    b(cabinets,"Top lip "+str(i),(.54,.64,.035),(-1.91,y,1.41),(.055,.095,.10))
    b(cabinets,"Bottom lip "+str(i),(.54,.64,.035),(-1.91,y,.51),(.04,.075,.075))
    b(cabinets,"Latch "+str(i),(.035,.035,.10),(-1.625,y+.20,1.15),(.51,.51,.43))

vent=asset("Port ventilation heater")
b(vent,"Rounded outer casing",(.23,.70,.74),(-2.02,.02,2.55),(.62,.62,.52))
b(vent,"Dark vent opening",(.035,.53,.52),(-1.88,.02,2.53),(.075,.095,.09))
for j in range(6):
    b(vent,"Horizontal grille "+str(j),(.045,.55,.035),(-1.85,.02,2.32+j*.077),(.64,.65,.55))
b(vent,"Upper control badge",(.045,.20,.055),(-1.85,.02,2.84),(.24,.27,.25))

lockers=asset("Rear metal lockers")
for i,x in enumerate((-.77,-.25,.27)):
    b(lockers,"Locker body "+str(i),(.50,.58,1.66),(x,4.15,1.03),P['locker'])
    b(lockers,"Door "+str(i),(.475,.025,1.56),(x,3.845,1.05),(.48,.51,.47))
    for j in range(5):
        b(lockers,"Upper louver %d %d"%(i,j),(.23,.014,.018),(x,3.824,1.55+j*.046),(.28,.33,.31))
    for j in range(4):
        b(lockers,"Lower louver %d %d"%(i,j),(.23,.014,.018),(x,3.824,.43+j*.045),(.29,.34,.31))
    b(lockers,"Door latch "+str(i),(.027,.045,.12),(x+.155,3.80,1.11),(.16,.19,.17))
    sphere(lockers,"Top bundled helmet "+str(i),(x,4.11,1.92),.16,(.35,.38,.33),(.85,.85,.7))
b(lockers,"Continuous plinth",(1.59,.57,.13),(-.25,4.15,.14),(.23,.27,.24))

chair=asset("Pale metal chair")
cx,cy=-.32,2.77
b(chair,"Seat",(.48,.46,.07),(cx,cy,.48),(.50,.52,.41))
b(chair,"Backrest",(.47,.065,.35),(cx,cy+.19,.86),(.57,.59,.49))
for i,x in enumerate((cx-.21,cx+.21)):
    r(chair,"Front leg "+str(i),(x,cy-.19,.025),(x,cy-.17,.49),.018,(.57,.58,.47))
    r(chair,"Rear leg and back "+str(i),(x,cy+.25,.025),(x,cy+.20,1.07),.019,(.57,.58,.47))
    r(chair,"Side stretcher "+str(i),(x,cy-.18,.23),(x,cy+.23,.23),.013,(.48,.49,.40))
r(chair,"Front stretcher",(cx-.21,cy-.18,.22),(cx+.21,cy-.18,.22),.014,(.48,.49,.40))
# Slightly skew the complete supported chair.
chair.turn('z',-13,pivot=(cx,cy,0))

utility=asset("Aft utility pedestal")
b(utility,"Cabinet body",(.78,.65,.88),(.83,3.09,.47),(.22,.25,.23))
b(utility,"Inset front panel",(.65,.035,.71),(.83,2.746,.48),(.26,.29,.26))
b(utility,"Top rim",(.88,.74,.07),(.83,3.09,.94),(.34,.36,.31))
b(utility,"Dark top basin",(.65,.51,.025),(.83,3.07,.985),(.08,.105,.095))
for x in (.59,1.07):
    r(utility,"Short upright "+str(x),(x,3.32,.98),(x,3.32,1.19),.018,P['pipe'])
r(utility,"Tap crosspiece",(.59,3.32,1.19),(1.07,3.32,1.19),.023,P['pipe'])

pipes=asset("Exposed services")
for i,x in enumerate((.56,.91,1.28)):
    r(pipes,"Rear vertical service "+str(i),(x,4.69,.25),(x,4.69,3.20),.026,(.18,.21,.18))
    r(pipes,"Upper return "+str(i),(x,4.69,3.20),(x-.35,4.69,3.20),.026,(.18,.21,.18))
r(pipes,"Black overhead main",(-1.15,3.39,2.54),(1.45,3.39,2.54),.035,(.045,.055,.045))
r(pipes,"Black descending main",(-1.15,3.39,.06),(-1.15,3.39,2.54),.03,(.045,.055,.045))
r(pipes,"Port overhead longitudinal",(-1.61,-3,2.95),(-1.61,4.8,2.95),.055,P['pipe'])
for y in (-1.1,1.2,3.6):
    r(pipes,"Pipe clamp "+str(y),(-1.61,y,2.90),(-1.61,y,3.18),.018,(.27,.29,.24))
r(pipes,"Crossing cream pipe",(-2.12,.9,2.62),(.20,.9,2.62),.043,P['pipe'])
r(pipes,"Rear pipe riser",(1.65,4.8,.1),(1.65,4.8,3.2),.055,P['pipe'])

board=asset("Starboard notice board")
b(board,"Gray board",(.045,1.13,.78),(2.135,2.68,2.06),(.25,.29,.26))
for z in (1.66,2.46):
    b(board,"Horizontal border "+str(z),(.065,1.18,.035),(2.10,2.68,z),(.39,.40,.32))
for y in (2.10,3.26):
    b(board,"Vertical border "+str(y),(.065,.035,.82),(2.10,y,2.06),(.39,.40,.32))

fire=asset("Red emergency station")
b(fire,"Wall mounting plate",(.065,.37,.59),(2.10,1.45,1.12),(.67,.055,.025))
sphere(fire,"Rounded red top",(2.065,1.45,1.42),.18,(.75,.065,.035),(.40,1,1))
b(fire,"Main shaped housing",(.16,.28,.36),(2.01,1.45,1.18),(.73,.055,.025))
r(fire,"Handle",(1.90,1.37,1.35),(1.90,1.53,1.35),.025,(.16,.17,.13))
b(fire,"White instruction label",(.015,.13,.12),(1.916,1.45,1.16),(.77,.75,.61))
r(fire,"Dark hose",(1.94,1.55,1.34),(1.94,1.56,1.03),.023,(.13,.10,.065))

bench=asset("Starboard foreground bench")
b(bench,"Green seat",(.53,2.22,.095),(1.72,-2.09,.49),P['green'])
for i,y in enumerate((-2.91,-1.28)):
    for j,x in enumerate((1.52,1.94)):
        r(bench,"Bench leg %d %d"%(i,j),(x,y,.025),(x,y,.45),.019,(.055,.085,.075))
    r(bench,"Crossbar "+str(i),(1.52,y,.17),(1.94,y,.17),.016,(.055,.085,.075))
r(bench,"Long brace",(1.73,-2.91,.15),(1.73,-1.28,.15),.016,(.055,.085,.075))

lamps=asset("Hanging industrial lights")
lamp_locations=[(-.89,-1.03,2.97),(-.52,1.78,2.94),(-.25,4.1,2.97)]
for i,(x,y,z) in enumerate(lamp_locations):
    r(lamps,"Suspension "+str(i),(x,y,z+.12),(x,y,3.46),.018,(.12,.14,.12))
    # Filled stepped bell profile, with broad lower white lip.
    for j,(rad,h) in enumerate(((.255,.035),(.235,.045),(.205,.045),(.16,.05),(.105,.055))):
        r(lamps,"Shade %d tier %d"%(i,j),(x,y,z+j*.037),(x,y,z+j*.037+h),rad,(.75,.77,.69))
    r(lamps,"Luminous underside "+str(i),(x,y,z-.009),(x,y,z+.005),.225,(.97,.98,.88))

# Audit expanded semantic membership before compilation.
for name,node in scene.members.items():
    print(name, sum(n.solid is not None for n in node.traverse()))
print("Whole scene primitives:",sum(n.solid is not None for n in scene.traverse()))
realize(scene)
set_view(CAM[0],CAM[1],lens=CAM[2])

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.39,.42,.37,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.25

area_emitter((-.85,-1.0,2.90),power=165,size=.6,target=(-.6,-.5,0),color=(1,.91,.74))
area_emitter((-.45,1.8,2.88),power=125,size=.48,target=(0,2,0),color=(.91,.97,1))
area_emitter((-.2,4.05,2.89),power=95,size=.45,target=(0,3.8,.2),color=(1,.96,.84))
area_emitter((.3,-4,2.5),power=115,size=3,target=(0,2,1.0),color=(.84,.89,1))

# Existing palette materials are adjusted globally only for shared surface properties.
for mat in bpy.data.materials:
    if mat.use_nodes:
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Roughness"].default_value=.73

# Target semantic descendants explicitly; copies keep local edits isolated.
def meshes_under(label):
    roots=[o for o in bpy.data.objects if o.type=='EMPTY' and o.name==label]
    if not roots:
        roots=[o for o in bpy.data.objects if o.type=='EMPTY' and o.name.startswith(label)]
    out=[]
    for root in roots:
        out.extend(o for o in root.children_recursive if o.type=='MESH')
    assert out, "Missing semantic material target: "+label
    return list(set(out))

for ob in meshes_under("Architecture"):
    for slot in ob.material_slots:
        if slot.material:
            col=slot.material.diffuse_color
            if abs(col[0]-P['floor'][0])<.015 and abs(col[1]-P['floor'][1])<.015:
                mat=slot.material.copy()
                slot.material=mat
                bs=mat.node_tree.nodes.get("Principled BSDF")
                if bs:
                    bs.inputs["Roughness"].default_value=.37

for ob in meshes_under("Hanging industrial lights"):
    for slot in ob.material_slots:
        if slot.material and slot.material.diffuse_color[0]>.9:
            mat=slot.material.copy()
            slot.material=mat
            bs=mat.node_tree.nodes.get("Principled BSDF")
            if bs:
                bs.inputs["Emission Color"].default_value=(1,.96,.83,1)
                bs.inputs["Emission Strength"].default_value=2.5

sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0.15
