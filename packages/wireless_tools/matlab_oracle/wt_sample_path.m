function path = wt_sample_path(filename)
%WT_SAMPLE_PATH Return a portable output path below matlab_oracle/samples.

if nargin ~= 1 || ~(ischar(filename) || isstring(filename))
    error('wireless_toolbox:SamplePath', 'filename must be a character vector or string scalar.');
end

path = fullfile(wt_sample_dir(), char(filename));
end
