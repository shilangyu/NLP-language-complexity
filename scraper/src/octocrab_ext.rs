use octocrab::{models, Octocrab, Result};

use crate::config::{github_limits::MAX_PAGE_SIZE, Language};

#[async_trait::async_trait]
pub trait OctocrabExt {
    async fn users_for_lang(&self, lang: Language) -> Result<Vec<models::User>>;
    async fn issues_of_user(&self, user_login: &str) -> Result<Vec<models::issues::Issue>>;
}

#[async_trait::async_trait]
impl OctocrabExt for Octocrab {
    /// https://docs.github.com/en/search-github/searching-on-github/searching-users
    async fn users_for_lang(&self, lang: Language) -> Result<Vec<models::User>> {
        let mut page = self
            .search()
            .users(&format!("followers:>170 language:{lang} type:user"))
            .sort("followers")
            .order("desc")
            .per_page(MAX_PAGE_SIZE)
            .send()
            .await?;

        // max a mount of search results
        let mut users = Vec::with_capacity(1000);

        loop {
            users.extend(page.items);

            page = match self.get_page::<models::User>(&page.next).await? {
                Some(next_page) => next_page,
                None => break,
            }
        }

        return Ok(users);
    }

    /// https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests
    async fn issues_of_user(&self, user_login: &str) -> Result<Vec<models::issues::Issue>> {
        let page = self
            .search()
            .issues_and_pull_requests(&format!("type:issues author:{user_login}"))
            .sort("interactions")
            .per_page(MAX_PAGE_SIZE)
            .send()
            .await?;

        return Ok(page.items);
    }
}
