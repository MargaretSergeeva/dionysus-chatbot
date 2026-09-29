import csv
import json
import time
import urllib.request
import urllib.error

# Configuration
API_URL = "http://localhost:8000/api/chat"
INPUT_CSV = "/workspace/artifacts/dionysus_100_test_questions.csv"
OUTPUT_REPORT = "/workspace/scratch/dionysus_eval_results.json"

def run_evaluation():
    print(f"Starting evaluation of Dionysus using {INPUT_CSV}...")
    
    results = []
    
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        questions = list(reader)
        
    print(f"Loaded {len(questions)} test cases.")
    
    for i, q in enumerate(questions, 1):
        q_id = q["id"]
        cat = q["category"]
        prompt = q["question_text"]
        expected = q["expected_answer"]
        target = q["target_source"]
        fail_criteria = q["failure_mode"]
        
        payload = json.dumps({"message": prompt}).encode("utf-8")
        req = urllib.request.Request(API_URL, data=payload, headers={"Content-Type": "application/json"})
        
        start_time = time.time()
        try:
            with urllib.request.urlopen(req) as response:
                bot_response = response.read().decode("utf-8")
                latency = round(time.time() - start_time, 3)
                status = "SUCCESS"
        except Exception as e:
            bot_response = f"ERROR: {str(e)}"
            latency = round(time.time() - start_time, 3)
            status = "FAILED"
            
        results.append({
            "id": q_id,
            "category": cat,
            "question": prompt,
            "expected_answer": expected,
            "target_source": target,
            "failure_criteria": fail_criteria,
            "status": status,
            "latency_seconds": latency,
            "bot_response": bot_response
        })
        
        print(f"[{i}/{len(questions)}] Question ID {q_id} ({cat}): {status} ({latency}s)")
        
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\nEvaluation script template ready. Results will be saved to {OUTPUT_REPORT}.")

if __name__ == "__main__":
    run_evaluation()
