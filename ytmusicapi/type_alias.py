from collections.abc import Callable
from typing import Any

JsonDict = dict[str, Any]
JsonList = list[JsonDict]

RequestFuncType = Callable[[str], JsonDict]
RequestFuncBodyType = Callable[[JsonDict], JsonDict]
ParseFuncType = Callable[[JsonList], JsonList]
ParseFuncDictType = Callable[[JsonDict], JsonDict]
