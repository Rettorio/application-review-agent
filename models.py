from typing import Optional
from pydantic import BaseModel
from enum import Enum
from pydantic.fields import Field

class ReviewClassification(str, Enum):
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    UI_UX = "ui_ux"
    PRAISE = "praise"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    SPAM = "spam"

class AppReview(BaseModel):
    app_id: str
    app_version: str
    at: str
    content: str
    replied_at: Optional[str] = None
    reply_content: Optional[str] = None
    review_created_version: str
    review_id: str
    score: int
    sort_order: str
    thumbs_up_count: int
    user_image: Optional[str] = None
    user_name: str

class AgentResponse(BaseModel):
    app_id: str = Field(description="The ID of the app being reviewed")
    app_version: str = Field(description="The version of the app being reviewed")
    review_id: str = Field(description="The ID of the review being classified")
    classification: ReviewClassification = Field(description="The classification result of the review")
    confidence: float = Field(description="The confidence score of the classification")

class AgentInput(BaseModel):
    app_id: str = Field(description="The ID of the app being reviewed")
    review_text: str = Field(description="The text of the review to classify")
    score: float = Field(description="The score of the review")
    thumbs_up_count: int = Field(description="The number of thumbs up for the review")

class Response(BaseModel):
    message: str = Field(description="The response message about the classification result")
    error: Optional[str] = Field(description="The error message, if any")
    result: Optional[AgentResponse] = Field(description="The classification result, if any")
