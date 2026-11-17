"""Swap the demo merchants for the RFP offer set (Dennis, 13 Nov 2026).

Card-linked, in-store offers use merchants from the mimojo card-linked network (UAE).
Affiliate and promo-code offers use Admitad GCC programmes and the 'Top offers for Lunedata' list.
Each old brand maps to a new brand of the same kind, so the offer covers, categories and amounts still fit.

apply(s, app) runs on the final built HTML of each prototype. It never touches embedded data: URIs.
Logos come from rfp-work/logos (downloaded from each brand's own site or Wikimedia Commons, 13 Nov 2026).
"""
import base64, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_DIR = os.path.join(ROOT, 'rfp-work', 'logos')
LUNE = 'https://brandlogos.azureedge.net/media/brand_logos/'
LDV = 'https://img.logo.dev/%s?token=pk_PCfI5A2ISc2tZmQNIql7Ww&size=128&format=png&retina=true'

# old name, new name, old Arabic, new Arabic, old logo files, old domains, new domain, logo file, old descriptor, new descriptor
B = [
    ('Carrefour', 'Grandiose', 'كارفور', 'جرانديوز', ['carrefour.png'], ['carrefouruae.com', 'carrefour.com'], 'grandiose.ae', 'grandiose.png', 'CARREFOUR', 'GRANDIOSE'),
    ('Lulu', 'Jones the Grocer', 'لولو', 'جونز ذا جروسر', [], ['luluhypermarket.com'], 'jonesthegrocer.com', 'jonesthegrocer.png', 'LULU HYPERMARKET', 'JONES THE GROCER'),
    ('Subway', 'Cafe Rider', 'صب واي', 'كافيه رايدر', ['Subway.png'], ['subway.com'], 'caferider.com', 'caferider.png', 'SUBWAY', 'CAFE RIDER'),
    ('KFC', 'Chowking', 'كنتاكي', 'تشاوكينج', ['KFC.png'], ['kfc.com', 'kfc.ae'], 'chowking.ph', 'chowking.png', 'KFC', 'CHOWKING'),
    ('Starbucks', 'Coffee Planet', 'ستاربكس', 'كوفي بلانيت', ['Starbucks_RsMC6xy.png'], ['starbucks.com', 'starbucks.ae'], 'coffeeplanet.com', 'coffeeplanet.jpg', 'STARBUCKS', 'COFFEE PLANET'),
    ('%Arabica', 'Gloria Jean’s', '% أرابيكا', 'جلوريا جينز', ['Arabica.png'], ['arabica.coffee', 'arabica.com'], 'gloriajeanscoffees.com', 'gloriajeans.png', '% ARABICA', 'GLORIA JEANS'),
    ("McDonald's", 'Krush Burger', 'ماكدونالدز', 'كراش برجر', ['McDonalds.png'], ['mcdonalds.com', 'mcdonalds.ae'], 'krushburger.com', 'krushburger.webp', 'MCDONALDS', 'KRUSH BURGER'),
    ('Shell', 'WashOn', 'شل', 'واش أون', ['Shell.png'], ['shell.com', 'shell.ae'], 'washon.ae', 'washon.png', 'SHELL', 'WASHON'),
    ('Spotify', 'Prime Video', 'سبوتيفاي', 'برايم فيديو', ['Spotify.png'], ['spotify.com'], 'primevideo.com', 'primevideo.png', 'SPOTIFY P', 'PRIMEVIDEO'),
    ('du', 'Samsung', 'دو', 'سامسونج', [], ['du.ae'], 'samsung.com', 'samsung.png', 'DU TELECOM', 'SAMSUNG AE'),
    ('Expedia', 'Booking.com', 'إكسبيديا', 'بوكينج', [], ['expedia.ae', 'expedia.com'], 'booking.com', 'booking.png', 'EXPEDIA', 'BOOKING.COM'),
    ('Etihad', 'Flynas', 'الاتحاد للطيران', 'طيران ناس', ['Etihad.png'], ['etihad.com'], 'flynas.com', 'flynas.png', 'ETIHAD AIRWAYS', 'FLYNAS'),
    ('Amazon', 'Sharaf DG', 'أمازون', 'شرف دي جي', [], ['amazon.ae'], 'sharafdg.com', 'sharafdg.png', 'AMAZON.AE', 'SHARAFDG.COM'),
    ('Namshi', 'H&M', None, None, ['Namshi_RZ1WGQo.png'], ['namshi.com'], 'hm.com', 'hm.png', 'NAMSHI', 'H&M'),
    ('Noon', 'NiceOne', None, None, [], [], 'niceonesa.com', 'niceone.png', None, None),
]

