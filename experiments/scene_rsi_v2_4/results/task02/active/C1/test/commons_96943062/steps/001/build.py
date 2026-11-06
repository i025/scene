from sceneact import *
import bpy
import math

# Estimated inventory in normalized image coordinates:
# carpet floor (0,.59)-(1,1); back beige wall (.12,.38)-(.53,.61);
# right wall (.52,0)-(1,.83), with whiteboard (.59,.26)-(.92,.58).
# Suspended tile ceiling fills the upper left, with missing tiles along the
# left margin. Bright glazed wall occupies the left edge below the ceiling.
# Hanging US flag (.45,.32)-(.51,.43); rear wall vent (.15,.44)-(.24,.48);
# small electrical boxes (.30,.46)-(.43,.54). Floor debris is distributed
# across the left foreground and center; yellow insulation overlaps strips
# at lower right (.56,.67)-(.90,.79). Hidden room extent is uncertain.
#
# Perspective estimate: longitudinal convergence around (.34,.48), rear
# floor boundary around y=.60. Scale is arbitrary; width 4.8, height 3.4.
# Expanded count: approximately 190 box/rod meshes, including ceiling grid,
# flag stripes, debris and panel frames; no Boolean or fillet expansion.

scene = Scene("Abandoned classroom")
C = {
    "wall": (.69,.67,.59),
    "ceiling": (.60,.63,.62),
    "grid": (.49,.53,.52),
    "floor": (.105,.119,.105),
    "base": (.055,.068,.064),
    "white": (.84,.86,.84),
    "metal": (.48,.53,.53),
    "dark": (.13,.16,.15),
    "yellow": (.62,.49,.17),
}
def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def cube(parent, name, size, center, color, rotation=None):
    n = box(size=size, center=center, color=color)
    if rotation:
        n.turn(euler=rotation)
    parent.include(name, n)
    return n

architecture = asset("Room architecture")
cube(architecture, "Carpet slab", (4.9,11,.12), (2.4,3.1,-.065), C["floor"])
cube(architecture, "Rear plaster wall", (4.9,.13,3.48), (2.4,8.13,1.7), C["wall"])
cube(architecture, "Right plaster wall", (.13,11,3.48), (4.865,3.1,1.7), (.77,.745,.67))
cube(architecture, "Rear black skirting", (4.8,.055,.115), (2.4,8.035,.058), C["base"])
cube(architecture, "Right black skirting", (.055,11,.115), (4.775,3.1,.058), C["base"])

windows = asset("Left translucent window wall")
cube(windows, "Translucent glazing", (.055,10.7,3.4), (-.045,3.0,1.7), (.88,.92,.92))
for y in [-1.8,-.4,1.0,2.4,3.8,5.2,6.6,8.0]:
    cube(windows, "Vertical glazing mullion %.1f" % y, (.075,.025,3.4), (0,y,1.7), (.74,.78,.77))
for z in [.05,1.15,2.25,3.35]:
    cube(windows, "Horizontal glazing rail %.2f" % z, (.075,10.8,.018), (0,3,z), (.78,.81,.80))

ceiling = asset("Suspended ceiling")
# Large individual panels leave several dark cavities next to the windows.
cube(ceiling, "Dark plenum", (5.0,11,.06), (2.4,3.0,3.56), (.105,.13,.13))
for ix in range(7):
    x = .35 + ix*.70
    for iy in range(9):
        y = -1.9 + iy*1.20
        missing = ix == 0 and iy in (3,4,5,7)
        if not missing:
            cube(ceiling, "Acoustic tile %d %d" % (ix,iy),
                 (.684,1.183,.033), (x,y,3.405), C["ceiling"])
for ix in range(8):
    cube(ceiling, "Long ceiling tee %d" % ix, (.014,10.85,.026),
         (ix*.70,3.0,3.38), C["grid"])
for iy in range(10):
    cube(ceiling, "Cross ceiling tee %d" % iy, (4.9,.014,.026),
         (2.4,-2.5+iy*1.20,3.38), C["grid"])

