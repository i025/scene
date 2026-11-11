# Reference inventory and visual comparison (normalized image coordinates):
# Raised platform: reference front edge crosses approximately (0,.58) to
# (.69,1); rendered edge crosses approximately (0,.50) to (1,.98), with
# too much empty foreground and its right end visible.
# Foreground cow: reference approximately (.35,.38)-(.84,.89); rendered
# cows are much smaller, approximately (.20,.40)-(.72,.70), with overly
# regular round patches and little contrast.
# Door: reference approximately (.32,.04)-(.43,.19); rendered approximately
# (.44,.23)-(.51,.43). Its top is much too low.
# Divider top bend: reference approximately (.84,.28); its proposed world
# correspondence projected to (.618,.494) previously. Correspondence is
# uncertain because multiple rails overlap.
# Worker: reference cropped by the right edge near (.95,.13)- (1,.43);
# previous render shows the worker near (.96,.38)- (1,.64).
# Rails cross in front of the cows; their long edges slope gently down to
# the right. The previous render has too much floor, small animals and a
# high view angle. Largest discrepancies, in order: framing and viewing
# angle, cow size and black/white distribution, then rail shape and detail.
#
# Corrections: lower camera and increase lens to enlarge foreground cows and
# bring the door upward; retain the foreground cow back as a protected anchor.
# Increase cow body width and patch coverage about each cow's own center.
# Camera trial calculations below compare the exact same four world points
# and reference estimates used before, without claiming that the projected
# points are necessarily visible contours. The platform edge and divider
# correspondences are uncertain. The door and cow back are prioritized.
# Camera pose, target and lens are independent parameters.
#
# Estimated expanded primitives: architecture 23, rails 8*10+2=82,
# cows 6*19=114, worker 7, bedding 22. Approximately 248 meshes.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(14)
scene = Scene("Modern free stall dairy barn")

STALL_SPACING = 1.28
PLATFORM_FRONT = -1.65
PLATFORM_BACK = 2.05
PLATFORM_TOP = .18

# The camera candidates are intentionally modest, rather than a large
# unchecked extrapolation. Numerical selection is performed after realization.
CAMERA_POSITION_OLD = (8.3, -12.8, 6.2)
CAMERA_TARGET_OLD = (0.0, .25, .95)
CAMERA_LENS_OLD = 45
CAMERA_POSITION_TRIAL = (8.3, -12.8, 5.5)
CAMERA_TARGET_TRIAL = (0.0, .25, 1.02)
CAMERA_LENS_TRIAL = 49
CAMERA_POSITION_FINAL = (8.3, -12.8, 4.8)
CAMERA_TARGET_FINAL = (0.0, .25, 1.08)
CAMERA_LENS_FINAL = 53

concrete = (.40,.41,.40)
walkway = (.29,.28,.23)
steel = (.51,.56,.58)
wall = (.46,.48,.48)
upper = (.73,.76,.77)
white = (.73,.72,.66)
black = (.025,.030,.027)
pink = (.46,.32,.29)
blue = (.025,.075,.17)

architecture = Asset("Barn architecture")
architecture.include("walkway", box((19,12,.14), center=(0,0,-.09), color=walkway))
architecture.include("raised concrete resting platform", box((15,3.7,.26),
    center=(0,(PLATFORM_FRONT+PLATFORM_BACK)/2,.05), color=concrete))
architecture.include("front concrete fascia", box((15,.10,.27),
    center=(0,PLATFORM_FRONT,.04), color=(.30,.31,.30)))
architecture.include("rear concrete wall", box((19,.16,2.6),
    center=(0,3.65,1.30), color=wall))
architecture.include("upper light wall", box((19,.18,1.55),
    center=(0,3.65,3.22), color=upper))
architecture.include("blue metal door", box((1.35,.10,1.95),
    center=(-2.55,3.52,1.05), color=blue))
architecture.include("door recessed panel", box((1.17,.04,1.60),
    center=(-2.55,3.44,1.04), color=(.035,.10,.21)))
for i,x in enumerate((-8,-5.6,-3.22,-.5,2.3,5.3,8.2)):
    architecture.include("blue wall column %d"%i, box((.11,.22,4.0),
        center=(x,3.48,2), color=(.045,.13,.24)))
for i,x in enumerate((-7,-5,-3,-1,1,3,5,7)):
    architecture.include("upper wall seam %d"%i, box((.025,.03,1.55),
        center=(x,3.53,3.22), color=(.43,.46,.47)))
