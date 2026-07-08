from cpa_harness.observation import Observation


def test_observation_minimal():
    obs = Observation(tool="read_file", result="int main() {}", exit_code=0)
    assert obs.tool == "read_file"
    assert obs.result == "int main() {}"
    assert obs.exit_code == 0


def test_observation_with_signal():
    obs = Observation(tool="exec_command", result="Segmentation fault", signal=11)
    assert obs.signal == 11


def test_observation_duration_tracks():
    obs = Observation(tool="read_file", result="", exit_code=0, duration_ms=42)
    assert obs.duration_ms == 42
