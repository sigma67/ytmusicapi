from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from typing import Any

from pydantic import BaseModel, ConfigDict


class YTMusicModel(BaseModel):
    """Base class for all response models.

    Supports both attribute and subscript access. Every declared field is always a key:
    one the API did not return reads back as ``None`` rather than raising or being absent.
    """

    # parsers may emit fields a model has not declared yet; keep them rather than drop them
    model_config = ConfigDict(extra="allow")

    def _as_dict(self) -> dict[str, Any]:
        """Declared fields in declaration order, then undeclared ones in arrival order.

        Values are left as-is, so nested models keep comparing via their own ``__eq__``.
        """
        data: dict[str, Any] = {name: getattr(self, name) for name in type(self).model_fields}
        data.update(self.model_extra or {})
        return data

    def __getitem__(self, key: str) -> Any:
        if key not in self:
            raise KeyError(key)
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key) if key in self else default

    def __contains__(self, key: object) -> bool:
        return key in type(self).model_fields or key in (self.model_extra or {})

    def keys(self) -> KeysView[str]:
        return self._as_dict().keys()

    def values(self) -> ValuesView[Any]:
        return self._as_dict().values()

    def items(self) -> ItemsView[str, Any]:
        return self._as_dict().items()

    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        return iter(self._as_dict())

    def __len__(self) -> int:
        return len(type(self).model_fields) + len(self.model_extra or {})

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            return self._as_dict() == other
        return super().__eq__(other)
