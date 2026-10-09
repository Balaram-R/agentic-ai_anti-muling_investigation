import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading


class InvestigationWindow:
    def __init__(self, root, api, investigation_id=None):
        self.root = root
        self.api = api
        self.investigation_id = investigation_id
        self.analysis_started = False
        self.last_case_signature = None
        self.refresh_job = None
        

        self.page_canvas = None
        self.page_scrollbar = None
        self.waiting_frame = None

        root.title("AI BANK - AML INVESTIGATION")
        root.geometry("1350x900")

        self.status = tk.StringVar(value="Loading investigation...")
        self.load_case()

    def schedule_refresh(self):
        if self.refresh_job is not None:
            try:
                self.root.after_cancel(self.refresh_job)
            except tk.TclError:
                pass

        self.refresh_job = self.root.after(2000, self.load_case)

    def set_investigation(self, investigation_id):
        self.investigation_id = investigation_id
        self.analysis_started = False
        self.last_case_signature = None
        self.load_case()

    def load_case(self):
        try:
            if self.investigation_id is None:
                alerts = self.api.open_alerts()

                if not alerts:
                    self.show_waiting_screen()
                    self.schedule_refresh()
                    return

                alert_id = alerts[0]["alert_id"]

                try:
                    investigation = self.api.investigation_by_alert(
                        alert_id
                    )
                except RuntimeError as e:
                    if "not found" in str(e).lower():
                        self.show_waiting_screen()
                        self.schedule_refresh()
                        return
                    raise

                self.investigation_id = investigation[
                    "investigation_id"
                ]

                self.analysis_started = False
                self.last_case_signature = None

            case = self.api.investigation_case(
                self.investigation_id
            )

            signature = repr(case)

            if signature != self.last_case_signature:
                self.case = case
                self.last_case_signature = signature
                self.build_ui()

            if (
                    case.get("agent_analysis") is None
                    and not self.analysis_started
                ):
                self.analysis_started = True

                self.status.set(
                    "Investigation loaded. "
                    "AI agents are analyzing evidence..."
                )

                def run_ai():
                    try:
                        self.api.run_investigation(
                            self.investigation_id
                        )

                        self.root.after(
                            0,
                            self.load_case,
                        )

                    except RuntimeError as e:
                        self.root.after(
                            0,
                            lambda: self._ai_run_failed(
                                str(e)
                            ),
                        )

                threading.Thread(
                    target=run_ai,
                    daemon=True,
                ).start()

            self.schedule_refresh()

        except RuntimeError as e:
            self.status.set(str(e))
            self.schedule_refresh()


    def _ai_run_failed(self, error):
        self.analysis_started = False
        self.status.set(
            f"AI investigation failed: {error}"
        )

    def add_text(self, parent, text, row, column=0, columnspan=1):
        label = ttk.Label(
            parent,
            text=text,
            wraplength=500,
            justify="left",
        )
        label.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            padx=10,
            pady=4,
            sticky="w",
        )
        return label

    def show_waiting_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.page_canvas = None
        self.page_scrollbar = None

        self.waiting_frame = ttk.LabelFrame(
            self.root,
            text="Investigation",
        )
        self.waiting_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(
            self.waiting_frame,
            text="Waiting for an active AML investigation...",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(120, 10))

        ttk.Label(
            self.waiting_frame,
            text="Automatically checking for new AML cases...",
            font=("Segoe UI", 11),
        ).pack()

        self.status.set("Monitoring AML investigations...")

    def build_ui(self):
        case = self.case

        if self.waiting_frame is not None:
            self.waiting_frame.destroy()
            self.waiting_frame = None

        # Remove previous investigation UI before rebuilding
        if self.page_canvas is not None:
            self.page_canvas.destroy()

        if self.page_scrollbar is not None:
            self.page_scrollbar.destroy()

    # ---------------------------------------------------------
        # SCROLLABLE PAGE
        # ---------------------------------------------------------

        self.page_canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
        )

        self.page_scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.page_canvas.yview,
        )

        content = ttk.Frame(self.page_canvas)

        content_window = self.page_canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw",
        )

        def configure_scroll_region(event=None):
            self.page_canvas.configure(
                scrollregion=self.page_canvas.bbox("all")
            )

        def configure_content_width(event):
            self.page_canvas.itemconfigure(
                content_window,
                width=event.width,
            )

        content.bind(
            "<Configure>",
            configure_scroll_region,
        )

        self.page_canvas.bind(
            "<Configure>",
            configure_content_width,
        )

        self.page_canvas.configure(
            yscrollcommand=self.page_scrollbar.set
        )

        self.page_canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        def mousewheel(event):
            self.page_canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units",
            )

        self.page_canvas.bind_all(
            "<MouseWheel>",
            mousewheel,
        )

        self.page_scrollbar.pack(
            side="right",
            fill="y",
        )

        self.content = content

        investigation = case["investigation"]
        alert = case["alert"]
        account = case["account"]
        profile = case["aml_profile"]

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

        header = ttk.LabelFrame(
            self.content,
            text="Investigation"
        )
        header.pack(
            fill="x",
            padx=12,
            pady=8,
        )

        self.add_text(
            header,
            f"Investigation ID: {investigation['investigation_id']}",
            0,
        )

        self.add_text(
            header,
            f"Assigned To: {investigation['assigned_to']}",
            1,
        )

        self.add_text(
            header,
            f"Status: {investigation['status']}",
            2,
        )

        # ---------------------------------------------------------
        # ALERT + CUSTOMER
        # ---------------------------------------------------------

        top = ttk.Frame(self.content)
        top.pack(
            fill="x",
            padx=12,
            pady=4,
        )

        alert_box = ttk.LabelFrame(
            top,
            text="AML Alert",
        )
        alert_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 6),
        )

        self.add_text(
            alert_box,
            f"Rule: {alert['rule_code']}",
            0,
        )

        self.add_text(
            alert_box,
            f"Severity: {alert['severity']}",
            1,
        )

        self.add_text(
            alert_box,
            f"Status: {alert['status']}",
            2,
        )

        self.add_text(
            alert_box,
            f"Transactions: {alert['transaction_count']}",
            3,
        )

        self.add_text(
            alert_box,
            f"Combined Amount: INR {float(alert['combined_amount']):,.2f}",
            4,
        )

        self.add_text(
            alert_box,
            f"Reason: {alert['reason']}",
            5,
        )

        customer_box = ttk.LabelFrame(
            top,
            text="Customer / AML Profile",
        )
        customer_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(6, 0),
        )

        self.add_text(
            customer_box,
            f"Customer: {account['customer_name']}",
            0,
        )

        self.add_text(
            customer_box,
            f"Account: {account['account_id']}",
            1,
        )

        self.add_text(
            customer_box,
            f"Risk Category: {profile['risk_category']}",
            2,
        )

        self.add_text(
            customer_box,
            (
                "Expected Transaction Range: "
                f"INR {float(profile['expected_min_transaction']):,.2f}"
                " - "
                f"INR {float(profile['expected_max_transaction']):,.2f}"
            ),
            3,
        )

        self.add_text(
            customer_box,
            (
                "Expected Daily Count: "
                f"{profile['expected_daily_transaction_count']}"
            ),
            4,
        )

        self.add_text(
            customer_box,
            (
                "Expected Monthly Volume: "
                f"INR {float(profile['expected_monthly_volume']):,.2f}"
            ),
            5,
        )

        # ---------------------------------------------------------
        # TRANSACTIONS
        # ---------------------------------------------------------

        transaction_box = ttk.LabelFrame(
            self.content,
            text="Transactions Under Investigation",
        )

        transaction_box.pack(
            fill="x",
            padx=12,
            pady=6,
        )

        columns = (
            "id",
            "sender",
            "receiver",
            "amount",
            "purpose",
            "timestamp",
            "status",
        )

        tree = ttk.Treeview(
            transaction_box,
            columns=columns,
            show="headings",
            height=5,
        )

        headings = (
            ("id", "Transaction ID", 170),
            ("sender", "Sender", 130),
            ("receiver", "Receiver", 130),
            ("amount", "Amount", 110),
            ("purpose", "Purpose", 130),
            ("timestamp", "Timestamp", 180),
            ("status", "Status", 90),
        )

        for column, title, width in headings:
            tree.heading(
                column,
                text=title,
            )
            tree.column(
                column,
                width=width,
            )

        tree.pack(
            fill="x",
            padx=5,
            pady=5,
        )

        for transaction in case["transactions"]:
            tree.insert(
                "",
                "end",
                values=(
                    transaction["transaction_id"],
                    transaction["sender_account_id"],
                    transaction["receiver_account_id"],
                    f"INR {float(transaction['amount']):,.2f}",
                    transaction["purpose"],
                    transaction["timestamp"],
                    transaction["status"],
                ),
            )

        # ---------------------------------------------------------
        # AGENT ANALYSIS
        # ---------------------------------------------------------

        agent_box = ttk.LabelFrame(
            self.content,
            text="Agent Findings",
        )

        agent_box.pack(
            fill="x",
            padx=12,
            pady=6,
        )

        agent_analysis = case.get("agent_analysis")

        if agent_analysis:
            findings = agent_analysis.get("findings", [])

            for finding in findings:
                self.add_text(
                    agent_box,
                    (
                        f"{finding['code']} | "
                        f"{finding['severity']}\n"
                        f"{finding['description']}"
                    ),
                    0,
                )

                evidence = finding.get("evidence", [])

                for evidence_item in evidence:
                    self.add_text(
                        agent_box,
                        f"Evidence: {evidence_item}",
                        1,
                    )
        else:
            self.add_text(
                agent_box,
                "No persisted agent analysis available.",
                0,
            )

        # ---------------------------------------------------------
        # POLICY + CRITIC
        # ---------------------------------------------------------

        governance = ttk.Frame(self.content)
        governance.pack(
            fill="x",
            padx=12,
            pady=6,
        )

        policy_box = ttk.LabelFrame(
            governance,
            text="Policy Evidence",
        )

        policy_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 6),
        )

        policy_evidence = []

        if agent_analysis:
            policy_evidence = agent_analysis.get(
                "policy_evidence",
                [],
            )

        policy_text = tk.Text(
            policy_box,
            height=7,
            width=70,
            wrap="word",
            font=("Segoe UI", 10),
        )

        policy_scroll = ttk.Scrollbar(
            policy_box,
            orient="vertical",
            command=policy_text.yview,
        )

        policy_text.configure(
            yscrollcommand=policy_scroll.set
        )

        policy_text.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5,
        )

        policy_scroll.pack(
            side="right",
            fill="y",
            pady=5,
        )

        if policy_evidence:
            for policy in policy_evidence:
                policy_text.insert(
                    "end",
                    f"{policy['policy_id']} - {policy['title']}\n"
                    f"{policy['text']}\n"
                    f"Relevance score: {policy['relevance_score']}\n\n"
                )
        else:
            policy_text.insert(
                "end",
                "No policy evidence available."
            )

        policy_text.configure(state="disabled")

        critic_box = ttk.LabelFrame(
            governance,
            text="Critic / Guardrail",
        )

        critic_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(6, 0),
        )

        critic = {}

        if agent_analysis:
            critic = agent_analysis.get(
                "critic",
                {},
            )

        critic_passed = critic.get("passed")

        if critic_passed is True:
            self.add_text(
                critic_box,
                "PASS - Investigation output passed governance checks.",
                0,
            )
        elif critic_passed is False:
            self.add_text(
                critic_box,
                "FAIL - Governance issues detected.",
                0,
            )

            for issue in critic.get("issues", []):
                self.add_text(
                    critic_box,
                    f"Issue: {issue}",
                    1,
                )
        else:
            self.add_text(
                critic_box,
                "Critic result unavailable.",
                0,
            )

        # ---------------------------------------------------------
        # RECOMMENDATION
        # ---------------------------------------------------------

        recommendation_box = ttk.LabelFrame(
            self.content,
            text="Recommendation",
        )

        recommendation_box.pack(
            fill="x",
            padx=12,
            pady=6,
        )

        recommendation = (
            agent_analysis.get("recommendation", {})
            if agent_analysis
            else {}
        )

        self.add_text(
            recommendation_box,
            f"Action: {recommendation.get('action', 'N/A')}",
            0,
        )

        self.add_text(
            recommendation_box,
            (
                "Rationale: "
                f"{recommendation.get('rationale', 'N/A')}"
            ),
            1,
        )

        self.add_text(
            recommendation_box,
            (
                "Human Approval Required: "
                f"{recommendation.get('requires_human_approval', 'N/A')}"
            ),
            2,
        )

        # ---------------------------------------------------------
        # HUMAN REVIEW
        # ---------------------------------------------------------

        review_box = ttk.LabelFrame(
            self.content,
            text="Human Review",
        )

        review_box.pack(
            fill="x",
            padx=12,
            pady=6,
        )

        self.review_status = tk.StringVar(
            value=f"Investigation status: {investigation['status']}"
        )

        ttk.Label(
            review_box,
            textvariable=self.review_status,
        ).pack(
            side="left",
            padx=10,
            pady=8,
        )

        self.start_review_button = ttk.Button(
            review_box,
            text="START REVIEW",
            command=self.start_review,
        )

        self.start_review_button.pack(
            side="left",
            padx=5,
            pady=8,
        )

        self.complete_review_button = ttk.Button(
            review_box,
            text="COMPLETE INVESTIGATION",
            command=self.complete_investigation,
        )

        self.complete_review_button.pack(
            side="left",
            padx=5,
            pady=8,
        )

        if investigation["status"] != "OPEN":
            self.start_review_button.state(["disabled"])

        if investigation["status"] != "IN_PROGRESS":
            self.complete_review_button.state(["disabled"])

        # ---------------------------------------------------------
        # FOOTER
        # ---------------------------------------------------------

        ttk.Label(
            self.content,
            textvariable=self.status,
        ).pack(
            fill="x",
            padx=12,
            pady=5,
        )

    def start_review(self):
        try:
            self.api.update_investigation_status(
                self.investigation_id,
                "IN_PROGRESS",
            )

            self.status.set(
                "Investigation moved to IN_PROGRESS."
            )

            self.load_case()

        except RuntimeError as e:
            messagebox.showerror(
                "Unable to start review",
                str(e),
            )

    def complete_investigation(self):
        conclusion = simpledialog.askstring(
            "Investigation Conclusion",
            "Enter the human investigator's conclusion:",
            parent=self.root,
        )

        if not conclusion or not conclusion.strip():
            return

        try:
            self.api.update_investigation_status(
                self.investigation_id,
                "COMPLETED",
                conclusion.strip(),
            )

            self.status.set(
                "Investigation completed."
            )

            self.load_case()

        except RuntimeError as e:
            messagebox.showerror(
                "Unable to complete investigation",
                str(e),
            )
