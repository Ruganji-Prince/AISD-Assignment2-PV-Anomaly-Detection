## Hardware-class recall under sensor measurement noise

| Noise | Coverage | Model | Short recall | Degradation recall | Open recall | HW macro recall |
| --- | --- | --- | --- | --- | --- | --- |
| Clean | 100.0000% | RF E4 | 0.9996 | 0.9907 | 1.0000 | 0.9968 |
| Clean | 100.0000% | LightGBM E4 | 0.4994 | 0.9930 | 0.9992 | 0.8305 |
| 1% | 92.1941 ± 0.0737% | RF E4 | 0.9994 ± 0.0004 | 0.9895 ± 0.0012 | 0.9958 ± 0.0019 | 0.9949 ± 0.0007 |
| 1% | 92.1941 ± 0.0737% | LightGBM E4 | 0.4971 ± 0.0011 | 0.9928 ± 0.0007 | 0.9954 ± 0.0018 | 0.8284 ± 0.0007 |
| 2% | 84.4133 ± 0.0997% | RF E4 | 0.9979 ± 0.0007 | 0.9835 ± 0.0010 | 0.9472 ± 0.0036 | 0.9762 ± 0.0013 |
| 2% | 84.4133 ± 0.0997% | LightGBM E4 | 0.4903 ± 0.0033 | 0.9870 ± 0.0021 | 0.9467 ± 0.0035 | 0.8080 ± 0.0019 |
| 5% | 74.7809 ± 0.1046% | RF E4 | 0.9812 ± 0.0032 | 0.8869 ± 0.0073 | 0.8120 ± 0.0077 | 0.8934 ± 0.0029 |
| 5% | 74.7809 ± 0.1046% | LightGBM E4 | 0.4288 ± 0.0043 | 0.8171 ± 0.0067 | 0.8096 ± 0.0075 | 0.6852 ± 0.0027 |
| 10% | 69.5123 ± 0.1124% | RF E4 | 0.8792 ± 0.0067 | 0.6584 ± 0.0076 | 0.7198 ± 0.0073 | 0.7525 ± 0.0039 |
| 10% | 69.5123 ± 0.1124% | LightGBM E4 | 0.3377 ± 0.0089 | 0.5643 ± 0.0099 | 0.7089 ± 0.0066 | 0.5370 ± 0.0036 |

Coverage decreases because the unchanged input-quality rules can convert noise-induced negative electrical readings to missing values and trigger abstention.

End-to-end pipeline robustness under Gaussian sensor noise, including existing input-quality/abstention rules.

## Overall classification under sensor measurement noise

| Noise | Coverage | RF Macro-F1 | LightGBM Macro-F1 | RF HW macro recall | LightGBM HW macro recall |
| --- | --- | --- | --- | --- | --- |
| Clean | 100.0000% | 0.9505 | 0.9021 | 0.9968 | 0.8305 |
| 1% | 92.1941 ± 0.0737% | 0.9386 ± 0.0003 | 0.8872 ± 0.0005 | 0.9949 ± 0.0007 | 0.8284 ± 0.0007 |
| 2% | 84.4133 ± 0.0997% | 0.9185 ± 0.0008 | 0.8528 ± 0.0011 | 0.9762 ± 0.0013 | 0.8080 ± 0.0019 |
| 5% | 74.7809 ± 0.1046% | 0.8519 ± 0.0009 | 0.7311 ± 0.0015 | 0.8934 ± 0.0029 | 0.6852 ± 0.0027 |
| 10% | 69.5123 ± 0.1124% | 0.7066 ± 0.0014 | 0.5693 ± 0.0023 | 0.7525 ± 0.0039 | 0.5370 ± 0.0036 |

Coverage decreases because the unchanged input-quality rules can convert noise-induced negative electrical readings to missing values and trigger abstention.

End-to-end pipeline robustness under Gaussian sensor noise, including existing input-quality/abstention rules.

## Hardware alerts at the original frozen thresholds

| Noise | Coverage | Model | Alert recall | Alert F1 | Combined FPR |
| --- | --- | --- | --- | --- | --- |
| Clean | 100.0000% | RF E4 | 0.9955 | 0.9896 | 0.0832% |
| Clean | 100.0000% | LightGBM E4 | 0.9969 | 0.9902 | 0.0839% |
| 1% | 92.1941 ± 0.0737% | RF E4 | 0.9930 ± 0.0007 | 0.9882 ± 0.0004 | 0.0843 ± 0.0022% |
| 1% | 92.1941 ± 0.0737% | LightGBM E4 | 0.9944 ± 0.0012 | 0.9891 ± 0.0006 | 0.0821 ± 0.0026% |
| 2% | 84.4133 ± 0.0997% | RF E4 | 0.9730 ± 0.0015 | 0.9778 ± 0.0009 | 0.0866 ± 0.0035% |
| 2% | 84.4133 ± 0.0997% | LightGBM E4 | 0.9740 ± 0.0017 | 0.9778 ± 0.0010 | 0.0920 ± 0.0045% |
| 5% | 74.7809 ± 0.1046% | RF E4 | 0.8867 ± 0.0040 | 0.9192 ± 0.0020 | 0.2144 ± 0.0107% |
| 5% | 74.7809 ± 0.1046% | LightGBM E4 | 0.8889 ± 0.0026 | 0.8875 ± 0.0016 | 0.5775 ± 0.0163% |
| 10% | 69.5123 ± 0.1124% | RF E4 | 0.7780 ± 0.0040 | 0.7675 ± 0.0032 | 1.2591 ± 0.0278% |
| 10% | 69.5123 ± 0.1124% | LightGBM E4 | 0.8001 ± 0.0055 | 0.6770 ± 0.0040 | 2.8472 ± 0.0372% |

Coverage decreases because the unchanged input-quality rules can convert noise-induced negative electrical readings to missing values and trigger abstention.

End-to-end pipeline robustness under Gaussian sensor noise, including existing input-quality/abstention rules.