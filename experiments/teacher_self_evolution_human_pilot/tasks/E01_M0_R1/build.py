from sceneact import *
import bpy, math, random
random.seed(12)
scene = Scene('Green room')
wall=(.43,.49,.40); trim=(.66,.64,.59); wood=(.23,.085,.025); darkwood=(.105,.039,.017); edgewood=(.32,.14,.055)
scene.include('floor',box((8.4,10,.12),center=(0,0,-.06),color=(.64,.63,.60)))
scene.include('back_wall',box((8.4,.14,3.75),center=(0,4,1.875),color=wall))
scene.include('left_wall',box((.14,10,3.75),center=(-4.2,-1,1.875),color=(.46,.52,.41)))
scene.include('right_wall',box((.14,10,3.75),center=(4.2,-1,1.875),color=(.42,.48,.39)))
scene.include('ceiling',box((8.4,10,.1),center=(0,-1,3.8),color=(.77,.77,.73)))
for i in range(-10,11):
 x=i*.39
 scene.include('floor_seam_%d'%i,box((.009,9.9,.003),center=(x,-.95,.002),color=(.46,.46,.43)))
 for j in range(2):
  scene.include('floor_grain_%d_%d'%(i,j),box((.003,random.uniform(1,3),.003),center=(x+random.uniform(.05,.30),random.uniform(-3,3),.003),color=(.57,.57,.54)))
scene.include('back_baseboard',box((8.3,.07,.19),center=(0,3.89,.095),color=trim))
scene.include('right_baseboard',box((.07,9.8,.19),center=(4.09,-.95,.095),color=trim))
scene.include('left_baseboard',box((.07,9.8,.19),center=(-4.09,-.95,.095),color=trim))
window_centers=(-1.28,1.05)
for wi,x in enumerate(window_centers):
 a=Asset('pointed_window_%d'%wi)
 z0,zspring,ztop=1.32,2.68,3.46
 half=.58
 a.include('lower_glass',box((1.11,.025,1.35),center=(x,3.895,(z0+zspring)/2),color=(.76,.83,.78)))
 a.include('sill',box((1.30,.18,.09),center=(x,3.80,1.28),color=(.56,.54,.49)))
 for side in (-1,1):
  a.include('jamb_%d'%side,box((.075,.10,1.39),center=(x+side*half,3.80,(z0+zspring)/2),color=(.57,.55,.50)))
  pts=[]
  for k in range(13):
   t=k/12
   pts.append((x+side*half*(1-t),3.79,zspring+(ztop-zspring)*(1-(1-t)**1.55)))
  a.include('pointed_arch_%d'%side,sweep_tube(points=pts,radius=.045,color=(.57,.55,.50)))
  inner=[]
  for k in range(10):
   t=k/9
   inner.append((x+side*.41*(1-t),3.75,2.72+.52*(1-(1-t)**1.6)))
  a.include('arched_muntin_%d'%side,sweep_tube(points=inner,radius=.019,color=(.42,.43,.40)))
 a.include('middle_vertical_muntin',box((.035,.07,.62),center=(x,3.76,1.66),color=(.53,.53,.49)))
 a.include('lower_crossbar',box((1.08,.06,.035),center=(x,3.76,1.70),color=(.53,.53,.49)))
 a.include('roller_blind',box((1.10,.06,.45),center=(x,3.72,2.43),color=(.56,.55,.50)))
 a.include('blind_bottom_rail',box((1.12,.08,.035),center=(x,3.68,2.20),color=(.68,.66,.60)))
 scene.include('window_%d'%wi,a)
 rad=Asset('radiator_%d'%wi)
 rad.include('body',box((1.52,.16,.72),center=(x,3.74,.83),color=(.83,.83,.79)))
 rad.include('top',box((1.55,.18,.055),center=(x,3.73,1.20),color=(.72,.73,.70)))
 scene.include('radiator_%d'%wi,rad)
cab=Asset('antique_wardrobe')
cab.include('main_case',box((1.75,.86,3.18),center=(-3.15,1.05,1.64),color=wood))
cab.include('left_side',box((.07,.92,3.20),center=(-4.00,1.05,1.66),color=(.27,.105,.03)))
cab.include('top_cornice',box((1.91,1.01,.13),center=(-3.15,1.04,3.27),color=darkwood))
cab.include('base_plinth',box((1.89,.98,.18),center=(-3.15,1.04,.12),color=darkwood))
for x in (-3.59,-2.72):
 cab.include('door_%.2f'%x,box((.79,.055,2.75),center=(x,.585,1.71),color=(.32,.13,.04)))
 cab.include('inset_panel_%.2f'%x,box((.64,.025,2.34),center=(x,.55,1.70),color=(.37,.17,.06)))
 for dx in (-.34,.34):
  cab.include('door_molding_%.2f_%.2f'%(x,dx),box((.035,.025,2.47),center=(x+dx,.525,1.70),color=(.16,.06,.02)))
 for z in (.46,2.93):
  cab.include('panel_horizontal_%.2f_%.2f'%(x,z),box((.71,.025,.035),center=(x,.525,z),color=(.16,.06,.02)))
 cab.include('handle_%.2f'%x,ball(.035,center=(x+(.27 if x < -3 else -.27),.49,1.61),color=(.69,.55,.27)))
