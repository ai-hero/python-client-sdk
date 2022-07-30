from .automation import Automation


class DetectSentiment(Automation):
    def add_short_text(self, guid: str, text: str) -> dict:
        assert text is not None
        assert guid is not None
        return super()._sync_job(
            {"type": "add_short_text", "thing": {"text": text, "guid": guid}}
        )

    def predict(self, guid: str, text: str) -> dict:
        assert text is not None
        assert guid is not None
        return super()._infer(
            {"type": "predict", "thing": {"text": text, "guid": guid}}
        )

    def set_ground_truth(self, guid: str, ground_truth: dict[str, bool]) -> dict:
        assert guid is not None
        return super()._sync_job(
            {
                "type": "set_ground_truth",
                "guid": guid,
                "ground_truth": ground_truth,
            }
        )

    def set_contender_prediction(
        self, guid: str, contender_prediction: dict[str, float]
    ) -> dict:
        assert guid is not None
        return super()._sync_job(
            {
                "type": "set_contender_prediction",
                "guid": guid,
                "contender_prediction": contender_prediction,
            }
        )

    def set_champion_prediction(
        self, guid: str, champion_prediction: dict[str, float]
    ) -> dict:
        assert guid is not None
        return super()._sync_job(
            {
                "type": "set_champion_prediction",
                "guid": guid,
                "champion_prediction": champion_prediction,
            }
        )

    def set_deployment_prediction(
        self, guid: str, deployment_prediction: dict[str, float]
    ) -> dict:
        assert guid is not None
        return super()._sync_job(
            {
                "type": "set_deployment_prediction",
                "guid": guid,
                "deployment_prediction": deployment_prediction,
            }
        )
