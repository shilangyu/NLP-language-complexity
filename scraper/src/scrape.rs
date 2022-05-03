use std::fs::File;
use std::future::Future;

use flate2::write::GzEncoder;
use flate2::Compression;
use futures::TryFutureExt;
use futures::{stream::FuturesUnordered, StreamExt};
use octocrab::Octocrab;
use tokio::time::sleep;

use crate::config::github_limits::{SEARCH_CALLS_PER_MINUTE, SEARCH_RATE_LIMIT_COOLDOWN};
use crate::config::{output_paths, Language};
use crate::octocrab_ext::OctocrabExt;
use crate::outputs::{Issue, User};
use crate::Result;

pub struct UserWithLanguage(pub String, pub Language);

pub async fn scrape_users(octocrab: &Octocrab) -> Result<Vec<UserWithLanguage>> {
    let mut wtr = csv::Writer::from_writer(GzEncoder::new(
        File::create(output_paths::USERS)?,
        Compression::best(),
    ));

    let mut results = Vec::new();

    for lang in Language::VALUES {
        let users = rate_limit_guard(|| octocrab.users_for_lang(lang)).await?;

        User::serialize_users(&users, lang, &mut wtr)?;

        results.extend(users.into_iter().map(|u| UserWithLanguage(u.login, lang)));
    }

    Ok(results)
}

pub async fn scrape_issues(octocrab: &Octocrab, users: Vec<UserWithLanguage>) -> Result {
    let mut wtr = csv::Writer::from_writer(GzEncoder::new(
        File::create(output_paths::ISSUES)?,
        Compression::best(),
    ));

    for chunk in users.chunks(SEARCH_CALLS_PER_MINUTE) {
        let mut batch = FuturesUnordered::new();
        for user in chunk {
            batch.push(
                octocrab
                    .issues_of_user(&user.0)
                    .map_ok(|issues| (issues, user.1)),
            );
        }

        while let Some(issues) = batch.next().await {
            let issues = issues?;

            Issue::serialize_issues(&issues.0, issues.1, &mut wtr)?;
        }

        println!("Waiting a minute to refresh rate limits.");
        sleep(SEARCH_RATE_LIMIT_COOLDOWN).await;
    }

    Ok(())
}

/// Retries the request a single time on github error
async fn rate_limit_guard<T, F>(f: impl Fn() -> F) -> octocrab::Result<T>
where
    F: Future<Output = octocrab::Result<T>>,
{
    match f().await {
        Err(octocrab::Error::GitHub { .. }) => {
            println!("Github error: possibly rate limit. Waiting a minute.");
            sleep(SEARCH_RATE_LIMIT_COOLDOWN).await;

            return f().await;
        }
        other => other,
    }
}
