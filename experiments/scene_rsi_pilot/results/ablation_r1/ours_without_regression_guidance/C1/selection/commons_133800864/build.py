from sceneact import *
import bpy, math, random

# Observations: the first rendering has a foreground wall occluding most of
# the window. Objects are also too small in the frame. Reference landmarks:
# roll approximately (276,130), towel (135,332), jug (262,396), sink (55,486).
# Main correction: camera framing, plus removing the erroneous foreground
# extent of the left wall. Expected effect: visible blinds, larger objects,
# and a closer foreground crop. Object dimensions and supports are preserved.
# Camera pose and focal length remain uncertain, independent parameters.
scene = Scene('Kitchen corner')
cream=(.73,.68,.53)
ivory=(.88,.85,.74)
metal=(.43,.43,.36)
random.seed(9)

def asset(name):
    return scene.include(name, Asset(name))
def cube(g,n,size,c,col):
    return g.include(n,box(size,center=c,color=col))
def cyl(g,n,r,h,c,col):
    return g.include(n,rod(r,length=h,center=c,color=col))
def tube(g,n,pts,r,col):
    return g.include(n,sweep_tube(points=pts,radius=r,color=col))

# Semantic mapping: Walls and Window describe architecture; Granite counter
# supports Sink, Faucet, Counter tin, Blender, jug and filter pitcher.
arch=asset('Walls')
cube(arch,'back',(4,.12,3.3),(0,.59,1.6),(.77,.73,.61))
# The earlier long return wall was between the camera and the window.
cube(arch,'left',(.12,.10,3.3),(-1.40,.56,1.6),(.79,.76,.66))

counter=asset('Granite counter')
cube(counter,'stone',(3.6,1.40,.075),(.10,-.12,.885),(.28,.27,.23))
cube(counter,'backsplash',(3.6,.045,.14),(.10,.49,.99),(.29,.28,.24))
cube(counter,'cabinet_base',(3.4,1.32,.85),(.1,-.12,.425),(.49,.43,.31))

win=asset('Window and blinds')
cube(win,'glass',(.99,.025,2.25),(-.83,.495,1.89),(.65,.81,.83))
for i,x in enumerate([-1.345,-.315]):
    cube(win,'frame_vertical_'+str(i),(.055,.065,2.38),(x,.446,1.89),ivory)
for i,z in enumerate([.70,1.75,3.06]):
    cube(win,'frame_horizontal_'+str(i),(1.07,.075,.055),(-.83,.44,z),ivory)
cube(win,'center_mullion',(.025,.06,2.25),(-.94,.43,1.88),ivory)
for i in range(31):
    sl=cube(win,'blind_'+str(i),(1.04,.055,.048),
            (-.83,.348,.73+i*.075),(.86,.85,.77))
    sl.turn('x',-9)
for i,x in enumerate([-.99,-.45]):
    cube(win,'blind_tape_'+str(i),(.018,.012,2.27),(x,.309,1.88),(.76,.75,.67))
cube(win,'bottom_rail',(1.08,.065,.045),(-.83,.33,.70),ivory)
for i in range(22):
    win.include('outdoor_leaf_'+str(i),
                ball(random.uniform(.018,.065),
                     center=(random.uniform(-1.28,-.36),.47,random.uniform(.85,2.99)),
                     color=(.33,.51,.40)))

cab=asset('Upper cream cabinet')
cube(cab,'carcass',(1.50,.49,1.53),(.48,.27,2.18),cream)
for j,(cx,w) in enumerate([(.33,.94),(.99,.36)]):
    cube(cab,'door_'+str(j),(w,.035,1.43),(cx,.006,2.20),(.78,.73,.59))
    cube(cab,'inset_'+str(j),(w-.12,.018,1.26),(cx,-.019,2.20),(.755,.704,.562))
    for k,x in enumerate([cx-w/2+.035,cx+w/2-.035]):
        cube(cab,'stile_%s_%s'%(j,k),(.04,.025,1.41),(x,-.036,2.20),(.82,.77,.63))
    for k,z in enumerate([1.515,2.885]):
        cube(cab,'rail_%s_%s'%(j,k),(w,.027,.045),(cx,-.036,z),(.82,.77,.63))
cab.include('door_knob',ball(.025,center=(.765,-.078,1.79),color=(.39,.35,.23)))

