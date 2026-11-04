from sceneact import *
import bpy, math, random
random.seed(21)

scene = Scene("Old timber dormitory")
cream=(.64,.65,.40)
wood=(.23,.135,.065)
iron=(.105,.125,.12)
linen=(.88,.89,.86)

def B(name,size,loc,color,parent=scene):
    n=box(size,center=loc,color=color)
    parent.include(name,n)
    return n

def R(name,a,b,radius=.024,color=iron,parent=scene):
    n=rod(radius=radius,start=a,end=b,color=color)
    parent.include(name,n)
    return n

B("floor_underlay",(8,12,.12),(0,0,-.105),(.21,.13,.065))
for i in range(27):
    x=-4+i*.30
    start=-6
    j=0
    while start<5:
        length=min(random.uniform(1.7,3.4),5-start)
        c=random.uniform(0,.07)
        B("oak_board_%d_%d"%(i,j),(.291,length-.012,.075),
          (x,start+length/2,-.027),(.30+c,.19+c*.68,.095+c*.42))
        for yy in (start+.07,start+length-.07):
            if random.random()<.65:
                for xx in (x-.095,x+.095):
                    R("nail_%d_%d_%s_%s"%(i,j,yy,xx),
                      (xx,yy,.011),(xx,yy,.016),.007,(.10,.085,.065))
        start+=length
        j+=1

B("back_plaster",(7.4,.18,3.5),(0,4.65,1.71),cream)
B("left_plaster",(.18,10.8,3.5),(-3.65,-.65,1.71),(.68,.68,.47))
B("ceiling",(7.4,11,.15),(0,-.7,3.49),(.58,.60,.40))
B("back_skirting",(7.25,.075,.14),(0,4.51,.07),wood)
B("left_skirting",(.07,10.8,.14),(-3.52,-.65,.07),wood)

for y in (-4.1,-2.25,-.45,1.30,3.15,4.48):
    B("upright_"+str(y),(.16,.16,3.46),(-3.51,y,1.72),wood)
for z in (1.12,2.37,3.34):
    B("wall_beam_"+str(z),(.17,10.8,.145),(-3.49,-.65,z),wood)
for y in (-2.4,2.0):
    B("ceiling_crossbeam_"+str(y),(7.25,.20,.24),(0,y,3.33),(.19,.115,.057))

B("window_dark_reveal",(.035,1.70,1.65),(-3.539,.15,1.76),(.21,.23,.19))
B("window_daylight",(.042,1.49,1.47),(-3.512,.15,1.77),(.80,.87,.87))
for y in (-.64,.15,.94):
    B("window_mullion_"+str(y),(.07,.055,1.56),(-3.47,y,1.77),(.72,.73,.65))
for z in (1.02,1.77,2.52):
    B("window_rail_"+str(z),(.07,1.65,.065),(-3.47,.15,z),(.73,.74,.66))
B("windowsill",(.24,1.83,.075),(-3.42,.15,.98),(.57,.52,.36))

def bunk(name,x0,x1,y0,y1):
    a=Asset(name)
    for x in (x0,x1):
        for y in (y0,y1):
            R("post_%s_%s"%(x,y),(x,y,.045),(x,y,2.29),.027,iron,a)
            a.include("cap_%s_%s"%(x,y),
                      ball(.031,center=(x,y,2.29),color=iron))
            R("foot_%s_%s"%(x,y),(x,y,.025),(x,y,.045),
              .067,(.29,.29,.25),a)
    for z in (.47,1.64):
        B("bed_base_"+str(z),(x1-x0,y1-y0,.065),
          ((x0+x1)/2,(y0+y1)/2,z),(.21,.23,.21),a)
        for y in (y0,y1):
            R("long_edge_%s_%s"%(z,y),(x0,y,z+.035),
              (x1,y,z+.035),.032,iron,a)
            R("lower_rail_%s_%s"%(z,y),(x0,y,z-.085),
              (x1,y,z-.085),.019,iron,a)
        for x in (x0,x1):
            R("end_edge_%s_%s"%(z,x),(x,y0,z+.035),
              (x,y1,z+.035),.027,iron,a)
        a.include("mattress_"+str(z),
                  fillet_box((x1-x0-.065,y1-y0-.055,.17),radius=.065,
                  center=((x0+x1)/2,(y0+y1)/2,z+.12),color=linen))
        B("blue_sheet_edge_"+str(z),(x1-x0-.06,.025,.045),
          ((x0+x1)/2,y0-.014,z+.065),(.38,.48,.62),a)
        a.include("duvet_"+str(z),
                  fillet_box((x1-x0-.18,y1-y0-.08,.115),radius=.052,
                  center=((x0+x1)/2+.035,(y0+y1)/2,z+.235),
                  color=(.92,.92,.89)))
        a.include("pillow_"+str(z),
                  fillet_box((.47,y1-y0-.17,.14),radius=.065,
                  center=(x0+.32,(y0+y1)/2,z+.31),
                  color=(.91,.92,.88)))
        for k in range(3):
            a.include("linen_fold_%s_%s"%(z,k),
                      fillet_box((.065,y1-y0-.17,.023),radius=.01,
                      center=(x0+.83+k*.32,(y0+y1)/2,z+.297),
                      color=(.86,.87,.84)))
    for x in (x0,x1):
        for z in (.75,.94,1.95,2.12):
            R("end_bar_%s_%s"%(x,z),(x,y0,z),(x,y1,z),.021,iron,a)
        for y in (y0+(y1-y0)*.32,y0+(y1-y0)*.68):
            R("end_spindle_%s_%s"%(x,y),(x,y,1.84),
              (x,y,2.12),.014,iron,a)
    for y in (y0,y1):
        for z in (1.98,2.13):
            R("guard_%s_%s"%(y,z),(x0,y,z),(x1,y,z),.020,iron,a)
    ly=y0+.09
    for y in (ly,ly+.38):
        R("ladder_upright_"+str(y),(x1+.055,y,.13),
          (x1+.055,y,1.94),.022,iron,a)
    for z in (.31,.59,.87,1.15,1.43,1.71):
        R("rung_"+str(z),(x1+.063,ly,z),
          (x1+.063,ly+.38,z),.019,(.27,.29,.27),a)
    B("number_plate",(.105,.026,.14),(x1,y0-.031,2.21),(.39,.43,.36),a)
    B("number_mark",(.028,.006,.063),(x1,y0-.048,2.21),(.75,.77,.65),a)
    scene.include(name,a)

