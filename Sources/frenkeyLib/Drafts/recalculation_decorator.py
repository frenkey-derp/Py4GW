from __future__ import annotations

import math
from functools import wraps
from inspect import Parameter, signature as inspect_signature
from typing import Any, Callable, TypeAlias, TypeVar, cast

import PyImGui

from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui


T = TypeVar('T')

_UNSET = object()

KeyResolver: TypeAlias = str | Callable[..., str]
ValueResolver: TypeAlias = Callable[..., Any]


class LayoutCalculationState:
    def __init__(self):
        self.signature: Any = _UNSET
        self.value: Any = None
        self.has_value = False
        self.dirty = True
        self.window_version = -1
        self.storage: dict[str, Any] = {}


class WindowLayoutState:
    def __init__(self):
        self.signature: Any = _UNSET
        self.version = 0
        self.storage: dict[str, Any] = {}
        self.scopes: dict[str, LayoutCalculationState] = {}


class LayoutRecalculationRegistry:
    def __init__(self):
        self._windows: dict[str, WindowLayoutState] = {}

    def _get_window_state(self, window_key: str) -> WindowLayoutState:
        return self._windows.setdefault(window_key, WindowLayoutState())

    def _get_scope_state(self, window_key: str, scope_key: str) -> LayoutCalculationState:
        window_state = self._get_window_state(window_key)
        return window_state.scopes.setdefault(scope_key, LayoutCalculationState())

    def get_window_storage(self, window_key: str) -> dict[str, Any]:
        return self._get_window_state(window_key).storage

    def get_scope_storage(self, window_key: str, scope_key: str) -> dict[str, Any]:
        return self._get_scope_state(window_key, scope_key).storage

    def get_cached_value(self, window_key: str, scope_key: str, default: Any = None) -> Any:
        scope_state = self._get_scope_state(window_key, scope_key)
        if scope_state.has_value:
            return scope_state.value
        return default

    def invalidate_window(self, window_key: str) -> None:
        self._get_window_state(window_key).version += 1

    def invalidate_scope(self, window_key: str, scope_key: str) -> None:
        self._get_scope_state(window_key, scope_key).dirty = True

    def invalidate_all(self, window_prefix: str | None = None) -> None:
        if window_prefix is None:
            for window_state in self._windows.values():
                window_state.version += 1
            return

        for window_key, window_state in self._windows.items():
            if window_key.startswith(window_prefix):
                window_state.version += 1

    def set_window_signature(self, window_key: str, window_signature: Any) -> bool:
        window_state = self._get_window_state(window_key)
        if window_state.signature == window_signature:
            return False

        window_state.signature = window_signature
        window_state.version += 1
        return True

    def needs_recalculation(
        self,
        window_key: str,
        scope_key: str,
        signature: Any = _UNSET,
        window_signature: Any = _UNSET,
    ) -> bool:
        if window_signature is not _UNSET:
            self.set_window_signature(window_key, window_signature)

        window_state = self._get_window_state(window_key)
        scope_state = self._get_scope_state(window_key, scope_key)

        return (
            not scope_state.has_value
            or scope_state.dirty
            or scope_state.signature != signature
            or scope_state.window_version != window_state.version
        )

    def recalculate(
        self,
        window_key: str,
        scope_key: str,
        calculator: Callable[[LayoutCalculationState], T],
        signature: Any = _UNSET,
        window_signature: Any = _UNSET,
    ) -> T:
        if window_signature is not _UNSET:
            self.set_window_signature(window_key, window_signature)

        window_state = self._get_window_state(window_key)
        scope_state = self._get_scope_state(window_key, scope_key)

        if (
            not scope_state.has_value
            or scope_state.dirty
            or scope_state.signature != signature
            or scope_state.window_version != window_state.version
        ):
            scope_state.value = calculator(scope_state)
            scope_state.signature = signature
            scope_state.has_value = True
            scope_state.dirty = False
            scope_state.window_version = window_state.version

        return cast(T, scope_state.value)


DEFAULT_LAYOUT_RECALCULATION_REGISTRY = LayoutRecalculationRegistry()


