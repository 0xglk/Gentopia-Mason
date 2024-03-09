from typing import AnyStr, List, Optional, Type
import requests
from pydantic import BaseModel, Field
from gentopia.tools.basetool import BaseTool

class GitHubSearcherArgs(BaseModel):
    username: str = Field(..., description="GitHub username")
    count_prints: int = Field(default=5, description="Number of repositories to display. Defaults to 5.")
    language: Optional[str] = Field(default=None, description="Programming language to filter repositories by.")

class GitHubSearcher(BaseTool):
    name = "github_repo_searcher"
    description = ("Fetches a list of public repositories for a given GitHub username, optionally filtered by programming language."
                   "Input should be a GitHub username and, optionally, a programming language.")
    args_schema: Optional[Type[BaseModel]] = GitHubSearcherArgs
    username: str = ""
    results: List = []

    def _run(self, username: AnyStr, count_prints: int = 5, language: Optional[str] = None) -> str:
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch repositories"
        
        self.username = username
        all_repos = response.json()
        
        if language:
            filtered_repos = [repo for repo in all_repos if repo['language'] and repo['language'].lower() == language.lower()]
        else:
            filtered_repos = all_repos

        top_repos = filtered_repos[:count_prints]

        ans = []
        for repo in top_repos:
            ans.append(str({
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description', 'No description provided.'),
                'language': repo['language'],
                'url': repo['html_url'],
            }))
        if not ans:
            return "No repositories available or matching the specified language"
        
        return '\n\n'.join(ans)

    async def _arun(self, *args: any, **kwargs: any) -> any:
        raise NotImplementedError

if __name__ == "__main__":
    fetcher = FetchUserRepos()
    result = fetcher._run("octocat", count_prints=5, language="Python")
    print(result)
