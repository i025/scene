"""Low-resolution native ray distances/object IDs, not depth ground truth from a photograph."""
def run(context):
    import bpy
    from mathutils import Vector
    scene=bpy.context.scene;camera=scene.camera
    if camera is None:return {'status':'unavailable','reason':'No active camera'}
    parameters=context['parameters'];size=parameters.get('size',32)
    if not 4<=size<=64:raise ValueError('Initial action supports size4..64; design another scoped action if needed')
    wanted=set(parameters.get('object_ids',[]));mapping={}
    for name in wanted:
        obj=bpy.data.objects[name]
        for part in [obj]+list(obj.children_recursive):mapping[part.name]=name
    dep=bpy.context.evaluated_depsgraph_get()
    projection=camera.calc_matrix_camera(dep,x=scene.render.resolution_x,y=scene.render.resolution_y,
                                        scale_x=scene.render.pixel_aspect_x,scale_y=scene.render.pixel_aspect_y)
    inverse=projection.inverted();world=camera.matrix_world
    depths=[];mask=[];hits={}
    for row in range(size):
        ds=[];ms=[]
        for col in range(size):
            clip=inverse@Vector((2*(col+.5)/size-1,1-2*(row+.5)/size,-1,1))
            point=Vector((clip.x/clip.w,clip.y/clip.w,clip.z/clip.w))
            near=world@point
            origin=near if camera.data.type=='ORTHO' else world.translation
            direction=(world.to_quaternion()@Vector((0,0,-1))) if camera.data.type=='ORTHO' else (near-origin).normalized()
            hit,location,normal,index,obj,matrix=scene.ray_cast(dep,origin,direction)
            name=obj.original.name if hit else None
            distance=float((location-origin).length) if hit else None
            ds.append(distance);ms.append(mapping.get(name,name) if not wanted or name in mapping else None)
            if name:hits[name]=hits.get(name,0)+1
        depths.append(ds);mask.append(ms)
    return {'status':'ok','width':size,'height':size,'camera':camera.name,
            'ray_distance_scene_units':depths,'object_id_mask':mask,'object_hit_counts':hits,
            'scope':'Constructed-scene camera rays at original author aspect; no photo depth or unique hidden geometry truth; aliases group only explicitly requested actual IDs.'}