bunk("front_left_bunk",-3.38,-.94,-.72,.40)
bunk("rear_left_bunk",-3.38,-.94,1.17,2.25)
bunk("far_left_bunk",-3.38,-.94,2.89,3.93)

cx=-.55
cy=4.30
cab=Asset("oak_locker")
B("carcass",(.91,.44,1.90),(cx,cy,1.01),(.33,.19,.073),cab)
B("dark_open_interior",(.37,.035,1.64),
  (cx+.205,cy-.241,1.10),(.105,.071,.037),cab)
B("left_door",(.40,.065,1.78),(cx-.225,cy-.274,1.06),(.37,.225,.085),cab)
for z,h in ((.58,.67),(1.47,.81)):
    B("recessed_panel_"+str(z),(.285,.018,h),
      (cx-.225,cy-.312,z),(.30,.17,.058),cab)
for x in (cx-.445,cx-.02,cx+.445):
    B("cabinet_stile_"+str(x),(.055,.078,1.90),
      (x,cy-.27,1.04),(.40,.255,.11),cab)
B("central_shelf",(.43,.42,.045),(cx+.22,cy-.04,.89),(.43,.28,.12),cab)
B("lower_open_panel",(.37,.035,.67),
  (cx+.22,cy-.23,.47),(.28,.16,.066),cab)
B("top_cornice",(1.04,.56,.075),(cx,cy,2.00),(.39,.25,.11),cab)
B("cornice_upper",(1.10,.59,.035),(cx,cy,2.052),(.43,.29,.13),cab)
B("bottom_moulding",(.99,.51,.075),(cx,cy,.10),(.36,.21,.08),cab)
for x in (cx-.36,cx+.36):
    B("foot_"+str(x),(.12,.34,.12),(x,cy,.055),(.24,.14,.054),cab)
R("door_pull",(cx-.07,cy-.322,.99),(cx-.07,cy-.35,.99),
  .026,(.11,.095,.055),cab)
R("clothes_rail",(cx+.05,cy-.09,1.83),(cx+.40,cy-.09,1.83),
  .013,(.26,.25,.19),cab)
for k in range(4):
    xx=cx+.09+k*.075
    R("hanger_left_"+str(k),(xx,cy-.11,1.78),
      (xx-.05,cy-.11,1.67),.007,(.16,.14,.10),cab)
    R("hanger_right_"+str(k),(xx-.05,cy-.11,1.67),
      (xx+.06,cy-.11,1.67),.007,(.16,.14,.10),cab)
scene.include("cupboard",cab)

R("wall_clock_body",(-.40,4.535,2.43),(-.40,4.49,2.43),
  .115,(.48,.55,.46))
R("clock_face",(-.40,4.485,2.43),(-.40,4.476,2.43),
  .095,(.63,.68,.58))
R("clock_hand",(-.40,4.465,2.43),(-.40,4.465,2.49),
  .004,(.27,.32,.28))

