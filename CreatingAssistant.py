#creats assestans
from openai import OpenAI
import os

client = OpenAI()
 
assistant = client.beta.assistants.create(
  name="مشروع  للرعاية الصحية لنقابة المهندسين ",
  instructions="""
You are an AI assistant specialized in searching and extracting information about restaurants and their menus from text files. Your task is to help users find specific details about restaurants, such as their names, addresses, descriptions, and menu items, including the name, description, category, and price of each menu item.

When a user provides a query, you should:
1. Search the provided text file for relevant information.
2. Extract and present the information in a clear and organized manner.

For example, if a user asks for the menu of a specific restaurant, you should return the menu items along with their descriptions, categories, and prices.

Here is an example of the text file format you will be working with:

Restaurant: Chili's
Address: City Stars Center, Omar Ibn El Khattab St., Phase 1, 5th Floor, Nasr City, Cairo, Egypt
Description: American and Tex-Mex cuisine
Menu:
  - Name: Triple Dipper™
    Description: A trio of your favorite appetizers. Choose three from options like Chicken Crispers®, Boneless Buffalo Wings, Southwestern Eggrolls, and more.
    Category: Appetizers
    Price: 220 EGP

  - Name: Texas Cheese Fries
    Description: Loaded with melted cheese, jalapeños, green onions, and topped with crispy bacon. Served with ranch dressing.
    Category: Appetizers
    Price: 180 EGP

  - Name: Southwestern Eggrolls
    Description: Crispy flour tortillas stuffed with smoked chicken, black beans, corn, jalapeño Jack cheese, red peppers, and spinach. Served with avocado-ranch dressing.
    Category: Appetizers
    Price: 190 EGP

  - Name: Boneless Buffalo Chicken Salad
    Description: Crispy chicken tossed in spicy Buffalo sauce, served over a bed of fresh greens with bacon, bleu cheese crumbles, pico de gallo, and tortilla strips. Served with ranch dressing.
    Category: Salads
    Price: 210 EGP

  - Name: Quesadilla Explosion Salad
    Description: Grilled chicken, cheese, tomatoes, corn relish, and tortilla strips, served with cheese quesadillas.
    Category: Salads
    Price: 200 EGP

Use this format to guide your responses and ensure the information is accurate and well-organized.
""",
  model="gpt-4o-mini",
  tools=[{"type": "file_search"}],
)

# Store the assistant ID
assistant_id = assistant.id
print(f"Assistant ID: {assistant_id}")
# Create a vector store caled "Financial Statements"
vector_store = client.beta.vector_stores.create(name="مشروع  للرعاية الصحية لنقابة المهندسين")
 
# Specify the folder path containing multiple text files
folder_path = 'C:\\Users\\hp\\Downloads\\Restaurants_Data\\Data'

# Get a list of all text files in the specified folder
file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.txt')]

# Ready the files for upload to OpenAI
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)


 
# Create a thread with a question
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content":"i need Restaurants that do sharwama",
    }
  ],
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)
 
# The thread now has a vector store with that file in its tool resources.
print(thread.tool_resources.file_search)


# Use the create and poll SDK helper to create a run and poll the status of
# the run until it's in a terminal state.

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)

messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

message_content = messages[0].content[0].text
annotations = message_content.annotations
citations = []
for index, annotation in enumerate(annotations):
    message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
    if file_citation := getattr(annotation, "file_citation", None):
        cited_file = client.files.retrieve(file_citation.file_id)
        citations.append(f"[{index}] {cited_file.filename}")

print(message_content.value)
print("\n".join(citations))