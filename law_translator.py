# law_translator.py

from law_compiler import compile_law
from law_enforcer import add_law

def translate_ui_to_law(plain_text: str):
    """
    Convert simple human feedback into a LawScript rule.
    VERY MVP version for demo.
    """

    text = plain_text.lower()

    # -------- PATTERN 1: inventory + refund --------
    if "refund" in text and "inventory" in text:
        if ">" in text or "more than" in text or "greater than" in text:
            law_text = '''
            LAW {
              when inventory > 0
              block refund_order
              because "Check inventory first"
            }
            '''
        elif "<" in text or "less than" in text:
            law_text = '''
            LAW {
              when inventory < 0
              block refund_order
              because "Inventory cannot be negative"
            }
            '''
        else:
            law_text = '''
            LAW {
              when inventory == 0
              block refund_order
              because "No inventory available"
            }
            '''

        law = compile_law(law_text)
        add_law(law)
        return law

    # -------- DEFAULT FALLBACK --------
    raise ValueError(f"Cannot translate this feedback yet: {plain_text}")
