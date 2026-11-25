import pytest

from autotrainer.core.message.message_handler import CommandResult


def test_skipped_defaults_to_false():
    assert CommandResult().skipped is False


def test_str_includes_skipped():
    assert "skipped=True" in str(CommandResult(succeeded=True, skipped=True))


@pytest.mark.parametrize("succeeded", [True, False])
def test_bool_follows_succeeded_when_skipped(succeeded):
    assert bool(CommandResult(succeeded=succeeded, skipped=True)) is succeeded
