from typing import Any, Callable, Generic, Mapping, Optional, Protocol, TypeVar, cast, get_args, runtime_checkable


@runtime_checkable
class JsonSerializable(Protocol):
    def to_dict(self) -> dict:
        ...

    @classmethod
    def from_dict(cls, data: dict) -> 'JsonSerializable':
        ...


JsonSerializableType = TypeVar('JsonSerializableType', bound=JsonSerializable)


class JsonSerializableList(list[JsonSerializableType]):
    def __init__(
        self,
        item_type: Optional[type[JsonSerializableType]] = None,
        data: Optional[list[JsonSerializableType]] = None,
    ):
        self.item_type = item_type
        for item in data or []:
            if isinstance(item, JsonSerializable):
                self.append(item)
        self.requires_save = False

    def to_dict(self) -> dict:
        return {
            'data': [item.to_dict() for item in self],
        }
        
    def clear(self):
        super().clear()

    def replace_from_dict(self, data: list[dict]):
        self.clear()
        self.extend(self._deserialize_items(data))

    def merge_missing_from_dict(self, data: list[dict]):
        existing_data = {id(item): item for item in self}
        
        for item in self._deserialize_items(data):
            if id(item) not in existing_data:
                self.append(item)

    def _deserialize_items(self, data: list[dict]) -> list[JsonSerializableType]:
        item_type = self._resolve_item_type()
        return [
            cast(JsonSerializableType, item_type.from_dict(entry))
            for entry in data
        ]

    def _resolve_item_type(self) -> type[JsonSerializableType]:
        if self.item_type is not None:
            return self.item_type

        orig_class = getattr(self, '__orig_class__', None)
        if orig_class is not None:
            generic_args = get_args(orig_class)
            if generic_args:
                item_type = generic_args[0]
                if isinstance(item_type, type):
                    self.item_type = cast(type[JsonSerializableType], item_type)
                    return self.item_type

        raise TypeError(
            'Could not resolve the list item type. '
            'Instantiate with an explicit item_type or use a typed generic like '
            'JsonSerializableList[MyValue](...).'
        )

    @classmethod
    def from_dict(
        cls,
        data: list[dict],
        item_type: Optional[type[JsonSerializableType]] = None,
    ) -> 'JsonSerializableList[JsonSerializableType]':
        container = cls(item_type=item_type)
        container.replace_from_dict(data)
        return container


T_DICT_KEY = TypeVar('T_DICT_KEY')
T_SERIALIZABLE_VALUE = TypeVar('T_SERIALIZABLE_VALUE', bound=JsonSerializable)


class JsonSerializableDictionary(dict[T_DICT_KEY, T_SERIALIZABLE_VALUE]):
    def __init__(
        self,
        value_type: Optional[type[T_SERIALIZABLE_VALUE]] = None,
        data: Optional[dict[T_DICT_KEY, T_SERIALIZABLE_VALUE]] = None,
        key_decoder: Optional[Callable[[str], T_DICT_KEY]] = None,
        key_encoder: Optional[Callable[[T_DICT_KEY], str]] = None,
    ):
        self.value_type = value_type
        self.key_decoder = key_decoder or cast(Callable[[str], T_DICT_KEY], lambda key: cast(T_DICT_KEY, key))
        self.key_encoder = key_encoder or cast(Callable[[T_DICT_KEY], str], lambda key: str(key))
        super().__init__(data if data is not None else {})
        self.requires_save = False

    def to_dict(self) -> dict[str, dict]:
        return {
            self.key_encoder(key): value.to_dict()
            for key, value in self.items()
        }

    def clear(self):
        super().clear()

    def replace_from_dict(self, data: Mapping[str, dict]):
        self.clear()
        self.update(self._deserialize_items(data))

    def merge_missing_from_dict(self, data: Mapping[str, dict]):
        for key, value in self._deserialize_items(data).items():
            if key not in self:
                self[key] = value

    def _deserialize_items(self, data: Mapping[str, dict]) -> dict[T_DICT_KEY, T_SERIALIZABLE_VALUE]:
        value_type = self._resolve_value_type()
        return {
            self.key_decoder(key): cast(T_SERIALIZABLE_VALUE, value_type.from_dict(value))
            for key, value in data.items()
        }

    def _resolve_value_type(self) -> type[T_SERIALIZABLE_VALUE]:
        if self.value_type is not None:
            return self.value_type

        orig_class = getattr(self, '__orig_class__', None)
        if orig_class is not None:
            generic_args = get_args(orig_class)
            if len(generic_args) >= 2:
                value_type = generic_args[1]
                if isinstance(value_type, type):
                    self.value_type = cast(type[T_SERIALIZABLE_VALUE], value_type)
                    return self.value_type

        raise TypeError(
            'Could not resolve the dictionary value type. '
            'Instantiate with an explicit value_type or use a typed generic like '
            'JsonSerializableDictionary[str, MyValue](...).'
        )

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, dict],
        value_type: Optional[type[T_SERIALIZABLE_VALUE]] = None,
        key_decoder: Optional[Callable[[str], T_DICT_KEY]] = None,
        key_encoder: Optional[Callable[[T_DICT_KEY], str]] = None,
    ) -> 'JsonSerializableDictionary[T_DICT_KEY, T_SERIALIZABLE_VALUE]':
        container = cls(value_type=value_type, key_decoder=key_decoder, key_encoder=key_encoder)
        container.replace_from_dict(data)
        return container
