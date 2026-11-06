from sceneact import *
import bpy
import math

# Reference inventory (normalized image bounds, approximate):
# floor: (.03,.62)-(.97,.95), pale polished uninterrupted surface.
# ceiling: (.03,.04)-(.97,.39), pale timber boards and exposed structure.
# branching timber column: (.11,.03)-(.69,.73), dark foot, broad curved
# left and right arms, open space between arms; rear surfaces uncertain.
# transverse beam: (.03,.24)-(.97,.44), broad grey timber face with vents.
# back walls: (.03,.41)-(.97,.65), white plaster, darker low skirting.
# timber wall panels: (.30,.43)-(.40,.63) and (.79,.43)-(.92,.66).
# pendants: (.56,.11)-(.61,.28), (.91,.20)-(.96,.33).
# ceiling seams, small knots, wall grilles and exit marker are visible.
# Named assets below preserve those groups and their editable components.
# Expanded primitive estimate: about 235 boxes/rods, no booleans or fillets.
# Geometry behind the camera and beyond the visible wall edges is uncertain.

scene = Scene('Timber hall')
timber = (.44,.45,.41)
pale_wood = (.66,.67,.61)
plaster = (.80,.80,.75)
floor_color = (.77,.78,.73)
dark = (.19,.21,.18)

floor = Asset('pale polished floor')
floor.include('slab', box((24,29,.16), center=(0,5,-.08), color=floor_color))
scene.include('floor', floor)

walls = Asset('white rear enclosure')
walls.include('rear left wall', box((10,.20,4.7), center=(-4.8,8,2.35), color=plaster))
walls.include('receding right wall', box((8,.20,4.7), center=(4.2,9,2.35), color=plaster))
walls.include('right return', box((.20,10,5.8), center=(9,5,2.9), color=plaster))
walls.include('left skirting', box((10,.055,.115), center=(-4.8,7.86,.058), color=dark))
walls.include('right skirting', box((8,.055,.115), center=(4.2,8.86,.058), color=dark))
walls.include('short corner return', box((.18,1.1,3.3), center=(.2,8.5,1.65), color=plaster))
scene.include('walls', walls)

roof = Asset('boarded timber ceiling')
roof.include('ceiling substrate', box((22,27,.18), center=(0,5,5.88), color=pale_wood))
for i in range(44):
    x = -10.75 + i*.50
    roof.include('board seam %02d'%i,
                 box((.012,27,.008), center=(x,5,5.781), color=(.46,.48,.43)))
for i in range(35):
    x = -9.5 + (i%13)*1.48
    y = -4 + (i//13)*5.2 + (i%3)*.7
    roof.include('small timber knot %02d'%i,
                 ball(.021, center=(x,y,5.772), color=(.35,.37,.32)))
scene.include('ceiling', roof)

beams = Asset('exposed overhead beams')
beams.include('wide cross beam', box((22,.64,.67), center=(0,5.0,4.14), color=timber))
beams.include('cross beam upper edge', box((22,.70,.055), center=(0,5,4.50), color=(.51,.52,.47)))
beams.include('left overhead rail', box((.30,20,.36), center=(-6.1,4,5.40), color=timber))
beams.include('right overhead rail', box((.28,20,.31), center=(5.65,4,5.42), color=timber))
beams.include('rear roof post', box((.20,.22,1.55), center=(1.2,5.0,5.13), color=pale_wood))
scene.include('beams', beams)

# Curved laminated column, built as overlapping short rectangular sections.
# Each arm is a separate semantic part. Widths control occupied space and fork gap.
column = Asset('curved laminated branching column')
column_y = .2
def segment(parent, name, a, b, width, depth, color):
    dx, dz = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx,dz)
    item = box((width,depth,length+.045),
               center=((a[0]+b[0])/2,column_y,(a[1]+b[1])/2), color=color)
    item.turn('y', math.degrees(math.atan2(dx,dz)))
    parent.include(name,item)

trunk = Asset('upright trunk')
trunk_points = [(-3.05,.06),(-3.07,.65),(-3.08,1.25),(-3.09,1.85),(-3.07,2.35)]
for i in range(len(trunk_points)-1):
    segment(trunk,'trunk section %02d'%i,trunk_points[i],trunk_points[i+1],.65,.72,timber)
column.include('trunk',trunk)
column.include('dark protective foot', box((.69,.77,.12), center=(-3.05,column_y,.06), color=(.20,.23,.18)))

left_points = [(-3.08,1.65),(-3.15,2.35),(-3.28,3.05),(-3.48,3.75),
               (-3.76,4.45),(-4.08,5.12),(-4.43,5.79),(-4.78,6.45)]
right_points = [(-3.08,1.45),(-3.00,2.10),(-2.80,2.77),(-2.45,3.40),
                (-1.97,3.97),(-1.38,4.47),(-.68,4.94),(.08,5.40),
                (.90,5.86),(1.76,6.33)]
