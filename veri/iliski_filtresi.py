# -*- coding: utf-8 -*-
"""İlişki hedef kalite filtresi (ayrı modül — hızlı import)"""

ZAYIF_HEDEF = {
    "üzerin", "üzerinde", "üzerine", "içinde", "içine", "için", "arasında", "arasına",
    "yanında", "yanına", "yakınında", "yakınına", "altında", "altına", "üstünde",
    "doğusun", "doğusunda", "batısın", "batısında", "kuzeyin", "kuzeyinde",
    "güneyin", "güneyinde", "tarafın", "tarafında", "kenarın", "kenarında",
    "bölgesin", "bölgesinde", "topraklar", "toprakların", "sınırların",
    "kelimesin", "kelimesi", "sürecinin", "sürecinde", "sürecin", "kavgaların",
    "birer", "bir", "olan", "olduğun", "olduğu", "bulunan", "yer", "alan",
    "yapının", "yapısın", "kısmın", "kısmı", "parçasın", "parçası",
    "tasarım", "tasarımın", "düzenin", "yönetimin", "yönetim",
    "var", "yok", "vardır", "yoktur",
}
FIIL_SON = ("dır", "dir", "dur", "dür", "tır", "tir", "mış", "miş", "muş", "müş",
            "yor", "mak", "mek", "ken", "arak", "erek", "makta", "mekte")
IYELIK_SON = (
    "sında", "sinde", "sunda", "sünde",
    "ların", "lerin", "ların", "lerin",
    "sının", "sinin", "sunun", "sünün",
    "asın", "esin", "usun", "üsün",
    "sın", "sin", "sun", "sün",
    "ığ", "iğ", "uğ", "üğ",
    "ığı", "iği", "uğu", "üğü",
    "sı", "si", "su", "sü",
    "li", "lı", "lu", "lü",
    "nın", "nin", "nun", "nün",
    "ın", "in", "un", "ün",
)

def hedef_kaliteli(subj, rel, hedef):
    h = hedef.strip()
    n = h.lower()
    if len(h) < 3 or len(h) > 50:
        return False
    if subj.strip().isdigit():
        return False
    son_kelime = n.split()[-1].strip("'")
    if son_kelime in ZAYIF_HEDEF:
        return False
    for e in IYELIK_SON:
        if e in ("ın", "in", "un", "ün") and len(son_kelime) < 5:
            continue
        # "li/lı/lu/lü" yalnızca 5+ karakter hedeflerde (4 harfli "dili" = gerçek kelime)
        if e in ("li", "lı", "lu", "lü") and len(son_kelime) < 5:
            continue
        if son_kelime.endswith(e):
            return False
    for e in FIIL_SON:
        if n.endswith(e):
            return False
    if n == subj.lower():
        return False
    return True
