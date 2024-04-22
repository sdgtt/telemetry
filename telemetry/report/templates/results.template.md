# $board_name

## Build information

```
Boot partition created with arguments:
  - BRANCH: $branch
  - PR_ID: $pr_id
  - TIMESTAMP: $timestamp
  - DIRECTION: $direction

Triggered by: $triggered_by
  - COMMIT SHA: $commit_sha
  - COMMIT_DATE: $commit_date

Test info
  - JOB NAME: $test_job_name
  - BUILD NO: $test_build_number
  - STATUS: $test_build_status
```

## HW Test Result Summary

| Stage | Result |
| ----------- | ----------- |
| U-Boot reached? | $uboot_reached_status |
| Linux prompt reached? | $linux_prompt_reached_status |
| IIO Drivers | $drivers_enumerated_status |
| DMESG | $dmesg_status |
| PYADI-IIO Tests | $pytest_tests_status |

## HW Test Result Details

#### Last Failing Stage

- $last_failing_stage

#### Last Failing Stage Failure

- $last_failing_stage_failure

#### Missing IIO Drivers

- $iio_drivers_missing_details

#### Found IIO Drivers

- $iio_drivers_found_details

#### DMESG Errors

- $dmesg_errors_found_details

#### PYADI-IIO tests Failures

- $pytest_failures_details

## Finished: $test_status
