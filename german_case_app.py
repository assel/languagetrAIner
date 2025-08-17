import streamlit as st
import json

# Initialize session state
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# Quiz questions with correct answers and analysis metadata
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "_______ (Der Mann) ist sehr nett.",
        "correct": "Der Mann",
        "case": "nominativ",
        "level": "basic",
        "type": "article"
    },
    {
        "id": 2, 
        "question": "Ich sehe _______ (der Mann) im Park.",
        "correct": "den Mann",
        "case": "akkusativ", 
        "level": "basic",
        "type": "article"
    },
    {
        "id": 3,
        "question": "_______ (Das Kind) spielt im Garten.",
        "correct": "Das Kind",
        "case": "nominativ",
        "level": "basic", 
        "type": "article"
    },
    {
        "id": 4,
        "question": "Ich gebe _______ (die Frau) das Buch.",
        "correct": "der Frau",
        "case": "dativ",
        "level": "intermediate",
        "type": "article"
    },
    {
        "id": 5,
        "question": "Er hilft _______ (sein Bruder) beim Umziehen.",
        "correct": "seinem Bruder", 
        "case": "dativ",
        "level": "intermediate",
        "type": "possessive"
    },
    {
        "id": 6,
        "question": "Wir fahren mit _______ (der Bus) zur Arbeit.",
        "correct": "dem Bus",
        "case": "dativ",
        "level": "intermediate",
        "type": "article"
    },
    {
        "id": 7,
        "question": "Das Auto _______ (meine Schwester) ist rot.",
        "correct": "meiner Schwester",
        "case": "genitiv",
        "level": "advanced",
        "type": "possessive"
    },
    {
        "id": 8,
        "question": "Trotz _______ (das schlechte Wetter) gehen wir spazieren.",
        "correct": "des schlechten Wetters",
        "case": "genitiv",
        "level": "advanced", 
        "type": "article_adjective"
    },
    {
        "id": 9,
        "question": "Der Lehrer erklärt _______ (die neuen Studenten) die Grammatik.",
        "correct": "den neuen Studenten",
        "case": "dativ",
        "level": "advanced",
        "type": "article_adjective"
    },
    {
        "id": 10,
        "question": "Er spricht mit _______ (sein alter Freund) über wichtige Probleme.",
        "correct": "seinem alten Freund",
        "case": "dativ",
        "level": "complex",
        "type": "possessive_adjective"
    },
    {
        "id": 11,
        "question": "Während _______ (der lange Winter) denken wir oft an warme Länder.",
        "correct": "des langen Winters",
        "case": "genitiv", 
        "level": "complex",
        "type": "article_adjective"
    },
    {
        "id": 12,
        "question": "Die Mutter _______ (das kleine Mädchen) kauft frische Blumen für ihre kranke Mutter.",
        "correct": "des kleinen Mädchens",
        "case": "genitiv",
        "level": "complex",
        "type": "article_adjective"
    }
]

def analyze_quiz_results(answers):
    """Analyze quiz results and identify problem areas"""
    analysis = {
        "total_correct": 0,
        "case_errors": {"nominativ": 0, "akkusativ": 0, "dativ": 0, "genitiv": 0},
        "type_errors": {"article": 0, "possessive": 0, "article_adjective": 0, "possessive_adjective": 0},
        "level_performance": {"basic": 0, "intermediate": 0, "advanced": 0, "complex": 0},
        "weakest_area": "",
        "strengths": []
    }
    
    for q in QUIZ_QUESTIONS:
        user_answer = answers.get(f"q_{q['id']}", "").strip()
        correct = q["correct"]
        
        if user_answer.lower() == correct.lower():
            analysis["total_correct"] += 1
            analysis["level_performance"][q["level"]] += 1
        else:
            analysis["case_errors"][q["case"]] += 1
            analysis["type_errors"][q["type"]] += 1
    
    # Calculate percentages for level performance
    level_totals = {"basic": 3, "intermediate": 3, "advanced": 3, "complex": 3}
    for level in analysis["level_performance"]:
        analysis["level_performance"][level] = analysis["level_performance"][level] / level_totals[level] * 100
    
    # Identify weakest area
    max_errors = max(analysis["case_errors"].values())
    for case, errors in analysis["case_errors"].items():
        if errors == max_errors and errors > 0:
            analysis["weakest_area"] = case
            break
    
    # Identify strengths
    for case, errors in analysis["case_errors"].items():
        if errors == 0:
            analysis["strengths"].append(case)
    
    return analysis

