from sqlmodel import SQLModel, Field


class Team(SQLModel, table=True):
    id: int = Field(primary_key=True, description="FRC Team Number")
    name: str = Field(default="")
    nickname: str = Field(default="")
    city: str = Field(default="")
    state_prov: str = Field(default="")
    country: str = Field(default="")
    school_name: str = Field(default="")
    rookie_year: int = Field(default=0)
    robot_name: str = Field(default="")
    accomplishments: str = Field(default="")
    wpakey: str = Field(default="")
    yellow_card: bool = Field(default=False)
    has_connected: bool = Field(default=False)
    fta_notes: str = Field(default="")
