
import streamlit as st
from analyzer import (extract_resume_text, analyze_resume, generate_ai_feedback)

st.set_page_config(
    page_title="AI Job Application Assistant",
    page_icon="💼",
    layout="wide"
)

st.title("💼 AI Job Application Assistant")
st.write(
    "Analyze your resume against a job description "
    "and identify skills you may need to highlight."
)

st.info(
    "Your match score measures text similarity. "
    "It does not predict hiring outcomes."
)

uploaded_file = st.file_uploader(
    "Upload your resume (PDF)",
    type=["pdf"]
)

job_description = st.text_area(
    "Paste the job description",
    height=250,
    placeholder="Paste the complete job description here..."
)

if st.button("Analyze Resume", type="primary"):
    if uploaded_file is None:
        st.error("Please upload a PDF resume.")
    elif not job_description.strip():
        st.error("Please paste a job description.")
    elif len(job_description.strip()) < 30:
        st.error("Please provide a more detailed job description.")
    else:
        try:
            with st.spinner("Reading resume and analyzing skills..."):
                resume_text = extract_resume_text(uploaded_file)
                results = analyze_resume(
                    resume_text, job_description
                    )

            # Show basic analysis immediately.
                st.subheader("Analysis Results")

                col1, col2, col3 = st.columns(3)
                col1.metric(
                    "Text Similarity",
                    f"{results['match_score']}%"
                )
                col2.metric(
                    "Matching Skills",
                    len(results["matched_skills"])
                )
                col3.metric(
                    "Potential Skill Gaps",
                    len(results["missing_skills"])
                )

                st.progress(results["match_score"] / 100)

                st.subheader("Skills Found in Your Resume")
                st.write(
                    ", ".join(results["resume_skills"])
                    or "No listed skills detected."
                )

                st.subheader("Matching Skills")
                st.write(
                    ", ".join(results["matched_skills"])
                    or "No matching skills detected."
                )

                st.subheader("Skills to Review")
                st.write(
                    ", ".join(results["missing_skills"])
                    or "No potential gaps detected."
                )
                st.caption(
                    "A skill not detected in your resume may still be "
                    "present under a different name or description."
                )

                # Download remains available independently of Gemini.
                report = (
                    "AI Job Application Assistant - Analysis Report\n\n"
                    f"Text Similarity: {results['match_score']}%\n\n"
                    f"Resume Skills: {', '.join(results['resume_skills'])}\n\n"
                    f"Matching Skills: {', '.join(results['matched_skills'])}\n\n"
                    f"Potential Gaps: {', '.join(results['missing_skills'])}\n"
                )

                st.download_button(
                    "Download Analysis Report",
                    data=report,
                    file_name="resume_analysis.txt",
                    mime="text/plain"
                )

                # Gemini failure won't erase the basic analysis.
                st.subheader("AI-Powered Recommendations")

                try:
                    with st.spinner("Generating AI recommendations..."):
                        ai_feedback = generate_ai_feedback(
                            resume_text,
                            job_description,
                            results
                        )

                    st.markdown(ai_feedback)

                except Exception as api_error:
                    st.warning(
                        "Basic resume analysis is complete, but AI "
                        "recommendations could not be generated. "
                        "Please try again later."
                    )
                    print(f"Gemini API error: {api_error}")

        except Exception as error:
            st.error(f"Analysis failed: {error}")
