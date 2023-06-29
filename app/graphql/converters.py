import strawberry


def strawberry_to_dict(
        strawberry_dataclass: object, *, include: set[str] | None = None, exclude: set[str] | None = None
) -> dict:
    return {
        k: v for k, v in strawberry.asdict(strawberry_dataclass).items()
        if (include is None or k in include) and (exclude is None or k not in exclude)
    }
