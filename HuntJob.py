# jobcopilot.py -job search assistant
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)

# tracks job search
applications = []
interview_questions = [
    "Tell me about a time you debugged something for days",
    "How do you learn new technologies?",
    "Describe a project you're proud of",
    "Why are you switching from AI to web dev?",
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Job Hunt Co-Pilot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: system-ui, sans-serif;
            background: #1a1a2e;
            margin: 0;
            padding: 20px;
            color: #eee;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            background: #16213e;
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #0f3460;
        }
        h1, h2 { color: #e94560; }
        .streak {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: #e94560;
        }
        .question-box {
            background: #0f3460;
            padding: 20px;
            border-radius: 16px;
            margin: 20px 0;
        }
        button {
            background: #e94560;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            background: #0f3460;
            border: 1px solid #e94560;
            border-radius: 8px;
            color: white;
            margin: 10px 0;
        }
        .application {
            background: #0f3460;
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
        }
        .rejection-counter {
            font-size: 24px;
            text-align: center;
            color: #e94560;
        }
        .tip {
            background: #e94560;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Job Hunt Co-Pilot</h1>
            <p>Built by an unemployed developer, for unemployed developers.</p>
            
            <div class="streak" id="streak">🔥 0 day streak</div>
            <div class="rejection-counter" id="rejections">Rejections: 0</div>
            <div style="text-align: center; font-size: 14px;">Each rejection = closer to yes</div>
        </div>
        
        <div class="card">
            <h2>📝 Log Today's Application</h2>
            <input type="text" id="company" placeholder="Company name">
            <input type="text" id="role" placeholder="Job title">
            <button onclick="logApplication()">Log It →</button>
        </div>
        
        <div class="card">
            <h2>Interview Question of the Day</h2>
            <div class="question-box" id="question">
                Click the button for a question
            </div>
            <button onclick="newQuestion()">Random Question</button>
            <textarea id="answer" rows="4" placeholder="Practice your answer here..."></textarea>
            <button onclick="saveAnswer()">Save My Answer</button>
        </div>
        
        <div class="card">
            <h2>Activity</h2>
            <div id="applications"></div>
        </div>
        
        <div class="card">
            <div class="tip">
                💡 <strong>Your AI edge:</strong> Most web devs can't explain AI. You can. Use that.
            </div>
        </div>
    </div>
    
    <script>
        let applications = [];
        let rejections = 0;
        let streak = 0;
        
        function loadData() {
            fetch('/data')
                .then(r => r.json())
                .then(data => {
                    applications = data.applications;
                    rejections = data.rejections;
                    streak = data.streak;
                    updateUI();
                });
        }
        
        function logApplication() {
            const company = document.getElementById('company').value;
            const role = document.getElementById('role').value;
            
            if (!company || !role) return;
            
            fetch('/application', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({company, role, date: new Date().toISOString()})
            }).then(() => {
                document.getElementById('company').value = '';
                document.getElementById('role').value = '';
                loadData();
            });
        }
        
        function newQuestion() {
            fetch('/random-question')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('question').innerHTML = data.question;
                });
        }
        
        function saveAnswer() {
            const answer = document.getElementById('answer').value;
            const question = document.getElementById('question').innerText;
            
            fetch('/save-answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question, answer})
            }).then(() => {
                alert('Answer saved! Keep practicing.');
            });
        }
        
        function updateUI() {
            const appsDiv = document.getElementById('applications');
            appsDiv.innerHTML = applications.slice(-5).reverse().map(app => `
                <div class="application">
                    📧 ${app.company} - ${app.role}<br>
                    <small>Applied: ${new Date(app.date).toLocaleDateString()}</small>
                </div>
            `).join('');
            
            document.getElementById('streak').innerHTML = `🔥 ${streak} day streak`;
            document.getElementById('rejections').innerHTML = `Rejections: ${rejections}`;
            
            if (applications.length === 0) {
                appsDiv.innerHTML = '<div class="application">No applications yet. Send one today!</div>';
            }
        }
        
        newQuestion();
        loadData();
        
        // Daily reminder
        if (applications.length === 0) {
            setTimeout(() => alert("Don't wait for ready. Apply to one job today."), 1000);
        }
    </script>
</body>
</html>
'''

# In-memory storage (replace with file later)
user_data = {
    'applications': [],
    'rejections': 0,
    'streak': 0,
    'answers': []
}

@app.route('/')
def index():
    return HTML

@app.route('/data')
def get_data():
    return jsonify(user_data)

@app.route('/application', methods=['POST'])
def add_application():
    data = request.json
    user_data['applications'].append(data)
    
    # Simple streak calculation
    last_app = user_data['applications'][-2] if len(user_data['applications']) > 1 else None
    if last_app:
        last_date = datetime.fromisoformat(last_app['date'])
        today = datetime.now()
        if (today - last_date).days == 1:
            user_data['streak'] += 1
        elif (today - last_date).days > 1:
            user_data['streak'] = 1
    else:
        user_data['streak'] = 1
    
    return jsonify({'success': True})

@app.route('/random-question')
def random_question():
    return jsonify({'question': random.choice(interview_questions)})

@app.route('/save-answer', methods=['POST'])
def save_answer():
    data = request.json
    user_data['answers'].append(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)