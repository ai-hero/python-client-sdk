import inspect
from abc import ABC
from uuid import uuid4
from threading import Thread
from .exceptions import AIHeroException
from .openai_helper import get_embedding, ChatCompletion, has_key
import traceback
from warnings import warn

INSTRUCTIONS = """
You are an 'Automated LLM Evaluation Assistant' that helps evaluate the performance of Large Language Models.

You will first be presented the test context (i.e. the input, prompt, and output to the LLM) delimited by three backticks\
To this you will respond ready, and wait for the questions that represent test cases for the context. 

Next, expect each interaction is a question from the user. Together, all questions form a test suite. \
Answer each question in teh suite using the context provided. \
You should return `PASS` if the test question passes and `FAIL` if the test question fails \
(this can be followed by a reason for the failure, but make sure the output starts with `PASS:` or `FAIL:`)
"""

TEST_TEXT_TEMPLATE = """
{output}
"""


class PromptTestSuite(ABC):
    def __init__(
        self, project_id, client, test_suite_id: str, instructions: str = INSTRUCTIONS
    ):
        self._project_id = project_id
        self._client = client
        self._test_suite_id = test_suite_id
        self._instructions = instructions
        from .promptstash import PromptStash

        self._eval_variant = PromptStash(self._project_id, self._client).stash_template(
            template_id=self._test_suite_id,
            body=self._instructions,
            prompt_format="jinja2",
        )
        print("Using eval variant:", self._eval_variant)

    def _sync_stash_eval(
        self,
        template_id: str,
        variant: str,
        test_run: dict,
    ):
        for completion in test_run["completions"]:
            rendered_inputs, prompt, output = (
                completion["rendered_inputs"],
                completion["prompt"],
                completion["output"],
            )
            inputs_embedding, err = get_embedding(rendered_inputs)
            if err:
                warn("Error generating embedding for rendered_inputs in child thread.")
                raise AIHeroException(err)
            prompt_embedding, err = get_embedding(prompt)
            if err:
                warn("Error generating embedding for prompt in child thread.")
                raise AIHeroException(err)
            output_embedding, err = get_embedding(output)
            if err:
                warn("Error generating embedding for output in child thread.")
                raise AIHeroException(err)

            completion["inputs_embedding"] = inputs_embedding
            completion["prompt_embedding"] = prompt_embedding
            completion["output_embedding"] = output_embedding

        other = test_run.get("other", {})
        other.update({"embedding_model": "text-embedding-ada-002"})
        test_run["other"] = other

        self._client.post(
            f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}/variants/{variant}/evals",
            obj=test_run,
            timeout=30,
        )
        print("Test stashed.")

    def run(
        self,
        template_id: str,
        variant: str,
        completions: list[dict],
        model: dict,
        metrics: dict,
        other: dict,
        test_text_template=TEST_TEXT_TEMPLATE,
    ):
        run_id = str(uuid4())
        evaluator = None
        tests = []
        for completion in completions:
            inputs, prompt, output = (
                completion["inputs"],
                completion["prompt"],
                completion["output"],
            )
            context = test_text_template.format(prompt=prompt, output=output, **inputs)
            evaluator = None
            method_list = inspect.getmembers(self, predicate=inspect.ismethod)
            test_cases = {}
            for method_name, method_object in method_list:
                if method_name.startswith("test_"):
                    print(f"Running {method_name}...")
                    passed = False
                    try:
                        method_object(output)
                        passed = True
                        test_cases[method_name] = {
                            "errored": False,
                            "passed": passed,
                        }
                    except KeyboardInterrupt:
                        print("Interrupted by user.")
                        break
                    except AssertionError as assertion_error:
                        print("AssertionError:", assertion_error)
                        test_cases[method_name] = {
                            "errored": False,
                            "passed": passed,
                            "details": f"{assertion_error}",
                        }
                    except Exception as exception:
                        print("Error:", exception)
                        test_cases[method_name] = {
                            "errored": True,
                            "error": str(exception),
                        }
                elif method_name.startswith("ask_"):
                    if has_key():
                        if evaluator is None:
                            print("Initializing evaluator...")
                            evaluator = ChatCompletion(
                                system_message=self._instructions
                            )
                            ready, error = evaluator.chat("```" + context + "```")
                            if error:
                                test_cases[method_name] = {
                                    "errored": True,
                                    "error": error,
                                }
                            else:
                                try:
                                    print("init", context, ready)
                                    assert "ready" in ready.lower()
                                except AssertionError:
                                    traceback.print_exc()
                                    test_cases[method_name] = {
                                        "errored": True,
                                        "error": "Could not initialize evaluator. Not ready.",
                                    }
                        if evaluator:
                            print(f"Running {method_name}...")
                            passed = False
                            ask = method_object()
                            try:
                                response, error = evaluator.chat(ask)
                                if error:
                                    test_cases[method_name] = {
                                        "errored": True,
                                        "error": error,
                                    }
                                else:
                                    passed = "PASS:" in response.upper()
                                    print(
                                        "Ask: ",
                                        run_id,
                                        self._eval_variant,
                                        template_id,
                                        variant,
                                        method_name,
                                        ask,
                                        response,
                                        passed,
                                    )
                                    test_cases[method_name] = {
                                        "errored": False,
                                        "passed": passed,
                                        "asked": ask,
                                        "details": response,
                                    }
                            except Exception as exc:
                                traceback.print_exc()
                                test_cases[method_name] = {
                                    "errored": True,
                                    "error": str(exc),
                                }
                    else:
                        print(f"Skipping {method_name} as OPENAI_API_KEY is not set...")
                        test_cases[method_name] = {
                            "errored": True,
                            "error": "Skipping as OPENAI_API_KEY is not set...",
                        }
            tests.append(test_cases)

        if has_key():
            Thread(
                target=self._sync_stash_eval,
                args=(
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
                                "model": "gpt3.5-turbo",
                            },
                        },
                        "other": other,
                    },
                ),
            ).start()
        else:
            raise AIHeroException("No OPENAI_API_KEY in env variables.")
