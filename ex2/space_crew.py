from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, model_validator, ValidationError


class Rank(str, Enum):
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: List[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission_rules(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        has_commander = any(
            m.rank in (Rank.commander, Rank.captain) for m in self.crew
        )
        if not has_commander:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            experienced = sum(
                1 for m in self.crew if m.years_experience >= 5
            )
            if experienced < len(self.crew) / 2:
                raise ValueError(
                    "Long missions (> 365 days) need 50% experienced crew "
                    "(5+ years)"
                )

        inactive = [m.name for m in self.crew if not m.is_active]
        if inactive:
            raise ValueError(
                f"All crew members must be active. Inactive: {inactive}"
            )

        return self


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 41)

    valid_mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2024, 6, 1),
        duration_days=900,
        crew=[
            CrewMember(
                member_id="CMD001",
                name="Sarah Connor",
                rank=Rank.commander,
                age=45,
                specialization="Mission Command",
                years_experience=20,
            ),
            CrewMember(
                member_id="NAV001",
                name="John Smith",
                rank=Rank.lieutenant,
                age=35,
                specialization="Navigation",
                years_experience=10,
            ),
            CrewMember(
                member_id="ENG001",
                name="Alice Johnson",
                rank=Rank.officer,
                age=30,
                specialization="Engineering",
                years_experience=8,
            ),
        ],
        budget_millions=2500.0,
    )
    print("Valid mission created:")
    print(f"Mission: {valid_mission.mission_name}")
    print(f"ID: {valid_mission.mission_id}")
    print(f"Destination: {valid_mission.destination}")
    print(f"Duration: {valid_mission.duration_days} days")
    print(f"Budget: ${valid_mission.budget_millions}M")
    print(f"Crew size: {len(valid_mission.crew)}")
    print("Crew members:")
    for member in valid_mission.crew:
        print(
            f"- {member.name} ({member.rank.value})"
            f" - {member.specialization}"
        )

    print()
    print("=" * 41)
    print("Expected validation error (no Commander/Captain):")
    try:
        SpaceMission(
            mission_id="M_FAIL",
            mission_name="Doomed Mission",
            destination="Pluto",
            launch_date=datetime(2024, 6, 1),
            duration_days=100,
            crew=[
                CrewMember(
                    member_id="CAD001",
                    name="Rookie",
                    rank=Rank.cadet,
                    age=20,
                    specialization="Training",
                    years_experience=0,
                ),
            ],
            budget_millions=100.0,
        )
    except ValidationError as e:
        msg = e.errors()[0]["msg"]
        print(msg.replace("Value error, ", ""))

    print()
    print("=" * 41)
    print("Expected validation error (inactive crew member):")
    try:
        SpaceMission(
            mission_id="M2024_BAD",
            mission_name="Ghost Ship",
            destination="Europa",
            launch_date=datetime(2024, 6, 1),
            duration_days=100,
            crew=[
                CrewMember(
                    member_id="CMD002",
                    name="Active Commander",
                    rank=Rank.commander,
                    age=40,
                    specialization="Command",
                    years_experience=15,
                    is_active=True,
                ),
                CrewMember(
                    member_id="CPT002",
                    name="Retired Captain",
                    rank=Rank.captain,
                    age=60,
                    specialization="Navigation",
                    years_experience=30,
                    is_active=False,
                ),
            ],
            budget_millions=500.0,
        )
    except ValidationError as e:
        msg = e.errors()[0]["msg"]
        print(msg.replace("Value error, ", ""))

    print()
    print("=" * 41)
    print("Expected validation error (budget over limit):")
    try:
        SpaceMission(
            mission_id="M2024_EXP",
            mission_name="Expensive Mission",
            destination="Titan",
            launch_date=datetime(2024, 6, 1),
            duration_days=100,
            crew=[
                CrewMember(
                    member_id="CMD003",
                    name="Big Spender",
                    rank=Rank.commander,
                    age=45,
                    specialization="Finance",
                    years_experience=20,
                ),
            ],
            budget_millions=15000.0,
        )
    except ValidationError as e:
        msg = e.errors()[0]["msg"]
        print(msg.replace("Value error, ", ""))


if __name__ == "__main__":
    main()
