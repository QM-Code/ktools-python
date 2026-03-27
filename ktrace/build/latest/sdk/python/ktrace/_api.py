from __future__ import annotations

import inspect
import threading
import time

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._format import COLOR_NAMES
from ._format import format_message
from ._format import normalize_color_or_throw
from ._selectors import SelectorPattern
from ._selectors import matches_selector
from ._selectors import normalize_channel_or_throw
from ._selectors import normalize_namespace_or_throw
from ._selectors import parse_selector_or_throw
from ._selectors import split_csv_preserving_braces


@dataclass
class OutputOptions:
    filenames: bool = False
    line_numbers: bool = False
    function_names: bool = False
    timestamps: bool = False


@dataclass(frozen=True)
class _Location:
    filename: str
    line: int
    function: str


def Color(color_name: str) -> str:
    return normalize_color_or_throw(color_name)


def _caller_location(skip: int = 2) -> _Location:
    frame = inspect.currentframe()
    try:
        for _ in range(skip):
            if frame is None or frame.f_back is None:
                break
            frame = frame.f_back
        if frame is None:
            return _Location("unknown", 0, "unknown")
        info = inspect.getframeinfo(frame)
        return _Location(Path(info.filename).stem, info.lineno, info.function)
    finally:
        del frame


class TraceLogger:
    def __init__(self, trace_namespace: str) -> None:
        self._namespace = normalize_namespace_or_throw(trace_namespace)
        self._channels: dict[str, str] = {}
        self._attached_logger: Logger | None = None
        self._changed_lock = threading.Lock()
        self._changed_keys: dict[tuple[str, str, int, str], str] = {}

    def addChannel(self, channel: str, color: str = "Default") -> None:
        channel_name = normalize_channel_or_throw(channel)
        self._channels[channel_name] = normalize_color_or_throw(color)

    def getNamespace(self) -> str:
        return self._namespace

    def shouldTraceChannel(self, channel: str) -> bool:
        if self._attached_logger is None:
            return False
        try:
            qualified_channel = f".{normalize_channel_or_throw(channel)}"
        except ValueError:
            return False
        return self._attached_logger.shouldTraceChannel(self, qualified_channel)

    def trace(self, channel: str, format_text: str, *args: object) -> None:
        if self._attached_logger is None:
            return
        channel_name = normalize_channel_or_throw(channel)
        self._attached_logger._emit_trace(  # noqa: SLF001
            self._namespace,
            channel_name,
            format_message(format_text, *args),
            _caller_location(),
        )

    def traceChanged(self, channel: str, key_expr: object, format_text: str, *args: object) -> None:
        if self._attached_logger is None:
            return
        channel_name = normalize_channel_or_throw(channel)
        location = _caller_location()
        site_key = (self._namespace, channel_name, location.line, location.function)
        key = str(key_expr)
        with self._changed_lock:
            previous = self._changed_keys.get(site_key)
            if previous == key:
                return
            self._changed_keys[site_key] = key

        self._attached_logger._emit_trace(  # noqa: SLF001
            self._namespace,
            channel_name,
            format_message(format_text, *args),
            location,
        )

    def info(self, format_text: str, *args: object) -> None:
        if self._attached_logger is None:
            return
        self._attached_logger._emit_log(  # noqa: SLF001
            self._namespace,
            "info",
            format_message(format_text, *args),
            _caller_location(),
        )

    def warn(self, format_text: str, *args: object) -> None:
        if self._attached_logger is None:
            return
        self._attached_logger._emit_log(  # noqa: SLF001
            self._namespace,
            "warning",
            format_message(format_text, *args),
            _caller_location(),
        )

    def error(self, format_text: str, *args: object) -> None:
        if self._attached_logger is None:
            return
        self._attached_logger._emit_log(  # noqa: SLF001
            self._namespace,
            "error",
            format_message(format_text, *args),
            _caller_location(),
        )


