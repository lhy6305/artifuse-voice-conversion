from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
from typing import Any
import wave

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import winsound
except ImportError:  # pragma: no cover
    winsound = None


TIE_LABEL = "打平"
FULL_AUDIO_SEGMENT_LABEL = "整段"
AUTO_SEGMENT_MIN_SECONDS = 8.0
SEGMENT_LENGTH_SECONDS = 4.0
SEGMENT_OVERLAP_SECONDS = 0.5


@dataclass(frozen=True)
class ReviewModeConfig:
    review_mode: str
    scoring_fields: tuple[tuple[str, str], ...]
    validity_options: tuple[tuple[str, str], ...]
    validity_field_label: str
    scoring_option_mode: str
    fixed_field_options: dict[str, tuple[str, ...]]
    blank_completed_label: str | None
    tie_policy: str
    help_text: str


COMPARATIVE_SCORING_FIELDS = (
    ("best_rhythm", "节奏最好"),
    ("best_boundary", "边界最好"),
    ("most_stable", "最稳定"),
    ("overall_pick", "综合首选"),
)

COMPARATIVE_REVIEW_MODE_CONFIG = ReviewModeConfig(
    review_mode="comparative",
    scoring_fields=COMPARATIVE_SCORING_FIELDS,
    validity_options=(
        ("yes", "可比较"),
        ("partial", "部分可比较"),
        ("no", "不建议比较"),
    ),
    validity_field_label="是否适合比较",
    scoring_option_mode="candidate_labels",
    fixed_field_options={},
    blank_completed_label=TIE_LABEL,
    tie_policy="已完成且可比较的记录中，留空评分字段按“打平”解释。",
    help_text="""\
判断词：

节奏最好：
- 停连自然
- 速度顺

边界最好：
- 断句清楚
- 句尾收住

最稳定：
- 不乱跳
- 不忽大忽小
- 不持续冒噪声

综合首选：
- 如果只留一个，就选它
- 留空视为打平

是否适合比较：
- 可比较：差异清楚，可判
- 部分可比较：能听，但受伪影影响
- 不建议比较：整体失真重，不强判

当前优先看：
- 静音控制
- 边界收束
- 能量起伏
- 持续噪声
- 刺耳感

当前先不看：
- 最终音色
- 绝对音高
- 高频质感

当前默认播放的是 bundle 里的 listening_audio_path：
- 具体可能是 decoded / decoded_pitch_matched / audit_proxy
- 以当前试听包清单为准
""",
)

MILESTONE_ACCEPTANCE_REVIEW_MODE_CONFIG = ReviewModeConfig(
    review_mode="milestone_acceptance",
    scoring_fields=(
        ("intelligibility", "可懂性"),
        ("stability", "稳定性"),
        ("basic_naturalness", "基本自然度"),
        ("milestone_verdict", "阶段结论"),
    ),
    validity_options=(
        ("yes", "可判"),
        ("partial", "部分可判"),
        ("no", "暂不判"),
    ),
    validity_field_label="是否适合判定",
    scoring_option_mode="fixed_options",
    fixed_field_options={
        "intelligibility": ("", "可懂", "部分可懂", "不可懂"),
        "stability": ("", "稳定", "轻微问题", "不稳定"),
        "basic_naturalness": ("", "基本自然", "偏技术信号", "明显不自然"),
        "milestone_verdict": ("", "通过", "边缘", "未通过"),
    },
    blank_completed_label=None,
    tie_policy="本模式不自动把留空解释为打平；门槛验收字段应显式填写。",
    help_text="""\
判断词：

可懂性：
- 可懂：主体内容大体能听清
- 部分可懂：能听出大意，但经常糊
- 不可懂：长期难辨识

稳定性：
- 稳定：没有明显持续破音、乱跳或 buzzing
- 轻微问题：偶发异常，但整体还能接受
- 不稳定：异常频繁，影响整体判断

基本自然度：
- 基本自然：虽然还不是最终成品，但已像正常语音
- 偏技术信号：还能听，但人工合成/技术信号感明显
- 明显不自然：长期不像正常语音

阶段结论：
- 通过：当前 no-res route 已达到本阶段门槛
- 边缘：接近门槛，但还不够稳
- 未通过：当前还不能算过门槛

是否适合判定：
- 可判：足以给出门槛判断
- 部分可判：能判断，但伪影会干扰
- 暂不判：当前样本失真过重，不强判

当前优先看：
- 可懂性
- 稳定性
- 基本自然度
- 持续 buzzing / 破音 / 句内乱跳

当前先不看：
- 最终音色是否完美
- MRSTFT / adversarial 成品级质感
- 与用户线 source-to-target 的真实闭环体验

当前默认播放的是 bundle 里的 listening_audio_path：
- milestone acceptance 当前应以 decoded 为主听
- aligned_target 只是 bootstrap objective 的对齐参考
""",
)

REVIEW_MODE_CONFIGS = {
    COMPARATIVE_REVIEW_MODE_CONFIG.review_mode: COMPARATIVE_REVIEW_MODE_CONFIG,
    MILESTONE_ACCEPTANCE_REVIEW_MODE_CONFIG.review_mode: MILESTONE_ACCEPTANCE_REVIEW_MODE_CONFIG,
}


def get_review_mode_config(review_mode: str) -> ReviewModeConfig:
    normalized = str(review_mode).strip().lower()
    if normalized not in REVIEW_MODE_CONFIGS:
        raise ValueError(f"Unsupported review mode: {review_mode}")
    return REVIEW_MODE_CONFIGS[normalized]


@dataclass
class CandidateTrack:
    label: str
    path: Path
    source_manifest: Path


@dataclass
class AuditRecord:
    record_id: str
    input_audio_path: Path | None = None
    audio_path: Path | None = None
    sample_rate: int | None = None
    candidates: list[CandidateTrack] = field(default_factory=list)
    source_manifests: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class ListeningSegment:
    label: str
    start_frame: int | None
    end_frame: int | None
    start_sec: float
    end_sec: float

    @property
    def is_full_audio(self) -> bool:
        return self.start_frame is None or self.end_frame is None