fx=1.48
B("hearth_slab",(2.04,.90,.065),(fx,4.12,.025),(.29,.28,.23))
B("fireplace_black_recess",(1.45,.055,1.20),(fx,4.535,.65),(.075,.068,.050))
for row in range(9):
    z=.12+row*.115
    for col in range(6):
        x=fx-.64+col*.235+(row%2)*.115
        if x>fx+.66:
            continue
        v=random.uniform(-.035,.035)
        B("firebrick_%d_%d"%(row,col),(.219,.06,.100),
          (x,4.483,z),(.19+v,.17+v,.125+v))
for side in (-1,1):
    for j in range(4):
        B("jamb_%d_%d"%(side,j),(.29,.36,.285),
          (fx+side*.86,4.34,.16+j*.285),
          (.43+random.uniform(-.035,.035),
           .42+random.uniform(-.025,.025),.33))
for k in range(9):
    xoff=-.84+k*.21
    top=1.48+.055*(1-(xoff/.93)**2)
    bottom=1.19+.10*(1-(xoff/.93)**2)
    B("lintel_stone_"+str(k),(.207,.37,top-bottom),
      (fx+xoff,4.34,(top+bottom)/2),
      (.46+random.uniform(-.035,.035),
       .445+random.uniform(-.025,.025),.35))
for side in (-1,1):
    R("inner_iron_"+str(side),(fx+side*.67,4.105,.09),
      (fx+side*.67,4.105,1.12),.018,(.17,.16,.12))
for i in range(8):
    R("grate_"+str(i),(fx-.48+i*.13,4.19,.09),
      (fx-.48+i*.13,4.19,.28),.012,(.10,.095,.075))
R("grate_front",(fx-.56,4.18,.14),(fx+.52,4.18,.14),
  .019,(.12,.11,.085))
guard=Asset("leaning_fireguard")
for k in range(9):
    xx=fx+.38+k*.031
    R("slat_"+str(k),(xx,4.055,.11),(xx-.09,4.10,.57),
      .009,(.62,.65,.59),guard)
R("guard_upper",(fx+.29,4.10,.57),(fx+.57,4.10,.57),
  .016,(.67,.69,.62),guard)
R("guard_bottom",(fx+.38,4.055,.11),(fx+.66,4.055,.11),
  .012,(.50,.52,.46),guard)
scene.include("fireguard",guard)
R("coal_scuttle",(fx+1.16,4.06,.02),(fx+1.16,4.06,.26),
  .105,(.10,.115,.10))
R("poker",(fx+1.05,4.17,.04),(fx+1.05,4.17,.65),
  .011,(.10,.105,.085))
B("small_wall_plate",(.055,.025,.12),
  (fx+1.04,4.54,1.46),(.31,.32,.24))

bunk("foreground_right_bunk",2.87,5.22,-3.55,-2.42)
B("near_wooden_bed_edge",(.10,.13,3.12),
  (2.83,-2.54,1.56),(.42,.22,.075))

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    col=tuple(bs.inputs["Base Color"].default_value)
    bs.inputs["Roughness"].default_value=.78
    if col[0]<.18 and col[1]<.19:
        bs.inputs["Metallic"].default_value=.62
        bs.inputs["Roughness"].default_value=.36
    tex=nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=38
    tex.inputs["Detail"].default_value=3
    bump=nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.16
    bump.inputs["Distance"].default_value=.025
    nt.links.new(tex.outputs["Fac"],bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if .2<col[0]<.5 and col[0]>col[1]*1.30:
        tex.inputs["Scale"].default_value=5
        coord=nt.nodes.new("ShaderNodeTexCoord")
        mapping=nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(5,.32,5)
        nt.links.new(coord.outputs["Generated"],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs["Vector"])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(col[0]*.55,col[1]*.55,col[2]*.55,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(col[0]*1.22,col[1]*1.22,col[2]*1.22,1)
        nt.links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])

set_view((3.25,-6.65,1.80),(-.36,2.70,1.43),lens=32,sensor=36)
area_emitter((-3.13,-.10,2.17),power=1050,size=2.4,
             target=(0,1.0,.7),color=(.91,.95,1.0))
area_emitter((.3,-3.2,3.1),power=260,size=4.0,
             target=(0,2,1.0),color=(1.0,.91,.74))
area_emitter((1.1,3.4,3.17),power=105,size=2.2,
             target=(0,2,0),color=(1.0,.94,.78))

sc=bpy.context.scene
world=sc.world
if world is None:
    world=bpy.data.worlds.new("Dormitory ambient")
    sc.world=world
world.use_nodes=True
background=world.node_tree.nodes.get("Background")
if background is None:
    background=world.node_tree.nodes.new("ShaderNodeBackground")
    output=world.node_tree.nodes.get("World Output")
    if output is None:
        output=world.node_tree.nodes.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.48,.54,.64,1)
background.inputs["Strength"].default_value=.23

sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.12
