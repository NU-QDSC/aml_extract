from pydantic import BaseModel
from typing import List
from genetic_abnormality import GeneticAbnormality


class GeneticAbnormalities(BaseModel):
    genetic_abnormalities: List[GeneticAbnormality]
