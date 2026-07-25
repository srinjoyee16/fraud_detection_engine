# Research kit (Weeks 1-3)

Everything you need to run the real research. Results go in `research/findings.md` once you have them. Don't write findings before the sessions happen.

## Week 1A: complaint mining

Collect 300-500 posts by hand or with a tool, from Reddit (r/india, r/IndianShopping, r/swiggy, r/zomato, r/FlipkartSeller-type communities), Play Store reviews of shopping and food apps (sort by newest, 1-2 stars), and seller forums. Save them as `research/data/posts.csv` with columns `source,url,text`. Then run:

```bash
python research/mine_complaints.py research/data/posts.csv
```

Hand-label the 60-post sample it creates (fill `human_issue` with one of: fake_photo_fraud, honest_claim_denied, slow_refund, pickup_inspection, proof_friction, other). Then check how well the rules match your judgement:

```bash
python research/mine_complaints.py --agreement research/output/hand_label_sample.csv
```

If kappa is below 0.6, tighten the patterns in the script and re-run. Report the post counts, the agreement score and 5-8 representative quotes.

## Week 1B: interviews (5 sellers or restaurant owners, 5 shoppers)

Keep each to 20-25 minutes. Ask about past behaviour, not opinions about your idea (The Mom Test).

**Sellers**
1. Tell me about the last time a customer claimed an item arrived damaged or wrong. What happened?
2. How did you find out whether the claim was genuine?
3. How often does this happen in a month? What does one false claim cost you?
4. What have you tried to protect yourself (packing videos, photos, disputes)? What worked?
5. When the platform decides, what do you see? What would you want to see?

**Shoppers (people who have filed a damage or wrong-item claim)**
1. Walk me through the last time you received something damaged or wrong.
2. What were you asked to provide? How long did the refund take?
3. Was anything about it frustrating or felt unfair?
4. If you were asked to take a live photo in the app with a prompt, how would that feel? (Ask this last, after the behaviour questions.)
5. Have you ever had a genuine claim rejected? What happened?

Log each interview in a table: participant type, city tier, key quotes, pains, current workaround, and a surprise. Afterwards, cluster the pains and compare them with the complaint-mining counts.

## Week 3: usability test of the working app (5-8 people)

Host the app on GitHub Pages so the camera works on phones. Give each participant three tasks: file a low-risk claim with a gallery photo, file a medium-risk claim using the live prompt, and file a high-risk claim with the claim code in frame. Measure completion (yes/no), time per task, retakes, and a 1-5 rating for "this felt fair". Ask one open question at the end: what would make you abandon this claim? Note that participants are friends and classmates, which is a bias, and record it.

## Week 2: detector test

Build a set of 40 real photos of your own damaged or undamaged items, then create 40 AI-edited versions with an open image editor. Run an open-source AI-image detector and the app's dHash near-duplicate check on all 80. Report precision, recall and false positives, both on the originals and after JPEG compression (quality 60). Then replace `DETECTOR_TPR` and `DETECTOR_FPR` in `analysis/simulate.py` with what you measured and re-run.
