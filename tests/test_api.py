from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.seed import seed
from app.main import app
from app.api.deps import get_db
@pytest.fixture
def client(tmp_path):
    e=create_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}",connect_args={"check_same_thread":False}); Base.metadata.create_all(e); S=sessionmaker(bind=e,expire_on_commit=False)
    with S() as db: seed(db)
    def override():
        with S() as db: yield db
    app.dependency_overrides[get_db]=override
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear(); Base.metadata.drop_all(e)
def p(amount="750000.00"): return {"transaction_type":"TRANSFER","sender_account_id":"AI-ACC-1842","receiver_account_id":"BANKB-ACC-5276","amount":amount,"currency":"INR","purpose":"GENERAL_TRANSFER"}
def test_valid(client):
    r=client.post("/transactions",json=p()); assert r.status_code==201; assert r.json()["status"]=="SETTLED"
def test_negative_and_zero(client):
    assert client.post("/transactions",json=p("-1")).status_code==422; assert client.post("/transactions",json=p("0")).status_code==422
def test_unknown_and_insufficient(client):
    x=p(); x["sender_account_id"]="UNKNOWN"; assert client.post("/transactions",json=x).status_code==404
    x=p(); x["receiver_account_id"]="UNKNOWN"; assert client.post("/transactions",json=x).status_code==404
    assert client.post("/transactions",json=p("999999999")).status_code==409
def test_retrieve_and_balances(client):
    s=client.get("/accounts/AI-ACC-1842").json(); r=client.get("/accounts/BANKB-ACC-5276").json(); t=client.post("/transactions",json=p()).json(); assert client.get("/transactions/"+t["transaction_id"]).status_code==200; assert client.get("/accounts/BANKB-ACC-5276/transactions").json()[0]["transaction_id"]==t["transaction_id"]; assert Decimal(client.get("/accounts/AI-ACC-1842").json()["balance"])==Decimal(s["balance"])-Decimal("750000.00"); assert Decimal(client.get("/accounts/BANKB-ACC-5276").json()["balance"])==Decimal(r["balance"])+Decimal("750000.00")
