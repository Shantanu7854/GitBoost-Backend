from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import google.generativeai as genai
import os

# Configure Gemini API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@api_view(["POST"])
def analyze_github(request):
    username = request.data.get("username")
    if not username:
        return Response({"error": "Username required"}, status=400)

    # Prepare GitHub request headers
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    profile_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos"

    try:
        profile_res = requests.get(profile_url, headers=headers, timeout=10)
        repos_res = requests.get(repos_url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        return Response({"error": "GitHub API request failed", "details": str(e)}, status=500)

    if profile_res.status_code == 404:
        return Response({"error": "GitHub user not found"}, status=404)
    elif profile_res.status_code != 200:
        return Response({"error": "GitHub API error", "status": profile_res.status_code}, status=500)

    profile = profile_res.json()
    repos = repos_res.json()

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

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return Response({"recommendations": response.text})
    except Exception as e:
        return Response({"error": "Gemini API error", "details": str(e)}, status=500)
