use std::env;

mod config;
mod octocrab_ext;
mod outputs;
mod scrape;

pub type Result<T = ()> = std::result::Result<T, Box<dyn std::error::Error + Send + Sync>>;

#[tokio::main]
async fn main() -> Result {
    let octocrab = octocrab::Octocrab::builder()
        .personal_token(env::var("GITHUB_TOKEN").expect("need to provide token in GITHUB_TOKEN"))
        .build()?;

    let users = scrape::scrape_users(&octocrab).await?;

    scrape::scrape_issues(&octocrab, users).await?;

    Ok(())
}
