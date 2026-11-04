from sceneact import *
import bpy
import math

# Evidence ledger (approximate pixels in the 512 x 341 reference):
# Left plaster/timber wall: (0,0)-(232,255); back corner near (231,66).
# Two complete metal bunks: near (0,94)-(208,307), far (179,111)-(273,266).
# Wardrobe: (276,116)-(340,233), on the floor against the back wall.
# Stone fireplace: (346,132)-(462,237), dark opening and a low hearth.
# Small leaning radiator: (417,191)-(440,229), supported by hearth.
# Waste bin: (440,215)-(459,239), on floor.
# Cropped foreground bunk: (466,0)-(512,341); retain this occluder.
# Floorboards converge toward back wall; wall timbers and bed posts remain vertical.
# Bed mattresses rest on their own decks, rails/posts belong to each bed owner.
# Scale is relative; far bed count, radiator identity and wall fixtures are uncertain.

# Camera parameters are independent of architecture and furniture dimensions.
CAMERA = dict(position=(3.15, -2.0, 1.72),
              target=(0.40, 6.4, 1.35), lens=32)
ROOM = dict(width=5.35, depth=6.7, height=3.05)
BED = dict(length=2.16, width=1.04, lower=0.51, upper=1.66,
           post_top=2.13)
POSES = dict(near=(-0.06, 0.50), far=(-0.06, 2.43))
C = dict(plaster=(0.67,0.67,0.43), left=(0.71,0.70,0.55),
         ceiling=(0.61,0.63,0.44), timber=(0.19,0.14,0.075),
         floor=(0.34,0.23,0.12), metal=(0.105,0.13,0.13),
         sheets=(0.84,0.85,0.80), white=(0.94,0.94,0.87),
         blanket=(0.49,0.57,0.61), oak=(0.34,0.20,0.075),
         stone=(0.43,0.42,0.33), soot=(0.105,0.095,0.07))
scene = Scene("Historic dormitory")

def B(owner, name, size, center, color):
    return owner.include(name, box(size, center=center, color=color))

def R(owner, name, start, end, radius=0.018, color=None):
    return owner.include(name, rod(radius=radius, start=start, end=end,
                                  color=color or C['metal']))

# Architecture owner: floor top z=0, inside back wall face y=6.7.
architecture = Asset("Architecture")
scene.include("architecture", architecture)
B(architecture, "floor_substrate", (5.55,9.0,.10), (2.6,2.3,-.07), C['floor'])
for i in range(23):
    shade = [(.34,.235,.135),(.39,.275,.16),(.30,.205,.115),
             (.36,.25,.14)][i % 4]
    B(architecture, f"floorboard_{i}", (.237,8.9,.045),
      (-.075+i*.241,2.3,-.0225), shade)
B(architecture,"left_plaster",(.14,8.8,3.1),(-.14,2.35,1.55),C['left'])
B(architecture,"back_plaster",(5.65,.16,3.1),(2.6,6.79,1.55),C['plaster'])
B(architecture,"ceiling",(5.65,8.8,.12),(2.6,2.35,3.11),C['ceiling'])
for i,y in enumerate([-1.7,.05,1.88,3.75,5.25,6.62]):
    B(architecture,f"wall_upright_{i}",(.15,.13,3.05),(-.035,y,1.525),C['timber'])
for i,z in enumerate([.12,1.16,2.32,3.00]):
    B(architecture,f"wall_horizontal_{i}",(.14,8.7,.12),(-.025,2.35,z),C['timber'])
for i,y in enumerate([1.25,4.6]):
    B(architecture,f"ceiling_beam_{i}",(5.5,.19,.21),(2.6,y,2.99),C['timber'])
B(architecture,"back_skirt",(5.35,.055,.12),(2.6,6.675,.06),C['timber'])

