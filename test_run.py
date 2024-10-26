from main import handler

json = {
    "max_pages_to_scrape": "2",
    "indeed_url": "https://nl.indeed.com/jobs?q=data+engineer&l=Randstad&from=searchOnDesktopSerp&vjk=4a22423f33e637de"
}

handler(json, None)
