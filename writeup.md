# Assignment 3 - Write UP

## Description
This assignment completes our movie chatbot system by implementing action functions that query our movie database and building a natural language interface. You implemented functions to search for movies by year, director, and actors, as well as the core search system that matches user queries to appropriate database operations. This builds directly on the pattern matching work from Assignment 2 to create a functional conversational AI system.

## What to complete
1. Complete all action functions in `a3.py` (title_by_year, title_by_year_range, etc.)
2. Implement the `search_pa_list` function to handle pattern matching and responses  
3. Add at least one new movie to the database with proper formatting
4. Create a new pattern/action pair and add it to the pa_list
5. Ensure all provided assert statements pass
6. Complete the reflection questions below
7. Push your code to github for grading

## Reflection Questions

1. What are some key programming concepts or techniques that you learned while completing this assignment?
 - Pattern matching with `%` and `_` to capture parts of input.
 - Filtering a list of tuples using small helper functions.
 - Clear return conventions (always lists) and simple control flow for no-match cases.
2. How does the overall movie chatbot system work? Explain the flow from when a user types a query to when they receive an answer.
 - Input is lowercased, cleaned, and split into words.
 - Each pattern in `pa_list` is tried with `match`; the first match wins.
 - The action runs with captured args and returns answers.
 - No answers → ["No answers"]. No pattern → ["I don't understand"].
 - Answers are printed; "bye" exits.
3. What are some real-world applications where this type of pattern-matching chatbot system could be useful? How might you extend or improve this system for practical use?
 - FAQs/help desks; small catalog/library searches; simple command bots.
 - Add fuzzy matching and synonyms. basic entity recognition for names and years.
 - Rank multiple matches and ask clarifying questions when ambiguous.