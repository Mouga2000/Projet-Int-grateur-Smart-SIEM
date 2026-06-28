# app/schemas/search_schemas.py
# -------------------------------
# Schémas Pydantic pour la recherche Elasticsearch
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, Field
#   from datetime import datetime
#   from typing import Optional, Any
#
#   class FilterCriteria(BaseModel):
#       field: str
#       operator: str = "eq"  # eq, neq, gt, gte, lt, lte, in, contains, exists, regex
#       value: Any
#
#   class DateRange(BaseModel):
#       from_date: Optional[datetime] = None
#       to_date: Optional[datetime] = None
#       field: str = "@timestamp"
#
#   class SearchRequest(BaseModel):
#       query: str = "*"
#       filters: list[FilterCriteria] = []
#       date_range: Optional[DateRange] = None
#       sources: list[str] = []
#       severities: list[str] = []
#       tags: list[str] = []
#       page: int = Field(1, ge=1)
#       size: int = Field(50, ge=1, le=1000)
#       sort_field: str = "@timestamp"
#       sort_order: str = "desc"  # asc | desc
#       aggs: Optional[dict] = None  # Agrégations ES (facettes, stats)
#
#   class SearchHit(BaseModel):
#       id: str
#       score: float
#       source: dict  # Le document Elasticsearch
#       highlight: Optional[dict] = None
#
#   class SearchResponse(BaseModel):
#       hits: list[SearchHit]
#       total: int
#       page: int
#       size: int
#       aggregations: Optional[dict] = None
#       took_ms: int
