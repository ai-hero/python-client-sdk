# Copyright (c) 2024 A.I. Hero, Inc.
# All Rights Reserved.
#
# This software and associated documentation files (the "Software") are provided "as is", without warranty
# of any kind, express or implied, including but not limited to the warranties of merchantability, fitness
# for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be
# liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise,
# arising from, out of, or in connection with the Software or the use or other dealings in the Software.
#
# Unauthorized copying of this file, via any medium, is strictly prohibited.

"""Helper functions for pydantic schemas."""

import json
from abc import ABC
from copy import deepcopy
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import validators
from pydantic import BaseModel, Field, SerializeAsAny, root_validator
from url_normalize import url_normalize


def normalize_title(title: str) -> str:
    """Normalize the title."""
    # List of common words that should not be capitalized unless they are the first word
    common_words = {
        "a",
        "an",
        "and",
        "but",
        "for",
        "nor",
        "or",
        "so",
        "yet",
        "at",
        "by",
        "in",
        "into",
        "of",
        "on",
        "onto",
        "out",
        "over",
        "the",
        "to",
        "with",
    }

    # Split the title into words
    words = title.split()

    # Capitalize the first word and preserve abbreviations
    normalized_words = [words[0].capitalize() if not words[0].isupper() else words[0]]

    # Process the remaining words
    for word in words[1:]:
        # Capitalize if not a common word and not all uppercase (preserve abbreviations)
        if word.lower() in common_words and not word.isupper():
            normalized_words.append(word.lower())
        else:
            normalized_words.append(word.capitalize() if not word.isupper() else word)

    # Join the normalized words back into a string
    normalized_title = " ".join(normalized_words)
    return normalized_title


def normalize_markdown_titles(markdown: str) -> str:
    """Normalize the titles in the markdown."""
    lines = markdown.split("\n")
    normalized_lines = []

    for line in lines:
        if line.startswith("#"):
            parts = line.split(" ", 1)
            if len(parts) > 1:
                normalized_title = normalize_title(parts[1])
                normalized_lines.append(f"{parts[0]} {normalized_title}")
            else:
                normalized_lines.append(line)
        else:
            normalized_lines.append(line)

    return "\n".join(normalized_lines)


class ModeEnum(str, Enum):
    """Mode enum indicating the various operational modes."""

    EDITING = "editing"
    EXPECTS = "expects"
    PROCESSING = "processing"
    OUTPUT = "output"
    IMPROVE = "improve"
    IMPROVING = "improving"


class TypeEnum(str, Enum):
    """Step type enum indicating the type of step."""

    INSTRUCTION = "instruction"
    MARKDOWN = "markdown"
    IMAGE = "image"
    CHAT = "chat"
    NOTE = "note"
    WEBPAGES = "webpages"
    FILES = "files"
    OBJECT = "object"
    QUERY = "query"


class Step(BaseModel, ABC):
    """Step schema defining a step in the workflow."""

    step_id: Optional[str] = Field(
        ...,
        title="Step ID",
        description="Unique identifier for the step",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Optional description of the step",
    )
    type: TypeEnum = Field(
        default=TypeEnum.MARKDOWN,
        title="Type",
        description="Type of the step, defined by TypeEnum",
    )
    mode: ModeEnum = Field(
        default=ModeEnum.OUTPUT,
        title="Mode",
        description="Mode of the step, defined by ModeEnum",
    )
    error: Optional[str] = Field(
        None,
        title="Error",
        description="Optional error message associated with the step",
    )

    @root_validator(pre=True)
    def check_step_id(cls, values: Any) -> Any:
        """Check if step_id is present."""
        if "step_id" not in values or not values["step_id"]:
            values["step_id"] = str(uuid4())
        return values

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Step":
        """Generate child class object."""
        step_type = data.get("type")
        if step_type == TypeEnum.INSTRUCTION:
            return Instruction(**data)
        elif step_type == TypeEnum.MARKDOWN:
            return Markdown(**data)
        elif step_type == TypeEnum.IMAGE:
            return Image(**data)
        elif step_type == TypeEnum.CHAT:
            return Chat(**data)
        elif step_type == TypeEnum.NOTE:
            return Note(**data)  # Assuming a generic Step for DOCUMENTATION
        elif step_type == TypeEnum.WEBPAGES:
            return Webpages(**data)
        elif step_type == TypeEnum.FILES:
            return Files(**data)
        elif step_type == TypeEnum.OBJECT:
            return JObject(**data)
        elif step_type == TypeEnum.QUERY:
            return Search(**data)
        else:
            raise ValueError(f"Unknown step type: {step_type} in step {data}")


class Markdown(Step):
    """Markdown step schema extending the Step schema."""

    markdown: str = Field(
        ...,
        title="Markdown",
        description="Markdown content of the step",
    )

    @root_validator(pre=True)
    def check_markdown(cls, values: Any) -> Any:
        """Normalize the markdown."""
        values["markdown"] = normalize_markdown_titles(values["markdown"])
        return values


