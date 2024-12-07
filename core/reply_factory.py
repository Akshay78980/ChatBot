
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is not None:
        current_question_id -= 1
        if current_question_id < len(PYTHON_QUESTION_LIST):
            question_el = PYTHON_QUESTION_LIST[current_question_id]

            question_and_answers = session.get('question_and_answers',[])

            if answer.strip() == question_el['answer']:
                total = session.get('total',0)
                total += 1
                session['total'] = total

            question_and_answers.append(question_el)
            question_and_answers[current_question_id]['your_ans'] = answer.strip()
            session['question_and_answers'] = question_and_answers
            
    
    else:
        session['total'] = 0
        session['question_and_answers'] = []

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''    
    if current_question_id is not None:
        if current_question_id < len(PYTHON_QUESTION_LIST):
            return PYTHON_QUESTION_LIST[current_question_id]['question_text'] + '<br><br> Options : <br>' + "<br>".join(PYTHON_QUESTION_LIST[current_question_id]['options']), current_question_id + 1
    else:
        return PYTHON_QUESTION_LIST[0]['question_text'] + '<br><br> Options : <br>' + "<br>".join(PYTHON_QUESTION_LIST[0]['options']), 1
    
    return "", 0


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    question_and_answers = session.get('question_and_answers')
    res = ""
    for item in question_and_answers:
        question_string = "Question : " + item['question_text'] + "<br>"
        correct_ans_string = "Correct Ans : " + item['answer'] + "<br>"
        your_ans_string = "Your Ans : " + item['your_ans'] + "<br>"
        res += question_string + correct_ans_string + your_ans_string + "<br>"

    res += "<br>Total score : " + str(session.get('total',0))

    return res