lights = asset("Ceiling fluorescent fixtures")
for i,(x,y) in enumerate([(1.05,.5),(1.75,3.0),(1.75,5.4)]):
    cube(lights, "Fixture metal rim %d" % i, (.63,1.12,.04), (x,y,3.374), (.58,.63,.62))
    cube(lights, "Frosted light diffuser %d" % i, (.574,1.052,.014), (x,y,3.347), (.75,.80,.79))
    cube(lights, "Diffuser central division %d" % i, (.58,.014,.018), (x,y,3.335), (.62,.67,.66))

board = asset("Right wall whiteboard")
board_y0, board_y1 = 2.40, 5.95
board_z0, board_z1 = 1.23, 2.99
cy, cz = (board_y0+board_y1)/2, (board_z0+board_z1)/2
cube(board, "White writing surface", (.035,board_y1-board_y0,board_z1-board_z0),
     (4.736,cy,cz), (.79,.82,.82))
for y in (board_y0,board_y1):
    cube(board, "Vertical aluminum end %.2f" % y, (.065,.031,1.82),
         (4.70,y,cz), (.53,.59,.60))
for z in (board_z0,board_z1):
    cube(board, "Horizontal aluminum edge %.2f" % z, (.065,3.59,.027),
         (4.70,cy,z), (.55,.61,.62))
cube(board, "Board central seam", (.007,.012,1.72), (4.709,4.65,cz), (.62,.66,.66))
cube(board, "Narrow marker tray", (.105,3.59,.026), (4.68,cy,board_z0-.026), (.56,.61,.60))
for y in (2.51,5.85):
    cube(board, "Upper mounting clip %.2f" % y, (.065,.038,.075),
         (4.70,y,3.012), (.47,.51,.50))

fixtures = asset("Rear wall fixtures")
cube(fixtures, "Vent outer metal frame", (.84,.035,.47), (.89,8.045,2.18), (.49,.54,.53))
cube(fixtures, "Vent dark inset", (.76,.025,.39), (.89,8.017,2.18), (.25,.31,.32))
for j in range(7):
    cube(fixtures, "Vent louver %d" % j, (.74,.022,.013), (.89,7.997,2.025+j*.05), (.37,.43,.43))
cube(fixtures, "Electrical recess", (.32,.04,.42), (2.17,8.026,1.92), (.39,.43,.41))
cube(fixtures, "Electrical recess interior", (.245,.022,.34), (2.17,7.997,1.92), (.12,.17,.16))
cube(fixtures, "Exposed electrical insert", (.09,.045,.24), (2.20,7.965,1.94), (.65,.67,.62))
cube(fixtures, "Dangling metal box cover", (.46,.065,.42), (2.43,7.90,1.55), (.41,.48,.47), (0,31,0))
for i,(x,z) in enumerate([(2.88,1.66),(3.13,1.65)]):
    cube(fixtures, "Small wall plate %d" % i, (.15,.025,.20), (x,8.022,z), (.77,.77,.69))
    cube(fixtures, "Plate dark insert %d" % i, (.059,.013,.055), (x,8.003,z+.025), (.37,.40,.36))

flag = asset("Hanging American flag")
flag.include("Angled flag staff", rod(radius=.012, start=(4.75,6.70,3.03),
                                     end=(3.63,6.70,3.76), color=(.20,.23,.21)))
# Narrow hanging fabric, with alternating stripes and a blue upper canton.
# Slight fold rotations retain the flag's draped vertical silhouette.
fx, fy, fz = 3.72,6.67,3.18
for i in range(13):
    x = fx + i*.025
    z = fz - i*.010
    col = (.62,.075,.07) if i%2 == 0 else (.84,.82,.72)
    cube(flag, "Hanging stripe %02d" % i, (.025,.014,.78),
         (x,fy+.045*math.sin(i*.48),z), col, (0,0,-3))
cube(flag, "Blue canton", (.177,.023,.345), (fx+.076,fy-.012,fz+.215), (.105,.16,.22))
for row in range(4):
    for col in range(4):
        cube(flag, "Canton star %d %d" % (row,col), (.009,.006,.010),
             (fx+.018+col*.038,fy-.027,fz+.09+row*.075), (.77,.80,.76))

