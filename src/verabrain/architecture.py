"""Architecture boundaries for the Python VeraBrain package skeleton."""

from typing import Final, Literal, TypeAlias

LayerName: TypeAlias = Literal["core", "application", "adapters", "infrastructure"]

_LAYER_NAMES: Final[tuple[LayerName, ...]] = (
    "core",
    "application",
    "adapters",
    "infrastructure",
)

_ALLOWED_DEPENDENCIES: Final[dict[LayerName, tuple[LayerName, ...]]] = {
    "core": (),
    "application": ("core",),
    "adapters": ("application",),
    "infrastructure": ("core", "application"),
}


def list_layers() -> tuple[LayerName, ...]:
    """Return the canonical package layer order."""

    return _LAYER_NAMES


def list_allowed_dependencies(layer: LayerName) -> tuple[LayerName, ...]:
    """Return the layers that a package layer may depend on."""

    return _ALLOWED_DEPENDENCIES[layer]


def can_depend_on(source: LayerName, target: LayerName) -> bool:
    """Report whether a source layer may depend on a target layer."""

    return target in _ALLOWED_DEPENDENCIES[source]
