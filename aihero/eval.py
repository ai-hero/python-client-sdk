"""Evaluation module for AIHero."""
import re
from io import StringIO
import traceback
from abc import ABC
from collections import defaultdict
from uuid import uuid4
from warnings import warn
from typing import List
import validators

from .exceptions import AIHeroException
from .openai_helper import ChatCompletion, get_embedding, has_key

INSTRUCTIONS = """
You are an teaching assistant that helps evaluate texts for some expectation.

For the text and the expectation, you will respond `PASS` if the expectation is met and `FAIL` if the expectation is not. \
You should also provide a reason for the failure, but make sure your response starts with `PASS:` or `FAIL:`
"""

TEST_TEXT_TEMPLATE = """
Text:
{text}

Expectation:
{expectation}
"""


class PromptTestSuite(ABC):
    """Abstract base class for prompt test suites."""

    def __init__(
        self, project_id, client, test_suite_id: str, instructions: str = INSTRUCTIONS
    ):
        """Initialize a prompt test suite."""
        self._project_id = project_id
        self._client = client
        self._test_suite_id = test_suite_id
        self._instructions = instructions

        from .promptstash import PromptStash  # pylint: disable=import-outside-toplevel

        self._eval_variant = PromptStash(self._project_id, self._client).stash_template(
            template_id=self._test_suite_id,
            body=self._instructions,
            prompt_format="f-string",
            other={"is_test_suite": True},
        )

    def _sync_stash_eval(
        self,
        template_id: str,
        variant: str,
        test_run: dict,
    ):
        """Sync a test run to the prompt stash."""
        for completion in test_run["completions"]:
            if has_key():
                rendered_inputs, prompt, output = (
                    completion["rendered_inputs"],
                    completion["prompt"],
                    completion["output"],
                )
                inputs_embedding, err = get_embedding(rendered_inputs)
                if err:
                    warn(
                        "Error generating embedding for rendered_inputs in child thread."
                    )
                    raise AIHeroException(err)
                if isinstance(prompt, str):
                    prompt_embedding, err = get_embedding(prompt)
                else:
                    assert isinstance(prompt, list)
                    sio = StringIO()
                    for message in prompt:
                        sio.write(
                            f"{message['role'].upper()}:\n-------------------\n{message['content']}\n-------------------\n"
                        )
                        sio.write("\n")
                    prompt_embedding, err = get_embedding(sio.getvalue())
                if err:
                    warn("Error generating embedding for prompt in child thread.")
                    raise AIHeroException(err)

                if isinstance(output, str):
                    output_embedding, err = get_embedding(output)
                else:
                    assert isinstance(output, dict)
                    output_embedding, err = get_embedding(output["content"])

                if err:
                    warn("Error generating embedding for output in child thread.")
                    raise AIHeroException(err)

                completion["inputs_embedding"] = inputs_embedding
                completion["prompt_embedding"] = prompt_embedding
                completion["output_embedding"] = output_embedding
            else:
                completion["inputs_embedding"] = None
                completion["prompt_embedding"] = None
                completion["output_embedding"] = None

        other = test_run.get("other", {})
        other.update({"embedding_model": "text-embedding-ada-002"})
        test_run["other"] = other

        self._client.post(
            f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}/variants/{variant}/evals",
            obj=test_run,
            timeout=30,
        )

    def run(
        self,
        template_id: str,
        variant: str,
        completions: List[dict],
        expectations: List[List[str]],
        model: dict,
        metrics: dict,
        other: dict,
    ):
        """Run a test suite."""
        assert template_id, "Please provide a template_id"
        assert isinstance(template_id, str), "template_id must be a string"
        assert validators.slug(
            template_id
        ), "template_id should be a valid slug (i.e. '^[-a-zA-Z0-9_]+$')"
        assert variant, "Please provide a variant"
        assert isinstance(variant, str), "variant must be a string"
        assert validators.md5(variant), "variant should be a valid MD5 hash"
        assert completions, "Please provide completions"
        assert isinstance(completions, list), "completions must be a list"
        for completion in completions:
            assert isinstance(completion, dict), "Each completion must be a dictionary"
            # Schema check
            for k in ["rendered_inputs", "prompt", "output", "inputs"]:
                assert k in completion, f"Each completion must have a '{k}' key"
                if k == "rendered_inputs":
                    assert isinstance(completion[k], str), f"{k} must be a str"
                elif k == "inputs":
                    assert isinstance(completion[k], dict), f"{k} must be a dict"
                elif k == "prompt":
                    assert isinstance(completion[k], str) or isinstance(
                        completion[k], list
                    ), f"{k} must be a string or a list"
                    if isinstance(completion[k], list):
                        for msg in completion[k]:
                            assert "role" in msg, "Each message must have a role"
                            assert "content" in msg, "Each message must have a content"

                elif k == "output":
                    assert isinstance(completion[k], str) or isinstance(
                        completion[k], dict
                    ), f"{k} must be a string or dict"

                    if isinstance(completion[k], dict):
                        msg = completion[k]
                        assert "role" in msg, "Each message must have a role"
                        assert "content" in msg, "Each message must have a content"
        assert expectations, "Please provide expectations"
        assert isinstance(
            expectations, list
        ), "expectations must be a list[list[strings]]"
        for expectation_list in expectations:
            assert isinstance(
                expectation_list, list
            ), "Inner expectations list must be a list"
            for expectation in expectation_list:
                assert isinstance(expectation, str), "Expectation must be a string"
        assert model, "Please provide a model"
        assert isinstance(model, dict), "model must be a dict"
        assert "name" in model, "model must have a name"
        assert isinstance(model["name"], str), "model name must be a string"
        assert "version" in model, "model must have a version"
        assert isinstance(model["version"], str), "model version must be a string"
        assert metrics, "Please provide metrics"
        assert isinstance(metrics, dict), "metrics must be a dict"
        assert "avg_time" in metrics, "metrics must have a avg_time"
        assert "times" in metrics, "metrics must have a times"
        assert len(metrics["times"]) == len(
            completions
        ), "Number of times must be equal to the number of completions."

        other = other or {}
        if other:
            assert isinstance(other, dict), "other must be a dict"
        run_id = str(uuid4())
        evaluator = None
        tests = []

        for completion in completions:
            print(f"Test Case: '{completion['rendered_inputs']}'")
            output = completion["output"]
            if isinstance(output, dict):
                output = output["content"]

            evaluator = ChatCompletion(system_message=self._instructions)
            test_cases = {}

            for expectation in expectations[0]:
                method_name = re.sub(
                    r"[^a-zA-Z0-9_]", "", expectation.lower().replace(" ", "_")
                )
                try:
                    test_question = TEST_TEXT_TEMPLATE.format(
                        text=output, expectation=expectation
                    )
                    response, error = evaluator.chat(test_question)
                    if error:
                        test_cases[method_name] = {
                            "errored": True,
                            "error": error,
                        }
                    else:
                        if "PASS" in response.upper():
                            passed = True
                        elif "FAIL" in response.upper():
                            passed = False
                        else:
                            raise AIHeroException(
                                expectation + " - did not return pass/fail: " + response
                            )
                        test_cases[method_name] = {
                            "errored": False,
                            "passed": passed,
                            "asked": expectation,
                            "details": response,
                        }
                except Exception as exc:  # pylint: disable=broad-except
                    traceback.print_exc()
                    test_cases[method_name] = {
                        "errored": True,
                        "error": str(exc),
                    }

            tests.append(test_cases)

        passed_counts = defaultdict(int)
        failed_counts = defaultdict(int)
        errored_counts = defaultdict(int)
        total_counts = defaultdict(int)
        for test_cases in tests:
            for method_name, method_results in test_cases.items():
                if method_name == "total":
                    continue
                total_counts[method_name] += 1
                if method_results.get("errored"):
                    errored_counts[method_name] += 1
                elif method_results.get("passed"):
                    passed_counts[method_name] += 1
                else:
                    failed_counts[method_name] += 1

        # Summarize results
        passed_count = 0
        failed_count = 0
        errored_count = 0
        total_count = 0

        summary = ""
        summary += "PASS/FAIL SUMMARY:\n"
        summary += "\tPASSED\tFAILED\tERRORED\tTOTAL\tTEST\n"
        for method_name in total_counts:
            total_count += total_counts[method_name]
            passed_count += passed_counts[method_name]
            failed_count += failed_counts[method_name]
            errored_count += errored_counts[method_name]
            summary += f"\t{passed_counts[method_name]}\t{failed_counts[method_name]}\t{errored_counts[method_name]}\t{total_counts[method_name]}\t{method_name}\n"
        summary += "TOTALS:\n"
        summary += f"\t{passed_count}\t{failed_count}\t{errored_count}\t{total_count}\n"
        print(summary)
        metrics["summary"] = {
            "passed": passed_count,
            "failed": failed_count,
            "errored": errored_count,
            "total": total_count,
        }
        self._sync_stash_eval(
            template_id,
            variant,
            {
                "test_suite_id": self._test_suite_id,
                "test_run_id": run_id,
                "completions": completions,
                "tests": tests,
                "model": model,
                "metrics": metrics,
                "evaluator": {
                    "template_id": self._test_suite_id,
                    "variant": self._eval_variant,
                    "model": {
                        "provider": "openai",
                        "api": "chat_completion",
                        "model": "gpt-3.5-turbo",
                    },
                },
                "other": other,
            },
        )

        return run_id, summary
