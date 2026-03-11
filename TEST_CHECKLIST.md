# CVFoster Testing Checklist

## ✅ Pre-Testing Setup

- [x] App running at http://localhost:8501
- [x] 4 sample CVs created (3 TXT + 1 DOCX)
- [x] Sample job postings loaded (7 jobs)

## 🧪 Test Case 1: Upload & Parse John Doe CV

### Steps:
1. Go to "Upload & Parse" page (should be default)
2. Click "Choose File" button
3. Select: `data/samples/Sample_CV_1_John_Doe.txt`
4. Verify parsing completes without errors

### Expected Results:
- [  ] File uploaded successfully
- [  ] CV text displays in text area
- [  ] Parse Results show format (TXT)
- [  ] Sections detected include: experience, skills, education, summary
- [  ] Full extracted text shows all CV content
- [  ] Detected sections expandable and readable

---

## 🧪 Test Case 2: Upload & Parse Emily Rodriguez (DOCX)

### Steps:
1. Go to "Upload & Parse" page
2. Click "Choose File" button
3. Select: `data/samples/Sample_CV_4_Emily_Rodriguez.docx`
4. Verify DOCX parsing works

### Expected Results:
- [  ] DOCX file parsed successfully
- [  ] Format shows as DOCX
- [  ] Extracted text contains Emily's resume content
- [  ] Section detection works (Frontend skills should be detected)
- [  ] No parsing errors

---

## 🧪 Test Case 3: Job Matching (John Doe)

### Steps:
1. After uploading John's CV, go to "Job Matching" page
2. Index should be created automatically
3. Select section: "experience"
4. Click "Find Matching Jobs"
5. Review results

### Expected Results:
- [  ] Index created shows: total_chunks, embedding_dim
- [  ] Top 3 job matches displayed
- [  ] Match #1 should include: Senior Software Engineer OR DevOps Engineer OR Full Stack Engineer
- [  ] Match scores: 0.3 - 0.7 range (semantic + keyword + seniority)
- [  ] Score breakdown shows components (semantic%, keyword%, seniority%)
- [  ] Matched CV section visible in expandable
- [  ] At least 2/3 matches are relevant (Precision@3 ≥ 0.7)

### Sample Expected Matches for John:
1. **Senior Software Engineer** (job_001) - Python, AWS, Docker match
2. **DevOps Engineer** (job_004) - Kubernetes, AWS, CI/CD match  
3. **Full Stack Engineer** (job_007) - JavaScript, Node.js, React match

---

## 🧪 Test Case 4: Job Matching (Sarah Johnson)

### Steps:
1. Upload Sarah's CV: `Sample_CV_2_Sarah_Johnson.txt`
2. Go to "Job Matching"
3. Select section: "skills"
4. Click "Find Matching Jobs"

### Expected Results:
- [  ] Top match should be: **Data Scientist** (job_002)
- [  ] "Python", "TensorFlow", "SQL" should match high
- [  ] Machine Learning Engineer should be in top 3
- [  ] Seniority "senior" should match with "mid"/"senior" jobs well

---

## 🧪 Test Case 5: Job Matching (Michael Chen)

### Steps:
1. Upload Michael's CV: `Sample_CV_3_Michael_Chen.txt`
2. Go to "Job Matching"
3. Select section: "technical skills"
4. Click "Find Matching Jobs"

### Expected Results:
- [  ] Top match should be: **DevOps Engineer** (job_004)
- [  ] Keywords: Kubernetes, Docker, AWS, CI/CD match
- [  ] Score should be among the highest due to keyword alignment

---

## 🧪 Test Case 6: CV Rewriting

### Steps:
1. Upload any CV (e.g., John Doe)
2. Go to "Rewrite" page
3. Select section: "experience"
4. Click "Generate Rewrite"

### Expected Results:
- [  ] Rewrite generates without error
- [  ] Original text displayed on left side
- [  ] Rewritten text displayed on right side
- [  ] Both texts are coherent and readable
- [  ] Rewritten length within ±10% of original
- [  ] "Download Rewritten Text" button present and functional
- [  ] Downloaded file contains rewritten content

---

## 🧪 Test Case 7: Error Handling - Unsupported File

### Steps:
1. Create a dummy file: test.xlsx (or use any unsupported format)
2. Go to "Upload & Parse"
3. Try to upload unsupported file
4. Verify error handling

### Expected Results:
- [  ] Streamlit shows error (file type not supported or parsing error)
- [  ] Graceful error message displayed
- [  ] App doesn't crash

---

## 🧪 Test Case 8: Error Handling - Empty File

### Steps:
1. Create empty text file: empty.txt
2. Go to "Upload & Parse"
3. Upload empty file

### Expected Results:
- [  ] File uploads
- [  ] Warning shown about empty content
- [  ] App handles gracefully

---

## 🧪 Test Case 9: Multiple CVs (Session State)

### Steps:
1. Upload John Doe CV
2. Go to Job Matching
3. Get results
4. Go back to Upload & Parse
5. Upload Emily's DOCX CV (new file)
6. Go to Job Matching again

### Expected Results:
- [  ] Index is cleared/updated with new CV
- [  ] New job matches for Emily shown
- [  ] No conflicts between old and new data
- [  ] Session state properly manages multiple uploads

---

## 🧪 Test Case 10: Performance Check

### Timing Targets:
Use a stopwatch or browser dev tools to measure:

1. **CV Parsing Time** (upload → section detection)
   - Target: ≤ 2 seconds
   - Actual: ________ seconds
   - [  ] Pass / [  ] Fail

2. **Job Matching Time** (index creation + search)
   - Target: ≤ 2 seconds  
   - Actual: ________ seconds
   - [  ] Pass / [  ] Fail

3. **CV Rewriting Time** (generate rewrite)
   - Target: ≤ 5 seconds
   - Actual: ________ seconds
   - [  ] Pass / [  ] Fail

---

## 📊 Evaluation Metrics

### Precision@3 (Job Matching)
- **Metric**: At least 2/3 of top matches are relevant
- **Formula**: # relevant matches / 3

**Test Results:**
- John Doe: ___/3 passes = ___% ✓ / ✗
- Sarah Johnson: ___/3 passes = ___% ✓ / ✗
- Michael Chen: ___/3 passes = ___% ✓ / ✗
- Emily Rodriguez: ___/3 passes = ___% ✓ / ✗

**Overall Precision@3**: ________ (Target: ≥ 0.7)

### Rewrite Quality
- The rewritten text should be:
  - [  ] Coherent and grammatically correct
  - [  ] Within 10% length of original
  - [  ] Readable and professional
  - [  ] Different from original (not just copied)

---

## 🐛 Known Issues / Notes

Issues found during testing:
1. ________________________________________________________________
2. ________________________________________________________________
3. ________________________________________________________________

---

## ✅ Final Summary

- **Total Tests Passed**: _____ / 10
- **Critical Issues**: _____
- **Minor Issues**: _____
- **Ready for Demo**: [  ] Yes / [  ] No

**Comments:**
________________________________________________________________
________________________________________________________________
________________________________________________________________
