import wikipediaapi

def get_wikipedia_url(person_name, language = 'en'):

    user_agent = 'YourProjectName (youremail@example.com)'
    wiki = wikipediaapi.Wikipedia(user_agent = user_agent, language = language)

    page = wiki.page(person_name)

    if page.exists():
        return page.fullurl
    else:
        return f"The wikipedia page for '{person_name} was not found'"
    
person_name = "Pelé"
language = 'en'
print(get_wikipedia_url(person_name, language))