debris = asset("Fallen ceiling debris")
# Broken panels are separate thin meshes with dark undersides and chipped overlays.
panel_data = [
    (.80,2.10,1.16,.48,12),
    (1.28,2.45,.83,.38,-17),
    (.50,4.12,.88,.39,-9),
    (.95,5.34,.82,.32,16),
    (1.65,5.62,.72,.27,-14),
    (1.82,3.32,.60,.22,4),
]
for i,(x,y,w,d,angle) in enumerate(panel_data):
    cube(debris, "Broken panel underside %d" % i, (w,d,.027), (x,y,.035),
         (.20,.23,.21), (0,2,angle))
    cube(debris, "Broken panel face %d" % i, (w*.88,d*.80,.012), (x-.025,y,.055),
         (.39,.41,.37), (0,2,angle))
    cube(debris, "Panel exposed pale edge %d" % i, (w*.62,.027,.012),
         (x,y-d*.32,.067), (.63,.64,.55), (0,0,angle))
cube(debris, "Long fallen ceiling tee", (1.40,.035,.022), (1.78,3.90,.047), (.64,.69,.69), (0,0,-13))
cube(debris, "Bent fallen tee end", (.30,.033,.025), (1.04,4.04,.06), (.68,.72,.70), (0,0,11))

insulation = asset("Yellow fallen insulation")
for i,(x,y,w,d,angle,z) in enumerate([
    (4.03,2.76,.88,1.08,-7,.10),
    (3.80,3.05,.96,.86,9,.15),
    (4.28,2.69,.80,1.00,-13,.19),
]):
    cube(insulation, "Insulation board %d" % i, (w,d,.055), (x,y,z),
         (.65+i*.015,.52+i*.012,.21), (0,-7+i*5,angle))
# Broad descending flap gives the foreground piece its bent profile.
cube(insulation, "Sloped broad insulation flap", (.91,.62,.045),
     (4.27,2.21,.13), (.69,.55,.22), (19,-4,-10))
cube(insulation, "Exposed fibrous edge", (.82,.035,.055),
     (3.77,2.74,.18), (.75,.65,.37), (0,0,9))

rails = asset("Long fallen metal wall strips")
cube(rails, "Diagonal white strip", (.065,2.68,.025), (4.40,1.13,.035), (.71,.73,.70), (0,0,25))
cube(rails, "Parallel dark metal channel", (.092,2.50,.023), (4.69,.97,.025), (.40,.44,.43), (0,0,25))
cube(rails, "Right edge pale strip", (.053,2.33,.021), (4.89,1.12,.055), (.75,.76,.70), (0,0,24))

small = asset("Loose floor fragments")
for i,(x,y,s) in enumerate([
    (2.5,4.9,.06),(3.4,4.1,.04),(3.7,3.7,.08),(1.1,6.3,.035),
    (2.1,5.3,.035),(2.85,2.8,.026),(3.5,6.8,.04),(4.1,1.0,.035)
]):
    cube(small, "Small plaster fragment %d" % i, (s,s*.57,.013),
         (x,y,.015), (.63,.64,.55), (0,0,i*29))

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70,.76,.79,1)
background.inputs["Strength"].default_value = .34

# Shared carpet material: subtle mottling, with no photograph-derived texture.
for mat in bpy.data.materials:
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value = .86
        col = bsdf.inputs["Base Color"].default_value
        if max(abs(col[j]-C["floor"][j]) for j in range(3)) < .035:
            nt = mat.node_tree
            noise = nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 160
            noise.inputs["Detail"].default_value = 2
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = .20
            ramp.color_ramp.elements[0].color = (.055,.066,.058,1)
            ramp.color_ramp.elements[1].position = .80
            ramp.color_ramp.elements[1].color = (.18,.19,.155,1)
            nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])

area_emitter(position=(.35,3.5,2.15), power=650, size=5.5,
             target=(3.7,4.2,1.4), color=(.89,.95,1.0))
area_emitter(position=(2.1,.4,3.15), power=110, size=3.5,
             target=(2.4,5.2,.6), color=(1.0,.95,.84))
set_view(position=(2.60,0,1.70), target=(4.50,8.0,1.92),
         lens=24, sensor=36)
sc.camera.data.clip_start = .05
sc.camera.data.clip_end = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = .1
