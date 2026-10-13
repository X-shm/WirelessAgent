"""End-to-end PDSCH simulation: TX → AWGN → RX.

Tests the complete cascade including:
- TX: CRC → LDPC → RM → modulation → layer map → OFDM
- Channel: AWGN
- RX: OFDM demod → soft demod → layer demap → rate recover → LDPC decode → CRC
"""
import argparse
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.nr_pdsch import pdsch_transmit, pdsch_receive


def test_perfect_channel():
    """Test TX→RX with no noise — should recover perfectly."""
    print("=== Perfect Channel Test ===")
    # Choose n_sc such that rm_len > info_len (code rate < 1)
    # info_len = nsys * zc, rm_len = n_sc * Qm
    # We want rm_len > info_len, i.e., n_sc > nsys * zc / Qm
    cases = [
        {'bgn': 1, 'mod': 'QPSK', 'zc': 4, 'nfft': 256, 'n_sc': 60},   # rm=120, info=88
        {'bgn': 1, 'mod': '16QAM', 'zc': 4, 'nfft': 256, 'n_sc': 36},  # rm=144, info=88
        {'bgn': 2, 'mod': 'QPSK', 'zc': 8, 'nfft': 256, 'n_sc': 60},   # rm=120, info=80
        {'bgn': 1, 'mod': '64QAM', 'zc': 16, 'nfft': 512, 'n_sc': 100}, # rm=600, info=352
    ]

    ok = 0
    for i, c in enumerate(cases):
        nsys = 22 if c['bgn'] == 1 else 10
        n_info = nsys * c['zc']
        n_tb = n_info - 24  # CRC24A
        Qm = {'QPSK': 2, '16QAM': 4, '64QAM': 6, '256QAM': 8, '1024QAM': 10}[c['mod']]
        rm_len = c['n_sc'] * Qm
        code_rate = n_info / rm_len

        np.random.seed(1000 + i)
        tb = np.random.randint(0, 2, n_tb, dtype=np.uint8)

        # TX
        tx_result = pdsch_transmit(tb, c['bgn'], c['mod'],
                                   c['nfft'], c['n_sc'], 1, rv=0)
        wf_r = np.array(tx_result['waveform_real'])
        wf_i = np.array(tx_result['waveform_imag'])
        waveform = wf_r + 1j * wf_i

        # RX (perfect channel)
        rx_result = pdsch_receive(waveform, c['bgn'], c['mod'],
                                  c['nfft'], c['n_sc'], 1, rv=0,
                                  max_iter=50, noise_var=1e-10, zc=c['zc'])

        rx_tb = np.array(rx_result['tb_bits'], dtype=np.uint8)
        crc_ok = rx_result['crc_ok']
        ber = np.sum(rx_tb != tb) / len(tb) if len(tb) > 0 else 0

        passed = crc_ok and ber == 0
        if passed: ok += 1
        status = "PASS" if passed else "FAIL"
        print(f"  [{i+1}/{len(cases)}] BG{c['bgn']} {c['mod']} Zc={c['zc']} "
              f"(rate={code_rate:.2f}): {status} "
              f"(CRC={crc_ok}, BER={ber:.2e})")

    print(f"  {ok}/{len(cases)} passed\n")
    return ok == len(cases)


def test_awgn_ber():
    """Test BER performance over AWGN channel."""
    print("=== AWGN BER Test ===")
    bgn = 1
    mod = 'QPSK'
    zc = 16
    nfft = 512
    n_sc = 200  # rm_len = 400, info = 352, code rate ≈ 0.88
    nsys = 22
    n_info = nsys * zc
    n_tb = n_info - 24

    snr_db_list = [-2, 0, 2, 4, 6, 8]
    n_blocks = 30

    Qm = 2
    rm_len = n_sc * Qm
    code_rate = n_info / rm_len
    print(f"  Config: BG{bgn} {mod} Zc={zc}, TB={n_tb} bits, "
          f"rate={code_rate:.3f}, {n_blocks} blocks per SNR")

    for snr_db in snr_db_list:
        np.random.seed(snr_db + 100)
        total_bits = 0
        total_errors = 0
        crc_pass = 0

        for _ in range(n_blocks):
            tb = np.random.randint(0, 2, n_tb, dtype=np.uint8)

            # TX
            tx_result = pdsch_transmit(tb, bgn, mod, nfft, n_sc, 1, rv=0)
            wf_r = np.array(tx_result['waveform_real'])
            wf_i = np.array(tx_result['waveform_imag'])
            waveform = wf_r + 1j * wf_i

            # AWGN (on time-domain waveform)
            snr_linear = 10 ** (snr_db / 10)
            sig_power = np.mean(np.abs(waveform) ** 2)
            noise_var = sig_power / snr_linear
            noise = np.sqrt(noise_var / 2) * (np.random.randn(len(waveform)) +
                                              1j * np.random.randn(len(waveform)))
            rx_waveform = waveform + noise

            # RX
            rx_result = pdsch_receive(rx_waveform, bgn, mod, nfft, n_sc, 1,
                                      rv=0, max_iter=20, noise_var=noise_var, zc=zc)

            rx_tb = np.array(rx_result['tb_bits'], dtype=np.uint8)
            errors = np.sum(rx_tb != tb)
            total_errors += errors
            total_bits += len(tb)
            if rx_result['crc_ok']:
                crc_pass += 1

        ber = total_errors / total_bits if total_bits > 0 else 0
        bler = 1 - crc_pass / n_blocks
        print(f"  SNR={snr_db:+2d} dB: BER={ber:.4e}, BLER={bler:.3f} "
              f"({crc_pass}/{n_blocks} CRC pass)")

    print()
    return True


def main():
    parser = argparse.ArgumentParser(description="NR PDSCH end-to-end regression")
    parser.add_argument(
        "--perfect-only",
        action="store_true",
        help="run only the deterministic noiseless TX/RX round-trip cases",
    )
    args = parser.parse_args()

    all_ok = True
    all_ok &= test_perfect_channel()
    if not args.perfect_only:
        all_ok &= test_awgn_ber()
    print("All done!" if all_ok else "Some tests failed!")
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