scene.include("architecture", architecture)

rails = Asset("Galvanized steel free stall dividers")
for i in range(8):
    x = (i-3.5)*STALL_SPACING
    stall = Asset("Divider %02d"%i)
    points = [(x,1.78,1.48), (x,.30,1.48), (x,-.16,1.46),
              (x,-.39,1.39), (x,-.48,1.27), (x,-.47,1.12),
              (x,-.35,1.02), (x,-.12,.94), (x,1.48,.78)]
    for j in range(len(points)-1):
        stall.include("loop segment %d"%j,
            rod(.038,start=points[j],end=points[j+1],color=steel))
    stall.include("front support",rod(.045,start=(x,-.48,.18),
        end=(x,-.48,1.24),color=steel))
    stall.include("rear support",rod(.042,start=(x,1.77,.18),
        end=(x,1.77,1.48),color=steel))
    rails.include("stall %02d"%i,stall)
for k,y in enumerate((1.72,2.12)):
    rails.include("continuous top rail %d"%k,rod(.033,
        start=(-5.9,y,1.50+k*.13),end=(5.9,y,1.50+k*.13),color=steel))
scene.include("stall equipment",rails)

def ellipsoid(center, scale, color):
    n = ball(1,center=center,color=color)
    n.resize(scale,pivot=center)
    return n

def make_cow(name,x,y,s,variant):
    a = Asset(name)
    def E(part,dx,dy,z,sx,sy,sz,color):
        center=(x+dx*s,y+dy*s,PLATFORM_TOP+z*s)
        a.include(part,ellipsoid(center,(sx*s,sy*s,sz*s),color))
    # Individual elongated, low bodies; black animals alternate with white.
    body_color = black if variant in (1,3) else white
    E("barrel",0,0,.43,.53,.94,.40,body_color)
    E("rump",0,-.64,.39,.50,.39,.35,body_color)
    E("shoulder",0,.57,.43,.46,.42,.34,body_color)
    E("neck",.06,.84,.47,.32,.43,.30,black)
    E("head",.12,1.15,.46,.26,.34,.23,black)
    E("muzzle",.12,1.42,.39,.20,.15,.12,pink)
    E("wet nose",.12,1.52,.40,.17,.085,.075,(.11,.10,.09))
    E("left ear",-.15,1.10,.61,.17,.16,.065,black)
    E("right ear",.37,1.10,.61,.17,.16,.065,black)
    E("folded rear leg",-.25,-.68,.16,.26,.34,.13,white)
    E("folded foreleg",.23,.62,.15,.23,.36,.12,white)
    E("udder",.13,-.44,.17,.23,.29,.14,pink)
    if body_color == white:
        patches=[(-.46,-.42,.49,.12,.33,.24),
                 (-.45,.27,.53,.12,.27,.25),
                 (.45,-.57,.44,.12,.30,.22),
                 (.46,.05,.52,.12,.28,.24),
                 (-.08,-.29,.79,.26,.28,.04),
                 (.10,.35,.78,.25,.24,.045)]
        for j,(dx,dy,z,sx,sy,sz) in enumerate(patches):
            E("dark coat patch %d"%j,dx,dy,z,sx,sy,sz,black)
    else:
        E("white shoulder marking",-.44,.38,.51,.12,.26,.22,white)
        E("white rump marking",.40,-.55,.48,.12,.24,.20,white)
    a.include("tail",rod(.028*s,
        start=(x,y-.92*s,PLATFORM_TOP+.33*s),
        end=(x+.17*s,y-1.28*s,PLATFORM_TOP+.10*s),
        color=(.20,.18,.14)))
    return a

cows=Asset("Resting Holstein cows")
for i,(x,y,s) in enumerate(((-3.95,-.02,.91),(-2.68,.04,.94),
                            (-1.38,.02,.96),(-.06,.00,1.00),
                            (1.23,.12,.98),(2.53,.38,.91))):
    cows.include("cow %d"%(i+1),make_cow("Holstein %d"%(i+1),x,y,s,i))
scene.include("cows",cows)

bedding=Asset("Thin scattered bedding")
for i in range(22):
    x=random.uniform(-5.7,5.7)
    y=random.uniform(-1.52,1.95)
    bedding.include("straw %02d"%i,box((random.uniform(.08,.22),.018,.008),
        center=(x,y,.187),color=random.choice(((.42,.36,.23),(.52,.46,.30),(.30,.29,.22)))))