def generate_ai_feedback(analysis):
    """Generate AI-style feedback based on analysis"""
    score_percent = (analysis["total_correct"] / 12) * 100
    
    feedback = f"**🔍 DIAGNOSTIC ANALYSIS:**\n\n"
    feedback += f"**Score: {analysis['total_correct']}/12 correct ({score_percent:.0f}%)**\n\n"
    
    # Strengths
    if analysis["strengths"]:
        feedback += f"**Your Strengths:** ✅\n"
        for strength in analysis["strengths"]:
            feedback += f"- **{strength.capitalize()}** cases - perfect!\n"
        feedback += "\n"
    
    # Main problem area
    if analysis["weakest_area"]:
        case = analysis["weakest_area"]
        error_count = analysis["case_errors"][case]
        feedback += f"**Main Problem Area: {case.upper()} ({error_count} errors)** ❌\n\n"
        
        # Case-specific advice
        if case == "dativ":
            feedback += "**DATIV** is your biggest challenge! Remember:\n"
            feedback += "- Used for indirect objects (to whom/for whom?)\n"
            feedback += "- After verbs like: geben, helfen, gehören, danken\n"
            feedback += "- After prepositions: mit, bei, von, zu, aus\n"
        elif case == "akkusativ":
            feedback += "**AKKUSATIV** needs work! Remember:\n"
            feedback += "- Used for direct objects (who/what receives the action?)\n"
            feedback += "- After verbs like: sehen, haben, kaufen, lesen\n"
            feedback += "- After prepositions: durch, für, ohne, um\n"
        elif case == "genitiv":
            feedback += "**GENITIV** is tricky! Remember:\n"
            feedback += "- Shows possession (whose?)\n"
            feedback += "- After prepositions: trotz, während, wegen\n"
            feedback += "- Masculine/Neuter: des + -s ending, Feminine: der\n"
        elif case == "nominativ":
            feedback += "**NOMINATIV** basics need attention! Remember:\n"
            feedback += "- Used for the subject (who/what does the action?)\n"
            feedback += "- No change from dictionary form\n"
    
    # Type-specific issues
    max_type_errors = max(analysis["type_errors"].values())
    for type_name, errors in analysis["type_errors"].items():
        if errors == max_type_errors and errors > 1:
            if "possessive" in type_name:
                feedback += "\n**Secondary Issue: Possessive Pronoun Endings** ❌\n"
                feedback += "Remember: mein → meinen (Akk. masc.), meinem (Dat. masc.), meiner (Dat. fem.)\n"
            elif "adjective" in type_name:
                feedback += "\n**Secondary Issue: Adjective Declensions** ❌\n"
                feedback += "Adjectives must match the case, gender, and number of their noun!\n"
    
    feedback += f"\n**Recommendation:** Let's focus on **{analysis['weakest_area'].upper()}** practice!"
    
    return feedback

# Main app
st.title("🇩🇪 German Case Diagnostic Tool")
st.write("*Learn German cases systematically - just like our Russian sessions!*")

if not st.session_state.quiz_completed:
    st.header("📋 Diagnostic Quiz")
    st.write("Fill in the correct form for each sentence. Don't worry about making mistakes - that's how we learn!")
    
    # Create form for quiz
    with st.form("diagnostic_quiz"):
        answers = {}
        
        for i, q in enumerate(QUIZ_QUESTIONS):
            st.write(f"**{i+1}.** {q['question']}")
            answers[f"q_{q['id']}"] = st.text_input(f"Answer {i+1}:", key=f"q_{q['id']}")
            st.write("---")
        
        submitted = st.form_submit_button("📊 Analyze My Results!")
        
        if submitted:
            # Check if all questions answered
            unanswered = [i+1 for i, q in enumerate(QUIZ_QUESTIONS) if not answers[f"q_{q['id']}"].strip()]
            
            if unanswered:
                st.error(f"Please answer all questions! Missing: {', '.join(map(str, unanswered))}")
            else:
                st.session_state.quiz_answers = answers
                st.session_state.quiz_completed = True
                st.rerun()

else:
    # Show results
    if not st.session_state.analysis_done:
        with st.spinner("🤔 Analyzing your answers..."):
            analysis = analyze_quiz_results(st.session_state.quiz_answers)
            feedback = generate_ai_feedback(analysis)
            
            st.session_state.analysis = analysis
            st.session_state.feedback = feedback
            st.session_state.analysis_done = True
    
    # Display feedback
    st.markdown(st.session_state.feedback)
    
    # Show detailed results
    with st.expander("📝 Detailed Results"):
        for q in QUIZ_QUESTIONS:
            user_answer = st.session_state.quiz_answers[f"q_{q['id']}"]
            correct = q["correct"]
            
            if user_answer.lower().strip() == correct.lower():
                st.success(f"**Q{q['id']}:** ✅ {user_answer}")
            else:
                st.error(f"**Q{q['id']}:** ❌ '{user_answer}' → **{correct}**")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Start Targeted Practice"):
            st.info("**Coming soon!** Targeted practice sessions based on your weak areas.")
            st.write("This would launch a practice session focusing on:", st.session_state.analysis['weakest_area'])
    
    with col2:
        if st.button("🔄 Take Quiz Again"):
            # Reset everything
            st.session_state.quiz_completed = False
            st.session_state.quiz_answers = {}
            st.session_state.analysis_done = False
            st.rerun()

# Footer
st.write("---")
st.write("*Prototype v0.1 - Built with ❤️ for systematic language learning*")