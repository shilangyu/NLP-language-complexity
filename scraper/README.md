# NLP language complexity scraper

A GitHub API scraper written in Rust for the NLP language complexity project.

Pre-scraped data can be found here (3th of May 2022): https://drive.google.com/uc?export=download&id=1BrTQHTMAvPC54rGmWMs0e_ATTgRD1NFz 233,686 instances (71MB gzipped, 235MB unpacked)

## Procedure

1. Get top 1000 users for each of the studied programming language
2. Get top 100 issues created by each user
3. Save issue content to csv

### Details

4 languages are studied,

- Python
- C
- Javascript
- Golang

due to their somewhat different target demographic.

Due to GitHub rate limiting, authentication is required using a github access token (provided through the env var `GITHUB_TOKEN`) which increases the amount of requests that can be done. Additionally, the search API has a reduced amount of requests allowed (namely 30 per minute) which forces the scraper to pause for a minute every time the limit was reached. This results in a very slow process: whole procedure takes around 3 hours (given a strong and stable internet connection). 134 minutes alone is spent on just waiting.

#### Ad 1

In a single request 100 users can be fetched, thus fetching all 4,000 users costs 40 requests (more than the rate limit allows).

> top 1000 users

Ranked by the amount of followers, gives a high level filter for quality of issues. All users have at least 170 followers. Only personal accounts are considered, organizations are filtered out.

> for each of the studied programming language

As assigned by the GitHub search API using the `language:` filter. [Quoting the search API reference](https://docs.github.com/en/search-github/searching-on-github/searching-users#search-by-repository-language): _"majority of their repositories [are] written in LANGUAGE"_

#### Ad 2

In a single request 100 issues of a single user can be fetched, thus fetching (up to) 400,000 issues costs 4,000 requests.

> top 100 issues

Ranked by the amount of interactions. Only the body of the posted issue is saved, the thread that follows is not.

#### Ad 3

Streamed directly to `.csv.gz` files.
