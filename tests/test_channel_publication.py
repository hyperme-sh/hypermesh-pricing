"""Mocked publication never contacts Docker, GitHub or a registry."""
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import publish_image as publisher

SHA = 'a' * 40
DIGEST = 'sha256:' + 'b' * 64


def fixture(fail_source=False, stale=False):
    calls = []
    def command(args):
        calls.append(args)
        if args[:2] == ['gh', 'api']:
            return ('c'*40 if stale else SHA) + '\n'
        if args[:2] == ['docker', 'push']:
            if fail_source:
                raise subprocess.CalledProcessError(1, args)
            return 'digest: ' + DIGEST + ' size: 123\n'
        return ''
    return calls, command


def test_main_verifies_source_before_advancing_channel():
    calls, command = fixture()
    def inspect(target):
        calls.append(['inspect', target])
        return DIGEST
    assert publisher.publish('refs/heads/main', SHA, command, inspect) == DIGEST
    immutable = publisher.IMAGE + ':sha-' + SHA
    moving = publisher.IMAGE + ':main'
    assert calls.index(['inspect', immutable]) < calls.index(['docker', 'push', moving])
    assert not any('pulls' in ' '.join(call) for call in calls)


@pytest.mark.parametrize('failure', ['push', 'verification', 'stale'])
def test_failure_before_channel_write_leaves_it_untouched(failure):
    calls, command = fixture(fail_source=failure == 'push', stale=failure == 'stale')
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        publisher.publish('refs/heads/main', SHA, command,
                          lambda target: 'sha256:'+'c'*64 if failure == 'verification' else DIGEST)
    assert not any(call[-1] == publisher.IMAGE + ':main' for call in calls)


def test_authorized_version_path_does_not_move_main():
    calls, command = fixture()
    assert publisher.publish('refs/tags/v0.1.1', SHA, command, lambda target: DIGEST) == DIGEST
    assert all(call[-1] != publisher.IMAGE + ':main' for call in calls)


def test_final_write_error_is_not_reported_as_success():
    calls, command = fixture()
    def ambiguous(args):
        if args == ['docker', 'push', publisher.IMAGE + ':main']:
            raise subprocess.CalledProcessError(1, args)
        return command(args)
    with pytest.raises(subprocess.CalledProcessError):
        publisher.publish('refs/heads/main', SHA, ambiguous, lambda target: DIGEST)
