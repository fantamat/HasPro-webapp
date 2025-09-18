import requests

LOGIN_URL = "http://localhost:8000/user/login/"
USERNAME = "admin"
PASSWORD = "admin"

LOGIN_TEST_URL = "http://localhost:8000/user/logout/"


def read_csrf_token(html_text):
    idx = html_text.find('name="csrfmiddlewaretoken"')
    if idx == -1:
        return ""
    start = html_text.find("value=", idx) + 7
    end = html_text.find('"', start)
    return html_text[start:end]



def login(session=None):
    if not session:
        session = requests.Session()

    # Get login page to fetch CSRF token
    response = session.get(LOGIN_URL)
    response.raise_for_status()

    csrf_token = read_csrf_token(response.text)

    login_data = {
        "login": USERNAME,
        "password": PASSWORD,
        "csrfmiddlewaretoken": csrf_token,
    }

    login_response = session.post(LOGIN_URL, data=login_data, headers={"Referer": LOGIN_URL})
    print("Login status code:", login_response.status_code)

    res = session.get(LOGIN_TEST_URL)

    if res.status_code != 200:
        raise Exception(f'Failed to login properly ({res.status_code})')

    return session

if __name__ == "__main__":
    login()