class Instruction(Step):
    """Instruction step schema extending the Step schema."""

    instruction: str = Field(
        ...,
        title="Instruction",
        description="The instruction to generate content with.",
    )
    markdown: Optional[str] = Field(
        None,
        title="Markdown",
        description="Markdown content of the step",
    )
    mute: bool = Field(
        default=False,
        title="Mute",
        description="Indicates if the instruction is muted",
    )
    pinned: bool = Field(
        default=False,
        title="Pinned",
        description="Indicates if the instruction is pinned",
    )
    feedback: Optional[str] = Field(
        None,
        title="Feedback",
        description="Optional feedback for the instruction",
    )
    partial: bool = Field(
        default=False,
        title="Partial",
        description="Indicates if the step is partial",
    )
    computed_at: Optional[int] = Field(
        None,
        title="Computed At",
        description="Timestamp when the workflow was computed",
    )

    @root_validator(pre=True)
    def check_instruction(cls, values: Any) -> Any:
        """Normalize the instruction."""
        if values.get("markdown"):
            values["markdown"] = normalize_markdown_titles(values["markdown"])
        return values


class Image(Step):
    """Image step schema extending the Step schema."""

    instruction: str = Field(
        ...,
        title="Instruction",
        description="The instruction to generate image with.",
    )
    filename: Optional[str] = Field(
        None,
        title="Filename",
        description="Filename of the image generated",
    )


class Webpages(Step):
    """Webpages step schema extending the Step schema."""

    urls: List[str] = Field(
        ...,
        title="URLs",
        description="List of webpages to analyze.",
    )
    metadata_webpages: Optional[Dict[str, Any]] = Field(
        None,
        title="Metadata Webpages",
        description="Optional metadata for the webpages",
    )
    processed_webpages: Optional[Dict[str, str]] = Field(
        None,
        title="Processed Webpages",
        description="Optional processed content of the webpages",
    )
    reload: Optional[bool] = Field(
        default=False,
        title="Reload",
        description="Indicates if the webpages should be reloaded",
    )

    @root_validator(pre=True)
    def check_webpage(cls, values: Any) -> Any:
        """Normalize the webpage."""
        if "urls" not in values:
            values["urls"] = []
        for url in values["urls"]:
            if not validators.url(url):
                raise ValueError(f"Invalid URL {url}")
        values["urls"] = [url_normalize(url) for url in values["urls"]]
        if "processed_webpages" not in values:
            values["processed_webpages"] = {}
        if "metadata_webpages" not in values:
            values["metadata_webpages"] = {}
        return values


class Files(Step):
    """Files step schema extending the Step schema."""

    files: List[str] = Field(
        ...,
        title="Files",
        description="List of filenames to analyze.",
    )
    processed_files: Optional[Dict[str, str]] = Field(
        None,
        title="Processed Files",
        description="Optional processed content of the files",
    )
    metadata_files: Optional[Dict[str, Any]] = Field(
        None,
        title="Metadata Files",
        description="Optional metadata for the files",
    )
    reload: Optional[bool] = Field(
        default=False,
        title="Reload",
        description="Indicates if the files should be reloaded",
    )

    @root_validator(pre=True)
    def check_files(cls, values: Any) -> Any:
        """Normalize the files."""
        if "files" not in values:
            values["files"] = []
        for filename in values["files"]:
            # Normalize file names and remove ../
            if "/./" in filename:
                raise ValueError(f"Invalid filename {filename}")
            if "/../" in filename:
                raise ValueError(f"Invalid filename {filename}")
            values["files"] = [Path(filename).name for filename in values["files"]]
        if "processed_files" not in values:
            values["processed_files"] = {}
        if "metadata_files" not in values:
            values["metadata_files"] = {}

        return values


class JObject(Step):
    """JSON step schema extending the Step schema."""

    json_schema: Dict[str, Any] = Field(
        ...,
        title="Schema",
        description="The json schema to generate output with.",
    )
    json_object: Optional[Dict[str, Any]] = Field(
        None,
        title="Object",
        description="The object dict generated.",
    )
    partial: bool = Field(
        default=False,
        title="Partial",
        description="Indicates if the step is partial",
    )
    computed_at: Optional[int] = Field(
        None,
        title="Computed At",
        description="Timestamp when the workflow was computed",
    )

    @root_validator(pre=True)
    def check_json(cls, values: Any) -> Any:
        """Normalize the json."""
        if "json_schema" not in values:
            values["json_schema"] = {}
        if "json_object" not in values:
            values["json_object"] = {}
        return values

    def llm_string(self, content_cache: Optional[Dict[str, str]]) -> str:
        """Return the string needed for LLM."""
        to_return = f"<schema>{json.dumps(self.json_schema, indent=2)}<schema>"
        if self.json_object:
            to_return += f"<object>{json.dumps(self.json_object, indent=2)}<objcet>"
        return to_return


class Chat(Step):
    """Chat step schema extending the Step schema."""

    messages: List[Dict[str, Any]] = Field(
        ...,
        title="Messages",
        description="List of messages in the chat",
    )
    partial: bool = Field(
        default=False,
        title="Partial",
        description="Indicates if the step is partial",
    )
    computed_at: Optional[int] = Field(
        None,
        title="Computed At",
        description="Timestamp when the workflow was computed",
    )

    @root_validator(pre=True)
    def check_chat(cls, values: Any) -> Any:
        """Normalize the chat."""
        if "messages" not in values:
            values["messages"] = []
        return values


