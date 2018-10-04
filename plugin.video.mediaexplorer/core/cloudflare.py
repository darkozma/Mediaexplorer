# -*- coding: utf-8 -*-
from core.libs import *
from decimal import Decimal


class Cloudflare:
    def __init__(self, response):
        self.timeout = 5
        self.domain = urlparse.urlparse(response["url"])[1]
        self.protocol = urlparse.urlparse(response["url"])[0]

        pattern = r'var s,t,o,p,b,r,e,a,k,i,n,g,f, ([^=]+)={"([^"]+)":' \
                  r'(?P<value>[^}]+).*?' \
                  r'(?:\1.\2(?P<op0>[+\-*/])=(?P<val0>[^;]+);)?' \
                  r'(?:\1.\2(?P<op1>[+\-*/])=(?P<val1>[^;]+);)?' \
                  r'(?:\1.\2(?P<op2>[+\-*/])=(?P<val2>[^;]+);)?' \
                  r'(?:\1.\2(?P<op3>[+\-*/])=(?P<val3>[^;]+);)?' \
                  r'(?:\1.\2(?P<op4>[+\-*/])=(?P<val4>[^;]+);)?' \
                  r'(?:\1.\2(?P<op5>[+\-*/])=(?P<val5>[^;]+);)?' \
                  r'(?:\1.\2(?P<op6>[+\-*/])=(?P<val6>[^;]+);)?' \
                  r'(?:\1.\2(?P<op7>[+\-*/])=(?P<val7>[^;]+);)?' \
                  r'(?:\1.\2(?P<op8>[+\-*/])=(?P<val8>[^;]+);)?' \
                  r'(?:\1.\2(?P<op9>[+\-*/])=(?P<val9>[^;]+);)?' \
                  r'a.value.*?, (?P<wait>\d+)\);.*?' \
                  r'<form id="challenge-form" action="(?P<auth_url>[^"]+)" method="get">[^<]+' \
                  r'<input type="hidden" name="jschl_vc" value="(?P<jschl_vc>[^"]+)[^<]+' \
                  r'<input type="hidden" name="pass" value="(?P<pass>[^"]+)"/>'

        match = re.compile(pattern, re.DOTALL).search(response['data'])
        if match:
            self.js_data = {
                "auth_url": match.group('auth_url'),
                "params": {
                    "jschl_vc": match.group('jschl_vc'),
                    "pass": match.group('pass'),
                },
                "value": match.group('value'),
                "op": [
                    [
                        match.group('op%s' % x),
                        match.group('val%s' % x)
                    ]
                    for x in range(9) if match.group('val%s' % x)
                ],
                "wait": int(match.group('wait')) / 1000,
            }

        else:
            self.js_data = dict()

        if response["headers"].get("refresh"):
            try:
                self.header_data = {
                    "auth_url": response["headers"]["refresh"].split("=")[1].split("?")[0],
                    "params": {
                        "pass": response["headers"]["refresh"].split("=")[2]
                    },
                    "wait": int(response["headers"]["refresh"].split(";")[0])
                }
            except Exception:
                self.header_data = dict()
        else:
            self.header_data = dict()

    @property
    def wait_time(self):
        if self.js_data:
            return self.js_data["wait"]
        else:
            return self.header_data["wait"]

    @property
    def is_cloudflare(self):
        return bool(self.header_data or self.js_data)

    def get_url(self):
        # Metodo #1 (javascript)
        if self.js_data:
            jschl_answer = self.decode(self.js_data["value"])

            for op, v in self.js_data["op"]:
                st = "%s %s %s" % (jschl_answer, op, self.decode(v))
                jschl_answer = Decimal(format(eval(st), '.15f'))

            self.js_data["params"]["jschl_answer"] = round(jschl_answer, 10) + len(self.domain)

            response = "%s://%s%s?%s" % (
                self.protocol,
                self.domain,
                self.js_data["auth_url"],
                urllib.urlencode(self.js_data["params"])
            )

            time.sleep(self.js_data["wait"])

            return response

        # Metodo #2 (headers)
        if self.header_data:
            response = "%s://%s%s?%s" % (
                self.protocol,
                self.domain,
                self.header_data["auth_url"],
                urllib.urlencode(self.header_data["params"])
            )

            time.sleep(self.header_data["wait"])

            return response


    def decode(self, data):
        data = re.sub("\!\+\[\]", "1", data)
        data = re.sub("\!\!\[\]", "1", data)
        data = re.sub("\[\]", "0", data)

        pos = data.find("/")
        numerador = data[:pos]
        denominador = data[pos + 1:]

        aux = re.compile('\(([0-9\+]+)\)').findall(numerador)
        num1 = ""
        for n in aux:
            num1 += str(eval(n))

        aux = re.compile('\(([0-9\+]+)\)').findall(denominador)
        num2 = ""
        for n in aux:
            num2 += str(eval(n))

        res = Decimal(float(num1) / float(num2))
        return Decimal(format(res, '.15f'))
