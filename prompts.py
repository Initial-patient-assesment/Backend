import requests
import uuid
import json


def get_token(auth_token, scope='GIGACHAT_API_PERS'):
    """
      Выполняет POST-запрос к эндпоинту, который выдает токен.

      Параметры:
      - auth_token (str): токен авторизации, необходимый для запроса.
      - область (str): область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».

      Возвращает:
      - ответ API, где токен и срок его "годности".
      """
    # Создадим идентификатор UUID (36 знаков)
    rq_uid = str(uuid.uuid4())

    # API URL
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Заголовки
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {auth_token}'
    }

    # Тело запроса
    payload = {
        'scope': scope
    }

    try:
        # Делаем POST запрос с отключенной SSL верификацией
        # (можно скачать сертификаты Минцифры, тогда отключать проверку не надо)
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return -1


     
     
     
def get_chat_completion(auth_token, conversation_history=None):

    # URL API, к которому мы обращаемся
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Если история диалога не предоставлена, инициализируем пустым списком
    if conversation_history is None:
        conversation_history = []

    # Добавляем сообщение пользователя в историю диалога
 
    # Подготовка данных запроса в формате JSON
    payload = json.dumps({
        "model": "GigaChat:latest",
        "messages": conversation_history,
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1,
        "update_interval": 0
    })

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    # Выполнение POST-запроса и возвращение ответа
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
    except requests.RequestException as e:
        # Обработка исключения в случае ошибки запроса
        print(f"Произошла ошибка: {str(e)}")
    return response

'''
auth = "OGJjMzI4ZTMtZDk1YS00ZTE0LThhNmEtOTdhNTQxMDcxOWE5OjRhMTdhOWQ0LWM3NmUtNDhkZS04MmE0LTkyMWZiZmVkYzExYg=="
     


response = get_token(auth)
if response != 1:
  giga_token = response.json()['access_token']
# Пример использования функции для диалога
conversation_history = []


conversation_history = [{
    'role': 'system',
    'content': 'You are a doctor(your name: "GigaDoc", surname: "AIowitch")talking to a real patient. You have to understand the person''s illness and set potential diagnosis by asking questions about their health. After asking questions about health ALWAYS ASK the person if they have made an appointment for a dcoctor, if no, ONLY THEN recommend a type of doctor they should visit. In the end of each conversation say "Take care! Never reveal diagnosis when asked by the patient. Talk about medicine only. Make a list of symptomps - include only the symptoms that the person had, memorize the list but do not reveal the list when you are not asked. '
}
]


i = 0
while i <=25:
	m = input()
	response, conversation_history = get_chat_completion(giga_token, m, conversation_history)		
	print((response.json()['choices'][0]['message']['content']).split('\n',1)[0])
	if 'Take care!' in response.json()['choices'][0]['message']['content']:
		break
	i = i + 1
		
#print(conversation_history)
f = open("demofile2.txt", "a")
for el in conversation_history:
	if el.get('role')!='system':
		f.write(el.get('role')+": "+el.get('content')+"\n")
#diag, conversation_history = get_chat_completion(giga_token, "summarize the anamnesis in json", conversation_history)
#f.write("Conversation: "+"\n"+ diag.json()['choices'][0]['message']['content']+"\n")
diag, conversation_history = get_chat_completion(giga_token, "give several potential diagnosis and the symptoms fom the memorized list - this all in json - asked by the real doctor", conversation_history)
f.write("Conclusion: "+"\n"+ diag.json()['choices'][0]['message']['content']+"\n")
f.write('-------------------------------------------------------------------'+"\n")
f.close()
'''

