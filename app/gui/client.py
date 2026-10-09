import requests
class ApiClient:
    def __init__(self,base_url): self.base_url=base_url.rstrip("/")
    def req(self,m,p,**kw):
        try: r=requests.request(m,self.base_url+p,timeout=5,**kw)
        except requests.RequestException as e: raise RuntimeError("Backend is unavailable. Start the application with 'python run.py'.") from e
        if r.status_code>=400:
            try: d=r.json().get("detail",r.text)
            except Exception: d=r.text
            raise RuntimeError(str(d))
        return r.json()
    def account(self,id): return self.req("GET",f"/accounts/{id}")
    def create(self,payload): return self.req("POST","/transactions",json=payload)
    def transactions(self,id): return self.req("GET",f"/accounts/{id}/transactions")
    def check_structuring(self, account_id):
        return self.req(
            "GET",
            f"/accounts/{account_id}/aml/structuring"
        )

    def open_alerts(self):
        return self.req(
            "GET",
            "/aml/alerts"
        )

    def create_investigation(self, alert_id, assigned_to=None):
        return self.req(
            "POST",
            f"/aml/alerts/{alert_id}/investigation",
            json={"assigned_to": assigned_to}
        )

    def investigation_by_alert(self, alert_id):
        return self.req(
            "GET",
            f"/aml/alerts/{alert_id}/investigation"
        )

    def investigation_case(self, investigation_id):
        return self.req(
            "GET",
            f"/aml/investigations/{investigation_id}/case"
        )

    def investigations(self):
        return self.req(
            "GET",
            "/aml/investigations"
        )


    def update_investigation_status(
        self,
        investigation_id,
        status,
        conclusion=None,
    ):
        payload = {
            "status": status,
        }

        if conclusion is not None:
            payload["conclusion"] = conclusion

        return self.req(
            "PATCH",
            f"/aml/investigations/{investigation_id}/status",
            json=payload,
        )

    def run_investigation(self, investigation_id):
        return self.req(
            "POST",
            f"/aml/investigations/{investigation_id}/run",
        )