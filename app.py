from flask import Flask, render_template, request
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI()

# Assistant ID
assistant_id = "asst_77sJLLnZBt0D9fuN8FvEkXZE"

# Function to interact with the assistant
def ask_assistant(prompt):
    thread = client.beta.threads.create(
        messages=[{
            "role": "user",
            "content": prompt,
            "attachments": [],
        }]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant_id
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

    return message_content.value

# Route to render the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    assistant_response = None
    if request.method == 'POST':
        prompt = request.form['prompt']
        assistant_response = ask_assistant(prompt)

    return render_template('index.html', response=assistant_response)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
