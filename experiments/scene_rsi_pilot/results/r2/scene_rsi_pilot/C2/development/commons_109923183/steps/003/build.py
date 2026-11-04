from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Inventory: chaise, four curved feet, high upholstered head, two side wings,
# one loose pillow, green label, cropped foreground cane chair; paneled wall,
# right pilaster, parquet floor, left window and curtains.
# Near/far order: foreground chair, front apron, cushion/pillow, head, wall.
# Arbitrary scale; hidden construction and dimensions remain hypotheses.
#
# Revision family: APPEARANCE.
# Visual observations: step 2 improves chaise framing and foreground cropping.
# Wall moldings still slope more than the reference, but the strongest remaining
# appearance errors are the bright discontinuous floor and missing textile pattern.
# Source inspection: Blender names are primitive names, so the previous
# name-based fabric assignment did not reliably identify upholstered descendants.
# Affected modules: floor finish and upholstered finishes. Register bounds of
# semantic fabric parts before realization to identify their compiled descendants.
# Floor base and boards receive one continuous world-coordinate wood finish.
# Camera, architecture, furniture geometry, attachments and supports are preserved.
# Risk: procedural textile detail may alias; keep contrast restrained.
# Runtime facts: steps 1 and 2 succeeded; step 2 reported 8.42 seconds render time.
# No numerical image calibration or validation of this revision is claimed.

scene = Scene('Paneled room with chaise')
L, W = 2.35, .94
seat_z, seat_h = .72, .25
wood = (.34, .39, .30)
gold = (.62, .54, .37)
cream = (.80, .745, .63)
wall = (.70, .685, .61)
trim = (.79, .77, .68)
CAMERA_POSITION = (1.25, -4.65, 3.48)
CAMERA_TARGET = (-.02, .02, .94)
CAMERA_LENS = 48
fabric_regions = []

def tube(parent, key, pts, radius, color):
    assert radius > 0
    assert all(sum((a[k]-b[k])**2 for k in range(3)) > 1e-15
               for a, b in zip(pts, pts[1:]))
    return parent.include(key, sweep_tube(points=pts, radius=radius, color=color))

