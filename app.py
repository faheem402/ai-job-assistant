
import streamlit as st
from analyzer import (
    extract_resume_text,
    analyze_resume,
    generate_ai_feedback,
)

st.set_page_config(
    page_title="AI Job Application Assistant",
    page_icon="💼",
    layout="wide",
)

# Keep analysis results across Streamlit reruns.
if "results" not in st.session_state:
    st.session_state.results = None

if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None

if "ai_error" not in st.session_state:
    st.session_state.ai_error = None

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
    type=["pdf"],
)

job_description = st.text_area(
    "Paste the job description",
    height=250,
    placeholder="Paste the complete job description here...",
)

if st.button("Analyze Resume", type="primary"):
    # Reset previous results when starting a new analysis.
    st.session_state.results = None
    st.session_state.ai_feedback = None
    st.session_state.ai_error = None

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
                    resume_text,
                    job_description,
                )

                # Save the basic results immediately.
                st.session_state.results = results

            # Generate AI feedback separately.
            try:
                with st.spinner("Generating AI recommendations..."):
                    feedback = generate_ai_feedback(
                        resume_text,
                        job_description,
                        results,
                    )

                st.session_state.ai_feedback = feedback

            except Exception as api_error:
                st.session_state.ai_error = (
                    "AI recommendations could not be generated. "
                    "Your basic analysis is still available. "
                    "Please try again later."
                )
                print(f"Gemini API error: {api_error}")

        except Exception as error:
            st.error(f"Analysis failed: {error}")


# Display saved results outside the button block.
results = st.session_state.results

if results is not None:
    st.subheader("Analysis Results")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Text Similarity",
        f"{results['match_score']}%",
    )
    col2.metric(
        "Matching Skills",
        len(results["matched_skills"]),
    )
    col3.metric(
        "Potential Skill Gaps",
        len(results["missing_skills"]),
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
        "A skill not detected in your resume may still be present "
        "under a different name or description."
    )

    st.subheader("AI-Powered Recommendations")

    if st.session_state.ai_feedback:
        st.markdown(st.session_state.ai_feedback)

    elif st.session_state.ai_error:
        st.warning(st.session_state.ai_error)

    else:
        st.info("AI recommendations have not been generated yet.")

    # Build a report containing both programmatic and AI results.
    report_parts = [
        "AI Job Application Assistant - Analysis Report",
        "",
        f"Text Similarity: {results['match_score']}%",
        "",
        f"Resume Skills: {', '.join(results['resume_skills'])}",
        "",
        f"Required Skills: {', '.join(results['required_skills'])}",
        "",
        f"Matching Skills: {', '.join(results['matched_skills'])}",
        "",
        f"Potential Skill Gaps: {', '.join(results['missing_skills'])}",
        "",
        "AI-POWERED RECOMMENDATIONS",
        "",
        (
            st.session_state.ai_feedback
            or "AI recommendations were unavailable for this analysis."
        ),
    ]

    report = "\n".join(report_parts)

    st.download_button(
        "Download Analysis Report",
        data=report,
        file_name="resume_analysis.txt",
        mime="text/plain",
        key="download_analysis_report",
    )
