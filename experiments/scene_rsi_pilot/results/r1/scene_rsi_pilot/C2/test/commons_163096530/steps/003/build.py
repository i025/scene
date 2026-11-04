from sceneact import *
import bpy

# Evidence/ownership ledger, approximate reference pixels:
# Architecture: left/back corner (231,66), back floor around y=231.
# Near bunk (0,94)-(208,307), far bunk (179,111)-(273,266).
# Wardrobe (276,116)-(340,233), fireplace (346,132)-(462,237).
# Radiator (417,191)-(440,229), bin (440,215)-(459,239).
# Foreground bunk crops x~470 through the full image height.
# Beds obscure left wall; their mattresses sit on their own decks.
# Wardrobe/bin/bunks stand on floor; radiator leans on hearth.
# Wall clock and fixtures are uncertain identifications.
#
# Measured evidence: two successful executions, reported elapsed 13.592/13.23 s.
# Visual estimates for step 2: corner ~(274,90), wardrobe ~(307,180),
# fireplace ~(406,189), near outer post x~200, right foreground crop x~475.
# Reference corner is left/up; near bed is still wider; far furniture is smaller.
# Vertical posts and floor convergence are plausible but not calibrated.
# Inventory is present; wardrobe partly overlaps far bunk in projection.
# No owner is moved to expose it. Radiator/hearth contact remains approximate.
#
# Selected family: MATERIAL APPEARANCE ONLY. Step 2 has pale gray metal,
# light tan timbers and floor, versus dark metal and brown wood in reference.
# Reduce reflectance of those identified material scopes, retaining camera,
# all geometry, lighting, bedding and stone. Prediction: dark frame silhouettes,
# stronger wall-timber separation and a darker floor. All geometric anchors
# and foreground crops should remain unchanged. Photographic color is uncertain.

CAMERA = dict(position=(4.0,-3.8,1.72),
              target=(.5,6.4,1.10),lens=34)
ROOM = dict(width=5.35,depth=6.7,height=3.05)
BED = dict(length=2.16,width=1.04,lower=.51,upper=1.66,post_top=2.13)
POSES = dict(near=(-.06,.50),far=(-.06,2.43))

# Appearance correction is confined to identified wood and metal finishes.
C = dict(plaster=(.67,.67,.43),left=(.71,.70,.55),
         ceiling=(.61,.63,.44),timber=(.055,.032,.012),
         floor=(.12,.066,.027),metal=(.018,.025,.028),
         sheets=(.84,.85,.80),white=(.94,.94,.87),
         blanket=(.49,.57,.61),oak=(.19,.085,.023),
         stone=(.43,.42,.33),soot=(.105,.095,.07))
FLOOR_COLORS=[(.12,.067,.030),(.15,.087,.038),
              (.095,.050,.021),(.13,.073,.029)]
scene=Scene("Historic dormitory")

def B(owner,name,size,center,color):
    return owner.include(name,box(size,center=center,color=color))

def R(owner,name,start,end,radius=.018,color=None):
    return owner.include(name,rod(radius=radius,start=start,end=end,
                                  color=color or C['metal']))

# architecture -> all fixed support surfaces, boards, timber and trim.
# Floor surface z=0, back wall inside face y=6.7.
architecture=Asset("Architecture")
scene.include("architecture",architecture)
B(architecture,"floor_substrate",(5.55,9,.10),(2.6,2.3,-.07),C['floor'])
for i in range(23):
    B(architecture,f"floorboard_{i}",(.237,8.9,.045),
      (-.075+i*.241,2.3,-.0225),FLOOR_COLORS[i%4])
B(architecture,"left_plaster",(.14,8.8,3.1),(-.14,2.35,1.55),C['left'])
B(architecture,"back_plaster",(5.65,.16,3.1),(2.6,6.79,1.55),C['plaster'])
B(architecture,"ceiling",(5.65,8.8,.12),(2.6,2.35,3.11),C['ceiling'])
for i,y in enumerate([-1.7,.05,1.88,3.75,5.25,6.62]):
    B(architecture,f"wall_upright_{i}",(.15,.13,3.05),
      (-.035,y,1.525),C['timber'])
