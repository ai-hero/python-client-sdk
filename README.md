# AI Hero Python SDK
*Go from Zero to ML in minutes.*

With [AI Hero](https://aihero.studio), you can protototype ML models to power your product features, automate routine tasks, and analyze customer feedback - all with a simple, no-code, self-serve platform. Choose from our growing list of automations to tag text, recommend products, tag images, detect customer sentiment, and other tasks!

## Usage
1. First, create an account on the [AI Hero Platform](https://api.aihero.studio).
2. Create an automation and train it. 
3. Create an API Key on the platform (from the menu on the left when inside your automation).
4. Install this library.
5. Start using it:

```python
from aihero import Client

# Create the client, which connects to AI Hero server.
client = Client()

# Get the automation object, using the automation id and your API key for that automation. 
automation = client.get_automation(automation_id='<YOUR_AUTOMATION_ID>',  api_key='<YOUR_API_KEY>')

# Predict using your trained automation.
# For example, for detecting sentiment in short text:
prediction = automation.predict(text="This works great!")

# predction object:
# {'explanation': 'The sentiment is positive', 'tags': {'negative': 0.00013113021850585938, 'positive': 0.9998688697814941}}

# Add more data to your trained model.
automation.add(text="It's great that I can add an example to the model.", guid="<SHARED_ID_FOR_TRACKING_DATA>")

```

