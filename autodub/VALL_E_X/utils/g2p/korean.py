import re
from g2pk import G2p
from jamo import h2j

_korean_g2p = G2p()


_choseong_to_ipa = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ᄀ', 'g'),
    ('ᄁ', 'g*'),
    ('ᄂ', 'n'),
    ('ᄃ', 't'),
    ('ᄄ', 't*'),
    ('ᄅ', 'ɾ'),
    ('ᄆ', 'm'),
    ('ᄇ', 'p'),
    ('ᄈ', 'p*'),
    ('ᄉ', 's'),
    ('ᄊ', 's*'),
    ('ᄋ', ''),
    ('ᄌ', 'dʑ'),
    ('ᄍ', 'dz*'),
    ('ᄎ', 'tsʰ'),
    ('ᄏ', 'k'),
    ('ᄐ', 'tʰ'),
    ('ᄑ', 'pʰ'),
    ('ᄒ', 'h'),
]]

_jungseong_to_ipa = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ᅡ','a'),
    ('ᅣ','ja'),
    ('ᅥ','ə'),
    ('ᅧ','jə'),
    ('ᅩ','o'),
    ('ᅭ','jo'),
    ('ᅮ','u'),
    ('ᅲ','ju'),
    ('ᅳ','ɯ'),
    ('ᅵ','i'),
    ('ᅢ','ɛ'),
    ('ᅦ','e'),
    ('ᅤ','jɛ'),
    ('ᅨ','je'),
    ('ᅪ','wa'),
    ('ᅫ','we'),
    ('ᅬ','wɛ'),
    ('ᅯ','wɔ'),
    ('ᅰ','wæ'),
    ('ᅱ','wi'),
    ('ᅴ','ɯi'),
]]

_jongseong_to_ipa = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ᆨ','k'),
    ('ᆫ','n'),
    ('ᆮ',''),
    ('ᆯ','t'),
    ('ᆷ','m'),
    ('ᆸ','p'),
    ('ᆼ','ŋ'),
]]

def korean_to_ipa2(text):
    text = _korean_g2p(text)
    text = h2j(text)
    
    for regex, replacement in _choseong_to_ipa:
        text = re.sub(regex, replacement, text)
        
    for regex, replacement in _jungseong_to_ipa:
        text = re.sub(regex, replacement, text)
        
    for regex, replacement in _jongseong_to_ipa:
        text = re.sub(regex, replacement, text)
        
    return text