from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@api_view(["POST"])
def analyze_github(request):
    username = request.data.get("username")
    if not username:
        return Response({"error": "Username required"}, status=400)

    # Load GitHub token from environment variable
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    # If token is set, use it
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    # GitHub API URLs
    profile_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos"

    # Make authenticated GitHub API calls
    profile_res = requests.get(profile_url, headers=headers)
    repos_res = requests.get(repos_url, headers=headers)

    if profile_res.status_code == 404:
        return Response({"error": "GitHub user not found"}, status=404)
    elif profile_res.status_code != 200:
        return Response({"error": "GitHub API error"}, status=500)

    profile = profile_res.json()
    repos = repos_res.json()

    # Prepare summary for Gemini
    summary = {
        "name": profile.get("name"),
        "bio": profile.get("bio"),
        "public_repos": profile.get("public_repos"),
        "followers": profile.get("followers"),
        "repos": [
            {
                "name": r["name"],
                "stars": r["stargazers_count"],
                "description": r["description"]
            }
            for r in repos
        ],
    }

    prompt = f"""This is a GitHub profile:
{summary}

Give me suggestions on how to improve this profile:
- Projects
- Bio
- Visibility
- Profile README
- Follower engagement
"""

    # Generate recommendations with Gemini
    model = genai.GenerativeModel("gemini-2.5-pro")
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        return Response({"error": "Gemini API error", "details": str(e)}, status=500)

    return Response({"recommendations": response.text})
