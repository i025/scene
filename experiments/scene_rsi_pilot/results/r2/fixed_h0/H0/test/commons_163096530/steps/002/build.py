from sceneact import *
import bpy, math, random

random.seed(19)
scene = Scene('Old dormitory')
iron = (.075, .09, .085)
wood = (.22, .125, .055)
stone = (.39, .37, .29)

def B(parent, name, size, loc, color):
    parent.include(name, box(size, center=loc, color=color))

def R(parent, name, radius, a, b, color=iron):
    parent.include(name, rod(radius, start=a, end=b, color=color))

floor = Asset('Individual old floorboards')
for i in range(30):
    x = -3.6 + i * .245
    y = -5.0
    j = 0
    while y < 4.25:
        length = min(random.uniform(1.5, 3.3), 4.25-y)
        c = random.uniform(0, .07)
        B(floor, f'board_{i}_{j}', (.239, length-.012, .085),
          (x, y+length/2, -.047), (.255+c, .166+c*.78, .088+c*.52))
        for k in range(3):
            xx = x + random.uniform(-.085, .085)
            B(floor, f'grain_{i}_{j}_{k}',
              (.002, length*random.uniform(.35, .9), .001),
              (xx, y+length/2, -.003), (.105, .078, .045))
        for k, yy in enumerate((y+.045, y+length-.045)):
            R(floor, f'nail_{i}_{j}_{k}', .007,
              (x+.075, yy, -.001), (x+.075, yy, .001), (.065, .06, .045))
        y += length
        j += 1
scene.include('floor', floor)

B(scene, 'back plaster wall', (7.2, .16, 3.35), (0, 4.32, 1.65), (.72, .72, .49))
B(scene, 'left plaster wall', (.15, 9.6, 3.35), (-3.6, -.4, 1.65), (.68, .68, .49))
B(scene, 'ceiling', (7.3, 9.6, .12), (0, -.4, 3.36), (.57, .60, .41))

timbers = Asset('Exposed ancient oak')
for j, y in enumerate([-4.1, -2.55, -.85, .8, 2.45, 4.18]):
    B(timbers, f'upright{j}', (.16, .145, 3.31), (-3.48, y, 1.66), wood)
for j, z in enumerate([.12, 1.05, 2.38, 3.23]):
    B(timbers, f'longrail{j}', (.17, 9.7, .145), (-3.47, -.4, z), wood)
B(timbers, 'ceiling crossing', (7.1, .20, .20), (0, 1.25, 3.27), (.15, .10, .046))
B(timbers, 'left ceiling edge', (.20, 9.8, .18), (-3.4, -.4, 3.26), wood)
scene.include('timbers', timbers)

def bunk(name, y, x0=-3.37, x1=-.72, width=.94):
    a = Asset(name)
    ya, yb = y-width/2, y+width/2
    for i, x in enumerate((x0, x1)):
        for j, yy in enumerate((ya, yb)):
            R(a, f'post{i}{j}', .025, (x, yy, .045), (x, yy, 2.24))
            a.include(f'cap{i}{j}', ball(.031, center=(x, yy, 2.24), color=iron))
            B(a, f'foot{i}{j}', (.10, .10, .025), (x, yy, .025), (.15, .16, .14))
    for level, z in enumerate((.43, 1.66)):
        B(a, f'bedbase{level}', (x1-x0+.035, width, .075),
          ((x0+x1)/2, y, z), iron)
        a.include(f'mattress{level}', fillet_box(
            (x1-x0-.045, width-.05, .155), radius=.065,
            center=((x0+x1)/2, y, z+.105), color=(.79, .81, .76)))
        B(a, f'blue mattress ticking{level}', (x1-x0-.045, width-.045, .047),
          ((x0+x1)/2, y, z+.035), (.22, .34, .47))
        a.include(f'sheet{level}', fillet_box(
            (x1-x0-.10, width-.065, .075), radius=.035,
            center=((x0+x1)/2-.01, y, z+.19), color=(.89, .90, .86)))
        a.include(f'pillow{level}', fillet_box(
            (.50, width*.71, .12), radius=.06,
            center=(x0+.37, y, z+.28), color=(.91, .91, .85)))
        blanket = box((.69, width-.045, .055),
                      center=(x1-.43, y, z+.24), color=(.79, .81, .78))
        blanket.turn('y', -2)
        a.include(f'folded bedding{level}', blanket)
        for side, yy in enumerate((ya, yb)):
            R(a, f'long edge{level}{side}', .023,
              (x0, yy, z+.01), (x1, yy, z+.01))
        for end, x in enumerate((x0, x1)):
            for k, h in enumerate((z+.33, z+.53)):
                R(a, f'endbar{level}{end}{k}', .018, (x, ya, h), (x, yb, h))
            if level == 1:
                B(a, f'end dark panel{end}', (.035, width-.09, .14),
                  (x, y, z+.36), (.12, .14, .12))
        if level == 1:
            for side, yy in enumerate((ya, yb)):
                R(a, f'upper guard{side}', .018,
                  (x0, yy, z+.42), (x1, yy, z+.42))
    for j, yy in enumerate((y-.29, y+.29)):
        R(a, f'ladder upright{j}', .021,
          (x1+.055, yy, .12), (x1+.055, yy, 1.98))
    for k in range(6):
        zz = .35+k*.285
        R(a, f'ladder rung{k}', .017,
          (x1+.063, y-.29, zz), (x1+.063, y+.29, zz))
    return a