def _resolve_key(
    value: KeyResolver | None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    fallback: str,
) -> str:
    if value is None:
        return fallback
    if callable(value):
        return value(*args, **kwargs)
    return value


def _resolve_value(
    resolver: ValueResolver | None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    if resolver is None:
        return _UNSET
    return resolver(*args, **kwargs)


def _resolve_registry(owner: Any, registry_attr: str) -> LayoutRecalculationRegistry:
    if owner is None:
        return DEFAULT_LAYOUT_RECALCULATION_REGISTRY

    current = getattr(owner, registry_attr, None)
    if isinstance(current, LayoutRecalculationRegistry):
        return current

    registry = LayoutRecalculationRegistry()
    setattr(owner, registry_attr, registry)
    return registry


def invalidate_layout(
    window_key: str,
    scope_key: str | None = None,
    registry: LayoutRecalculationRegistry | None = None,
) -> None:
    active_registry = registry or DEFAULT_LAYOUT_RECALCULATION_REGISTRY
    if scope_key is None:
        active_registry.invalidate_window(window_key)
        return

    active_registry.invalidate_scope(window_key, scope_key)


def get_layout_storage(
    window_key: str,
    scope_key: str | None = None,
    registry: LayoutRecalculationRegistry | None = None,
) -> dict[str, Any]:
    active_registry = registry or DEFAULT_LAYOUT_RECALCULATION_REGISTRY
    if scope_key is None:
        return active_registry.get_window_storage(window_key)
    return active_registry.get_scope_storage(window_key, scope_key)


def recalculate_layout(
    window_key: KeyResolver,
    scope_key: KeyResolver | None = None,
    *,
    signature: ValueResolver | None = None,
    window_signature: ValueResolver | None = None,
    registry_attr: str = '_layout_recalculation_registry',
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        fallback_scope_key = func.__qualname__
        func_signature = inspect_signature(func)
        accepts_layout_state = 'layout_state' in func_signature.parameters
        accepts_layout_storage = 'layout_storage' in func_signature.parameters

        if accepts_layout_state and func_signature.parameters['layout_state'].kind not in (Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            raise TypeError(f'{func.__qualname__} uses an unsupported layout_state parameter kind.')

        if accepts_layout_storage and func_signature.parameters['layout_storage'].kind not in (Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            raise TypeError(f'{func.__qualname__} uses an unsupported layout_storage parameter kind.')

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            owner = args[0] if args else None
            registry = _resolve_registry(owner, registry_attr)
            resolved_window_key = _resolve_key(window_key, args, kwargs, fallback='')
            resolved_scope_key = _resolve_key(scope_key, args, kwargs, fallback=fallback_scope_key)
            resolved_signature = _resolve_value(signature, args, kwargs)
            resolved_window_signature = _resolve_value(window_signature, args, kwargs)

            def calculator(layout_state: LayoutCalculationState) -> T:
                call_kwargs: dict[str, Any] = dict(kwargs)
                if accepts_layout_state and 'layout_state' not in call_kwargs:
                    call_kwargs['layout_state'] = layout_state
                if accepts_layout_storage and 'layout_storage' not in call_kwargs:
                    call_kwargs['layout_storage'] = layout_state.storage
                return func(*args, **call_kwargs)

            return registry.recalculate(
                resolved_window_key,
                resolved_scope_key,
                calculator,
                signature=resolved_signature,
                window_signature=resolved_window_signature,
            )

        return wrapper

    return decorator


class MockLayoutWindow:
    WINDOW_ID = 'layout_recalculation_demo'

    def __init__(self):
        self._layout_recalculation_registry = LayoutRecalculationRegistry()
        self.visible = True
        self.search_text = ''
        self.category_labels = ['All', 'Weapons', 'Materials', 'Consumables', 'Collector']
        self.sort_labels = ['Score', 'Name', 'Category']
        self.selected_category_index = 0
        self.selected_sort_index = 0
        self.minimum_score = 120
        self.max_rows = 80
        self.compact_mode = False
        self.only_even_stacks = False
        self.dataset_version = 0
        self.recalculation_runs = 0
        self.summary_recalculation_runs = 0
        self.selected_entry_key = ''
        self.current_window_size = (520.0, 640.0)
        self.current_content_width = 480.0
        self.current_table_height = 320.0
        self.items = self._build_mock_items()

    def _build_mock_items(self) -> list[dict[str, Any]]:
        categories = self.category_labels[1:]
        rarities = ['Common', 'Uncommon', 'Rare', 'Exotic']
        items: list[dict[str, Any]] = []
        for index in range(240):
            category = categories[index % len(categories)]
            rarity = rarities[index % len(rarities)]
            tier = 1 + (index % 5)
            stack = ((index * 7) % 250) + 1
            items.append(
                {
                    'key': f'{category.lower()}_{index}',
                    'name': f'{category[:-1] if category.endswith("s") else category} Cache {index:03d}',
                    'category': category,
                    'rarity': rarity,
                    'tier': tier,
                    'stack': stack,
                    'base_value': 45 + ((index * 13) % 180),
                    'power': 20 + ((index * 11) % 90),
                    'weight': 5 + ((index * 17) % 70),
                }
            )
        return items

    def _mutate_mock_items(self) -> None:
        self.dataset_version += 1
        for index, item in enumerate(self.items):
            item['base_value'] = 35 + ((index * 13 + self.dataset_version * 19) % 210)
            item['power'] = 15 + ((index * 11 + self.dataset_version * 23) % 110)
            item['stack'] = ((index * 7 + self.dataset_version * 5) % 250) + 1

    def _refresh_layout_metrics(self) -> None:
        window_width, window_height = PyImGui.get_window_size()
        self.current_window_size = (float(window_width), float(window_height))

        # Use stable geometry derived from the actual window size rather than
        # the constantly shifting "remaining content" cursor state.
        self.current_content_width = max(240.0, float(window_width) - 48.0)
        self.current_table_height = max(180.0, float(window_height) - 360.0)

    def _window_layout_signature(self, *_args: Any, **_kwargs: Any) -> tuple[int, int, int, int]:
        return (
            int(self.current_window_size[0] // 20),
            int(self.current_window_size[1] // 20),
            int(self.current_content_width // 25),
            int(self.current_table_height // 20),
        )

    @recalculate_layout(
        window_key=lambda self, *_args, **_kwargs: self.WINDOW_ID,
        scope_key='heavy_rows',
        signature=lambda self, *_args, **_kwargs: (
            self.search_text.strip().lower(),
            self.selected_category_index,
            self.selected_sort_index,
            self.minimum_score,
            self.max_rows,
            self.compact_mode,
            self.only_even_stacks,
            self.dataset_version,
            self.selected_entry_key,
        ),
        window_signature=lambda self, *_args, **_kwargs: self._window_layout_signature(),
    )
    def _build_visible_rows(
        self,
        *,
        layout_storage: dict[str, Any],
        layout_state: LayoutCalculationState,
    ) -> list[dict[str, Any]]:
        self.recalculation_runs += 1
        normalized_search = self.search_text.strip().lower()
        selected_category = self.category_labels[self.selected_category_index]
        content_width = max(180.0, self.current_content_width - 130.0)
        rows: list[dict[str, Any]] = []

        layout_storage['last_selected_entry_key'] = self.selected_entry_key
        layout_storage['build_reason'] = {
            'dirty': layout_state.dirty,
            'window_version': layout_state.window_version,
        }

        for item in self.items:
            if selected_category != 'All' and item['category'] != selected_category:
                continue

            if self.only_even_stacks and item['stack'] % 2 != 0:
                continue

            haystack = f"{item['name']} {item['category']} {item['rarity']}".lower()
            if normalized_search and normalized_search not in haystack:
                continue

            computed_score = 0.0
            for factor in range(1, 14):
                signal = math.sqrt(item['power'] * factor + item['tier'] * 19 + self.dataset_version)
                score_boost = (item['base_value'] / max(1, factor)) + (item['stack'] % (factor + 3))
                computed_score += signal * 4.5 + score_boost

            computed_score -= item['weight'] * 1.35
            computed_score += item['tier'] * 12

            score = int(computed_score)
            if score < self.minimum_score:
                continue

            details = (
                f"{item['rarity']} | Tier {item['tier']} | Stack {item['stack']} | "
                f"Base {item['base_value']} | Weight {item['weight']} | Score {score}"
            )
            details_width = PyImGui.calc_text_size(details)[0]
            wrapped_lines = max(1, int(math.ceil(details_width / content_width)))
            row_height = 24 if self.compact_mode else max(28, 20 + wrapped_lines * 16)

            rows.append(
                {
                    'key': item['key'],
                    'name': item['name'],
                    'category': item['category'],
                    'rarity': item['rarity'],
                    'stack': item['stack'],
                    'score': score,
                    'details': details,
                    'details_width': details_width,
                    'row_height': row_height,
                    'selected': item['key'] == self.selected_entry_key,
                }
            )

        if self.selected_sort_index == 0:
            rows.sort(key=lambda row: (-int(row['score']), str(row['name'])))
        elif self.selected_sort_index == 1:
            rows.sort(key=lambda row: (str(row['name']), -int(row['score'])))
        else:
            rows.sort(key=lambda row: (str(row['category']), -int(row['score']), str(row['name'])))

        limited_rows = rows[:self.max_rows]
        layout_storage['row_count'] = len(limited_rows)
        layout_storage['peak_score'] = max((int(row['score']) for row in limited_rows), default=0)
        return limited_rows

    @recalculate_layout(
        window_key=lambda self, *_args, **_kwargs: self.WINDOW_ID,
        scope_key='summary_cards',
        signature=lambda self, rows: (
            tuple((str(row['category']), int(row['score'])) for row in rows[:24]),
            len(rows),
            self.selected_entry_key,
        ),
        window_signature=lambda self, *_args, **_kwargs: self._window_layout_signature(),
    )
    def _build_summary_cards(
        self,
        rows: list[dict[str, Any]],
        *,
        layout_storage: dict[str, Any],
        layout_state: LayoutCalculationState,
    ) -> list[dict[str, Any]]:
        self.summary_recalculation_runs += 1
        buckets: dict[str, dict[str, Any]] = {}
        for row in rows:
            bucket = buckets.setdefault(
                str(row['category']),
                {
                    'category': row['category'],
                    'count': 0,
                    'total_score': 0,
                    'top_name': row['name'],
                    'top_score': row['score'],
                },
            )
            bucket['count'] += 1
            bucket['total_score'] += int(row['score'])
            if int(row['score']) > int(bucket['top_score']):
                bucket['top_score'] = int(row['score'])
                bucket['top_name'] = row['name']

        cards: list[dict[str, Any]] = []
        for bucket in buckets.values():
            average_score = int(bucket['total_score'] / max(1, bucket['count']))
            preview_text = f"Top: {bucket['top_name']} ({bucket['top_score']})"
            preview_width = PyImGui.calc_text_size(preview_text)[0]
            cards.append(
                {
                    'title': f"{bucket['category']} x{bucket['count']}",
                    'average_score': average_score,
                    'preview': preview_text,
                    'preview_width': preview_width,
                }
            )

        cards.sort(key=lambda card: (-int(card['average_score']), str(card['title'])))
        layout_storage['dirty'] = layout_state.dirty
        layout_storage['card_count'] = len(cards)
        return cards[:3]

    def _draw_toolbar(self) -> None:
        self.search_text = ImGui.input_text('Search', self.search_text, 0)
        self.selected_category_index = ImGui.combo('Category', self.selected_category_index, self.category_labels)
        self.selected_sort_index = ImGui.combo('Sort', self.selected_sort_index, self.sort_labels)
        self.minimum_score = ImGui.slider_int('Minimum Score', self.minimum_score, 50, 1800)
        self.max_rows = ImGui.slider_int('Max Rows', self.max_rows, 10, 150)
        self.compact_mode = ImGui.checkbox('Compact Rows', self.compact_mode)
        self.only_even_stacks = ImGui.checkbox('Even Stacks Only', self.only_even_stacks)

        if ImGui.button('Invalidate Row Cache', 170, 0):
            invalidate_layout(self.WINDOW_ID, 'heavy_rows', registry=self._layout_recalculation_registry)

        PyImGui.same_line(0, 6)
        if ImGui.button('Invalidate Whole Window', 190, 0):
            invalidate_layout(self.WINDOW_ID, registry=self._layout_recalculation_registry)

        PyImGui.same_line(0, 6)
        if ImGui.button('Mutate Dataset', 140, 0):
            self._mutate_mock_items()

    def _draw_summary_cards(self, cards: list[dict[str, Any]]) -> None:
        if not cards:
            ImGui.text_wrapped('No summary cards available for the current filters.')
            return

        if ImGui.begin_table('##layout_summary_cards', len(cards), PyImGui.TableFlags.SizingStretchProp):
            for card in cards:
                PyImGui.table_next_column()
                ImGui.text(str(card['title']))
                ImGui.text_colored(f"Avg Score: {card['average_score']}", (220, 220, 180, 255), font_size=12)
                ImGui.text_wrapped(str(card['preview']))
            ImGui.end_table()

    def _draw_rows_table(self, rows: list[dict[str, Any]]) -> None:
        flags = (
            PyImGui.TableFlags.Borders
            | PyImGui.TableFlags.RowBg
            | PyImGui.TableFlags.Resizable
            | PyImGui.TableFlags.ScrollY
            | PyImGui.TableFlags.SizingStretchProp
        )

        if ImGui.begin_table('##layout_heavy_rows', 5, flags, height=self.current_table_height):
            PyImGui.table_setup_column('Item', PyImGui.TableColumnFlags.WidthStretch, 180)
            PyImGui.table_setup_column('Category', PyImGui.TableColumnFlags.WidthFixed, 110)
            PyImGui.table_setup_column('Rarity', PyImGui.TableColumnFlags.WidthFixed, 90)
            PyImGui.table_setup_column('Stack', PyImGui.TableColumnFlags.WidthFixed, 55)
            PyImGui.table_setup_column('Score', PyImGui.TableColumnFlags.WidthFixed, 70)
            PyImGui.table_headers_row()

            for row in rows:
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                label = f"{row['name']}##{row['key']}"
                if ImGui.selectable(label, bool(row['selected'])):
                    self.selected_entry_key = str(row['key'])

                if PyImGui.is_item_hovered():
                    ImGui.begin_tooltip()
                    ImGui.text(str(row['name']), font_size=16)
                    ImGui.separator()
                    ImGui.text_wrapped(str(row['details']))
                    ImGui.end_tooltip()

                PyImGui.table_next_column()
                ImGui.text(str(row['category']))
                PyImGui.table_next_column()
                ImGui.text(str(row['rarity']))
                PyImGui.table_next_column()
                ImGui.text(str(row['stack']))
                PyImGui.table_next_column()
                ImGui.text(str(row['score']))

            ImGui.end_table()

    def draw(self) -> None:
        if not self.visible:
            return

        PyImGui.set_next_window_size((920, 720), PyImGui.ImGuiCond.FirstUseEver)
        if PyImGui.begin('Layout Recalculation Demo'):
            self._refresh_layout_metrics()
            self._draw_toolbar()

            ImGui.separator()
            ImGui.text_wrapped(
                'This mock window intentionally does expensive per-row scoring, text measuring, and '
                'summary aggregation. The decorator only recalculates when filters, data, or the '
                'effective window layout signature changes.'
            )
            ImGui.separator()

            rows = self._build_visible_rows()
            cards = self._build_summary_cards(rows)
            row_storage = get_layout_storage(self.WINDOW_ID, 'heavy_rows', registry=self._layout_recalculation_registry)
            summary_storage = get_layout_storage(self.WINDOW_ID, 'summary_cards', registry=self._layout_recalculation_registry)

            ImGui.text(
                f'Row recalculations: {self.recalculation_runs} | '
                f'Summary recalculations: {self.summary_recalculation_runs} | '
                f'Visible rows: {len(rows)}'
            )
            ImGui.text(
                f"Last peak score: {row_storage.get('peak_score', 0)} | "
                f"Summary cards: {summary_storage.get('card_count', 0)}"
            )

            ImGui.separator()
            self._draw_summary_cards(cards)
            ImGui.separator()
            self._draw_rows_table(rows)

        PyImGui.end()


WINDOW = MockLayoutWindow()


def main():
    WINDOW.draw()


if __name__ == '__main__':
    main()