# Text that only makes sense for the old brand. Applied first, longest first.
PHRASES = [
    ("Pay your du mobile or home bill online with your linked ${CARD} card and get cashback.", "Buy Galaxy phones and devices on the Samsung online store with your linked ${CARD} card and get cashback."),
    ("Get 5% cashback when you pay your du bill online.", "Get 5% cashback on Galaxy devices from the Samsung online store."),
    ("Pay your du bill", "Galaxy devices at Samsung"),
    ("Fill up at any Shell station with your linked ${CARD} card and get cashback on fuel.", "Book a WashOn car wash with your linked ${CARD} card and get cashback."),
    ("Get 5% cashback on fuel at Shell stations.", "Get 5% cashback on WashOn car washes."),
    ("Fuel at Shell", "Car wash by WashOn"),
    ("Pay for Spotify Premium", "Pay for a Prime Video subscription"),
    ("cashback on Spotify Premium", "cashback on a Prime Video subscription"),
    ("Spotify Premium", "Prime Video subscription"),
    ("Everyday essentials on Amazon.ae", "Electronics at Sharaf DG"),
    ("on Amazon.ae and get cashback on your orders", "at Sharaf DG online and get cashback on your orders"),
    ("cashback on Amazon.ae orders", "cashback on Sharaf DG online orders"),
    ("Big basket shopping at Lulu", "Gourmet groceries at Jones the Grocer"),
    ("Lulu Hypermarket LLC", "Jones the Grocer LLC"),
    ("Lulu Hypermarket", "Jones the Grocer"),
    ("Hypermarket Saver", "Gourmet Saver"),
    ("Lulu Online", "Jones the Grocer Online"),
    ("Arabica Coffee Trading LLC", "Gloria Jean’s Coffees UAE LLC"),
    ("in restaurant or on McDelivery", "in restaurant or by delivery"),
    ("McDelivery", "Delivery app"),
    ("Expedia Inc. (UAE branch)", "Booking.com B.V. (UAE branch)"),
    ("Subway Gulf Franchise LLC", "Cafe Rider Trading LLC"),
    ("Bill Pay Cashback", "Galaxy Cashback"),
    ("'Fuel Up'", "'Car Care Cashback'"),
    ('"Fuel Up"', '"Car Care Cashback"'),
    (">Fuel Up<", ">Car Care Cashback<"),
    ("Starbucks app", "Coffee Planet app"),
    # categories that change with the brand
    ("['du', 'Household', 'Phone Bill', 4814,", "['du', 'Shopping', 'Online Shopping', 5732,"),
    ("['Shell', 'Transportation', 'Fuel and E-charging', 5541,", "['Shell', 'Transportation', 'Car Wash', 7542,"),
    ("['Spotify', 'Entertainment', 'Music Streaming', 5815,", "['Spotify', 'Entertainment', 'Video Streaming', 5815,"),
    ("domain:'du.ae',pct:5,cap:25,days:24,cat:'9',sub:'9-4'", "domain:'du.ae',pct:5,cap:25,days:24,cat:'11',sub:'11-5'"),
    ("cat:'14',sub:'14-6'", "cat:'14',sub:'14-9'"),
    ("cat:'4',sub:'4-11'", "cat:'4',sub:'4-12'"),
    ("'4-11':'Music Streaming'", "'4-11':'Music Streaming','4-12':'Video Streaming','11-5':'Electronics','14-9':'Car Wash'"),
]

