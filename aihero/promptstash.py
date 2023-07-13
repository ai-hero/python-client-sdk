from threading import Thread
from .client import Client
from .exceptions import AIHeroException
from .openai_helper import get_embedding, has_key
from warnings import warn


class PromptStash:
    def __init__(
        self,
        project_id: str,
        client: Client,
    ):
        self._project_id = project_id
        self._client = client

    def variant(
        self,
        template_id: str,
        variant: str = None,
        body: str = None,
        name: str = None,
        description: str = None,
        prompt_format: str = "f-string",
        sections: str = None,
        author: str = None,
        other: dict = None,
    ):
        if variant is None and body is None:
            prompt_template_dict = self._client.get(
                f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}",
                error_msg=f"Could fetch prompt template {template_id} for project {self._project_id}",
                network_errors={
                    400: "Please check the prompt_template_id.",
                    403: f"Could not access project {self._project_id}. Please check the API key.",
                },
            )
        else:
            if variant:
                prompt_template_dict = self._client.get(
                    f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}/variants/{variant}",
                    error_msg=f"Could fetch variant {variant} of prompt template {template_id} for project {self._project_id}",
                    network_errors={
                        400: "Please check the prompt_variant.",
                        403: f"Could not access project {self._project_id}. Please check the API key.",
                    },
                )
            else:
                prompt_template_dict = {
                    "body": body,
                    "prompt_format": prompt_format,
                    "sections": {},
                    "author": "",
                    "other": {},
                }
                if name:
                    prompt_template_dict["name"] = name
                if description:
                    prompt_template_dict["description"] = description
                if sections:
                    prompt_template_dict["sections"] = sections
                if author:
                    prompt_template_dict["author"] = author
                if other:
                    prompt_template_dict["other"] = other
                # No variant found
                prompt_template_dict = self._client.post(
                    f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}",
                    obj=prompt_template_dict,
                    error_msg=f"Could update variant {variant} of prompt template {template_id} for project {self._project_id}",
                    network_errors={
                        400: "Please check the prompt_variant or the arguments.",
                        403: f"Could not access project {self._project_id}. Please check the API key.",
                    },
                )
            return prompt_template_dict["variant"], prompt_template_dict["template"]

    def _sync_stash(
        self,
        template_id: str,
        variant: str,
        prompt: str,
        output: str,
        inputs: str = None,
        other: dict = None,
    ):
        prompt_embedding, err = get_embedding(prompt)
        if err:
            warn("Error generating embedding for prompt in child thread.")
            raise AIHeroException(err)
        output_embedding, err = get_embedding(output)
        if err:
            warn("Error generating embedding for output in child thread.")
            raise AIHeroException(err)

        stash_obj = {
            "prompt": prompt,
            "output": output,
            "prompt_embedding": prompt_embedding,
            "output_embedding": output_embedding,
        }

        if inputs:
            inputs_embedding, err = get_embedding(inputs)
            if err:
                warn("Error generating embedding for output in child thread.")
                raise AIHeroException(err)
            stash_obj["inputs"] = inputs
            stash_obj["inputs_embedding"] = inputs_embedding

        if other is None:
            other = {}
        other.update({"embedding_model": "text-embedding-ada-002"})
        stash_obj["other"] = other

        self._client.post(
            f"/tools/promptstash/projects/{self._project_id}/prompt_templates/{template_id}/variants/{variant}/stash",
            obj=stash_obj,
            timeout=30,
        )
        print("Prompt stashed.")

    def stash(
        self,
        variant: str,
        prompt: str,
        output: str,
        inputs: str = None,
        other: dict = None,
    ):
        if has_key():
            Thread(
                target=self._sync_stash,
                args=(variant, prompt, output, inputs, other),
            ).start()
        else:
            raise AIHeroException("No OPENAI_API_KEY in env variables.")