paper=asset('Paper towel and wall bracket')
cyl(paper,'spindle',.017,1.00,(.46,-.18,2.22),metal)
paper.include('finial',ball(.036,center=(.46,-.18,2.728),color=(.47,.44,.34)))
cyl(paper,'roll',.155,.73,(.46,-.18,2.265),(.94,.92,.82))
cube(paper,'hanging_sheet',(.265,.018,.72),(.455,-.319,2.26),(.95,.93,.85))
for i,x in enumerate([.34,.57]):
    paper.include('bracket_'+str(i),rod(.017,start=(x,-.06,1.865),
                                       end=(x,-.19,1.865),color=metal))
    paper.include('bracket_end_'+str(i),
                  ball(.023,center=(x,-.19,1.865),color=metal))

towel=asset('Towel ring and hanging towel')
towel.include('mount_plate',rod(.055,length=.025,center=(-.278,.115,1.90),
                                axis='+x',color=metal))
towel.include('mount_arm',rod(.018,start=(-.29,.115,1.90),
                              end=(-.365,.055,1.90),color=metal))
pts=[]
for i in range(65):
    a=2*math.pi*i/64
    pts.append((-.36+.105*math.sin(a),-.005+.025*math.sin(a),
                1.745+.15*math.cos(a)))
tube(towel,'ring',pts,.008,(.52,.54,.48))

# Cloth mesh is attached to the towel semantic hierarchy after realization.
verts=[]; faces=[]
cols=18; rows=28
for j in range(rows):
    t=j/(rows-1)
    width=.15+.10*math.sin(t*math.pi*.75)
    for i in range(cols):
        u=i/(cols-1)
        verts.append((-.365+(u-.5)*width,
                      -.095-.045*math.sin(u*math.pi*5)*(.35+.65*t)-.03*t,
                      1.61-.66*t+.025*math.cos(u*math.pi*3)*t*t))
for j in range(rows-1):
    for i in range(cols-1):
        a=j*cols+i
        faces.append((a,a+1,a+cols+1,a+cols))

sink=asset('Sink')
cube(sink,'basin_dark',(.74,.54,.03),(-.66,-.63,.929),(.035,.044,.039))
for i,x in enumerate([-.99,-.33]):
    cube(sink,'rim_side_'+str(i),(.035,.57,.025),(x,-.63,.946),metal)
for i,y in enumerate([-.90,-.36]):
    cube(sink,'rim_end_'+str(i),(.72,.03,.025),(-.66,y,.946),metal)
faucet=asset('Faucet')
cyl(faucet,'base',.064,.023,(-.68,-.26,.945),metal)
tube(faucet,'neck',[(-.68,-.26,.95),(-.68,-.26,1.07),
                    (-.68,-.28,1.25),(-.68,-.32,1.29),
                    (-.68,-.39,1.29),(-.68,-.42,1.23)],.016,metal)
faucet.include('left_handle',rod(.012,start=(-.78,-.26,.965),
                                 end=(-.83,-.29,1.035),color=metal))
cyl(faucet,'small_cap',.045,.022,(-.41,-.25,.948),(.24,.24,.19))
soap=asset('Cropped sponge tray')
cube(soap,'tray',(.18,.16,.024),(-1.08,-.43,.95),metal)
cube(soap,'sponge',(.14,.11,.035),(-1.08,-.43,.979),(.75,.71,.48))

tin=asset('Counter tin')
cyl(tin,'body',.062,.25,(-.18,.20,1.05),(.31,.33,.20))
cyl(tin,'lid',.066,.018,(-.18,.20,1.184),(.48,.46,.29))
cube(tin,'label',(.074,.008,.13),(-.18,.137,1.04),(.61,.58,.40))

blender=asset('Blender')
cyl(blender,'base',.10,.26,(.07,.15,1.055),(.025,.032,.028))
cyl(blender,'rim',.105,.035,(.07,.15,1.20),(.065,.069,.057))
cup=blender.include('clear_cup',rod(.071,length=.28,center=(.05,.15,1.365),
                                   color=(.56,.58,.51),opacity=.30))
cup.turn('y',-12)
tube(blender,'cup_glint',[(.00,.081,1.24),(-.054,.081,1.50),
                           (.025,.081,1.51)],.006,(.79,.80,.71))

jug=asset('Filtered water jug')
jug.include('body',fillet_box((.30,.235,.32),radius=.055,
                              center=(.365,-.14,1.09),color=(.70,.73,.66)))
cyl(jug,'shoulder',.115,.12,(.365,-.14,1.285),(.72,.74,.68))
cyl(jug,'neck',.045,.09,(.365,-.14,1.375),(.78,.79,.71))
cyl(jug,'cap',.048,.026,(.365,-.14,1.428),(.83,.83,.74))