DATA = re.compile(r'data:[a-z/+.-]+;base64,[A-Za-z0-9+/=]+')
MIME = {'png': 'image/png', 'jpg': 'image/jpeg', 'webp': 'image/webp', 'svg': 'image/svg+xml'}


def logo_data(fn):
    p = os.path.join(LOGO_DIR, fn)
    return 'data:%s;base64,%s' % (MIME[fn.rsplit('.', 1)[1]], base64.b64encode(open(p, 'rb').read()).decode())


def new_key(b):
    return 'lx-' + b[7]


def _text(t):
    for a, z in PHRASES:
        t = t.replace(a, z)
    for b in B:
        old, new, ar0, ar1, files, doms, dom, fn, d0, d1 = b
        for f in files:
            t = t.replace("'" + f + "'", "'" + new_key(b) + "'").replace("L:" + f + "'", "L:" + new_key(b) + "'").replace('/' + f, '/' + new_key(b))
        for d in doms:
            t = re.sub(r'(?<![\w-])' + re.escape(d) + r'(?![\w-])', dom, t)
        if ar0:
            t = t.replace("'" + ar0 + "'", "'" + ar1 + "'")
        if d0 and d0 != old:
            t = t.replace("'" + d0 + "'", "'" + d1 + "'")
        # object keys written as bare identifiers: Starbucks: 'x' -> 'Coffee Planet': 'x'
        if re.fullmatch(r'[A-Za-z_]\w*', old):
            t = re.sub(r'(?<![\w.\'"])' + re.escape(old) + r':\s', "'" + new + "': ", t)
        if old == 'du':
            t = t.replace("'du'", "'Samsung'").replace('"du"', '"Samsung"').replace('>du<', '>Samsung<')
        else:
            esc_old = old.replace("'", "\\'")
            if esc_old != old:
                t = t.replace(esc_old, new)
            t = re.sub(r'(?<![\w%])' + re.escape(old) + r'(?![\w])', new, t)
    return t


def _covers(s):
    """The Shell cover shows the Shell sign: WashOn takes the city cover, Samsung the delivery cover."""
    m = re.search(r'window\.__COVERS__=(\{.*?\});', s)
    if not m:
        return s
    c = json.loads(m.group(1))
    if 'nb-shell' in c and 'nb-du' in c and 'nb-amazon' in c:
        c['nb-shell'], c['nb-du'] = c['nb-du'], c['nb-amazon']
    return s[:m.start(1)] + json.dumps(c) + s[m.end(1):]


def apply(s, app):
    parts, last = [], 0
    for m in DATA.finditer(s):
        parts.append(_text(s[last:m.start()]))
        parts.append(m.group(0))
        last = m.end()
    parts.append(_text(s[last:]))
    s = ''.join(parts)
    s = _covers(s)
    logos = {}
    for b in B:
        d = logo_data(b[7])
        logos[LUNE + new_key(b)] = d
        logos[LDV % b[6]] = d
    if 'window.__LOGOS__={' in s:
        # merge into the existing map: renamed old keys still hold the old images, so the new images must win
        i = s.index('window.__LOGOS__=') + len('window.__LOGOS__=')
        m, end = json.JSONDecoder().raw_decode(s, i)
        m.update(logos)
        s = s[:i] + json.dumps(m) + s[end:]
    else:
        # no logo map in this app (merchant portal): put the image itself where the URL was built
        for b in B:
            d = logo_data(b[7])
            k = new_key(b)
            s = re.sub(r"\b(?:LUNE_LOGO|LOGO|LUNE|L)\s*\+\s*'" + re.escape(k) + "'", "'" + d + "'", s)
            s = re.sub(r"\bLDV?\('" + re.escape(b[6]) + r"'\)", "'" + d + "'", s)
            s = s.replace("'" + LDV % b[6] + "'", "'" + d + "'")
    return s
