% PUSCH ACK, RI, CQI short-block coding across selected Qd/modulations.
root = fileparts(mfilename('fullpath'));
records = {};
for kind = {'ACK','RI','CQI'}
    k = kind{1};
    for modulation = {'QPSK','16QAM','64QAM'}
        modname = modulation{1};
        if strcmp(k,'CQI')
            lengths = 1:11;
            qds = 16;
        else
            lengths = 1:4;
            qds = [4 8 16];
        end
        for qd = qds
            for n = lengths
                chs = struct('Modulation',modname,'QdACK',qd, ...
                    'QdRI',qd,'QdCQI',qd,'OACK',n,'ORI',n,'OCQI',n);
                entry = ['lte' k];
                zero = zeros(n,1);
                baseline = feval([entry 'Encode'],chs,zero);
                basis = zeros(n,numel(baseline));
                for bit = 1:n
                    input = zero;
                    input(bit) = 1;
                    basis(bit,:) = feval([entry 'Encode'],chs,input).';
                end
                if strcmp(k,'CQI')
                    full = [];
                else
                    full = zeros(2^n,numel(baseline));
                    for value = 0:2^n-1
                        input = bitget(value,1:n).';
                        full(value+1,:) = feval([entry 'Encode'],chs,input).';
                    end
                end
                trials = {};
                for t = 1:3
                    input = mod((1:n)*t+floor((1:n)/3),2).';
                    encoded = feval([entry 'Encode'],chs,input);
                    soft = 2*double(encoded)-1;
                    soft(encoded<0) = 0;
                    [decoded,blockerr] = feval([entry 'Decode'],chs,soft);
                    noisy = soft;
                    noisy(1:4:end) = -0.25*noisy(1:4:end);
                    [noisydecoded,noisyerr] = feval([entry 'Decode'],chs,noisy);
                    trials{end+1} = struct('bits',input.','coded',encoded.', ...
                        'decoded',decoded.','block_error',blockerr, ...
                        'noisy_soft',noisy.','noisy_decoded',noisydecoded.', ...
                        'noisy_error',noisyerr); %#ok<AGROW>
                end
                records{end+1} = struct('entry',entry,'n',n,'qd',qd, ...
                    'modulation',modname,'zero',baseline.','basis',basis, ...
                    'full',full,'trials',{trials}); %#ok<AGROW>
            end
        end
    end
end
output = fullfile(root,'samples','lte_ul_control_codes.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
fprintf('cases %d\n',numel(records));
