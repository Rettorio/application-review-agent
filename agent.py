import os
import google.cloud.logging
from dotenv import load_dotenv
from google.adk.agents import Agent
from app_reviews_classification.models import AppReview,ReviewClassification,AgentResponse,Response


_ = load_dotenv()
model_name = os.getenv("MODEL")
if model_name is None:
    raise ValueError("MODEL environment variable is not set")
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()  # pyright: ignore[reportUnknownMemberType]

def create_agent_response(review: AppReview, classification: str, confidence: float) -> AgentResponse:
    """
    Classifies the review with the given classification and confidence.
    Args:
        review (AppReview): The review to classify.
        classification (str): The classification to apply.
        confidence (float): The confidence level of the classification.
    Returns:
        AgentResponse: The classification result.
    Raises:
        ValueError: If the classification is invalid.
    """
    normalized = classification.strip().lower()
    try:
        classification = ReviewClassification(normalized)
    except ValueError:
        valid_values = [e.value for e in ReviewClassification]
        raise ValueError(str.format("Invalid classification {0}. Must be one of: {1}", classification, valid_values))
    return AgentResponse(
        app_id=review.app_id,
        app_version=review.app_version,
        review_id=review.review_id,
        classification=classification,
        confidence=confidence,
    )


root_agent = Agent(
    name="app_review_classifier",
    model=model_name,
    instruction="""
    You are an app reviews classifier that categorizes app reviews.
    Analyze the review object and classify it as :
        1. bug_report, mention crashes,errors or things not working.
        2. feature_request, mention new features, improvements or suggest new ideas (like: 'I wish the app did x').
        3. ui_ux, mention UI/UX issues or suggestions.
        4. praise, general positive feedback.
        5. neutral, general feedback or no clear classification.
        6. negative, general negative feedback not a bug_report, feature_request or ui_ux.
        7. spam, if the review is spam or irrelevant.

    Brief about the apps:
    Here are the apps you need to classify reviews for
        1.{app_id: 'app.bpjs.mobile', name: 'Mobile JKN', about: 'Cara Mudah AKSes information Jaminan Kesehatan Nasional, BPJS Kesehatan'}
        2. {app_id: 'superapps.polri.presisi.presisi', name: 'Super App Polri', about: ' **SuperApp POLRI** adalah pintu gerbang digital Anda untuk semua layanan kepolisian.'}
        3. {app_id: 'id.go.kominfo.digitalent', name: 'Digitalent Mobile', about: 'Digital Talent Scholarship adalah program pelatihan pengembangan kompetens'}

    you will be given input such as app_id,review_text,score,thumbs_up_count
    and you need to classify the review based on those information use app_id to link to the app's brief.

    Guidelines:
    1. First you need to determine if the review is valid and can be parsed.
       If the review is invalid, return {message: 'Invalid review object, Classification failed', error: 'error_validation_from_parse_review', result: None}.
       Otherwise, proceed to the next step.
    2. After successfully parsing, classify the review based on :
        - app_id, to recognize the app is about.
        - content, to understand the review's sentiment and context.
        - score, to understand the review's rating.
        - thumbs_up_count, to understand the review's popularity or how many people found it helpful or agree with it.
    3. After classifying, use the create_agent_response tool to create a response object.
    4. Wrap the AgentResponse object in a Response object with appropriate message, error, and result fields, and return it.

    Constraints:
    - If the user input is others than Classification like not invalid or valid reviews
      Reply with message: 'Review Classification failed' and error: 'Input is not a valid review' and result: None.
    """,
    output_schema=Response,
    tools=[create_agent_response]
)
