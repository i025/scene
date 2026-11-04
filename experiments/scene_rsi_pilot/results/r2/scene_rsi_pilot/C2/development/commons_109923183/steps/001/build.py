from sceneact import *
import bpy
import math
import random

# Inventory: cream upholstered chaise, carved sage-and-gold wooden frame,
# four curved feet, raised head and arms, one loose ivory pillow, green label.
# Architecture: pale paneled rear wall, right pilaster, dark parquet floor,
# bright window and hanging curtains at left. A cane chair is cropped foreground.
# Arbitrary scale: chaise length about 2.35 units. Hidden construction is hypothetical.
# Near/far order: foreground chair, chaise front rail, seat/pillow, head, wall.
# Camera and furniture parameters are independent; no calibration is assumed.

scene = Scene('Paneled room with chaise')
L, W = 2.35, .94
seat_z, seat_h = .72, .25
wood = (.34, .39, .30)
gold = (.62, .54, .37)
cream = (.80, .745, .63)
wall = (.70, .685, .61)
trim = (.79, .77, .68)

def tube(parent, key, pts, radius, color):
    parent.include(key, sweep_tube(points=pts, radius=radius, color=color))

def beam(parent, key, size, center, color):
    parent.include(key, box(size=size, center=center, color=color))

# Broad floor and inexpensive individual parquet boards.
scene.include('floor', box((9, 8, .12), center=(0, 0, -.08),
                           color=(.20, .105, .06)))
parquet = Asset('Parquet')
random.seed(9)
for i in range(-8, 9):
    for j in range(-7, 6):
        x, y = i*.43, j*.43
        c = random.uniform(.85, 1.13)
        col = (.25*c, .135*c, .075*c)
        board = box((.60, .142, .012), center=(x, y, -.012), color=col)
        board.turn('z', 45 if (i+j)%2 == 0 else -45)
        parquet.include(f'board_{i}_{j}', board)
scene.include('parquet', parquet)

# Wall with low baseboard, recessed panel outlines and upper dado bands.
scene.include('rear_wall', box((8, .15, 3.7), center=(0, 1.15, 1.80), color=wall))
for n, z, h, depth in [
    ('base', .10, .17, .065), ('base_lip', .21, .035, .09),
    ('dado_lower', 1.76, .045, .055), ('dado', 1.84, .065, .075),
    ('upper_band', 2.17, .035, .04), ('upper_band2', 2.40, .025, .035)]:
    scene.include(n, box((8, depth, h), center=(0, 1.045, z), color=trim))

def wall_panel(name, x0, x1, z0, z1):
    p = Asset(name)
    for k, inset in enumerate((0, .035)):
        yy = 1.055 - k*.012
        r = .012 if k == 0 else .008
        tube(p, f'border_{k}', [
            (x0+inset, yy, z0+inset), (x1-inset, yy, z0+inset),
            (x1-inset, yy, z1-inset), (x0+inset, yy, z1-inset),
            (x0+inset, yy, z0+inset)], r, trim)
    scene.include(name, p)

wall_panel('large_recessed_panel', -2.6, 1.95, .32, 1.68)
wall_panel('upper_recessed_panel', -2.6, 1.95, 1.99, 2.9)
for i, x in enumerate((-1.65, .55)):
    scene.include(f'wall_seam_{i}', box((.008, .008, 3.3),
                                       center=(x, 1.067, 1.65), color=(.45,.43,.36)))
scene.include('right_pilaster', box((.36,.36,3.3), center=(2.25,1.0,1.65),
                                    color=(.78,.78,.71)))
scene.include('right_return', box((1.5,.13,3.3), center=(3.15,1.2,1.65),
                                  color=(.76,.77,.70)))

# Window and curtain folds. Window remains bright but is actual geometry.
window = Asset('Left window and curtains')
beam(window, 'window_light', (.07, 1.1, 3.4), (-2.45,.12,1.7), (.94,.95,.89))
for i in range(13):
    yy = -.39 + i*.078
    xx = -2.35 + .025*math.sin(i*1.7)
    window.include(f'curtain_fold_{i}', rod(.052, start=(xx,yy,.05),
                   end=(xx-.11,yy,3.35), color=(.78+.025*(i%3), .72+.025*(i%3), .60+.03*(i%3))))
scene.include('window', window)

chaise = Asset('Chaise longue')
# Seat cushion is supported continuously by the wood apron.
chaise.include('fabric_seat', fillet_box((L,W,seat_h), radius=.12,
              center=(.04,0,seat_z), color=cream))
