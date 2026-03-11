# Sample CVs for Testing CVFoster

This directory contains sample CV files for testing the CVFoster application.

## Available Samples

### 1. Sample_CV_1_John_Doe.txt
- **Profile**: Senior Software Engineer with 7+ years experience
- **Key Skills**: Python, JavaScript, AWS, Docker, Full-Stack Development
- **Format**: TXT
- **Use**: Test basic parsing, section detection, job matching for backend engineers

### 2. Sample_CV_2_Sarah_Johnson.txt
- **Profile**: Senior Data Scientist with 5+ years experience
- **Key Skills**: Python, TensorFlow, Machine Learning, NLP, AWS, PyTorch
- **Format**: TXT
- **Use**: Test CV parsing for ML/Data Science roles, check keyword matching

### 3. Sample_CV_3_Michael_Chen.txt
- **Profile**: DevOps Engineer (Senior) with 6+ years experience
- **Key Skills**: Kubernetes, AWS, Terraform, Docker, CI/CD, Linux
- **Format**: TXT
- **Use**: Test DevOps/Infrastructure role matching, container technology matching

### Sample_CV_4_Emily_Rodriguez.docx
- **Profile**: Senior Frontend Developer with 5+ years experience
- **Key Skills**: React, JavaScript, TypeScript, Node.js, AWS
- **Format**: DOCX
- **Use**: Test DOCX parsing, frontend role matching
- **Note**: Generate using `python create_sample_docx.py`

## How to Generate DOCX Sample

To create the DOCX sample:

```bash
cd "c:\Github\(Streamlit app)\CVFoster\data\samples"
C:\Users\Lewis\AppData\Local\Python\bin\python.exe create_sample_docx.py
```

This will create `Sample_CV_4_Emily_Rodriguez.docx` in the current directory.

## Testing Workflow

1. **Try uploading each TXT sample** to the "Upload & Parse" page
2. **Verify section detection** (Experience, Skills, Education, etc.)
3. **Test Job Matching**:
   - John's CV should match with Senior/Mid-level backend jobs
   - Sarah's CV should match with Data Science jobs
   - Michael's CV should match with DevOps jobs
   - Emily's CV should match with Frontend jobs
4. **Test CV Rewriting** on different sections
5. **Test error handling** with corrupted/empty files

## Sample Matches (Expected Results)

### John Doe CV
- **Best matches**: Senior Software Engineer, DevOps Engineer, Full Stack Engineer
- **Top keywords**: Python, JavaScript, AWS, Docker, React, Kubernetes

### Sarah Johnson CV
- **Best matches**: Data Scientist, Machine Learning Engineer
- **Top keywords**: Python, TensorFlow, Machine Learning, NLP, Statistics

### Michael Chen CV
- **Best matches**: DevOps Engineer, Cloud Systems Engineer
- **Top keywords**: Kubernetes, Docker, AWS, Terraform, CI/CD

### Emily Rodriguez CV
- **Best matches**: Frontend Developer, Full Stack Engineer
- **Top keywords**: React, JavaScript, TypeScript, Node.js, HTML/CSS

## Notes

- All CVs are realistic and contain actual job-relevant content
- Samples cover different skill levels and specializations
- Use for end-to-end testing of the application workflow
- Expected Precision@3 for job matching: ≥ 0.7 (at least 2/3 matches should be relevant)
