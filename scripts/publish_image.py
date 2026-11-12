"""Publish verified image bytes, then advance the existing moving main channel."""
import os
import re
import subprocess

from resolve_pricing_digest import IMAGE, inspect_ref, write_output
from bump_panopticon_pin import require_tag


def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def publish(ref, revision, run=command, inspect=inspect_ref):
    if not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('Full source revision required')
    if ref == 'refs/heads/main':
        tags = ['sha-' + revision, 'main']
    elif ref.startswith('refs/tags/'):
        tags = [require_tag(ref.removeprefix('refs/tags/'))]
    else:
        raise ValueError('Unsupported publication ref')
    digest = None
    for tag in tags:
        if tag == 'main':
            current = run(['gh', 'api', 'repos/hyperme-sh/hypermesh-pricing/commits/main', '--jq', '.sha']).strip()
            if current != revision:
                raise ValueError('Superseded main revision; channel left unchanged')
        target = IMAGE + ':' + tag
        run(['docker', 'tag', 'hypermesh-pricing:candidate', target])
        output = run(['docker', 'push', target])
        matches = set(re.findall(r'digest: (sha256:[0-9a-f]{64})(?:\s|$)', output))
        if len(matches) != 1:
            raise ValueError('Image push did not identify exactly one digest')
        pushed = matches.pop()
        if inspect(target) != pushed or (digest is not None and pushed != digest):
            raise ValueError('Published image differs from verified candidate')
        digest = pushed
    return digest


if __name__ == '__main__':
    digest = publish(os.environ['GITHUB_REF'], os.environ['GITHUB_SHA'])
    write_output(digest)
    line = 'image digest: ' + IMAGE + '@' + digest
    print(line)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
            stream.write(line + '\n')
