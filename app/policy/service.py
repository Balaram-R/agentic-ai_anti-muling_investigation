from dataclasses import dataclass

from app.policy.retriever import PolicyMatch, PolicyRetriever


@dataclass
class PolicyEvidence:
    policy_id: str
    title: str
    text: str
    relevance_score: int


class PolicyService:
    FINDING_QUERY_MAP = {
        "STRUCTURING_PATTERN": (
            "structuring multiple transactions transaction count "
            "combined amount short period monitoring"
        ),
        "CUSTOMER_RISK_CATEGORY": (
            "customer risk risk category customer profile"
        ),
        "ABOVE_EXPECTED_TRANSACTION_SIZE": (
            "transaction monitoring transaction amount customer profile"
        ),
    }

    def __init__(self, retriever=None):
        self.retriever = retriever or PolicyRetriever()

    def retrieve_for_findings(
        self,
        finding_codes: list[str],
        top_k: int = 2,
    ) -> list[PolicyEvidence]:

        query_parts = []

        for finding_code in finding_codes:
            mapped_query = self.FINDING_QUERY_MAP.get(
                finding_code,
                finding_code.replace("_", " "),
            )
            query_parts.append(mapped_query)

        query = " ".join(query_parts)

        matches: list[PolicyMatch] = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        return [
            PolicyEvidence(
                policy_id=match.policy_id,
                title=match.title,
                text=match.text,
                relevance_score=match.score,
            )
            for match in matches
        ]