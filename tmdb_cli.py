#!/usr/bin/env python3
"""
TMDB API CLI - A terminal UI for querying The Movie Database API
"""

import os
import sys
from typing import List, Tuple, Callable, Any, Optional
from match import match

try:
    import requests
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich import print as rprint
    from dotenv import load_dotenv
except ImportError:
    print("Required packages not found. Please install dependencies:")
    print("uv pip install requests rich python-dotenv")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Initialize Rich console
console = Console()

# TMDB API Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

if not TMDB_API_KEY:
    console.print("[bold red]Warning:[/bold red] TMDB_API_KEY environment variable not set!")
    console.print("Get your API key from: https://www.themoviedb.org/settings/api")
    console.print("Set it with: export TMDB_API_KEY='your_key_here'")


# API Helper Functions
def search_movies_by_title(title: str) -> List[dict]:
    """Search for movies by title using TMDB API"""
    if not TMDB_API_KEY:
        return []

    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        console.print(f"[red]Error searching movies: {e}[/red]")
        return []


def get_movie_details(movie_id: int) -> Optional[dict]:
    """Get detailed information about a movie"""
    if not TMDB_API_KEY:
        return None

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "credits"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        console.print(f"[red]Error getting movie details: {e}[/red]")
        return None


def search_movies_by_year(year: str) -> List[dict]:
    """Search for movies by year"""
    if not TMDB_API_KEY:
        return []

    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "primary_release_year": year
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        console.print(f"[red]Error searching by year: {e}[/red]")
        return []


def search_movies_by_year_range(start_year: str, end_year: str) -> List[dict]:
    """Search for movies within a year range"""
    if not TMDB_API_KEY:
        return []

    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "primary_release_date.gte": f"{start_year}-01-01",
        "primary_release_date.lte": f"{end_year}-12-31"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        console.print(f"[red]Error searching by year range: {e}[/red]")
        return []