pitch=asset('Blue filter pitcher')
pitch.include('blue_body',fillet_box((.29,.22,.37),radius=.055,
                                    center=(.69,.235,1.125),color=(.045,.095,.18)))
cyl(pitch,'upper_blue',.137,.12,(.69,.235,1.345),(.065,.10,.17))
lid=pitch.include('silver_lid',rod(.151,length=.031,center=(.69,.225,1.416),
                                  color=(.37,.39,.35)))
lid.resize((1,.78,1))
tube(pitch,'clear_handle',[(.805,.21,1.355),(.90,.21,1.32),
                           (.95,.21,1.20),(.945,.21,1.07),
                           (.89,.21,1.01),(.81,.21,1.035)],.026,(.53,.57,.52))
tube(pitch,'handle_highlight',[(.815,.185,1.35),(.899,.185,1.31),
                               (.933,.185,1.19),(.922,.185,1.08)],
     .008,(.75,.76,.68))

# Audit: all dimensions positive; both fillet radii .055 are below half
# the smallest dimension. Indexed inclusion keys are unique. Sweep points
# differ. Counter contact heights are preserved, without bind dependencies.
realize(scene)

def mesh_object(name,v,f,color,parent_name):
    me=bpy.data.meshes.new(name)
    me.from_pydata(v,[],f)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    root=bpy.data.objects.get(parent_name)
    if root:
        ob.parent=root
        ob.matrix_parent_inverse=root.matrix_world.inverted()
    mat=bpy.data.materials.new(name+'_material')
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    bs=mat.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=.92
    ob.data.materials.append(mat)
    return ob

cloth=mesh_object('Ivory draped towel',verts,faces,(.85,.82,.71),
                  'Towel ring and hanging towel')
sol=cloth.modifiers.new('Cloth thickness','SOLIDIFY')
sol.thickness=.008
sub=cloth.modifiers.new('Soft folds','SUBSURF')
sub.levels=1
for p in cloth.data.polygons:
    p.use_smooth=True

v=[]; f=[]
for z,rx,ry in [(1.22,.145,.11),(1.32,.092,.075),(1.385,.043,.042)]:
    for i in range(48):
        a=i*2*math.pi/48
        v.append((.365+rx*math.cos(a),-.14+ry*math.sin(a),z))
for j in range(2):
    for i in range(48):
        f.append((j*48+i,j*48+(i+1)%48,
                  (j+1)*48+(i+1)%48,(j+1)*48+i))
shoulder=mesh_object('Jug tapered shoulder',v,f,(.72,.74,.67),
                     'Filtered water jug')
for p in shoulder.data.polygons:
    p.use_smooth=True

def descendants(key):
    root=bpy.data.objects.get(key)
    return list(root.children_recursive) if root else []

for ob in descendants('Granite counter'):
    if ob.type!='MESH':
        continue
    mat=ob.data.materials[0].copy()
    ob.data.materials[0]=mat
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    noise=nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=145
    noise.inputs['Detail'].default_value=2.2
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.22
    ramp.color_ramp.elements[0].color=(.065,.06,.047,1)
    ramp.color_ramp.elements[1].position=.77
    ramp.color_ramp.elements[1].color=(.55,.51,.40,1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
    nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.73
    bump=nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.16
    bump.inputs['Distance'].default_value=.006
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs[0],bs.inputs['Normal'])

for ob in [cloth]+[o for o in descendants('Paper towel and wall bracket')
                    if o.type=='MESH']:
    if not ob.data.materials:
        continue
    mat=ob.data.materials[0].copy()
    ob.data.materials[0]=mat
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    ns=nt.nodes.new('ShaderNodeTexNoise')
    ns.inputs['Scale'].default_value=220
    bump=nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.13
    bump.inputs['Distance'].default_value=.003
    nt.links.new(ns.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

if bpy.context.scene.world is None:
    bpy.context.scene.world=bpy.data.worlds.new('World')
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.76,.78,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35
area_emitter((-2,-.35,2.3),power=290,size=1.7,
             target=(.3,.1,1.4),color=(.83,.92,1))
area_emitter((-.1,-2.4,3.1),power=95,size=2.5,
             target=(.2,.1,1.3),color=(1,.84,.61))

# Narrower field of view and a small aim correction; scene scale is unchanged.
set_view((-1.65,-3.45,2.22),(.16,.12,1.75),lens=61,sensor=36)
sc=bpy.context.scene
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
