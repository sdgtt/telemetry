function log_ad9361_tx_quad_cal_test(test_name, device, failed, iterations, channel, date, server,test)

if nargin < 6
    % '2020-09-16T19:22:31.999032'
    date = datestr(now,'yyyy-mm-ddTHH:MM:SS.FFF');
end
if nargin < 7
    server = "alpine";
end
if nargin < 8
    test = false;
end

tel = py.telemetry.ingest(pyargs("server",server));
tel.use_test_index = test;
tel.log_ad9361_tx_quad_cal_test(test_name, device, failed, iterations, channel, date);