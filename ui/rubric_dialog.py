"""
Rubric management dialog for creating and editing rubrics.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, List, Callable
from pathlib import Path

from core.rubric import Rubric, RubricCriterion, RubricManager, PerformanceLevel


class RubricDialog(ctk.CTkToplevel):
    """Dialog for creating/editing rubrics."""

    def __init__(self, parent, rubric_manager: RubricManager, rubric: Optional[Rubric] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)

        self.rubric_manager = rubric_manager
        self.rubric = rubric
        self.on_save_callback = on_save
        self.criteria_frames = []

        # Detect mode from existing rubric
        self.is_detailed_mode = False
        if rubric and rubric.criteria:
            # Check if any criterion has performance levels
            self.is_detailed_mode = any(c.performance_levels for c in rubric.criteria)

        # Window setup
        self.title("Edit Rubric" if rubric else "Create Rubric")
        self.geometry("900x700")  # Increased width for detailed mode
        self.transient(parent)
        self.grab_set()

        self._create_ui()

        # Load rubric data if editing
        if rubric:
            self._load_rubric()

    def _create_ui(self):
        """Create dialog UI."""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Mode selector (only show if creating new rubric)
        if not self.rubric:
            mode_frame = ctk.CTkFrame(container)
            mode_frame.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(mode_frame, text="Rubric Type:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5))

            self.mode_selector = ctk.CTkSegmentedButton(
                mode_frame,
                values=["Simple", "Detailed (with Performance Levels)"],
                command=self._on_mode_change,
                width=400
            )
            self.mode_selector.pack(side="left", padx=5)
            self.mode_selector.set("Simple" if not self.is_detailed_mode else "Detailed (with Performance Levels)")

        # Rubric name
        name_frame = ctk.CTkFrame(container)
        name_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(name_frame, text="Rubric Name:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5))
        self.name_entry = ctk.CTkEntry(name_frame, width=300)
        self.name_entry.pack(side="left", padx=5)

        # Description
        desc_frame = ctk.CTkFrame(container)
        desc_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(desc_frame, text="Description:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5))
        self.desc_entry = ctk.CTkEntry(desc_frame, width=400)
        self.desc_entry.pack(side="left", padx=5)

        # Criteria section
        criteria_header = ctk.CTkFrame(container)
        criteria_header.pack(fill="x", pady=(10, 5))

        ctk.CTkLabel(
            criteria_header,
            text="Criteria",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            criteria_header,
            text="+ Add Criterion",
            command=self._add_criterion,
            width=120
        ).pack(side="right", padx=10)

        # Scrollable frame for criteria
        self.criteria_scroll = ctk.CTkScrollableFrame(container, height=300)
        self.criteria_scroll.pack(fill="both", expand=True, pady=5)

        # Add initial criterion if creating new
        if not self.rubric:
            self._add_criterion()

        # Button frame
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_rubric,
            width=120,
            fg_color="green"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=120,
            fg_color="gray"
        ).pack(side="right", padx=5)

    def _on_mode_change(self, value):
        """Handle mode change."""
        self.is_detailed_mode = (value == "Detailed (with Performance Levels)")
        # Clear and rebuild criteria section
        self.criteria_frames = []
        for widget in self.criteria_scroll.winfo_children():
            widget.destroy()
        # Add initial criterion
        self._add_criterion()

    def _add_criterion(self, criterion: Optional[RubricCriterion] = None):
        """Add a criterion input section."""
        if self.is_detailed_mode:
            self._add_detailed_criterion(criterion)
        else:
            self._add_simple_criterion(criterion)

    def _add_simple_criterion(self, criterion: Optional[RubricCriterion] = None):
        """Add a simple criterion input row."""
        frame = ctk.CTkFrame(self.criteria_scroll)
        frame.pack(fill="x", pady=5, padx=5)

        # Criterion name
        ctk.CTkLabel(frame, text="Name:", width=60).pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(frame, width=150)
        name_entry.pack(side="left", padx=5)

        # Description
        ctk.CTkLabel(frame, text="Description:", width=80).pack(side="left", padx=5)
        desc_entry = ctk.CTkEntry(frame, width=300)
        desc_entry.pack(side="left", padx=5)

        # Weight
        ctk.CTkLabel(frame, text="Weight:", width=60).pack(side="left", padx=5)
        weight_entry = ctk.CTkEntry(frame, width=50)
        weight_entry.pack(side="left", padx=5)
        weight_entry.insert(0, "1.0")

        # Remove button
        remove_btn = ctk.CTkButton(
            frame,
            text="✕",
            command=lambda: self._remove_criterion(frame),
            width=30,
            fg_color="red"
        )
        remove_btn.pack(side="left", padx=5)

        # Load data if editing
        if criterion:
            name_entry.insert(0, criterion.name)
            desc_entry.insert(0, criterion.description)
            weight_entry.delete(0, "end")
            weight_entry.insert(0, str(criterion.weight))

        self.criteria_frames.append({
            'frame': frame,
            'name': name_entry,
            'description': desc_entry,
            'weight': weight_entry,
            'performance_levels': []
        })

    def _add_detailed_criterion(self, criterion: Optional[RubricCriterion] = None):
        """Add a detailed criterion with performance levels."""
        # Main criterion container
        outer_frame = ctk.CTkFrame(self.criteria_scroll, fg_color=("gray85", "gray25"))
        outer_frame.pack(fill="x", pady=10, padx=5)

        # Header row (name and weight)
        header_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        # Criterion name
        ctk.CTkLabel(header_frame, text="Criterion Name:", width=120).pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(header_frame, width=200)
        name_entry.pack(side="left", padx=5)

        # Weight
        ctk.CTkLabel(header_frame, text="Weight (%):", width=80).pack(side="left", padx=(20, 5))
        weight_entry = ctk.CTkEntry(header_frame, width=60)
        weight_entry.pack(side="left", padx=5)
        weight_entry.insert(0, "5")  # Default to 5%

        # Remove criterion button
        remove_btn = ctk.CTkButton(
            header_frame,
            text="Remove Criterion",
            command=lambda: self._remove_criterion(outer_frame),
            width=120,
            fg_color="red"
        )
        remove_btn.pack(side="right", padx=5)

        # Performance levels section
        pl_section = ctk.CTkFrame(outer_frame, fg_color="transparent")
        pl_section.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Performance levels header
        pl_header = ctk.CTkFrame(pl_section, fg_color="transparent")
        pl_header.pack(fill="x", pady=5)

        ctk.CTkLabel(pl_header, text="Performance Levels:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(
            pl_header,
            text="+ Add Level",
            command=lambda: self._add_performance_level(pl_container, None),
            width=100
        ).pack(side="right")

        # Container for performance level entries
        pl_container = ctk.CTkFrame(pl_section, fg_color="transparent")
        pl_container.pack(fill="both", expand=True)

        # Load data if editing
        performance_levels_data = []
        if criterion:
            name_entry.insert(0, criterion.name)
            # Weight as percentage
            weight_pct = criterion.weight * 100
            weight_entry.delete(0, "end")
            weight_entry.insert(0, str(int(weight_pct)))

            # Add performance levels if they exist
            if criterion.performance_levels:
                for pl in criterion.performance_levels:
                    self._add_performance_level(pl_container, pl)
                    performance_levels_data.append(pl)
            else:
                # Add one empty performance level
                self._add_performance_level(pl_container, None)
        else:
            # Add one empty performance level for new criterion
            self._add_performance_level(pl_container, None)

        self.criteria_frames.append({
            'frame': outer_frame,
            'name': name_entry,
            'description': None,  # Not used in detailed mode
            'weight': weight_entry,
            'performance_levels': pl_container
        })

    def _add_performance_level(self, parent, performance_level: Optional[PerformanceLevel] = None):
        """Add a performance level entry row."""
        pl_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"))
        pl_frame.pack(fill="x", pady=3, padx=5)

        # Level name
        ctk.CTkLabel(pl_frame, text="Level:", width=50).pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(pl_frame, width=120)
        name_entry.pack(side="left", padx=5)

        # Score range
        ctk.CTkLabel(pl_frame, text="Range:", width=50).pack(side="left", padx=5)
        range_entry = ctk.CTkEntry(pl_frame, width=80)
        range_entry.pack(side="left", padx=5)

        # Description
        ctk.CTkLabel(pl_frame, text="Description:", width=80).pack(side="left", padx=5)
        desc_entry = ctk.CTkEntry(pl_frame, width=300)
        desc_entry.pack(side="left", padx=5)

        # Remove button
        ctk.CTkButton(
            pl_frame,
            text="✕",
            command=lambda: pl_frame.destroy(),
            width=30,
            fg_color="red"
        ).pack(side="left", padx=5)

        # Load data if provided
        if performance_level:
            name_entry.insert(0, performance_level.name)
            range_entry.insert(0, performance_level.score_range)
            desc_entry.insert(0, performance_level.description)

        # Store references
        pl_frame.name_entry = name_entry
        pl_frame.range_entry = range_entry
        pl_frame.desc_entry = desc_entry

    def _remove_criterion(self, frame):
        """Remove a criterion row."""
        # Find and remove from list
        self.criteria_frames = [c for c in self.criteria_frames if c['frame'] != frame]
        frame.destroy()

    def _load_rubric(self):
        """Load rubric data into form."""
        if not self.rubric:
            return

        self.name_entry.insert(0, self.rubric.name)
        self.desc_entry.insert(0, self.rubric.description)

        # Load criteria
        for criterion in self.rubric.criteria:
            self._add_criterion(criterion)

    def _save_rubric(self):
        """Save rubric."""
        # Validate
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Rubric name is required")
            return

        if not self.criteria_frames:
            messagebox.showerror("Error", "At least one criterion is required")
            return

        # Collect criteria based on mode
        criteria = []
        for i, cf in enumerate(self.criteria_frames):
            cname = cf['name'].get().strip()

            if not cname:
                messagebox.showerror("Error", f"Criterion {i+1} name is required")
                return

            # Parse weight
            try:
                if self.is_detailed_mode:
                    # Weight is entered as percentage
                    weight_pct = float(cf['weight'].get())
                    cweight = weight_pct / 100.0
                else:
                    # Weight is entered as decimal
                    cweight = float(cf['weight'].get())
            except ValueError:
                messagebox.showerror("Error", f"Criterion {i+1} weight must be a number")
                return

            if self.is_detailed_mode:
                # Collect performance levels
                pl_container = cf['performance_levels']
                performance_levels = []

                for pl_widget in pl_container.winfo_children():
                    pl_name = pl_widget.name_entry.get().strip()
                    pl_range = pl_widget.range_entry.get().strip()
                    pl_desc = pl_widget.desc_entry.get().strip()

                    if pl_name or pl_desc:  # Only add if at least name or desc is provided
                        if not pl_name:
                            messagebox.showerror("Error", f"Criterion {i+1}: Performance level name is required")
                            return
                        if not pl_desc:
                            messagebox.showerror("Error", f"Criterion {i+1}: Performance level '{pl_name}' description is required")
                            return

                        performance_levels.append(PerformanceLevel(
                            name=pl_name,
                            score_range=pl_range,
                            description=pl_desc
                        ))

                if not performance_levels:
                    messagebox.showerror("Error", f"Criterion {i+1} '{cname}' must have at least one performance level")
                    return

                criterion = RubricCriterion(
                    name=cname,
                    weight=cweight,
                    performance_levels=performance_levels
                )
            else:
                # Simple criterion
                cdesc = cf['description'].get().strip()
                criterion = RubricCriterion(
                    name=cname,
                    description=cdesc,
                    weight=cweight
                )

            criteria.append(criterion)

        # Create/update rubric
        rubric = Rubric(
            name=name,
            description=self.desc_entry.get().strip(),
            criteria=criteria
        )

        # Save
        if self.rubric_manager.save_rubric(rubric):
            messagebox.showinfo("Success", "Rubric saved successfully")
            if self.on_save_callback:
                self.on_save_callback(rubric)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save rubric")


class RubricSelectorDialog(ctk.CTkToplevel):
    """Dialog for selecting a rubric."""

    def __init__(self, parent, rubric_manager: RubricManager, on_select: Callable):
        super().__init__(parent)

        self.rubric_manager = rubric_manager
        self.on_select_callback = on_select
        self.selected_rubric = None

        # Create StringVar once and reuse it
        self.rubric_var = ctk.StringVar(value="")

        # Window setup
        self.title("Select Rubric")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        self._create_ui()
        self._load_rubrics()

    def _create_ui(self):
        """Create dialog UI."""
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header = ctk.CTkFrame(container)
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="Select a Rubric",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            header,
            text="New Rubric",
            command=self._create_new_rubric,
            width=100
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            header,
            text="Import",
            command=self._import_rubric,
            width=100
        ).pack(side="right", padx=5)

        # Rubric list
        self.rubric_listbox = ctk.CTkScrollableFrame(container)
        self.rubric_listbox.pack(fill="both", expand=True, pady=5)

        # Button frame
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Select",
            command=self._select_rubric,
            width=120,
            fg_color="green"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Edit",
            command=self._edit_rubric,
            width=120
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Delete",
            command=self._delete_rubric,
            width=120,
            fg_color="red"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=120,
            fg_color="gray"
        ).pack(side="right", padx=5)

    def _load_rubrics(self):
        """Load and display available rubrics."""
        # Save current selection
        current_selection = self.rubric_var.get()

        # Clear existing
        for widget in self.rubric_listbox.winfo_children():
            widget.destroy()

        rubric_names = self.rubric_manager.list_rubrics()

        if not rubric_names:
            ctk.CTkLabel(
                self.rubric_listbox,
                text="No rubrics available. Create a new one!",
                text_color="gray"
            ).pack(pady=20)
            return

        # Create radio buttons for rubrics (reuse existing rubric_var)
        for name in rubric_names:
            rb = ctk.CTkRadioButton(
                self.rubric_listbox,
                text=name,
                variable=self.rubric_var,
                value=name
            )
            rb.pack(anchor="w", pady=5, padx=10)

        # Restore selection if the rubric still exists
        if current_selection and current_selection in rubric_names:
            self.rubric_var.set(current_selection)

    def _create_new_rubric(self):
        """Open dialog to create new rubric."""
        dialog = RubricDialog(self, self.rubric_manager, on_save=lambda r: self._load_rubrics())

    def _import_rubric(self):
        """Import rubric from file (JSON or Excel)."""
        file_path = filedialog.askopenfilename(
            title="Import Rubric",
            filetypes=[
                ("Rubric files", "*.json;*.xlsx"),
                ("JSON files", "*.json"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        path = Path(file_path)

        # Handle Excel import
        if path.suffix.lower() in ['.xlsx', '.xls']:
            from core.excel_import import ExcelRubricImporter
            from ui.excel_preview_dialog import ExcelPreviewDialog

            # Check if openpyxl is available
            if not ExcelRubricImporter.is_available():
                # Offer to install openpyxl
                if messagebox.askyesno(
                    "Install Required Package",
                    "Excel import requires the 'openpyxl' package.\n\n"
                    "Would you like to install it now?\n\n"
                    "This will take a few moments.",
                    icon='question'
                ):
                    # Show installing message
                    progress_window = ctk.CTkToplevel(self)
                    progress_window.title("Installing Package")
                    progress_window.geometry("400x150")
                    progress_window.transient(self)
                    progress_window.grab_set()

                    ctk.CTkLabel(
                        progress_window,
                        text="Installing openpyxl...\n\nThis may take a few moments.",
                        font=ctk.CTkFont(size=14)
                    ).pack(expand=True, pady=20)

                    progress_bar = ctk.CTkProgressBar(progress_window, mode="indeterminate")
                    progress_bar.pack(pady=10, padx=20, fill="x")
                    progress_bar.start()

                    progress_window.update()

                    # Install in background thread to keep UI responsive
                    import threading

                    def install_package():
                        from install_openpyxl import OpenpyxlInstaller
                        installer = OpenpyxlInstaller()
                        success = installer.install()

                        # Close progress window and show result
                        progress_window.after(0, lambda: self._handle_install_result(success, progress_window, path))

                    thread = threading.Thread(target=install_package, daemon=True)
                    thread.start()
                else:
                    return

            # Continue with import if openpyxl is available
            if ExcelRubricImporter.is_available():
                self._do_excel_import(path)

        # Handle JSON import
        elif path.suffix.lower() == '.json':
            rubric = self.rubric_manager.import_rubric(path)
            if rubric:
                messagebox.showinfo("Success", f"Imported rubric '{rubric.name}'")
                self._load_rubrics()
            else:
                messagebox.showerror("Error", "Failed to import rubric")
        else:
            messagebox.showerror("Error", "Unsupported file format. Use .json or .xlsx files.")

    def _handle_install_result(self, success: bool, progress_window, file_path: Path):
        """Handle the result of openpyxl installation."""
        progress_window.destroy()

        if success:
            messagebox.showinfo(
                "Installation Complete",
                "openpyxl has been installed successfully!\n\n"
                "Proceeding with Excel import..."
            )
            # Now import the Excel file
            self._do_excel_import(file_path)
        else:
            messagebox.showerror(
                "Installation Failed",
                "Failed to install openpyxl.\n\n"
                "Please install it manually:\n"
                "pip install openpyxl\n\n"
                "Or check your internet connection and try again."
            )

    def _do_excel_import(self, file_path: Path):
        """Perform Excel import after ensuring openpyxl is available."""
        from core.excel_import import ExcelRubricImporter
        from ui.excel_preview_dialog import ExcelPreviewDialog

        # Parse Excel file
        parsed_data = ExcelRubricImporter.parse_excel(file_path)
        if not parsed_data:
            messagebox.showerror("Error", "Failed to parse Excel file")
            return

        # Show preview dialog
        def on_confirm(rubric: Rubric):
            if self.rubric_manager.save_rubric(rubric):
                messagebox.showinfo("Success", f"Imported rubric '{rubric.name}'")
                self._load_rubrics()
            else:
                messagebox.showerror("Error", "Failed to save imported rubric")

        preview_dialog = ExcelPreviewDialog(self, parsed_data, on_confirm=on_confirm)

    def _edit_rubric(self):
        """Edit selected rubric."""
        selected_name = self.rubric_var.get()
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a rubric to edit")
            return

        rubric = self.rubric_manager.load_rubric(selected_name)
        if rubric:
            dialog = RubricDialog(self, self.rubric_manager, rubric, on_save=lambda r: self._load_rubrics())

    def _delete_rubric(self):
        """Delete selected rubric."""
        selected_name = self.rubric_var.get()
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a rubric to delete")
            return

        if messagebox.askyesno("Confirm", f"Delete rubric '{selected_name}'?"):
            if self.rubric_manager.delete_rubric(selected_name):
                messagebox.showinfo("Success", "Rubric deleted")
                self._load_rubrics()
            else:
                messagebox.showerror("Error", "Failed to delete rubric")

    def _select_rubric(self):
        """Select rubric and close dialog."""
        selected_name = self.rubric_var.get()

        if not selected_name:
            messagebox.showwarning("Warning", "Please select a rubric")
            return

        rubric = self.rubric_manager.load_rubric(selected_name)

        if rubric:
            if self.on_select_callback:
                self.on_select_callback(rubric)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to load rubric")
