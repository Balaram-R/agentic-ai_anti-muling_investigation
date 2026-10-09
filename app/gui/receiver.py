import tkinter as tk
from tkinter import ttk
from app.gui.time_utils import format_timestamp
class ReceiverWindow:
    def __init__(self,root,api):
        self.root=root; self.api=api; self.id="BANKB-ACC-5276"; root.title("BANK B — RECEIVED MONEY"); root.geometry("1380x680"); self.status=tk.StringVar(value="Ready")
        h=ttk.LabelFrame(root,text="Account"); h.pack(fill="x",padx=12,pady=10); ttk.Label(h,text="Bank: Bank B | Customer: Priya Menon").pack(anchor="w",padx=10,pady=4); ttk.Label(h,text=f"Account: {self.id}").pack(anchor="w",padx=10,pady=4); self.balance=ttk.Label(h); self.balance.pack(anchor="w",padx=10,pady=4)
        b=ttk.LabelFrame(root,text="Received Transactions"); b.pack(fill="both",expand=True,padx=12,pady=8); cols=("id","sender","amount","currency","purpose","timestamp","status"); self.tree=ttk.Treeview(b,columns=cols,show="headings")
        for c,t,w in (("id","Transaction ID",170),("sender","Sender Account",145),("amount","Amount",100),("currency","Currency",75),("purpose","Purpose",150),("timestamp","Timestamp",180),("status","Status",90)): self.tree.heading(c,text=t); self.tree.column(c,width=w)
        self.tree.pack(fill="both",expand=True); ttk.Label(root,textvariable=self.status).pack(fill="x",padx=12,pady=5); self.refresh()
    def refresh(self):
        try:
            a=self.api.account(self.id); self.balance.config(text=f"Balance: ₹{float(a['balance']):,.2f} {a['currency']}"); rows=[x for x in self.api.transactions(self.id) if x["receiver_account_id"]==self.id]; known={self.tree.item(i,"values")[0] for i in self.tree.get_children()}
            for t in rows:
                if t["transaction_id"] not in known: self.tree.insert("","end",values=(t["transaction_id"],t["sender_account_id"],f"₹{float(t['amount']):,.2f}",t["currency"],t["purpose"],format_timestamp(t["timestamp"]),t["status"]))
        except RuntimeError as e: self.status.set(str(e))
        self.root.after(1500,self.refresh)
