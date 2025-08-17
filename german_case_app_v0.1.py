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

def get_detailed_explanation(question_id, user_answer, correct_answer):
    """Generate detailed explanation for each specific question"""
    
    explanations = {
        1: {
            'context': 'Subject of the sentence (Nominativ)',
            'rule': 'The subject (who/what IS very nice) stays in Nominativ case',
            'why_wrong': 'No case change needed here - this is the basic dictionary form',
            'memory_tip': 'Ask: WHO is very nice? → Der Mann (subject = Nominativ)'
        },
        2: {
            'context': 'Direct object after "sehen" (Akkusativ)', 
            'rule': '"sehen" takes Akkusativ - you see someone/something directly',
            'why_wrong': 'You need Akkusativ because "Mann" receives the action of seeing',
            'memory_tip': 'Ask: I see WHOM? → den Mann (masculine Akkusativ = der → den)'
        },
        3: {
            'context': 'Subject of the sentence (Nominativ)',
            'rule': 'The subject (who/what plays) stays in Nominativ case', 
            'why_wrong': 'No case change needed - "Das Kind" is doing the action',
            'memory_tip': 'Neuter nouns stay the same in Nominativ and Akkusativ'
        },
        4: {
            'context': 'Indirect object after "geben" (Dativ)',
            'rule': '"geben" always takes Dativ - you give something TO someone',
            'why_wrong': 'The woman receives the book, so she\'s the indirect object',
            'memory_tip': 'Ask: I give TO WHOM? → der Frau (feminine Dativ: die → der)'
        },
        5: {
            'context': 'Object after "helfen" (Dativ)', 
            'rule': '"helfen" always takes Dativ - you help TO someone',
            'why_wrong': 'Need possessive pronoun in Dativ case + masculine noun',
            'memory_tip': 'sein + Dativ masculine = seinem, Bruder stays Bruder'
        },
        6: {
            'context': 'After preposition "mit" (Dativ)',
            'rule': '"mit" always takes Dativ case',
            'why_wrong': 'All transportation with "mit" uses Dativ case',
            'memory_tip': 'mit + masculine Dativ: der Bus → dem Bus'
        },
        7: {
            'context': 'Showing possession (Genitiv)',
            'rule': 'Possession: "das Auto meiner Schwester" = the car OF my sister',
            'why_wrong': 'Need possessive pronoun in Genitiv case',
            'memory_tip': 'Whose car? → meiner Schwester (feminine Genitiv: meine → meiner)'
        },
        8: {
            'context': 'After preposition "trotz" (Genitiv)',
            'rule': '"trotz" always takes Genitiv case',
            'why_wrong': 'Need neuter Genitiv with adjective declension',
            'memory_tip': 'trotz + neuter Genitiv: das → des, adjective gets -en ending'
        },
        9: {
            'context': 'Indirect object after "erklären" (Dativ)',
            'rule': '"erklären" takes Dativ - you explain something TO someone', 
            'why_wrong': 'The students receive the explanation (indirect object)',
            'memory_tip': 'Plural Dativ: die → den, adjective gets -en ending'
        },
        10: {
            'context': 'After preposition "mit" (Dativ)',
            'rule': '"mit" takes Dativ, possessive + adjective must match',
            'why_wrong': 'Need possessive pronoun + adjective in Dativ masculine',
            'memory_tip': 'mit + sein + Dativ masc. = seinem alten (both get -em/-en)'
        },
        11: {
            'context': 'After preposition "während" (Genitiv)',
            'rule': '"während" always takes Genitiv case',
            'why_wrong': 'Need masculine Genitiv with adjective declension',
            'memory_tip': 'während + masculine Genitiv: der → des, adjective gets -en'
        },
        12: {
            'context': 'Showing possession (Genitiv)',
            'rule': 'Possession: "die Mutter des kleinen Mädchens" = the mother OF the little girl',
            'why_wrong': 'Need neuter Genitiv with adjective declension', 
            'memory_tip': 'Whose mother? → des kleinen Mädchens (neuter Genitiv: das → des)'
        }
    }
    
    if question_id in explanations:
        exp = explanations[question_id]
        return f"""
❌ **Your answer:** "{user_answer}"  
✅ **Correct:** "{correct_answer}"

💡 **Why:** {exp['rule']}  
📝 **Context:** {exp['context']}  
❗ **Your mistake:** {exp['why_wrong']}  
🎯 **Memory tip:** {exp['memory_tip']}
"""
    else:
        return f"❌ Your answer: '{user_answer}' → ✅ Correct: '{correct_answer}'"

