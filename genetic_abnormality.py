from pydantic import BaseModel, Field


class GeneticAbnormality(BaseModel):
    name: str = Field(description="the name of the genetic abnormality detected on the pathology report")
    status: str | None = Field(description="the presence of the specific genetic abnormality. Should be POSITIVE if it is found or NEGATIVE if it is not detected.")
    percentage: float | None = Field(description="the percentage of abnormal cells for the specific genetic abnormality, but only if positive and if the information is available")
