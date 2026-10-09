from alembic import op
import sqlalchemy as sa
revision="0001_initial"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("accounts",sa.Column("account_id",sa.String(32),primary_key=True),sa.Column("bank_name",sa.String(100),nullable=False),sa.Column("customer_name",sa.String(150),nullable=False),sa.Column("account_number",sa.String(32),unique=True,nullable=False),sa.Column("balance",sa.Numeric(18,2),nullable=False),sa.Column("currency",sa.String(3),nullable=False)); op.create_index("ix_accounts_account_number","accounts",["account_number"])
    tt=sa.Enum("UPI","TRANSFER",name="transaction_type")
    tp=sa.Enum("GENERAL_TRANSFER","SHOP_PAYMENT","BILL_PAYMENT","SALARY","INVESTMENT","OTHER",name="transaction_purpose")
    ts=sa.Enum("PROCESSING","SETTLED",name="transaction_status")
    op.create_table("transactions",sa.Column("transaction_id",sa.String(36),primary_key=True),sa.Column("transaction_type",tt,nullable=False),sa.Column("sender_account_id",sa.String(32),sa.ForeignKey("accounts.account_id"),nullable=False),sa.Column("receiver_account_id",sa.String(32),sa.ForeignKey("accounts.account_id"),nullable=False),sa.Column("amount",sa.Numeric(18,2),nullable=False),sa.Column("currency",sa.String(3),nullable=False),sa.Column("purpose",tp,nullable=False),sa.Column("timestamp",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.Column("status",ts,nullable=False)); op.create_index("ix_tx_sender_ts","transactions",["sender_account_id","timestamp"]); op.create_index("ix_tx_receiver_ts","transactions",["receiver_account_id","timestamp"])
def downgrade():
    op.drop_index("ix_tx_receiver_ts",table_name="transactions"); op.drop_index("ix_tx_sender_ts",table_name="transactions"); op.drop_table("transactions"); bind=op.get_bind(); sa.Enum(name="transaction_status").drop(bind,checkfirst=True); sa.Enum(name="transaction_purpose").drop(bind,checkfirst=True); sa.Enum(name="transaction_type").drop(bind,checkfirst=True); op.drop_index("ix_accounts_account_number",table_name="accounts"); op.drop_table("accounts")
