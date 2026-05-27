class HybridRouter:

    def __init__(
        self,
        rule_layer,
        ai_router
    ):

        self.rule_layer = rule_layer
        self.ai_router = ai_router

    def classify(self, message: str):

        rule_result = self.rule_layer.classify(
            message
        )

        # -------------------------
        # Rule succeeded
        # -------------------------

        if rule_result != "unknown":

            return {
                "type": rule_result,
                "confidence": 1.0,
                "reason": "Matched deterministic pattern in Rule Layer",
                "source": "rule"
            }

        # -------------------------
        # AI fallback
        # -------------------------

        ai_result = self.ai_router.classify(
            message
        )

        # Ensure correct dictionary structure and key presence
        return {
            "type": ai_result.get("type", "chat"),
            "confidence": ai_result.get("confidence", 0.5),
            "reason": ai_result.get("reason", "Decided by AI model"),
            "source": "ai"
        }