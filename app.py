import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from resume_assessment import assess_resumes_for_jobs

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

"""
Update your xlsx file with colums 1 as 'Job Title' and column 2 as 'Skills Required' below 
so our program can use those requirements to judge and grade all the resumes. 
"""
JOB_SKILLS_PATH = 'job_skills.xlsx'         #update path here.

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/assess', methods=['POST'])
def assess_resumes():
    folder_path = request.form['folder_path']
    job_skills_df = pd.read_excel(JOB_SKILLS_PATH)
    results = assess_resumes_for_jobs(folder_path, job_skills_df)
    
    results_df = pd.DataFrame(results)
    results_df = results_df[results_df['Grade'] > 0]
    
    grouped = results_df.groupby('Resume').apply(lambda x: x.nlargest(3, 'Grade')).reset_index(drop=True)
    grouped['Average Grade'] = grouped.groupby('Resume')['Grade'].transform('mean')
    
    top_resumes_df = grouped.sort_values(by='Average Grade', ascending=False)
    
    return render_template('results.html', tables=[top_resumes_df.to_html(classes='data', header="true")])

if __name__ == "__main__":
    app.run(debug=True)