for i,z in enumerate([.12,1.16,2.32,3]):
    B(architecture,f"wall_horizontal_{i}",(.14,8.7,.12),
      (-.025,2.35,z),C['timber'])
for i,y in enumerate([1.25,4.6]):
    B(architecture,f"ceiling_beam_{i}",(5.5,.19,.21),
      (2.6,y,2.99),C['timber'])
B(architecture,"back_skirt",(5.35,.055,.12),(2.6,6.675,.06),C['timber'])

# make_bunk -> separate near_bunk, far_bunk, foreground_bunk owners.
# Attached frame, bedding, rails and ladder move together.
# Mattress support uses deck surfaces BED lower/upper, not guard-rail AABBs.
def make_bunk(name,x0,yc,length=None,width=None):
    length=length or BED['length']
    width=width or BED['width']
    a=Asset(name)
    x1=x0+length
    ya,yb=yc-width/2,yc+width/2
    for ix,x in enumerate([x0,x1]):
        for iy,y in enumerate([ya,yb]):
            R(a,f"post_{ix}_{iy}",(x,y,.025),(x,y,BED['post_top']),.026)
            B(a,f"foot_{ix}_{iy}",(.09,.085,.025),(x,y,.013),(.10,.11,.09))
            a.include(f"cap_{ix}_{iy}",ball(.030,
                      center=(x,y,BED['post_top']),color=C['metal']))
    for level,z in enumerate([BED['lower'],BED['upper']]):
        B(a,f"deck_{level}",(length,width,.055),
          ((x0+x1)/2,yc,z-.027),C['metal'])
        for iy,y in enumerate([ya,yb]):
            R(a,f"long_frame_{level}_{iy}",(x0,y,z),(x1,y,z),.023)
        B(a,f"mattress_{level}",(length-.075,width-.065,.13),
          ((x0+x1)/2,yc,z+.067),C['sheets'])
        B(a,f"sheet_top_{level}",(length-.06,width-.05,.025),
          ((x0+x1)/2,yc,z+.145),C['white'])
        B(a,f"folded_blanket_{level}",(.40,width-.045,.035),
          (x1-.26,yc,z+.175),C['blanket'])
        pillow=a.include(f"pillow_{level}",ball(.23,
                         center=(x0+.32,yc,z+.205),color=C['white']))
        pillow.resize((1.12,1.65,.28),pivot=(x0+.32,yc,z+.205))
        for ix,x in enumerate([x0,x1]):
            for j,dz in enumerate([.25,.43]):
                R(a,f"end_rail_{level}_{ix}_{j}",
                  (x,ya,z+dz),(x,yb,z+dz),.017)
    for iy,y in enumerate([ya,yb]):
        for j,z in enumerate([1.94,2.055]):
            R(a,f"guard_{iy}_{j}",(x0,y,z),(x1,y,z),.016)
    lx=x1+.025
    for i,y in enumerate([yc-.30,yc+.30]):
        R(a,f"ladder_side_{i}",(lx,y,.10),(lx,y,1.96),.019)
    for j,z in enumerate([.35,.66,.97,1.28,1.59]):
        R(a,f"ladder_rung_{j}",(lx,yc-.30,z),(lx,yc+.30,z),.016)
    return a

for name,(x,y) in POSES.items():
    scene.include(f"{name}_bunk",make_bunk(f"{name.title()} bunk",x,y))

foreground=make_bunk("Foreground cropped bunk",4.30,-.65,2.12,1.02)
scene.include("foreground_bunk",foreground)
B(foreground,"warm_wood_end_panel",(.055,.93,1.97),
  (4.28,-.65,1.04),(.25,.115,.032))