def search_person(name: str) -> List[dict]:
    """Search for a person (actor/director)"""
    if not TMDB_API_KEY:
        return []

    url = f"{TMDB_BASE_URL}/search/person"
    params = {
        "api_key": TMDB_API_KEY,
        "query": name
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        console.print(f"[red]Error searching person: {e}[/red]")
        return []


def get_movies_by_person(person_id: int, role: str = "cast") -> List[dict]:
    """Get movies for a person (actor or crew member)"""
    if not TMDB_API_KEY:
        return []

    url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits"
    params = {
        "api_key": TMDB_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get(role, [])
    except Exception as e:
        console.print(f"[red]Error getting person's movies: {e}[/red]")
        return []


# Action Functions (similar to a3.py structure)
def title_by_year(matches: List[str]) -> List[str]:
    """Find movies made in a specific year"""
    year = matches[0]
    movies = search_movies_by_year(year)
    if not movies:
        return ["No answers"]
    return [movie["title"] for movie in movies[:10]]  # Limit to 10 results


def title_by_year_range(matches: List[str]) -> List[str]:
    """Find movies made between two years"""
    start_year, end_year = matches[0], matches[1]
    movies = search_movies_by_year_range(start_year, end_year)
    if not movies:
        return ["No answers"]
    return [movie["title"] for movie in movies[:10]]


def title_before_year(matches: List[str]) -> List[str]:
    """Find movies made before a year"""
    year = int(matches[0])
    movies = search_movies_by_year_range("1900", str(year - 1))
    if not movies:
        return ["No answers"]
    return [movie["title"] for movie in movies[:10]]


def title_after_year(matches: List[str]) -> List[str]:
    """Find movies made after a year"""
    year = int(matches[0])
    current_year = 2025
    movies = search_movies_by_year_range(str(year + 1), str(current_year))
    if not movies:
        return ["No answers"]
    return [movie["title"] for movie in movies[:10]]


def director_by_title(matches: List[str]) -> List[str]:
    """Find director of a movie"""
    title = matches[0]
    movies = search_movies_by_title(title)
    if not movies:
        return ["No answers"]

    # Get detailed info for first match
    details = get_movie_details(movies[0]["id"])
    if not details or "credits" not in details:
        return ["No answers"]

    directors = [crew["name"] for crew in details["credits"].get("crew", [])
                 if crew["job"] == "Director"]
    return directors if directors else ["No answers"]


def title_by_director(matches: List[str]) -> List[str]:
    """Find movies by a director"""
    director_name = matches[0]
    persons = search_person(director_name)
    if not persons:
        return ["No answers"]

    # Get movies where this person was a director
    movies = get_movies_by_person(persons[0]["id"], role="crew")
    director_movies = [movie["title"] for movie in movies
                       if movie.get("job") == "Director"]

    return director_movies[:10] if director_movies else ["No answers"]


def actors_by_title(matches: List[str]) -> List[str]:
    """Find actors in a movie"""
    title = matches[0]
    movies = search_movies_by_title(title)
    if not movies:
        return ["No answers"]

    details = get_movie_details(movies[0]["id"])
    if not details or "credits" not in details:
        return ["No answers"]

    actors = [cast["name"] for cast in details["credits"].get("cast", [])[:10]]
    return actors if actors else ["No answers"]


def year_by_title(matches: List[str]) -> List[str]:
    """Find the year a movie was made"""
    title = matches[0]
    movies = search_movies_by_title(title)
    if not movies:
        return ["No answers"]

    release_date = movies[0].get("release_date", "")
    if release_date:
        year = release_date.split("-")[0]
        return [year]
    return ["No answers"]


def title_by_actor(matches: List[str]) -> List[str]:
    """Find movies an actor appeared in"""
    actor_name = matches[0]
    persons = search_person(actor_name)
    if not persons:
        return ["No answers"]

    movies = get_movies_by_person(persons[0]["id"], role="cast")
    titles = [movie["title"] for movie in movies[:10]]
    return titles if titles else ["No answers"]


def bye_action(dummy: List[str]) -> None:
    """Exit the program"""
    raise KeyboardInterrupt


# Pattern-Action List
pa_list: List[Tuple[List[str], Callable[[List[str]], List[str]]]] = [
    (str.split("what movies were made in _"), title_by_year),
    (str.split("what movies were made between _ and _"), title_by_year_range),
    (str.split("what movies were made before _"), title_before_year),
    (str.split("what movies were made after _"), title_after_year),
    (str.split("who directed %"), director_by_title),
    (str.split("who was the director of %"), director_by_title),
    (str.split("what movies were directed by %"), title_by_director),
    (str.split("who acted in %"), actors_by_title),
    (str.split("when was % made"), year_by_title),
    (str.split("in what movies did % appear"), title_by_actor),
    (["bye"], bye_action),
]


def search_pa_list(src: List[str]) -> List[str]:
    """Match query against patterns and execute corresponding action"""
    for pattern, action in pa_list:
        result = match(pattern, src)
        if result is not None:
            answers = action(result)
            return answers if answers else ["No answers"]
    return ["I don't understand"]


def display_welcome():
    """Display welcome banner"""
    welcome_text = """
[bold cyan]🎬 TMDB Movie Database CLI[/bold cyan]

Welcome to the TMDB movie query system!

[yellow]Example queries:[/yellow]
  • what movies were made in 2020
  • what movies were made between 2010 and 2015
  • who directed inception
  • what movies were directed by christopher nolan
  • who acted in the dark knight
  • when was interstellar made
  • in what movies did leonardo dicaprio appear
  • limit 5 (set result limit)
  • bye (to exit)
    """
    console.print(Panel(welcome_text, border_style="cyan"))


def query_loop():
    """Main query loop with Rich UI"""
    display_welcome()

    # Default limit for results
    result_limit = 10

    while True:
        try:
            console.print()
            query = Prompt.ask("[bold green]Your query[/bold green]").replace("?", "").lower()

            # Check for limit command
            if query.startswith("limit "):
                try:
                    new_limit = int(query.split()[1])
                    if new_limit > 0:
                        result_limit = new_limit
                        console.print(f"[green]✓ Result limit set to {result_limit}[/green]")
                    else:
                        console.print("[red]Limit must be a positive number[/red]")
                except (ValueError, IndexError):
                    console.print("[red]Usage: limit <number>[/red]")
                continue

            query_words = query.split()
            if not query_words:
                continue

            with console.status("[bold yellow]Searching TMDB...", spinner="dots"):
                answers = search_pa_list(query_words)

            # Limit results to the specified limit
            if answers not in [["I don't understand"], ["No answers"]]:
                answers = answers[:result_limit]

            # Display results
            if answers == ["I don't understand"]:
                console.print("[red]❌ I don't understand that query. Try rephrasing it.[/red]")
            elif answers == ["No answers"]:
                console.print("[yellow]⚠️  No results found.[/yellow]")
            else:
                console.print(f"\n[bold cyan]Found {len(answers)} result(s):[/bold cyan]")
                for i, ans in enumerate(answers, 1):
                    console.print(f"  [green]{i}.[/green] {ans}")

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    console.print("\n[bold cyan]👋 So long![/bold cyan]\n")


if __name__ == "__main__":
    query_loop()
