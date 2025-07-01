from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@api_view(["POST"])
def analyze_github(request):
    username = request.data.get("username")
    if not username:
        return Response({"error": "Username required"}, status=400)

    # Fetch GitHub profile & repos
    profile_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos"

    profile_res = requests.get(profile_url)
    repos_res = requests.get(repos_url)

    if profile_res.status_code != 200:
        return Response({"error": "GitHub user not found"}, status=404)

    profile = profile_res.json()
    repos = repos_res.json()

    summary = {
        "name": profile.get("name"),
        "bio": profile.get("bio"),
        "public_repos": profile.get("public_repos"),
        "followers": profile.get("followers"),
        "repos": [
            {"name": r["name"], "stars": r["stargazers_count"], "description": r["description"]}
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
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content(prompt)

    return Response({"recommendations": response.text})
