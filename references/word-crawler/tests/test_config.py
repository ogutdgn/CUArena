import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import config


def test_paths_and_pins():
    assert config.OUTPUT_ROOT.as_posix().endswith("output/ui-structure")
    assert config.SCHEMA_VERSION == 1
    assert config.BUILD_PREFIX == "16.0.20131"
    rd = config.new_run_dir()
    assert rd.exists() and "OneDrive" not in str(rd)


def test_boundary_for_exact_and_prefix():
    assert config.boundary_for("ribbon.file")["decision"] == "D4"
    assert config.boundary_for("ribbon.home.voice.dictate")["policy"] == "excluded"
    assert config.boundary_for("ribbon.home.copilot.copilot")["decision"] == "D8"
    assert config.boundary_for("ribbon.home.add-ins.get-add-ins")["decision"] == "D8"
    assert config.boundary_for("ribbon.home.font.bold") is None