scene.include('nearest left bunk', bunk('Nearest bunk', -.05))
scene.include('middle left bunk', bunk('Middle bunk', 1.53))
scene.include('last left bunk', bunk('Back bunk', 2.98))

cab = Asset('Honey brown wardrobe')
cx, cy, cw = -.18, 4.01, 1.08
for i, x in enumerate((cx-cw/2+.055, cx+cw/2-.055)):
    B(cab, f'side{i}', (.085, .51, 1.79), (x, cy, 1.04), (.30, .17, .065))
    for j, yy in enumerate((cy-.18, cy+.18)):
        B(cab, f'leg{i}{j}', (.09, .09, .16), (x, yy, .13), (.22, .12, .045))
B(cab, 'back', (cw, .045, 1.78), (cx, cy+.23, 1.05), (.20, .112, .043))
B(cab, 'top cornice', (cw+.14, .60, .075), (cx, cy, 1.97), (.34, .21, .09))
B(cab, 'cornice rim', (cw+.19, .62, .035), (cx, cy, 2.015), (.29, .17, .064))
B(cab, 'bottom', (cw, .55, .09), (cx, cy, .22), (.30, .17, .06))
B(cab, 'central stile', (.065, .53, 1.74), (cx, cy, 1.08), (.33, .19, .07))
B(cab, 'left door', (.465, .055, 1.64),
  (cx-.265, cy-.275, 1.08), (.38, .235, .105))
for j, z in enumerate((.64, 1.48)):
    B(cab, f'recessed panel{j}', (.34, .018, .64),
      (cx-.265, cy-.31, z), (.32, .19, .077))
    for k, x in enumerate((cx-.465, cx-.065)):
        B(cab, f'door frame{j}{k}', (.035, .025, .69),
          (x, cy-.326, z), (.42, .265, .12))
B(cab, 'door middle rail', (.45, .035, .07),
  (cx-.265, cy-.33, 1.06), (.42, .25, .10))
cab.include('knob', ball(.022, center=(cx-.085, cy-.365, 1.02),
                         color=(.13, .10, .055)))
B(cab, 'open shelf', (.47, .49, .055), (cx+.265, cy, 1.04), (.39, .23, .09))
R(cab, 'hanging rail', .014, (cx+.075, cy, 1.83),
  (cx+.46, cy, 1.83), (.16, .13, .08))
for j in range(4):
    x = cx+.13+j*.075
    R(cab, f'hanger{j}', .009, (x, cy, 1.86),
      (x, cy-.035, 1.69), (.17, .16, .12))
    garment = box((.08, .17, .43), center=(x, cy+.04, 1.51),
                  color=(.075+j*.017, .068+j*.014, .048+j*.01))
    garment.turn('y', random.uniform(-5, 5))
    cab.include(f'coat{j}', garment)
scene.include('wardrobe', cab)

fire = Asset('Old stone fireplace')
fx = 1.83
B(fire, 'black firebox', (1.31, .035, 1.27), (fx, 4.20, .69), (.065, .059, .043))
for row in range(9):
    for col in range(5):
        x = fx-.58+col*.27+(row % 2)*.105
        if x < fx+.62:
            c = random.uniform(.075, .16)
            B(fire, f'sooty brick{row}_{col}', (.245, .045, .116),
              (x, 4.165, .12+row*.133), (c, c*.87, c*.65))
B(fire, 'left jamb', (.29, .31, 1.26), (fx-.78, 4.09, .66), stone)
B(fire, 'right jamb', (.29, .31, 1.26), (fx+.78, 4.09, .66), stone)
B(fire, 'wide lintel', (1.86, .35, .30), (fx, 4.08, 1.47), (.44, .43, .34))
B(fire, 'mantel top', (1.96, .38, .105), (fx, 4.07, 1.65), (.47, .46, .37))
for i in range(9):
    t = math.pi*(i+.5)/9
    x = fx+.65*math.cos(t)
    z = 1.18+.20*math.sin(t)
    block = box((.235, .12, .13), center=(x, 3.90, z), color=(.37, .36, .29))
    slope = math.atan2(.20*math.cos(t), -.65*math.sin(t))
    block.turn('y', -math.degrees(slope))
    fire.include(f'arch stone{i}', block)
for side in (-1, 1):
    B(fire, f'inner upright{side}', (.075, .11, 1.09),
      (fx+side*.65, 3.91, .63), (.43, .41, .32))
    for j, z in enumerate((.32, .73, 1.13)):
        B(fire, f'jamb joint{side}_{j}', (.285, .012, .012),
          (fx+side*.78, 3.925, z), (.25, .25, .20))
