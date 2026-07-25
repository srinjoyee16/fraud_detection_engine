# Existing solutions and competitive landscape

Researched October 2026 from public sources. Vendor claims are their own and have not been independently verified.

## How the problem is handled today

Responses fall into six groups, and each one leaves a gap.

| Approach | Who does it (public examples) | What it gets right | Where it falls short |
|---|---|---|---|
| Customer history scoring | Zomato's "karma score" on customer and rider behaviour, which its CEO has said is not always accurate | Cheap, uses data the platform already has | Weak on new accounts, and can't judge the photo itself |
| AI-image detection after upload | Taobao/Tmall detector for refund photos (announced Jan 2026); commercial detector tools | No change to the shopper flow | Fragile. In public benchmarks, detector accuracy collapses on compressed JPEGs (one academic detector fell from 95% to 0.2% at JPEG quality 50); a 16-method study found about 21-24% mean accuracy on the newest generators; a May 2026 audit found about 13% false positives on real photos across commercial tools |
| More proof from everyone | US brands asking for second angles, video or video calls (Modern Retail, Mar 2026) | Raises the effort of faking | Adds friction for every honest shopper, which hurts CSAT and repeat purchase |
| Return or inspect before refund | Common retail policy; inspection at pickup | Most reliable | Slowest refunds; costly at marketplace scale |
| Seller-side evidence | Deliverect Resolve (overhead cameras recording restaurant packing, Australia) | Gives the merchant a way to dispute | Needs hardware; covers the packing step, not damage in transit |
| Capture-time verification and provenance | Switch Labs VerifyAI (live in-app capture, server timestamps, vision-model policy check); Truepic (provenance); C2PA Content Credentials, now signed by default on Google Pixel 10 | Removes the fake gallery image instead of trying to detect it | Usually sold as a blanket step for every claim; C2PA phone support is still thin in India, and researchers have found weaknesses in it |
| Return-abuse fraud platforms | Forter (whose data names AI-generated damage claims as the fastest-growing form of return abuse) and similar trust-and-safety vendors | Cross-merchant signal, mature risk scoring | Focused on account and transaction risk; the photo step and doorstep logistics sit outside them |

## The gap Proof-of-Claim fills

Nobody I found combines the three things a large marketplace with its own logistics can do together. The first is a claim-level risk score that decides how much proof a claim needs, so most honest shoppers keep instant refunds. The second is capture-time verification, used only on the riskier claims. The third is the marketplace's own pickup network as a final physical check, with seller visibility into every decision.

Live capture on its own is not new, since a vendor already sells it. The contribution here is the tiering: routing friction to where fraud is and keeping it away from honest shoppers. That's also what the simulation tests.

## Existing frameworks used

- **C2PA / Content Credentials** for photo provenance where devices support it (accepted as equivalent to live capture in FR6).
- **Perceptual hashing** (for example pHash) for near-duplicate image matching across claims.
- **Graduated response** from trust-and-safety practice: friction matched to risk rather than one rule for everyone.
- **Cost-based decision thresholds** from fraud modelling: bands are set on expected cost, not on the model score alone.

## Sources

- Modern Retail, "From Boll & Branch to Bogg, brands are battling a surge of AI-driven return fraud" (2 Mar 2026)
- Retail Gazette, "Retailers face surge in AI-generated fake damage claims and refund scams" (Jun 2026), citing Forter data
- Switch Labs, "AI image detectors and damage claims" (summarising AIGIBench, arXiv 2602.07814 and a May 2026 NewsGuard audit)
- OECD AI Incidents Monitor (Taobao/Tmall detector); Curly Tales and Storyboard18 (Zomato, Jan 2026); QSR Media (Deliverect Resolve); Google (Pixel 10 Content Credentials)
