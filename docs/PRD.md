# PRD: Proof-of-Claim - risk-tiered verification for "damaged / wrong item" refunds

Author: Srinjoyee Chakravarty | Status: Concept (personal case study) | Last updated: October 2026

This is a self-initiated case study. It uses public reporting and a synthetic simulation. It is not affiliated with, or based on internal data from, any company.

## 1. Problem

Refunds for "item arrived damaged" or "wrong item delivered" usually rest on one photo the shopper uploads. Generative AI has made that photo cheap to fake: a crack added to a screen, a stain on a kurta, an insect in a food order, or a recycled image from someone else's claim. In January 2026, Zomato's CEO said publicly that some customers use AI to doctor food photos for refunds, and a Mumbai bakery went viral after spotting an AI-generated "smashed cake" used to claim a Rs 1,820 refund. US brands have reported the same pattern with AI-faked damage photos, and Taobao and Tmall announced an AI-image detector for refund claims in early 2026.

The obvious fixes each hurt someone. An AI-image detector alone is an arms race: it misses better fakes and wrongly flags real photos, which means honest shoppers get denied. Inspecting every return at the door catches most fraud but makes every honest shopper wait days for their money. Sellers absorb the loss either way and have little say in the decision.

The problem: **make faked refund claims expensive to attempt, while keeping refunds instant for the large majority of honest shoppers.**

## 2. Users

**Meera, honest shopper.** Her speaker arrived with a cracked grille. She wants her money back today without proving her innocence. Every extra step feels like being accused.

**Arjun, opportunistic claimant.** He has learned that one edited photo usually gets a refund and he keeps the item. He will not bother if faking becomes effortful or likely to fail.

**The seller.** A small electronics seller whose margin on a Rs 2,499 item disappears with one false claim. Wants evidence-based decisions and visibility into why refunds were granted.

**The pickup agent.** Can check an item at the door in about a minute if the app tells them exactly what to look for.

## 3. Key insight

Detection after the fact is a losing race; **verification at the moment of capture** changes the economics. If a risky claim can only be supported by a live, in-app photo with a random prompt (tilt the box to show the label, hold the item next to an order QR code), an AI-edited gallery image cannot be used at all. The fraudster now has to physically damage the item, which most will not do. Honest shoppers lose about 20 seconds. Combined with a claim risk score, this extra step only reaches the claims that need it.

## 4. Solution

A claim risk score is computed when the shopper opens the return flow, using account age, past claim rate, time from delivery to claim, item value and category, the SKU's real defect rate, whether it was an open-box delivery, and photo signals (missing camera metadata, AI-detector score, near-duplicate match against other claims).

| Band | Share of claims (sim) | Proof required | Refund timing |
|---|---|---|---|
| Low | ~55% | Any photo, gallery allowed | Instant |
| Medium | ~30% | Live in-app capture with a random prompt, signed at capture | On pickup scan |
| High | ~12% | Live capture with order QR in frame + doorstep inspection | After the agent's check at the door |
| Very high | ~3% | Live video + doorstep inspection + specialist review | Within 48 hours, one-tap appeal |

The AI detector is one input to the score, never a verdict on its own.

## 5. Functional requirements

**FR1 - Claim risk scoring (P0).** Score is returned within 200 ms of opening the return flow. Acceptance: on timeout the claim falls to the medium band (live capture), never to auto-denial; every decision logs the top contributing signals.

**FR2 - Live capture mode (P0).** For medium and above, the proof step opens the in-app camera only, with a randomly chosen prompt. Acceptance: gallery upload is disabled for that claim; each capture stores device time, app-signed hash and prompt ID; a capture that does not show the prompted element can be retaken twice before routing to review.

**FR3 - Doorstep inspection (P0).** The pickup agent's app shows the claim photo and a checklist for that issue type. Acceptance: a match releases the refund immediately; a mismatch routes to review with photos from both sides; the shopper is told the outcome before the agent leaves.

**FR4 - Specialist review and appeal (P1).** Very-high claims and inspection mismatches go to a review queue. Acceptance: decision within 48 hours; every denial includes a reason and a one-tap appeal; appeals are reviewed by a different reviewer.

**FR5 - Seller visibility (P1).** Sellers see the band, evidence and outcome for each claim on their products. Acceptance: sellers can dispute an approved claim once with their own evidence (for example, packing video).

**FR6 - Content Credentials (P2).** Where the device camera supports C2PA signing, accept signed photos from the gallery as equivalent to live capture.

## 6. Metrics

**North Star:** fraud loss per 1,000 claims at constant honest-shopper experience.
**Guardrails:** share of honest claims refunded instantly, average refund wait for honest shoppers, wrongful-denial rate (overturned on appeal), return-flow drop-off for honest shoppers, CSAT after refund.
**Secondary:** live-capture completion rate, inspection match rate, review queue time, seller dispute rate.

## 7. Risks

The model may treat new users unfairly because account age is a strong signal, so new users should never go above the medium band on account age alone. Live capture needs a working camera and connectivity; a low-bandwidth fallback (single compressed frame) is needed for Tier-3 users. Fraud adapts: if fraudsters move to physical damage, doorstep inspection and SKU-level defect baselines carry more weight. Agents may rubber-stamp inspections, so 5% of inspections are audited.

## 8. Rollout

Phase 1: risk score in shadow mode for two weeks (scores logged, no change to shoppers) to calibrate bands. Phase 2: live capture for the medium and high bands in electronics and fashion as an A/B test. Phase 3: doorstep inspection and review queue, seller dashboard, then C2PA acceptance.
