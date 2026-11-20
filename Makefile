export PYTHONPATH := .
up:        ; docker compose up -d
init:      ; python -m kb.db
models:    ; docker compose exec ollama ollama pull bge-m3 && docker compose exec ollama ollama pull qwen2.5:7b-instruct
check:     ; python scripts/check_llm.py
seed:      ; python scripts/seed_synthetic.py
api:       ; uvicorn kb.api:app --reload --port 8000
ui:        ; streamlit run ui/app.py
bot:       ; python bot/slack_bot.py
eval:      ; python eval/run_eval.py eval/questions.yaml --judge
compare:   ; python scripts/compare_variants.py eval/questions.yaml
calibrate: ; python scripts/calibrate_threshold.py eval/questions.yaml
test:      ; pytest -q -m "not integration"
itest:     ; pytest -q -m integration
purge:     ; python scripts/purge_logs.py 90
