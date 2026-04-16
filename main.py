import hashlib
import json
import base64
import requests

session = requests.Session()
session.headers.update({
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
    'origin': 'https://cointiply.com',
    'referer': 'https://cointiply.com/login',
})

chalresp = session.get(
    "https://verify.cointiply.com/v1/challenge",
    params={"apiKey": "key_1jctbboe300f0ahtlq2"},
    headers={"accept": "*/*", "sec-fetch-site": "same-site"},
)
cdata = chalresp.json()
print("challenge:", cdata)


def sc(data: dict) -> str:
    salt    = data["salt"]
    target  = data["challenge"]
    max_num = data.get("maxNumber") or data.get("maxnumber", 100000)
    algorithm = data.get("algorithm", "SHA-256")

    for num in range(max_num + 1):
        digest = hashlib.sha256(f"{salt}{num}".encode()).hexdigest()
        if digest == target:
            payload = {
                "algorithm": algorithm,
                "challenge":  target,
                "number":     num,
                "salt":       salt,
                "signature":  data["signature"],
                "verified":   True,
            }
            encoded = base64.b64encode(json.dumps(payload).encode()).decode()
            print(f"solved solution: number={num}")
            return encoded

    raise ValueError("solve failed")

payl = sc(cdata)


rsp = session.post(
    'https://verify.cointiply.com/v1/verify',
    params={'apiKey': "key_1jctbboe300f0ahtlq2"},
    headers={
        'accept': '*/*',
        'content-type': 'application/json',
        'sec-fetch-site': 'same-site',
    },
    json={"payload": payl},
)
vdata = rsp.json()
print("verify:", rsp.status_code, json.dumps(vdata, indent=2))


cap = vdata["payload"]


session.get('https://cointiply.com/login')
xsrf = session.cookies.get("XSRF-TOKEN")
if xsrf:
    print(f"xsrf: {xsrf}")
session.headers.update({
    'x-xsrf-token':     xsrf,
    'x-requested-with': 'XMLHttpRequest',
    'content-type':     'application/json',
    'accept':           'application/json, text/plain, */*',
    'sec-fetch-site':   'same-origin',
})


resp = session.post(
    'https://cointiply.com/userlogin',
    params={'__cb': '20251215'},
    json={
        'email':             'email@gmail.com',
        'password':          'password',
        'redirect':          None,
        'captcha_code':      cap,
        'captcha_challenge': 'altcha',
        'captcha_type':      'altcha',
    },
)
print(resp.text)