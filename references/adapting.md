# Applying the method beyond AI features

The phases never change. What changes is the judge, the hard checks, and what "live" means.

| What you are improving | Real cases | Judge | Hard checks | Live verdict |
|---|---|---|---|---|
| AI feature / agent / prompt / model swap | Real production inputs | Blind pairwise model judge, other vendor, both orders | Links load, quotes appear in source, facts match, cost per run, latency, schema valid | Usage, complaints, retries, regenerations |
| Email / subject line | Past campaigns and their results | Blind judge as pre-screen only | Offer valid, links work, no broken merge fields, no claim you cannot back | Open and click rate vs past sends of the same genre |
| Landing / pricing page | Real traffic, past copy, objections from sales and support | Blind judge as pre-screen only | Prices match checkout, page speed, mobile layout, accessibility | A/B test on conversion — check traffic is enough to reach a result first |
| YouTube titles / thumbnails | Your past videos and their CTR | Blind judge as pre-screen only | Title length, readability at small size | Platform test-and-compare CTR, then watch time |
| Code change / performance | Real workloads and inputs | Usually none | Test suite, benchmarks on real inputs, error rate, memory | Production latency and error dashboards |
| Cost / cloud bill | Real invoices and usage line items | None | $ per month per line, latency, error rate, availability, backups | Next invoices vs baseline |
| Support / sales process | Real past tickets or calls | Blind judge on reply quality | Policy correct, resolution time, refund accuracy | Resolution rate, CSAT, conversion |

## Notes per domain

- **Behaviour outcomes** (opens, clicks, sign-ups, revenue): the model judge is a cheap filter so you only spend real traffic on strong candidates. The live number decides.
- **Slow feedback** (SEO rankings, retention): decide on hard checks and leading indicators, ship reversibly, and schedule the real-world check for when the data can exist.
- **Costs**: start from the real invoice, not a usage estimate. Seats, other projects on the same account and duplicate charges often matter more than any optimisation.
- **Copy and marketing claims**: every number in the copy must come from a measurement; the render or review step should check for invented deadlines, prices that differ from checkout, and broken personalisation.
- **No current version** (a brand-new thing): compare two or more candidates against each other with the same blind method, then compare the winner against the user's stated bar.