# Each bunk owns posts, feet, mattress supports, bedding, guards and ladder.
# Actual mattress support heights are lower/upper, independent of rail AABBs.
def make_bunk(name, x0, yc, length=None, width=None):
    length = length or BED['length']
    width = width or BED['width']
    a = Asset(name)
    x1=x0+length
    ya,yb=yc-width/2,yc+width/2
    for ix,x in enumerate([x0,x1]):
        for iy,y in enumerate([ya,yb]):
            R(a,f"post_{ix}_{iy}",(x,y,.025),(x,y,BED['post_top']),.026)
            B(a,f"foot_{ix}_{iy}",(.09,.085,.025),(x,y,.013),(.28,.29,.25))
            a.include(f"cap_{ix}_{iy}",ball(.030,center=(x,y,BED['post_top']),
                                          color=C['metal']))
    for level,z in enumerate([BED['lower'],BED['upper']]):
        B(a,f"deck_{level}",(length,width,.055),((x0+x1)/2,yc,z-.027),C['metal'])
        for iy,y in enumerate([ya,yb]):
            R(a,f"long_frame_{level}_{iy}",(x0,y,z),(x1,y,z),.023)
        B(a,f"mattress_{level}",(length-.075,width-.065,.13),
          ((x0+x1)/2,yc,z+.067),C['sheets'])
        B(a,f"sheet_top_{level}",(length-.06,width-.05,.025),
          ((x0+x1)/2,yc,z+.145),C['white'])
        B(a,f"folded_blanket_{level}",(.40,width-.045,.035),
          (x1-.26,yc,z+.175),C['blanket'])
        pillow = a.include(f"pillow_{level}",ball(.23,
                            center=(x0+.32,yc,z+.205),color=C['white']))
        pillow.resize((1.12,1.65,.28),pivot=(x0+.32,yc,z+.205))
        # End rails and the upper safety rails preserve open spaces.
        for ix,x in enumerate([x0,x1]):
            for j,dz in enumerate([.25,.43]):
                R(a,f"end_rail_{level}_{ix}_{j}",(x,ya,z+dz),(x,yb,z+dz),.017)
    for iy,y in enumerate([ya,yb]):
        for j,z in enumerate([1.94,2.055]):
            R(a,f"guard_{iy}_{j}",(x0,y,z),(x1,y,z),.016)
    # Ladder attached to the room-facing short end.
    lx=x1+.025
    for i,y in enumerate([yc-.30,yc+.30]):
        R(a,f"ladder_side_{i}",(lx,y,.10),(lx,y,1.96),.019)
    for j,z in enumerate([.35,.66,.97,1.28,1.59]):
        R(a,f"ladder_rung_{j}",(lx,yc-.30,z),(lx,yc+.30,z),.016)
    return a

for name,(x,y) in POSES.items():
    scene.include(f"{name}_bunk",make_bunk(f"{name.title()} bunk",x,y))

# Foreground bunk owner extends outside the right crop.
foreground = make_bunk("Foreground cropped bunk",4.30,-.65,2.12,1.02)
scene.include("foreground_bunk",foreground)
B(foreground,"warm_wood_end_panel",(.055,.93,1.97),(4.28,-.65,1.04),
  (.42,.25,.10))

# Wardrobe: floor-supported case, open upper compartment and lower panels.
ward = Asset("Oak wardrobe")
scene.include("wardrobe",ward)
wx,wy=1.63,6.36
ww,wd,wh=.80,.48,1.75
B(ward,"back",(ww,.045,wh),(wx,wy+wd/2-.02,wh/2+.06),(.20,.12,.045))
for i,x in enumerate([wx-ww/2+.045,wx+ww/2-.045]):
    B(ward,f"side_{i}",(.09,wd,wh),(x,wy,wh/2+.06),C['oak'])
    for j,y in enumerate([wy-wd/2+.045,wy+wd/2-.045]):
        B(ward,f"foot_{i}_{j}",(.10,.10,.10),(x,y,.05),(.25,.14,.045))
