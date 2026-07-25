# Experiment plan: Proof-of-Claim Phase 2

## Hypothesis

Requiring live in-app capture for medium- and high-risk "damaged / wrong item" claims will cut fraud loss per 1,000 claims by at least 30%, without lowering the share of honest claims refunded within 24 hours by more than 3 percentage points.

## Design

Randomise at buyer level, 50/50, in electronics and fashion. Control keeps the current photo-upload flow. Treatment applies the band rules. The risk score runs in both arms, so the two arms can be compared within the same band. Fraud is not observed directly, so it is measured through proxies: claims later disproved at pickup inspection, sellers' upheld disputes, and claims abandoned at the proof step.

## Metrics and stop rules

| Type | Metric | Rule |
|---|---|---|
| Primary | Fraud loss per 1,000 claims (proxy) | Ship if down 30% or more and significant |
| Guardrail | Honest claims refunded within 24h | Stop if down more than 3 pp |
| Guardrail | Return-flow drop-off, low and medium bands | Stop if up more than 2 pp |
| Guardrail | Wrongful denials overturned on appeal | Stop if above 10 per 10,000 honest claims |
| Secondary | Live-capture completion, retake rate, CSAT | Monitor |

## Sample size

Fraud proxies are rare, so the test is powered on the medium and high bands, where most fraud sits. If about 15% of claims in those bands are false and we want to detect a drop to 10.5% (a 30% relative cut) at 80% power and 5% significance, each arm needs roughly 860 claims from those bands. Run at least three weeks so pickup and inspection outcomes are back for most claims.

## Readout questions

Did abandonment at the live-capture step come mostly from claims the model scored as risky (good) or from honest shoppers (bad)? Did fraud shift to other issue types such as "missing parts", which would need the same treatment?
