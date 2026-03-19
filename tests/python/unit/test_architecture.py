from importlib import import_module

from verabrain import can_depend_on, list_allowed_dependencies, list_layers


def test_list_layers_returns_core_first_boundary_order() -> None:
    assert list_layers() == ("core", "application", "adapters", "infrastructure")


def test_application_and_infrastructure_depend_inward() -> None:
    assert list_allowed_dependencies("application") == ("core",)
    assert list_allowed_dependencies("infrastructure") == ("core", "application")


def test_core_and_adapters_do_not_gain_reverse_dependencies() -> None:
    assert can_depend_on("core", "application") is False
    assert can_depend_on("core", "adapters") is False
    assert can_depend_on("adapters", "core") is False
    assert can_depend_on("adapters", "infrastructure") is False


def test_layer_packages_are_importable() -> None:
    for module_name in (
        "verabrain.core",
        "verabrain.application",
        "verabrain.adapters",
        "verabrain.infrastructure",
    ):
        module = import_module(module_name)
        assert module.__doc__
