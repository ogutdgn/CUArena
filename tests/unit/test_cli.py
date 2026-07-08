from pipeline.run import parse_args

def test_defaults():
    a = parse_args(["notepad"])
    assert a.app == "notepad" and a.stages == "0,1" and not a.no_agent

def test_flags():
    a = parse_args(["word", "--no-agent", "--max-containers", "5"])
    assert a.no_agent and a.max_containers == 5
