from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import winsound
except ImportError:  # pragma: no cover
    winsound = None


SCORING_FIELDS = (
    ("best_rhythm", "节奏最好"),
    ("best_boundary", "边界最好"),
    ("most_stable", "最稳定"),
    ("overall_pick", "综合首选"),
)

VALIDITY_OPTIONS = (
    ("yes", "可比较"),
    ("partial", "部分可比较"),
    ("no", "不建议比较"),
)

VALIDITY_CODE_TO_LABEL = {code: label for code, label in VALIDITY_OPTIONS}
VALIDITY_LABEL_TO_CODE = {label: code for code, label in VALIDITY_OPTIONS}

GUI_HELP_TEXT = """\
这些维度到底在听什么：

1. 节奏最好
就是听哪条更像正常人在说话。
重点不是“好不好听”，而是停顿顺不顺、快慢自然不自然。

2. 边界最好
就是听一句话该停的地方有没有停住，该收的时候有没有收住。
如果句尾拖着不收，或者中间断句很硬，这项一般就不会高。

3. 最稳定
就是听整段有没有突然发飘、忽大忽小、毛刺、抖动、结构突然塌掉。
稳定不等于平淡，而是不要失控。

4. 综合首选
如果只能留一个继续往下看，就选它。
它不一定每一项都第一，但整体最顺、最靠谱。

5. 是否适合比较
如果这一条三者差异几乎听不出来，或者全都失真得厉害，
就不要硬判胜负，可以记成“部分可比较”或“不建议比较”。

这次最该关注：
- 停顿对不对
- 断句自然不自然
- 能量起伏乱不乱
- student_proxy 有没有跟上 teacher_proxy 的结构

这次先别太关注：
- 最终音色像不像
- 谁更“好听”
- 绝对音高高一点还是低一点
- 高频细节漂不漂亮

当前这版 Stage3 proxy 还有一个很重要的边界：
- 载频基本是固定的，teacher 和 student 会听起来都接近单调嗡声
- 所以不要把“有没有音节感、有没有真实旋律起伏”当成这版 proxy 的主要判断依据
- 它更适合听：
  - 停顿有没有出来
  - 整体能量包络是不是跟上了
  - 有没有明显发飘、塌陷、忽大忽小
"""


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


