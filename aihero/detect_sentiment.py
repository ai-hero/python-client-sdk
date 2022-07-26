from .automation import Automation


class DetectSentiment(Automation):
    def add_short_text(self, guid: str, text: str) -> dict:
        assert text is not None
        assert guid is not None
        return super()._sync_job(
            {"type": "add_short_text", "row": {"text": text, "guid": guid}}
        )

    def predict(self, guid: str, text: str) -> dict:
        assert text is not None
        assert guid is not None
        return super()._infer("predict", {"text": text, "guid": guid})

    def set_ground_truth(self, guid: str, ground_truth: dict[str, bool]) -> dict:
        assert guid is not None
        return super()._sync_job(
            {
                "type": "set_ground_truth",
                "guid": guid,
                "ground_truth": ground_truth,
            }
        )
