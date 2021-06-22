function log_lte_test(results, date, server, test)

    if nargin < 2
        % '2020-09-16T19:22:31.999032'
        date = datestr(now,'yyyy-mm-ddTHH:MM:SS.FFF');
    end
    if nargin < 3
        server = "alpine";
    end
    if nargin < 4
        test = false;
    end

    tel = py.telemetry.ingest(pyargs("server",server)); disp(properties(tel));
    % tel.use_test_index = test;
    for i = 1:numel(results)
        device_name = results(i).Details.DeviceName;
        tx_attn = results(i).Details.TxAttn;
        rx_gain_control_mode = results(i).Details.RxGainControlMode;
        lo_freq = results(i).Details.LOFreq;
        tmn = results(i).Details.TMN;
        bw = results(i).Details.BW;
        evm_pbch = results(i).Details.evmPBCH;
        evm_pcfich = results(i).Details.evmPCFICH;
        evm_phich = results(i).Details.evmPHICH;
        evm_pdcch = results(i).Details.evmPDCCH;
        evm_rs = results(i).Details.evmRS;
        evm_sss = results(i).Details.evmSSS;
        evm_pss = results(i).Details.evmPSS;
        evm_pdsch = results(i).Details.evmPDSCH;

        tel.log_lte_evm_test(device_name, tx_attn, rx_gain_control_mode, lo_freq, ...
            tmn, bw, evm_pbch, evm_pcfich, evm_phich, evm_pdcch, evm_rs, ...
            evm_sss, evm_pss, evm_pdsch, date);
    end
