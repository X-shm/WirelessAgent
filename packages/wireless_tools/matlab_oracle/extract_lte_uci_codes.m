% R2026a UCI encoder basis and independent deterministic decoder samples.
root = fileparts(mfilename('fullpath'));
entries = {'lteUCI',11,13; 'lteUCI3',22,22};
records = {};
for e = 1:size(entries,1)
    entry = entries{e,1};
    decode_max = entries{e,2};
    encode_max = entries{e,3};
    for n = 1:encode_max
        zero = zeros(n,1);
        base = feval([entry 'Encode'],zero);
        basis = zeros(n,numel(base));
        for bit = 1:n
            input = zero;
            input(bit) = 1;
            basis(bit,:) = feval([entry 'Encode'],input).';
        end
        trials = {};
        for t = 1:3
            input = mod((1:n)*t + floor((1:n)/3),2).';
            encoded = feval([entry 'Encode'],input);
            trial = struct('bits',input.','coded',encoded.');
            if n <= decode_max
                trial.decoded = feval([entry 'Decode'],2*double(encoded)-1,n).';
                soft = 2*double(encoded)-1;
                soft(1:4:end) = -0.25*soft(1:4:end);
                trial.noisy_soft = soft.';
                trial.noisy_decoded = feval([entry 'Decode'],soft,n).';
            end
            trials{end+1} = trial; %#ok<AGROW>
        end
        records{end+1} = struct('entry',entry,'n',n,'zero',base.', ...
            'basis',basis,'trials',{trials}); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_uci_codes.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