B(ward,"base",(ww+.04,wd+.04,.10),(wx,wy,.13),C['oak'])
B(ward,"cornice",(ww+.12,wd+.10,.08),(wx,wy,wh+.10),(.29,.17,.06))
B(ward,"middle_shelf",(ww-.12,wd-.03,.055),(wx,wy,.73),C['oak'])
B(ward,"center_divider",(.05,wd-.03,wh-.08),(wx+.02,wy,.91),C['oak'])
B(ward,"left_door",(.35,.055,1.48),(wx-.20,wy-wd/2-.01,.90),(.39,.235,.085))
for i,z in enumerate([.51,1.26]):
    B(ward,f"left_inset_{i}",(.26,.018,.58),(wx-.20,wy-wd/2-.045,z),(.32,.185,.065))
B(ward,"lower_right_door",(.31,.05,.53),(wx+.205,wy-wd/2,.435),C['oak'])
R(ward,"hanging_bar",(wx+.07,wy-.04,1.66),(wx+.32,wy-.04,1.66),.012)
for i in range(3):
    x=wx+.10+i*.075
    R(ward,f"hook_{i}",(x,wy-.04,1.65),(x,wy-.04,1.57),.009)
for i,(x,z) in enumerate([(wx-.07,.91),(wx+.30,.48)]):
    ward.include(f"knob_{i}",ball(.018,center=(x,wy-wd/2-.06,z),
                                  color=(.13,.11,.06)))

# Fireplace owner: stone jambs, curved opening, fireback and hearth.
fire = Asset("Stone fireplace")
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
# Sparse irregular masonry inside the opening; the dark mortar remains visible.
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

# Loose radiator leans back above the actual hearth surface.
radiator=Asset("Leaning radiator")
scene.include("radiator",radiator)
rx,ry=3.98,6.18
for i in range(8):
    x=rx-.13+i*.037
    R(radiator,f"fin_{i}",(x,ry,.10),(x,ry+.11,.60),.012,
      (.66,.68,.62))
for j,z in enumerate([.13,.57]):
    y=ry+(z-.10)*.22
    R(radiator,f"header_{j}",(rx-.15,y,z),(rx+.15,y,z),.018,(.56,.59,.54))

bin_asset=Asset("Small waste bin")
scene.include("waste_bin",bin_asset)
R(bin_asset,"body",(4.34,6.00,.02),(4.34,6.00,.27),.085,(.075,.085,.078))
R(bin_asset,"rim",(4.34,6.00,.26),(4.34,6.00,.275),.092,(.16,.17,.15))

# Small wall fittings are independent Assets supported by wall faces.
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

# Pre-execution self-review:
# Inventory owners and actual supports are explicit above. Architecture carries timbers;
# beds carry every attached part; wardrobe/fireplace/radiator/bin remain editable owners.
# Anchors: far left/back junction around (231,66), wardrobe near (308,176),
# near bed outer post around (138,205), right foreground crop around x=477.
# These are visual hypotheses; no calibration or rendered feedback is available.
# About 350 primitives: bed rail/post families dominate; floor uses only 23 strips.
# No dense textile decoration, fillet expansions or densely sampled straight tubing.
# Dimensions are positive; rods have distinct endpoints; all loop slots are unique.
# Boolean opening cutters are contained in the fireplace owner's carved surround.
# Realize precedes camera, world, lighting and scoped material edits.
realize(scene)

# Restrained procedural variation, scoped through known semantic markers.
# Material copies preserve other owners even when SceneAct shares finishes.
def add_surface_variation(slot, scale, strength, distance):
    marker=bpy.data.objects.get(slot)
    assert marker is not None, slot
    meshes=[o for o in marker.children_recursive if o.type=='MESH']
    assert meshes, slot
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
             target=(1.2,3.2,.7),color=(1.0,.95,.80))
area_emitter((1.7,3.1,2.8),power=150,size=3.0,
             target=(2.7,6.2,1.0),color=(.91,.94,1.0))
