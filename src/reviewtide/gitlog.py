"""Parse a `git log --numstat` export.

The expected export is produced by:

    git log --numstat --date=iso-strict \
        --pretty=format:'commit%x09%H%x09%an%x09%ad'

Each commit begins with a header line whose first field is the literal
token `commit`, followed by the hash, author name, and an ISO 8601 date.
Numstat lines follow, one per changed file:

