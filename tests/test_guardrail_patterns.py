from cpa_harness.guardrails.patterns import (
    L0_PATTERNS, L2A_WHITELIST, L2B_WHITELIST, L2C_BLACKLIST,
    matches_any,
)


def test_l0_patterns_match_dangerous_commands():
    assert matches_any("rm -rf /", L0_PATTERNS)
    assert matches_any("rm -rf /etc", L0_PATTERNS)
    assert matches_any("mkfs.ext4 /dev/sda", L0_PATTERNS)
    assert matches_any("shutdown -h now", L0_PATTERNS)
    assert matches_any("dd if=/dev/zero of=/dev/sda", L0_PATTERNS)


def test_l0_patterns_dont_match_safe_commands():
    assert not matches_any("gcc main.c -o main", L0_PATTERNS)
    assert not matches_any("ls -la", L0_PATTERNS)
    assert not matches_any("cat main.c", L0_PATTERNS)


def test_l2a_whitelist_contains_compile_commands():
    assert "gcc" in L2A_WHITELIST
    assert "make" in L2A_WHITELIST
    assert "valgrind" in L2A_WHITELIST


def test_l2c_blacklist_contains_network_commands():
    assert "curl" in L2C_BLACKLIST
    assert "wget" in L2C_BLACKLIST