cab.include('curved_crown',sweep_tube(points=[(-4.03,.51,3.25),(-3.80,.51,3.30),(-3.55,.51,3.38),(-3.15,.51,3.42),(-2.75,.51,3.38),(-2.50,.51,3.30),(-2.25,.51,3.25)],radius=.065,color=darkwood))
scene.include('wardrobe',cab)
chair=Asset('simple_chair_behind_cabinet')
chair.include('seat',box((.65,.62,.08),center=(-1.98,2.20,.62),color=(.64,.59,.50)))
for x in (-2.25,-1.71):
 for y in (1.96,2.43):
  chair.include('leg_%.2f_%.2f'%(x,y),rod(.033,start=(x,y,.04),end=(x,y,.63),color=darkwood))
for x in (-2.25,-1.71):
 chair.include('back_post_%.2f'%x,rod(.034,start=(x,2.45,.58),end=(x,2.48,1.43),color=darkwood))
chair.include('back_top',box((.61,.07,.08),center=(-1.98,2.47,1.40),color=darkwood))
for x in (-2.15,-1.98,-1.81):
 chair.include('back_slat_%.2f'%x,box((.035,.045,.65),center=(x,2.46,1.06),color=darkwood))
scene.include('simple_chair',chair)
tx,ty=1.15,1.05
table=Asset('oval_pedestal_table')
top=ball(1,center=(tx,ty,1.04),color=(.30,.14,.065)); top.resize((1.25,.71,.075)); table.include('oval_tabletop',top)
rim=ball(1,center=(tx,ty,1.00),color=darkwood); rim.resize((1.27,.73,.055)); table.include('carved_table_edge',rim)
table.include('central_column',rod(.115,start=(tx,ty,.29),end=(tx,ty,1.00),color=darkwood))
for z,r in ((.33,.18),(.45,.15),(.72,.15),(.91,.17)):
 table.include('column_turning_%.2f'%z,ball(r,center=(tx,ty,z),color=edgewood))
for i in range(4):
 a=i*math.pi/2+.3
 pts=[(tx,ty,.34),(tx+.25*math.cos(a),ty+.25*math.sin(a),.29),(tx+.48*math.cos(a),ty+.48*math.sin(a),.12),(tx+.67*math.cos(a),ty+.67*math.sin(a),.09)]
 table.include('curved_pedestal_foot_%d'%i,sweep_tube(points=pts,radius=.065,color=darkwood))
scene.include('table',table)
def ornate_chair(name,cx,cy,angle,cushion=False):
 a=Asset(name)
 a.include('upholstered_seat',fillet_box((.72,.65,.16),radius=.07,center=(0,0,.55),color=(.62,.60,.55)))
 a.include('seat_frame',box((.76,.68,.09),center=(0,0,.46),color=darkwood))
 for x in (-.30,.30):
  for y in (-.25,.25):
   a.include('curved_leg_%.2f_%.2f'%(x,y),sweep_tube(points=[(x,y,.46),(x*1.07,y*1.08,.29),(x*1.08,y*1.18,.06)],radius=.035,color=darkwood))
 for x in (-.32,.32):
  a.include('back_upright_%.2f'%x,sweep_tube(points=[(x,.27,.49),(x*1.10,.31,.85),(x*1.05,.35,1.22),(x*.92,.35,1.39)],radius=.04,color=darkwood))
 a.include('carved_crest',sweep_tube(points=[(-.30,.35,1.34),(-.19,.35,1.42),(0,.35,1.38),(.19,.35,1.42),(.30,.35,1.34)],radius=.045,color=darkwood))
 a.include('open_back_curl_left',sweep_tube(points=[(-.20,.34,1.31),(-.12,.34,1.18),(-.08,.34,.99),(0,.34,.90)],radius=.025,color=edgewood))
 a.include('open_back_curl_right',sweep_tube(points=[(.20,.34,1.31),(.12,.34,1.18),(.08,.34,.99),(0,.34,.90)],radius=.025,color=edgewood))
 if cushion:
  a.include('striped_cushion',fillet_box((.73,.63,.10),radius=.05,center=(0,0,.68),color=(.39,.39,.37)))
  for i in range(9):
   a.include('cushion_stripe_%d'%i,box((.012,.57,.006),center=(-.31+i*.077,0,.733),color=(.66,.65,.60)))
 a.turn('+z',angle,pivot=(0,0,0)); a.move((cx,cy,0)); scene.include(name,a)
