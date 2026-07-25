# Build roadmap: from case study to working project

The case study is real and defensible as it stands. This is how to build it into a working system over the next few weeks.

## Week 1 - Discovery with real evidence
Mine public complaints (Reddit food-delivery and e-commerce communities, seller forums, Play Store reviews of shopping apps) for two sides of the problem: sellers and restaurants hit by false claims, and honest shoppers whose refunds were denied. Label 100-200 posts by issue type and who was harmed. Interview 5 sellers or restaurant owners and 5 shoppers who have filed a damage claim.

## Week 2 - Image signals on real data
Build a small evaluation set: real product-damage photos plus AI-edited versions you create with an open image-editing model. Test an open-source AI-image detector and a perceptual-hash near-duplicate check on it, and report precision and false positives. This replaces the detector accuracy assumed in the simulation.

## Week 3 - Working live-capture prototype
Turn the prototype into a web app (for example Streamlit or a simple React page) that opens the camera, shows a random prompt, hashes the capture and attaches a timestamp. Run a usability test with 5-8 people: time to complete, retakes, and how fair the step felt.

## Week 4 - Re-run the simulation and write up
Replace assumptions with what you measured (detector accuracy, live-capture completion and drop-off), re-run the policy comparison, and publish a short write-up showing which conclusions held and which changed.

## Production path (for the write-up's scaling section)
Risk scoring as a low-latency service called at return-flow start; signals from order, account and logistics systems; image checks run asynchronously; C2PA Content Credentials accepted as camera-device support grows; seller dispute dashboard; weekly model retraining with fraud outcomes from inspections and appeals.
