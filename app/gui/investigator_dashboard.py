import tkinter as tk
from tkinter import ttk, messagebox


class InvestigatorDashboard:
    """Standalone showcase GUI for the AML human-investigation layer."""

    def __init__(self, root, api):
        self.root = root
        self.api = api
        self.investigation_id = None
        self.case = None
        self.last_signature = None
        self.refresh_job = None

        self.root.title("AI BANK - AML INVESTIGATOR")
        self.root.geometry("1250x900")
        self.root.minsize(1050, 750)

        self.refresh()

    def refresh(self):
        try:
            investigations = self.api.investigations()

            if not investigations:
                self.investigation_id = None
                self.case = None
                self.last_signature = None
                self.show_waiting()
            else:
                investigation_id = investigations[0]["investigation_id"]

                if investigation_id != self.investigation_id:
                    self.investigation_id = investigation_id
                    self.last_signature = None

                case = self.api.investigation_case(self.investigation_id)
                signature = repr(case)

                if signature != self.last_signature:
                    self.case = case
                    self.last_signature = signature
                    self.build()

        except RuntimeError as e:
            self.show_error(str(e))

        self.refresh_job = self.root.after(2000, self.refresh)

    def refresh_now(self):
        if self.refresh_job is not None:
            try:
                self.root.after_cancel(self.refresh_job)
            except tk.TclError:
                pass
        self.last_signature = None
        self.refresh()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_waiting(self):
        self.clear()
        frame = ttk.Frame(self.root, padding=40)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="AML INVESTIGATOR",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(140, 15))

        ttk.Label(
            frame,
            text="Waiting for a new AML investigation...",
            font=("Segoe UI", 13),
        ).pack()

        ttk.Label(
            frame,
            text="Create an AML alert from the Send Money window.",
            font=("Segoe UI", 10),
        ).pack(pady=8)

    def show_error(self, message):
        self.clear()
        frame = ttk.Frame(self.root, padding=30)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="AML INVESTIGATOR",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=30)

        ttk.Label(
            frame,
            text=message,
            wraplength=900,
            justify="left",
        ).pack()

    def section(self, parent, title):
        box = ttk.LabelFrame(parent, text=title, padding=10)
        box.pack(fill="x", padx=12, pady=6)
        return box

    def label(self, parent, text, font=None):
        widget = ttk.Label(
            parent,
            text=text,
            font=font or ("Segoe UI", 10),
            wraplength=1100,
            justify="left",
        )
        widget.pack(anchor="w", pady=2)
        return widget

    def build(self):
        self.clear()

        case = self.case
        investigation = case["investigation"]
        alert = case["alert"]
        account = case["account"]
        profile = case["aml_profile"]
        status = investigation["status"]

        agent = case.get("agent_analysis") or {}
        analysis = agent.get("analysis") or {}
        recommendation = agent.get("recommendation") or case.get(
            "recommendation", {}
        )

        if status == "OPEN":
            self.build_preview(
                account,
                profile,
                alert,
                recommendation,
            )
            return

        behavior = case.get("behavior", {})
        findings = analysis.get("findings", [])
        policy = agent.get("policy_evidence", [])
        critic = agent.get("critic") or {}

        self.build_detail(
            account,
            profile,
            alert,
            behavior,
            findings,
            policy,
            critic,
            recommendation,
        )

    def build_preview(
        self,
        account,
        profile,
        alert,
        recommendation,
    ):
        body = ttk.Frame(self.root, padding=12)
        body.pack(fill="both", expand=True)

        customer = self.section(body, "CUSTOMER")
        self.label(
            customer,
            f"{account['customer_name']}    "
            f"Account: {account['account_id']}    "
            f"Risk: {profile['risk_category']}",
        )

        alert_box = self.section(body, "ALERT")
        self.label(
            alert_box,
            f"{alert['rule_code']}    {alert['severity']}",
            ("Segoe UI", 14, "bold"),
        )
        self.label(
            alert_box,
            f"{alert['transaction_count']} transactions | "
            f"₹{float(alert['combined_amount']):,.2f} | 60 minutes",
        )

        rec_box = self.section(body, "AI RECOMMENDATION")
        self.label(
            rec_box,
            recommendation.get("action", "N/A"),
            ("Segoe UI", 13, "bold"),
        )
        self.label(
            rec_box,
            recommendation.get("rationale", "N/A"),
        )

        review = self.section(body, "HUMAN REVIEW")
        self.label(
            review,
            "AI analysis is ready. Human investigator review is required.",
        )

        ttk.Button(
            review,
            text="START REVIEW",
            command=self.start_review,
        ).pack(anchor="w", pady=(8, 2))

    def build_detail(
        self,
        account,
        profile,
        alert,
        behavior,
        findings,
        policy,
        critic,
        recommendation,
    ):
        canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=canvas.yview,
        )
        content = ttk.Frame(canvas, padding=(0, 0, 12, 20))

        window_id = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw",
        )

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                window_id,
                width=e.width,
            ),
        )

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        customer = self.section(content, "CUSTOMER")
        self.label(
            customer,
            f"{account['customer_name']}    "
            f"Account: {account['account_id']}    "
            f"Risk: {profile['risk_category']}",
            ("Segoe UI", 11, "bold"),
        )

        alert_box = self.section(content, "ALERT")
        self.label(
            alert_box,
            f"{alert['rule_code']}    {alert['severity']}",
            ("Segoe UI", 13, "bold"),
        )
        self.label(
            alert_box,
            f"{alert['transaction_count']} transactions | "
            f"₹{float(alert['combined_amount']):,.2f} | 60 minutes",
        )
        self.label(alert_box, f"Reason: {alert['reason']}")

        behavior_box = self.section(content, "BEHAVIOR OVER TIME")
        monthly = behavior.get("monthly", [])

        if monthly:
            for item in monthly:
                count = int(item.get("transaction_count", 0))
                bar = "█" * min(max(count, 1), 40)
                self.label(
                    behavior_box,
                    f"{item['month']}   {bar}   "
                    f"{count} tx | Outgoing "
                    f"₹{float(item['outgoing']):,.2f}",
                )
        else:
            self.label(
                behavior_box,
                "No monthly behavior data available.",
            )

        finding_box = self.section(content, "AI FINDINGS")

        if findings:
            for finding in findings:
                severity = finding.get("severity", "N/A")
                marker = "🔴" if severity == "HIGH" else "🟠"

                self.label(
                    finding_box,
                    f"{marker} {finding.get('code', 'UNKNOWN')}    "
                    f"{severity}",
                    ("Segoe UI", 10, "bold"),
                )
                self.label(
                    finding_box,
                    finding.get("description", ""),
                )

                for item in finding.get("evidence", []):
                    self.label(finding_box, f"  • {item}")
        else:
            self.label(
                finding_box,
                "No AI findings available.",
            )

        bottom = ttk.Frame(content)
        bottom.pack(fill="x", padx=12, pady=6)

        policy_box = ttk.LabelFrame(
            bottom,
            text="POLICY",
            padding=10,
        )
        policy_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5),
        )

        if policy:
            for item in policy:
                self.label(
                    policy_box,
                    f"{item.get('policy_id', 'N/A')} - "
                    f"{item.get('title', 'N/A')}",
                    ("Segoe UI", 10, "bold"),
                )
                self.label(policy_box, item.get("text", ""))
        else:
            self.label(policy_box, "No policy evidence.")

        critic_box = ttk.LabelFrame(
            bottom,
            text="CRITIC / GUARDRAIL",
            padding=10,
        )
        critic_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0),
        )

        passed = critic.get("passed", False)
        self.label(
            critic_box,
            "✓ PASSED" if passed else "✗ FAILED",
            ("Segoe UI", 12, "bold"),
        )

        issues = critic.get("issues", [])
        if issues:
            for issue in issues:
                self.label(critic_box, f"• {issue}")
        else:
            self.label(
                critic_box,
                "Investigation output passed governance checks.",
            )

        rec_box = self.section(content, "RECOMMENDATION")
        self.label(
            rec_box,
            recommendation.get("action", "N/A"),
            ("Segoe UI", 13, "bold"),
        )
        self.label(
            rec_box,
            recommendation.get("rationale", "N/A"),
        )
        self.label(
            rec_box,
            "Human approval required: "
            f"{recommendation.get('requires_human_approval', 'N/A')}",
        )

        review_box = self.section(content, "HUMAN DECISION")

        ttk.Button(
            review_box,
            text="ESCALATE",
            command=lambda: self.complete_with(
                "Escalated for further review."
            ),
        ).pack(side="left", padx=5)

        ttk.Button(
            review_box,
            text="REQUEST INFO",
            command=lambda: self.complete_with(
                "Additional information requested."
            ),
        ).pack(side="left", padx=5)

        ttk.Button(
            review_box,
            text="CLOSE",
            command=lambda: self.complete_with(
                "Investigation closed after human review."
            ),
        ).pack(side="left", padx=5)

    def start_review(self):
        try:
            self.api.update_investigation_status(
                self.investigation_id,
                "IN_PROGRESS",
            )
            self.refresh_now()
        except RuntimeError as e:
            messagebox.showerror(
                "Unable to start review",
                str(e),
            )

    def complete_with(self, conclusion):
        if not messagebox.askyesno(
            "Complete Investigation",
            f"{conclusion}\n\nComplete this investigation?",
        ):
            return

        try:
            self.api.update_investigation_status(
                self.investigation_id,
                "COMPLETED",
                conclusion,
            )
            messagebox.showinfo(
                "Investigation Complete",
                "Human investigation decision recorded.",
            )
            self.refresh_now()
        except RuntimeError as e:
            messagebox.showerror(
                "Unable to complete investigation",
                str(e),
            )
