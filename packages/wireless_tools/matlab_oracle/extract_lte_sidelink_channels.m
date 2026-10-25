% Physical sidelink channel modulation oracle across modes and modulation.
root = fileparts(mfilename('fullpath'));
records = {};
for entry = {'ltePSBCH','ltePSCCH','ltePSSCH'}
    name = entry{1};
    if strcmp(name,'ltePSBCH')
        cases = {struct('NSLID',0),struct('NSLID',167),struct('NSLID',335)};
        lengths = [1152 864 1008];
    elseif strcmp(name,'ltePSCCH')
        cases = {struct(),struct(),struct()};
        lengths = [288 240 480];
    else
        cases = {struct('SidelinkMode','D2D','CyclicPrefixSL','Normal', ...
                        'Modulation','QPSK','NSAID',37,'NSubframePSSCH',0), ...
                 struct('SidelinkMode','D2D','CyclicPrefixSL','Extended', ...
                        'Modulation','16QAM','NSAID',255,'NSubframePSSCH',7), ...
                 struct('SidelinkMode','V2X','CyclicPrefixSL','Normal', ...
                        'Modulation','QPSK','NXID',513,'NSubframePSSCH',3)};
        lengths = [288 480 240];
    end
    for k = 1:numel(cases)
        ue = cases{k};
        length_bits = lengths(k);
        bits = mod((0:length_bits-1)*7+k,2).';
        if strcmp(name,'ltePSCCH')
            values = feval(name,bits);
            [soft,decoded] = ltePSCCHDecode(values);
        else
            values = feval(name,ue,bits);
            [soft,decoded] = feval([name 'Decode'],ue,values);
        end
        records{end+1} = struct('entry',name,'config',ue,'bits',bits.', ...
            'real',real(values(:)).','imag',imag(values(:)).', ...
            'soft',soft(:).','decoded_real',real(decoded(:)).', ...
            'decoded_imag',imag(decoded(:)).'); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_sidelink_channels.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