class AudioAuditApp:
    def __init__(
        self,
        root: tk.Tk,
        manifest_paths: list[Path],
        output_dir: Path,
    ) -> None:
        self.root = root
        self.output_dir = output_dir.resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.export_json_path = self.output_dir / "audio_audit_review.json"
        self.export_md_path = self.output_dir / "audio_audit_review.md"
        self.progress_json_path = self.output_dir / "audio_audit_progress.json"

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
        self.session_notes_text: tk.Text | None = None
        self.notes_text: tk.Text | None = None
        self.valid_var = tk.StringVar(value=VALIDITY_CODE_TO_LABEL["yes"])
        self.completed_var = tk.BooleanVar(value=False)
        self.field_vars: dict[str, tk.StringVar] = {
            field_id: tk.StringVar(value="") for field_id, _ in SCORING_FIELDS
        }
        self.score_widgets: dict[str, ttk.Combobox] = {}
        self.candidate_frames: list[ttk.Frame] = []

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
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=10)
        left.grid(row=0, column=0, sticky="ns")
        left.rowconfigure(4, weight=1)

        ttk.Label(left, text="试听包").grid(row=0, column=0, sticky="w")
        bundle_controls = ttk.Frame(left)
        bundle_controls.grid(row=1, column=0, sticky="ew", pady=(6, 10))
        ttk.Button(bundle_controls, text="添加试听包", command=self.open_bundle_dialog).grid(row=0, column=0, sticky="ew")
        ttk.Button(bundle_controls, text="重新载入", command=self.reload_loaded_manifests).grid(row=1, column=0, sticky="ew", pady=(6, 0))

        ttk.Label(left, text="筛选").grid(row=2, column=0, sticky="w")
        filter_entry = ttk.Entry(left, textvariable=self.record_filter_var, width=40)
        filter_entry.grid(row=3, column=0, sticky="new", pady=(6, 6))
        filter_entry.bind("<KeyRelease>", self.on_filter_changed)

        self.record_listbox = tk.Listbox(left, width=46, height=36, exportselection=False)
        self.record_listbox.grid(row=4, column=0, sticky="nsew")
        self.record_listbox.bind("<<ListboxSelect>>", self.on_record_selected)

        left_actions = ttk.Frame(left)
        left_actions.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(left_actions, text="上一条", command=self.go_prev).grid(row=0, column=0, sticky="ew")
        ttk.Button(left_actions, text="下一条", command=self.go_next).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ttk.Button(left_actions, text="保存进度", command=self.save_progress).grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(left_actions, text="导出结果", command=self.export_review).grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(left, textvariable=self.summary_var, wraplength=300, justify="left").grid(
            row=6, column=0, sticky="ew", pady=(10, 0)
        )

        right = ttk.Frame(self.root, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
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
        ttk.Button(playback_frame, text="播放输入", command=self.play_input).grid(row=0, column=0, sticky="w")
        ttk.Button(playback_frame, text="停止播放", command=self.stop_audio).grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.candidates_container = ttk.Frame(playback_frame)
        self.candidates_container.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.candidates_container.columnconfigure(0, weight=1)

        scoring_frame = ttk.LabelFrame(right, text="结构评分", padding=10)
        scoring_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        scoring_frame.columnconfigure(1, weight=1)
        row_index = 0
        for field_id, field_label in SCORING_FIELDS:
            ttk.Label(scoring_frame, text=field_label).grid(row=row_index, column=0, sticky="w")
            combo = ttk.Combobox(
                scoring_frame,
                textvariable=self.field_vars[field_id],
                state="readonly",
            )
            combo.grid(row=row_index, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
            self.score_widgets[field_id] = combo
            row_index += 1

        ttk.Label(scoring_frame, text="是否适合比较").grid(row=row_index, column=0, sticky="w")
        validity_combo = ttk.Combobox(
            scoring_frame,
            textvariable=self.valid_var,
            values=[label for _code, label in VALIDITY_OPTIONS],
            state="readonly",
        )
        validity_combo.grid(row=row_index, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        row_index += 1

        ttk.Checkbutton(scoring_frame, text="本条已完成", variable=self.completed_var).grid(
            row=row_index, column=0, columnspan=2, sticky="w"
        )

        help_frame = ttk.LabelFrame(right, text="这些维度怎么听", padding=10)
        help_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        help_frame.columnconfigure(0, weight=1)
        help_frame.rowconfigure(0, weight=1)
        help_text = tk.Text(help_frame, height=12, wrap="word")
        help_text.grid(row=0, column=0, sticky="nsew")
        help_text.insert("1.0", GUI_HELP_TEXT)
        help_text.configure(state="disabled")

        notes_frame = ttk.LabelFrame(right, text="单条备注", padding=10)
        notes_frame.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)
        self.notes_text = tk.Text(notes_frame, height=9, wrap="word")
        self.notes_text.grid(row=0, column=0, sticky="nsew")

        session_frame = ttk.LabelFrame(right, text="本次会话备注", padding=10)
        session_frame.grid(row=6, column=0, sticky="nsew", pady=(10, 0))
        session_frame.columnconfigure(0, weight=1)
        session_frame.rowconfigure(0, weight=1)
        self.session_notes_text = tk.Text(session_frame, height=8, wrap="word")
        self.session_notes_text.grid(row=0, column=0, sticky="nsew")

        footer = ttk.Frame(right)
        footer.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status_var, wraplength=900, justify="left").grid(row=0, column=0, sticky="w")

    def bind_shortcuts(self) -> None:
        self.root.bind("<Control-s>", lambda _event: self.save_progress())
        self.root.bind("<Control-e>", lambda _event: self.export_review())
        self.root.bind("<Left>", lambda _event: self.go_prev())
        self.root.bind("<Right>", lambda _event: self.go_next())

    def open_bundle_dialog(self) -> None:
        selected = filedialog.askopenfilenames(
            title="选择 proxy_audio_export.json 文件",
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
            branch_label = str(payload.get("branch_label", resolved_manifest.parent.name))
            for record_payload in payload.get("records", []):
                record_id = str(record_payload["record_id"])
                record = record_accumulator.get(record_id)
                if record is None:
                    record = AuditRecord(record_id=record_id)
                    record_accumulator[record_id] = record
                record.source_manifests.append(resolved_manifest)
                record.audio_path = coalesce_path(record.audio_path, record_payload.get("audio_path"))
                if record_payload.get("sample_rate") is not None:
                    record.sample_rate = int(record_payload["sample_rate"])
                record.input_audio_path = coalesce_path(record.input_audio_path, record_payload.get("input_audio_path"))

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
            validity = validity_label_from_value(str(review.get("valid_for_comparison", "yes")))
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
            self.clear_candidate_widgets()
            self.status_var.set("当前筛选条件下没有记录。")
            return
        record_id = self.filtered_record_ids[self.current_index]
        record = self.records_by_id[record_id]
        self.current_record_var.set(record.record_id)
        self.input_path_var.set("" if record.input_audio_path is None else record.input_audio_path.as_posix())
        self.audio_path_var.set("" if record.audio_path is None else record.audio_path.as_posix())
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
            ttk.Button(frame, text="播放", command=lambda path=candidate.path: self.play_audio(path)).grid(row=0, column=2, sticky="e")
            self.candidate_frames.append(frame)

        options = [""] + [candidate.label for candidate in record.candidates]
        for field_id, _field_label in SCORING_FIELDS:
            self.score_widgets[field_id].configure(values=options)

    def clear_candidate_widgets(self) -> None:
        for frame in self.candidate_frames:
            frame.destroy()
        self.candidate_frames.clear()

    def load_review_state(self, record_id: str) -> None:
        review = self.review_state.get(record_id, {})
        for field_id, _field_label in SCORING_FIELDS:
            self.field_vars[field_id].set(str(review.get(field_id, "")))
        self.valid_var.set(validity_label_from_value(str(review.get("valid_for_comparison", "yes"))))
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
            for field_id, _field_label in SCORING_FIELDS
        }
        self.review_state[record_id]["valid_for_comparison"] = validity_code_from_value(self.valid_var.get().strip())
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
        self.play_audio(record.input_audio_path)

    def play_audio(self, path: Path) -> None:
        if winsound is None:
            messagebox.showerror("音频听审工具", "当前 Python 环境不可用 winsound，无法直接播放 wav。")
            return
        if not path.exists():
            messagebox.showerror("音频听审工具", f"音频文件不存在：\n{path}")
            return
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        self.status_var.set(f"正在播放：{path.name}")

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


def resolve_manifest_path(path: Path) -> Path:
    candidate = path.resolve()
    if candidate.is_dir():
        candidate = candidate / "proxy_audio_export.json"
    if not candidate.exists():
        raise FileNotFoundError(f"找不到 proxy_audio_export 清单文件：{candidate}")
    return candidate


def coalesce_path(current: Path | None, raw_path: object) -> Path | None:
    if current is not None:
        return current
    if raw_path in {None, ""}:
        return None
    return Path(str(raw_path)).resolve()


def build_candidate_map(branch_label: str, record_payload: dict[str, Any]) -> dict[str, str | None]:
    if "student_proxy_audio_path" in record_payload or "teacher_proxy_audio_path" in record_payload:
        return {
            f"{branch_label}:teacher_proxy": record_payload.get("teacher_proxy_audio_path"),
            f"{branch_label}:student_proxy": record_payload.get("student_proxy_audio_path"),
        }
    return {
        branch_label: record_payload.get("proxy_audio_path"),
    }


def build_review_summary(
    records_by_id: dict[str, AuditRecord],
    review_state: dict[str, dict[str, Any]],
    manifest_paths: list[Path],
    session_notes: str,
) -> dict[str, Any]:
    aggregate: dict[str, dict[str, int]] = {}
    for field_id, _field_label in SCORING_FIELDS:
        counter = Counter()
        for record_id in records_by_id:
            selected = str(review_state.get(record_id, {}).get(field_id, "")).strip()
            if selected:
                counter[selected] += 1
        aggregate[field_id] = dict(sorted(counter.items()))
    validity_counter = Counter(
        validity_code_from_value(str(review_state.get(record_id, {}).get("valid_for_comparison", "yes")).strip())
        for record_id in records_by_id
    )
    completed_count = sum(1 for record_id in records_by_id if bool(review_state.get(record_id, {}).get("completed", False)))

    records_payload: list[dict[str, Any]] = []
    for record_id, record in records_by_id.items():
        review = dict(review_state.get(record_id, {}))
        records_payload.append(
            {
                "record_id": record_id,
                "input_audio_path": None if record.input_audio_path is None else record.input_audio_path.as_posix(),
                "audio_path": None if record.audio_path is None else record.audio_path.as_posix(),
                "candidate_labels": [candidate.label for candidate in record.candidates],
                "review": review,
            }
        )

    return {
        "manifest_paths": [path.as_posix() for path in manifest_paths],
        "record_count": len(records_by_id),
        "completed_count": completed_count,
        "session_notes": session_notes,
        "aggregate": {
            "by_field": aggregate,
            "valid_for_comparison": dict(sorted(validity_counter.items())),
        },
        "records": records_payload,
    }


def build_review_markdown(summary: dict[str, Any]) -> str:
    field_label_map = dict(SCORING_FIELDS)
    lines = [
        "# 音频听审结果",
        "",
        "## 概览",
        f"- 总记录数: {summary['record_count']}",
        f"- 已完成数: {summary['completed_count']}",
        f"- 清单文件: {summary['manifest_paths']}",
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
    lines.append("### 是否适合比较")
    for label, value in summary["aggregate"]["valid_for_comparison"].items():
        lines.append(f"- {validity_label_from_value(label)}: {value}")
    lines.extend(["", "## 会话备注", summary["session_notes"] or "（空）", "", "## 单条记录"])
    for record in summary["records"]:
        lines.append(f"### {record['record_id']}")
        lines.append(f"- 候选音频: {record['candidate_labels']}")
        review = record["review"]
        for field_id, _field_label in SCORING_FIELDS:
            lines.append(f"- {field_label_map[field_id]}: {review.get(field_id, '')}")
        lines.append(f"- 是否适合比较: {validity_label_from_value(str(review.get('valid_for_comparison', 'yes')))}")
        lines.append(f"- 是否完成: {review.get('completed', False)}")
        lines.append(f"- 备注: {review.get('notes', '')}")
        lines.append("")
    return "\n".join(lines)


def validity_label_from_value(value: str) -> str:
    normalized = value.strip()
    if normalized in VALIDITY_CODE_TO_LABEL:
        return VALIDITY_CODE_TO_LABEL[normalized]
    if normalized in VALIDITY_LABEL_TO_CODE:
        return normalized
    return VALIDITY_CODE_TO_LABEL["yes"]


def validity_code_from_value(value: str) -> str:
    normalized = value.strip()
    if normalized in VALIDITY_LABEL_TO_CODE:
        return VALIDITY_LABEL_TO_CODE[normalized]
    if normalized in VALIDITY_CODE_TO_LABEL:
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
    return parser


def launch_audio_audit_gui(
    bundle_paths: list[Path],
    output_dir: Path,
    auto_close_ms: int | None = None,
) -> None:
    root = tk.Tk()
    app = AudioAuditApp(
        root=root,
        manifest_paths=bundle_paths,
        output_dir=output_dir,
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
        auto_close_ms=args.auto_close_ms,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
