from flask import Flask, request, jsonify
from tasks import fill_form_task


app = Flask(__name__)

@app.route('/fill-form', methods=['POST'])
def fill_form():
    # Extract data from request
    user_data = request.json

    # Trigger the Celery task asynchronously and return task ID
    task = fill_form_task.delay(user_data)
    
    return jsonify({"status": "Form filling initiated", "task_id": task.id, 'success':True}), 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)