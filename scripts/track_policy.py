"""Central file/status policy shared by catalog validation and generation.

Canonical paths are already checked against their catalog owner. Unknown/future
tracks retain the previous two-language requirement until separately authorized.
"""

READY = frozenset({"implemented", "tested", "reviewed"})


# Preserved identity helper for the B5/B7 shared canonical. Phase19 now
# authorizes the NumPy ML language policy throughout B7; AI remains deferred.
def shared_numpy_autoencoder(algorithm: dict) -> bool:
    return (algorithm.get("id") == "vanilla-autoencoders"
            and algorithm.get("category") == "B7"
            and algorithm.get("canonical_location") == "machine-learning/deep-learning/vanilla-autoencoders")


def track(algorithm: dict) -> str:
    path = algorithm.get("canonical_location", "")
    if path.startswith("dsa/"):
        return "dsa"
    if path.startswith("machine-learning/"):
        return "machine-learning"
    return "deferred"


def cpp_required(algorithm: dict) -> bool:
    return track(algorithm) != "machine-learning"


def implementation_fields(algorithm: dict) -> tuple[str, ...]:
    fields = ("documentation_status", "python_status")
    return fields + (("cpp_status",) if cpp_required(algorithm) else ())


def is_complete(algorithm: dict) -> bool:
    return (
        all(algorithm.get(field) in READY for field in implementation_fields(algorithm))
        and algorithm.get("test_status") in {"tested", "reviewed"}
        and (cpp_required(algorithm) or algorithm.get("cpp_status") in READY | {"planned"})
    )
