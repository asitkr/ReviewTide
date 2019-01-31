"""Parse a pull request export in JSON Lines format.

Each line is one JSON object describing a pull request. The offline export
is expected to carry these fields:

    id            integer or string, unique per pull request
    author        login of the person who opened it
    directories   list of top-level directories the change touched
    opened_at     ISO 8601 timestamp when the PR was opened
    reviews       list of review events, each with:
                      reviewer    login of the reviewer
                      submitted_at ISO 8601 timestamp
