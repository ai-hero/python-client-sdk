# AI Hero Python SDK
*Go from Zero to ML in minutes.*

With [AI Hero](https://aihero.studio), you can protototype ML models to power your product features, automate routine tasks, and analyze customer feedback - all with a simple, no-code, self-serve platform. Choose from our growing list of automations to tag text, recommend products, tag images, detect customer sentiment, and other tasks!

# Usage

## Creating an Automation with this Python API.

1. First, install this library.
```shell
pip install aihero
```

2. Establish a connection to AI Hero in your Python program.
```python
from aihero import Client
aihero_client = Client()
```

3. To create an automation, you'll need a temporary authorization key to your workspace. 
```python
aihero_client.request_auth_secret(email="<YOUR_EMAIL_ADDRESS>")

# You'll be sent a auth_key in your email. Use it to get access to your workspace. 
# This auth_key is valid ONLY for two hours and meant as a temporary access. 
# Once you create the automation, you'll be able to create and use an API key that will last longer.

workspace = aihero_client.get_workspace(auth_secret="<AUTH_KEY_FROM_EMAIL>")
```

4. Next create an automation from the types available. See the next section for all types supported.
```python
automation = workspace.create_automation(
        automation_type="detect_sentiment", 
        name="Detect sentiment in customer reviews", 
        description="Find customer sentiment in online reviews submitted by customers."
    )

# Get your automation id.
automation_id = automation["_id"]
``` 

The next time, you can use the API key you can find on the web console to get access to the automation directly:
```python
# Get the automation object, using the automation id and your API key for that automation. 
automation = aihero_client.get_automation(automation_id='<YOUR_AUTOMATION_ID>',  api_key='<YOUR_API_KEY>')
```

5. Start using it:
```python
# Predict using your trained automation.
# For example, for detecting sentiment in short text:
prediction = automation.predict(text="This works great!")

# predction object:
# {'explanation': 'The sentiment is positive', 'tags': {'negative': 0.00013113021850585938, 'positive': 0.9998688697814941}}
```

## Predicting using an Automation created on the [AI Hero Platform](https://api.aihero.studio).
1. We assume you have created an automation on [AI Hero Platform](https://api.aihero.studio) and trained it.
2. Create an API Key on the platform (from the menu on the left when inside your automation).
3. Install this library.
```shell
pip install aihero
```

4. Start using the automation:
```python
from aihero import Client

# Create the client, which connects to AI Hero server.
aihero_client = Client()

# Get the automation object, using the automation id and your API key for that automation. 
automation = aihero_client.get_automation(automation_id='<YOUR_AUTOMATION_ID>',  api_key='<YOUR_API_KEY>')

# Predict using your trained automation.
# For example, for detecting sentiment in short text:
prediction = automation.predict(text="This works great!")

# predction object:
# {'explanation': 'The sentiment is positive', 'tags': {'negative': 0.00013113021850585938, 'positive': 0.9998688697814941}}

# Add more data to your trained model.
automation.add(text="It's great that I can add an example to the model.", guid="<SHARED_ID_FOR_TRACKING_DATA>")

```


# Available Automations with the API

## Detect Sentiment in Short Text

1. Creating an automation with the API if you havent already:
```python
automation = workspace.create_automation(
        automation_type="detect_sentiment", 
        name="Detect sentiment in customer reviews", 
        description="Find customer sentiment in online reviews submitted by customers."
    )
```

2. Start using it! No training required. 
```python
# Predict using your trained automation.
# For example, for detecting sentiment in short text:
prediction = automation.predict(text="This works great!")

# predction object:
# {'explanation': 'The sentiment is positive', 'tags': {'negative': 0.00013113021850585938, 'positive': 0.9998688697814941}}
```


## Tag Short Text
1. Creating an automation with the API if you havent already:
```python
automation = workspace.create_automation(
        automation_type="tag_short_text", 
        name="<NAME_YOUR_MODEL>", 
        description="<DESCRIBE_WHAT_YOUR_MODEL_WILL_DO>"
    )
```
2. Set the tags you want to tag your model with:
```python
automation.set_tags(['<TAG/CATEGORY 1>', '<TAG/CATEGORY 2>', '<TAG/CATEGORY 3>'])

print(automation.get_tags())
```


3. Add the data to train the model with:
```python
automation.add(
    text="It's great that I can add training data to the model.", 
    guid="<SHARED_ID_FOR_TRACKING_DATA>"
)
```

4. Trigger the learning:
```python
# Trigger relearn. You'll be notified when the automation is ready for review. 
relearning_job = automation.relearn()

# To check the status.
print(automation.get_status(relearning_job))
```

5. Start using it!
```python
# Predict using your trained automation.
prediction = automation.predict(text="This works great!")
```


## Tag Entire Images
1. Creating an automation with the API if you havent already:
```python
automation = workspace.create_automation(
        automation_type="tag_entire_images", 
        name="<NAME_YOUR_MODEL>", 
        description="<DESCRIBE_WHAT_YOUR_MODEL_WILL_DO>"
    )
```
2. Set the tags you want to tag your model with:
```python
automation.set_tags(['<TAG/CATEGORY 1>', '<TAG/CATEGORY 2>', '<TAG/CATEGORY 3>'])

print(automation.get_tags())
```

3. Add the data to train the model with:
```python
automation.add(image_url="<IMAGE_URL>", guid="<SHARED_ID_FOR_TRACKING_DATA>")
```

4. Trigger the learning:
```python
# Trigger relearn. You'll be notified when the automation is ready for review. 
relearning_job = automation.relearn()

# To check the status.
print(automation.get_status(relearning_job))
```

5. Start using it!
```python
# Predict using your trained automation.
prediction = automation.predict(image_url="<IMAGE_URL>")
```

# Improving your Automations.
To improve the automation, teach it with feedback on how it has learned:
```python
# Trigger relearn. You'll be notified when the automation is ready for review. 
relearning_job = automation.relearn()

# To check the status.
print(automation.get_status(relearning_job))
```

Once you've been notified. Use the UI to teach the automation by giving feedback on the predictions. 


You can also add more data to train the model with:
```python
automation.add(
    text="More data training data to the model.",
    guid="<SHARED_ID_FOR_TRACKING_DATA>"
)
```


# Pricing.
Please check your automation at [AI Hero Platform](https://api.aihero.studio) for pricing information to the model. 
