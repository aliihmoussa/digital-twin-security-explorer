from dtsec_explorer.domain.transforms import filter_attacks


def test_filter_attacks_by_layer_property_and_query():
    attacks = [
        {
            "id": "AT1.1",
            "name": "Data Tampering",
            "description": "Modify gathered data",
            "layer_key": "layer1",
            "security_properties": ["Integrity", "Authorization"],
            "severity": "High",
        },
        {
            "id": "AT2.1",
            "name": "Model Poisoning",
            "description": "Poison model updates",
            "layer_key": "layer2",
            "security_properties": ["Integrity"],
            "severity": "Critical",
        },
    ]

    result = filter_attacks(
        attacks,
        layer_key="layer1",
        security_property="Integrity",
        severities=["High", "Critical"],
        query="tamper",
    )

    assert [a["id"] for a in result] == ["AT1.1"]


def test_filter_attacks_sorts_by_severity_then_id():
    attacks = [
        {"id": "ATX.2", "name": "B", "description": "", "layer_key": "layer1", "security_properties": [], "severity": "Low"},
        {"id": "ATX.1", "name": "A", "description": "", "layer_key": "layer1", "security_properties": [], "severity": "Critical"},
        {"id": "ATX.3", "name": "C", "description": "", "layer_key": "layer1", "security_properties": [], "severity": "Critical"},
    ]

    result = filter_attacks(attacks, None, "All", ["Critical", "Low"], "")
    assert [a["id"] for a in result] == ["ATX.1", "ATX.3", "ATX.2"]
