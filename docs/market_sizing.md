# Market sizing: the value at stake for one large Indian marketplace

This is a top-down Fermi estimate. Every input is an assumption, stated so it can be challenged and replaced. None of it is company data.

## Logic

Annual orders × share with a "damaged / wrong / defective" claim × average claim value = total claim value. Multiply by the share of claims that are false to get fraud exposure. Multiply by the reduction the simulation found (63%) to get value at stake.

## Estimate

| Input | Low | Base | High | Reasoning |
|---|---|---|---|---|
| Annual orders | 1.0 B | 1.5 B | 2.0 B | Order of magnitude for a top Indian marketplace |
| Claim rate (damaged / wrong / defective) | 1.5% | 2.0% | 2.5% | A subset of all returns; excludes "changed my mind" |
| Claims per year | 15 M | 30 M | 50 M | |
| Average claim value | Rs 1,000 | Rs 1,200 | Rs 1,400 | Mix of fashion, electronics and home |
| Total claim value | Rs 1,500 Cr | Rs 3,600 Cr | Rs 7,000 Cr | |
| Share of claims that are false | 5% | 8% | 10% | Public US estimates put return fraud at about 9% of returns |
| **Fraud exposure per year** | **Rs 75 Cr** | **Rs 288 Cr** | **Rs 700 Cr** | |
| Reduction from Proof-of-Claim (simulation) | 63% | 63% | 63% | |
| **Fraud loss avoided per year** | **Rs 47 Cr** | **Rs 181 Cr** | **Rs 441 Cr** | |
| Added ops cost (about Rs 9 per claim) | Rs 14 Cr | Rs 27 Cr | Rs 45 Cr | Inspection and review |

In the base case, about Rs 180 Cr a year of fraud loss is avoided for about Rs 27 Cr of added operating cost. Even the low case pays for itself several times over. The weakest input is the fraud share, which is also the hardest number to observe. That's why Phase 1 runs the score in shadow mode first.

## What's not counted

The estimate doesn't count seller trust and retention (sellers bear part of the loss and leave platforms that don't protect them), or the value of keeping instant refunds for honest shoppers compared with blanket policies. It also doesn't count the deterrent effect over time, as word spreads that faking doesn't work.
