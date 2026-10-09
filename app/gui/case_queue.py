import tkinter as tk
from tkinter import ttk, messagebox


class AMLCaseQueueWindow:
    def __init__(self, root, api):
        self.root = root
        self.api = api

        self.root.title("AI BANK - AML CASE QUEUE")
        self.root.geometry("900x650")

        self.build_ui()
        self.refresh()

    def build_ui(self):
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=15, pady=12)

        ttk.Label(
            header,
            text="AML CASE QUEUE",
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")

        self.count_label = ttk.Label(header, text="")
        self.count_label.pack(side="right")

        columns = (
            "severity",
            "status",
            "account",
            "assigned_to",
            "opened_at",
        )

        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=22,
        )

        headings = {
            "severity": "Severity",
            "status": "Status",
            "account": "Account",
            "assigned_to": "Assigned To",
            "opened_at": "Opened",
        }

        widths = {
            "severity": 100,
            "status": 120,
            "account": 180,
            "assigned_to": 180,
            "opened_at": 180,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column])

        self.tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5,
        )

        self.tree.bind(
            "<Double-1>",
            self.open_selected_case,
        )

        footer = ttk.Frame(self.root)
        footer.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            footer,
            text="Double-click a case to open the investigation",
        ).pack(side="left")

        ttk.Button(
            footer,
            text="Refresh Now",
            command=self.refresh,
        ).pack(side="right")

    def refresh(self):
        try:
            cases = self.api.investigations()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for case in cases:
                self.tree.insert(
                    "",
                    "end",
                    iid=case["investigation_id"],
                    values=(
                        case["alert_id"],
                        case["status"],
                        case["assigned_to"] or "-",
                        case["opened_at"],
                        case["investigation_id"],
                    ),
                )

            self.count_label.config(
                text=f"Active Cases: {len(cases)}"
            )

        except RuntimeError as e:
            messagebox.showerror(
                "AML Queue Error",
                str(e),
            )

        finally:
            self.root.after(2000, self.refresh)

    def open_selected_case(self, event=None):
        selection = self.tree.selection()

        if not selection:
            return

        investigation_id = selection[0]

        messagebox.showinfo(
            "Selected Investigation",
            f"Investigation ID:\n{investigation_id}\n\n"
            "The detailed investigation screen will be connected next.",
        )