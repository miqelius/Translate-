"""Validated result schema."""
from pydantic import BaseModel, Field


class TranslationResult(BaseModel):
    final_translation: str = Field(description="საბოლოო დამუშავებული და სრულყოფილი თარგმანი.")
    confidence_score: int = Field(ge=0, le=100, description="სანდოობის ქულა 0-დან 100-მდე.")
    issues_fixed: list[str] = Field(default_factory=list, description="აღმოფხვრილი პრობლემებისა და შესწორებების სია.")
    summary: str = Field(description="მოკლე რეპორტი რა შეიცვალა სინთეზისას.")