beam(chaise, 'seat_support', (2.23,.84,.10), (.015,0,.545), wood)

# Curved side aprons and their fine gilded edges.
for side, yy in [('front',-.472), ('rear',.472)]:
    pts = [(-1.11,yy,.63),(-.98,yy,.55),(-.72,yy,.53),
           (-.36,yy,.51),(.04,yy,.48),(.42,yy,.49),
           (.83,yy,.50),(1.12,yy,.53),(1.20,yy,.61)]
    tube(chaise, f'{side}_wood_apron', pts, .048, wood)
    tube(chaise, f'{side}_gold_upper', [(x,y-.003,z+.025) for x,y,z in pts], .009, gold)
    tube(chaise, f'{side}_gold_lower', [(x,y-.004,z-.033) for x,y,z in pts], .009, gold)
    tube(chaise, f'{side}_cushion_piping',
         [(-1.06,yy,.73),(-.6,yy,.625),(.2,yy,.62),(.9,yy,.625),(1.16,yy,.70)],
         .012, (.65,.59,.45))
tube(chaise, 'foot_end_frame', [(1.17,-.46,.55),(1.22,-.30,.57),
     (1.24,0,.58),(1.22,.30,.57),(1.17,.46,.55)], .037, wood)

# Four cabriole legs, each attached to the apron. All parts share asset ownership.
for ix, x in enumerate((-.96,1.04)):
    for iy, y in enumerate((-.37,.37)):
        sign = -1 if x < 0 else 1
        yy = y*1.10
        pts = [(x,y,.56),(x+sign*.045,yy,.43),
               (x+sign*.015,yy,.26),(x-sign*.03,yy,.10),
               (x+sign*.015,yy,.065)]
        tube(chaise, f'leg_{ix}_{iy}', pts, .033, wood)
        tube(chaise, f'leg_gilt_{ix}_{iy}',
             [(a,b-.021,c) for a,b,c in pts], .008, gold)
        chaise.include(f'foot_{ix}_{iy}', ball(.043, center=pts[-1], color=wood))

# Raised head: closely fitted upholstered strips create a shaped back,
# with a continuous wooden crest and fine inset border.
for i in range(16):
    yy = -.44 + i*.0585
    u = yy/.47
    top = 1.44 + .17*math.sqrt(max(0,1-u*u))
    bottom = .70
    xx = -1.09 - .16*((top-bottom)/.9)
    p = fillet_box((.14,.070,top-bottom), radius=.034,
                   center=(xx,yy,(top+bottom)/2), color=cream)
    p.turn('y', -11)
    chaise.include(f'fabric_head_{i}', p)
head_outline = [(-1.11,-.48,.72),(-1.25,-.49,1.19),
                (-1.31,-.43,1.44),(-1.32,-.28,1.58),
                (-1.33,-.08,1.65),(-1.32,.12,1.62),
                (-1.29,.32,1.51),(-1.23,.46,1.38),
                (-1.08,.49,1.15),(-.98,.48,.79)]
tube(chaise, 'head_carved_wood', head_outline, .035, wood)
tube(chaise, 'head_gilding', [(x+.022,y-.006,z) for x,y,z in head_outline], .010, gold)

# Upholstered side wings taper from the high head to the seat.
for side, yy in [('near',-.46),('far',.46)]:
    outline = [(-1.12,yy,1.35),(-.97,yy,1.22),
               (-.77,yy,1.12),(-.56,yy,1.10),(-.48,yy,1.14)]
    for k in range(10):
        t = k/9
        x = -1.10 + .58*t
        top = 1.32-.27*t+.07*t*t
        low = .68
        chaise.include(f'fabric_{side}_wing_{k}',
            fillet_box((.074,.095,top-low), radius=.035,
                       center=(x,yy,(top+low)/2), color=cream))
    tube(chaise, f'{side}_arm_wood', outline, .031, wood)
    tube(chaise, f'{side}_arm_gold',
         [(x,y-.015,z+.014) for x,y,z in outline], .009, gold)
    tube(chaise, f'{side}_wing_lower',
         [(-1.12,yy,.76),(-.96,yy,.64),(-.70,yy,.61),(-.51,yy,.68)],
         .031, wood)

# Restrained carved rosettes at the crest and center of the visible apron.
for label, loc, rad in [('crest',(-1.33,-.10,1.65),.048),
                        ('apron',(.12,-.51,.485),.065)]:
    for j in range(7):
        a = j*2*math.pi/7
        chaise.include(f'{label}_petal_{j}', ball(rad*.39,
            center=(loc[0]+math.cos(a)*rad*.60,loc[1]-.012,loc[2]+math.sin(a)*rad*.60),
            color=gold))

