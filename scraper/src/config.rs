use std::fmt;

use serde::Serialize;

#[derive(Copy, Clone, Debug, Serialize)]
pub enum Language {
    Python,
    C,
    Javascript,
    Go,
}

impl Language {
    pub const VALUES: [Self; 4] = [Self::Python, Self::C, Self::Javascript, Self::Go];
}

impl fmt::Display for Language {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{}",
            match self {
                Language::Python => "python",
                Language::C => "c",
                Language::Javascript => "javascript",
                Language::Go => "go",
            }
        )
    }
}

pub mod output_paths {
    pub const USERS: &str = "users.csv.gz";
    pub const ISSUES: &str = "issues.csv.gz";
}

pub mod github_limits {
    use std::time::Duration;

    pub const MAX_PAGE_SIZE: u8 = 100;
    pub const SEARCH_CALLS_PER_MINUTE: usize = 30;
    pub const SEARCH_RATE_LIMIT_COOLDOWN: Duration = Duration::from_secs(60);
}