class Logger:
    def __init__(self) -> None:
        self._output_options = OutputOptions()
        self._registered_channels: dict[str, dict[str, str]] = {}
        self._enabled_channels: set[str] = set()
        self._attached_loggers: list[TraceLogger] = []
        self._output_lock = threading.Lock()

    def addTraceLogger(self, logger: TraceLogger) -> None:
        if logger._attached_logger is not None and logger._attached_logger is not self:  # noqa: SLF001
            raise ValueError("trace logger is already attached to another logger")

        logger._attached_logger = self  # noqa: SLF001
        self._attached_loggers.append(logger)
        channels = self._registered_channels.setdefault(logger.getNamespace(), {})
        for channel_name, color in logger._channels.items():  # noqa: SLF001
            existing = channels.get(channel_name)
            if existing is None or existing == color or color == "Default":
                channels[channel_name] = existing or color
                continue
            if existing == "Default":
                channels[channel_name] = color
                continue
            raise ValueError(
                "conflicting explicit channel colors for "
                f"'{logger.getNamespace()}.{channel_name}': '{existing}' vs '{color}'"
            )

    def enableChannel(self, channel_or_logger: str | TraceLogger, qualified_channel: str | None = None) -> None:
        if isinstance(channel_or_logger, TraceLogger):
            if qualified_channel is None:
                raise ValueError("trace channel must not be empty")
            self.enableChannels(qualified_channel, channel_or_logger.getNamespace())
            return
        self.enableChannels(channel_or_logger)

    def enableChannels(self, selectors_csv: str, local_namespace: str = "") -> None:
        self._apply_selectors(selectors_csv, local_namespace, enable=True)

    def shouldTraceChannel(self, channel_or_logger: str | TraceLogger, qualified_channel: str | None = None) -> bool:
        if isinstance(channel_or_logger, TraceLogger):
            if qualified_channel is None:
                return False
            try:
                qualified = self._resolve_channel_reference(qualified_channel, channel_or_logger.getNamespace())
            except ValueError:
                return False
            return qualified in self._enabled_channels

        try:
            qualified = self._resolve_channel_reference(channel_or_logger, "")
        except ValueError:
            return False
        return qualified in self._enabled_channels

    def disableChannel(self, channel_or_logger: str | TraceLogger, qualified_channel: str | None = None) -> None:
        if isinstance(channel_or_logger, TraceLogger):
            if qualified_channel is None:
                raise ValueError("trace channel must not be empty")
            self.disableChannels(qualified_channel, channel_or_logger.getNamespace())
            return
        self.disableChannels(channel_or_logger)

    def disableChannels(self, selectors_csv: str, local_namespace: str = "") -> None:
        self._apply_selectors(selectors_csv, local_namespace, enable=False)

    def setOutputOptions(self, options: OutputOptions) -> None:
        self._output_options = OutputOptions(
            filenames=bool(options.filenames),
            line_numbers=bool(options.line_numbers),
            function_names=bool(options.function_names),
            timestamps=bool(options.timestamps),
        )

    def getOutputOptions(self) -> OutputOptions:
        return OutputOptions(
            filenames=self._output_options.filenames,
            line_numbers=self._output_options.line_numbers,
            function_names=self._output_options.function_names,
            timestamps=self._output_options.timestamps,
        )

    def getNamespaces(self) -> list[str]:
        return sorted(self._registered_channels)

    def getChannels(self, trace_namespace: str) -> list[str]:
        namespace = normalize_namespace_or_throw(trace_namespace)
        return sorted(self._registered_channels.get(namespace, {}))

    def makeInlineParser(self, local_trace_logger: TraceLogger, trace_root: str = "trace") -> Any:
        import kcli

        local_namespace = local_trace_logger.getNamespace()

        def on_root(context: Any, value: str) -> None:
            self.enableChannels(value, local_namespace)

        def on_examples(context: Any) -> None:
            option_root = f"--{context.root}"
            print("")
            print("General trace selector pattern:")
            print(f"  {option_root} <namespace>.<channel>[.<subchannel>[.<subchannel>]]")
            print("")
            print("Trace selector examples:")
            print(f"  {option_root} '.abc'")
            print(f"  {option_root} '.abc.xyz'")
            print(f"  {option_root} 'otherapp.channel'")
            print(f"  {option_root} '*.*'")
            print(f"  {option_root} '*.*.*'")
            print(f"  {option_root} '*.*.*.*'")
            print(f"  {option_root} '*.{ '{net,io}' }'")
            print("")

        def on_namespaces(context: Any) -> None:
            namespaces = self.getNamespaces()
            if not namespaces:
                print("No trace namespaces defined.\n")
                return
            print("\nAvailable trace namespaces:")
            for trace_namespace in namespaces:
                print(f"  {trace_namespace}")
            print("")

        def on_channels(context: Any) -> None:
            printed_any = False
            for trace_namespace in self.getNamespaces():
                for channel in self.getChannels(trace_namespace):
                    if not printed_any:
                        print("\nAvailable trace channels:")
                        printed_any = True
                    print(f"  {trace_namespace}.{channel}")
            if not printed_any:
                print("No trace channels defined.\n")
                return
            print("")

        def on_colors(context: Any) -> None:
            print("\nAvailable trace colors:")
            for color_name in COLOR_NAMES:
                print(f"  {color_name}")
            print("")

        def on_files(context: Any) -> None:
            options = self.getOutputOptions()
            options.filenames = True
            options.line_numbers = True
            self.setOutputOptions(options)

        def on_functions(context: Any) -> None:
            options = self.getOutputOptions()
            options.filenames = True
            options.line_numbers = True
            options.function_names = True
            self.setOutputOptions(options)

        def on_timestamps(context: Any) -> None:
            options = self.getOutputOptions()
            options.timestamps = True
            self.setOutputOptions(options)

        parser = kcli.InlineParser(trace_root)
        parser.setRootValueHandler(on_root, "<channels>", "Trace selected channels.")
        parser.setHandler("-examples", on_examples, "Show selector examples.")
        parser.setHandler("-namespaces", on_namespaces, "Show initialized trace namespaces.")
        parser.setHandler("-channels", on_channels, "Show initialized trace channels.")
        parser.setHandler("-colors", on_colors, "Show available trace colors.")
        parser.setHandler("-files", on_files, "Include source file and line in trace output.")
        parser.setHandler("-functions", on_functions, "Include function names in trace output.")
        parser.setHandler("-timestamps", on_timestamps, "Include timestamps in trace output.")
        return parser

    def _apply_selectors(self, selectors_csv: str, local_namespace: str, *, enable: bool) -> None:
        selector_text = str(selectors_csv).strip()
        if not selector_text:
            raise RuntimeError("trace selector list must not be empty")

        raw_selectors = split_csv_preserving_braces(selector_text)
        patterns = [parse_selector_or_throw(raw_selector, local_namespace) for raw_selector in raw_selectors]

        for pattern in patterns:
            matches = self._matching_channels(pattern)
            if matches:
                if enable:
                    self._enabled_channels.update(matches)
                else:
                    self._enabled_channels.difference_update(matches)
                continue

            action = "enable" if enable else "disable"
            namespace = local_namespace or "ktrace"
            self._emit_log(
                namespace,
                "warning",
                f"{action} ignored channel selector '{pattern.text}' because it matched no registered channels",
                None,
            )

    def _matching_channels(self, pattern: SelectorPattern) -> list[str]:
        matches: list[str] = []
        for trace_namespace in sorted(self._registered_channels):
            for channel in sorted(self._registered_channels[trace_namespace]):
                qualified = f"{trace_namespace}.{channel}"
                if matches_selector(pattern, qualified):
                    matches.append(qualified)
        return matches

    def _resolve_channel_reference(self, reference: str, local_namespace: str) -> str:
        token = str(reference).strip()
        if not token:
            raise ValueError("trace channel must not be empty")
        if token.startswith("."):
            namespace = normalize_namespace_or_throw(local_namespace)
            qualified = f"{namespace}{token}"
        elif "." in token:
            qualified = token
        elif local_namespace:
            qualified = f"{normalize_namespace_or_throw(local_namespace)}.{token}"
        else:
            raise ValueError(f"invalid trace channel '{token}'")

        namespace, _, channel = qualified.partition(".")
        normalize_namespace_or_throw(namespace)
        normalize_channel_or_throw(channel)
        return qualified

    def _emit_trace(self, trace_namespace: str, channel: str, message: str, location: _Location | None) -> None:
        qualified = f"{trace_namespace}.{channel}"
        if qualified not in self._enabled_channels:
            return
        prefix = self._build_prefix(trace_namespace, channel, location)
        self._write_line(prefix, message)

    def _emit_log(
        self,
        trace_namespace: str,
        severity: str,
        message: str,
        location: _Location | None,
    ) -> None:
        prefix = self._build_prefix(trace_namespace, severity, location)
        self._write_line(prefix, message)

    def _build_prefix(self, trace_namespace: str, label: str, location: _Location | None) -> str:
        parts = [f"[{trace_namespace}]"]
        if self._output_options.timestamps:
            parts.append(f"[{time.time():.6f}]")
        parts.append(f"[{label}]")
        if location is not None and self._output_options.filenames:
            if self._output_options.function_names:
                parts.append(f"[{location.filename}:{location.line}:{location.function}]")
            elif self._output_options.line_numbers:
                parts.append(f"[{location.filename}:{location.line}]")
            else:
                parts.append(f"[{location.filename}]")
        return " ".join(parts)

    def _write_line(self, prefix: str, message: str) -> None:
        with self._output_lock:
            print(f"{prefix} {message}", flush=True)
