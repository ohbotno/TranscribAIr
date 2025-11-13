"""
Preview dialog for Excel rubric imports.
Shows parsed rubric data before final import.
"""
import customtkinter as ctk
from typing import Optional, Callable
from core.excel_import import ParsedRubricData
from core.rubric import Rubric


class ExcelPreviewDialog(ctk.CTkToplevel):
    """Dialog to preview and confirm Excel rubric import."""

    def __init__(self, parent, parsed_data: ParsedRubricData, on_confirm: Optional[Callable[[Rubric], None]] = None):
        super().__init__(parent)

        self.parsed_data = parsed_data
        self.on_confirm_callback = on_confirm
        self.confirmed = False

        # Window setup
        self.title("Preview Excel Import")
        self.geometry("800x700")
        self.transient(parent)
        self.grab_set()

        self._create_ui()

    def _create_ui(self):
        """Create preview dialog UI."""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Preview Rubric Import",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # Rubric metadata section
        metadata_frame = ctk.CTkFrame(container)
        metadata_frame.pack(fill="x", pady=(0, 10))

        # Rubric name (editable)
        name_row = ctk.CTkFrame(metadata_frame)
        name_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(name_row, text="Rubric Name:", font=ctk.CTkFont(weight="bold"), width=120, anchor="w").pack(side="left")
        self.name_entry = ctk.CTkEntry(name_row, width=400)
        self.name_entry.pack(side="left", padx=5)
        self.name_entry.insert(0, self.parsed_data.rubric_name)

        # Rubric description (editable)
        desc_row = ctk.CTkFrame(metadata_frame)
        desc_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(desc_row, text="Description:", font=ctk.CTkFont(weight="bold"), width=120, anchor="w").pack(side="left")
        self.desc_entry = ctk.CTkEntry(desc_row, width=400)
        self.desc_entry.pack(side="left", padx=5)
        self.desc_entry.insert(0, self.parsed_data.rubric_description)

        # Rubric type
        type_row = ctk.CTkFrame(metadata_frame)
        type_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(type_row, text="Rubric Type:", font=ctk.CTkFont(weight="bold"), width=120, anchor="w").pack(side="left")
        type_text = "Analytic (with performance levels)" if self.parsed_data.is_analytic else "Simple"
        ctk.CTkLabel(type_row, text=type_text, anchor="w").pack(side="left", padx=5)

        # Performance levels summary (if analytic)
        if self.parsed_data.is_analytic:
            levels_row = ctk.CTkFrame(metadata_frame)
            levels_row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(levels_row, text="Performance Levels:", font=ctk.CTkFont(weight="bold"), width=120, anchor="w").pack(side="left")
            levels_text = ", ".join(self.parsed_data.performance_level_names)
            ctk.CTkLabel(levels_row, text=levels_text, anchor="w", wraplength=500).pack(side="left", padx=5)

        # Criteria count
        count_row = ctk.CTkFrame(metadata_frame)
        count_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(count_row, text="Criteria Count:", font=ctk.CTkFont(weight="bold"), width=120, anchor="w").pack(side="left")
        ctk.CTkLabel(count_row, text=str(len(self.parsed_data.criteria_data)), anchor="w").pack(side="left", padx=5)

        # Criteria details section
        criteria_label = ctk.CTkLabel(
            container,
            text="Criteria Details",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        criteria_label.pack(pady=(10, 5))

        # Scrollable frame for criteria
        criteria_scroll = ctk.CTkScrollableFrame(container, height=350)
        criteria_scroll.pack(fill="both", expand=True, pady=5)

        # Display each criterion
        for idx, criterion in enumerate(self.parsed_data.criteria_data, 1):
            self._create_criterion_preview(criteria_scroll, idx, criterion)

        # Button frame
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Import",
            command=self._confirm_import,
            width=120,
            fg_color="green"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=120,
            fg_color="gray"
        ).pack(side="right", padx=5)

    def _create_criterion_preview(self, parent, index: int, criterion_data: dict):
        """Create a preview widget for a single criterion."""
        # Criterion container
        crit_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"))
        crit_frame.pack(fill="x", pady=5, padx=5)

        # Header row
        header_frame = ctk.CTkFrame(crit_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)

        # Criterion number and name
        name_text = f"{index}. {criterion_data['name']}"
        ctk.CTkLabel(
            header_frame,
            text=name_text,
            font=ctk.CTkFont(weight="bold", size=13),
            anchor="w"
        ).pack(side="left")

        # Weight
        weight_pct = criterion_data['weight'] * 100
        weight_text = f"Weight: {weight_pct:.0f}%"
        ctk.CTkLabel(
            header_frame,
            text=weight_text,
            font=ctk.CTkFont(size=11),
            anchor="e"
        ).pack(side="right", padx=5)

        # Content
        content_frame = ctk.CTkFrame(crit_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=(0, 5))

        if self.parsed_data.is_analytic and criterion_data['performance_levels']:
            # Show performance levels in a compact format
            for pl in criterion_data['performance_levels']:
                pl_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                pl_frame.pack(fill="x", pady=2)

                # Level name and range
                level_header = f"  • {pl['name']}"
                if pl['score_range']:
                    level_header += f" ({pl['score_range']})"
                level_header += ":"

                ctk.CTkLabel(
                    pl_frame,
                    text=level_header,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    anchor="w"
                ).pack(anchor="w")

                # Description
                desc_text = pl['description']
                if len(desc_text) > 100:
                    desc_text = desc_text[:97] + "..."

                ctk.CTkLabel(
                    pl_frame,
                    text=f"    {desc_text}",
                    font=ctk.CTkFont(size=10),
                    anchor="w",
                    wraplength=700,
                    text_color="gray"
                ).pack(anchor="w", padx=(10, 0))
        else:
            # Simple description
            desc_text = criterion_data['description']
            if desc_text:
                if len(desc_text) > 150:
                    desc_text = desc_text[:147] + "..."
                ctk.CTkLabel(
                    content_frame,
                    text=desc_text,
                    font=ctk.CTkFont(size=11),
                    anchor="w",
                    wraplength=700
                ).pack(anchor="w", pady=2)

    def _confirm_import(self):
        """Confirm and proceed with import."""
        # Update rubric name and description from editable fields
        self.parsed_data.rubric_name = self.name_entry.get().strip()
        self.parsed_data.rubric_description = self.desc_entry.get().strip()

        if not self.parsed_data.rubric_name:
            from tkinter import messagebox
            messagebox.showerror("Invalid Name", "Rubric name cannot be empty.")
            return

        self.confirmed = True

        # Build rubric object
        from core.rubric import RubricCriterion, PerformanceLevel
        criteria = []
        for crit_data in self.parsed_data.criteria_data:
            if self.parsed_data.is_analytic and crit_data['performance_levels']:
                # Create criterion with performance levels
                perf_levels = [
                    PerformanceLevel(
                        name=pl['name'],
                        score_range=pl['score_range'],
                        description=pl['description']
                    )
                    for pl in crit_data['performance_levels']
                ]
                criterion = RubricCriterion(
                    name=crit_data['name'],
                    weight=crit_data['weight'],
                    performance_levels=perf_levels
                )
            else:
                # Simple criterion
                criterion = RubricCriterion(
                    name=crit_data['name'],
                    description=crit_data['description'],
                    weight=crit_data['weight']
                )

            criteria.append(criterion)

        rubric = Rubric(
            name=self.parsed_data.rubric_name,
            description=self.parsed_data.rubric_description,
            criteria=criteria
        )

        if self.on_confirm_callback:
            self.on_confirm_callback(rubric)

        self.destroy()

    def _cancel(self):
        """Cancel import."""
        self.confirmed = False
        self.destroy()
