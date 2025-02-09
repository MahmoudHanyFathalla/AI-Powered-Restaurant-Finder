from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from flask_cors import CORS  # Add this import
# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Initialize OpenAI client
client = OpenAI()

# Assistant ID
assistant_id = "asst_77sJLLnZBt0D9fuN8FvEkXZE"

# Function to interact with the assistant
def ask_assistant(prompt):
    try:
        # Create a thread
        thread = client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": prompt,
                "attachments": [],
            }]
        )

        # Get the response from the assistant
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant_id
        )

        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text

        # Process annotations and citations (if applicable)
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        return {"response": message_content.value}
    except Exception as e:
        return {"error": str(e)}

# Route to render the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    assistant_response = None
    if request.method == 'POST':
        prompt = request.form['prompt']
        result = ask_assistant(prompt)
        assistant_response = result.get("response") if "response" in result else result.get("error")

    return render_template('index.html', response=assistant_response)

# API Endpoint for external usage
@app.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request. 'prompt' is required."}), 400

    prompt = data['prompt']
    result = ask_assistant(prompt)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)


#http://127.0.0.1:5000/api/ask
#https://bf53-154-176-71-150.ngrok-free.app/api/ask