# wardrobe -> floor-supported case and all attached panels/hardware.
# Separate dimensions/pose retained; only wood palette corrected.
ward=Asset("Oak wardrobe")
scene.include("wardrobe",ward)
wx,wy=1.63,6.36
ww,wd,wh=.80,.48,1.75
B(ward,"back",(ww,.045,wh),(wx,wy+wd/2-.02,wh/2+.06),(.09,.040,.010))
for i,x in enumerate([wx-ww/2+.045,wx+ww/2-.045]):
    B(ward,f"side_{i}",(.09,wd,wh),(x,wy,wh/2+.06),C['oak'])
    for j,y in enumerate([wy-wd/2+.045,wy+wd/2-.045]):
        B(ward,f"foot_{i}_{j}",(.10,.10,.10),(x,y,.05),(.12,.05,.012))
B(ward,"base",(ww+.04,wd+.04,.10),(wx,wy,.13),C['oak'])
B(ward,"cornice",(ww+.12,wd+.10,.08),(wx,wy,wh+.10),(.15,.065,.018))
B(ward,"middle_shelf",(ww-.12,wd-.03,.055),(wx,wy,.73),C['oak'])
B(ward,"center_divider",(.05,wd-.03,wh-.08),(wx+.02,wy,.91),C['oak'])
B(ward,"left_door",(.35,.055,1.48),(wx-.20,wy-wd/2-.01,.90),(.23,.105,.028))
for i,z in enumerate([.51,1.26]):
    B(ward,f"left_inset_{i}",(.26,.018,.58),
      (wx-.20,wy-wd/2-.045,z),(.17,.072,.018))
B(ward,"lower_right_door",(.31,.05,.53),(wx+.205,wy-wd/2,.435),C['oak'])
R(ward,"hanging_bar",(wx+.07,wy-.04,1.66),(wx+.32,wy-.04,1.66),.012)
for i in range(3):
    x=wx+.10+i*.075
    R(ward,f"hook_{i}",(x,wy-.04,1.65),(x,wy-.04,1.57),.009)
for i,(x,z) in enumerate([(wx-.07,.91),(wx+.30,.48)]):
    ward.include(f"knob_{i}",ball(.018,center=(x,wy-wd/2-.06,z),
                                  color=(.13,.11,.06)))

# fireplace -> hearth, carved curved surround, ash and masonry.
# Geometry and stone material retained; hearth top z=.065.
fire=Asset("Stone fireplace")
scene.include("fireplace",fire)
fx,fy=3.47,6.49
B(fire,"hearth",(1.92,.85,.065),(fx,6.25,.0325),(.29,.28,.23))
B(fire,"dark_fireback",(1.32,.06,1.10),(fx,6.66,.61),C['soot'])
outer=box((1.83,.27,1.47),center=(fx,fy,.80),color=C['stone'])
lower_cut=box((1.28,.75,.94),center=(fx,fy,.48))
arch_cut=rod(radius=.64,start=(fx,fy-.40,.94),end=(fx,fy+.40,.94))
arch_cut.resize((1,1,.36),pivot=(fx,fy,.94))
fire.include("carved_surround",subtract(outer,lower_cut,arch_cut))
B(fire,"mantel_cap",(1.91,.32,.105),(fx,fy-.015,1.52),(.49,.48,.39))
for row in range(6):
    for col in range(4):
        xx=fx-.48+col*.30+(row%2)*.075
        if xx<fx+.60:
            B(fire,f"firebrick_{row}_{col}",(.275,.07,.12),
              (xx,6.61,.17+row*.145),
              [(.21,.20,.15),(.25,.235,.18),(.16,.155,.12)][(row+col)%3])
for side in [-1,1]:
    for j in range(3):
        B(fire,f"jamb_joint_{side}_{j}",(.265,.008,.013),
          (fx+side*.78,fy-.139,.35+j*.35),(.32,.32,.26))
B(fire,"ash",(1.06,.38,.025),(fx,6.39,.09),(.12,.12,.10))

