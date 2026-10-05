# REST API & Webhook Troubleshooter Bot

A FAQ chatbot that helps developers debug common REST API and webhook problems
(HTTP status codes, authentication, CORS, rate limits, webhook failures).

> Status: work in progress

## Task requirements

- [ ] Collect FAQs on REST APIs and webhooks
- [ ] Preprocess text with spaCy (tokenize, clean, lemmatize)
- [ ] Match user questions with TF-IDF + cosine similarity
- [ ] Display the best matching answer as a chatbot response
- [ ] Optional: Streamlit chat UI

## How it works

1. **Collect:** FAQ pairs stored in `data/faqs.csv`
2. **Preprocess:** clean and normalize text with spaCy
3. **Match:** TF-IDF vectors + cosine similarity
4. **Respond:** return the best answer, or a fallback if confidence is low

## Project structure

- `data/` - FAQ dataset and test questions
- `src/` - preprocessing, matching, and chatbot logic
- `app/` - Streamlit UI
- `notebooks/` - experiments
- `tests/` - automated tests
- `docs/` - screenshots and demo

## Setup

Instructions will be added once the project is complete.

## Results

Evaluation results will be added here.

## Limitations and future work

To be added.