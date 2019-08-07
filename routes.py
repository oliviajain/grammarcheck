from flask import Flask, request, render_template
from handwritingRecognition import convertToText, grammarAnalysis

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    path = request.form['pic']
    processed_path = path.lower()
    textualSubmission = convertToText(processed_path)
    total_errors, error_counts, mistake_info, flag = grammarAnalysis(textualSubmission)
    return display_report(total_errors, error_counts, mistake_info, flag)

def display_report(total_errors, error_counts, mistake_info, flag):
	return render_template('report.html', total_errors=total_errors, error_counts=error_counts, mistake_info=mistake_info, flag=flag)