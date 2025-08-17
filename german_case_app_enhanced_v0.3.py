import streamlit as st
import json
import random
from datetime import datetime, timedelta
import math

# Page config
st.set_page_config(
    page_title="German Case Master",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize comprehensive session state
def init_session_state():
    defaults = {
        'user_profile': {
            'name': '',
            'level': 'beginner',
            'total_sessions': 0,
            'total_correct': 0,
            'total_questions': 0,
            'streak_days': 0,
            'last_session': None,
            'achievements': []
        },
        'quiz_completed': False,
        'quiz_answers': {},
        'analysis_done': False,
        'practice_mode': False,
        'practice_questions': [],
        'current_mode': 'diagnostic',
        'question_history': {},  # For spaced repetition
        'session_stats': {'correct': 0, 'total': 0, 'start_time': None},
        'show_explanations': True,
        'difficulty_preference': 'adaptive'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Comprehensive question database
QUIZ_QUESTIONS = [
    {
        "id": 1, "question": "_______ (Der Mann) ist sehr nett.", "correct": "Der Mann",
        "case": "nominativ", "level": "basic", "type": "article", "gender": "masculine",
        "hint": "Who is being nice? (Subject of sentence)", "context": "everyday_description",
        "explanation": "Subject of sentence - no case change needed"
    },
    {
        "id": 2, "question": "Ich sehe _______ (der Mann) im Park.", "correct": "den Mann",
        "case": "akkusativ", "level": "basic", "type": "article", "gender": "masculine",
        "hint": "Who/what do I see? (Direct object)", "context": "everyday_action",
        "explanation": "Direct object after 'sehen' - masculine der→den"
    },
    {
        "id": 3, "question": "_______ (Das Kind) spielt im Garten.", "correct": "Das Kind",
        "case": "nominativ", "level": "basic", "type": "article", "gender": "neuter",
        "hint": "Who is playing? (Subject)", "context": "everyday_description",
        "explanation": "Subject - neuter stays unchanged in nominativ"
    },
    {
        "id": 4, "question": "Ich gebe _______ (die Frau) das Buch.", "correct": "der Frau",
        "case": "dativ", "level": "intermediate", "type": "article", "gender": "feminine",
        "hint": "To whom do I give? (Indirect object)", "context": "everyday_action",
        "explanation": "Indirect object after 'geben' - feminine die→der"
    },
    {
        "id": 5, "question": "Er hilft _______ (sein Bruder) beim Umziehen.", "correct": "seinem Bruder",
        "case": "dativ", "level": "intermediate", "type": "possessive", "gender": "masculine",
        "hint": "helfen + Dativ (to whom does he help?)", "context": "family_relationships",
        "explanation": "Dativ after 'helfen' - possessive sein→seinem"
    },
    {
        "id": 6, "question": "Wir fahren mit _______ (der Bus) zur Arbeit.", "correct": "dem Bus",
        "case": "dativ", "level": "intermediate", "type": "article", "gender": "masculine",
        "hint": "mit always takes Dativ", "context": "transportation",
        "explanation": "Preposition 'mit' requires Dativ - der→dem"
    },
    {
        "id": 7, "question": "Das Auto _______ (meine Schwester) ist rot.", "correct": "meiner Schwester",
        "case": "genitiv", "level": "advanced", "type": "possessive", "gender": "feminine",
        "hint": "Whose car? (Possession = Genitiv)", "context": "family_relationships",
        "explanation": "Possession requires Genitiv - meine→meiner"
    },
    {
        "id": 8, "question": "Trotz _______ (das schlechte Wetter) gehen wir spazieren.", "correct": "des schlechten Wetters",
        "case": "genitiv", "level": "advanced", "type": "article_adjective", "gender": "neuter",
        "hint": "trotz always takes Genitiv", "context": "weather",
        "explanation": "Preposition 'trotz' + Genitiv with adjective declension"
    },
    {
        "id": 9, "question": "Der Lehrer erklärt _______ (die neuen Studenten) die Grammatik.", "correct": "den neuen Studenten",
        "case": "dativ", "level": "advanced", "type": "article_adjective", "gender": "plural",
        "hint": "erklären + Dativ (to whom?)", "context": "education",
        "explanation": "Dativ after 'erklären' - plural die→den + adjective -en"
    },
    {
        "id": 10, "question": "Er spricht mit _______ (sein alter Freund) über wichtige Probleme.", "correct": "seinem alten Freund",
        "case": "dativ", "level": "complex", "type": "possessive_adjective", "gender": "masculine",
        "hint": "mit + Dativ, possessive + adjective endings", "context": "social_relationships",
        "explanation": "Preposition 'mit' + Dativ with possessive and adjective"
    },
    {
        "id": 11, "question": "Während _______ (der lange Winter) denken wir oft an warme Länder.", "correct": "des langen Winters",
        "case": "genitiv", "level": "complex", "type": "article_adjective", "gender": "masculine",
        "hint": "während always takes Genitiv", "context": "time_seasons",
        "explanation": "Preposition 'während' + Genitiv with adjective"
    },
    {
        "id": 12, "question": "Die Mutter _______ (das kleine Mädchen) kauft frische Blumen.", "correct": "des kleinen Mädchens",
        "case": "genitiv", "level": "complex", "type": "article_adjective", "gender": "neuter",
        "hint": "Whose mother? (Possession = Genitiv)", "context": "family_relationships",
        "explanation": "Possession with Genitiv + adjective declension"
    }
]

# Extended practice questions for different contexts
PRACTICE_QUESTIONS = {
    "dativ": [
        {"question": "Ich helfe _______ (meine Mutter) in der Küche.", "correct": "meiner Mutter", "context": "family"},
        {"question": "Das Buch gehört _______ (der Student).", "correct": "dem Studenten", "context": "education"},
        {"question": "Sie gibt _______ (das Kind) einen Apfel.", "correct": "dem Kind", "context": "food"},
        {"question": "Nach _______ (das Konzert) gehen wir essen.", "correct": "dem Konzert", "context": "entertainment"},
        {"question": "Bei _______ (kaltes Wetter) bleibe ich zu Hause.", "correct": "kaltem Wetter", "context": "weather"},
        {"question": "Aus _______ (die große Stadt) kommt viel Lärm.", "correct": "der großen Stadt", "context": "city_life"},
    ],
    "akkusativ": [
        {"question": "Ich kaufe _______ (ein neues Auto).", "correct": "ein neues Auto", "context": "shopping"},
        {"question": "Wir besuchen _______ (unsere Großeltern).", "correct": "unsere Großeltern", "context": "family"},
        {"question": "Er liest _______ (das interessante Buch).", "correct": "das interessante Buch", "context": "education"},
        {"question": "Für _______ (mein Bruder) kaufe ich ein Geschenk.", "correct": "meinen Bruder", "context": "family"},
        {"question": "Ohne _______ (warme Kleidung) ist es kalt.", "correct": "warme Kleidung", "context": "clothing"},
        {"question": "Durch _______ (der dunkle Wald) führt ein Pfad.", "correct": "den dunklen Wald", "context": "nature"},
    ],
    "genitiv": [
        {"question": "Das Haus _______ (meine Eltern) ist groß.", "correct": "meiner Eltern", "context": "family"},
        {"question": "Wegen _______ (das schlechte Wetter) bleiben wir zu Hause.", "correct": "des schlechten Wetters", "context": "weather"},
        {"question": "Der Name _______ (die neue Lehrerin) ist Müller.", "correct": "der neuen Lehrerin", "context": "education"},
        {"question": "Statt _______ (der teure Wein) nehmen wir Bier.", "correct": "des teuren Weins", "context": "food"},
        {"question": "Trotz _______ (die große Hitze) arbeiten wir weiter.", "correct": "der großen Hitze", "context": "weather"},
        {"question": "Während _______ (die lange Reise) haben wir viel gesehen.", "correct": "der langen Reise", "context": "travel"},
    ],
    "nominativ": [
        {"question": "_______ (Mein Vater) arbeitet in Berlin.", "correct": "Mein Vater", "context": "family"},
        {"question": "_______ (Die schönen Blumen) stehen auf dem Tisch.", "correct": "Die schönen Blumen", "context": "home"},
        {"question": "Das ist _______ (unser neues Auto).", "correct": "unser neues Auto", "context": "transportation"},
        {"question": "_______ (Das kleine Kind) spielt im Garten.", "correct": "Das kleine Kind", "context": "family"},
        {"question": "_______ (Die beste Lösung) ist oft die einfachste.", "correct": "Die beste Lösung", "context": "abstract"},
        {"question": "_______ (Frisches Obst) ist sehr gesund.", "correct": "Frisches Obst", "context": "food"},
    ]
}

# Multiple choice questions for variety
MULTIPLE_CHOICE_QUESTIONS = [
    {
        "question": "Ich gebe _______ das Buch.",
        "options": ["der Frau", "die Frau", "den Frau", "dem Frau"],
        "correct": "der Frau",
        "case": "dativ",
        "explanation": "'geben' takes Dativ - feminine die→der"
    },
    {
        "question": "Er sieht _______ im Park.",
        "options": ["der Mann", "den Mann", "dem Mann", "des Mannes"],
        "correct": "den Mann", 
        "case": "akkusativ",
        "explanation": "'sehen' takes Akkusativ - masculine der→den"
    },
    {
        "question": "Das Auto _______ ist neu.",
        "options": ["meiner Schwester", "meine Schwester", "meinen Schwester", "meinem Schwester"],
        "correct": "meiner Schwester",
        "case": "genitiv", 
        "explanation": "Possession requires Genitiv - feminine meine→meiner"
    }
]

# Achievements system
ACHIEVEMENTS = {
    'first_quiz': {'name': '🎯 First Steps', 'description': 'Completed your first diagnostic quiz'},
    'perfect_basic': {'name': '✨ Basic Master', 'description': 'Perfect score on all basic questions'},
    'case_specialist': {'name': '🏆 Case Specialist', 'description': 'Mastered all four German cases'},
    'practice_warrior': {'name': '⚡ Practice Warrior', 'description': 'Completed 10 practice sessions'},
    'streak_week': {'name': '🔥 Week Streak', 'description': 'Practiced for 7 consecutive days'},
    'perfectionist': {'name': '💎 Perfectionist', 'description': 'Achieved 100% on a full diagnostic'},
}

def calculate_spaced_repetition_interval(question_id, correct, previous_interval=1):
    """Calculate next review interval using spaced repetition algorithm"""
    if question_id not in st.session_state.question_history:
        st.session_state.question_history[question_id] = {
            'correct_count': 0,
            'total_attempts': 0,
            'last_seen': datetime.now(),
            'interval': 1,
            'ease_factor': 2.5
        }
    
    history = st.session_state.question_history[question_id]
    history['total_attempts'] += 1
    
    if correct:
        history['correct_count'] += 1
        # Increase interval based on performance
        if history['correct_count'] >= 2:
            history['interval'] = min(history['interval'] * history['ease_factor'], 30)
        else:
            history['interval'] = min(history['interval'] * 1.3, 7)
    else:
        # Reset interval for incorrect answers
        history['interval'] = 1
        history['ease_factor'] = max(history['ease_factor'] - 0.2, 1.3)
    
    history['last_seen'] = datetime.now()
    return history['interval']

def get_adaptive_questions(target_case=None, difficulty='adaptive', num_questions=5):
    """Get questions based on user performance and spaced repetition"""
    available_questions = PRACTICE_QUESTIONS.get(target_case, []) if target_case else []
    
    # Add quiz questions of the same case
    quiz_questions_filtered = [q for q in QUIZ_QUESTIONS if not target_case or q['case'] == target_case]
    
    # Convert to practice format
    for q in quiz_questions_filtered:
        available_questions.append({
            'question': q['question'],
            'correct': q['correct'],
            'context': q.get('context', 'general'),
            'id': q['id']
        })
    
    if difficulty == 'adaptive':
        # Prioritize questions that need review based on spaced repetition
        now = datetime.now()
        questions_with_priority = []
        
        for q in available_questions:
            q_id = q.get('id', hash(q['question']))
            if q_id in st.session_state.question_history:
                history = st.session_state.question_history[q_id]
                days_since = (now - history['last_seen']).days
                if days_since >= history['interval']:
                    priority = history['interval'] - days_since  # Higher priority for overdue
                    questions_with_priority.append((q, priority))
            else:
                questions_with_priority.append((q, 100))  # New questions get high priority
        
        # Sort by priority and take top questions
        questions_with_priority.sort(key=lambda x: x[1], reverse=True)
        selected = [q[0] for q in questions_with_priority[:num_questions]]
    else:
        selected = random.sample(available_questions, min(num_questions, len(available_questions)))
    
    random.shuffle(selected)
    return selected

def update_achievements(analysis=None):
    """Check and update user achievements"""
    profile = st.session_state.user_profile
    new_achievements = []
    
    # First quiz completion
    if 'first_quiz' not in profile['achievements'] and st.session_state.quiz_completed:
        profile['achievements'].append('first_quiz')
        new_achievements.append('first_quiz')
    
    # Perfect score on diagnostics
    if analysis and analysis['total_correct'] == 12 and 'perfectionist' not in profile['achievements']:
        profile['achievements'].append('perfectionist')
        new_achievements.append('perfectionist')
    
    # Basic questions mastery
    if analysis:
        basic_questions = [q for q in QUIZ_QUESTIONS if q['level'] == 'basic']
        basic_correct = sum(1 for item in analysis['detailed_feedback'] 
                          if any(q['id'] == item['question'] and q['level'] == 'basic' 
                                for q in QUIZ_QUESTIONS) and item['correct'])
        if basic_correct == len(basic_questions) and 'perfect_basic' not in profile['achievements']:
            profile['achievements'].append('perfect_basic')
            new_achievements.append('perfect_basic')
    
    # Case specialist - no errors in any case
    if analysis and not analysis['case_errors'].values() and 'case_specialist' not in profile['achievements']:
        profile['achievements'].append('case_specialist') 
        new_achievements.append('case_specialist')
    
    return new_achievements

def generate_comprehensive_feedback(analysis):
    """Enhanced AI feedback with personalized recommendations"""
    score_percent = (analysis["total_correct"] / 12) * 100
    profile = st.session_state.user_profile
    
    feedback = f"## 🎯 Personal German Case Analysis\n\n"
    feedback += f"**Your Score: {analysis['total_correct']}/12 ({score_percent:.0f}%)**\n\n"
    
    # Personalized greeting based on performance history
    if profile['total_sessions'] > 1:
        prev_accuracy = (profile['total_correct'] / profile['total_questions']) * 100 if profile['total_questions'] > 0 else 0
        if score_percent > prev_accuracy:
            feedback += f"🎉 **Excellent improvement!** You've increased your accuracy from {prev_accuracy:.0f}% to {score_percent:.0f}%!\n\n"
        elif score_percent == prev_accuracy:
            feedback += f"📈 **Consistent performance!** You're maintaining your {score_percent:.0f}% accuracy.\n\n"
        else:
            feedback += f"💪 **Keep practicing!** Every expert has ups and downs. Your overall progress is still strong.\n\n"
    
    # Performance assessment with learning path
    if score_percent >= 90:
        feedback += "🏆 **Outstanding!** You have excellent command of German cases. Ready for advanced German grammar!\n\n"
        feedback += "**🎯 Next Challenge:** Try complex sentence structures with multiple cases\n\n"
    elif score_percent >= 80:
        feedback += "🌟 **Very Good!** You understand German cases well. Just need fine-tuning!\n\n"
        feedback += "**🎯 Next Step:** Focus on the trickiest patterns and exceptions\n\n"
    elif score_percent >= 60:
        feedback += "📚 **Good Progress!** You're getting the fundamentals. Time to solidify your knowledge!\n\n"
        feedback += "**🎯 Next Step:** Regular practice with your weak areas\n\n"
    elif score_percent >= 40:
        feedback += "🚀 **Building Foundation!** You understand some patterns. Let's strengthen the basics!\n\n"
        feedback += "**🎯 Next Step:** Focus on one case at a time with lots of examples\n\n"
    else:
        feedback += "🌱 **Great Start!** Every German learner starts here. You're building important foundations!\n\n"
        feedback += "**🎯 Next Step:** Start with Nominativ and Akkusativ - the most common cases\n\n"
    
    # Strengths analysis
    if analysis["strengths"]:
        feedback += f"### 🟢 Your Strengths\n"
        for strength in analysis["strengths"]:
            case_count = len([q for q in QUIZ_QUESTIONS if q['case'] == strength])
            feedback += f"- **{strength.capitalize()}** - Perfect {case_count}/{case_count}! 🎯\n"
        feedback += "\n"
    
    # Detailed weak area analysis with specific recommendations
    if analysis["weakest_areas"]:
        feedback += f"### 🔴 Priority Focus Areas\n"
        
        for case in analysis["weakest_areas"]:
            error_count = analysis["case_errors"][case]
            case_questions = [q for q in QUIZ_QUESTIONS if q['case'] == case]
            
            feedback += f"\n**{case.upper()} Case** ({error_count} errors)\n"
            
            # Case-specific deep dive
            if case == "dativ":
                feedback += "```\n🎯 DATIV Mastery Plan:\n"
                feedback += "• Key Question: 'wem?' (to/for whom?)\n"
                feedback += "• Must-Know Verbs: geben, helfen, gehören, danken, antworten\n"
                feedback += "• Always Dativ: mit, bei, von, zu, aus, nach, seit\n"
                feedback += "• Pattern: der→dem, die→der, das→dem, mein→meinem/meiner\n"
                feedback += "• Memory Trick: 'I give TO someone' = Dativ\n```\n"
                
            elif case == "akkusativ":
                feedback += "```\n🎯 AKKUSATIV Mastery Plan:\n"
                feedback += "• Key Question: 'wen/was?' (whom/what?)\n"
                feedback += "• Most Common: Direct objects of action verbs\n" 
                feedback += "• Always Akkusativ: durch, für, ohne, um, gegen, bis\n"
                feedback += "• Pattern: der→den, die→die, das→das, mein→meinen/meine\n"
                feedback += "• Memory Trick: 'I see WHAT/WHOM directly' = Akkusativ\n```\n"
                
            elif case == "genitiv":
                feedback += "```\n🎯 GENITIV Mastery Plan:\n"
                feedback += "• Key Question: 'wessen?' (whose?)\n"
                feedback += "• Main Use: Showing possession/relationship\n"
                feedback += "• Prepositions: trotz, während, wegen, statt, außerhalb\n"
                feedback += "• Pattern: der→des, die→der, das→des + noun often gets -(e)s\n"
                feedback += "• Memory Trick: 'The car OF my sister' = Genitiv\n```\n"
                
            elif case == "nominativ":
                feedback += "```\n🎯 NOMINATIV Mastery Plan:\n"
                feedback += "• Key Question: 'wer/was?' (who/what does the action?)\n"
                feedback += "• Always: Subject of sentence, after 'sein/werden/bleiben'\n"
                feedback += "• No Change: Use dictionary form\n"
                feedback += "• Pattern: der/die/das stay unchanged\n"
                feedback += "• Memory Trick: 'WHO does something' = Nominativ\n```\n"
    
    # Learning recommendations based on error patterns
    type_errors = analysis.get("type_errors", {})
    max_type_errors = max(type_errors.values()) if type_errors.values() else 0
    
    if max_type_errors > 1:
        for error_type, count in type_errors.items():
            if count == max_type_errors:
                if "possessive" in error_type:
                    feedback += "\n📚 **Extra Focus Needed:** Possessive Pronouns\n"
                    feedback += "• mein/dein/sein/ihr/unser/euer follow the same pattern as articles\n"
                    feedback += "• Example: mein→meinen (Akk.), meinem (Dat.), meines (Gen.)\n\n"
                elif "adjective" in error_type:
                    feedback += "\n📚 **Extra Focus Needed:** Adjective Declensions\n"
                    feedback += "• Adjectives must match their noun's case, gender, and number\n"
                    feedback += "• After der/die/das: mostly -e or -en endings\n"
                    feedback += "• After ein/kein: more varied endings\n\n"
    
    # Personalized study plan
    feedback += "## 📋 Your Personalized Study Plan\n\n"
    
    if len(analysis["weakest_areas"]) >= 3:
        feedback += "**Week 1-2:** Focus on your weakest case first\n"
        feedback += f"**Week 3-4:** Master {analysis['weakest_areas'][1] if len(analysis['weakest_areas']) > 1 else 'mixed practice'}\n"
        feedback += "**Week 5+:** Mixed case practice and real-world application\n\n"
    elif len(analysis["weakest_areas"]) == 2:
        feedback += "**This Week:** Alternate between your two challenge areas\n"
        feedback += "**Next Week:** Mixed practice combining all cases\n\n"
    elif len(analysis["weakest_areas"]) == 1:
        feedback += "**This Week:** Intensive practice with your challenge case\n"
        feedback += "**Next Week:** Advanced mixed exercises\n\n"
    else:
        feedback += "**This Week:** Advanced German grammar topics!\n"
        feedback += "**Suggested Topics:** Subjunctive mood, passive voice, complex sentences\n\n"
    
    return feedback

# Sidebar for user profile and navigation
with st.sidebar:
    st.title("🎓 Your Progress")
    
    # User profile section
    with st.expander("👤 Profile", expanded=True):
        name = st.text_input("Name:", st.session_state.user_profile['name'])
        if name != st.session_state.user_profile['name']:
            st.session_state.user_profile['name'] = name
        
        level = st.selectbox("Level:", ['beginner', 'intermediate', 'advanced'], 
                           index=['beginner', 'intermediate', 'advanced'].index(st.session_state.user_profile['level']))
        st.session_state.user_profile['level'] = level
    
    # Progress statistics
    profile = st.session_state.user_profile
    if profile['total_questions'] > 0:
        accuracy = (profile['total_correct'] / profile['total_questions']) * 100
        st.metric("Overall Accuracy", f"{accuracy:.1f}%")
        st.metric("Total Questions", profile['total_questions'])
        st.metric("Sessions Completed", profile['total_sessions'])
    
    # Achievements
    if profile['achievements']:
        st.subheader("🏆 Achievements")
        for achievement in profile['achievements']:
            if achievement in ACHIEVEMENTS:
                st.success(f"{ACHIEVEMENTS[achievement]['name']}")
    
    # Quick navigation
    st.subheader("🚀 Quick Actions")
    
    if st.button("📊 New Diagnostic", use_container_width=True):
        # Reset quiz state
        st.session_state.quiz_completed = False
        st.session_state.quiz_answers = {}
        st.session_state.analysis_done = False
        st.session_state.current_mode = 'diagnostic'
        st.rerun()
    
    if st.button("⚡ Quick Practice", use_container_width=True):
        st.session_state.current_mode = 'quick_practice'
        st.session_state.practice_questions = get_adaptive_questions(num_questions=5)
        st.rerun()
    
    if st.button("🎯 Targeted Practice", use_container_width=True):
        st.session_state.current_mode = 'case_selection'
        st.rerun()

# Main content area
st.title("🇩🇪 German Case Master")
st.markdown("*Master German cases with AI-powered adaptive learning*")

# Mode-based content rendering
if st.session_state.current_mode == 'case_selection':
    st.header("🎯 Choose Your Focus Area")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 Case Practice")
        cases = ['nominativ', 'akkusativ', 'dativ', 'genitiv']
        for case in cases:
            if st.button(f"Practice {case.upper()}", key=f"case_{case}", use_container_width=True):
                st.session_state.current_mode = 'targeted_practice'
                st.session_state.target_case = case
                st.session_state.practice_questions = get_adaptive_questions(case, num_questions=8)
                st.rerun()
    
    with col2:
        st.subheader("🎮 Practice Modes")
        if st.button("🔀 Mixed Cases", use_container_width=True):
            st.session_state.current_mode = 'mixed_practice'
            st.session_state.practice_questions = get_adaptive_questions(num_questions=10)
            st.rerun()
        
        if st.button("🎲 Multiple Choice", use_container_width=True):
            st.session_state.current_mode = 'multiple_choice'
            st.session_state.practice_questions = MULTIPLE_CHOICE_QUESTIONS.copy()
            random.shuffle(st.session_state.practice_questions)
            st.rerun()
        
        if st.button("⚡ Speed Round", use_container_width=True):
            st.session_state.current_mode = 'speed_round'
            st.session_state.practice_questions = get_adaptive_questions(num_questions=15)
            st.session_state.session_stats = {'correct': 0, 'total': 0, 'start_time': datetime.now()}
            st.rerun()

elif st.session_state.current_mode == 'multiple_choice':
    st.header("🎲 Multiple Choice Practice")
    
    if st.session_state.practice_questions:
        current_q = st.session_state.practice_questions[0]
        
        st.write(f"**Question:** {current_q['question']}")
        
        selected = st.radio("Choose the correct answer:", current_q['options'], key="mc_answer")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Check Answer"):
                correct = selected == current_q['correct']
                if correct:
                    st.success(f"🎉 Correct! {current_q['explanation']}")
                else:
                    st.error(f"❌ Wrong. Correct: {current_q['correct']}\n{current_q['explanation']}")
                
                st.session_state.practice_questions.pop(0)
                if st.session_state.practice_questions:
                    st.rerun()
                else:
                    st.success("🎉 Multiple Choice Practice Complete!")
        
        with col2:
            if st.button("💡 Explain"):
                st.info(f"**Grammar Point:** {current_q['explanation']}")
        
        with col3:
            if st.button("⏭️ Skip"):
                st.session_state.practice_questions.pop(0)
                if st.session_state.practice_questions:
                    st.rerun()
        
        st.progress((len(MULTIPLE_CHOICE_QUESTIONS) - len(st.session_state.practice_questions)) / len(MULTIPLE_CHOICE_QUESTIONS))
    
    else:
        st.success("🎉 Multiple Choice Session Complete!")
        if st.button("🔄 Practice Again"):
            st.session_state.practice_questions = MULTIPLE_CHOICE_QUESTIONS.copy()
            random.shuffle(st.session_state.practice_questions)
            st.rerun()

elif st.session_state.current_mode == 'speed_round':
    st.header("⚡ Speed Round Challenge")
    
    if not st.session_state.session_stats['start_time']:
        st.session_state.session_stats['start_time'] = datetime.now()
    
    elapsed = datetime.now() - st.session_state.session_stats['start_time']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏱️ Time", f"{elapsed.seconds}s")
    with col2:
        st.metric("✅ Correct", st.session_state.session_stats['correct'])
    with col3:
        st.metric("📊 Total", st.session_state.session_stats['total'])
    
    if st.session_state.practice_questions and elapsed.seconds < 300:  # 5 minute limit
        current_q = st.session_state.practice_questions[0]
        
        st.write(f"**Quick! Fill in the blank:**")
        st.write(current_q['question'])
        
        answer = st.text_input("Your answer:", key=f"speed_{st.session_state.session_stats['total']}")
        
        if st.button("⚡ Submit") and answer:
            correct = answer.strip().lower() == current_q['correct'].lower()
            st.session_state.session_stats['total'] += 1
            
            if correct:
                st.session_state.session_stats['correct'] += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Wrong. Answer: {current_q['correct']}")
            
            st.session_state.practice_questions.pop(0)
            st.rerun()
    
    else:
        # Speed round finished
        accuracy = (st.session_state.session_stats['correct'] / st.session_state.session_stats['total']) * 100 if st.session_state.session_stats['total'] > 0 else 0
        st.header("🏁 Speed Round Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Final Score", f"{st.session_state.session_stats['correct']}/{st.session_state.session_stats['total']}")
        with col2:
            st.metric("Accuracy", f"{accuracy:.1f}%")
        
        if accuracy >= 80:
            st.success("🏆 Excellent speed and accuracy!")
        elif accuracy >= 60:
            st.success("🎯 Good performance under pressure!")
        else:
            st.info("💪 Keep practicing for better speed!")

elif st.session_state.current_mode in ['targeted_practice', 'mixed_practice', 'quick_practice']:
    case_name = st.session_state.get('target_case', 'Mixed Cases').title()
    st.header(f"🎯 {case_name} Practice")
    
    if st.session_state.practice_questions:
        current_q = st.session_state.practice_questions[0]
        progress = 1 - (len(st.session_state.practice_questions) / max(len(st.session_state.practice_questions) + 1, 8))
        
        st.progress(progress)
        st.write(f"**Question {max(8 - len(st.session_state.practice_questions) + 1, 1)}:** {current_q['question']}")
        
        # Context badge
        if 'context' in current_q:
            context_emoji = {
                'family': '👨‍👩‍👧‍👦', 'education': '📚', 'food': '🍎', 'weather': '🌤️',
                'transportation': '🚌', 'shopping': '🛒', 'entertainment': '🎭'
            }
            st.badge(f"{context_emoji.get(current_q['context'], '💬')} {current_q['context'].replace('_', ' ').title()}")
        
        answer = st.text_input("Your answer:", key=f"practice_{len(st.session_state.practice_questions)}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Check", use_container_width=True) and answer:
                correct = answer.strip().lower() == current_q['correct'].lower()
                
                # Update spaced repetition
                if 'id' in current_q:
                    calculate_spaced_repetition_interval(current_q['id'], correct)
                
                # Show feedback
                if correct:
                    st.success(f"🎉 Perfect! '{current_q['correct']}'")
                    if st.session_state.show_explanations and 'explanation' in current_q:
                        st.info(current_q['explanation'])
                else:
                    st.error(f"❌ Correct answer: '{current_q['correct']}'")
                    if 'explanation' in current_q:
                        st.info(f"💡 {current_q['explanation']}")
                
                # Move to next question
                st.session_state.practice_questions.pop(0)
                if st.session_state.practice_questions:
                    st.rerun()
                else:
                    st.success("🎉 Practice session complete! Great job!")
        
        with col2:
            if st.button("💡 Hint", use_container_width=True):
                hints = {
                    "dativ": "Ask yourself: 'To whom?' or 'For whom?'",
                    "akkusativ": "Ask yourself: 'Whom?' or 'What?' (direct object)",
                    "genitiv": "Ask yourself: 'Whose?' (shows possession)",
                    "nominativ": "Ask yourself: 'Who?' or 'What?' (subject)"
                }
                # Try to detect case from question or use general hint
                case_hint = "Think about the grammar rule for this case!"
                for case, hint in hints.items():
                    if case in current_q.get('question', '').lower():
                        case_hint = hint
                        break
                st.info(case_hint)
        
        with col3:
            if st.button("⏭️ Skip", use_container_width=True):
                st.session_state.practice_questions.pop(0)
                if st.session_state.practice_questions:
                    st.rerun()
    
    else:
        st.success("🎉 Practice Complete!")
        if st.button("🔄 More Practice", use_container_width=True):
            case = st.session_state.get('target_case')
            st.session_state.practice_questions = get_adaptive_questions(case, num_questions=8)
            st.rerun()

elif not st.session_state.quiz_completed:
    # Main diagnostic quiz
    st.header("📋 German Case Diagnostic")
    
    with st.expander("ℹ️ How This Works", expanded=True):
        st.markdown("""
        **🎯 This diagnostic will:**
        - Test all 4 German cases (Nominativ, Akkusativ, Dativ, Genitiv)
        - Analyze your strengths and weaknesses
        - Create a personalized study plan
        - Track your progress over time
        
        **💡 Tips:**
        - Take your time and think about each answer
        - Use the hints if you're unsure
        - Don't worry about mistakes - they help us learn!
        """)
    
    # Settings
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.show_explanations = st.checkbox("Show explanations after answers", value=True)
    with col2:
        difficulty = st.selectbox("Question difficulty:", ['adaptive', 'basic', 'intermediate', 'advanced'])
    
    # Filter questions by difficulty if not adaptive
    questions_to_use = QUIZ_QUESTIONS
    if difficulty != 'adaptive':
        questions_to_use = [q for q in QUIZ_QUESTIONS if q['level'] == difficulty or q['level'] == 'basic']
    
    # Quiz form
    with st.form("comprehensive_diagnostic"):
        answers = {}
        
        for i, q in enumerate(questions_to_use):
            st.markdown(f"### Question {i+1}")
            st.write(q['question'])
            
            # Show context and level info
            level_colors = {'basic': '🟢', 'intermediate': '🟡', 'advanced': '🔴', 'complex': '🟣'}
            st.caption(f"{level_colors.get(q['level'], '⚪')} {q['level'].title()} | Case: {q['case'].title()} | Type: {q['type'].replace('_', ' ').title()}")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                answers[f"q_{q['id']}"] = st.text_input(
                    "Your answer:", 
                    key=f"q_{q['id']}",
                    placeholder="Enter the correct German form..."
                )
            with col2:
                if st.checkbox(f"💡", key=f"hint_{q['id']}"):
                    st.info(q['hint'])
            
            st.divider()
        
        submitted = st.form_submit_button("🚀 Analyze My German Skills!", use_container_width=True)
        
        if submitted:
            unanswered = [i+1 for i, q in enumerate(questions_to_use) if not answers[f"q_{q['id']}"].strip()]
            
            if unanswered:
                st.error(f"Please answer all questions! Missing: {', '.join(map(str, unanswered))}")
            else:
                st.session_state.quiz_answers = answers
                st.session_state.quiz_completed = True
                st.session_state.user_profile['total_sessions'] += 1
                st.rerun()

else:
    # Results and analysis
    if not st.session_state.analysis_done:
        with st.spinner("🤖 AI analyzing your German skills..."):
            # Analyze results
            analysis = analyze_quiz_results(st.session_state.quiz_answers)
            
            # Update user profile
            profile = st.session_state.user_profile
            profile['total_correct'] += analysis['total_correct']
            profile['total_questions'] += 12
            profile['last_session'] = datetime.now().isoformat()
            
            # Check for achievements
            new_achievements = update_achievements(analysis)
            
            # Generate comprehensive feedback
            feedback = generate_comprehensive_feedback(analysis)
            
            # Store in session state
            st.session_state.analysis = analysis
            st.session_state.feedback = feedback
            st.session_state.new_achievements = new_achievements
            st.session_state.analysis_done = True
    
    # Show new achievements
    if st.session_state.get('new_achievements'):
        for achievement in st.session_state.new_achievements:
            if achievement in ACHIEVEMENTS:
                st.balloons()
                st.success(f"🏆 **New Achievement Unlocked!** {ACHIEVEMENTS[achievement]['name']}\n{ACHIEVEMENTS[achievement]['description']}")
        st.session_state.new_achievements = []  # Clear after showing
    
    # Main feedback
    st.markdown(st.session_state.feedback)
    
    # Interactive action buttons
    st.subheader("🚀 What's Next?")
    
    if st.session_state.analysis["weakest_areas"]:
        st.write("**Recommended Practice:**")
        cols = st.columns(min(len(st.session_state.analysis["weakest_areas"]), 4))
        
        for i, case in enumerate(st.session_state.analysis["weakest_areas"][:4]):
            with cols[i]:
                if st.button(f"Master {case.upper()}", key=f"master_{case}", use_container_width=True):
                    st.session_state.current_mode = 'targeted_practice'
                    st.session_state.target_case = case
                    st.session_state.practice_questions = get_adaptive_questions(case, num_questions=8)
                    st.rerun()
    else:
        st.success("🎉 **Congratulations!** You've mastered all basic German cases!")
        if st.button("🎯 Advanced Challenges", use_container_width=True):
            st.session_state.current_mode = 'case_selection'
            st.rerun()
    
    # Additional options
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎲 Mixed Practice", use_container_width=True):
            st.session_state.current_mode = 'mixed_practice'
            st.session_state.practice_questions = get_adaptive_questions(num_questions=10)
            st.rerun()
    
    with col2:
        if st.button("⚡ Speed Challenge", use_container_width=True):
            st.session_state.current_mode = 'speed_round'
            st.session_state.practice_questions = get_adaptive_questions(num_questions=15)
            st.session_state.session_stats = {'correct': 0, 'total': 0, 'start_time': datetime.now()}
            st.rerun()
    
    with col3:
        if st.button("📊 New Diagnostic", use_container_width=True):
            st.session_state.quiz_completed = False
            st.session_state.quiz_answers = {}
            st.session_state.analysis_done = False
            st.session_state.current_mode = 'diagnostic'
            st.rerun()
    
    # Detailed analysis in expandable sections
    with st.expander("🔍 Detailed Question Analysis"):
        for item in st.session_state.analysis["detailed_feedback"]:
            if item["correct"]:
                st.success(item["explanation"])
            else:
                st.error(item["explanation"])
    
    with st.expander("📈 Performance Analytics"):
        # Visual performance breakdown
        import pandas as pd
        
        # Case performance chart
        case_data = []
        for case in ['nominativ', 'akkusativ', 'dativ', 'genitiv']:
            case_questions = [q for q in QUIZ_QUESTIONS if q['case'] == case]
            errors = st.session_state.analysis["case_errors"][case]
            correct = len(case_questions) - errors
            accuracy = (correct / len(case_questions)) * 100
            case_data.append({
                'Case': case.capitalize(),
                'Correct': correct,
                'Total': len(case_questions),
                'Accuracy': accuracy
            })
        
        df = pd.DataFrame(case_data)
        st.bar_chart(df.set_index('Case')['Accuracy'])
        st.dataframe(df, use_container_width=True)

# Footer with app info
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🇩🇪 German Case Master v1.0")
with col2:
    st.caption("Built with ❤️ for systematic language learning")
with col3:
    if st.session_state.user_profile['total_questions'] > 0:
        overall_accuracy = (st.session_state.user_profile['total_correct'] / st.session_state.user_profile['total_questions']) * 100
        st.caption(f"Your overall accuracy: {overall_accuracy:.1f}%")
                