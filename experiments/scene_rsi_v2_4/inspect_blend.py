"""Fixed Blender evidence collector; never overwrite the submitted project.

Run with Blender --background --python inspect_blend.py -- --blend FILE
--output-dir DIR --mode inspect|views|mechanical|probe --settings JSON.
All geometric measurements are in scene units or explicitly normalized; AABBs
are approximate extents, not mesh collision tests or 3D reconstruction accuracy.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'backend'))
from devices import configure_cycles


STRUCTURAL_WORDS = {"floor", "wall", "walls", "ceiling", "ground"}
BLUE = (0.02, 0.08, 0.8, 1.0)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False))


def matrix_values(matrix) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix]


def finite(values) -> bool:
    return all(math.isfinite(float(value)) for value in values)


def json_number(value):
    if isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, "__len__") and not isinstance(value, (str, bytes)):
        return [json_number(v) for v in value]
    return None


def material_values(material) -> dict | None:
    if material is None:
        return None
    result = {
        "name": material.name,
        "diffuse_color": list(material.diffuse_color),
        "roughness": material.roughness,
        "metallic": material.metallic,
        "use_nodes": material.use_nodes,
        "nodes": [],
        "links": [],
    }
    if material.use_nodes:
        for node in sorted(material.node_tree.nodes, key=lambda item: item.name):
            inputs = {}
            for socket in node.inputs:
                if hasattr(socket, "default_value"):
                    value = json_number(socket.default_value)
                    if value is not None:
                        inputs[socket.identifier] = value
            outputs = {socket.identifier: json_number(socket.default_value)
                       for socket in node.outputs if hasattr(socket, "default_value")}
            record = {"name": node.name, "type": node.bl_idname, "inputs": inputs, "outputs": outputs}
            if hasattr(node, "color_ramp"):
                record["color_ramp"] = [[element.position, list(element.color)]
                                        for element in node.color_ramp.elements]
            result["nodes"].append(record)
        result["links"] = sorted(
            [link.from_node.name, link.from_socket.identifier,
             link.to_node.name, link.to_socket.identifier]
            for link in material.node_tree.links
        )
    return result


def is_structural(obj) -> bool:
    # Frozen name-based applicability rule, not a semantic object detector.
    separated = re.sub(r"([a-z])([A-Z])", r"\1_\2", obj.name).lower()
    words = set(re.findall(r"[a-z]+", separated))
    return bool(words & STRUCTURAL_WORDS)


def mesh_valid(obj) -> bool:
    return obj.type == "MESH" and len(obj.data.vertices) > 0 and all(
        finite(vertex.co) for vertex in obj.data.vertices
    ) and finite(value for row in obj.matrix_world for value in row)


def descendants(obj) -> list:
    return sorted(obj.children_recursive, key=lambda item: item.name)


def parent_chain(obj) -> list[str]:
    names = []
    parent = obj.parent
    while parent is not None:
        names.append(parent.name)
        parent = parent.parent
    return names


def bounds(points) -> dict | None:
    points = list(points)
    if not points or not all(finite(point) for point in points):
        return None
    low = [min(point[axis] for point in points) for axis in range(3)]
    high = [max(point[axis] for point in points) for axis in range(3)]
    return {"min": low, "max": high,
            "diagonal_scene_units": (Vector(high) - Vector(low)).length,
            "kind": "approximate_AABB_not_mesh_collision"}


def local_bounds(obj) -> dict | None:
    return bounds(vertex.co for vertex in obj.data.vertices) if obj.type == "MESH" else None


def world_bounds(obj) -> dict | None:
    if obj.type != "MESH":
        return None
    # Evaluated bounding-box corners include modifier extents approximately.
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return bounds(evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box)


def choose_target() -> dict:
    valid = [obj for obj in bpy.context.scene.objects if mesh_valid(obj) and not is_structural(obj)]
    groups = []
    for obj in bpy.context.scene.objects:
        if obj.type != "EMPTY" or obj.parent is None:
            continue
        children = descendants(obj)
        meshes = [child for child in children if child.type == "MESH"]
        if len([child for child in meshes if child in valid]) >= 2 and not any(
            is_structural(child) for child in meshes
        ):
            groups.append(obj)
    if groups:
        group = sorted(groups, key=lambda obj: obj.name)[0]
        return {"object": group.name, "kind": "group",
                "mesh_names": [obj.name for obj in descendants(group) if obj in valid],
                "group_name": group.name,
                "rule": "lexicographically first non-root EMPTY with >=2 nonstructural finite mesh descendants"}
    if valid:
        target = sorted(valid, key=lambda obj: obj.name)[0]
        return {"object": target.name, "kind": "single_mesh", "mesh_names": [target.name],
                "group_name": None, "rule": "lexicographically first nonstructural finite mesh",
                "group_not_applicable_reason": "No qualifying non-root EMPTY with at least two mesh descendants"}
    return {"object": None, "kind": None, "mesh_names": [], "group_name": None,
            "rule": "No finite nonstructural mesh is available",
            "group_not_applicable_reason": "No eligible edit target exists"}


def scene_bounds() -> dict | None:
    points = []
    for obj in bpy.context.scene.objects:
        if mesh_valid(obj) and not is_structural(obj):
            box = world_bounds(obj)
            if box:
                points.extend([box["min"], box["max"]])
    return bounds(points)


def approximate_relations(objects, diagonal):
    """AABB contact/overlap candidates only; no mesh collision or semantic truth."""
    rows = [o for o in objects if o['type'] == 'MESH' and o['world_geometry_aabb_approx']]
    contacts, overlaps = [], []
    scale = max(diagonal, 1e-9)
    for i, a in enumerate(rows):
        ba = a['world_geometry_aabb_approx']
        for b in rows[i + 1:]:
            bb = b['world_geometry_aabb_approx']
            extent = [min(ba['max'][d], bb['max'][d]) - max(ba['min'][d], bb['min'][d]) for d in range(3)]
            if all(e > 0 for e in extent):
                overlaps.append({'objects': [a['name'], b['name']], 'overlap_volume_normalized': math.prod(extent) / scale ** 3})
            if extent[0] > 0 and extent[1] > 0:
                for top, bottom, upper, lower in [(a, b, ba, bb), (b, a, bb, ba)]:
                    gap = (upper['min'][2] - lower['max'][2]) / scale
                    if abs(gap) <= 0.01:
                        contacts.append({'upper': top['name'], 'lower': bottom['name'], 'vertical_gap_normalized': gap})
    return {'approximate_support_candidates': contacts, 'approximate_overlap_candidates': overlaps, 'semantic_support_pass': None, 'true_mesh_collision_pass': None, 'limitation': 'AABB candidates only, not true mesh contact/collision; no ground truth support labels'}


def structural_checks():
    from regression import geometric_checks
    return geometric_checks()


def projected_box(obj):
    from bpy_extras.object_utils import world_to_camera_view
    camera=bpy.context.scene.camera
    if camera is None:return None
    meshes=[o for o in [obj]+descendants(obj) if o.type=='MESH']
    points=[world_to_camera_view(bpy.context.scene,camera,o.matrix_world @ Vector(v)) for o in meshes for v in o.bound_box]
    points=[v for v in points if v.z>0]
    if not points:return None
    return [min(v.x for v in points),1-max(v.y for v in points),max(v.x for v in points),1-min(v.y for v in points)]


def structure() -> dict:
    bpy.context.view_layer.update()
    objects = []
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    valid_meshes = [obj for obj in meshes if mesh_valid(obj)]
    for obj in sorted(bpy.context.scene.objects, key=lambda item: item.name):
        objects.append({
            "name": obj.name, "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "parent_chain": parent_chain(obj),
            "matrix_world": json_number(matrix_values(obj.matrix_world)),
            "matrix_local": json_number(matrix_values(obj.matrix_local)),
            "vertex_count": len(obj.data.vertices) if obj.type == "MESH" else None,
            "finite_nonempty_mesh": mesh_valid(obj) if obj.type == "MESH" else None,
            "excluded_as_structural": is_structural(obj),
            "local_vertex_bbox": local_bounds(obj), "world_geometry_aabb_approx": world_bounds(obj),
            "materials": [material_values(slot.material) for slot in obj.material_slots],
            "hide_render": obj.hide_render, "projected_bbox_normalized_approx": projected_box(obj),
        })
    target = choose_target()
    finite_matrices = all(finite(value for row in obj.matrix_world for value in row)
                          for obj in bpy.context.scene.objects)
    return {
        "blend_opened": True, "mesh_count": len(meshes),
        "finite_nonempty_mesh_count": len(valid_meshes),
        "vertex_count": sum(len(obj.data.vertices) for obj in meshes),
        "finite_matrices": finite_matrices,
        "structure_requirement": "At least 3 nonempty finite meshes, all meshes finite and all object matrices finite",
        "structure_pass": len(valid_meshes) >= 3 and len(valid_meshes) == len(meshes) and finite_matrices,
        "empty_parent_group_available": target["group_name"] is not None,
        "group_interpretation": "Structural operability only; no claim of semantic or true 3D recovery",
        "target": target, "scene_nonstructural_aabb_approx": scene_bounds(),
        "objects": objects,
        "approximate_relations": approximate_relations(objects, (scene_bounds() or {}).get("diagonal_scene_units", 1)),
        "structural_checks": structural_checks(),
        "measurement_limit": "AABB extents are approximate, not collision tests; unknown scale, no metric 3D accuracy",
    }


def configure(settings: dict) -> dict:
    settings = settings.get("render", settings)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    device = configure_cycles(scene, settings)
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.cycles.samples = int(settings.get("samples", 32))
    scene.cycles.seed = int(settings.get("seed", 0))
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = bool(settings.get("use_adaptive_sampling", False))
    if "denoise" in settings:
        scene.cycles.use_denoising = bool(settings["denoise"])
    resolution = settings.get("resolution")
    if resolution:
        scene.render.resolution_x, scene.render.resolution_y = map(int, resolution)
    if "width" in settings:
        scene.render.resolution_x = int(settings["width"])
    if "height" in settings:
        scene.render.resolution_y = int(settings["height"])
    if "formal_resolution_long_edge" in settings:
        scale = int(settings["formal_resolution_long_edge"]) / max(scene.render.resolution_x, scene.render.resolution_y)
        scene.render.resolution_x = max(1, round(scene.render.resolution_x * scale))
        scene.render.resolution_y = max(1, round(scene.render.resolution_y * scale))
    scene.render.resolution_percentage = 100
    color = settings.get("color_management", settings)
    for name in ["view_transform", "look", "exposure", "gamma"]:
        if name in color:
            setattr(scene.view_settings, name, color[name])
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.use_border = False
    scene.render.use_compositing = False
    scene.render.use_sequencer = False
    return {
        "engine": "CYCLES", "device": device['device'], "device_mapping": device, "threads": 2,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "samples": scene.cycles.samples, "seed": scene.cycles.seed,
        "use_adaptive_sampling": scene.cycles.use_adaptive_sampling,
        "denoise": scene.cycles.use_denoising,
        "view_transform": scene.view_settings.view_transform,
        "look": scene.view_settings.look, "exposure": scene.view_settings.exposure,
        "gamma": scene.view_settings.gamma,
    }


def render(output: Path, name: str, ledger: dict) -> None:
    path = output / name
    bpy.context.scene.render.filepath = str(path)
    ledger["render_attempts"] += 1
    write_json(output / "render_ledger.json", ledger)
    bpy.ops.render.render(write_still=True)
    ledger["renders_completed"] += 1
    ledger["images"].append(name)
    write_json(output / "render_ledger.json", ledger)


def snapshot_objects() -> dict:
    bpy.context.view_layer.update()
    records = {}
    for obj in bpy.context.scene.objects:
        records[obj.name] = {
            "matrix_world": matrix_values(obj.matrix_world),
            "matrix_local": matrix_values(obj.matrix_local),
            "vertices": [list(vertex.co) for vertex in obj.data.vertices] if obj.type == "MESH" else None,
            "materials": [material_values(slot.material) for slot in obj.material_slots],
            "parent": obj.parent.name if obj.parent else None,
        }
    return records


def unchanged(before: dict, after: dict, excluded: set[str]) -> dict:
    names = sorted(set(before) - excluded)
    changes = {name: [field for field, value in before[name].items()
                     if after.get(name, {}).get(field) != value] for name in names}
    changes = {name: fields for name, fields in changes.items() if fields}
    extra = sorted(set(after) - set(before))
    return {"pass": not changes and not extra, "checked_objects": len(names),
            "changed_fields": changes, "added_objects": extra,
            "comparison": "Exact direct comparison of matrices, local vertices, material values/nodes and parent; no hashes"}


def blue_material(name: str, original=None):
    material = original.copy() if original else bpy.data.materials.new(name)
    material.name = name
    material.diffuse_color = BLUE
    material.use_nodes = True
    # A prescribed material replacement, independent of original shader layout.
    material.node_tree.nodes.clear()
    shader = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = BLUE
    shader.inputs["Roughness"].default_value = 0.45
    output = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def set_blue(mesh_names: list[str]) -> None:
    for name in mesh_names:
        obj = bpy.data.objects[name]
        # Single-user mesh prevents material slots on another object changing.
        obj.data = obj.data.copy()
        if not obj.material_slots:
            obj.data.materials.append(blue_material(f"RSI_blue_{name}"))
        else:
            for index, slot in enumerate(obj.material_slots):
                obj.material_slots[index].material = blue_material(f"RSI_blue_{name}_{index}", slot.material)


def blue_success(mesh_names: list[str]) -> bool:
    return bool(mesh_names) and all(
        obj.material_slots and all(
            slot.material and max(abs(slot.material.diffuse_color[i] - BLUE[i]) for i in range(4)) < 1e-7
            and any(node.type == "BSDF_PRINCIPLED" and max(
                abs(node.inputs["Base Color"].default_value[i] - BLUE[i]) for i in range(4)
            ) < 1e-7 for node in slot.material.node_tree.nodes)
            for slot in obj.material_slots
        ) for obj in [bpy.data.objects[name] for name in mesh_names]
    )


def reload_blend(blend: Path, settings: dict) -> None:
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    configure(settings)
    bpy.context.view_layer.update()


def relative_matrices(group) -> dict:
    inverse = group.matrix_world.inverted()
    return {obj.name: matrix_values(inverse @ obj.matrix_world) for obj in descendants(group)}


def max_matrix_delta(before: dict, after: dict) -> float:
    return max((abs(before[name][row][col] - after[name][row][col])
                for name in before for row in range(4) for col in range(4)), default=0.0)


def mechanical(blend: Path, output: Path, settings: dict, initial: dict, ledger: dict) -> None:
    target = initial["target"]
    result = {"test_type": "prescribed_Blender_operations_not_text_instruction_editing",
              "target_selection": target, "original_blend_unchanged": True,
              "relation_tolerance": 1e-5,
              "material": {"applicable": bool(target["mesh_names"])},
              "move": {"applicable": target["group_name"] is not None}}
    render(output, "before.png", ledger)
    if target["mesh_names"]:
        before = snapshot_objects()
        set_blue(target["mesh_names"])
        after = snapshot_objects()
        result["material"].update({
            "target_success": blue_success(target["mesh_names"]),
            "target_geometry_unchanged": all(before[name]["vertices"] == after[name]["vertices"]
                                             and before[name]["matrix_world"] == after[name]["matrix_world"]
                                             for name in target["mesh_names"]),
            "non_target_preservation": unchanged(before, after, set(target["mesh_names"])),
            "operation": "Copy target mesh/materials, replace target surface with blue Principled shader",
        })
        result["material"]["pass"] = all([
            result["material"]["target_success"], result["material"]["target_geometry_unchanged"],
            result["material"]["non_target_preservation"]["pass"]])
        render(output, "after_material.png", ledger)
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "edited_material.blend"))
        result["material"]["edited_blend"] = "edited_material.blend"
    else:
        result["material"].update({"pass": False, "reason": "No eligible target; expected object presence is not inferred"})
    if target["group_name"]:
        reload_blend(blend, settings)
        group = bpy.data.objects[target["group_name"]]
        before = snapshot_objects()
        relative_before = relative_matrices(group)
        diagonal = initial["scene_nonstructural_aabb_approx"]["diagonal_scene_units"]
        displacement = Vector((diagonal * 0.1, 0, 0))
        old_position = group.matrix_world.translation.copy()
        matrix = group.matrix_world.copy()
        matrix.translation += displacement
        group.matrix_world = matrix
        bpy.context.view_layer.update()
        actual = group.matrix_world.translation - old_position
        relative_after = relative_matrices(group)
        relation_error = max_matrix_delta(relative_before, relative_after)
        after = snapshot_objects()
        target_names = {group.name} | {obj.name for obj in descendants(group)}
        non_target = unchanged(before, after, target_names)
        target_success = diagonal > 0 and (actual - displacement).length <= 1e-5 * max(diagonal, 1)
        result["move"].update({
            "displacement_scene_units": list(displacement), "displacement_normalized": [0.1, 0, 0],
            "normalization": "nonstructural scene AABB diagonal; no true metric scale",
            "target_success": target_success,
            "relation_max_abs_matrix_delta": relation_error,
            "part_relations_preserved": relation_error <= 1e-5,
            "non_target_preservation": non_target,
            "pass": target_success and relation_error <= 1e-5 and non_target["pass"],
        })
        render(output, "after_move.png", ledger)
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "edited.blend"))
        result["move"]["edited_blend"] = "edited.blend"
    else:
        result["move"].update({"pass": None, "reason": target["group_not_applicable_reason"]})
        if target["mesh_names"]:
            bpy.ops.wm.save_as_mainfile(filepath=str(output / "edited.blend"))
            result["edited_blend_note"] = "No combination exists; edited.blend contains the material operation"
    result["render_attempts"] = ledger["render_attempts"]
    result["renders_completed"] = ledger["renders_completed"]
    write_json(output / "mechanical.json", result)


def views(output: Path, initial: dict, ledger: dict) -> None:
    scene = bpy.context.scene
    camera = scene.camera
    box = initial["scene_nonstructural_aabb_approx"]
    if camera is None or box is None:
        write_json(output / "views.json", {"status": "not_applicable", "reason": "Missing camera or finite nonstructural bounds"})
        return
    center = (Vector(box["min"]) + Vector(box["max"])) * 0.5
    original = camera.matrix_world.copy()
    orbit = Matrix.Translation(center) @ Matrix.Rotation(math.radians(60), 4, "Z") @ Matrix.Translation(-center)
    camera.matrix_world = orbit @ original
    bpy.context.view_layer.update()
    render(output, "view_side60.png", ledger)
    # Fixed overhead rule uses the original distance, with an extent-based minimum.
    distance = max((original.translation - center).length, box["diagonal_scene_units"] * 0.6, 1e-6)
    position = center + Vector((0, 0, distance))
    camera.matrix_world = (center - position).to_track_quat("-Z", "Y").to_matrix().to_4x4()
    camera.matrix_world.translation = position
    bpy.context.view_layer.update()
    render(output, "view_top.png", ledger)
    camera.matrix_world = original
    write_json(output / "views.json", {
        "status": "completed", "rule": "Orbit original camera +60 degrees around world Z; overhead at original camera distance or 0.6 scene diagonal",
        "center_scene_units": list(center), "images": ledger["images"],
        "interpretation": "Structure inspection only; no unseen-view ground truth or recovery accuracy",
    })


def probe(output: Path, name: str, initial: dict, ledger: dict, object_id=None) -> None:
    scene = bpy.context.scene
    if name in ('camera_focal', 'camera_tilt'):
        target = {'object': None, 'mesh_names': [], 'group_name': None}
    else:
        obj = bpy.data.objects.get(object_id)
        if obj is None:
            write_json(output / 'probe.json', {'status': 'unknown_target', 'object_id': object_id})
            return
        target = {'object': obj.name, 'mesh_names': [o.name for o in [obj] + descendants(obj) if o.type == 'MESH'], 'group_name': obj.name if obj.type == 'EMPTY' else None}
    if name not in ('camera_focal', 'camera_tilt') and not target['mesh_names']:
        write_json(output / 'probe.json', {'status':'not_applicable','object_id':object_id,'reason':'Requested real object has no Mesh geometry'})
        return
    report = {"probe": name, "target_selection": target,
              "target_mesh_visibility_before": [{"object_id":n,"hide_render":bool(bpy.data.objects[n].hide_render)} for n in target['mesh_names']],
              "interpretation": "Controlled observation, not proof of causal attribution or true 3D accuracy"}
    before = snapshot_objects()
    if name == "camera_tilt":
        camera = scene.camera
        report['camera_matrix_before'] = matrix_values(camera.matrix_world)
        camera.matrix_world = camera.matrix_world @ Matrix.Rotation(math.radians(4), 4, 'X')
        bpy.context.view_layer.update()
        report['camera_matrix_after'] = matrix_values(camera.matrix_world)
        report['local_pitch_degrees'] = 4
        report['geometry_unchanged'] = unchanged(before, snapshot_objects(), {camera.name})['pass']
    elif name == "camera_focal":
        camera = scene.camera
        if camera is None or camera.data.type != "PERSP":
            report.update({"status": "not_applicable", "reason": "Requires an existing perspective camera"})
            write_json(output / "probe.json", report)
            return
        report["focal_length_before"] = camera.data.lens
        camera.data.lens *= 1.1
        report["focal_length_after"] = camera.data.lens
        report["geometry_unchanged"] = unchanged(before, snapshot_objects(), set())["pass"]
    elif not target["object"]:
        report.update({"status": "not_applicable", "reason": "No eligible target"})
        write_json(output / "probe.json", report)
        return
    elif name == "object_scale":
        obj = bpy.data.objects[target["object"]]
        report["scale_before"] = list(obj.scale)
        target_boxes = [world_bounds(bpy.data.objects[n]) for n in target["mesh_names"]]
        target_box = bounds(point for box in target_boxes if box for point in [box["min"], box["max"]])
        center = (Vector(target_box["min"]) + Vector(target_box["max"])) * 0.5
        camera_before = scene.camera.matrix_world.copy() if scene.camera else None
        original = obj.matrix_world.copy()
        obj.matrix_world = Matrix.Translation(center) @ Matrix.Scale(1.1, 4) @ Matrix.Translation(-center) @ original
        bpy.context.view_layer.update()
        report["scale_after"] = list(obj.scale)
        report["scale_factor"] = 1.1
        report["pivot_world_scene_units"] = list(center)
        report["pivot_rule"] = "Target geometry AABB center; avoids moving geometry center when SceneAct group origin is world zero"
        report["fixed_camera"] = bool(scene.camera and scene.camera.matrix_world == camera_before)
        report["non_target_preserved"] = unchanged(before, snapshot_objects(),
                                           {obj.name} | {child.name for child in descendants(obj)})["pass"]
    elif name == "object_depth":
        obj = bpy.data.objects[target['object']]
        boxes = [world_bounds(bpy.data.objects[n]) for n in target['mesh_names']]
        box = bounds(point for b in boxes if b for point in [b['min'], b['max']])
        center = (Vector(box['min']) + Vector(box['max'])) * .5
        offset = (center - scene.camera.matrix_world.translation) * .1
        report['depth_offset_scene_units'] = list(offset)
        obj.matrix_world = Matrix.Translation(offset) @ obj.matrix_world
        bpy.context.view_layer.update()
        report['non_target_preserved'] = unchanged(before, snapshot_objects(), {obj.name} | {o.name for o in descendants(obj)})['pass']
        report['intervention'] = 'Move target center 10percent farther along its camera ray, preserve size/camera.'
    elif name == "isolate":
        kept = set(target["mesh_names"])
        hidden = []
        for obj in scene.objects:
            if obj.type == "MESH" and obj.name not in kept:
                obj.hide_render = True
                hidden.append(obj.name)
        report["kept_meshes"] = sorted(kept)
        report["hidden_meshes"] = sorted(hidden)
    render(output, f"probe_{name}.png", ledger)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / 'probe_scene.blend'))
    report['probe_blend']='probe_scene.blend'
    report['original_scene_not_modified']=True
    report.update({"status": "completed", "images": ledger["images"], "render_attempts": ledger["render_attempts"]})
    write_json(output / "probe.json", report)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["inspect", "views", "mechanical", "probe", "regression"], required=True)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--test")
    parser.add_argument("--object-id")
    parser.add_argument("--probe", choices=["camera_focal", "camera_tilt", "object_scale", "object_depth", "isolate"])
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if args.mode == "probe" and not args.probe:
        parser.error("--mode probe requires --probe")
    blend = args.blend.resolve()
    output = args.output_dir.resolve()
    if output == blend.parent or blend in [output / "edited.blend", output / "edited_material.blend"]:
        parser.error("Use a separate evaluation output directory to preserve the submitted project")
    output.mkdir(parents=True, exist_ok=True)
    settings = json.loads(args.settings.read_text())
    reload_blend(blend, settings)
    actual_settings = configure(settings)
    initial = structure()
    initial["input_blend"] = str(blend)
    initial["render_settings"] = actual_settings
    write_json(output / "scene_structure.json", initial)
    ledger = {"render_attempts": 0, "renders_completed": 0, "images": [], "settings": actual_settings}
    write_json(output / "render_ledger.json", ledger)
    if args.mode == "regression":
        from regression import execute_test
        write_json(output / "regression.json", execute_test(args.test))
    elif args.mode == "mechanical":
        mechanical(blend, output, settings, initial, ledger)
    elif args.mode == "views":
        views(output, initial, ledger)
    elif args.mode == "probe":
        probe(output, args.probe, initial, ledger, args.object_id)


if __name__ == "__main__":
    main()
