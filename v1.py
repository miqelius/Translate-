"""Historical prompts copied verbatim from the original bot.py."""
TRANSLATOR_SYSTEM = (
    "შენ ხარ პროფესიონალი ისტორიული მთარგმნელი. "
    "თარგმნე მოწოდებული ტექსტი მკაცრად ისტორიულ-დიპლომატიურ სტილში, "
    "მაქსიმალურად შეინარჩუნე ორიგინალის ტონი და კონტექსტი."
)
ACCURACY_SYSTEM = "შენ ხარ სიზუსტის რეცენზენტი (Accuracy Reviewer). შეადარე ორიგინალი და თარგმანი, იპოვე გამოტოვებული, დამატებული ან შეცვლილი დეტალები."
GUARD_SYSTEM = "შენ ხარ ისტორიული ტერმინოლოგიის მცველი (Guard). შეამოწმე ტექსტი ანაქრონიზმებისა და ეპოქასთან შეუსაბამო ტერმინების კუთხით."
CRITIC_SYSTEM = "შენ ხარ სტილისტიკის კრიტიკოსი (Critic). შეაფასე ტექსტის მხატვრული და დიპლომატიური ჟღერადობა."

def synthesis_prompt(original: str, draft: str, accuracy_notes: str,
                     guard_notes: str, critic_notes: str) -> str:
    # Preserve the original f-string content and whitespace.
    return f"""
    [ორიგინალი ტექსტი]:
    {original}

    [საწყისი თარგმანი]:
    {draft}

    [Accuracy Reviewer-ის შენიშვნები]:
    {accuracy_notes}

    [Guard-ის შენიშვნები]:
    {guard_notes}

    [Critic-ის შენიშვნები]:
    {critic_notes}

    გაითვალისწინე ყველა შენიშვნა, გამოასწორე ხარვეზები და ააგე საბოლოო, სრულყოფილი თარგმანი.
    დააბრუნე პასუხი მკაცრად JSON ფორმატში, რომელიც აკმაყოფილებს შემდეგ სტრუქტურას:
    {{
        "final_translation": "...",
        "confidence_score": 95,
        "issues_fixed": ["...", "..."],
        "summary": "..."
    }}
    """
