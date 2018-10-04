# -*- coding: utf-8 -*-
from core.libs import *
import base64
import random
import string
import math

def get_video_url(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    
    if 'Archive no Encontrado' in data:
        return 'El archivo no existe'

    params = scrapertools.find_multiple_matches(data, 'input.*?name="([^"]*)" value="([^"]*)"')

    data = httptools.downloadpage(item.url, post=dict(params)).data
    key = scrapertools.find_single_match(data, 'data-sitekey="([^"]+)"')




    port = '443' if item.url.startswith('https') else '80'

    params = {
        'k': key,
        'co': base64.b64encode('%s:%s' % (urlparse.urlparse(item.url)[0] + '://' + urlparse.urlparse(item.url)[1], port)),
        'hl': 'es',
        'v': 'r20170906140949',
        'size': 'normal',
        'cb': int2base(int(math.floor(2147483648 * random.random())), 36) + int2base(
            abs(int(math.floor(2147483648 * random.random())) ^ int(time.time())), 36)
    }

    data = httptools.downloadpage('https://www.google.com/recaptcha/api2/anchor?' + urllib.urlencode(params)).data
    open('d:\\asd.html', 'wb').write(data)


    #bcr:
    a = []
    try {
    for (var b = (0,p.gd_.gd_)().firstChild; b; )
    a.push(Rm(b)),
    b = b.nextSibling
    } catch (c) {}
    return Cg(a)

    post = {
        'v': 'r20170906140949',
        'reason': 'fi',
        'bcr': '%5B1112069405%2C387249032%2C2143179418%2C246401906%2C-1624681564%2C-62677403%2C437642220%5D',
        'c': '03AOmkcwJc8ek9pR-auZBsCcfE3yS19t1cjVPikxeN4ckfRZOzvR8jwfIGr-sWzDNtIJWmKdFR3cY4bMaSaXh2tbviOWUkpzTSBI0Rp6ovpBpLk3azb69qCevdZLaRlTKrLCFO3VTu1cyspj1FFLCgqyyDTDgJr1CnBoGOfHvWn6nk6xjDq5CncodG4jsWreEzfmVcpyipdtC12IXHkd1KPqsGOy96JQm126BveJqjoN7gFzi1udwgJFBbcsqt0Pt_zu-8t781fS3fFyreKWQJyVQoThFBN9n9FXzGV_Mkc6ub51P-FOEvrCWTbT27JtxPjyEtNS1wm7gqBrTfTj2s386YCA01YhVnf126LEATRfpnP8ThaqM7tMNm4CG2Nk0TQX4xd3YtbDypsKuCD6ZQoW2RKqGLzoNmYC8BoMJTvbP_UFdnzVqHB_U',
        'chr': '%5B4%2C75%2C88%5D',
        'hr': '-131239433',
        'bg': '!urygvJ1H1AFG00KW0LVBUSDj_OtmRKAHAAAB8VcAAAE9nAUQ4_tkeBK4B_rHztiRrJy2r-ABFrritZsZU9jXGcD1eVPBvK0UWJyh9hDdgl_eahqdQ08CbD45wWP8I7OMYSi8Z0bjNQykyv7BxU4huwAt47SpT5-G8kJ03ZX-XUjH6N_RFG0gXPz4wsPCtKDXDTeWOf_HqxaPIxnu1jm0Cvkfz3vutJimyFeTalQdZeKLOINoZCxhqVR3ZMYzSYzCp5KBZAzA8Zbv2WW-dbf5bAdEzzwhv3vPgjlugdp1ShfKwS8nHxFw1Q18ZvoBUIwnTy7pokzKEdzabd4q9AGRbx9gA8zWuyXytgYz5EwCsVReQQB0YaFlbDqNAqmjMZ2wGfMq3oyx6J2dprSy2v16QLPYGv8JUgF1i-c5xigDooBoXHKFV1cC7DWwBvIno39oq70nht65TR_HdsCT-erbDb2yCRwXxs_3b81VW4_8mII09fAIobZcQyM3ejbahwqu8xNPTHys71yFI_h0TItM3F_Gf7CkaPp9c8w0r2NUNrPLGUuydzb52HDLVDnsDyjwa7YP4QN1FqFpKaOnq4exsOCQuvvqIlqy2Fv9WCGxGnHxqQpTZ_qjlH8UvgStz2g_XAEXYJAS4zBKdju3qqxWKMgv0ygw26Oc1sMgbyqYyGgv83i82nqtasPyqeO0hCQ6nAslRvIhhNtneggbO55g9M1YQPkK1XBDPIk6QO-AKkOhH3dARHKgcqBJRBTbb1I3D0fuSh7BtjCmdnJG5Oq4py1B3ytpo4unSw0b1z4Hg5s1xtiTGNl-JgKXBtn3aLn2tp8NR6R-TfN6eUuMCC7REvn57B1u1Ejcj0WrktXR1kI6apsiW95qE9BPDLzGFKh39nlfg9fI2r9dMK6_NuYv-_5y2MN2sybIs8bcjvvpmkcgGkMpRiL2Lg3AXg6-RYrPJAr5DYtlBQYcmaTL-qrXq8sxztggQ8siSy691KJ1x1IHcD-bPxFSUH4UsOiCGD-3kJlkQ8uqWYs8wZ04uQMSBPpAH2h6qSN8fjCHhomil9WBfgY2n9lchvVABs574S57RGn8KtDPgw82FnI7YuXT4-NbxeZC_ZPbxrWuiPpdATdrCX4uhJJt1tnokcGO6_XBaLQgkb-WdM_lju4pNEFK1VEJC6eYlU1dPw56OlgDdrSMvO0subCSCGqi8ic9W_UYSDSq4Q27LsN4fNimLNyapDR2rknxiCzAkq8kM0Q4W836qNybPBctdBLzzx0jenbA7oD76N-G6WbyuTyf_uH2-YTqEmXIJaXtkHVBm27EB_oCQPrVIT4q3jfmd3fvFx6-Khft7VMSaRWzNzU23kArUekqyE2s9lMPltGoon6kwUHuTdr_s8ga5Ps62fPiHRpYszvNol5xBkBii7xI4KyYLPkYgzXaXmLbYbrN9c0oIpmM_L7LR_uAaYN_Nte2tE89l0fZBtjwGdPzPSgCszHsQ6-VMaf7PqLQgrR-IXepSZ2PegxnXDEmo5UIaUB5gUaVTrM73msoANRYSudZRbte6DzEj1gOfyjHMDqugsAQXaqoO-29RWx5AaYcalaZ_Bg2U9iIezd5llH-UtCIu7aEhUPMtHPV0Tff7L0mZIcp6k4qT-Qt4vUV3k9UG7CVdNpae_2xQc8eTqDUntpqArFdUoxepSQMxrHJGcwTwILFraK5HAeaMql-KDj-G1lkPCScFQ7R-xFDKdpXzw-FTWxr-sK91Tv1WpEu_8HyAZ1xrqPrjmy8'

    }

    data = httptools.downloadpage('https://www.google.com/recaptcha/api2/reload?k=%s' % key, post = post).data
    open('d:\\asd.html', 'wb').write(data)
    #itemlist.append(Video(url=url, type=type))

    return itemlist


digs = string.digits + string.letters
def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[x % base])
        x /= base

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)
