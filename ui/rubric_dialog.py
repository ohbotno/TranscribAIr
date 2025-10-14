"""
Rubric management dialog for creating and editing rubrics.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, List, Callable
from pathlib import Path

from core.rubric import Rubric, RubricCriterion, RubricManager


class RubricDialog(ctk.CTkToplevel):
    """Dialog for creating/editing rubrics."""

    def __init__(self, parent, rubric_manager: RubricManager, rubric: Optional[Rubric] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)

        self.rubric_manager = rubric_manager
        self.rubric = rubric
        self.on_save_callback = on_save
        self.criteria_frames = []

        # Window setup
        self.title("Edit Rubric" if rubric else "Create Rubric")
        self.geometry("700x600")
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

    def _add_criterion(self, criterion: Optional[RubricCriterion] = None):
        """Add a criterion input row."""
        frame = ctk.CTkFrame(self.criteria_scroll)
        frame.pack(fill="x", pady=5, padx=5)

        # Criterion name
        ctk.CTkLabel(frame, text="Name:", width=60).pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(frame, width=150)
        name_entry.pack(side="left", padx=5)

        # Description
        ctk.CTkLabel(frame, text="Description:", width=80).pack(side="left", padx=5)
        desc_entry = ctk.CTkEntry(frame, width=250)
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
            'weight': weight_entry
        })

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

        # Collect criteria
        criteria = []
        for i, cf in enumerate(self.criteria_frames):
            cname = cf['name'].get().strip()
            cdesc = cf['description'].get().strip()

            if not cname:
                messagebox.showerror("Error", f"Criterion {i+1} name is required")
                return

            try:
                cweight = float(cf['weight'].get())
            except ValueError:
                messagebox.showerror("Error", f"Criterion {i+1} weight must be a number")
                return

            criteria.append(RubricCriterion(cname, cdesc, cweight))

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

        # Create radio buttons for rubrics
        self.rubric_var = ctk.StringVar(value="")
        for name in rubric_names:
            rb = ctk.CTkRadioButton(
                self.rubric_listbox,
                text=name,
                variable=self.rubric_var,
                value=name
            )
            rb.pack(anchor="w", pady=5, padx=10)

    def _create_new_rubric(self):
        """Open dialog to create new rubric."""
        dialog = RubricDialog(self, self.rubric_manager, on_save=lambda r: self._load_rubrics())

    def _import_rubric(self):
        """Import rubric from file."""
        file_path = filedialog.askopenfilename(
            title="Import Rubric",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            rubric = self.rubric_manager.import_rubric(Path(file_path))
            if rubric:
                messagebox.showinfo("Success", f"Imported rubric '{rubric.name}'")
                self._load_rubrics()
            else:
                messagebox.showerror("Error", "Failed to import rubric")

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
