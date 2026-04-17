# Sample fixtures

These two files are authored test vectors. They are not exported from a real
repository. They were hand written to exercise every code path in reviewtide
and to give the bus-factor signal something real to find. Do not treat them as
production data.

## gitlog.numstat

A `git log --numstat` export in the format reviewtide expects:

```
commit\t<hash>\t<author>\t<iso-date>
<added>\t<deleted>\t<path>
```

Twenty commits across five top-level directories: `src`, `tests`, `docs`,
`cli`, and `infra`. Every commit that touches `infra` is authored by Dana Kim,
so `infra` has a bus factor of 1 by construction. `docs` also happens to have a
single author in this vector. Line counts are plausible but invented.

## pr_export.jsonl

A pull request export in JSON Lines, one PR object per line, matching the
commits above in author, directory, and timing. Twenty PRs. Two of them
(ids 107 and 116) carry no reviews, so the "never reviewed" count is a real,
non-zero signal. Review timestamps were chosen to spread first-response
latency from about one hour to about sixty-seven hours so the percentile
summary has a real shape rather than a flat line.

Every number reviewtide prints from these files is computed from the file
contents. Nothing in the output is hard coded.
