import google.generativeai as genai
from datetime import date
from .models import GeminiSuggestion, ChildMilestone, ActivityReport


def calculate_age_in_months(dob):
    today = date.today()
    return (today.year - dob.year) * 12 + today.month - dob.month


def generate_ai_suggestion(child):
    genai.configure(api_key="AIzaSyDu6pYMC1YUzAXfDni6nt8opsmX_fiCe0g")

    milestones = ChildMilestone.objects.filter(child=child).exclude(status='pending')
    activities = ActivityReport.objects.filter(child=child).order_by('-date')[:5]
    age_months = calculate_age_in_months(child.date_of_birth)

    milestone_summary = "\n".join([
        f"- {m.milestone.category}: {m.milestone.description} → {m.status.capitalize()}"
        for m in milestones
    ]) or "No milestone progress yet."

    activity_summary = "\n".join([
        f"{a.date}: {a.activities_done} | Notes: {a.notes}"
        for a in activities
    ]) or "No recent activities recorded."

    prompt = f"""
    You are an AI child development expert.

    Provide personalized suggestions for the parent.

    IMPORTANT:
    Return plain text only.
    Do NOT use stars, bullet points, markdown, or special characters.

    Child: {child.child_name}
    Age: {age_months} months

    Milestones:
    {milestone_summary}

    Recent Activities:
    {activity_summary}
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    suggestion_text = response.text if hasattr(response, "text") else str(response)

    # Remove stars if model still adds them
    suggestion_text = suggestion_text.replace("*", "")

    GeminiSuggestion.objects.create(child=child, suggestion_text=suggestion_text)
    return suggestion_text
