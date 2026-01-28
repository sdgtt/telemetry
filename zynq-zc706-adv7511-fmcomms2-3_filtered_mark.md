# zynq-zc706-adv7511-fmcomms2-3

## Build information

```
Boot partition created with arguments:
  - BRANCH: main
  - PR_ID: 123
  - TIMESTAMP: 2024-01-28
  - DIRECTION: forward

Triggered by: cseci
  - COMMIT SHA: abc123def456
  - COMMIT_DATE: 2024-01-27

Test info
  - JOB NAME: test
  - BUILD NO: 1
  - STATUS: UNSTABLE
```

## HW Test Result Summary

| Stage | Result |
| ----------- | ----------- |
| U-Boot reached? | ✔ |
| Linux prompt reached? | ✔ |
| IIO Drivers | ✔ |
| DMESG | ❌ |
| PYADI-IIO Tests | ❌ |

## HW Test Result Details

#### Last Failing Stage

- No Details

#### Last Failing Stage Failure

- No Details

#### Missing IIO Drivers

- No missing drivers

#### Found IIO Drivers

- iio:device0 - ad9361-phy<br>iio:device1 - cf-ad9361-dds-core-lpc

#### DMESG Errors

- ad9361 spi1.0: Failed to initialize device [KNOWN: Sporadic SPI init failure - under investigation]<br>cf_axi_dds: probe failed with error -110 [KNOWN: Known timing issue on ZC706 - JIRA-456]

#### PYADI-IIO tests Failures

- test_ad9361_rx_gain::FAILED - AssertionError: Expected gain 20, got 18 [KNOWN: Flaky gain test - JIRA-789]

## Finished: UNSTABLE