# Loose pillow: its tilt and softness are hypotheses from the single photograph.
pillow = Asset('Loose ivory pillow')
pillow.include('fabric_pillow', fillet_box((.24,.63,.63), radius=.115,
               center=(-.89,-.05,1.17), color=(.90,.84,.69)))
pillow.turn('y', -19)
pillow.turn('x', -8)
chaise.include('pillow', pillow)

# Small dark green museum label resting on the far half of the cushion.
label = Asset('Green label')
beam(label, 'card', (.105,.185,.006), (.69,.14,.856), (.055,.22,.17))
for i in range(3):
    beam(label, f'printing_{i}', (.047,.003,.002),
         (.69,.12+i*.018,.860), (.73,.78,.65))
chaise.include('label', label)
scene.include('chaise', chaise)

# Cropped foreground cane chair, with complete seat assembly and slim legs.
chair = Asset('Foreground cane chair')
cx, cy, cz = -1.03, -1.63, .46
beam(chair, 'cane_base', (.58,.58,.04), (cx,cy,cz), (.46,.35,.20))
for i in range(21):
    q = -.26+i*.026
    tube(chair, f'cane_x_{i}', [(cx-.27,cy+q,cz+.025),(cx+.27,cy+q,cz+.025)],
         .0034, (.65,.51,.31))
    tube(chair, f'cane_y_{i}', [(cx+q,cy-.27,cz+.027),(cx+q,cy+.27,cz+.027)],
         .0034, (.65,.51,.31))
tube(chair, 'seat_frame', [(cx-.32,cy-.31,cz),(cx+.32,cy-.31,cz),
     (cx+.32,cy+.31,cz),(cx-.32,cy+.31,cz),(cx-.32,cy-.31,cz)], .042, wood)
for i, xx in enumerate((cx-.27,cx+.27)):
    for j, yy in enumerate((cy-.26,cy+.26)):
        tube(chair, f'leg_{i}_{j}', [(xx,yy,cz),(xx,yy,.06)], .024, wood)
scene.include('foreground_chair', chair)

# Preflight: positive dimensions and valid fillet radii; all tube points differ.
# Unique semantic keys preserve repeated pieces. Composite transforms happen
# only after inclusion. No ancestor bindings or detached geometry are used.
realize(scene)

# Procedural textiles are assigned through semantic object names.
fabric = bpy.data.materials.new('Woven ivory with muted rose ticking')
fabric.use_nodes = True
nodes = fabric.node_tree.nodes
links = fabric.node_tree.links
bs = nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value = .88
tex = nodes.new('ShaderNodeTexCoord')
wave = nodes.new('ShaderNodeTexWave')
wave.wave_type = 'BANDS'
wave.bands_direction = 'Y'
wave.inputs['Scale'].default_value = 43
wave.inputs['Distortion'].default_value = .6
links.new(tex.outputs['Generated'],wave.inputs['Vector'])
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .78
ramp.color_ramp.elements[0].color = (.77,.70,.59,1)
ramp.color_ramp.elements[1].position = .91
ramp.color_ramp.elements[1].color = (.57,.36,.33,1)
links.new(wave.outputs['Color'],ramp.inputs[0])
mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MIX'
mix.inputs[0].default_value = .25
mix.inputs[1].default_value = (.84,.77,.65,1)
links.new(ramp.outputs['Color'],mix.inputs[2])
links.new(mix.outputs[0],bs.inputs['Base Color'])
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 180
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .15
bump.inputs['Distance'].default_value = .012
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs[0],bs.inputs['Normal'])
for obj in bpy.context.scene.objects:
    name = obj.name.lower()
    if obj.type == 'MESH' and 'fabric' in name and 'pillow' not in name:
        obj.data.materials.clear()
        obj.data.materials.append(fabric)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes.get('Background').inputs[0].default_value = (.72,.76,.79,1)
sc.world.node_tree.nodes.get('Background').inputs[1].default_value = .40

# Independent camera fit: elevated oblique view, foot at right, head at left.
set_view((3.10,-5.35,3.48), (-.02,.02,.94), lens=48)
area_emitter((-3.2,-1.0,3.3), power=550, size=2.8,
             target=(0,0,.6), color=(1.0,.92,.79))
area_emitter((1,-3,3.6), power=110, size=4,
             target=(0,0,.7), color=(.88,.93,1.0))
sc.view_settings.view_transform = 'AgX'
