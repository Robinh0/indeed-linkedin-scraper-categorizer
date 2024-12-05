COLUMNS = [
    "location",
    "programming_languages",
    "backend_frameworks",
    "frontend_frameworks",
    "seniority_level",
    "company_type",
    "years_of_experience",
    "company_industry",
    "company_size",
    "has_django",
    "has_python",
    "is_fullstack",
    "is_sustainability_focused",
]

FUNCTION_CONTEXT = [{
    "name": "choose_from_options",
    "description": "Analyse the job post and choose the correct category from the provided options. Please do not include the text from the recruiters signature in your analysis, this can be at the end of the text prompt.",
    "parameters": {
        "type": "object",
        "properties": {
            "has_python": {
                "type": "string",
                "description": "Is Python specifically mentioned as a requirement for this job post? Return exactly the has_python json key",
                "enum": ['True', 'False']
            },
            "has_django": {
                "type": "string",
                "description": "Is Django specifically mentioned as a requirement for this job post? Return exactly the has_django json key",
                "enum": ['True', 'False']
            },
            "is_fullstack": {
                "type": "string",
                "description": "Is this a fullstack role with React, Angular or Vue? Return exactly the is_fullstack json key",
                "enum": ['True', 'False']
            },
            "frontend_frameworks": {
                "type": "string",
                "description": "What frontend frameworks are mentioned? Return all that are mentioned. Return exactly the frontend_frameworks json key",
            },
            "backend_frameworks": {
                "type": "string",
                "description": "What backend frameworks are mentioned? Return all that are mentioned. Return exactly the backend_frameworks json key",
            },
            "programming_languages": {
                "type": "string",
                "description": "What programming languages are mentioned? Return all that are mentioned. Return exactly the programming_languages json key",
            },
            "company_type": {
                "type": "string",
                "description": "Is this a consultancy or an in house job position? Return exactly the company_type json key",
                "enum": ['in_house', 'consultancy']
            },
            "seniority_level": {
                "type": "string",
                "description": "Is this a junior, medior or a senior job position? Return exactly the seniority_level json key",
                "enum": ['junior', 'medior/junior', 'medior', 'medior/senior', 'senior']
            },
            "years_of_experience": {
                "type": "string",
                "description": "How many years of experience is required for this job role as a number? Return exactly the years_of_experience json key",
            },
            "is_sustainability_focused": {
                "type": "string",
                "description": "Is job post specifically oriented towards sustainability and making an impact on the planet and reducing footprint? Return exactly the is_sustainability_focused json key",
                "enum": ['True', 'False']
            },
            "company_industry": {
                "type": "string",
                "description": "What is the company industry? Return exactly the company_industry json key",
            },
            "location": {
                "type": "string",
                "description": "What is the location of the company in the job post? Return exactly the location json key",
            },
            "company_size": {
                "type": "integer",
                "description": "If the company name is mentioned, what is the estimated company size in FTE? Return exactly the company_size json key",
            },
        },
    },
    "required": COLUMNS
}]
