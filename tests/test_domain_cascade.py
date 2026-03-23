from dtsec_explorer.domain.cascade import build_cascade_sankey, parse_cascade_target_layers


def test_parse_cascade_target_layers():
    assert parse_cascade_target_layers("Layer 2: Wrong commands") == [2]
    assert parse_cascade_target_layers("Layer 1 and Layer 3 impacted") == [1, 3]


def test_build_cascade_sankey_deduplicates_per_attack_target_pair():
    flat_attacks = [
        {
            "layer_key": "layer1",
            "cascade_effects": [
                "Layer 2: issue",
                "Layer 2: another mention",
                "Layer 3: issue",
            ],
        },
        {
            "layer_key": "layer2",
            "cascade_effects": ["Layer 3: issue", "Complete DT failure"],
        },
    ]

    labels, source, target, value = build_cascade_sankey(flat_attacks)
    assert labels == ["Physical (L1)", "Intermediate (L2)", "Digital (L3)"]

    flows = {(s, t): v for s, t, v in zip(source, target, value)}
    assert flows[(0, 1)] == 1
    assert flows[(0, 2)] == 1
    assert flows[(1, 2)] == 1
