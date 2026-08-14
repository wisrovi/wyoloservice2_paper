#!/usr/bin/env bash

# List of all completed papers to validate
papers=(
  "paper_1_mlops"
  "paper_2_xai"
  "paper_3_robustness"
  "paper_4_crossdomain"
  "paper_5_statistical"
  "paper_6_llm_reporting"
  "paper_7_wpipe"
  "paper_8_hardware_complexity"
  "paper_9_outlier_failure_analysis"
)

echo "Starting validation of all completed papers..."

for paper in "${papers[@]}"; do
  echo "--------------------------------------------------"
  echo "Validating $paper..."
  ./run_revisor.sh "$paper"
  echo "Finished $paper."
done

echo "All validations complete."
