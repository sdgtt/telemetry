function [x, y, t] = ad9361_tx_quad_cal_test(test_name, device, channel, server, test)

if nargin < 4
    server = "alpine";
end
if nargin < 5
    test = false;
end
tel = py.telemetry.searches(pyargs("server",server));
% tel.use_test_index = test;
o = tel.ad9361_tx_quad_cal_test(pyargs("test_name",test_name,"device",device,"channel",channel));
xp = o{1};
yp = o{2};
tp = o{3};

l = length(xp);
x = cell(l,1);
y = zeros(l,1);
t = zeros(l,1);

for k = 1:l
   x{k} = string(xp{k}); 
   y(k) = double(yp{k}); 
   t(k) = double(tp{k}); 
end


end