# radiator -> independent loose hearth-supported owner, lean unchanged.
radiator=Asset("Leaning radiator")
scene.include("radiator",radiator)
rx,ry=3.98,6.18
for i in range(8):
    x=rx-.13+i*.037
    R(radiator,f"fin_{i}",(x,ry,.10),(x,ry+.11,.60),.012,(.66,.68,.62))
for j,z in enumerate([.13,.57]):
    y=ry+(z-.10)*.22
    R(radiator,f"header_{j}",(rx-.15,y,z),(rx+.15,y,z),.018,(.56,.59,.54))

# waste_bin -> separate floor-supported owner.
bin_asset=Asset("Small waste bin")
scene.include("waste_bin",bin_asset)
R(bin_asset,"body",(4.34,6,.02),(4.34,6,.27),.085,(.075,.085,.078))
R(bin_asset,"rim",(4.34,6,.26),(4.34,6,.275),.092,(.16,.17,.15))

# wall_clock/fixtures -> uncertain independent wall-mounted objects.
clock=Asset("Round wall fitting")
scene.include("wall_clock",clock)
R(clock,"rim",(1.71,6.675,2.17),(1.71,6.64,2.17),.105,(.45,.49,.41))
R(clock,"face",(1.71,6.637,2.17),(1.71,6.629,2.17),.087,(.63,.65,.54))
R(clock,"hand",(1.71,6.619,2.17),(1.69,6.619,2.22),.004,(.32,.35,.28))
for i,y in enumerate([.65,3.15,5.55]):
    fixture=Asset(f"Wall fixture {i}")
    B(fixture,"mount",(.075,.13,.24),(.055,y,2.32),(.25,.29,.25))
    B(fixture,"small_face",(.015,.075,.095),(.102,y,2.32),(.52,.54,.43))
    scene.include(f"wall_fixture_{i}",fixture)

# Inline pre-execution self-review:
# All major semantic owners and their dependent components retained.
# Architecture/camera anchors fixed; no geometry changed to adjust appearance.
# Floor, deck and hearth supports explicit; approximate contacts not certified.
# Around a few hundred primitives, mostly bunk rods; 23 boards and <=24 bricks.
# No dense cloth ornament, sampled straight tubes or costly fillet expansions.
# Positive finite dimensions, distinct rod endpoints, unique loop include slots.
# All geometry is inside SceneAct graph; curved fireplace opening retained.
# Realize precedes camera/world/lights. Surface variation resolves known markers,
# asserts nonempty descendants and copies mesh/material data before editing.
# Non-target appearance values, transforms and lighting remain as in step 2.
realize(scene)

def add_surface_variation(slot,scale,strength,distance):
    marker=bpy.data.objects.get(slot)
    assert marker is not None,slot
    meshes=[o for o in marker.children_recursive if o.type=='MESH']
    assert meshes,slot
    for ob in meshes:
        if not ob.data.materials:
            continue
        ob.data=ob.data.copy()
        for index,material in enumerate(list(ob.data.materials)):
            if material is None:
                continue
            mat=material.copy()
            ob.data.materials[index]=mat
            mat.use_nodes=True
            nt=mat.node_tree
            bsdf=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if bsdf is None:
                continue
            bsdf.inputs['Roughness'].default_value=.83
            noise=nt.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=scale
            noise.inputs['Detail'].default_value=2
            bump=nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=strength
            bump.inputs['Distance'].default_value=distance
            nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])

add_surface_variation("architecture",8,.22,.035)
add_surface_variation("fireplace",18,.35,.025)
add_surface_variation("wardrobe",7,.17,.018)

set_view(**CAMERA)
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new("World")
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.60,.51,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.42
area_emitter((3.8,-.9,2.7),power=750,size=3.8,
             target=(1.2,3.2,.7),color=(1,.95,.80))
area_emitter((1.7,3.1,2.8),power=150,size=3,
             target=(2.7,6.2,1),color=(.91,.94,1))
