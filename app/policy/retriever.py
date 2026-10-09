from dataclasses import dataclass

from app.policy.corpus import POLICY_DOCUMENTS


@dataclass
class PolicyMatch:
    policy_id: str
    title: str
    text: str
    score: int


class PolicyRetriever:
    def __init__(self, documents=None):
        self.documents = documents or POLICY_DOCUMENTS

    def retrieve(self, query: str, top_k: int = 2) -> list[PolicyMatch]:
        query_terms = {
            term.strip().lower()
            for term in query.replace(",", " ").split()
            if term.strip()
        }

        matches = []

        for document in self.documents:
            searchable = " ".join(
                [
                    document["title"],
                    document["text"],
                    *document["keywords"],
                ]
            ).lower()

            score = sum(
                1
                for term in query_terms
                if term in searchable
            )

            if score > 0:
                matches.append(
                    PolicyMatch(
                        policy_id=document["policy_id"],
                        title=document["title"],
                        text=document["text"],
                        score=score,
                    )
                )

        matches.sort(
            key=lambda match: match.score,
            reverse=True,
        )

        return matches[:top_k]