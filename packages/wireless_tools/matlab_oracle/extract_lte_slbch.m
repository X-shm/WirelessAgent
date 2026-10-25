% Sidelink BCH transport coding and soft decoding in all legal modes.
root = fileparts(mfilename('fullpath'));
configs = {struct('SidelinkMode','D2D','CyclicPrefixSL','Normal'), ...
           struct('SidelinkMode','D2D','CyclicPrefixSL','Extended'), ...
           struct('SidelinkMode','V2X','CyclicPrefixSL','Normal')};
records = {};
for k = 1:numel(configs)
    ue = configs{k};
    bits = mod((0:39)*7+k,2).';
    coded = lteSLBCH(ue,bits);
    [decoded,err] = lteSLBCHDecode(ue,2*double(coded)-1);
    assert(isequal(decoded,bits) && err==0);
    records{end+1} = struct('config',ue,'bits',bits.', ...
        'coded',coded.'); %#ok<AGROW>
end
output = fullfile(root,'samples','lte_slbch.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