B(fire, 'hearth', (2.02, .78, .055), (fx, 3.89, .025), (.24, .235, .19))
B(fire, 'hearth lip', (1.76, .23, .06), (fx, 3.59, .035), (.31, .30, .24))
scene.include('fireplace', fire)

guard = Asset('Leaning metal fire guard')
for i in range(9):
    x = 2.25+i*.027
    R(guard, f'bar{i}', .009, (x, 3.79, .10),
      (x-.075, 3.88, .64), (.61, .64, .59))
R(guard, 'top rail', .017, (2.175, 3.88, .64),
  (2.40, 3.88, .64), (.61, .64, .59))
R(guard, 'bottom rail', .014, (2.25, 3.79, .10),
  (2.475, 3.79, .10), (.48, .51, .47))
scene.include('guard', guard)
R(scene, 'coal bucket', .105, (2.91, 3.91, .025),
  (2.91, 3.91, .29), (.075, .078, .062))
R(scene, 'poker', .012, (2.73, 3.93, .04),
  (2.70, 3.96, .77), (.08, .075, .056))

R(scene, 'clock body', .125, (-.15, 4.205, 2.48),
  (-.15, 4.16, 2.48), (.42, .49, .43))
R(scene, 'clock face', .109, (-.15, 4.155, 2.48),
  (-.15, 4.148, 2.48), (.59, .65, .56))
R(scene, 'clock hour', .005, (-.15, 4.135, 2.48),
  (-.177, 4.135, 2.516), (.25, .29, .25))
R(scene, 'clock minute', .004, (-.15, 4.132, 2.48),
  (-.15, 4.132, 2.55), (.25, .29, .25))

right = Asset('Cropped foreground bunk')
for j, y in enumerate((-3.1, -.8)):
    for i, x in enumerate((3.0, 3.96)):
        R(right, f'post{i}{j}', .035, (x, y, .02), (x, y, 2.55), iron)
        right.include(f'cap{i}{j}', ball(.039, center=(x, y, 2.55), color=iron))
for k, z in enumerate((.50, 1.81)):
    B(right, f'base{k}', (.95, 2.3, .07), (3.48, -1.95, z), iron)
    B(right, f'mattress{k}', (.9, 2.22, .17),
      (3.48, -1.95, z+.11), (.83, .84, .79))
    for j, y in enumerate((-3.1, -.8)):
        for hidx, h in enumerate((z+.31, z+.49)):
            R(right, f'end_{k}_{j}_{hidx}', .019,
              (3, y, h), (3.96, y, h), iron)
    R(right, f'side{k}', .021, (3, -3.1, z+.45), (3, -.8, z+.45), iron)
B(right, 'wooden bed end', (.105, .095, 2.23),
  (2.94, -.81, 1.16), (.46, .24, .076))
for i, y in enumerate((-2.89, -2.34)):
    R(right, f'ladder{i}', .024, (2.96, y, .14), (2.96, y, 2.42), iron)
for j in range(8):
    z = .27+j*.29
    R(right, f'rung{j}', .019, (2.96, -2.89, z), (2.96, -2.34, z), iron)
scene.include('foreground right bed', right)

for j, y in enumerate((-.1, 1.5, 2.95)):
    B(scene, f'wall light casing{j}', (.09, .14, .25),
      (-3.37, y, 2.36), (.24, .28, .23))
    B(scene, f'wall light glass{j}', (.018, .095, .13),
      (-3.311, y, 2.385), (.63, .69, .60))

realize(scene)

processed = set()
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat is None or mat.name in processed:
            continue
        processed.add(mat.name)
        mat.use_nodes = True
        bs = mat.node_tree.nodes.get('Principled BSDF')
        if bs is None:
            continue
        bs.inputs['Roughness'].default_value = .79
        if any(word in obj.name.lower() for word in
               ('board', 'plaster', 'ceiling', 'jamb', 'lintel',
                'timber', 'cornice', 'panel')):
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            tex = nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value = 19
            tex.inputs['Detail'].default_value = 3
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = .17
            bump.inputs['Distance'].default_value = .035
            links.new(tex.outputs['Fac'], bump.inputs['Height'])
            links.new(bump.outputs['Normal'], bs.inputs['Normal'])

set_view((3.28, -6.55, 2.04), (-.16, 2.32, 1.46), lens=31.5)
area_emitter((-.6, -2.5, 3.05), power=650, size=4.5,
             target=(-.9, 1.6, .4), color=(1, .96, .82))
area_emitter((2.4, -.9, 2.8), power=260, size=3.1,
             target=(-1.2, 3, 1.3), color=(.82, .89, 1))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Dormitory ambient world')
world = sc.world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (.48, .52, .41, 1)
background.inputs['Strength'].default_value = .38

sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.render.resolution_x = 512
sc.render.resolution_y = 341
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .35
sc.render.image_settings.file_format = 'PNG'
