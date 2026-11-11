"""Actual saved development evidence and stub-only wire contract; no CLI/Blender."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
import model_evidence
import pilot
import research


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def main():
    spec = importlib.util.spec_from_file_location('A03_evidence', HERE / 'before_A04_model_evidence.py')
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    rows = []
    captured = []
    current_bound = model_evidence.bound_payload

    def collect(packet, limit):
        captured.append(copy.deepcopy(packet))
        return current_bound(packet, limit)

    model_evidence.bound_payload = collect
    for version in [pilot.H_START, 'H02', 'H04']:
        dev = pilot.manifest('development')
        for start in range(0, len(dev), 3):
            paths = [ROOT / 'results' / version / 'development' / scene['scene_id'] / '1/record.json'
                     for scene in dev[start:start + 3]]
            if not all(path.exists() for path in paths):
                continue
            records = [pilot.read(path) for path in paths]
            packet, _, images = pilot.context_for(records, version, ROOT / 'initial_m', 7)
            assert len(images) == 6
            rows.append({'H': version, 'start': start, 'bytes': len(encoded(packet).encode())})
    model_evidence.bound_payload = current_bound
    assert any(row['H'] == 'H04' and row['start'] == 6 for row in rows)

    unchanged = []
    for original in captured:
        before, after = copy.deepcopy(original), copy.deepcopy(original)
        error = None
        try:
            legacy.bound_payload(before, 420000)
        except ValueError as exc:
            error = str(exc)
        current_bound(after, 420000)
        assert json.loads(encoded(after)) == after
        before.pop('common_evidence_projection')
        after.pop('common_evidence_projection')
        assert before == after  # No object ID, program, error, or observation dropped.
        unchanged.append({'legacy_error': error, 'evidence_fields_identical': True})

    packet = json.loads((HERE / 'packet_before_projection.json').read_text())
    current_bound(packet, 420000)
    calls = []
    stop = {'decision': 'stop', **{key: '' for key in
            ['scene_id', 'action_name', 'expectation', 'analysis', 'scope', 'new_action_source']},
            'parameters_json': '{}', 'changes': []}

    def stub(prompt, config, folder, images, **options):
        payload = json.loads(prompt.split('\n', 1)[1])
        assert payload['development'] == packet['development']
        assert len(prompt.encode()) <= 480000
        calls.append({'prompt_bytes': len(prompt.encode()), 'attachments': len(images)})
        (HERE / 'stub_transmitted_prompt.txt').write_text(prompt)
        return json.dumps(stop), {}

    research.call = stub
    api = research.ResearchAPI(pilot.cfg(), HERE / 'stub_only', ROOT / 'candidates/C07/H',
                               ROOT / 'candidates/C07/M', {}, ['actual_reference', 'actual_render'] * 3)
    result = research.load_meta(ROOT / 'initial_m').research(packet, api)
    assert result['decision']['decision'] == 'stop' and len(calls) == 1
    assert not list((HERE / 'stub_only').rglob('request.json'))
    oversized = {'development': [], 'evidence': 'x' * 500000}
    try:
        current_bound(oversized, 420000)
    except ValueError:
        pass
    else:
        raise AssertionError('True oversized input was allowed')
    output = {'status': 'passed', 'panels': rows, 'legacy_comparison': unchanged,
              'actual_failed_packet_default_bytes': 428577,
              'actual_failed_packet_compact_bytes': len(encoded(packet).encode()),
              'stub_calls': calls, 'same_evidence_fields': True,
              'new_CLI_calls': 0, 'new_Blender_jobs': 0,
              'packet_limit_bytes': 420000, 'M_prompt_limit_bytes': 480000}
    (HERE / 'tests.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(output, ensure_ascii=False))


if __name__ == '__main__':
    main()
