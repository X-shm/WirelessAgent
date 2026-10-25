function gen_samples_optimization_toolbox()
% Generate official MATLAB Optimization Toolbox reference samples.
% Run from any directory; output is written beside this script.
base = fileparts(mfilename('fullpath'));
outDir = fullfile(base, 'samples');
if ~exist(outDir, 'dir'), mkdir(outDir); end
opts = optimoptions('fmincon','Display','off','OptimalityTolerance',1e-10,'ConstraintTolerance',1e-10);

% fmincon supported subset: quadratic objective, linear constraints/bounds.
p = '{"H":2,"f":-4,"x0":[0],"bounds":[[0,3]]}';
x = fmincon(@(x) x.^2-4*x,0,[],[],[],[],0,3,[],opts);
write_sample(outDir,'constrained_nonlinear_optimize',p,struct('x',x,'objective',x.^2-4*x));

% linprog: min x1+2*x2 subject to x1+x2 >= 4 and x >= 0.
p = '{"c":[1,2],"A_ub":[[-1,-1]],"b_ub":[-4],"bounds":[[0,null],[0,null]]}';
[x,fval] = linprog([1;2],[-1 -1],-4,[],[],[0;0],[],optimoptions('linprog','Display','none'));
write_sample(outDir,'linear_programming',p,struct('x',x(:).','objective',fval));

% quadprog: min x^2-4*x subject to 0 <= x <= 3.
p = '{"H":2,"f":-4,"x0":[0],"bounds":[[0,3]]}';
[x,fval] = quadprog(2,-4,[],[],[],[],0,3,0,optimoptions('quadprog','Display','off'));
write_sample(outDir,'quadratic_programming',p,struct('x',x(:).','objective',fval));

% intlinprog: small integer resource split.
p = '{"c":[-3,-2],"integer_variables":[0,1],"A_ub":[[2,1],[1,2]],"b_ub":[4,4],"bounds":[[0,10],[0,10]]}';
[x,fval] = intlinprog([-3;-2],[1 2;1 2],[2 1;1 2],[4;4],[],[],[0;0],[10;10], ...
    optimoptions('intlinprog','Display','off'));
write_sample(outDir,'mixed_integer_linear_programming',p,struct('x',x(:).','objective',fval));

% fminimax: balance two linear objective functions over [0,2].
p = '{"objective_matrix":[[1],[-1]],"objective_offset":[-1,1],"bounds":[[0,2]]}';
[x,fval] = fminimax(@(x)[x-1;1-x],1,[],[],[],[],0,2,[],optimoptions('fminimax','Display','off'));
write_sample(outDir,'minimax_optimization',p,struct('x',x,'objective',max([x-1,1-x])));

% fgoalattain: hit two weighted linear goals.
p = '{"objective_matrix":[[1],[-1]],"goals":[1,-1],"weights":[1,1],"bounds":[[0,2]]}';
[x,~,attainfactor] = fgoalattain(@(x)[x;-x],0,[1;-1],[1;1],[],[],[],[],0,2,[],optimoptions('fgoalattain','Display','off'));
write_sample(outDir,'goal_attainment_optimization',p, ...
    struct('x',x,'attainment',attainfactor,'objective_values',[x;-x]));

% optimoptions: preserve the common subset used by the Python adapters.
opts = optimoptions('quadprog','Algorithm','active-set','Display','off', ...
    'MaxIterations',500,'OptimalityTolerance',1e-7);
p = '{"solver":"quadprog","settings":{"algorithm":"active-set","max_iterations":500,"tolerance":1e-7,"display":false}}';
write_sample(outDir,'create_optimization_options',p, ...
    struct('solver','quadprog','options',struct('algorithm',char(opts.Algorithm), ...
    'max_iterations',opts.MaxIterations,'tolerance',opts.OptimalityTolerance, ...
    'display',strcmpi(opts.Display,'iter')),'coverage', ...
    'common normalized settings only; not full MATLAB option parity'));

% optimwarmstart: the portable adapter preserves x0/options, not MATLAB active-set history.
ws = optimwarmstart([1;3],opts);
p = '{"solver":"quadprog","x0":[1,3],"options":{"algorithm":"active-set"}}';
write_sample(outDir,'create_optimization_warmstart',p, ...
    struct('solver','quadprog','x0',ws.X(:).','options',struct('algorithm',char(ws.Options.Algorithm)), ...
    'active_set_reuse',false, ...
    'coverage','initial-point descriptor only; MATLAB active-set history is not serialized or reused'));
end

function write_sample(outDir,name,problem,expected)
if isfield(expected,'x') && ~iscell(expected.x)
    expected.x = num2cell(expected.x(:).');
end
payload = ['[{"problem":' char(problem) ',"expected":' jsonencode(expected) '}]'];
fid = fopen(fullfile(outDir,[name '_samples.json']),'w');
if fid < 0, error('Cannot create sample file for %s',name); end
cleanup = onCleanup(@() fclose(fid));
fwrite(fid,payload,'char');
end
