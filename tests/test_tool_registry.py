from app.agents.tool_registry import ToolRegistry


def test_tool_registry_exposes_investigator_tools():
    registry = ToolRegistry()

    assert registry.account_tools is not None
    assert registry.transaction_tools is not None
    assert registry.aml_profile_tools is not None
    assert registry.alert_tools is not None


def test_tool_registry_exposes_tool_methods():
    registry = ToolRegistry()

    assert callable(registry.get_account)
    assert callable(registry.get_transactions)
    assert callable(registry.get_aml_profile)
    assert callable(registry.get_alert_evidence)