def beam(parent, key, size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    return parent.include(key, box(size=size, center=center, color=color))

def upholstery(parent, key, node):
    attached = parent.include(key, node)
    lo, hi = attached.limits
    fabric_regions.append((tuple(lo), tuple(hi)))
    return attached

beam(scene, 'floor', (9,8,.12), (0,0,-.08), (.20,.105,.06))
parquet = Asset('Parquet')
random.seed(9)
for i in range(-8,9):
    for j in range(-7,6):
        c = random.uniform(.85,1.13)
        board = box((.60,.142,.012), center=(i*.43,j*.43,-.012),
                    color=(.25*c,.135*c,.075*c))
        board.turn('z',45 if (i+j)%2 == 0 else -45)
        parquet.include(f'board_{i}_{j}',board)
scene.include('parquet',parquet)

beam(scene,'rear_wall',(8,.15,3.7),(0,1.15,1.80),wall)
for n,z,h,d in [
    ('base',.10,.17,.065),('base_lip',.21,.035,.09),
    ('dado_lower',1.76,.045,.055),('dado',1.84,.065,.075),
    ('upper_band',2.17,.035,.04),('upper_band2',2.40,.025,.035)]:
    beam(scene,n,(8,d,h),(0,1.045,z),trim)

def wall_panel(name,x0,x1,z0,z1):
    p = Asset(name)
    for k,inset in enumerate((0,.035)):
        yy = 1.055-k*.012
        tube(p,f'border_{k}',[
            (x0+inset,yy,z0+inset),(x1-inset,yy,z0+inset),
            (x1-inset,yy,z1-inset),(x0+inset,yy,z1-inset),
            (x0+inset,yy,z0+inset)],.012 if k == 0 else .008,trim)
    scene.include(name,p)

wall_panel('large_recessed_panel',-2.6,1.95,.32,1.68)
wall_panel('upper_recessed_panel',-2.6,1.95,1.99,2.9)
for i,x in enumerate((-1.65,.55)):
    beam(scene,f'wall_seam_{i}',(.008,.008,3.3),
         (x,1.067,1.65),(.45,.43,.36))
beam(scene,'right_pilaster',(.36,.36,3.3),(2.25,1,1.65),(.78,.78,.71))
beam(scene,'right_return',(1.5,.13,3.3),(3.15,1.2,1.65),(.76,.77,.70))

window = Asset('Left window and curtains')
beam(window,'window_light',(.07,1.1,3.4),(-2.45,.12,1.7),(.94,.95,.89))
for i in range(13):
    yy = -.39+i*.078
    xx = -2.35+.025*math.sin(i*1.7)
    window.include(f'curtain_fold_{i}',rod(.052,start=(xx,yy,.05),
        end=(xx-.11,yy,3.35),
        color=(.78+.025*(i%3),.72+.025*(i%3),.60+.03*(i%3))))
scene.include('window',window)

chaise = Asset('Chaise longue')
upholstery(chaise,'fabric_seat',
    fillet_box((L,W,seat_h),radius=.12,center=(.04,0,seat_z),color=cream))
beam(chaise,'seat_support',(2.23,.84,.10),(.015,0,.545),wood)
for side,yy in [('front',-.472),('rear',.472)]:
    pts = [(-1.11,yy,.63),(-.98,yy,.55),(-.72,yy,.53),
           (-.36,yy,.51),(.04,yy,.48),(.42,yy,.49),
           (.83,yy,.50),(1.12,yy,.53),(1.20,yy,.61)]
    tube(chaise,f'{side}_wood_apron',pts,.048,wood)
    tube(chaise,f'{side}_gold_upper',
         [(x,y-.003,z+.025) for x,y,z in pts],.009,gold)
    tube(chaise,f'{side}_gold_lower',
         [(x,y-.004,z-.033) for x,y,z in pts],.009,gold)
    tube(chaise,f'{side}_cushion_piping',
         [(-1.06,yy,.73),(-.6,yy,.625),(.2,yy,.62),
          (.9,yy,.625),(1.16,yy,.70)],.012,(.65,.59,.45))
tube(chaise,'foot_end_frame',[(1.17,-.46,.55),(1.22,-.30,.57),
     (1.24,0,.58),(1.22,.30,.57),(1.17,.46,.55)],.037,wood)

for ix,x in enumerate((-.96,1.04)):
    for iy,y in enumerate((-.37,.37)):
        sign = -1 if x < 0 else 1
        yy = y*1.10
        pts = [(x,y,.56),(x+sign*.045,yy,.43),
               (x+sign*.015,yy,.26),(x-sign*.03,yy,.10),
               (x+sign*.015,yy,.065)]
        tube(chaise,f'leg_{ix}_{iy}',pts,.033,wood)
        tube(chaise,f'leg_gilt_{ix}_{iy}',
             [(a,b-.021,c) for a,b,c in pts],.008,gold)
        chaise.include(f'foot_{ix}_{iy}',ball(.043,center=pts[-1],color=wood))

for i in range(16):
    yy = -.44+i*.0585
    top = 1.44+.17*math.sqrt(max(0,1-(yy/.47)**2))
    bottom = .70
    xx = -1.09-.16*((top-bottom)/.9)
    p = fillet_box((.14,.070,top-bottom),radius=.034,
                  center=(xx,yy,(top+bottom)/2),color=cream)
    p.turn('y',-11)
    upholstery(chaise,f'fabric_head_{i}',p)

head_outline = [
    (-1.11,-.48,.72),(-1.25,-.49,1.19),(-1.31,-.43,1.44),
    (-1.32,-.28,1.58),(-1.33,-.08,1.65),(-1.32,.12,1.62),
    (-1.29,.32,1.51),(-1.23,.46,1.38),(-1.08,.49,1.15),(-.98,.48,.79)]
tube(chaise,'head_carved_wood',head_outline,.035,wood)
tube(chaise,'head_gilding',
     [(x+.022,y-.006,z) for x,y,z in head_outline],.010,gold)
for side,yy in [('near',-.46),('far',.46)]:
    outline = [(-1.12,yy,1.35),(-.97,yy,1.22),(-.77,yy,1.12),
               (-.56,yy,1.10),(-.48,yy,1.14)]
    for k in range(10):
        t = k/9
        x = -1.10+.58*t
        top = 1.32-.27*t+.07*t*t
        low = .68
        upholstery(chaise,f'fabric_{side}_wing_{k}',
            fillet_box((.074,.095,top-low),radius=.035,
                       center=(x,yy,(top+low)/2),color=cream))
    tube(chaise,f'{side}_arm_wood',outline,.031,wood)
    tube(chaise,f'{side}_arm_gold',
         [(x,y-.015,z+.014) for x,y,z in outline],.009,gold)
    tube(chaise,f'{side}_wing_lower',
         [(-1.12,yy,.76),(-.96,yy,.64),(-.70,yy,.61),(-.51,yy,.68)],
         .031,wood)

for label_name,loc,rad in [
    ('crest',(-1.33,-.10,1.65),.048),('apron',(.12,-.51,.485),.065)]:
    for j in range(7):
        a = j*2*math.pi/7
        chaise.include(f'{label_name}_petal_{j}',ball(rad*.39,
            center=(loc[0]+math.cos(a)*rad*.60,loc[1]-.012,
                    loc[2]+math.sin(a)*rad*.60),color=gold))

pillow = Asset('Loose ivory pillow')
pillow.include('fabric_pillow',fillet_box((.24,.63,.63),radius=.115,
               center=(-.89,-.05,1.17),color=(.90,.84,.69)))
pillow.turn('y',-19)
pillow.turn('x',-8)
chaise.include('pillow',pillow)
label = Asset('Green label')
beam(label,'card',(.105,.185,.006),(.69,.14,.856),(.055,.22,.17))
for i in range(3):
    beam(label,f'printing_{i}',(.047,.003,.002),
         (.69,.12+i*.018,.860),(.73,.78,.65))
chaise.include('label',label)
scene.include('chaise',chaise)

chair = Asset('Foreground cane chair')
cx,cy,cz = -1.03,-1.63,.46
beam(chair,'cane_base',(.58,.58,.04),(cx,cy,cz),(.46,.35,.20))
for i in range(21):
    q = -.26+i*.026
    tube(chair,f'cane_x_{i}',
         [(cx-.27,cy+q,cz+.025),(cx+.27,cy+q,cz+.025)],
         .0034,(.65,.51,.31))
    tube(chair,f'cane_y_{i}',
         [(cx+q,cy-.27,cz+.027),(cx+q,cy+.27,cz+.027)],
         .0034,(.65,.51,.31))
tube(chair,'seat_frame',[
    (cx-.32,cy-.31,cz),(cx+.32,cy-.31,cz),(cx+.32,cy+.31,cz),
    (cx-.32,cy+.31,cz),(cx-.32,cy-.31,cz)],.042,wood)
for i,xx in enumerate((cx-.27,cx+.27)):
    for j,yy in enumerate((cy-.26,cy+.26)):
        tube(chair,f'leg_{i}_{j}',[(xx,yy,cz),(xx,yy,.06)],.024,wood)
scene.include('foreground_chair',chair)

# Preflight: all dimensions finite/positive, fillet radii within half minimum
# dimensions, distinct rod endpoints, unique repeated keys and no bindings.
# Every movable object's supports and trim remain in its semantic assembly.
# Realization is followed by materials, world, active camera and lighting.
realize(scene)
sc = bpy.context.scene

def material(name,color,roughness):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Roughness'].default_value = roughness
    return m

# A continuous walnut finish covers the existing floor assembly, including
# exposed substrate between boards. World coordinates prevent per-board resets.
floor_mat = material('Parquet dark polished walnut',(.105,.042,.023),.34)
n = floor_mat.node_tree.nodes
l = floor_mat.node_tree.links
bs = n.get('Principled BSDF')
coord = n.new('ShaderNodeTexCoord')
mapping = n.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value[2] = math.radians(45)
l.new(coord.outputs['Object'],mapping.inputs['Vector'])
brick = n.new('ShaderNodeTexBrick')
brick.inputs['Color1'].default_value = (.10,.037,.020,1)
brick.inputs['Color2'].default_value = (.19,.083,.043,1)
brick.inputs['Mortar'].default_value = (.077,.027,.016,1)
brick.inputs['Scale'].default_value = 1
brick.inputs['Mortar Size'].default_value = .0015
brick.inputs['Mortar Smooth'].default_value = .001
brick.inputs['Brick Width'].default_value = .64
brick.inputs['Row Height'].default_value = .14
l.new(mapping.outputs['Vector'],brick.inputs['Vector'])
grain_mapping = n.new('ShaderNodeVectorMath')
grain_mapping.operation = 'MULTIPLY'
grain_mapping.inputs[1].default_value = (4,95,2)
l.new(mapping.outputs['Vector'],grain_mapping.inputs[0])
grain = n.new('ShaderNodeTexNoise')
grain.inputs['Scale'].default_value = 3
grain.inputs['Detail'].default_value = 2
l.new(grain_mapping.outputs[0],grain.inputs['Vector'])
grain_ramp = n.new('ShaderNodeValToRGB')
grain_ramp.color_ramp.elements[0].color = (.48,.40,.35,1)
grain_ramp.color_ramp.elements[1].color = (.95,.87,.77,1)
l.new(grain.outputs['Fac'],grain_ramp.inputs[0])
mix = n.new('ShaderNodeMixRGB')
mix.blend_type = 'MULTIPLY'
mix.inputs[0].default_value = .48
l.new(brick.outputs['Color'],mix.inputs[1])
l.new(grain_ramp.outputs['Color'],mix.inputs[2])
l.new(mix.outputs[0],bs.inputs['Base Color'])

fabric = material('Ivory rose striped upholstery',(.76,.66,.53),.86)
n = fabric.node_tree.nodes
l = fabric.node_tree.links
bs = n.get('Principled BSDF')
coord = n.new('ShaderNodeTexCoord')
wave = n.new('ShaderNodeTexWave')
wave.wave_type = 'BANDS'
wave.bands_direction = 'Y'
wave.inputs['Scale'].default_value = 7.5
wave.inputs['Distortion'].default_value = .12
l.new(coord.outputs['Object'],wave.inputs['Vector'])
ramp = n.new('ShaderNodeValToRGB')
ramp.color_ramp.interpolation = 'CONSTANT'
ramp.color_ramp.elements[0].position = 0
ramp.color_ramp.elements[0].color = (.79,.71,.61,1)
ramp.color_ramp.elements[1].position = .90
ramp.color_ramp.elements[1].color = (.54,.31,.30,1)
e = ramp.color_ramp.elements.new(.96)
e.color = (.85,.78,.66,1)
l.new(wave.outputs['Fac'],ramp.inputs[0])
l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
noise = n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 210
noise.inputs['Detail'].default_value = 2
l.new(coord.outputs['Object'],noise.inputs['Vector'])
bump = n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .12
bump.inputs['Distance'].default_value = .002
l.new(noise.outputs['Fac'],bump.inputs['Height'])
l.new(bump.outputs[0],bs.inputs['Normal'])

# Resolve compiled descendants by containment in registered semantic part
# bounds, not by shared finish color or unreliable primitive object names.
def mesh_bounds(obj):
    pts = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return ([min(p[k] for p in pts) for k in range(3)],
            [max(p[k] for p in pts) for k in range(3)])

def contained(lo,hi,region):
    rlo,rhi = region
    eps = .00015
    return all(lo[k] >= rlo[k]-eps and hi[k] <= rhi[k]+eps
               for k in range(3))

for obj in sc.objects:
    if obj.type != 'MESH':
        continue
    lo,hi = mesh_bounds(obj)
    chosen = None
    if hi[2] < -.001:
        chosen = floor_mat
    elif any(contained(lo,hi,r) for r in fabric_regions):
        chosen = fabric
    if chosen is not None:
        obj.data.materials.clear()
        obj.data.materials.append(chosen)

if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes.get('Background').inputs[0].default_value = (.72,.76,.79,1)
sc.world.node_tree.nodes.get('Background').inputs[1].default_value = .40
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
area_emitter((-3.2,-1,3.3),power=550,size=2.8,
             target=(0,0,.6),color=(1,.92,.79))
area_emitter((1,-3,3.6),power=110,size=4,
             target=(0,0,.7),color=(.88,.93,1))
sc.view_settings.view_transform = 'AgX'
