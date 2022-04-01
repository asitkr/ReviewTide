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
