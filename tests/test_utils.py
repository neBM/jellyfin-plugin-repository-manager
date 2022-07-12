import os
import sys
import json

import pytest
from py._path.local import LocalPath
import jprm


TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data",
)


@pytest.mark.datafiles(
    os.path.join(TEST_DATA_DIR, "jprm.yaml"),
    os.path.join(TEST_DATA_DIR, "jprm.json"),
)
def test_load_manifest(datafiles: LocalPath):
    assert jprm.load_manifest(datafiles / "jprm.yaml") == json.load(
        datafiles / "jprm.json"
    )


@pytest.mark.datafiles(
    os.path.join(TEST_DATA_DIR, "jprm.yaml"),
    os.path.join(TEST_DATA_DIR, "jprm.json"),
)
def test_get_config(datafiles: LocalPath):
    assert jprm.get_config(datafiles) == json.load(datafiles / "jprm.json")


@pytest.mark.datafiles(
    os.path.join(TEST_DATA_DIR, "jprm.yaml"),
    os.path.join(TEST_DATA_DIR, "jprm.json"),
)
def test_get_config_old(datafiles: LocalPath):
    (datafiles / "jprm.yaml").rename(datafiles / "build.yaml")
    assert jprm.get_config(datafiles) == json.load(datafiles / "jprm.json")


def test_invalid_manifest(tmpdir: LocalPath):
    with open(tmpdir / "jprm.yaml", "wt") as fh:
        fh.write("]]]")
    assert jprm.get_config(tmpdir) is None


def test_no_manifest(tmpdir: LocalPath):
    assert jprm.get_config(tmpdir) is None


@pytest.mark.parametrize(
    "cmd,kw,res",
    [
        ("true", {}, ("", "", 0)),
        ("false", {}, ("", "", 1)),
        ("echo '123'", {"shell": True}, ("123\n", "", 0)),
        ("echo '123'", {"shell": False}, ("'123'\n", "", 0)),
        ("echo '123' > /dev/stderr", {"shell": True}, ("", "123\n", 0)),
    ],
)
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Unix only commands")
def test_run_os_command(cmd, kw, res):
    assert jprm.run_os_command(cmd, **kw) == res


def test_run_os_command_error(tmpdir: LocalPath):
    with pytest.raises(FileNotFoundError):
        jprm.run_os_command("echo", cwd=tmpdir / "potatoe")


def test_version():
    ver = jprm.Version("1.2.3.0")
    assert ver.major == 1
    assert ver.minor == 2
    assert ver.build == 3
    assert ver.revision == 0
    assert str(ver) == "1.2.3.0"
    assert ver.values() == (1, 2, 3, 0)
    assert ver.keys() == ("major", "minor", "build", "revision")
    assert dict(ver.items()) == {"major": 1, "minor": 2, "build": 3, "revision": 0}
    assert "major" in ver
    assert len(ver) == 4

    del ver["revision"]
    assert str(ver) == "1.2.3"
    ver.major = 2
    assert str(ver) == "2.2.3"
    ver.minor = 0
    assert str(ver) == "2.0.3"
    ver.build = None
    assert str(ver) == "2.0"

    ver["major"] = 3
    assert str(ver) == "3.0"

    ver["minor"] = None
    assert str(ver) == "3"

    assert ver == jprm.Version(ver)

    assert repr(ver) == "<Version('3')>"
    assert [x for x in ver] == [3, None, None, None]

    assert ver.get("foo", False) is False
    assert ver.get("minor", False) is None
    assert ver.get("major", False) == 3

    assert ver == jprm.Version(3)

    with pytest.raises(ValueError):
        jprm.Version("1.2.3-beta.2")

    with pytest.raises(TypeError):
        jprm.Version(3.5)

    with pytest.raises(KeyError):
        print(ver["__len__"])

    assert ver.full() == "3.0.0.0"