def analyze_quiz_results(answers):
    """Analyze quiz results and identify problem areas"""
    analysis = {
        "total_correct": 0,
        "case_errors": {"nominativ": 0, "akkusativ": 0, "dativ": 0, "genitiv": 0},
        "type_errors": {"article": 0, "possessive": 0, "article_adjective": 0, "possessive_adjective": 0},
        "level_performance": {"basic": 0, "intermediate": 0, "advanced": 0, "complex": 0},
        "weakest_area": "",
        "strengths": [],
        "detailed_feedback": []
    }
    
    for q in QUIZ_QUESTIONS:
        user_answer = answers.get(f"q_{q['id']}", "").strip()
        correct = q["correct"]
        
        if user_answer.lower() == correct.lower():
            analysis["total_correct"] += 1
            analysis["level_performance"][q["level"]] += 1
            analysis["detailed_feedback"].append({
                "question": q["id"],
                "correct": True,
                "message": f"✅ **Question {q['id']}:** Perfect! '{user_answer}' is correct."
            })
        else:
            analysis["case_errors"][q["case"]] += 1
            analysis["type_errors"][q["type"]] += 1
            analysis["detailed_feedback"].append({
                "question": q["id"], 
                "correct": False,
                "explanation": get_detailed_explanation(q["id"], user_answer, correct)
            })
    
    # Calculate percentages for level performance
    level_totals = {"basic": 3, "intermediate": 3, "advanced": 3, "complex": 3}
    for level in analysis["level_performance"]:
        analysis["level_performance"][level] = analysis["level_performance"][level] / level_totals[level] * 100
    
    # Identify weakest area
    max_errors = max(analysis["case_errors"].values()) if any(analysis["case_errors"].values()) else 0
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
    
    # Performance level assessment
    if score_percent >= 85:
        feedback += "**🎉 Excellent work!** You have a strong grasp of German cases.\n\n"
    elif score_percent >= 70:
        feedback += "**📈 Good progress!** You're getting the hang of German cases.\n\n"
    elif score_percent >= 50:
        feedback += "**💪 Keep going!** You understand the basics, now let's fine-tune.\n\n"
    else:
        feedback += "**🚀 Great start!** Every expert was once a beginner - let's build systematically.\n\n"
    
    # Strengths
    if analysis["strengths"]:
        feedback += f"**Your Strengths:** ✅\n"
        for strength in analysis["strengths"]:
            feedback += f"- **{strength.capitalize()}** cases - perfect mastery!\n"
        feedback += "\n"
    
    # Main problem area
    if analysis["weakest_area"]:
        case = analysis["weakest_area"]
        error_count = analysis["case_errors"][case]
        feedback += f"**Main Focus Area: {case.upper()} ({error_count} errors)** ❌\n\n"
        
        # Case-specific advice
        if case == "dativ":
            feedback += "**DATIV** is your biggest challenge! Master these patterns:\n"
            feedback += "- **Key question:** To whom/for whom? (wem?)\n"
            feedback += "- **Dativ verbs:** geben, helfen, gehören, danken, erklären\n"
            feedback += "- **Dativ prepositions:** mit, bei, von, zu, aus, nach\n"
            feedback += "- **Endings:** der→dem, die→der, das→dem, mein→meinem/meiner\n"
        elif case == "akkusativ":
            feedback += "**AKKUSATIV** needs work! Focus on:\n"
            feedback += "- **Key question:** Who/what receives the action? (wen/was?)\n"
            feedback += "- **Akkusativ verbs:** sehen, haben, kaufen, lesen, trinken\n"
            feedback += "- **Akkusativ prepositions:** durch, für, ohne, um, gegen\n"
            feedback += "- **Endings:** der→den, die→die, das→das, mein→meinen/meine\n"
        elif case == "genitiv":
            feedback += "**GENITIV** is tricky but learnable! Remember:\n"
            feedback += "- **Key question:** Whose? (wessen?)\n"
            feedback += "- **Genitiv prepositions:** trotz, während, wegen, statt\n"
            feedback += "- **Possession:** das Auto meiner Schwester\n"
            feedback += "- **Endings:** der→des, die→der, das→des, mein→meines/meiner\n"
        elif case == "nominativ":
            feedback += "**NOMINATIV** fundamentals need attention:\n"
            feedback += "- **Key question:** Who/what does the action? (wer/was?)\n"
            feedback += "- **Subject of sentence:** Der Mann ist nett\n"
            feedback += "- **After 'sein':** Das ist ein Mann\n"
            feedback += "- **No change from dictionary form**\n"
    
    # Type-specific issues
    max_type_errors = max(analysis["type_errors"].values()) if any(analysis["type_errors"].values()) else 0
    for type_name, errors in analysis["type_errors"].items():
        if errors == max_type_errors and errors > 1:
            if "possessive" in type_name:
                feedback += "\n**📝 Additional Focus: Possessive Pronoun Endings**\n"
                feedback += "- mein → meinen (Akk. masc.), meinem (Dat. masc.), meiner (Dat. fem./Gen. fem.)\n"
                feedback += "- Pattern follows articles: der→den→dem→des\n"
            elif "adjective" in type_name:
                feedback += "\n**📝 Additional Focus: Adjective Declensions**\n"
                feedback += "- Adjectives must match case, gender, and number of their noun\n"
                feedback += "- After 'der/die/das': meist -e or -en endings\n"
    
    if analysis['weakest_area']:
        feedback += f"\n🎯 **Next step:** Let's do targeted practice on **{analysis['weakest_area'].upper()}** cases!"
    else:
        feedback += f"\n🚀 **You're ready for advanced topics!** Consider practicing mixed texts or complex sentences."
    
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
    
    # Show detailed question-by-question analysis
    st.header("📝 Detailed Question Analysis")
    
    for item in st.session_state.analysis["detailed_feedback"]:
        if item["correct"]:
            st.success(item["message"])
        else:
            st.error(item["explanation"])
    
    # Show summary statistics
    with st.expander("📊 Performance Statistics"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Case Performance:**")
            for case, errors in st.session_state.analysis["case_errors"].items():
                if errors == 0:
                    st.success(f"✅ {case.capitalize()}: Perfect!")
                else:
                    st.error(f"❌ {case.capitalize()}: {errors} errors")
        
        with col2:
            st.write("**Level Performance:**")
            for level, percentage in st.session_state.analysis["level_performance"].items():
                st.write(f"**{level.capitalize()}:** {percentage:.0f}%")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Start Targeted Practice"):
            if st.session_state.analysis['weakest_area']:
                st.info(f"**Coming soon!** Targeted practice sessions for {st.session_state.analysis['weakest_area'].upper()} cases.")
                st.write("This would launch a personalized practice session focusing on your weak areas!")
            else:
                st.success("🎉 You've mastered all basic cases! Ready for advanced practice.")
    
    with col2:
        if st.button("🔄 Take Quiz Again"):
            # Reset everything
            st.session_state.quiz_completed = False
            st.session_state.quiz_answers = {}
            st.session_state.analysis_done = False
            st.rerun()

# Footer
st.write("---")
st.write("*Prototype v0.2 - Built with ❤️ for systematic language learning*")