for label,points,width in [('left rising arm',left_points,.59),
                            ('broad sweeping right arm',right_points,.62)]:
    arm=Asset(label)
    for i in range(len(points)-1):
        segment(arm,'curved section %02d'%i,points[i],points[i+1],width,.72,timber)
    # Thin lamination lines on the camera-facing surface follow the curved profile.
    for j in range(8):
        offset = (j-3.5)*width/9
        for i in range(len(points)-1):
            a,b=points[i],points[i+1]
            dx,dz=b[0]-a[0],b[1]-a[1]
            L=math.hypot(dx,dz)
            ox,oz=offset*dz/L,-offset*dx/L
            line=rod(.006,start=(a[0]+ox,column_y-.369,a[1]+oz),
                     end=(b[0]+ox,column_y-.369,b[1]+oz),
                     color=(.33,.35,.31))
            arm.include('lamination %02d %02d'%(j,i),line)
    column.include(label,arm)
scene.include('main branching support',column)

panels = Asset('vertical timber wall infills')
for label,x,y,width in [('left',-3.65,7.77,1.7),('right',6.0,8.77,2.1)]:
    panel=Asset(label+' timber screen')
    panel.include('backing',box((width,.17,3.05),center=(x,y,1.525),color=pale_wood))
    for i in range(9):
        px=x-width/2+(i+.5)*width/9
        panel.include('board joint %02d'%i,
                      box((.017,.012,3.05),center=(px,y-.093,1.525),
                          color=(.44,.46,.40)))
    panels.include(label,panel)
panels.include('left panel lintel',box((2.1,.28,.25),center=(-3.65,7.73,3.17),color=timber))
panels.include('right panel lintel',box((2.4,.28,.24),center=(6,8.73,3.17),color=timber))
scene.include('wall timber',panels)

vents=Asset('rectangular ventilation grilles')
for i,(x,width) in enumerate([(-7.6,1.35),(-.6,1.5),(6.35,1.25)]):
    vent=Asset('beam grille %d'%i)
    vent.include('pale frame',box((width,.027,.29),center=(x,4.662,4.09),color=(.72,.73,.68)))
    vent.include('dark recess',box((width-.07,.016,.22),center=(x,4.641,4.09),color=(.28,.30,.27)))
    for j in range(4):
        vent.include('vertical fin %d'%j,box((.012,.012,.215),
                     center=(x-width*.34+j*width*.22,4.628,4.09),color=(.47,.49,.43)))
    vents.include('vent %d'%i,vent)
vents.include('left small wall grille',box((.76,.04,.23),center=(-7.4,7.82,3.12),color=(.40,.42,.37)))
vents.include('rear wall service grille',box((.48,.025,.18),center=(3.8,8.86,.35),color=(.62,.64,.58)))
scene.include('ventilation',vents)

fixtures=Asset('suspended cylindrical luminaires')
for label,x,y,z in [('central',1.15,1.7,4.72),('right',7.35,3.1,4.53)]:
    lamp=Asset(label+' pendant')
    lamp.include('ceiling attachment',rod(.047,start=(x,y,5.70),end=(x,y,5.78),color=dark))
    lamp.include('slim suspension',rod(.018,start=(x,y,z+.49),end=(x,y,5.72),color=dark))
    lamp.include('cylindrical shade',rod(.24,start=(x,y,z-.43),end=(x,y,z+.43),color=(.40,.42,.37)))
    lamp.include('white underside diffuser',rod(.224,start=(x,y,z-.447),end=(x,y,z-.428),color=(.96,.96,.88)))
    fixtures.include(label,lamp)
scene.include('pendants',fixtures)

details=Asset('small wall details')
details.include('exit sign backing',box((.24,.035,.19),center=(4.91,8.83,2.84),color=(.37,.43,.36)))
details.include('exit sign light mark',box((.045,.012,.12),center=(4.91,8.805,2.84),color=(.83,.85,.76)))
for i,x in enumerate([-2.5,2.8]):
    details.include('low outlet %d'%i,box((.065,.025,.052),center=(x,7.86,.15),color=(.25,.28,.23)))
scene.include('wall details',details)

realize(scene)

# Shared restrained surface variation gives the grey timber its visible grain.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.77
        c=bs.inputs['Base Color'].default_value
        if abs(c[0]-timber[0])<.025 and abs(c[1]-timber[1])<.025:
            nodes=mat.node_tree.nodes
            tex=nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=5
            tex.inputs['Detail'].default_value=2
            coord=nodes.new('ShaderNodeTexCoord')
            mapping=nodes.new('ShaderNodeVectorMath')
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(6,7,.35)
            mat.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0])
            mat.node_tree.links.new(mapping.outputs[0],tex.inputs['Vector'])
            ramp=nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.16
            ramp.color_ramp.elements[0].color=(.28,.30,.26,1)
            ramp.color_ramp.elements[1].position=.85
            ramp.color_ramp.elements[1].color=(.57,.58,.52,1)
            mat.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0])
            mat.node_tree.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        if abs(c[0]-floor_color[0])<.015:
            bs.inputs['Roughness'].default_value=.32

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.82,.84,.79,1)
background.inputs['Strength'].default_value=.65

set_view((.3,-12.8,2.45),(.15,4.8,2.96),lens=31.5,sensor=36)
area_emitter((-6,-3,4.5),power=1800,size=8,target=(-1,4,1.3))
area_emitter((5,-1,5.3),power=1200,size=7,target=(2,6,.3))
area_emitter((0,7,5.5),power=600,size=5,target=(0,2,0))
sc.render.resolution_x=512
sc.render.resolution_y=406
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.5
