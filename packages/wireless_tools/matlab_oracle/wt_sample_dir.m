function sample_dir = wt_sample_dir()
%WT_SAMPLE_DIR Return the portable directory for checked-in oracle samples.
%
% All MATLAB generators must resolve paths from their own location rather
% than from MATLAB's current folder or a developer-specific drive path.

script_dir = fileparts(mfilename('fullpath'));
sample_dir = fullfile(script_dir, 'samples');
if ~exist(sample_dir, 'dir')
    mkdir(sample_dir);
end
end
