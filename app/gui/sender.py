import tkinter as tk
from tkinter import ttk, messagebox

from app.gui.client import ApiClient
from app.gui.time_utils import format_timestamp


class SenderWindow:
    def __init__(self, root, api, on_investigation_created=None):
        self.root = root
        self.api = api
        self.on_investigation_created = on_investigation_created
        self.id = "AI-ACC-1842"
        root.title("AI BANK — SEND MONEY")
        root.geometry("1020x680")
        self.balance = tk.StringVar()
        self.receiver = tk.StringVar(value="BANKB-ACC-5276")
        self.amount = tk.StringVar()
        self.typ = tk.StringVar(value="TRANSFER")
        self.purpose = tk.StringVar(value="GENERAL_TRANSFER")
        self.status = tk.StringVar(value="Ready")
        h = ttk.LabelFrame(root, text="Account")
        h.pack(fill="x", padx=12, pady=10)
        ttk.Label(h, text="Bank: AI Bank | Customer: Balaram Ramji").pack(anchor="w", padx=10, pady=4)
        ttk.Label(h, text=f"Account: {self.id}").pack(anchor="w", padx=10, pady=4)
        ttk.Label(h, textvariable=self.balance).pack(anchor="w", padx=10, pady=4)
        f = ttk.LabelFrame(root, text="Send Synthetic Transaction")
        f.pack(fill="x", padx=12, pady=5)
        for i, (label, var) in enumerate((("Receiver Account", self.receiver), ("Amount", self.amount))):
            ttk.Label(f, text=label).grid(row=i, column=0, padx=10, pady=7, sticky="w")
            ttk.Entry(f, textvariable=var, width=30).grid(row=i, column=1, padx=10, pady=7)
        ttk.Label(f, text="Transaction Type").grid(row=2, column=0, padx=10, pady=7, sticky="w")
        ttk.Combobox(f, textvariable=self.typ, values=["TRANSFER", "UPI"], state="readonly", width=27).grid(row=2, column=1)
        ttk.Label(f, text="Purpose").grid(row=3, column=0, padx=10, pady=7, sticky="w")
        ttk.Combobox(f, textvariable=self.purpose, values=["GENERAL_TRANSFER", "SHOP_PAYMENT", "BILL_PAYMENT", "SALARY", "INVESTMENT", "OTHER"], state="readonly", width=27).grid(row=3, column=1)
        ttk.Button(f, text="SEND", command=self.send).grid(row=4, column=0, columnspan=2, pady=10)
        box = ttk.LabelFrame(root, text="Transaction History")
        box.pack(fill="both", expand=True, padx=12, pady=8)
        self.tree = ttk.Treeview(box, columns=("id", "receiver", "amount", "timestamp", "status"), show="headings")
        for c, t, w in (("id", "Transaction ID", 180), ("receiver", "Receiver", 150), ("amount", "Amount", 110), ("timestamp", "Timestamp", 180), ("status", "Status", 90)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True)
        ttk.Label(root, textvariable=self.status).pack(fill="x", padx=12, pady=5)
        self.refresh()

    def refresh(self):
        try:
            account = self.api.account(self.id)
            self.balance.set(f"Balance: ₹{float(account['balance']):,.2f} {account['currency']}")
            rows = self.api.transactions(self.id)
            for item in self.tree.get_children():
                self.tree.delete(item)
            for transaction in rows:
                self.tree.insert("", "end", values=(transaction["transaction_id"], transaction["receiver_account_id"], f"₹{float(transaction['amount']):,.2f}", format_timestamp(transaction["timestamp"]), transaction["status"]))
        except RuntimeError as e:
            self.status.set(str(e))

    def _find_existing_investigation(self, alert_id):
        try:
            return self.api.investigation_by_alert(alert_id)

        except RuntimeError as e:
            if "not found" in str(e).lower():
                return None

            raise

    def send(self):
        try:
            receiver = self.receiver.get().strip()

            if not receiver:
                raise ValueError("Receiver account is required")

            amount = float(self.amount.get())

            if amount <= 0:
                raise ValueError("Amount must be greater than zero")

            transaction = self.api.create({
                "transaction_type": self.typ.get(),
                "sender_account_id": self.id,
                "receiver_account_id": receiver,
                "amount": f"{amount:.2f}",
                "currency": "INR",
                "purpose": self.purpose.get(),
            })

            self.amount.set("")
            self.status.set(
                f"Settled: {transaction['transaction_id']}"
            )

            self.refresh()

            aml = self.api.check_structuring(self.id)

            if not aml["triggered"]:
                messagebox.showinfo(
                    "Transaction Successful",
                    f"Transaction ID: "
                    f"{transaction['transaction_id']}\n"
                    f"Status: {transaction['status']}\n\n"
                    f"AML Check: "
                    f"No structuring pattern detected.",
                )
                return

            # -------------------------------------------------
            # AML ALERT TRIGGERED
            # -------------------------------------------------

            existing_investigation = (
                self._find_existing_investigation(
                    aml["alert_id"]
                )
            )

            if existing_investigation:

                investigation_id = (
                    existing_investigation["investigation_id"]
                )

                if self.on_investigation_created:
                    self.on_investigation_created(investigation_id)

                investigation_message = (
                    "This AML alert is already under investigation."
                )

            else:

                try:
                    investigation = (
                        self.api.create_investigation(
                            aml["alert_id"],
                            assigned_to="AML-INVESTIGATOR-01",
                        )
                    )

                    investigation_id = (
                        investigation["investigation_id"]
                    )

                    if self.on_investigation_created:
                        self.on_investigation_created(investigation_id)

                    investigation_message = (
                        "A new AML investigation was created."
                    )

                except RuntimeError as e:

                    if "investigation already exists" in str(e).lower():

                        investigation_id = None

                        investigation_message = (
                            "An investigation already exists "
                            "for this AML alert."
                        )

                    else:
                        raise

            messagebox.showwarning(
                "AML Alert Triggered",
                f"STRUCTURING ALERT\n\n"
                f"Transaction Count: "
                f"{aml['transaction_count']}\n"
                f"Combined Amount: "
                f"₹{float(aml['combined_amount']):,.2f}\n\n"
                f"Reason:\n{aml['reason']}\n\n"
                f"Alert ID: {aml['alert_id']}\n"
                f"Investigation ID: "
                f"{investigation_id or 'Existing investigation'}\n\n"
                f"{investigation_message}",
            )

        except (ValueError, RuntimeError) as e:

            self.status.set(str(e))

            messagebox.showerror(
                "Transaction Error",
                str(e),
            )