"""PromptStash class for stashing prompts and feedbacks to the AI Hero Prompt Stash."""
from datetime import datetime
from threading import Thread
from warnings import warn
from io import StringIO
from typing import Optional, Union
import validators
from uuid import uuid4
from .client import Client
from .eval import PromptTestSuite
from .exceptions import AIHeroException
from .openai_helper import get_embedding, has_key


class PromptStash:
    """PromptStash class for stashing prompts and feedbacks to the AI Hero Prompt Stash."""

    def __init__(
        self,
        project_id: str,
        client: Client,
    ):
        assert project_id, "Please provide a project_id"
        assert isinstance(project_id, str), "project_id must be a string"
        assert validators.uuid(project_id), "project_id should be a valid UUID"
        assert client, "Please provide a client"
        assert isinstance(client, Client), "client must be a Client object"

        self._project_id = project_id
        self._client = client

    def stash_template(
        self,
        template_id: str,
        body: Union[str, list],
        name: Optional[str] = None,
        description: Optional[str] = None,
        prompt_format: str = "f-string",
        sections: Optional[dict] = None,
        author: str = "",
        other: Optional[dict] = None,
    ) -> str:
        """Stash a prompt template to the AI Hero Prompt Stash."""
        assert template_id, "Please provide a template_id"
        assert isinstance(template_id, str), "template_id must be a string"
        assert validators.slug(
            template_id
        ), "template_id should be a valid slug (i.e. '^[-a-zA-Z0-9_]+$')"
        assert body, "Please provide a body"
        assert isinstance(body, str) or isinstance(
            body, list
        ), "body must be a string or list"
        if isinstance(body, list):
            for body_item in body:
                assert isinstance(body_item, dict), "body must be a list of dicts"
                assert (
                    "role" in body_item
                ), "body must be a list of dicts with a 'role' key"
                assert body_item["role"] in [
                    "system",
                    "user",
                    "assistant",
                    "function",
                ], "body must be a list of dicts with a 'role' key with value 'system', 'user', 'assistant' or 'function'"
                assert (
                    "content" in body_item
                ), "body must be a list of dicts with a 'content' key"
                assert isinstance(
                    body_item["content"], str
                ), "body must be a list of dicts with a 'content' key with value of type string"
        if name:
            assert isinstance(name, str), "name must be a string"
        if description:
            assert isinstance(description, str), "description must be a string"
        assert prompt_format in [
            "f-string",
            "jinja2",
        ], "prompt_format must be either 'f-string' or 'jinja2'"
        if sections:
            assert isinstance(sections, dict), "sections must be a dictionary"
        if author:
            assert isinstance(author, str), "author must be a string"
        if other:
            assert isinstance(other, dict), "other must be a dictionary"

        prompt_template_dict = {
            "name": name or None,
            "description": description or None,
            "body": body,
            "prompt_format": prompt_format,
            "sections": sections or {},
            "author": author or "",
            "other": other or {},
        }

        # No variant found
        prompt_template_dict = self._client.post(
            f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}",
            obj=prompt_template_dict,
            error_msg=f"Couldn't stash prompt template {template_id} for project {self._project_id}",
            network_errors={
                400: "Please check the prompt_variant or the arguments.",
                403: f"Could not access project {self._project_id}. Please check the API key.",
                404: "Could not find the template.",
            },
        )
        return prompt_template_dict["variant"]

    def variant(self, template_id: str, variant: str = None) -> Union[str, list]:
        """Get a prompt template variant from the AI Hero Prompt Stash."""
        assert template_id, "Please provide a template_id"
        assert isinstance(template_id, str), "template_id must be a string"
        assert validators.slug(
            template_id
        ), "template_id should be a valid slug (i.e. '^[-a-zA-Z0-9_]+$')"
        if variant:
            assert isinstance(variant, str), "variant must be a string"
            assert validators.md5(variant), "variant should be a valid MD5 hash"

        if variant is None:
            # Get latest
            prompt_template_dict = self._client.get(
                f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}",
                error_msg=f"Could fetch prompt template {template_id} for project {self._project_id}",
                network_errors={
                    400: "Please check the prompt_template_id.",
                    403: f"Could not access project {self._project_id}. Please check the API key.",
                    404: "Could not find the variant.",
                },
            )
        else:
            prompt_template_dict = self._client.get(
                f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}/variants/{variant}",
                error_msg=f"Could fetch variant {variant} of prompt template {template_id} for project {self._project_id}",
                network_errors={
                    400: "Please check the prompt_variant.",
                    403: f"Could not access project {self._project_id}. Please check the API key.",
                    404: "Could not find the variant.",
                },
            )
        return prompt_template_dict["template"]

    def _sync_stash_completion(
        self,
        trace_id: str,
        step_id: str,
        template_id: str,
        variant: str,
        inputs: dict,
        rendered_inputs: str,
        prompt: Union[str, list],
        output: str,
        model: dict,
        metrics: dict,
        other: dict = None,
        created_at: str = None,
    ):
        """Sync a completion to the AI Hero Prompt Stash."""
        other = other or {}

        if has_key():
            inputs_embedding, err = get_embedding(rendered_inputs)
            if err:
                warn("Error generating embedding for rendered_inputs in child thread.")
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

            other["embedding_model"] = "text-embedding-ada-002"
        else:
            inputs_embedding = None
            prompt_embedding = None
            output_embedding = None

        stash_obj = {
            "trace_id": trace_id,
            "step_id": step_id,
            "step_type": "completion",
            "template_id": template_id,
            "variant": variant,
            "inputs": inputs,
            "rendered_inputs": rendered_inputs,
            "prompt": prompt,
            "output": output,
            "inputs_embedding": inputs_embedding,
            "prompt_embedding": prompt_embedding,
            "output_embedding": output_embedding,
            "model": model,
            "metrics": metrics,
            "other": other,
            "created_at": created_at or datetime.now().isoformat(),
        }
        self._client.post(
            f"/tools/promptstash/projects/{self._project_id}/stash",
            obj=stash_obj,
            timeout=30,
        )
        print("Prompt stashed.")

    def stash_completion(
        self,
        trace_id: str,
        step_id: str,
        template_id: str,
        variant: str,
        inputs: dict,
        rendered_inputs: str,
        prompt: Union[str, list],
        output: Union[str, dict],
        model: dict,
        metrics: dict,
        other: dict = None,
    ):
        """Stash a completion to the AI Hero Prompt Stash."""
        assert trace_id, "Please provide a trace_id"
        assert isinstance(trace_id, str), "trace_id must be a string"
        assert validators.uuid(trace_id), "trace_id should be a valid UUID"
        assert step_id, "Please provide a step_id"
        assert isinstance(step_id, str), "step_id must be a string"
        assert validators.uuid(step_id), "step_id should be a valid UUID"
        assert template_id, "Please provide a template_id"
        assert isinstance(template_id, str), "template_id must be a string"
        assert validators.slug(
            template_id
        ), "template_id should be a valid slug (i.e. '^[-a-zA-Z0-9_]+$')"
        assert variant, "Please provide a variant"
        assert isinstance(variant, str), "variant must be a string"
        assert validators.md5(variant), "variant should be a valid MD5 hash"
        assert inputs is not None, "Please provide inputs"
        assert isinstance(inputs, dict), "inputs must be a dict"
        for k, _ in inputs.items():
            assert isinstance(k, str), "inputs keys must be strings"
        assert rendered_inputs is not None, "Please provide rendered_inputs"
        assert isinstance(rendered_inputs, str), "rendered_inputs must be a string"
        assert prompt, "Please provide a prompt"
        assert isinstance(prompt, str) or isinstance(
            prompt, list
        ), "prompt must be a string or list"
        if isinstance(prompt, list):
            for prompt_item in prompt:
                assert isinstance(prompt_item, dict), "prompt must be a list of dicts"
                assert (
                    "role" in prompt_item
                ), "prompt must be a list of dicts with a 'role' key"
                assert prompt_item["role"] in [
                    "system",
                    "user",
                    "assistant",
                    "function",
                ], "prompt must be a list of dicts with a 'role' key with value 'system', 'user', 'assistant' or 'function'"
                assert (
                    "content" in prompt_item
                ), "prompt must be a list of dicts with a 'content' key"
                assert isinstance(
                    prompt_item["content"], str
                ), "prompt must be a list of dicts with a 'content' key with value of type string"
        assert output, "Please provide an output"
        assert isinstance(output, str) or isinstance(
            output, dict
        ), "output must be a string or dict"
        if isinstance(output, dict):
            assert "role" in output, "output must be a list of dicts with a 'role' key"
            assert output["role"] in [
                "system",
                "user",
                "assistant",
                "function",
            ], "output must be a list of dicts with a 'role' key with value 'system', 'user', 'assistant' or 'function'"
            assert (
                "content" in output
            ), "output must be a list of dicts with a 'content' key"
            assert isinstance(
                output["content"], str
            ), "output must be a list of dicts with a 'content' key with value of type string"
        assert model, "Please provide a model"
        assert isinstance(model, dict), "model must be a dict"
        assert "name" in model, "model must have a name"
        assert isinstance(model["name"], str), "model name must be a string"
        assert "version" in model, "model must have a version"
        assert isinstance(model["version"], str), "model version must be a string"
        assert metrics, "Please provide metrics"
        assert isinstance(metrics, dict), "metrics must be a dict"
        assert "time" in metrics, "metrics must have a time"
        if other:
            assert isinstance(other, dict), "other must be a dict"

        Thread(
            target=self._sync_stash_completion,
            args=(
                trace_id,
                step_id,
                template_id,
                variant,
                inputs,
                rendered_inputs,
                prompt,
                output,
                model,
                metrics,
                other,
            ),
        ).start()

    def _sync_stash_feedback(
        self,
        trace_id: str,
        step_id: str,
        thumbs_up: bool,
        thumbs_down: bool,
        correction: str,
        annotations: dict,
        other: dict = None,
        created_at: str = None,
    ):
        """Sync a feedback to the AI Hero Prompt Stash."""
        stash_obj = {
            "trace_id": trace_id,
            "step_id": step_id,
            "step_type": "feedback",
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "correction": correction,
            "annotations": annotations,
            "created_at": created_at or datetime.now().isoformat(),
        }
        if other is None:
            other = {}
        stash_obj["other"] = other
        self._client.post(
            f"/tools/promptstash/projects/{self._project_id}/stash",
            obj=stash_obj,
            timeout=30,
        )
        print("Feedback stashed.")

    def stash_feedback(
        self,
        trace_id: str,
        for_step_id: str,
        thumbs_up: bool,
        thumbs_down: bool,
        correction: str = None,
        annotations: dict = None,
        for_message_id: str = None,
        other: dict = None,
    ):
        """Stash a feedback to the AI Hero Prompt Stash."""
        assert trace_id, "Please provide a trace_id"
        assert isinstance(trace_id, str), "trace_id must be a string"
        assert validators.uuid(trace_id), "trace_id should be a valid UUID"
        step_id = str(uuid4())
        assert for_step_id, "Please provide a for_step_id"
        assert isinstance(for_step_id, str), "for_step_id must be a string"
        assert validators.uuid(for_step_id), "for_step_id should be a valid UUID"
        assert isinstance(thumbs_up, bool), "thumbs_up must be a bool"
        assert isinstance(thumbs_down, bool), "thumbs_down must be a bool"
        if thumbs_up and thumbs_down:
            raise ValueError("thumbs_up and thumbs_down cannot both be True")
        if correction:
            assert isinstance(correction, str), "correction must be a string"
        annotations = annotations or {}
        assert isinstance(annotations, dict), "annotations must be a dict"
        for k, _ in annotations.items():
            assert isinstance(k, str), "annotations keys must be strings"
        if for_message_id:
            assert isinstance(for_message_id, str), "message_id must be a string"
            assert validators.uuid(for_message_id), "message_id should be a valid UUID"
        if other:
            assert isinstance(other, dict), "other must be a dict"
        other = other or {}
        other["for_step_id"] = for_step_id
        if for_message_id:
            other["for_message_id"] = for_message_id
        Thread(
            target=self._sync_stash_feedback,
            args=(
                trace_id,
                step_id,
                thumbs_up,
                thumbs_down,
                correction,
                annotations,
                other,
            ),
        ).start()

    def build_test_suite(self, test_suite_id: str) -> PromptTestSuite:
        """Build a test suite."""
        assert test_suite_id, "Please provide a test_suite_id"
        assert isinstance(test_suite_id, str), "test_suite_id must be a string"
        assert validators.slug(
            test_suite_id
        ), "test_suite_id should be a valid slug (i.e. '^[-a-zA-Z0-9_]+$')"
        return PromptTestSuite(
            project_id=self._project_id,
            client=self._client,
            test_suite_id=test_suite_id,
        )
