import subprocess
import time
from unittest import mock

from luminous_nix.core.native_nix_api import NativeNixAPI


def _mk_result(rc=0, out="", err=""):
    class R:
        returncode = rc
        stdout = out
        stderr = err

    return R()


def test_install_uses_nix_profile_when_available():
    api = NativeNixAPI()
    calls = []

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        calls.append(cmd)
        # First check: `nix profile list`
        if isinstance(cmd, list) and cmd[:3] == ["nix", "profile", "list"]:
            return _mk_result(0, "")
        # Install call via nix profile
        if isinstance(cmd, list) and cmd[:3] == ["nix", "profile", "install"]:
            return _mk_result(0, "installed")
        return _mk_result(1, "unexpected")

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        ok, out, ms = api._install_subprocess("vim", "user", time.time())
        assert ok, out
    # Assert that nix profile install was used
    assert any(isinstance(c, list) and c[:3] == ["nix", "profile", "install"] for c in calls)
    # Ensure no nix-env fallback used
    assert not any(isinstance(c, list) and c and c[0] == "nix-env" for c in calls)


def test_install_falls_back_to_nix_env_variants():
    api = NativeNixAPI()
    calls = []

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        calls.append(cmd)
        # Pretend nix profile is unavailable
        if isinstance(cmd, list) and cmd[:3] == ["nix", "profile", "list"]:
            return _mk_result(1, "")
        # First nix-env attempt (nixpkgs)
        if isinstance(cmd, list) and cmd[:3] == ["nix-env", "-iA",]:
            # Return non-zero for first variant, zero for second
            if cmd[2].startswith("nixpkgs."):
                return _mk_result(1, "not found")
            return _mk_result(0, "installed")
        return _mk_result(1, "unexpected")

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        ok, out, ms = api._install_subprocess("vim", "user", time.time())
        assert ok, out

    # Verify both nix-env variants were attempted in order
    env_calls = [c for c in calls if isinstance(c, list) and c and c[0] == "nix-env"]
    assert env_calls, "expected nix-env calls"
    assert env_calls[0][2].startswith("nixpkgs."), env_calls
    assert env_calls[-1][2].startswith("nixos."), env_calls