scene.include("bedding",bedding)

person=Asset("Barn worker")
px,py=5.15,2.95
person.include("torso",box((.40,.25,.60),center=(px,py,1.35),color=(.08,.20,.37)))
person.include("head",ellipsoid((px,py,1.83),(.14,.13,.18),(.49,.35,.27)))
person.include("hair",ellipsoid((px,py+.015,1.95),(.14,.13,.09),(.12,.10,.09)))
for side in (-1,1):
    person.include("leg %d"%side,rod(.085,start=(px+side*.10,py,1.06),
        end=(px+side*.12,py,.43),color=(.08,.11,.15)))
    person.include("arm %d"%side,rod(.07,start=(px+side*.23,py,1.54),
        end=(px+side*.29,py-.06,1.15),color=(.08,.20,.37)))
scene.include("worker",person)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.70,.76,.82,1)
background.inputs["Strength"].default_value=.48

# SceneAct meshes carry shared finishes. Adjust surface response by their
# material colors, preserving the separate editable geometry.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    c=bsdf.inputs["Base Color"].default_value
    if abs(c[0]-steel[0])<.015 and abs(c[1]-steel[1])<.015:
        bsdf.inputs["Metallic"].default_value=.72
        bsdf.inputs["Roughness"].default_value=.26
    elif c[0]<.15 and c[1]<.15 and c[2]<.15:
        bsdf.inputs["Roughness"].default_value=.50
    else:
        bsdf.inputs["Roughness"].default_value=.83

sc.render.resolution_x=512
sc.render.resolution_y=285
sc.render.resolution_percentage=100

# The world coordinates below are unchanged from the previous execution.
# Cow geometry was enlarged about its own center, but the stable comparison
# point remains the same world-space point, rather than being moved to fit.
# Old projections from the prior execution are independently recomputed.
anchors=[
    ("platform edge",(1.5,PLATFORM_FRONT,PLATFORM_TOP),(.68,.98),.5),
    ("door top left",(-3.225,3.43,2.025),(.32,.04),1.4),
    ("cow upper back",(-.06,-.05,.96),(.50,.46),1.3),
    ("divider top",(1.92,-.16,1.46),(.84,.28),.4),
]

def camera_state(position,target,lens):
    set_view(position,target,lens=lens)
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    projection=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    result=[]
    for name,p,ref,w in anchors:
        q=projection @ cam.matrix_world.inverted() @ Vector((*p,1))
        result.append(None if q.w<=1e-8 else
            (.5*(q.x/q.w+1),.5*(1-q.y/q.w)))
    return result

states=[
    (CAMERA_POSITION_OLD,CAMERA_TARGET_OLD,CAMERA_LENS_OLD),
    (CAMERA_POSITION_TRIAL,CAMERA_TARGET_TRIAL,CAMERA_LENS_TRIAL),
    (CAMERA_POSITION_FINAL,CAMERA_TARGET_FINAL,CAMERA_LENS_FINAL),
]
projected=[camera_state(*state) for state in states]
def score(points):
    return sum(w*((p[0]-ref[0])**2+(p[1]-ref[1])**2)
        for (_,_,ref,w),p in zip(anchors,points) if p is not None)

# Protect the cow-back anchor against a large regression. The door has the
# strongest weight because its visible rectangular corner is more reliable.
old_cow_error=math.dist(projected[0][2],anchors[2][2])
eligible=[0]
for i in (1,2):
    cow_error=math.dist(projected[i][2],anchors[2][2])
    if cow_error<=old_cow_error+.055:
        eligible.append(i)
chosen=min(eligible,key=lambda i:score(projected[i]))
camera_state(*states[chosen])
for j,(name,p,ref,w) in enumerate(anchors):
    old=projected[0][j]
    trial=projected[1][j]
    final=projected[chosen][j]
    if old is None or trial is None or final is None:
        continue
    def residual(q):
        return ((q[0]-ref[0])*512,(q[1]-ref[1])*285)
    print("%s ref=%s old=%s old_res_px=%s trial=%s trial_res_px=%s final=%s final_res_px=%s"%
          (name,ref,old,residual(old),trial,residual(trial),final,residual(final)))

area_emitter((0,-2,7),power=1600,size=8,target=(0,0,0),color=(.82,.90,1))
area_emitter((-5,1,5),power=700,size=6,target=(0,0,0),color=(.90,.94,1))
