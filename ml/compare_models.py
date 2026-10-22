"""
Compare a newly trained candidate model with the current production model.

Both models are scored on the same fresh test set (prepare_data() from train.py)
using macro F1. The candidate is promoted only if it beats the current model by
at least the margin, or if there is no usable current model yet.
"""
import argparse
import json
import os

import joblib
from sklearn.metrics import f1_score

from train import prepare_data

MODEL_FILE = "baseline_xgb.pkl"
LABEL_MAP_FILE = "label_map.pkl"


def load_model(folder):
    model = joblib.load(os.path.join(folder, MODEL_FILE))
    label_map = joblib.load(os.path.join(folder, LABEL_MAP_FILE))
    return model, label_map


def score(model, label_map, X_test, y_test):
    y_true = y_test.map(label_map)
    y_pred = model.predict(X_test)
    return round(float(f1_score(y_true, y_pred, average="macro")), 4)


def decide(candidate_dir, current_dir, margin):
    result = {
        "margin": margin,
        "candidate_macro_f1": None,
        "current_macro_f1": None,
        "difference": None,
    }

    current_files = [os.path.join(current_dir, f) for f in (MODEL_FILE, LABEL_MAP_FILE)]
    if not all(os.path.exists(path) for path in current_files):
        result["decision"] = "promote"
        result["reason"] = "No current production model yet"
        return result

    X_train, X_test, y_train, y_test = prepare_data()

    candidate_model, candidate_map = load_model(candidate_dir)
    result["candidate_macro_f1"] = score(candidate_model, candidate_map, X_test, y_test)

    try:
        current_model, current_map = load_model(current_dir)
        result["current_macro_f1"] = score(current_model, current_map, X_test, y_test)
    except Exception as error:
        result["decision"] = "promote"
        result["reason"] = f"Current model could not be loaded or scored: {error}"
        return result

    difference = round(result["candidate_macro_f1"] - result["current_macro_f1"], 4)
    result["difference"] = difference

    if difference >= margin - 1e-9:
        result["decision"] = "promote"
        result["reason"] = f"Candidate beats current model by {difference:+.4f} (needs {margin})"
    else:
        result["decision"] = "keep"
        result["reason"] = f"Candidate is {difference:+.4f} vs current model (needs {margin})"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", default="models")
    parser.add_argument("--current-dir", default="current_model")
    parser.add_argument("--margin", type=float, default=0.02)
    parser.add_argument("--title", default="Model comparison")
    args = parser.parse_args()

    result = decide(args.candidate_dir, args.current_dir, args.margin)
    print(json.dumps(result, indent=2))

    with open(os.path.join(args.candidate_dir, "decision.json"), "w") as f:
        json.dump(result, f, indent=2)

    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"promote={'true' if result['decision'] == 'promote' else 'false'}\n")

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write(f"### {args.title}\n\n")
            f.write(f"- Decision: **{result['decision']}**\n")
            f.write(f"- Reason: {result['reason']}\n")
            f.write(f"- Candidate macro_f1: {result['candidate_macro_f1']}\n")
            f.write(f"- Current macro_f1: {result['current_macro_f1']}\n\n")


if __name__ == "__main__":
    main()