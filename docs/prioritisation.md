# Options considered and prioritisation

## RICE scoring

Reach is the share of fraud exposure the option addresses. Impact is net impact on fraud loss, on a 0.25-3 scale. Confidence reflects how much evidence exists. Effort is in person-months.

| Option | Reach | Impact | Confidence | Effort | RICE |
|---|---|---|---|---|---|
| Live capture for every claim | 100 | 1 | 60% | 3 | 20.0 |
| Return item before any refund | 100 | 0.5 | 80% | 2 | 20.0 |
| **Proof-of-Claim (risk-tiered)** | 87 | 2 | 60% | 6 | **17.4** |
| Inspect every pickup | 100 | 1 | 80% | 8 | 10.0 |
| Seller packing-video evidence | 60 | 1 | 50% | 4 | 7.5 |
| AI-image detector gate | 35 | 0.5 | 40% | 2 | 3.5 |
| Cross-platform offender registry | 40 | 1 | 30% | 9 | 1.3 |

## Why the top RICE score isn't the pick

RICE on its own put two blanket options at the top. Both are cheap to build and reach every claim. But RICE only scores the benefit, and the cost of these options falls on honest shoppers, who are about 92% of claimants. So I added a guardrail gate: an option is out if it removes instant refunds for most honest shoppers.

| Option | Honest shoppers who keep instant refunds | Passes gate? |
|---|---|---|
| Live capture for every claim | 0% (everyone does the capture step) | No |
| Return item before any refund | 0% | No |
| Inspect every pickup | 0% (4-day average wait in simulation) | No |
| Proof-of-Claim (risk-tiered) | 59% instant, 0.8-day average wait | Yes |
| AI-image detector gate | 96%, but about 12 per 10k honest shoppers wrongly denied | Yes, but low impact |

With the gate applied, Proof-of-Claim is the clear pick. Live capture for every claim is kept as a **fallback** for categories or regions where the risk model can't be trained yet.

## Rejected ideas and why

- **Detector as the decision maker:** public benchmarks show detectors fail on compressed images and new generators, and they wrongly flag real photos, so honest shoppers get denied. Kept only as one input to the risk score.
- **Cross-platform offender registry:** strong in theory, but it needs data-sharing agreements and raises privacy questions under India's DPDP Act. Too slow and uncertain for v1.
- **Seller packing videos:** useful, but they need seller hardware and don't cover damage in transit. Moved to the seller dispute flow (FR5) as optional evidence.

## How my thinking changed

I started out assuming better AI-image detection was the answer, since the problem is AI-generated images. The research changed that. Detection is losing the arms race, and most fraud doesn't even use AI photos (35% in the simulation's assumption). That moved the design from detecting fakes to verifying at capture, and from treating every claim the same to routing friction by risk.
