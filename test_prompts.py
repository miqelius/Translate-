from prompts.historical.v1 import (
    ACCURACY_SYSTEM,
    CRITIC_SYSTEM,
    GUARD_SYSTEM,
    TRANSLATOR_SYSTEM,
    synthesis_prompt,
)


def test_historical_system_prompts_are_preserved():
    assert TRANSLATOR_SYSTEM == (
        "შენ ხარ პროფესიონალი ისტორიული მთარგმნელი. "
        "თარგმნე მოწოდებული ტექსტი მკაცრად ისტორიულ-დიპლომატიურ სტილში, "
        "მაქსიმალურად შეინარჩუნე ორიგინალის ტონი და კონტექსტი."
    )
    assert ACCURACY_SYSTEM == "შენ ხარ სიზუსტის რეცენზენტი (Accuracy Reviewer). შეადარე ორიგინალი და თარგმანი, იპოვე გამოტოვებული, დამატებული ან შეცვლილი დეტალები."
    assert GUARD_SYSTEM == "შენ ხარ ისტორიული ტერმინოლოგიის მცველი (Guard). შეამოწმე ტექსტი ანაქრონიზმებისა და ეპოქასთან შეუსაბამო ტერმინების კუთხით."
    assert CRITIC_SYSTEM == "შენ ხარ სტილისტიკის კრიტიკოსი (Critic). შეაფასე ტექსტის მხატვრული და დიპლომატიური ჟღერადობა."

def test_synthesis_prompt_contains_all_inputs():
    prompt = synthesis_prompt("ORIGINAL", "DRAFT", "ACCURACY", "GUARD", "STYLE")
    for value in ("ORIGINAL", "DRAFT", "ACCURACY", "GUARD", "STYLE"):
        assert value in prompt
