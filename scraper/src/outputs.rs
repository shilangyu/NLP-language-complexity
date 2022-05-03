use octocrab::models;
use serde::Serialize;

use crate::config::Language;

#[derive(Clone, Serialize)]
pub struct User<'a> {
    pub login: &'a String,
    pub language: Language,
}

impl<'a> User<'a> {
    pub fn serialize_users(
        users: &Vec<models::User>,
        lang: Language,
        wtr: &mut csv::Writer<impl std::io::Write>,
    ) -> crate::Result {
        for user in users {
            wtr.serialize(User {
                login: &user.login,
                language: lang,
            })?;
        }
        wtr.flush()?;

        Ok(())
    }
}

#[derive(Clone, Serialize)]
pub struct Issue<'a> {
    author_login: &'a String,
    language: Language,
    source_link: &'a str,
    content: &'a String,
}

impl<'a> Issue<'a> {
    pub fn serialize_issues(
        issues: &Vec<models::issues::Issue>,
        lang: Language,
        wtr: &mut csv::Writer<impl std::io::Write>,
    ) -> crate::Result {
        for issue in issues {
            wtr.serialize(Issue {
                author_login: &issue.user.login,
                language: lang,
                source_link: issue.html_url.as_str(),
                content: issue.body.as_ref().unwrap_or(&String::new()),
            })?;
        }
        wtr.flush()?;

        Ok(())
    }
}