class AudioAuditApp:
    def __init__(
        self,
        root: tk.Tk,
        manifest_paths: list[Path],
        output_dir: Path,
        review_mode: str,
    ) -> None:
        self.review_mode_config = get_review_mode_config(review_mode)
        self.root = root
        self.output_dir = output_dir.resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.export_json_path = self.output_dir / "audio_audit_review.json"
        self.export_md_path = self.output_dir / "audio_audit_review.md"
        self.progress_json_path = self.output_dir / "audio_audit_progress.json"
        self.segment_cache_dir = self.output_dir / "_segment_cache"
        self.segment_cache_dir.mkdir(parents=True, exist_ok=True)
        self.playback_cache_dir = self.output_dir / "_playback_cache"
        self.playback_cache_dir.mkdir(parents=True, exist_ok=True)

        self.records_by_id: dict[str, AuditRecord] = {}
        self.record_order: list[str] = []
        self.filtered_record_ids: list[str] = []
        self.loaded_manifest_paths: list[Path] = []
        self.review_state: dict[str, dict[str, Any]] = {}
        self.current_index = 0

        self.root.title("音频听审工具")
        self.root.geometry("1280x940")
        self.root.minsize(1120, 820)

        self.record_listbox: tk.Listbox | None = None
        self.record_filter_var = tk.StringVar()
        self.summary_var = tk.StringVar(value="尚未加载试听包。")
        self.status_var = tk.StringVar(value="就绪。")
        self.current_record_var = tk.StringVar(value="")
        self.input_path_var = tk.StringVar(value="")
        self.audio_path_var = tk.StringVar(value="")
        self.segment_var = tk.StringVar(value=FULL_AUDIO_SEGMENT_LABEL)
        self.segment_summary_var = tk.StringVar(value="当前播放整段。")
        self.session_notes_text: tk.Text | None = None
        self.notes_text: tk.Text | None = None
        self.segment_combo: ttk.Combobox | None = None
        self.right_canvas: tk.Canvas | None = None
        self.right_canvas_window_id: int | None = None
        self.valid_var = tk.StringVar(value=self.review_mode_config.validity_options[0][1])
        self.completed_var = tk.BooleanVar(value=False)
        self.field_vars: dict[str, tk.StringVar] = {
            field_id: tk.StringVar(value="") for field_id, _ in self.review_mode_config.scoring_fields
        }
        self.score_widgets: dict[str, ttk.Combobox] = {}
        self.candidate_frames: list[ttk.Frame] = []
        self.current_segments: list[ListeningSegment] = [ListeningSegment(FULL_AUDIO_SEGMENT_LABEL, None, None, 0.0, 0.0)]

        self.build_layout()
        self.bind_shortcuts()
        if manifest_paths:
            self.load_manifests(manifest_paths)
        else:
            self.try_restore_manifests_from_progress()
        self.try_restore_progress()
        self.refresh_record_list()
        self.refresh_current_record()

    def build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_pane = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main_pane.grid(row=0, column=0, sticky="nsew")

        left = ttk.Frame(main_pane, padding=10, width=420)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(4, weight=1)
        main_pane.add(left, weight=1)

        ttk.Label(left, text="试听包").grid(row=0, column=0, sticky="w")
        bundle_controls = ttk.Frame(left)
        bundle_controls.grid(row=1, column=0, sticky="ew", pady=(6, 10))
        ttk.Button(bundle_controls, text="添加试听包", command=self.open_bundle_dialog).grid(row=0, column=0, sticky="ew")
        ttk.Button(bundle_controls, text="重新载入", command=self.reload_loaded_manifests).grid(row=1, column=0, sticky="ew", pady=(6, 0))

        ttk.Label(left, text="筛选").grid(row=2, column=0, sticky="w")
        filter_entry = ttk.Entry(left, textvariable=self.record_filter_var, width=40)
        filter_entry.grid(row=3, column=0, sticky="new", pady=(6, 6))
        filter_entry.bind("<KeyRelease>", self.on_filter_changed)

        list_frame = ttk.Frame(left)
        list_frame.grid(row=4, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.record_listbox = tk.Listbox(list_frame, width=46, height=36, exportselection=False)
        self.record_listbox.grid(row=0, column=0, sticky="nsew")
        record_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.record_listbox.yview)
        record_scrollbar.grid(row=0, column=1, sticky="ns")
        self.record_listbox.configure(yscrollcommand=record_scrollbar.set)
        self.record_listbox.bind("<<ListboxSelect>>", self.on_record_selected)
        self.record_listbox.bind("<Up>", lambda _event: "break")
        self.record_listbox.bind("<Down>", lambda _event: "break")
        self.record_listbox.bind("<Left>", lambda _event: "break")
        self.record_listbox.bind("<Right>", lambda _event: "break")

        left_actions = ttk.Frame(left)
        left_actions.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(left_actions, text="上一条", command=self.go_prev).grid(row=0, column=0, sticky="ew")
        ttk.Button(left_actions, text="下一条", command=self.go_next).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ttk.Button(left_actions, text="保存进度", command=self.save_progress).grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(left_actions, text="导出结果", command=self.export_review).grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(left, textvariable=self.summary_var, wraplength=300, justify="left").grid(
            row=6, column=0, sticky="ew", pady=(10, 0)
        )

        right_container = ttk.Frame(main_pane, padding=10)
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(0, weight=1)
        main_pane.add(right_container, weight=3)

        self.right_canvas = tk.Canvas(right_container, highlightthickness=0)
        self.right_canvas.grid(row=0, column=0, sticky="nsew")
        right_scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=self.right_canvas.yview)
        right_scrollbar.grid(row=0, column=1, sticky="ns")
        self.right_canvas.configure(yscrollcommand=right_scrollbar.set)

        right = ttk.Frame(self.right_canvas)
        self.right_canvas_window_id = self.right_canvas.create_window((0, 0), window=right, anchor="nw")
        right.bind("<Configure>", self.on_right_frame_configured)
        self.right_canvas.bind("<Configure>", self.on_right_canvas_configured)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(4, weight=1)
        right.rowconfigure(5, weight=1)
        right.rowconfigure(6, weight=1)

        header = ttk.Label(right, textvariable=self.current_record_var, font=("TkDefaultFont", 12, "bold"))
        header.grid(row=0, column=0, sticky="w")

        meta_frame = ttk.Frame(right)
        meta_frame.grid(row=1, column=0, sticky="ew", pady=(8, 8))
        meta_frame.columnconfigure(1, weight=1)
        ttk.Label(meta_frame, text="试听输入").grid(row=0, column=0, sticky="nw")
        ttk.Entry(meta_frame, textvariable=self.input_path_var, state="readonly").grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ttk.Label(meta_frame, text="原始样本").grid(row=1, column=0, sticky="nw", pady=(6, 0))
        ttk.Entry(meta_frame, textvariable=self.audio_path_var, state="readonly").grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))

        playback_frame = ttk.LabelFrame(right, text="播放", padding=10)
        playback_frame.grid(row=2, column=0, sticky="ew")
        playback_frame.columnconfigure(1, weight=1)
        playback_frame.columnconfigure(2, weight=0)
        playback_frame.columnconfigure(3, weight=0)
        ttk.Button(playback_frame, text="播放输入", command=self.play_input).grid(row=0, column=0, sticky="w")
        ttk.Button(playback_frame, text="停止播放", command=self.stop_audio).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Label(playback_frame, text="试听片段").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.segment_combo = ttk.Combobox(
            playback_frame,
            textvariable=self.segment_var,
            state="readonly",
        )
        self.segment_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(10, 0))
        self.segment_combo.bind("<<ComboboxSelected>>", self.on_segment_changed)
        ttk.Button(playback_frame, text="上一段", command=self.go_prev_segment).grid(row=1, column=2, sticky="w", padx=(8, 0), pady=(10, 0))
        ttk.Button(playback_frame, text="下一段", command=self.go_next_segment).grid(row=1, column=3, sticky="w", padx=(8, 0), pady=(10, 0))
        ttk.Label(playback_frame, textvariable=self.segment_summary_var, wraplength=900, justify="left").grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(8, 0),
        )
        self.candidates_container = ttk.Frame(playback_frame)
        self.candidates_container.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        self.candidates_container.columnconfigure(0, weight=1)

        scoring_frame = ttk.LabelFrame(right, text="结构评分", padding=10)
        scoring_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        scoring_frame.columnconfigure(1, weight=1)
        row_index = 0
        for field_id, field_label in self.review_mode_config.scoring_fields:
            ttk.Label(scoring_frame, text=field_label).grid(row=row_index, column=0, sticky="w")
            combo = ttk.Combobox(
                scoring_frame,
                textvariable=self.field_vars[field_id],
                state="readonly",
            )
            combo.grid(row=row_index, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
            self.score_widgets[field_id] = combo
            row_index += 1

        ttk.Label(scoring_frame, text=self.review_mode_config.validity_field_label).grid(row=row_index, column=0, sticky="w")
        validity_combo = ttk.Combobox(
            scoring_frame,
            textvariable=self.valid_var,
            values=[label for _code, label in self.review_mode_config.validity_options],
            state="readonly",
        )
        validity_combo.grid(row=row_index, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        row_index += 1

        ttk.Checkbutton(scoring_frame, text="本条已完成", variable=self.completed_var).grid(
            row=row_index, column=0, columnspan=2, sticky="w"
        )

        help_frame = ttk.LabelFrame(right, text="判断词", padding=10)
        help_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        help_frame.columnconfigure(0, weight=1)
        help_frame.rowconfigure(0, weight=1)
        help_text = tk.Text(help_frame, height=12, wrap="word")
        help_text.grid(row=0, column=0, sticky="nsew")
        help_text.insert("1.0", self.review_mode_config.help_text)
        help_text.configure(state="disabled")

        notes_frame = ttk.LabelFrame(right, text="单条备注", padding=10)
        notes_frame.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)
        notes_frame.columnconfigure(1, weight=0)
        self.notes_text = tk.Text(notes_frame, height=9, wrap="word")
        self.notes_text.grid(row=0, column=0, sticky="nsew")
        notes_scrollbar = ttk.Scrollbar(notes_frame, orient="vertical", command=self.notes_text.yview)
        notes_scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        session_frame = ttk.LabelFrame(right, text="本次会话备注", padding=10)
        session_frame.grid(row=6, column=0, sticky="nsew", pady=(10, 0))
        session_frame.columnconfigure(0, weight=1)
        session_frame.rowconfigure(0, weight=1)
        session_frame.columnconfigure(1, weight=0)
        self.session_notes_text = tk.Text(session_frame, height=8, wrap="word")
        self.session_notes_text.grid(row=0, column=0, sticky="nsew")
        session_scrollbar = ttk.Scrollbar(session_frame, orient="vertical", command=self.session_notes_text.yview)
        session_scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        self.session_notes_text.configure(yscrollcommand=session_scrollbar.set)

        footer = ttk.Frame(right)
        footer.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status_var, wraplength=900, justify="left").grid(row=0, column=0, sticky="w")

    def bind_shortcuts(self) -> None:
        self.root.bind("<Control-s>", lambda _event: self.save_progress())
        self.root.bind("<Control-e>", lambda _event: self.export_review())

    def on_right_frame_configured(self, _event: tk.Event[tk.Misc]) -> None:
        if self.right_canvas is None:
            return
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))

    def on_right_canvas_configured(self, event: tk.Event[tk.Misc]) -> None:
        if self.right_canvas is None or self.right_canvas_window_id is None:
            return
        self.right_canvas.itemconfigure(self.right_canvas_window_id, width=event.width)

    def open_bundle_dialog(self) -> None:
        selected = filedialog.askopenfilenames(
            title="选择试听包清单文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
        )
        if not selected:
            return
        self.load_manifests([Path(item) for item in selected])
        self.try_restore_progress()
        self.refresh_record_list()
        self.refresh_current_record()

    def reload_loaded_manifests(self) -> None:
        if not self.loaded_manifest_paths:
            messagebox.showinfo("音频听审工具", "当前还没有加载任何试听包。")
            return
        self.load_manifests(self.loaded_manifest_paths)
        self.try_restore_progress()
        self.refresh_record_list()
        self.refresh_current_record()

    def on_filter_changed(self, _event: object) -> None:
        self.save_current_record_state()
        self.refresh_record_list()
        self.refresh_current_record()

    def load_manifests(self, manifest_paths: list[Path]) -> None:
        self.records_by_id = {}
        self.record_order = []
        self.filtered_record_ids = []
        self.loaded_manifest_paths = []
        record_accumulator: dict[str, AuditRecord] = {}

        for manifest_path in manifest_paths:
            resolved_manifest = resolve_manifest_path(manifest_path)
            payload = json.loads(resolved_manifest.read_text(encoding="utf-8"))
            branch_label = infer_manifest_branch_label(payload=payload, resolved_manifest=resolved_manifest)
            for record_payload in payload.get("records", []):
                record_id = str(record_payload["record_id"])
                record = record_accumulator.get(record_id)
                if record is None:
                    record = AuditRecord(record_id=record_id)
                    record_accumulator[record_id] = record
                record.source_manifests.append(resolved_manifest)
                record.audio_path = coalesce_path(
                    record.audio_path,
                    record_payload.get("audio_path"),
                    record_payload.get("target_audio_path"),
                )
                if record_payload.get("sample_rate") is not None:
                    record.sample_rate = int(record_payload["sample_rate"])
                record.input_audio_path = coalesce_path(
                    record.input_audio_path,
                    record_payload.get("input_audio_path"),
                    record_payload.get("aligned_target_audio_path"),
                )

                candidate_map = build_candidate_map(branch_label=branch_label, record_payload=record_payload)
                for label, path in candidate_map.items():
                    if path is None:
                        continue
                    resolved_path = Path(path).resolve()
                    if not resolved_path.exists():
                        continue
                    if any(existing.label == label and existing.path == resolved_path for existing in record.candidates):
                        continue
                    record.candidates.append(
                        CandidateTrack(
                            label=label,
                            path=resolved_path,
                            source_manifest=resolved_manifest,
                        )
                    )
            self.loaded_manifest_paths.append(resolved_manifest)

        self.records_by_id = dict(sorted(record_accumulator.items()))
        self.record_order = list(self.records_by_id.keys())
        self.refresh_summary()
        self.status_var.set("试听包元数据已加载。")
        if self.current_index >= len(self.record_order):
            self.current_index = max(0, len(self.record_order) - 1)

    def try_restore_manifests_from_progress(self) -> None:
        payload = self.read_progress_payload()
        if payload is None:
            return
        manifest_paths = [Path(item) for item in payload.get("loaded_manifests", [])]
        if not manifest_paths:
            return
        existing_manifest_paths: list[Path] = []
        for path in manifest_paths:
            try:
                resolve_manifest_path(path)
            except FileNotFoundError:
                continue
            existing_manifest_paths.append(path)
        if not existing_manifest_paths:
            self.status_var.set("找到了旧进度文件，但其中记录的试听包都已经不存在了。")
            return
        self.load_manifests(existing_manifest_paths)
        self.status_var.set("已从旧进度文件恢复试听包列表。")

    def read_progress_payload(self) -> dict[str, Any] | None:
        if not self.progress_json_path.exists():
            return None
        return json.loads(self.progress_json_path.read_text(encoding="utf-8"))

    def try_restore_progress(self) -> None:
        payload = self.read_progress_payload()
        if payload is None:
            return
        progress_review_mode = str(payload.get("review_mode", COMPARATIVE_REVIEW_MODE_CONFIG.review_mode)).strip().lower()
        if progress_review_mode != self.review_mode_config.review_mode:
            self.status_var.set(
                "发现旧进度文件，但评审模式与当前会话不一致，未自动套用旧评分。"
            )
            return
        manifests = [Path(item).resolve() for item in payload.get("loaded_manifests", [])]
        if manifests and manifests != [item.resolve() for item in self.loaded_manifest_paths]:
            self.status_var.set("发现旧进度文件，但当前加载的试听包不一致，未自动套用旧评分。")
            return
        self.review_state = dict(payload.get("review_state", {}))
        self.current_index = int(payload.get("current_index", self.current_index))
        if self.session_notes_text is not None:
            self.session_notes_text.delete("1.0", tk.END)
            self.session_notes_text.insert("1.0", str(payload.get("session_notes", "")))
        self.refresh_summary()
        self.status_var.set("已恢复上次听审进度。")

    def refresh_record_list(self) -> None:
        if self.record_listbox is None:
            return
        filter_text = self.record_filter_var.get().strip().lower()
        self.record_listbox.delete(0, tk.END)
        filtered_ids: list[str] = []
        for record_id in self.record_order:
            if filter_text and filter_text not in record_id.lower():
                continue
            filtered_ids.append(record_id)
            review = self.review_state.get(record_id, {})
            status = "[x]" if review.get("completed") else "[ ]"
            validity = validity_label_from_value(
                str(review.get("valid_for_comparison", "yes")),
                self.review_mode_config,
            )
            self.record_listbox.insert(tk.END, f"{status} {record_id} ({validity})")
        self.filtered_record_ids = filtered_ids
        if filtered_ids:
            selected_index = min(self.current_index, len(filtered_ids) - 1)
            self.current_index = selected_index
            self.record_listbox.selection_clear(0, tk.END)
            self.record_listbox.selection_set(selected_index)
            self.record_listbox.activate(selected_index)
            self.record_listbox.see(selected_index)
        else:
            self.current_index = 0
        self.refresh_summary()

    def on_record_selected(self, _event: object) -> None:
        if self.record_listbox is None:
            return
        selection = self.record_listbox.curselection()
        if not selection:
            return
        self.save_current_record_state()
        self.current_index = int(selection[0])
        self.refresh_current_record()

    def refresh_current_record(self) -> None:
        if not self.filtered_record_ids:
            self.current_record_var.set("当前没有可显示记录")
            self.input_path_var.set("")
            self.audio_path_var.set("")
            self.refresh_segments(None)
            self.clear_candidate_widgets()
            self.status_var.set("当前筛选条件下没有记录。")
            return
        record_id = self.filtered_record_ids[self.current_index]
        record = self.records_by_id[record_id]
        self.current_record_var.set(record.record_id)
        self.input_path_var.set("" if record.input_audio_path is None else record.input_audio_path.as_posix())
        self.audio_path_var.set("" if record.audio_path is None else record.audio_path.as_posix())
        self.refresh_segments(record)
        self.render_candidates(record)
        self.load_review_state(record_id)
        self.status_var.set(f"正在查看 {self.current_index + 1}/{len(self.filtered_record_ids)}：{record_id}")

    def render_candidates(self, record: AuditRecord) -> None:
        self.clear_candidate_widgets()
        for row_index, candidate in enumerate(record.candidates):
            frame = ttk.Frame(self.candidates_container)
            frame.grid(row=row_index, column=0, sticky="ew", pady=(0, 6))
            frame.columnconfigure(1, weight=1)
            ttk.Label(frame, text=candidate.label).grid(row=0, column=0, sticky="w")
            entry = ttk.Entry(frame)
            entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
            entry.insert(0, candidate.path.as_posix())
            entry.configure(state="readonly")
            ttk.Button(frame, text="播放", command=lambda path=candidate.path: self.play_track(path)).grid(row=0, column=2, sticky="e")
            self.candidate_frames.append(frame)

        for field_id, _field_label in self.review_mode_config.scoring_fields:
            if self.review_mode_config.scoring_option_mode == "candidate_labels":
                options = [""] + [candidate.label for candidate in record.candidates]
            else:
                options = list(self.review_mode_config.fixed_field_options.get(field_id, ("",)))
            self.score_widgets[field_id].configure(values=options)

    def clear_candidate_widgets(self) -> None:
        for frame in self.candidate_frames:
            frame.destroy()
        self.candidate_frames.clear()

    def load_review_state(self, record_id: str) -> None:
        review = self.review_state.get(record_id, {})
        for field_id, _field_label in self.review_mode_config.scoring_fields:
            self.field_vars[field_id].set(str(review.get(field_id, "")))
        self.valid_var.set(
            validity_label_from_value(
                str(review.get("valid_for_comparison", "yes")),
                self.review_mode_config,
            )
        )
        self.completed_var.set(bool(review.get("completed", False)))
        if self.notes_text is not None:
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", str(review.get("notes", "")))

    def save_current_record_state(self) -> None:
        if not self.filtered_record_ids:
            return
        record_id = self.filtered_record_ids[self.current_index]
        self.review_state[record_id] = {
            field_id: self.field_vars[field_id].get().strip()
            for field_id, _field_label in self.review_mode_config.scoring_fields
        }
        self.review_state[record_id]["valid_for_comparison"] = validity_code_from_value(
            self.valid_var.get().strip(),
            self.review_mode_config,
        )
        self.review_state[record_id]["completed"] = bool(self.completed_var.get())
        if self.notes_text is not None:
            self.review_state[record_id]["notes"] = self.notes_text.get("1.0", tk.END).strip()

    def play_input(self) -> None:
        if not self.filtered_record_ids:
            return
        record_id = self.filtered_record_ids[self.current_index]
        record = self.records_by_id[record_id]
        if record.input_audio_path is None:
            messagebox.showwarning("音频听审工具", "这一条没有可播放的 input.wav。")
            return
        self.play_track(record.input_audio_path)

    def play_track(self, path: Path) -> None:
        segment = self.get_selected_segment()
        playback_path = path
        if not segment.is_full_audio:
            playback_path = self.materialize_segment_audio(path=path, segment=segment)
        self.play_audio(playback_path)
        if segment.is_full_audio:
            self.status_var.set(f"正在播放整段：{path.name}")
            return
        self.status_var.set(
            f"正在播放 {segment.label}：{path.name} "
            f"({segment.start_sec:.1f}s - {segment.end_sec:.1f}s)"
        )

    def play_audio(self, path: Path) -> None:
        if winsound is None:
            messagebox.showerror("音频听审工具", "当前 Python 环境不可用 winsound，无法直接播放 wav。")
            return
        if not path.exists():
            messagebox.showerror("音频听审工具", f"音频文件不存在：\n{path}")
            return
        playback_path = self.prepare_playback_path(path)
        try:
            winsound.PlaySound(str(playback_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except RuntimeError as exc:
            messagebox.showerror(
                "音频听审工具",
                f"播放失败：\n{playback_path}\n\n{exc}",
            )
            self.status_var.set(f"播放失败：{playback_path.name}")
            return

    def prepare_playback_path(self, path: Path) -> Path:
        normalized_path = path.resolve()
        if normalized_path.suffix.lower() != ".wav":
            return normalized_path
        # winsound uses legacy Win32 file APIs underneath on some systems.
        # Materializing a short cached path avoids silent playback failures
        # when deeply nested bundle paths exceed classic MAX_PATH-style limits.
        cache_key = hashlib.sha1(normalized_path.as_posix().encode("utf-8")).hexdigest()[:16]
        cache_path = self.playback_cache_dir / f"{cache_key}_{normalized_path.name}"
        if cache_path.exists():
            return cache_path
        cache_path.write_bytes(normalized_path.read_bytes())
        return cache_path

    def stop_audio(self) -> None:
        if winsound is None:
            return
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.status_var.set("已停止播放。")

    def go_prev(self) -> None:
        if not self.filtered_record_ids:
            return
        if self.current_index <= 0:
            return
        self.save_current_record_state()
        self.current_index -= 1
        self.refresh_record_list()
        self.refresh_current_record()

    def go_next(self) -> None:
        if not self.filtered_record_ids:
            return
        if self.current_index >= len(self.filtered_record_ids) - 1:
            return
        self.save_current_record_state()
        self.current_index += 1
        self.refresh_record_list()
        self.refresh_current_record()

    def save_progress(self) -> None:
        self.save_current_record_state()
        payload = {
            "review_mode": self.review_mode_config.review_mode,
            "loaded_manifests": [path.as_posix() for path in self.loaded_manifest_paths],
            "current_index": self.current_index,
            "review_state": self.review_state,
            "session_notes": "" if self.session_notes_text is None else self.session_notes_text.get("1.0", tk.END).strip(),
        }
        self.progress_json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
        self.refresh_record_list()
        self.status_var.set(f"进度已保存：{self.progress_json_path}")

    def refresh_summary(self) -> None:
        if not self.record_order:
            self.summary_var.set("尚未加载试听包。")
            return
        completed_count = sum(
            1 for record_id in self.record_order if bool(self.review_state.get(record_id, {}).get("completed", False))
        )
        filtered_count = len(self.filtered_record_ids) if self.filtered_record_ids else len(self.record_order)
        self.summary_var.set(
            f"已加载 {len(self.loaded_manifest_paths)} 个试听包，"
            f"共 {len(self.record_order)} 条记录。"
            f"已完成 {completed_count}/{len(self.record_order)}。"
            f"当前可见 {filtered_count} 条。"
        )

    def export_review(self) -> None:
        self.save_progress()
        self.save_current_record_state()
        summary = build_review_summary(
            records_by_id=self.records_by_id,
            review_state=self.review_state,
            manifest_paths=self.loaded_manifest_paths,
            session_notes="" if self.session_notes_text is None else self.session_notes_text.get("1.0", tk.END).strip(),
            review_mode_config=self.review_mode_config,
        )
        self.export_json_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
        self.export_md_path.write_text(
            build_review_markdown(summary),
            encoding="utf-8",
            newline="\n",
        )
        self.status_var.set(f"评审结果已导出：{self.export_json_path} / {self.export_md_path}")
        messagebox.showinfo("音频听审工具", f"评审结果已导出到：\n{self.export_json_path}\n{self.export_md_path}")

    def refresh_segments(self, record: AuditRecord | None) -> None:
        if self.segment_combo is None:
            return
        self.current_segments = build_segments_for_record(record)
        segment_labels = [segment.label for segment in self.current_segments]
        self.segment_combo.configure(values=segment_labels)
        default_label = segment_labels[0] if segment_labels else FULL_AUDIO_SEGMENT_LABEL
        self.segment_var.set(default_label)
        self.update_segment_summary()

    def on_segment_changed(self, _event: object | None = None) -> None:
        self.update_segment_summary()

    def update_segment_summary(self) -> None:
        segment = self.get_selected_segment()
        if segment.is_full_audio:
            if len(self.current_segments) <= 1:
                self.segment_summary_var.set("当前播放整段。当前记录较短，无需自动切段。")
            else:
                self.segment_summary_var.set(
                    f"当前播放整段。当前记录也支持分段试听，共 {len(self.current_segments) - 1} 段。"
                )
            return
        self.segment_summary_var.set(
            f"当前片段：{segment.label}，范围 {segment.start_sec:.1f}s - {segment.end_sec:.1f}s。"
        )

    def get_selected_segment(self) -> ListeningSegment:
        selected_label = self.segment_var.get().strip()
        for segment in self.current_segments:
            if segment.label == selected_label:
                return segment
        return self.current_segments[0]

    def go_prev_segment(self) -> None:
        if len(self.current_segments) <= 1:
            return
        current_label = self.segment_var.get().strip()
        labels = [segment.label for segment in self.current_segments]
        if current_label not in labels:
            self.segment_var.set(labels[0])
            self.update_segment_summary()
            return
        current_index = labels.index(current_label)
        if current_index <= 0:
            return
        self.segment_var.set(labels[current_index - 1])
        self.update_segment_summary()

    def go_next_segment(self) -> None:
        if len(self.current_segments) <= 1:
            return
        current_label = self.segment_var.get().strip()
        labels = [segment.label for segment in self.current_segments]
        if current_label not in labels:
            self.segment_var.set(labels[0])
            self.update_segment_summary()
            return
        current_index = labels.index(current_label)
        if current_index >= len(labels) - 1:
            return
        self.segment_var.set(labels[current_index + 1])
        self.update_segment_summary()

    def materialize_segment_audio(self, path: Path, segment: ListeningSegment) -> Path:
        if segment.is_full_audio or path.suffix.lower() != ".wav":
            return path
        cache_key = hashlib.sha1(
            f"{path.resolve().as_posix()}::{segment.start_frame}::{segment.end_frame}".encode("utf-8")
        ).hexdigest()[:16]
        cache_path = self.segment_cache_dir / f"{path.stem}__{cache_key}__segment.wav"
        if cache_path.exists():
            return cache_path
        with wave.open(str(path), "rb") as reader:
            start_frame = max(0, int(segment.start_frame or 0))
            end_frame = max(start_frame, min(reader.getnframes(), int(segment.end_frame or reader.getnframes())))
            reader.setpos(start_frame)
            frames = reader.readframes(end_frame - start_frame)
            with wave.open(str(cache_path), "wb") as writer:
                writer.setnchannels(reader.getnchannels())
                writer.setsampwidth(reader.getsampwidth())
                writer.setframerate(reader.getframerate())
                writer.setcomptype(reader.getcomptype(), reader.getcompname())
                writer.writeframes(frames)
        return cache_path


def resolve_manifest_path(path: Path) -> Path:
    candidate = path.resolve()
    if candidate.is_dir():
        for filename in ("proxy_audio_export.json", "nores_vocoder_audio_export.json"):
            candidate_path = candidate / filename
            if candidate_path.exists():
                return candidate_path
        candidate = candidate / "proxy_audio_export.json"
    if not candidate.exists():
        raise FileNotFoundError(f"找不到试听包清单文件：{candidate}")
    return candidate


def coalesce_path(current: Path | None, *raw_paths: object) -> Path | None:
    if current is not None:
        return current
    for raw_path in raw_paths:
        if raw_path in {None, ""}:
            continue
        return Path(str(raw_path)).resolve()
    return None


def infer_manifest_branch_label(payload: dict[str, Any], resolved_manifest: Path) -> str:
    branch_label = payload.get("branch_label")
    if isinstance(branch_label, str) and branch_label.strip():
        return branch_label.strip()
    selected_summary = payload.get("selected_checkpoint_summary")
    if isinstance(selected_summary, dict) and selected_summary.get("step") is not None:
        selection_target = str(payload.get("selection_target", "checkpoint")).strip() or "checkpoint"
        return f"{selection_target}:step{int(selected_summary['step'])}"
    checkpoint_path = payload.get("checkpoint_path")
    if isinstance(checkpoint_path, str) and checkpoint_path.strip():
        return Path(checkpoint_path).stem
    return resolved_manifest.parent.name


def build_candidate_map(branch_label: str, record_payload: dict[str, Any]) -> dict[str, str | None]:
    if "student_proxy_audio_path" in record_payload or "teacher_proxy_audio_path" in record_payload:
        return {
            f"{branch_label}:teacher_proxy": record_payload.get("teacher_proxy_audio_path"),
            f"{branch_label}:student_proxy": record_payload.get("student_proxy_audio_path"),
        }
    primary_listening_path = select_primary_listening_path(record_payload)
    if primary_listening_path is not None:
        return {
            branch_label: primary_listening_path,
        }
    if "decoded_audio_path" in record_payload:
        return {
            branch_label: record_payload.get("decoded_audio_path"),
        }
    return {
        branch_label: record_payload.get("proxy_audio_path"),
    }


def select_primary_listening_path(record_payload: dict[str, Any]) -> str | None:
    listening_audio_path = record_payload.get("listening_audio_path")
    if isinstance(listening_audio_path, str) and listening_audio_path.strip():
        return listening_audio_path
    listening_audio_source = str(record_payload.get("listening_audio_source", "")).strip().lower()
    if listening_audio_source == "decoded":
        decoded_audio_path = record_payload.get("decoded_audio_path")
        if isinstance(decoded_audio_path, str) and decoded_audio_path.strip():
            return decoded_audio_path
    if listening_audio_source == "decoded_pitch_matched":
        decoded_pitch_matched_audio_path = record_payload.get("decoded_pitch_matched_audio_path")
        if isinstance(decoded_pitch_matched_audio_path, str) and decoded_pitch_matched_audio_path.strip():
            return decoded_pitch_matched_audio_path
    if listening_audio_source == "audit_proxy":
        audit_proxy_audio_path = record_payload.get("audit_proxy_audio_path")
        if isinstance(audit_proxy_audio_path, str) and audit_proxy_audio_path.strip():
            return audit_proxy_audio_path
    return None


def build_review_summary(
    records_by_id: dict[str, AuditRecord],
    review_state: dict[str, dict[str, Any]],
    manifest_paths: list[Path],
    session_notes: str,
    review_mode_config: ReviewModeConfig,
) -> dict[str, Any]:
    aggregate: dict[str, dict[str, int]] = {}
    for field_id, _field_label in review_mode_config.scoring_fields:
        counter = Counter()
        for record_id in records_by_id:
            review = dict(review_state.get(record_id, {}))
            selected = normalize_review_choice(
                field_id=field_id,
                review=review,
                review_mode_config=review_mode_config,
            )
            if selected:
                counter[selected] += 1
        aggregate[field_id] = dict(sorted(counter.items()))
    validity_counter = Counter(
        validity_code_from_value(
            str(review_state.get(record_id, {}).get("valid_for_comparison", "yes")).strip(),
            review_mode_config,
        )
        for record_id in records_by_id
    )
    completed_count = sum(1 for record_id in records_by_id if bool(review_state.get(record_id, {}).get("completed", False)))

    records_payload: list[dict[str, Any]] = []
    for record_id, record in records_by_id.items():
        review = dict(review_state.get(record_id, {}))
        interpreted_review = {
            field_id: normalize_review_choice(
                field_id=field_id,
                review=review,
                review_mode_config=review_mode_config,
            )
            for field_id, _field_label in review_mode_config.scoring_fields
        }
        records_payload.append(
            {
                "record_id": record_id,
                "input_audio_path": None if record.input_audio_path is None else record.input_audio_path.as_posix(),
                "audio_path": None if record.audio_path is None else record.audio_path.as_posix(),
                "candidate_labels": [candidate.label for candidate in record.candidates],
                "review": review,
                "interpreted_review": interpreted_review,
            }
        )

    return {
        "review_mode": review_mode_config.review_mode,
        "field_labels": {field_id: field_label for field_id, field_label in review_mode_config.scoring_fields},
        "validity_field_label": review_mode_config.validity_field_label,
        "validity_options": {
            code: label for code, label in review_mode_config.validity_options
        },
        "manifest_paths": [path.as_posix() for path in manifest_paths],
        "record_count": len(records_by_id),
        "completed_count": completed_count,
        "session_notes": session_notes,
        "tie_policy": review_mode_config.tie_policy,
        "aggregate": {
            "by_field": aggregate,
            "valid_for_comparison": dict(sorted(validity_counter.items())),
        },
        "records": records_payload,
    }


def build_review_markdown(summary: dict[str, Any]) -> str:
    field_label_map = {
        str(field_id): str(field_label)
        for field_id, field_label in dict(summary.get("field_labels", {})).items()
    }
    validity_options = {
        str(code): str(label) for code, label in dict(summary.get("validity_options", {})).items()
    }
    lines = [
        "# 音频听审结果",
        "",
        "## 概览",
        f"- 评审模式: {summary.get('review_mode', COMPARATIVE_REVIEW_MODE_CONFIG.review_mode)}",
        f"- 总记录数: {summary['record_count']}",
        f"- 已完成数: {summary['completed_count']}",
        f"- 清单文件: {summary['manifest_paths']}",
        f"- 留空解释: {summary.get('tie_policy', '（未声明）')}",
        "",
        "## 汇总统计",
    ]
    for field_id, counts in summary["aggregate"]["by_field"].items():
        lines.append(f"### {field_label_map[field_id]}")
        if counts:
            for label, value in counts.items():
                lines.append(f"- {label}: {value}")
        else:
            lines.append("- 暂无")
    lines.append(f"### {summary.get('validity_field_label', '是否适合比较')}")
    for label, value in summary["aggregate"]["valid_for_comparison"].items():
        lines.append(f"- {validity_options.get(str(label), str(label))}: {value}")
    lines.extend(["", "## 会话备注", summary["session_notes"] or "（空）", "", "## 单条记录"])
    for record in summary["records"]:
        lines.append(f"### {record['record_id']}")
        lines.append(f"- 候选音频: {record['candidate_labels']}")
        review = record["review"]
        interpreted_review = record.get("interpreted_review", {})
        for field_id in field_label_map:
            lines.append(f"- {field_label_map[field_id]}: {interpreted_review.get(field_id, review.get(field_id, ''))}")
        lines.append(
            f"- {summary.get('validity_field_label', '是否适合比较')}: "
            f"{validity_options.get(str(review.get('valid_for_comparison', 'yes')), str(review.get('valid_for_comparison', 'yes')))}"
        )
        lines.append(f"- 是否完成: {review.get('completed', False)}")
        lines.append(f"- 备注: {review.get('notes', '')}")
        lines.append("")
    return "\n".join(lines)


def normalize_review_choice(
    field_id: str,
    review: dict[str, Any],
    review_mode_config: ReviewModeConfig,
) -> str:
    selected = str(review.get(field_id, "")).strip()
    if selected:
        return selected
    is_completed = bool(review.get("completed", False))
    validity_code = validity_code_from_value(
        str(review.get("valid_for_comparison", "yes")).strip(),
        review_mode_config,
    )
    if (
        is_completed
        and validity_code != "no"
        and review_mode_config.blank_completed_label is not None
    ):
        return review_mode_config.blank_completed_label
    return ""


def build_segments_for_record(record: AuditRecord | None) -> list[ListeningSegment]:
    full_audio_segment = [ListeningSegment(FULL_AUDIO_SEGMENT_LABEL, None, None, 0.0, 0.0)]
    if record is None:
        return full_audio_segment
    duration_source = record.input_audio_path
    if duration_source is None and record.candidates:
        duration_source = record.candidates[0].path
    if duration_source is None or duration_source.suffix.lower() != ".wav":
        return full_audio_segment
    duration_seconds, sample_rate, frame_count = read_wav_duration(duration_source)
    if duration_seconds < AUTO_SEGMENT_MIN_SECONDS or sample_rate <= 0 or frame_count <= 0:
        return full_audio_segment
    segments: list[ListeningSegment] = []
    step_seconds = max(0.5, SEGMENT_LENGTH_SECONDS - SEGMENT_OVERLAP_SECONDS)
    segment_count = max(1, int(math.ceil(max(0.0, duration_seconds - SEGMENT_OVERLAP_SECONDS) / step_seconds)))
    for index in range(segment_count):
        start_sec = min(duration_seconds, index * step_seconds)
        end_sec = min(duration_seconds, start_sec + SEGMENT_LENGTH_SECONDS)
        start_frame = int(round(start_sec * sample_rate))
        end_frame = int(round(end_sec * sample_rate))
        if end_frame <= start_frame:
            continue
        segments.append(
            ListeningSegment(
                label=f"片段 {index + 1}",
                start_frame=start_frame,
                end_frame=end_frame,
                start_sec=start_sec,
                end_sec=end_sec,
            )
        )
        if end_sec >= duration_seconds:
            break
    if not segments:
        return full_audio_segment
    segments.append(ListeningSegment(FULL_AUDIO_SEGMENT_LABEL, None, None, 0.0, duration_seconds))
    return segments


def read_wav_duration(path: Path) -> tuple[float, int, int]:
    try:
        with wave.open(str(path), "rb") as reader:
            sample_rate = int(reader.getframerate())
            frame_count = int(reader.getnframes())
    except (wave.Error, FileNotFoundError, EOFError, OSError):
        return 0.0, 0, 0
    if sample_rate <= 0 or frame_count <= 0:
        return 0.0, sample_rate, frame_count
    return frame_count / float(sample_rate), sample_rate, frame_count


def validity_label_from_value(value: str, review_mode_config: ReviewModeConfig) -> str:
    code_to_label = {code: label for code, label in review_mode_config.validity_options}
    label_to_code = {label: code for code, label in review_mode_config.validity_options}
    normalized = value.strip()
    if normalized in code_to_label:
        return code_to_label[normalized]
    if normalized in label_to_code:
        return normalized
    return code_to_label["yes"]


def validity_code_from_value(value: str, review_mode_config: ReviewModeConfig) -> str:
    code_to_label = {code: label for code, label in review_mode_config.validity_options}
    label_to_code = {label: code for code, label in review_mode_config.validity_options}
    normalized = value.strip()
    if normalized in label_to_code:
        return label_to_code[normalized]
    if normalized in code_to_label:
        return normalized
    return "yes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="用于试听 proxy-audio bundle 的中文听审 GUI。"
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        nargs="*",
        default=[],
        help="启动时预加载的 bundle 目录或 proxy_audio_export.json 文件。",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/audio/audio_audit_gui_exports"),
        help="用于保存进度文件和导出评审结果的目录。",
    )
    parser.add_argument(
        "--auto-close-ms",
        type=int,
        default=None,
        help="可选 smoke test 模式：窗口在指定毫秒后自动关闭。",
    )
    parser.add_argument(
        "--review-mode",
        default=COMPARATIVE_REVIEW_MODE_CONFIG.review_mode,
        choices=sorted(REVIEW_MODE_CONFIGS.keys()),
        help="评审模式：comparative 用于多分支对比，milestone_acceptance 用于单 bundle 的绝对门槛验收。",
    )
    return parser


def launch_audio_audit_gui(
    bundle_paths: list[Path],
    output_dir: Path,
    review_mode: str = COMPARATIVE_REVIEW_MODE_CONFIG.review_mode,
    auto_close_ms: int | None = None,
) -> None:
    root = tk.Tk()
    app = AudioAuditApp(
        root=root,
        manifest_paths=bundle_paths,
        output_dir=output_dir,
        review_mode=review_mode,
    )
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(app))
    if auto_close_ms is not None:
        root.after(max(1, int(auto_close_ms)), lambda: on_close(app))
    root.mainloop()


def on_close(app: AudioAuditApp) -> None:
    app.save_progress()
    app.stop_audio()
    app.root.destroy()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    launch_audio_audit_gui(
        bundle_paths=list(args.bundle),
        output_dir=args.output_dir,
        review_mode=args.review_mode,
        auto_close_ms=args.auto_close_ms,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
