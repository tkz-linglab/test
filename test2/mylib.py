
EXCLUDE_OBJ_WORD = {"my", "your", "her", "its", "our", "their", "a", "an", "the"}
SUBJECT_DEPS = {"nsubj", "nsubjpass", "expl"}
EXCLUDE_ADVERBS = {
    "however", "therefore", "thus", "furthermore", "moreover", "nevertheless",
    "nonetheless", "instead", "consequently", "accordingly", "meanwhile",
    "besides", "otherwise", "hence", "so", "how", "why", "when"
}

def has_subject_between(left_tok, verb_tok, sent):
    i1, i2 = left_tok.i, verb_tok.i
    for t in sent:
        if i1 < t.i < i2 and t.dep_ in SUBJECT_DEPS and t.head == verb_tok:
            return True
    return False

def is_followed_by_comma(tok):
    if tok.i + 1 >= len(tok.doc):
        return False
    next_token = tok.doc[tok.i + 1]
    return next_token.is_punct and next_token.text == ","

def is_how_plus_adv(tok):
    if tok.pos_ != "ADV":
        return False
    if tok.i - 1 >= 0:
        prev_token = tok.doc[tok.i - 1]
        return prev_token.text.lower() == "how"
    return False

def is_hyphenated_token(tok):
    """
    トークン tok がハイフン結合語なら True を返す。
    - "part" "-" "time" → "part" と "time" が True
    """
    HYPHENS = {"-", "‐", "‒", "–", "−"}  # hyphen, en dash, minus など
    text = tok.text
    # トークン自身がハイフン記号なら True
    if text in HYPHENS:
        return True
    # 直前または直後がハイフン記号トークンの場合
    doc = tok.doc
    i = tok.i
    if i - 1 >= 0 and doc[i - 1].text in HYPHENS:
        return True
    if i + 1 < len(doc) and doc[i + 1].text in HYPHENS:
        return True
    return False

def is_excluded_ing(token) -> bool:
    """
    token が -ing 語で、例外リストに含まれず、
    直前のトークンが VERB の場合に True。
    """
    EXCEPT_ING = {"thing", "something", "anything", "nothing"}
    word = token.lower_

    if word.endswith("ing") and word not in EXCEPT_ING:
        doc = token.doc
        if token.i > 0 and doc[token.i - 1].pos_ == "VERB":
            return True
    return False

# 判定ヘルパー
def is_adj_noun(token):
    return (
        token.dep_ in ("amod", "compound")
        and token.head.pos_ == "NOUN"
        and token.i < token.head.i
        and not is_hyphenated_token(token)
        and not is_hyphenated_token(token.head)
    )

def is_verb_obj(token):
    return (
        token.dep_ in {"dobj"}
        and token.text.lower() not in EXCLUDE_OBJ_WORD
        and not is_excluded_ing(token)
        and token.head.pos_ == "VERB"
        and token.head.lemma_ != "be"
        and token.head.i < token.i
        and not is_hyphenated_token(token)
        and not is_hyphenated_token(token.head)
    )

def is_verb_adv(token):
    return (
        token.dep_ in ("advmod", "npadvmod", "prt")
        and token.head.pos_ == "VERB"
        and token.head.lemma_ != "be"
        and token.head.i < token.i
        and not is_hyphenated_token(token)
        and not is_hyphenated_token(token.head)
    )

def is_adv_verb(token, sent):
    return (
        token.dep_ in ("advmod", "npadvmod")
        and token.head.pos_ == "VERB"
        and token.head.lemma_ != "be"
        and token.i < token.head.i
        and token.text.lower() not in EXCLUDE_ADVERBS
        and not is_followed_by_comma(token)
        and not has_subject_between(token, token.head, sent)
        and not is_how_plus_adv(token)
        and not is_hyphenated_token(token)
        and not is_hyphenated_token(token.head)
    )

def is_adv_adj(token):
    return (
        token.dep_ in ("advmod", "npadvmod")
        and token.head.pos_ == "ADJ"
        and token.i < token.head.i
        and not is_hyphenated_token(token)
        and not is_hyphenated_token(token.head)
    )
