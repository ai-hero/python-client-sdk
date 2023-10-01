# AI Hero Python SDK
The AI Hero Python SDK offers a powerful set of tools for managing and developing AI models. With our latest release, you can easily manage prompt templates and versions, allowing for easier and more effective model development, testing, and deployment.

AI Hero's PromptCraft and PromptStash helps you with:
- Prompt Creation: Define and format AI's interaction templates.
- Project Initialization: Quickly set up projects with a dedicated ID and API key.
- Version Control for Prompts: Easily stash, manage, and recall prompt variants.
- Track and Monitor AI Interactions: Document and visualize every AI interaction in real-time.
- Analysis and Oversight: Observe AI's steps and decision-making.
- Evaluation: Implement automated testing for AI's responses and compare your previous runs.
- Feedback System: Seamlessly log user feedback on AI outputs.

## Installation
Install AI Hero using pip:
```bash
pip install aihero==0.3.1
```

# PromptCraft
Are you a product manager navigating the dynamic AI space? Imagine having the power to track edits in a shared document, but for AI prompts. With prompt versioning, we can keep an eye on alterations, dip back into past iterations, and streamline updates. Ever wished you could pull up an older version of an AI prompt for clarity or comparison without diving deep into the technical weeds? "PromptCraft" is your ally, tailor-made to simplify the journey for those on the product side of things.

## How to use it
In a folder for your project, create a file `.env` containing the following API Keys:
```
OPENAI_API_KEY=<Your OpenAI API Key>
AI_HERO_PROJECT_ID=<Project ID from your project the AI Hero Website>
AI_HERO_PROJECT_API_KEY=<API Key for the project>
```

## Running PromptCraft
If you're using the Completions API:
```
aihero promptcraft completions
```

OR if you are using the Chat Completions API:
```
aihero promptcraft chat_completions
```

There's more coming soon!
- We're building a notebook for Retrieval Augmented Generation.
- Hit us up if you'd like a custom demo at `team@aihero.studio`.