ornate_chair('left_dining_chair',.10,.58,-18,True)
ornate_chair('right_dining_chair',2.95,.43,-28,False)
lamp=Asset('reading_lamp')
lamp.include('foot',rod(.16,start=(1.87,2.45,.03),end=(1.87,2.45,.07),color=(.33,.33,.30)))
lamp.include('slender_stem',rod(.018,start=(1.87,2.45,.07),end=(1.84,2.45,1.83),color=(.39,.40,.37)))
lamp.include('angled_arm',rod(.018,start=(1.84,2.45,1.83),end=(1.62,2.45,2.23),color=(.39,.40,.37)))
shade=ball(1,center=(1.60,2.45,2.22),color=(.70,.71,.67)); shade.resize((.16,.16,.09)); lamp.include('small_shade',shade)
scene.include('reading_lamp',lamp)
picture=Asset('framed_picture')
picture.include('frame',box((.055,.91,.58),center=(4.09,2.42,2.27),color=(.42,.26,.13)))
picture.include('mat',box((.025,.81,.48),center=(4.052,2.42,2.27),color=(.80,.79,.69)))
picture.include('pale_artwork',box((.018,.59,.31),center=(4.032,2.42,2.27),color=(.64,.69,.57)))
for i in range(7):
 picture.include('art_mark_%d'%i,box((.01,.025,random.uniform(.05,.14)),center=(4.019,2.19+i*.07,2.23+random.uniform(-.03,.05)),color=(.36,.46,.31)))
scene.include('wall_picture',picture)
scene.include('table_paper',box((.64,.38,.012),center=(1.15,1.03,1.126),color=(.79,.78,.69)))
scene.include('saucer',rod(.11,start=(.60,1.22,1.13),end=(.60,1.22,1.145),color=(.78,.77,.71)))
scene.include('cup',rod(.065,start=(.60,1.22,1.145),end=(.60,1.22,1.23),color=(.79,.78,.72)))
scene.include('flower_vase',rod(.075,start=(1.38,1.13,1.13),end=(1.38,1.13,1.32),color=(.43,.48,.38)))
for i in range(5):
 x=1.38+random.uniform(-.09,.09); y=1.13+random.uniform(-.07,.07); z=1.52+random.uniform(-.02,.09)
 scene.include('flower_stem_%d'%i,rod(.009,start=(1.38,1.13,1.27),end=(x,y,z),color=(.25,.38,.15)))
 scene.include('flower_%d'%i,ball(.035,center=(x,y,z),color=(.68,.12,.09) if i%2 else (.76,.58,.12)))
realize(scene)
def upper_pane(name,x):
 verts=[(x-.55,3.88,2.67),(x+.55,3.88,2.67)]
 for k in range(13):
  t=k/12
  verts.append((x+.55*(1-t),3.88,2.67+.77*(1-(1-t)**1.55)))
 for k in range(1,13):
  t=k/12
  verts.append((x-.55*t,3.88,2.67+.77*(1-t**1.55)))
 mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],[list(range(len(verts)))]); mesh.update()
 ob=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(ob)
 mat=bpy.data.materials.new(name+'_daylight'); mat.diffuse_color=(.85,.90,.85,1); mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.85,.90,.85,1); bs.inputs['Emission Color'].default_value=(.85,.90,.83,1); bs.inputs['Emission Strength'].default_value=.65
 ob.data.materials.append(mat)
for i,x in enumerate(window_centers): upper_pane('upper_window_glass_%d'%i,x)
for ob in bpy.data.objects:
 if 'lower_glass' in ob.name and ob.type == 'MESH' and ob.data is not None:
  for mat in ob.data.materials:
   if mat and mat.use_nodes:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
     bs.inputs['Emission Color'].default_value=(.7,.78,.7,1)
     bs.inputs['Emission Strength'].default_value=.35
if bpy.context.scene.world is None:
 bpy.context.scene.world=bpy.data.worlds.new('Room world')
bpy.context.scene.world.color=(.55,.55,.53)
bpy.context.scene.world.use_nodes=True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.75,.70,1)
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
set_view((0,-7.7,2.55),(-.10,2.5,1.65),lens=24,sensor=36)
area_emitter((-1.3,3.35,2.8),power=500,size=2.0,target=(-1,0,0),color=(1,.97,.88))
area_emitter((1.1,3.35,2.8),power=500,size=2.0,target=(1,0,0),color=(1,.97,.88))
area_emitter((0,-3.5,3.3),power=350,size=5,target=(0,1,1),color=(1,.94,.84))