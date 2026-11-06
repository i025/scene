"""Offline archive-only tests with synthetic text, not experimental observations."""
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prepare_archive', HERE / 'prepare_archive.py')
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


def run():
    body = 'Synthetic licensed-scope test only.\n家具 "chair" must retain editable parts.\n'
    tests = []
    with tempfile.TemporaryDirectory(prefix='scene_v3_archive_redaction_') as raw:
        root = Path(raw)
        used = root / 'never_opened_attachments' / 'synthetic_used.md'
        unused = root / 'never_opened_attachments' / 'synthetic_unused_test.md'
        task = root / 'results' / 'H01' / 'selection' / 'synthetic_used' / '1' / 'task.json'
        task.parent.mkdir(parents=True)
        original = {'instruction': 'Public task query.\nPUBLIC TASK ATTACHMENT ' + used.name + ':\n' + body,
                    'public_attachment_sources': [str(used)], 'role': 'H',
                    'usage': {'input_tokens': 123, 'output_tokens': 17},
                    'budget': 4, 'failure_type': 'model_service_error', 'observed_model': None}
        task.write_text(json.dumps(original, ensure_ascii=False))
        manifest = [{'scene_id': 'synthetic_used', 'attachments': [str(used)]},
                    {'scene_id': 'synthetic_unused_test', 'attachments': [str(unused)]}]
        embedded = archive.embedded_public_specs(root, manifest, [task])
        assert len(embedded) == 1 and embedded[0]['body'] == body
        assert not used.exists() and not unused.exists()
        tests.append('Only existing task records opened; attachment originals and unused Test spec paths never opened')
        for ascii_only in (False, True):
            current = original
            for depth in range(1, 4):
                data = json.dumps(current, ensure_ascii=ascii_only).encode()
                output, changes = archive.public_text(data, [], embedded)
                parsed = json.loads(output)
                for _ in range(depth - 1):
                    parsed = json.loads(parsed)
                assert 'WITHHELD_PUBLIC_TASK_ATTACHMENT' in parsed['instruction']
                assert body not in parsed['instruction']
                assert parsed['role'] == 'H' and parsed['usage'] == original['usage']
                assert parsed['budget'] == 4 and parsed['failure_type'] == original['failure_type']
                assert parsed['observed_model'] is None
                assert changes[0]['kind'] == 'embedded_public_spec_withheld'
                current = data.decode()
        tests.append('Unicode/ASCII JSON and two nested JSON serializations redact full body while role, usage, budget, failure and unknown routing remain intact')
        output, changes = archive.public_text(('Prompt:\n' + original['instruction']).encode(), [], embedded)
        assert body.encode() not in output and b'WITHHELD_PUBLIC_TASK_ATTACHMENT' in output
        assert task.read_text() == json.dumps(original, ensure_ascii=False)
        tests.append('Plain prompt redacted and original task record unchanged')
    result = {'scope': 'Synthetic deterministic archive tests only', 'status': 'passed',
              'tests': tests, 'new_model_calls': 0, 'new_Blender_jobs': 0,
              'actual_Test_specs_images_or_rubrics_opened': False}
    (HERE / 'public_specs_redaction_test.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    run()
