import os
import fitz
import docx
import re
import pandas as pd
from docx import Document

skills_relation = {
    'Java': ['Python', 'C++', 'C#', 'Kotlin', 'Scala'],
    'AWS': ['Azure', 'Google Cloud', 'OpenStack', 'Oracle Cloud'],
    'Machine Learning': ['Deep Learning', 'Data Science', 'Natural Language Processing', 'Reinforcement Learning'],
    'Web Development': ['Frontend', 'Backend', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask'],
    'SQL': ['MySQL', 'PostgreSQL', 'SQLite', 'Oracle', 'SQL Server'],
    'Networking': ['TCP/IP', 'Firewalls', 'DNS', 'Load Balancers', 'VPN'],
    'Agile': ['Scrum', 'Kanban', 'XP', 'SAFe'],
    'Security': ['Penetration Testing', 'Encryption', 'Security Auditing', 'SOC', 'Compliance'],
    'Cloud Computing': ['Google Cloud', 'Azure', 'AWS', 'IBM Cloud', 'Alibaba Cloud'],
    'Data Analysis': ['Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'R', 'Excel'],
    'JavaScript': ['TypeScript', 'Node.js', 'React', 'Vue.js', 'Angular', 'jQuery'],
    'C++': ['C#', 'Objective-C', 'Rust', 'Go'],
    'Python': ['Ruby', 'Perl', 'R', 'Julia'],
    'C#': ['Java', 'F#', '.NET', 'VB.NET'],
    'Swift': ['Objective-C', 'Kotlin', 'Dart'],
    'Ruby': ['Python', 'Perl', 'Elixir'],
    'Go': ['Rust', 'D', 'C'],
    'PHP': ['JavaScript', 'Hack', 'Laravel', 'Symfony'],
    'Rust': ['C++', 'Swift', 'Go', 'D'],
    'Data Engineering': ['Hadoop', 'Spark', 'Kafka', 'Flink', 'Airflow'],
    'DevOps': ['Docker', 'Kubernetes', 'Jenkins', 'Ansible', 'Terraform', 'Puppet'],
    'Mobile Development': ['Android', 'iOS', 'Flutter', 'React Native'],
    'Business Intelligence': ['Tableau', 'Power BI', 'Looker', 'QlikView'],
    'UI/UX Design': ['Sketch', 'Figma', 'Adobe XD', 'InVision'],
    'Blockchain': ['Ethereum', 'Hyperledger', 'Solidity', 'Chaincode'],
    'Big Data': ['Hadoop', 'Spark', 'Hive', 'Pig'],
    'Testing': ['Selenium', 'JUnit', 'TestNG', 'Cucumber'],
    'Game Development': ['Unity', 'Unreal Engine', 'Godot'],
    'System Administration': ['Linux', 'Windows Server', 'Active Directory', 'Bash', 'PowerShell'],
    'AI': ['Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'Reinforcement Learning'],
    'Robotics': ['ROS', 'OpenCV', 'Gazebo'],
    'IoT': ['Arduino', 'Raspberry Pi', 'MQTT'],
    'CRM': ['Salesforce', 'Zoho CRM', 'HubSpot'],
    'ERP': ['SAP', 'Oracle ERP', 'Microsoft Dynamics'],
    'Project Management': ['JIRA', 'Trello', 'Asana'],
    'Version Control': ['Git', 'SVN', 'Mercurial'],
    'CI/CD': ['Jenkins', 'Travis CI', 'CircleCI'],
    'Web Frameworks': ['Django', 'Flask', 'Ruby on Rails', 'Spring'],
    'Containers': ['Docker', 'Kubernetes'],
    'Automation': ['Ansible', 'Puppet', 'Chef']
}

def extract_text_from_pdf(pdf_path):
    text = ""
    document = fitz.open(pdf_path)
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def match_keywords(resume_text, required_skills):
    matches = [skill for skill in required_skills if re.search(rf"\b{skill}\b", resume_text, re.IGNORECASE)]
    return matches

def infer_skills(existing_skills, required_skills):
    inferred_skills = []
    for required_skill in required_skills:
        if required_skill not in existing_skills:
            for skill in existing_skills:
                if skill in skills_relation and required_skill in skills_relation[skill]:
                    inferred_skills.append(required_skill)
                    break
    return inferred_skills

def resume_grader(assessment, required_skills):
    value_counts = {}
    for key, value in assessment.items():
        count = len([item for item in value if item])
        value_counts[key] = count
    return ((((value_counts['matched_skills']) * 1 + (value_counts['inferred_skills']) * 0.5) / len(required_skills)) * 100)

def assess_resume(file_path, required_skills):
    if file_path.endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        resume_text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported File Format, Please upload a .PDF or a .DOCX file.")

    matched_skills = match_keywords(resume_text, required_skills)
    unmatched_skills = set(required_skills) - set(matched_skills)
    existing_skills = match_keywords(resume_text, skills_relation.keys())
    inferred_skills = infer_skills(existing_skills, unmatched_skills)

    assessment = {
        "matched_skills": matched_skills,
        "inferred_skills": inferred_skills
    }

    grade = resume_grader(assessment, required_skills)
    assessment['grade'] = grade

    return assessment

def assess_resumes_for_jobs(folder_path, job_skills_df):
    results = []
    for index, row in job_skills_df.iterrows():
        job_title = row['Job Title']
        required_skills = row['Skills Required'].split(', ')
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if file_path.endswith('.pdf') or file_path.endswith('.docx'):
                try:
                    assessment = assess_resume(file_path, required_skills)
                    results.append({
                        'Job Title': job_title,
                        'Resume': filename,
                        'Matched Skills': ', '.join(assessment['matched_skills']),
                        'Inferred Skills': ', '.join(assessment['inferred_skills']),
                        'Grade': assessment['grade']
                    })
                except ValueError as e:
                    results.append({
                        'Job Title': job_title,
                        'Resume': filename,
                        'Error': str(e)
                    })
    return results
