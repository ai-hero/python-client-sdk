# AI Hero Python SDK
*Go from Zero to ML in minutes.*

With [AI Hero](https://aihero.studio), you can protototype automations to power your product features, automate routine tasks, and analyze customer feedback - all with a simple python library or our no-code, self-serve platform. 

An automation is an abstraction of an ML model. Apart from training data, it may include a database, heuristics, business logic, etc.

Choose from our growing list of automations to tag text, recommend products, tag images, detect customer sentiment, and other tasks!

# Usage

## Using an automation created on the [AI Hero Platform](https://api.aihero.studio) with this Python API.

1. First, install this library.
```shell
pip install aihero
```

2. Establish a connection to AI Hero in your Python program.
```python
from aihero import Client
aihero_client = Client()
```

3. We recommend you use the [AI Hero Platform](https://api.aihero.studio) to create your automation. For example, we can create an automation to detect sentiment in short text. 


4. Using the platform, you can create an API key. Use it with this python API to get access to your automation.
```python
# Get the automation object, using the automation id and your API key for that automation. 
automation = aihero_client.get_automation(automation_id='<YOUR_AUTOMATION_ID>',  api_key='<YOUR_API_KEY>')
```

5. To start using your automation, you can use the predict function.
```python
# Predict using your trained automation.
# For example, for detecting sentiment in short text:
prediction = automation.predict(guid="<UNIQUE_ID>", text="This works great!")

# predction object:
# {'explanation': 'The sentiment is positive', 'tags': {'negative': 0.00013113021850585938, 'positive': 0.9998688697814941}}
```


# Available Automations with the API
To use any of the automations below, please create one on the platform if you havent already, and get your API key.

## Detect Sentiment in Short Text
The sentiment detection automation does not need any training and is ready to use. 
```python
# Predict using your trained automation.
# For example, for detecting sentiment in short text:
prediction = automation.predict(guid="<UNIQUE_ID>", text="This works great!")

# predction object:
# {'explanation': 'The sentiment is positive', 'tags': {'negative': 0.00013113021850585938, 'positive': 0.9998688697814941}}
```


## Tag Short Text
1. Set the tags you want to tag your model with:
```python
automation.set_tags(['<TAG/CATEGORY 1>', '<TAG/CATEGORY 2>', '<TAG/CATEGORY 3>'])

print(automation.get_tags())
```

2. Add the texts to train the model with:
```python
automation.add_short_text(
    guid="<UNIQUE_ID>", 
    text="It's great that I can add training data to the model."
)
```

3. You can then trigger AI Hero so that it will try to understand the data. Without feedback or ground truth, AI Hero attempts its best prediction based on its understanding of the data. With enough feedback or ground truth, AI Hero will use Machine Learning to fit a model to your data. 
```python
# Trigger understanding. You'll be notified when the automation is ready. 
understanding_job = automation.understand()

# To check the status.
print(automation.get_status(understanding_job))
```

4. Once you get an email notifying you that your automation is ready, you can start using it with the API.
```python
# Predict using your trained automation.
prediction = automation.predict(guid="<UNIQUE_ID>", text="This works great!")
```

## Tag Entire Images
1. Set the tags you want to tag your model with:
```python
automation.set_tags(['<TAG/CATEGORY 1>', '<TAG/CATEGORY 2>', '<TAG/CATEGORY 3>'])

print(automation.get_tags())
```

2. Add the images to train the model with:
```python
automation.add_image(guid="<UNIQUE_ID>", image_url="<IMAGE_URL>")
```

3. You can then trigger AI Hero so that it will try to understand the data. Without feedback or ground truth, AI Hero attempts its best prediction based on its understanding of the data. With enough feedback or ground truth, AI Hero will use Machine Learning to fit a model to your data. 
```python
# Trigger understanding. You'll be notified when the automation is ready. 
understanding_job = automation.understand()

# To check the status.
print(automation.get_status(understanding_job))
```

5. Once you get an email notifying you that your automation is ready, you can start using it with the API.
```python
# Predict using your trained automation.
prediction = automation.predict(guid="<UNIQUE_ID>", image_url="<IMAGE_URL>")
```

# Improving your Automations.
While AI Hero does the best job it can, it may need some more examples to improve. In the email you get when learning is completed, click on the link in the email to teach the automation by giving feedback on the predictions. 

You can also add more ground truth examples for it to learn with:
```python
automation.set_ground_truth(
    guid="<UNIQUE_ID>",
    ground_truth={"<TAG/CATEGORY 1>": True, "<TAG/CATEGORY 2>": False, "<TAG/CATEGORY 3>": True}
)
```

# Pricing.
Please check your automation at [AI Hero Platform](https://api.aihero.studio) for pricing information to the automation. 
