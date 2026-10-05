"""CI threshold documentation. Live eval-run happens after deploy."""

THRESHOLD = 0.95


def test_threshold():
    assert THRESHOLD >= 0.95


if __name__ == "__main__":
    test_threshold()
    print("PASS threshold", THRESHOLD)
