from flask import Flask, request, render_template
from apis import convert_to_text, grammar_analysis

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def form_post():
    path = request.form['pic']
    processed_path = path.lower()
    textual_submission = convert_to_text(processed_path)
    total_errors, error_counts, mistake_info, flag = grammar_analysis(textual_submission)
    return display_report(total_errors, error_counts, mistake_info, flag)

def display_report(total_errors, error_counts, mistake_info, flag):
	return render_template(
		'report.html',
		total_errors=total_errors,
		error_counts=error_counts, 
		mistake_info=mistake_info, 
		flag=flag)