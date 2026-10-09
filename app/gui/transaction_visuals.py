import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class TransactionVisualsWindow:
    """
    Full investigator analytics workspace.

    Shows:
    - Case / customer / alert summary
    - Risk and AML profile
    - Monthly behaviour
    - Evidence indicators
    - AI findings
    - Policy evidence
    - Critic / guardrail result
    - Recommendation
    - Alert transactions
    - Full account transaction history
    """

    def __init__(self, root, api, investigation_id=None):
        self.root = root
        self.api = api
        self.investigation_id = investigation_id
        self.case = None
        self.account_transactions = []

        root.title("AI BANK - INVESTIGATOR ANALYTICS")
        root.geometry("1450x950")

        self.load_case()

    # ---------------------------------------------------------
    # DATA
    # ---------------------------------------------------------

    def load_case(self):
        try:
            if self.investigation_id is None:
                investigations = self.api.investigations()

                if not investigations:
                    self.show_message(
                        "No active AML investigation."
                    )
                    return

                self.investigation_id = investigations[0][
                    "investigation_id"
                ]

            self.case = self.api.investigation_case(
                self.investigation_id
            )

            account_id = self.case["account"]["account_id"]

            # IMPORTANT:
            # Case transactions are the alert evidence.
            # Account transactions provide the wider behavioural picture.
            try:
                self.account_transactions = self.api.transactions(
                    account_id
                )
            except RuntimeError:
                self.account_transactions = (
                    self.case.get("transactions", [])
                )

            self.build_ui()

        except RuntimeError as e:
            self.show_message(str(e))

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def section(self, title):
        frame = ttk.LabelFrame(
            self.content,
            text=title,
        )
        frame.pack(
            fill="x",
            padx=12,
            pady=7,
        )
        return frame

    def label(self, parent, text, row, column=0, span=1):
        widget = ttk.Label(
            parent,
            text=text,
            wraplength=600,
            justify="left",
        )
        widget.grid(
            row=row,
            column=column,
            columnspan=span,
            padx=10,
            pady=4,
            sticky="w",
        )
        return widget

    def show_message(self, message):
        self.clear()

        ttk.Label(
            self.root,
            text=message,
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=80)

    # ---------------------------------------------------------
    # MAIN UI
    # ---------------------------------------------------------

    def build_ui(self):
        self.clear()

        case = self.case

        investigation = case["investigation"]
        alert = case["alert"]
        account = case["account"]
        profile = case["aml_profile"]

        # Scrollable page
        canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
        )

        scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=canvas.yview,
        )

        self.content = ttk.Frame(canvas)

        window_id = canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )

        def configure_scroll(event=None):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        def configure_width(event):
            canvas.itemconfigure(
                window_id,
                width=event.width,
            )

        self.content.bind(
            "<Configure>",
            configure_scroll,
        )

        canvas.bind(
            "<Configure>",
            configure_width,
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header = self.section(
            "AML INVESTIGATION"
        )

        self.label(
            header,
            f"Investigation ID: "
            f"{investigation['investigation_id']}",
            0,
        )

        self.label(
            header,
            f"Status: {investigation['status']}",
            1,
        )

        self.label(
            header,
            f"Alert: {alert['rule_code']} | "
            f"Severity: {alert['severity']}",
            2,
        )

        self.label(
            header,
            f"Alert Transactions: "
            f"{alert.get('transaction_count', 0)} | "
            f"Combined Amount: "
            f"₹{float(alert.get('combined_amount', 0)):,.2f}",
            3,
        )

        # -----------------------------------------------------
        # CUSTOMER / ACCOUNT
        # -----------------------------------------------------

        customer = self.section(
            "CUSTOMER & ACCOUNT"
        )

        self.label(
            customer,
            f"Customer: "
            f"{account.get('customer_name', 'N/A')}",
            0,
        )

        self.label(
            customer,
            f"Account: "
            f"{account.get('account_id', 'N/A')}",
            1,
        )

        self.label(
            customer,
            f"Balance: "
            f"₹{float(account.get('balance', 0)):,.2f} "
            f"{account.get('currency', '')}",
            2,
        )

        self.label(
            customer,
            f"AML Risk Category: "
            f"{profile.get('risk_category', 'N/A')}",
            0,
            1,
        )

        self.label(
            customer,
            f"Baseline Window: "
            f"{profile.get('baseline_window_days', 'N/A')} days",
            1,
            1,
        )

        self.label(
            customer,
            f"Expected Monthly Volume: "
            f"₹{float(profile.get('expected_monthly_volume', 0)):,.2f}",
            2,
            1,
        )

        # -----------------------------------------------------
        # MONTHLY BEHAVIOUR
        # -----------------------------------------------------

        behavior = (
            case.get("behavior")
            or investigation.get("behavior")
            or {}
        )

        monthly = behavior.get(
            "monthly",
            [],
        )

        chart_frame = self.section(
            "MONTHLY TRANSACTION BEHAVIOUR"
        )

        figure = Figure(
            figsize=(12, 3.5),
            dpi=100,
        )

        axis = figure.add_subplot(111)

        if monthly:
            months = [
                item.get("month", "")
                for item in monthly
            ]

            incoming = [
                float(item.get("incoming", 0))
                for item in monthly
            ]

            outgoing = [
                float(item.get("outgoing", 0))
                for item in monthly
            ]

            counts = [
                int(item.get("transaction_count", 0))
                for item in monthly
            ]

            x = range(len(months))
            width = 0.36

            axis.bar(
                [i - width / 2 for i in x],
                incoming,
                width,
                label="Incoming",
            )

            axis.bar(
                [i + width / 2 for i in x],
                outgoing,
                width,
                label="Outgoing",
            )

            axis.set_xticks(list(x))
            axis.set_xticklabels(months)
            axis.set_ylabel("Amount (INR)")
            axis.set_title(
                "Monthly Incoming vs Outgoing Volume"
            )
            axis.legend()
            axis.grid(
                axis="y",
                alpha=0.25,
            )

        else:
            axis.text(
                0.5,
                0.5,
                "No monthly behaviour data available",
                ha="center",
                va="center",
            )
            axis.set_axis_off()

        figure.tight_layout()

        chart = FigureCanvasTkAgg(
            figure,
            master=chart_frame,
        )

        chart.draw()

        chart.get_tk_widget().pack(
            fill="both",
            expand=True,
        )

        # Monthly table
        if monthly:
            monthly_frame = ttk.Frame(
                chart_frame
            )
            monthly_frame.pack(
                fill="x",
                padx=10,
                pady=5,
            )

            for col, heading in enumerate(
                [
                    "Month",
                    "Tx Count",
                    "Incoming",
                    "Outgoing",
                ]
            ):
                ttk.Label(
                    monthly_frame,
                    text=heading,
                    font=("Segoe UI", 9, "bold"),
                ).grid(
                    row=0,
                    column=col,
                    padx=15,
                    sticky="w",
                )

            for row, item in enumerate(
                monthly,
                start=1,
            ):
                values = [
                    item.get("month", ""),
                    item.get("transaction_count", 0),
                    f"₹{float(item.get('incoming', 0)):,.2f}",
                    f"₹{float(item.get('outgoing', 0)):,.2f}",
                ]

                for col, value in enumerate(values):
                    ttk.Label(
                        monthly_frame,
                        text=str(value),
                    ).grid(
                        row=row,
                        column=col,
                        padx=15,
                        pady=2,
                        sticky="w",
                    )

        # -----------------------------------------------------
        # BEHAVIOURAL EVIDENCE
        # -----------------------------------------------------

        evidence = behavior.get(
            "evidence",
            [],
        )

        evidence_frame = self.section(
            "BEHAVIOURAL EVIDENCE"
        )

        if evidence:
            for item in evidence:
                ttk.Label(
                    evidence_frame,
                    text="• " + str(item),
                    wraplength=1250,
                    justify="left",
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=3,
                )
        else:
            ttk.Label(
                evidence_frame,
                text="No behavioural evidence returned.",
            ).pack(
                anchor="w",
                padx=12,
                pady=5,
            )

        # -----------------------------------------------------
        # FINDINGS
        # -----------------------------------------------------

        findings = case.get(
            "findings",
            [],
        )

        findings_frame = self.section(
            "DETERMINISTIC AML FINDINGS"
        )

        if findings:
            for finding in findings:
                text = (
                    f"[{finding.get('severity', 'N/A')}] "
                    f"{finding.get('code', '')}\n"
                    f"{finding.get('title', '')}\n"
                    f"{finding.get('description', '')}"
                )

                ttk.Label(
                    findings_frame,
                    text=text,
                    wraplength=1250,
                    justify="left",
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=6,
                )
        else:
            ttk.Label(
                findings_frame,
                text="No findings.",
            ).pack(
                anchor="w",
                padx=12,
                pady=5,
            )

        # -----------------------------------------------------
        # AI ANALYSIS
        # -----------------------------------------------------

        agent_analysis = case.get(
            "agent_analysis"
        ) or {}

        analysis = agent_analysis.get(
            "analysis",
            {},
        )

        ai_frame = self.section(
            "AI INVESTIGATION FINDINGS"
        )

        ai_findings = analysis.get(
            "findings",
            [],
        )

        if ai_findings:
            for finding in ai_findings:
                text = (
                    f"[{finding.get('severity', 'N/A')}] "
                    f"{finding.get('code', '')}\n"
                    f"{finding.get('description', '')}\n"
                    f"Evidence: "
                    f"{'; '.join(map(str, finding.get('evidence', [])))}"
                )

                ttk.Label(
                    ai_frame,
                    text=text,
                    wraplength=1250,
                    justify="left",
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=6,
                )
        else:
            ttk.Label(
                ai_frame,
                text="AI findings are not available yet.",
            ).pack(
                anchor="w",
                padx=12,
                pady=5,
            )

        # -----------------------------------------------------
        # POLICY EVIDENCE
        # -----------------------------------------------------

        policies = case.get(
            "agent_analysis",
            {},
        ).get(
            "policy_evidence",
            [],
        )

        policy_frame = self.section(
            "POLICY / RAG EVIDENCE"
        )

        if policies:
            for policy in policies:
                text = (
                    f"{policy.get('policy_id', '')} - "
                    f"{policy.get('title', '')}\n"
                    f"{policy.get('text', '')}\n"
                    f"Relevance: "
                    f"{policy.get('relevance_score', 'N/A')}"
                )

                ttk.Label(
                    policy_frame,
                    text=text,
                    wraplength=1250,
                    justify="left",
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=6,
                )
        else:
            ttk.Label(
                policy_frame,
                text="No policy evidence returned.",
            ).pack(
                anchor="w",
                padx=12,
                pady=5,
            )

        # -----------------------------------------------------
        # CRITIC
        # -----------------------------------------------------

        critic = case.get(
            "agent_analysis",
            {},
        ).get(
            "critic",
            {},
        )

        critic_frame = self.section(
            "CRITIC / GUARDRAIL"
        )

        ttk.Label(
            critic_frame,
            text=(
                f"Passed: "
                f"{critic.get('passed', 'N/A')}"
            ),
        ).pack(
            anchor="w",
            padx=12,
            pady=4,
        )

        issues = critic.get(
            "issues",
            [],
        )

        for issue in issues:
            ttk.Label(
                critic_frame,
                text="• " + str(issue),
                wraplength=1250,
            ).pack(
                anchor="w",
                padx=20,
                pady=2,
            )

        # -----------------------------------------------------
        # ASSESSMENT / RECOMMENDATION
        # -----------------------------------------------------

        assessment = case.get(
            "assessment",
            {},
        )

        recommendation = case.get(
            "recommendation",
            {},
        )

        decision_frame = self.section(
            "ASSESSMENT & RECOMMENDATION"
        )

        self.label(
            decision_frame,
            f"Outcome: "
            f"{assessment.get('outcome', 'N/A')}",
            0,
        )

        self.label(
            decision_frame,
            f"Assessment rationale: "
            f"{assessment.get('rationale', 'N/A')}",
            1,
        )

        self.label(
            decision_frame,
            f"Recommended action: "
            f"{recommendation.get('action', 'N/A')}",
            2,
        )

        self.label(
            decision_frame,
            f"Recommendation rationale: "
            f"{recommendation.get('rationale', 'N/A')}",
            3,
        )

        self.label(
            decision_frame,
            f"Human approval required: "
            f"{recommendation.get('requires_human_approval', 'N/A')}",
            4,
        )

        # -----------------------------------------------------
        # ALERT TRANSACTIONS
        # -----------------------------------------------------

        alert_transactions = case.get(
            "transactions",
            []
        )

        self.transaction_table(
            "ALERT TRANSACTIONS",
            alert_transactions,
            account["account_id"],
        )

        # -----------------------------------------------------
        # FULL ACCOUNT HISTORY
        # -----------------------------------------------------

        self.transaction_table(
            f"FULL ACCOUNT TRANSACTION HISTORY "
            f"({len(self.account_transactions)} transactions)",
            self.account_transactions,
            account["account_id"],
        )

        # -----------------------------------------------------
        # HUMAN DECISION
        # -----------------------------------------------------

        human_frame = self.section(
            "HUMAN REVIEW"
        )

        conclusion = investigation.get(
            "conclusion"
        )

        if conclusion:
            ttk.Label(
                human_frame,
                text=f"Human conclusion: {conclusion}",
                wraplength=1250,
            ).pack(
                anchor="w",
                padx=12,
                pady=5,
            )
        else:
            ttk.Label(
                human_frame,
                text="Awaiting human investigator decision.",
            ).pack(
                anchor="w",
                padx=12,
                pady=5,
            )

    # ---------------------------------------------------------
    # TRANSACTION TABLE
    # ---------------------------------------------------------

    def transaction_table(
        self,
        title,
        transactions,
        account_id,
    ):
        frame = self.section(title)

        ttk.Label(
            frame,
            text=f"Transaction count: {len(transactions)}",
            font=("Segoe UI", 9, "bold"),
        ).pack(
            anchor="w",
            padx=12,
            pady=4,
        )

        columns = (
            "transaction_id",
            "direction",
            "amount",
            "timestamp",
            "counterparty",
            "purpose",
            "status",
        )

        table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=9,
        )

        headings = {
            "transaction_id": "Transaction ID",
            "direction": "Direction",
            "amount": "Amount",
            "timestamp": "Timestamp",
            "counterparty": "Counterparty",
            "purpose": "Purpose",
            "status": "Status",
        }

        widths = {
            "transaction_id": 180,
            "direction": 100,
            "amount": 120,
            "timestamp": 190,
            "counterparty": 160,
            "purpose": 180,
            "status": 90,
        }

        for column in columns:
            table.heading(
                column,
                text=headings[column],
            )
            table.column(
                column,
                width=widths[column],
            )

        scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=table.yview,
        )

        table.configure(
            yscrollcommand=scroll.set
        )

        table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=5,
        )

        scroll.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=5,
        )

        for transaction in transactions:
            sender = transaction.get(
                "sender_account_id",
                "",
            )

            receiver = transaction.get(
                "receiver_account_id",
                "",
            )

            if sender == account_id:
                direction = "OUTGOING"
                counterparty = receiver
            else:
                direction = "INCOMING"
                counterparty = sender

            table.insert(
                "",
                "end",
                values=(
                    transaction.get(
                        "transaction_id",
                        "",
                    ),
                    direction,
                    f"₹{float(transaction.get('amount', 0)):,.2f}",
                    transaction.get(
                        "timestamp",
                        "",
                    ),
                    counterparty,
                    transaction.get(
                        "purpose",
                        "",
                    ),
                    transaction.get(
                        "status",
                        "",
                    ),
                ),
            )