class Search(Step):
    """Search step schema extending the Step schema."""

    query: str = Field(
        ...,
        title="Search Query",
        description="The search query",
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        title="Search Result",
        description="The search result generated.",
    )
    partial: bool = Field(
        default=False,
        title="Partial",
        description="Indicates if the step is partial",
    )
    computed_at: Optional[int] = Field(
        None,
        title="Computed At",
        description="Timestamp when the workflow was computed",
    )

    @root_validator(pre=True)
    def check_search(cls, values: Any) -> Any:
        """Normalize the search."""
        if "query" not in values:
            values["query"] = ""
        return values


class Note(Step):
    """Documentation that the agent doesn't see. For humans."""

    markdown: str = Field(
        ...,
        title="Note",
        description="The note",
    )

    @root_validator(pre=True)
    def check_note_markdown(cls, values: Any) -> Any:
        """Normalize the markdown."""
        values["markdown"] = normalize_markdown_titles(values["markdown"])
        return values


class StatusEnum(str, Enum):
    """Status enum indicating the status of the workflow."""

    SUCCESS = "success"
    PENDING = "pending"
    RUNNING = "running"
    ABORTED = "aborted"
    FAILED = "failed"


class KindEnum(str, Enum):
    """Kind enum indicating the kind of workflow."""

    SIMPLE = "simple"
    AUTOMATED = "automated"


class Workflow(BaseModel):
    """Workflow schema defining a workflow."""

    # Workflow related fields
    kind: KindEnum = Field(
        default=KindEnum.SIMPLE,
        title="Kind",
        description="The kind of workflow",
    )
    project_id: str = Field(
        ...,
        title="Project ID",
        description="Unique identifier for the project",
    )
    workflow_id: str = Field(
        ...,
        title="Workflow ID",
        description="Unique identifier for the workflow",
    )
    name: str = Field(
        ...,
        title="Name",
        description="Name of the workflow",
    )
    description: str = Field(
        ...,
        title="Description",
        description="Description of the workflow",
    )
    status: StatusEnum = Field(
        default=StatusEnum.SUCCESS,
        title="Status",
        description="Current status of the workflow",
    )
    steps: List[SerializeAsAny[Step]] = Field(
        default_factory=list,
        title="Steps",
        description="List of steps in the workflow",
    )
    computed_at: Optional[int] = Field(
        None,
        title="Computed At",
        description="Timestamp when the workflow was computed",
    )
    pinned: bool = Field(
        default=False,
        title="Pinned",
        description="Indicates if the workflow is pinned",
    )
    stage: str = Field(
        default="test",
        title="Stage",
        description="Current stage of the workflow",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        title="Created At",
        description="Timestamp when the workflow was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        title="Updated At",
        description="Timestamp when the workflow was last updated",
    )
    archived: bool = Field(
        default=False,
        title="Archived",
        description="Indicates if the workflow is archived",
    )

    # Run related fields
    run_id: Optional[str] = Field(
        None,
        title="Run ID",
        description="Unique identifier for the run",
    )
    account_id: Optional[str] = Field(
        None,
        title="Account ID",
        description="Unique identifier for the account",
    )
    model_used: Optional[str] = Field(
        None,
        title="Model Used",
        description="Model used for the workflow",
    )
    start_at: Optional[datetime] = Field(
        None,
        title="Start At",
        description="Timestamp when the workflow started",
    )
    end_at: Optional[datetime] = Field(
        None,
        title="End At",
        description="Timestamp when the workflow ended",
    )
    run_time: Optional[float] = Field(
        None,
        title="Run Time",
        description="Total run time of the workflow",
    )
    version: Optional[int] = Field(
        None,
        title="Version",
        description="Version of the workflow",
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """Create a Workflow instance from a dictionary."""
        data_copy = deepcopy(data)
        steps_data = data_copy.get("steps", [])
        steps = [Step.from_dict(step) for step in steps_data]
        data_copy["steps"] = steps
        return cls(**data_copy)


class Project(BaseModel):
    project_id: str = Field(
        ...,
        title="Project ID",
        description="Unique identifier for the project",
    )
    name: str = Field(
        ...,
        title="Name",
        description="Name of the project",
    )
    description: str = Field(
        ...,
        title="Description",
        description="Description of the project",
    )
    thumbnail: str = Field(
        "",
        title="Thumbnail",
        description="Thumbnail of the project",
    )
    subscription: Dict[str, Any] = Field(
        {},
        title="Subscription",
        description="Subscription details of the project",
    )
    archived: bool = Field(
        default=False,
        title="Archived",
        description="Indicates if the project is archived",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        title="Created At",
        description="Timestamp when the project was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        title="Updated At",
        description="Timestamp when the project was last updated",
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create a Workflow instance from a dictionary."""
        data_copy = deepcopy(data)
        return cls(**data_copy)
