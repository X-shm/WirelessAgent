% MATLAB R2026a vectors for LTE Turbo PCCC and QPP verification.
root = fileparts(mfilename('fullpath'));
lengths = [40 48 512 6144];
records = cell(1,numel(lengths)+1);
for index = 1:numel(lengths)
    k = lengths(index);
    n = 0:k-1;
    bits = int8(mod(7*n + floor(n/5),2));
    coded = lteTurboEncode(bits(:));
    record = struct('bits',double(bits),'coded',double(coded(:)).');
    if k <= 512
        rate = struct();
        recovered = struct();
        for rv = 0:3
            field = sprintf('rv%d',rv);
            matched = lteRateMatchTurbo(coded,min(2*k,1024),rv);
            rate.(field) = double(matched(:)).';
            softmatched = 2*double(matched)-1;
            restored = lteRateRecoverTurbo(softmatched,k-24,rv);
            recovered.(field) = double(restored{1}(:)).';
        end
        record.rate_match = rate;
        record.rate_recover = recovered;
    end
    if k <= 512
        nsoft = (1:numel(coded)).';
        soft = (2*double(coded)-1) + 0.8*sin(0.37*nsoft) + 0.6*cos(0.11*nsoft);
        record.soft = soft.';
        record.decoded = double(lteTurboDecode(soft,5)).';
    end
    records{index} = record;
end
bits = int8(mod(0:39,2));
bits(1:4) = -1;
coded = lteTurboEncode(bits(:));
records{end} = struct('bits',double(bits),'coded',double(coded(:)).');
output = fullfile(root,'samples','lte_turbo.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
