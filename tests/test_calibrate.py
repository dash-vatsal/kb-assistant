from kb.calibration import suggest_threshold


def test_separable_distributions():
    t, rec, ref = suggest_threshold(pos=[0.6, 0.7, 0.8], neg=[0.1, 0.2, 0.3])
    assert 0.3 < t <= 0.6 and rec == 1.0 and ref == 1.0


def test_overlap_reports_tradeoff():
    t, rec, ref = suggest_threshold(pos=[0.3, 0.7], neg=[0.4, 0.2])
    assert 0 <= rec <= 1 and 0 <= ref <= 1
