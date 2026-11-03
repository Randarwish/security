"""Download an immutable dataset revision; keep data out of Git."""
import argparse
import hashlib
import json
from pathlib import Path

DATASET = 'deepset/prompt-injections'
REVISION = 'b4218bf21defc7780bfca76d7048fd23f165977a'


def prepare(output):
    from datasets import load_dataset
    output.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(DATASET, revision=REVISION)
    manifest = {'dataset': DATASET, 'revision': REVISION, 'files': {}}
    for split in ('train', 'test'):
        rows = [{'text': row['text'], 'label': int(row['label'])} for row in dataset[split]]
        if not rows or any(not isinstance(r['text'], str) or r['label'] not in (0, 1) for r in rows):
            raise ValueError('Unexpected dataset schema')
        payload = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows).encode()
        path = output / f'{split}.jsonl'
        path.write_bytes(payload)
        manifest['files'][path.name] = {'rows': len(rows), 'sha256': hashlib.sha256(payload).hexdigest()}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('data/promptshield'))
    prepare(parser.parse_args().output)
