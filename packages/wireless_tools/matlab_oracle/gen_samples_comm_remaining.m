function gen_samples_comm_remaining()
% Generate compact R2026a oracle samples for independent Communications slices.
root = fileparts(fileparts(mfilename('fullpath')));
sample = struct;
[h,g,k] = cyclgen(7, [1 1 0 1]);
sample.cyclgen = struct('h',h,'g',g,'k',k);
message = mod((0:15)',2);
sample.tpcenc = tpcenc(message,[7;7],[4;4]).';
c = iqimbal2coef(2,15);
sample.iqimbal2coef = struct('real',real(c),'imag',imag(c));
x = reshape(0:7,[2,2,2]);
p = eye(2);
sample.ofdmPrecode = ofdmPrecode(x,p);
sample.bersync = bersync([0 5],0.1,'carrier');
sample.gsmInfo = gsmInfo(gsmDownlinkConfig);
indices = dvbs2ldpc(1/2,'indices');
sample.dvbs2ldpc_first5 = indices(indices(:,1)<=5,:);
path = fullfile(root,'matlab_oracle','samples','comm_remaining_oracle.json');
fid = fopen(path,'w');
assert(fid ~= -1,'Unable to open oracle sample file');
cleanup = onCleanup(@() fclose(fid));
fwrite(fid,jsonencode(sample),'char');
end
